"""
symmetrize.py - per-pathway hemisphere correction. the right hemisphere of the MaleCNS is more
completely traced (+9.7% synaptic weight); the LIF's one global rescale can't fix pathways that
differ by more or less than that. here, for every (pre type, post type) pair, the total synaptic
weight onto LEFT targets and onto RIGHT targets is made equal by scaling each side toward their
mean (both sides move, so no pathway is doubled). midline cells ('M') are left alone. labelled:
"the animal is symmetric per pathway; the difference is the map." writes brain_sym.npz.
"""
import numpy as np, pandas as pd
d = dict(np.load("brain_whole.npz")); ty = d["type"].astype(str); side = d["side"].astype(str); pre, post, w = d["pre"], d["post"], d["w"].astype(np.float64)
df = pd.DataFrame({"k": pd.Series(ty[pre]) + "->" + pd.Series(ty[post]), "s": side[post], "w": w})
tot = df[df.s.isin(["L", "R"])].groupby(["k", "s"]).w.sum().unstack("s").fillna(0.0)
both = tot[(tot.L > 0) & (tot.R > 0)]; mean = (both.L + both.R) / 2
scale = pd.DataFrame({"L": mean / both.L, "R": mean / both.R}).clip(0.25, 4.0)
sc = np.ones(len(w))
for s in "LR":
    m = df.s.to_numpy() == s; keys = df.k.to_numpy()[m]; f = scale[s].reindex(keys).fillna(1.0).to_numpy(); sc[m] = f
d["w"] = np.rint(w * sc).astype(d["w"].dtype)
np.savez("brain_sym.npz", **d)
print(f"{len(both)} pathways symmetrized ({(~tot.index.isin(both.index)).sum()} one-sided left alone); scale factors: L median {scale.L.median():.3f} (IQR {scale.L.quantile(.25):.3f}-{scale.L.quantile(.75):.3f}), R median {scale.R.median():.3f}")
for s in "LR": print(f"  total weight onto {s} targets: before {tot[s].sum():,.0f}  after {df.assign(w2=d['w'])[df.s == s].w2.sum():,.0f}")
