"""
fastlif: the same LIF step as ref/flybrain/scripts/flysim.py, compiled with numba.

    from fastlif import FastFlyBrain      # drop-in for FlyBrain
    M = FastFlyBrain("brain_whole.npz", seed=0); spk = M.step()

what is compiled: the synaptic propagation (walk the out-edges of every neuron that fired and
accumulate into a buffer; the numpy path did a ragged gather + np.add.at) and the membrane update
(decay, integrate, refractory, floor, threshold) as one fused pass over N neurons. everything
small stays numpy: the delay line, APL, driven-receptor Poisson draws, short-term depression,
plasticity. the arithmetic is written in the same order and precision (float32 state, float32
constants) as flysim.step, so the two engines agree spike-for-spike from the same seed; run
`python world/fastlif.py` to check that on a brain.
"""
import sys, time
import numpy as np
from numba import njit, prange
import numba; numba.set_num_threads(min(8, numba.config.NUMBA_NUM_THREADS))   # 8 beat 16 on this 16-core box (memory-bound kernels)
sys.path.insert(0, "ref/flybrain/scripts")
from flysim import FlyBrain, Params  # noqa: E402


@njit(cache=True, fastmath=False, nogil=True)
def _propagate(src, scale, has_scale, out_ptr, out_tgt, out_w, acc):
    acc[:] = 0.0
    for k in range(src.shape[0]):
        s = src[k]; sc = scale[k] if has_scale else np.float32(1.0)
        for e in range(out_ptr[s], out_ptr[s + 1]):
            acc[out_tgt[e]] += out_w[e] * sc
    return acc


@njit(cache=True, fastmath=False, nogil=True)
def _propagate_into(src, scale, has_scale, out_ptr, out_tgt, out_w, acc, g):
    """same sum as _propagate, then g += acc (kept as a separate pass so the float32 summation order matches flysim: acc first, then one add into g)."""
    acc[:] = 0.0
    for k in range(src.shape[0]):
        s = src[k]; sc = scale[k] if has_scale else np.float32(1.0)
        for e in range(out_ptr[s], out_ptr[s + 1]):
            acc[out_tgt[e]] += out_w[e] * sc
    for i in range(g.shape[0]):
        g[i] += acc[i]


@njit(cache=True, fastmath=False, nogil=True)
def _reset(idx, v, refrac, v_reset, refractory):
    for k in range(idx.shape[0]):
        v[idx[k]] = v_reset; refrac[idx[k]] = refractory


@njit(cache=True, fastmath=False, parallel=True, nogil=True)
def _membrane(v, g, refrac, ext, noise, v_th, free, dt, tau_syn, tau_m, v_floor, spk):
    """g decay -> syn; dv; refractory gate; floor; threshold. `free` (refrac <= 0 before the update) is written out for the receptor gate."""
    n = v.shape[0]
    for i in prange(n):
        g[i] -= g[i] * (dt / tau_syn)
        if g[i] < 1e-20 and g[i] > -1e-20: g[i] = 0.0   # flush decayed conductances before they go subnormal (09-19: a quiet brain stepped 1.8x slower after 20 s; no float32 voltage can see 1e-20)
        syn = g[i] * (dt / tau_m)
        dv = (-v[i] / tau_m) * dt + syn + ext[i] * (dt / tau_m) + noise[i]
        if refrac[i] <= 0.0:
            free[i] = True
            v[i] += dv
            if v[i] < -v_floor: v[i] = -v_floor
            spk[i] = v[i] >= v_th[i]
        else:
            free[i] = False
            refrac[i] -= dt
            if v[i] < -v_floor: v[i] = -v_floor
            spk[i] = False


