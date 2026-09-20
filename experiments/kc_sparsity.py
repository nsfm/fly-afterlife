"""kc_sparsity.py - the Kenyon-cell sparsity calibration, standalone (09-19 evening; the morning's numbers were made inline).
the standing brain (tonic floor, 2 s warm-up), then five food-ORN types (DM1, DM2, DM3, DM4, DM5: Or42b, Or22a, Or47a, Or59b,
Or85a) at 150 Hz for 1 s; reports the fraction of KCs that fire at least once in that second and the mean KC rate.
life: ~5-10 % of KCs respond to an odour (Turner 2008; Honegger 2011).

    uv run python experiments/kc_sparsity.py 0.185 0.22 0.25 0.275
"""
import sys, os, numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(ROOT, "world")); sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "seam"))
sys.path.insert(0, os.path.join(ROOT, "ref", "flybrain", "scripts"))   # flysim (the reference LIF engine, TheMrRaGe/flybrain)
from flysim import Params
from fastlif import FastFlyBrain
from fly_afterlife.receptors import Registry, tonic_floor
from fly_afterlife.effectors import apply_tonic

ODOUR = ["ORN_DM1", "ORN_DM2", "ORN_DM3", "ORN_DM4", "ORN_DM5"]; HZ = 150.0; WARM = 2.0; STIM = 1.0; DT = 0.001

def measure(w, seed=0, integrate="exact"):
    M = FastFlyBrain(os.path.join(ROOT, "brain_whole.npz"), seed=seed, params=Params(mv_per_synapse=w)); M.integrate = integrate
    ty = M.type.astype(str); kc = np.flatnonzero(np.char.startswith(ty, "KC")); orn = np.flatnonzero(np.isin(ty, ODOUR))
    REG = Registry(); fl = tonic_floor(M, REG); flc = np.unique(np.concatenate([rc.cells for rc in fl]))
    M.driven[:] = False; M.driven[flc] = True; M.driven[orn] = True; M._driven_idx = np.flatnonzero(M.driven)
    n_warm = int(WARM / DT); n_stim = int(STIM / DT); fired = np.zeros(len(kc), bool); spikes_kc = 0
    for i in range(n_warm + n_stim):
        apply_tonic(REG, M, i * DT, DT)
        if i >= n_warm: M.drive_hz[orn] = HZ
        M.step(); idx = M.last_idx
        if i >= n_warm and len(idx): m = np.isin(idx, kc); spikes_kc += int(m.sum()); fired[np.searchsorted(kc, idx[m])] = True
    return dict(w=w, kc=len(kc), orn=len(orn), frac=fired.mean(), hz=spikes_kc / len(kc) / STIM)

if __name__ == "__main__":
    ws = [float(a) for a in sys.argv[1:]] or [0.185, 0.275]
    print(f"{'w (mV)':>8s} {'KCs':>6s} {'ORNs':>5s} {'KCs firing':>11s} {'mean KC Hz':>11s}")
    for w in ws:
        r = measure(w); print(f"{r['w']:8.3f} {r['kc']:6d} {r['orn']:5d} {r['frac'] * 100:10.1f}% {r['hz']:11.2f}", flush=True)
