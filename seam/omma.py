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
    def _shade_kernel(origin, d, sky, ground, soft, has_drum, drum, has_walls, walls, pillars, spheres, lum, has_floor, floor_tex, floor_half, discs, has_sun, sun, has_ring, ring):
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
            if has_sun and dz > 0:
                ca = dx * sun[0] + dy * sun[1] + dz * sun[2]
                if ca > 0: l += sun[3] * ca ** sun[4]
                if sun[5] > 0.0 and ca > sun[5]: l = sun[6]   # the disc: within cos(half-angle) of the sun, a clipped luminance (09-18)
            tmin = np.inf
            if has_floor and dz < -1e-9:
                t = -oz / dz
                if t < tmin:
                    hx = ox + t * dx; hy = oy + t * dy; H = floor_tex.shape[0]; W = floor_tex.shape[1]
                    ix = int((hx + floor_half) / (2 * floor_half) * W); iy = int((hy + floor_half) / (2 * floor_half) * H)
                    if ix < 0: ix = 0
                    if ix > W - 1: ix = W - 1
                    if iy < 0: iy = 0
                    if iy > H - 1: iy = H - 1
                    tmin = t; l = floor_tex[iy, ix]
            for k in range(discs.shape[0]):
                if abs(dz) > 1e-9:
                    t = (discs[k, 2] - oz) / dz
                    if t > 0 and t < tmin:
                        hx = ox + t * dx; hy = oy + t * dy
                        if (hx - discs[k, 0]) ** 2 + (hy - discs[k, 1]) ** 2 <= discs[k, 3] * discs[k, 3]:
                            tmin = t; l = discs[k, 4]
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
            if has_ring:   # a cylinder wall seen from inside: radius ring[0], height ring[1], albedo ring[2]; the far root of the quadratic
                a_ = dx * dx + dy * dy
                if a_ > 1e-12:
                    b_ = 2.0 * (ox * dx + oy * dy); c_ = ox * ox + oy * oy - ring[0] * ring[0]; disc_ = b_ * b_ - 4.0 * a_ * c_
                    if disc_ > 0:
                        t = (-b_ + np.sqrt(disc_)) / (2.0 * a_)
                        if t > 0 and t < tmin:
                            hz = oz + t * dz
                            if hz >= 0 and hz <= ring[1]:
                                tmin = t; l = ring[2]
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
    def __init__(self, sky=0.85, ground=0.35, horizon_soft=0.15, spheres=(), drum=None, pillars=(), walls=None, pillar_height=1.5, floor=None, discs=(), sun=None, ring=None):
        self.sky, self.ground, self.soft = sky, ground, horizon_soft; self.pillar_height = pillar_height
        self.floor = floor                       # None = the sky/ground gradient by ray direction (the room); else dict(tex=(H,W) float32 luminance albedo, half=extent in m): a real plane at z = 0
        self.discs = list(discs)                 # (x, y, z, r, albedo): horizontal discs (leaves, a puddle), seen from below and above
        self.sun = sun                           # None or dict(dir=(dx, dy, dz) unit, boost, k): sky brightens toward the sun as boost * max(0, d.dir)^k
        self.ring = ring                         # None or dict(radius, height, albedo): a circular wall seen from inside (the open-field arena, 09-18)
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
            fl = self.floor; ftex = np.ascontiguousarray(fl["tex"], np.float32) if fl is not None else np.zeros((1, 1), np.float32); fhalf = float(fl["half"]) if fl is not None else 1.0
            dsc = np.array([[x, y, z, r, a] for x, y, z, r, a in self.discs], np.float64).reshape(-1, 5)
            sn = self.sun; sunv = np.zeros(7)
            if sn is not None: sd = np.asarray(sn["dir"], float); sd = sd / np.linalg.norm(sd); sunv = np.array([sd[0], sd[1], sd[2], sn["boost"], sn["k"], (np.cos(np.radians(sn["disc_deg"])) if sn.get("disc_deg", 0) > 0 else 0.0), sn.get("disc_lum", 1.0)], np.float64)
            _shade_kernel(np.asarray(origin, np.float64), np.ascontiguousarray(d, np.float64), float(self.sky), float(self.ground), float(self.soft), dr is not None, drum, wl is not None, walls, pil, sph, lum, fl is not None, ftex, fhalf, dsc, sn is not None, sunv, self.ring is not None, (np.array([self.ring["radius"], self.ring["height"], self.ring["albedo"]], np.float64) if self.ring is not None else np.zeros(3)))
            return np.clip(lum, 0, 1) if sn is not None else lum
        lum = np.where(d[:, 2] > 0, self.sky, self.ground).astype(np.float32)
        band = np.clip(0.5 + d[:, 2] / self.soft, 0, 1); lum = self.ground + (self.sky - self.ground) * band
        if self.drum is not None:
            dr = self.drum; az = np.degrees(np.arctan2(d[:, 1], d[:, 0])); elv = np.degrees(np.arcsin(np.clip(d[:, 2], -1, 1)))
            band = np.abs(elv) < dr["half_height_deg"]; stripe = ((az - dr["phase_deg"]) // (dr["period_deg"] / 2)) % 2 == 0
            lum = np.where(band, np.where(stripe, dr["lo"], dr["hi"]), lum).astype(np.float32)
        if self.sun is not None:
            sd = np.asarray(self.sun["dir"], float); sd /= np.linalg.norm(sd); cosang = np.clip(d @ sd, 0, 1)
            lum = np.where(d[:, 2] > 0, lum + self.sun["boost"] * cosang ** self.sun["k"], lum).astype(np.float32)
            if self.sun.get("disc_deg", 0) > 0: lum = np.where((d[:, 2] > 0) & (cosang > np.cos(np.radians(self.sun["disc_deg"]))), np.float32(self.sun.get("disc_lum", 1.0)), lum).astype(np.float32)
        tmin = np.full(len(d), np.inf)
        if self.floor is not None:                     # the ground is a plane at z = 0 with a texture; the horizon gradient only above it
            fl = self.floor; down = d[:, 2] < -1e-9; t = np.where(down, -origin[2] / np.where(down, d[:, 2], -1.0), np.inf)
            hx = origin[0] + t * d[:, 0]; hy = origin[1] + t * d[:, 1]; tex = fl["tex"]; H, W = tex.shape; half = fl["half"]
            ix = np.clip(((hx + half) / (2 * half) * W).astype(np.int64), 0, W - 1); iy = np.clip(((hy + half) / (2 * half) * H).astype(np.int64), 0, H - 1)
            ok = down & (t < tmin); tmin[ok] = t[ok]; lum[ok] = tex[iy[ok], ix[ok]]
        for dx_, dy_, dz_, r_, alb_ in self.discs:     # horizontal disc at height dz_
            dd = d[:, 2]; t = np.where(np.abs(dd) > 1e-9, (dz_ - origin[2]) / np.where(np.abs(dd) > 1e-9, dd, 1.0), np.inf)
            hx = origin[0] + t * d[:, 0]; hy = origin[1] + t * d[:, 1]; ok = (t > 0) & (t < tmin) & ((hx - dx_) ** 2 + (hy - dy_) ** 2 <= r_ * r_); tmin[ok] = t[ok]; lum[ok] = alb_
        if self.walls is not None:                     # four axis-aligned planes; the fly is inside, so the nearest forward hit is the wall it faces
            wl = self.walls
            for axis, sgn in ((0, 1), (0, -1), (1, 1), (1, -1)):
                dd = d[:, axis]; t = np.where(np.abs(dd) > 1e-9, (sgn * wl["half"] - origin[axis]) / np.where(np.abs(dd) > 1e-9, dd, 1.0), np.inf)
                oth = 1 - axis; hp = origin[oth] + t * d[:, oth]; hz = origin[2] + t * d[:, 2]
                ok = (t > 0) & (np.abs(hp) <= wl["half"] + 1e-6) & (hz >= 0) & (hz <= wl["height"]) & (t < tmin); tmin[ok] = t[ok]; lum[ok] = wl["albedo"]
        if self.ring is not None:                      # a cylinder wall seen from inside: the far root
            rg = self.ring; a_ = d[:, 0] ** 2 + d[:, 1] ** 2; b_ = 2 * (origin[0] * d[:, 0] + origin[1] * d[:, 1]); c_ = origin[0] ** 2 + origin[1] ** 2 - rg["radius"] ** 2
            disc_ = b_ * b_ - 4 * a_ * c_; ok0 = (a_ > 1e-12) & (disc_ > 0); t = np.where(ok0, (-b_ + np.sqrt(np.where(ok0, disc_, 0.0))) / np.where(ok0, 2 * a_, 1.0), np.inf)
            hz = origin[2] + t * d[:, 2]; ok = ok0 & (t > 0) & (hz >= 0) & (hz <= rg["height"]) & (t < tmin); tmin[ok] = t[ok]; lum[ok] = rg["albedo"]
        for pil in self.pillars:                       # ray-cylinder in the xy plane, standing on the floor (z = 0) up to `height` (default 1.5 m)
            px, py, r, alb = pil[:4]; ph = pil[4] if len(pil) > 4 else self.pillar_height
            ox, oy = origin[0] - px, origin[1] - py; a = d[:, 0] ** 2 + d[:, 1] ** 2; bq = ox * d[:, 0] + oy * d[:, 1]; cq = ox * ox + oy * oy - r * r
            disc = bq * bq - a * cq; hit = (disc > 0) & (a > 1e-9); t = (-bq - np.sqrt(np.where(hit, disc, 0))) / np.maximum(a, 1e-9)
            hz = origin[2] + t * d[:, 2]; ok = hit & (t > 0) & (t < tmin) & (hz >= 0) & (hz <= ph); tmin[ok] = t[ok]; lum[ok] = alb
        for c, r, alb in self.spheres:
            oc = origin - c; b = d @ oc; disc = b * b - (oc @ oc - r * r)
            hit = disc > 0; t = -b - np.sqrt(np.where(hit, disc, 0))
            ok = hit & (t > 0) & (t < tmin); tmin[ok] = t[ok]; lum[ok] = alb
        return np.clip(lum, 0, 1) if self.sun is not None else lum   # the sun can push the sky past 1; the eye sees [0, 1]

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
