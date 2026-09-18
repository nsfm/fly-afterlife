#!/usr/bin/env python3
"""
replay_app.py - the replay viewer as a native window. no server, no PNG, no browser.

the human view is rendered by HIS raytracer (seam/omma.py Scene.shade, the numba kernel), not a second
implementation: same primitives, same luminance, same clipping, a pinhole camera at his eye.

    uv run --with pygame-ce python world/replay_app.py world/room_v7.npz
    uv run --with pygame-ce python world/replay_app.py world/garden/solo_s3.npz --size 640x320 --fov 150
    uv run --with pygame-ce python world/replay_app.py world/room_v7.npz --bench 120      # headless timing, no window

(`uv add pygame-ce` once and the plain `uv run python world/replay_app.py ...` works.)

four panels: the human view; his retina (the saved per-column luminance at its own az/el); the map (the world,
his path, her, touch rings); the traces (per-frame spike counts, each scaled to its own max, plus his pace).

keys   space play/pause | left/right step a frame | shift+left/right jump 1 s | [ ] slower/faster
       home/end first/last | click or drag the bar to scrub | q or esc quit

playback keeps the episode's own clock (its fps, x the speed) and drops frames when it must. the human view
is the only expensive panel - 204,800 rays through the kernel, ~3 ms in the room, ~8 ms in the garden (30
grass cylinders) - so it renders in a worker thread reading ahead of the playhead, into an LRU of grayscale
frames; the rest of the window (2 ms) runs at the display rate and the view shows the newest frame that
finished. the info line says how far behind it is. everything else is incremental: the map's path only ever
grows, the retina is a precomputed scatter of pixel indices, the traces are drawn once and only the playhead
moves, and the labels and legend are baked into one background surface.

two things about the npz worth knowing, both handled here:
  - a solo run (pair.py --no-female) still logs her pose, frozen at her start, with dist = inf. she was NOT
    in the scene his eye saw. --her auto (the default) believes dist and leaves her out; --her always puts
    her back, which is what replay.py does unconditionally.
  - floor_rgb row 0 is y = -half (omma indexes iy from y), so the map flips it; the html viewer does not.
"""
import os, sys, time, argparse, threading, collections
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "seam")); sys.path.insert(0, os.path.join(ROOT, "src"))

FLY_W = np.array([0.20, 0.70, 0.10])                      # his luminance weights on an RGB floor texture
TRACE_KEYS = ["DNa02_L", "DNa02_R", "legMN", "pC1", "pIP10", "DN_L", "DN_R"]
COLS = [(226, 166, 59), (122, 184, 255), (155, 226, 155), (224, 122, 154), (201, 160, 255), (255, 208, 112), (127, 208, 208), (255, 158, 122), (170, 170, 170)]
BG, PANEL, INK, DIM = (11, 14, 20), (0, 0, 0), (216, 222, 233), (154, 163, 178)
HIM, HER = (226, 166, 59), (224, 122, 154)
SPEEDS = [0.25, 0.5, 1, 2, 3, 4, 6, 8, 12, 16, 24, 30]

# ---- three small kernels for the per-frame pixel work (numpy fallbacks if numba is missing, as omma does)
try:
    from numba import njit, prange
    @njit(cache=True, parallel=True, fastmath=True)
    def _rot(r0, c, s, out):                        # rays into world frame: a yaw by his heading, = r0 @ R.T
        for i in prange(r0.shape[0]):
            x = r0[i, 0]; y = r0[i, 1]
            out[i, 0] = c * x - s * y; out[i, 1] = s * x + c * y; out[i, 2] = r0[i, 2]

    @njit(cache=True, parallel=True)
    def _gray_rgb(g, out):                          # (H,W) luminance -> (H,W,3) for one blit
        H, W = g.shape
        for y in prange(H):
            for x in range(W):
                v = g[y, x]; out[y, x, 0] = v; out[y, x, 1] = v; out[y, x, 2] = v

    @njit(cache=True)
    def _paint(row, idx, src, flat):                # scatter the retina's dots straight into the panel's pixels
        for k in range(idx.shape[0]):
            v = row[src[k]]; j = idx[k]
            flat[j, 0] = v; flat[j, 1] = v; flat[j, 2] = v
