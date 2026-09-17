"""
receptors: the registry that turns world state into drive rates on connectome cells.

a receptor class is one row of the physiology table (docs/physiology/): which cells (selected
from the annotation table by class / type / entryNerve / rootSide / receptorType, or handed in
as indices), a transducer (the model that turns a stimulus into a rate, with its state and its
citation), and a stimulus function (what world/body variable it reads).

    reg = Registry()
    reg.add(ReceptorClass("bristle_L", cells=sel(brain, cls="mechanosensory_tactile", side="L"),
                          transducer=Hold(150.0), stimulus=lambda s: s.touched in ("L", "B"),
                          source="pair.py 09-16 (uncalibrated; see mechanosensation brief)"))
    reg.apply(brain, state, t)        # sets brain.drive_hz for every registered class

design rules (docs/ARCHITECTURE.md): a receptor is a row, not a loop; every constant carries its
source; state-dependent gates are applied at the drive because the engine's driven cells are
Poisson sources that ignore their membrane. this first version reproduces the drives in
world/pair.py exactly (same floats, same frame timing) so the oracle runs pass; per-millisecond
resolution and the physiology kernels come after, one per run.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Any
import numpy as np
import pandas as pd

ANNOT = "data/body-annotations-male-cns-v1.0-minconf-0.5.feather"
_annot_cache: dict[str, pd.DataFrame] = {}


def annotations(path: str = ANNOT) -> pd.DataFrame:
    """the MaleCNS body-annotation table, cached. columns of interest: bodyId, class, type,
    superclass, somaSide, rootSide, entryNerve, exitNerve, receptorType, somaLocation."""
    if path not in _annot_cache:
        _annot_cache[path] = pd.read_feather(path)
    return _annot_cache[path]


def select(brain, cls: str | None = None, type_prefix: str | None = None, side: str | None = None,
           entry_nerve: str | list[str] | None = None, root_side: str | None = None,
           receptor_type: str | None = None, body_ids=None, subclass: str | list[str] | None = None) -> np.ndarray:
    """indices into `brain` of the cells matching every given filter. class/type/side come
    from the brain's own arrays (fast path); entryNerve/rootSide/receptorType/subclass come from the
    annotation table by bodyId (MN subclass: fl/ml/hl = front/middle/hind leg, ad abdominal, wm wing, hm haltere, nm neck; Marin 2024). returns a sorted int64 index array."""
    m = np.ones(brain.N, bool)
    if cls is not None: m &= brain.cls.astype(str) == cls
    if type_prefix is not None: m &= np.char.startswith(brain.type.astype(str), type_prefix)
    if side is not None: m &= brain.side.astype(str) == side
    if body_ids is not None: m &= np.isin(brain.bodyId, np.asarray(body_ids))
    if entry_nerve is not None or root_side is not None or receptor_type is not None or subclass is not None:
        a = annotations(); am = np.ones(len(a), bool)
        if subclass is not None:
            subs = [subclass] if isinstance(subclass, str) else list(subclass); am &= a["subclass"].astype(str).isin(subs).to_numpy()
        if entry_nerve is not None:
            nerves = [entry_nerve] if isinstance(entry_nerve, str) else list(entry_nerve)
            am &= a["entryNerve"].astype(str).isin(nerves).to_numpy()
        if root_side is not None: am &= (a["rootSide"].astype(str) == root_side).to_numpy()
        if receptor_type is not None: am &= (a["receptorType"].astype(str) == receptor_type).to_numpy()
        m &= np.isin(brain.bodyId, a.loc[am, "bodyId"].to_numpy())
    return np.flatnonzero(m).astype(np.int64)


# ---- transducers: stimulus -> rate (Hz), with state. step() is called once per frame.

class Transducer:
    source: str = ""
    def reset(self) -> None: ...
    def step(self, stim: Any, t: float, dt: float) -> float | np.ndarray:
        raise NotImplementedError


@dataclass
class Hold(Transducer):
    """a fixed rate while the stimulus is true, else 0. the pre-physiology bristle rule."""
    hz: float
    source: str = "pair.py 2026-09-16: 150 Hz while touched (uncalibrated; mechanosensation brief says onset burst + plateau)"
    def step(self, stim, t, dt): return self.hz if stim else 0.0


@dataclass
class Scaled(Transducer):
    """rate = gain x clip(stim, 0, 1). used for flyvis T4/T5 (stim = rest-subtracted activity)."""
    gain: float
    source: str = "seam v2: rate = GAIN x clip((act - rest) / A_REF, 0, 1); 150 Hz is Shiu's Poisson default, not a measurement"
    def step(self, stim, t, dt): return self.gain * np.clip(np.asarray(stim, np.float32), 0, 1)


@dataclass
class Adapting(Transducer):
    """slowly-adapting afferent: at stimulus onset the rate jumps to `onset_hz` and decays with `tau_ms` to
    `plateau_hz` while the stimulus holds; 0 when it does not. stim is a bool. the bristle brief (Corfas & Dudai
    1990): ~200 Hz onset, tau ~30 ms, 10-25 Hz plateau, plus seconds-scale fatigue (not modelled yet) and
    direction gating (about half a contact patch fires; approximated by `fraction` on the rate)."""
    onset_hz: float = 200.0
    tau_ms: float = 30.0
    plateau_hz: float = 20.0
    fraction: float = 0.5
    retrigger_hz: float = 10.0            # while the stimulus holds, a new onset burst every 1/retrigger_hz s: each step re-deflects the bristles (0 = single burst)
    source: str = "mechanosensation brief 2026-09-16: Corfas & Dudai 1990 (J Neurosci 10:491); direction gating as a rate fraction; step-locked re-deflection is a labelled choice (2026-09-17)"
    _prev: bool = field(default=False, init=False)
    _t_on: float = field(default=-1e9, init=False)
    def reset(self): self._prev = False; self._t_on = -1e9
    def step(self, stim, t, dt):
        stim = bool(stim)
        if stim and not self._prev: self._t_on = t
        elif stim and self.retrigger_hz > 0 and (t - self._t_on) >= 1.0 / self.retrigger_hz - 1e-9: self._t_on = t
        self._prev = stim
        if not stim: return 0.0
        age_ms = (t - self._t_on) * 1000.0
        return self.fraction * (self.plateau_hz + (self.onset_hz - self.plateau_hz) * float(np.exp(-age_ms / self.tau_ms)))


@dataclass
class TapBurst(Transducer):
    """a burst at each stimulus onset, decaying exponentially: hz x exp(-(t - t_on) / tau),
    zero after 3 tau. stim is a bool (in contact); onset = rising edge."""
    hz: float = 60.0
    tau_ms: float = 300.0
    source: str = "chemo brief: contact GRN ceiling ~60 Hz (Weiss 2011), a single tap is a complete trigger (Kohatsu 2011)"
    _prev: bool = field(default=False, init=False)
    _t_on: float = field(default=-1e9, init=False)
    def reset(self): self._prev = False; self._t_on = -1e9
    def step(self, stim, t, dt):
        stim = bool(stim)
        if stim and not self._prev: self._t_on = t
        self._prev = stim
        age_ms = (t - self._t_on) * 1000.0
        return self.hz * float(np.exp(-age_ms / self.tau_ms)) if age_ms < 3 * self.tau_ms else 0.0


@dataclass
class GaitLeg(Transducer):
    """one leg's proprioceptors under a tripod gait: rate = peak x (tonic + (1 - tonic) x pace x
    max(0, sin(2 pi (f_step t - phase)))). stim = pace in [0, 1]. the campaniform brief says
    the load signal should be dF/dt bursts at stance onset, not this tonic term: next version."""
    peak: float
    phase: float
    step_hz: float = 10.0
    tonic: float = 0.15
    phasic: float = 0.85                    # literal, not 1 - tonic: keeps the port bit-identical to pair.py
    source: str = "pair.py 2026-09-16 --proprio: tripod at 10 Hz (Wosnitza 2013 says up to 16), 15% tonic load (wrong shape per Zill 2024)"
    def step(self, stim, t, dt):
        """stim = pace in [0, 1], or (pace, t_eval) to evaluate the cycle at another time
        (pair.py evaluates the gait at the chunk's end time for every frame in it; kept as is
        for the oracle, to be fixed as its own change)."""
        pace, tt = (stim if isinstance(stim, tuple) else (stim, t))
        return self.peak * (self.tonic + self.phasic * float(pace) * max(0.0, np.sin(2 * np.pi * (self.step_hz * tt - self.phase))))


@dataclass
class HotCells(Transducer):
    """arista hot cells (Gr28b.d, VP2): tonic, absolute temperature, exponential: 17 / 37 / 74 Hz at 20 / 25 / 30 C,
    Q10 ~4.4 (Budelli 2019, Neuron). rate = r25 x Q10^((T - 25) / 10). stim = T in C. the phasic on-warming component
    (~1 s) is not modelled yet."""
    r25: float = 37.0
    q10: float = 4.4
    source: str = "chemo brief 2026-09-16 s.4: Budelli et al. 2019 (Neuron); Gallio 2011; Ni 2013"
    def step(self, stim, t, dt): return self.r25 * float(self.q10 ** ((float(stim) - 25.0) / 10.0))


@dataclass
class CoolingCells(Transducer):
    """arista cooling cells (Ir21a/Ir25a/Ir93a, VP3): purely phasic. rest ~95 Hz regardless of temperature; >50%
    above rest for a 0.1 C drop, ~3x for 0.2 C, peaking ~0.65 s after cooling onset and adapting back while the
    cooling continues; suppressed by warming (Budelli 2019). model: c = -dT/dt (C/s, + = cooling) low-passed with
    tau_rise, minus an adapting copy with tau_adapt; rate = rest x max(0, 1 + gain x (c_f - a)). gain 5 per C/s puts a
    0.2 C drop over half a second at ~3x. stim = T in C; the transducer differentiates."""
    rest_hz: float = 95.0
    gain: float = 5.0
    tau_rise_s: float = 0.3
    tau_adapt_s: float = 2.0
    source: str = "chemo brief 2026-09-16 s.4: Budelli et al. 2019 (Neuron), rates and time course; gain inferred from the 0.2 C / 3x figure"
    _T: float | None = field(default=None, init=False)
    _c: float = field(default=0.0, init=False)
    _a: float = field(default=0.0, init=False)
    def reset(self): self._T = None; self._c = 0.0; self._a = 0.0
    def step(self, stim, t, dt):
        T = float(stim)
        if self._T is None: self._T = T
        cool = -(T - self._T) / dt; self._T = T                       # C/s, positive when cooling
        self._c += (cool - self._c) * dt / self.tau_rise_s
        self._a += (self._c - self._a) * dt / self.tau_adapt_s
        return self.rest_hz * max(0.0, 1.0 + self.gain * (self._c - self._a))


@dataclass
class Gate(Transducer):
    """multiply another transducer's rate by a state-dependent factor (e.g. 0 while a
    descending walk command is on, for hook FeCO axons: Dallmann 2025). stim = (inner_stim, gate_on)."""
    inner: Transducer
    factor_when_on: float
    source: str = ""
    def reset(self): self.inner.reset()
    def step(self, stim, t, dt):
        inner_stim, on = stim
        r = self.inner.step(inner_stim, t, dt)
        return r * (self.factor_when_on if on else 1.0)


# ---- the registry

@dataclass
class ReceptorClass:
    name: str
    cells: np.ndarray                       # indices into the brain
    transducer: Transducer
    stimulus: Callable[[Any], Any]           # state -> stim for the transducer
    source: str = ""                         # where the rule and its constants come from
    enabled: bool = True


class Registry:
    def __init__(self): self.classes: list[ReceptorClass] = []
    def add(self, rc: ReceptorClass) -> ReceptorClass:
        self.classes.append(rc); return rc
    def reset(self):
        for rc in self.classes: rc.transducer.reset()
    def apply(self, brain, state, t: float, dt: float) -> None:
        """set brain.drive_hz for every enabled class from the current state. classes are
        applied in registration order; a later class overwrites an earlier one on shared cells."""
        for rc in self.classes:
            if not rc.enabled or rc.cells.size == 0: continue
            brain.drive_hz[rc.cells] = rc.transducer.step(rc.stimulus(state), t, dt)
    def table(self) -> str:
        """one line per class: name, cell count, transducer, source. for the record."""
        return "\n".join(f"{rc.name:24s} {rc.cells.size:6d} cells  {type(rc.transducer).__name__:10s} {rc.transducer.source or rc.source}" for rc in self.classes)
