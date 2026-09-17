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
steering: his DNa02 (vision; efference off; rest-sub), his leg-asymmetry on touch; hers DNa02 + heading noise
  (sd 15 deg/s). both walk at 0.3 / 0.15 m/s. readouts per chunk: his pC1 (all P1 types), pIP10, mAL, LC10a,
  DNa02 L/R; her pC1a-e, vpoEN, ORN_DA1, DNa02 L/R; distance, contacts, song bouts.
"""
import os, sys, argparse, time, numpy as np, torch
sys.path.insert(0, "seam"); sys.path.insert(0, "ref/flybrain/scripts")
os.environ.setdefault("FLYVIS_ROOT_DIR", "/home/nate/code/fly-afterlife/flyvis_data")
from omma import Eye, Scene
from flysim import FlyBrain, Params
ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--seconds", type=float, default=30.0); ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--model", default="flow/0000/000"); ap.add_argument("--no-female", action="store_true"); ap.add_argument("--gain", type=float, default=3.0); ap.add_argument("--drive-gain", type=float, default=150.0)
args = ap.parse_args(); fps, CH = 100, 10; rng = np.random.default_rng(args.seed)
g = np.load("seam/eye_geom.npz"); eye = Eye("seam/eye_geom.npz")
posts = np.array([(0.0, 1.6, 0.2, 0.05), (0.0, -1.6, 0.2, 0.05)], np.float32)
# ---- flyvis (his eye)
import flyvis
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
M = FlyBrain("brain_whole.npz", seed=args.seed); mty = M.type.astype(str); mns = M.side.astype(str); mcls = M.cls.astype(str)
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
M.define_odor("flyodour", n_channels=1, seed=0); M._odor_map["flyodour"] = {"ORN_VA1v": 1.0, "ORN_VA1d": 0.6}
M.driven[:] = False
for cl in M.SENSORY_CLASSES: M.driven[M.cls == cl] = True
for t, (idx, _) in groups.items(): M.driven[idx] = True
M._driven_idx = np.flatnonzero(M.driven); M.reset(); SPF = int(round(1000 / fps / M.p.dt))
# ---- her brain
RF = {}
if not args.no_female:
    F = FlyBrain("brain_female2.npz", seed=args.seed + 100, balance_hemispheres=False, params=Params(mv_per_synapse=0.5)); fty = F.type.astype(str); fns = F.side.astype(str); fcls = F.cls.astype(str)
    RF = {}
    for name, sel in [("DNa02", fty == "DNa02"), ("pC1", np.char.startswith(fty, "pC1")), ("vpoEN", fty == "vpoEN"), ("ORN_DA1", fty == "ORN_DA1"), ("JO", np.char.startswith(fty, "JO")), ("DN", F.sc == "descending_neuron")]:
        for s in "LR": RF[f"{name}_{s}"] = np.flatnonzero(sel & (fns == s))
        RF[name] = np.flatnonzero(sel)
    JO = RF["JO"]; TACT_F = {s_: np.flatnonzero((fcls == "mechanosensory") & ~np.char.startswith(fty, "JO") & (fns == s_)) for s_ in "LR"}
    F.define_odor("cVA", n_channels=1, seed=0); F._odor_map["cVA"] = {"ORN_DA1": 1.0}
    F.driven[:] = False
    for cl in F.SENSORY_CLASSES: F.driven[F.cls == cl] = True
    F._driven_idx = np.flatnonzero(F.driven); F.reset()
    print(f"her readouts: pC1 {len(RF['pC1'])}, vpoEN {len(RF['vpoEN'])}, ORN_DA1 {len(RF['ORN_DA1'])}, JO {len(JO)}, DNa02 {len(RF['DNa02_L'])}/{len(RF['DNa02_R'])}")
print(f"his readouts: pC1 {len(RM['pC1'])}, pIP10 {len(RM['pIP10'])}, mAL {len(RM['mAL'])}, LC10a {len(RM['LC10a'])}, ORN_VA1v {len(RM['ORN_VA1v_L'])}/{len(RM['ORN_VA1v_R'])}")
# ---- world state
mx, my, mh = -1.2, 0.0, 0.0; fx, fy, fh = 1.2, 0.3, 180.0; LAM = 0.8; BODY = 0.05
def scene_now():
    sph = [(np.array([x, y, 0.5]), r, a) for x, y, r, a in posts]
    if not args.no_female: sph.append((np.array([fx, fy, 0.5]), 0.15, 0.1))
    return Scene(spheres=sph)
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
# ---- loop
T = int(args.seconds * fps); LUM, POSE, POSE2, TOUCH, SONG = [], [], [], [], []; log = {f"m_{k}": [] for k in RM} | ({f"f_{k}": [] for k in RF} if not args.no_female else {}) | {"dist": [], "song": []}
ema = 0.0; leg_rest = 0.0; pip_hist = []; contacts = 0; t0 = time.time()
for c in range(T // CH):
    lum = np.zeros((CH, eye.n), np.float32); touched_m = [None] * CH; touched_f = [None] * CH
    for f in range(CH):
        sc = scene_now(); lum[f] = eye.render(sc, pos=(mx, my, 0.5), heading_deg=mh); POSE.append((mx, my, mh)); POSE2.append((fx, fy, fh))
        # move
        mx += 0.3 / fps * np.cos(np.radians(mh)); my += 0.3 / fps * np.sin(np.radians(mh))
        if not args.no_female: fx += 0.15 / fps * np.cos(np.radians(fh)); fy += 0.15 / fps * np.sin(np.radians(fh))
        # walls (4 x 4 m): reflect heading
        for (px_, py_, hh_, who) in ((mx, my, mh, "m"), (fx, fy, fh, "f")):
            pass
        if abs(mx) > 2: mh = 180 - mh; mx = np.clip(mx, -2, 2)
        if abs(my) > 2: mh = -mh; my = np.clip(my, -2, 2)
        if abs(fx) > 2: fh = 180 - fh; fx = np.clip(fx, -2, 2)
        if abs(fy) > 2: fh = -fh; fy = np.clip(fy, -2, 2)
        # contacts: posts for him; each other
        for ox, oy, r_, _ in posts:
            dd = np.hypot(mx - ox, my - oy)
            if dd < r_ + BODY:
                mx, my = ox + (mx - ox) / max(dd, 1e-6) * (r_ + BODY), oy + (my - oy) / max(dd, 1e-6) * (r_ + BODY)
                brg = (np.degrees(np.arctan2(oy - my, ox - mx)) - mh + 180) % 360 - 180; touched_m[f] = "L" if brg > 8 else ("R" if brg < -8 else "B")
        if not args.no_female:
            dd = np.hypot(mx - fx, my - fy)
            if dd < 2 * BODY + 0.1:
                contacts += 1; brg = (np.degrees(np.arctan2(fy - my, fx - mx)) - mh + 180) % 360 - 180; touched_m[f] = "L" if brg > 8 else ("R" if brg < -8 else "B")
                brg2 = (np.degrees(np.arctan2(my - fy, mx - fx)) - fh + 180) % 360 - 180; touched_f[f] = "L" if brg2 > 8 else ("R" if brg2 < -8 else "B")
        TOUCH.append(touched_m[f])
    a = flyvis_chunk(lum); cntM = {k: 0 for k in RM}; cntF = {k: 0 for k in RF} if not args.no_female else {}
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
        for s_ in "LR": M.drive_hz[TACT_M[s_]] = 150.0 if (tm == "B" or tm == s_) else 0.0
        if not args.no_female:
            tf = touched_f[f]
            for s_ in "LR": F.drive_hz[TACT_F[s_]] = 150.0 if (tf == "B" or tf == s_) else 0.0
            F.drive_hz[JO] = 100.0 if singing else 0.0
        for _ in range(SPF):
            spk = M.step()
            for k, r in RM.items(): cntM[k] += int(spk[r].sum())
            if not args.no_female:
                spf = F.step()
                for k, r in RF.items(): cntF[k] += int(spf[r].sum())
    # his steering: DNa02 (vision) + leg asymmetry on touch
    net_ = cntM["DNa02_R"] - cntM["DNa02_L"] - rest_net; ema += (net_ - ema) / 3.0; yaw = float(np.clip(args.gain * ema, -12, 12)) * -1
    asym = (cntM["legMN_R"] - cntM["legMN_L"]) / max(cntM["legMN_R"] + cntM["legMN_L"], 1)
    if any(touched_m): yaw += float(np.clip(30.0 * (asym - leg_rest), -12, 12))
    else: leg_rest += (asym - leg_rest) / 20.0
    mh += yaw
    # her steering: DNa02 (whatever it hears) + noise
    if not args.no_female:
        fnet = cntF["DNa02_L"] - cntF["DNa02_R"]; fh += float(np.clip(3.0 * fnet, -12, 12)) + rng.normal(0, 1.5)
    # song detection: pIP10 above running mean + 2 sd
    p = cntM["pIP10"]; pip_hist.append(p); mu, sd = (np.mean(pip_hist[:-1]), np.std(pip_hist[:-1]) + 0.5) if len(pip_hist) > 5 else (p, 1e9)
    song = bool(p > mu + 2 * sd); log["song"].append(song and not args.no_female and dist < 0.4); log["dist"].append(dist)
    for k in RM: log[f"m_{k}"].append(cntM[k])
    for k in RF: log[f"f_{k}"].append(cntF[k])
    if c % 50 == 49:
        print(f"t={(c+1)/10:5.1f}s  him ({mx:+.2f},{my:+.2f}) {mh:+6.0f}  her ({fx:+.2f},{fy:+.2f})  dist {dist:4.2f}  pC1 {sum(log['m_pC1'][-50:])} pIP10 {sum(log['m_pIP10'][-50:])} LC10a {sum(log['m_LC10a'][-50:])} | her pC1 {sum(log['f_pC1'][-50:]) if not args.no_female else '-'} vpoEN {sum(log['f_vpoEN'][-50:]) if not args.no_female else '-'} | contacts {contacts} songs {sum(log['song'][-50:])}  ({time.time()-t0:.0f}s)", flush=True)
    LUM.append((np.clip(lum, 0, 1) * 255).astype(np.uint8))
Tn = len(POSE)
np.savez_compressed(args.out, fps=fps, chunk=CH, lum=np.concatenate(LUM), pose=np.array(POSE, np.float32), pose2=np.array(POSE2, np.float32), objects=posts, fov=150.0, contacts=contacts,
                    az=np.degrees(np.arctan2(eye.dir0[:, 1], eye.dir0[:, 0])).astype(np.float32), el=np.degrees(np.arcsin(np.clip(eye.dir0[:, 2], -1, 1))).astype(np.float32), side=eye.side,
                    touch=np.array([{"L": 1, "R": 2, "B": 3}.get(t_, 0) for t_ in TOUCH], np.int8), heading_chunk=np.array([p[2] for p in POSE[::CH]]),
                    **{f"n_{k}": np.repeat(np.array(v, np.int16), CH)[:Tn] for k, v in log.items() if k not in ("dist", "song")}, dist=np.repeat(np.array(log["dist"], np.float32), CH)[:Tn], song=np.repeat(np.array(log["song"], np.int8), CH)[:Tn])
print("wrote", args.out, f"contacts {contacts}, song chunks {sum(log['song'])}, mean dist {np.mean(log['dist']):.2f}")
