"""build_leg_senses.py - the per-leg sensory maps the body loop needs (campaign item 6, 09-22).

every sensory cell of brain_cord.npz (vnc_sensory + sensory_ascending/_tbc + sensory_descending) gets a leg, a modality and, for
proprioceptors, an organ subtype. the leg comes from the MaleCNS annotation (entryNerve x rootSide: ProLN / ProAN / VProN / DProN ->
front, MesoLN -> middle, MetaLN -> hind); every cell is ALSO scored from its wiring (which leg's motor neurons, and which leg's
premotor cells, its output synapses land on) as an independent check, and the one leg-proprioceptor with no nerve is placed by that.
subtypes come from the MANC type vocabulary (docs/physiology/leg_biomech_parts/manc_leg_sensory_annotation.md) and the per-cell
MaleCNS subclass / synonyms. writes world/leg_senses.npz (per leg x modality, bodyIds) and world/leg_senses.csv (per cell).

    uv run python scripts/build_leg_senses.py
"""
import numpy as np, pandas as pd, re, json

ANNOT = "data/body-annotations-male-cns-v1.0-minconf-0.5.feather"
LEG6 = ["lf", "lm", "lh", "rf", "rm", "rh"]
NERVE_SEG = {"ProLN": "f", "ProAN": "f", "VProN": "f", "DProN": "f", "MesoLN": "m", "MetaLN": "h"}
MAIN_NERVE = {"ProLN", "MesoLN", "MetaLN"}
SENS_SC = ["vnc_sensory", "sensory_ascending", "sensory_ascending_tbc", "sensory_descending"]

# ---- the MANC vocabulary (Marin et al. 2024; MANC v1.2.3 synonyms), types as MaleCNS carries them
CLAW = {"SNpp50": "claw_50", "SNpp51": "claw_51"}              # extension / flexion tuning per the E_table label; ledger row 1: may be swapped
HOOK = {"SNpp39": "hook_39", "SNpp41": "hook_41"}              # flexion / extension hook (body_loop's reading)
CLUB = {"SNpp40", "SNpp43", "SNpp47", "SNpp56", "SNpp57", "SNpp58", "SNpp59", "SNpp60", "SApp23"}
CO_UNCL = {"SNpp42", "SNpp44", "SNpp46", "SNpp48", "SNpp49"}   # leg chordotonal, no FeCO subtype in MANC
HP = {"SNpp45": "hair_plate_45", "SNpp52": "hair_plate_52"}     # SNpp52: the authors' caveat, may be campaniform
CS = {"SNpp53", "SNpp63"}                                      # SNpp53 = trochanter CS (TrCS), bilateral

b = np.load("brain_cord.npz", allow_pickle=True)
N = len(b["bodyId"]); bid = b["bodyId"].astype(np.int64); typ = b["type"].astype(str); cls = b["cls"].astype(str); sc = b["sc"].astype(str)
pre, post, w = b["pre"].astype(np.int64), b["post"].astype(np.int64), b["w"].astype(np.float64)
a = pd.read_feather(ANNOT).set_index("bodyId")

# ---- the wiring score: A0 = leg motor neurons (world/legmn.npz), A1 = each cell's share of its output onto them, A2 = one hop further
wb = np.load("brain_whole.npz", allow_pickle=True)["bodyId"].astype(np.int64); lm = np.load("world/legmn.npz")
pos = {int(x): i for i, x in enumerate(bid)}
A0 = np.zeros((N, 6))
for g, L in (("fl", "f"), ("ml", "m"), ("hl", "h")):
    for s in "LR":
        for i in lm[f"{g}_{s}"]:
            j = pos.get(int(wb[i]))
            if j is not None: A0[j, LEG6.index(s.lower() + L)] = 1.0
isMN = A0.sum(1) > 0; isSens = np.isin(sc, SENS_SC)
def spread(A, mask_src):
    D = np.zeros((N, 6)); np.add.at(D, pre, w[:, None] * A[post]); D[~mask_src] = 0
    s = D.sum(1, keepdims=True); return np.divide(D, s, out=np.zeros_like(D), where=s > 0)
inter = ~isMN & ~isSens
A1 = spread(A0, inter)
A2 = spread(A1, inter); A2[A1.sum(1) > 0] = 0            # only for cells with no direct motor output
T = A0 + A1 + 0.5 * A2
S = np.zeros((N, 6)); np.add.at(S, pre, w[:, None] * T[post])
Ssum = S.sum(1); OUTW = np.bincount(pre, weights=w, minlength=N)

