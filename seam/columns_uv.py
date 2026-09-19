"""columns_uv.py - a retinal column for the cells the UV / colour pathway starts from: R7 (R7p, R7y, R7d, R7_unclear, R7R8_unclear),
R8 (R8p, R8y, R8d, R8_unclear) and Dm2. same rule as columns_all.py: the cell's own assignedOlHex; else the hex column
carrying the most synaptic weight among its hex-tagged inputs; else among its hex-tagged outputs (photoreceptors have no
inputs, so they are placed by where they project). writes seam/columns_uv.npz: idx, type, side, hex1, hex2, how, share."""
import numpy as np, pandas as pd, pyarrow.feather as f
d = np.load('brain_whole.npz'); ty = d['type'].astype(str); side = d['side'].astype(str); bid = d['bodyId']; pre, post, w = d['pre'], d['post'], d['w']
a = f.read_table('data/body-annotations-male-cns-v1.0-minconf-0.5.feather', columns=['bodyId', 'assignedOlHex1', 'assignedOlHex2']).to_pandas().set_index('bodyId')
hex1 = a.assignedOlHex1.reindex(bid).to_numpy().astype(float); hex2 = a.assignedOlHex2.reindex(bid).to_numpy().astype(float); has = ~np.isnan(hex1)
TYPES = [t for t in sorted(set(ty)) if t.startswith(('R7', 'R8')) or t == 'Dm2']

def best_partner(cells, direction):
    me, other = (post, pre) if direction == 'in' else (pre, post)
    m = np.isin(me, cells) & has[other]
    if not m.any(): return pd.DataFrame(columns=['h1', 'h2', 'share'])
    df = pd.DataFrame({'me': me[m], 'w': np.abs(w[m]), 'h1': hex1[other[m]].astype(int), 'h2': hex2[other[m]].astype(int)})
    g = df.groupby(['me', 'h1', 'h2']).w.sum().reset_index(); tot = g.groupby('me').w.transform('sum'); g['share'] = g.w / tot
    return g.sort_values('w', ascending=False).drop_duplicates('me').set_index('me')[['h1', 'h2', 'share']]

rows = []
for t in TYPES:
    cells = np.flatnonzero(ty == t); own = has[cells]
    for c in cells[own]: rows.append((c, t, side[c], int(hex1[c]), int(hex2[c]), 'self', 1.0))
    rest = cells[~own]; bi = best_partner(rest, 'in'); left = np.array([c for c in rest if c not in bi.index]); bo = best_partner(left, 'out') if len(left) else bi.iloc[0:0]
    for c in rest:
        if c in bi.index: r = bi.loc[c]; rows.append((c, t, side[c], int(r.h1), int(r.h2), 'in', float(r.share)))
        elif c in bo.index: r = bo.loc[c]; rows.append((c, t, side[c], int(r.h1), int(r.h2), 'out', float(r.share)))
    print(f"{t:14s} {len(cells):5d} cells: placed {sum(1 for r in rows if r[1] == t):5d}  (self {own.sum()}, in {len(bi)}, out {sum(1 for r in rows if r[1] == t and r[5] == 'out')})")
df = pd.DataFrame(rows, columns=['idx', 'type', 'side', 'hex1', 'hex2', 'how', 'share'])
np.savez('seam/columns_uv.npz', **{c: (df[c].to_numpy() if pd.api.types.is_numeric_dtype(df[c]) else df[c].to_numpy().astype(str)) for c in df.columns})
print(f"{len(df)} cells placed across {df.type.nunique()} types -> seam/columns_uv.npz")
