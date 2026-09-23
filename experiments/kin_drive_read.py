"""kin_drive_read.py <run> [<run> ...]: KIN-DRIVE reads (experiments/body_loop.py --kin-drive): the cord listening to a real fly's step.

per leg and motor pool, and per cited premotor cell logged with --log-x, against the IMPOSED step (the run's kin_swing: 1 = the foot moving
forward relative to the thorax, per ms; body_loop.py --kin-drive says how it is made):
  rate in the imposed swing and in the imposed stance (Hz per cell), their ratio (swing / stance);
  the phase of every spike within its step cycle (cycle = one swing onset to the next, phase linear in time, 0 = swing onset), in 8 bins;
  the vector strength (|mean of e^(i 2 pi phase)|) and its mean phase, against a shuffled-cycle null: the spike train rolled circularly
  within the read window by a random offset (0.5 s to the window minus 0.5 s; rng seed 0), 20 draws, the 95th percentile; LOCKED = above it
  (and >= 20 spikes).
the read window: from --t0 (default 3.0 s: the warm-up's 2 s + the command's 1 s ramp) to the end, the same for every arm; only whole cycles.
the motor neurons come from frames (10 ms bins; each bin's spikes put at its centre, so the phase is quantised to 10 ms of a ~90 ms cycle:
a vector strength shrinks by at most ~2 % for that, and the null is quantised alike); the premotor cells from x_ms (1 ms). the pools by leg
via world/legmn.npz; the premotor cells by leg from the annotation's soma neuromere and soma side (T1 / T2 / T3, L / R); a cell in A1 has no
leg and is left out. for the bilateral 07B / 19B cells the soma's leg is a convention, not their target: said beside them.

    uv run python experiments/kin_drive_read.py world/body/loop/kd_a_walk world/body/loop/kd_e_walk_deaf
"""
import sys, argparse, numpy as np
import pandas as pd

ap = argparse.ArgumentParser(); ap.add_argument("runs", nargs="+"); ap.add_argument("--t0", type=float, default=3.0); ap.add_argument("--draws", type=int, default=20)
ap.add_argument("--min-spikes", type=int, default=20); args = ap.parse_args()
LEG6 = ["lf", "lm", "lh", "rf", "rm", "rh"]
POOLS = [("levators", ["Tr flexor MN", "Acc. tr flexor MN"]), ("depressors", ["Tr extensor MN", "Sternotrochanter MN"]),
         ("promotors", ["Tergopleural/Pleural promotor MN", "Sternal anterior rotator MN"]), ("remotors", ["Pleural remotor/abductor MN", "Sternal posterior rotator MN"]),
         ("Ti flexors", ["Ti flexor MN", "Acc. ti flexor MN"]), ("Ti extensors", ["Ti extensor MN"])]
lm = np.load("world/legmn.npz"); wb = np.load("brain_whole.npz", allow_pickle=True)["bodyId"].astype(np.int64)
LEG_OF = {}
for g, L in (("fl", "f"), ("ml", "m"), ("hl", "h")):
    for s in "LR":
        for i in lm[f"{g}_{s}"]: LEG_OF[int(wb[i])] = s.lower() + L
ANN = pd.read_feather("data/body-annotations-male-cns-v1.0-minconf-0.5.feather", columns=["bodyId", "somaSide", "somaNeuromere"])
ANN = {int(b): (str(s), str(n)) for b, s, n in zip(ANN.bodyId, ANN.somaSide, ANN.somaNeuromere)}
def soma_leg(b):
    s, n = ANN.get(int(b), ("", "")); return (s.lower() + {"T1": "f", "T2": "m", "T3": "h"}[n]) if (s in ("L", "R") and n in ("T1", "T2", "T3")) else None

def cycles(sw, t0):
    """swing onsets (rising edges of the mask at or after t0); returns the phase per ms (nan outside whole cycles) and the mean swing fraction."""
    on = np.flatnonzero(np.diff(sw.astype(np.int8)) == 1) + 1; on = on[on >= t0]; ph = np.full(len(sw), np.nan)
    for a, b in zip(on[:-1], on[1:]): ph[a:b] = (np.arange(a, b) - a) / (b - a)
    fr = np.nanmean(np.where(np.isnan(ph), np.nan, sw)) if len(on) > 1 else np.nan
    return ph, fr, len(on) - 1

