"""
dn_equalize.py - tracing-asymmetry correction for the descending output, at the source.

for each descending type on the wheel list (+ DNa02), scale the synaptic INPUT onto its left
cells and onto its right cells so that, averaged over a direction-balanced open-loop stimulus set
(world left + world right, odour left + odour right, touch left + touch right, and still), the
left and right cells fire at the same rate. direction-averaged, so the directional response is
untouched; per type and per side, so nothing else in the brain changes. iterated (rates are
nonlinear in input). labelled: "the animal is symmetric; the map is not." writes world/dn_gains.json.
"""
import sys, json, numpy as np
sys.path.insert(0, "ref/flybrain/scripts")
from flysim import FlyBrain
g = np.load("seam/eye_geom.npz"); types = ["T4a", "T4b", "T4c", "T4d", "T5a", "T5b", "T5c", "T5d"]
cols = np.load("seam/t4t5_columns.npz"); gkey = {(str(s), int(a), int(h)): i for i, (s, a, h) in enumerate(zip(g["side"], g["hex1"], g["hex2"]))}
gi = np.array([gkey[(str(s), int(a), int(h))] for s, a, h in zip(cols["side"], cols["hex1"], cols["hex2"])])
rest = np.load("seam/worldN_empty.npz"); yaw = {k: np.load(f"seam/worldN_yaw_{k}.npz") for k in ("left", "right")}
wheel = [w["type"] for w in json.load(open("world/dn_wheel.json"))["consistent"]] + ["DNa02"]
b = FlyBrain("brain_whole.npz", seed=0); ty = b.type.astype(str); ns = b.side.astype(str); cls_ = b.cls.astype(str); b.define_odor("A", n_channels=12, seed=7)
TACT = {s_: np.flatnonzero((cls_ == "mechanosensory_tactile") & (ns == s_)) for s_ in "LR"}
cells = {(t, s_): np.flatnonzero((ty == t) & (ns == s_) & (b.sc == "descending_neuron")) for t in wheel for s_ in "LR"}
edge_mask = {k: np.isin(b._out_tgt, v) for k, v in cells.items()}          # in-edges of those cells in the CSC out-edge arrays
gains = {k: 1.0 for k in cells}
def setup_vision(w):
    gr = {}
    for s_ in "LR":
        colmap = dict(zip(w[f"{s_}_idx"].tolist(), w[f"{s_}_col"].tolist()))
        for t in types:
            kk = (cols["type"] == t) & (cols["side"] == s_); hx = np.array([colmap.get(int(i), -1) for i in gi[kk]]); ok = hx >= 0
            gr[(t, s_)] = (cols["idx"][kk][ok], hx[ok], w[f"{s_}_{t}"], rest[f"{s_}_{t}"][20:100].mean(0))
    return gr
def run(cond):
    b.driven[:] = False
    for cl in b.SENSORY_CLASSES: b.driven[b.cls == cl] = True
    gr = None
    if cond.startswith("vision"):
        gr = setup_vision(yaw["right" if cond.endswith("worldleft") else "left"])
        for _, (idx, _, _, _) in gr.items(): b.driven[idx] = True
    b._driven_idx = np.flatnonzero(b.driven); b.reset(); b.drive_hz[:] = 0; b.g[:] = 0; b.refrac[:] = 0
    for _ in range(500): b.step()
    if cond == "odour_left": b.smell_bilateral(left={"A": 1.0}, right={"A": 0.4})
    if cond == "odour_right": b.smell_bilateral(left={"A": 0.4}, right={"A": 1.0})
    if cond == "touch_left": b.drive_hz[TACT["L"]] = 150.0
    if cond == "touch_right": b.drive_hz[TACT["R"]] = 150.0
    cnt = np.zeros(b.N, np.int32)
    for f in range(100):
        if gr is not None:
            for (t, s_), (idx, hx, a, r_) in gr.items(): b.drive_hz[idx] = 150.0 * np.clip((a[100 + f] - r_)[hx], 0, 1)
        for _ in range(10): cnt += b.step()
    return cnt
conds = ["still", "vision_worldleft", "vision_worldright", "odour_left", "odour_right", "touch_left", "touch_right"]
base_w = b._out_w.copy()
for it in range(4):
    tot = {k: 0.0 for k in cells}
    for cond in conds:
        c = run(cond)
        for k, v in cells.items(): tot[k] += c[v].sum() / max(len(v), 1)
    print(f"iteration {it}: per-cell rate over the 7 conditions (L / R): " + "  ".join(f"{t} {tot[(t,'L')]:.0f}/{tot[(t,'R')]:.0f}" for t in wheel), flush=True)
    for t in wheel:
        L, Rr = tot[(t, "L")], tot[(t, "R")]; m = (L + Rr) / 2
        for s_, v in (("L", L), ("R", Rr)):
            if v > 0 and m > 0: gains[(t, s_)] *= float(np.clip((m / v) ** 0.7, 0.5, 2.0))
    for k, msk in edge_mask.items(): b._out_w[msk] = base_w[msk] * gains[k]
json.dump({f"{t}|{s_}": float(gains[(t, s_)]) for (t, s_) in gains}, open("world/dn_gains.json", "w"), indent=1)
print("gains:", {f"{t}|{s_}": round(float(gains[(t, s_)]), 2) for (t, s_) in gains})
