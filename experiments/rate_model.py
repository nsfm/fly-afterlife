"""rate_model.py - the positive control: Pugliese et al. 2026's rate model of the fly cord, run on THIS project's wiring (brain_cord.npz).

one question: does their model oscillate on our wiring file? if it does, the wiring is cleared and our spiking engine is the variable; if it
does not, the difference is in our cut or our signs.

source: Pugliese SM, Chou GM, Abe ETT, Turcu D, Lancaster JK, Tuthill JC, Brunton BW, "Connectome simulations identify a central pattern
generator circuit for fly walking", bioRxiv 10.1101/2025.09.12.675944 v2 (2026-04-30), PMC13142387, Methods (read 2026-09-22). our notes:
docs/research/sources/pugliese_2026_connectome_cpg.md, docs/physiology/walking_review.md §0 and §7. results: docs/physiology/rate_model_control.md.

the equation (Methods, verbatim form):

    tau_i dr_i/dt = max( r_max,i tanh( a_i ( r_max,i I_i(t) + b sum_j w_ij r_j(t) - theta_i ) ), 0 ) - r_i(t)

every parameter and where it comes from:
    b        0.03 per synapse, same for all cells                                     Methods ("b = 0.03 throughout most analyses";
             "increasing bACh to 0.045 still produced viable oscillatory dynamics, but larger deviations resulted in either runaway network
             activity or insufficient neuron recruitment"). --b-inh sets a separate inhibitory b (sensitivity, not in the paper's default).
    w_ij     synapse count j -> i (edges with >= 5 synapses; brain_cord.npz 'w'),     Methods (5-synapse floor; ACh +, GABA/Glu -)
             times sign of presynaptic j: +1 ACh, -1 GABA / glutamate (and the 6 histamine cells, as the project file has them);
             0 for 'unclear' / octopamine / serotonin (1,014 cells: their outputs are dropped; Pugliese sign only ACh/GABA/Glu)
    tau      ~ N(0.020, 0.002) s                                                      Methods
    r_max    ~ N(200, 10) Hz                                                          Methods
    theta*   ~ N(7.5, 0.6)                                                            Methods
    a*       ~ N(1, 0.1)                                                              Methods
             all four truncated at zero (we clip at 1e-3 of the mean), redrawn per cell per replicate (--seed)
    size     "a_i* was divided by the median-normalized size of each neuron i"; "theta_i* was multiplied by the median-normalized size"
             (Methods): a_i = a*_i / s_i, theta_i = theta*_i s_i, s_i = size_i / median(size over the simulated cells).
             Pugliese used volume (MANC, mCNS) or surface area (FANC, BANC). OUR FILE HAS NO VOLUME. substitution, stated:
               --size insyn : size = the cell's total INPUT synapse count, taken from brain_whole.npz (so a descending neuron keeps
                              the brain inputs the headless cut removed: its size does not change with the cut)
               --size total : input + output synapse count (brain_whole.npz)
               --size none  : a = a*, theta = theta* (their own negative control: "without adjusting a and theta for size, the network
                              does not produce robust oscillations in response to DNg100 input even when this input is adjusted down")
             a cell with size 0 is floored at 1 synapse before normalising. --size-power p uses proxy ** p (sensitivity only).
    I        tonic input to DNg100 from t = 20 ms (Methods: onset 20 ms), --dn-input. Methods: "Istim = 250 in MANC, 150 in FANC,
             and 400 in the two CNS datasets" (MaleCNS is ours: 400 is the matched value). NOTE: as the equation is written the input
             enters as r_max * I, so any I above ~0.1 saturates DNg100 at r_max; the paper also says frequency rises with the input.
             we therefore sweep I over decades (0.01 .. 400) rather than trust one value. --dn-side L|R|both (screen: one DNg100;
             interleg tests: both).
    r(0)     0 (Methods: "the simulation begins as a quiescent network")
    solver   Pugliese: Dopri5 adaptive (rtol 2e-6). here: Heun (RK2) at fixed dt (--dt, default 0.5 ms = tau/40).
    network  --subnet front: the paper's construction: all front-leg MNs (world/legmn.npz fl_L + fl_R), every non-DN cell with a synapse
             onto one of them ("premotor"), every DN with a synapse onto a premotor cell or a front MN.
             --subnet all: the whole cord file (23,074 cells).

readout (after --skip, default 0.5 s, so the onset transient does not pose as a slow rhythm; the paper recruits MNs after 0.25 s):
    per leg, the promotor pool (Tergopleural/Pleural promotor MN + Sternal anterior rotator MN) and the remotor pool (Pleural
    remotor/abductor MN + Sternal posterior rotator MN), summed rate: its modulation depth (sd / mean: the spectral ratio is scale-free, so a
    flat pool with a 0.1 Hz wobble can post a large ratio; the depth says whether there is a rhythm to speak of); the spectrum's peak in 5-20 Hz and its ratio to the 1-40 Hz band
    median; the promotor-remotor cross-correlation extremum over +-150 ms and its lag; an autocorrelation rhythmicity score in the spirit of
    the paper's (per active MN, the height of the first autocorrelation peak with prominence >= 0.05; 0 if none; averaged over active MNs:
    the paper's exact formula is not given in the text we read, this is our approximation); the mean rate of the named rhythm cells.

    uv run python experiments/rate_model.py --size insyn --dn-input 400 --subnet front --seconds 5 --seed 0
"""
import argparse, time, numpy as np, scipy.sparse as sp
from scipy.signal import find_peaks

