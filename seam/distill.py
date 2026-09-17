"""
distill.py - train the transplant to reproduce flyvis on the real wiring (student-teacher).

the teacher is flyvis model 000 on its lattice; the student is the transplant (flyvis dynamics on the
MaleCNS per-cell optic lobe) with learnable per-type-pair synapse strengths (604), per-type time constants
and biases (65 + 65) and per-type input scale. stimuli are synthetic (moving bars, gratings, expanding
discs, drifting dots) rendered on the flyvis lattice and mapped to our columns through the derived map
(front -> image-right, dorsal -> image-up). loss: MSE between student and teacher activity for every
cell type present in both, at mapped columns, over the clip, after each network's own grey rest is
subtracted (so we match responses, not operating points). no loom-specific target; the loom is the test.

    uv run python seam/distill.py --check          # feasibility: one clip forward+backward, timing, grad norms
    uv run python seam/distill.py --steps 300 --out seam/tx_distilled.npz
"""
import os, sys, json, time, argparse, numpy as np, torch
sys.path.insert(0, "seam"); os.environ.setdefault("FLYVIS_ROOT_DIR", "/home/nate/code/fly-afterlife/flyvis_data")
ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true"); ap.add_argument("--steps", type=int, default=200); ap.add_argument("--out", default="seam/tx_distilled.npz")
ap.add_argument("--clip", type=int, default=40); ap.add_argument("--fps", type=int, default=100); ap.add_argument("--dt", type=float, default=0.005); ap.add_argument("--lr", type=float, default=0.01); ap.add_argument("--eye", default="L"); args = ap.parse_args()
dev = torch.device("cuda")
import flyvis
from flyvis import NetworkView
from flyvis.datasets.rendering.eye import BoxEye
# ---------------- teacher
net = NetworkView("flow/0000/000").init_network(); net.eval()
nodes = net.connectome.nodes; ntype = nodes.type[:].astype(str); nu = nodes.u[:]; nv = nodes.v[:]
lattice = sorted({(u, v) for u in range(-15, 16) for v in range(max(-15, -15 - u), min(15, 15 - u) + 1)}); idx_of = {uv: i for i, uv in enumerate(lattice)}
teacher_types = sorted(set(ntype)); tt_idx = {t: np.flatnonzero(ntype == t) for t in teacher_types}
t_uv = {t: {(int(nu[j]), int(nv[j])): k for k, j in enumerate(tt_idx[t])} for t in teacher_types}   # per type: (u,v) -> column within that type's activity
eye = BoxEye(extent=15, kernel_size=13)
def teacher_run(hexmovie):
    with torch.no_grad(): la = net.simulate(hexmovie, dt=1 / args.fps, as_layer_activity=True)
    return {t: torch.as_tensor(np.asarray(getattr(la, t).squeeze(0)), device=dev) for t in teacher_types}
# ---------------- student graph (as transplant.py, real cells + virtual R1..R8 + CT1 compartments)
g = np.load("seam/ol_graph.npz"); P = json.load(open("seam/flyvis_params.json")); spec = json.load(open(flyvis.connectome_file))
import pandas as pd
pc = pd.read_csv("seam/pair_counts.csv"); geom = np.load("seam/eye_geom.npz")
colkey = {(str(s), int(a), int(b)): i for i, (s, a, b) in enumerate(zip(geom["side"], geom["hex1"], geom["hex2"]))}
d = np.load("brain_whole.npz"); bid_all = d["bodyId"]; cols = np.load("seam/columns_all.npz")
cell_col = {int(bid_all[i]): colkey.get((str(s), int(a), int(b)), -1) for i, s, a, b in zip(cols["idx"], cols["side"], cols["hex1"], cols["hex2"])}
bid = g["bodyId"]; fvt = g["fvtype"].astype(str); ty = g["type"].astype(str); side = g["side"].astype(str); pre, post, w = g["pre"], g["post"], g["w"].astype(np.float32)
col_of = np.array([cell_col.get(int(b), -1) for b in bid])
keep = ~np.isin(ty, ["R1-R6", "CT1"]) & (side == args.eye)      # one eye for training
real_idx = np.flatnonzero(keep); n_real = len(real_idx); remap = np.full(len(bid), -1); remap[real_idx] = np.arange(n_real)
node_type = list(fvt[real_idx]); node_col = list(col_of[real_idx])
eye_cols = np.flatnonzero(geom["side"] == args.eye); ncol = len(eye_cols); col_local = {int(c): i for i, c in enumerate(eye_cols)}
node_col = [col_local.get(int(c), -1) for c in node_col]
NR = 8; r_base = n_real
for c in range(ncol):
    for k in range(1, NR + 1): node_type.append(f"R{k}"); node_col.append(c)
ct_base = len(node_type)
for c in range(ncol):
    for layer in ("CT1(M10)", "CT1(Lo1)"): node_type.append(layer); node_col.append(c)
