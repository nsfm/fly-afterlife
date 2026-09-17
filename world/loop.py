"""
loop.py - the closed loop, generalised. the fly's DNa02 turn him; the world re-renders from where he is.

    uv run python world/loop.py --mode drum|bar|walk|blind --seed 0 --seconds 20 --out world/x.npz [--bar-az 60]

modes
  drum   striped drum, programme as closedloop.py (regression test)
  bar    one dark vertical bar (15 deg wide, +-30 deg tall, 0.2) on an even 0.6 field, fixed in the
         world at --bar-az deg from his initial heading. fixation = his heading turning to put it ahead.
  walk   the arena of posts (episode.py's world, bright ball too). he walks at 0.3 m/s along his
         heading; DNa02 steers. hits (within radius+0.05 of a post) are logged; he passes through.
  blind  as walk but the retina is held at rest (no visual drive): heading noise only. the control.
every 100 ms chunk: render 10 frames of both retinas -> flyvis per eye (state carried) -> LIF
(v2 seam, common rest from a 1 s warm-up on the first frame) -> DNa02 R-L, EMA 3 chunks ->
yaw = 3 deg/spike (right = right turn) clipped +-12 deg/chunk.
"""
import os, sys, argparse, time, numpy as np, torch
sys.path.insert(0, "seam"); sys.path.insert(0, "ref/flybrain/scripts")
os.environ.setdefault("FLYVIS_ROOT_DIR", "/home/nate/code/fly-afterlife/flyvis_data")
from omma import Eye, Scene
ap = argparse.ArgumentParser(); ap.add_argument("--mode", required=True); ap.add_argument("--out", required=True); ap.add_argument("--seconds", type=float, default=20.0)
ap.add_argument("--model", default="flow/0000/000"); ap.add_argument("--gain", type=float, default=3.0); ap.add_argument("--smooth", type=float, default=3.0)
ap.add_argument("--drive-gain", type=float, default=150.0); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--bar-az", type=float, default=60.0)
ap.add_argument("--speed", type=float, default=0.3); ap.add_argument("--tag", default=""); ap.add_argument("--touch", action="store_true", help="posts are solid: on contact he is held at the surface and the leg bristles on the touched side fire (150 Hz) into the LIF"); ap.add_argument("--body", type=float, default=0.05); ap.add_argument("--std", action="store_true", help="short-term synaptic depression in the LIF"); ap.add_argument("--std-scope", default="global", help="global | central (cb_intrinsic + descending presynaptic cells only)"); ap.add_argument("--std-u", type=float, default=0.08); ap.add_argument("--hp", type=int, default=0, help="running-baseline high-pass on the steering signal, in chunks (0 = off)"); ap.add_argument("--yawprefix", default="seam/worldN", help="prefix of the empty/yaw_left/yaw_right renders used for efference + motion calibration (per flyvis model)"); ap.add_argument("--efference", action="store_true", help="efference copy: subtract the wheel response predicted by his own last turn (calibrated open loop on world rotation at 90 deg/s; Kim, Fitzgerald & Maimon 2015)"); ap.add_argument("--brain-gains", default=None, help="world/brain_gains.npz: per-cell input gain (whole-brain hemisphere homeostasis)"); ap.add_argument("--dn-gains", default=None, help="world/dn_gains.json: per-type per-side input scaling on the wheel cells (tracing-asymmetry correction at the source)"); ap.add_argument("--brain", default="brain_whole.npz"); ap.add_argument("--no-vision", action="store_true", help="no flyvis, no T4/T5 drive (a brain without a retinal column map, e.g. the female)"); ap.add_argument("--wsyn", type=float, default=None, help="override mV per synapse (shiu 0.275)"); ap.add_argument("--wheel", default="dna02", help="dna02 | screened (pooled DN types from world/dn_wheel.json; carries vision, odour and touch)"); ap.add_argument("--norm", action="store_true", help="scale each side of the wheel by its own resting rate (plateau warm-up) and steer on the relative asymmetry: yaw = ngain * (L/L_rest - R/R_rest)"); ap.add_argument("--ngain", type=float, default=6.0); ap.add_argument("--norm-ref", default="still", help="still | motion: per-side reference rates from open-loop yaw_left + yaw_right renders (seam/worldN_yaw_*.npz), direction-averaged"); ap.add_argument("--wgain", type=float, default=1.0, help="deg per net pooled spike (L-R), screened wheel"); ap.add_argument("--rest-chunks", type=int, default=20); ap.add_argument("--smell-gain", type=float, default=0.3, help="deg per net DNa spike (L-R), toward the stronger side"); ap.add_argument("--plastic", action="store_true"); ap.add_argument("--reward", action="store_true", help="sugar + PAM dopamine on contact with the A post"); ap.add_argument("--memory-in", default=None); ap.add_argument("--memory-out", default=None); ap.add_argument("--odour-lambda", type=float, default=0.6); ap.add_argument("--no-landmarks", action="store_true"); ap.add_argument("--rest-sub", action="store_true", help="subtract the DNa02 R-L resting offset measured over a 2 s still-world warm-up (with visual drive) at the wheel"); ap.add_argument("--leg-gain", type=float, default=30.0, help="deg per chunk per unit leg-motor asymmetry (R-L)/(R+L), rest asymmetry subtracted; more left-leg drive = right turn"); ap.add_argument("--world-seed", type=int, default=1); args = ap.parse_args()
fps, CH = 100, 10; g = np.load("seam/eye_geom.npz"); eye = Eye("seam/eye_geom.npz"); rng = np.random.default_rng(args.world_seed)
# ---- world
posts = [(x, y, 0.2, 0.05) for x, y in rng.uniform(-2.5, 2.5, size=(8, 2)) if np.hypot(x + 2.0, y) > 0.8]
if args.mode == "forage":
    objects = np.zeros((0, 4), np.float32) if args.no_landmarks else np.array([(-0.5, 1.8, 0.2, 0.05), (-0.5, -1.8, 0.2, 0.05), (1.8, 0.0, 0.2, 0.05)], np.float32)   # visible landmarks only
    SOURCES = {"A": (1.5, 1.2), "B": (1.5, -1.2)}; PATCH = 0.5   # invisible odour patches; A has sugar
    ODOUR = {}
