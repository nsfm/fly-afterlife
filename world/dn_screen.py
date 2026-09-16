"""
dn_screen.py - screen every descending-neuron type for a consistent steering laterality, open loop.

conditions and the turn a fly should make:
  vision: world rotates LEFT (yaw_right render: fly turned right, world moved left)  -> turn LEFT  (optomotor)
          world rotates RIGHT (yaw_left render)                                       -> turn RIGHT
  odour:  stronger on the LEFT antenna (1.0 / 0.4)                                    -> turn LEFT  (toward)
          stronger on the RIGHT                                                        -> turn RIGHT
  touch:  LEFT leg bristles                                                            -> turn RIGHT (away)
          RIGHT leg bristles                                                           -> turn LEFT
for each DN type with cells on both sides: per condition, (L - R) spikes over 1 s, both seeds.
a type's "turn-left index" per modality = (L-R | should-turn-left) - (L-R | should-turn-right).
consistent = same sign of that index in all three modalities (either all positive: more of it on
the left means turn left, 'ipsi'; or all negative, 'contra'). writes world/dn_screen.json.
"""
import sys, json, numpy as np
sys.path.insert(0, "ref/flybrain/scripts")
from flysim import FlyBrain
g = np.load("seam/eye_geom.npz"); types = ["T4a", "T4b", "T4c", "T4d", "T5a", "T5b", "T5c", "T5d"]
cols = np.load("seam/t4t5_columns.npz"); gkey = {(str(s), int(a), int(h)): i for i, (s, a, h) in enumerate(zip(g["side"], g["hex1"], g["hex2"]))}
gi = np.array([gkey[(str(s), int(a), int(h))] for s, a, h in zip(cols["side"], cols["hex1"], cols["hex2"])])
rest = np.load("seam/worldN_empty.npz"); yaw = {k: np.load(f"seam/worldN_yaw_{k}.npz") for k in ("left", "right")}
out = {}
for seed in (0, 1):
    b = FlyBrain("brain_whole.npz", seed=seed); ty = b.type.astype(str); ns = b.side.astype(str); cls_ = b.cls.astype(str)
    dn = np.flatnonzero(b.sc == "descending_neuron"); dtypes = sorted({t for t in ty[dn] if ((ty == t) & (ns == "L")).any() and ((ty == t) & (ns == "R")).any()})
    idxL = {t: np.flatnonzero((ty == t) & (ns == "L") & (b.sc == "descending_neuron")) for t in dtypes}; idxR = {t: np.flatnonzero((ty == t) & (ns == "R") & (b.sc == "descending_neuron")) for t in dtypes}
    b.define_odor("A", n_channels=12, seed=7); TACT = {s_: np.flatnonzero((cls_ == "mechanosensory_tactile") & (ns == s_)) for s_ in "LR"}
    def setup_vision(w):
        groups = {}
        for s in "LR":
            colmap = dict(zip(w[f"{s}_idx"].tolist(), w[f"{s}_col"].tolist()))
            for t in types:
                kk = (cols["type"] == t) & (cols["side"] == s); hx = np.array([colmap.get(int(i), -1) for i in gi[kk]]); ok = hx >= 0
                groups[(t, s)] = (cols["idx"][kk][ok], hx[ok], w[f"{s}_{t}"], rest[f"{s}_{t}"][20:100].mean(0))
        return groups
    def run(cond):
        b.driven[:] = False
        for cl in b.SENSORY_CLASSES: b.driven[b.cls == cl] = True
        groups = None
        if cond.startswith("vision"):
            groups = setup_vision(yaw["right" if cond.endswith("worldleft") else "left"])
            for _, (idx, _, _, _) in groups.items(): b.driven[idx] = True
        b._driven_idx = np.flatnonzero(b.driven); b.reset(); b.drive_hz[:] = 0; b.g[:] = 0; b.refrac[:] = 0
        for _ in range(500): b.step()
        if cond == "odour_left": b.smell_bilateral(left={"A": 1.0}, right={"A": 0.4})
        if cond == "odour_right": b.smell_bilateral(left={"A": 0.4}, right={"A": 1.0})
        if cond == "touch_left": b.drive_hz[TACT["L"]] = 150.0
        if cond == "touch_right": b.drive_hz[TACT["R"]] = 150.0
        cnt = np.zeros(b.N, np.int32)
        for f in range(100):
            if groups is not None:
                for (t, s), (idx, hx, a, r_) in groups.items(): b.drive_hz[idx] = 150.0 * np.clip((a[100 + f] - r_)[hx], 0, 1)
            for _ in range(10): cnt += b.step()
        return cnt
    for cond in ["vision_worldleft", "vision_worldright", "odour_left", "odour_right", "touch_left", "touch_right"]:
        c = run(cond)
        for t in dtypes: out.setdefault(t, {}).setdefault(cond, []).append([int(c[idxL[t]].sum()), int(c[idxR[t]].sum())])
        print(f"seed {seed} {cond} done", flush=True)
json.dump(out, open("world/dn_screen.json", "w"))
# selection
rows = []
for t, d in out.items():
    def lr(cond): return np.mean([a - b_ for a, b_ in d[cond]])
    def tot(cond): return np.mean([a + b_ for a, b_ in d[cond]])
    vis = lr("vision_worldleft") - lr("vision_worldright"); od = lr("odour_left") - lr("odour_right"); tc = lr("touch_right") - lr("touch_left")
    spikes = np.mean([tot(c) for c in d])
    rows.append((t, vis, od, tc, spikes))
print(f"\n{'type':10s} {'vision':>8s} {'odour':>8s} {'touch':>8s} {'spikes/s':>9s}   turn-left index per modality (L-R when should turn left, minus when should turn right)")
cons = []
for t, vis, od, tc, sp in sorted(rows, key=lambda r: -abs(r[1]) - abs(r[2]) - abs(r[3])):
    signs = [np.sign(v) for v in (vis, od, tc) if abs(v) >= 2]
    ok = len(signs) == 3 and len(set(signs)) == 1
    if ok: cons.append((t, int(signs[0]), vis, od, tc, sp))
    if abs(vis) + abs(od) + abs(tc) > 10: print(f"{t:10s} {vis:+8.1f} {od:+8.1f} {tc:+8.1f} {sp:9.0f}   {'CONSISTENT ' + ('ipsi' if ok and signs[0] > 0 else 'contra') if ok else ''}")
print(f"\nconsistent across all three modalities (|index| >= 2 each): {len(cons)} types")
for t, sg, vis, od, tc, sp in cons: print(f"  {t:10s} {'ipsi ' if sg > 0 else 'contra'}  vision {vis:+.1f} odour {od:+.1f} touch {tc:+.1f}  {sp:.0f} spikes/s")
json.dump({"consistent": [{"type": t, "sign": sg} for t, sg, *_ in cons]}, open("world/dn_wheel.json", "w"), indent=1)
