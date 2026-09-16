"""
ideal_t4t5.py - is the LIF's LPLC2 circuit able to detect expansion at all?

drive the LIF's own T4/T5 cells (by column, left eye) with an IDEAL direction-selective
pattern, no flyvis, no transplant:
  expand:   a ring growing from radius 2 to 12 columns over 1 s around a centre at
            ~60 deg left; on the ring, each column's outward direction is decomposed
            into (front, dorsal); T4b/T5b fire on the front side, T4a/T5a on the back,
            T4c/T5c on the top, T4d/T5d on the bottom, rate = RATE * |cos|.
  contract: same ring shrinking, assignments mirrored (inward motion).
  flash:    all 8 subtypes on a fixed ring (radius 7) at once, first 200 ms only.
  static:   nothing driven (control for baseline).
readout: LPLC2 L/R, LPi L, GF, all DN, per 100 ms.
"""
import sys, numpy as np
sys.path.insert(0, "ref/flybrain/scripts")
from flysim import FlyBrain
RATE, SPF = 150.0, 10
b = FlyBrain("brain_whole.npz", seed=0); ty = b.type.astype(str); ns = b.side.astype(str)
cols = np.load("seam/t4t5_columns.npz"); g = np.load("seam/eye_geom.npz")
gkey = {(str(s), int(a), int(h)): i for i, (s, a, h) in enumerate(zip(g["side"], g["hex1"], g["hex2"]))}
gi = np.array([gkey[(str(s), int(a), int(h))] for s, a, h in zip(cols["side"], cols["hex1"], cols["hex2"])])
L = cols["side"] == "L"; idx = cols["idx"][L]; sub = cols["type"][L]; sx = g["sx"][gi[L]]; sy = g["sy"][gi[L]]
az = np.degrees(np.arctan2(g["dir"][:, 1], g["dir"][:, 0])); el = np.degrees(np.arcsin(g["dir"][:, 2]))
c0 = np.argmin((az - 60) ** 2 + el ** 2 * (g["side"] == "L") + 1e6 * (g["side"] != "L")); cx, cy = g["sx"][c0], g["sy"][c0]
dx, dy = sx - cx, sy - cy; r = np.hypot(dx, dy); ux, uy = dx / np.maximum(r, 1e-6), dy / np.maximum(r, 1e-6)
R = {k: np.flatnonzero(sel) for k, sel in [("LPLC2_L", (ty == "LPLC2") & (ns == "L")), ("LPLC2_R", (ty == "LPLC2") & (ns == "R")), ("LPi_L", np.char.startswith(ty, "LPi") & (ns == "L")), ("GF", ty == "DNp01"), ("DN", b.sc == "descending_neuron")]}
def ring_drive(radius, sign, width=1.0, nonsel=False):
    on = np.abs(r - radius) < width; d = np.zeros(len(idx))
    for s_, comp in (("a", -ux), ("b", ux), ("c", uy), ("d", -uy)):     # a: outward motion is front-to-back on the BACK side (ux<0)
        k = on & np.char.endswith(sub, s_)
        d[k] = RATE * (1.0 if nonsel else np.clip(sign * comp[k], 0, 1))
    return d
MIX = 0.0
def run(name):
    b.driven[:] = False
    for cl in b.SENSORY_CLASSES: b.driven[b.cls == cl] = True
    b.driven[idx] = True; b._driven_idx = np.flatnonzero(b.driven); b.reset(); b.drive_hz[:] = 0; b.g[:] = 0; b.refrac[:] = 0
    bins = {k: [0] * 20 for k in R}
    for f in range(200):
        t = (f - 100) / 100.0
        if name == "expand" and f >= 100: b.drive_hz[idx] = (1 - MIX) * ring_drive(2 + 10 * t, +1) + MIX * ring_drive(2 + 10 * t, +1, nonsel=True)
        elif name == "contract" and f >= 100: b.drive_hz[idx] = (1 - MIX) * ring_drive(12 - 10 * t, -1) + MIX * ring_drive(12 - 10 * t, -1, nonsel=True)
        elif name == "flash" and 100 <= f < 120: b.drive_hz[idx] = ring_drive(7, +1, nonsel=True)
        else: b.drive_hz[idx] = 0
        for _ in range(SPF):
            spk = b.step()
            for k, ii in R.items(): bins[k][f // 10] += int(spk[ii].sum())
    tot = {k: sum(v[10:]) for k, v in bins.items()}
    return tot
    print(f"{name:9s} LPLC2 L {tot['LPLC2_L']:4d}  R {tot['LPLC2_R']:3d}  LPi_L {tot['LPi_L']:5d}  GF {tot['GF']:3d}  DN {tot['DN']:5d}   LPLC2_L/100ms: " + " ".join(f"{x:3d}" for x in bins["LPLC2_L"][10:]), flush=True)
print(f"ideal drive on the LEFT eye's own T4/T5 cells; centre column {c0} at az {az[c0]:.0f} el {az[c0]*0+el[c0]:.0f}; ring columns driven per frame ~{int((np.abs(r-7)<1).sum())}")
print("mixing an ideal directional pattern with a non-directional one (all subtypes on the ring); MIX = non-directional fraction")
print(f"{'MIX':5s} {'expand LPLC2_L':>15s} {'contract':>9s} {'ratio':>6s}   {'GF exp/con':>10s}")
for MIX in [0.0, 0.25, 0.5, 0.75, 0.9, 1.0]:
    globals()["MIX"] = MIX; e = run("expand"); c = run("contract")
    print(f"{MIX:5.2f} {e['LPLC2_L']:15d} {c['LPLC2_L']:9d} {e['LPLC2_L']/max(c['LPLC2_L'],1):6.1f}   {e['GF']:4d}/{c['GF']:<4d}", flush=True)
