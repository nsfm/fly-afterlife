"""
transplant.py - flyvis's learned physiology on the real per-cell optic lobe of the male fly.

    uv run python seam/transplant.py --test gratings [--rescale none|pair] [--dt 0.005]
    uv run python seam/transplant.py --stims loom_left recede_left ... --out seam/tx   (saves T4/T5 per cell)

NODES
  real: every ol_graph.npz cell except real photoreceptors (13% traced; retina is outside
        the volume) and CT1 (see below). fvtype gives its flyvis parameters.
  virtual photoreceptors: R1..R6 per retinal column (eye_geom), wired to that column's
        cells with flyvis's own R->target counts at offset (0,0). labelled gap-fill.
  CT1 compartments: CT1(M10) and CT1(Lo1) per column; each real CT1 edge is moved to
        the compartment of its partner's column, layer by partner type (T4/Mi/C -> M10,
        T5/Tm -> Lo1). what flyvis does; what the biology says (Meier & Borst 2019).
EDGES  weight = sign(pair) * count * strength(pair) [* rescale(pair)]. pairs flyvis has no
       parameters for are dropped (counted). --rescale pair multiplies by
       flyvis_syn_per_target / malecns_syn_per_target, clipped to [0.2, 5].
DYNAMICS  tau dv/dt = -v + bias + sum w * relu(v_pre) + x   (flyvis PPNeuronIGRSynapses),
       euler, rate 1/max(tau, dt) as flyvis. 1 s of grey to steady state first.
"""
import sys, json, argparse, time, numpy as np, pandas as pd, torch
sys.path.insert(0, "seam"); sys.path.insert(0, "ref/flybrain/scripts")
import flyvis
from omma import Eye, Scene
ap = argparse.ArgumentParser(); ap.add_argument("--test", default=None); ap.add_argument("--stims", nargs="*", default=[])
ap.add_argument("--rescale", default="none"); ap.add_argument("--dt", type=float, default=0.005); ap.add_argument("--fps", type=int, default=100)
ap.add_argument("--diag", action="store_true"); ap.add_argument("--homeostat", type=int, default=0, help="N iterations of per-type bias correction so each type rests (grey) where flyvis rests"); ap.add_argument("--speed", type=float, default=60.0); ap.add_argument("--record", nargs="*", default=[]); ap.add_argument("--gain", type=float, default=1.0, help="global scale on every weight (labelled fudge; see spectral radius)"); ap.add_argument("--out", default="seam/tx"); ap.add_argument("--geom", default="seam/eye_geom.npz"); args = ap.parse_args()
dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ---------------------------------------------------------------- data
g = np.load("seam/ol_graph.npz"); P = json.load(open("seam/flyvis_params.json")); spec = json.load(open(flyvis.connectome_file))
pc = pd.read_csv("seam/pair_counts.csv")
geom = np.load(args.geom); eye = Eye(args.geom)
colkey = {(str(s), int(a), int(b)): i for i, (s, a, b) in enumerate(zip(geom["side"], geom["hex1"], geom["hex2"]))}
d = np.load("brain_whole.npz"); bid_all = d["bodyId"]; cols = np.load("seam/columns_all.npz")
cell_col = {int(bid_all[i]): colkey.get((str(s), int(a), int(b)), -1) for i, s, a, b in zip(cols["idx"], cols["side"], cols["hex1"], cols["hex2"])}
bid = g["bodyId"]; fvt = g["fvtype"].astype(str); ty = g["type"].astype(str); side = g["side"].astype(str); pre, post, w = g["pre"], g["post"], g["w"].astype(np.float32)
col_of = np.array([cell_col.get(int(b), -1) for b in bid])
strength = {k: v["strength"] for k, v in P["edges"].items()}; sign = {k: v["sign"] for k, v in P["edges"].items()}
resc = {f"{r.s}->{r.t}": float(np.clip(r.flyvis_syn_per_target / r.malecns_syn_per_target, 0.2, 5.0)) for r in pc.itertuples() if r.malecns_syn_per_target == r.malecns_syn_per_target and r.malecns_syn_per_target > 0}

