"""
omma.py - the ommatidium raytracer. scene -> luminance per retinal column.

Each column is one apposition-eye pixel: a bundle of rays jittered inside a gaussian
acceptance cone (half-width at half-max RHO deg, Drosophila ~4.5-5), averaged.
Scene is analytic for now: sky gradient, ground plane, dark spheres. Same sampler
works on a cubemap later.

    from omma import Eye, Scene
    eye = Eye()                                  # loads seam/eye_geom.npz
    lum = eye.render(scene, pos, heading)        # (n_columns,) in [0,1]
"""
import numpy as np
RHO = 4.5; N_RAYS = 24
try:
    from numba import njit, prange
    _HAVE_NUMBA = True
except ImportError:  # pragma: no cover
    _HAVE_NUMBA = False


if _HAVE_NUMBA:
    @njit(cache=True, parallel=True)
    def _shade_kernel(origin, d, sky, ground, soft, has_drum, drum, has_walls, walls, pillars, spheres, lum):
        """same primitives as Scene.shade, one ray per iteration. drum = (period, phase, lo, hi, half_height); walls = (half, height, albedo);
        pillars (k, 5) = x, y, r, albedo, height (standing on z = 0); spheres (k, 5) = cx, cy, cz, r, albedo."""
        ox, oy, oz = origin[0], origin[1], origin[2]
        for i in prange(d.shape[0]):
            dx, dy, dz = d[i, 0], d[i, 1], d[i, 2]
            band = 0.5 + dz / soft
            if band < 0.0: band = 0.0
            if band > 1.0: band = 1.0
            l = ground + (sky - ground) * band
            if has_drum:
                s = dz
                if s < -1.0: s = -1.0
                if s > 1.0: s = 1.0
                elv = np.degrees(np.arcsin(s))
                if abs(elv) < drum[4]:
                    az = np.degrees(np.arctan2(dy, dx))
                    l = drum[2] if (np.floor((az - drum[1]) / (drum[0] / 2)) % 2) == 0 else drum[3]
            tmin = np.inf
            if has_walls:
                for w in range(4):
                    axis = 0 if w < 2 else 1; sgn = 1.0 if (w % 2) == 0 else -1.0
                    dd = dx if axis == 0 else dy; oo = ox if axis == 0 else oy
                    if abs(dd) > 1e-9:
                        t = (sgn * walls[0] - oo) / dd
                        if t > 0 and t < tmin:
                            hp = (oy + t * dy) if axis == 0 else (ox + t * dx); hz = oz + t * dz
                            if abs(hp) <= walls[0] + 1e-6 and hz >= 0 and hz <= walls[1]:
                                tmin = t; l = walls[2]
            for k in range(pillars.shape[0]):
                px, py, r, alb, ph = pillars[k, 0], pillars[k, 1], pillars[k, 2], pillars[k, 3], pillars[k, 4]
                cx = ox - px; cy = oy - py; a = dx * dx + dy * dy; bq = cx * dx + cy * dy; cq = cx * cx + cy * cy - r * r
                disc = bq * bq - a * cq
                if disc > 0 and a > 1e-9:
                    t = (-bq - np.sqrt(disc)) / a
                    if t > 0 and t < tmin:
                        hz = oz + t * dz
                        if hz >= 0 and hz <= ph:
                            tmin = t; l = alb
            for k in range(spheres.shape[0]):
                cx = ox - spheres[k, 0]; cy = oy - spheres[k, 1]; cz = oz - spheres[k, 2]; r = spheres[k, 3]
                b = dx * cx + dy * cy + dz * cz; disc = b * b - (cx * cx + cy * cy + cz * cz - r * r)
                if disc > 0:
                    t = -b - np.sqrt(disc)
                    if t > 0 and t < tmin:
                        tmin = t; l = spheres[k, 4]
            lum[i] = l