else:
    objects = np.array(posts + [(1.5, 1.0, 0.25, 1.0)], np.float32) if args.mode in ("walk", "blind", "spin") else np.zeros((0, 4), np.float32)
spheres = [(np.array([x, y, 0.5]), r, a) for x, y, r, a in objects]
drum = dict(period_deg=30.0, phase_deg=0.0, lo=0.2, hi=0.8, half_height_deg=30.0)
bar = dict(width_deg=15.0, az_world=args.bar_az, lo=0.2, bg=0.6, half_height_deg=30.0)
def scene_at(t):
    if args.mode == "spin":
        w = 0.0; acc = 0.0
        for sec, rate in [(2, 0), (4, 30), (1, 0), (4, -30), (1, 0)]:
            if t < acc + sec: w = rate; break
            acc += sec
        ph = np.radians(scene_at.phase); c_, s_ = np.cos(ph), np.sin(ph)
        rot = [(np.array([c_ * ox - s_ * oy, s_ * ox + c_ * oy, 0.5]), r_, a_) for ox, oy, r_, a_ in objects]
        return Scene(spheres=rot), w
    if args.mode == "drum":
        w = 0.0; acc = 0.0
        for sec, rate in [(2, 0), (4, 30), (1, 0), (4, -30), (1, 0)]:
            if t < acc + sec: w = rate; break
            acc += sec
        return Scene(drum=dict(drum, phase_deg=scene_at.phase)), w
    if args.mode == "bar":
        # a bar is a drum with one stripe: emulate with a drum of period 360 whose 'lo' stripe is 15 deg wide -> custom
        return Scene(sky=bar["bg"], ground=bar["bg"], horizon_soft=1e-3, spheres=[], drum=dict(period_deg=360.0, phase_deg=bar["az_world"], lo=bar["lo"], hi=bar["bg"], half_height_deg=bar["half_height_deg"], bar_width=bar["width_deg"])), 0.0
    return Scene(spheres=spheres), 0.0
scene_at.phase = 0.0
if args.mode == "forage": args.touch = True
# a narrow bar: patch Scene.shade's drum branch to honour bar_width (stripe only within [phase, phase+width])
import omma
_shade = omma.Scene.shade
def shade_bar(self, origin, d):
    if self.drum is not None and "bar_width" in self.drum:
        dr = self.drum; lum = np.full(len(d), dr["hi"], np.float32); az = np.degrees(np.arctan2(d[:, 1], d[:, 0])); elv = np.degrees(np.arcsin(np.clip(d[:, 2], -1, 1)))
        rel = (az - dr["phase_deg"] + 180.0) % 360.0 - 180.0; inbar = (np.abs(rel) < dr["bar_width"] / 2) & (np.abs(elv) < dr["half_height_deg"])
        return np.where(inbar, dr["lo"], lum).astype(np.float32)
    return _shade(self, origin, d)
