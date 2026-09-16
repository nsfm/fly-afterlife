"""
seam_v2.py - per-eye seam. each of our T4/T5 cells is driven by ITS OWN eye's flyvis
run at ITS OWN column. no swept map: the column -> lattice map is derived in
world_flyvis.py from flyvis's direction convention + our dorsal (DRA) + FRONT_SIGN.

    uv run python seam/seam_v2.py --stims loom_ahead loom_left recede_ahead --seeds 0 1 2

Drive: rate = GAIN * clip((act - act_rest) / A_REF, 0, 1), act_rest = per-column mean
over frames 20-100 of the same stimulus (the held pre-period). GAIN 150, A_REF 1.

Readouts over the 1 s stimulus window, per seed, per side where it makes sense:
LPLC2 L/R, LC4, DNp01 (GF), DNa02 L/R, DNa family L/R, all DN L/R, plus 100 ms bins
for LPLC2 and GF.
"""
import sys, json, argparse, time, numpy as np
sys.path.insert(0, "ref/flybrain/scripts")
from flysim import FlyBrain
ap = argparse.ArgumentParser(); ap.add_argument("--stims", nargs="+", required=True); ap.add_argument("--seeds", type=int, nargs="+", default=[0])
ap.add_argument("--gain", type=float, default=150.0); ap.add_argument("--a-ref", type=float, default=1.0); ap.add_argument("--out", default=None)
ap.add_argument("--prefix", default="seam/world"); args = ap.parse_args()
SPF = 10; types = ["T4a", "T4b", "T4c", "T4d", "T5a", "T5b", "T5c", "T5d"]
cols = np.load("seam/t4t5_columns.npz"); g = np.load("seam/eye_geom.npz")
gkey = {(str(s), int(a), int(b)): i for i, (s, a, b) in enumerate(zip(g["side"], g["hex1"], g["hex2"]))}
gi = np.array([gkey[(str(s), int(a), int(b))] for s, a, b in zip(cols["side"], cols["hex1"], cols["hex2"])])

rows = []
for seed in args.seeds:
    b = FlyBrain("brain_whole.npz", seed=seed); ty = b.type.astype(str); ns = b.side.astype(str)
    R = {}
    for name, sel in [("LPLC2", ty == "LPLC2"), ("LC4", ty == "LC4"), ("GF", ty == "DNp01"), ("DNa02", ty == "DNa02"),
                      ("DNa", np.char.startswith(ty, "DNa")), ("DN", b.sc == "descending_neuron"), ("HS", np.char.startswith(ty, "HS"))]:
        for s in "LR": R[f"{name}_{s}"] = np.flatnonzero(sel & (ns == s))
    for stim in args.stims:
        w = np.load(f"{args.prefix}_{stim}.npz")
        # per cell: flyvis hex index in its own eye, -1 if outside the lattice
        hexidx = np.full(len(gi), -1)
        for s in "LR":
            k = cols["side"] == s; colmap = dict(zip(w[f"{s}_idx"].tolist(), w[f"{s}_col"].tolist()))
            hexidx[k] = [colmap.get(int(i), -1) for i in gi[k]]
        m = hexidx >= 0; idx, tt, ss, sd = cols["idx"][m], cols["type"][m], hexidx[m], cols["side"][m]
        groups = {}
        for t in types:
            for s in "LR":
                kk = (tt == t) & (sd == s); a = w[f"{s}_{t}"]
                groups[(t, s)] = (idx[kk], ss[kk], a, a[20:100].mean(0))
        b.driven[:] = False
        for cl in b.SENSORY_CLASSES: b.driven[b.cls == cl] = True
        b.driven[idx] = True; b._driven_idx = np.flatnonzero(b.driven)
        b.reset(); b.drive_hz[:] = 0; b.g[:] = 0; b.refrac[:] = 0
        cnt = {k: 0 for k in R}; bins = {k: [0] * 20 for k in ["LPLC2_L", "LPLC2_R", "GF_L", "GF_R", "DNa_L", "DNa_R"]}; t0 = time.time()
        for f in range(200):
            for (t, s), (ii, hx, a, rest) in groups.items():
                b.drive_hz[ii] = args.gain * np.clip((a[f] - rest)[hx] / args.a_ref, 0, 1)
            for _ in range(SPF):
                spk = b.step()
                if f >= 100:
                    for k, r in R.items(): cnt[k] += int(spk[r].sum())
                for k in bins: bins[k][f // 10] += int(spk[R[k]].sum())
        rows.append({"seed": seed, "stim": stim, "gain": args.gain, "during": cnt, "bins100ms": bins})
        print(f"{stim:13s} seed {seed} {time.time()-t0:4.1f}s  LPLC2 L/R {cnt['LPLC2_L']}/{cnt['LPLC2_R']}  GF {cnt['GF_L']+cnt['GF_R']}  "
              f"DNa02 L/R {cnt['DNa02_L']}/{cnt['DNa02_R']}  DNa L/R {cnt['DNa_L']}/{cnt['DNa_R']}  HS L/R {cnt['HS_L']}/{cnt['HS_R']}  DN L/R {cnt['DN_L']}/{cnt['DN_R']}", flush=True)
        print("    LPLC2 L+R /100ms:", " ".join(f"{a+c:3d}" for a, c in zip(bins["LPLC2_L"], bins["LPLC2_R"])), "  GF:", " ".join(f"{a+c}" for a, c in zip(bins["GF_L"], bins["GF_R"])))
if args.out: json.dump(rows, open(args.out, "w"), indent=0)