rows = []
for i in np.flatnonzero(isSens):
    t = typ[i]; ann = a.loc[bid[i]] if bid[i] in a.index else None
    nerve = str(ann["entryNerve"]) if ann is not None and pd.notna(ann["entryNerve"]) else ""
    rside = str(ann["rootSide"]) if ann is not None and pd.notna(ann["rootSide"]) else ""
    sub = str(ann["subclass"]) if ann is not None and pd.notna(ann["subclass"]) else ""
    syn = str(ann["synonyms"]) if ann is not None and pd.notna(ann["synonyms"]) else ""
    _fm = re.match(r"^([A-Za-z]+?)(?:\d|$)", t); fam = _fm.group(1) if _fm else t
    # wiring vote
    if Ssum[i] > 0:
        k = int(np.argmax(S[i])); inf_leg = LEG6[k]; share = S[i, k] / Ssum[i]
        seg_share = max(S[i, [0, 3]].sum(), S[i, [1, 4]].sum(), S[i, [2, 5]].sum()) / Ssum[i]
    else: inf_leg, share, seg_share = "", 0.0, 0.0
    inf_conf = "high" if share >= 0.6 else "medium" if share >= 0.4 else "low" if share > 0 else "none"
    # the leg
    if nerve in NERVE_SEG and rside in ("L", "R"):
        leg = rside.lower() + NERVE_SEG[nerve]; by = "annotated"
        conf = "high" if nerve in MAIN_NERVE else "medium"      # the T1 accessory nerves: MANC calls them front-leg (hair plates, SNta42, SNta33)
        if inf_leg and inf_leg != leg and inf_conf in ("high", "medium"): conf = "medium" if conf == "high" else "low"
    elif nerve == "" and inf_leg and inf_conf in ("high", "medium"):
        leg, by, conf = inf_leg, "inferred", inf_conf
    elif nerve == "":
        leg, by, conf = "", "unassigned", "none"
    else:
        leg, by, conf = "", f"not_leg:{nerve}", "high"
    # the modality: cls where it names one; the MANC family where cls is unknown / blank
    c = cls[i]
    if c in ("mechanosensory_tactile",): mod = "tactile"
    elif c == "mechanosensory_proprioceptive": mod = "proprio"
    elif c in ("gustatory",): mod = "gustatory"
    elif c == "chemosensory": mod = "chemo"
    else:
        f2 = t.split(",")[0][:4]
        mod = {"SNta": "tactile", "SNpp": "proprio", "SApp": "proprio", "SNch": "chemo", "SAch": "chemo"}.get(f2, "gustatory" if t.startswith(("LgLG", "LgAG")) else "unknown")
    mod_by = "cls" if c in ("mechanosensory_tactile", "mechanosensory_proprioceptive", "gustatory", "chemosensory") else ("type" if mod != "unknown" else "none")
    # the subtype
    st = ""
    if mod == "proprio":
        parts = t.split(",")
        if parts[0] in CLAW and len(parts) == 1: st = CLAW[parts[0]]
        elif parts[0] in HOOK and len(parts) == 1: st = HOOK[parts[0]]
        elif all(p in CLUB for p in parts): st = "club"
        elif parts[0] in CO_UNCL: st = "co_unclassified"
        elif parts[0] in HP: st = HP[parts[0]]
        elif parts[0] in CS or sub == "campaniform sensilla": st = "campaniform"
        elif sub == "hair plate" or syn == "hair plate": st = "hair_plate_xx"
        elif sub == "chordotonal organ": st = "co_unclassified"
        else: st = "untyped"
    rows.append(dict(bodyId=int(bid[i]), type=t, cls=c, sc=sc[i], fam=fam, entryNerve=nerve, rootSide=rside, subclass=sub, synonyms=syn,
                     leg=leg, modality=mod, modality_by=mod_by, subtype=st, assigned_by=by, confidence=conf,
                     wiring_leg=inf_leg, wiring_share=round(float(share), 3), wiring_seg_share=round(float(seg_share), 3), out_syn=int(OUTW[i])))
D = pd.DataFrame(rows)
D.to_csv("world/leg_senses.csv", index=False)

