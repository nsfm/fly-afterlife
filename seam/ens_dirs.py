"""per-model T4/T5 direction convention on gratings (image-right/left/up/down), models 000-009.
biology in flyvis image space (from the paper's convention, verified on 000): T4a/T5a = image-left (front-to-back with front at image-right),
T4b/T5b = image-right, T4c/T5c = up, T4d/T5d = down. flags each subtype as matching or not; joins with the ensemble loom outcome."""
import os, json, numpy as np, torch
os.environ.setdefault("FLYVIS_ROOT_DIR", "/home/nate/code/fly-afterlife/flyvis_data")
import flyvis
from flyvis import NetworkView
H = W = 200; fps = 100; T = 200; yy, xx = np.mgrid[0:H, 0:W]
from flyvis.datasets.rendering.eye import BoxEye
eye = BoxEye(extent=15, kernel_size=13)
def grating(dx, dy):
    f = np.full((T, H, W), 0.5, np.float32)
    for t in range(100, T):
        coord = xx * dx + yy * dy - (t - 100) * 2.0; f[t] = np.where(((coord // 20) % 2) == 0, 0.2, 0.8)
    return eye(torch.tensor(f[None]), hex_sample=True)
movies = {"right": grating(1, 0), "left": grating(-1, 0), "down": grating(0, 1), "up": grating(0, -1)}
types = ["T4a", "T4b", "T4c", "T4d", "T5a", "T5b", "T5c", "T5d"]; expect = {"a": "left", "b": "right", "c": "up", "d": "down"}
summ = json.load(open("seam/ens/loom_outcome.json")) if os.path.exists("seam/ens/loom_outcome.json") else {}
out = {}
print(f"{'model':5s} " + "".join(f"{t:>7s}" for t in types) + "   match/8   loom>recede (L,R)")
for i in range(10):
    m = f"{i:03d}"; net = NetworkView(f"flow/0000/{m}").init_network(); net.eval()
    pref = {}; shifts = {}
    for t in types: shifts[t] = {}
    for d, mv in movies.items():
        with torch.no_grad(): act = net.simulate(mv.to(flyvis.device), dt=1 / fps, as_layer_activity=True)
        for t in types:
            a = np.asarray(getattr(act, t).squeeze(0)); shifts[t][d] = float(a[120:].mean() - a[20:100].mean())
    row = []; nmatch = 0
    for t in types:
        best = max(shifts[t], key=shifts[t].get); ok = best == expect[t[-1]]; nmatch += ok; row.append(f"{best[:1]}{'*' if ok else ' '}")
    out[m] = {"pref": {t: max(shifts[t], key=shifts[t].get) for t in types}, "shifts": shifts, "nmatch": nmatch}
    lo = summ.get(m, "?")
    print(f"{m:5s} " + "".join(f"{r:>7s}" for r in row) + f"   {nmatch}/8       {lo}", flush=True)
    del net; torch.cuda.empty_cache()
json.dump(out, open("seam/ens/dirs.json", "w"), indent=1)
