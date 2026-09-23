"""syn_rev_test.py - reversal potentials per transmitter class (world/fastlif.py set_syn_rev; 09-22, campaign item 2b) on a ten-cell brain:
five presynaptic cells each onto its own target, no noise, no drive. pairs: ACh -> a cell at rest; GABA -> a cell at rest; GABA -> a cell
held at +5 mV by a tonic ext current; glutamate -> a cell at rest (one synapse each); GABA -> a cell at rest by 20,000 synapses (the shunt).
each presynaptic cell is kicked over threshold once and the target's PSP is read per ms against a run with no kick (so the held cell's
baseline cancels). deterministic; exits 1 on any failure.

    uv run python experiments/syn_rev_test.py

checks:
  1. off vs on with the reversals far (ACh +1e6, GABA and glutamate -1e6 mV re rest): the conductance per synapse is mv_per_synapse / 1e6,
     the driving force 1e6 - v, so the PSPs are the current-based ones to within float32 rounding and v / 1e6; both integrators
  2. on at 70:-5:-5, exact integrator: one ACh synapse at rest gives today's EPSP (first order: x (70 - v) / 70); one GABA synapse at rest
     gives today's PSP shape x 5 / 70, and onto the cell held at +5 mV x 10 / 70 (twice); glutamate = GABA. the closed form is the
     current-based g0 A (e^-t/tau_s - e^-t/tau_m) times the driving force at the holding voltage over E_ach (first order in the PSP)
  4. --syn-rev-hold each (kap_c = sign_c / |E_c|): the far case is unchanged (all |E| = 1e6); at 70:-5:-5 one GABA synapse at rest gives
     TODAY'S IPSP (-0.0433 mV peak, the closed form), onto the cell at +5 mV twice that, glutamate = GABA, the ACh EPSP as under ach
  3. the shunt: 20,000 GABA synapses (the record would put the cell on the -7 mV floor) cannot take it below E_GABA = -5 mV, either
     integrator (the step's phi(x) = (1 - e^-x) / x lands a big conductance on its reversal instead of past it)
"""
import os, sys, tempfile, numpy as np
sys.path.insert(0, "ref/flybrain/scripts"); sys.path.insert(0, "world")
from flysim import Params
from fastlif import FastFlyBrain

PRE_NT = ["acetylcholine", "gaba", "gaba", "glutamate", "gaba"]; NSYN = np.array([1.0, 1.0, 1.0, 1.0, 20000.0], np.float32)
NT = [x for p in PRE_NT for x in (p, "acetylcholine")]; n = len(NT)
PRE, POST = np.arange(0, n, 2), np.arange(1, n, 2); HELD = POST[2]; V_HOLD = 5.0; STEPS = 200
LAB = ["ACh -> rest", "GABA -> rest", "GABA -> +5 mV", "Glu -> rest", "GABA x20000 -> rest"]
path = os.path.join(tempfile.mkdtemp(), "brain_syn_rev_test.npz")
np.savez(path, bodyId=np.arange(n, dtype=np.int64), type=np.array([f"t{i}" for i in range(n)]), cls=np.array(["test"] * n), sc=np.array(["test"] * n),
         side=np.array(["M"] * n), nt=np.array(NT), sign=np.array([{"acetylcholine": 1, "gaba": -1, "glutamate": -1}[x] for x in NT], np.int8),
         pre=PRE, post=POST, w=NSYN)

def run(integrate, rev, kick=True, hold="ach"):
    M = FastFlyBrain(path, seed=0, params=Params(noise=0.0)); M.integrate = integrate
    M.driven[:] = False; M._driven_idx = np.flatnonzero(M.driven); M.reset()
    if rev: M.set_syn_rev(rev, hold)
    M._ext[HELD] = np.float32(V_HOLD); M.v[HELD] = np.float32(V_HOLD)   # held at +5 mV (steady state of dv = (-v + ext) / tau_m)
    if kick: M.v[PRE] = np.float32(10.0)   # over threshold: each presynaptic cell fires once at step 0
    V = np.zeros((STEPS, len(POST)), np.float32)
    for k in range(STEPS): M.step(); V[k] = M.v[POST]
    return V, M.p

def psp(integrate, rev, hold="ach"): a, p = run(integrate, rev, hold=hold); b, _ = run(integrate, rev, kick=False, hold=hold); return (a.astype(np.float64) - b), a, p

def closed(t, g0, tau_s, tau_m):
    return g0 * tau_s / (tau_s - tau_m) * (np.exp(-t / tau_s) - np.exp(-t / tau_m))

ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"  {'PASS' if cond else 'FAIL'}  {name}{('  ' + detail) if detail else ''}")

print("1. off vs on with the reversals far (1e6:-1e6:-1e6)")
for integ in ("euler", "exact"):
    a, _, _ = psp(integ, ""); b, _, _ = psp(integ, "1e6:-1e6:-1e6"); d = np.abs(a - b)[:, :4].max(0)
    check(f"{integ}: the four one-synapse PSPs agree to 1e-6 mV (the held cell: float32 ulp at 5 mV, 4.8e-7)", d.max() < 1e-6, "max |dv| " + ", ".join(f"{l} {x:.2g}" for l, x in zip(LAB, d)) + f" (peaks {np.abs(a[:, :4]).max(0).round(4).tolist()} mV)")