out = {}
for leg in LEG6:
    d = D[D.leg == leg]
    out[f"{leg}_tactile"] = d[d.modality == "tactile"].bodyId.to_numpy(np.int64)
    out[f"{leg}_proprio_all"] = d[d.modality == "proprio"].bodyId.to_numpy(np.int64)
    for st in ["claw_50", "claw_51", "hook_39", "hook_41", "club", "co_unclassified", "hair_plate_45", "hair_plate_52", "hair_plate_xx", "campaniform", "untyped"]:
        out[f"{leg}_{st}"] = d[d.subtype == st].bodyId.to_numpy(np.int64)
    out[f"{leg}_hair_plate"] = d[d.subtype.str.startswith("hair_plate")].bodyId.to_numpy(np.int64)
    out[f"{leg}_gustatory"] = d[d.modality == "gustatory"].bodyId.to_numpy(np.int64)
    out[f"{leg}_chemo"] = d[d.modality == "chemo"].bodyId.to_numpy(np.int64)
    out[f"{leg}_unknown"] = d[d.modality == "unknown"].bodyId.to_numpy(np.int64)
out["legs"] = np.array(LEG6); out["README"] = np.array(
    "per leg (lf lm lh rf rm rh) x key: bodyIds (MaleCNS v1.0) of the leg's sensory cells in brain_cord.npz. keys: tactile, proprio_all, "
    "claw_50 / claw_51 (FeCO claw, SNpp50 / SNpp51), hook_39 / hook_41 (FeCO hook), club (FeCO club incl. SApp23), co_unclassified (leg "
    "chordotonal, no FeCO subtype), hair_plate (= _45 + _52 + _xx), campaniform (SNpp53 TrCS + subclass-labelled CS), untyped (SNppxx etc.), "
    "gustatory, chemo, unknown. built by scripts/build_leg_senses.py; per-cell table world/leg_senses.csv; docs/physiology/leg_senses_map.md")
np.savez_compressed("world/leg_senses.npz", **out)

# ---- the report
pd.set_option("display.width", 250)
print("sensory cells:", len(D), dict(D.sc.value_counts()))
print("assigned_by:", dict(D.assigned_by.value_counts()))
L = D[D.leg != ""]
print("\nper leg x modality (leg cells):\n", pd.crosstab(L.modality, L.leg)[LEG6].to_string())
print("\nper leg x proprio subtype:\n", pd.crosstab(L[L.modality == "proprio"].subtype, L[L.modality == "proprio"].leg)[LEG6].to_string())
print("\nper leg x sc:\n", pd.crosstab(L.sc, L.leg)[LEG6].to_string())
print("\nconfidence:", dict(L.confidence.value_counts()), " by:", dict(L.assigned_by.value_counts()))
ann = L[L.assigned_by == "annotated"]; hasw = ann[ann.wiring_leg != ""]
agree = (hasw.wiring_leg == hasw.leg); seg_agree = hasw.wiring_leg.str[1] == hasw.leg.str[1]; side_agree = hasw.wiring_leg.str[0] == hasw.leg.str[0]
print(f"\nwiring check on {len(hasw)} annotated leg cells with output onto scored cells (of {len(ann)}): leg agrees {agree.mean():.3f}, segment {seg_agree.mean():.3f}, side {side_agree.mean():.3f}")
for m in ["tactile", "proprio", "gustatory", "chemo", "unknown"]:
    h = hasw[hasw.modality == m]
    if len(h): print(f"  {m:9s} n={len(h):5d}  leg {np.mean(h.wiring_leg == h.leg):.3f}  seg {np.mean(h.wiring_leg.str[1] == h.leg.str[1]):.3f}  side {np.mean(h.wiring_leg.str[0] == h.leg.str[0]):.3f}  (high-conf wiring only: leg {np.mean(h[h.wiring_share >= 0.6].wiring_leg == h[h.wiring_share >= 0.6].leg):.3f}, n={int((h.wiring_share >= 0.6).sum())})")
for nv in ["ProLN", "ProAN", "VProN", "DProN", "MesoLN", "MetaLN"]:
    h = hasw[hasw.entryNerve == nv]
    if len(h): print(f"  {nv:7s} n={len(h):5d}  leg {np.mean(h.wiring_leg == h.leg):.3f}  seg {np.mean(h.wiring_leg.str[1] == h.leg.str[1]):.3f}")
