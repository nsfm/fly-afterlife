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

    def _propagate(self, spikes, scale=None):
        if self.engine == "dense": return super()._propagate(spikes, scale)
        has = scale is not None
        return _propagate(spikes.astype(np.int64), (scale.astype(np.float32) if has else np.zeros(1, np.float32)), has,
                          self._out_ptr, self._out_tgt, self._out_w, self._acc)

    def step(self):
        p, dt = self.p, self.p.dt
        arrived = self._dly.pop(0); arrived_scale = self._dly_scale.pop(0)
        if getattr(self, "std_on", False):
            self._dly_scale.append(self._std_x[self.last_idx].copy() if self.last_idx.size else None)
        else:
            self._dly_scale.append(None)
        self._dly.append(self.last_idx)
        if arrived.size:
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
        if getattr(self, "integrate", "euler") == "exact":
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
        self.last_spikes = spk.astype(np.float32)
        if getattr(self, "adapt_on", False):   # spike-frequency adaptation: a (mV) decays with tau_a, jumps by b per spike, subtracted from the drive (an AdEx-style w in voltage units)
            self._adapt_a *= np.float32(1.0 - dt / self.adapt_tau)
            if self.last_idx.size: self._adapt_a[self.last_idx] += np.float32(self.adapt_b)
        if getattr(self, "rebound_on", False):   # post-inhibitory rebound: r tracks the hyperpolarisation below rest with tau_r (an I_h-like sag) and pushes back as a depolarising current g_r x r, which outlasts the inhibition
            self._reb_r += (np.float32(self.rebound_g) * np.maximum(-self.v, np.float32(0.0)) - self._reb_r) * np.float32(dt / self.rebound_tau)
        if getattr(self, "std_on", False):
            m = self._std_mask
            self._std_x[m] += (1.0 - self._std_x[m]) * (dt / p.std_tau_rec_ms)
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
