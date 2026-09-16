"""
columns.py - give every T4/T5 cell in the MaleCNS build a retinal column.

T4/T5 carry no assignedOlHex coordinates in the annotations, but their columnar
inputs do (Mi1/Mi4/Mi9 for T4, Tm1/Tm2/Tm9 for T5). Each cell's home column is the
hex column that contributes the most synaptic weight among its hex-tagged inputs.
Read from the wiring, not assigned. T4/T5 dendrites span ~3 columns, so the home
column holds only ~35-45% of tagged input; that is the biology, not a bad fit.

Writes t4t5_columns.npz:
    idx[N]   index into brain_whole.npz node table
    type[N]  T4a..T5d
    side[N]  L / R
    hex1[N], hex2[N]   assignedOlHex column of the home column
    share[N] fraction of hex-tagged input weight in the home column
"""
import numpy as np, pyarrow.feather as f, pandas as pd

d = np.load('brain_whole.npz'); ty = d['type'].astype(str); side = d['side'].astype(str)
bid = d['bodyId']; pre, post, w = d['pre'], d['post'], d['w']
a = f.read_table('data/body-annotations-male-cns-v1.0-minconf-0.5.feather',
                 columns=['bodyId', 'assignedOlHex1', 'assignedOlHex2']).to_pandas().set_index('bodyId')
hex1 = a.assignedOlHex1.reindex(bid).to_numpy(); hex2 = a.assignedOlHex2.reindex(bid).to_numpy()
has_hex = ~np.isnan(hex1)

types = ['T4a', 'T4b', 'T4c', 'T4d', 'T5a', 'T5b', 'T5c', 'T5d']
cells = np.flatnonzero(np.isin(ty, types))
m = np.isin(post, cells) & has_hex[pre]
df = pd.DataFrame({'post': post[m], 'w': w[m],
                   'h1': hex1[pre[m]].astype(int), 'h2': hex2[pre[m]].astype(int)})
bycol = df.groupby(['post', 'h1', 'h2']).w.sum().reset_index()
tot = bycol.groupby('post').w.transform('sum'); bycol['share'] = bycol.w / tot
home = bycol.sort_values('w', ascending=False).drop_duplicates('post').set_index('post')
home = home.reindex(cells)
ok = home.h1.notna().to_numpy()
out = dict(idx=cells[ok], type=ty[cells[ok]], side=side[cells[ok]],
           hex1=home.h1.to_numpy()[ok].astype(int), hex2=home.h2.to_numpy()[ok].astype(int),
           share=home.share.to_numpy()[ok].astype(np.float32))
np.savez('seam/t4t5_columns.npz', **out)
print(f"{ok.sum()} of {len(cells)} T4/T5 cells placed; {(~ok).sum()} without a hex-tagged input")
for s in 'LR':
    k = out['side'] == s
    print(f"  side {s}: {k.sum()} cells, hex1 {out['hex1'][k].min()}-{out['hex1'][k].max()}, hex2 {out['hex2'][k].min()}-{out['hex2'][k].max()}, "
          f"{len(set(zip(out['hex1'][k], out['hex2'][k])))} distinct columns, median share {np.median(out['share'][k]):.2f}")
