"""leg_pairs.py <run> [<run> ...]: the coupling between legs on the body (09-23, campaign item 7: the 19B -> 19A sweep). one block per run
(a body_loop.py --out prefix: <run>.npz and <run>.cells.npz), then one summary table.

    uv run python experiments/leg_pairs.py world/body/loop/i7_x1_s11 world/body/loop/i7_x10_s11 ...

definitions (every number below is a choice of this reader, the same for every run):
- the standing line: the mean after the warm-up (2.0 s) of the feet (tarsal_force summed: tarsus1-5, net of the pads), the other leg segments
  (other_leg_force summed) and the body (body_force), uN; as body_loop.py prints it.
- rates: x_ms (the --log-x cells at 1 ms), Hz per cell by type, after 2.0 s. absent types print nan.
- a lift: the leg's tarsal_force smoothed over 21 ms (boxcar, 'same') at or under 0.05 uN for >= 50 ms, the run starting at or after 2.1 s.
- in-bout: onset-to-onset intervals of <= 400 ms (twice the five-hertz gap); the gap is their median, with their cv.
- per pair (lm-rm, lf-rf; B = the right leg, A = the left):
  xc   the onset trains binned at 10 ms from 2.1 s, Pearson r over lags -500..+500 ms (B shifted by +lag): r at 0 and the largest |r| with its lag;
       null95 = the 95th percentile of the largest |r| over the same lags with B circularly rolled by >= 1 s (200 rolls, rng 0). coupling at a
       lag reads as |r| above null95.
  off  the fraction of ms (from 2.1 s) with both feet off (smoothed force <= 0.05) against the product of the two singles (independence);
       ratio = seen / independent (1 = independent, < 1 = the legs avoid each other, > 1 = they co-lift).
  ph   B's onsets that fall inside an in-bout cycle of A (between two A onsets <= 400 ms apart), phase = (b - a_i) / (a_i+1 - a_i), counted
       in quarters; and A's onsets in B's cycles the same way; anti = the middle two quarters' share of both counts pooled (0.5 uniform;
       antiphase > 0.5), with a two-sided binomial p against 0.5 (the two directions are not independent draws: read p as a guide).
  xc is not computed (nan) when either leg has fewer than 5 lifts: with one or two onsets the largest |r| and its null are the same number.
- the promotor / remotor pools, left against right per segment, from the motor-neuron log (frames, 10 ms, from 2.1 s): summed spikes of
  the pool per 10 ms; pro = Tergopleural/Pleural promotor + Sternal anterior rotator (+ MNhl62 on the hind legs), rem = Pleural
  remotor/abductor + Sternal posterior rotator (+ MNhl29 on the hind legs), as body_loop.py's --hind-map v2 maps them. printed: r at lag 0
  of L-pro / R-pro, L-rem / R-rem, L-pro / R-rem (alternation would make the first two negative at 0 and the third positive), and the most
  negative r of L-pro / R-pro over +-500 ms with its lag. pools with no spikes print nan.
"""
import sys, os, ast, math, numpy as np

LEG6 = ["lf", "lm", "lh", "rf", "rm", "rh"]; T0 = 2100; WARM = 2000; INB = 400; LAGS = 50; MINL = 5
PRO = ("Tergopleural/Pleural promotor MN", "Sternal anterior rotator MN"); REM = ("Pleural remotor/abductor MN", "Sternal posterior rotator MN")
RATE_TYPES = ["AN19B009", "IN19B005", "IN19A011", "IN19A012", "IN19A001", "IN19A016", "IN19B003", "IN17A001", "IN09A002", "IN13A002"]

def runs(mask):
    d = np.diff(np.concatenate([[0], mask.astype(np.int8), [0]])); return list(zip(np.flatnonzero(d == 1), np.flatnonzero(d == -1)))

def lifts(ft):
    sm = np.convolve(ft, np.ones(21) / 21, "same"); off = sm <= 0.05
    on = np.array([a for a, b in runs(off) if b - a >= 50 and a >= T0], np.int64); return on, off

def inbout(on):
    ii = np.diff(on); ii = ii[ii <= INB]; return ii

def xcorr(x, y, lags=LAGS):
    x = x - x.mean(); y = y - y.mean(); n = len(x); sx = np.sqrt((x * x).sum()); sy = np.sqrt((y * y).sum())
    if sx == 0 or sy == 0: return np.full(2 * lags + 1, np.nan)
    return np.array([(x[max(0, -k):n - max(0, k)] * y[max(0, k):n - max(0, -k)]).sum() / (sx * sy) for k in range(-lags, lags + 1)])   # y shifted by +k bins

