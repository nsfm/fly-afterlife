"""
run_flyvis.py - render stimuli onto the flyvis retina, run one pretrained model,
save per-column T4/T5 activity with each column's (u, v) for the seam.

Stimuli (200x200 px, 100 fps, 1.5 s, grey 0.5 background):
  loom     dark disc at centre, radius 2 -> 62 px over the last 1.0 s
  recede   same disc played backwards (contraction)
  translate dark disc radius 20 px sweeping left->right over the last 1.0 s
  static   dark disc radius 30 px appears at 0.5 s and stays
Writes seam/flyvis_out.npz: {stim}_{type}: (T, 721) float32; u, v: (721,) ints; fps
"""
import os, time, numpy as np, torch
os.environ.setdefault("FLYVIS_ROOT_DIR", "/home/nate/code/fly-afterlife/flyvis_data")
import flyvis
from flyvis import NetworkView
from flyvis.datasets.rendering.eye import BoxEye

H = W = 200; fps = 100; T = 150
yy, xx = np.mgrid[0:H, 0:W]; cy = cx = H / 2
def disc(frames, t, r, x=None, y=None):
    x = cx if x is None else x; y = cy if y is None else y
    frames[t][(yy - y) ** 2 + (xx - x) ** 2 < r * r] = 0.0
stims = {}
f = np.full((T, H, W), 0.5, np.float32)
for t in range(50, T): disc(f, t, 2 + (t - 50) * 0.6)
stims["loom"] = f
stims["recede"] = np.concatenate([f[:50], f[50:][::-1]])
f = np.full((T, H, W), 0.5, np.float32)
for t in range(50, T): disc(f, t, 20, x=20 + (t - 50) * 1.6)
stims["translate"] = f
f = np.full((T, H, W), 0.5, np.float32)
for t in range(50, T): disc(f, t, 30)
stims["static"] = f

nv = NetworkView("flow/0000/000"); net = nv.init_network(); net.eval()
eye = BoxEye(extent=15, kernel_size=13)
types = ["T4a", "T4b", "T4c", "T4d", "T5a", "T5b", "T5c", "T5d"]
nodes = net.connectome.nodes
ntype = nodes.type[:].astype(str); u = nodes.u[:]; v = nodes.v[:]
out = {"fps": fps}
for ty in types:
    m = ntype == ty
    out[f"u_{ty}"] = u[m]; out[f"v_{ty}"] = v[m]
for name, frames in stims.items():
    hexmovie = eye(torch.tensor(frames[None]), hex_sample=True)
    t0 = time.time()
    with torch.no_grad():
        act = net.simulate(hexmovie.to(flyvis.device), dt=1 / fps, as_layer_activity=True)
    for ty in types:
        a = np.asarray(getattr(act, ty).squeeze(0), dtype=np.float32)   # (T, 721)
        out[f"{name}_{ty}"] = a
    pk = max(out[f"{name}_{ty}"].max() for ty in types)
    print(f"{name:10s} sim {time.time()-t0:.2f}s  T4/T5 peak {pk:.2f}  mean-during {np.mean([out[f'{name}_{ty}'][60:].mean() for ty in types]):+.3f}")
np.savez("seam/flyvis_out.npz", **out)
print("u range", u.min(), u.max(), "per-type columns", int((ntype == "T4a").sum()))