PRO = ("Tergopleural/Pleural promotor MN", "Sternal anterior rotator MN")
REM = ("Pleural remotor/abductor MN", "Sternal posterior rotator MN")
NAMED = ("DNg100", "IN17A001", "INXXX466", "IN16B036", "IN19A007", "IN09A002")


def load(subnet, size_mode, size_power=1.0):
    C = np.load("brain_cord.npz", allow_pickle=True)
    B = np.load("brain_whole.npz", allow_pickle=True)
    lm = np.load("world/legmn.npz")
    bid, ty, sc, side = C["bodyId"], C["type"].astype(str), C["sc"].astype(str), C["side"].astype(str)
    sign = C["sign"].astype(np.float64)
    pre, post, w = C["pre"], C["post"], C["w"].astype(np.float64)
    n = len(bid)
    legof = np.array([""] * n, dtype=object)
    pos = {int(b): i for i, b in enumerate(bid)}
    for g, L in (("fl", "f"), ("ml", "m"), ("hl", "h")):
        for s in "LR":
            for b in B["bodyId"][lm[f"{g}_{s}"]]:
                if int(b) in pos: legof[pos[int(b)]] = s.lower() + L
    isdn = np.char.startswith(sc, "descending")
    if subnet == "front":
        mn = np.isin(legof, ["lf", "rf"])
        into_mn = mn[post]
        prem = np.zeros(n, bool); prem[pre[into_mn]] = True; prem &= ~isdn & ~mn
        tgt = prem | mn
        dn = np.zeros(n, bool); dn[pre[tgt[post]]] = True; dn &= isdn
        keep = mn | prem | dn
    else:
        keep = np.ones(n, bool)
    idx = np.flatnonzero(keep); new = -np.ones(n, np.int64); new[idx] = np.arange(len(idx))
    em = keep[pre] & keep[post]
    W = sp.csr_matrix((w[em] * sign[pre[em]], (new[post[em]], new[pre[em]])), shape=(len(idx), len(idx)))
    W.sum_duplicates()
    # size from brain_whole (cut-independent)
    wb = B["w"].astype(np.float64); nb = len(B["bodyId"])
    insyn = np.bincount(B["post"], wb, nb); outsyn = np.bincount(B["pre"], wb, nb)
    bpos = {int(b): i for i, b in enumerate(B["bodyId"])}
    bi = np.array([bpos[int(b)] for b in bid[idx]])
    if size_mode == "none": size = np.ones(len(idx))
    elif size_mode == "insyn": size = insyn[bi]
    else: size = insyn[bi] + outsyn[bi]
    size = np.maximum(size, 1.0) ** size_power; size = size / np.median(size)
    info = dict(n=len(idx), nnz=W.nnz, n_mn=int(keep[np.isin(legof, ["lf", "rf"])].sum()) if subnet == "front" else int((legof != "").sum()),
                n_dn=int(dn.sum()) if subnet == "front" else int(isdn.sum()), n_prem=int(prem.sum()) if subnet == "front" else -1)
    return W, size, ty[idx], side[idx], legof[idx], info


