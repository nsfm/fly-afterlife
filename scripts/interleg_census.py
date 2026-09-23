"""interleg_census.py - which cord interneurons carry one leg's signal to another leg's motor side (09-23; docs/physiology/interleg.md).

the question after the lift read: each leg makes its own five-hertz reflex bout and the six are uncoupled. which cells in the file would
couple them? a census, no run.

    legs of the motor neurons: world/legmn.npz (indices into brain_whole.npz, mapped by bodyId into brain_cord.npz)
    legs of the sensory cells: world/leg_senses.csv, column `leg` (annotated by nerve, or inferred by wiring where the nerve is missing)
    premotor cells (one synapse upstream of the leg MNs): every non-sensory, non-motor cell with >= PM_MIN synapses onto leg MNs. a
        premotor cell is a LEG's (one-hot) only if >= PM_LOCAL (0.8) of its MN output is on that leg; multi-leg premotor cells carry no leg
        (they are candidates themselves; letting them carry their mixed vector smears every downstream cell into "interleg": --pm-local 0).
        the leg neuropil of everything else is inferred only through these.
    a candidate: sc == vnc_intrinsic. for each candidate X:
        out[j] = synapses X -> leg-j MNs + sum over X's premotor targets c of w(X->c) * share_c[j]
        in[i]  = synapses leg-i sensory cells -> X + sum over X's premotor inputs c of w(c->X) * share_c[i]
        flow[i, j] = in[i] / sum(in) * out[j]      (X's leg output, split by where its leg input came from)
        interleg = sum of flow[i, j] for i != j    (synapse-weighted: output that carries another leg's signal)
    pairs are contralateral (same segment, other side: lf-rf, lm-rm, lh-rh), ipsilateral (same side, neighbouring or not: lf-lm,
    lm-lh, lf-lh) or diagonal (other side AND other segment). a cell's class: contralateral or ipsilateral if >= 70 % of its interleg
    flow is that kind, else both (diagonal counts toward both).
    cells with leg output but no leg input (driven only by DNs, ANs or unassigned cells) cannot be given a from-leg: counted, not ranked.

writes world/interleg.csv (one row per cell) and prints the top types.
    uv run python scripts/interleg_census.py [--top 40] [--pm-min 10]
"""
import argparse, csv, re, numpy as np

ap = argparse.ArgumentParser(); ap.add_argument("--top", type=int, default=40); ap.add_argument("--pm-min", type=int, default=10)
ap.add_argument("--out", default="world/interleg.csv"); ap.add_argument("--min-leg-out", type=float, default=20.0)
ap.add_argument("--pm-local", type=float, default=0.8, help="a premotor cell counts as one leg's only if >= this share of its MN output is on that "
                "leg (0 = every premotor cell carries its full leg vector, which smears multi-leg premotor cells into everything downstream)")
args = ap.parse_args()

LEG6 = ["lf", "lm", "lh", "rf", "rm", "rh"]
SIDE = {l: l[0] for l in LEG6}; SEG = {l: l[1] for l in LEG6}
def kind(a, b):
    if SEG[a] == SEG[b]: return "contra"
    if SIDE[a] == SIDE[b]: return "ipsi"
    return "diag"

b = np.load("brain_cord.npz", allow_pickle=True)
N = len(b["bodyId"]); bid = b["bodyId"].astype(np.int64); typ = b["type"].astype(str); sc = b["sc"].astype(str)
nt = b["nt"].astype(str); sign = b["sign"].astype(int); side = b["side"].astype(str)
pre, post, w = b["pre"].astype(np.int64), b["post"].astype(np.int64), b["w"].astype(np.float64)
pos = {int(x): i for i, x in enumerate(bid)}

# ---- the leg motor neurons (A0) and the leg sensory cells (S0), one-hot over the six legs
wb = np.load("brain_whole.npz", allow_pickle=True)["bodyId"].astype(np.int64); lm = np.load("world/legmn.npz")
A0 = np.zeros((N, 6))
for g, L in (("fl", "f"), ("ml", "m"), ("hl", "h")):
    for s in "LR":
        for i in lm[f"{g}_{s}"]:
            j = pos.get(int(wb[i]))
            if j is not None: A0[j, LEG6.index(s.lower() + L)] = 1.0
S0 = np.zeros((N, 6)); n_sens_leg = 0
for r in csv.DictReader(open("world/leg_senses.csv")):
    if r["leg"] in LEG6 and int(r["bodyId"]) in pos: S0[pos[int(r["bodyId"])], LEG6.index(r["leg"])] = 1.0; n_sens_leg += 1
isMN = A0.sum(1) > 0; isSens = np.char.find(sc, "sensory") >= 0

