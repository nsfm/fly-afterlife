"""
world_flyvis.py - render a scene through both compound eyes and run flyvis per eye.

    uv run python seam/world_flyvis.py --stim loom_ahead --out seam/world_loom_ahead.npz

Pipeline per frame: omma.Eye.render -> luminance per retinal column -> that column's
flyvis hex (u, v) -> (T, 721) movie per eye -> flyvis network 000 -> activity per type.

THE COLUMN -> FLYVIS MAP IS DERIVED, NOT SWEPT. flyvis's T4a prefers image-left,
T4c image-up (measured, flyvis_dirs.py). biological T4a prefers FRONT-TO-BACK motion, so
the front must sit at image-RIGHT for front-to-back to run toward image-left. our
dorsal is known from the DRA. so: our sheet +sx (front) -> flyvis image-right, our
+sy (dorsal) -> flyvis image-up. (first draft had front at image-left; HS under yaw
came out on the wrong side and the synthetic T4a/T4b -> HS test made the reason plain.) flyvis BoxEye places hex (u, v) at image
(row = u + v/2, col = v), rows increasing downward. hence  v = +sx,  u = -sy - v/2.
columns outside the 721-hex lattice are not rendered into flyvis and get no drive.

Stimuli (2 s, 100 fps, fly at origin heading +x, ground at z=0, eye at z=0.5):
  loom_ahead   dark ball approaches from straight ahead, hits at t=2 s
  loom_left    same, from 60 deg left
  loom_right   same, from 60 deg right
  recede_ahead ball starts at contact distance ahead, moves away
  yaw_left     fly rotates left at 90 deg/s in a world with a dark ball ring (HS test)
  yaw_right    mirror
  static_ahead ball hangs 1.0 m ahead

Writes: {eye}_{type}: (T, 721) activity; {eye}_u/v/col: the per-column lattice map
(col = index into eye_geom's column list, -1 if unmapped); lum_{eye}: (T, n_cols).
"""
import os, sys, argparse, time, numpy as np, torch
sys.path.insert(0, "seam")
os.environ.setdefault("FLYVIS_ROOT_DIR", "/home/nate/code/fly-afterlife/flyvis_data")
from omma import Eye, Scene
ap = argparse.ArgumentParser(); ap.add_argument("--stim", nargs="+", required=True); ap.add_argument("--out", default="seam/world")
ap.add_argument("--geom", default="seam/eye_geom.npz"); ap.add_argument("--fps", type=int, default=100); ap.add_argument("--seconds", type=float, default=2.0)
args = ap.parse_args()
T = int(args.fps * args.seconds); eye = Eye(args.geom); g = np.load(args.geom)

def ball_path(az_deg, t):
    """dark ball, radius 0.15, approaching along a bearing; distance 3 m -> 0.3 m over the last second."""
    az = np.radians(az_deg); dist = 3.0 if t < 1.0 else 3.0 - 2.6 * (t - 1.0)
    return (np.array([np.cos(az) * dist, np.sin(az) * dist, 0.5]), 0.3, 0.05)
