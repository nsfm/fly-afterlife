"""size: size-scaled excitability (the review of 09-22; campaign item 3), one block shared by world/cord.py and experiments/body_loop.py
so the two cannot drift. each cell's size S (its total input synapses, or a CSV of bodyId,size) over the median S_med scales its incoming
synapses by (S_med / S)^gain, its threshold to 7 mV x (S / S_med)^thr, and its membrane noise by (S_med / S)^noise (M._noise_scale, the
engine's per-cell term); every factor clipped to [1 / clip, clip]. all off by default.

    add_size_args(ap)          # --size-gain --size-thr --size-noise --size-clip --size-from
    apply_size(M, args)        # after the brain is built, before the run; prints what it did
"""
from __future__ import annotations
import numpy as np

SENSORY_SC = ["vnc_sensory", "sensory_ascending", "sensory_descending", "vnc_sensory_tbc", "sensory_ascending_tbc"]


def add_size_args(ap) -> None:
    ap.add_argument("--size-gain", type=float, default=0.0, help="size-scaled excitability, the input-resistance form (the review of 09-22; Pugliese 2026: gain and threshold scaled by cell size were necessary for the rhythm; Azevedo 2020: Rin 150 / 300 / 700 MOhm for fast / intermediate / slow MNs): every synapse onto cell i is scaled by (S_med / S_i)^A, S_i the cell's total input synapses (the size proxy this file has), S_med the median over the cord's neurons; a small cell gets a bigger PSP per synapse. 0 = off (E; sweep A)")
    ap.add_argument("--size-thr", type=float, default=0.0, help="size-scaled excitability, the threshold form: v_th_i = 7 mV x (S_i / S_med)^B; a small cell sits closer to threshold (Azevedo 2020: slow MNs rest 20 mV nearer threshold than fast). 0 = off (E; sweep B)")
    ap.add_argument("--size-noise", type=float, default=0.0, help="scale each cell's membrane noise by (S_med / S)^k with the same sizes as --size-gain (09-22, campaign item 3): the same current noise on a higher-resistance cell is a larger voltage noise; 0 = off (the engine unchanged)")
    ap.add_argument("--size-clip", type=float, default=4.0, help="clip on both size factors")
    ap.add_argument("--size-from", default="", help="a csv with bodyId and size columns (Pugliese 2026's wTable for the male front-leg network: voxel volume per cell) used as the size measure instead of the input-synapse proxy; cells not in it take the median (their set_sizes does the same for NaN)")


def apply_size(M, args) -> None:
    """the size block of world/cord.py (09-22), moved here unchanged: a no-op unless --size-gain, --size-thr or --size-noise > 0."""
    if not (args.size_gain > 0 or args.size_thr > 0 or args.size_noise > 0): return
    _S = np.bincount(M._out_tgt, weights=np.abs(M._out_w), minlength=M.N) / M.p.mv_per_synapse; _neur = ~np.isin(M.sc.astype(str), SENSORY_SC) & (_S > 0)
    if args.size_from:
        import csv as _csv; _sz = {}
        with open(args.size_from) as _f:
            for row in _csv.DictReader(_f):
                try: _sz[int(row["bodyId"])] = float(row["size"])
                except Exception: pass
        _S = np.array([_sz.get(int(b_), np.nan) for b_ in M.bodyId]); _have = np.isfinite(_S); _neur = _have & _neur; print(f"sizes from {args.size_from}: {int(_have.sum())} cells matched of {M.N}; the rest at the median")
        _Smed = float(np.nanmedian(_S[_have])); _S = np.where(_have, _S, _Smed); _ratio = _S / _Smed
    else:
        _Smed = float(np.median(_S[_neur])); _ratio = np.where(_S > 0, _S / _Smed, 1.0)
    if args.size_gain > 0:
        _f = np.clip(_ratio ** (-args.size_gain), 1.0 / args.size_clip, args.size_clip).astype(np.float32); M._out_w *= _f[M._out_tgt]
        print(f"size gain: synapses onto each cell scaled by (S_med / S)^{args.size_gain} (S_med {_Smed:.0f}); factors {np.round(np.quantile(_f[_neur], [0.05, 0.5, 0.95]), 2)}")
    if args.size_noise > 0:
        _n = np.clip(_ratio ** (-args.size_noise), 1.0 / args.size_clip, args.size_clip).astype(np.float32); M._noise_scale = np.where(_neur, _n, 1.0).astype(np.float32)
        print(f"size noise: membrane noise scaled by (S_med / S)^{args.size_noise}; factors {np.round(np.quantile(_n[_neur], [0.05, 0.5, 0.95]), 2)}")
    if args.size_thr > 0:
        _t = np.clip(_ratio ** args.size_thr, 1.0 / args.size_clip, args.size_clip); M.v_th[_neur] = (np.float32(M.p.v_thresh) * _t[_neur]).astype(np.float32)
        print(f"size threshold: v_th = 7 x (S / S_med)^{args.size_thr}; thresholds {np.round(np.quantile(M.v_th[_neur], [0.05, 0.5, 0.95]), 2)} mV")
