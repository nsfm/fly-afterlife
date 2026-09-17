"""
pair.py - two flies in one room. the male (MaleCNS, flyvis eye, touch) and the female (FlyWire, W_syn 0.5,
no eye) walk the same arena, each on its own descending neurons.

    uv run python world/pair.py --seconds 30 --out world/pair0.npz [--no-female]  (control: him alone)

senses between them (labelled, all through named receptors):
  he sees her: a dark sphere r=0.15 at eye height (albedo 0.1) in his raytraced retina.
  he smells her: fly odour (methyl laurate, Or47b -> ORN_VA1v) and female cuticular cue (Or88a -> ORN_VA1d),
     concentration exp(-d / 0.8) at each antenna, bilateral.
  she smells him: cVA (Or67d -> ORN_DA1), same law.
  touch: both, leg bristles (his VNC bristles; her 'mechanosensory' class) on the contacted side.
  song: if his pIP10 fires above its running mean + 2 sd in a chunk and she is within 0.4 m, that chunk is
     a song bout: her Johnston's organ (JO-*, mechanosensory) is driven at 100 Hz.
steering: his DNa02 (vision; efference off; rest-sub) when free; while his bristles are pressed (wall, pillar, her) the leg-MN asymmetry steers alone, gain calibrated so the bristle-evoked asymmetry is worth 6 deg/chunk; hers DNa02 + heading noise, turn-away on contact
  (sd 15 deg/s). both walk at 0.3 / 0.15 m/s. readouts per chunk: his pC1 (all P1 types), pIP10, mAL, LC10a,
  DNa02 L/R; her pC1a-e, vpoEN, ORN_DA1, DNa02 L/R; distance, contacts, song bouts.
"""
import os, sys, argparse, time, numpy as np, torch
sys.path.insert(0, "seam"); sys.path.insert(0, "ref/flybrain/scripts"); sys.path.insert(0, "world")
os.environ.setdefault("FLYVIS_ROOT_DIR", "/home/nate/code/fly-afterlife/flyvis_data")
from omma import Eye, Scene
from flysim import FlyBrain, Params
from fastlif import FastFlyBrain   # numba step, verified spike-for-spike against flysim (world/fastlif.py)
ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--seconds", type=float, default=30.0); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--numpy-engine", action="store_true", help="use the original numpy LIF step instead of the numba one (same spikes, slower)"); ap.add_argument("--her-albedo", type=float, default=0.1, help="her body tone (0.1 dark; 0.5 = invisible against this room, the control)"); ap.add_argument("--proprio", type=float, default=0.0, help="peak Hz for his six legs of proprioceptors (leg-nerve cells only, world/legs.npz): tripod gait at 10 Hz, each leg in its stance half-cycle, scaled by pace, plus a 15 pct tonic load term; 0 = silent (was always silent)"); ap.add_argument("--deterministic", action="store_true", help="torch deterministic algorithms for flyvis: same seed -> same run, bit for bit (default GPU kernels differ at 1e-6 per call, which flips Poisson draws); costs ~+130 ms per chunk")
ap.add_argument("--model", default="flow/0000/000"); ap.add_argument("--no-female", action="store_true"); ap.add_argument("--gain", type=float, default=3.0); ap.add_argument("--drive-gain", type=float, default=150.0)
args = ap.parse_args(); fps, CH = 100, 10; rng = np.random.default_rng(args.seed)
g = np.load("seam/eye_geom.npz"); eye = Eye("seam/eye_geom.npz")
posts = np.array([(0.0, 1.6, 0.35, 0.85), (0.0, -1.6, 0.35, 0.85)], np.float32)   # pillars pale (0.85): she is the only dark thing in the room
WALLS = dict(half=2.0, height=1.0, albedo=0.6)   # the room: 4 x 4 m, walls 1 m tall, lighter than the floor, darker than the sky   # pillars: floor-to-sky cylinders, bark-dark
# ---- flyvis (his eye)
import flyvis
if args.deterministic: os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8"); torch.use_deterministic_algorithms(True)
from flyvis import NetworkView
net = NetworkView(args.model).init_network(); net.eval()
lattice = sorted({(u, v) for u in range(-15, 16) for v in range(max(-15, -15 - u), min(15, 15 - u) + 1)}); idx_of = {uv: i for i, uv in enumerate(lattice)}
types = ["T4a", "T4b", "T4c", "T4d", "T5a", "T5b", "T5c", "T5d"]; ntype = net.connectome.nodes.type[:].astype(str); tix = {t: np.flatnonzero(ntype == t) for t in types}
eyemap = {}
for s in "LR":
    k = np.flatnonzero(g["side"] == s); v = np.rint(+g["sx"][k]).astype(int); u = np.rint(-g["sy"][k] - v / 2.0).astype(int)
    col = np.array([idx_of.get((int(a), int(b)), -1) for a, b in zip(u, v)]); ok = col >= 0; eyemap[s] = (k[ok], col[ok])