# ---------------------------------------------------------------- nodes
keep = ~np.isin(ty, ["R1-R6", "CT1"])
n_real = int(keep.sum()); real_idx = np.flatnonzero(keep); remap = np.full(len(bid), -1); remap[real_idx] = np.arange(n_real)
node_type = list(fvt[real_idx]); node_side = list(side[real_idx]); node_col = list(col_of[real_idx]); node_bid = list(bid[real_idx])
ncol = len(colkey); col_side = geom["side"]
# virtual R1..R6 per column
r_base = n_real
NR = 8   # R1..R6 (motion path) AND R7, R8 (colour path; in flyvis they carry the tonic drive into Mi1/Mi4)
for c in range(ncol):
    for k in range(1, NR + 1):
        node_type.append(f"R{k}"); node_side.append(str(col_side[c])); node_col.append(c); node_bid.append(-1)
# CT1 compartments per column: index = ct_base + 2*c + (0: M10, 1: Lo1)
ct_base = len(node_type)
for c in range(ncol):
    for layer in ("CT1(M10)", "CT1(Lo1)"):
        node_type.append(layer); node_side.append(str(col_side[c])); node_col.append(c); node_bid.append(-2)
N = len(node_type); node_type = np.array(node_type); node_col = np.array(node_col); node_side = np.array(node_side)
tau = np.array([P["nodes"][t]["tau_s"] for t in node_type], np.float32); bias = np.array([P["nodes"][t]["bias"] for t in node_type], np.float32)
print(f"nodes: {n_real} real + {NR*ncol} virtual R + {2*ncol} CT1 compartments = {N}")

# ---------------------------------------------------------------- edges
E_pre, E_post, E_w = [], [], []; dropped = {}
def add(p, q, count, spre, spost):
    key = f"{spre}->{spost}"
    if key not in strength: dropped[key] = dropped.get(key, 0) + 1; return
    wt = sign[key] * count * strength[key] * (resc.get(key, 1.0) if args.rescale == "pair" else 1.0)
    E_pre.append(p); E_post.append(q); E_w.append(wt)
ct_ids = set(np.flatnonzero(ty == "CT1").tolist()); r_ids = set(np.flatnonzero(ty == "R1-R6").tolist())
M10 = lambda t: t.startswith(("T4", "Mi", "C2", "C3", "Tm3", "L", "TmY")) ; layer_of = lambda t: 0 if M10(t) else 1
for p, q, c in zip(pre, post, w):
    p, q = int(p), int(q)
    if p in r_ids or q in r_ids: continue
    if p in ct_ids and q in ct_ids: continue
    if p in ct_ids:
        cc = col_of[q]
        if cc < 0: continue
        lay = layer_of(fvt[q]); add(ct_base + 2 * cc + lay, remap[q], c, ["CT1(M10)", "CT1(Lo1)"][lay], fvt[q]); continue
    if q in ct_ids:
        cc = col_of[p]
        if cc < 0: continue
        lay = layer_of(fvt[p]); add(remap[p], ct_base + 2 * cc + lay, c, fvt[p], ["CT1(M10)", "CT1(Lo1)"][lay]); continue
    add(remap[p], remap[q], c, fvt[p], fvt[q])
n_real_edges = len(E_pre)
# virtual R edges from flyvis spec at offset (0,0)
r_spec = {}
for e in spec["edges"]:
    if e["src"] in [f"R{k}" for k in range(1, NR + 1)]:
        n0 = sum(o[1] for o in e["offsets"] if tuple(o[0]) == (0, 0)) if e["offsets"] and isinstance(e["offsets"][0][0], list) else sum(o[2] for o in e["offsets"] if (o[0], o[1]) == (0, 0))
        if n0 > 0: r_spec[(e["src"], e["tar"])] = n0
by_col_type = {}
for i in range(n_real):
    if node_col[i] >= 0: by_col_type.setdefault((node_col[i], node_type[i]), []).append(i)
for c in range(ncol):
    for k in range(1, NR + 1):
        rn = r_base + NR * c + (k - 1)
        for (src, tar), n0 in r_spec.items():
            if src != f"R{k}": continue
            for j in by_col_type.get((c, tar), []): add(rn, j, n0, src, tar)
