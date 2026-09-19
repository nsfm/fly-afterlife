"""goal.py - does the comparator fire? reads a <run>.cells.npz (pair.py --ring --goal G --log-types ...) and asks whether
PFL3 left minus right follows the heading error (heading - goal), and whether DNa02 does.

    uv run python experiments/goal.py world/compass/goal_g200.npz 200
"""
import sys, numpy as np

f = sys.argv[1].replace(".npz", "") + ".cells.npz"; goal = float(sys.argv[2]); C = np.load(f, allow_pickle=True)
ty = C["type"].astype(str); side = C["side"].astype(str); cnt = C["counts"].astype(float); pose = C["pose_chunk"]; n = cnt.shape[0]
heading = pose[:n, 2] % 360; err = (heading - goal + 180) % 360 - 180   # + : he faces right of the goal (clockwise), should turn left
print(f"{n} chunks; goal {goal:.0f} deg; heading error: mean {err.mean():+.0f}, sd {err.std():.0f}, |err| < 30 deg in {(np.abs(err) < 30).mean() * 100:.0f}% of chunks")
print(f"{'type':10s} {'cells':>5s} {'Hz/cell':>8s} {'L Hz':>6s} {'R Hz':>6s}")
for t in sorted(set(ty)):
    m = ty == t; print(f"{t:10s} {m.sum():5d} {cnt[:, m].mean() * 10:8.2f} {cnt[:, m & (side == 'L')].mean() * 10 if (m & (side == 'L')).any() else 0:6.2f} {cnt[:, m & (side == 'R')].mean() * 10 if (m & (side == 'R')).any() else 0:6.2f}")
k = np.ones(5) / 5
for t in ("PFL3", "DNa02", "LAL121", "AOTU019", "DNa03"):
    m = ty == t
    if not m.any(): continue
    L = np.convolve(cnt[:, m & (side == "L")].sum(1), k, mode="same"); R = np.convolve(cnt[:, m & (side == "R")].sum(1), k, mode="same"); d = L - R
    if d.std() == 0: print(f"{t}: L-R flat"); continue
    s = np.sin(np.radians(err)); r = np.corrcoef(d, s)[0, 1]; big = np.abs(err) > 45
    print(f"{t}: corr(L-R, sin(error)) {r:+.3f}; mean L-R when the goal is to his left {d[err < -45].mean() if (err < -45).any() else float('nan'):+.2f}, to his right {d[err > 45].mean() if (err > 45).any() else float('nan'):+.2f}, ahead {d[np.abs(err) < 30].mean() if (np.abs(err) < 30).any() else float('nan'):+.2f} (spikes per chunk)")