except ImportError:                                 # pragma: no cover
    def _rot(r0, c, s, out): np.dot(r0, np.array([[c, s, 0.0], [-s, c, 0.0], [0.0, 0.0, 1.0]]), out=out)
    def _gray_rgb(g, out): out[:] = g[:, :, None]
    def _paint(row, idx, src, flat): flat[idx] = row[src][:, None]


# ---------------------------------------------------------------- the episode
class Episode:
    """one npz: poses, the saved retina, the world, and the Scene his eye actually saw."""

    def __init__(self, path, her_mode="auto"):
        E = np.load(path, allow_pickle=True); self.E = E; self.path = path
        self.pose = np.asarray(E["pose"], np.float64); self.n = len(self.pose); self.fps = int(E["fps"])
        self.world = str(E["world"]) if "world" in E.files else "room"
        self.lum = E["lum"] if E["lum"].dtype == np.uint8 else (np.clip(E["lum"], 0, 1) * 255).astype(np.uint8)
        self.az = np.asarray(E["az"], np.float64); self.el = np.asarray(E["el"], np.float64)
        self.touch = np.asarray(E["touch"]) if "touch" in E.files else None
        self.touch_kind = np.asarray(E["touch_kind"]) if "touch_kind" in E.files else None
        self.walls = np.asarray(E["walls"], np.float64) if "walls" in E.files else None
        self.objects = np.asarray(E["objects"], np.float64) if "objects" in E.files else np.zeros((0, 4))
        self.her_r = float(E["her_r"]) if "her_r" in E.files else 0.12
        self.her_alb = float(E["her_albedo"]) if "her_albedo" in E.files else 0.1
        self.pose2 = np.asarray(E["pose2"], np.float64) if "pose2" in E.files else None
        # she is logged even when she was not in the world (pair.py --no-female freezes her pose and dist = inf).
        # `auto` believes dist; without it, a pose2 that never moves means she was not there.
        moved = self.pose2 is not None and float(np.abs(self.pose2[:, :2] - self.pose2[0, :2]).max()) > 1e-3
        seen = bool(np.isfinite(np.asarray(E["dist"])).any()) if "dist" in E.files else moved
        self.her = self.pose2 is not None and (seen or moved) if her_mode == "auto" else (her_mode == "always" and self.pose2 is not None)
        if self.world == "garden":
            self.half = float(E["floor_half"]); rgb = np.asarray(E["floor_rgb"], np.uint8)
            self.floor_rgb = rgb; self.tex = ((rgb.astype(np.float32) / 255.0) @ FLY_W).astype(np.float32)
            self.grass = np.asarray(E["grass"], np.float64); self.leaves = np.asarray(E["leaves"], np.float64)
            self.stone = np.asarray(E["stone"], np.float64); self.fruit = np.asarray(E["fruit"], np.float64)
            self.puddle = np.asarray(E["puddle"], np.float64); self.sunspot = np.asarray(E["sunspot"], np.float64)
            self.wind = np.asarray(E["wind"], np.float64)
            self.w_h = float(self.walls[1]) if self.walls is not None else 0.3
            self.w_a = float(self.walls[2]) if self.walls is not None else 0.5
        else:
            self.half = float(self.walls[0]) if self.walls is not None else 2.5
            self.floor_rgb = None
            self.pillar_h = float(E["pillar_height"]) if "pillar_height" in E.files else 1.5
        self._static = None
        self.traces = collections.OrderedDict()
        for k in TRACE_KEYS:
            if "n_m_" + k in E.files: self.traces[k] = np.asarray(E["n_m_" + k], np.float64)
        if "v_m" in E.files: self.traces["v_m (pace)"] = np.asarray(E["v_m"], np.float64)
        self._static = None if self.her else self.scene_at(0)     # nothing moves in his world when she is not in it

    # the same rebuild replay.py does, from what the episode saved
    def scene_at(self, i):
        from omma import Scene
        if self._static is not None: return self._static
        E = self.E
        sph = [(np.array([self.pose2[i][0], self.pose2[i][1], 0.5]), self.her_r, self.her_alb)] if self.her else []
        if self.world == "garden":
            st, fr, pu = self.stone, self.fruit, self.puddle
            sph += [(np.array([st[0], st[1], st[2]]), float(st[3]), float(st[4])), (np.array([fr[0], fr[1], fr[2]]), float(fr[3]), float(fr[4]))]
            return Scene(sky=0.85, ground=0.35, spheres=sph, pillars=[tuple(map(float, g)) for g in self.grass],
                         walls=dict(half=self.half, height=self.w_h, albedo=self.w_a), floor=dict(tex=self.tex, half=self.half),
                         discs=[tuple(map(float, l)) for l in self.leaves] + [tuple(map(float, pu))], sun=dict(dir=(0.6, 0.3, 0.74), boost=0.3, k=10))
        w = dict(half=float(self.walls[0]), height=float(self.walls[1]), albedo=float(self.walls[2])) if self.walls is not None else None
        return Scene(sky=float(E["sky"]), ground=float(E["ground"]), spheres=sph,
                     pillars=[tuple(map(float, p)) for p in self.objects], walls=w, pillar_height=self.pillar_h)


