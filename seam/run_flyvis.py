"""
run_flyvis.py - render stimuli onto the flyvis retina, run one pretrained model,
save per-column activity for every modelled cell type, with (u, v) per column.

All stimuli: 200x200 px, 100 fps, 2.0 s (200 frames). Frames 0-99 are a HELD
pre-period so nothing appears instantly except in the flash control:
  loom       grey 1s, then dark disc grows r=2 -> 62 px over 1 s
  recede     full disc (r=62) held 1s, then shrinks 62 -> 2 px over 1 s
  translate  grey 1s, then r=20 disc sweeps left -> right over 1 s
  static     full disc (r=62) held 2s                (disc present, no motion)
  flash      grey 1s, then full disc appears instantly and stays  (onset confound)
Analysis window is frames 100-199 everywhere. Writes seam/flyvis_out.npz:
  {stim}_{type}: (200, 721) float32;  u_{type}, v_{type}: (721,);  fps
"""
import os, time, numpy as np, torch
os.environ.setdefault("FLYVIS_ROOT_DIR", "/home/nate/code/fly-afterlife/flyvis_data")
import flyvis
from flyvis import NetworkView
from flyvis.datasets.rendering.eye import BoxEye

H = W = 200; fps = 100; T = 200; R0, R1 = 2.0, 62.0
yy, xx = np.mgrid[0:H, 0:W]; cy = cx = H / 2
def disc(frames, t, r, x=None, y=None):
    x = cx if x is None else x; y = cy if y is None else y
    frames[t][(yy - y) ** 2 + (xx - x) ** 2 < r * r] = 0.0
grey = lambda: np.full((T, H, W), 0.5, np.float32)
stims = {}
f = grey(); [disc(f, t, R0 + (R1 - R0) * (t - 100) / 99) for t in range(100, T)]; stims["loom"] = f
f = grey(); [disc(f, t, R1) for t in range(0, 100)]; [disc(f, t, R1 - (R1 - R0) * (t - 100) / 99) for t in range(100, T)]; stims["recede"] = f
f = grey(); [disc(f, t, 20, x=20 + (t - 100) * 1.6) for t in range(100, T)]; stims["translate"] = f
f = grey(); [disc(f, t, R1) for t in range(T)]; stims["static"] = f
f = grey(); [disc(f, t, R1) for t in range(100, T)]; stims["flash"] = f

nv = NetworkView("flow/0000/000"); net = nv.init_network(); net.eval()
eye = BoxEye(extent=15, kernel_size=13)
nodes = net.connectome.nodes; ntype = nodes.type[:].astype(str); u = nodes.u[:]; v = nodes.v[:]
types = sorted(set(ntype))
out = {"fps": fps, "types": np.array(types)}
for ty in types:
    m = ntype == ty; out[f"u_{ty}"] = u[m]; out[f"v_{ty}"] = v[m]
for name, frames in stims.items():
    hexmovie = eye(torch.tensor(frames[None]), hex_sample=True)
    t0 = time.time()
    with torch.no_grad():
        act = net.simulate(hexmovie.to(flyvis.device), dt=1 / fps, as_layer_activity=True)
    for ty in types:
        out[f"{name}_{ty}"] = np.asarray(getattr(act, ty).squeeze(0), dtype=np.float32)
    t45 = [out[f"{name}_{t}"] for t in ["T4a","T4b","T4c","T4d","T5a","T5b","T5c","T5d"]]
    print(f"{name:10s} sim {time.time()-t0:.2f}s  T4/T5 peak {max(a.max() for a in t45):.2f}  "
          f"mean pre {np.mean([a[20:100].mean() for a in t45]):+.3f}  during {np.mean([a[100:].mean() for a in t45]):+.3f}")
np.savez("seam/flyvis_out.npz", **out)
print(len(types), "types saved")
