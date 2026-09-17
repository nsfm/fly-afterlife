"""
effectors: readout populations -> body commands, and the calibrations they rest on.

    steer = Steering(gain=3.0, rest_net=rest_net, leg_gain=leg_gain)    # his wheel + touch reflex
    pace = Pace(leg_stand=leg_stand)                                      # his speed from leg MN output
    hers = HerSteering(rng)                                               # her DNa02 wheel + noise + turn-away
    song = SongDetector()                                                 # pIP10 above running mean + 2 sd

each rule is labelled with what it assumes. this first version reproduces world/pair.py exactly
(same expressions, same rng call order) so the oracle check passes. known problems, to be fixed
as their own runs (docs/TODO.md): the pace rule is degenerate when the standing leg-MN rate is 0
(the corrected synapse constants), the DNa02 offset is a fixed subtraction where the physiology
says a running per-side baseline, and the touch reflex gain is calibrated per run rather than
cached per brain configuration.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np


@dataclass
class Steering:
    """his yaw per chunk: DNa02 right-minus-left (offset-subtracted, EMA over 3 chunks, gain, clip 12 deg,
    ipsilateral sign) when free; while any bristle is pressed, the leg-MN asymmetry alone (gain calibrated
    so the bristle-evoked asymmetry is worth REFLEX_DEG per chunk), vision dropped for the chunk."""
    gain: float
    rest_net: float
    leg_gain: float
    ema: float = 0.0
    leg_rest: float = 0.0
    source: str = "pair.py 2026-09-16; Rayshubskiy 2020 says yaw is linear in R-L with zero at zero -> running baseline next"

    def step(self, cnt: dict, touched_any: bool) -> float:
        net_ = cnt["DNa02_R"] - cnt["DNa02_L"] - self.rest_net; self.ema += (net_ - self.ema) / 3.0; yaw = float(np.clip(self.gain * self.ema, -12, 12)) * -1
        asym = (cnt["legMN_R"] - cnt["legMN_L"]) / max(cnt["legMN_R"] + cnt["legMN_L"], 1)
        if touched_any: yaw = float(np.clip(self.leg_gain * (asym - self.leg_rest), -12, 12))   # bristles pressed: the legs steer
        else: self.leg_rest += (asym - self.leg_rest) / 20.0
        return yaw


@dataclass
class RunningBaselineSteering:
    """the vision brief's rule: rotational velocity is linear in DNa02 right-minus-left through its whole range,
    zero at zero (Rayshubskiy 2020), so the resting lean is not physiology. each side is referenced to its own
    running mean (tau chunks) before differencing, instead of one fixed offset measured standing. the touch
    reflex is as in Steering. this is the FIRST running-baseline correction tried; the fixed ones (still offset,
    plateau offset, still- and motion-normalised ratios) all failed on 2026-09-16."""
    gain: float
    leg_gain: float
    tau: float = 20.0                  # chunks (2 s at 100 ms): the brief's ~2 s
    wheel: str = "DNa02"              # readout population: "DNa02" (one type, the record) or "DN" (every descending neuron)
    ema: float = 0.0
    leg_rest: float = 0.0
    base_L: float | None = None
    base_R: float | None = None
    source: str = "vision_motor_courtship brief 2026-09-16: running per-side baseline (~2 s) before differencing"

    def step(self, cnt: dict, touched_any: bool) -> float:
        L, R = float(cnt[self.wheel + "_L"]), float(cnt[self.wheel + "_R"])
        if self.base_L is None: self.base_L, self.base_R = L, R
        net_ = (R - self.base_R) - (L - self.base_L); self.ema += (net_ - self.ema) / 3.0; yaw = float(np.clip(self.gain * self.ema, -12, 12)) * -1
        self.base_L += (L - self.base_L) / self.tau; self.base_R += (R - self.base_R) / self.tau   # update after use: the current chunk is compared to the past
        asym = (cnt["legMN_R"] - cnt["legMN_L"]) / max(cnt["legMN_R"] + cnt["legMN_L"], 1)
        if touched_any: yaw = float(np.clip(self.leg_gain * (asym - self.leg_rest), -12, 12))
        else: self.leg_rest += (asym - self.leg_rest) / 20.0
        return yaw


@dataclass
class Pace:
    """his speed: v = v_min + v_range x clip((leg MN - standing) / (4 x standing), 0, 1).
    degenerate when standing = 0 (corrected constants): saturates on any output. absolute reference + MN class weights next."""
    leg_stand: float
    v_min: float = 0.05
    v_range: float = 0.45
    source: str = "pair.py 2026-09-16 18:54; Azevedo 2020: slow MNs fire ~30 Hz standing, force per spike 0.1/1/10 uN by class"

    def step(self, cnt: dict) -> float:
        drive_m = (cnt["legMN"] - self.leg_stand) / max(4 * self.leg_stand, 1); return self.v_range * float(np.clip(drive_m, 0, 1)) + self.v_min


@dataclass
class MultiWheelSteering:
    """several readout populations, each left-minus-right through its own running baseline, summed:
    yaw = -sum_i gain_i x EMA_3((R_i - base_R_i) - (L_i - base_L_i)), clipped at 12 deg per chunk; the touch reflex as in
    Steering. built 2026-09-17 from the population test: DNa02 carries vision and not warmth, the DN population carries
    warmth and barely vision, so each gets its own channel. wheels = [(population, gain), ...]."""
    wheels: list
    leg_gain: float
    tau: float = 20.0
    ema: dict = field(default_factory=dict)
    base: dict = field(default_factory=dict)
    leg_rest: float = 0.0
    source: str = "2026-09-17 10:10, the record 'the DN-population wheel on the drum'"

    def step(self, cnt: dict, touched_any: bool) -> float:
        yaw = 0.0
        for w, g in self.wheels:
            L, R = float(cnt[w + "_L"]), float(cnt[w + "_R"])
            if w not in self.base: self.base[w] = [L, R]; self.ema[w] = 0.0
            net_ = (R - self.base[w][1]) - (L - self.base[w][0]); self.ema[w] += (net_ - self.ema[w]) / 3.0; yaw += g * self.ema[w] * -1
            self.base[w][0] += (L - self.base[w][0]) / self.tau; self.base[w][1] += (R - self.base[w][1]) / self.tau
        yaw = float(np.clip(yaw, -12, 12))
        asym = (cnt["legMN_R"] - cnt["legMN_L"]) / max(cnt["legMN_R"] + cnt["legMN_L"], 1)
        if touched_any: yaw = float(np.clip(self.leg_gain * (asym - self.leg_rest), -12, 12))
        else: self.leg_rest += (asym - self.leg_rest) / 20.0
        return yaw


@dataclass
class RunningPace:
    """his speed from leg-MN output against its own running mean: v = v_min + v_range x clip(count / (k x mean), 0, 1),
    mean updated after use (tau chunks). the fixed rule referenced a standing rate the corrected brain does not have
    (0 at 0.185 mV), so it saturated; this one is the same estimator the steering now uses: the fly's recent history
    is the reference. k = 2: his mean output is half speed, twice it is full. no class weighting yet (Azevedo 2020:
    slow MNs tonic ~30 Hz, force per spike 0.1 / 1 / 10 uN by class); the readout still counts every leg MN alike."""
    k: float = 2.0
    tau: float = 20.0
    v_min: float = 0.05
    v_range: float = 0.45
    mean: float | None = None
    source: str = "2026-09-17 morning; estimator, labelled; MN class weights are the physiology item"

    def step(self, cnt: dict) -> float:
        c = float(cnt["legMN"])
        if self.mean is None: self.mean = max(c, 1.0)
        v = self.v_range * float(np.clip(c / max(self.k * self.mean, 1.0), 0, 1)) + self.v_min
        self.mean += (c - self.mean) / self.tau
        return v


@dataclass
class HerSteering:
    """her yaw per chunk: DNa02 left-minus-right x 3, clip 12, plus N(0, 1.5) heading noise; on contact, turn away
    from the touched side (labelled stand-in for the leg reflex she has no cord for). consumes the episode rng."""
    rng: np.random.Generator
    source: str = "pair.py 2026-09-16 (the room)"

    def step(self, cnt: dict, touched: list) -> float:
        fnet = cnt["DNa02_L"] - cnt["DNa02_R"]; dh = float(np.clip(3.0 * fnet, -12, 12)) + self.rng.normal(0, 1.5)
        if any(touched):
            side_ = [t_ for t_ in touched if t_][-1]; dh += -8.0 if side_ == "L" else (8.0 if side_ == "R" else self.rng.choice([-8.0, 8.0]))
        return dh


@dataclass
class SongDetector:
    """a song bout = his pIP10 count above its running mean + 2 sd (after 5 chunks)."""
    hist: list = field(default_factory=list)
    source: str = "pair.py 2026-09-16 (the song); pIP10 never follows P1 in this LIF, so this has fired ~never"

    def step(self, p: int) -> bool:
        self.hist.append(p); mu, sd = (np.mean(self.hist[:-1]), np.std(self.hist[:-1]) + 0.5) if len(self.hist) > 5 else (p, 1e9)
        return bool(p > mu + 2 * sd)


# ---- calibrations (run once per brain configuration; each is pair.py's loop, verbatim)

def dna02_rest_offset(M, RM, drive_frame, render_chunk, CH, SPF, chunks=20) -> float:
    """his DNa02 right-minus-left per chunk while standing with vision on: the fixed offset the wheel subtracts."""
    rl = rr = 0
    for c in range(chunks):
        a = render_chunk()
        for f in range(CH):
            drive_frame(a, f)
            for _ in range(SPF): spk = M.step(); rl += int(spk[RM["DNa02_L"]].sum()); rr += int(spk[RM["DNa02_R"]].sum())
    return (rr - rl) / chunks


def standing_baselines(M, F, RM, RF, drive_frame, render_chunk, CH, SPF, chunks=10) -> tuple[float, float]:
    """his leg-MN spikes per chunk and her DN spikes per chunk, standing with vision on."""
    leg_stand = 0; dn_stand_f = 0
    for c in range(chunks):
        a = render_chunk()
        for f in range(CH):
            drive_frame(a, f)
            for _ in range(SPF):
                leg_stand += int(M.step()[RM["legMN"]].sum())
                if F is not None: dn_stand_f += int(F.step()[RF["DN"]].sum())
    return leg_stand / chunks, dn_stand_f / chunks


def reflex_gain(M, RM, TACT_M, CH, SPF, reflex_deg=6.0, chunks=10, drive_hz=150.0, kernel=None, fps=100) -> tuple[float, dict]:
    """drive his left bristles, then his right, standing; the leg-MN asymmetry (R-L)/(R+L) each evokes is worth
    reflex_deg per chunk. returns (gain, asymmetry per side). leaves the bristles at 0. with `kernel` (a transducer
    such as Adapting) the bristles get the kernel's own time course for sustained contact instead of a constant,
    so the gain matches what the loop will deliver."""
    asym_side = {}
    for s_ in "LR":
        if kernel is not None: kernel.reset()
        for s2 in "LR": M.drive_hz[TACT_M[s2]] = drive_hz if s2 == s_ else 0.0
        rl = rr = 0
        for c in range(chunks):
            for f in range(CH):
                if kernel is not None: M.drive_hz[TACT_M[s_]] = kernel.step(True, (c * CH + f) / fps, 1.0 / fps)
                for _ in range(SPF): spk = M.step(); rl += int(spk[RM["legMN_L"]].sum()); rr += int(spk[RM["legMN_R"]].sum())
        asym_side[s_] = (rr - rl) / max(rr + rl, 1)
    for s2 in "LR": M.drive_hz[TACT_M[s2]] = 0.0
    return reflex_deg / max(abs(asym_side["L"] - asym_side["R"]) / 2, 1e-3), asym_side