print("2. on at 70:-5:-5, exact integrator, one synapse each")
cur, _, p = psp("exact", ""); V, _, _ = psp("exact", "70:-5:-5"); g0 = float(p.mv_per_synapse); E_ACH = 70.0
k0 = int(np.flatnonzero(np.abs(V[:, 0]) > 0)[0]); t = (np.arange(STEPS - k0) + 1) * p.dt
base = closed(t, g0, p.tau_syn, p.tau_m)
for j, (lab, drive) in enumerate(zip(LAB[:4], [(E_ACH - 0.0) / E_ACH, (-5.0 - 0.0) / E_ACH, (-5.0 - V_HOLD) / E_ACH, (-5.0 - 0.0) / E_ACH])):
    v = V[k0:, j]; ref = base * drive; pk = np.argmax(np.abs(v)); err = np.abs(v - ref).max() / np.abs(ref).max()
    check(f"{lab}: = today's PSP x {drive:+.4f} (closed form, 1 % of peak)", err < 0.01, f"peak {v[pk]:+.5f} mV at {t[pk]:.0f} ms (closed form {ref[np.argmax(np.abs(ref))]:+.5f}; today's current {cur[k0:, j][np.argmax(np.abs(cur[k0:, j]))]:+.5f}); max |err| {100 * err:.2f} % of peak")
pr, ph = np.abs(V[k0:, 1]).max(), np.abs(V[k0:, 2]).max()
check("IPSP at +5 mV / IPSP at rest = (5 + 5) / 5 = 2", abs(ph / pr - 2.0) < 0.01, f"{ph / pr:.4f}")
check("IPSP at rest / today's IPSP = 5 / 70 = 0.0714", abs(pr / np.abs(cur[k0:, 1]).max() - 5 / 70) < 0.001, f"{pr / np.abs(cur[k0:, 1]).max():.4f}")
check("glutamate row = GABA row (same reversal, same tau)", np.array_equal(V[:, 1], V[:, 3]))
Ve, _, _ = psp("euler", "70:-5:-5"); pe = np.abs(Ve[:, :3]).max(0)
check("euler: IPSP at +5 / at rest = 2, and at rest / EPSP = 5 / 70", abs(pe[2] / pe[1] - 2) < 0.01 and abs(pe[1] / pe[0] - 5 / 70) < 0.001, f"{pe[2] / pe[1]:.4f}, {pe[1] / pe[0]:.4f}")

print("3. the shunt: 20,000 GABA synapses onto a cell at rest")
for integ in ("euler", "exact"):
    a, _ = run(integ, ""); b, _ = run(integ, "70:-5:-5")
    check(f"{integ}: on, the cell never goes below E_GABA = -5 mV (off: the -7 mV floor)", b[:, 4].min() >= -5.0 - 1e-4 and a[:, 4].min() <= -7.0 + 1e-4,
          f"min v on {b[:, 4].min():+.4f} mV, off {a[:, 4].min():+.4f} mV")

print("4. --syn-rev-hold each: every class's PSP at rest is today's")
for integ in ("euler", "exact"):
    a, _, _ = psp(integ, ""); b, _, _ = psp(integ, "1e6:-1e6:-1e6", "each"); d = np.abs(a - b)[:, :4].max()
    check(f"{integ}: far reversals (1e6:-1e6:-1e6) = the current PSPs to 1e-6 mV", d < 1e-6, f"max |dv| {d:.2g}")
Vh, _, _ = psp("exact", "70:-5:-5", "each")
for j, (lab, drive) in enumerate(zip(LAB[:4], [1.0, -1.0, -(5.0 + V_HOLD) / 5.0, -1.0])):
    v = Vh[k0:, j]; ref = base * drive; pk = np.argmax(np.abs(v)); err = np.abs(v - ref).max() / np.abs(ref).max()
    check(f"{lab}: = today's PSP x {drive:+.1f} (closed form, 1 % of peak)", err < 0.01, f"peak {v[pk]:+.5f} mV at {t[pk]:.0f} ms (closed form {ref[np.argmax(np.abs(ref))]:+.5f}); max |err| {100 * err:.2f} % of peak")
qr, qh = np.abs(Vh[k0:, 1]).max(), np.abs(Vh[k0:, 2]).max(); qc = np.abs(cur[k0:, 1]).max()
check("IPSP at rest = today's (-0.0433 mV) to 1 % (short by the IPSP's own pull on a 5 mV driving force, second order: ~PSP / 2 / 5)", abs(qr / qc - 1) < 0.01, f"{-qr:+.5f} vs {-qc:+.5f} mV ({qr / qc:.4f})")
check("IPSP at +5 mV / at rest = 2", abs(qh / qr - 2.0) < 0.01, f"{qh / qr:.4f}")
check("glutamate row = GABA row", np.array_equal(Vh[:, 1], Vh[:, 3]))
check("the ACh row = hold ach's (ACh's scale is E_ach either way)", np.array_equal(Vh[:, 0], V[:, 0]))
for integ in ("euler", "exact"):
    b, _ = run(integ, "70:-5:-5", hold="each")
    check(f"{integ}: the shunt at 14x the conductance still stops at E_GABA", b[:, 4].min() >= -5.0 - 1e-4, f"min v {b[:, 4].min():+.4f} mV")
print("SYN REV TEST", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