state = {"L": None, "R": None}
def flyvis_chunk(lum_chunk):
    out = {}
    for s in "LR":
        k, col = eyemap[s]; movie = np.full((1, CH, 1, 721), 0.5, np.float32); movie[0, :, 0, col] = lum_chunk[:, k].T
        with torch.no_grad(): st = net.simulate(torch.tensor(movie, device=flyvis.device), dt=1 / fps, initial_state=state[s], as_states=True)
        state[s] = st[-1]; act = torch.stack([x.nodes.activity[0] for x in st]).cpu().numpy()
        for t in types: out[(s, t)] = act[:, tix[t]]
    return out
# ---- his brain
Brain = FlyBrain if args.numpy_engine else FastFlyBrain
M = Brain("brain_whole.npz", seed=args.seed); mty = M.type.astype(str); mns = M.side.astype(str); mcls = M.cls.astype(str)
cols = np.load("seam/t4t5_columns.npz"); gkey = {(str(s), int(a), int(h)): i for i, (s, a, h) in enumerate(zip(g["side"], g["hex1"], g["hex2"]))}
gi = np.array([gkey[(str(s), int(a), int(h))] for s, a, h in zip(cols["side"], cols["hex1"], cols["hex2"])])
groups = {}
for s in "LR":
    k, col = eyemap[s]; colmap = dict(zip(k.tolist(), col.tolist()))
    for t in types:
        kk = (cols["type"] == t) & (cols["side"] == s); hx = np.array([colmap.get(int(i), -1) for i in gi[kk]]); ok = hx >= 0; groups[(t, s)] = (cols["idx"][kk][ok], hx[ok])
RM = {}
for name, sel in [("DNa02", mty == "DNa02"), ("pC1", np.char.startswith(mty, "pC1")), ("pIP10", mty == "pIP10"), ("mAL", np.char.startswith(mty, "mAL")), ("LC10a", mty == "LC10a"), ("ORN_VA1v", mty == "ORN_VA1v"), ("legMN", M.sc == "vnc_motor"), ("DN", M.sc == "descending_neuron")]:
    for s in "LR": RM[f"{name}_{s}"] = np.flatnonzero(sel & (mns == s))
    if name in ("pC1", "pIP10", "mAL", "LC10a"): RM[name] = np.flatnonzero(sel)
