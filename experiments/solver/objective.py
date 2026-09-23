"""the solver's objective (docs/SOLVER.md, "the objective"): read a body run's saved arrays with the readers' own rules and score them.
every rule below is the reader's (experiments/leg_pairs.py for lifts and pairs, the puppet reader for speed, body_loop.py's standing
line); the targets are the kinematic replay's and the puppet's numbers; the weights are ours and stated here and in the doc.

score = (W_STAND stand + W_STEP step + W_COORD coord + W_PROG prog) x (1 - min(0.9, P_BODY [body on the floor] + P_MN x fraction + P_TYPE x n)),
or x FALL_FACTOR instead if he falls. in [0, 1], higher is better; the prefilter's rejects score below 0 (run.py).
"""
from __future__ import annotations
import os, sys, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))   # experiments/, for leg_pairs
import leg_pairs as LP

# ---- weights and targets (the doc copies this block)
W_STAND, W_STEP, W_COORD, W_PROG = 0.20, 0.25, 0.30, 0.25   # sum 1
STAND_FULL = 10.05          # uN: his weight, all of it on the tarsi = 1
BODY_TOUCH = 1.0            # uN of mean body (thorax / abdomen / head) floor reaction after the warm-up: above it, P_BODY
P_BODY = 0.50               # the hard penalty for the body on the floor (a factor: half the score gone)
BODY_FALL = 3.0             # uN: above it he has fallen; the whole score x FALL_FACTOR
FALL_FACTOR = 0.02
LIFT_BAND = (5.0, 11.0)     # Hz per leg: the puppet's 5 Hz to the replay's 11 Hz; full credit inside
LIFT_SOFT, LIFT_ZERO = 15.0, 20.0   # 11-15 Hz ramps 1 -> 0.5, 15-20 ramps 0.5 -> 0; below 5 Hz credit is rate / 5 (0 lifts = 0)
BOTH_OFF_GOOD, BOTH_OFF_ZERO = 0.5, 1.0   # both-off / independence: <= 0.5 full, >= 1 (independence) none, linear between
ANTI_GOOD, ANTI_ZERO = 0.75, 0.5          # antiphase share: >= 0.75 full, <= 0.5 (chance) none; x min(1, n / ANTI_N)
ANTI_N = 20
PAIR_LIFTS = 40             # a pair's two credits x min(1, the pair's fewer lifts / 40): rare lifts make both-off and phase noise (40 in 17.9 s ~ 2.2 Hz)
SPEED_CAP = 2.0             # mm/s along heading: credit speed / 2, capped at 1 (the puppet walks 1.6, the replay 10.4)
MN_RANGE = (0.5, 60.0)      # Hz per leg motor neuron, mean after the warm-up
P_MN = 0.20                 # x the fraction of leg MNs outside MN_RANGE
TYPE_MAX = 200.0            # Hz per cell, any logged type (the leg MN types and the gained interneuron types)
P_TYPE, P_TYPE_CAP = 0.10, 0.30   # per type above TYPE_MAX, capped
PAIRS = (("lm-rm", 1, 4), ("lf-rf", 0, 3))
# the lift rule. 'standard' = leg_pairs.py's (smoothed 21 ms, <= 0.05 uN for >= 50 ms), the brief's and the default. 'fine' = the replay reader's
# (kin_read.py: 5 ms, >= 10 ms), which sees an 11 Hz swing of ~40 ms; the standard rule does not (the replay scores 0-2 lifts/s under it).
LIFT_RULES = {"standard": (21, 50), "fine": (5, 10)}
LEG6 = LP.LEG6; W = 2000; T0 = LP.T0


def _yaw(Q):
    w, x, y, z = Q.T; return np.arctan2(2 * (w * z + x * y), 1 - 2 * (y ** 2 + z ** 2))


def lifts(ft, rule="standard"):
    """leg_pairs.lifts with the rule's smoothing and minimum run; 'standard' is leg_pairs.lifts exactly."""
    if rule == "standard": return LP.lifts(ft)
    w, mn = LIFT_RULES[rule]; sm = np.convolve(ft, np.ones(w) / w, "same"); off = sm <= 0.05
    return np.array([a for a, b in LP.runs(off) if b - a >= mn and a >= T0], np.int64), off