print("R spec (0,0) counts:", {k: v for k, v in r_spec.items() if k[0] in ("R1", "R7", "R8")})
print(f"edges: {n_real_edges} real (+CT1 compartments) + {len(E_pre) - n_real_edges} virtual R = {len(E_pre)}; dropped pairs without flyvis params: {sum(dropped.values())} edges over {len(dropped)} pairs")
print("  biggest dropped:", sorted(dropped.items(), key=lambda x: -x[1])[:6])
Ew = np.array(E_w, np.float32) * args.gain; print(f"weights: finite {np.isfinite(Ew).all()}, |w| max {np.abs(Ew).max():.3f}, mean {np.abs(Ew).mean():.4f}; in-degree max {np.bincount(E_post).max()}; per-node |in| max {pd.Series(np.abs(Ew)).groupby(np.array(E_post)).sum().max():.2f}")
W = torch.sparse_coo_tensor(torch.tensor([E_post, E_pre]), torch.tensor(Ew, dtype=torch.float32), (N, N)).coalesce().to_sparse_csr().to(dev)
tau_t = torch.tensor(np.maximum(tau, args.dt), device=dev); bias_t = torch.tensor(bias, device=dev)
r_nodes = torch.arange(r_base, r_base + NR * ncol, device=dev); r_col = torch.tensor(np.repeat(np.arange(ncol), NR), device=dev)

# ---------------------------------------------------------------- sim
def run(lum_frames, v0=None, record_types=("T4a", "T4b", "T4c", "T4d", "T5a", "T5b", "T5c", "T5d")):
    record_types = tuple(record_types) + tuple(args.record)
    """lum_frames: (T, ncol) luminance. returns v0 (final state), rec {type: (T, n_cells_of_type)} for real cells."""
    v = bias_t.clone() if v0 is None else v0.clone(); sub = max(1, int(round(1 / args.fps / args.dt)))
    rec_idx = {t: torch.tensor(np.flatnonzero(node_type == t), device=dev) for t in record_types}
    rec = {t: torch.zeros((len(lum_frames), len(ix)), device=dev) for t, ix in rec_idx.items()}
    x = torch.zeros(N, device=dev)
    for f, lum in enumerate(lum_frames):
        x[r_nodes] = torch.tensor(lum, device=dev, dtype=torch.float32)[r_col]
        for _ in range(sub):
            I = W @ torch.relu(v)
            v = v + (args.dt / tau_t) * (-v + bias_t + I + x)
        if args.diag and (f in (0, 50, 99) or not torch.isfinite(v).all()):
            am = int(torch.nan_to_num(v.abs(), nan=1e30).argmax()); print(f"    frame {f}: max|v| {v.abs().max().item():.3g} at node {am} ({node_type[am]}, col {node_col[am]}), mean relu(v) {torch.relu(v).mean().item():.3g}, finite {torch.isfinite(v).all().item()}", flush=True)
            if not torch.isfinite(v).all(): break
        for t, ix in rec_idx.items(): rec[t][f] = v[ix]
    return v, {t: r.cpu().numpy() for t, r in rec.items()}, rec_idx
def steady(lum, seconds=1.0):
    v, _, _ = run(np.repeat(lum[None], int(seconds * args.fps), 0)); return v

if args.homeostat:
    import os
    if not os.path.exists("seam/flyvis_rest.json"):
        from flyvis import NetworkView
        net = NetworkView("flow/0000/000").init_network(); net.eval()
        with torch.no_grad(): st = net.steady_state(1.0, 1 / args.fps, 1, value=0.5)
        fa = st.nodes.activity.detach().cpu().numpy().ravel(); ft = net.connectome.nodes.type[:].astype(str)
        json.dump({t: float(fa[ft == t].mean()) for t in sorted(set(ft))}, open("seam/flyvis_rest.json", "w"), indent=1); del net
    target = json.load(open("seam/flyvis_rest.json"))
    type_idx = {t: torch.tensor(np.flatnonzero(node_type == t), device=dev) for t in set(node_type) if not t.startswith("R")}
    for it in range(args.homeostat):
        v_grey = steady(np.full(ncol, 0.5, np.float32)) if it == 0 else run(np.repeat(np.full(ncol, 0.5, np.float32)[None], 50, 0), v_grey)[0]
        err = {t: target[t] - v_grey[ix].mean().item() for t, ix in type_idx.items()}
        for t, ix in type_idx.items(): bias_t[ix] += 0.5 * err[t]
        worst = sorted(err.items(), key=lambda x: -abs(x[1]))[:4]
        print(f"  homeostat {it}: mean|err| {np.mean([abs(e) for e in err.values()]):.3f}  worst {[(t, round(e, 2)) for t, e in worst]}", flush=True)
    bias_np = bias_t.cpu().numpy(); shift = {t: float(bias_np[ix.cpu().numpy()].mean() - P["nodes"][t]["bias"]) for t, ix in type_idx.items()}
    print("  bias shifts (transplant - flyvis), largest:", sorted(shift.items(), key=lambda x: -abs(x[1]))[:8])