N = len(node_type); node_type = np.array(node_type); node_col = np.array(node_col)
type_names = sorted(set(node_type)); type_id = {t: i for i, t in enumerate(type_names)}; node_tid = np.array([type_id[t] for t in node_type])
pairs = sorted(P["edges"]); pair_id = {k: i for i, k in enumerate(pairs)}
E_pre, E_post, E_cnt, E_pair = [], [], [], []
def add(p, q, count, spre, spost):
    key = f"{spre}->{spost}"
    if key in pair_id: E_pre.append(p); E_post.append(q); E_cnt.append(count); E_pair.append(pair_id[key])
ct_ids = set(np.flatnonzero(ty == "CT1").tolist()); r_ids = set(np.flatnonzero(ty == "R1-R6").tolist())
layer_of = lambda t: 0 if t.startswith(("T4", "Mi", "C2", "C3", "Tm3", "L", "TmY")) else 1
for p, q, c in zip(pre, post, w):
    p, q = int(p), int(q)
    if p in r_ids or q in r_ids or (p in ct_ids and q in ct_ids): continue
    if p in ct_ids:
        if remap[q] < 0 or node_col[remap[q]] < 0: continue
        lay = layer_of(fvt[q]); add(ct_base + 2 * node_col[remap[q]] + lay, remap[q], c, ["CT1(M10)", "CT1(Lo1)"][lay], fvt[q]); continue
    if q in ct_ids:
        if remap[p] < 0 or node_col[remap[p]] < 0: continue
        lay = layer_of(fvt[p]); add(remap[p], ct_base + 2 * node_col[remap[p]] + lay, c, fvt[p], ["CT1(M10)", "CT1(Lo1)"][lay]); continue
    if remap[p] < 0 or remap[q] < 0: continue
    add(remap[p], remap[q], c, fvt[p], fvt[q])
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
            if src == f"R{k}":
                for j in by_col_type.get((c, tar), []): add(rn, j, n0, src, tar)
E_pre = torch.tensor(E_pre, device=dev); E_post = torch.tensor(E_post, device=dev); E_cnt = torch.tensor(E_cnt, dtype=torch.float32, device=dev); E_pair = torch.tensor(E_pair, device=dev)
resc = {f"{r.s}->{r.t}": float(np.clip(r.flyvis_syn_per_target / r.malecns_syn_per_target, 0.2, 5.0)) for r in pc.itertuples() if r.malecns_syn_per_target == r.malecns_syn_per_target and r.malecns_syn_per_target > 0}
pair_sign = torch.tensor([P["edges"][k]["sign"] for k in pairs], device=dev); pair_resc = torch.tensor([resc.get(k, 1.0) for k in pairs], device=dev)
# ---------------- learnable physiology (log-parametrised where positive)
log_strength = torch.nn.Parameter(torch.log(torch.tensor([P["edges"][k]["strength"] for k in pairs], device=dev) * 0.8 + 1e-6))
log_tau = torch.nn.Parameter(torch.log(torch.tensor([P["nodes"][t]["tau_s"] for t in type_names], device=dev)))
bias = torch.nn.Parameter(torch.tensor([P["nodes"][t]["bias"] for t in type_names], device=dev))
log_inscale = torch.nn.Parameter(torch.zeros(len(type_names), device=dev))
node_tid_t = torch.tensor(node_tid, device=dev); r_nodes = torch.arange(r_base, r_base + NR * ncol, device=dev); r_col = torch.tensor(np.repeat(np.arange(ncol), NR), device=dev)
adapt_mask = torch.tensor(~np.char.startswith(node_type, "R"), device=dev, dtype=torch.float32)
def forward(lum_frames, record):
    """lum_frames (T, ncol) tensor. returns dict type -> (T, n_cells) activity (real cells only)."""
    vals = pair_sign[E_pair] * E_cnt * torch.exp(log_strength[E_pair]) * pair_resc[E_pair]
    tau = torch.clamp(torch.exp(log_tau[node_tid_t]), min=args.dt); b = bias[node_tid_t]; insc = torch.exp(log_inscale[node_tid_t])
    v = b.clone(); A = torch.relu(v) * adapt_mask; x = torch.zeros(N, device=dev); sub = int(round(1 / args.fps / args.dt)); ka = args.dt * 1000.0 / 300.0
    rec_idx = {t: torch.tensor(np.flatnonzero(node_type == t), device=dev) for t in record}; out = {t: [] for t in record}
    for f in range(lum_frames.shape[0]):
        x = torch.zeros(N, device=dev).index_put((r_nodes,), lum_frames[f][r_col])
        for _ in range(sub):
            I = insc * torch.zeros(N, device=dev).index_add(0, E_post, vals * torch.relu(v)[E_pre])
            v = v + (args.dt / tau) * (-v + b + I + x - A); A = A + ka * (torch.relu(v) * adapt_mask - A)
        for t, ix in rec_idx.items(): out[t].append(v[ix])
    return {t: torch.stack(o) for t, o in out.items()}