# ---- premotor cells: leg vector = share of MN output per leg
toMN = np.zeros((N, 6)); np.add.at(toMN, pre, w[:, None] * A0[post])
pm_ok = (toMN.sum(1) >= args.pm_min) & ~isMN & ~isSens
P = np.zeros((N, 6)); P[pm_ok] = toMN[pm_ok] / toMN[pm_ok].sum(1, keepdims=True)
if args.pm_local > 0:
    loc = P.max(1) >= args.pm_local; oh = np.zeros_like(P); oh[np.arange(N), P.argmax(1)] = 1.0
    P = np.where(loc[:, None], oh, 0.0)
n_pm_local = int((P.sum(1) > 0).sum())

# ---- per cell: leg output (onto MNs + premotor), leg input (from sensory + premotor)
self_ = pre == post
OUT = np.zeros((N, 6)); np.add.at(OUT, pre[~self_], w[~self_, None] * (A0 + P)[post[~self_]])
IN = np.zeros((N, 6)); np.add.at(IN, post[~self_], w[~self_, None] * (S0 + P)[pre[~self_]])
OUT_MN = toMN
TOT_OUT = np.bincount(pre, weights=w, minlength=N)

def hemilineage(t):
    m = re.match(r"^IN(\d{2}[AB])(?:\.(\d{2}[AB]))?", t)
    if m: return m.group(1) + ("/" + m.group(2) if m.group(2) else "")
    if t.startswith("INXXX"): return "XXX (unassigned)"
    m = re.match(r"^IN(\d{2}X)", t)
    if m: return m.group(1)
    return "-"

cand = np.flatnonzero((sc == "vnc_intrinsic") & (OUT.sum(1) >= args.min_leg_out))
rows = []; no_input = []
for x in cand:
    o = OUT[x]; i_ = IN[x]
    if i_.sum() <= 0: no_input.append(x); continue
    F = np.outer(i_ / i_.sum(), o)
    il = F.sum() - np.trace(F)
    k = {"contra": 0.0, "ipsi": 0.0, "diag": 0.0}; pairs = []
    for a in range(6):
        for c in range(6):
            if a != c and F[a, c] > 0: k[kind(LEG6[a], LEG6[c])] += F[a, c]; pairs.append((F[a, c], f"{LEG6[a]}->{LEG6[c]}"))
    pairs.sort(reverse=True)
    if il <= 0: cls_ = "-"
    elif k["contra"] >= 0.7 * il: cls_ = "contralateral"
    elif k["ipsi"] >= 0.7 * il: cls_ = "ipsilateral"
    else: cls_ = "both"
    from_l = [LEG6[a] for a in np.argsort(-i_) if i_[a] >= 0.15 * i_.sum()]
    to_l = [LEG6[a] for a in np.argsort(-o) if o[a] >= 0.15 * o.sum()]
    rows.append(dict(type=typ[x], bodyId=int(bid[x]), hemilineage=hemilineage(typ[x]), side=side[x], nt=nt[x], sign=int(sign[x]),
                     from_legs="|".join(from_l), to_legs="|".join(to_l), interleg_syn=round(il, 1), leg_out_syn=round(o.sum(), 1),
                     mn_direct_syn=round(OUT_MN[x].sum(), 1), total_out_syn=int(TOT_OUT[x]),
                     frac_interleg=round(il / max(TOT_OUT[x], 1), 3), contra_syn=round(k["contra"], 1), ipsi_syn=round(k["ipsi"], 1),
                     diag_syn=round(k["diag"], 1), top_pairs=" ".join(p for f, p in pairs[:3] if f >= 0.1 * il), **{"class": cls_}))

rows.sort(key=lambda r: -r["interleg_syn"])
cols = ["type", "bodyId", "hemilineage", "side", "nt", "sign", "from_legs", "to_legs", "interleg_syn", "leg_out_syn", "mn_direct_syn",
        "total_out_syn", "frac_interleg", "contra_syn", "ipsi_syn", "diag_syn", "top_pairs", "class"]
with open(args.out, "w", newline="") as f:
    wr = csv.DictWriter(f, fieldnames=cols); wr.writeheader(); [wr.writerow(r) for r in rows]

# ---- by type
T = {}
for r in rows:
    t = T.setdefault(r["type"], dict(n=0, il=0.0, out=0.0, legout=0.0, c=0.0, i=0.0, d=0.0, pairs={}, sign=set(), nt=set(), hl=r["hemilineage"], mn=0.0))
    t["n"] += 1; t["il"] += r["interleg_syn"]; t["out"] += r["total_out_syn"]; t["legout"] += r["leg_out_syn"]; t["mn"] += r["mn_direct_syn"]
    t["c"] += r["contra_syn"]; t["i"] += r["ipsi_syn"]; t["d"] += r["diag_syn"]; t["sign"].add(r["sign"]); t["nt"].add(r["nt"])
    for p in r["top_pairs"].split():
        a, c = p.split("->"); key = f"{a}->{c}"; t["pairs"][key] = t["pairs"].get(key, 0) + 1
