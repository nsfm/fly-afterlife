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

class Scene:
    def __init__(self, sky=0.85, ground=0.35, horizon_soft=0.15, spheres=(), drum=None):
        self.sky, self.ground, self.soft = sky, ground, horizon_soft
        self.spheres = list(spheres)             # (centre xyz, radius, albedo)
        self.drum = drum                         # None or dict(period_deg, phase_deg, lo, hi, half_height_deg): a striped cylinder at infinity
    def shade(self, origin, d):
        """d: (N,3) unit rays from origin. returns (N,) luminance."""
        lum = np.where(d[:, 2] > 0, self.sky, self.ground).astype(np.float32)
        band = np.clip(0.5 + d[:, 2] / self.soft, 0, 1); lum = self.ground + (self.sky - self.ground) * band
        if self.drum is not None:
            dr = self.drum; az = np.degrees(np.arctan2(d[:, 1], d[:, 0])); elv = np.degrees(np.arcsin(np.clip(d[:, 2], -1, 1)))
            band = np.abs(elv) < dr["half_height_deg"]; stripe = ((az - dr["phase_deg"]) // (dr["period_deg"] / 2)) % 2 == 0
            lum = np.where(band, np.where(stripe, dr["lo"], dr["hi"]), lum).astype(np.float32)
        tmin = np.full(len(d), np.inf)
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
    eye.picture(lum, "seam/fly_sees.png", "what he sees: a dark ball 3 m ahead, a smaller one at 60 deg left")
    print("wrote seam/fly_sees.png; lum range", lum.min().round(2), lum.max().round(2))