TACT_M = {s_: np.flatnonzero((mcls == "mechanosensory_tactile") & (mns == s_)) for s_ in "LR"}
_legs = np.load("world/legs.npz"); LEGS = {k: _legs[k] for k in _legs.files}; STEP_HZ = 10.0   # his six legs' proprioceptors by entry nerve (ProLN/MesoLN/MetaLN) x root side; haltere, wing, abdominal sensors stay silent
TRIPOD = {"L1": 0.0, "R2": 0.0, "L3": 0.0, "R1": 0.5, "L2": 0.5, "R3": 0.5}   # alternating tripods, half a cycle apart
_sp = np.load("world/ppk23_split.npz"); PPK_F = np.flatnonzero(np.isin(M.bodyId, _sp["F"])); PPK_M = np.flatnonzero(np.isin(M.bodyId, _sp["M"]))   # contact-pheromone leg neurons, F- and M-responsive by wiring; both fire on contact in life (Kallman 2015), P1 weighs them
TAP_HZ = 60.0; TAP_MS = 300.0; tap_t = -1e9   # a tap is a burst: ~60 Hz cap (Weiss 2011 GRN ceiling), ~300 ms, not a 150 Hz hold (docs/physiology/chemo_thermo_hygro.md)
RM["ppkF"] = PPK_F; RM["DNp09"] = np.flatnonzero(np.char.startswith(mty, "DNp09")); RM["MDN"] = np.flatnonzero(np.char.startswith(mty, "MDN")); RM["legMN"] = np.flatnonzero(M.sc == "vnc_motor")
M.define_odor("flyodour", n_channels=1, seed=0); M._odor_map["flyodour"] = {"ORN_VA1v": 1.0, "ORN_VA1d": 0.6}
M.driven[:] = False
for cl in M.SENSORY_CLASSES: M.driven[M.cls == cl] = True
for t, (idx, _) in groups.items(): M.driven[idx] = True
M._driven_idx = np.flatnonzero(M.driven); M.reset(); SPF = int(round(1000 / fps / M.p.dt))
# ---- her brain
RF = {}
if not args.no_female:
    F = Brain("brain_female2.npz", seed=args.seed + 100, balance_hemispheres=False, params=Params(mv_per_synapse=0.45)); fty = F.type.astype(str); fns = F.side.astype(str); fcls = F.cls.astype(str)
    RF = {}
    for name, sel in [("DNa02", fty == "DNa02"), ("pC1", np.char.startswith(fty, "pC1")), ("vpoEN", fty == "vpoEN"), ("ORN_DA1", fty == "ORN_DA1"), ("JO", np.char.startswith(fty, "JO")), ("DN", F.sc == "descending_neuron")]:
        for s in "LR": RF[f"{name}_{s}"] = np.flatnonzero(sel & (fns == s))
        RF[name] = np.flatnonzero(sel)
    JO = RF["JO"]; TACT_F = {s_: np.flatnonzero((fcls == "mechanosensory") & ~np.char.startswith(fty, "JO") & (fns == s_)) for s_ in "LR"}
    F.define_odor("cVA", n_channels=1, seed=0); F._odor_map["cVA"] = {"ORN_DA1": 1.0}
    F.driven[:] = False
    for cl in F.SENSORY_CLASSES: F.driven[F.cls == cl] = True
    F._driven_idx = np.flatnonzero(F.driven); F.reset()
    RF["DNp09"] = np.flatnonzero(np.char.startswith(fty, "DNp09")); RF["MDN"] = np.flatnonzero(np.char.startswith(fty, "MDN"))
    print(f"her readouts: pC1 {len(RF['pC1'])}, vpoEN {len(RF['vpoEN'])}, ORN_DA1 {len(RF['ORN_DA1'])}, JO {len(JO)}, DNa02 {len(RF['DNa02_L'])}/{len(RF['DNa02_R'])}")
print(f"his readouts: pC1 {len(RM['pC1'])}, pIP10 {len(RM['pIP10'])}, mAL {len(RM['mAL'])}, LC10a {len(RM['LC10a'])}, ORN_VA1v {len(RM['ORN_VA1v_L'])}/{len(RM['ORN_VA1v_R'])}")
# ---- world state
mx, my, mh = -1.2, 0.0, 0.0; fx, fy, fh = 1.2, 0.3, 180.0; LAM = 0.8; BODY = 0.08; HER_R = 0.12; HER_ALB = args.her_albedo   # a fly is dark; against a 0.4 floor, 0.6 walls and pale pillars she is the one dark object he can approach   # his body (drawn as a 16 cm fly), hers 24 cm; contact when the bodies meet
def scene_now():
    sph = []
    if not args.no_female: sph.append((np.array([fx, fy, 0.5]), HER_R, HER_ALB))   # her: the larger sex, fly-coloured (a mid-tone against bark and sky)
    return Scene(sky=0.8, ground=0.4, spheres=sph, pillars=[(x, y, r, a) for x, y, r, a in posts], walls=WALLS)
