#!/usr/bin/env python3
"""
replay_app.py - the replay viewer as a native window. no server, no PNG, no browser.

the human view is rendered by HIS raytracer (seam/omma.py Scene.shade, the numba kernel), not a second
implementation: same primitives, same luminance, same clipping, a pinhole camera at his eye.

    uv run python world/replay_app.py world/feed/latch_s12.npz --scale 2
    uv run python world/replay_app.py world/garden3/gated_s12.npz --fov 110 --eye pano
    uv run python world/replay_app.py world/room_v7.npz --bench 120          # headless timing, no window

four panels under one header: the human view; his eye (either the per-ommatidium dots at their own az/el, or
the nearest-column panorama the web player had - a Voronoi of his sampling on a cylinder); the map (the world,
his path, her, touch rings); the traces (per-frame spike counts, each scaled to its own max, plus his pace).

keys   space play/pause          left/right step a frame       shift+left/right jump 1 s
       , . step a frame          home/end first/last           l loop
       [ ] slower/faster         - = human FOV -/+ 5 deg (shift: 15)      0 reset FOV
       v cycle the eye panel (dots / panorama)                 s camera smoothing on/off
       u cycle the human view's UV layer (off / tint / hatch / both)      c cycle the eye's channel
       h or ? keyboard help      q or esc quit                 click or drag the bar to scrub
       mouse wheel over the human view also changes its FOV

the on-screen controls at the top do the same things; everything is clickable. --eye pano opens on the
panorama, --no-smooth opens on the raw per-chunk heading, --loop loops, --cap sets the display frame cap,
--uv tint|hatch|both opens with the UV layer on, --chan uv|both opens the eye on the UV retina.

UV (09-18). R7/R8 see a world we do not: the sky is the source, vegetation and soil are near-black, water is
a mirror and the sun is a clipped disc. two things show it here, and neither is a recolouring of the green
image - both come from the UV world itself.
  - the human view's false-colour layer (`u`). a SECOND raytrace of the same pose through a UV Scene rebuilt
    the way garden.scene_uv builds it (sky 1.0, ground 0.06, floor 0.05 x the saved texture's own contrast,
    grass / leaves 0.04, stone 0.30, fruit 0.05, puddle 0.90, rim 0.15, sun disc 2.5 deg clipped to 1.0),
    composited over the grayscale visible image as a violet tint proportional to UV luminance, a violet
    crosshatch whose spacing tightens in five steps with it, or both. it is a second shade call per frame,
    cached in its own LRU beside the first, rendered by the same worker thread and (at --uv-div 2) at half
    resolution. only for `world == "garden"` - that is the only world with a UV description.
  - the eye panel's channel (`c`), when the run was made with --uv and the file carries `lum_uv`: green
    (the saved R1-R6 luminance, as before), uv (the saved R7 luminance, in violet), or both (UV over green
    in one blend: green stays green, UV-bright goes violet, both-bright goes white). works in dots and pano.
the ocelli would go next to the eye panel - but nothing drives them yet (no receptors identified), so there
is no panel for them and there should not be one until there is a signal to draw.

WHY THE HUMAN VIEW JUDDERED (and what `s` does about it). steering is applied once per 100 ms chunk, so
pose[:, 2] is a staircase: 9 frames in 10 have exactly zero heading change and the tenth jumps by up to 12 deg.
his eye does not show it (the dots sit at fixed panel positions; only their brightness changes) but a pinhole
camera does - the whole image snaps ten times a second. with smoothing on, the CAMERA heading is the chunk
headings linearly interpolated at their chunk centres and then run through a centred K-frame box filter, and
the camera position through the same box filter. that is a viewer-side smoothing of how we look at what he
did, not a change to what he did: the map, the retina, the traces and the readout all still show the real pose.
press `s` to see the raw staircase.

playback keeps the episode's own clock (its fps, x the speed) and drops frames when it must. the human view is
the only expensive panel - HVW*HVH rays through the kernel, ~2.5 ms in the room, ~7 ms in the garden (30 grass
cylinders) - so it renders in a worker thread reading ahead of the playhead, into an LRU of grayscale frames;
the rest of the window runs at the display rate and the view shows the newest finished frame at or before the
playhead (never one ahead, which used to make it stutter backwards). the header says how far behind it is.
everything else is incremental: the map's path only ever grows, the dots are a precomputed scatter of pixel
indices, the panorama is one precomputed nearest-column table (built once, in the background), the traces are
drawn once and only a two-pixel strip is repainted as the playhead moves, and every label, the legend and the
scrubber's touch ticks are baked into one background surface.

the window is drawn at the device resolution (everything scales with --scale, fonts included) instead of being
drawn small and smoothscaled up, which is both sharper and, at --scale 2, about three times faster.

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

# one muted palette, used everywhere
BG     = (14, 17, 23)        # the window
CARD   = (21, 25, 33)        # a panel's chrome (title strip, control bar)
PANEL  = (8, 10, 14)         # inside a panel, where pixels live
EDGE   = (40, 47, 60)        # hairlines
EDGE2  = (30, 36, 46)
INK    = (224, 230, 239)     # primary text
DIM    = (144, 154, 170)     # secondary text
FAINT  = (92, 101, 117)      # tertiary text, ticks
HIM    = (226, 166, 59)      # amber: him, the playhead, the filled bar
HER    = (224, 122, 154)
BTN    = (28, 33, 43); BTN_HOT = (40, 47, 60); BTN_ON = (60, 47, 24); BTN_ON_HOT = (76, 59, 30)
BLANK  = (16, 19, 26)        # the panorama beyond 5.5 deg of any column: he samples nothing there
SPEEDS = [0.1, 0.25, 0.5, 1, 2, 3, 4, 6, 8, 12, 16, 24, 30]
PANO_LIM = 5.5               # deg: the web player's acceptance radius for the nearest-column splat

# ---- the UV false colour. one hue, used by every UV thing in the window so the eye learns it in one look.
UVC    = (186, 118, 255)     # "this is ultraviolet": the tint, the hatch, the UV dots, the UV chips
UV_TR, UV_TG, UV_TB = 196.0, 74.0, 255.0        # what a UV luminance of 1.0 tints the visible image toward
UV_HR, UV_HG, UV_HB = 208.0, 120.0, 255.0       # the crosshatch ink
UV_TINT_MAX = 0.78           # tint weight at full UV: below 1 so the visible image is never fully erased
UV_MODES = ("off", "tint", "hatch", "both")     # what `u` cycles
UV_BITS = {"off": 0, "tint": 1, "hatch": 2, "both": 3}
UV_TITLE = {"tint": "tint", "hatch": "crosshatch", "both": "tint + crosshatch"}
CHANS = ("green", "uv", "both")                 # what `c` cycles (only when the file has lum_uv)
# the UV world, as garden.Garden.UV writes it (src/fly_afterlife/garden.py). kept verbatim so the viewer's
# second raytrace is the same world his R7s were shown, not a lookalike.
UV_ALB = dict(sky=1.0, ground=0.06, floor=0.05, grass=0.04, leaf=0.04, stone=0.30, fruit=0.05,
              puddle=0.90, rim=0.15, her=0.05, disc_deg=2.5)

# ---- small kernels for the per-frame pixel work (numpy fallbacks if numba is missing, as omma does)
try:
    from numba import njit, prange
    @njit(cache=True, parallel=True, fastmath=True)
    def _rot(r0, c, s, out):                        # rays into world frame: a yaw by his heading, = r0 @ R.T
        for i in prange(r0.shape[0]):
            x = r0[i, 0]; y = r0[i, 1]
            out[i, 0] = c * x - s * y; out[i, 1] = s * x + c * y; out[i, 2] = r0[i, 2]

    @njit(cache=True)
    def _gray_rgb(g, out):                          # (H,W) luminance -> (H,W,3) for one blit
        H, W = g.shape
        for y in range(H):
            for x in range(W):
                v = g[y, x]; out[y, x, 0] = v; out[y, x, 1] = v; out[y, x, 2] = v

    @njit(cache=True)
    def _paint(row, idx, src, flat):                # scatter the eye's dots straight into the panel's pixels
        for k in range(idx.shape[0]):
            v = row[src[k]]; j = idx[k]
            flat[j, 0] = v; flat[j, 1] = v; flat[j, 2] = v

    @njit(cache=True)
    def _splat(row, near, flat, br, bg_, bb):       # panorama: every pixel takes its nearest column's luminance
        for q in range(near.shape[0]):
            k = near[q]
            if k < 0:
                flat[q, 0] = br; flat[q, 1] = bg_; flat[q, 2] = bb
            else:
                v = row[k]; flat[q, 0] = v; flat[q, 1] = v; flat[q, 2] = v

    @njit(cache=True)
    def _paint2(row, rowu, idx, src, flat, chan):    # the dots in UV (chan 1) or UV-over-green (chan 2)
        for k in range(idx.shape[0]):
            s = src[k]; j = idx[k]; w = float(rowu[s])
            if chan == 1:
                flat[j, 0] = np.uint8(w * 0.60); flat[j, 1] = np.uint8(w * 0.24); flat[j, 2] = np.uint8(w)
            else:
                v = float(row[s]); g = 0.88 * v + 0.12 * w
                flat[j, 0] = np.uint8(w * 0.90); flat[j, 1] = np.uint8(g if g < 255.0 else 255.0); flat[j, 2] = np.uint8(w * 0.96)

    @njit(cache=True, parallel=True)
    def _splat2(row, rowu, near, flat, chan, br, bg_, bb):          # the same, for the panorama
        for q in prange(near.shape[0]):
            k = near[q]
            if k < 0:
                flat[q, 0] = br; flat[q, 1] = bg_; flat[q, 2] = bb
            elif chan == 1:
                w = float(rowu[k]); flat[q, 0] = np.uint8(w * 0.60); flat[q, 1] = np.uint8(w * 0.24); flat[q, 2] = np.uint8(w)
            else:
                v = float(row[k]); w = float(rowu[k]); g = 0.88 * v + 0.12 * w
                flat[q, 0] = np.uint8(w * 0.90); flat[q, 1] = np.uint8(g if g < 255.0 else 255.0); flat[q, 2] = np.uint8(w * 0.96)

    @njit(cache=True, parallel=True, fastmath=True)
    def _uv_comp(g, u, mode, out):
        """the human view's false-colour composite: gray visible (H,W) + UV (h,w, possibly smaller) -> (H,W,3).
        mode is a bit field: 1 = violet tint proportional to UV, 2 = violet crosshatch whose spacing tightens
        with UV in five steps (each coarse family is a subset of the finer one, so density grows smoothly and
        the lines never jump around between frames)."""
        H, W = g.shape; hu, wu = u.shape
        xm = np.empty(W, np.int64); ym = np.empty(H, np.int64)      # the upscale, out of the inner loop
        for x in range(W): xm[x] = x * wu // W
        for y in range(H): ym[y] = y * hu // H
        for y in prange(H):
            yu = ym[y]
            for x in range(W):
                v = float(g[y, x]); w = float(u[yu, xm[x]]) / 255.0
                r = v; gg = v; b = v
                if mode & 1:
                    t = UV_TINT_MAX * w
                    r = v * (1.0 - t) + UV_TR * t; gg = v * (1.0 - t) + UV_TG * t; b = v * (1.0 - t) + UV_TB * t
                if mode & 2:
                    lv = int(w * 5.0 + 0.5)
                    if lv > 0:
                        s = x + y; d = x - y; on = False
                        if lv == 1: on = (s % 16) == 0
                        elif lv == 2: on = (s % 8) == 0
                        elif lv == 3: on = (s % 8) == 0 or (d % 8) == 0
                        elif lv == 4: on = (s % 4) == 0 or (d % 8) == 0
                        else: on = (s % 4) == 0 or (d % 4) == 0
                        if on:
                            r = 0.30 * r + 0.70 * UV_HR; gg = 0.30 * gg + 0.70 * UV_HG; b = 0.30 * b + 0.70 * UV_HB
                out[y, x, 0] = np.uint8(r if r < 255.0 else 255.0)
                out[y, x, 1] = np.uint8(gg if gg < 255.0 else 255.0)
                out[y, x, 2] = np.uint8(b if b < 255.0 else 255.0)

    @njit(cache=True, parallel=True)
    def _nearest(cx, cy, cz, cel, PW, PH, cos_lim, lim, out):
        """for each panorama pixel (azimuth across, elevation up), the nearest column within `lim` deg, else -1.
        the |elevation| prefilter cuts the inner loop from 1764 columns to a few dozen."""
        n = cx.shape[0]
        for j in prange(PH):
            eld = 90.0 - (j + 0.5) / PH * 180.0
            sel = np.empty(n, np.int64); m = 0
            for k in range(n):
                if abs(cel[k] - eld) <= lim: sel[m] = k; m += 1
            el = np.radians(eld); ce = np.cos(el); se = np.sin(el)
            for i in range(PW):
                best = -1
                if m > 0:
                    az = np.radians(180.0 - (i + 0.5) / PW * 360.0)
                    px = ce * np.cos(az); py = ce * np.sin(az)
                    bd = cos_lim
                    for q in range(m):
                        k = sel[q]; d = px * cx[k] + py * cy[k] + se * cz[k]
                        if d > bd: bd = d; best = k
                out[j * PW + i] = best
except ImportError:                                 # pragma: no cover
    def _rot(r0, c, s, out): np.dot(r0, np.array([[c, s, 0.0], [-s, c, 0.0], [0.0, 0.0, 1.0]]), out=out)
    def _gray_rgb(g, out): out[:] = g[:, :, None]
    def _paint(row, idx, src, flat): flat[idx] = row[src][:, None]
    def _splat(row, near, flat, br, bg_, bb):
        v = np.where(near >= 0, row[np.maximum(near, 0)], 0)
        flat[:] = v[:, None]; flat[near < 0] = (br, bg_, bb)
    def _uv_rgb(v, w, chan):                                   # (N,) green, (N,) uv -> (N,3) uint8
        v = v.astype(np.float32); w = w.astype(np.float32)
        if chan == 1: out = np.stack([w * 0.60, w * 0.24, w], 1)
        else: out = np.stack([w * 0.90, np.minimum(0.88 * v + 0.12 * w, 255), w * 0.96], 1)
        return out.astype(np.uint8)
    def _paint2(row, rowu, idx, src, flat, chan): flat[idx] = _uv_rgb(row[src], rowu[src], chan)
    def _splat2(row, rowu, near, flat, chan, br, bg_, bb):
        k = np.maximum(near, 0); flat[:] = _uv_rgb(row[k], rowu[k], chan); flat[near < 0] = (br, bg_, bb)
    def _uv_comp(g, u, mode, out):
        H, W = g.shape; hu, wu = u.shape
        w = (u[(np.arange(H) * hu // H)[:, None], (np.arange(W) * wu // W)[None, :]].astype(np.float32) / 255.0)
        v = g.astype(np.float32); rgb = np.repeat(v[:, :, None], 3, 2)
        if mode & 1:
            t = (UV_TINT_MAX * w)[:, :, None]
            rgb = rgb * (1 - t) + t * np.array([UV_TR, UV_TG, UV_TB], np.float32)
        if mode & 2:
            lv = np.rint(w * 5.0).astype(np.int64); x = np.arange(W)[None, :]; y = np.arange(H)[:, None]
            s = x + y; d = x - y; on = np.zeros((H, W), bool)
            for L, sp, dp in ((1, 16, 0), (2, 8, 0), (3, 8, 8), (4, 4, 8), (5, 4, 4)):
                m = lv == L; on |= m & ((s % sp == 0) | ((d % dp == 0) if dp else False))
            rgb[on] = 0.30 * rgb[on] + 0.70 * np.array([UV_HR, UV_HG, UV_HB], np.float32)
        out[:] = np.clip(rgb, 0, 255).astype(np.uint8)
    def _nearest(cx, cy, cz, cel, PW, PH, cos_lim, lim, out):
        for j in range(PH):
            eld = 90.0 - (j + 0.5) / PH * 180.0
            sel = np.flatnonzero(np.abs(cel - eld) <= lim)
            if not len(sel): out[j * PW:(j + 1) * PW] = -1; continue
            el = np.radians(eld); az = np.radians(180.0 - (np.arange(PW) + 0.5) / PW * 360.0)
            p = np.stack([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.full(PW, np.sin(el))], 1)
            d = p @ np.stack([cx[sel], cy[sel], cz[sel]], 1).T
            k = d.argmax(1); best = np.where(d[np.arange(PW), k] > cos_lim, sel[k], -1)
            out[j * PW:(j + 1) * PW] = best


def box(a, k):
    """centred k-frame moving average, edges held. kills the per-chunk kink without shifting the signal."""
    a = np.asarray(a, np.float64)
    if k <= 1: return a.copy()
    lo = k // 2; hi = k - 1 - lo
    b = np.concatenate([np.full(lo, a[0]), a, np.full(hi, a[-1])])
    c = np.cumsum(np.concatenate([[0.0], b]))
    return (c[k:] - c[:-k]) / k


# ---------------------------------------------------------------- the episode
class Episode:
    """one npz: poses, the saved retina, the world, the Scene his eye actually saw, and a smoothed camera."""

    def __init__(self, path, her_mode="auto"):
        E = np.load(path, allow_pickle=True); self.E = E; self.path = path
        self.pose = np.asarray(E["pose"], np.float64); self.n = len(self.pose); self.fps = int(E["fps"])
        self.world = str(E["world"]) if "world" in E.files else "room"
        self.lum = E["lum"] if E["lum"].dtype == np.uint8 else (np.clip(E["lum"], 0, 1) * 255).astype(np.uint8)
        # the second retina: runs made with --uv save R7's world in the same columns (09-18). absent in older files.
        self.lum_uv = None
        if "lum_uv" in E.files:
            lu = E["lum_uv"]
            self.lum_uv = lu if lu.dtype == np.uint8 else (np.clip(lu, 0, 1) * 255).astype(np.uint8)
            if self.lum_uv.shape != self.lum.shape: self.lum_uv = None      # a mismatched retina is worse than none
        self.az = np.asarray(E["az"], np.float64); self.el = np.asarray(E["el"], np.float64)
        self.side = np.asarray(E["side"]) if "side" in E.files else None
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
        # the dish (world == "arena"): a circular wall, not the square one the walls array looks like. its height
        # and albedo still come from walls (2.8, 0.47, 0.6 in the dish runs); the radius has its own key.
        self.arena = self.world == "arena"
        self.arena_r = float(E["arena_radius"]) if "arena_radius" in E.files else self.half
        if self.arena:
            self.w_h = float(self.walls[1]) if self.walls is not None else 0.47
            self.w_a = float(self.walls[2]) if self.walls is not None else 0.6
        self.can_uv = self.world == "garden"     # the only world with a UV description to raytrace (garden.scene_uv)
        self._static = None; self._static_uv = None; self._tex_uv = None
        self.traces = collections.OrderedDict()
        for k in TRACE_KEYS:
            if "n_m_" + k in E.files: self.traces[k] = np.asarray(E["n_m_" + k], np.float64)
        if "v_m" in E.files: self.traces["v_m (pace)"] = np.asarray(E["v_m"], np.float64)
        self._static = None if self.her else self.scene_at(0)     # nothing moves in his world when she is not in it
        self.K = self._chunk_frames()
        self.cam_h, self.cam_xy = self._camera()

    def _chunk_frames(self):
        """how many frames one control chunk lasts. steering is applied once per chunk, so pose heading is a
        staircase with this period - which is exactly what makes a pinhole camera judder."""
        E = self.E
        if "heading_chunk" in E.files:
            k = len(np.asarray(E["heading_chunk"]).ravel())
            if k > 1 and self.n % k == 0 and self.n // k > 1: return self.n // k
        d = np.abs(np.diff(np.unwrap(np.radians(self.pose[:, 2]))))
        idx = np.flatnonzero(d > 1e-9)
        if len(idx) > 3:
            g = np.diff(idx); g = g[g > 0]
            if len(g): return int(np.clip(np.median(g), 1, max(1, self.n // 4)))
        return 1

    def _camera(self):
        """the viewer's camera track: the same pose, smoothed, for the human view only.

        heading: the per-chunk headings placed at their chunk centres, linearly interpolated to every frame,
        then a centred K-frame box filter (so the angular rate is continuous instead of kinking at each centre).
        position: the same box filter - it is piecewise linear at the chunk rate, so this only rounds the corners.
        neither is ever used for the map, the retina, the traces or the readout."""
        K = self.K
        h = np.unwrap(np.radians(self.pose[:, 2]))
        if K <= 1:
            return self.pose[:, 2].copy(), self.pose[:, :2].copy()
        c = np.arange(0, self.n, K)                        # first frame of each chunk
        hs = np.interp(np.arange(self.n), c + (K - 1) / 2.0, h[c])
        return np.degrees(box(hs, K)), np.stack([box(self.pose[:, 0], K), box(self.pose[:, 1], K)], 1)

    def heading_steps(self):
        """(fraction of frames whose heading is unchanged, largest single-frame step in deg) - the diagnosis."""
        d = np.abs(np.degrees(np.diff(np.unwrap(np.radians(self.pose[:, 2])))))
        if not len(d): return 0.0, 0.0
        return float((d < 1e-9).mean()), float(d.max())

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
        if self.arena:      # the dish: one cylinder wall seen from inside, not four planes (the square was a lie)
            return Scene(sky=float(E["sky"]), ground=float(E["ground"]), spheres=sph,
                         pillars=[tuple(map(float, p)) for p in self.objects], walls=None,
                         ring=dict(radius=self.arena_r, height=self.w_h, albedo=self.w_a), pillar_height=self.pillar_h)
        w = dict(half=float(self.walls[0]), height=float(self.walls[1]), albedo=float(self.walls[2])) if self.walls is not None else None
        return Scene(sky=float(E["sky"]), ground=float(E["ground"]), spheres=sph,
                     pillars=[tuple(map(float, p)) for p in self.objects], walls=w, pillar_height=self.pillar_h)

    def scene_uv_at(self, i):
        """the same frame in R7's world, built exactly as garden.scene_uv builds it from the same saved arrays:
        a bright sky, a near-black floor keeping only the texture's own contrast, dark vegetation, a bright
        stone, a mirror puddle and a clipped sun disc. garden only - no other world has a UV description."""
        from omma import Scene
        if self._static_uv is not None: return self._static_uv
        if not self.can_uv: return None
        u = UV_ALB
        if self._tex_uv is None:
            tt = self.tex; self._tex_uv = (u["floor"] * (0.6 + 0.8 * (tt - tt.min()) / (tt.max() - tt.min() + 1e-9))).astype(np.float32)
        st, fr, pu = self.stone, self.fruit, self.puddle
        sph = [(np.array([self.pose2[i][0], self.pose2[i][1], 0.5]), self.her_r, u["her"])] if self.her else []
        sph += [(np.array([st[0], st[1], st[2]]), float(st[3]), u["stone"]), (np.array([fr[0], fr[1], fr[2]]), float(fr[3]), u["fruit"])]
        s = Scene(sky=u["sky"], ground=u["ground"], spheres=sph,
                  pillars=[(float(g[0]), float(g[1]), float(g[2]), u["grass"], float(g[4])) for g in self.grass],
                  walls=dict(half=self.half, height=self.w_h, albedo=u["rim"]), floor=dict(tex=self._tex_uv, half=self.half),
                  discs=[(float(l[0]), float(l[1]), float(l[2]), float(l[3]), u["leaf"]) for l in self.leaves]
                        + [(float(pu[0]), float(pu[1]), float(pu[2]), float(pu[3]), u["puddle"])],
                  sun=dict(dir=(0.6, 0.3, 0.74), boost=0.4, k=6, disc_deg=u["disc_deg"], disc_lum=1.0))
        if not self.her: self._static_uv = s
        return s


# ---------------------------------------------------------------- the human view
class HumanView:
    """pinhole camera at his eye, rays rotated by the camera heading, shaded by his kernel. LRU of gray frames."""

    def __init__(self, ep, W, H, fov_deg, smooth=True, cap=256, uv="off", uv_div=1):
        self.ep, self.W, self.H = ep, W, H
        self.cache = collections.OrderedDict(); self.cap = cap; self.lock = threading.Lock()
        self.gen = 0; self.fov = None; self.smooth = smooth
        # the UV layer: a second LRU of gray UV frames, same keys, optionally at 1/uv_div the resolution (a
        # false-colour wash and a hatch density do not need the full grid, and half res is a quarter of the rays)
        self.ucache = collections.OrderedDict(); self.uv = uv if ep.can_uv else "off"
        self.ud = max(1, int(uv_div)); self.UW = max(8, W // self.ud); self.UH = max(8, H // self.ud)
        self._build(fov_deg)

    def _rays(self, W, H, fov_deg):
        fov = np.radians(fov_deg); fx = np.tan(fov / 2); fy = fx * H / W
        u = (np.arange(W) + 0.5) / W * 2 - 1; v = 1 - (np.arange(H) + 0.5) / H * 2; U, V = np.meshgrid(u, v)
        r0 = np.stack([np.ones_like(U), -U * fx, V * fy], -1).reshape(-1, 3)   # forward +x, left +y, up +z
        return np.ascontiguousarray(r0 / np.linalg.norm(r0, axis=1, keepdims=True))

    def _build(self, fov_deg):
        self.r0 = self._rays(self.W, self.H, fov_deg)
        self.buf = np.empty_like(self.r0)                  # rotated rays, reused (the kernel wants C-contiguous f8)
        self.r0u = self.r0 if self.ud == 1 else self._rays(self.UW, self.UH, fov_deg)   # the UV lens is the same lens
        self.bufu = self.buf if self.ud == 1 else np.empty_like(self.r0u)
        self.fov = float(fov_deg)

    def configure(self, fov_deg=None, smooth=None):
        """change the lens or the camera track. everything cached was shot with the old one, so it all goes."""
        with self.lock:
            if fov_deg is not None and abs(fov_deg - self.fov) > 1e-9: self._build(fov_deg)
            if smooth is not None: self.smooth = bool(smooth)
            self.cache.clear(); self.ucache.clear(); self.gen += 1

    def set_uv(self, mode):
        """turn the UV layer on or off. the visible frames stay valid - only the UV LRU is affected."""
        with self.lock:
            self.uv = mode if self.ep.can_uv else "off"
            if self.uv == "off": self.ucache.clear()

    def pose_at(self, i):
        if self.smooth: return self.ep.cam_xy[i, 0], self.ep.cam_xy[i, 1], self.ep.cam_h[i]
        p = self.ep.pose[i]; return p[0], p[1], p[2]

    def render(self, i):
        """shade whatever frame i is still missing - the visible pass, the UV pass, or both. one pose, two lenses."""
        with self.lock:
            gen, r0, buf, r0u, bufu, uv = self.gen, self.r0, self.buf, self.r0u, self.bufu, self.uv
            need_g = i not in self.cache; need_u = uv != "off" and i not in self.ucache
        if not (need_g or need_u): return self.get(i)
        x, y, h = self.pose_at(i); hr = np.radians(h); c, s = np.cos(hr), np.sin(hr); o = np.array([x, y, 0.5])
        g = uimg = None
        if need_g:
            _rot(r0, c, s, buf)
            g = (np.clip(self.ep.scene_at(i).shade(o, buf), 0, 1) * 255).astype(np.uint8).reshape(self.H, self.W)
        if need_u:
            if self.ud != 1 or not need_g: _rot(r0u, c, s, bufu)
            sc = self.ep.scene_uv_at(i)
            if sc is not None:
                uimg = (np.clip(sc.shade(o, bufu), 0, 1) * 255).astype(np.uint8).reshape(self.UH, self.UW)
        with self.lock:
            if gen != self.gen: return g                   # the lens changed while we were shading: drop it
            if g is not None:
                self.cache[i] = g; self.cache.move_to_end(i)
                while len(self.cache) > self.cap:
                    k, _ = self.cache.popitem(last=False); self.ucache.pop(k, None)   # keep the two LRUs in step
            if uimg is not None:
                self.ucache[i] = uimg; self.ucache.move_to_end(i)
                while len(self.ucache) > self.cap: self.ucache.popitem(last=False)
            return g if g is not None else self.cache.get(i)

    def get(self, i):
        with self.lock:
            g = self.cache.get(i)
            if g is not None: self.cache.move_to_end(i)
        return g

    def newest_at_or_before(self, i):
        """the frame to actually show: never one AHEAD of the playhead, or the view stutters backwards.
        returns (frame index, gray, uv gray or None) - the UV is always the same frame as the gray."""
        with self.lock:
            g = self.cache.get(i)
            if g is not None: return i, g, self.ucache.get(i)
            if not self.cache: return i, None, None
            below = [k for k in self.cache if k <= i]
            j = max(below) if below else min(self.cache)
            return j, self.cache[j], self.ucache.get(j)

    def has(self, i):
        with self.lock: return i in self.cache and (self.uv == "off" or i in self.ucache)


class RenderThread(threading.Thread):
    """renders the wanted frame, then reads ahead. the shade kernel gives the GIL back, so the window keeps moving."""

    def __init__(self, hv, lookahead=24):
        super().__init__(daemon=True); self.hv = hv; self.look = lookahead
        self.cv = threading.Condition(); self.want = 0; self.step = 1; self.stop = False

    def ask(self, i, step):
        with self.cv:
            if i != self.want or step != self.step: self.want, self.step = i, max(1, int(step)); self.cv.notify()

    def poke(self):
        with self.cv: self.cv.notify()

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


# ---------------------------------------------------------------- the eye panel
def retina_index(az, el, RW, RH, rad=1):
    """the dots view: one scatter of (2r+1)^2 dots, precomputed - flat pixel indices and which column feeds each."""
    xs = np.rint(RW / 2 - az / 190.0 * (RW / 2)).astype(np.int64)      # left of fly = left of panel
    ys = np.rint(RH / 2 - el / 95.0 * (RH / 2)).astype(np.int64)
    d = np.arange(-rad, rad + 1); dx, dy = np.meshgrid(d, d)
    XX = xs[:, None] + dx.ravel()[None, :]; YY = ys[:, None] + dy.ravel()[None, :]
    ok = (XX >= 0) & (XX < RW) & (YY >= 0) & (YY < RH)
    src = np.repeat(np.arange(len(az))[:, None], (2 * rad + 1) ** 2, 1)
    return (YY * RW + XX)[ok].astype(np.int64), src[ok].astype(np.int64)


class Pano:
    """the web player's other fly view: each pixel of a cylindrical az/el panorama takes the luminance of the
    nearest ommatidium within 5.5 deg, blank beyond - a Voronoi tiling of his sampling. one table, built once."""

    def __init__(self, az, el, PW, PH, lim=PANO_LIM):
        self.PW, self.PH, self.lim = int(PW), int(PH), float(lim)
        self.az = np.asarray(az, np.float64); self.el = np.asarray(el, np.float64)
        self.near = None; self.secs = None; self.started = False

    def start(self):
        if self.started: return
        self.started = True; threading.Thread(target=self._build, daemon=True).start()

    def _build(self):
        t0 = time.perf_counter()
        a = np.radians(self.az); e = np.radians(self.el)
        cx = np.ascontiguousarray(np.cos(e) * np.cos(a)); cy = np.ascontiguousarray(np.cos(e) * np.sin(a)); cz = np.ascontiguousarray(np.sin(e))
        out = np.full(self.PW * self.PH, -1, np.int64)
        _nearest(cx, cy, cz, np.ascontiguousarray(self.el), self.PW, self.PH, float(np.cos(np.radians(self.lim))), self.lim, out)
        self.secs = time.perf_counter() - t0; self.near = out

    @property
    def ready(self): return self.near is not None


# ---------------------------------------------------------------- static panels
def bin_max(a, w):
    n = len(a); starts = (np.arange(w) * n) // w; ends = np.concatenate([starts[1:], [n]])
    return np.array([a[s:e].max() if e > s else a[min(s, n - 1)] for s, e in zip(starts, ends)])


def make_traces(pg, ep, W, H, font):
    surf = pg.Surface((W, H)); surf.fill(PANEL)
    keys = list(ep.traces); rows = max(1, len(keys)); rh = H / rows; head = font.get_height() + 3
    for j, k in enumerate(keys):
        v = bin_max(ep.traces[k], W); mx = float(v.max()); y0 = j * rh; top = y0 + head; hgt = rh - head - 5
        col = COLS[j % len(COLS)]
        pg.draw.line(surf, EDGE2, (0, int(top + hgt)), (W, int(top + hgt)))
        pts = [(x, top + hgt - (v[x] / mx if mx > 0 else 0.0) * hgt) for x in range(W)]
        pg.draw.aalines(surf, col, False, pts)
        surf.blit(font.render(f"{k}   {'silent' if mx <= 0 else 'max %g' % mx}", True, col), (5, int(y0) + 2))
        if j: pg.draw.line(surf, EDGE2, (0, int(y0)), (W, int(y0)))
    return surf


def make_map(pg, ep, S, cx, cy, size, font):
    """the world, drawn once: the garden's own floor texture and its objects, or the room's pillars."""
    surf = pg.Surface((size, size)); surf.fill(PANEL)
    def w2(x, y): return (cx + x * S, cy - y * S)
    a, b = w2(-ep.half, ep.half); c, d = w2(ep.half, -ep.half); rect = pg.Rect(int(a), int(b), int(c - a), int(d - b))
    if ep.arena:                      # a dish, not a box: the floor and the rim are one circle of arena_radius
        pg.draw.circle(surf, (23, 27, 35), (cx, cy), ep.arena_r * S)
        for o in ep.objects:
            pg.draw.circle(surf, (242, 239, 230) if o[3] > 0.5 else (58, 64, 78), w2(o[0], o[1]), max(2.0, o[2] * S))
        pg.draw.circle(surf, (150, 142, 124), (cx, cy), ep.arena_r * S, max(1, int(size / 420.0)))
        return surf
    if ep.floor_rgb is not None:
        # tex row 0 is y = -half (omma indexes iy from y), and the map's top is y = +half, so flip it
        img = np.ascontiguousarray(ep.floor_rgb[::-1].transpose(1, 0, 2))
        fs = pg.image.frombuffer(img.tobytes(), (img.shape[1], img.shape[0]), "RGB")
        surf.blit(pg.transform.smoothscale(fs, (rect.w, rect.h)), rect.topleft)
    else:
        pg.draw.rect(surf, (23, 27, 35), rect)
    ov = pg.Surface((size, size), pg.SRCALPHA)
    u = size / 420.0
    if ep.world == "garden":
        for lx, ly, lz, lr, _ in ep.leaves:
            pg.draw.circle(ov, (60, 120, 40, 90), w2(lx, ly), max(2.0 * u, lr * S))
        sx, sy, ss = ep.sunspot; pg.draw.circle(ov, (255, 208, 112, 64), w2(sx, sy), max(2.0 * u, ss * S))
        surf.blit(ov, (0, 0))
        for gx, gy, gr, _, _ in ep.grass: pg.draw.circle(surf, (42, 90, 26), w2(gx, gy), max(2.0, 3 * u))
        for o, col in ((ep.stone, (160, 154, 144)), (ep.fruit, (154, 26, 26))):
            pg.draw.circle(surf, col, w2(o[0], o[1]), max(2.0 * u, o[3] * S))
        pu = ep.puddle; pg.draw.circle(surf, (51, 68, 102), w2(pu[0], pu[1]), max(2.0 * u, pu[3] * S))
        wx, wy = w2(-ep.half + 0.4, ep.half - 0.4); w = ep.wind
        pg.draw.line(surf, (236, 240, 248), (wx, wy), (wx + w[0] * 30 * u, wy - w[1] * 30 * u), max(1, int(2 * u)))
        surf.blit(font.render("wind", True, (236, 240, 248)), (wx + 4 * u, wy + 4 * u))
    else:
        for o in ep.objects:
            pg.draw.circle(surf, (242, 239, 230) if o[3] > 0.5 else (58, 64, 78), w2(o[0], o[1]), max(2.0 * u, o[2] * S))
    pg.draw.rect(surf, (150, 142, 124), rect, max(1, int(u)))
    return surf


def legend_rows(ep):
    if ep.world == "garden":
        rows = [((60, 120, 40), "leaf overhead"), ((255, 208, 112), "sun patch +6C"), ((42, 90, 26), "grass stalk"),
                ((160, 154, 144), "stone"), ((154, 26, 26), "fruit (plume)"), ((51, 68, 102), "puddle"),
                ((236, 240, 248), "wind arrow")]
    else:
        rows = []
        if ep.arena: rows.append(((150, 142, 124), "dish rim, r = %.2g m" % ep.arena_r))
        if len(ep.objects) and (ep.objects[:, 3] > 0.5).any(): rows.append(((242, 239, 230), "pale pillar"))
        if len(ep.objects) and (ep.objects[:, 3] <= 0.5).any(): rows.append(((58, 64, 78), "dark pillar"))
    rows.append((HIM, "him (line = heading)"))
    if ep.her: rows.append((HER, "her"))
    rows.append((DIM, "o touching wall / rim / stalk"))
    if ep.her: rows.append((HER, "o touching her"))
    return rows


# ---------------------------------------------------------------- tiny UI kit
class Btn:
    __slots__ = ("id", "label", "rect", "on", "hot", "tip")
    def __init__(self, bid, label, tip=""): self.id = bid; self.label = label; self.rect = None; self.on = False; self.hot = False; self.tip = tip


def clock_str(t):
    m, s = divmod(max(0.0, t), 60.0)
    return f"{int(m):d}:{s:05.2f}"


HELP = [("space", "play / pause"), ("left / right   or   , .", "step one frame"), ("shift + left / right", "jump one second"),
        ("home / end", "first / last frame"), ("l", "loop at the end"), ("[  ]", "slower / faster"),
        ("-  =", "human FOV -/+ 5 deg  (shift: 15)"), ("0", "human FOV back to the default"),
        ("v", "eye panel: ommatidial dots / panorama"), ("s", "camera smoothing on / off (human view only)"),
        ("u", "human view UV layer: off / tint / hatch / both"), ("c", "eye channel: green / UV / both"),
        ("click / drag the bar", "scrub"), ("h  or  ?", "this card"), ("q  or  esc", "quit")]


# ---------------------------------------------------------------- the app
def run(args):
    if args.bench: os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import pygame as pg

    ep = Episode(args.npz, args.her)
    HVW, HVH = (int(v) for v in args.size.split("x"))
    S = float(args.scale)
    def U(v): return int(round(v * S))

    pg.init(); pg.display.set_caption(f"fly replay - {os.path.basename(args.npz)}")
    def F(px): return pg.font.Font(None, max(11, int(round(px * S))))
    f_h1, f_ui, f_lab, f_leg, f_small, f_mono = F(23), F(20), F(19), F(17), F(16), F(21)

    # ---- layout, in logical units; every rect below is already in device pixels
    PAD, EW, EH, MAPS = 14, 560, 280, 420
    HEAD = 100                                                # title row + control row + scrubber + ticks
    TITLE_H = 20                                              # a panel's title strip
    RULER = 15                                                # the azimuth ruler under the eye panel
    LOGW = PAD + HVW + PAD + EW + PAD
    rowA = HEAD + 6
    rowA_h = TITLE_H + max(HVH, EH + RULER)
    rowB = rowA + rowA_h + 12
    rowB_h = TITLE_H + MAPS
    LEG_Y = rowB + rowB_h + 14
    TRW = LOGW - 3 * PAD - MAPS
    W = U(LOGW)
    # the legend flows: each chip is as wide as its own label, wrapping at the window edge
    leg = legend_rows(ep); lx = U(PAD); ly = 0; leg_pos = []
    for col, txt in leg:
        w_ = f_leg.size(txt[2:] if txt.startswith("o ") else txt)[0] + U(26)
        if lx > U(PAD) and lx + w_ > W - U(PAD): lx = U(PAD); ly += 1
        leg_pos.append((lx, ly)); lx += w_ + U(10)
    LEG_ROWS = ly + 1
    FOOTd = U(LEG_Y) + LEG_ROWS * U(17) + U(7)
    H = FOOTd + U(24)
    R_HV  = pg.Rect(U(PAD), U(rowA) + U(TITLE_H), U(HVW), U(HVH))
    R_EYE = pg.Rect(U(PAD + HVW + PAD), U(rowA) + U(TITLE_H), U(EW), U(EH))
    R_RUL = pg.Rect(R_EYE.x, R_EYE.bottom, R_EYE.w, U(RULER))
    R_MAP = pg.Rect(U(PAD), U(rowB) + U(TITLE_H), U(MAPS), U(MAPS))
    R_TR  = pg.Rect(U(PAD + MAPS + PAD), U(rowB) + U(TITLE_H), U(TRW), U(MAPS))
    R_BAR = pg.Rect(U(PAD), U(70), W - 2 * U(PAD), U(12))
    R_HEAD = pg.Rect(0, 0, W, U(HEAD))
    R_FOOT = pg.Rect(0, FOOTd, W, H - FOOTd)

    display = pg.display.set_mode((W, H))

    uv_mode = args.uv if ep.can_uv else "off"
    chan = args.chan if ep.lum_uv is not None else "green"
    hv = HumanView(ep, HVW, HVH, args.fov, smooth=not args.no_smooth, cap=args.cache, uv=uv_mode, uv_div=args.uv_div)
    t0 = time.perf_counter(); hv.render(0); t_compile = time.perf_counter() - t0
    if ep.can_uv:                                             # compile the UV pass and the composite too, before timing
        hv.set_uv("both"); hv.render(0); hv.set_uv(uv_mode)
    worker = RenderThread(hv); worker.start()

    RAD = max(1, int(round(1.2 * S)))
    ridx, rsrc = retina_index(ep.az, ep.el, R_EYE.w, R_EYE.h, RAD)
    EBUF = np.empty((R_EYE.h, R_EYE.w, 3), np.uint8); EBUF[:] = PANEL; EFLAT = EBUF.reshape(-1, 3)
    PBUF = np.empty((R_EYE.h, R_EYE.w, 3), np.uint8); PFLAT = PBUF.reshape(-1, 3)
    HVBUF = np.empty((HVH, HVW, 3), np.uint8)
    HVSCALED = [None]                                         # the upscaled human view, allocated once and reused
    pano = Pano(ep.az, ep.el, R_EYE.w, R_EYE.h); pano.start()
    _paint(ep.lum[0], ridx, rsrc, EFLAT); _gray_rgb(hv.get(0), HVBUF)      # compile the pixel kernels before timing
    _splat(ep.lum[0], np.full(4, -1, np.int64), PFLAT[:4], *BLANK)
    if ep.lum_uv is not None:
        _paint2(ep.lum[0], ep.lum_uv[0], ridx, rsrc, EFLAT, 2)
        _splat2(ep.lum[0], ep.lum_uv[0], np.full(4, -1, np.int64), PFLAT[:4], 2, *BLANK)
    if ep.can_uv:
        _u0 = hv.newest_at_or_before(0)[2]
        if _u0 is not None: _uv_comp(hv.get(0), _u0, 3, HVBUF)

    MS = R_MAP.w / (2 * ep.half + 0.4); mcx = mcy = R_MAP.w / 2
    base = make_map(pg, ep, MS, mcx, mcy, R_MAP.w, f_leg)
    path = pg.Surface((R_MAP.w, R_MAP.w), pg.SRCALPHA)
    PTS = [(mcx + p[0] * MS, mcy - p[1] * MS) for p in ep.pose]
    PTS2 = [(mcx + p[0] * MS, mcy - p[1] * MS) for p in ep.pose2] if ep.her else None
    path_to = 0
    traces = make_traces(pg, ep, R_TR.w, R_TR.h, f_small)

    # ---- the background: everything that never changes
    chrome = pg.Surface((W, H)); chrome.fill(BG)
    def card(rect, pad_top=0):
        r = pg.Rect(rect.x, rect.y - pad_top, rect.w, rect.h + pad_top)
        pg.draw.rect(chrome, CARD, r, border_radius=U(6)); pg.draw.rect(chrome, EDGE, r, max(1, int(S)), border_radius=U(6))
    for r in (R_HV, R_MAP, R_TR): card(r, U(TITLE_H))
    card(pg.Rect(R_EYE.x, R_EYE.y, R_EYE.w, R_EYE.h + R_RUL.h), U(TITLE_H))
    def title(rect, txt, col=DIM): chrome.blit(f_lab.render(txt, True, col), (rect.x + U(4), rect.y - U(TITLE_H) + U(4)))
    title(R_MAP, "map   the world from above, his path behind him")
    title(R_TR, "traces   spikes per frame, each scaled to its own max")
    for (col, txt), (lx, lrow) in zip(leg, leg_pos):
        ly = U(LEG_Y) + lrow * U(17); rr = U(5)
        if txt.startswith("o "): pg.draw.circle(chrome, col, (lx + rr, ly + U(8)), rr, max(1, int(round(1.6 * S)))); txt = txt[2:]
        else: pg.draw.circle(chrome, col, (lx + rr, ly + U(8)), rr)
        chrome.blit(f_leg.render(txt, True, DIM), (lx + U(14), ly + U(1)))
    # the scrubber's groove, with a tick everywhere he touched something
    pg.draw.rect(chrome, (24, 29, 38), R_BAR, border_radius=U(3))
    if ep.touch is not None:
        tt = np.flatnonzero(np.asarray(ep.touch) != 0)
        if len(tt):
            for i in tt[:: max(1, len(tt) // 900)]:
                x = R_BAR.x + int(i / max(1, ep.n - 1) * (R_BAR.w - 1))
                k = int(ep.touch_kind[i]) if ep.touch_kind is not None else 1
                pg.draw.line(chrome, HER if k == 2 else (70, 78, 94), (x, R_BAR.bottom - U(3)), (x, R_BAR.bottom - U(1)))
    for q in range(5):                                        # time ticks under the bar
        x = R_BAR.x + int(q / 4 * (R_BAR.w - 1)); lab = clock_str(q / 4 * (ep.n - 1) / ep.fps)
        s_ = f_small.render(lab, True, FAINT)
        chrome.blit(s_, (min(max(R_BAR.x, x - s_.get_width() // 2), R_BAR.right - s_.get_width()), R_BAR.bottom + U(3)))
        pg.draw.line(chrome, EDGE2, (x, R_BAR.bottom + U(1)), (x, R_BAR.bottom + U(2)))
    meta = f"{os.path.basename(args.npz)}   {ep.world}   {ep.n} frames @ {ep.fps} fps   {ep.lum.shape[1]} ommatidia" + ("   + her" if ep.her else "")
    chrome.blit(f_h1.render("fly replay", True, HIM), (U(PAD), U(9)))
    chrome.blit(f_lab.render(meta, True, FAINT), (U(PAD) + f_h1.size("fly replay")[0] + U(12), U(12)))
    pg.draw.line(chrome, EDGE, (0, U(HEAD) - 1), (W, U(HEAD) - 1), max(1, int(S)))
    pg.draw.line(chrome, EDGE, (U(PAD), U(LEG_Y) - U(5)), (W - U(PAD), U(LEG_Y) - U(5)), max(1, int(S)))

    # ---- the azimuth rulers, one per eye mode (baked; only one is blitted per frame)
    def ruler(span, labels):
        s = pg.Surface((R_RUL.w, R_RUL.h)); s.fill(CARD)
        for a, lab in labels:
            x = int(R_RUL.w / 2 - a / span * (R_RUL.w / 2))
            pg.draw.line(s, EDGE, (x, 0), (x, U(4)))
            t = f_small.render(lab, True, FAINT)
            s.blit(t, (min(max(0, x - t.get_width() // 2), R_RUL.w - t.get_width()), U(4)))
        return s
    LABS = [(180, "180 left"), (90, "90 left"), (0, "ahead"), (-90, "90 right"), (-180, "180 right")]
    RULERS = {"dots": ruler(190.0, LABS), "pano": ruler(180.0, LABS)}
    EYE_TITLE = {"dots": f"his eye   {ep.lum.shape[1]:,} ommatidia at their own azimuth / elevation",
                 "pano": "his eye   nearest-ommatidium panorama, blank past %.1f deg" % PANO_LIM}
    CHAN_TXT = {"green": "   green R1-R6", "uv": "   UV R7", "both": "   UV over green"}
    EYE_SURF = {(m, c): f_lab.render(EYE_TITLE[m] + (CHAN_TXT[c] if ep.lum_uv is not None else ""), True,
                                     DIM if c == "green" else UVC) for m in EYE_TITLE for c in CHANS}

    # ---- the control bar
    # the cycling buttons (uv, chan) are sized for their widest label so the bar does not twitch as they change
    UV_LAB = {"off": "uv off", "tint": "uv tint", "hatch": "uv hatch", "both": "uv tint+hatch"}
    CH_LAB = {"green": "eye green", "uv": "eye UV", "both": "eye UV+green"}
    order = [("home", "|<"), ("prev", "<"), ("play", "pause"), ("next", ">"), ("end", ">|"), None,
             ("slower", "-"), ("speed", "x30.00"), ("faster", "+"), None,
             ("fovdn", "-"), ("fov", "fov 150"), ("fovup", "+"), None,
             ("dots", "dots"), ("pano", "panorama"), ("chan", max(CH_LAB.values(), key=len)), None,
             ("uv", max(UV_LAB.values(), key=len)), ("smooth", "smooth"), ("loop", "loop"), None, ("help", "?")]
    btns = collections.OrderedDict(); x = U(PAD); BH = U(26); BY = U(36)
    for it in order:
        if it is None: x += U(12); continue
        bid, lab = it
        w = max(U(26), f_ui.size(lab)[0] + U(16))
        b = Btn(bid, lab); b.rect = pg.Rect(x, BY, w, BH); btns[bid] = b; x += w + U(4)
    btns["speed"].tip = "ro"; btns["fov"].tip = "ro"
    if not ep.can_uv: btns["uv"].tip = "ro"; btns["uv"].label = "uv n/a"        # no UV world to raytrace
    if ep.lum_uv is None: btns["chan"].tip = "ro"; btns["chan"].label = "no lum_uv"

    pos = 0.0; playing = False; spd = SPEEDS.index(1); dragging = False; looping = bool(args.loop)
    eye_mode = args.eye; show_help = False; fov = float(args.fov)
    clock = pg.time.Clock(); last = time.perf_counter()
    stats = collections.defaultdict(lambda: collections.deque(maxlen=4096))   # bounded: the live loop runs for hours
    last_px = [None]; full = [True]        # repaint the whole background: first frame, and after the help card

    def draw_path(i):
        nonlocal path_to
        if i < path_to: path.fill((0, 0, 0, 0)); path_to = 0
        if i > path_to:
            pg.draw.lines(path, (226, 166, 59, 190), False, PTS[path_to:i + 1], max(1, int(round(1.2 * S))))
            path_to = i

    def draw_btn(b):
        on = b.on
        col = (BTN_ON_HOT if b.hot else BTN_ON) if on else (BTN_HOT if b.hot else BTN)
        if b.tip == "ro": col = (18, 22, 29)
        pg.draw.rect(display, col, b.rect, border_radius=U(5))
        pg.draw.rect(display, HIM if on else EDGE, b.rect, max(1, int(S)), border_radius=U(5))
        t = f_ui.render(b.label, True, HIM if on else (DIM if b.tip == "ro" else INK))
        display.blit(t, (b.rect.centerx - t.get_width() // 2, b.rect.centery - t.get_height() // 2))

    def help_card():
        ov = pg.Surface((W, H), pg.SRCALPHA); ov.fill((8, 10, 14, 216)); display.blit(ov, (0, 0))
        cw, ch = U(560), U(24) * (len(HELP) + 3)
        r = pg.Rect((W - cw) // 2, (H - ch) // 2, cw, ch)
        pg.draw.rect(display, CARD, r, border_radius=U(8)); pg.draw.rect(display, EDGE, r, max(1, int(S)), border_radius=U(8))
        display.blit(f_h1.render("keys", True, HIM), (r.x + U(18), r.y + U(14)))
        for k, (key, what) in enumerate(HELP):
            y = r.y + U(46) + k * U(24)
            display.blit(f_ui.render(key, True, INK), (r.x + U(18), y))
            display.blit(f_ui.render(what, True, DIM), (r.x + U(230), y))
        display.blit(f_small.render("h, ? or esc to close", True, FAINT), (r.x + U(18), r.bottom - U(22)))

    def frame(i):
        t = time.perf_counter()
        if full[0]: display.blit(chrome, (0, 0)); last_px[0] = None; full[0] = False
        # -- human view (the newest finished frame at or before the playhead), plus the UV false colour over it
        j, g, ug = hv.newest_at_or_before(i)
        if g is not None:
            if uv_mode != "off" and ug is not None: _uv_comp(g, ug, UV_BITS[uv_mode], HVBUF)
            else: _gray_rgb(g, HVBUF)
            src = pg.image.frombuffer(HVBUF, (HVW, HVH), "RGB")
            if R_HV.w == HVW and R_HV.h == HVH: display.blit(src, R_HV.topleft)
            else:
                if HVSCALED[0] is None: HVSCALED[0] = pg.transform.smoothscale(src, R_HV.size)
                else: pg.transform.smoothscale(src, R_HV.size, HVSCALED[0])
                display.blit(HVSCALED[0], R_HV.topleft)
        else:
            pg.draw.rect(display, PANEL, R_HV)
        stats["hv"].append(time.perf_counter() - t); t = time.perf_counter()
        # -- the eye: dots, or the nearest-column panorama
        mode = eye_mode; ch = 0 if chan == "green" else (1 if chan == "uv" else 2)
        if mode == "pano" and pano.ready:
            if ch: _splat2(ep.lum[i], ep.lum_uv[i], pano.near, PFLAT, ch, *BLANK)
            else: _splat(ep.lum[i], pano.near, PFLAT, *BLANK)
            display.blit(pg.image.frombuffer(PBUF, (R_EYE.w, R_EYE.h), "RGB"), R_EYE.topleft)
            pg.draw.line(display, (226, 166, 59, 90), (R_EYE.centerx, R_EYE.y), (R_EYE.centerx, R_EYE.bottom), 1)
            pg.draw.line(display, (70, 78, 94), (R_EYE.x, R_EYE.centery), (R_EYE.right, R_EYE.centery), 1)
        else:
            mode = "dots"
            # the written pixels are the same set every frame, so no clear - but a channel switch changes what is
            # written into them, not which, so there is nothing stale to wipe either
            if ch: _paint2(ep.lum[i], ep.lum_uv[i], ridx, rsrc, EFLAT, ch)
            else: _paint(ep.lum[i], ridx, rsrc, EFLAT)
            display.blit(pg.image.frombuffer(EBUF, (R_EYE.w, R_EYE.h), "RGB"), R_EYE.topleft)
        display.blit(RULERS[mode], R_RUL.topleft)
        display.blit(chrome, (R_EYE.x, R_EYE.y - U(TITLE_H)), pg.Rect(R_EYE.x, R_EYE.y - U(TITLE_H), R_EYE.w, U(TITLE_H)))
        display.blit(EYE_SURF[(eye_mode if (eye_mode == "dots" or pano.ready) else "dots", chan)], (R_EYE.x + U(4), R_EYE.y - U(TITLE_H) + U(4)))
        if eye_mode == "pano" and not pano.ready:
            t_ = f_small.render("building the nearest-ommatidium table...", True, FAINT)
            display.blit(t_, (R_EYE.centerx - t_.get_width() // 2, R_EYE.centery))
        # an ocelli panel would go here - but nothing identifies or drives the three ocelli yet, so there is no signal to draw.
        stats["eye"].append(time.perf_counter() - t); t = time.perf_counter()
        # -- map
        display.blit(base, R_MAP.topleft); draw_path(i); display.blit(path, R_MAP.topleft)
        hx, hy = PTS[i]; hx += R_MAP.x; hy += R_MAP.y
        if PTS2 is not None:
            qx, qy = PTS2[i]; pg.draw.circle(display, HER, (qx + R_MAP.x, qy + R_MAP.y), U(5))
        pg.draw.circle(display, HIM, (hx, hy), U(5))
        hr = np.radians(ep.pose[i][2]); pg.draw.line(display, HIM, (hx, hy), (hx + U(14) * np.cos(hr), hy - U(14) * np.sin(hr)), max(1, int(round(2 * S))))
        if ep.touch is not None and ep.touch[i]:
            kind = int(ep.touch_kind[i]) if ep.touch_kind is not None else 1
            pg.draw.circle(display, HER if kind == 2 else DIM, (hx, hy), U(9), max(1, int(round(2 * S))))
        stats["map"].append(time.perf_counter() - t); t = time.perf_counter()
        # -- traces: repaint only the strip the playhead left behind
        px = R_TR.x + int(i / max(1, ep.n - 1) * (R_TR.w - 1))
        if last_px[0] is None: display.blit(traces, R_TR.topleft)
        else:
            w_ = max(2, int(2 * S)) + abs(px - last_px[0])
            x0 = max(R_TR.x, min(px, last_px[0]) - 1)
            r_ = pg.Rect(x0, R_TR.y, min(w_ + 2, R_TR.right - x0), R_TR.h)
            display.blit(traces, r_.topleft, pg.Rect(r_.x - R_TR.x, 0, r_.w, r_.h))
        pg.draw.line(display, (244, 247, 252), (px, R_TR.y), (px, R_TR.bottom), max(1, int(S)))
        last_px[0] = px
        stats["tr"].append(time.perf_counter() - t); t = time.perf_counter()
        # -- header: the panel title that carries state, the readout, the buttons, the bar
        display.blit(chrome, (0, 0), R_HEAD)
        display.blit(chrome, (R_HV.x, R_HV.y - U(TITLE_H)), pg.Rect(R_HV.x, R_HV.y - U(TITLE_H), R_HV.w, U(TITLE_H)))
        hv_txt = f"human view   his raytracer, pinhole {fov:g} deg" + ("   camera smoothed" if hv.smooth else "   raw pose")
        display.blit(f_lab.render(hv_txt, True, DIM), (R_HV.x + U(4), R_HV.y - U(TITLE_H) + U(4)))
        if uv_mode != "off":                                  # the mode belongs in the title, in the UV colour
            display.blit(f_lab.render("   + UV " + UV_TITLE[uv_mode] + ("" if hv.ud == 1 else " (half res)"), True, UVC),
                         (R_HV.x + U(4) + f_lab.size(hv_txt)[0], R_HV.y - U(TITLE_H) + U(4)))
        btns["play"].label = "pause" if playing else "play"
        btns["speed"].label = f"x{SPEEDS[spd]:g}"; btns["fov"].label = f"fov {fov:g}"
        btns["dots"].on = eye_mode == "dots"; btns["pano"].on = eye_mode == "pano"
        if ep.can_uv: btns["uv"].label = UV_LAB[uv_mode]; btns["uv"].on = uv_mode != "off"
        if ep.lum_uv is not None: btns["chan"].label = CH_LAB[chan]; btns["chan"].on = chan != "green"
        btns["smooth"].on = hv.smooth; btns["loop"].on = looping; btns["help"].on = show_help
        for b in btns.values(): draw_btn(b)
        fill = pg.Rect(R_BAR.x, R_BAR.y, max(U(3), int(R_BAR.w * i / max(1, ep.n - 1))), R_BAR.h)
        pg.draw.rect(display, (120, 92, 38), fill, border_radius=U(3))
        kx = R_BAR.x + int(R_BAR.w * i / max(1, ep.n - 1))
        pg.draw.circle(display, HIM, (min(kx, R_BAR.right - U(4)), R_BAR.centery), U(6))
        pg.draw.rect(display, EDGE, R_BAR, max(1, int(S)), border_radius=U(3))
        tt = f_mono.render(f"{clock_str(i / ep.fps)} / {clock_str((ep.n - 1) / ep.fps)}", True, INK)
        display.blit(tt, (W - U(PAD) - tt.get_width(), U(10)))
        fr = f_small.render(f"frame {i} / {ep.n - 1}", True, FAINT)
        display.blit(fr, (W - U(PAD) - fr.get_width(), U(10) + tt.get_height() + U(1)))
        # -- footer
        display.blit(chrome, (0, R_FOOT.y), R_FOOT)
        lag = "" if j == i else f"   view {j - i:+d}"
        pano_s = "" if (pano.secs is None or eye_mode != "pano") else f"   pano table {pano.secs * 1000:.0f} ms"
        info = (f"heading {ep.pose[i][2] % 360:5.1f} deg" + (f"  ->  camera {ep.cam_h[i] % 360:5.1f} deg" if hv.smooth and ep.K > 1 else "")
                + f"   steering chunk {ep.K} frames ({ep.K * 1000 // ep.fps} ms)   {clock.get_fps():4.0f} fps{lag}{pano_s}")
        display.blit(f_small.render(info, True, FAINT), (U(PAD), R_FOOT.y + U(5)))
        if show_help: help_card()
        pg.display.flip()
        stats["chrome"].append(time.perf_counter() - t)

    if args.bench:
        n = min(args.bench, ep.n); step = max(1, ep.n // max(1, n))
        worker.close()                                     # bench renders synchronously, to time the kernel honestly
        if args.eye == "pano":
            while not pano.ready: time.sleep(0.02)
        t0 = time.perf_counter(); sync = []
        for k in range(n):
            i = min(ep.n - 1, k * step)
            ts = time.perf_counter(); hv.render(i); sync.append(time.perf_counter() - ts)
            frame(i)
        wall = time.perf_counter() - t0
        def ms(a): a = np.array(a) * 1000; return f"mean {a.mean():6.2f}  p50 {np.median(a):6.2f}  p95 {np.percentile(a, 95):6.2f}"
        zero, mx = ep.heading_steps()
        print(f"{args.npz}: {ep.n} frames, {ep.fps} fps, world={ep.world}, her in scene={ep.her}, retina {ep.lum.shape[1]} columns"
              + ("  + lum_uv" if ep.lum_uv is not None else "  (no lum_uv)") + (f", dish r={ep.arena_r:g} m" if ep.arena else ""))
        print(f"  window {W}x{H} (scale {S:g}), eye panel {eye_mode}/{chan}, fov {fov:g}, uv layer {uv_mode}"
              + (f" at {hv.UW}x{hv.UH}" if uv_mode != "off" else "") + (" (this world has no UV description)" if not ep.can_uv else ""))
        print(f"  control bar ends at x={max(b.rect.right for b in btns.values())} of {W}")
        print(f"  steering chunk {ep.K} frames: {zero * 100:.0f}% of frames have no heading change, largest step {mx:.1f} deg")
        print(f"  first render (numba compile) {t_compile * 1000:.0f} ms" + (f", pano table {pano.secs * 1000:.0f} ms" if pano.secs else ""))
        print(f"  shade {HVW}x{HVH} ({HVW * HVH} rays" + (f" + {hv.UW * hv.UH} UV rays" if uv_mode != "off" else "") + f")  ms: {ms(sync)}")
        for k in ("hv", "eye", "map", "tr", "chrome"): print(f"  panel {k:7s} ms: {ms(stats[k])}")
        tot = sum(float(np.median(stats[k])) for k in ("hv", "eye", "map", "tr", "chrome")) * 1000
        print(f"  window without the raytracer (p50 sum): {tot:.2f} ms/frame  ->  {1000 / tot:.0f} fps")
        print(f"  {n} frames incl. synchronous render in {wall:.2f} s = {n / wall:.1f} fps")
        if args.shot:
            pg.image.save(display, args.shot); print(f"  wrote {args.shot}")
        pg.quit(); return

    zero, mxs = ep.heading_steps()
    print(f"{args.npz}: {ep.n} frames at {ep.fps} fps ({ep.world}); her in his scene: {ep.her}; numba compile {t_compile * 1000:.0f} ms")
    print(f"  steering chunk = {ep.K} frames ({ep.K * 1000 // ep.fps} ms): {zero * 100:.0f}% of frames have no heading change, "
          f"largest single-frame step {mxs:.1f} deg -> the human camera is smoothed by default (s toggles)")

    def set_fov(v):
        nonlocal fov
        v = float(np.clip(v, 30.0, 170.0))
        if abs(v - fov) < 1e-9: return
        fov = v; hv.configure(fov_deg=fov); worker.poke()

    def scrub_to(mx_):
        return float(np.clip((mx_ - R_BAR.x) / max(1, R_BAR.w), 0, 1) * (ep.n - 1))

    def press(bid, shift=False):
        nonlocal playing, pos, spd, eye_mode, show_help, looping, uv_mode, chan
        if bid == "play": playing = not playing
        elif bid == "prev": pos = max(0, int(pos) - 1); playing = False
        elif bid == "next": pos = min(ep.n - 1, int(pos) + 1); playing = False
        elif bid == "home": pos = 0.0
        elif bid == "end": pos = ep.n - 1.0
        elif bid == "slower": spd = max(0, spd - 1)
        elif bid == "faster": spd = min(len(SPEEDS) - 1, spd + 1)
        elif bid == "fovdn": set_fov(fov - (15 if shift else 5))
        elif bid == "fovup": set_fov(fov + (15 if shift else 5))
        elif bid == "fov": set_fov(args.fov)
        elif bid in ("dots", "pano"):
            eye_mode = bid
            if bid == "pano": pano.start()
        elif bid == "uv":
            if ep.can_uv:
                uv_mode = UV_MODES[(UV_MODES.index(uv_mode) + (-1 if shift else 1)) % len(UV_MODES)]
                hv.set_uv(uv_mode); worker.poke()             # the UV LRU needs filling; the visible one is untouched
        elif bid == "chan":
            if ep.lum_uv is not None: chan = CHANS[(CHANS.index(chan) + (-1 if shift else 1)) % len(CHANS)]
        elif bid == "smooth": hv.configure(smooth=not hv.smooth); worker.poke()
        elif bid == "loop": looping = not looping
        elif bid == "help":
            show_help = not show_help
            if not show_help: full[0] = True

    running = True
    while running:
        for e in pg.event.get():
            if e.type == pg.QUIT: running = False
            elif e.type == pg.KEYDOWN:
                sh = e.mod & pg.KMOD_SHIFT
                if e.key == pg.K_ESCAPE and show_help: show_help = False; full[0] = True
                elif e.key in (pg.K_q, pg.K_ESCAPE): running = False
                elif e.key == pg.K_SPACE: playing = not playing
                elif e.key in (pg.K_LEFT, pg.K_COMMA): pos = max(0, int(pos) - (ep.fps if sh else 1)); playing = False
                elif e.key in (pg.K_RIGHT, pg.K_PERIOD): pos = min(ep.n - 1, int(pos) + (ep.fps if sh else 1)); playing = False
                elif e.key == pg.K_LEFTBRACKET: press("slower")
                elif e.key == pg.K_RIGHTBRACKET: press("faster")
                elif e.key == pg.K_HOME: pos = 0.0
                elif e.key == pg.K_END: pos = ep.n - 1.0
                elif e.key == pg.K_MINUS: press("fovdn", sh)
                elif e.key in (pg.K_EQUALS, pg.K_PLUS): press("fovup", sh)
                elif e.key == pg.K_0: set_fov(args.fov)
                elif e.key == pg.K_v: press("pano" if eye_mode == "dots" else "dots")
                elif e.key == pg.K_u: press("uv", sh)
                elif e.key == pg.K_c: press("chan", sh)
                elif e.key == pg.K_s: press("smooth")
                elif e.key == pg.K_l: press("loop")
                elif e.key in (pg.K_h, pg.K_SLASH, pg.K_QUESTION): press("help")
            elif e.type == pg.MOUSEBUTTONDOWN and e.button == 1:
                if show_help: show_help = False; full[0] = True
                elif R_BAR.inflate(0, U(10)).collidepoint(e.pos): dragging = True; pos = scrub_to(e.pos[0])
                else:
                    for b in btns.values():
                        if b.tip != "ro" and b.rect.collidepoint(e.pos): press(b.id, pg.key.get_mods() & pg.KMOD_SHIFT); break
            elif e.type == pg.MOUSEBUTTONUP and e.button == 1: dragging = False
            elif e.type == pg.MOUSEMOTION:
                for b in btns.values(): b.hot = b.tip != "ro" and b.rect.collidepoint(e.pos)
                if dragging: pos = scrub_to(e.pos[0])
            elif e.type == pg.MOUSEWHEEL:
                mxp = pg.mouse.get_pos()
                if R_HV.collidepoint(mxp): set_fov(fov - 5 * e.y)
        now = time.perf_counter(); dt = min(0.25, now - last); last = now
        if playing and not dragging:
            pos += SPEEDS[spd] * ep.fps * dt                # the episode's own clock; frames drop, time does not
            if pos >= ep.n - 1:
                if looping: pos -= (ep.n - 1)
                else: pos = ep.n - 1.0; playing = False
        i = int(pos)
        worker.ask(i, max(1, round(SPEEDS[spd] * ep.fps / max(1e-6, clock.get_fps() or 60))))
        frame(i)
        clock.tick(args.cap)
    worker.close(); pg.quit()


def main():
    ap = argparse.ArgumentParser(description="native replay viewer for a fly episode npz")
    ap.add_argument("npz")
    ap.add_argument("--fov", type=float, default=100.0, help="human-view horizontal field of view in degrees (- and = change it live)")
    ap.add_argument("--size", default="640x320", help="the human view's render resolution (it is upscaled to the panel)")
    ap.add_argument("--eye", default="dots", choices=("dots", "pano"), help="which fly view to open with")
    ap.add_argument("--uv", default="off", choices=UV_MODES, help="human-view UV false-colour layer to open with (garden only; `u` cycles)")
    ap.add_argument("--chan", default="green", choices=CHANS, help="eye panel channel to open with (needs lum_uv in the file; `c` cycles)")
    ap.add_argument("--uv-div", type=int, default=1, help="render the UV pass at 1/N the human view's resolution (2 = a quarter of the rays)")
    ap.add_argument("--no-smooth", action="store_true", help="open with the raw per-chunk heading (judders; `s` toggles)")
    ap.add_argument("--loop", action="store_true", help="loop at the end")
    ap.add_argument("--cache", type=int, default=256, help="human-view frames kept (LRU)")
    ap.add_argument("--cap", type=int, default=120, help="display frame-rate cap")
    ap.add_argument("--scale", type=float, default=1.0, help="window scale for high-DPI screens (e.g. 1.5 or 2)")
    ap.add_argument("--her", default="auto", choices=("auto", "always", "never"), help="put her in his scene: auto believes the episode's dist / her pose moving")
    ap.add_argument("--bench", type=int, default=0, help="render N frames headless, print timings, no window")
    ap.add_argument("--shot", default=None, help="with --bench: save the last window to this png")
    run(ap.parse_args())


if __name__ == "__main__":
    main()
