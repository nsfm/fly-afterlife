"""flyvis's own direction convention: full-field square-wave grating moving in each of
four image directions; which T4/T5 subtype fires most. Writes seam/flyvis_dirs.npz."""
import os, numpy as np, torch
os.environ.setdefault("FLYVIS_ROOT_DIR", "/home/nate/code/fly-afterlife/flyvis_data")
import flyvis
from flyvis import NetworkView
from flyvis.datasets.rendering.eye import BoxEye
H = W = 200; T = 200; fps = 100; period = 40; speed = 2.0   # px/frame
yy, xx = np.mgrid[0:H, 0:W]
stims = {}
for name, (dx, dy) in {"right": (1, 0), "left": (-1, 0), "down": (0, 1), "up": (0, -1)}.items():
    f = np.full((T, H, W), 0.5, np.float32)
    for t in range(100, T):
        phase = (t - 100) * speed
        coord = xx * dx + yy * dy - phase
        f[t] = np.where(((coord // (period / 2)) % 2) == 0, 0.2, 0.8)
    stims[name] = f
nv = NetworkView("flow/0000/000"); net = nv.init_network(); net.eval()
eye = BoxEye(extent=15, kernel_size=13)
types = ["T4a","T4b","T4c","T4d","T5a","T5b","T5c","T5d"]; out = {}
print(f"{'grating':8s}" + "".join(f"{t:>7s}" for t in types))
for name, frames in stims.items():
    hexmovie = eye(torch.tensor(frames[None]), hex_sample=True)
    with torch.no_grad():
        act = net.simulate(hexmovie.to(flyvis.device), dt=1/fps, as_layer_activity=True)
    row = []
    for t in types:
        a = np.asarray(getattr(act, t).squeeze(0)); out[f"{name}_{t}"] = a
        row.append(a[120:].mean() - a[20:100].mean())
    print(f"{name:8s}" + "".join(f"{x:7.3f}" for x in row))
np.savez("seam/flyvis_dirs.npz", **out)
