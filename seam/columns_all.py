"""
columns_all.py - a retinal column for every cell of every flyvis-modelled type
present in the MaleCNS build.

Column = the cell's own assignedOlHex if it has one; otherwise the hex column that
contributes the most synaptic weight among its hex-tagged INPUTS (as for T4/T5);
otherwise, among its hex-tagged OUTPUTS. Read from the wiring, labelled by source.

Name bridges: flyvis R1..R6 -> ours 'R1-R6'; flyvis CT1(M10)/CT1(Lo1) -> ours 'CT1'
(2 cells, not columnar; left out). Types absent from our build are skipped.

Writes seam/columns_all.npz: idx, type (our name), fvtype (flyvis name), side,
hex1, hex2, how ('self'|'in'|'out'), share
"""
import json, numpy as np, pandas as pd, pyarrow.feather as f, flyvis
spec = json.load(open(flyvis.connectome_file)); fvtypes = sorted(n['name'] for n in spec['nodes'])
d = np.load('brain_whole.npz'); ty = d['type'].astype(str); side = d['side'].astype(str)
bid = d['bodyId']; pre, post, w = d['pre'], d['post'], d['w']
a = f.read_table('data/body-annotations-male-cns-v1.0-minconf-0.5.feather',
                 columns=['bodyId', 'assignedOlHex1', 'assignedOlHex2']).to_pandas().set_index('bodyId')
hex1 = a.assignedOlHex1.reindex(bid).to_numpy(); hex2 = a.assignedOlHex2.reindex(bid).to_numpy()
has = ~np.isnan(hex1)

def best_partner(cells, direction):
    """strongest hex-tagged partner column per cell. direction 'in': partners are pre."""
    me, other = (post, pre) if direction == 'in' else (pre, post)
    m = np.isin(me, cells) & has[other]
    df = pd.DataFrame({'me': me[m], 'w': w[m], 'h1': hex1[other[m]].astype(int), 'h2': hex2[other[m]].astype(int)})
    if not len(df): return pd.DataFrame(columns=['h1', 'h2', 'share'])
    g = df.groupby(['me', 'h1', 'h2']).w.sum().reset_index()
    g['share'] = g.w / g.groupby('me').w.transform('sum')
    return g.sort_values('w', ascending=False).drop_duplicates('me').set_index('me')[['h1', 'h2', 'share']]

rows = []
for fvt in fvtypes:
    ours = 'R1-R6' if fvt in ('R1', 'R2', 'R3', 'R4', 'R5', 'R6') else fvt
    if fvt.startswith('CT1'): continue
    cells = np.flatnonzero(ty == ours)
    if not len(cells): continue
    h1 = np.full(len(cells), -1); h2 = np.full(len(cells), -1); how = np.full(len(cells), '', dtype='<U4'); share = np.zeros(len(cells), np.float32)
    own = has[cells]; h1[own] = hex1[cells[own]]; h2[own] = hex2[cells[own]]; how[own] = 'self'; share[own] = 1.0
    for direction in ('in', 'out'):
        need = h1 < 0
        if not need.any(): break
        bp = best_partner(cells[need], direction).reindex(cells[need])
        ok = bp.h1.notna().to_numpy()
        tgt = np.flatnonzero(need)[ok]
        h1[tgt] = bp.h1.to_numpy()[ok]; h2[tgt] = bp.h2.to_numpy()[ok]; how[tgt] = direction; share[tgt] = bp.share.to_numpy()[ok]
    k = h1 >= 0
    for i in np.flatnonzero(k):
        rows.append((cells[i], ours, fvt, side[cells[i]], h1[i], h2[i], how[i], share[i]))
    print(f"{fvt:9s} {len(cells):5d} cells  placed {k.sum():5d}  self {int((how=='self').sum()):5d} in {int((how=='in').sum()):5d} out {int((how=='out').sum()):5d}")
df = pd.DataFrame(rows, columns=['idx', 'type', 'fvtype', 'side', 'hex1', 'hex2', 'how', 'share'])
np.savez('seam/columns_all.npz', **{c: df[c].to_numpy() for c in df.columns})
print(f"\n{len(df)} cells placed across {df.fvtype.nunique()} flyvis types")
