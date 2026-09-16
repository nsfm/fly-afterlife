"""export_viewer.py - bundle an episode + its neural readouts into the viewer HTML (data inlined)."""
import sys, json, base64, numpy as np
ep = np.load(sys.argv[1]); nr = np.load(sys.argv[2]); tpl = open("world/viewer_template.html").read(); out = sys.argv[3]
lum = (np.clip(ep["lum"], 0, 1) * 255).astype(np.uint8)
data = {"fps": int(ep["fps"]), "T": int(lum.shape[0]), "n": int(lum.shape[1]), "fov": float(ep["fov"]),
        "pose": np.round(ep["pose"], 4).tolist(), "objects": np.round(ep["objects"], 3).tolist(),
        "az": np.round(ep["az"], 1).tolist(), "el": np.round(ep["el"], 1).tolist(), "side": ["L" if s == "L" else "R" for s in ep["side"]],
        "lum_b64": base64.b64encode(lum.tobytes()).decode(),
        "traces": {k[2:]: nr[k].astype(int).tolist() for k in nr.files if k.startswith("n_")},
        "ncells": {k[7:]: int(nr[k]) for k in nr.files if k.startswith("ncells_")}}
html = tpl.replace("/*__DATA__*/null", json.dumps(data))
open(out, "w").write(html); print(f"wrote {out}: {len(html)/1e6:.1f} MB, {data['T']} frames, {data['n']} columns")
