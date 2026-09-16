"""tx_pattern.py - the expansion-pattern metric (as flyvis_pattern.py) on the TRANSPLANT's own T4/T5 output, per cell by column."""
import sys, numpy as np
prefix = sys.argv[1] if len(sys.argv) > 1 else "seam/tx"
types = ["T4a","T4b","T4c","T4d","T5a","T5b","T5c","T5d"]; comp = {"a": (-1, 0), "b": (+1, 0), "c": (0, +1), "d": (0, -1)}
g = np.load("seam/eye_geom.npz"); az = np.degrees(np.arctan2(g["dir"][:, 1], g["dir"][:, 0])); el = np.degrees(np.arcsin(g["dir"][:, 2]))
colkey = {(str(s), int(a), int(b)): i for i, (s, a, b) in enumerate(zip(g["side"], g["hex1"], g["hex2"]))}
d = np.load("brain_whole.npz"); bid_all = d["bodyId"]; cols = np.load("seam/columns_all.npz")
cell_col = {int(bid_all[i]): colkey.get((str(s), int(a), int(b)), -1) for i, s, a, b in zip(cols["idx"], cols["side"], cols["hex1"], cols["hex2"])}
rest = np.load(f"{prefix}_empty.npz")
print(f"{'stim':20s} " + "".join(f"{t:>8s}" for t in types) + "    mean   |static-like| = mean|per-subtype|")
for stim in ["loom_left", "recede_left", "static_left", "flash_left", "loom_left_bright", "recede_left_bright", "static_left_bright", "loom_right", "recede_right"]:
    try: w = np.load(f"{prefix}_{stim}.npz")
    except FileNotFoundError: continue
    eye = "L" if "left" in stim else "R"; az0 = 60 if eye == "L" else -60
    c0 = np.argmin((az - az0) ** 2 + el ** 2 + 1e6 * (g["side"] != eye)); cx, cy = g["sx"][c0], g["sy"][c0]
    row = []
    for t in types:
        m = w[f"side_{t}"] == eye; bids = w[f"bid_{t}"][m]; ci = np.array([cell_col.get(int(x), -1) for x in bids]); ok = ci >= 0
        a = np.clip(w[f"act_{t}"][100:, m] - rest[f"act_{t}"][20:100, m].mean(0), 0, None).sum(0)[ok]
        dx, dy = g["sx"][ci[ok]] - cx, g["sy"][ci[ok]] - cy; r = np.hypot(dx, dy); ux, uy = dx / np.maximum(r, 1e-6), dy / np.maximum(r, 1e-6)
        cf, cd = comp[t[-1]]; outward = cf * ux + cd * uy; keep = r > 0.5
        row.append(np.average(outward[keep], weights=a[keep]) if a[keep].sum() > 0 else np.nan)
    print(f"{stim:20s} " + "".join(f"{x:+8.3f}" for x in row) + f"   {np.nanmean(row):+.3f}   {np.nanmean(np.abs(row)):.3f}", flush=True)