@njit(cache=True, fastmath=False, parallel=True, nogil=True)
def _membrane_exact(v, g, refrac, ext, noise, v_th, free, e_m, e_s, k_g, one_m_em, dt, v_floor, spk, freeze_g):
    """the exact step of the linear system dv/dt = (-v + g + ext) / tau_m, dg/dt = -g / tau_syn over dt (Shiu 2024's
    Brian2 method='linear'; 09-19): v <- v e_m + ext (1 - e_m) + g A (e_s - e_m) with A = tau_syn / (tau_syn - tau_m),
    then g <- g e_s. forward Euler at dt = 1 ms puts the synaptic potential's peak 16 % low (docs/MINECRAFT_OPEN.md)."""
    n = v.shape[0]
    for i in prange(n):
        gi = g[i]
        if gi < 1e-20 and gi > -1e-20: gi = 0.0
        if refrac[i] <= 0.0:
            free[i] = True
            v[i] = v[i] * e_m + ext[i] * one_m_em + gi * k_g + noise[i]
            if v[i] < -v_floor: v[i] = -v_floor
            spk[i] = v[i] >= v_th[i]
        else:
            free[i] = False
            refrac[i] -= dt
            if v[i] < -v_floor: v[i] = -v_floor
            spk[i] = False
            if freeze_g:   # Shiu 2024's "(unless refractory)" on dg/dt: the synaptic conductance does not decay while the cell is refractory (opt-in, 09-21; False = the record, bit for bit)
                g[i] = gi; continue
        g[i] = gi * e_s


# ---- per-transmitter synaptic decay (09-22, campaign item 2; off by default, and when off none of this runs: the kernels above are the record) ----
# the file's one tau_syn (Shiu 2024's 5 ms) is an ACh number put on every synapse; GABA and glutamate (inhibitory at the fly's central
# synapses, GluCl) decay slower. the class is the PRESYNAPTIC cell's transmitter, so the propagation picks the class's conductance row once
# per spiking source and walks its out-edges as before (no per-synapse cost, and later edits to _out_w, size gain, edge scale, the mirror,
# still apply); the membrane sums the rows. class 0 is everything else (histamine, the modulators, 'unclear') at the engine's tau_syn.
NT_CLASS = {"acetylcholine": 1, "gaba": 2, "glutamate": 3}
SYN_TAU_HELP = ("per-transmitter synaptic decay, ACH:GABA:GLU in ms (e.g. 5:20:20), by the presynaptic cell's nt: acetylcholine, gaba, "
                "glutamate each decay with their own tau; every other cell (histamine, the modulators, unclear) keeps the engine's tau_syn "
                "(5 ms). a labelled engine term (campaign item 2), off by default ('' or off = the record, bit for bit)")


@njit(cache=True, fastmath=False, nogil=True)
def _propagate_into_nt(src, scale, has_scale, out_ptr, out_tgt, out_w, pre_cls, gc):
    """the arrivals straight into their class's conductance row gc[pre_cls[s]] (the on path only; no shared accumulator, so the float32
    order within a step is g + a + b rather than flysim's g + (a + b): same up to rounding, never compared bit for bit)."""
    for k in range(src.shape[0]):
        s = src[k]; sc = scale[k] if has_scale else np.float32(1.0); c = pre_cls[s]
        for e in range(out_ptr[s], out_ptr[s + 1]):
            gc[c, out_tgt[e]] += out_w[e] * sc


@njit(cache=True, fastmath=False, parallel=True, nogil=True)
def _membrane_nt(v, gc, kdec, refrac, ext, noise, v_th, free, dt, tau_m, v_floor, spk):
    """_membrane with one decaying g per transmitter class: each row decays by its own dt / tau, the rows sum into syn. with one class
    live on a cell the sum is 0 + g (exact) and the step is _membrane's, bit for bit (experiments/syn_tau_test.py checks it)."""
    n = v.shape[0]
    for i in prange(n):
        gs = np.float32(0.0)
        for c in range(gc.shape[0]):
            gc[c, i] -= gc[c, i] * kdec[c]
            if gc[c, i] < 1e-20 and gc[c, i] > -1e-20: gc[c, i] = 0.0
            gs += gc[c, i]
        syn = gs * (dt / tau_m)
        dv = (-v[i] / tau_m) * dt + syn + ext[i] * (dt / tau_m) + noise[i]
        if refrac[i] <= 0.0:
            free[i] = True
            v[i] += dv
            if v[i] < -v_floor: v[i] = -v_floor
            spk[i] = v[i] >= v_th[i]
        else:
            free[i] = False
            refrac[i] -= dt
            if v[i] < -v_floor: v[i] = -v_floor
            spk[i] = False