# ---------------------------------------------------------------- the human view
class HumanView:
    """pinhole camera at his eye, rays rotated by his heading, shaded by his kernel. LRU of grayscale frames."""

    def __init__(self, ep, W, H, fov_deg, cap=256):
        self.ep, self.W, self.H = ep, W, H
        fov = np.radians(fov_deg); fx = np.tan(fov / 2); fy = fx * H / W
        u = (np.arange(W) + 0.5) / W * 2 - 1; v = 1 - (np.arange(H) + 0.5) / H * 2; U, V = np.meshgrid(u, v)
        r0 = np.stack([np.ones_like(U), -U * fx, V * fy], -1).reshape(-1, 3)   # forward +x, left +y, up +z
        self.r0 = np.ascontiguousarray(r0 / np.linalg.norm(r0, axis=1, keepdims=True))
        self.buf = np.empty_like(self.r0)                      # rotated rays, reused (the kernel wants C-contiguous f8)
        self.cache = collections.OrderedDict(); self.cap = cap; self.lock = threading.Lock()

    def render(self, i):
        x, y, h = self.ep.pose[i]; hr = np.radians(h)
        _rot(self.r0, np.cos(hr), np.sin(hr), self.buf)
        img = self.ep.scene_at(i).shade(np.array([x, y, 0.5]), self.buf).reshape(self.H, self.W)
        g = (np.clip(img, 0, 1) * 255).astype(np.uint8)
        with self.lock:
            self.cache[i] = g; self.cache.move_to_end(i)
            while len(self.cache) > self.cap: self.cache.popitem(last=False)
        return g

    def get(self, i):
        with self.lock:
            g = self.cache.get(i)
            if g is not None: self.cache.move_to_end(i)
        return g

    def has(self, i):
        with self.lock: return i in self.cache


class RenderThread(threading.Thread):
    """renders the wanted frame, then reads ahead. the shade kernel gives the GIL back, so the window keeps moving."""

    def __init__(self, hv, lookahead=24):
        super().__init__(daemon=True); self.hv = hv; self.look = lookahead
        self.cv = threading.Condition(); self.want = 0; self.step = 1; self.stop = False

    def ask(self, i, step):
        with self.cv:
            if i != self.want or step != self.step: self.want, self.step = i, max(1, int(step)); self.cv.notify()

    def close(self):
        with self.cv: self.stop = True; self.cv.notify()

    def run(self):
        while True:
            with self.cv:
                if self.stop: return
                i, st = self.want, self.step
            if not self.hv.has(i): self.hv.render(i); continue
            nxt = None
            for k in range(1, self.look + 1):
                j = min(self.hv.ep.n - 1, i + k * st)
                if not self.hv.has(j): nxt = j; break
            if nxt is not None: self.hv.render(nxt); continue
            with self.cv:
                if not self.stop and self.want == i and self.step == st: self.cv.wait(0.05)


# ---------------------------------------------------------------- panels
def retina_index(az, el, RW, RH):
    """one scatter of 3x3 dots, precomputed: flat pixel indices and which column feeds each."""
    xs = np.rint(RW / 2 - az / 190.0 * (RW / 2)).astype(np.int64)      # left of fly = left of panel
    ys = np.rint(RH / 2 - el / 95.0 * (RH / 2)).astype(np.int64)
    d = np.array([-1, 0, 1]); dx, dy = np.meshgrid(d, d)
    XX = xs[:, None] + dx.ravel()[None, :]; YY = ys[:, None] + dy.ravel()[None, :]
    ok = (XX >= 0) & (XX < RW) & (YY >= 0) & (YY < RH)
    src = np.repeat(np.arange(len(az))[:, None], 9, 1)
    return (YY * RW + XX)[ok].astype(np.int64), src[ok].astype(np.int64)