def simulate(W, size, ty, side, T, dt, I, dn_side, seed, b=0.03, rec_idx=None, b_inh=None):
    rng = np.random.default_rng(seed); n = W.shape[0]
    tn = lambda m, s: np.maximum(rng.normal(m, s, n), 1e-3 * m)
    tau, rmax, th0, a0 = tn(0.020, 0.002), tn(200, 10), tn(7.5, 0.6), tn(1, 0.1)
    a = a0 / size; th = th0 * size
    inp = np.zeros(n); dng = (ty == "DNg100") & ((side == dn_side) if dn_side in "LR" else True)
    inp[dng] = I
    Wb = W.tocsr().copy(); Wb.data = np.where(Wb.data > 0, b, b if b_inh is None else b_inh) * Wb.data
    nstep = int(round(T / dt)); on = int(round(0.020 / dt)); every = max(1, int(round(0.001 / dt)))
    rec = np.zeros((nstep // every + 1, len(rec_idx)), np.float32)
    r = np.zeros(n); act_max = np.zeros(n)
    def f(r, drive):
        return (np.maximum(rmax * np.tanh(a * (rmax * drive + Wb @ r - th)), 0) - r) / tau
    k = 0
    for s in range(nstep):
        drive = inp if s >= on else 0 * inp
        k1 = f(r, drive); k2 = f(r + dt * k1, drive); r = r + 0.5 * dt * (k1 + k2)
        if s % every == 0:
            rec[k] = r[rec_idx]; k += 1
            if s * dt >= 0.25: np.maximum(act_max, r, out=act_max)
    return rec[:k], act_max


def spectrum(x, fs=1000.0):
    y = x - x.mean(); F = np.abs(np.fft.rfft(y * np.hanning(len(y)))) ** 2; fr = np.fft.rfftfreq(len(y), 1 / fs)
    band = (fr >= 1) & (fr <= 40); pk = (fr >= 5) & (fr <= 20)
    if y.std() < 1e-9: return np.nan, 0.0
    j = np.flatnonzero(pk)[np.argmax(F[pk])]
    return fr[j], F[j] / max(np.median(F[band]), 1e-30)


def peak_1_40(x, fs=1000.0):
    """the global spectral peak in 1-40 Hz and its ratio to the band median (a 5-20 Hz 'peak' sitting at 5 Hz under a 1/f slope is not a rhythm)."""
    y = x - x.mean()
    if y.std() < 1.0: return np.nan, 0.0
    F = np.abs(np.fft.rfft(y * np.hanning(len(y)))) ** 2; fr = np.fft.rfftfreq(len(y), 1 / fs); band = (fr >= 1) & (fr <= 40)
    j = np.flatnonzero(band)[np.argmax(F[band])]; return fr[j], F[j] / max(np.median(F[band]), 1e-30)


def xcorr(p, r, maxlag=150):
    yp, yr = p - p.mean(), r - r.mean(); n = len(yp)
    if yp.std() < 1e-9 or yr.std() < 1e-9: return np.nan, 0, np.nan, 0
    lags = np.arange(-maxlag, maxlag + 1)
    cc = np.array([np.corrcoef(yp[max(0, -L):n - max(0, L)], yr[max(0, L):n - max(0, -L)])[0, 1] for L in lags])
    return cc.min(), int(lags[np.argmin(cc)]), cc.max(), int(lags[np.argmax(cc)])


def ac_score(x):
    y = x - x.mean()
    if y.std() < 1.0: return 0.0          # < 1 Hz of modulation: not counted as rhythmic
    ac = np.correlate(y, y, "full")[len(y) - 1:len(y) + 300] / (y @ y)
    pk, pr = find_peaks(ac, prominence=0.05)
    return float(ac[pk[0]]) if len(pk) else 0.0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--size", choices=["none", "insyn", "total"], default="insyn")
    ap.add_argument("--dn-input", type=float, default=400.0)
    ap.add_argument("--dn-side", choices=["L", "R", "both"], default="both")
    ap.add_argument("--subnet", choices=["front", "all"], default="front")
    ap.add_argument("--seconds", type=float, default=5.0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--reps", type=int, default=1, help="replicates (seed, seed+1, ...)")
    ap.add_argument("--b", type=float, default=0.03)
    ap.add_argument("--b-inh", type=float, default=None, help="separate b for inhibitory synapses (default = --b; the paper gridded bACh separately)")
    ap.add_argument("--size-power", type=float, default=1.0, help="size = proxy ** p (sensitivity only: volume may grow sub-linearly with synapse count; paper: p = 1 on volume)")
    ap.add_argument("--dt", type=float, default=0.0005)
    ap.add_argument("--skip", type=float, default=0.5, help="seconds discarded before the readout (paper: MN recruitment after 0.25 s)")
    ap.add_argument("--save", default="", help="optional .npz for the recorded traces")
    A = ap.parse_args()
    t0 = time.time()
    W, size, ty, side, leg, info = load(A.subnet, A.size, A.size_power)
    print(f"# subnet={A.subnet} size={A.size}^{A.size_power} I={A.dn_input} side={A.dn_side} b={A.b} b_inh={A.b_inh} T={A.seconds}s: {info['n']} cells "
          f"(DN {info['n_dn']}, MN {info['n_mn']}, premotor {info['n_prem']}), {info['nnz']} edges; built {time.time() - t0:.1f}s")
    named = {nm: np.flatnonzero(ty == nm) for nm in NAMED}
    legs = [l for l in ("lf", "rf", "lm", "rm", "lh", "rh") if (leg == l).any()]
    mnidx = np.flatnonzero(leg != "")
    rec_idx = np.unique(np.concatenate([mnidx] + list(named.values())))
    col = {c: k for k, c in enumerate(rec_idx)}
    allres = []
    for rep in range(A.reps):
        seed = A.seed + rep; t1 = time.time()
        R, act = simulate(W, size, ty, side, A.seconds, A.dt, A.dn_input, A.dn_side, seed, A.b, rec_idx, A.b_inh)
        X = R[int(A.skip * 1000):].astype(np.float64)
        nact = int((act > 0.01).sum()); sat = int((act > 150).sum())
        print(f"seed {seed}: {time.time() - t1:.0f}s; cells active (>0.01 Hz after 250 ms) {nact}/{info['n']}, near r_max (>150 Hz) {sat}")
        res = dict(seed=seed, nact=nact, sat=sat, legs={}, named={})
        for l in legs:
            mp = (leg == l) & np.isin(ty, PRO); mr = (leg == l) & np.isin(ty, REM)
            p = X[:, [col[i] for i in np.flatnonzero(mp)]].sum(1); r = X[:, [col[i] for i in np.flatnonzero(mr)]].sum(1)
            fp, qp = spectrum(p); fr_, qr = spectrum(r); gp = peak_1_40(p); gr = peak_1_40(r); cmin, lmin, cmax, lmax = xcorr(p, r)
            mns = X[:, [col[i] for i in np.flatnonzero(leg == l)]]
            active = mns.max(0) > 0.01
            dp = p.std() / max(p.mean(), 1e-9); dr = r.std() / max(r.mean(), 1e-9)
            sc = np.mean([ac_score(mns[:, j]) for j in np.flatnonzero(active)]) if active.any() else 0.0
            res["legs"][l] = (p.mean(), r.mean(), fp, qp, fr_, qr, cmin, lmin, cmax, lmax, int(active.sum()), int(len(active)), sc, dp, dr)
            print(f"  {l}: pro {p.mean():7.2f} Hz(sum) sd/mean {dp:.2f} peak {fp:5.1f} Hz x{qp:7.1f} (1-40 peak {gp[0]:.1f}) | rem {r.mean():7.2f} sd/mean {dr:.2f} peak {fr_:5.1f} x{qr:7.1f} (1-40 peak {gr[0]:.1f}) | "
                  f"xcorr min {cmin:+.2f}@{lmin:+d}ms max {cmax:+.2f}@{lmax:+d}ms | MNs active {active.sum()}/{len(active)} ac-score {sc:.2f}")
        for nm, ii in named.items():
            v = [(side[i], X[:, col[i]].mean(), X[:, col[i]].std(), *peak_1_40(X[:, col[i]])) for i in ii]
            res["named"][nm] = v
            print(f"  {nm:9s} " + "  ".join(f"{s}:{m:5.1f}±{sd:5.1f}" + (f"@{f:.1f}Hz x{q:.0f}" if sd >= 1 else "") for s, m, sd, f, q in v))
        allres.append(res)
        if A.save:
            np.savez_compressed(A.save.replace(".npz", f"_s{seed}.npz"), R=R, idx=rec_idx, type=ty[rec_idx], leg=leg[rec_idx].astype(str), side=side[rec_idx])
    return allres


if __name__ == "__main__":
    main()
