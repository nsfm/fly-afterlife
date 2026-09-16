"""
flyvis_pattern.py - does flyvis's OWN T4/T5 output for the ball carry the expansion pattern?

for each subtype, the activity-weighted mean of its outward component (the component of
the unit vector from the ball centre that its preferred direction points along):
  T4a/T5a: -u_front (fires behind the ball if expanding)   T4b/T5b: +u_front (ahead)
  T4c/T5c: +u_dorsal (above)                                T4d/T5d: -u_dorsal (below)
expansion -> all eight positive; contraction -> all negative; static -> ~0.
also the fraction of each subtype's activity that is directional (|weighted mean|).
"""
import sys, json, numpy as np
types = ["T4a","T4b","T4c","T4d","T5a","T5b","T5c","T5d"]; comp = {"a": (-1, 0), "b": (+1, 0), "c": (0, +1), "d": (0, -1)}
g = np.load("seam/eye_geom.npz"); az = np.degrees(np.arctan2(g["dir"][:, 1], g["dir"][:, 0])); el = np.degrees(np.arcsin(g["dir"][:, 2]))
TAU = float([a for a in sys.argv[1:] if a.startswith("--tau=")][0][6:]) if any(a.startswith("--tau=") for a in sys.argv[1:]) else 0.0
models = [a for a in sys.argv[1:] if not a.startswith("--")] or ["000", "001"]
def highpass(a, tau_frames):
    if tau_frames <= 0: return a
    ema = np.zeros_like(a[0]); out = np.zeros_like(a); k = 1.0 / tau_frames
    for i in range(len(a)):
        ema += k * (a[i] - ema); out[i] = a[i] - ema
    return out
print(f"high-pass tau {TAU:.0f} ms" if TAU else "no high-pass"); print(f"{'model':5s} {'stim':20s} " + "".join(f"{t:>8s}" for t in types) + "    mean   (activity-weighted outward component; + = expansion-consistent)")
for m in models:
    rest = np.load(f"seam/ens/m{m}_empty.npz")
    for stim in ["loom_left", "recede_left", "static_left", "loom_left_bright", "recede_left_bright", "loom_right", "recede_right"]:
        try: w = np.load(f"seam/ens/m{m}_{stim}.npz")
        except FileNotFoundError: continue
        eye = "L" if "left" in stim else "R"; az0 = 60 if eye == "L" else -60
        c0 = np.argmin((az - az0) ** 2 + el ** 2 + 1e6 * (g["side"] != eye)); cx, cy = g["sx"][c0], g["sy"][c0]
        col, idx = w[f"{eye}_col"], w[f"{eye}_idx"]; ok = col >= 0
        sx = np.full(721, np.nan); sy = np.full(721, np.nan); sx[col[ok]] = g["sx"][idx[ok]]; sy[col[ok]] = g["sy"][idx[ok]]
        dx, dy = sx - cx, sy - cy; r = np.hypot(dx, dy); ux, uy = dx / np.maximum(r, 1e-6), dy / np.maximum(r, 1e-6)
        row = []
        for t in types:
            raw = w[f"{eye}_{t}"] - rest[f"{eye}_{t}"][20:100].mean(0); a = np.clip(highpass(raw, TAU / 10.0)[100:], 0, None).sum(0)   # per column, summed over the second
            a[np.isnan(sx)] = 0; cf, cd = comp[t[-1]]; outward = cf * ux + cd * uy
            keep = ~np.isnan(sx) & (r > 0.5); row.append(np.average(outward[keep], weights=a[keep]) if a[keep].sum() > 0 else np.nan)
        print(f"{m:5s} {stim:20s} " + "".join(f"{x:+8.3f}" for x in row) + f"   {np.nanmean(row):+.3f}", flush=True)