def antennae(x, y, h):
    hr = np.radians(h); fwd = np.array([np.cos(hr), np.sin(hr)]); left = np.array([-np.sin(hr), np.cos(hr)]); p = np.array([x, y])
    return p + 0.1 * fwd + 0.15 * left, p + 0.1 * fwd - 0.15 * left
# warm-up: flyvis state + T4/T5 rest on the still scene; LIF rest
acc = {}
for c in range(10):
    a = flyvis_chunk(np.stack([eye.render(scene_now(), pos=(mx, my, 0.5), heading_deg=mh) for _ in range(CH)]))
    if c >= 5:
        for k_, v_ in a.items(): acc.setdefault(k_, []).append(v_)
rest = {k_: np.concatenate(v_).mean(0) for k_, v_ in acc.items()}
for _ in range(500):
    M.step()
    if not args.no_female: F.step()
# DNa02 resting offset for him (vision on)
rl = rr = 0
for c in range(20):
    a = flyvis_chunk(np.stack([eye.render(scene_now(), pos=(mx, my, 0.5), heading_deg=mh) for _ in range(CH)]))
    for f in range(CH):
        for (t, s), (idx, hx) in groups.items(): M.drive_hz[idx] = args.drive_gain * np.clip((a[(s, t)][f] - rest[(s, t)])[hx], 0, 1)
        for _ in range(SPF): spk = M.step(); rl += int(spk[RM["DNa02_L"]].sum()); rr += int(spk[RM["DNa02_R"]].sum())
rest_net = (rr - rl) / 20; print(f"his DNa02 rest offset {rest_net:+.2f}/chunk")
leg_stand = 0; dn_stand_f = 0
for c in range(10):
    a = flyvis_chunk(np.stack([eye.render(scene_now(), pos=(mx, my, 0.5), heading_deg=mh) for _ in range(CH)]))
    for f in range(CH):
        for (t, s), (idx, hx) in groups.items(): M.drive_hz[idx] = args.drive_gain * np.clip((a[(s, t)][f] - rest[(s, t)])[hx], 0, 1)
        for _ in range(SPF):
            leg_stand += int(M.step()[RM["legMN"]].sum())
            if not args.no_female: dn_stand_f += int(F.step()[RF["DN"]].sum())
leg_stand /= 10; dn_stand_f /= 10; print(f"pace baselines per chunk: his leg MN {leg_stand:.0f}, her DN {dn_stand_f:.0f}")
# touch-reflex calibration: drive his left bristles, then his right, standing; the leg-MN asymmetry each evokes is worth REFLEX_DEG per chunk
asym_side = {}
for s_ in "LR":
    for s2 in "LR": M.drive_hz[TACT_M[s2]] = 150.0 if s2 == s_ else 0.0
    rl = rr = 0
    for c in range(10):
        for f in range(CH):
            for _ in range(SPF): spk = M.step(); rl += int(spk[RM["legMN_L"]].sum()); rr += int(spk[RM["legMN_R"]].sum())
    asym_side[s_] = (rr - rl) / max(rr + rl, 1)
