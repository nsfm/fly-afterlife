"""benchmark.py - score a walking fly against the published open-field statistics (docs/BENCHMARKS.md).

    uv run python experiments/benchmark.py world/arena/*.npz            # our runs (x, y, heading at 100 Hz, a circular arena)
    uv run python experiments/benchmark.py --dat data/opynfield/8.4cm/*.dat --arena-cm 8.4   # the Roman lab's flies

units: one sim metre is 15 mm in life (his body 0.16 m = 2.5 mm). every metric is computed at the source's sampling
interval (decimated from 100 Hz), and durations are given raw and time-rescaled by the ratio of the walking mode to
the published 13 mm/s (the time-rescaling control). rows follow the table in docs/BENCHMARKS.md.
"""
from __future__ import annotations
import sys, glob, argparse, numpy as np

MM_PER_SIM_M = 15.0
STOP_MM_S = 1.0                     # Valente 2007: a stationary fly's noise floor
WALL_BAND_MM = 6.0                  # Soibam 2012: "within 6 mm of the wall"
PUBLISHED_WALK_MODE_MM_S = 13.0     # Valente 2007: 11-15 at room temperature
WALK_MODE_FLOOR = 4.0               # the valley between the stop mode and the walking mode on smoothed tracks (measured on opynfield run1: 10th pct 0.6, 75th 11.6)


def load_npz(path):
    e = np.load(path, allow_pickle=True); pose = e["pose"]; fps = int(e["fps"])
    R = float(e["arena_radius"]) if "arena_radius" in e.files else None
    return pose[:, 0] * MM_PER_SIM_M, pose[:, 1] * MM_PER_SIM_M, pose[:, 2], fps, (R * MM_PER_SIM_M if R else None)


def load_dat(path, arena_cm):
    """opynfield / BuriTrack .txt: tab-separated time (s), x, y (cm), ~30 Hz, NaN on tracking dropouts (dropped).
    centre = the midpoint of the extent per axis; the arena radius is arena_cm / 2 (the 99.5th-percentile radius is
    printed as a check). heading from displacement."""
    a = np.genfromtxt(path, delimiter="\t"); a = a[np.isfinite(a).all(1)]
    t, x, y = a[:, 0], a[:, 1] * 10.0, a[:, 2] * 10.0
    fps = 1.0 / np.median(np.diff(t)); x = x - (x.min() + x.max()) / 2; y = y - (y.min() + y.max()) / 2
    R = arena_cm * 10 / 2; r995 = np.percentile(np.hypot(x, y), 99.5)
    if abs(r995 - R) > 0.15 * R: print(f"  note: {path.split('/')[-1]}: 99.5th pct radius {r995:.1f} mm vs arena {R:.1f}", file=sys.stderr)
    x, y = smooth(x, fps), smooth(y, fps)
    return x, y, heading_from_path(x, y, fps), fps, R


SMOOTH_S = 0.15                     # boxcar on tracked centroids (video jitter); our own poses are exact and are not smoothed


