"""
seam_v1.py - drive EVERY flyvis-modelled cell type present in our fly, not just T4/T5.

    uv run python seam/seam_v1.py --map +wu --gain 150 --seeds 0 1 2 [--only T4T5]

Same seam as v0, one column map (columns_all.npz), all 55 types. The LIF's optic
lobe becomes a pass-through for flyvis: every columnar cell fires at a rate set by
flyvis, and the LIF's own synapses onto those cells are irrelevant (driven cells
ignore membrane). What the LIF computes is everything flyvis doesn't model: the
projection neurons (LC/LPLC/LT/...), tangentials, central brain, DNs, VNC.

Readouts per stimulus, over the 1 s stimulus window, per seed: LPLC2, LPLC1, LC4,
LC6, LC11, LC16, VS, HS, DNp01 (GF), DNp02, DNp04, DNp11, all DN, leg motor.
"""
import sys, json, argparse, time, numpy as np
sys.path.insert(0, "ref/flybrain/scripts")
from flysim import FlyBrain
ap = argparse.ArgumentParser(); ap.add_argument("--map", default="+wu"); ap.add_argument("--gain", type=float, default=150.0)
ap.add_argument("--a-ref", type=float, default=1.0); ap.add_argument("--seeds", type=int, nargs="+", default=[0])
ap.add_argument("--only", default=None, help="T4T5 to restrict to v0's cells"); ap.add_argument("--out", default=None)
ap.add_argument("--baseline", action="store_true", help="drive with change from rest: rate ~ (act - act_rest)+, act_rest = per-cell mean over the grey pre-period of the loom stimulus")
ap.add_argument("--std", default=None, help="flyvis: depression on driven cells' outputs; all: every presynaptic neuron")
ap.add_argument("--shuffle", type=int, default=None, help="control: permute the column assignment within each type with this seed, destroying spatial structure")
ap.add_argument("--stims", nargs="+", default=["loom", "recede", "translate", "static", "flash"])
args = ap.parse_args()
CENTRE, SPF = (18.5, 20.0), 10
cols = np.load("seam/columns_all.npz"); fv = np.load("seam/flyvis_out.npz")
fvtypes = [str(t) for t in fv["types"]]
if args.only == "T4T5":
    keep = np.isin(cols["fvtype"], ["T4a", "T4b", "T4c", "T4d", "T5a", "T5b", "T5c", "T5d"])
    cols = {k: cols[k][keep] for k in cols.files}
keys = {t: {(int(a), int(c)): i for i, (a, c) in enumerate(zip(fv[f"u_{t}"], fv[f"v_{t}"]))} for t in fvtypes}

sign = 1 if args.map[0] == "+" else -1; perm = args.map[1:]
a = np.rint(cols["hex1"] - CENTRE[0]).astype(int); c = np.rint(cols["hex2"] - CENTRE[1]).astype(int)
trip = {"u": a, "v": c, "w": -a - c}; U, V = sign * trip[perm[0]], sign * trip[perm[1]]
src = np.array([keys[str(t)].get((int(u), int(v)), -1) if str(t) in keys else -1
                for t, u, v in zip(cols["fvtype"], U, V)])
m = src >= 0
idx, tt, ss = cols["idx"][m], cols["fvtype"][m].astype(str), src[m]
if args.shuffle is not None:
    rng = np.random.default_rng(args.shuffle)
    for t in set(tt):
        k = np.flatnonzero(tt == t); ss[k] = rng.permutation(ss[k])
groups = {t: (idx[tt == t], ss[tt == t]) for t in set(tt)}
rest = {t: (fv[f"loom_{t}"][20:100].mean(0) if args.baseline else 0.0) for t in groups}
print(f"driving {m.sum()} cells of {len(set(tt))} types ({(~m).sum()} outside the lattice)")

rows = []
for seed in args.seeds:
    b = FlyBrain("brain_whole.npz", seed=seed); ty = b.type.astype(str)
    R = {k: np.flatnonzero(ty == k) for k in ["LPLC2", "LPLC1", "LC4", "LC6", "LC11", "LC16", "DNp01", "DNp02", "DNp04", "DNp11"]}
    R["LPi"] = np.flatnonzero(np.char.startswith(ty, "LPi"))
    for k in ["LPi34", "LPi21", "LPi12", "LPi43"]: R[k] = np.flatnonzero(ty == k)
    R["VS"] = np.flatnonzero(np.char.startswith(ty, "VS")); R["HS"] = np.flatnonzero(np.char.startswith(ty, "HS"))
    R["DN"] = b.pop["DN"]; R["legMN"] = np.flatnonzero(b.sc == "vnc_motor")
    b.driven[:] = False
    for cl in b.SENSORY_CLASSES: b.driven[b.cls == cl] = True
    b.driven[idx] = True; b._driven_idx = np.flatnonzero(b.driven)
    if args.std == "flyvis": b.pop["flyvis"] = idx; b.enable_std(("flyvis",))
    elif args.std == "all": b.enable_std(None)
    for stim in args.stims:
        b.reset(); b.drive_hz[:] = 0; b.g[:] = 0; b.refrac[:] = 0
        cnt = {k: 0 for k in R}; pre = {k: 0 for k in R}; t0 = time.time()
        bins = {k: [0] * 20 for k in ["LPLC2", "LPi", "DNp01", "DN"]}
        for f in range(200):
            for t, (ii, s_) in groups.items():
                b.drive_hz[ii] = args.gain * np.clip((fv[f"{stim}_{t}"][f] - rest[t])[s_] / args.a_ref, 0, 1)
            for s in range(SPF):
                spk = b.step()
                tgt = cnt if f >= 100 else pre
                for k, r in R.items(): tgt[k] += int(spk[r].sum())
                for k in bins: bins[k][f // 10] += int(spk[R[k]].sum())
        row = {"seed": seed, "stim": stim, "gain": args.gain, "map": args.map, "baseline": args.baseline, "std": args.std, "shuffle": args.shuffle, "pre": pre, "during": cnt, "bins100ms": bins}
        rows.append(row)
        print(f"   LPLC2/100ms: " + " ".join(f"{x:3d}" for x in bins["LPLC2"]) + f"   GF: " + " ".join(f"{x:d}" for x in bins["DNp01"]))
        print(f"{stim:10s} seed {seed} {time.time()-t0:4.1f}s  " + "  ".join(f"{k} {pre[k]:d}->{cnt[k]:d}" for k in ["LPLC2", "LPi", "LPi34", "LPi21", "LPi12", "LPi43", "DNp01", "DN"]), flush=True)
if args.out: json.dump(rows, open(args.out, "w"), indent=0)
