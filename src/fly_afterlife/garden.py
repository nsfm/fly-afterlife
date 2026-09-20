"""
garden: the enriched world (docs/GARDEN.md). a 6 x 6 m patch at fly scale with a textured floor, grass, leaves
with shade beneath, a stone, a fruit (odour plume, sugar on its skin), a puddle (humidity, water), a sun with a
warm patch, and a low rim. the world carries RGB; his eye gets a fly luminance (green-heavy, red-blind).

    g = Garden(seed=0)
    g.scene([her])                     # omma.Scene with floor texture, discs, pillars with heights, spheres, sun, rim
    g.temperature(x, y); g.humidity(x, y); g.odour(x, y, t)   # fields
    g.step_frame(him, her, fps)        # move, rim, grass / stone / fruit holds, puddle and fruit taste events, the pair
"""
from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np
from .world import Room
from .body import Body
from omma import Scene

FLY_RGB_W = np.array([0.20, 0.70, 0.10])     # R1-R6 are UV/green broadband and red-blind: green-heavy luminance (E)


def fly_lum(rgb) -> float:
    return float(np.dot(np.asarray(rgb, float), FLY_RGB_W))


def value_noise(rng, n, period_px, octaves=2):
    """cheap value noise on an n x n grid: bilinear interpolation of random lattices, summed over octaves."""
    out = np.zeros((n, n)); amp = 1.0
    for o in range(octaves):
        p = max(2, int(period_px / (2 ** o))); k = n // p + 2; lat = rng.random((k, k))
        ys, xs = np.mgrid[0:n, 0:n] / p; y0 = ys.astype(int); x0 = xs.astype(int); fy = ys - y0; fx = xs - x0
        fy = fy * fy * (3 - 2 * fy); fx = fx * fx * (3 - 2 * fx)
        v = (lat[y0, x0] * (1 - fx) + lat[y0, x0 + 1] * fx) * (1 - fy) + (lat[y0 + 1, x0] * (1 - fx) + lat[y0 + 1, x0 + 1] * fx) * fy
        out += amp * v; amp *= 0.5
    return (out - out.min()) / (out.max() - out.min() + 1e-9)


