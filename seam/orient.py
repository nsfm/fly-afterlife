"""
orient.py - calibrate the column map against LPLC2's known loom selectivity.

The 12 symmetries of the hex lattice in axial coords: permutations of (u, v, w=-u-v)
with a global sign. For each, per eye: drive T4/T5 with loom and with recede, read
LPLC2 (that eye) and the giant fiber over the stimulus window. The right map is the
one where loom >> recede (Klapoetke et al. 2017). Biology calibrates the map; the
map is not fit to our own downstream result.
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
side = cols["side"]; nside = b.side.astype(str); SPF = 10

def colmap(perm, sign):
    a = np.rint(cols["hex1"] - CENTRE[0]).astype(int); c = np.rint(cols["hex2"] - CENTRE[1]).astype(int)
    w = -a - c; trip = {"u": a, "v": c, "w": w}
    u, v = sign * trip[perm[0]], sign * trip[perm[1]]
    src = np.full(len(u), -1)
    for t in types:
        for i in np.flatnonzero(cols["type"] == t):
            src[i] = keys[t].get((int(u[i]), int(v[i])), -1)
    return src

def run(stim, src, eye):
    m = (src >= 0) & (side == eye)
    idx, tt, ss = cols["idx"][m], cols["type"][m], src[m]
    b.driven[:] = False
    for c in b.SENSORY_CLASSES: b.driven[b.cls == c] = True
    b.driven[idx] = True; b._driven_idx = np.flatnonzero(b.driven)
    b.reset(); b.drive_hz[:] = 0; b.g[:] = 0; b.refrac[:] = 0
    lp_eye = LPLC2[nside[LPLC2] == eye]; lp = gf = 0
    for f in range(200):
        for t in types:
            k = tt == t
            b.drive_hz[idx[k]] = MAX_HZ * np.clip(fv[f"{stim}_{t}"][f][ss[k]] / A_REF, 0, 1)
        for s in range(SPF):
            spk = b.step()
            if f >= 100: lp += spk[lp_eye].sum(); gf += spk[GF].sum()
    return int(lp), int(gf)

perms = [p for p in itertools.permutations("uvw", 2)]
print(f"{'map':10s} {'eye':3s} {'loom LPLC2':>10s} {'recede LPLC2':>12s} {'loom GF':>8s} {'recede GF':>10s}  ratio")
for perm, sign in itertools.product(perms, [1, -1]):
    src = colmap(perm, sign)
    for eye in "LR":
        ll, lg = run("loom", src, eye); rl, rg = run("recede", src, eye)
        print(f"{('+' if sign>0 else '-')+''.join(perm):10s} {eye:3s} {ll:10d} {rl:12d} {lg:8d} {rg:10d}  {ll/max(rl,1):5.2f}", flush=True)
