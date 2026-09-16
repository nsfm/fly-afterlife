"""
brain_equalize.py - whole-brain hemisphere homeostasis for the LIF.

for EVERY cell type with cells on both sides (central brain, descending, VNC), scale the synaptic
input onto its left cells and its right cells so that, averaged over a direction-balanced open-loop
stimulus set (still, world left/right, odour left/right, touch left/right), left and right cells
fire at the same rate. driven sensory cells are excluded (their rate is set by the stimulus).
iterated with damping; gains clipped [0.33, 3]. labelled: "the animal is symmetric per pathway; the
map is not." writes world/brain_gains.npz (per-cell input gain, aligned to brain_whole.npz).
"""
import sys, json, numpy as np, pandas as pd
sys.path.insert(0, "ref/flybrain/scripts")
from flysim import FlyBrain
g = np.load("seam/eye_geom.npz"); types = ["T4a", "T4b", "T4c", "T4d", "T5a", "T5b", "T5c", "T5d"]
cols = np.load("seam/t4t5_columns.npz"); gkey = {(str(s), int(a), int(h)): i for i, (s, a, h) in enumerate(zip(g["side"], g["hex1"], g["hex2"]))}
gi = np.array([gkey[(str(s), int(a), int(h))] for s, a, h in zip(cols["side"], cols["hex1"], cols["hex2"])])
rest = np.load("seam/worldN_empty.npz"); yaw = {k: np.load(f"seam/worldN_yaw_{k}.npz") for k in ("left", "right")}
b = FlyBrain("brain_whole.npz", seed=0); ty = b.type.astype(str); ns = b.side.astype(str); cls_ = b.cls.astype(str); b.define_odor("A", n_channels=12, seed=7)
TACT = {s_: np.flatnonzero((cls_ == "mechanosensory_tactile") & (ns == s_)) for s_ in "LR"}
driven_types = set(ty[b.driven]) | set(types)
# groups: (type, side) for types with cells on both sides, not driven
df = pd.DataFrame({"t": ty, "s": ns, "i": np.arange(b.N)}); df = df[df.s.isin(["L", "R"]) & ~df.t.isin(driven_types)]
both = df.groupby("t").s.nunique(); keep = both[both == 2].index; df = df[df.t.isin(keep)]
grp = {k: v.i.to_numpy() for k, v in df.groupby(["t", "s"])}
print(f"{len(keep)} types x 2 sides = {len(grp)} groups, {len(df)} cells")
tgt_edge = b._out_tgt; edge_group = np.full(len(tgt_edge), -1, np.int32); keys = list(grp)
cell_group = np.full(b.N, -1, np.int32)
for gi_, k in enumerate(keys): cell_group[grp[k]] = gi_
edge_group = cell_group[tgt_edge]
gain = np.ones(len(keys), np.float32); base_w = b._out_w.copy()
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
for it in range(6):
    tot = np.zeros(b.N)
    for cond in conds: tot += run(cond)
    rate = np.array([tot[grp[k]].mean() for k in keys])
    L = np.array([rate[i] for i, k in enumerate(keys) if k[1] == "L"]); R = np.array([rate[i] for i, k in enumerate(keys) if k[1] == "R"])
    active = (L + R) > 2; asym = np.abs(L - R) / np.maximum(L + R, 1e-9)
    print(f"iteration {it}: {int(active.sum())} active types; median |L-R|/(L+R) {np.median(asym[active]):.3f}, mean {asym[active].mean():.3f}; DN total L/R {tot[(b.sc=='descending_neuron')&(ns=='L')].sum():.0f}/{tot[(b.sc=='descending_neuron')&(ns=='R')].sum():.0f}", flush=True)
    for i, k in enumerate(keys):
        t, s_ = k; j = keys.index((t, "R" if s_ == "L" else "L")); m = (rate[i] + rate[j]) / 2
        if rate[i] > 0.5 and m > 0.5: gain[i] = float(np.clip(gain[i] * (m / rate[i]) ** 0.5, 0.33, 3.0))
    scale = np.where(edge_group >= 0, gain[np.maximum(edge_group, 0)], 1.0); b._out_w[:] = base_w * scale
cell_gain = np.where(cell_group >= 0, gain[np.maximum(cell_group, 0)], 1.0).astype(np.float32)
np.savez("world/brain_gains.npz", gain=cell_gain, bodyId=b.bodyId)
print("saved world/brain_gains.npz; gain range", cell_gain.min(), cell_gain.max(), "; groups changed >10%:", int((np.abs(gain - 1) > 0.1).sum()), "of", len(keys))
