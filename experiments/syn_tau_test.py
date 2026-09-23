"""syn_tau_test.py - the per-transmitter synaptic decay (world/fastlif.py set_syn_tau; 09-22, campaign item 2) on a six-cell brain: three
presynaptic cells, one each of acetylcholine, gaba and glutamate, each onto its own target by 10 synapses, no noise, no drive. each
presynaptic cell is kicked over threshold once and the target's PSP is read per ms. deterministic; exits 1 on any failure.

    uv run python experiments/syn_tau_test.py

checks:
  1. off vs on at the engine's own tau (5:5:5): bit-identical voltages, both integrators (one class live per cell, so the sums are exact)
  2. on at 5:20:20, exact integrator: every target's trace equals the closed form g0 A (e^-t/tau_s - e^-t/tau_m) (at tau_s = tau_m, the
     limit g0 t/tau_m e^-t/tau_m) to 1e-5 mV, sign by the file (ACh +, GABA and glutamate -)
  3. the expected amounts: the IPSP's area over the EPSP's is tau_GABA / tau_ACh = 4 (the charge a PSP carries is g0 tau_s), its peak comes
     at tau_m = 20 ms against ln(tau_m / tau_s) tau_s tau_m / (tau_m - tau_s) = 9.24 ms, and its half-width is the closed form's
  4. the Euler integrator at 5:20:20: the area ratio is Euler's discrete (20 - 1) / (5 - 1) = 4.75 (it decays g before reading it:
     the record's 16 %-low 5 ms synapse, docs/MINECRAFT_OPEN.md)
"""
import os, sys, tempfile, numpy as np
sys.path.insert(0, "ref/flybrain/scripts"); sys.path.insert(0, "world")
from flysim import Params
from fastlif import FastFlyBrain

NT = ["acetylcholine", "acetylcholine", "gaba", "acetylcholine", "glutamate", "acetylcholine"]   # pre, post pairs: (0 -> 1), (2 -> 3), (4 -> 5)
PRE, POST = np.array([0, 2, 4]), np.array([1, 3, 5]); NSYN = 10.0; STEPS = 200
path = os.path.join(tempfile.mkdtemp(), "brain_syn_tau_test.npz"); n = len(NT)
np.savez(path, bodyId=np.arange(n, dtype=np.int64), type=np.array([f"t{i}" for i in range(n)]), cls=np.array(["test"] * n), sc=np.array(["test"] * n),
         side=np.array(["M"] * n), nt=np.array(NT), sign=np.array([{"acetylcholine": 1, "gaba": -1, "glutamate": -1}[x] for x in NT], np.int8),
         pre=PRE, post=POST, w=np.full(3, NSYN, np.float32))

def run(integrate, spec):
    M = FastFlyBrain(path, seed=0, params=Params(noise=0.0)); M.integrate = integrate
    M.driven[:] = False; M._driven_idx = np.flatnonzero(M.driven); M.reset()
    if spec: M.set_syn_tau(spec)
    M.v[PRE] = np.float32(10.0)   # over threshold: each presynaptic cell fires once at step 0
    V = np.zeros((STEPS, 3), np.float32)
    for k in range(STEPS): M.step(); V[k] = M.v[POST]
    return V, M.p

def closed(t, g0, tau_s, tau_m):
    if abs(tau_s - tau_m) < 1e-6 * tau_m: return g0 * (t / tau_m) * np.exp(-t / tau_m)
    return g0 * tau_s / (tau_s - tau_m) * (np.exp(-t / tau_s) - np.exp(-t / tau_m))

def fwhm(t, v):
    a = np.abs(v); h = a.max() / 2; above = np.flatnonzero(a >= h); i0, i1 = above[0], above[-1]
    lo = t[i0 - 1] + (h - a[i0 - 1]) / (a[i0] - a[i0 - 1]) * (t[i0] - t[i0 - 1]); hi = t[i1] + (a[i1] - h) / (a[i1] - a[i1 + 1]) * (t[i1 + 1] - t[i1])
    return hi - lo

ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"  {'PASS' if cond else 'FAIL'}  {name}{('  ' + detail) if detail else ''}")

