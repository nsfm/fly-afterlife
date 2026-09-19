"""arena: the open-field dish of the locomotion literature (docs/BENCHMARKS.md). a circle of radius `radius` (2.8 sim m =
4.2 cm, Soibam 2012 / the opynfield corpus), a low wall of height `height` (0.47 m = 7 mm), a uniform floor (the room's
sky / ground gradient), nothing else: the wall is the only visual object, which is the point (Soibam: the wall is
explored by sight). he starts at the centre. same interface as Room (scene / step_frame / wall)."""
from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np
from .world import Room
from .body import Body
from omma import Scene


@dataclass
class Arena(Room):
    radius: float = 2.8
    contacts: int = 0
    events: list = field(default_factory=list)

    def __post_init__(self):
        self.half = self.radius; self.posts = []

    def scene(self, others: list) -> Scene:
        sph = [(np.array([b.x, b.y, 0.5]), b.r, b.albedo) for b in others if b.present]
        return Scene(sky=self.sky, ground=self.ground, spheres=sph, pillars=[], walls=None, ring=dict(radius=self.radius, height=self.height, albedo=self.albedo))

    def wall(self, b: Body) -> None:
        """hold inside the circle; the side the wall is on (relative to heading) owns the touch."""
        d = np.hypot(b.x, b.y); W_ = self.radius - b.r
        if d <= W_: return
        b.x, b.y = b.x / d * W_, b.y / d * W_
        brg_ = (np.degrees(np.arctan2(b.y, b.x)) - b.h + 180) % 360 - 180      # bearing of the wall = outward radial
        b.touched = "L" if brg_ >= 0 else "R"; b.kind = 1

    def step_frame(self, m: Body, f, fps: int) -> None:
        m.clear_contact()
        if f is not None: f.clear_contact()
        m.advance(fps)
        if f is not None and f.present: f.advance(fps)
        self.wall(m)
        if f is not None and f.present: self.wall(f); self.pair(m, f)
