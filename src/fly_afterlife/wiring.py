"""wiring corrections, labelled. `mirror_normalise` (09-18): for every bilateral cell type, scale each cell's incoming
excitatory and inhibitory weights so that the left and right cells of the type receive the pair's mean total input.
the assumption: bilateral pairs are mirror images in life, and left-right differences in traced synapse counts are
reconstruction (the right ventral cord carries ~0.85x the left's traced input in MaleCNS v1.0; IN12B014 R 0.69x).
opt-in (`--mirror`); the oracle runs without it. factors clipped to [1/clip, clip]. only FastFlyBrain's edge list is
scaled (the dense engine's matrix is left as loaded)."""
from __future__ import annotations
import numpy as np


def mirror_normalise(M, clip: float = 2.0, scope: str = "all") -> dict:
    mty = M.type.astype(str); side = M.side.astype(str); tgt = M._out_tgt; w = M._out_w
    if scope == "vnc": inscope = np.isin(M.sc.astype(str), ["vnc_motor"]) | np.char.startswith(mty, "IN") | np.char.startswith(mty, "AN") | np.char.startswith(mty, "SN")
    else: inscope = np.ones(M.N, bool)
    exc = np.zeros(M.N); np.add.at(exc, tgt, np.clip(w, 0, None)); inh = np.zeros(M.N); np.add.at(inh, tgt, np.clip(-w, 0, None))
    f_exc = np.ones(M.N, np.float32); f_inh = np.ones(M.N, np.float32); n_types = 0
    for t in np.unique(mty[inscope]):
        L = np.flatnonzero((mty == t) & (side == "L") & inscope); R = np.flatnonzero((mty == t) & (side == "R") & inscope)
        if len(L) == 0 or len(R) == 0: continue
        n_types += 1
        for tot, f in ((exc, f_exc), (inh, f_inh)):
            mL = tot[L].mean(); mR = tot[R].mean(); target = 0.5 * (mL + mR)
            if target <= 0: continue
            for cells, m in ((L, mL), (R, mR)):
                if m > 0: f[cells] = np.clip(target / m, 1.0 / clip, clip)
    pos = w > 0; w[pos] *= f_exc[tgt[pos]]; w[~pos] *= f_inh[tgt[~pos]]
    return dict(types=n_types, exc_factor_median_R=float(np.median(f_exc[(side == "R") & (f_exc != 1)])) if ((side == "R") & (f_exc != 1)).any() else 1.0,
                exc_factor_median_L=float(np.median(f_exc[(side == "L") & (f_exc != 1)])) if ((side == "L") & (f_exc != 1)).any() else 1.0, clipped=int(((f_exc == clip) | (f_exc == 1 / clip)).sum()))


def ring_map(M, er_cells, rho_deg, wedge_deg_of, sun_az_deg, kappa: float = 2.0, floor: float = 0.1) -> int:
    """the plastic map from a ring neuron's visual field to the heading wedge it spares (Kim 2019; Fisher 2019), set by
    construction (09-18 night): ring cell k with field azimuth rho_k (relative to heading) keeps its inhibition onto every
    EPG wedge except theta_k = sun_az - rho_k, the wedge that represents his heading when the sun sits at rho_k; there the
    weight is scaled by `floor` (a von Mises notch of width 1/kappa). in life this map is learned; here it is imposed,
    labelled. er_cells: the ring cells (indices); rho_deg: their field azimuths; wedge_deg_of: {epg cell index: wedge deg}.
    returns the number of edges scaled."""
    tgt = M._out_tgt; w = M._out_w; src = np.repeat(np.arange(M.N), np.diff(M._out_ptr)); n = 0
    wedge = np.full(M.N, np.nan); 
    for i, a in wedge_deg_of.items(): wedge[i] = a
    for c, rho in zip(er_cells, rho_deg):
        theta_k = (sun_az_deg - rho) % 360.0; e = np.flatnonzero((src == c) & np.isfinite(wedge[tgt]))
        if e.size == 0: continue
        d = np.radians(wedge[tgt[e]] - theta_k); notch = np.exp(kappa * (np.cos(d) - 1.0))   # 1 at the spared wedge, -> 0 away from it
        w[e] = (w[e] * (1.0 - (1.0 - floor) * notch)).astype(np.float32); n += e.size
    return n