omma.Scene.shade = shade_bar
# ---- flyvis
if not args.no_vision:
    import flyvis
    from flyvis import NetworkView
    net = NetworkView(args.model).init_network(); net.eval()
lattice = sorted({(u, v) for u in range(-15, 16) for v in range(max(-15, -15 - u), min(15, 15 - u) + 1)}); idx_of = {uv: i for i, uv in enumerate(lattice)}
types = ["T4a", "T4b", "T4c", "T4d", "T5a", "T5b", "T5c", "T5d"]
if not args.no_vision: ntype = net.connectome.nodes.type[:].astype(str); tix = {t: np.flatnonzero(ntype == t) for t in types}
eyemap = {}
for s in "LR":
    k = np.flatnonzero(g["side"] == s); v = np.rint(+g["sx"][k]).astype(int); u = np.rint(-g["sy"][k] - v / 2.0).astype(int)
    col = np.array([idx_of.get((int(a), int(b)), -1) for a, b in zip(u, v)]); ok = col >= 0; eyemap[s] = (k[ok], col[ok])
state = {"L": None, "R": None}
def flyvis_chunk(lum_chunk):
    out = {}
    if args.no_vision: return out
    for s in "LR":
        k, col = eyemap[s]; movie = np.full((1, CH, 1, 721), 0.5, np.float32); movie[0, :, 0, col] = lum_chunk[:, k].T
        with torch.no_grad(): st = net.simulate(torch.tensor(movie, device=flyvis.device), dt=1 / fps, initial_state=state[s], as_states=True)
        state[s] = st[-1]; act = torch.stack([x.nodes.activity[0] for x in st]).cpu().numpy()
        for t in types: out[(s, t)] = act[:, tix[t]]
    return out
# ---- LIF
import json as _json
from flysim import FlyBrain, Params
b = FlyBrain(args.brain, seed=args.seed, balance_hemispheres=(args.brain == "brain_whole.npz"), params=(Params(mv_per_synapse=args.wsyn) if args.wsyn else None)); ty = b.type.astype(str); ns = b.side.astype(str)
cols = np.load("seam/t4t5_columns.npz"); gkey = {(str(s), int(a), int(h)): i for i, (s, a, h) in enumerate(zip(g["side"], g["hex1"], g["hex2"]))}
gi = np.array([gkey[(str(s), int(a), int(h))] for s, a, h in zip(cols["side"], cols["hex1"], cols["hex2"])])
groups = {}
for s in ([] if args.no_vision else "LR"):
    k, col = eyemap[s]; colmap = dict(zip(k.tolist(), col.tolist()))
    for t in types:
        kk = (cols["type"] == t) & (cols["side"] == s); hx = np.array([colmap.get(int(i), -1) for i in gi[kk]]); ok = hx >= 0; groups[(t, s)] = (cols["idx"][kk][ok], hx[ok])
cls_ = b.cls.astype(str); TACT = {s_: np.flatnonzero((cls_ == "mechanosensory_tactile") & (ns == s_)) for s_ in "LR"}
if args.wheel == "screened":
    WHEEL = _json.load(open("world/dn_wheel.json"))["consistent"]; wtypes = [w["type"] for w in WHEEL]
    R_W = {s_: np.flatnonzero(np.isin(ty, wtypes) & (ns == s_) & (b.sc == "descending_neuron")) for s_ in "LR"}
    print(f"screened wheel: {len(wtypes)} types, {len(R_W['L'])} L + {len(R_W['R'])} R cells: {wtypes}")
R = {}
if args.wheel == "screened": R["W_L"], R["W_R"] = R_W["L"], R_W["R"]
for name, sel in [("HS", np.char.startswith(ty, "HS")), ("DNa02", ty == "DNa02"), ("DNa", np.char.startswith(ty, "DNa")), ("DN", b.sc == "descending_neuron"), ("LPLC2", ty == "LPLC2"), ("GF", ty == "DNp01"), ("legMN", b.sc == "vnc_motor")]:
    for s in "LR": R[f"{name}_{s}"] = np.flatnonzero(sel & (ns == s))
