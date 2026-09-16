"""
neural.py - run an episode's retinal luminance through flyvis (per eye) and the LIF; per-frame readouts.

    uv run python world/neural.py --ep world/ep0.npz --out world/ep0_neural.npz [--model flow/0000/000]

open loop: the whole episode is one flyvis movie per eye (state carried inside simulate),
then the LIF runs the whole episode with the v2 seam (T4/T5 drive, common rest = 1 s of
the fly standing still on frame 0... here: rest = mean of frames 20-100 which is the
first straight segment; labelled).
"""
import os, sys, argparse, time, numpy as np, torch
sys.path.insert(0, "seam"); sys.path.insert(0, "ref/flybrain/scripts")
os.environ.setdefault("FLYVIS_ROOT_DIR", "/home/nate/code/fly-afterlife/flyvis_data")
ap = argparse.ArgumentParser(); ap.add_argument("--ep", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--model", default="flow/0000/000"); ap.add_argument("--gain", type=float, default=150.0); ap.add_argument("--a-ref", type=float, default=1.0)
ap.add_argument("--seed", type=int, default=0); args = ap.parse_args()
ep = np.load(args.ep); lum = ep["lum"]; fps = int(ep["fps"]); T = len(lum); g = np.load("seam/eye_geom.npz")
import flyvis
from flyvis import NetworkView
net = NetworkView(args.model).init_network(); net.eval()
lattice = sorted({(u, v) for u in range(-15, 16) for v in range(max(-15, -15 - u), min(15, 15 - u) + 1)}); idx_of = {uv: i for i, uv in enumerate(lattice)}
types = ["T4a", "T4b", "T4c", "T4d", "T5a", "T5b", "T5c", "T5d"]; act = {}
t0 = time.time()
for s in "LR":
    k = np.flatnonzero(g["side"] == s); v = np.rint(+g["sx"][k]).astype(int); u = np.rint(-g["sy"][k] - v / 2.0).astype(int)
    col = np.array([idx_of.get((int(a), int(b)), -1) for a, b in zip(u, v)]); ok = col >= 0
    movie = np.full((1, T, 1, 721), 0.5, np.float32); movie[0, :, 0, col[ok]] = lum[:, k[ok]].T
    with torch.no_grad(): la = net.simulate(torch.tensor(movie, device=flyvis.device), dt=1 / fps, as_layer_activity=True)
    for t in types: act[(s, t)] = np.asarray(getattr(la, t).squeeze(0), dtype=np.float32)
    act[(s, "idx")] = k; act[(s, "col")] = col
print(f"flyvis {T} frames x 2 eyes in {time.time()-t0:.1f}s")
# LIF
from flysim import FlyBrain
b = FlyBrain("brain_whole.npz", seed=args.seed); ty = b.type.astype(str); ns = b.side.astype(str)
cols = np.load("seam/t4t5_columns.npz"); gkey = {(str(s), int(a), int(h)): i for i, (s, a, h) in enumerate(zip(g["side"], g["hex1"], g["hex2"]))}
gi = np.array([gkey[(str(s), int(a), int(h))] for s, a, h in zip(cols["side"], cols["hex1"], cols["hex2"])])
groups = {}
for s in "LR":
    colmap = dict(zip(act[(s, "idx")].tolist(), act[(s, "col")].tolist()))
    for t in types:
        kk = (cols["type"] == t) & (cols["side"] == s); hx = np.array([colmap.get(int(i), -1) for i in gi[kk]]); ok = hx >= 0
        a = act[(s, t)]; groups[(t, s)] = (cols["idx"][kk][ok], hx[ok], a, a[20:100].mean(0))
R = {}
for name, sel in [("HS", np.char.startswith(ty, "HS")), ("VS", np.char.startswith(ty, "VS")), ("LPLC2", ty == "LPLC2"), ("DNa02", ty == "DNa02"), ("DNa", np.char.startswith(ty, "DNa")), ("DN", b.sc == "descending_neuron"), ("GF", ty == "DNp01")]:
    for s in "LR": R[f"{name}_{s}"] = np.flatnonzero(sel & (ns == s))
b.driven[:] = False
for cl in b.SENSORY_CLASSES: b.driven[b.cls == cl] = True
for t, (idx, _, _, _) in groups.items(): b.driven[idx] = True
b._driven_idx = np.flatnonzero(b.driven); b.reset(); b.drive_hz[:] = 0; b.g[:] = 0; b.refrac[:] = 0
SPF = int(round(1000 / fps / b.p.dt)); counts = {k: np.zeros(T, np.int16) for k in R}; t0 = time.time()
for f in range(T):
    for (t, s), (idx, hx, a, rest) in groups.items(): b.drive_hz[idx] = args.gain * np.clip((a[f] - rest)[hx] / args.a_ref, 0, 1)
    for _ in range(SPF):
        spk = b.step()
        for k, r in R.items(): counts[k][f] += int(spk[r].sum())
print(f"LIF {T} frames in {time.time()-t0:.1f}s")
np.savez_compressed(args.out, fps=fps, **{f"n_{k}": v for k, v in counts.items()}, **{f"ncells_{k}": len(v) for k, v in R.items()})
for k in ["HS_L", "HS_R", "DNa02_L", "DNa02_R", "LPLC2_L", "LPLC2_R", "GF_L", "GF_R"]:
    c = counts[k]; print(f"  {k:8s} total {int(c.sum()):6d}   per second: " + " ".join(f"{int(c[i:i+fps].sum()):5d}" for i in range(0, T, fps)))
