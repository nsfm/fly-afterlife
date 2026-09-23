"""leg_senses: the per-leg sensory map (world/leg_senses.npz, scripts/build_leg_senses.py; docs/physiology/leg_senses_map.md)
as engine indices. campaign item 6 (09-22): the body loop's --senses v2 and the cord's --floor standing read their rows from here.

    LS = leg_cells(M.bodyId)          # LS["lm"]["campaniform"] -> sorted int64 indices into the brain
    standing = union(LS, ("campaniform", "untyped"))
"""
from __future__ import annotations
import numpy as np

LEGS = ("lf", "lm", "lh", "rf", "rm", "rh")
KEYS = ("tactile", "proprio_all", "claw_50", "claw_51", "hook_39", "hook_41", "club", "co_unclassified",
        "hair_plate_45", "hair_plate_52", "hair_plate_xx", "hair_plate", "campaniform", "untyped")


def leg_cells(body_ids, path: str = "world/leg_senses.npz") -> dict:
    """{leg: {key: indices}}: the map's bodyIds for each leg and key, mapped to indices of `body_ids` (cells absent from the
    brain file are dropped). `hair_plate` = the three hair-plate keys together."""
    z = np.load(path, allow_pickle=True); pos = {int(b): i for i, b in enumerate(np.asarray(body_ids))}
    return {leg: {k: np.array(sorted(pos[int(b)] for b in z[f"{leg}_{k}"] if int(b) in pos), np.int64) for k in KEYS} for leg in LEGS}


def union(LS: dict, keys, legs=LEGS) -> np.ndarray:
    """every leg's cells of the named keys, one sorted index array."""
    parts = [LS[l][k] for l in legs for k in keys]
    return np.unique(np.concatenate(parts)).astype(np.int64) if parts else np.zeros(0, np.int64)


def counts(LS: dict, keys) -> str:
    """'key: lf a, lm b, ... (total)' per key, for the startup print."""
    return "\n".join(f"  {k:16s} " + " ".join(f"{l} {len(LS[l][k]):4d}" for l in LEGS) + f"   total {sum(len(LS[l][k]) for l in LEGS)}" for k in keys)
