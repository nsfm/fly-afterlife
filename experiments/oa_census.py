"""oa_census.py - the cord's octopaminergic cells, read from the wiring (campaign item 5; docs/physiology/octopamine_state.md §1).

    uv run python experiments/oa_census.py                         # brain_cord.npz (edges >= 5 synapses, the file of record)
    uv run python experiments/oa_census.py --brain brain_cord_all.npz   # every edge (item 1's rebuild)

prints, for every cell whose consensus transmitter is octopamine, and for the EN / EA / OA / VUM efferents the prediction leaves
'unclear': type, side, exit nerve, input synapses, its largest presynaptic types (synapses, the presynaptic transmitter and the
sign the engine gives it), and its output synapses split into onto-OA and onto-other. then the descending neurons onto the OA
cells, and the cord (non-DN) cells onto them. read-only; no simulation.
"""
import sys, argparse, collections
import numpy as np
sys.path.insert(0, "src")

ap = argparse.ArgumentParser()
ap.add_argument("--brain", default="brain_cord.npz")
ap.add_argument("--top", type=int, default=6, help="presynaptic types listed per OA type")
ap.add_argument("--unclear", action="store_true", help="also census the EN/EA/VUM efferents whose transmitter is 'unclear'")
args = ap.parse_args()

d = np.load(args.brain, allow_pickle=True)
ty, sc, side, nt, sign = (d[k].astype(str) if d[k].dtype.kind in "US" else d[k] for k in ("type", "sc", "side", "nt", "sign"))
bid, pre, post, w = d["bodyId"], d["pre"], d["post"], d["w"]
N = len(ty)
try:
    from fly_afterlife.receptors import annotations
    A = annotations().set_index("bodyId"); _ex = A["exitNerve"]; exitn = np.array([str(_ex.get(int(b))) if int(b) in A.index and isinstance(_ex.get(int(b)), str) else "" for b in bid])
except Exception as e:   # the annotation table is optional; the census runs on the npz alone
    print(f"(annotations unavailable: {e}; exit nerves not shown)"); exitn = np.array([""] * N)

is_oa = nt == "octopamine"
pref = np.any([np.char.startswith(ty, p) for p in ("EN", "EA", "OA")], axis=0) | (np.char.find(ty, "VUM") >= 0)
sel = is_oa | (pref & (nt == "unclear") & args.unclear)
print(f"{args.brain}: {N} cells, {len(w)} edges, {int(w.sum())} synapses")
print(f"octopaminergic by consensus nt: {int(is_oa.sum())} cells; superclasses {dict(collections.Counter(sc[is_oa]))}")
print(f"EN/EA/OA/VUM by type prefix: {int(pref.sum())} cells, their nt {dict(collections.Counter(nt[pref]))}")
print(f"the engine's sign on the octopaminergic cells' outputs: {dict(collections.Counter(sign[is_oa].tolist()))} (0 = their synapses deliver nothing)\n")

in_syn = np.bincount(post, weights=w, minlength=N); out_syn = np.bincount(pre, weights=w, minlength=N)
out_to_oa = np.bincount(pre[is_oa[post]], weights=w[is_oa[post]], minlength=N)
sgn = lambda i: {1: "+", -1: "-", 0: "0"}.get(int(sign[i]), "?")

print("per type (cells: side / exit nerve / in / out):")
for t in sorted(set(ty[sel])):
    cells = np.flatnonzero(sel & (ty == t))
    print(f"\n{t}  n={len(cells)}  nt={nt[cells[0]]}  sc={sc[cells[0]]}")
    for i in cells:
        print(f"   {int(bid[i])}  {side[i] or '?'}  exit {exitn[i] or '-':10s}  in {int(in_syn[i]):5d}  out {int(out_syn[i]):4d} (onto OA cells {int(out_to_oa[i])})")
    m = np.isin(post, cells); c = collections.Counter()
    for p_, w_ in zip(pre[m], w[m]): c[(ty[p_], nt[p_], sgn(p_))] += int(w_)
    tot = sum(c.values())
    for (pt, pn, ps), n_ in c.most_common(args.top):
        print(f"      <- {pt:12s} {n_:5d} syn ({100 * n_ / max(tot, 1):4.1f} %)  {pn} {ps}")
    mo = np.isin(pre, cells); co = collections.Counter()
    for q_, w_ in zip(post[mo], w[mo]): co[(ty[q_], sc[q_])] += int(w_)
    if co: print("      -> " + ", ".join(f"{qt} ({qs}) {n_}" for (qt, qs), n_ in co.most_common(4)))

print("\n\ndescending neurons onto the octopaminergic cells (synapses; per target type):")
m = is_oa[post] & (sc[pre] == "descending_neuron"); c = collections.defaultdict(collections.Counter)
for p_, q_, w_ in zip(pre[m], post[m], w[m]): c[(ty[p_], nt[p_])][f"{ty[q_]}{side[q_]}"] += int(w_)
for (pt, pn), tg in sorted(c.items(), key=lambda kv: -sum(kv[1].values())):
    print(f"   {pt:10s} {pn:13s} {sum(tg.values()):5d}   " + ", ".join(f"{k} {v}" for k, v in tg.most_common(8)))

print("\ncord cells (not DNs) onto the octopaminergic cells, top 15 types (synapses, nt, sign, n targets):")
m = is_oa[post] & (sc[pre] != "descending_neuron"); c = collections.Counter(); tg = collections.defaultdict(set)
for p_, q_, w_ in zip(pre[m], post[m], w[m]): c[(ty[p_], nt[p_], sgn(p_), sc[p_])] += int(w_); tg[ty[p_]].add(ty[q_])
for (pt, pn, ps, psc), n_ in c.most_common(15):
    print(f"   {pt:12s} {pn:13s} {ps}  {psc:18s} {n_:5d}   onto {','.join(sorted(tg[pt]))[:70]}")

print("\nthe leg octopamine cells (EN00B008) and the walking command, directly:")
for dn in ("DNg100", "DNp68"):
    for tgt in ("EN00B008",):
        m = (ty[pre] == dn) & (ty[post] == tgt)
        print(f"   {dn} -> {tgt}: {int(w[m].sum())} synapses over {int(m.sum())} edges " + ", ".join(f"[{side[p_]}->{int(bid[q_])}{side[q_]} {int(w_)}]" for p_, q_, w_ in zip(pre[m], post[m], w[m])))