class Scene:
    def __init__(self, sky=0.85, ground=0.35, horizon_soft=0.15, spheres=(), drum=None, pillars=(), walls=None, pillar_height=1.5):
        self.sky, self.ground, self.soft = sky, ground, horizon_soft; self.pillar_height = pillar_height
        self.walls = walls                       # None or dict(half, height, albedo): a square room |x|,|y| <= half, walls from the floor to `height`
        self.spheres = list(spheres)             # (centre xyz, radius, albedo)
        self.pillars = list(pillars)             # (x, y, radius, albedo): vertical cylinders, floor to sky
        self.drum = drum                         # None or dict(period_deg, phase_deg, lo, hi, half_height_deg): a striped cylinder at infinity
    def shade(self, origin, d, numpy=False):
        """d: (N,3) unit rays from origin. returns (N,) luminance. compiled path unless numpy=True (kept for checking)."""
        if _HAVE_NUMBA and not numpy:
            dr = self.drum; drum = np.array([dr["period_deg"], dr["phase_deg"], dr["lo"], dr["hi"], dr["half_height_deg"]], np.float64) if dr is not None else np.zeros(5)
            wl = self.walls; walls = np.array([wl["half"], wl["height"], wl["albedo"]], np.float64) if wl is not None else np.zeros(3)
            pil = np.array([[p[0], p[1], p[2], p[3], (p[4] if len(p) > 4 else self.pillar_height)] for p in self.pillars], np.float64).reshape(-1, 5)
            sph = np.array([[c[0], c[1], c[2], r, a] for c, r, a in self.spheres], np.float64).reshape(-1, 5)
            lum = np.empty(len(d), np.float32)
            _shade_kernel(np.asarray(origin, np.float64), np.ascontiguousarray(d, np.float64), float(self.sky), float(self.ground), float(self.soft), dr is not None, drum, wl is not None, walls, pil, sph, lum)
            return lum
        lum = np.where(d[:, 2] > 0, self.sky, self.ground).astype(np.float32)
        band = np.clip(0.5 + d[:, 2] / self.soft, 0, 1); lum = self.ground + (self.sky - self.ground) * band
        if self.drum is not None:
            dr = self.drum; az = np.degrees(np.arctan2(d[:, 1], d[:, 0])); elv = np.degrees(np.arcsin(np.clip(d[:, 2], -1, 1)))
            band = np.abs(elv) < dr["half_height_deg"]; stripe = ((az - dr["phase_deg"]) // (dr["period_deg"] / 2)) % 2 == 0
            lum = np.where(band, np.where(stripe, dr["lo"], dr["hi"]), lum).astype(np.float32)
        tmin = np.full(len(d), np.inf)
        if self.walls is not None:                     # four axis-aligned planes; the fly is inside, so the nearest forward hit is the wall it faces
            wl = self.walls
            for axis, sgn in ((0, 1), (0, -1), (1, 1), (1, -1)):
                dd = d[:, axis]; t = np.where(np.abs(dd) > 1e-9, (sgn * wl["half"] - origin[axis]) / np.where(np.abs(dd) > 1e-9, dd, 1.0), np.inf)
                oth = 1 - axis; hp = origin[oth] + t * d[:, oth]; hz = origin[2] + t * d[:, 2]
                ok = (t > 0) & (np.abs(hp) <= wl["half"] + 1e-6) & (hz >= 0) & (hz <= wl["height"]) & (t < tmin); tmin[ok] = t[ok]; lum[ok] = wl["albedo"]
        for pil in self.pillars:                       # ray-cylinder in the xy plane, standing on the floor (z = 0) up to `height` (default 1.5 m)
            px, py, r, alb = pil[:4]; ph = pil[4] if len(pil) > 4 else self.pillar_height
            ox, oy = origin[0] - px, origin[1] - py; a = d[:, 0] ** 2 + d[:, 1] ** 2; bq = ox * d[:, 0] + oy * d[:, 1]; cq = ox * ox + oy * oy - r * r
            disc = bq * bq - a * cq; hit = (disc > 0) & (a > 1e-9); t = (-bq - np.sqrt(np.where(hit, disc, 0))) / np.maximum(a, 1e-9)
            hz = origin[2] + t * d[:, 2]; ok = hit & (t > 0) & (t < tmin) & (hz >= 0) & (hz <= ph); tmin[ok] = t[ok]; lum[ok] = alb
        for c, r, alb in self.spheres:
            oc = origin - c; b = d @ oc; disc = b * b - (oc @ oc - r * r)
            hit = disc > 0; t = -b - np.sqrt(np.where(hit, disc, 0))
            ok = hit & (t > 0) & (t < tmin); tmin[ok] = t[ok]; lum[ok] = alb
        return lum

class Eye:
    def __init__(self, path="seam/eye_geom.npz", seed=0):
        g = np.load(path); self.side = g["side"]; self.dir0 = g["dir"]; self.hex1 = g["hex1"]; self.hex2 = g["hex2"]
        self.n = len(self.side); rng = np.random.default_rng(seed)
        # fixed jitter pattern per column: gaussian in the tangent plane, sigma = RHO / sqrt(2 ln 2)
        sig = np.radians(RHO) / np.sqrt(2 * np.log(2))
        self.jit = rng.normal(0, sig, size=(self.n, N_RAYS, 2)).astype(np.float32)
        u = np.cross(self.dir0, [0, 0, 1.0]); bad = np.linalg.norm(u, axis=1) < 1e-6; u[bad] = [1.0, 0, 0]
        u /= np.linalg.norm(u, axis=1, keepdims=True); v = np.cross(self.dir0, u)
        self.rays0 = (self.dir0[:, None, :] + self.jit[:, :, 0, None] * u[:, None, :] + self.jit[:, :, 1, None] * v[:, None, :])
        self.rays0 /= np.linalg.norm(self.rays0, axis=2, keepdims=True)
    def render(self, scene, pos=(0, 0, 0.5), heading_deg=0.0):
        h = np.radians(heading_deg); R = np.array([[np.cos(h), -np.sin(h), 0], [np.sin(h), np.cos(h), 0], [0, 0, 1]])
        rays = self.rays0.reshape(-1, 3) @ R.T
        lum = scene.shade(np.asarray(pos, float), rays).reshape(self.n, N_RAYS)
        return lum.mean(1)
    def picture(self, lum, path, title=""):
        """both retinas as az/el scatter, coloured by luminance."""
        import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
        az = np.degrees(np.arctan2(self.dir0[:, 1], self.dir0[:, 0])); el = np.degrees(np.arcsin(np.clip(self.dir0[:, 2], -1, 1)))
        fig, ax = plt.subplots(figsize=(11, 4.5)); ax.set_facecolor("k")
        ax.scatter(az, el, c=lum, cmap="gray", vmin=0, vmax=1, s=14); ax.set_xlim(190, -190); ax.set_ylim(-95, 95)
        ax.set_xlabel("azimuth (deg; left of fly is left of plot)"); ax.set_ylabel("elevation"); ax.set_title(title)
        fig.tight_layout(); fig.savefig(path, dpi=110); plt.close(fig)

if __name__ == "__main__":
    import time
    eye = Eye(); t0 = time.time()
    scene = Scene(spheres=[(np.array([3.0, 0.0, 0.6]), 0.6, 0.05), (np.array([1.5, 2.5, 0.5]), 0.4, 0.1)])
    lum = eye.render(scene); print(f"{eye.n} columns x {N_RAYS} rays in {1000*(time.time()-t0):.1f} ms")
    eye.picture(lum, "docs/figures/fly_sees.png", "what he sees: a dark ball 3 m ahead, a smaller one at 60 deg left")
    print("wrote seam/fly_sees.png; lum range", lum.min().round(2), lum.max().round(2))
