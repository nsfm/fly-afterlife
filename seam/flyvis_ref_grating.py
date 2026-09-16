"""flyvis reference for the transplant's grating test: 6-column period square wave, 12 columns/s (=30 deg period, 60 deg/s at 5 deg/column), 1 s grey then 1 s motion."""
import os, numpy as np, torch
os.environ.setdefault("FLYVIS_ROOT_DIR", "/home/nate/code/fly-afterlife/flyvis_data")
import flyvis
from flyvis import NetworkView
nv = NetworkView("flow/0000/000"); net = nv.init_network(); net.eval()
nodes = net.connectome.nodes; ntype = nodes.type[:].astype(str); u = nodes.u[:]; v = nodes.v[:]
# build the hex movie directly in (u,v): column x-coordinate = v (image-right), y = -(u + v/2)
X = v.astype(float); Y = -(u + v / 2.0)
fps = 100; T = 200; types = ["T4a","T4b","T4c","T4d","T5a","T5b","T5c","T5d"]
inp = ntype == "R1"; xr, yr = X[inp], Y[inp]        # 721 columns in R1 order == lattice order
def movie(coord, sgn, speed_cols=12.0, period=6.0):
    m = np.full((T, 721), 0.5, np.float32)
    for t in range(100, T): m[t] = np.where(((coord - sgn * speed_cols * (t - 100) / fps) // (period / 2)) % 2 == 0, 0.2, 0.8)
    return torch.tensor(m[None, :, None, :], device=flyvis.device)
print(f"{'motion':12s}" + "".join(f"{t:>14s}" for t in types) + "   (mean shift / temporal modulation)")
res = {}
for name, coord, sgn in (("image-right", xr, +1), ("image-left", xr, -1), ("image-up", yr, +1), ("image-down", yr, -1)):
    with torch.no_grad(): act = net.simulate(movie(coord, sgn), dt=1 / fps, as_layer_activity=True)
    row = []
    for t in types:
        a = np.asarray(getattr(act, t).squeeze(0)); res[(name, t)] = (a[120:].mean() - a[20:100].mean(), a[120:].std(0).mean()); row.append(res[(name, t)])
    print(f"{name:12s}" + "".join(f"{m:+7.3f}/{md:5.3f} " for m, md in row))
chain = ["R1","L1","L2","L3","L4","L5","C2","C3","T1","Mi1","Tm3","Mi4","Mi9","Tm1","Tm2","Tm4","Tm9","CT1(M10)","CT1(Lo1)","T4a","T4b","T5a","T5b"]
with torch.no_grad(): act = net.simulate(movie(xr, +1), dt=1 / fps, as_layer_activity=True)
print("\nflyvis chain under image-right grating: rest / during-mean / temporal modulation / frac of cells with rest>0")
for t in chain:
    a = np.asarray(getattr(act, t).squeeze(0)); print(f"  {t:9s} rest {a[20:100].mean():+.3f}  during {a[120:].mean():+.3f}  mod {a[120:].std(0).mean():.3f}  active {np.mean(a[20:100].mean(0) > 0):.2f}")
print("DS: T4a right-left", f"{res[('image-right','T4a')][0]-res[('image-left','T4a')][0]:+.3f}", " T4b", f"{res[('image-right','T4b')][0]-res[('image-left','T4b')][0]:+.3f}", " T4c up-down", f"{res[('image-up','T4c')][0]-res[('image-down','T4c')][0]:+.3f}", " T4d", f"{res[('image-up','T4d')][0]-res[('image-down','T4d')][0]:+.3f}")