b.driven[:] = False
for cl in b.SENSORY_CLASSES: b.driven[b.cls == cl] = True
for t, (idx, _) in groups.items(): b.driven[idx] = True
b._driven_idx = np.flatnonzero(b.driven); b.reset(); b.drive_hz[:] = 0; b.g[:] = 0; b.refrac[:] = 0; SPF = int(round(1000 / fps / b.p.dt))
if args.brain_gains:
    bg = np.load(args.brain_gains)["gain"]; assert len(bg) == b.N; b._out_w[:] = b._out_w * bg[b._out_tgt]; print(f"brain gains applied: {int((np.abs(bg - 1) > 0.1).sum())} cells changed >10%")
if args.dn_gains:
    _g = _json.load(open(args.dn_gains)); n_e = 0
    for key, gval in _g.items():
        t_, s_ = key.split("|"); cellsK = np.flatnonzero((ty == t_) & (ns == s_) & (b.sc == "descending_neuron")); msk = np.isin(b._out_tgt, cellsK); b._out_w[msk] *= gval; n_e += int(msk.sum())
    print(f"dn gains applied to {n_e} input edges of {len(_g)} (type, side) groups")
if args.std:
    b.p.std_u = args.std_u
    if args.std_scope == "central":
        b.pop["central"] = np.flatnonzero(np.isin(b.sc, ["cb_intrinsic", "descending_neuron", "visual_projection"])); n_ = b.enable_std(("central",))
    else: n_ = b.enable_std(None)
    print(f"STD on ({args.std_scope}, U={args.std_u}):", n_, "presynaptic cells")
if args.mode == "forage":
    b.define_odor("A", n_channels=12, seed=7); b.define_odor("B", n_channels=12, seed=11)
    if args.plastic or args.reward or args.memory_in:
        n_pl = b.enable_plasticity(); b.enable_compartments(); print(f"plasticity on: {n_pl} KC->MBON synapses; PAM types {sorted(t for t in b._da_by_type if t.startswith('PAM'))[:4]}...")
        if args.memory_in:
            mem = np.load(args.memory_in)["w"]; b._out_w[b._plastic] = mem; print(f"memory loaded: mean weight {float(np.mean(mem / np.maximum(b._w0, 1e-9))):.4f} of naive")
    b._driven_idx = np.flatnonzero(b.driven)
# ---- warm-up on the first frame
x, y, heading = (-2.0, 0.0, 0.0) if args.mode in ("walk", "blind") else (0.0, 0.0, 0.0)
def render_frames(n, sc, pos, hd): return np.stack([eye.render(sc, pos=pos, heading_deg=hd) for _ in range(n)])
acc = {}
for c in range(10):
    sc, _ = scene_at(0.0); a = flyvis_chunk(render_frames(CH, sc, (x, y, 0.5), heading))
    if c >= 5:
        for k_, v_ in a.items(): acc.setdefault(k_, []).append(v_)
rest = {k_: np.concatenate(v_).mean(0) for k_, v_ in acc.items()} if acc else {}
for _ in range(500): b.step()
def motion_reference(keyL, keyR):
    """open loop: drive the LIF with the yaw_left and yaw_right renders (1 s each), return per-side mean spikes per chunk over both."""
    restN = np.load("seam/worldN_empty.npz"); tot = {"L": 0, "R": 0}; nch = 0
    for k in ("left", "right"):
        w = np.load(f"seam/worldN_yaw_{k}.npz"); gr = {}
        for s_ in "LR":
            colmap = dict(zip(w[f"{s_}_idx"].tolist(), w[f"{s_}_col"].tolist()))
            for t in types:
                kk = (cols["type"] == t) & (cols["side"] == s_); hx = np.array([colmap.get(int(i), -1) for i in gi[kk]]); ok = hx >= 0
                gr[(t, s_)] = (cols["idx"][kk][ok], hx[ok], w[f"{s_}_{t}"], restN[f"{s_}_{t}"][20:100].mean(0))
        b.reset(); b.drive_hz[:] = 0; b.g[:] = 0; b.refrac[:] = 0
        for f in range(200):
            for (t, s_), (idx, hx, a, r_) in gr.items(): b.drive_hz[idx] = args.drive_gain * np.clip((a[f] - r_)[hx], 0, 1)
            for _ in range(SPF):
                spk = b.step()
                if f >= 100: tot["L"] += int(spk[R[keyL]].sum()); tot["R"] += int(spk[R[keyR]].sum())
            if f >= 100 and f % CH == CH - 1: nch += 1
    b.reset(); b.drive_hz[:] = 0; b.g[:] = 0; b.refrac[:] = 0
    for _ in range(500): b.step()
    return max(tot["L"] / nch, 0.05), max(tot["R"] / nch, 0.05)