@njit(cache=True, fastmath=False, parallel=True, nogil=True)
def _membrane_exact_nt(v, gc, e_s, k_g, refrac, ext, noise, v_th, free, e_m, one_m_em, dt, v_floor, spk, freeze_g):
    """_membrane_exact with one g per class: the linear system is a sum, so each row contributes g_c k_g,c to v and decays by its own e_s,c."""
    n = v.shape[0]
    for i in prange(n):
        gk = np.float32(0.0)
        for c in range(gc.shape[0]):
            gi = gc[c, i]
            if gi < 1e-20 and gi > -1e-20: gi = 0.0
            gc[c, i] = gi; gk += gi * k_g[c]
        if refrac[i] <= 0.0:
            free[i] = True
            v[i] = v[i] * e_m + ext[i] * one_m_em + gk + noise[i]
            if v[i] < -v_floor: v[i] = -v_floor
            spk[i] = v[i] >= v_th[i]
        else:
            free[i] = False
            refrac[i] -= dt
            if v[i] < -v_floor: v[i] = -v_floor
            spk[i] = False
            if freeze_g: continue
        for c in range(gc.shape[0]):
            gc[c, i] = gc[c, i] * e_s[c]


def exact_kg(tau_s, tau_m, dt):
    """(e_s, k_g) of the exact step for one synaptic tau, in float64 as step() computes them. k_g = A (e_s - e_m), A = tau_s / (tau_s - tau_m),
    is 0/0 at tau_s = tau_m (GABA at 20 ms against the 20 ms membrane); its limit there is (dt / tau_m) e_m, the alpha function t/tau e^(-t/tau)."""
    e_m = np.exp(-dt / tau_m); e_s = np.exp(-dt / tau_s)
    if abs(tau_s - tau_m) < 1e-6 * tau_m: return e_s, (dt / tau_m) * e_m
    return e_s, (tau_s / (tau_s - tau_m)) * (e_s - e_m)


# ---- reversal potentials per transmitter class (09-22, campaign item 2b; off by default, and when off none of this runs) ----
# the engine is current-based: a synapse adds g to dv whatever the membrane is doing, so fourteen-to-one inhibition holds a cell on the floor
# and no threshold reaches it (docs/SEAM.md "campaign item 3"). in the fly GABA-A (Rdl) and GluCl are Cl- channels that reverse near rest
# (Rohrbough & Broadie 2002, larval MNs; knobs.md 1): a shunt, not a current. this term puts each class's row on a conductance to its own
# reversal E_c (mV re rest, the engine's convention: rest 0, threshold 7): dv gets g_c kap_c (E_c - v) in place of g_c, kap_c = sign_c / E_ach.
# the scale: one ACh synapse at rest drives E_ach / E_ach = today's current, so the EPSP at rest is today's (to first order in the PSP / E_ach),
# and the conductance per synapse is mv_per_synapse / E_ach of the leak's (0.185 / 70 = 0.0026 at 70:-5:-5). a GABA or glutamate synapse at
# rest then drives |E_c| / E_ach of today's (5 / 70: the IPSP is 14x smaller than the 0.185 mV-scale pull of the record), grows as the cell
# depolarises, and reverses below E_c. v in the driving force is the step's start (frozen over dt), and the summed synaptic conductance x
# (in units of the step) enters as phi(x) = (1 - e^-x) / x, the exact relaxation of v toward the reversals over the step, so a big
# conductance lands on E_c instead of overshooting it (phi -> 1 as x -> 0: far reversals reduce to the current step, experiments/syn_rev_test.py).
# class 0 (histamine, the modulators, unclear) stays a current. the rows are the per-class ones of item 2 (_gc); the term implies them.
SYN_REV_HELP = ("reversal potentials per transmitter class, ACH:GABA:GLU in mV relative to rest (e.g. 70:-5:-5: ACh reverses 70 mV above rest, "
                "GABA and glutamate 5 below, Cl- near rest as knobs.md 1 has it; GABA or GLU may be 'off' to stay a current). a synapse of a class "
                "with a reversal drives the membrane toward it: dv += g (E - v) / E_ACH in place of dv += g, so the conductance per synapse is "
                "mv_per_synapse / E_ACH of the leak's and ONE ACh SYNAPSE AT REST GIVES TODAY'S PSP; an inhibitory synapse at rest gives today's "
                "PSP x |E_GABA| / E_ACH (5 / 70: 14x SMALLER than the record's inhibition at rest), growing as the cell depolarises (x2 at "
                "+5 mV) and reversing below E: inhibition becomes a shunt that cannot hold a cell below its reversal. the other cells (histamine, "
                "modulators, unclear) stay currents. implies the per-class rows (--syn-tau; at the engine's 5 ms if not given). a labelled "
                "engine term (campaign item 2b), off by default ('' or off = the record, bit for bit)")


