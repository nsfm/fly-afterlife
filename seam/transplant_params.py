"""dump flyvis model 000's learned per-type physiology to seam/flyvis_params.json:
  nodes: {type: {tau_s, bias}}   edges: {"src->tgt": {strength, sign, n_syn_per_target (their spec)}}"""
import os, json, numpy as np, torch
os.environ.setdefault("FLYVIS_ROOT_DIR", "/home/nate/code/fly-afterlife/flyvis_data")
import flyvis, pandas as pd
from flyvis import NetworkView
net = NetworkView("flow/0000/000").init_network(); net.eval(); p = net._param_api()
nodes = net.connectome.nodes; ntype = nodes.type[:].astype(str)
tc = p.nodes.time_const.detach().cpu().numpy(); bias = p.nodes.bias.detach().cpu().numpy()
out = {"model": "flow/0000/000", "dynamics": "tau dv/dt = -v + bias + sum(sign*syn_count*strength*relu(v_pre)) + input",
       "nodes": {t: {"tau_s": float(tc[ntype == t].mean()), "bias": float(bias[ntype == t].mean())} for t in sorted(set(ntype))}}
e = net.connectome.edges; st = e.source_type[:].astype(str); tt = e.target_type[:].astype(str)
ss = p.edges.syn_strength.detach().cpu().numpy(); sg = p.edges.sign.detach().cpu().numpy(); sc = p.edges.syn_count.detach().cpu().numpy()
tgt = e.target_index[:]
df = pd.DataFrame({"s": st, "t": tt, "ss": ss, "sg": sg, "sc": sc, "tgt": tgt})
# their per-target-cell total synapses from a source type (central column, to avoid rim truncation)
u = nodes.u[:]; v = nodes.v[:]; central = np.flatnonzero((u == 0) & (v == 0))
per_tgt = df[df.tgt.isin(central)].groupby(["s", "t"]).sc.sum()
pairs = df.drop_duplicates(["s", "t"]).set_index(["s", "t"])
out["edges"] = {f"{s}->{t}": {"strength": float(r.ss), "sign": float(r.sg), "n_syn_per_target": float(per_tgt.get((s, t), np.nan))} for (s, t), r in pairs.iterrows()}
json.dump(out, open("seam/flyvis_params.json", "w"), indent=1)
print(len(out["nodes"]), "types,", len(out["edges"]), "type pairs written to seam/flyvis_params.json")
print("tau range", min(n["tau_s"] for n in out["nodes"].values()), max(n["tau_s"] for n in out["nodes"].values()))
