"""
closedloop.py - the optomotor experiment, closed loop. the fly's own descending neurons turn him.

    uv run python world/closedloop.py --out world/drum0.npz [--gain 0.15] [--readout DNa|DNa02]

apparatus: a striped drum (30 deg period, 60 deg tall band, contrast 0.2/0.8) at infinity
around a fly fixed at the origin; only his heading changes. drum: still 2 s, +30 deg/s
for 4 s, still 1 s, -30 deg/s for 4 s, still 1 s (+ = toward the fly's left, i.e.
counter-clockwise from above).

loop, every CHUNK = 100 ms: render 10 frames of both retinas at the current heading;
flyvis per eye with state carried from the previous chunk; LIF 100 steps with T4/T5
driven (v2 seam, rest from a 1 s still-drum warm-up); count the steering readout
(default: DNa family, right minus left; DNa02 optional); yaw += GAIN * (R - L) deg,
clipped to +-12 deg per chunk (120 deg/s). sign = ipsilateral turning (Rayshubskiy 2020):
right DNa drives a right turn. logs heading, drum angle, counts per chunk.
"""
import os, sys, argparse, time, numpy as np, torch
sys.path.insert(0, "seam"); sys.path.insert(0, "ref/flybrain/scripts")
os.environ.setdefault("FLYVIS_ROOT_DIR", "/home/nate/code/fly-afterlife/flyvis_data")
from omma import Eye, Scene
ap = argparse.ArgumentParser(); ap.add_argument("--out", default="world/drum0.npz"); ap.add_argument("--model", default="flow/0000/000")
ap.add_argument("--gain", type=float, default=0.15, help="deg of yaw per net spike per 100 ms chunk"); ap.add_argument("--readout", default="DNa")
ap.add_argument("--drive-gain", type=float, default=150.0); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--open-loop", action="store_true"); args = ap.parse_args()
fps, CH = 100, 10; g = np.load("seam/eye_geom.npz"); eye = Eye("seam/eye_geom.npz")
drum = dict(period_deg=30.0, phase_deg=0.0, lo=0.2, hi=0.8, half_height_deg=30.0)
prog = [(2.0, 0.0), (4.0, +30.0), (1.0, 0.0), (4.0, -30.0), (1.0, 0.0)]      # (seconds, drum deg/s)
import flyvis
from flyvis import NetworkView
net = NetworkView(args.model).init_network(); net.eval()
lattice = sorted({(u, v) for u in range(-15, 16) for v in range(max(-15, -15 - u), min(15, 15 - u) + 1)}); idx_of = {uv: i for i, uv in enumerate(lattice)}
ntype = net.connectome.nodes.type[:].astype(str); types = ["T4a", "T4b", "T4c", "T4d", "T5a", "T5b", "T5c", "T5d"]
tix = {t: np.flatnonzero(ntype == t) for t in types}
eyemap = {}
for s in "LR":
    k = np.flatnonzero(g["side"] == s); v = np.rint(+g["sx"][k]).astype(int); u = np.rint(-g["sy"][k] - v / 2.0).astype(int)
    col = np.array([idx_of.get((int(a), int(b)), -1) for a, b in zip(u, v)]); ok = col >= 0; eyemap[s] = (k[ok], col[ok])
def flyvis_chunk(lum_chunk, state):
    """lum_chunk (CH, n_cols) -> per-eye per-type activity (CH, 721); carries state per eye."""
    out = {}
    for s in "LR":
        k, col = eyemap[s]; movie = np.full((1, CH, 1, 721), 0.5, np.float32); movie[0, :, 0, col] = lum_chunk[:, k].T
        with torch.no_grad():
            st = net.simulate(torch.tensor(movie, device=flyvis.device), dt=1 / fps, initial_state=state[s], as_states=True)
        state[s] = st[-1]; act = torch.stack([x.nodes.activity[0] for x in st]).cpu().numpy()   # (CH, n_nodes)
        for t in types: out[(s, t)] = act[:, tix[t]]
    return out
from flysim import FlyBrain
b = FlyBrain("brain_whole.npz", seed=args.seed); ty = b.type.astype(str); ns = b.side.astype(str)
cols = np.load("seam/t4t5_columns.npz"); gkey = {(str(s), int(a), int(h)): i for i, (s, a, h) in enumerate(zip(g["side"], g["hex1"], g["hex2"]))}
gi = np.array([gkey[(str(s), int(a), int(h))] for s, a, h in zip(cols["side"], cols["hex1"], cols["hex2"])])
groups = {}
for s in "LR":
    k, col = eyemap[s]; colmap = dict(zip(k.tolist(), col.tolist()))
    for t in types:
        kk = (cols["type"] == t) & (cols["side"] == s); hx = np.array([colmap.get(int(i), -1) for i in gi[kk]]); ok = hx >= 0
        groups[(t, s)] = (cols["idx"][kk][ok], hx[ok])