print("\nannotated cells whose wiring points confidently elsewhere (share >= 0.6), by type:\n",
      hasw[(~agree) & (hasw.wiring_share >= 0.6)].groupby(["modality", "type"]).size().sort_values(ascending=False).head(25).to_string())
print("\nnot assigned / not leg:", dict(D[D.leg == ""].assigned_by.value_counts()))
print("inferred / unassigned cells:\n", D[D.assigned_by.isin(["inferred", "unassigned"])][["bodyId", "type", "cls", "wiring_leg", "wiring_share", "confidence"]].to_string())
nl = D[D.assigned_by.str.startswith("not_leg")]
print("\nnon-leg-nerve sensory cells whose wiring points into leg neuropil with share >= 0.6:", int((nl.wiring_share >= 0.6).sum()), "of", len(nl),
      dict(nl[nl.wiring_share >= 0.6].entryNerve.value_counts()))

# ---- against the existing sets
legs = np.load("world/legs.npz"); SENS = {"lf": "L1", "lm": "L2", "lh": "L3", "rf": "R1", "rm": "R2", "rh": "R3"}
cmp = {}
for leg in LEG6:
    old = set(int(wb[i]) for i in legs[SENS[leg]]); new = set(out[f"{leg}_proprio_all"].tolist())
    in_cord = set(x for x in old if x in pos)
    old_types = D.set_index("bodyId").reindex(list(old - new))
    cmp[leg] = dict(legs_npz=len(old), in_cord=len(in_cord), mine=len(new), both=len(old & new), only_legs_npz=len(old - new), only_mine=len(new - old),
                    only_mine_types=D[D.bodyId.isin(new - old)].groupby(["entryNerve", "type"]).size().to_dict(),
                    only_old_leg=D[D.bodyId.isin(old - new)].groupby(["leg", "modality", "type"]).size().to_dict())
    # body_loop's sets (built from legs.npz by type)
    oldc = np.array(sorted(in_cord)); oty = np.array([typ[pos[x]] for x in oldc])
    bl = dict(claw_e=set(oldc[oty == "SNpp50"]), claw_f=set(oldc[oty == "SNpp51"]), hook_f=set(oldc[oty == "SNpp39"]), hook_e=set(oldc[oty == "SNpp41"]),
              load=set(oldc[~np.isin(oty, ["SNpp50", "SNpp51", "SNpp39", "SNpp41"])]))
    cmp[leg]["body_loop"] = {k: len(v) for k, v in bl.items()}
    cmp[leg]["claw_e_vs_claw_50"] = (len(bl["claw_e"] & set(out[f"{leg}_claw_50"].tolist())), len(out[f"{leg}_claw_50"]))
    cmp[leg]["claw_f_vs_claw_51"] = (len(bl["claw_f"] & set(out[f"{leg}_claw_51"].tolist())), len(out[f"{leg}_claw_51"]))
    cmp[leg]["hook_f_vs_hook_39"] = (len(bl["hook_f"] & set(out[f"{leg}_hook_39"].tolist())), len(out[f"{leg}_hook_39"]))
    cmp[leg]["hook_e_vs_hook_41"] = (len(bl["hook_e"] & set(out[f"{leg}_hook_41"].tolist())), len(out[f"{leg}_hook_41"]))
    cmp[leg]["load_by_my_subtype"] = D[D.bodyId.isin(bl["load"])].groupby("subtype").size().to_dict()
print("\nagainst world/legs.npz and body_loop's sets:")
for leg in LEG6: print(leg, json.dumps({k: ({"|".join(map(str, kk)) if isinstance(kk, tuple) else kk: vv for kk, vv in v.items()} if isinstance(v, dict) else v) for k, v in cmp[leg].items()}, default=str))
# the floor stand-in (receptors.py floor_leg_proprio: cls proprio, entryNerve in the three main leg nerves)
fl = D[(D.cls == "mechanosensory_proprioceptive") & D.entryNerve.isin(MAIN_NERVE)]
print(f"\nfloor_leg_proprio (as receptors.py selects it): {len(fl)} cells; by my subtype {dict(fl.subtype.value_counts())}")
print("my leg proprio_all total:", int(sum(len(out[f'{l}_proprio_all']) for l in LEG6)), " leg tactile total:", int(sum(len(out[f'{l}_tactile']) for l in LEG6)))