def frame_scene(t):
    s = STIM
    if s == "loom_ahead":  return Scene(spheres=[ball_path(0, t)]), 0.0
    if s == "loom_left":   return Scene(spheres=[ball_path(60, t)]), 0.0
    if s == "loom_right":  return Scene(spheres=[ball_path(-60, t)]), 0.0
    if s in ("recede_left", "recede_right"):
        az = np.radians(60 if s == "recede_left" else -60); dist = 0.4 if t < 1.0 else 0.4 + 2.6 * (t - 1.0)
        return Scene(spheres=[(np.array([np.cos(az) * dist, np.sin(az) * dist, 0.5]), 0.3, 0.05)]), 0.0
    if s in ("static_left", "static_right"):
        az = np.radians(60 if s == "static_left" else -60)
        return Scene(spheres=[(np.array([np.cos(az) * 1.0, np.sin(az) * 1.0, 0.5]), 0.3, 0.05)]), 0.0
    if s == "recede_ahead":
        dist = 0.4 if t < 1.0 else 0.4 + 2.6 * (t - 1.0)
        return Scene(spheres=[(np.array([dist, 0, 0.5]), 0.3, 0.05)]), 0.0
    if s == "static_ahead": return Scene(spheres=[(np.array([1.0, 0, 0.5]), 0.3, 0.05)]), 0.0
    if s in ("yaw_left", "yaw_right"):
        ring = [(np.array([2 * np.cos(a), 2 * np.sin(a), 0.5]), 0.25, 0.05) for a in np.radians(np.arange(0, 360, 30))]
        h = 0.0 if t < 1.0 else (90.0 * (t - 1.0)) * (1 if s == "yaw_left" else -1)
        return Scene(spheres=ring), h
    raise SystemExit(f"unknown stim {s}")

# per-eye lattice map
out = {"fps": args.fps}
lattice = {(u, v) for u in range(-15, 16) for v in range(max(-15, -15 - u), min(15, 15 - u) + 1)}
idx_of = {uv: i for i, uv in enumerate(sorted(lattice))}   # flyvis node order within a type is by (u, v)? verified below
for s in "LR":
    k = np.flatnonzero(g["side"] == s)
    v = np.rint(+g["sx"][k]).astype(int); u = np.rint(-g["sy"][k] - v / 2.0).astype(int)   # front -> image-RIGHT, so front-to-back motion runs toward image-left = flyvis T4a
    col = np.array([idx_of.get((int(a), int(b)), -1) for a, b in zip(u, v)])
    out[f"{s}_u"], out[f"{s}_v"], out[f"{s}_col"], out[f"{s}_idx"] = u, v, col, k
    print(f"eye {s}: {(col >= 0).sum()} of {len(k)} columns inside the flyvis lattice")

import flyvis
from flyvis import NetworkView
nv = NetworkView("flow/0000/000"); net = nv.init_network(); net.eval()
nodes = net.connectome.nodes; ntype = nodes.type[:].astype(str); nu = nodes.u[:]; nv_ = nodes.v[:]
types = sorted(set(ntype)); out["types"] = np.array(types)
t4 = ntype == "T4a"; assert [tuple(x) for x in zip(nu[t4], nv_[t4])] == sorted(lattice), "flyvis node order is not sorted (u,v)"
base = dict(out)
for STIM in args.stim:
  out = dict(base)
  t0 = time.time(); lum = np.zeros((T, eye.n), np.float32)
  for f in range(T):
    scene, heading = frame_scene(f / args.fps); lum[f] = eye.render(scene, heading_deg=heading)
  out["lum"] = lum
  for s in "LR":
      k, col = out[f"{s}_idx"], out[f"{s}_col"]; ok = col >= 0
      movie = np.full((1, T, 1, 721), 0.5, np.float32); movie[0, :, 0, col[ok]] = lum[:, k[ok]].T
      with torch.no_grad():
          act = net.simulate(torch.tensor(movie, device=flyvis.device), dt=1 / args.fps, as_layer_activity=True)
      for ty in types: out[f"{s}_{ty}"] = np.asarray(getattr(act, ty).squeeze(0), dtype=np.float32)
      t45 = [out[f"{s}_{t}"] for t in ["T4a", "T4b", "T4c", "T4d", "T5a", "T5b", "T5c", "T5d"]]
      print(f"eye {s}: flyvis done; T4/T5 mean pre {np.mean([a[20:100].mean() for a in t45]):+.3f} during {np.mean([a[100:].mean() for a in t45]):+.3f} peak {max(a.max() for a in t45):.2f}")
  np.savez(f"{args.out}_{STIM}.npz", **out); print(f"{STIM}: rendered+flyvis in {time.time()-t0:.1f}s -> {args.out}_{STIM}.npz")