def efference_calibration(keyL, keyR):
    """per side: spikes per chunk per (deg/s of world rotation), signed: world moving LEFT positive. from yaw_left/yaw_right renders (90 deg/s)."""
    restN = np.load(f"{args.yawprefix}_empty.npz"); resp = {}
    for k, worldrate in (("right", +90.0), ("left", -90.0)):   # yaw_right render = fly turned right = world moved LEFT
        w = np.load(f"{args.yawprefix}_yaw_{k}.npz"); gr = {}
        for s_ in "LR":
            colmap = dict(zip(w[f"{s_}_idx"].tolist(), w[f"{s_}_col"].tolist()))
            for t in types:
                kk = (cols["type"] == t) & (cols["side"] == s_); hx = np.array([colmap.get(int(i), -1) for i in gi[kk]]); ok = hx >= 0
                gr[(t, s_)] = (cols["idx"][kk][ok], hx[ok], w[f"{s_}_{t}"], restN[f"{s_}_{t}"][20:100].mean(0))
        b.reset(); b.drive_hz[:] = 0; b.g[:] = 0; b.refrac[:] = 0; cl_ = cr_ = 0; pl = pr = 0
        for f in range(200):
            for (t, s_), (idx, hx, a, r_) in gr.items(): b.drive_hz[idx] = args.drive_gain * np.clip((a[f] - r_)[hx], 0, 1)
            for _ in range(SPF):
                spk = b.step(); L_ = int(spk[R[keyL]].sum()); R_ = int(spk[R[keyR]].sum())
                if f >= 100: cl_ += L_; cr_ += R_
                elif f >= 20: pl += L_; pr += R_
        resp[worldrate] = ((cl_ - pl * 100 / 80) / 10, (cr_ - pr * 100 / 80) / 10)   # per chunk, above the still pre-period
    b.reset(); b.drive_hz[:] = 0; b.g[:] = 0; b.refrac[:] = 0
    for _ in range(500): b.step()
    kL = (resp[90.0][0] - resp[-90.0][0]) / 180.0; kR = (resp[90.0][1] - resp[-90.0][1]) / 180.0
    print(f"efference calibration: world LEFT 90 deg/s -> L {resp[90.0][0]:+.2f} R {resp[90.0][1]:+.2f} per chunk; world RIGHT -> L {resp[-90.0][0]:+.2f} R {resp[-90.0][1]:+.2f}; slope per deg/s: L {kL:+.4f} R {kR:+.4f}")
    return kL, kR
leg_rest = 0.0; rest_net = 0.0; dna_rest = 0.0
if args.mode == "forage":
    sc0, _ = scene_at(0.0); dl = dr_ = 0; nch = 20
    for c in range(nch):
        a0 = flyvis_chunk(render_frames(CH, sc0, (x, y, 0.5), heading))
        for f in range(CH):
            for (tt, s_), (idx, hx) in groups.items(): b.drive_hz[idx] = args.drive_gain * np.clip((a0[(s_, tt)][f] - rest[(s_, tt)])[hx], 0, 1)
            for _ in range(SPF):
                spk = b.step(); dl += int(spk[R["DNa_L"]].sum()); dr_ += int(spk[R["DNa_R"]].sum())
    dna_rest = (dl - dr_) / nch; print(f"DNa offset with vision on, no odour (L-R per chunk): {dna_rest:+.2f}")
if args.rest_sub:
    sc0, _ = scene_at(0.0); rl = rr = 0; nch = args.rest_chunks
    for c in range(nch):
        a0 = flyvis_chunk(render_frames(CH, sc0, (x, y, 0.5), heading))
        for f in range(CH):
            for (tt, s_), (idx, hx) in groups.items(): b.drive_hz[idx] = args.drive_gain * np.clip((a0[(s_, tt)][f] - rest[(s_, tt)])[hx], 0, 1)
            for _ in range(SPF):
                spk = b.step(); rl += int(spk[R["DNa02_L"]].sum()); rr += int(spk[R["DNa02_R"]].sum())
    rest_net = (rr - rl) / nch; dL_rest, dR_rest = max(rl / nch, 0.05), max(rr / nch, 0.05); print(f"DNa02 resting offset (R-L per chunk): {rest_net:+.2f}  (L {rl}, R {rr} over {nch} chunks)")
    if args.norm_ref == "motion": dL_rest, dR_rest = motion_reference("DNa02_L", "DNa02_R"); print(f"DNa02 MOTION reference per chunk: L {dL_rest:.2f} R {dR_rest:.2f}")
    if args.efference: eff_kL, eff_kR = efference_calibration("DNa02_L", "DNa02_R")