def train(on, n):
    t = np.zeros(n); b = (on - T0) // 10; t[b[(b >= 0) & (b < n)]] = 1; return t

def binom_p(k, n):   # two-sided exact against 0.5
    if n == 0: return float("nan")
    pk = [math.comb(n, i) / 2 ** n for i in range(n + 1)]; return min(1.0, sum(p for p in pk if p <= pk[k] + 1e-12))

def pair(A_on, B_on, A_off, B_off, n_ms):
    nb = (n_ms - T0) // 10; a = train(A_on, nb); b = train(B_on, nb); r = xcorr(a, b); lag = np.arange(-LAGS, LAGS + 1) * 10
    if np.isnan(r).all(): r0 = rmax = lmax = null = float("nan")
    else:
        r0 = r[LAGS]; k = int(np.nanargmax(np.abs(r))); rmax = r[k]; lmax = lag[k]; rng = np.random.default_rng(0)
        null = np.percentile([np.nanmax(np.abs(xcorr(a, np.roll(b, int(rng.integers(100, nb - 100)))))) for _ in range(200)], 95) if nb > 300 else float("nan")
    ao = A_off[T0:]; bo = B_off[T0:]; both = float((ao & bo).mean()); ind = float(ao.mean() * bo.mean())
    def quarters(X, Y):   # Y's onsets in X's in-bout cycles
        q = np.zeros(4, int)
        for i in range(len(X) - 1):
            a0, a1 = X[i], X[i + 1]
            if a1 - a0 > INB: continue
            for bb in Y[(Y >= a0) & (Y < a1)]: q[min(3, int(4 * (bb - a0) / (a1 - a0)))] += 1
        return q
    qBA = quarters(A_on, B_on); qAB = quarters(B_on, A_on); q = qBA + qAB; n = int(q.sum()); anti = (q[1] + q[2]) / n if n else float("nan")
    few = min(len(A_on), len(B_on)) < MINL
    if few: r0 = rmax = lmax = null = float("nan")
    return dict(r0=r0, rmax=rmax, lmax=lmax, null=null, both=both, ind=ind, ratio=both / ind if ind > 0 else float("nan"), qBA=qBA, qAB=qAB, q=q, n=n, anti=anti, p=binom_p(int(q[1] + q[2]), n), few=few)

def leg_of_mn(bid):
    lm = np.load("world/legmn.npz"); wb = np.load("brain_whole.npz", allow_pickle=True)["bodyId"].astype(np.int64); out = {}
    for g, L in (("fl", "f"), ("ml", "m"), ("hl", "h")):
        for s in "LR":
            if f"{g}_{s}" in lm.files:
                for i in lm[f"{g}_{s}"]: out[int(wb[i])] = s.lower() + L
    return np.array([out.get(int(b), "") for b in bid])

