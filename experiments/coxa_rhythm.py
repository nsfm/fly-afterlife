"""coxa_rhythm.py - the within-leg rhythm, scored the way the field's result has it (Pugliese 2026: coxa promotor vs remotor at 7-15 Hz;
the review of 09-22): per leg, the promotor pool (Tergopleural/Pleural promotor + Sternal anterior rotator) against the remotor pool
(Pleural remotor/abductor + Sternal posterior rotator), from a <run>.cells.npz with per-frame counts (10 ms):
  - the cross-correlation between the two pools over lags -150..+150 ms: a within-leg rhythm at f Hz puts the antiphase trough near 500/f ms
    and a positive peak near 1000/f ms;
  - each pool's autocorrelation at 30 / 70 / 140 ms and the first lag at which it goes below -0.1 (a rhythm has a negative lobe; a tonic
    cell does not);
  - the spectrum of each pool (1-40 Hz), the peak and its ratio to the band median, and the same for a phase-shuffled null (each cell rolled
    by a random offset: a tonic cell keeps its line, a shared rhythm loses it).
    uv run python experiments/coxa_rhythm.py <run>.npz [...]
"""
import sys, numpy as np
lm = np.load("world/legmn.npz"); _bid = np.load("brain_whole.npz", allow_pickle=True)["bodyId"]; legof = {}
for g, L in (("fl", "f"), ("ml", "m"), ("hl", "h")):
    for s in "LR":
        for i in lm[f"{g}_{s}"]: legof[int(_bid[i])] = s.lower() + L
PRO = ("Tergopleural/Pleural promotor MN", "Sternal anterior rotator MN"); REM = ("Pleural remotor/abductor MN", "Sternal posterior rotator MN")
LEG6 = ["lf", "lm", "lh", "rf", "rm", "rh"]; rng = np.random.default_rng(0)
def spec(x):
    y = x - x.mean(); F = np.abs(np.fft.rfft(y * np.hanning(len(y)))) ** 2; fr = np.fft.rfftfreq(len(y), 0.01); m = (fr >= 1) & (fr <= 40); return fr[m], F[m]
for f in sys.argv[1:]:
    C = np.load(f.replace(".npz", "") + ".cells.npz", allow_pickle=True); ty = C["type"].astype(str); X = C["frames"].astype(float)[200:]; leg = np.array([legof.get(int(b), "") for b in C["bodyId"]]); n = X.shape[0]
    print(f"\n{f.split('/')[-1]}: {n / 100:.0f} s after the warm-up")
    print(f"  {'leg':4s} {'pro Hz':>7s} {'rem Hz':>7s} {'xcorr min (lag ms)':>19s} {'xcorr max (lag)':>16s} {'pro autocorr 30/70/140':>24s} {'lobe':>6s} {'pro peak Hz (x med / null x med)':>32s}")
    for l in LEG6:
        mp = (leg == l) & np.isin(ty, PRO); mr = (leg == l) & np.isin(ty, REM)
        if not (mp.any() and mr.any()): continue
        p = X[:, mp].sum(1); r = X[:, mr].sum(1); hp, hr = X[:, mp].mean() * 100, X[:, mr].mean() * 100
        yp = p - p.mean(); yr = r - r.mean()
        if yp.std() == 0 or yr.std() == 0: print(f"  {l:4s} {hp:7.2f} {hr:7.2f}  (flat)"); continue
        lags = np.arange(-15, 16); cc = np.array([np.corrcoef(yp[max(0, -L):n - max(0, L)], yr[max(0, L):n - max(0, -L)])[0, 1] for L in lags])
        ac = np.correlate(yp, yp, mode="full")[n - 1:n + 20] / (yp @ yp); neg = np.flatnonzero(ac[1:] < -0.1)
        fr, F = spec(p); pk = int(np.argmax(F)); null = np.zeros_like(F)
        for _ in range(5):
            Xs = X[:, mp].copy()
            for j in range(Xs.shape[1]): Xs[:, j] = np.roll(Xs[:, j], int(rng.integers(0, n)))
            null += spec(Xs.sum(1))[1] / 5
        print(f"  {l:4s} {hp:7.2f} {hr:7.2f} {cc.min():+8.2f} ({lags[np.argmin(cc)] * 10:+4d})    {cc.max():+6.2f} ({lags[np.argmax(cc)] * 10:+4d})   {np.round(ac[[3, 7, 14]], 2)}   {str(neg[0] * 10 + 10) + ' ms' if len(neg) else '-':>6s}   {fr[pk]:5.1f} (x{F[pk] / max(np.median(F), 1e-12):.1f} / x{null[pk] / max(np.median(null), 1e-12):.1f})")
