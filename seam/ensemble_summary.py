"""summarize seam/ens/m*.json into one table: per model, ipsilateral LPLC2 loom/recede/static, GF, HS under yaw."""
import json, glob, numpy as np, pandas as pd
rows = []
for f in sorted(glob.glob("seam/ens/m*.json")):
    m = f.split("/")[-1][1:4]; d = {r["stim"]: r["during"] for r in json.load(open(f))}
    g = lambda s, k: d[s][k] if s in d else np.nan
    rows.append({"model": m, "LPLC2 loom L": g("loom_left", "LPLC2_L"), "recede L": g("recede_left", "LPLC2_L"), "static L": g("static_left", "LPLC2_L"),
                 "LPLC2 loom R": g("loom_right", "LPLC2_R"), "recede R": g("recede_right", "LPLC2_R"), "static R": g("static_right", "LPLC2_R"),
                 "GF loom R": g("loom_right", "GF_L") + g("loom_right", "GF_R"), "GF recede R": g("recede_right", "GF_L") + g("recede_right", "GF_R"),
                 "yawL HS_L": g("yaw_left", "HS_L"), "yawL HS_R": g("yaw_left", "HS_R")})
t = pd.DataFrame(rows).set_index("model"); print(t.to_string())
print("\nloom > recede (ipsilateral LPLC2): left", int((t["LPLC2 loom L"] > t["recede L"]).sum()), "of", len(t), "; right", int((t["LPLC2 loom R"] > t["recede R"]).sum()), "of", len(t))
print("yaw_left HS_R > HS_L:", int((t["yawL HS_R"] > t["yawL HS_L"]).sum()), "of", len(t))
print("median loom/recede ratio: left", round(float((t["LPLC2 loom L"] / t["recede L"].clip(lower=1)).median()), 2), " right", round(float((t["LPLC2 loom R"] / t["recede R"].clip(lower=1)).median()), 2))