@dataclass
class Garden(Room):
    seed: int = 0
    n_grass: int = 30
    tex_px: int = 512
    wind: tuple = (1.0, 0.3)                      # wind direction (unit), the plume blows this way
    sun_dir: tuple = (0.6, 0.3, 0.74)
    grass: list = field(default_factory=list)     # (x, y, r, albedo, height)
    leaves: list = field(default_factory=list)    # (x, y, z, r, albedo)
    stone: tuple = None
    fruit: tuple = None
    puddle: tuple = None
    sunspot: tuple = None                         # (x, y, sigma): the warm sunlit patch
    tex: np.ndarray = None                        # (H, W) fly luminance albedo
    rgb: np.ndarray = None                        # (H, W, 3) uint8 for the viewer
    whiff: dict = field(default_factory=dict)     # per source: (state, until_t)
    events: list = field(default_factory=list)    # (t, who, what)

    def __post_init__(self):
        self.half = 3.0; self.height = 0.3; self.albedo = 0.5; self.sky = 0.85; self.ground = 0.35; self.posts = []
        rng = np.random.default_rng(self.seed); n = self.tex_px
        # the floor: soil and leaf litter, two scales (fine ~5 cm, patches ~40 cm at 6 m / 512 px = 1.2 cm per px)
        fine = value_noise(rng, n, period_px=4, octaves=2); coarse = value_noise(rng, n, period_px=34, octaves=2)
        soil = np.array([0.36, 0.26, 0.16]); litter = np.array([0.58, 0.47, 0.26]); moss = np.array([0.25, 0.40, 0.15])
        mix = np.clip(0.55 * coarse + 0.45 * fine, 0, 1)[..., None]; rgb = soil * (1 - mix) + litter * mix
        mossy = np.clip((coarse - 0.65) * 3, 0, 1)[..., None]; rgb = rgb * (1 - mossy) + moss * mossy
        # objects
        self.stone = (-1.6, 1.4, 0.3, 0.6, fly_lum((0.62, 0.60, 0.55)))
        self.fruit = (1.4, -1.2, 0.22, 0.3, fly_lum((0.62, 0.10, 0.10)))
        self.puddle = (-1.2, -1.6, 0.005, 0.55, fly_lum((0.20, 0.26, 0.36)))
        self.sunspot = (1.6, 1.6, 0.9)
        self.leaves = [(0.2, 0.9, 1.1, 0.8, fly_lum((0.18, 0.32, 0.12))), (-0.9, -0.2, 0.8, 0.6, fly_lum((0.20, 0.36, 0.14))), (2.0, 0.2, 1.4, 0.9, fly_lum((0.16, 0.30, 0.11)))]
        for _ in range(self.n_grass):
            x, y = rng.uniform(-2.7, 2.7, 2); self.grass.append((float(x), float(y), 0.03, fly_lum((0.22, 0.45, 0.16)), float(rng.uniform(0.5, 2.0))))
        # shade under the leaves and the sunlit patch, baked into the floor
        ys, xs = np.mgrid[0:n, 0:n]; wx = (xs + 0.5) / n * 6 - 3; wy = (ys + 0.5) / n * 6 - 3; shade = np.ones((n, n))
        for lx, ly, lz, lr, _ in self.leaves: shade *= 1 - 0.45 * np.clip(1 - (np.hypot(wx - lx, wy - ly) - lr) / 0.3, 0, 1)
        sx, sy, ss = self.sunspot; shade *= 1 + 0.25 * np.exp(-((wx - sx) ** 2 + (wy - sy) ** 2) / (2 * ss ** 2))
        rgb = np.clip(rgb * shade[..., None], 0, 1)
        self.rgb = (rgb * 255).astype(np.uint8); self.tex = (rgb @ FLY_RGB_W).astype(np.float32)
        self.wind = np.asarray(self.wind, float) / np.linalg.norm(self.wind)

    # ---- the eye's view
    def scene(self, others):
        sph = [(np.array([b.x, b.y, 0.5]), b.r, b.albedo) for b in others if b.present]
        sx, sy, sz, sr, sa = self.stone; fx, fy, fz, fr, fa = self.fruit; sph += [(np.array([sx, sy, sz]), sr, sa), (np.array([fx, fy, fz]), fr, fa)]
        px, py, pz, pr, pa = self.puddle
        return Scene(sky=self.sky, ground=self.ground, spheres=sph, pillars=list(self.grass), walls=dict(half=self.half, height=self.height, albedo=self.albedo),
                     floor=dict(tex=self.tex, half=self.half), discs=list(self.leaves) + [(px, py, pz, pr, pa)], sun=dict(dir=self.sun_dir, boost=0.3, k=10))

    # ---- the UV eye's view (09-18): the sky is the source (Rayleigh), the ground dark (vegetation and soil absorb UV), water a mirror,
    # the sun a clipped disc. albedos are estimates (E); the eye's acceptance angle supplies the bloom.
    UV = dict(sky=1.0, ground=0.06, floor=0.05, grass=0.04, leaf=0.04, stone=0.30, fruit=0.05, puddle=0.90, rim=0.15, her=0.05, disc_deg=2.5)

    def scene_uv(self, others):
        u = self.UV; sph = [(np.array([b.x, b.y, 0.5]), b.r, u["her"]) for b in others if b.present]
        sx, sy, sz, sr, _ = self.stone; fx, fy, fz, fr, _ = self.fruit; sph += [(np.array([sx, sy, sz]), sr, u["stone"]), (np.array([fx, fy, fz]), fr, u["fruit"])]
        px, py, pz, pr, _ = self.puddle
        if not hasattr(self, "_tex_uv"): tt = self.tex; self._tex_uv = (u["floor"] * (0.6 + 0.8 * (tt - tt.min()) / (tt.max() - tt.min() + 1e-9))).astype(np.float32)
        return Scene(sky=u["sky"], ground=u["ground"], spheres=sph, pillars=[(x, y, r, u["grass"], h) for x, y, r, _, h in self.grass], walls=dict(half=self.half, height=self.height, albedo=u["rim"]),
                     floor=dict(tex=self._tex_uv, half=self.half), discs=[(x, y, z, r, u["leaf"]) for x, y, z, r, _ in self.leaves] + [(px, py, pz, pr, u["puddle"])], sun=dict(dir=self.sun_dir, boost=0.4, k=6, disc_deg=u["disc_deg"], disc_lum=1.0))

    # ---- fields
    def _shade_at(self, x, y):
        s = 1.0
        for lx, ly, lz, lr, _ in self.leaves: s *= 1 - 0.45 * float(np.clip(1 - (np.hypot(x - lx, y - ly) - lr) / 0.3, 0, 1))
        return s

    OCELLI = dict(median=0.0, left=60.0, right=-60.0)   # where each ocellus looks, degrees of yaw from his heading; all three look up at the sky
    def sky_light(self, x, y, h):
        """the sky brightness each ocellus sees, 0..1 (09-19, the ocellar stand-in): the leaf shade sampled 0.3 m out along
        the ocellus's line of sight (the leaves are 0.8-1.4 m up: what is over him, roughly), times the sky, plus the sun's disc
        when it is in that ocellus's field (the sun is 27 deg azimuth, 48 deg up; boost 0.3 as the raytracer uses), over the
        open-sky-with-sun value so 1 = open sky facing the sun, ~0.7 = open sky facing away, ~0.4 = under a leaf."""
        az = float(np.degrees(np.arctan2(self.sun_dir[1], self.sun_dir[0]))); out = {}
        for k, off in self.OCELLI.items():
            a = np.radians(h + off); sh = self._shade_at(x + 0.3 * np.cos(a), y + 0.3 * np.sin(a)) / 1.0
            sun = 0.3 * max(0.0, float(np.cos(np.radians(az - (h + off)))))
            out[k] = float(np.clip(sh * (self.sky + sun) / (self.sky + 0.3), 0.0, 1.0))
        return out

    def temperature(self, x, y):
        sx, sy, ss = self.sunspot; px, py, _, pr, _ = self.puddle
        T = 25.0 + 6.0 * float(np.exp(-((x - sx) ** 2 + (y - sy) ** 2) / (2 * ss ** 2)))       # the sun patch
        T -= 3.0 * (1 - self._shade_at(x, y)) / 0.45                                          # shade under leaves
        T -= 2.0 * float(np.clip(1 - (np.hypot(x - px, y - py) - pr) / 0.3, 0, 1))             # over the water
        return T

    def humidity(self, x, y):
        sx, sy, ss = self.sunspot; px, py, _, pr, _ = self.puddle
        return 0.4 + 0.5 * float(np.clip(1 - (np.hypot(x - px, y - py) - pr) / 0.4, 0, 1)) - 0.15 * float(np.exp(-((x - sx) ** 2 + (y - sy) ** 2) / (2 * ss ** 2)))

    def odour(self, x, y, t, sources=None, rng=None):
        """concentration per source at (x, y), time t: a Gaussian plume downwind (sigma grows with distance) times an
        intermittent whiff state (Bernoulli per 100 ms with a probability that falls with downwind distance).
        a simplified plume; power-law whiff / blank durations (Gorur-Shandilya 2017) are the next refinement."""
        out = {}; rng = rng or np.random.default_rng(int(t * 1000) % 2 ** 31)
        srcs = sources or {"fruit": (self.fruit[0], self.fruit[1])}
        for name, (sx, sy) in srcs.items():
            r = np.array([x - sx, y - sy]); s = float(r @ self.wind); c = float(np.hypot(*(r - s * self.wind)))
            if s < -0.2: out[name] = 0.0; continue
            s = max(s, 0.0); sig = 0.25 + 0.3 * s; C = float(np.exp(-c * c / (2 * sig * sig)) / (1 + s))
            st = self.whiff.get(name, (1, -1.0))
            if t >= st[1]:
                on = rng.random() < 0.7 / (1 + s); dur = 0.1 + 0.4 * rng.random(); st = (1 if on else 0, t + dur); self.whiff[name] = st
            out[name] = C * st[0]
        return out

    # ---- contacts
    def step_frame(self, m: Body, f, fps: int) -> None:
        m.clear_contact()
        if f is not None: f.clear_contact()
        m.advance(fps)
        if f is not None and f.present: f.advance(fps)
        self.wall(m)
        if f is not None: self.wall(f)
        m.taste = None
        for b in ([m] + ([f] if f is not None and f.present else [])):
            for gx, gy, gr, _, _ in self.grass:
                dd = np.hypot(b.x - gx, b.y - gy)
                if dd < gr + b.r: b.x, b.y = gx + (b.x - gx) / max(dd, 1e-6) * (gr + b.r), gy + (b.y - gy) / max(dd, 1e-6) * (gr + b.r); b.touched = "L" if b.bearing_to(gx, gy) >= 0 else "R"; b.kind = 1
            for ox, oy, _, r_, _ in (self.stone, self.fruit):
                dd = np.hypot(b.x - ox, b.y - oy)
                if dd < r_ + b.r:
                    b.x, b.y = ox + (b.x - ox) / max(dd, 1e-6) * (r_ + b.r), oy + (b.y - oy) / max(dd, 1e-6) * (r_ + b.r); b.touched = "L" if b.bearing_to(ox, oy) >= 0 else "R"; b.kind = 1
                if (ox, oy) == (self.fruit[0], self.fruit[1]) and b is m and dd < r_ + b.r + 0.01: m.taste = "sugar"   # tarsi on the skin: standing against the fruit is tasting it (09-18 14:05; before, only pushing into it counted, and a halted fly does not push)
            px, py, _, pr, _ = self.puddle
            if np.hypot(b.x - px, b.y - py) < pr and b is m: m.taste = "water" if m.taste is None else m.taste
        if f is not None and f.present: self.pair(m, f)
