"""
seam_v3.py - the transplant drives the LIF. no column map: the transplant's T4/T5 cells
ARE the LIF's T4/T5 cells, matched by bodyId.

    uv run python seam/seam_v3.py --stims loom_left recede_left static_left ... --seeds 0 1 2 --rest empty

drive: rate = GAIN * clip((act - act_rest) / A_REF, 0, 1) on each T4/T5 cell, act_rest
from the transplant's empty-scene run (frames 20-100). A_REF = 0.5 for the transplant
(its T4 modulation peaks ~0.5-0.9 vs flyvis's ~1.5 on the flat loom). readouts as v2.
"""
import sys, json, argparse, time, numpy as np
sys.path.insert(0, "ref/flybrain/scripts")
from flysim import FlyBrain
ap = argparse.ArgumentParser(); ap.add_argument("--stims", nargs="+", required=True); ap.add_argument("--seeds", type=int, nargs="+", default=[0])
ap.add_argument("--gain", type=float, default=150.0); ap.add_argument("--a-ref", type=float, default=0.5); ap.add_argument("--out", default=None)
ap.add_argument("--prefix", default="seam/tx"); ap.add_argument("--rest", default="empty"); args = ap.parse_args()
SPF = 10; types = ["T4a", "T4b", "T4c", "T4d", "T5a", "T5b", "T5c", "T5d"]
restw = np.load(f"{args.prefix}_{args.rest}.npz")
rows = []
for seed in args.seeds:
    b = FlyBrain("brain_whole.npz", seed=seed); ty = b.type.astype(str); ns = b.side.astype(str); bid2i = {int(x): i for i, x in enumerate(b.bodyId)}
    R = {}
    for name, sel in [("LPLC2", ty == "LPLC2"), ("LC4", ty == "LC4"), ("GF", ty == "DNp01"), ("DNa02", ty == "DNa02"), ("DNa", np.char.startswith(ty, "DNa")), ("DN", b.sc == "descending_neuron"), ("HS", np.char.startswith(ty, "HS"))]:
        for s in "LR": R[f"{name}_{s}"] = np.flatnonzero(sel & (ns == s))
    for stim in args.stims:
        w = np.load(f"{args.prefix}_{stim}.npz"); groups = {}; n_drv = 0
        for t in types:
            bids = w[f"bid_{t}"]; ok = np.array([int(x) in bid2i for x in bids]); idx = np.array([bid2i[int(x)] for x in bids[ok]])
            groups[t] = (idx, w[f"act_{t}"][:, ok], restw[f"act_{t}"][20:100, ok].mean(0)); n_drv += len(idx)
        b.driven[:] = False
        for cl in b.SENSORY_CLASSES: b.driven[b.cls == cl] = True
        for t, (idx, _, _) in groups.items(): b.driven[idx] = True
        b._driven_idx = np.flatnonzero(b.driven); b.reset(); b.drive_hz[:] = 0; b.g[:] = 0; b.refrac[:] = 0
        cnt = {k: 0 for k in R}; bins = {k: [0] * 20 for k in ["LPLC2_L", "LPLC2_R", "GF_L", "GF_R"]}; t0 = time.time(); T = w["act_T4a"].shape[0]
        for f in range(T):
            for t, (idx, a, rest) in groups.items(): b.drive_hz[idx] = args.gain * np.clip((a[f] - rest) / args.a_ref, 0, 1)
            for _ in range(SPF):
                spk = b.step()
                if f >= 100:
                    for k, r in R.items(): cnt[k] += int(spk[r].sum())
                for k in bins: bins[k][f // 10] += int(spk[R[k]].sum())
        rows.append({"seed": seed, "stim": stim, "gain": args.gain, "a_ref": args.a_ref, "during": cnt, "bins100ms": bins})
        print(f"{stim:13s} seed {seed} {time.time()-t0:4.1f}s ({n_drv} driven)  LPLC2 L/R {cnt['LPLC2_L']}/{cnt['LPLC2_R']}  GF {cnt['GF_L']+cnt['GF_R']}  DNa02 L/R {cnt['DNa02_L']}/{cnt['DNa02_R']}  HS L/R {cnt['HS_L']}/{cnt['HS_R']}  DN L/R {cnt['DN_L']}/{cnt['DN_R']}", flush=True)
if args.out: json.dump(rows, open(args.out, "w"), indent=0)