def read_body(prefix: str, rule: str = "standard") -> dict:
    """every read the score uses, from <prefix>.npz and <prefix>.cells.npz (body_loop.py's saved arrays)."""
    D = np.load(prefix + ".npz", allow_pickle=True); C = np.load(prefix + ".cells.npz", allow_pickle=True)
    FT = D["tarsal_force"].astype(float); n = len(FT); secs = (n - T0) / 1000.0
    R = dict(lift_rule=rule, feet=float(FT[W:].sum(1).mean()), other=float(np.nanmean(D["other_leg_force"][W:].sum(1))), body=float(np.nanmean(D["body_force"][W:])))
    R["body_p95"] = float(np.nanpercentile(D["body_force"][W:], 95))
    on, off = {}, {}
    for i, l in enumerate(LEG6): on[l], off[l] = lifts(FT[:, i], rule)
    R["lifts"] = {l: int(len(on[l])) for l in LEG6}; R["lift_hz"] = {l: len(on[l]) / secs for l in LEG6}
    R["off_frac"] = {l: float(off[l][T0:].mean()) for l in LEG6}
    for name, a, b in PAIRS:
        la, lb = LEG6[a], LEG6[b]; p = LP.pair(on[la], on[lb], off[la], off[lb], n)
        R[name] = dict(both=p["both"], ind=p["ind"], ratio=p["ratio"], anti=p["anti"], n=p["n"], few=bool(p["few"]))
    P = D["thorax"].astype(float); ya = _yaw(D["quat"].astype(float)); dP = np.diff(P[W:, :2], axis=0) * 1000; h = np.stack([np.cos(ya[W + 1:]), np.sin(ya[W + 1:])], 1)
    R["speed_fwd"] = float((dP * h).sum(1).mean()); R["speed_abs"] = float(np.linalg.norm(dP, axis=1).mean()); R["thorax_z"] = float(P[W:, 2].mean())
    hz = C["frames"].astype(float)[W // 10:].mean(0) * 100.0; ty = C["type"].astype(str)
    R["mn_mean_hz"] = float(hz.mean()); R["mn_out_frac"] = float(((hz < MN_RANGE[0]) | (hz > MN_RANGE[1])).mean())
    R["mn_below"] = int((hz < MN_RANGE[0]).sum()); R["mn_above"] = int((hz > MN_RANGE[1]).sum()); R["mn_n"] = int(len(hz))
    types = {t: float(hz[ty == t].mean()) for t in sorted(set(ty))}
    if "x_ms" in C.files and C["x_ms"].size:
        xh = C["x_ms"].astype(float)[W:].mean(0) * 1000.0; xt = C["x_type"].astype(str)
        for t in sorted(set(xt)): types[t] = float(xh[xt == t].mean())
    R["type_hz"] = types; R["types_over"] = sorted(t for t, v in types.items() if v > TYPE_MAX)
    return R


def _ramp(x, zero, full):   # 0 at zero, 1 at full, linear, clipped; works for either direction
    if not np.isfinite(x): return 0.0
    return float(np.clip((x - zero) / (full - zero), 0.0, 1.0))


def lift_credit(r: float) -> float:
    if r < LIFT_BAND[0]: return r / LIFT_BAND[0]
    if r <= LIFT_BAND[1]: return 1.0
    if r <= LIFT_SOFT: return 1.0 - 0.5 * (r - LIFT_BAND[1]) / (LIFT_SOFT - LIFT_BAND[1])
    return max(0.0, 0.5 - 0.5 * (r - LIFT_SOFT) / (LIFT_ZERO - LIFT_SOFT))


def score(R: dict) -> dict:
    stand = float(np.clip(R["feet"] / STAND_FULL, 0.0, 1.0))
    step = float(np.mean([lift_credit(R["lift_hz"][l]) for l in LEG6]))
    cc = []
    for name, a, b in PAIRS:
        p = R[name]
        if p["few"]: cc += [0.0, 0.0]; continue
        gate = min(1.0, min(R["lifts"][LEG6[a]], R["lifts"][LEG6[b]]) / PAIR_LIFTS)
        cc += [gate * _ramp(p["ratio"], BOTH_OFF_ZERO, BOTH_OFF_GOOD), gate * _ramp(p["anti"], ANTI_ZERO, ANTI_GOOD) * min(1.0, p["n"] / ANTI_N)]
    coord = float(np.mean(cc)); prog = float(np.clip(R["speed_fwd"] / SPEED_CAP, 0.0, 1.0))
    pen_body = P_BODY if R["body"] > BODY_TOUCH else 0.0
    pen_mn = P_MN * R["mn_out_frac"]; pen_type = min(P_TYPE_CAP, P_TYPE * len(R["types_over"]))
    pos = W_STAND * stand + W_STEP * step + W_COORD * coord + W_PROG * prog
    fell = R["body"] > BODY_FALL
    total = FALL_FACTOR * pos if fell else pos * (1.0 - min(0.9, pen_body + pen_mn + pen_type))
    return dict(total=float(total), raw=float(pos), stand=stand, step=step, coord=coord, prog=prog, pen_body=pen_body, pen_mn=pen_mn, pen_type=pen_type, fell=bool(fell))


def read_cord(prefix: str, warmup: float = 2.0, legmn_types=None) -> dict:
    """the prefilter's reads from world/cord.py's <prefix>.cells.npz (frames at 10 ms, cord_hz = every spike in the cord per frame)."""
    C = np.load(prefix + ".cells.npz", allow_pickle=True); fr = C["frames"].astype(float)[int(warmup * 100):] * 100.0; ty = C["type"].astype(str)
    mn = np.isin(ty, legmn_types) if legmn_types is not None else np.char.endswith(ty, " MN") | np.char.startswith(ty, "MN")
    hz = fr.mean(0); n_cells = int(np.load("brain_cord.npz", allow_pickle=True)["type"].shape[0])
    types = {t: float(hz[ty == t].mean()) for t in sorted(set(ty))}
    return dict(mn_mean_hz=float(hz[mn].mean()), cord_hz=float(C["cord_hz"][int(warmup * 100):].mean() * 100.0 / n_cells), type_hz=types,
                types_over=sorted(t for t, v in types.items() if v > TYPE_MAX))


def cord_verdict(R: dict, cord_runaway_hz: float) -> str:
    """'' = pass; else the reason. the brief's rule: the leg MNs' mean rate (per cell, pooled) inside MN_RANGE, and no runaway."""
    if R["mn_mean_hz"] < MN_RANGE[0]: return f"leg MN mean {R['mn_mean_hz']:.2f} Hz < {MN_RANGE[0]}"
    if R["mn_mean_hz"] > MN_RANGE[1]: return f"leg MN mean {R['mn_mean_hz']:.1f} Hz > {MN_RANGE[1]}"
    if R["cord_hz"] > cord_runaway_hz: return f"cord runaway: {R['cord_hz']:.1f} Hz/cell > {cord_runaway_hz}"
    return ""
