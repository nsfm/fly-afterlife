"""
eye_geom.py - a viewing direction for every retinal column of each eye.

FROM THE DATA
  - the column lattice: assignedOlHex1/2 per lamina column, ~880 per eye. neighbour
    test (seam session 2026-09-15): interior columns have six neighbours under the
    convention where (+1,+1) is a neighbour, i.e. standard axial (q, r) = (hex1, -hex2).
    all three lattice axes then span 36-39 columns: a regular hexagonal eye.
  - the dorsal rim: R7d/R8d photoreceptors (polarization vision, a thin strip along
    the dorsal margin of every fly eye) -> their strongest hex-tagged postsynaptic
    partner gives their column. dorsal = direction from the sheet centroid to the
    DRA centroid, per eye.

CHOICES (labelled)
  - interommatidial angle 6.3 deg horizontal, 4.4 deg vertical (anisotropic; chosen 2026-09-16 so the
    frontal edge reaches the midline at the equator - with 5.0 uniform there was a 35 deg blind wedge
    dead ahead; male acute zone not modelled).
  - azimuthal-equidistant wrap of the flat sheet onto the sphere about the optical
    axis (right eye: az +90, el +15; left mirrored). one column = IOA deg of arc.
  - FRONT_SIGN: which in-sheet direction (perpendicular to dorsal) is the front of the
    fly. +1 for now; the rotating-world HS test decides.

Writes seam/eye_geom.npz: side, hex1, hex2, sx, sy (sheet coords in columns: +sx =
front, +sy = dorsal), az, el (deg), dir (unit vectors, fly frame +x fwd +y left +z up).
"""
import argparse, numpy as np, pandas as pd, pyarrow.feather as pf
_ap = argparse.ArgumentParser(); _ap.add_argument("--sign", type=int, default=-1); _ap.add_argument("--out", default="seam/eye_geom.npz"); _a = _ap.parse_args()
IOA_H, IOA_V, AXIS_AZ, AXIS_EL, FRONT_SIGN = 6.3, 4.4, 90.0, 15.0, _a.sign   # deg per column, horizontal / vertical (anisotropic lattice; chosen so the frontal edge reaches ~-5 deg at the equator and the vertical extent stays ~+-70)

c = np.load("seam/t4t5_columns.npz")
cols = sorted({(str(s), int(a), int(b)) for s, a, b in zip(c["side"], c["hex1"], c["hex2"])})
side = np.array([s for s, _, _ in cols]); h1 = np.array([a for _, a, _ in cols]); h2 = np.array([b for _, _, b in cols])

# --- DRA columns from the wiring ------------------------------------------------------
d = np.load("brain_whole.npz"); ty = d["type"].astype(str); nside = d["side"].astype(str); bid = d["bodyId"]; pre, post, w = d["pre"], d["post"], d["w"]
a = pf.read_table("data/body-annotations-male-cns-v1.0-minconf-0.5.feather", columns=["bodyId", "assignedOlHex1", "assignedOlHex2"]).to_pandas().set_index("bodyId")
H1 = a.assignedOlHex1.reindex(bid).to_numpy(); H2 = a.assignedOlHex2.reindex(bid).to_numpy(); has = ~np.isnan(H1)
dra = np.flatnonzero(np.isin(ty, ["R7d", "R8d"])); m = np.isin(pre, dra) & has[post]
df = pd.DataFrame({"c": pre[m], "w": w[m], "h1": H1[post[m]].astype(int), "h2": H2[post[m]].astype(int)})
g = df.groupby(["c", "h1", "h2"]).w.sum().reset_index().sort_values("w", ascending=False).drop_duplicates("c")
g["side"] = nside[g.c.to_numpy()]

# --- axial (q, r) = (h1, -h2) -> pointy-top cartesian, in column units ----------------
def sheet(q, r): return q + r / 2.0, r * np.sqrt(3) / 2.0
x, y = sheet(h1.astype(float), -h2.astype(float))
out = {"side": side, "hex1": h1, "hex2": h2, "sx": np.zeros(len(cols)), "sy": np.zeros(len(cols)),
       "az": np.zeros(len(cols)), "el": np.zeros(len(cols)), "dir": np.zeros((len(cols), 3))}
def sph(az, el):
    az, el = np.radians(az), np.radians(el); return np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
for s, sgn in (("R", -1), ("L", +1)):
    k = side == s; cx, cy = x[k].mean(), y[k].mean()
    gd = g[g.side == s]; dx, dy = sheet(gd.h1.to_numpy(float), -gd.h2.to_numpy(float))
    dv = np.array([dx.mean() - cx, dy.mean() - cy]); dv /= np.linalg.norm(dv)
    rot = np.pi / 2 - np.arctan2(dv[1], dv[0])          # bring dorsal to +y
    xs, ys = x[k] - cx, y[k] - cy
    sy = xs * np.sin(rot) + ys * np.cos(rot); sx = (xs * np.cos(rot) - ys * np.sin(rot)) * FRONT_SIGN
    out["sx"][k] = sx; out["sy"][k] = sy
    axis = sph(sgn * AXIS_AZ, AXIS_EL)
    up = np.array([0, 0, 1.0]) - axis * axis[2]; up /= np.linalg.norm(up)
    front = np.array([1.0, 0, 0]) - axis * axis[0]; front /= np.linalg.norm(front)
    rr = np.radians(np.hypot(sx * IOA_H, sy * IOA_V)); th = np.arctan2(sy * IOA_V, sx * IOA_H)
    dirs = np.cos(rr)[:, None] * axis + np.sin(rr)[:, None] * (np.cos(th)[:, None] * front + np.sin(th)[:, None] * up)
    dirs /= np.linalg.norm(dirs, axis=1, keepdims=True); out["dir"][k] = dirs
    out["az"][k] = np.degrees(np.arctan2(dirs[:, 1], dirs[:, 0])); out["el"][k] = np.degrees(np.arcsin(np.clip(dirs[:, 2], -1, 1)))
    print(f"eye {s}: {k.sum()} columns; DRA {len(gd)} cells, dorsal vector in sheet {dv.round(2)}; sheet extent sx {sx.min():.0f}..{sx.max():.0f} sy {sy.min():.0f}..{sy.max():.0f}; "
          f"az {out['az'][k].min():.0f}..{out['az'][k].max():.0f} el {out['el'][k].min():.0f}..{out['el'][k].max():.0f}")
    # where do the DRA columns land after the wrap? (should be the top edge)
    dk = np.isin(list(zip(h1[k], h2[k])), list(zip(gd.h1, gd.h2))) if False else np.array([(p, q_) in set(zip(gd.h1, gd.h2)) for p, q_ in zip(h1[k], h2[k])])
    print(f"        DRA columns after wrap: median el {np.median(out['el'][k][dk]):.0f} deg (eye median {np.median(out['el'][k]):.0f})")
np.savez(_a.out, **out)
fr = np.abs(out["az"]) < 15
print(f"frontal wedge |az|<15: L {fr[side=='L'].sum()} R {fr[side=='R'].sum()} columns")
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(11, 4.5))
for s, col in (("L", "tab:blue"), ("R", "tab:red")):
    k = side == s; ax.scatter(out["az"][k], out["el"][k], s=6, c=col, label=f"{s} eye")
ax.set_xlim(190, -190); ax.set_ylim(-95, 95); ax.set_xlabel("azimuth (deg; 0 ahead, left of fly = left of plot)"); ax.set_ylabel("elevation"); ax.legend(); ax.set_title("where each retinal column looks")
fig.tight_layout(); fig.savefig(_a.out.replace(".npz", ".png"), dpi=110)