w_rest = 0.0; eff_kL = eff_kR = 0.0; last_yaw_rate = 0.0
if args.wheel == "screened":
    sc0, _ = scene_at(0.0); wl = wr = 0; nch = args.rest_chunks
    for c in range(nch):
        a0 = flyvis_chunk(render_frames(CH, sc0, (x, y, 0.5), heading))
        for f in range(CH):
            for (tt, s_), (idx, hx) in groups.items(): b.drive_hz[idx] = args.drive_gain * np.clip((a0[(s_, tt)][f] - rest[(s_, tt)])[hx], 0, 1)
            for _ in range(SPF):
                spk = b.step(); wl += int(spk[R["W_L"]].sum()); wr += int(spk[R["W_R"]].sum())
    w_rest = (wl - wr) / nch; wL_rest, wR_rest = max(wl / nch, 0.05), max(wr / nch, 0.05); print(f"screened wheel resting offset (L-R per chunk, vision on): {w_rest:+.2f}  ({wl} / {wr} over {nch} chunks)")
    if args.norm_ref == "motion": wL_rest, wR_rest = motion_reference("W_L", "W_R"); print(f"screened wheel MOTION reference per chunk: L {wL_rest:.2f} R {wR_rest:.2f}")
    if args.efference: eff_kL, eff_kR = efference_calibration("W_L", "W_R")
