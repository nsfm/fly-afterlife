"""score a warm-corner run: where he went relative to the warm spot, and what temperature he experienced.

    uv run python experiments/score_thermo.py world/thermo/rest_s10.npz world/thermo/field_s10.npz ...

the field: T = 25 + 8 exp(-d^2 / 2 0.8^2) C at (1.5, 1.5). thermotaxis in life is avoidance of warm (preferred
25 C; Sayeed & Benzer 1996; Ni 2013): the prediction is LESS time in the warm zone with the field than with the
cells at their 25 C rest. the control ("rest") has the same room, the same cells firing at their rest rates,
and no field, so the only difference is the field.
"""
import sys, numpy as np
import os
HOT = (1.5, 1.5); COLD = (-1.5, -1.5); SIG = 0.8; DT = float(os.environ.get("HOT_DT", "8")); DTC = float(os.environ.get("COLD_DT", "0"))
def T_at(x, y): return 25.0 + DT * np.exp(-((x - HOT[0]) ** 2 + (y - HOT[1]) ** 2) / (2 * SIG ** 2)) + DTC * np.exp(-((x - COLD[0]) ** 2 + (y - COLD[1]) ** 2) / (2 * SIG ** 2))
print(f'{"run":26s} {"mean T felt":>11s} {"time T>28":>9s} {"time T>30":>9s} {"time T<20":>9s} {"time T<15":>9s} {"d hot":>6s} {"d cold":>6s} {"wall":>5s} {"walked":>7s}')
for path in sys.argv[1:]:
    e = np.load(path, allow_pickle=True); pose = e['pose']; T = T_at(pose[:, 0], pose[:, 1]); d = np.hypot(pose[:, 0] - HOT[0], pose[:, 1] - HOT[1])
    onwall = (np.abs(pose[:, 0]) > 1.91) | (np.abs(pose[:, 1]) > 1.91)
    dc = np.hypot(pose[:, 0] - COLD[0], pose[:, 1] - COLD[1])
    print(f'{path.split("/")[-1]:26s} {T.mean():11.2f} {(T > 28).mean()*100:8.1f}% {(T > 30).mean()*100:8.1f}% {(T < 20).mean()*100:8.1f}% {(T < 15).mean()*100:8.1f}% {d.mean():6.2f} {dc.mean():6.2f} {onwall.mean():5.2f} {np.hypot(*np.diff(pose[:, :2], axis=0).T).sum():6.1f}m')
