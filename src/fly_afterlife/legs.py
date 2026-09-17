"""
legs: from leg motor neuron spikes to a body command, with muscles.

the model of docs/physiology/leg_motor.md s.6, built 2026-09-17 after the motor audit showed that a
left-minus-right count over all motor neurons has a different sign for every input:

    per MN i (leg MNs only: subclass fl / ml / hl), side s, segment g:
        delta_i  = count_i - running baseline_i                      (quiet standing is not zero)
        f_i      = force per spike from class (10 / 1 / 0.1 uN) or from size: (S_i / S_ref) ** alpha
        a_i      = f_i * (1 - exp(-delta_i / k))                       (muscle tension summates sublinearly)
        P_{s,g}  = sum_i w_i * a_i                                     (w: signed muscle weight, stance drive +)
    forward      = c_f * sum_{s,g} lambda_g * P_{s,g}
    yaw_left     = c_y * sum_g lambda_g * mu_g * (P_{R,g} - P_{L,g})   (turn toward the side with LESS stance drive;
                                                                         Yang 2024; front legs brake: mu_T1 < 0)

every constant carries its source; the ones marked (E) are the brief's estimates. this is a labelled
effector, not a circuit we found: what it adds is that the sign of a motor pattern comes from which
muscles fire, not from which side has more spikes.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np

# signed muscle weights by type-name substring (brief s.6 step 3; stance drive positive). first match wins.
MUSCLE_W = [
    ("Pleural remotor", 1.0), ("Sternal posterior rotator", 1.0),          # ThC retraction: the propulsive stroke
    ("Sternotrochanter", 0.8), ("Tr extensor", 0.8),                       # CTr depression: support + push
    ("Ta depressor", 0.4), ("Ta levator", 0.4), ("ltm", 0.4),               # grip
    ("Acc. ti flexor", 0.5), ("Ti flexor", 0.5),                           # loads the leg in stance (also the withdrawal muscle)
    ("Ti extensor", 0.2),                                                  # late stance / swing
    ("Sternal anterior rotator", -0.6), ("promotor", -0.6),                # protraction = swing
    ("Acc. tr flexor", -0.6), ("Tr flexor", -0.6),                         # levation = leg off the ground
    ("Fe reductor", 0.0), ("Sternal adductor", 0.0), ("Tergotr", 0.0),     # postural / rotational / jump
]
LAMBDA = {"fl": 0.3, "ml": 1.0, "hl": 1.0}          # segment weight on thrust (E)
MU = {"fl": -0.5, "ml": 1.0, "hl": 1.0}             # segment sign on yaw: front legs brake (Isakov 2016; E, medium confidence)


def muscle_weight(type_name: str) -> float:
    for key, w in MUSCLE_W:
        if key in type_name: return w
    return 0.0                                       # unnamed MNml## / MNhl## types: no muscle known, no weight


@dataclass
class LegModel:
    """the effector. built from a brain: leg MN indices, their segment, side, muscle weight and force."""
    brain: object
    legmn_path: str = "world/legmn.npz"
    alpha: float = 2.5          # force ~ size^alpha, chosen so fast:slow ~ 100 over the size span (E)
    k: float = 5.0              # saturation, spikes per 100 ms bin (E, ~50 Hz)
    tau: float = 20.0           # running baseline, chunks
    c_y: float = 1.0            # deg per chunk per unit asymmetry, calibrated by `calibrate_yaw`
    c_f: float = 1.0
    clip_deg: float = 12.0
    source: str = "docs/physiology/leg_motor.md s.6 (Azevedo 2020; Lesser 2024; Yang 2024; Isakov 2016)"
    base: np.ndarray | None = field(default=None, init=False)

    def __post_init__(self):
        B = self.brain; lm = np.load(self.legmn_path); ty = B.type.astype(str)
        self.cells = lm["leg"]; n = len(self.cells)
        self.side = np.array(["L" if i in set(lm["leg_L"].tolist()) else "R" for i in self.cells])
        segof = {}
        for seg in ("fl", "ml", "hl"):
            for i in np.concatenate([lm[f"{seg}_L"], lm[f"{seg}_R"]]): segof[int(i)] = seg
        self.seg = np.array([segof[int(i)] for i in self.cells])
        self.w = np.array([muscle_weight(ty[i]) for i in self.cells], np.float64)
        insyn = np.bincount(B._out_tgt, weights=np.abs(B._out_w), minlength=B.N) / B.p.mv_per_synapse
        S = insyn[self.cells]; S_ref = np.median(S[S > 0]) if (S > 0).any() else 1.0
        self.f = np.clip(S / S_ref, 0.2, 5.0) ** self.alpha               # relative force per spike by size, span clipped to the brief's 3-5x (the raw synapse counts span 0-19k, a tracing confound; no class labels in the table)
        self.lam = np.array([LAMBDA[s] for s in self.seg]); self.mu = np.array([MU[s] for s in self.seg])
        self.n_weighted = int((self.w != 0).sum())

    def drive(self, counts_all: np.ndarray) -> tuple[float, float, dict]:
        """counts_all: per-cell spike counts for the chunk (length brain.N). returns (forward, yaw_left, P by side/segment)."""
        c = counts_all[self.cells].astype(np.float64)
        if self.base is None: self.base = c.copy()
        delta = np.maximum(c - self.base, 0.0); self.base += (c - self.base) / self.tau
        a = self.f * (1.0 - np.exp(-delta / self.k)) * self.w
        P = {}
        for s in "LR":
            for g in ("fl", "ml", "hl"): P[(s, g)] = float(a[(self.side == s) & (self.seg == g)].sum())
        forward = self.c_f * sum(LAMBDA[g] * (P[("L", g)] + P[("R", g)]) for g in ("fl", "ml", "hl"))
        yaw_left = self.c_y * sum(LAMBDA[g] * MU[g] * (P[("R", g)] - P[("L", g)]) for g in ("fl", "ml", "hl"))
        return forward, yaw_left, P

    def pattern_yaw(self, counts_a: np.ndarray, counts_b: np.ndarray) -> float:
        """open-loop: the yaw the model assigns to pattern a relative to baseline pattern b (no running state)."""
        delta = np.maximum(counts_a[self.cells] - counts_b[self.cells], 0.0); a = self.f * (1.0 - np.exp(-delta / self.k)) * self.w
        P = {(s, g): float(a[(self.side == s) & (self.seg == g)].sum()) for s in "LR" for g in ("fl", "ml", "hl")}
        return self.c_y * sum(LAMBDA[g] * MU[g] * (P[("R", g)] - P[("L", g)]) for g in ("fl", "ml", "hl"))


@dataclass
class LegSteering:
    """steering effector that adds the leg model's yaw to a brain-side wheel (DNa02, running baseline), because in this
    LIF the DNa02 command does not reach the legs (09-17 12:30). the touch reflex is kept as a separate labelled reflex
    (withdrawal is not walking; Medeiros 2024) and overrides while bristles are pressed."""
    legs: LegModel
    wheel_gain: float
    leg_gain: float
    tau: float = 20.0
    ema: float = 0.0
    base_L: float | None = None
    base_R: float | None = None
    leg_rest: float = 0.0
    last: dict = field(default_factory=dict)
    needs_cells: bool = True

    def step(self, cnt: dict, touched_any: bool, cells: np.ndarray | None = None) -> float:
        L, R = float(cnt["DNa02_L"]), float(cnt["DNa02_R"])
        if self.base_L is None: self.base_L, self.base_R = L, R
        net_ = (R - self.base_R) - (L - self.base_L); self.ema += (net_ - self.ema) / 3.0; yaw = self.wheel_gain * self.ema * -1
        self.base_L += (L - self.base_L) / self.tau; self.base_R += (R - self.base_R) / self.tau
        fwd, yl, P = self.legs.drive(cells) if cells is not None else (0.0, 0.0, {})
        yaw += yl; self.last = dict(forward=fwd, yaw_legs=yl, yaw_wheel=self.wheel_gain * self.ema * -1)
        yaw = float(np.clip(yaw, -12, 12))
        asym = (cnt["legMN_R"] - cnt["legMN_L"]) / max(cnt["legMN_R"] + cnt["legMN_L"], 1)
        if touched_any: yaw = float(np.clip(self.leg_gain * (asym - self.leg_rest), -12, 12))
        else: self.leg_rest += (asym - self.leg_rest) / 20.0
        return yaw
