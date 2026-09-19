"""compass.py - is the heading bump alive? reads a <run>.cells.npz written by pair.py --log-types (per-cell spike counts per
chunk for EPG / PEN / PFL / Delta7) and the annotation table for the wedge each EPG cell occupies (instance names
EPG(PB08)_L1..L8 / R1..R8: sixteen bridge glomeruli tiling the eight wedges of the ellipsoid body).

    uv run python experiments/compass.py world/compass/garden_s12.npz

reports: EPG rates; the bump (population-vector length over the wedges, per chunk, against a shuffle); the bump's phase
against his heading (circular correlation, and the offset's spread: a live compass keeps a constant offset); PEN, Delta7,
PFL rates and PFL3 left-right against the heading error. wedge angles: L_i -> (i - 1) x 45 deg, R_j -> (8 - j) x 45 deg
(the mirror tiling of Hulse 2021, to a half-wedge; enough for phase tracking, not for absolute offsets)."""
from __future__ import annotations
import sys, re, numpy as np


def wedge_angles(bodyIds):
    import pyarrow.feather as F
    t = F.read_table("data/body-annotations-male-cns-v1.0-minconf-0.5.feather", columns=["bodyId", "instance"])
    inst = dict(zip(t.column("bodyId").to_pylist(), t.column("instance").to_pylist()))
    ang = np.full(len(bodyIds), np.nan)
    for k, b in enumerate(bodyIds):
        m = re.search(r"_([LR])(\d)", str(inst.get(int(b), "")))
        if m: i = int(m.group(2)); ang[k] = ((i - 1) * 45.0) if m.group(1) == "L" else ((8 - i) * 45.0)
    return ang, inst


def circ_corr(a, b):
    """circular-circular correlation (Jammalamadaka), angles in degrees."""
    a = np.radians(a); b = np.radians(b); a = a - np.angle(np.exp(1j * a).mean()); b = b - np.angle(np.exp(1j * b).mean())
    return float(np.sum(np.sin(a) * np.sin(b)) / np.sqrt(np.sum(np.sin(a) ** 2) * np.sum(np.sin(b) ** 2)))


if __name__ == "__main__":
    f = sys.argv[1].replace(".npz", "") + ".cells.npz"; C = np.load(f, allow_pickle=True)
    ty = C["type"].astype(str); side = C["side"].astype(str); cnt = C["counts"].astype(float); pose = C["pose_chunk"]; bid = C["bodyId"]
    n_chunk = cnt.shape[0]; heading = pose[:n_chunk, 2] % 360
    print(f"{n_chunk} chunks ({n_chunk / 10:.0f} s); cells logged {cnt.shape[1]}")
    print(f"{'type':14s} {'cells':>5s} {'Hz/cell':>8s} {'L Hz':>6s} {'R Hz':>6s} {'silent cells':>12s}")
    for t in sorted(set(ty)):
        m = ty == t; r = cnt[:, m].mean(0) * 10   # per chunk -> Hz
        print(f"{t:14s} {m.sum():5d} {r.mean():8.2f} {cnt[:, m & (side == 'L')].mean() * 10 if (m & (side == 'L')).any() else 0:6.2f} {cnt[:, m & (side == 'R')].mean() * 10 if (m & (side == 'R')).any() else 0:6.2f} {(r < 0.05).sum():12d}")
    epg = ty == "EPG"; ang, inst = wedge_angles(bid); w = ang[epg]; e = cnt[:, epg]; ok = np.isfinite(w)
    print(f"\nEPG: {epg.sum()} cells, {ok.sum()} with a wedge label; wedges present: {sorted(set(w[ok]))}")
    if e.sum() == 0: print("EPG silent: no bump to measure."); sys.exit()
    # the bump: population vector over wedges per chunk, smoothed over 5 chunks (0.5 s)
    k = np.ones(5) / 5; es = np.apply_along_axis(lambda x: np.convolve(x, k, mode="same"), 0, e[:, ok]); wr = np.radians(w[ok])
    Z = (es * np.exp(1j * wr)).sum(1); tot = es.sum(1); pvl = np.abs(Z) / np.maximum(tot, 1e-9); phase = np.degrees(np.angle(Z)) % 360
    rng = np.random.default_rng(0); pvl_sh = np.mean([np.mean(np.abs((es * np.exp(1j * rng.permutation(wr))).sum(1)) / np.maximum(tot, 1e-9)) for _ in range(50)])
    active = tot > np.percentile(tot, 25)
    print(f"bump: mean population-vector length {pvl[active].mean():.3f} (shuffled wedges {pvl_sh:.3f}); EPG total per chunk {tot.mean():.1f}")
    # does the phase follow his heading?
    cc = circ_corr(phase[active], heading[active]); cc_neg = circ_corr(phase[active], -heading[active])
    off = (phase[active] - heading[active]) % 360; R_off = np.abs(np.exp(1j * np.radians(off)).mean())
    off2 = (phase[active] + heading[active]) % 360; R_off2 = np.abs(np.exp(1j * np.radians(off2)).mean())
    print(f"phase vs heading: circular correlation {cc:+.3f} (vs -heading {cc_neg:+.3f}); offset concentration {R_off:.3f} (mirror {R_off2:.3f}); 1 = a constant offset, 0 = unrelated")
    # PFL3 left-right vs the heading error, if there is a bump
    pfl = ty == "PFL3"
    if pfl.any():
        L = cnt[:, pfl & (side == "L")].sum(1); R = cnt[:, pfl & (side == "R")].sum(1); print(f"PFL3 L {L.mean() * 10:.2f} Hz-sum, R {R.mean() * 10:.2f}; L-R sd per chunk {np.std(L - R):.2f}")
    # turning: does EPG phase advance when he turns? compare phase velocity with heading velocity
    dphi = (np.diff(phase) + 180) % 360 - 180; dh = (np.diff(heading) + 180) % 360 - 180; m2 = active[1:] & (np.abs(dh) > 2)
    if m2.sum() > 10: print(f"turns (> 2 deg/chunk, n={m2.sum()}): corr(bump velocity, heading velocity) {np.corrcoef(dphi[m2], dh[m2])[0, 1]:+.3f}")