# ---------------- column correspondence: our column (this eye) -> flyvis hex
sx, sy = geom["sx"][eye_cols], geom["sy"][eye_cols]; vv = np.rint(+sx).astype(int); uu = np.rint(-sy - vv / 2.0).astype(int)
our2hex = np.array([idx_of.get((int(a), int(b)), -1) for a, b in zip(uu, vv)])
# ---------------- stimuli on the flyvis lattice (721 hexes) -> also our columns through our2hex
xs = np.array([v for u, v in lattice], float); ys = np.array([-(u + v / 2.0) for u, v in lattice], float)
def make_clip(T, rng):
    kind = rng.choice(["bar", "grating", "loom", "dots"]); m = np.full((T, 721), 0.5, np.float32); ang = rng.uniform(0, 2 * np.pi); dx, dy = np.cos(ang), np.sin(ang); speed = rng.uniform(4, 20) / args.fps
    proj = xs * dx + ys * dy
    for t in range(T):
        if kind == "bar": m[t] = np.where(np.abs(proj - (-12 + speed * t)) < rng.uniform(1, 3), rng.choice([0.2, 0.8]), 0.5)
        elif kind == "grating": per = rng.uniform(4, 10); m[t] = np.where(((proj - speed * t) // (per / 2)) % 2 == 0, 0.2, 0.8)
        elif kind == "loom": r = 0.5 + speed * 1.5 * t; m[t] = np.where(np.hypot(xs - rng.uniform(-4, 4), ys - rng.uniform(-4, 4)) < r, rng.choice([0.2, 0.8]), 0.5)
        else:
            if t == 0: pts = rng.uniform(-15, 15, size=(12, 2)); val = rng.choice([0.2, 0.8], size=12)
            m[t] = 0.5
            for (px, py), va in zip(pts, val): m[t] = np.where(np.hypot(xs - (px + dx * speed * t), ys - (py + dy * speed * t)) < 1.5, va, m[t])
    return kind, m
common = [t for t in type_names if t in tt_idx and not t.startswith("R") and not t.startswith("CT1")]
teacher_rest = None
def clip_loss(m, rng_seed=0):
    global teacher_rest
    hexmovie = torch.tensor(m[None, :, None, :], device=dev)
    te = teacher_run(hexmovie)
    lum_ours = torch.tensor(m[:, np.maximum(our2hex, 0)], device=dev); lum_ours[:, our2hex < 0] = 0.5
    st = forward(lum_ours, common)
    loss = 0.0; n = 0
    for t in common:
        ix = np.flatnonzero(node_type == t); cols_ = node_col[ix]; ok = (cols_ >= 0) & (our2hex[np.maximum(cols_, 0)] >= 0)
        if ok.sum() < 5: continue
        hexes = our2hex[cols_[ok]]; tcol = np.array([t_uv[t].get(lattice[h], -1) for h in hexes]); ok2 = tcol >= 0
        if ok2.sum() < 5: continue
        sel = np.flatnonzero(ok)[ok2]; tt = te[t][:, torch.tensor(tcol[ok2], device=dev)]; ss = st[t][:, torch.tensor(sel, device=dev)]
        tt = tt - tt[:5].mean(0); ss = ss - ss[:5].mean(0)             # responses, not operating points
        loss = loss + torch.mean((ss - tt) ** 2); n += 1
    return loss / max(n, 1)
if args.check:
    rng = np.random.default_rng(0); kind, m = make_clip(args.clip, rng)
    t0 = time.time(); loss = clip_loss(m); t1 = time.time(); loss.backward(); t2 = time.time()
    print(f"student: {N} nodes, {len(E_pre)} edges, eye {args.eye}; common types {len(common)}; clip '{kind}' {args.clip} frames: forward {t1-t0:.1f}s backward {t2-t1:.1f}s loss {loss.item():.4f}")
    print(f"grad norms: strength {log_strength.grad.norm():.3e} tau {log_tau.grad.norm():.3e} bias {bias.grad.norm():.3e} inscale {log_inscale.grad.norm():.3e}; vram {torch.cuda.max_memory_allocated()/1e9:.2f} GB")
    sys.exit()
opt = torch.optim.Adam([log_strength, log_tau, bias, log_inscale], lr=args.lr); rng = np.random.default_rng(1); hist = []
for step in range(args.steps):
    kind, m = make_clip(args.clip, rng); opt.zero_grad(); loss = clip_loss(m); loss.backward()
    torch.nn.utils.clip_grad_norm_([log_strength, log_tau, bias, log_inscale], 1.0); opt.step(); hist.append(loss.item())
    if step % 10 == 0: print(f"step {step:4d} {kind:8s} loss {loss.item():.4f}  (running {np.mean(hist[-10:]):.4f})", flush=True)
np.savez(args.out, strength=torch.exp(log_strength).detach().cpu().numpy(), pairs=np.array(pairs), tau=torch.exp(log_tau).detach().cpu().numpy(), bias=bias.detach().cpu().numpy(), inscale=torch.exp(log_inscale).detach().cpu().numpy(), types=np.array(type_names), hist=np.array(hist))
print("saved", args.out)