def bin_max(a, w):
    n = len(a); starts = (np.arange(w) * n) // w; ends = np.concatenate([starts[1:], [n]])
    return np.array([a[s:e].max() if e > s else a[min(s, n - 1)] for s, e in zip(starts, ends)])


def make_traces(pg, ep, W, H):
    surf = pg.Surface((W, H)); surf.fill(PANEL); f = pg.font.Font(None, 16)
    keys = list(ep.traces); rows = max(1, len(keys)); rh = H / rows; head = 15
    for j, k in enumerate(keys):
        v = bin_max(ep.traces[k], W); mx = float(v.max()); y0 = j * rh; top = y0 + head; hgt = rh - head - 5
        col = COLS[j % len(COLS)]
        pts = [(x, top + hgt - (v[x] / mx if mx > 0 else 0.0) * hgt) for x in range(W)]
        pg.draw.aalines(surf, col, False, pts)
        surf.blit(f.render(f"{k}  ({'silent' if mx <= 0 else 'max %g' % mx})", True, col), (4, int(y0) + 2))
        pg.draw.line(surf, (30, 36, 48), (0, int(y0 + rh) - 2), (W, int(y0 + rh) - 2))
    return surf


def make_map(pg, ep, S, cx, cy, size):
    """the world, drawn once: the garden's own floor texture and its objects, or the room's pillars."""
    surf = pg.Surface((size, size)); surf.fill(BG)
    def w2(x, y): return (cx + x * S, cy - y * S)
    a, b = w2(-ep.half, ep.half); c, d = w2(ep.half, -ep.half); rect = pg.Rect(int(a), int(b), int(c - a), int(d - b))
    if ep.floor_rgb is not None:
        # tex row 0 is y = -half (omma indexes iy from y), and the map's top is y = +half, so flip it
        img = np.ascontiguousarray(ep.floor_rgb[::-1].transpose(1, 0, 2))
        fs = pg.image.frombuffer(img.tobytes(), (img.shape[1], img.shape[0]), "RGB")
        surf.blit(pg.transform.smoothscale(fs, (rect.w, rect.h)), rect.topleft)
    ov = pg.Surface((size, size), pg.SRCALPHA)
    if ep.world == "garden":
        for lx, ly, lz, lr, _ in ep.leaves:
            pg.draw.circle(ov, (60, 120, 40, 90), w2(lx, ly), max(2.0, lr * S))
        sx, sy, ss = ep.sunspot; pg.draw.circle(ov, (255, 208, 112, 64), w2(sx, sy), max(2.0, ss * S))
        surf.blit(ov, (0, 0))
        for gx, gy, gr, _, _ in ep.grass: pg.draw.circle(surf, (42, 90, 26), w2(gx, gy), 3)
        for o, col in ((ep.stone, (160, 154, 144)), (ep.fruit, (154, 26, 26))):
            pg.draw.circle(surf, col, w2(o[0], o[1]), max(2.0, o[3] * S))
        pu = ep.puddle; pg.draw.circle(surf, (51, 68, 102), w2(pu[0], pu[1]), max(2.0, pu[3] * S))
        wx, wy = w2(-ep.half + 0.4, ep.half - 0.4); w = ep.wind
        pg.draw.line(surf, (255, 255, 255), (wx, wy), (wx + w[0] * 30, wy - w[1] * 30), 2)
        f = pg.font.Font(None, 16); surf.blit(f.render("wind", True, (255, 255, 255)), (wx + 4, wy + 4))
    else:
        for o in ep.objects:
            pg.draw.circle(surf, (242, 239, 230) if o[3] > 0.5 else (42, 47, 58), w2(o[0], o[1]), max(2.0, o[2] * S))
    pg.draw.rect(surf, (200, 190, 170), rect, 1)
    return surf