@njit(cache=True, fastmath=False, nogil=True)
def _phi(x):
    """(1 - e^-x) / x, the fraction of the frozen-force step a conductance x (in units of the step) delivers; the series near 0."""
    if x < 1e-3 and x > -1e-3: return np.float32(1.0) - x * np.float32(0.5) + x * x / np.float32(6.0)
    return np.float32((1.0 - np.exp(-x)) / x)


@njit(cache=True, fastmath=False, parallel=True, nogil=True)
def _membrane_nt_rev(v, gc, kdec, has_rev, e_rev, kap, refrac, ext, noise, v_th, free, dt, tau_m, v_floor, spk):
    """_membrane_nt with the rows of has_rev[c] on a conductance to e_rev[c]: syn = (sum of current rows) dt/tau_m + sum_c g_c kap_c (E_c - v) dt/tau_m phi."""
    n = v.shape[0]; k = dt / tau_m
    for i in prange(n):
        vi = v[i]; gs = np.float32(0.0); gr = np.float32(0.0); x = np.float32(0.0)
        for c in range(gc.shape[0]):
            gc[c, i] -= gc[c, i] * kdec[c]
            if gc[c, i] < 1e-20 and gc[c, i] > -1e-20: gc[c, i] = 0.0
            if has_rev[c]:
                gg = gc[c, i] * kap[c]; gr += gg * (e_rev[c] - vi); x += gg
            else: gs += gc[c, i]
        syn = gs * k + gr * k * _phi(x * k)
        dv = (-vi / tau_m) * dt + syn + ext[i] * k + noise[i]
        if refrac[i] <= 0.0:
            free[i] = True
            v[i] += dv
            if v[i] < -v_floor: v[i] = -v_floor
            spk[i] = v[i] >= v_th[i]
        else:
            free[i] = False
            refrac[i] -= dt
            if v[i] < -v_floor: v[i] = -v_floor
            spk[i] = False


@njit(cache=True, fastmath=False, parallel=True, nogil=True)
def _membrane_exact_nt_rev(v, gc, e_s, k_g, has_rev, e_rev, kap, refrac, ext, noise, v_th, free, e_m, one_m_em, dt, v_floor, spk, freeze_g):
    """_membrane_exact_nt with the rows of has_rev[c] on a conductance to e_rev[c]: a row contributes g_c k_g,c kap_c (E_c - v) phi in place of g_c k_g,c."""
    n = v.shape[0]
    for i in prange(n):
        vi = v[i]; gk = np.float32(0.0); gr = np.float32(0.0); x = np.float32(0.0)
        for c in range(gc.shape[0]):
            gi = gc[c, i]
            if gi < 1e-20 and gi > -1e-20: gi = 0.0
            gc[c, i] = gi
            if has_rev[c]:
                gg = gi * k_g[c] * kap[c]; gr += gg * (e_rev[c] - vi); x += gg
            else: gk += gi * k_g[c]
        if refrac[i] <= 0.0:
            free[i] = True
            v[i] = vi * e_m + ext[i] * one_m_em + gk + gr * _phi(x) + noise[i]
            if v[i] < -v_floor: v[i] = -v_floor
            spk[i] = v[i] >= v_th[i]
        else:
            free[i] = False
            refrac[i] -= dt
            if v[i] < -v_floor: v[i] = -v_floor
            spk[i] = False
            if freeze_g: continue
        for c in range(gc.shape[0]):
            gc[c, i] = gc[c, i] * e_s[c]


@njit(cache=True, nogil=True)
def _count_live(di, drive_hz):
    c = 0
    for k in range(di.shape[0]):
        if drive_hz[di[k]] > 0.0: c += 1
    return c


@njit(cache=True, nogil=True)
def _drive_gate(di, drive_hz, r, free, spk, dt32):
    """the numpy block it replaces: for each driven cell with a positive rate, spk = (uniform < hz * dt / 1000) & free,
    the uniforms drawn by the Generator in driven order; cells at rate 0 are silenced. arithmetic kept in float32 as
    numpy did it (hz float32 times a weak python float, then divided by 1000 in float32) so the comparison is identical."""
    j = 0; k1000 = np.float32(1000.0)
    for k in range(di.shape[0]):
        i = di[k]; hz = drive_hz[i]
        if hz > 0.0:
            thr = (hz * dt32) / k1000
            spk[i] = (r[j] < thr) and free[i]
            j += 1
        else:
            spk[i] = False


