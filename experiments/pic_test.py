"""pic_test.py - the persistent inward current (world/fastlif.py set_pic; 09-23, campaign item 4) on a one-cell brain: no synapses, no drive,
a tonic ext current as the only input. the term: I = g m (70 - v) / 70 mV per ms, dm/dt = (m_inf(v) - m) / tau, m_inf a Boltzmann at
v_half, k (mV re rest; threshold 7, reset 0). deterministic where it says so; exits 1 on any failure.

    uv run python experiments/pic_test.py

checks:
  a. below v_half the cell is quiet: v_half +5, k 1, tau 50, at ext 0 and ext 1 mV, g 0.25 and 1: no spike in 2 s, v within 0.02 mV of the
     lowest fixed point of v = ext + tau_m g m_inf(v) (70 - v) / 70 (the small window current below v_half)
  b. near v_half it fires: ext 4.5 mV (2.5 under threshold: the cell alone sits at 4.5 and never fires), the term on: at g 0.1 m activates
     and holds the cell on a subthreshold plateau (its fixed point); at g 0.25 / 0.5 / 1 / 2 the cell fires repetitively (>= 10 spikes in
     the last second, CV of the ISI < 0.1) at a rate that rises with g, both integrators
  c. off vs on at g = 0: bit for bit (every v, every spike, 3 s, noise on at the record's 0.15 mV, ext 6.5 so the noise fires it), both integrators
"""
import os, sys, tempfile, numpy as np
sys.path.insert(0, "ref/flybrain/scripts"); sys.path.insert(0, "world")
from flysim import Params
from fastlif import FastFlyBrain

path = os.path.join(tempfile.mkdtemp(), "brain_pic_test.npz")
np.savez(path, bodyId=np.arange(1, dtype=np.int64), type=np.array(["cell"]), cls=np.array(["test"]), sc=np.array(["test"]), side=np.array(["M"]),
         nt=np.array(["acetylcholine"]), sign=np.array([1], np.int8), pre=np.zeros(0, np.int64), post=np.zeros(0, np.int64), w=np.zeros(0, np.float32))

def run(integrate, pic, ext, ms, noise=0.0, seed=0):
    M = FastFlyBrain(path, seed=seed, params=Params(noise=noise)); M.integrate = integrate
    M.driven[:] = False; M._driven_idx = np.flatnonzero(M.driven)
    line = M.set_pic(pic) if pic else ""; M.reset()
    M._ext[0] = np.float32(ext)
    V = np.zeros(ms, np.float32); S = np.zeros(ms, bool)
    for k in range(ms): S[k] = bool(M.step()[0]); V[k] = M.v[0]
    return V, S, line

def fixed_point(ext, g, vh, k, tau_m=20.0):
    """the lowest v with v = ext + tau_m g m_inf(v) (70 - v) / 70 (m at steady state), iterated up from ext."""
    v = ext
    for _ in range(10000): v = ext + tau_m * g / (1 + np.exp(-(v - vh) / k)) * (70 - v) / 70
    return v

ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"  {'PASS' if cond else 'FAIL'}  {name}{('  ' + detail) if detail else ''}")

print("a. below v_half: quiet (v_half +5 mV re rest, k 1, tau 50 ms)")
for integ in ("euler", "exact"):
    for ext in (0.0, 1.0):
        for g in (0.25, 1.0):
            V, S, _ = run(integ, f"cell:{g}:5:1:50", ext, 2000)
            vss = fixed_point(ext, g, 5.0, 1.0)
            check(f"{integ} ext {ext:g} g {g:g}: no spike, v settles at the lowest fixed point {vss:.3f}", S.sum() == 0 and abs(V[-1] - vss) < 0.02, f"spikes {int(S.sum())}, v {V[-1]:.3f} mV")

print("b. near v_half: the current activates and the cell fires (ext 4.5 mV; threshold 7)")
for integ in ("euler", "exact"):
    V0, S0, _ = run(integ, "", 4.5, 2000)
    check(f"{integ} off: the cell sits at {V0[-1]:.2f} mV and never fires", S0.sum() == 0)
    V, S, _ = run(integ, "cell:0.1:5:1:50", 4.5, 2000); vss = fixed_point(4.5, 0.1, 5.0, 1.0)
    check(f"{integ} g 0.1: the current activates but holds the cell under threshold (a subthreshold plateau at {vss:.2f} mV)", S.sum() == 0 and abs(V[-1] - vss) < 0.02, f"v {V[-1]:.3f} mV, 0 spikes")
    rates = []
    for g in (0.25, 0.5, 1.0, 2.0):
        V, S, line = run(integ, f"cell:{g}:5:1:50", 4.5, 2000)
        isi = np.diff(np.flatnonzero(S[1000:])); hz = float(S[1000:].sum()); rates.append(hz)
        cv = float(isi.std() / isi.mean()) if isi.size > 1 else float("nan")
        check(f"{integ} g {g:g}: repetitive firing", hz >= 10 and cv < 0.1, f"{hz:.0f} Hz in the last second, ISI {isi.mean() if isi.size else float('nan'):.1f} ms (CV {cv:.3f}), first spike at {int(np.argmax(S))} ms")
    check(f"{integ}: the rate rises with g", all(b > a for a, b in zip(rates, rates[1:])), " / ".join(f"{r:.0f}" for r in rates) + " Hz at g 0.25 / 0.5 / 1 / 2")

print("c. off vs on at g = 0: bit for bit (noise 0.15, ext 6.5 so the noise fires it, 3 s)")
for integ in ("euler", "exact"):
    Va, Sa, _ = run(integ, "", 6.5, 3000, noise=0.15, seed=7); Vb, Sb, _ = run(integ, "cell:0:5:1:50", 6.5, 3000, noise=0.15, seed=7)
    check(f"{integ}: v and spikes identical", np.array_equal(Va, Vb) and np.array_equal(Sa, Sb) and Sa.sum() > 0, f"{int(Sa.sum())} spikes each, max |dv| {np.abs(Va - Vb).max():.3g}")

print("PIC TEST", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
