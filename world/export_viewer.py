"""export_viewer.py - bundle an episode + its neural readouts into the viewer HTML (data inlined)."""
import sys, json, base64, numpy as np
ep = np.load(sys.argv[1]); nr = np.load(sys.argv[2]) if sys.argv[2] != "-" else ep; tpl = open("world/viewer_template.html").read(); out = sys.argv[3]
STRIDE = int(sys.argv[5]) if len(sys.argv) > 5 else 1   # keep every STRIDE-th frame (long episodes); fps scales down accordingly
lum = (ep["lum"] if ep["lum"].dtype == np.uint8 else (np.clip(ep["lum"], 0, 1) * 255).astype(np.uint8))[::STRIDE]
data = {"fps": int(ep["fps"]) // STRIDE, "T": int(lum.shape[0]), "n": int(lum.shape[1]), "fov": float(ep["fov"]),
        "pose": np.round(ep["pose"][::STRIDE], 4).tolist(), "objects": np.round(ep["objects"], 3).tolist(),
        "az": np.round(ep["az"], 1).tolist(), "el": np.round(ep["el"], 1).tolist(), "side": ["L" if s == "L" else "R" for s in ep["side"]],
        "lum_b64": base64.b64encode(lum.tobytes()).decode(),
        "traces": {k[2:]: nr[k][::STRIDE].astype(int).tolist() for k in nr.files if k.startswith("n_")},
        "ncells": {k[7:]: int(nr[k]) for k in nr.files if k.startswith("ncells_")},
        "pose2": (np.round(ep["pose2"], 4).tolist() if "pose2" in ep.files else None), "pillars": bool("pillars" in ep.files and ep["pillars"]), "sky": float(ep["sky"]) if "sky" in ep.files else None, "ground": float(ep["ground"]) if "ground" in ep.files else None, "her_r": float(ep["her_r"]) if "her_r" in ep.files else None, "her_albedo": float(ep["her_albedo"]) if "her_albedo" in ep.files else None, "dist": (np.round(ep["dist"], 3).tolist() if "dist" in ep.files else None), "song": (ep["song"].astype(int).tolist() if "song" in ep.files else None),
        "touch": (ep["touch"][::STRIDE].astype(int).tolist() if "touch" in ep.files and len(ep["touch"]) else None), "touch_kind": (ep["touch_kind"][::STRIDE].astype(int).tolist() if "touch_kind" in ep.files else None), "body_r": (float(ep["body_r"]) if "body_r" in ep.files else None), "walls": (ep["walls"].tolist() if "walls" in ep.files else None), "thermal": ([float(v) for v in sys.argv[6].split(",")] if len(sys.argv) > 6 else None),
        "drum": ({"period": float(ep["drum_period"]), "lo": float(ep["drum_lo"]), "hi": float(ep["drum_hi"]), "half_height": float(ep["drum_half_height"]), "phase": np.round(ep["drum_phase"][::STRIDE], 2).tolist()} if "drum_phase" in ep.files else None)}
name = sys.argv[4] if len(sys.argv) > 4 else "episode 0"
html = tpl.replace("/*__DATA__*/null", json.dumps(data)).replace("<title>Fly Afterlife Viewer</title>", f"<title>Fly Afterlife {name.title()}</title>").replace("fly afterlife · episode 0", f"fly afterlife · {name}")
open(out, "w").write(html); print(f"wrote {out}: {len(html)/1e6:.1f} MB, {data['T']} frames, {data['n']} columns")
