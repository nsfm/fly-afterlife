"""gait_score.py - one line per run for a sweep: is there anything gait-shaped in the leg motor output?
reads <run>.cells.npz (per-frame counts of the leg MNs). columns:
  MN Hz      mean Hz per leg motor neuron after 2 s
  active     leg MNs above 1 Hz
  flex Hz    tibia flexors (Ti flexor + Acc. ti flexor), Hz per cell
  ext Hz     tibia extensors
  antag      the most negative antagonist correlation over legs and joints (30 ms smoothing; -1 = alternation)
  legs       the most negative inter-leg correlation at lag 0 (30 ms; tripod would be negative between neighbours)
  beat       population rhythm: the cross-spectrum between two random halves of a leg's cells (Welch 2.56 s windows, 10 splits),
             peak over 1-25 Hz divided by the band's median |cross-power|, best leg. a tonic cell is in one half only and makes no
             cross-power; a rhythm shared across cells does. (E) a first measure, not a standard one; ~1-3 is noise.
    uv run python experiments/gait_score.py <run>.npz [<run2>.npz ...]
"""
import sys, numpy as np
lm = np.load("world/legmn.npz"); _bid = np.load("brain_whole.npz", allow_pickle=True)["bodyId"]; segof = {}
for g in ("fl", "ml", "hl"):
    for s in "LR":
        for i in lm[f"{g}_{s}"]: segof[int(_bid[i])] = g
sm = lambda x, w: np.convolve(x, np.ones(w) / w, mode="same")
PAIRS = [(("Ti flexor", "Acc. ti flexor"), ("Ti extensor",)), (("Tr flexor", "Acc. tr flexor"), ("Sternotrochanter", "Tr extensor")), (("Sternal anterior rotator", "promotor"), ("Pleural remotor", "Sternal posterior rotator"))]
def has(ty, keys): return np.array([any(k in t for k in keys) for t in ty])
print(f"{'run':28s} {'MN Hz':>6s} {'active':>6s} {'flex Hz':>7s} {'ext Hz':>6s} {'antag':>6s} {'legs':>6s} {'beat':>6s}  beat leg/Hz")
rng = np.random.default_rng(0)
for f in sys.argv[1:]:
    C = np.load(f.replace(".npz", "") + ".cells.npz", allow_pickle=True); ty = C["type"].astype(str); side = C["side"].astype(str); X = C["frames"].astype(float)[200:]
    seg = np.array([segof.get(int(b), "?") for b in C["bodyId"]]); n = X.shape[0]; hz = X.mean(0) * 100
    flex = has(ty, ("Ti flexor", "Acc. ti flexor")); ext = has(ty, ("Ti extensor",))
    antag = 0.0; legs_ = 0.0; beat = 0.0; bl = "-"
    LEGS = [(g, s) for g in ("fl", "ml", "hl") for s in "LR"]; sig = {}
    for (g, s) in LEGS:
        m = (seg == g) & (side == s)
        for a, b in PAIRS:
            ma = m & has(ty, a); mb = m & has(ty, b)
            if ma.any() and mb.any():
                A = sm(X[:, ma].sum(1), 3); B = sm(X[:, mb].sum(1), 3)
                if A.std() > 0 and B.std() > 0: antag = min(antag, np.corrcoef(A, B)[0, 1])
        x = X[:, m].sum(1); sig[(g, s)] = sm(x, 3) - sm(x, 50)
        if x.sum() > 20 and m.sum() >= 4:
            # population rhythm: the cross-spectrum between two random halves of the leg's cells (Welch, 2.56 s windows), averaged over
            # 10 splits; a cell's own regular firing is in one half only and makes no cross-power; a rhythm shared across cells does.
            cells_ = np.flatnonzero(m); W = 256; nw = n // W; cs = 0
            for _ in range(10):
                p_ = rng.permutation(cells_); h1, h2 = p_[: len(p_) // 2], p_[len(p_) // 2:]
                A = X[: nw * W, h1].sum(1).reshape(nw, W); B = X[: nw * W, h2].sum(1).reshape(nw, W); A = A - A.mean(1, keepdims=True); B = B - B.mean(1, keepdims=True)
                FA = np.fft.rfft(A * np.hanning(W), axis=1); FB = np.fft.rfft(B * np.hanning(W), axis=1); cs = cs + (np.conj(FA) * FB).mean(0).real / 10
            fr = np.fft.rfftfreq(W, 0.01); mm = (fr >= 1) & (fr <= 25); c = cs[mm]; c = np.maximum(c, 0); r = c / max(np.median(np.abs(cs[mm])), 1e-12); j = int(np.argmax(r))
            if r[j] > beat: beat = r[j]; bl = f"{s}{['fl', 'ml', 'hl'].index(g) + 1}/{fr[mm][j]:.1f}"
    for a in LEGS:
        for b in LEGS:
            if a < b and sig[a].std() > 0 and sig[b].std() > 0: legs_ = min(legs_, np.corrcoef(sig[a], sig[b])[0, 1])
    name = f.split("/")[-1].replace(".npz", "")
    print(f"{name:28s} {hz.mean():6.2f} {int((hz > 1).sum()):6d} {hz[flex].mean():7.2f} {hz[ext].mean():6.1f} {antag:+6.2f} {legs_:+6.2f} {beat:6.1f}  {bl}")