def read(train, sw, ph, t0, rng, per_ms):
    """train: spikes per time bin (ms or 10 ms, summed over the pool's cells); returns rates, ratio, histogram, vs, mean phase, null95, n."""
    step = 1 if per_ms else 10; ctr = np.arange(len(train)) * step + (0 if per_ms else 5); ok = (ctr >= t0) & (ctr < len(sw))
    tr = train[ok].astype(float); c = ctr[ok]; s_ = sw[c].astype(bool); p_ = ph[c]
    t_sw = s_.sum() * step / 1000.0; t_st = (~s_).sum() * step / 1000.0
    r_sw = tr[s_].sum() / max(t_sw, 1e-9); r_st = tr[~s_].sum() / max(t_st, 1e-9)
    def vs(x):
        m = ~np.isnan(p_) & (x > 0); w = x[m]; z = (w * np.exp(2j * np.pi * p_[m])).sum() / max(w.sum(), 1e-9); return abs(z), (np.angle(z) / (2 * np.pi)) % 1.0, int(w.sum())
    v, mp, n = vs(tr); h = np.histogram(p_[~np.isnan(p_)], bins=8, range=(0, 1), weights=tr[~np.isnan(p_)])[0]
    L = len(tr); lo = max(1, 500 // step); null = [vs(np.roll(tr, int(rng.integers(lo, max(lo + 1, L - lo)))))[0] for _ in range(args.draws)]
    return dict(r_sw=r_sw, r_st=r_st, ratio=r_sw / r_st if r_st > 0 else (np.inf if r_sw > 0 else np.nan), hist=h / max(h.sum(), 1e-9), vs=v, mp=mp, n=n, null=float(np.percentile(null, 95)))

def verdict(r, frac):
    if r["n"] < args.min_spikes: return "too few", "-"
    return ("LOCKED" if r["vs"] > r["null"] else "no"), ("swing" if r["mp"] < frac else "stance")

ALL = {}
for run in args.runs:
    D = np.load(run + ".npz", allow_pickle=True); C = np.load(run + ".cells.npz", allow_pickle=True)
    assert "kin_swing" in D.files, f"{run}: not a --kin-drive run"
    a_ = str(D["args"]); SW = D["kin_swing"]; n_ms = len(SW); t0 = int(args.t0 * 1000); rng = np.random.default_rng(0)
    print(f"\nKIN-DRIVE | {run.split('/')[-1]}  ({n_ms / 1000:.0f} s; read {args.t0:g} s to the end; the imposed step from kin_swing)")
    for key in ("walk", "dn_playback", "loop", "claw_labels", "senses"):
        i = a_.find(f"'{key}': "); print(f"KIN-DRIVE |   {key}: {a_[i + len(key) + 4: a_.find(',', i)] if i >= 0 else '?'}")
    PH = {}; FR = {}
    for li, l in enumerate(LEG6):
        PH[l], FR[l], nc = cycles(SW[:, li], t0)
        per = np.diff(np.flatnonzero(np.diff(SW[t0:, li].astype(np.int8)) == 1)); print(f"KIN-DRIVE |   {l}: {nc} imposed cycles, period median {np.median(per):.0f} ms, swing fraction {FR[l]:.2f} (swing = phase 0 to {FR[l]:.2f})")
    hdr = f"KIN-DRIVE |   {'leg':3s} {'pool / cell':22s} {'n':>3s} {'spk':>6s} {'swing Hz':>8s} {'stance':>7s} {'ratio':>6s} {'VS':>5s} {'null95':>6s} {'locked':>7s} {'mean ph':>7s} {'fires in':>8s}  phase histogram (8 bins, % of spikes; 0 = swing onset)"
    print(hdr)
    FRM = C["frames"]; ty = C["type"].astype(str); bid = C["bodyId"].astype(np.int64); legc = np.array([LEG_OF.get(int(b), "") for b in bid])
    rows = []
    for l in LEG6:
        li = LEG6.index(l)
        for pname, T in POOLS:
            m = np.isin(ty, T) & (legc == l)
            if not m.any(): print(f"KIN-DRIVE |   {l:3s} {pname:22s}   0  (no cells)"); continue
            r = read(FRM[:, m].sum(1), SW[:, li], PH[l], t0, rng, per_ms=False); nc = int(m.sum())
            r["r_sw"] /= nc; r["r_st"] /= nc; lk, ph_ = verdict(r, FR[l]); rows.append((l, pname, lk, ph_, r["ratio"]))
            print(f"KIN-DRIVE |   {l:3s} {pname:22s} {nc:3d} {r['n']:6d} {r['r_sw']:8.2f} {r['r_st']:7.2f} {r['ratio']:6.2f} {r['vs']:5.2f} {r['null']:6.2f} {lk:>7s} {r['mp']:7.2f} {ph_:>8s}  " + " ".join(f"{x * 100:3.0f}" for x in r["hist"]))
    if "x_ms" in C.files:
        X = C["x_ms"]; xt = C["x_type"].astype(str); xb = C["x_bodyId"].astype(np.int64)
        print("KIN-DRIVE |   premotor cells (--log-x, 1 ms), each against its soma's leg (07B / 19B: bilateral, the soma's leg a convention)")
        for t in sorted(set(xt)):
            for j in np.flatnonzero(xt == t):
                l = soma_leg(xb[j])
                if l is None: print(f"KIN-DRIVE |   -   {t + ' ' + str(xb[j]):22s}  (soma not in T1-T3: no leg, left out)"); continue
                r = read(X[:, j], SW[:, LEG6.index(l)], PH[l], t0, rng, per_ms=True); lk, ph_ = verdict(r, FR[l]); rows.append((l, f"{t} {xb[j]}", lk, ph_, r["ratio"]))
                print(f"KIN-DRIVE |   {l:3s} {t + ' ' + str(xb[j]):22s} {1:3d} {r['n']:6d} {r['r_sw']:8.2f} {r['r_st']:7.2f} {r['ratio']:6.2f} {r['vs']:5.2f} {r['null']:6.2f} {lk:>7s} {r['mp']:7.2f} {ph_:>8s}  " + " ".join(f"{x * 100:3.0f}" for x in r["hist"]))
    ALL[run.split("/")[-1]] = {(a, b): (c, d, e) for a, b, c, d, e in rows}
    lk = [r_ for r_ in rows if r_[2] == "LOCKED"]
    print(f"KIN-DRIVE |   locked: {len(lk)} of {sum(r_[2] != 'too few' for r_ in rows)} rows with >= {args.min_spikes} spikes: " + ", ".join(f"{a} {b} ({c}, x{d:.2f})" for a, b, _, c, d in lk))
if len(ALL) > 1:   # the arms side by side: per row, L (locked) / . (not) / ~ (too few), the phase it fires in, the swing / stance ratio
    names = list(ALL); keys = [k for k in dict.fromkeys(k for n in names for k in ALL[n])]
    print("\nKIN-DRIVE | the arms side by side (L = locked above the null, . = not, ~ = < %d spikes; sw / st = mean phase in swing / stance; x = swing / stance rate)" % args.min_spikes)
    print("KIN-DRIVE |   " + f"{'leg':3s} {'pool / cell':22s} " + " ".join(f"{n[:16]:>16s}" for n in names))
    for k in keys:
        cells = []
        for n in names:
            c_ = ALL[n].get(k)
            cells.append("-" if c_ is None else "~" if c_[0] == "too few" else f"{'L' if c_[0] == 'LOCKED' else '.'} {c_[1][:2]} x{c_[2]:.2f}")
        print("KIN-DRIVE |   " + f"{k[0]:3s} {k[1]:22s} " + " ".join(f"{c:>16s}" for c in cells))
