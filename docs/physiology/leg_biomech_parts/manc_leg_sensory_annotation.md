# Leg sensory neurons in the MANC / MaleCNS connectomes — labelling, vocabulary, counts

Working notes for the whole-fly sim. Everything here is VERIFIED against either the
Marin et al. PDF or the live annotation databases, unless marked otherwise.
Source detail: `docs/research/sources/marin_2024_manc_annotation.md`,
`takemura_2024_manc_vnc_connectome.md`, `malecns_2026_v1.0.md`, `fanc_leg_sensory.md`.

## TL;DR for the sim

- MANC systematic sensory names are `[SN|SA][ch|pp|ta|xx]NN`.
  **pp = proprioceptive, ta = tactile, ch = CHEMOsensory, xx = unknown modality.**
  `SN` = doesn't ascend, `SA` = ascends to brain. Number = arbitrary cluster index.
  `xx` in the number slot = untypable.
- The **sense organ** is NOT in the name. It's in `subclass`:
  `chordotonal organ`, `campaniform sensilla`, `hair plate`, `strand receptor`,
  `mechanosensory bristle`, `taste bristle`.
- **FeCO claw/hook/club are separable**, via the `synonyms` field in MANC
  (`"FeCO claw"`, `"FeCO hook"`, `"FeCO club"`). In MaleCNS `synonyms` is mostly empty —
  match the `type` string against the MANC type lists below instead.
- Leg sensory recovery is **poor and biased** (front legs worst, left side worse than
  right, ~25% of leg proprioceptors untypable). Do not read a missing type as biology.

## 1. The full systematic-type vocabulary

Grammar: `PREFIX + MODALITY + NUMBER`

| slot | values | meaning |
|---|---|---|
| prefix | `SN` | sensory neuron, stays in the VNC |
| | `SA` | sensory ascending — goes up the cervical connective to the brain |
| modality | `ch` | chemosensory |
| | `pp` | proprioceptive |
| | `ta` | tactile |
| | `xx` | unknown |
| number | `01`…`63` | connectivity-cluster index. No anatomical meaning. Serial leg types keep one number across T1/T2/T3. |
| | `xx` | that modality, but not assignable to a type |

Source, verbatim (Marin et al. 2024, "Systematic typing of sensory neurons"):
> "Final sensory cell types were assigned a prefix indicating whether they ascend to the
> neck connective (SA) or not (SN) and an abbreviation based on their inferred modality -
> 'ch' for chemosensory, 'pp' for proprioceptive, 'ta' for tactile, or 'xx' for unknown.
> Each distinct type within a modality was given a unique number; neurons that could not be
> classified as a specific type were assigned 'xx' as their number."

Ranges actually present in MANC v1.2.3:
`SAch01–02, SAchxx` · `SApp01–23, SAppxx` · `SAxx01, SAxx02, SAxxxx` ·
`SNch01–12, SNchxx` · `SNpp01–63, SNppxx` · `SNta01–45 (15/16/17 absent), SNtaxx` ·
`SNxx01–33, SNxxxx`.
Also `DNut035`/`DNxn051` carry `modality=proprioceptive` but are DESCENDING neurons
(`DNx02`, `DNx01` = antennal campaniform sensilla entering via CvC) — exclude them if you
filter on modality alone.

**No `SNhp`, no `SNcs`, no `SNta`=tarsal.** Those don't exist.

## 2. The 63 leg sensory types (reproduces the paper exactly)

Defined as: >50% of that type's neurons enter through a leg nerve. Verified against the
live MANC v1.2.3 table — the count matches the paper's "63 distinct cell types
(9 chemosensory, 22 proprioceptive, 27 tactile, and 5 of unknown modality)" on the nose.

