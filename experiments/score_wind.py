"""score garden wind runs: python experiments/score_wind.py world/garden3 off wind gated [--seeds 10,11,12]
upwind cos = mean cos(heading - upwind); t upwind = frames within 45 deg of upwind; d fruit min; t<0.6 = frames within
0.6 m of the fruit; sugar = frames in contact with its skin; rim = fraction of frames on the rim; touch = touch frames."""
import sys, os, numpy as np
d = sys.argv[1]; tags = [a for a in sys.argv[2:] if not a.startswith("--")]
seeds = [int(s) for s in (sys.argv[sys.argv.index("--seeds") + 1] if "--seeds" in sys.argv else "10,11,12").split(",")]
print(f'{"run":14s} {"walked":>7s} {"upwind cos":>10s} {"t upwind":>8s} {"d fruit min":>11s} {"t<0.6":>6s} {"sugar":>6s} {"rim":>5s} {"touch":>6s}')
for tag in tags:
    for s in seeds:
        f = f"{d}/{tag}_s{s}.npz"
        if not os.path.exists(f): print(f"{tag}_s{s}: missing"); continue
        e = np.load(f, allow_pickle=True); pose = e["pose"]; fr = e["fruit"]; wind = e["wind"]; up = np.degrees(np.arctan2(-wind[1], -wind[0]))
        rel = (pose[:, 2] - up + 180) % 360 - 180; c = np.cos(np.radians(rel)); d_f = np.hypot(pose[:, 0] - fr[0], pose[:, 1] - fr[1])
        onrim = (np.abs(pose[:, 0]) > 2.91) | (np.abs(pose[:, 1]) > 2.91)
        print(f'{tag + "_s" + str(s):14s} {np.hypot(*np.diff(pose[:, :2], axis=0).T).sum():6.1f}m {c.mean():+10.2f} {(np.abs(rel) < 45).mean() * 100:7.1f}% {d_f.min():11.2f} {(d_f < 0.6).mean() * 100:5.1f}% {(d_f < fr[3] + 0.09).sum():6d} {onrim.mean():5.2f} {(e["touch"] > 0).sum():6d}')
