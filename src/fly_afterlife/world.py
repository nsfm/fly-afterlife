"""
world: the room. walls, pillars, the other fly, and the queries the senses need.

    room = Room(half=2.0, height=1.0, albedo=0.6, posts=[(x, y, r, albedo), ...])
    room.step_frame(him, her, fps)        # move both, resolve walls, pillars, the pair
    scene = room.scene([her])             # an omma.Scene for his eye (bodies as spheres)
    room.contacts                         # frames of fly-fly contact so far

this first version reproduces world/pair.py's physics expression for expression (including two
different pillar-hold formulas for him and her, which are numerically not identical and are kept
so the oracle check passes; unify as its own change). scalar fields (odour plume, temperature,
humidity, light) come next (docs/ARCHITECTURE.md).
"""
from __future__ import annotations
from dataclasses import dataclass, field
import sys
import numpy as np
sys.path.insert(0, "seam")
from omma import Scene  # noqa: E402
from .body import Body


@dataclass
class Room:
    half: float = 2.0            # walls at |x|, |y| = half
    height: float = 1.0          # wall height (m), what the eye sees
    albedo: float = 0.6
    sky: float = 0.8
    ground: float = 0.4
    posts: list = field(default_factory=list)   # (x, y, r, albedo): floor-to-sky cylinders
    contacts: int = 0            # frames of fly-fly contact

    # ---- the eye's view
    def scene(self, others: list[Body]) -> Scene:
        sph = [(np.array([b.x, b.y, 0.5]), b.r, b.albedo) for b in others if b.present]
        return Scene(sky=self.sky, ground=self.ground, spheres=sph, pillars=[(x, y, r, a) for x, y, r, a in self.posts], walls=dict(half=self.half, height=self.height, albedo=self.albedo))

    # ---- contacts
    def wall(self, b: Body) -> None:
        """hold at the wall; the side the wall is on (relative to heading) owns the touch."""
        W_ = self.half - b.r; nx_ = ny_ = 0.0; px_, py_ = b.x, b.y
        if px_ > W_: px_ = W_; nx_ = -1.0
        if px_ < -W_: px_ = -W_; nx_ = 1.0
        if py_ > W_: py_ = W_; ny_ = -1.0
        if py_ < -W_: py_ = -W_; ny_ = 1.0
        b.x, b.y = px_, py_
        if nx_ == 0.0 and ny_ == 0.0: return
        brg_ = (np.degrees(np.arctan2(-ny_, -nx_)) - b.h + 180) % 360 - 180      # bearing of the wall (opposite the inward normal)
        b.touched = "L" if brg_ >= 0 else "R"; b.kind = 1   # no head-on class for a wall: whichever side touched first owns the reflex

    def pillars_ratio(self, b: Body) -> None:
        """his pillar hold (pair.py form: scale the offset vector)."""
        for ox, oy, r_, _ in self.posts:
            dd = np.hypot(b.x - ox, b.y - oy)
            if dd < r_ + b.r:
                b.x, b.y = ox + (b.x - ox) / max(dd, 1e-6) * (r_ + b.r), oy + (b.y - oy) / max(dd, 1e-6) * (r_ + b.r)
                brg = (np.degrees(np.arctan2(oy - b.y, ox - b.x)) - b.h + 180) % 360 - 180; b.touched = "L" if brg >= 0 else "R"; b.kind = 1

    def pillars_angle(self, b: Body) -> None:
        """her pillar hold (pair.py form: polar angle). numerically distinct from pillars_ratio; kept for the oracle."""
        for ox, oy, r_, _ in self.posts:
            ddf = np.hypot(b.x - ox, b.y - oy)
            if ddf < r_ + b.r:
                ang_ = np.arctan2(b.y - oy, b.x - ox); b.x, b.y = ox + (r_ + b.r) * np.cos(ang_), oy + (r_ + b.r) * np.sin(ang_)
                brg_ = (np.degrees(np.arctan2(oy - b.y, ox - b.x)) - b.h + 180) % 360 - 180; b.touched = "L" if brg_ >= 0 else "R"

    def pair(self, m: Body, f: Body) -> None:
        """solid bodies: push apart on overlap; both feel the contact (kind 2 on him; 8-degree head-on class kept here)."""
        dd = np.hypot(m.x - f.x, m.y - f.y)
        if dd < m.r + f.r:
            self.contacts += 1; m.kind = 2; push = (m.r + f.r - dd) / 2; ux_, uy_ = (m.x - f.x) / max(dd, 1e-6), (m.y - f.y) / max(dd, 1e-6)
            m.x += ux_ * push; m.y += uy_ * push; f.x -= ux_ * push; f.y -= uy_ * push
            brg = (np.degrees(np.arctan2(f.y - m.y, f.x - m.x)) - m.h + 180) % 360 - 180; m.touched = "L" if brg > 8 else ("R" if brg < -8 else "B")
            brg2 = (np.degrees(np.arctan2(m.y - f.y, m.x - f.x)) - f.h + 180) % 360 - 180; f.touched = "L" if brg2 > 8 else ("R" if brg2 < -8 else "B")

    def step_frame(self, m: Body, f: Body, fps: int) -> None:
        """one frame: move, then walls, pillars and the pair, in pair.py's order. contacts are
        cleared first; after this call each body's `touched` / `kind` describe this frame."""
        m.clear_contact(); f.clear_contact()
        m.advance(fps)
        if f.present: f.advance(fps)
        self.wall(m); self.wall(f)
        self.pillars_ratio(m)
        if f.present:
            self.pillars_angle(f)
            self.pair(m, f)

    def distance(self, m: Body, f: Body) -> float:
        return np.hypot(m.x - f.x, m.y - f.y) if f.present else np.inf


@dataclass
class Drum:
    """the optomotor drum: a striped cylinder at infinity around a fly that turns in place (loop.py --mode drum).
    programme = [(seconds, deg/s), ...]; the drum's phase advances every frame; the body does not translate."""
    period_deg: float = 30.0
    lo: float = 0.2
    hi: float = 0.8
    half_height_deg: float = 30.0
    programme: list = field(default_factory=lambda: [(2, 0.0), (4, 30.0), (1, 0.0), (4, -30.0), (1, 0.0)])
    sky: float = 0.85
    ground: float = 0.35
    phase: float = 0.0
    frame: int = 0
    contacts: int = 0
    source: str = "closedloop.py / loop.py --mode drum, 2026-09-16: still 2 s, left 30 deg/s 4 s, still 1 s, right 30 deg/s 4 s, still 1 s"

    def rate(self, t: float) -> float:
        acc = 0.0
        for sec, r in self.programme:
            if t < acc + sec: return r
            acc += sec
        return 0.0

    def scene(self, others: list) -> Scene:
        return Scene(sky=self.sky, ground=self.ground, drum=dict(period_deg=self.period_deg, phase_deg=self.phase, lo=self.lo, hi=self.hi, half_height_deg=self.half_height_deg))

    def step_frame(self, m: Body, f, fps: int) -> None:
        m.clear_contact()
        if f is not None: f.clear_contact()
        self.phase += self.rate(self.frame / fps) / fps; self.frame += 1
        m.advance(fps)

    def distance(self, m: Body, f) -> float: return np.inf