| modality | leg types | count |
|---|---|---|
| chemosensory (9) | `SNch05 SNch06 SNch07 SNch08 SNch09 SNch10 SNch11` + ascending `SAch01 SAch02` | 9 |
| proprioceptive (22) | `SNpp39 SNpp40 SNpp41 SNpp42 SNpp43 SNpp44 SNpp45 SNpp46 SNpp47 SNpp48 SNpp49 SNpp50 SNpp51 SNpp52 SNpp53 SNpp55 SNpp56 SNpp57 SNpp58 SNpp59 SNpp60` + ascending `SApp23` | 22 |
| tactile (27) | `SNta19`–`SNta45` (contiguous) | 27 |
| unknown (5) | `SNxx29 SNxx30 SNxx32 SNxx33` + ascending `SAxx02` | 5 |

Catch-alls that also sit mostly in the legs: `SNchxx` (2), `SAchxx` (19), `SNppxx` (152),
`SNtaxx` (19), `SNxxxx` (306).

## 3. Leg proprioceptor types — the ones the sim cares about

| systematicType | organ (`subclass`) | `synonyms` | n (v1.2.3) | note |
|---|---|---|---|---|
| `SNpp39` | chordotonal organ | FeCO hook | 35 | flexion/extension hook; inhibits tibia extensor via GABAergic IN19A005 |
| `SNpp41` | chordotonal organ | FeCO hook | 23 | opposing hook; inhibits tibia flexor via GABAergic IN19A015, activates extensor |
| `SNpp50` | chordotonal organ | FeCO claw | 62 | activates tibia extensor (direct + 2 cholinergic serial types) |
| `SNpp51` | chordotonal organ | FeCO claw | 27 | activates tibia flexor + acc. flexor, inhibits extensor via 2 glutamatergic types |
| `SApp23` | chordotonal organ | FeCO club | 26 | **ascending** club type |
| `SNpp40 43 47 56 57 58 59 60` | chordotonal organ | FeCO club | 24,17,27,13,12,15,8,41 | clubs — **no appreciable MN connectivity at all** |
| `SNpp42 44 46 48 49` | chordotonal organ | (none) | 18,6,4,6,6 | unclassified leg chordotonal |
| `SNpp45` | hair plate | hair plate | 40 | → 13B + 19A; top partner IN13B001; onto plural remotor/abductor, sternal rotators/abductor MNs. Candidate walking-speed/gait signal |
| `SNpp52` | hair plate | hair plate | 20 | → 14A + 13A + 19A; top partner IN14A001; onto tergopleural/pleural promotor MNs. Candidate posture signal. **Might actually be a campaniform type** (authors' own caveat) |
| `SNpp53` | campaniform sensilla | TrCS | 8 | trochanter / bilateral CS. 2 per leg nerve except ProLN_L. Bilateral. Strong onto Tergotrochanter MNs both sides + dorsal MNs iii1, STTMm |
| `SNpp55` | (blank) | — | 2 | |
| `SNpp63` | campaniform sensilla | — | 6 | |
| `SNppxx` | mixed | mixed | 152 | **the untypable pool — contains most leg campaniform sensilla and extra hair plates** |

Non-leg proprioceptors worth knowing: `SNpp19` = neck/prosternal-organ hair plate (29, via
PrN); `SNpp17/18/22` = prosternal chordotonal organ pCO (51, via ProCN); `SNpp01/02/03` =
Wheeler's organ (60, abdominal AbN3); `SNpp54` = strand receptor (2, AbNT).

### FeCO totals

- MANC v1.2.3: **188 club + 95 claw + 65 hook = 348** FeCO axons across all six legs.
- MaleCNS v1.0: **207 club + 94 claw + 61 hook = 362.**
- Real animal: **~150 FeCO neurons per leg** → ~900 across six legs. So the connectomes
  recover **~40%**.
- Per-leg FeCO in MANC v1.2.3: T1L 21, T1R 55, T2L 49, T2R 83, T3L 67, T3R 73.
  **Front-left is the worst-sampled leg in the dataset.**
- FANC (front-left leg only, Lee et al. 2025) got 80 T1L FeCO axons vs MANC's 22 — about
  50% of the true T1L population, and split into **five** functional subtypes
  (claw-extension 8, claw-flexion 13, hook-extension 9, hook-flexion 13, club 37).
  If you want the best-resolved single-leg FeCO circuit, it is FANC T1L, not MANC.

## 4. Nerves

| abbrev | full name | neuromere | carries |
|---|---|---|---|
| `ProLN` | prothoracic leg nerve | T1 | front leg — bulk |
| `ProAN` | prothoracic accessory nerve | T1 | front leg — **hair plates ONLY** (5/side: SNpp45, SNpp52, SNppxx) |
| `VProN` | ventral prothoracic nerve | T1 | front leg — SNta42 (bilateral tactile) + hair plates SNpp45 |
| `DProN` | dorsal prothoracic nerve | T1 | front leg — SNta33 (intersegmental tactile), hair plate SNpp52/SNpp45, SNxx29 heat nociceptor, SNxx30 |
| `PrN` | prosternal nerve | T1 | neck hair plate (prosternal organ) |
| `ProCN` | prothoracic chordotonal nerve | T1 | pCO |
| `ADMN` | anterior dorsal mesothoracic nerve | T2 | wing (CS, chemo + tactile margin bristles) |
| `PDMN` | posterior dorsal mesothoracic nerve | T2 | notum bristles |
| `MesoAN` | mesothoracic accessory nerve | T2 | (motor; no sensory in MANC) |
| `MesoLN` | mesothoracic leg nerve | T2 | **all** middle-leg sensory |
| `DMetaN` | dorsal metathoracic nerve | T3 | haltere |
| `MetaLN` | metathoracic leg nerve | T3 | **all** hind-leg sensory |
| `AbN1–4`, `AbNT` | abdominal nerves / fused trunk | A | abdomen |
| `CvC` | cervical connective | — | DNs, ANs, and DNx01/DNx02 antennal CS |

**There is no `MetaAN`.** **`ProLN` is not split into named branches** — the front leg is
split across four separate *nerves* instead (ProLN/ProAN/VProN/DProN), which is why the
front-leg query needs four nerve names and the middle/hind only one each.

Sensory neurons per nerve x modality, MANC v1.2.3 (VERIFIED, complete):

```
nerve      chemo proprio tactile unknown  total
ProLN_L      161      35     220      80    496   } front-left leg = 529
ProAN_L        0       5       0       0      5   }
VProN_L        0       2       4       2      8   }
DProN_L        0       4      13       3     20   }
ProLN_R      138      76     200     106    520   } front-right leg = 554
ProAN_R        0       5       0       0      5   }
VProN_R        0       5       5       2     12   }
DProN_R        0       3      11       3     17   }
MesoLN_L      95      78     309      54    536     middle-left leg
MesoLN_R     105     125     379      37    646     middle-right leg
MetaLN_L     137     111     336      87    671     hind-left leg
MetaLN_R     153     137     402      55    747     hind-right leg
---- leg subtotal: 3,683 (tactile 1879, chemo 789, proprio 586, unknown 429) ----
ADMN_L       193     120     172      15    500     wing
ADMN_R       198     115     177      12    502
PDMN_L         0       6     120       3    129     notum
PDMN_R         0       6     117       3    126
DMetaN_L       0     196      17       1    214     haltere
DMetaN_R       0     195      19       1    215
PrN_L          0      14       0       0     14     prosternal organ
PrN_R          0      15       0       0     15
ProCN_L        0      25       0       0     25     pCO
ProCN_R        0      26       0       0     26
AbN2_L/R       2/2     0/0     0/0   46/38   48/40  abdomen
AbN3_L/R       2/2   27/33     0/0   63/57   92/92
AbN4_L/R       8/8     0/0     0/0 279/278 287/286
AbNT_L/R       6/6     1/1     0/0 102/100 109/107
CvC            0       6       0       0      6     DNx01/DNx02
ProNTBD_L/R    0     0/6       0     2/1     2/7
------------------------------------------------
ALL         1216    1378    2502    1430   6526
```

## 5. Dataset totals, for context

| dataset | neurons | sensory | leg sensory | leg proprioceptors | FeCO |
|---|---|---|---|---|---|
| MANC v1.2.3 (male VNC) | ~23,000 traced (23,748 bodies) | 6,526 | 3,683 | 586 | 348 |
| MaleCNS v1.0 (whole male CNS) | 166,691 (whole CNS) | 6,955 VNC sensory | 3,975 | 672 | 362 |
| FANC (female VNC, Azevedo 2024) | 14,600 somata (sensory somata NOT included) | sparse, per-study | — | — | 80 in T1L only (Lee 2025) |

MANC synapses: 10 M TBars / 74 M PSDs / 44 m cable.
FANC synapses: ~45 M; MNs 485 (371 leg); ANs 1,668; INs 12,468.

## 6. Field-name crosswalk — MANC vs MaleCNS

| concept | MANC (neuPrint camelCase) | MANC (Clio/DVID snake_case) | MaleCNS v1.0 |
|---|---|---|---|
| broad class | `class` = `"sensory neuron"` / `"sensory ascending"` / `"Sensory TBD"` / `"sensory descending"` | `class` | `superclass` = `vnc_sensory` / `sensory_ascending` / `vnc_sensory_tbc` / `sensory_descending` |
| modality | `modality` = `proprioceptive`/`tactile`/`chemosensory`/`unknown` | `modality` | `class` = `mechanosensory_proprioceptive` / `mechanosensory_tactile` / `gustatory` or `chemosensory` / `unknown_sensory` |
| sense organ | `subclass` | `subclass` | `subclass` (same values + body-region values) |
| systematic name | `systematicType` | `systematic_type` | **no such field** — it's in `type` and `mancType` |
| curated name | `type` | `type` | `type` (may be comma-joined, e.g. `SNta02,SNta09`) |
| FeCO subtype | `synonyms` = `"FeCO claw"` etc. | `synonyms` | `synonyms` **mostly empty — don't rely on it** |
| nerve | `entryNerve` = `MetaLN_R` (side included) | `entry_nerve` | `entryNerve` = `MetaLN` (**no side**) |
| side | `rootSide` = `LHS`/`RHS` | `root_side` | `rootSide` = `L`/`R` |
| instance | `SNpp38_ProLN_R` (nerve suffix) | `instance` | `SApp10_R` (**side suffix, not nerve**) |
| serial set | `serial`, `serialMotif` | `serial` | `mancSerial`, `mcnsSerial`, `serialMotif` |
| midline pair | `group` | `group` | `group`, `mancGroup` |
| cluster id | `subcluster` | `subcluster` | — |

Fields that are **always empty for sensory neurons in both**: `somaNeuromere`, `somaSide`,
`hemilineage`, `exitNerve`. Their somata are peripheral / excised.

## 7. How to actually pull the data (no credentials needed)

MANC v1.2.3 full annotation table, straight from Janelia's public DVID:
```bash
curl -s "https://manc-dvid.janelia.org/api/node/4dd0dc4934554caabf6555f914bc1aab/segmentation_annotations/keyrangevalues/0/Z?json=true" -o manc_v123.json   # 20 MB, 27,408 bodies
# v1.2.1 (the eLife-submission version) node: 3ddc3f3ca7c94af89b48c15442789629
# DAG:  https://manc-dvid.janelia.org/api/repo/1ec355123bf94e588557a4568d26d258/info
```
MaleCNS v1.0 annotations:
```bash
curl -sL -o mcns.feather "https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/body-annotations-male-cns-v1.0-minconf-0.5.feather"  # 14 MB, 211,577 bodies
```
MANC v1.0 flat connectome (connectivity, if you need edges without a neuPrint token):
```
gs://flyem-manc-exports/v1.0/manc-traced-adjacencies-v1.0/traced-connections.csv   (75 MB)
gs://flyem-manc-exports/v1.0/manc-traced-adjacencies-v1.0/traced-neurons.csv       (630 KB)
gs://flyem-manc-exports/v1.0/manc-v1.0-neuron-properties.feather                   (17 MB)
```
⚠ **The MANC flat export bucket only has v1.0, and v1.0 sensory type NUMBERS differ from
v1.2.x** (the paper says sensory neurons were "systematically retyped"). E.g. `SNpp50–53`
do not exist in v1.0. For annotations use DVID v1.2.3; for edges, v1.0 bodyIds are stable
so you can join, but re-derive the types.

neuPrint (needs a free Google-auth token):
```python
from neuprint import Client, NeuronCriteria as NC, fetch_neurons
c = Client('neuprint.janelia.org', dataset='manc:v1.2.3', token=TOK)
prop, _ = fetch_neurons(NC(class_='sensory neuron', modality='proprioceptive'))
feco, _ = fetch_neurons(NC(systematicType=['SNpp39','SNpp41','SNpp50','SNpp51']))
```
```cypher
MATCH (n:Neuron)
WHERE n.class IN ['sensory neuron','sensory ascending']
  AND n.modality='proprioceptive'
  AND n.entryNerve =~ '(ProLN|ProAN|VProN|DProN|MesoLN|MetaLN)_[LR]'
RETURN n.bodyId, n.systematicType, n.subclass, n.synonyms, n.entryNerve, n.target
```

## 8. Caveats to carry into the model

1. **~25% of leg proprioceptors are `SNppxx`** — untyped. 152 neurons in v1.2.3.
2. **Leg campaniform sensilla other than TrCS are not separable from hair plates.**
   Only 10 leg neurons carry `subclass="campaniform sensilla"` in MANC (the TrCS). The real
   fly has ~1,200 CS body-wide. Anything you want to model as a leg strain/load sensor
   other than TrCS is not individually resolved in MANC.
3. **Counts per hemineuromere vary wildly for non-biological reasons** (dark staining,
   degradation, segmentation failure). The authors say so explicitly, and warn against
   reading absence of a tactile type in a neuromere as biology.
4. **FeCO clubs have no motor connectivity** in MANC — they go to intersegmental/ascending
   vibration pathways (confirmed independently in FANC by Lee et al. 2025). Only claw and
   hook close local reflex loops, and only **ipsilaterally**.
5. The sign predictions (claw/hook → tibia extensor vs flexor) assume glutamate is
   inhibitory in the leg premotor circuit. That is an assumption, stated as such in the paper.

## 9. Late additions / corrections

- **All FeCO afferents enter via the main leg nerve only** — `ProLN`, `MesoLN`, `MetaLN`.
  Zero FeCO in ProAN/VProN/DProN. Verified: the FeCO x nerve crosstab has exactly six
  nonzero columns.
- **The T1 accessory nerves are highly specialised** (VERIFIED, v1.2.3):
  - `ProAN_L/R`: 5 neurons each, **100% hair plate** (`SNpp45`, `SNpp52`, `SNppxx`).
  - `VProN_L/R`: 8 / 12 neurons — `SNta42` (the bilateral tactile type) ×4 each, plus hair
    plate `SNpp45`, plus `SNxxxx`.
  - `DProN_L/R`: 20 / 17 neurons — dominated by `SNta33` (the intersegmental tactile type,
    13 / 11), plus hair plate `SNpp52`/`SNpp45`, plus `SNxx29` (heat nociceptor) ×2 and
    `SNxx30` ×1 each.
  So if you only query `ProLN` for the front leg you lose all the ProAN hair plates, the
  bilateral tactile type, and the intersegmental tactile type.
- **Known error in the Marin preprint text**: the Discussion reads "13,060 VNC intrinsic
  neurons, **185 ascending neurons**, 1328 descending neurons, 737 motor neurons…". The
  database has 1,865 ascending neurons (v1.2.3) / 1,866 (v1.0). "185" is a typo or an
  extraction artefact; don't propagate it.
- Two totals coexist in the Marin preprint and don't quite reconcile: "nearly 6500 sensory
  neurons" / "systematic cell typing of **6462** sensory neurons" (both v1.2.1), vs a
  modality tally of 1,211 + 1,347 + 2,497 + 1,422 = **6,477**. The live v1.2.3 database
  gives **6,526**. Use 6,526 if you're working from the data, ~6,500 if you're citing.
