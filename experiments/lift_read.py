"""lift_read.py <run> [...]: the movement senses on the body's own lifts. lift onsets from the left front foot's net force (F_net <= 0.05 for >= 50 ms,
after >= 100 ms on the ground); lift-triggered averages of the logged types (x_ms, 1 ms) and of the lf motor pools from -300 to +400 ms;
inter-lift intervals against a Poisson null (cv, serial correlation); which cells LEAD the lift (rate change in the 100 ms before onset vs baseline)."""
import sys, numpy as np
lm = np.load("world/legmn.npz"); wb = np.load("brain_whole.npz", allow_pickle=True)["bodyId"].astype(np.int64)
lf_ids = set(int(wb[i]) for k in lm.files if k.startswith("fl_L") for i in lm[k]) if any(k.startswith("fl_L") for k in lm.files) else set()
def runs(mask):
    out = []; i = 0; n = len(mask)
    while i < n:
        if mask[i]:
            j = i
            while j < n and mask[j]: j += 1
            out.append((i, j)); i = j
        else: i += 1
    return out
for f in sys.argv[1:]:
    D = np.load(f + ".npz", allow_pickle=True); C = np.load(f + ".cells.npz", allow_pickle=True)
    FL = D["leg_force"]; n_ms = len(FL); Fnet = np.convolve(FL[:, 0], np.ones(21) / 21, "same")   # lf, per ms, smoothed over 21 ms (the contact flickers)
    off = Fnet <= 0.05; on = ~off
    lifts = [(a, b) for a, b in runs(off) if b - a >= 50 and a >= 2100]
    onsets = np.array([a for a, b in lifts]); durs = np.array([b - a for a, b in lifts])
    print(f"\n{f.split('/')[-1]}: {len(lifts)} lifts of the left front foot (>= 50 ms off the ground after >= 100 ms on it), duration median {np.median(durs) if len(durs) else 0:.0f} ms")
    if len(onsets) > 3:
        ii = np.diff(onsets); cv = ii.std() / ii.mean(); sc = np.corrcoef(ii[:-1], ii[1:])[0, 1] if len(ii) > 3 else np.nan
        print(f"  inter-lift intervals: mean {ii.mean():.0f} ms, median {np.median(ii):.0f}, cv {cv:.2f} (Poisson 1.0, clock 0), serial correlation {sc:+.2f}; shortest {ii.min()} ms")
    if "x_ms" not in C.files or len(onsets) < 3: continue
    X = C["x_ms"].astype(float); xt = C["x_type"].astype(str); win = np.arange(-300, 401)
    base = X[2000:].mean(0) * 1000
    print(f"  {'type':10s} {'base Hz':>8s} {'-100..0':>8s} {'0..100':>8s} {'100..300':>9s}  lead? (pre/base)")
    rows = []
    for t in sorted(set(xt)):
        m = xt == t; segs = np.array([X[o - 300:o + 401][:, m].sum(1) for o in onsets if o + 401 <= n_ms]); tr = segs.mean(0) * 1000 / m.sum()
        pre = tr[200:300].mean(); post = tr[300:400].mean(); late = tr[400:600].mean(); b0 = base[m].mean()
        rows.append((pre / max(b0, 0.05), t, b0, pre, post, late))
    for ratio, t, b0, pre, post, late in sorted(rows, reverse=True): print(f"  {t:10s} {b0:8.1f} {pre:8.1f} {post:8.1f} {late:9.1f}  {ratio:5.2f}")
    fr = C["frames"].astype(float); ty = C["type"].astype(str); bid = C["bodyId"].astype(np.int64); lf = np.array([int(b) in lf_ids for b in bid])
    for name, T in (("lf Ti flexor", ["Ti flexor MN"]), ("lf Ti extensor", ["Ti extensor MN"]), ("lf promotor", ["Tergopleural/Pleural promotor MN", "Sternal anterior rotator MN"]), ("lf remotor", ["Pleural remotor/abductor MN", "Sternal posterior rotator MN"]), ("lf Tr flexor", ["Tr flexor MN"]), ("lf Tr extensor", ["Tr extensor MN"])):
        m = np.isin(ty, T) & (lf if lf.any() else True)
        if not m.any(): continue
        segs = np.array([fr[(o - 300) // 10:(o + 400) // 10][:, m].sum(1) for o in onsets if o + 401 <= n_ms]); tr = segs.mean(0) * 100 / m.sum(); b0 = fr[200:][:, m].mean() * 100
        print(f"  {name:14s} base {b0:5.1f} Hz | -300..-100 {tr[0:20].mean():5.1f} | -100..0 {tr[20:30].mean():5.1f} | 0..100 {tr[30:40].mean():5.1f} | 100..300 {tr[40:60].mean():5.1f}")