class FastFlyBrain(FlyBrain):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self._free_buf = np.zeros(self.N, np.bool_); self._spk_buf = np.zeros(self.N, np.bool_)
        self._zero_noise = np.zeros(self.N, np.float32)
        self._empty_f64 = np.zeros(0, np.float64)
        self.integrate = "euler"   # "exact": the linear system stepped exactly (Shiu 2024, Brian2 method=linear); "euler": the reference engine (flysim), the record

    def set_syn_tau(self, spec):
        """per-transmitter synaptic decay (09-22, campaign item 2): spec 'ACH:GABA:GLU' in ms (SYN_TAU_HELP), or None / '' / 'off' to leave it off.
        the one parser for world/cord.py and experiments/body_loop.py. returns a line for the log."""
        if spec is None or str(spec).strip() in ("", "off"): self.syn_tau_on = False; return "per-transmitter synaptic decay: off"
        if self.engine == "dense": raise ValueError("--syn-tau runs on the event engine only")
        taus = [float(x) for x in str(spec).split(":")]
        if len(taus) != 3 or min(taus) <= 0: raise ValueError(f"--syn-tau wants ACH:GABA:GLU, three positive ms; got {spec!r}")
        self._pre_cls = np.array([NT_CLASS.get(str(x).lower(), 0) for x in self.nt], np.int64)
        self._syn_taus = np.array([self.p.tau_syn] + taus, np.float64)   # class 0 (other) keeps the engine's tau_syn
        self._gc = np.zeros((4, self.N), np.float32); self._gc[0] = self.g   # whatever conductance is live now carries on at the default decay
        self.g = np.zeros(self.N, np.float32); self.syn_tau_on = True   # self.g stays zero while on; the conductance lives in _gc (class x cell)
        n = np.bincount(self._pre_cls, minlength=4)
        return (f"per-transmitter synaptic decay: ACh {taus[0]:g} ms ({n[1]} cells), GABA {taus[1]:g} ms ({n[2]}), glutamate {taus[2]:g} ms ({n[3]}), "
                f"other {self.p.tau_syn:g} ms ({n[0]}); signs as the file has them")

    def set_syn_rev(self, spec):
        """reversal potentials per transmitter class (09-22, campaign item 2b): spec 'ACH:GABA:GLU' in mV re rest (SYN_REV_HELP), or None / '' / 'off'.
        the one parser for world/cord.py and experiments/body_loop.py; call after set_syn_tau (it turns the per-class rows on at the engine's tau_syn
        if they are off). returns a line for the log."""
        if spec is None or str(spec).strip() in ("", "off"): self.syn_rev_on = False; return "reversal potentials: off"
        f = [x.strip() for x in str(spec).split(":")]
        if len(f) != 3: raise ValueError(f"--syn-rev wants ACH:GABA:GLU in mV re rest; got {spec!r}")
        e = [None if x.lower() in ("off", "x", "") else float(x) for x in f]
        if e[0] is None or not e[0] > float(self.p.v_thresh): raise ValueError(f"--syn-rev: ACh sets the scale and must reverse above threshold ({self.p.v_thresh:g} mV re rest); got {spec!r}")
        pre = ""
        if not getattr(self, "syn_tau_on", False): t_ = float(self.p.tau_syn); pre = self.set_syn_tau(f"{t_:g}:{t_:g}:{t_:g}") + "; "
        csign = np.array([0.0, 1.0, -1.0, -1.0])   # the class's sign as the file gives it (ACh +, GABA and glutamate -)
        self._has_rev = np.array([False, True, e[1] is not None, e[2] is not None], np.bool_)
        self._e_rev = np.array([0.0] + [x if x is not None else 0.0 for x in e], np.float32)
        self._kap = np.where(self._has_rev, csign / e[0], 0.0).astype(np.float32)   # conductance per mV of the row, re the leak: g kap (E - v); one ACh synapse at rest = g
        sg = np.asarray(self.sign, np.float64); odd = [int(((self._pre_cls == c) & (np.sign(sg) != csign[c]) & (sg != 0)).sum()) for c in (1, 2, 3)]
        self.syn_rev_on = True
        lab = lambda x: "off (a current)" if x is None else f"{x:+g} mV"
        return (pre + f"reversal potentials (re rest): ACh {lab(e[0])}, GABA {lab(e[1])}, glutamate {lab(e[2])}, other a current; conductance per synapse "
                f"{self.p.mv_per_synapse:g} / {e[0]:g} = {self.p.mv_per_synapse / e[0]:.4g} of the leak's; an inhibitory synapse at rest drives "
                f"{(abs(e[1]) / e[0]) if e[1] is not None else float('nan'):.3g} of today's" + (f"; WARNING cells whose sign is not their class's: ACh {odd[0]}, GABA {odd[1]}, glu {odd[2]} (their conductance is negative)" if any(odd) else ""))

    def reset(self):
        super().reset()
        if getattr(self, "syn_tau_on", False): self._gc[:] = 0.0

    def _propagate(self, spikes, scale=None):
        if self.engine == "dense": return super()._propagate(spikes, scale)
        has = scale is not None
        return _propagate(spikes.astype(np.int64), (scale.astype(np.float32) if has else np.zeros(1, np.float32)), has,
                          self._out_ptr, self._out_tgt, self._out_w, self._acc)

    def step(self):
        p, dt = self.p, self.p.dt
        arrived = self._dly.pop(0); arrived_scale = self._dly_scale.pop(0)
        if getattr(self, "graded_on", False) or getattr(self, "std_on", False):   # per-emission scales: depression (09-21) and graded units (09-22)
            sc_ = (self._std_pre if getattr(self, "_std_pre", None) is not None else self._std_x[self.last_idx].copy()) if getattr(self, "std_on", False) else np.ones(self.last_idx.size, np.float32)   # the scale a spike delivers is the resource BEFORE that spike's own decrement (09-22, the review's second pass: it was read after, so a fresh synapse delivered 1 - u)
            if getattr(self, "graded_on", False) and self._graded_scale.size:
                sc_ = np.concatenate([sc_, self._graded_scale]).astype(np.float32); self.last_idx = np.concatenate([self.last_idx, self._graded_idx])
            self._dly_scale.append(sc_ if self.last_idx.size else None)
        else:
            self._dly_scale.append(None)
        if getattr(self, "delay_on", False):   # per-cell conduction delays (09-22): the delay line is Dmax long; a cell's emission is inserted at its own delay
            self._dly.append(np.zeros(0, np.int64)); sc_all = self._dly_scale.pop(); self._dly_scale.append(None)
            while len(self._dly) < int(self._dly_max): self._dly.append(np.zeros(0, np.int64)); self._dly_scale.append(None)   # reset() rebuilds the line at the engine's length; keep it Dmax long
            idx = self.last_idx
            if idx.size:
                dl = self._cell_delay[idx]; sc_all = sc_all if sc_all is not None else np.ones(idx.size, np.float32)
                for d in np.unique(dl):
                    m_ = dl == d; k = int(d) - 1; self._dly[k] = np.concatenate([self._dly[k], idx[m_]])
                    prev = self._dly_scale[k]; self._dly_scale[k] = np.concatenate([prev if prev is not None else np.ones(self._dly[k].size - int(m_.sum()), np.float32), sc_all[m_]]).astype(np.float32)
        else:
            self._dly.append(self.last_idx)
        nt_on = getattr(self, "syn_tau_on", False)
        if arrived.size and nt_on:   # per-transmitter decay (09-22, campaign item 2): each arrival into its presynaptic class's row
            has = arrived_scale is not None
            _propagate_into_nt(arrived.astype(np.int64), (arrived_scale.astype(np.float32) if has else np.zeros(1, np.float32)), has, self._out_ptr, self._out_tgt, self._out_w, self._pre_cls, self._gc)
        elif arrived.size:
            if self.engine == "dense": self.g += self._propagate(arrived, arrived_scale)
            else:
                has = arrived_scale is not None
                _propagate_into(arrived.astype(np.int64), (arrived_scale.astype(np.float32) if has else np.zeros(1, np.float32)), has, self._out_ptr, self._out_tgt, self._out_w, self._acc, self.g)
        # APL: the numpy step subtracts from syn AFTER computing it from the decayed g; same here (syn_out is pre-APL, so apply to v directly below)
        if p.noise:
            if p.exact_noise: noise = self.rng.standard_normal(self.N, dtype=np.float32) * np.float32(p.noise)
            else:
                o = self._noise_off; noise = self._noise_pool[o:o + self.N]; self._noise_off = (o + self._noise_step) % (self._noise_pool.size - self.N)
        else: noise = self._zero_noise
        spk = self._spk_buf
        if len(self._kc) and p.apl_w:
            # fold the APL conductance into ext for the KCs for this step (identical arithmetic: ext*(dt/tau_m) - apl_w*apl*(dt/tau_m))
            ext = self._ext.copy(); ext[self._kc] -= np.float32(p.apl_w * self._apl)
        else: ext = self._ext
        free = self._free_buf   # refrac <= 0 before the update, as in flysim: gates the Poisson receptors below
        if getattr(self, "adapt_on", False) or getattr(self, "rebound_on", False):   # 09-21 night: two labelled intrinsic currents, off by default (docs/SEAM.md "the switch"); as a current on the ext path so the compiled membrane kernels are untouched
            ext = ext - (self._adapt_a if getattr(self, "adapt_on", False) else 0.0) + (self._reb_r if getattr(self, "rebound_on", False) else 0.0); ext = np.ascontiguousarray(ext, dtype=np.float32)
        rev_on = nt_on and getattr(self, "syn_rev_on", False)   # reversal potentials (09-22, campaign item 2b): the per-class rows on conductances
        if rev_on and getattr(self, "integrate", "euler") == "exact":
            e_m = np.exp(-dt / p.tau_m); ek = [exact_kg(t_, p.tau_m, dt) for t_ in self._syn_taus]
            _membrane_exact_nt_rev(self.v, self._gc, np.array([e for e, _ in ek], np.float32), np.array([k for _, k in ek], np.float32), self._has_rev, self._e_rev, self._kap, self.refrac, ext,
                                   np.ascontiguousarray(noise, dtype=np.float32), self.v_th, free, np.float32(e_m), np.float32(1.0 - e_m), np.float32(dt), np.float32(p.v_thresh), spk, bool(getattr(self, "refrac_freeze", False)))
        elif rev_on:
            _membrane_nt_rev(self.v, self._gc, np.float32(dt) / self._syn_taus.astype(np.float32), self._has_rev, self._e_rev, self._kap, self.refrac, ext, np.ascontiguousarray(noise, dtype=np.float32), self.v_th, free,
                             np.float32(dt), np.float32(p.tau_m), np.float32(p.v_thresh), spk)
        elif nt_on and getattr(self, "integrate", "euler") == "exact":
            e_m = np.exp(-dt / p.tau_m); ek = [exact_kg(t_, p.tau_m, dt) for t_ in self._syn_taus]
            _membrane_exact_nt(self.v, self._gc, np.array([e for e, _ in ek], np.float32), np.array([k for _, k in ek], np.float32), self.refrac, ext, np.ascontiguousarray(noise, dtype=np.float32), self.v_th, free,
                               np.float32(e_m), np.float32(1.0 - e_m), np.float32(dt), np.float32(p.v_thresh), spk, bool(getattr(self, "refrac_freeze", False)))
        elif nt_on:
            _membrane_nt(self.v, self._gc, np.float32(dt) / self._syn_taus.astype(np.float32), self.refrac, ext, np.ascontiguousarray(noise, dtype=np.float32), self.v_th, free,
                         np.float32(dt), np.float32(p.tau_m), np.float32(p.v_thresh), spk)
        elif getattr(self, "integrate", "euler") == "exact":
            e_m = np.exp(-dt / p.tau_m); e_s = np.exp(-dt / p.tau_syn); A = p.tau_syn / (p.tau_syn - p.tau_m)
            _membrane_exact(self.v, self.g, self.refrac, ext, np.ascontiguousarray(noise, dtype=np.float32), self.v_th, free,
                            np.float32(e_m), np.float32(e_s), np.float32(A * (e_s - e_m)), np.float32(1.0 - e_m), np.float32(dt), np.float32(p.v_thresh), spk, bool(getattr(self, "refrac_freeze", False)))
        else:
            _membrane(self.v, self.g, self.refrac, ext, np.ascontiguousarray(noise, dtype=np.float32), self.v_th, free,
                  np.float32(dt), np.float32(p.tau_syn), np.float32(p.tau_m), np.float32(p.v_thresh), spk)
        di = self._driven_idx
        if di.size:   # the driven-cell Poisson draw in one kernel (09-18, docs/PERFORMANCE.md: 1.2x on the step; same rng call, same float32 arithmetic, spike-identical)
            n_live = _count_live(di, self.drive_hz)
            r = self.rng.random(n_live) if n_live else self._empty_f64
            _drive_gate(di, self.drive_hz, r, free, spk, np.float32(dt))
        self.last_idx = np.flatnonzero(spk); _reset(self.last_idx, self.v, self.refrac, np.float32(p.v_reset), np.float32(p.refractory))
        if getattr(self, "graded_on", False):   # graded (non-spiking) units, 09-22: never reset (their threshold is out of reach), and each step they emit onto their targets a fraction of a spike = gain x clip((v - v0) / (v1 - v0), 0, 1); a labelled engine change (docs/SEAM.md "graded premotor interneurons")
            gv = self.v[self._graded_cells]; gs = np.clip((gv - np.float32(self.graded_v0)) / np.float32(self.graded_v1 - self.graded_v0), 0.0, 1.0) * np.float32(self.graded_gain)
            on = gs > 0; self._graded_idx = self._graded_cells[on]; self._graded_scale = gs[on].astype(np.float32)
        self.last_spikes = spk.astype(np.float32)
        if getattr(self, "adapt_on", False):   # spike-frequency adaptation: a (mV) decays with tau_a, jumps by b per spike, subtracted from the drive (an AdEx-style w in voltage units)
            self._adapt_a *= np.float32(1.0 - dt / self.adapt_tau)
            if self.last_idx.size: self._adapt_a[self.last_idx] += np.float32(self.adapt_b)
        if getattr(self, "rebound_on", False):   # post-inhibitory rebound: r tracks the hyperpolarisation below rest with tau_r (an I_h-like sag) and pushes back as a depolarising current g_r x r, which outlasts the inhibition
            self._reb_r += (np.float32(self.rebound_g) * np.maximum(-self.v, np.float32(0.0)) - self._reb_r) * np.float32(dt / self.rebound_tau)
        if getattr(self, "std_on", False):
            m = self._std_mask
            self._std_x[m] += (1.0 - self._std_x[m]) * (dt / p.std_tau_rec_ms)
            self._std_pre = self._std_x[self.last_idx].copy() if self.last_idx.size else np.zeros(0, np.float32)   # what these spikes deliver next step
            hit = self.last_idx[m[self.last_idx]] if self.last_idx.size else self.last_idx
            if hit.size: self._std_x[hit] *= (1.0 - p.std_u)
        if len(self._kc) and p.apl_w:
            n_kc = float(spk[self._kc].sum()) / dt; self._apl += (n_kc - self._apl) * (dt / p.apl_tau_ms)
        return spk.copy()


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "brain_whole.npz"; steps = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    A = FlyBrain(path, seed=0); B = FastFlyBrain(path, seed=0)
    drive = np.flatnonzero(A.sc == "sensory")[:2000] if hasattr(A, "sc") else np.arange(2000)
    A.drive_hz[drive] = 50.0; B.drive_hz[drive] = 50.0
    B.step()  # compile
    A = FlyBrain(path, seed=0); B = FastFlyBrain(path, seed=0); A.drive_hz[drive] = 50.0; B.drive_hz[drive] = 50.0
    same = 0; na = nb = 0; t_a = t_b = 0.0
    for i in range(steps):
        t = time.perf_counter(); sa = A.step(); t_a += time.perf_counter() - t
        t = time.perf_counter(); sb = B.step(); t_b += time.perf_counter() - t
        same += int(np.array_equal(sa, sb)); na += int(sa.sum()); nb += int(sb.sum())
        if not np.array_equal(sa, sb) and same == i: print(f"first divergence at step {i}: {int(sa.sum())} vs {int(sb.sum())} spikes, |dv| max {np.abs(A.v - B.v).max():.3g}")
    print(f"{path}: {steps} steps; identical steps {same}/{steps}; spikes {na} vs {nb}; numpy {1e3 * t_a / steps:.2f} ms/step, numba {1e3 * t_b / steps:.2f} ms/step ({t_a / t_b:.1f}x)")