def legend_rows(ep):
    if ep.world == "garden":
        rows = [((60, 120, 40), "leaf overhead (shade)"), ((255, 208, 112), "sun patch (+6 C)"), ((42, 90, 26), "grass stalk"),
                ((160, 154, 144), "stone"), ((154, 26, 26), "fruit (plume, sugar)"), ((51, 68, 102), "puddle (humid)"),
                ((255, 255, 255), "wind (arrow)")]
    else:
        rows = []
        if len(ep.objects) and (ep.objects[:, 3] > 0.5).any(): rows.append(((242, 239, 230), "pale pillar"))
        if len(ep.objects) and (ep.objects[:, 3] <= 0.5).any(): rows.append(((42, 47, 58), "dark pillar"))
    rows.append((HIM, "him (line = heading)"))
    if ep.her: rows.append((HER, "her"))
    rows.append((DIM, "o touching wall / rim / stalk"))
    if ep.her: rows.append((HER, "o touching her"))
    return rows


# ---------------------------------------------------------------- the app
def run(args):
    if args.bench: os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import pygame as pg

    ep = Episode(args.npz, args.her)
    HVW, HVH = (int(v) for v in args.size.split("x"))
    RW, RH = 560, 280
    PAD = 16; MAPS = 420
    row2 = 28 + max(HVH, RH) + 36
    WIN_W = PAD + HVW + PAD + RW + PAD
    TRW = WIN_W - (PAD + MAPS + PAD) - PAD; TRH = MAPS
    LEG_Y = row2 + MAPS + 6; BAR_Y = LEG_Y + 108; WIN_H = BAR_Y + 52
    R_HV = pg.Rect(PAD, 28, HVW, HVH); R_RET = pg.Rect(PAD + HVW + PAD, 28, RW, RH)
    R_MAP = pg.Rect(PAD, row2, MAPS, MAPS); R_TR = pg.Rect(PAD + MAPS + PAD, row2, TRW, TRH)
    R_BAR = pg.Rect(PAD, BAR_Y, WIN_W - 2 * PAD, 16)

    pg.init(); pg.display.set_caption(f"replay - {os.path.basename(args.npz)}")
    screen = pg.display.set_mode((WIN_W, WIN_H))
    f_lab = pg.font.Font(None, 19); f_leg = pg.font.Font(None, 16); f_info = pg.font.Font(None, 20)

    hv = HumanView(ep, HVW, HVH, args.fov, cap=args.cache)
    t0 = time.perf_counter(); hv.render(0); t_compile = time.perf_counter() - t0
    worker = RenderThread(hv); worker.start()

    ridx, rsrc = retina_index(ep.az, ep.el, RW, RH)
    RBUF = np.zeros((RH, RW, 3), np.uint8); RFLAT = RBUF.reshape(-1, 3)
    HVBUF = np.empty((HVH, HVW, 3), np.uint8)
    _paint(ep.lum[0], ridx, rsrc, RFLAT); _gray_rgb(hv.get(0), HVBUF)      # compile the pixel kernels before we time anything

    S = MAPS / (2 * ep.half + 0.4); cx = cy = MAPS / 2
    base = make_map(pg, ep, S, cx, cy, MAPS)
    path = pg.Surface((MAPS, MAPS), pg.SRCALPHA)
    PTS = [(cx + p[0] * S, cy - p[1] * S) for p in ep.pose]
    PTS2 = [(cx + p[0] * S, cy - p[1] * S) for p in ep.pose2] if ep.her else None
    path_to = 0
    traces = make_traces(pg, ep, TRW, TRH)

    chrome = pg.Surface((WIN_W, WIN_H)); chrome.fill(BG)
    chrome.blit(f_lab.render(f"human view: his raytracer, pinhole {args.fov:g} deg", True, DIM), (R_HV.x, 8))
    chrome.blit(f_lab.render("his retina (left of fly = left of panel)", True, DIM), (R_RET.x, 8))
    chrome.blit(f_lab.render("map", True, DIM), (R_MAP.x, row2 - 20))
    chrome.blit(f_lab.render("traces (per frame, each scaled to its own max)", True, DIM), (R_TR.x, row2 - 20))
    for k, (col, txt) in enumerate(legend_rows(ep)):
        lx = R_MAP.x + (k % 2) * 212; ly = LEG_Y + (k // 2) * 17
        if txt.startswith("o "): pg.draw.circle(chrome, col, (lx + 6, ly + 7), 5, 2); txt = txt[2:]
        else: pg.draw.circle(chrome, col, (lx + 6, ly + 7), 5)
        chrome.blit(f_leg.render(txt, True, DIM), (lx + 16, ly))
    pg.draw.rect(chrome, (30, 36, 48), R_BAR)

    pos = 0.0; playing = False; spd = 2; dragging = False
    clock = pg.time.Clock(); last = time.perf_counter(); stats = collections.defaultdict(list)

    def draw_path(i):
        nonlocal path_to
        if i < path_to:
            path.fill((0, 0, 0, 0)); path_to = 0
        if i > path_to:
            pg.draw.lines(path, (226, 166, 59, 190), False, PTS[path_to:i + 1], 1); path_to = i

    def frame(i):
        t = time.perf_counter()
        screen.blit(chrome, (0, 0))
        # -- human view (newest finished frame; the worker is chasing i)
        g = hv.get(i)
        j = i
        if g is None:
            with hv.lock:
                if hv.cache: j = min(hv.cache, key=lambda k: abs(k - i)); g = hv.cache[j]
        if g is not None:
            _gray_rgb(g, HVBUF)
            screen.blit(pg.image.frombuffer(HVBUF, (HVW, HVH), "RGB"), R_HV.topleft)
        stats["hv"].append(time.perf_counter() - t); t = time.perf_counter()
        # -- retina
        _paint(ep.lum[i], ridx, rsrc, RFLAT)      # the written pixels are the same set every frame, so no clear
        screen.blit(pg.image.frombuffer(RBUF, (RW, RH), "RGB"), R_RET.topleft)
        stats["ret"].append(time.perf_counter() - t); t = time.perf_counter()
        # -- map
        screen.blit(base, R_MAP.topleft); draw_path(i); screen.blit(path, R_MAP.topleft)
        hx, hy = PTS[i]; hx += R_MAP.x; hy += R_MAP.y
        if PTS2 is not None:
            qx, qy = PTS2[i]; pg.draw.circle(screen, HER, (qx + R_MAP.x, qy + R_MAP.y), 5)
        pg.draw.circle(screen, HIM, (hx, hy), 5)
        hr = np.radians(ep.pose[i][2]); pg.draw.line(screen, HIM, (hx, hy), (hx + 14 * np.cos(hr), hy - 14 * np.sin(hr)), 2)
        if ep.touch is not None and ep.touch[i]:
            kind = int(ep.touch_kind[i]) if ep.touch_kind is not None else 1
            pg.draw.circle(screen, HER if kind == 2 else DIM, (hx, hy), 9, 2)
        stats["map"].append(time.perf_counter() - t); t = time.perf_counter()
        # -- traces + playhead
        screen.blit(traces, R_TR.topleft)
        px = R_TR.x + int(i / max(1, ep.n - 1) * (TRW - 1))
        pg.draw.line(screen, (255, 255, 255), (px, R_TR.y), (px, R_TR.bottom), 1)
        stats["tr"].append(time.perf_counter() - t); t = time.perf_counter()
        # -- the bar and the one line of text (everything else is baked into `chrome`)
        pg.draw.rect(screen, HIM, pg.Rect(R_BAR.x, R_BAR.y, int(R_BAR.w * i / max(1, ep.n - 1)), R_BAR.h))
        pg.draw.rect(screen, (60, 68, 84), R_BAR, 1)
        lag = "" if j == i else f"   [view {j - i:+d}]"
        info = (f"frame {i} / {ep.n - 1}    t = {i / ep.fps:6.2f} s    heading {ep.pose[i][2] % 360:5.1f} deg"
                f"    x{SPEEDS[spd]:g}    {'playing' if playing else 'paused'}    {clock.get_fps():4.0f} fps{lag}")
        screen.blit(f_info.render(info, True, INK), (PAD, BAR_Y + 26))
        pg.display.flip()
        stats["chrome"].append(time.perf_counter() - t)

    if args.bench:
        n = min(args.bench, ep.n); step = max(1, ep.n // max(1, n))
        worker.close()                                     # bench renders synchronously, to time the kernel honestly
        t0 = time.perf_counter(); sync = []
        for k in range(n):
            i = min(ep.n - 1, k * step)
            ts = time.perf_counter(); hv.render(i); sync.append(time.perf_counter() - ts)
            frame(i)
        wall = time.perf_counter() - t0
        def ms(a): a = np.array(a) * 1000; return f"mean {a.mean():6.2f}  p50 {np.median(a):6.2f}  p95 {np.percentile(a, 95):6.2f}"
        print(f"{args.npz}: {ep.n} frames, {ep.fps} fps, world={ep.world}, her in scene={ep.her}, retina {ep.lum.shape[1]} columns")
        print(f"  first render (numba compile) {t_compile * 1000:.0f} ms")
        print(f"  shade {HVW}x{HVH} ({HVW * HVH} rays)  ms: {ms(sync)}")
        for k in ("hv", "ret", "map", "tr", "chrome"): print(f"  panel {k:7s} ms: {ms(stats[k])}")
        tot = sum(float(np.median(stats[k])) for k in ("hv", "ret", "map", "tr", "chrome")) * 1000
        print(f"  window without the raytracer (p50 sum): {tot:.2f} ms/frame  ->  {1000 / tot:.0f} fps")
        print(f"  {n} frames incl. synchronous render in {wall:.2f} s = {n / wall:.1f} fps")
        if args.shot:
            pg.image.save(screen, args.shot); print(f"  wrote {args.shot}")
        pg.quit(); return

    print(f"{args.npz}: {ep.n} frames at {ep.fps} fps ({ep.world}); her in his scene: {ep.her}; numba compile {t_compile * 1000:.0f} ms")
    running = True
    while running:
        for e in pg.event.get():
            if e.type == pg.QUIT: running = False
            elif e.type == pg.KEYDOWN:
                sh = e.mod & pg.KMOD_SHIFT
                if e.key in (pg.K_q, pg.K_ESCAPE): running = False
                elif e.key == pg.K_SPACE: playing = not playing
                elif e.key == pg.K_LEFT: pos = max(0, pos - (ep.fps if sh else 1)); playing = False
                elif e.key == pg.K_RIGHT: pos = min(ep.n - 1, pos + (ep.fps if sh else 1)); playing = False
                elif e.key == pg.K_LEFTBRACKET: spd = max(0, spd - 1)
                elif e.key == pg.K_RIGHTBRACKET: spd = min(len(SPEEDS) - 1, spd + 1)
                elif e.key == pg.K_HOME: pos = 0.0
                elif e.key == pg.K_END: pos = ep.n - 1
            elif e.type == pg.MOUSEBUTTONDOWN and e.button == 1 and R_BAR.collidepoint(e.pos):
                dragging = True; pos = np.clip((e.pos[0] - R_BAR.x) / R_BAR.w, 0, 1) * (ep.n - 1)
            elif e.type == pg.MOUSEBUTTONUP and e.button == 1: dragging = False
            elif e.type == pg.MOUSEMOTION and dragging:
                pos = np.clip((e.pos[0] - R_BAR.x) / R_BAR.w, 0, 1) * (ep.n - 1)
        now = time.perf_counter(); dt = now - last; last = now
        if playing and not dragging:
            pos += SPEEDS[spd] * ep.fps * dt                # the episode's own clock; frames drop, time does not
            if pos >= ep.n - 1: pos = ep.n - 1.0; playing = False
        i = int(pos)
        worker.ask(i, max(1, round(SPEEDS[spd] * ep.fps / max(1e-6, clock.get_fps() or 60))))
        frame(i)
        clock.tick(120)
    worker.close(); pg.quit()


def main():
    ap = argparse.ArgumentParser(description="native replay viewer for a fly episode npz")
    ap.add_argument("npz"); ap.add_argument("--fov", type=float, default=150.0); ap.add_argument("--size", default="640x320")
    ap.add_argument("--cache", type=int, default=256, help="human-view frames kept (LRU)")
    ap.add_argument("--her", default="auto", choices=("auto", "always", "never"), help="put her in his scene: auto believes the episode's dist / her pose moving")
    ap.add_argument("--bench", type=int, default=0, help="render N frames headless, print timings, no window")
    ap.add_argument("--shot", default=None, help="with --bench: save the last window to this png")
    run(ap.parse_args())


if __name__ == "__main__":
    main()
