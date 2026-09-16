"""
orient.py - use LPLC2's known loom selectivity to calibrate the column map.

Eight orientations of our (hex1, hex2) onto flyvis (u, v): swap axes or not, flip u
or not, flip v or not. For each, per eye, drive T4/T5 with the loom and with the
recede stimulus and read LPLC2 + giant fiber. The correct orientation is the one
where loom >> recede. This is calibration against biology (Klapoetke et al. 2017),
not a fit to our own result.
"""
import sys, itertools, time, numpy as np
sys.path.insert(0, "ref/flybrain/scripts")
from flysim import FlyBrain
MAX_HZ, A_REF, CENTRE = 150.0, 1.0, (18.5, 20.0)
b = FlyBrain("brain_whole.npz"); ty = b.type.astype(str)
cols = np.load("seam/t4t5_columns.npz"); fv = np.load("seam/flyvis_out.npz")
types = ["T4a", "T4b", "T4c", "T4d", "T5a", "T5b", "T5c", "T5d"]
keys = {t: {(int(a), int(c)): i for i, (a, c) in enumerate(zip(fv[f"u_{t}"], fv[f"v_{t}"]))} for t in types}
LPLC2 = np.flatnonzero(ty == "LPLC2"); GF = np.flatnonzero(ty == "DNp01")
side = cols["side"]; LP_side = b.side.astype(str)
steps_per_frame = 10

def colmap(swap, fu, fv_):
    a = cols["hex1"] - CENTRE[0]; c = cols["hex2"] - CENTRE[1]
    u, v = (c, a) if swap else (a, c)
    if fu: u = -u
    if fv_: v = -v
    u = np.rint(u).astype(int); v = np.rint(v).astype(int)
    src = np.full(len(u), -1)
    for t in types:
        for i in np.flatnonzero(cols["type"] == t):
            src[i] = keys[t].get((u[i], v[i]), -1)
    return src

def run(stim, src, eye):
    m = (src >= 0) & (side == eye)
    idx, tt, ss = cols["idx"][m], cols["type"][m], src[m]
    b.driven[:] = False
    for c in b.SENSORY_CLASSES: b.driven[b.cls == c] = True
    b.driven[idx] = True; b._driven_idx = np.flatnonzero(b.driven)
    b.reset(); b.drive_hz[:] = 0; b.g[:] = 0; b.refrac[:] = 0
    T = fv[f"{stim}_T4a"].shape[0]; lp = gf = 0
    for f in range(T):
        for t in types:
            k = tt == t
            b.drive_hz[idx[k]] = MAX_HZ * np.clip(fv[f"{stim}_{t}"][f][ss[k]] / A_REF, 0, 1)
        for s in range(steps_per_frame):
            spk = b.step()
            if f >= 50:
                lp += spk[LPLC2[LP_side[LPLC2] == eye]].sum(); gf += spk[GF].sum()
    return int(lp), int(gf)

print(f"{'orientation':22s} {'eye':3s} {'loom LPLC2':>10s} {'recede LPLC2':>12s} {'loom GF':>8s} {'recede GF':>10s}  ratio")
for swap, fu, fv_ in itertools.product([False, True], repeat=3):
    src = colmap(swap, fu, fv_)
    for eye in "LR":
        t0 = time.time()
        ll, lg = run("loom", src, eye); rl, rg = run("recede", src, eye)
        name = f"swap={int(swap)} flipu={int(fu)} flipv={int(fv_)}"
        print(f"{name:22s} {eye:3s} {ll:10d} {rl:12d} {lg:8d} {rg:10d}  {ll/max(rl,1):5.2f}", flush=True)