# ---- loop
T = int(args.seconds * fps); LUM, POSE, PHASE, TOUCH, SMELL, REWARD = [], [], [], [], [], []; n_reward_frames = 0; A_contacts = B_contacts = 0; log = {k: [] for k in R}; hits = 0; ema = 0.0; hp_base = 0.0; t0 = time.time(); bearing = []
for c in range(T // CH):
    t = c * CH / fps; sc, w = scene_at(t); lum = np.zeros((CH, eye.n), np.float32)
    for f in range(CH):
        if args.mode == "drum": scene_at.phase += w / fps; sc = Scene(drum=dict(drum, phase_deg=scene_at.phase))
        if args.mode == "spin": scene_at.phase += w / fps; sc, _ = scene_at(t)
        lum[f] = eye.render(sc, pos=(x, y, 0.5), heading_deg=heading) if args.mode != "blind" else np.full(eye.n, 0.5, np.float32)
        POSE.append((x, y, heading)); PHASE.append(scene_at.phase if args.mode in ("drum", "spin") else (bar["az_world"] if args.mode == "bar" else 0.0))
        if args.mode in ("walk", "blind", "forage"):
            x += args.speed / fps * np.cos(np.radians(heading)); y += args.speed / fps * np.sin(np.radians(heading))
            touched = None
            touching_index = -1
            for oi_, (ox, oy, r_, _) in enumerate(objects):
                dd = np.hypot(x - ox, y - oy)
                if dd < r_ + args.body:
                    hits += 1; touching_index = oi_
                    if args.touch:
                        x, y = ox + (x - ox) / max(dd, 1e-6) * (r_ + args.body), oy + (y - oy) / max(dd, 1e-6) * (r_ + args.body)   # held at the surface
                        brg = (np.degrees(np.arctan2(oy - y, ox - x)) - heading + 180) % 360 - 180
                        touched = "L" if brg > 8 else ("R" if brg < -8 else "B")
                    break
            TOUCH.append(touched)
            if args.mode == "forage":
                hr_ = np.radians(heading); fwd = np.array([np.cos(hr_), np.sin(hr_)]); left = np.array([-np.sin(hr_), np.cos(hr_)])
                antL = np.array([x, y]) + 0.1 * fwd + 0.15 * left; antR = np.array([x, y]) + 0.1 * fwd - 0.15 * left
                cl, cr = {}, {}
                for name, (ox, oy) in SOURCES.items():
                    cl[name] = float(np.exp(-np.hypot(*(antL - [ox, oy])) / args.odour_lambda)); cr[name] = float(np.exp(-np.hypot(*(antR - [ox, oy])) / args.odour_lambda))
                SMELL.append((cl, cr))
                inA = np.hypot(x - SOURCES["A"][0], y - SOURCES["A"][1]) < PATCH; inB = np.hypot(x - SOURCES["B"][0], y - SOURCES["B"][1]) < PATCH
                A_contacts += inA; B_contacts += inB
                REWARD.append(bool(inA) and args.reward)
    LUM.append((np.clip(lum, 0, 1) * 255).astype(np.uint8))
    a = flyvis_chunk(lum) if args.mode != "blind" else None; cnt = {k: 0 for k in R}
    for f in range(CH):
        if a is not None:
            for (tt, s), (idx, hx) in groups.items(): b.drive_hz[idx] = args.drive_gain * np.clip((a[(s, tt)][f] - rest[(s, tt)])[hx], 0, 1)
        if args.touch:
            tch = TOUCH[c * CH + f] if c * CH + f < len(TOUCH) else None
            for s_ in "LR": b.drive_hz[TACT[s_]] = 150.0 if (tch == "B" or tch == s_) else 0.0
        if args.mode == "forage":
            fi = c * CH + f
            if fi < len(SMELL): cl, cr = SMELL[fi]; b.smell_bilateral(left=cl, right=cr)
            rw = fi < len(REWARD) and REWARD[fi]
            if rw:
                b.taste(1.0); n_reward_frames += 1
                for tname in getattr(b, "_da_by_type", {}):
                    if tname.startswith("PAM"): b.stimulate_type(tname, 200.0, mv=45.0)
            else:
                b.taste(0.0); b.drive_hz[b.pop["gustatory"]] = 0.0
                for tname in getattr(b, "_da_by_type", {}):
                    if tname.startswith("PAM"): b.stimulate_type(tname, 0.0)
        for _ in range(SPF):
            spk = b.step()
            for k, r in R.items(): cnt[k] += int(spk[r].sum())
    if args.efference:
        world_rate_from_self = -last_yaw_rate                       # deg/s; his left turn = world moving right
        predL, predR = eff_kL * world_rate_from_self, eff_kR * world_rate_from_self
        for kL_, kR_ in ((("W_L", "W_R") if args.wheel == "screened" else ("DNa02_L", "DNa02_R")),):
            cnt[kL_] = max(cnt[kL_] - predL, 0.0); cnt[kR_] = max(cnt[kR_] - predR, 0.0)
    if args.wheel == "screened":
        if args.norm: net_ = cnt["W_L"] / wL_rest - cnt["W_R"] / wR_rest; gain_ = args.ngain
        else: net_ = (cnt["W_L"] - cnt["W_R"]) - w_rest; gain_ = args.wgain
        if args.hp: hp_base += (net_ - hp_base) / args.hp; net_ = net_ - hp_base
        ema += (net_ - ema) / max(args.smooth, 1.0)
        yaw = float(np.clip(gain_ * ema, -12, 12))          # more on the left -> left turn
    else:
        if args.norm and args.rest_sub: net_ = cnt["DNa02_L"] / dL_rest - cnt["DNa02_R"] / dR_rest; ema += (net_ - ema) / max(args.smooth, 1.0); yaw = float(np.clip(args.ngain * ema, -12, 12))
        else:
            net_ = cnt["DNa02_R"] - cnt["DNa02_L"] - rest_net; ema += (net_ - ema) / max(args.smooth, 1.0)
            yaw = float(np.clip(args.gain * ema, -12, 12)) * -1
    if args.mode == "forage" and args.wheel != "screened":
        fi = min(c * CH + CH - 1, len(SMELL) - 1); cl, cr = SMELL[fi]; presence = min(1.0, sum(cl.values()) + sum(cr.values()))
        dna_net = (cnt["DNa_L"] - cnt["DNa_R"]) - dna_rest
        if presence < 0.05: dna_rest += 0.02 * dna_net                      # slow drift tracking when nothing is in the air
        yaw += float(np.clip(args.smell_gain * presence * dna_net, -12, 12))   # more left DNa -> left turn (toward the stronger side)
    if args.touch and args.wheel != "screened":
        asym = (cnt["legMN_R"] - cnt["legMN_L"]) / max(cnt["legMN_R"] + cnt["legMN_L"], 1)
        touched_chunk = any(TOUCH[c * CH + f] for f in range(CH) if c * CH + f < len(TOUCH))
        if not touched_chunk: leg_rest += (asym - leg_rest) / 20.0          # running baseline from untouched chunks
        else: yaw += float(np.clip(args.leg_gain * (asym - leg_rest), -12, 12))   # more right-leg drive -> left turn (+heading); only while touching
    heading += yaw; last_yaw_rate = yaw * fps / CH
    for k in R: log[k].append(cnt[k])
    if args.mode == "bar": bearing.append(((bar["az_world"] - heading + 180) % 360) - 180)
    if args.mode == "forage" and c % 50 == 49: print(f"   smell A L/R {SMELL[-1][0][chr(65)]:.2f}/{SMELL[-1][1][chr(65)]:.2f} B {SMELL[-1][0][chr(66)]:.2f}/{SMELL[-1][1][chr(66)]:.2f}  reward frames {n_reward_frames}  mem {b.learn() if getattr(b, chr(112)+chr(108)+chr(97)+chr(115)+chr(116)+chr(105)+chr(99)+chr(95)+chr(111)+chr(110), False) else 1.0:.4f}", flush=True)
    if c % 50 == 49: print(f"t={t+0.1:5.1f}s heading {heading:+7.1f}" + (f"  wheel L/R {sum(log[chr(87)+chr(95)+chr(76)][-50:])}/{sum(log[chr(87)+chr(95)+chr(82)][-50:])}" if args.wheel == "screened" else "") + (f"  touches L/R/both {TOUCH.count(chr(76))}/{TOUCH.count(chr(82))}/{TOUCH.count(chr(66))}" if args.touch else "") + (f"  bar bearing {bearing[-1]:+6.1f}" if bearing else "") + (f"  pos ({x:+.2f},{y:+.2f}) hits {hits}" if args.mode in ('walk', 'blind') else "") + f"  DNa02 L/R {sum(log['DNa02_L'][-50:])}/{sum(log['DNa02_R'][-50:])}  ({time.time()-t0:.0f}s)", flush=True)
Tn = len(POSE); per_frame = {f"n_{k}": np.repeat(np.array(log[k], np.int16), CH)[:Tn] for k in R}
extra = {}
if args.mode == "drum": extra = dict(drum_period=drum["period_deg"], drum_lo=drum["lo"], drum_hi=drum["hi"], drum_half_height=drum["half_height_deg"], drum_phase=np.array(PHASE, np.float32))
if args.mode == "bar": extra = dict(bar_width=bar["width_deg"], bar_lo=bar["lo"], bar_bg=bar["bg"], bar_half_height=bar["half_height_deg"], bar_az=np.array(PHASE, np.float32), bearing=np.array(bearing, np.float32))
if args.memory_out and getattr(b, "plastic_on", False): np.savez(args.memory_out, w=b._out_w[b._plastic], w0=b._w0); print("memory saved", args.memory_out)
if args.mode == "forage":
    p_ = np.array(POSE); dA = np.hypot(p_[:, 0] - SOURCES["A"][0], p_[:, 1] - SOURCES["A"][1]); dB = np.hypot(p_[:, 0] - SOURCES["B"][0], p_[:, 1] - SOURCES["B"][1])
    fa = int(np.argmax(dA < PATCH)) if (dA < PATCH).any() else -1; fb = int(np.argmax(dB < PATCH)) if (dB < PATCH).any() else -1
    print(f"FORAGE: frames in A patch {A_contacts}, in B patch {B_contacts}; first arrival A {fa/fps if fa>=0 else None} s, B {fb/fps if fb>=0 else None} s; min dist A {dA.min():.2f} B {dB.min():.2f}; reward frames {n_reward_frames}")
touch_side = np.array([{"L": 1, "R": 2, "B": 3}.get(t_, 0) for t_ in TOUCH], np.int8) if TOUCH else np.zeros(0, np.int8)
np.savez_compressed(args.out, fps=fps, chunk=CH, mode=args.mode, touch=touch_side, sources=np.array([[*SOURCES["A"], PATCH], [*SOURCES["B"], PATCH]], np.float32) if args.mode == "forage" else np.zeros((0, 3), np.float32), a_frames=A_contacts if args.mode == "forage" else 0, b_frames=B_contacts if args.mode == "forage" else 0, lum=np.concatenate(LUM), pose=np.array(POSE, np.float32), objects=objects, fov=150.0, hits=hits,
                    az=np.degrees(np.arctan2(eye.dir0[:, 1], eye.dir0[:, 0])).astype(np.float32), el=np.degrees(np.arcsin(np.clip(eye.dir0[:, 2], -1, 1))).astype(np.float32), side=eye.side,
                    heading_chunk=np.array([p[2] for p in POSE[::CH]]), **per_frame, **{f"ncells_{k}": len(v) for k, v in R.items()}, **extra)
print("wrote", args.out, f"hits={hits}" if args.mode in ("walk", "blind") else "")
