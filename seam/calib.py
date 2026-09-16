"""
calib.py - pick the column map and drive gain with statistics.
Top 4 hex symmetries from orient.py x MAX_HZ {150, 400} x 5 stimuli x 3 seeds,
BOTH eyes driven (same map per eye; the loom is on the midline). Readouts over the
stimulus window (1 s): LPLC2 all, LC4 all, DNp01 GF, all DN, per-seed.
Writes seam/calib.json.
"""
import sys, json, itertools, time, numpy as np
sys.path.insert(0, "ref/flybrain/scripts")
from flysim import FlyBrain
A_REF, CENTRE, SPF = 1.0, (18.5, 20.0), 10
MAPS = ["+wu", "+uw", "-wv", "-vu"]; GAINS = [150.0, 400.0]; STIMS = ["loom", "recede", "translate", "static", "flash"]; SEEDS = [0, 1, 2]
cols = np.load("seam/t4t5_columns.npz"); fv = np.load("seam/flyvis_out.npz")
types = ["T4a", "T4b", "T4c", "T4d", "T5a", "T5b", "T5c", "T5d"]
keys = {t: {(int(a), int(c)): i for i, (a, c) in enumerate(zip(fv[f"u_{t}"], fv[f"v_{t}"]))} for t in types}

def colmap(name):
    sign = 1 if name[0] == "+" else -1; perm = name[1:]
    a = np.rint(cols["hex1"] - CENTRE[0]).astype(int); c = np.rint(cols["hex2"] - CENTRE[1]).astype(int)
    trip = {"u": a, "v": c, "w": -a - c}; u, v = sign * trip[perm[0]], sign * trip[perm[1]]
    src = np.full(len(u), -1)
    for t in types:
        for i in np.flatnonzero(cols["type"] == t): src[i] = keys[t].get((int(u[i]), int(v[i])), -1)
    return src

out = []
for seed in SEEDS:
    b = FlyBrain("brain_whole.npz", seed=seed); ty = b.type.astype(str)
    R = {"LPLC2": np.flatnonzero(ty == "LPLC2"), "LC4": np.flatnonzero(ty == "LC4"), "GF": np.flatnonzero(ty == "DNp01"),
         "DNp11": np.flatnonzero(ty == "DNp11"), "DN": b.pop["DN"], "VS": np.flatnonzero(np.char.startswith(ty, "VS"))}
    for mname in MAPS:
        src = colmap(mname); m = src >= 0
        idx, tt, ss = cols["idx"][m], cols["type"][m], src[m]
        b.driven[:] = False
        for c in b.SENSORY_CLASSES: b.driven[b.cls == c] = True
        b.driven[idx] = True; b._driven_idx = np.flatnonzero(b.driven)
        for gain, stim in itertools.product(GAINS, STIMS):
            b.reset(); b.drive_hz[:] = 0; b.g[:] = 0; b.refrac[:] = 0
            cnt = {k: 0 for k in R}; t0 = time.time()
            for f in range(200):
                for t in types:
                    k = tt == t; b.drive_hz[idx[k]] = gain * np.clip(fv[f"{stim}_{t}"][f][ss[k]] / A_REF, 0, 1)
                for s in range(SPF):
                    spk = b.step()
                    if f >= 100:
                        for k, ii in R.items(): cnt[k] += int(spk[ii].sum())
            row = {"seed": seed, "map": mname, "gain": gain, "stim": stim, **cnt}
            out.append(row); print(json.dumps(row), flush=True)
json.dump(out, open("seam/calib.json", "w"), indent=0)
print("done", len(out), "runs")