R = {}
for name, sel in [("HS", np.char.startswith(ty, "HS")), ("DNa02", ty == "DNa02"), ("DNa", np.char.startswith(ty, "DNa")), ("DN", b.sc == "descending_neuron"), ("LPLC2", ty == "LPLC2"), ("GF", ty == "DNp01")]:
    for s in "LR": R[f"{name}_{s}"] = np.flatnonzero(sel & (ns == s))
b.driven[:] = False
for cl in b.SENSORY_CLASSES: b.driven[b.cls == cl] = True
for t, (idx, _) in groups.items(): b.driven[idx] = True
b._driven_idx = np.flatnonzero(b.driven); b.reset(); b.drive_hz[:] = 0; b.g[:] = 0; b.refrac[:] = 0
SPF = int(round(1000 / fps / b.p.dt))
# warm-up: 1 s on the still drum -> flyvis state + rest levels
heading, phase = 0.0, 0.0; state = {"L": None, "R": None}
def render(heading, phase, n):
    sc = Scene(drum=dict(drum, phase_deg=phase)); return np.stack([eye.render(sc, heading_deg=heading) for _ in range(n)])
rest = {}; acc = {}
for c in range(10):
    a = flyvis_chunk(render(heading, phase, CH), state)
    if c >= 5:
        for k_, v_ in a.items(): acc.setdefault(k_, []).append(v_)
rest = {k_: np.concatenate(v_).mean(0) for k_, v_ in acc.items()}
for _ in range(100 * 5):   # LIF warm-up on rest (zero drive)
    b.step()
log = {"t": [], "heading": [], "drum": [], **{k: [] for k in R}}; t = 0.0; t0 = time.time(); nchunks = 0
LUM = []; POSE = []; PHASE = []
for sec, w in prog:
    for c in range(int(sec / (CH / fps))):
        lum = np.zeros((CH, eye.n), np.float32)
        for f in range(CH):
            lum[f] = eye.render(Scene(drum=dict(drum, phase_deg=phase)), heading_deg=heading); POSE.append((0.0, 0.0, heading)); PHASE.append(phase); phase += w / fps
        LUM.append((np.clip(lum, 0, 1) * 255).astype(np.uint8))
        a = flyvis_chunk(lum, state); cnt = {k: 0 for k in R}
        for f in range(CH):
            for (tt, s), (idx, hx) in groups.items(): b.drive_hz[idx] = args.drive_gain * np.clip((a[(s, tt)][f] - rest[(s, tt)])[hx], 0, 1)
            for _ in range(SPF):
                spk = b.step()
                for k, r in R.items(): cnt[k] += int(spk[r].sum())
        net_ = cnt[f"{args.readout}_R"] - cnt[f"{args.readout}_L"]
        if not args.open_loop: heading += float(np.clip(args.gain * net_, -12, 12)) * -1   # right DNa -> right turn = clockwise = negative heading
        t += CH / fps; log["t"].append(t); log["heading"].append(heading); log["drum"].append(phase)
        for k in R: log[k].append(cnt[k])
        nchunks += 1
        if nchunks % 10 == 0: print(f"t={t:5.1f}s drum {w:+5.1f} deg/s  heading {heading:+7.1f}  HS L/R {sum(log['HS_L'][-10:])}/{sum(log['HS_R'][-10:])}  {args.readout} L/R {sum(log[args.readout+'_L'][-10:])}/{sum(log[args.readout+'_R'][-10:])}   ({time.time()-t0:.0f}s)", flush=True)
T = len(POSE); per_frame = {f"n_{k}": np.repeat(np.array(log[k], np.int16), CH)[:T] for k in R}
np.savez_compressed(args.out, fps=fps, chunk=CH, drum_period=drum["period_deg"], drum_lo=drum["lo"], drum_hi=drum["hi"], drum_half_height=drum["half_height_deg"], drum_phase=np.array(PHASE, np.float32), prog=np.array(prog), gain=args.gain, readout=args.readout,
                    lum=np.concatenate(LUM), pose=np.array(POSE, np.float32), objects=np.zeros((0, 4), np.float32), fov=150.0, az=np.degrees(np.arctan2(eye.dir0[:, 1], eye.dir0[:, 0])).astype(np.float32), el=np.degrees(np.arcsin(np.clip(eye.dir0[:, 2], -1, 1))).astype(np.float32), side=eye.side,
                    heading_chunk=np.array(log["heading"]), drum_chunk=np.array(log["drum"]), t_chunk=np.array(log["t"]), **per_frame, **{f"ncells_{k}": len(v) for k, v in R.items()})
print("wrote", args.out)
