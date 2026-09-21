"""
body: a physical fly. pose, speed, collision radius, and what it is touching this frame.

the body knows nothing about neurons: effectors set its speed and heading, the world resolves
its contacts. the male and the female are the same class with different radii and brains.

this first version reproduces world/pair.py's kinematics exactly (same expressions, same float
order) so the oracle check passes. gait phases, six legs and body-part contacts come next
(docs/ARCHITECTURE.md).
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass
class Body:
    name: str
    x: float
    y: float
    h: float                     # heading, degrees, counter-clockwise from +x
    r: float                     # collision radius (m); drawn at this size
    v: float = 0.0               # forward speed (m/s)
    albedo: float = 0.1          # how the other fly's eye sees it
    present: bool = True         # False = the body exists (pose is logged) but is not in the world
    touched: str | None = None   # "L" / "R" / "B" / None: side of this frame's contact, relative to heading
    kind: int = 0                # 0 none, 1 wall or pillar, 2 the other fly
    labellum: str | None = None  # what the labellum touches: "sugar" when he stands still on the fruit (a geometry stand-in for extension, 09-21)
    z: float = 0.0               # height of his feet above the ground (m): 0 on the floor, up the dome of a fruit or a stone when the world lets him climb (09-21)
    ant_ahead: float = 0.1       # antenna tips: this far ahead of the body centre (m) ...
    ant_half: float = 0.15       # ... and this far to each side. the defaults are the original wide geometry (09-19: 4.5 mm apart at
                                 # 15 mm per m, twelve times a fly's ~0.35 mm; `pair.py --antennae real` sets 0.08 / 0.012)

    def advance(self, fps: int) -> None:
        """one frame of straight walking at speed v along heading h."""
        self.x += self.v / fps * np.cos(np.radians(self.h)); self.y += self.v / fps * np.sin(np.radians(self.h))

    def clear_contact(self) -> None:
        self.touched = None; self.kind = 0

    def antennae(self) -> tuple[np.ndarray, np.ndarray]:
        """left and right antenna tips (the odour, warmth and humidity sample points) at the current pose."""
        return self.antennae_at(self.x, self.y, self.h)

    def antennae_at(self, x: float, y: float, h: float) -> tuple[np.ndarray, np.ndarray]:
        """the antenna tips for a given pose (the episode samples the world at each frame's logged pose)."""
        hr = np.radians(h); fwd = np.array([np.cos(hr), np.sin(hr)]); left = np.array([-np.sin(hr), np.cos(hr)]); p = np.array([x, y])
        return p + self.ant_ahead * fwd + self.ant_half * left, p + self.ant_ahead * fwd - self.ant_half * left

    def bearing_to(self, x: float, y: float) -> float:
        """bearing of a point relative to heading, degrees in (-180, 180]; + = left."""
        return (np.degrees(np.arctan2(y - self.y, x - self.x)) - self.h + 180) % 360 - 180

    @property
    def pose(self) -> tuple[float, float, float]: return (self.x, self.y, self.h)