def pools(C):
    fr = C["frames"].astype(float)[T0 // 10:]; ty = C["type"].astype(str); lg = leg_of_mn(C["bodyId"].astype(np.int64)); res = {}
    for seg in "fmh":
        P = {}; N = {}
        for s in "lr":
            for k, T in (("pro", PRO + (("MNhl62",) if seg == "h" else ())), ("rem", REM + (("MNhl29",) if seg == "h" else ()))):
                m = (lg == s + seg) & np.isin(ty, T); P[s + k] = fr[:, m].sum(1); N[s + k] = max(1, int(m.sum()))
        pp = xcorr(P["lpro"], P["rpro"]); rr = xcorr(P["lrem"], P["rrem"]); pr = xcorr(P["lpro"], P["rrem"])
        k = int(np.nanargmin(pp)) if not np.isnan(pp).all() else LAGS
        res[seg] = dict(pp=pp[LAGS], rr=rr[LAGS], pr=pr[LAGS], ppmin=pp[k], ppmin_lag=(k - LAGS) * 10, hz=[P[x].mean() * 100 / N[x] for x in ("lpro", "rpro", "lrem", "rrem")])
    return res

def arm_label(D):
    try: a = ast.literal_eval(str(D["args"]))
    except Exception: return "?"
    cmd = f"playback {os.path.basename(a['dn_playback'])}" if a.get("dn_playback") else f"{a.get('walk_dn', 'DNg100')} {a.get('walk', 0):g}"
    es = a.get("edge_scale") or ""; es = ("edge x" + es.rsplit(":", 1)[1]) if es else "edge x1"; dr = a.get("drive") or ""
    return f"seed {a.get('seed')}, {cmd}, {es}" + (f", drive {dr}" if dr else "")

def read(f):
    D = np.load(f + ".npz", allow_pickle=True); C = np.load(f + ".cells.npz", allow_pickle=True); FT = D["tarsal_force"]; n_ms = len(FT)
    st = (float(FT[WARM:].sum(1).mean()), float(np.nanmean(D["other_leg_force"][WARM:].sum(1))), float(np.nanmean(D["body_force"][WARM:])))
    L = {leg: lifts(FT[:, i]) for i, leg in enumerate(LEG6)}
    rates = {}
    if "x_ms" in C.files:
        X = C["x_ms"][WARM:n_ms].astype(float); xt = C["x_type"].astype(str)
        for t in RATE_TYPES:
            m = xt == t; rates[t] = X[:, m].mean() * 1000 if m.any() else float("nan")
    R = dict(name=os.path.basename(f), label=arm_label(D), stand=st, rates=rates, lifts={}, pairs={}, pools=pools(C))
    for leg in LEG6:
        on, off = L[leg]; ii = inbout(on); R["lifts"][leg] = (len(on), float(np.median(ii)) if len(ii) else float("nan"), float(ii.std() / ii.mean()) if len(ii) > 2 else float("nan"), float(off[T0:].mean()))
    for A, B in (("lm", "rm"), ("lf", "rf")): R["pairs"][A + "-" + B] = pair(L[A][0], L[B][0], L[A][1], L[B][1], n_ms)
    return R

def show(R):
    s = R["stand"]; print(f"\n== {R['name']}  ({R['label']})")
    print(f"  standing: feet {s[0]:.2f} / other {s[1]:.2f} / body {s[2]:.2f} uN")
    if R["rates"]: print("  rates Hz/cell: " + ", ".join(f"{t} {v:.1f}" for t, v in R["rates"].items()))
    print("  lifts (n / in-bout gap ms / cv / time off): " + " | ".join(f"{l} {n}" + (f" / {g:.0f} / {c:.2f}" if n > 2 and not np.isnan(g) else "") + f" / {o * 100:.0f}%" for l, (n, g, c, o) in R["lifts"].items()))
    for k, p in R["pairs"].items():
        print(f"  {k}: xc r0 {p['r0']:+.3f}, max {p['rmax']:+.3f} at {p['lmax']:+.0f} ms (null95 {p['null']:.3f}); both off {p['both'] * 100:.1f} % vs indep {p['ind'] * 100:.1f} % (x{p['ratio']:.2f}); "
              f"phase quarters B in A {'/'.join(map(str, p['qBA']))}, A in B {'/'.join(map(str, p['qAB']))}, anti {p['anti']:.2f} of {p['n']} (p {p['p']:.2f})")
    for seg, v in R["pools"].items():
        print(f"  pools {seg}: Hz/cell L-pro {v['hz'][0]:.1f} R-pro {v['hz'][1]:.1f} L-rem {v['hz'][2]:.1f} R-rem {v['hz'][3]:.1f}; r0 pro-pro {v['pp']:+.3f}, rem-rem {v['rr']:+.3f}, Lpro-Rrem {v['pr']:+.3f}; "
              f"pro-pro min {v['ppmin']:+.3f} at {v['ppmin_lag']:+.0f} ms")

if __name__ == "__main__":
    out = [read(f.replace(".cells.npz", "").replace(".npz", "")) for f in sys.argv[1:]]
    for R in out: show(R)
    print("\nsummary: run | feet/other/body | AN19B009 IN19B005 IN19A011 IN19A012 Hz | lifts lf lm lh rf rm rh | lm-rm: xc max@lag (null95), both-off seen/indep, anti/n (p) | lf-rf: same | pro-pro r0 f m h")
    for R in out:
        s = R["stand"]; r = R["rates"]; P = R["pairs"]
        f = lambda p: f"{p['rmax']:+.2f}@{p['lmax']:+.0f} ({p['null']:.2f}), {p['both'] * 100:.1f}/{p['ind'] * 100:.1f}, {p['anti']:.2f}/{p['n']} ({p['p']:.2f})"
        print(f"{R['name']:18s} | {s[0]:.2f}/{s[1]:.2f}/{s[2]:.2f} | " + " ".join(f"{r.get(t, float('nan')):.1f}" for t in RATE_TYPES[:4]) + " | " + " ".join(str(R['lifts'][l][0]) for l in LEG6)
              + f" | {f(P['lm-rm'])} | {f(P['lf-rf'])} | " + " ".join(f"{R['pools'][g]['pp']:+.2f}" for g in "fmh"))
