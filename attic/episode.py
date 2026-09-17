"""
episode.py - an arena, a scripted walk, and everything a viewer needs per frame.

    uv run python world/episode.py --out world/ep0.npz [--seconds 6] [--fps 100]

world: ground plane z=0, sky gradient, 8 dark posts (spheres r=0.2 at eye height 0.5)
scattered in a 6x6 m arena, one bright ball. the fly walks at 0.3 m/s with a scripted
yaw profile (straight, left 60 deg, straight, right 90 deg, straight, left 30 deg).

per frame, from the SAME raytracer (omma.Scene.shade):
  lum      (T, n_columns)   what each retinal column samples (both eyes)
  human    (T, H, W) uint8  pinhole first-person raster, FOV 150 deg, from the fly's eye height, heading fwd
and from the object list, for the viewer's independent top-down drawing:
  pose     (T, 3)  x, y, heading_deg
  objects  (N, 4)  x, y, radius, albedo
"""
import sys, argparse, numpy as np
sys.path.insert(0, "seam")
from omma import Eye, Scene
ap = argparse.ArgumentParser(); ap.add_argument("--out", default="world/ep0.npz"); ap.add_argument("--seconds", type=float, default=6.0)
ap.add_argument("--fps", type=int, default=100); ap.add_argument("--hw", type=int, nargs=2, default=[90, 160]); ap.add_argument("--fov", type=float, default=150.0)
ap.add_argument("--seed", type=int, default=1); args = ap.parse_args()
rng = np.random.default_rng(args.seed); T = int(args.seconds * args.fps)
posts = [(x, y, 0.2, 0.05) for x, y in rng.uniform(-2.5, 2.5, size=(8, 2)) if np.hypot(x + 2.0, y) > 0.8]
objects = np.array(posts + [(1.5, 1.0, 0.25, 1.0)], np.float32)     # last one is the bright ball
scene = Scene(spheres=[(np.array([x, y, 0.5]), r, a) for x, y, r, a in objects])
# scripted walk
speed = 0.3; segs = [(1.0, 0.0), (1.0, +60.0), (1.0, 0.0), (1.0, -90.0), (1.0, 0.0), (1.0, +30.0)]   # (seconds, total yaw over the segment)
pose = np.zeros((T, 3), np.float32); x, y, h = -2.0, 0.0, 0.0; f = 0
for sec, yaw in segs:
    n = int(sec * args.fps)
    for i in range(n):
        if f >= T: break
        h += yaw / n; x += speed / args.fps * np.cos(np.radians(h)); y += speed / args.fps * np.sin(np.radians(h)); pose[f] = (x, y, h); f += 1
while f < T: pose[f] = pose[f - 1]; f += 1
eye = Eye("seam/eye_geom.npz")
H, W = args.hw; fov = np.radians(args.fov); ys, xs = np.mgrid[0:H, 0:W]
px = (xs + 0.5) / W * 2 - 1; py = 1 - (ys + 0.5) / H * 2; fx = np.tan(fov / 2); fy = fx * H / W
cam = np.stack([np.ones_like(px), -px * fx, py * fy], -1).reshape(-1, 3); cam /= np.linalg.norm(cam, axis=1, keepdims=True)   # +x fwd, +y left, +z up
lum = np.zeros((T, eye.n), np.float32); human = np.zeros((T, H, W), np.uint8)
for t in range(T):
    x, y, h = pose[t]; hr = np.radians(h); R = np.array([[np.cos(hr), -np.sin(hr), 0], [np.sin(hr), np.cos(hr), 0], [0, 0, 1]])
    lum[t] = eye.render(scene, pos=(x, y, 0.5), heading_deg=h)
    human[t] = (np.clip(scene.shade(np.array([x, y, 0.5]), cam @ R.T).reshape(H, W), 0, 1) * 255).astype(np.uint8)
np.savez_compressed(args.out, lum=lum, human=human, pose=pose, objects=objects, fps=args.fps, fov=args.fov,
                    az=np.degrees(np.arctan2(eye.dir0[:, 1], eye.dir0[:, 0])).astype(np.float32), el=np.degrees(np.arcsin(np.clip(eye.dir0[:, 2], -1, 1))).astype(np.float32), side=eye.side)
print(f"{T} frames, {eye.n} columns, human {H}x{W} fov {args.fov}; objects {len(objects)}; path from {pose[0][:2].round(2)} to {pose[-1][:2].round(2)} -> {args.out}")