t0 = time.time(); az = np.degrees(np.arctan2(eye.dir0[:, 1], eye.dir0[:, 0])); el = np.degrees(np.arcsin(np.clip(eye.dir0[:, 2], -1, 1)))
v_grey = steady(np.full(ncol, 0.5, np.float32)); print(f"steady state on grey in {time.time()-t0:.1f}s; N={N}")

if args.test == "decompose":
    # resting input to each target type, decomposed by source type: transplant (L eye) vs flyvis (central column)
    from flyvis import NetworkView
    net = NetworkView("flow/0000/000").init_network(); net.eval(); pp = net._param_api()
    fn = net.connectome.nodes; ft = fn.type[:].astype(str); fu = fn.u[:]; fvv = fn.v[:]
    fe = net.connectome.edges; fsrc = fe.source_index[:]; ftgt = fe.target_index[:]; fw = pp.edges.weight.detach().cpu().numpy()
    with torch.no_grad(): st = net.steady_state(1.0, 1 / args.fps, 1, value=0.5)
    fv_rest = st.nodes.activity.detach().cpu().numpy().ravel(); fr = np.maximum(fv_rest, 0)
    Wc = W.to_sparse_coo().coalesce(); ri, ci = Wc.indices().cpu().numpy(); wv = Wc.values().cpu().numpy()
    vr = torch.relu(v_grey).cpu().numpy(); tx_in = wv * vr[ci]
    for tgt in ["Mi1", "Mi4", "Mi9", "Tm3", "L5", "T4a", "Tm9", "CT1(M10)", "T5a"]:
        # flyvis: central-ish targets (|u|,|v| <= 3) to avoid the rim
        mt = (ft == tgt) & (np.abs(fu) <= 3) & (np.abs(fvv) <= 3); tgt_ids = np.flatnonzero(mt)
        me = np.isin(ftgt, tgt_ids); contrib = pd.Series(fw[me] * fr[fsrc[me]]).groupby(ft[fsrc[me]]).sum() / max(len(tgt_ids), 1)
        # transplant: L eye targets with a column
        tt_ids = np.flatnonzero((node_type == tgt) & (node_side == "L") & (node_col >= 0)); me2 = np.isin(ri, tt_ids)
        contrib2 = pd.Series(tx_in[me2]).groupby(node_type[ci[me2]]).sum() / max(len(tt_ids), 1)
        both = pd.concat([contrib.rename("flyvis"), contrib2.rename("transplant")], axis=1).fillna(0.0)
        both["diff"] = both.transplant - both.flyvis; both = both.reindex(both["diff"].abs().sort_values(ascending=False).index)
        print(f"\n{tgt}: rest flyvis {fv_rest[mt].mean():+.3f} (bias {P['nodes'][tgt]['bias']:+.3f}, total in {contrib.sum():+.3f})  transplant {v_grey[torch.tensor(tt_ids, device=dev)].mean().item():+.3f} (total in {contrib2.sum():+.3f})")
        print(both.head(7).round(3).to_string())
    raise SystemExit
