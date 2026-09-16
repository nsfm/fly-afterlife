"""
seam.py - the hybrid. flyvis (graded optic lobe) drives the MaleCNS LIF at T4/T5.

    flyvis T4/T5 activity per column  ->  firing rate  ->  our fly's T4/T5 cells as
    Poisson sources  ->  real wiring: T4/T5 -> LPLC2/LC/VS/HS -> giant fiber -> DNs

LABELLED CHOICES (v0):
  1. column map: our (hex1, hex2) per eye -> flyvis (u, v) by centring and flipping
     one axis (our occupancy slides the opposite way to flyvis's lattice). Nearest
     column; our eye has ~880 columns vs flyvis's 721, so the rim gets no drive.
  2. rate = MAX_HZ * clip(activity / A_REF, 0, 1). flyvis activity is in arbitrary
     units; a full-contrast loom peaks ~1.5. A_REF=1.0, MAX_HZ=150.
  3. both eyes get the same flyvis output (stimulus is on the midline; a lateral
     stimulus needs a mirrored second run).
  4. the LIF's own optic lobe stays at 0 Hz rest. Only T4/T5 are driven.
"""
import sys, time, numpy as np
sys.path.insert(0, "ref/flybrain/scripts")
from flysim import FlyBrain

MAX_HZ, A_REF = 150.0, 1.0
FLIP_V = True          # choice 1
CENTRE = (18.5, 20.0)  # hex1, hex2 centroid of our eye

b = FlyBrain("brain_whole.npz")
ty = b.type.astype(str)
cols = np.load("seam/t4t5_columns.npz"); fv = np.load("seam/flyvis_out.npz")
types = ["T4a", "T4b", "T4c", "T4d", "T5a", "T5b", "T5c", "T5d"]

# --- column map ---------------------------------------------------------------
u = cols["hex1"] - CENTRE[0]; v = cols["hex2"] - CENTRE[1]
if FLIP_V: v = -v
u = np.rint(u).astype(int); v = np.rint(v).astype(int)
inside = (np.abs(u) <= 15) & (np.abs(v) <= 15) & (np.abs(u + v) <= 15)
src_col = np.full(len(u), -1)
for t in types:
    m = cols["type"] == t
    key = {(int(a), int(c)): i for i, (a, c) in enumerate(zip(fv[f"u_{t}"], fv[f"v_{t}"]))}
    for i in np.flatnonzero(m & inside):
        src_col[i] = key.get((u[i], v[i]), -1)
mapped = src_col >= 0
print(f"column map: {mapped.sum()} of {len(u)} T4/T5 cells inside the flyvis lattice "
      f"({mapped.mean():.0%}); rim without drive: {(~mapped).sum()}")
cell_idx = cols["idx"][mapped]; cell_type = cols["type"][mapped]; cell_src = src_col[mapped]

# --- make T4/T5 spike sources ------------------------------------------------------
b.driven[cell_idx] = True
b._driven_idx = np.flatnonzero(b.driven)

# --- readouts ----------------------------------------------------------------------
def pop(prefix=None, exact=None, sc=None):
    m = np.ones(b.N, bool)
    if prefix: m &= np.char.startswith(ty, prefix)
    if exact: m &= np.isin(ty, exact)
    if sc: m &= b.sc == sc
    return np.flatnonzero(m)
R = {"LPLC2": pop(exact=["LPLC2"]), "LPLC1": pop(exact=["LPLC1"]), "LC4": pop(exact=["LC4"]),
     "LC6": pop(exact=["LC6"]), "LC11": pop(exact=["LC11"]), "LC16": pop(exact=["LC16"]),
     "VS/HS": pop(prefix="VS") if len(pop(prefix="VS")) else pop(prefix="HS"),
     "DNp01 GF": pop(exact=["DNp01"]), "DNp02": pop(exact=["DNp02"]), "DNp11": pop(exact=["DNp11"]),
     "all DN": b.pop["DN"], "leg MN": pop(sc="vnc_motor")}
R = {k: v for k, v in R.items() if len(v)}
fps = int(fv["fps"]); steps_per_frame = int(round(1000 / fps / b.p.dt))

def run(stim):
    b.reset(); b.drive_hz[:] = 0.0
    b.g[:] = 0; b.refrac[:] = 0
    T = fv[f"{stim}_T4a"].shape[0] if stim else 150
    rec = np.zeros((T * steps_per_frame, b.N), bool)
    for f in range(T):
        if stim:
            for t in types:
                m = cell_type == t
                a = fv[f"{stim}_{t}"][f][cell_src[m]]
                b.drive_hz[cell_idx[m]] = MAX_HZ * np.clip(a / A_REF, 0, 1)
        for s in range(steps_per_frame):
            rec[f * steps_per_frame + s] = b.step()
    return rec

results = {}
for stim in [None, "static", "translate", "recede", "loom"]:
    t0 = time.time(); rec = run(stim); name = stim or "no drive"
    pre, dur = rec[100:500], rec[500:]           # frames 10-50 baseline, 50-150 stimulus
    row = {}
    for k, idx in R.items():
        hz_pre = pre[:, idx].sum() / len(idx) / (pre.shape[0] / 1000)
        hz_dur = dur[:, idx].sum() / len(idx) / (dur.shape[0] / 1000)
        row[k] = (hz_pre, hz_dur, int(dur[:, idx].sum()))
    results[name] = row
    t4 = rec[:, cell_idx].sum() / len(cell_idx) / (rec.shape[0] / 1000)
    print(f"{name:10s} {time.time()-t0:5.1f}s  T4/T5 mean {t4:5.1f} Hz", flush=True)

print(f"\n{'readout':10s}" + "".join(f"{n:>22s}" for n in results))
print(f"{'':10s}" + "".join(f"{'pre -> during (spk)':>22s}" for _ in results))
for k in R:
    line = f"{k:10s}"
    for n, row in results.items():
        p, d, s = row[k]; line += f"{p:6.1f} -> {d:6.1f} ({s:5d})"
    print(line)
