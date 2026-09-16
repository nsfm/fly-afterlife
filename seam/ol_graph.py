"""
ol_graph.py - the real optic lobe as a graph, for the transplant.

Cells: every traced, typed cell whose type flyvis has parameters for (48 ol_intrinsic
types present + R1-R6 as 'R1-R6' + CT1), both eyes. Edges: from the RAW weights table,
NO synapse threshold (flyvis's spec counts every synapse). Also writes the per-pair
count comparison: MaleCNS mean synapses per target cell from a source type vs flyvis's.
Outputs: seam/ol_graph.npz (idx, bodyId, type, fvtype, side, pre, post, w) and
seam/pair_counts.csv
"""
import json, numpy as np, pandas as pd, pyarrow.feather as pf, pyarrow.compute as pc, pyarrow as pa
fv = json.load(open("seam/flyvis_params.json")); fvtypes = set(fv["nodes"])
name_map = {"R1-R6": "R1"}   # our name -> flyvis name (R1..R6 share params ~ identical; use R1's)
ann = pf.read_table("data/body-annotations-male-cns-v1.0-minconf-0.5.feather", columns=["bodyId", "type", "superclass", "somaSide", "rootSide", "status"]).to_pandas()
ann = ann[(ann.status == "Traced") & ann.type.notna()]
def fvname(t):
    if t in fvtypes: return t
    if t == "R1-R6": return "R1"
    if t == "CT1": return "CT1(M10)"
    return None
ann["fvtype"] = ann.type.map(fvname); keep = ann[ann.fvtype.notna()].copy()
side = keep.somaSide.where(keep.somaSide.isin(["L", "R"]), keep.rootSide).fillna("M")
keep["side"] = side.to_numpy()
print(f"{len(keep)} cells of {keep.type.nunique()} our-types -> {keep.fvtype.nunique()} flyvis types; sides {keep.side.value_counts().to_dict()}")
ids = keep.bodyId.to_numpy(np.int64); order = np.argsort(ids); ids_sorted = ids[order]
tbl = pf.read_table("data/connectome-weights-male-cns-v1.0-minconf-0.5.feather")
pre = tbl["body_pre"].to_numpy(); post = tbl["body_post"].to_numpy(); w = tbl["weight"].to_numpy()
def to_idx(x):
    i = np.searchsorted(ids_sorted, x); np.clip(i, 0, len(ids_sorted) - 1, out=i)
    return np.where(ids_sorted[i] == x, order[i], -1)
pi = to_idx(pre); qi = to_idx(post); m = (pi >= 0) & (qi >= 0)
print(f"edges among them (raw, no threshold): {m.sum():,}  synapses {w[m].sum():,}   (weight>=5 would keep {(m & (w >= 5)).sum():,})")
np.savez("seam/ol_graph.npz", bodyId=ids, type=keep.type.to_numpy().astype(str), fvtype=keep.fvtype.to_numpy().astype(str),
         side=keep.side.to_numpy().astype(str), pre=pi[m].astype(np.int32), post=qi[m].astype(np.int32), w=w[m].astype(np.int32))
# pair comparison: mean synapses per TARGET cell from a source type (over target cells that get >=1)
ft = keep.fvtype.to_numpy(); df = pd.DataFrame({"s": ft[pi[m]], "t": ft[qi[m]], "tgt": qi[m], "w": w[m]})
per_tgt = df.groupby(["s", "t", "tgt"]).w.sum().groupby(["s", "t"]).mean()
rows = []
for k, e in fv["edges"].items():
    s, t = k.split("->"); ours = per_tgt.get((s, t), np.nan)
    rows.append((s, t, e["n_syn_per_target"], ours, e["strength"], e["sign"]))
cmp = pd.DataFrame(rows, columns=["s", "t", "flyvis_syn_per_target", "malecns_syn_per_target", "strength", "sign"])
cmp["ratio"] = cmp.malecns_syn_per_target / cmp.flyvis_syn_per_target
cmp.to_csv("seam/pair_counts.csv", index=False)
ok = cmp.dropna(); print(f"\npairs with data in both: {len(ok)} of {len(cmp)}; missing in MaleCNS: {cmp.malecns_syn_per_target.isna().sum()}")
print(f"ratio MaleCNS/flyvis synapses per target: median {ok.ratio.median():.2f}, IQR {ok.ratio.quantile(.25):.2f}-{ok.ratio.quantile(.75):.2f}, corr(log) {np.corrcoef(np.log(ok.flyvis_syn_per_target), np.log(ok.malecns_syn_per_target))[0,1]:.2f}")
big = ok[ok.flyvis_syn_per_target > 20].sort_values("flyvis_syn_per_target", ascending=False)
print("\nheaviest pairs:"); print(big.head(15).round(2).to_string(index=False))