if args.test == "probe":
    Wc = W.to_sparse_coo().coalesce(); rows = Wc.indices()[0]
    indeg_R = torch.bincount(rows, minlength=N)[r_base:r_base + NR * ncol]
    print("in-degree of virtual R nodes: max", int(indeg_R.max()), "nonzero", int((indeg_R > 0).sum()))
    r1 = np.flatnonzero(node_type == "R1"); vr = v_grey[torch.tensor(r1, device=dev)].cpu().numpy()
    print(f"R1 after grey steady: mean {vr.mean():.3f} sd {vr.std():.3f} min {vr.min():.3f} max {vr.max():.3f}; bias R1 {P['nodes']['R1']['bias']:.3f}; expected bias+0.5 = {P['nodes']['R1']['bias']+0.5:.3f}")
    print("r_col first 12:", r_col[:12].tolist(), " r_nodes first 3:", r_nodes[:3].tolist(), " node_type there:", node_type[r_base:r_base+3].tolist())
    fr = np.where(((az - 30.0) // 15.0) % 2 == 0, 0.2, 0.8).astype(np.float32)
    v1, rec, rec_idx = run(np.repeat(fr[None], 30, 0), v_grey, record_types=("R1", "L1"))
    vr = v1[torch.tensor(r1, device=dev)].cpu().numpy(); print(f"R1 after 0.3 s of static grating: mean {vr.mean():.3f} sd {vr.std():.3f} min {vr.min():.3f} max {vr.max():.3f}  (expected two values: bias+0.2 and bias+0.8)")
    l1 = rec["L1"][-1]; print(f"L1 then: mean {l1.mean():.3f} sd {l1.std():.3f}")
    raise SystemExit
if args.test == "gratings":
    # square-wave stripes, 30 deg period (6 columns), SPEED deg/s, on a cylinder (az) or stack (el); 1 s grey then 1 s motion
    types = ["T4a", "T4b", "T4c", "T4d", "T5a", "T5b", "T5c", "T5d"]; SPEED = args.speed
    res = {}
    for name, coord, sgn in (("+az", az, +1), ("-az", az, -1), ("+el", el, +1), ("-el", el, -1)):
        frames = np.full((args.fps, ncol), 0.5, np.float32)
        frames = np.concatenate([frames, np.stack([np.where(((coord - sgn * SPEED * t / args.fps) // 15.0) % 2 == 0, 0.2, 0.8).astype(np.float32) for t in range(args.fps)])])
        chain_types = ("R1","L1","L2","L3","L4","L5","C2","C3","T1","Mi1","Tm3","Mi4","Mi9","Tm1","Tm2","Tm4","Tm9","CT1(M10)","CT1(Lo1)")
        _, rec, rec_idx = run(frames, v_grey, record_types=tuple(types) + chain_types)
        if name == "+az":
            print("transplant chain under +az grating (L eye): rest / during-mean / temporal modulation / frac of cells with rest>0")
            for t in chain_types + ("T4a", "T4b", "T5a", "T5b"):
                ix = rec_idx[t].cpu().numpy(); ms = node_side[ix] == "L"; a = rec[t][:, ms]
                print(f"  {t:9s} rest {a[20:args.fps].mean():+.3f}  during {a[args.fps+20:].mean():+.3f}  mod {a[args.fps+20:].std(0).mean():.3f}  active {np.mean(a[20:args.fps].mean(0) > 0):.2f}   n={ms.sum()}")
        for s in "LR":
            for t in rec:
                ix = rec_idx[t].cpu().numpy(); ms = node_side[ix] == s; a = rec[t][:, ms]
                res[(name, s, t)] = (a[args.fps + 20:].mean() - a[20:args.fps].mean(), a[args.fps + 20:].std(0).mean())
    print(f"\nmean shift (during - rest) and temporal modulation (mean over cells of sd over time), gain {args.gain} rescale {args.rescale} speed {SPEED} deg/s")
    print(f"{'type':5s} {'eye':3s} " + "".join(f"{n:>14s}" for n in ("+az", "-az", "+el", "-el")) + "    DS(az)=(+az)-(-az)  DS(el)")
    for t in ["Mi1", "Tm3", "Mi9", "Mi4", "Tm1", "Tm9"] + types:
        for s in "LR":
            r = [res[(n, s, t)] for n in ("+az", "-az", "+el", "-el")]
            print(f"{t:5s} {s:3s} " + "".join(f"{m:+7.3f}/{md:5.3f} " for m, md in r) + f"   {r[0][0]-r[1][0]:+.3f}   {r[2][0]-r[3][0]:+.3f}")
    print("biology: +az motion is front-to-back on the LEFT eye (T4a/T5a should win there) and back-to-front on the RIGHT (T4b/T5b); +el up = T4c/T5c, -el = T4d/T5d")
for stim in args.stims:
    sys.path.insert(0, "seam"); import world_flyvis as wf  # reuse its frame_scene? it parses args; inline instead
    raise SystemExit("stims: not wired yet")