def smooth(a, fps):
    k = max(1, int(round(SMOOTH_S * fps))); k += (k + 1) % 2; ker = np.ones(k) / k
    pad = np.r_[np.full(k // 2, a[0]), a, np.full(k // 2, a[-1])]; return np.convolve(pad, ker, mode="valid")


def heading_from_path(x, y, fps):
    """heading from displacement while moving (> 1 mm/s), held through stops (a standing fly keeps its heading)."""
    dx, dy = np.gradient(x), np.gradient(y); v = np.hypot(dx, dy) * fps; h = np.degrees(np.arctan2(dy, dx)); h[v <= STOP_MM_S] = np.nan
    idx = np.arange(len(h)); good = np.isfinite(h)
    if not good.any(): return np.zeros_like(h)
    return np.interp(idx, idx[good], np.unwrap(np.radians(h[good])) * 180 / np.pi) % 360


def decimate(x, y, h, fps, target_fps):
    k = max(1, int(round(fps / target_fps))); return x[::k], y[::k], h[::k], fps / k


def runs(mask):
    ch = np.diff(np.r_[0, mask.astype(int), 0]); a = np.where(ch == 1)[0]; b = np.where(ch == -1)[0]; return b - a


def metrics(x, y, h, fps, R):
    out = {}
    # speed at 30 fps (Valente / Soibam), mm/s
    x3, y3, h3, f3 = decimate(x, y, h, fps, 30.0); v = np.hypot(np.diff(x3), np.diff(y3)) * f3
    walking = v > STOP_MM_S; out["frac_below_1mm_s"] = float((~walking).mean())
    vw = v[walking]; vm = v[v > WALK_MODE_FLOOR]; hist, edges = np.histogram(vm, bins=np.arange(WALK_MODE_FLOOR, 40, 1.0)); mode = float(edges[np.argmax(hist)] + 0.5) if vm.size else 0.0   # the walking mode is the peak above the valley; the stop mode sits below it
    out["walk_mode_mm_s"] = mode; out["walk_median_mm_s"] = float(np.median(vw)) if vw.size else 0.0
    bouts = runs(walking) / f3; pauses = runs(~walking) / f3   # TODO (09-18): a hysteresis on the walking threshold; at 1 mm/s on smoothed tracks the real flies' bouts fragment (0.35 s vs Valente's 1.4-2.1)
    out["bout_mean_s"] = float(bouts.mean()) if bouts.size else 0.0; out["bout_over_10s_frac"] = float((bouts > 10).mean()) if bouts.size else 0.0
    out["pause_mean_s"] = float(pauses.mean()) if pauses.size else 0.0; out["pause_under_0.3s_frac"] = float((pauses < 0.3).mean()) if pauses.size else 0.0
    # turn angle at dt = 0.04 s (Soibam PLoS ONE, 25 fps) and dt = 1 s (Soibam Brain Behav)
    for tag, dt in (("0.04s", 0.04), ("1s", 1.0)):
        xd, yd, hd, fd = decimate(x, y, h, fps, 1.0 / dt); vd = np.hypot(np.diff(xd), np.diff(yd)) * fd
        dh = np.abs((np.diff(hd) + 180) % 360 - 180)[vd > STOP_MM_S]
        if tag == "0.04s": out["turn0.04_within_30_45_60"] = tuple(float((dh < a).mean()) for a in (30, 45, 60)) if dh.size else (0, 0, 0)
        else: hist, edges = np.histogram(dh, bins=np.arange(0, 181, 3.6)); out["turn1s_mode_deg"] = float(edges[np.argmax(hist)] + 1.8) if dh.size else 0.0
    # angular velocity at 30 fps: crossings of 45 deg/s, 99th percentile (Katsov 2017)
    om = ((np.diff(h3) + 180) % 360 - 180) * f3; up = np.flatnonzero((np.abs(om[1:]) >= 45) & (np.abs(om[:-1]) < 45))
    out["omega_p99_deg_s"] = float(np.percentile(np.abs(om), 99)) if om.size else 0.0   # TODO: on tracked centroids this tail is displacement noise (2,500 deg/s on real flies); needs a heading filter before it can be compared
    out["inter_turn_ms"] = float(np.mean(np.diff(up)) / f3 * 1000) if up.size > 1 else 0.0
    # wall occupancy (circular arena): within 6 mm of the wall; outer third of the radius
    if R:
        r = np.hypot(x3, y3); out["wall_6mm_frac"] = float((r > R - WALL_BAND_MM).mean()); out["outer_third_frac"] = float((r > 2 * R / 3).mean())
        # circling bias: signed angular momentum sign fraction (Buchanan 2015)
        ang = np.unwrap(np.arctan2(y3, x3)); out["circling_bias"] = float(np.sign(np.diff(ang)).mean())
    # the time-rescaling control: durations with time scaled by (walk mode / published)
    k = mode / PUBLISHED_WALK_MODE_MM_S if mode > 0 else 1.0
    out["bout_mean_s_rescaled"] = out["bout_mean_s"] * k; out["pause_mean_s_rescaled"] = out["pause_mean_s"] * k; out["inter_turn_ms_rescaled"] = out["inter_turn_ms"] * k
    return out


TARGETS = [("frac_below_1mm_s", "fraction below 1 mm/s", "reported per study; bimodal"), ("walk_mode_mm_s", "walking mode (mm/s)", "11-15 (Valente); 17.5 at 34 C"),
           ("bout_mean_s", "walking bout mean (s)", "decay 1.4-2.1 (Valente fig. 8)"), ("pause_mean_s", "pause mean (s)", "decay 0.14-0.17; 76% < 0.3 s"),
           ("pause_under_0.3s_frac", "pauses under 0.3 s", "0.76 at the rim"), ("turn0.04_within_30_45_60", "turn angle 0.04 s within 30/45/60", "0.60 / 0.72 / 0.80"),
           ("turn1s_mode_deg", "turn angle 1 s, mode (deg)", "12.6 edge, 3.6 centre"), ("inter_turn_ms", "inter-turn interval (ms)", "250 +/- 110 (Katsov)"),
           ("omega_p99_deg_s", "99th pct |omega| (deg/s)", "< ~450"), ("wall_6mm_frac", "within 6 mm of the wall", "0.88-0.90 (8.4 cm)"), ("outer_third_frac", "outer third of radius", "0.899 (Soibam BB)"),
           ("circling_bias", "circling bias (signed)", "population 0, individuals biased"), ("bout_mean_s_rescaled", "bout mean, time-rescaled", "as above"), ("pause_mean_s_rescaled", "pause mean, time-rescaled", "as above"), ("inter_turn_ms_rescaled", "inter-turn, time-rescaled", "as above")]


def fmt(v):
    return "/".join(f"{a:.2f}" for a in v) if isinstance(v, tuple) else (f"{v:.2f}" if isinstance(v, float) else str(v))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("files", nargs="*"); ap.add_argument("--dat", nargs="*", default=[]); ap.add_argument("--arena-cm", type=float, default=8.4); ap.add_argument("--radius-sim", type=float, default=None, help="arena radius in sim m if the npz lacks it")
    a = ap.parse_args(); rows = []
    for f in a.files:
        x, y, h, fps, R = load_npz(f); R = R or (a.radius_sim * MM_PER_SIM_M if a.radius_sim else None); rows.append((f.split("/")[-1], metrics(x, y, h, fps, R)))
    for f in a.dat:
        x, y, h, fps, R = load_dat(f, a.arena_cm); rows.append((f.split("/")[-1], metrics(x, y, h, fps, R)))
    if not rows: sys.exit("no files")
    print(f"{'metric':36s} {'published':32s} " + " ".join(f"{n[:14]:>14s}" for n, _ in rows) + ("      mean" if len(rows) > 1 else ""))
    for key, label, pub in TARGETS:
        vals = [m.get(key) for _, m in rows]
        if all(v is None for v in vals): continue
        mean = "" if len(rows) < 2 or isinstance(vals[0], tuple) else f"{np.mean([v for v in vals if v is not None]):10.2f}"
        print(f"{label:36s} {pub:32s} " + " ".join(f"{fmt(v) if v is not None else '-':>14s}" for v in vals) + mean)
