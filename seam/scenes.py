"""scenes.py - the shared stimulus set for the world renderer. frame_scene(stim, t) -> (Scene, heading_deg).
fly at origin heading +x, ground z=0, eye z=0.5. every stimulus holds its pre-state for the first second."""
import numpy as np
from omma import Scene
def ball_path(az_deg, t, r=0.3):
    az = np.radians(az_deg); dist = 3.0 if t < 1.0 else 3.0 - 2.6 * (t - 1.0)
    return (np.array([np.cos(az) * dist, np.sin(az) * dist, 0.5]), r, 0.05)
def frame_scene(s, t):
    if s == "empty":        return Scene(), 0.0
    if s == "loom_ahead":   return Scene(spheres=[ball_path(0, t)]), 0.0
    if s == "loom_left":    return Scene(spheres=[ball_path(60, t)]), 0.0
    if s == "loom_right":   return Scene(spheres=[ball_path(-60, t)]), 0.0
    if s in ("recede_ahead", "recede_left", "recede_right"):
        az = np.radians({"recede_ahead": 0, "recede_left": 60, "recede_right": -60}[s]); dist = 0.4 if t < 1.0 else 0.4 + 2.6 * (t - 1.0)
        return Scene(spheres=[(np.array([np.cos(az) * dist, np.sin(az) * dist, 0.5]), 0.3, 0.05)]), 0.0
    if s in ("static_ahead", "static_left", "static_right"):
        az = np.radians({"static_ahead": 0, "static_left": 60, "static_right": -60}[s])
        return Scene(spheres=[(np.array([np.cos(az), np.sin(az), 0.5]), 0.3, 0.05)]), 0.0
    if s in ("yaw_left", "yaw_right"):
        ring = [(np.array([2 * np.cos(a), 2 * np.sin(a), 0.5]), 0.25, 0.05) for a in np.radians(np.arange(0, 360, 30))]
        h = 0.0 if t < 1.0 else (90.0 * (t - 1.0)) * (1 if s == "yaw_left" else -1)
        return Scene(spheres=ring), h
    raise SystemExit(f"unknown stim {s}")