print("1. off vs on at the engine's own tau (5:5:5)")
for integ in ("euler", "exact"):
    a, _ = run(integ, ""); b, _ = run(integ, "5:5:5")
    check(f"{integ}: bit-identical", np.array_equal(a, b), f"max |dv| {np.abs(a - b).max():.3g} mV")

print("2-3. on at ACh 5 / GABA 20 / glutamate 20 ms, exact integrator")
V, p = run("exact", "5:20:20"); g0 = NSYN * p.mv_per_synapse; taus = (5.0, 20.0, 20.0)
k0 = int(np.flatnonzero(np.abs(V[:, 0]) > 0)[0]); t = (np.arange(STEPS - k0) + 1) * p.dt   # the arrival step is v(dt) of the closed form
res = {}
for j, (lab, sgn, ts) in enumerate(zip(("ACh EPSP", "GABA IPSP", "Glu IPSP"), (1, -1, -1), taus)):
    v = V[k0:, j].astype(np.float64); ref = sgn * closed(t, g0, ts, p.tau_m)
    check(f"{lab} = closed form (tau_s {ts:g} ms)", np.abs(v - ref).max() < 1e-5 and np.sign(v[np.argmax(np.abs(v))]) == sgn, f"max |err| {np.abs(v - ref).max():.2g} mV, peak {v[np.argmax(np.abs(v))]:+.3f} mV")
    tt = np.linspace(1e-3, 150, 150001); rr = closed(tt, g0, ts, p.tau_m)
    res[lab] = dict(area=np.abs(v).sum() * p.dt, peak_t=t[np.argmax(np.abs(v))], fwhm=fwhm(t, v), fwhm_ref=fwhm(tt, rr), peak_t_ref=tt[np.argmax(rr)], area_ref=g0 * ts)
for lab, r in res.items(): print(f"     {lab}: area {r['area']:.2f} mV ms (closed form {r['area_ref']:.2f}), peak at {r['peak_t']:.0f} ms ({r['peak_t_ref']:.2f}), half-width {r['fwhm']:.2f} ms ({r['fwhm_ref']:.2f})")
E, I = res["ACh EPSP"], res["GABA IPSP"]; ratio = I["area"] / E["area"]
check("IPSP / EPSP area = tau_GABA / tau_ACh = 4", abs(ratio - 4.0) < 0.02, f"{ratio:.3f}")
check("IPSP peaks at tau_m, EPSP at 9.24 ms (1 ms grid)", abs(I["peak_t"] - 20.0) <= 1 and abs(E["peak_t"] - 9.24) <= 1, f"{I['peak_t']:.0f} vs {E['peak_t']:.0f} ms")
check("half-widths match the closed form (1 ms grid, 0.2 ms)", abs(I["fwhm"] - I["fwhm_ref"]) < 0.2 and abs(E["fwhm"] - E["fwhm_ref"]) < 0.2,
      f"IPSP {I['fwhm']:.2f} ms vs EPSP {E['fwhm']:.2f} ms: {I['fwhm'] / E['fwhm']:.2f}x longer (closed form {I['fwhm_ref'] / E['fwhm_ref']:.2f}x)")
check("glutamate row = GABA row (same tau)", np.array_equal(V[:, 1], V[:, 2]))

print("4. Euler integrator at 5:20:20")
Ve, _ = run("euler", "5:20:20"); ae = np.abs(Ve).sum(0)
ex = (20.0 / p.dt - 1) / (5.0 / p.dt - 1)   # Euler decays g before reading it, so a spike delivers g0 (tau_s / dt - 1), not g0 tau_s: 19 / 4
check("IPSP / EPSP area = (20 - 1) / (5 - 1) = 4.75 (Euler's own)", abs(ae[1] / ae[0] - ex) < 0.01, f"{ae[1] / ae[0]:.3f}; IPSP sign {np.sign(Ve[:, 1].sum()):+.0f}")
print("SYN TAU TEST", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