for s2 in "LR": M.drive_hz[TACT_M[s2]] = 0.0
REFLEX_DEG = 6.0; leg_gain = REFLEX_DEG / max(abs(asym_side["L"] - asym_side["R"]) / 2, 1e-3)
print(f"touch reflex: leg-MN asymmetry (R-L)/(R+L) with left bristles {asym_side['L']:+.3f}, right {asym_side['R']:+.3f} -> gain {leg_gain:.0f} deg per unit asymmetry")
v_m = 0.3; v_f = 0.15
# ---- loop
T = int(args.seconds * fps); LUM, POSE, POSE2, TOUCH, SONG, TKIND = [], [], [], [], [], []; log = {f"m_{k}": [] for k in RM} | ({f"f_{k}": [] for k in RF} if not args.no_female else {}) | {"dist": [], "song": [], "v_m": [], "v_f": []}
ema = 0.0; leg_rest = 0.0; pip_hist = []; contacts = 0; t0 = time.time(); prev_kind = 0
for c in range(T // CH):
    lum = np.zeros((CH, eye.n), np.float32); touched_m = [None] * CH; touched_f = [None] * CH; kind_m = [0] * CH
    for f in range(CH):
        sc = scene_now(); lum[f] = eye.render(sc, pos=(mx, my, 0.5), heading_deg=mh); POSE.append((mx, my, mh)); POSE2.append((fx, fy, fh))
        # move
        mx += v_m / fps * np.cos(np.radians(mh)); my += v_m / fps * np.sin(np.radians(mh))
        if not args.no_female: fx += v_f / fps * np.cos(np.radians(fh)); fy += v_f / fps * np.sin(np.radians(fh))
        # walls (4 x 4 m): reflect heading
        for (px_, py_, hh_, who) in ((mx, my, mh, "m"), (fx, fy, fh, "f")):
            pass
        def wall(px_, py_, hh_, r_):
            """hold at the wall; return the side the wall is on relative to heading (L/R/B) or None."""
            W_ = 2.0 - r_; nx_ = ny_ = 0.0
            if px_ > W_: px_ = W_; nx_ = -1.0
            if px_ < -W_: px_ = -W_; nx_ = 1.0
            if py_ > W_: py_ = W_; ny_ = -1.0
            if py_ < -W_: py_ = -W_; ny_ = 1.0
            if nx_ == 0.0 and ny_ == 0.0: return px_, py_, None
            brg_ = (np.degrees(np.arctan2(-ny_, -nx_)) - hh_ + 180) % 360 - 180      # bearing of the wall (opposite the inward normal)
            return px_, py_, ("L" if brg_ >= 0 else "R")   # no head-on class for a wall: whichever side touched first owns the reflex (both sides driven = no asymmetry = pinned for minutes, seed 3)
        mx, my, wm = wall(mx, my, mh, BODY); fx, fy, wf = wall(fx, fy, fh, HER_R)
        if wm: touched_m[f] = wm; kind_m[f] = 1
        if wf: touched_f[f] = wf
        # contacts: posts for him; each other
        for ox, oy, r_, _ in posts:
            dd = np.hypot(mx - ox, my - oy)
            if dd < r_ + BODY:
                mx, my = ox + (mx - ox) / max(dd, 1e-6) * (r_ + BODY), oy + (my - oy) / max(dd, 1e-6) * (r_ + BODY)
                brg = (np.degrees(np.arctan2(oy - my, ox - mx)) - mh + 180) % 360 - 180; touched_m[f] = "L" if brg >= 0 else "R"; kind_m[f] = 1
        if not args.no_female:
            for ox, oy, r_, _ in posts:
                ddf = np.hypot(fx - ox, fy - oy)
                if ddf < r_ + HER_R:
                    ang_ = np.arctan2(fy - oy, fx - ox); fx, fy = ox + (r_ + HER_R) * np.cos(ang_), oy + (r_ + HER_R) * np.sin(ang_)
                    brg_ = (np.degrees(np.arctan2(oy - fy, ox - fx)) - fh + 180) % 360 - 180; touched_f[f] = "L" if brg_ >= 0 else "R"
            dd = np.hypot(mx - fx, my - fy)
            if dd < BODY + HER_R:
                contacts += 1; kind_m[f] = 2; push = (BODY + HER_R - dd) / 2; ux_, uy_ = (mx - fx) / max(dd, 1e-6), (my - fy) / max(dd, 1e-6); mx += ux_ * push; my += uy_ * push; fx -= ux_ * push; fy -= uy_ * push   # solid bodies
                brg = (np.degrees(np.arctan2(fy - my, fx - mx)) - mh + 180) % 360 - 180; touched_m[f] = "L" if brg > 8 else ("R" if brg < -8 else "B")
                brg2 = (np.degrees(np.arctan2(my - fy, mx - fx)) - fh + 180) % 360 - 180; touched_f[f] = "L" if brg2 > 8 else ("R" if brg2 < -8 else "B")
        TOUCH.append(touched_m[f]); TKIND.append(kind_m[f])
    a = flyvis_chunk(lum); cntM = {k: 0 for k in RM}; cntF = {k: 0 for k in RF} if not args.no_female else {}; accM = np.zeros(M.N, np.int32); accF = np.zeros(F.N, np.int32) if not args.no_female else None
    dist = np.hypot(mx - fx, my - fy) if not args.no_female else np.inf
    # smells at antennae (chunk-constant)
    aL, aR = antennae(mx, my, mh)
    if not args.no_female:
        cL, cR = float(np.exp(-np.hypot(*(aL - [fx, fy])) / LAM)), float(np.exp(-np.hypot(*(aR - [fx, fy])) / LAM)); M.smell_bilateral(left={"flyodour": cL}, right={"flyodour": cR})
        bL, bR = antennae(fx, fy, fh); dL, dR = float(np.exp(-np.hypot(*(bL - [mx, my])) / LAM)), float(np.exp(-np.hypot(*(bR - [mx, my])) / LAM)); F.smell_bilateral(left={"cVA": dL}, right={"cVA": dR})
    singing = bool(pip_hist) and len(pip_hist) >= 5 and (log["song"] and log["song"][-1]) and dist < 0.4
    for f in range(CH):
        for (t, s), (idx, hx) in groups.items(): M.drive_hz[idx] = args.drive_gain * np.clip((a[(s, t)][f] - rest[(s, t)])[hx], 0, 1)
        tm = touched_m[f]
        if args.proprio > 0:   # tripod gait: each leg's proprioceptors fire in its stance phase, rate scaled by his pace; standing = a low tonic load signal
            ph_ = STEP_HZ * (len(POSE) / fps); pace_ = float(np.clip(v_m / 0.45, 0, 1))
            for leg_, idx_ in LEGS.items(): M.drive_hz[idx_] = args.proprio * (0.15 + 0.85 * pace_ * max(0.0, np.sin(2 * np.pi * (ph_ - TRIPOD[leg_]))))
        for s_ in "LR": M.drive_hz[TACT_M[s_]] = 150.0 if (tm == "B" or tm == s_) else 0.0
        t_f = (len(POSE) - CH + f) / fps   # this frame's time (POSE already holds the whole chunk)
        if kind_m[f] == 2 and (kind_m[f - 1] if f > 0 else prev_kind) != 2: tap_t = t_f   # contact onset with her = a tap
        tap_ = TAP_HZ * np.exp(-(t_f - tap_t) * 1000.0 / TAP_MS) if (t_f - tap_t) * 1000.0 < 3 * TAP_MS else 0.0
        M.drive_hz[PPK_F] = tap_; M.drive_hz[PPK_M] = tap_   # her cuticle: both channels burst on the tap, decaying; only contact with HER counts
        if not args.no_female:
            tf = touched_f[f]
            for s_ in "LR": F.drive_hz[TACT_F[s_]] = 150.0 if (tf == "B" or tf == s_) else 0.0
            F.drive_hz[JO] = 100.0 if singing else 0.0
        for _ in range(SPF):
            M.step(); accM[M.last_idx] += 1          # per-cell spike counts for the chunk; groups are summed once per chunk (same numbers, far fewer calls)
            if not args.no_female: F.step(); accF[F.last_idx] += 1
    prev_kind = kind_m[-1]
    for k, r in RM.items(): cntM[k] = int(accM[r].sum())
    if not args.no_female:
        for k, r in RF.items(): cntF[k] = int(accF[r].sum())
    # his steering: DNa02 (vision) + leg asymmetry on touch
    net_ = cntM["DNa02_R"] - cntM["DNa02_L"] - rest_net; ema += (net_ - ema) / 3.0; yaw = float(np.clip(args.gain * ema, -12, 12)) * -1
    asym = (cntM["legMN_R"] - cntM["legMN_L"]) / max(cntM["legMN_R"] + cntM["legMN_L"], 1)
    if any(touched_m): yaw = float(np.clip(leg_gain * (asym - leg_rest), -12, 12))   # bristles pressed: the legs steer, vision is dropped for the chunk
    else: leg_rest += (asym - leg_rest) / 20.0
    mh += yaw
    # pace: speed = v_max * clip((leg MN - standing) / (4 x standing), 0, 1); backward if MDN outfires DNp09 (labelled)
    drive_m = (cntM["legMN"] - leg_stand) / max(4 * leg_stand, 1); v_m = 0.45 * float(np.clip(drive_m, 0, 1)) + 0.05
    # (MDN, the backward-walking driver, fires tonically ~25 Hz per cell under visual drive in this LIF while DNp09 is silent; a reverse rule on it walked him backward all run. no reverse rule. logged for the record.)
    if not args.no_female:
        v_f = 0.15   # she has no nerve cord: constant pace, labelled
    # her steering: DNa02 (whatever it hears) + noise
    if not args.no_female:
        fnet = cntF["DNa02_L"] - cntF["DNa02_R"]; fh += float(np.clip(3.0 * fnet, -12, 12)) + rng.normal(0, 1.5)
        if any(touched_f):   # she has no leg circuits: on contact, turn away from the touched side (labelled stand-in for the reflex he has through his cord)
            side_ = [t_ for t_ in touched_f if t_][-1]; fh += -8.0 if side_ == "L" else (8.0 if side_ == "R" else rng.choice([-8.0, 8.0]))
    # song detection: pIP10 above running mean + 2 sd
    p = cntM["pIP10"]; pip_hist.append(p); mu, sd = (np.mean(pip_hist[:-1]), np.std(pip_hist[:-1]) + 0.5) if len(pip_hist) > 5 else (p, 1e9)
    song = bool(p > mu + 2 * sd); log["song"].append(song and not args.no_female and dist < 0.4); log["dist"].append(dist); log["v_m"].append(v_m); log["v_f"].append(v_f)
    for k in RM: log[f"m_{k}"].append(cntM[k])
    for k in RF: log[f"f_{k}"].append(cntF[k])
    if c % 50 == 49:
        print(f"t={(c+1)/10:5.1f}s  him ({mx:+.2f},{my:+.2f}) {mh:+6.0f}  her ({fx:+.2f},{fy:+.2f})  dist {dist:4.2f}  pC1 {sum(log['m_pC1'][-50:])} pIP10 {sum(log['m_pIP10'][-50:])} LC10a {sum(log['m_LC10a'][-50:])} | her pC1 {sum(log['f_pC1'][-50:]) if not args.no_female else '-'} vpoEN {sum(log['f_vpoEN'][-50:]) if not args.no_female else '-'} | contacts {contacts} songs {sum(log['song'][-50:])} | pace him {np.mean(log['v_m'][-50:]):.2f} her {np.mean(log['v_f'][-50:]):.2f} m/s  ({time.time()-t0:.0f}s)", flush=True)
    LUM.append((np.clip(lum, 0, 1) * 255).astype(np.uint8))
Tn = len(POSE)
np.savez_compressed(args.out, fps=fps, chunk=CH, lum=np.concatenate(LUM), pose=np.array(POSE, np.float32), pose2=np.array(POSE2, np.float32), objects=posts, pillars=True, sky=0.8, ground=0.4, her_albedo=HER_ALB, walls=np.array([WALLS['half'], WALLS['height'], WALLS['albedo']], np.float32), fov=150.0, contacts=contacts,
                    az=np.degrees(np.arctan2(eye.dir0[:, 1], eye.dir0[:, 0])).astype(np.float32), el=np.degrees(np.arcsin(np.clip(eye.dir0[:, 2], -1, 1))).astype(np.float32), side=eye.side,
                    touch=np.array([{"L": 1, "R": 2, "B": 3}.get(t_, 0) for t_ in TOUCH], np.int8), touch_kind=np.array(TKIND, np.int8), body_r=BODY, her_r=HER_R, heading_chunk=np.array([p[2] for p in POSE[::CH]]),
                    **{f"n_{k}": np.repeat(np.array(v, np.int16), CH)[:Tn] for k, v in log.items() if k not in ("dist", "song", "v_m", "v_f")}, v_m=np.repeat(np.array(log["v_m"], np.float32), CH)[:Tn], v_f=np.repeat(np.array(log["v_f"], np.float32), CH)[:Tn], dist=np.repeat(np.array(log["dist"], np.float32), CH)[:Tn], song=np.repeat(np.array(log["song"], np.int8), CH)[:Tn])
print("wrote", args.out, f"contacts {contacts}, song chunks {sum(log['song'])}, mean dist {np.mean(log['dist']):.2f}")