def tcls(t):
    il = t["c"] + t["i"] + t["d"]
    return "contralateral" if t["c"] >= 0.7 * il else "ipsilateral" if t["i"] >= 0.7 * il else "both"
def generic(pairs):
    """the type's per-cell pairs, folded by mirror (lm->rm and rm->lm -> m<->m contra)"""
    g = {}
    for p, n in pairs.items():
        a, c = p.split("->"); k = kind(a, c)
        lab = f"{a[1]}<->{c[1]} {k}" if k == "contra" else f"{a[1]}->{c[1]} {k}"
        g[lab] = g.get(lab, 0) + n
    return ", ".join(f"{k} x{n}" for k, n in sorted(g.items(), key=lambda kv: -kv[1])[:3])
ranked = sorted(T.items(), key=lambda kv: -kv[1]["il"])
SG = {1: "+ACh", -1: "-", 0: "?"}
print(f"interleg census: {N} cells; leg MNs {int(isMN.sum())}; leg sensory cells with a leg {int((S0.sum(1) > 0).sum())}; premotor (>= {args.pm_min} syn onto leg MNs) {int(pm_ok.sum())}, of them leg-local (>= {args.pm_local:.0%} of MN output on one leg) {n_pm_local}")
print(f"candidates (vnc_intrinsic, leg output >= {args.min_leg_out:.0f} syn): {len(cand)}; ranked (with leg input) {len(rows)}; "
      f"leg output but no leg input (not assigned a from-leg): {len(no_input)} cells, {sum(OUT[x].sum() for x in no_input):.0f} leg-output syn")
tot_il = sum(r["interleg_syn"] for r in rows)
print(f"total interleg flow {tot_il:.0f} syn: contra {sum(r['contra_syn'] for r in rows) / tot_il:.2f}, ipsi {sum(r['ipsi_syn'] for r in rows) / tot_il:.2f}, diag {sum(r['diag_syn'] for r in rows) / tot_il:.2f}")
print(f"\n{'#':>3s} {'type':16s} {'hl':8s} {'n':>2s} {'sign':>4s} {'interleg':>8s} {'frac out':>8s} {'frac leg':>8s} {'MN%':>4s} {'class':13s} pairs (cells)")
for k, (t, v) in enumerate(ranked[:args.top], 1):
    sg = "/".join(SG[s] for s in sorted(v["sign"], reverse=True)); ntx = "/".join(sorted(v["nt"]))
    sg = sg if ntx != "glutamate" else "-Glu"
    print(f"{k:3d} {t:16s} {v['hl']:8s} {v['n']:2d} {sg:>4s} {v['il']:8.0f} {v['il'] / max(v['out'], 1):8.2f} {v['il'] / max(v['legout'], 1):8.2f} "
          f"{100 * v['mn'] / max(v['legout'], 1):4.0f} {tcls(v):13s} {generic(v['pairs'])}")
# hemilineage roll-up
H = {}
for t, v in T.items():
    h = H.setdefault(v["hl"], [0.0, 0.0, 0.0, 0.0]); h[0] += v["il"]; h[1] += v["c"]; h[2] += v["i"]; h[3] += v["d"]
print("\nby hemilineage (interleg syn; contra / ipsi / diag share):")
for h, (il, c, i, d) in sorted(H.items(), key=lambda kv: -kv[1][0])[:20]:
    print(f"  {h:18s} {il:9.0f}   {c / il:.2f} / {i / il:.2f} / {d / il:.2f}")

# ---- the silencing sets for the body read (docs/physiology/interleg.md), and matched random controls
def pick(key, share, k=12):
    return [t for t, v in sorted(T.items(), key=lambda kv: -kv[1][key]) if v[key] >= share * (v["c"] + v["i"] + v["d"]) and "," not in t][:k]
SETS = {"contra12": pick("c", 0.7), "ipsi12": pick("i", 0.7), "top12": [t for t, v in ranked[:12]]}
ntype = {t: int((typ == t).sum()) for t in set(typ)}
top200 = {t for t, _ in ranked[:200]}
pool = sorted(t for t in T if t not in top200 and "," not in t)   # a comma in a type name cannot pass through --silence (it splits on commas)
rng = np.random.default_rng(0)
print("\nsilencing sets (--silence), cells in brackets:")
for name, L in SETS.items(): print(f"  {name:9s} [{sum(ntype[t] for t in L):3d}] {','.join(L)}")
for d in range(3):
    target = sum(ntype[t] for t in SETS["top12"])
    for _ in range(2000):
        L = list(rng.choice(pool, 12, replace=False))
        if abs(sum(ntype[t] for t in L) - target) <= 4: break
    print(f"  control{d}  [{sum(ntype[t] for t in L):3d}] {','.join(L)}   (12 intrinsic types with leg output, outside the interleg top 200, seed 0)")
print(f"\nwrote {args.out} ({len(rows)} cells)")
