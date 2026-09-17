"""
build_flywire.py - the female FlyWire brain (FAFB v783) in the same node-table format as brain_whole.npz.

    uv run python seam/build_flywire.py --out brain_female.npz [--min-weight 5]

inputs: data/flywire/neuron_annotations.tsv (flyconnectome/flywire_annotations supplemental file 1)
        data/flywire/proofread_connections_783.feather (zenodo 10676866): pre_pt_root_id, post_pt_root_id, syn_count
output fields as build_creature.py --whole: bodyId (root_id), type (cell_type, falling back to
hemibrain_type then cell_class), cls (cell_class), sc (super_class), nt (top_nt), side, sign, pre, post, w.
differences from the male: no VNC (FAFB is brain only), sides are given directly, transmitters are
per-neuron predictions (top_nt) rather than consensus. class/superclass vocabularies differ from
MaleCNS and are mapped where the LIF engine needs them (olfactory, gustatory, mechanosensory,
Kenyon_Cell, MBON, DAN, ALPN, descending_neuron, visual, cb_motor).
"""
import argparse, numpy as np, pandas as pd, pyarrow.feather as pf
ap = argparse.ArgumentParser(); ap.add_argument("--out", default="brain_female.npz"); ap.add_argument("--min-weight", type=int, default=5); a = ap.parse_args()
SIGN = {"acetylcholine": 1, "gaba": -1, "glutamate": -1, "histamine": -1, "dopamine": 0, "octopamine": 0, "serotonin": 0}
ann = pd.read_csv("data/flywire/neuron_annotations.tsv", sep="\t", usecols=["root_id", "flow", "super_class", "cell_class", "cell_sub_class", "cell_type", "hemibrain_type", "top_nt", "known_nt", "side"], dtype={"root_id": np.int64}, low_memory=False)
print(f"{len(ann):,} neurons; super_class: {ann.super_class.value_counts().to_dict()}")
print("cell_class (top):", ann.cell_class.value_counts().head(15).to_dict())
ty = ann.cell_type.fillna(ann.hemibrain_type).fillna(ann.cell_class).fillna("unknown").astype(str)
# map FlyWire vocab -> the class/superclass strings the LIF engine keys on
cls = ann.cell_class.fillna("").astype(str).copy(); sc = ann.super_class.fillna("").astype(str).copy(); sub = ann.cell_sub_class.fillna("").astype(str)
cls[(sc == "sensory") & cls.str.contains("olfactory")] = "olfactory"; cls[(sc == "sensory") & cls.str.contains("gustatory")] = "gustatory"
cls[(sc == "sensory") & cls.str.contains("mechanosensory")] = "mechanosensory"; cls[(sc == "sensory") & cls.str.contains("thermo")] = "thermosensory"; cls[(sc == "sensory") & cls.str.contains("hygro")] = "hygrosensory"
cls[cls.str.lower().str.startswith("kenyon")] = "Kenyon_Cell"; cls[cls == "MBON"] = "MBON"; cls[cls == "DAN"] = "DAN"; cls[cls == "ALPN"] = "ALPN"; cls[cls == "ALLN"] = "ALLN"
cls[(sc == "sensory") & cls.str.contains("visual")] = "visual"
sc[sc == "descending"] = "descending_neuron"; sc[sc == "motor"] = "cb_motor"; sc[sc == "ascending"] = "ascending_neuron"; sc[sc == "endocrine"] = "cb_endocrine"; sc[sc == "central"] = "cb_intrinsic"; sc[sc == "optic"] = "ol_intrinsic"; sc[sc == "visual_projection"] = "visual_projection"; sc[sc == "visual_centrifugal"] = "visual_centrifugal"
side = ann.side.fillna("").astype(str).str.lower().map({"left": "L", "right": "R", "center": "M", "na": "M"}).fillna("M")
nt = ann.known_nt.fillna(ann.top_nt).fillna("unknown").astype(str).str.lower()   # known transmitter where the literature has one, else the prediction
nt[cls == "Kenyon_Cell"] = "acetylcholine"                                           # KCs are cholinergic (Barnstedt et al. 2016); labelled override
sign = np.array([SIGN.get(x, 0) for x in nt], np.int8)
ids = ann.root_id.to_numpy(np.int64); order = np.argsort(ids); ids_s = ids[order]
print(f"signs: + {int((sign>0).sum()):,}  - {int((sign<0).sum()):,}  0 {int((sign==0).sum()):,};  sides {side.value_counts().to_dict()}")
con = pf.read_table("data/flywire/proofread_connections_783.feather", columns=["pre_pt_root_id", "post_pt_root_id", "syn_count"]).to_pandas()
print(f"connections table: {len(con):,} rows, {con.syn_count.sum():,} synapses")
def to_idx(x):
    i = np.searchsorted(ids_s, x); np.clip(i, 0, len(ids_s) - 1, out=i); return np.where(ids_s[i] == x, order[i], -1)
pre = to_idx(con.pre_pt_root_id.to_numpy(np.int64)); post = to_idx(con.post_pt_root_id.to_numpy(np.int64)); w = con.syn_count.to_numpy(np.int32)
m = (pre >= 0) & (post >= 0) & (w >= a.min_weight)
print(f"edges kept (both ends annotated, weight >= {a.min_weight}): {m.sum():,}")
np.savez(a.out, bodyId=ids, type=ty.to_numpy().astype(str), cls=cls.to_numpy().astype(str), sc=sc.to_numpy().astype(str), nt=nt.to_numpy().astype(str), side=side.to_numpy().astype(str), sign=sign,
         pre=pre[m].astype(np.int32), post=post[m].astype(np.int32), w=w[m].astype(np.int32))
print("wrote", a.out, "populations:", {k: int((cls == k).sum()) for k in ["olfactory", "gustatory", "mechanosensory", "Kenyon_Cell", "MBON", "DAN", "ALPN", "visual"]}, {k: int((sc == k).sum()) for k in ["descending_neuron", "cb_motor", "cb_intrinsic", "ol_intrinsic", "visual_projection"]})
