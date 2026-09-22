# Marin et al. 2024 — Systematic annotation of the MANC connectome

**(in progress)** — notes compiled 2026-09-21.

## Citation

Marin EC, Morris BJ, Stürner T, Champion AS, Krzeminski D, Badalamente G, Gkantia M,
Dunne CR, Eichler K, Takemura S, Tamimi IFM, Fang S, Moon SS, Cheong HSJ, Li F,
Schlegel P, Ahnert SE, Berg S, Janelia FlyEM Project Team, Card GM, Costa M,
Shepherd D, Jefferis GSXE (2024). *Systematic annotation of a complete adult male
Drosophila nerve cord connectome reveals principles of functional organisation.*
**eLife 13:RP97766.**

- eLife reviewed-preprint DOI: **10.7554/eLife.97766.1** (Reviewed Preprint v1, posted 2024-07-22) — VERIFIED (fetched elifesciences.org/reviewed-preprints/97766).
- Underlying preprint: bioRxiv **10.1101/2023.06.05.543407**, v posted 2024-03-11 — VERIFIED (downloaded and read the 559-page full PDF; all quoted text below is from that PDF unless marked otherwise).
- Note: as of the fetch there was **no eLife Version of Record**; it was still a Reviewed Preprint. Citing "eLife 13:RP97766" is correct in eLife's RP style.

## THE SENSORY NAMING SCHEME — verbatim, VERIFIED

> "Final sensory cell types were assigned a prefix indicating whether they ascend to the
> neck connective (**SA**) or not (**SN**) and an abbreviation based on their inferred
> modality - **"ch" for chemosensory, "pp" for proprioceptive, "ta" for tactile, or "xx"
> for unknown**. Each distinct type within a modality was given a unique number; neurons
> that could not be classified as a specific type were assigned **"xx" as their number**."
> — Marin et al., section *Systematic typing of sensory neurons*

So the grammar is `[SN|SA] + [ch|pp|ta|xx] + NN`:

| token | meaning | VERIFIED |
|---|---|---|
| `SN` | sensory neuron, does NOT ascend to the brain via the neck connective | yes |
| `SA` | sensory ascending — same as SN but ascends through the cervical connective (CvC) to the brain | yes |
| `ch` | **chemosensory** (responsive to chemical stimuli) — NOT "chordotonal" | yes |
| `pp` | **proprioceptive** (location/movement of the body) | yes |
| `ta` | **tactile** (responsive to touch) — NOT "tarsal" | yes |
| `xx` (2nd–3rd char) | modality **unknown** / could not be assigned | yes |
| `NN` numeric suffix | arbitrary index for a distinct **connectivity cluster** within that modality (assigned by weighted-nearest-neighbour clustering + hierarchical clustering, then manually curated). It is *not* an anatomical code and carries no meaning beyond "distinct type N". Serially repeating leg types keep the same number across T1/T2/T3. | yes |
| `xx` (numeric slot, e.g. `SNppxx`, `SNtaxx`, `SNchxx`, `SNxxxx`) | neuron of that modality that **could not be assigned to any specific type** | yes |

**There is no `SNhp` and no `SNcs` code.** Hair plates and campaniform sensilla are
proprioceptors, so they are `SNpp##`; the sensillum identity lives in the **`subclass`**
field, not in the systematic type. Chordotonal organs are likewise `SNpp##` (`ch` is
already taken by chemosensory).

Instance = systematicType + entry nerve (+ side), e.g. `SNpp38_ProLN_R`. Verified in
the v1.0 `traced-neurons.csv` instance column.

## Systematic-type schemes for the other classes (for context)

- `DN` + target-VNC-neuropil abbrev + number; instance uses entry nerve (CvC) + root side.
- `MN` + subclass (target muscle category abbrev) + number; instance = exit nerve. Leg MNs use `fl`/`ml`/`hl` (front/middle/hind leg) as the subclass.
- `IN` / `AN` + hemilineage + number; instance = soma neuromere + side.
- `EN` / `EA` (efferent, non-ascending / ascending) + hemilineage + number.

## Annotation fields (MANC schema)

The paper's Table 1 ("Glossary of annotation terms") is a rendered image, not text —
could not extract its cell contents from the PDF. But the **actual field list** was read
directly off the MANC v1.0 neuron-properties export (see below), 56 columns:

```
bodyId instance type pre post downstream upstream size status cropped statusLabel
cellBodyFiber somaRadius somaLocation roiInfo ntGabaProb modality source prefix
subcluster target origin positionType somaNeuromere hemilineage entryNerve rootPosition
longTract birthtime avgLocation position synonyms neuropilsAxonal neuropilsDendritic
predictedNtProb serial ntUnknownProb systematicType namingUser ntAcetylcholineProb
serialMotif subclass predictedNt tag tosomaPosition class transmission rootSide
exitNerve ntGlutamateProb group receptorType somaSide synweight inputRois outputRois
```

Note the format split, VERIFIED from the Table 1 caption: **Clio Neuroglancer uses
snake_case (`entry_nerve`), neuPrint uses camelCase (`entryNerve`).**

Fields that matter for sensory neurons (from the paper text, VERIFIED):
- `class` — broad class; sensory neurons are `"sensory neuron"` or `"sensory ascending"` (or `"Sensory TBD"` if unresolved).
- `systematicType` — the `SN../SA..` name above.
- `type` — usually identical to systematicType; differs where light-level names or finer splits were applied.
- `instance` — type + `_<entryNerve>` (+side).
- `subclass` — **the sensillum/organ identity**, e.g. `"mesothoracic leg FeCO claw"`.
- `modality` — `chemosensory` / `proprioceptive` / `tactile` / `unknown`. (Central neurons instead get one or two modality labels or `"mixed"` when they are 2nd-order sensory processors.)
- `entryNerve` — nerve of entry, with side, e.g. `MetaLN_R`. This is the sensory instance suffix.
- `exitNerve` — motor neurons only; empty for sensory.
- `somaNeuromere` — essentially **empty for sensory neurons** (their somata are peripheral, outside the VNC volume). Use `entryNerve` / `rootSide` instead.
- `rootSide` — `LHS`/`RHS`, side of axon entry into the VNC (used in place of somaSide for peripheral neurons).
- `target` — target neuropil(s), dot-separated, e.g. `LegNpT3_R`, `mVACT2_R.LegNpT2_R`, `ANm`, `Ov_L`, `multi`.
- `subcluster` — the numeric connectivity-cluster ID from the WNN/HDBSCAN clustering used to build the types.
- `serial` — serial-set ID linking homologues across neuromeres.
- `group` — ID linking left/right homologues across the midline.
- `hemilineage` — **empty for sensory neurons** (they are not neuroblast-derived VNC neurons).
- `synonyms` — light-level literature names where matched.

## Counts — MANC as a whole (from the paper text, VERIFIED)

- ~6,500 sensory neurons in MANC (abstract/discussion wording "nearly 6500"); another passage in the same PDF says the sensory typing pipeline covered **6,462 sensory neurons**. There is a small internal inconsistency between the modality tally and these totals (see next line).
- Modality tally, main text: **1,211 chemosensory + 1,347 proprioceptive + 2,497 tactile + 1,422 unknown = 6,477.**
- 1,328 descending neurons (per the same PDF: "descending neurons, 737 motor neurons, ~100 other efferent neurons, and nearly 6500 sensory neurons").
- 98.7% of neurons (16,556 of 16,778) matched across the midline, excluding sensory neurons and VUM neurons.
- Serial homologues identified for 36.7% of VNC-origin neurons.

## Leg sensory types — counts (VERIFIED from paper text)

> "we successfully reconstructed the majority of leg sensory neurons, surpassing previous
> efforts (Phelps et al., 2021), and identified **63 distinct cell types (9 chemosensory,
> 22 proprioceptive, 27 tactile, and 5 of unknown modality)**."

- Leg sensory output targets: ~67% intrinsic neurons, ~22% ascending neurons, ~9% each other, ≤1% everything else.
- Chemosensory leg types: 9; 7 present in all three leg pairs, `SNch08` T1-only (male-specific, fru+, pheromone), `SNch10` T1+T3 only.
- Proprioceptive leg types: 22, of which 19 map to known cell types/functional classes. **~25% of proprioceptive neurons could not be typed and were annotated `SNppxx`.**
- Tactile leg types: 27. Three morphological categories: intersegmental (`SNta22`, `SNta33`), bilateral (`SNta42`), and local (vast majority). `SNta41` is unusual for direct MN connectivity.
- Unknown leg types: 5 — `SNxx29` (ppk+, Gr28b.d+ **heat nociceptors**), `SAxx02`, `SNxx30` (likely proprioceptive), `SNxx32` (one per MesoLN, innervates midline), `SNxx33` (probably the single mechanosensory cell of each taste bristle).

## FeCO / chordotonal — YES, claw/hook/club are separable (VERIFIED)

> "We identified **24 distinct connectivity types of chordotonal sensory neurons: 13 from
> the femoral chordotonal organ (FeCO), three from Wheeler's organ, three from the
> prosternal chordotonal organ (pCO), and 5 unclassified types**. **Two of the FeCO types
> morphologically resemble the "hooks," two the "claws," and 9 the "clubs"** previously
> reported in the light-level literature (Mamiya et al., 2018)."

Named FeCO types in the paper (these are **v1.2.1** numbering):
- hooks: `SNpp39`, `SNpp41`
- claws: `SNpp50`, `SNpp51`
- clubs: 9 types, not individually enumerated in the text
- FeCO size reference: "~152 neurons located in the proximal femur" (citing Kuan et al., 2020).

Predicted signs in the tibia premotor circuit (from Marin et al. Fig 59D, via Cheong et al. companion):
- `SNpp41` (hook): inhibits tibia flexor + accessory tibia flexor MN via GABAergic serial type `IN19A015`; activates tibia extensor MN.
- `SNpp39` (hook): inhibits tibia extensor via GABAergic `IN19A005`, which also inhibits `IN19A015` → disinhibits tibia flexor + acc. tibia flexor MN.
- `SNpp51` (claw): activates tibia flexor + acc. tibia flexor; inhibits tibia extensor via two glutamatergic serial types.
- `SNpp50` (claw): activates tibia extensor directly and via two cholinergic serial types; weakly disinhibits flexors with delay.
- **FeCO club types have no appreciable effective connectivity to any motor neuron.**
- Claw/hook effective connectivity is **ipsilateral only** — no contralateral MN targets.

## Campaniform sensilla (VERIFIED)

> "Approximately 1200 campaniform sensilla (CS) are distributed over the legs, wings,
> halteres, and antennae of the fly (Gnatzy et al., 1987). We identified **46 CS types: 21
> from the wings, 6 from the base of the wings, 14 from the halteres, one serial type from
> the legs, and one from the antenna**."

- Trochanter CS (TrCS, "bilateral campaniform sensilla") = **`SNpp53`** (v1.2.1). Two per leg nerve except left prothoracic (consistent with Phelps et al. 2021). Bilateral morphology; strongest MN association is the Tergotrochanter MNs bilaterally, plus dorsal MNs iii1, STTMm, weakly i1/i2.
- Antennal CS descends to VNC as `DNx01` and shares TrCS-like connectivity.
- Leg CS other than TrCS were **NOT separable** from hair plates — they sit inside the untyped `SNppxx` pool.

## Hair plates (VERIFIED)

> "We annotated **two leg hair plate types, SNpp45 and SNpp52**, but there may be more in
> our unclassified proprioceptive population (SNppxx)."
- `SNpp19` = **neck/prosternal organ hair plate** (two fused hair plates, ventral neck; encodes head rotation). ~50% of its output onto ascending neurons; effective connectivity to bilateral TH1, TH2, AD, neck and haltere MNs.
- `SNpp45`: targets hemilineage 13B strongly (+19A); top partner `IN13B001`; stronger to plural remotor/abductor, sternal posterior + anterior rotator, sternal abductor MNs → candidate walking-speed/gait role.
- `SNpp52`: targets 14A and 13A (+19A); top partner `IN14A001`; strong onto tergopleural/pleural promotor MNs → candidate posture role. **Authors caveat that `SNpp52` might actually be a campaniform sensilla type, not a hair plate.**
- Hair plate and leg-CS afferents are morphologically near-identical, so this boundary is genuinely soft in MANC.

## Nerve nomenclature (VERIFIED, from the paper's VNC-anatomy section)

| abbrev | full name | neuromere |
|---|---|---|
| CvC | cervical connective (VNC↔brain) | — |
| CvN | cervical nerve (lateral to CvC) | — |
| DProN | dorsal prothoracic nerve | T1 |
| PrN | prosternal nerve | T1 |
| ProCN | prothoracic chordotonal nerve | T1 |
| ProAN | prothoracic accessory nerve | T1 |
| VProN | ventral prothoracic nerve | T1 |
| ProLN | prothoracic leg nerve | T1 |
| ADMN | anterior dorsal mesothoracic nerve | T2 |
| PDMN | posterior dorsal mesothoracic nerve | T2 |
| MesoAN | mesothoracic accessory nerve | T2 |
| MesoLN | mesothoracic leg nerve | T2 |
| DMetaN | dorsal metathoracic nerve | T3 |
| MetaLN | metathoracic leg nerve | T3 |
| AbN1–AbN4 | first–fourth abdominal nerves (bilaterally paired) | A |
| AbNT | fused abdominal nerve trunk | A |

There is **no `MetaAN`** in the MANC nerve vocabulary (only ProAN and MesoAN exist).
`ProLN` is NOT subdivided into named branches in MANC — instead the front leg's afferents
are split across four separate nerves.

**Which sensory populations arrive by which nerve (VERIFIED):**
- **Front leg (T1): ProLN + DProN + VProN + ProAN** — all four are pooled as "right/left front leg" origin for clustering.
- **Middle leg (T2): MesoLN only.**
- **Hind leg (T3): MetaLN only.**
- Neck / prosternal organ hair plate → **PrN**
- Prothoracic (prosternal) chordotonal organ pCO → **ProCN**
- Wing (blade CS, hinge CS, wing margin chemo + tactile bristles) → **ADMN**
- Notum (macro- and microchaetes) → **PDMN**
- Haltere (campaniform fields) → **DMetaN**
- Abdomen → AbN2, AbN3, AbN4, AbNT (one AbN1 afferent expected but not recovered).

## Modality layering in leg neuropil (VERIFIED)

Ventral→dorsal within LegNp: chemosensory (ventral-most, near midline, in the VAC) →
tactile (adjacent ventral, broad somatotopic spread) → proprioceptive (dorsal regions,
with organ-specific variation). FeCO **club** projections are restricted to the ipsilateral
**mVAC**; **claw** makes a three-pointed projection in ipsilateral LegNp; **hook** is
club-like with a single bifurcating process near entry.

In the neck connective, ascending sensory axons keep this order: chemosensory near the
ventral midline, tactile adjacent, proprioceptive more dorsal; and by body origin,
leg+notum ventromedial → neck → wing → haltere progressively more dorsal.

## Hemilineage targets by modality (VERIFIED)

- chemosensory → mainly 05B (and 09B)
- tactile → 01B, 05B, 09B, **especially 23B**
- proprioceptive → diverse; leg proprioceptors prefer **09A**
- chordotonal types → strongly upstream of 09A; one FeCO claw type → 13A; one FeCO hook type → 14A (notably *not* 13B, contra Agrawal et al. 2020)

---

# PRIMARY DATA: MANC v1.2.3 annotations pulled live from Janelia DVID

**How I got it (reproducible, no auth needed):**

```bash
# repo DAG -> find the tagged release node
curl -s https://manc-dvid.janelia.org/api/repo/1ec355123bf94e588557a4568d26d258/info
# v1.2.1 node = 3ddc3f3ca7c94af89b48c15442789629  ("2024-03-09 - MANC v1.2.1 for eLife submission")
# v1.2.2 / v1.2.3 node = 4dd0dc4934554caabf6555f914bc1aab   <-- what neuPrint serves as manc:v1.2.3
curl -s "https://manc-dvid.janelia.org/api/node/4dd0dc4934554caabf6555f914bc1aab/segmentation_annotations/keyrangevalues/0/Z?json=true" -o dvid_v123.json
```
→ 20 MB JSON, 27,408 body records, snake_case field names. **These are the actual
annotation values, VERIFIED by direct read, not second-hand.** Public read, no token.
(The v1.0 flat export is also public at `gs://flyem-manc-exports/v1.0/manc-v1.0-neuron-properties.feather`
— but **v1.0 sensory type numbers are DIFFERENT from v1.2.x**; the paper says sensory
neurons were "systematically retyped" between v1.0 and v1.2.1. Use v1.2.x.)

Full field list, v1.2.3 (snake_case; neuPrint serves the camelCase forms):
```
avg_location birthtime bodyid class cluster confidence description entry_nerve exit_nerve
group group_old hemilineage instance long_tract modality neuropils_axonal
neuropils_dendritic nt_acetylcholine_prob nt_gaba_prob nt_glutamate_prob nt_unknown_prob
old_bodyids origin position position_type predicted_nt predicted_nt_prob prefix
receptor_type reviewer root_position root_side serial serial_motif soma_neuromere
soma_position soma_side source status subclass subclassabbr subcluster synonyms
systematic_type tag target to_review tosoma_position transmission type typing_notes
user vfb_id
```

## `class` values, whole dataset (v1.2.3, n=27,408 bodies)

| class | n |
|---|---|
| intrinsic neuron | 13,066 |
| sensory neuron | 5,927 |
| (blank/NaN — untraced fragments, glia leftovers) | 3,211 |
| ascending neuron | 1,865 |
| descending neuron | 1,322 |
| motor neuron | 733 |
| sensory ascending | 535 |
| glia | 349 |
| TBD | 122 |
| Interneuron TBD | 113 |
| efferent neuron | 92 |
| Sensory TBD | 58 |
| efferent ascending | 9 |
| sensory descending | 6 |

**Total sensory-class bodies = 5,927 + 535 + 58 + 6 = 6,526.**
(Paper's text figure was 6,462 typed sensory neurons in v1.2.1; 6,477 by modality tally.
The 6,526 here is v1.2.3 and is the number you actually get from the database.)

## `modality` values for sensory neurons (v1.2.3) — VERIFIED counts

| modality | n |
|---|---|
| tactile | 2,502 |
| unknown | 1,430 |
| proprioceptive | 1,378 |
| chemosensory | 1,216 |
| **total** | **6,526** |

(Paper v1.2.1 text: tactile 2,497 / unknown 1,422 / proprioceptive 1,347 / chemosensory 1,211.)

## `subclass` values for sensory neurons — THE SENSILLUM VOCABULARY (v1.2.3)

This is the field that names the sense organ. Complete list with counts:

| subclass | n | modality |
|---|---|---|
| `mechanosensory bristle` | 2,473 | tactile (2,469) + unknown (4) |
| `` (blank) | 1,610 | mostly unknown (1,426) + proprioceptive (169) |
| `taste bristle` | 1,210 | chemosensory |
| `campaniform sensilla` | 564 | proprioceptive |
| `chordotonal organ` | 507 | proprioceptive |
| `hair plate` | 130 | proprioceptive |
| `metathoracic leg` | 10 | tactile (leftover v1.0-style value) |
| `mesothoracic leg` | 10 | mixed (leftover) |
| `prothoracic leg` | 4 | mixed (leftover) |
| `ut`, `xn` | 4, 2 | these are DN subclasses on `DNx01`/`DNx02`, not real sensory subclasses |
| `strand receptor` | 2 | proprioceptive |

So **the four real proprioceptor sensillum classes in MANC are:
`chordotonal organ` (507), `campaniform sensilla` (564), `hair plate` (130),
`strand receptor` (2)**, plus 169 proprioceptive neurons with a blank subclass.

## FeCO claw / hook / club ARE separable — they live in `synonyms`

`subclass` only says `chordotonal organ`. The **claw/hook/club distinction is in the
`synonyms` field** (neuPrint: `synonyms`). Complete sensory `synonyms` vocabulary (v1.2.3):

| synonyms value | n |
|---|---|
| `wing margin bristle` | 730 |
| `haltere CS` | 333 |
| `NA` (literal string) | 258 |
| **`FeCO club`** | **188** |
| `wing CS Whitlock and Palka 1995` | 132 |
| **`hair plate`** | **101** |
| **`FeCO claw`** | **95** |
| `proximal wing CS Dickerson et al 2019` | 85 |
| **`FeCO hook`** | **65** |
| `Wheeler's organ` | 60 |
| `pCO` | 51 |
| `ppk nociceptive` | 36 |
| `knob hair sensilla, Chan & Dickinson JCN 1996` | 36 |
| `neck hair plate` | 29 |
| `ppk heat nociceptive` | 23 |
| `medial Type I` | 12 |
| **`TrCS`** | **10** |
| `haltere CS dF2 Chan Dickinson JCN 1996` | 4 |
| `strand receptor` | 2 |

**FeCO total in MANC v1.2.3 = 188 club + 95 claw + 65 hook = 348 neurons across all 6 legs**
(i.e. ~58 per leg vs. the ~152/leg in the real animal — so MANC recovers roughly 38% of FeCO).

### The 24 chordotonal types, fully enumerated (VERIFIED from the database)

| group | systematic types | # types | # neurons |
|---|---|---|---|
| **FeCO club** | `SApp23`, `SNpp40`, `SNpp43`, `SNpp47`, `SNpp56`, `SNpp57`, `SNpp58`, `SNpp59`, `SNpp60` | 9 | 182 (+6 in `SNppxx`) |
| **FeCO claw** | `SNpp50`, `SNpp51` | 2 | 89 (+6 in `SNppxx`) |
| **FeCO hook** | `SNpp39`, `SNpp41` | 2 | 57 (+8 in `SNppxx`) |
| Wheeler's organ (abdominal, AbN3) | `SNpp01`, `SNpp02`, `SNpp03` | 3 | 60 |
| prosternal chordotonal organ pCO (ProCN) | `SNpp17`, `SNpp18`, `SNpp22` | 3 | 51 |
| unclassified chordotonal | `SNpp42`, `SNpp44`, `SNpp46`, `SNpp48`, `SNpp49` | 5 | 51 |
| | | **24** | |

This reproduces the paper's "24 distinct connectivity types of chordotonal sensory
neurons: 13 from the FeCO (2 hook, 2 claw, 9 club), three from Wheeler's organ, three from
the pCO, and 5 unclassified" **exactly**. Note `SApp23` is the one FeCO club type that
**ascends** to the brain (SA prefix) — worth knowing if you want brain-projecting FeCO.

### FeCO neuron counts per systematic type per leg nerve (v1.2.3, VERIFIED)

FeCO club (188):
```
                 MesoLN_L MesoLN_R MetaLN_L MetaLN_R ProLN_L ProLN_R
SApp23                  3        5        4        6       2       6
SNpp40                  4        5        5        5       0       5
SNpp43                  0        5        4        3       1       4
SNpp47                  2        6        6        9       1       3
SNpp56                  1        2        4        4       0       2
SNpp57                  3        4        3        0       1       1
SNpp58                  3        5        3        2       1       1
SNpp59                  1        1        1        2       2       1
SNpp60                  3       12       11       10       1       4
SNppxx (club-tagged)    0        2        0        1       1       1
```
FeCO claw (95):
```
SNpp50                 12       15       12       10       3      10
SNpp51                  4        7        2        6       1       7
SNppxx (claw-tagged)    1        1        2        2       0       0
```
FeCO hook (65):
```
SNpp39                  7        8        6        6       3       5
SNpp41                  3        4        3        5       3       4
SNppxx (hook-tagged)    2        1        1        2       1       1
```
Per-leg FeCO totals (by leg nerve): ProLN_L 21, ProLN_R 55, MesoLN_L 49, MesoLN_R 83, MetaLN_L 67, MetaLN_R 73.
**Front-leg (T1) FeCO recovery is markedly worse, T1-left worst of all.** Reconstruction
bias, not biology — the paper says so explicitly ("the fewest were recovered from the
front legs, whilst in general more neurons were recovered on the right side than the left").

### Hair plate + TrCS (v1.2.3, VERIFIED)

`synonyms == "hair plate"` (leg), n=101:
```
        DProN_L DProN_R MesoLN_L MesoLN_R MetaLN_L MetaLN_R ProAN_L ProAN_R ProLN_L ProLN_R VProN_L VProN_R
SNpp45        1       0        7        9        6        7       2       0       1       1       2       4   (=40)
SNpp52        3       3        2        2        1        6       0       1       0       2       0       0   (=20)
SNppxx        0       0        3        9        2       12       3       4       3       5       0       0   (=41)
```
Note: **leg hair plate afferents enter by FIVE different T1 nerves** (ProLN, ProAN, VProN,
DProN as well as the obvious one) — this is the clearest case where the front leg's
four-nerve split matters.

`synonyms == "neck hair plate"` = `SNpp19`, n=29, enters via `PrN_L`/`PrN_R` (prosternal organ).

`synonyms == "TrCS"` (trochanter campaniform sensilla), n=10:
`SNpp53` = 2 per nerve in MesoLN_L/R and MetaLN_L/R (8), plus 2 in `SNppxx` from `ProLN_R`.
**None from ProLN_L** — matches the paper's statement and Phelps et al. 2021.

`synonyms == "strand receptor"` = `SNpp54`, n=2, abdominal (`AbNT_L`, `AbNT_R`).

## Sensory neurons per entry nerve x modality — MANC v1.2.3, VERIFIED, complete

```
entry_nerve  chemo  proprio  tactile  unknown   total
ADMN_L         193      120      172       15     500   wing (CS, chemo+tactile margin bristles)
ADMN_R         198      115      177       12     502
AbN2_L           2        0        0       46      48
AbN2_R           2        0        0       38      40
AbN3_L           2       27        0       63      92   Wheeler's organ
AbN3_R           2       33        0       57      92
AbN4_L           8        0        0      279     287
AbN4_R           8        0        0      278     286
AbNT_L           6        1        0      102     109   strand receptor
AbNT_R           6        1        0      100     107
CvC              0        6        0        0       6   DNx01/DNx02 (antennal CS descending)
DMetaN_L         0      196       17        1     214   haltere
DMetaN_R         0      195       19        1     215
DProN_L          0        4       13        3      20   FRONT LEG
DProN_R          0        3       11        3      17   FRONT LEG
MesoLN_L        95       78      309       54     536   MIDDLE LEG
MesoLN_R       105      125      379       37     646   MIDDLE LEG
MetaLN_L       137      111      336       87     671   HIND LEG
MetaLN_R       153      137      402       55     747   HIND LEG
PDMN_L           0        6      120        3     129   notum bristles
PDMN_R           0        6      117        3     126
PrN_L            0       14        0        0      14   prosternal organ hair plate
PrN_R            0       15        0        0      15
ProAN_L          0        5        0        0       5   FRONT LEG
ProAN_R          0        5        0        0       5   FRONT LEG
ProCN_L          0       25        0        0      25   prosternal chordotonal organ pCO
ProCN_R          0       26        0        0      26
ProLN_L        161       35      220       80     496   FRONT LEG
ProLN_R        138       76      200      106     520   FRONT LEG
ProNTBD_L        0        0        0        2       2   (unresolved prothoracic nerve)
ProNTBD_R        0        6        0        1       7
VProN_L          0        2        4        2       8   FRONT LEG
VProN_R          0        5        5        2      12   FRONT LEG
? (blank)        0        0        1        0       1
-------------------------------------------------------
ALL           1216     1378     2502     1430    6526
```

**LEG nerves only (ProLN+ProAN+VProN+DProN+MesoLN+MetaLN, both sides) = 3,683 sensory
neurons: 1,879 tactile, 789 chemosensory, 586 proprioceptive, 429 unknown.**

Per leg (all six, summing the nerves that serve each):
- front-left  (ProLN_L + ProAN_L + VProN_L + DProN_L) = 496+5+8+20 = **529**
- front-right (ProLN_R + ProAN_R + VProN_R + DProN_R) = 520+5+12+17 = **554**
- middle-left  (MesoLN_L) = **536**, middle-right (MesoLN_R) = **646**
- hind-left    (MetaLN_L) = **671**, hind-right   (MetaLN_R) = **747**

Leg sensory by sensillum subclass x nerve (v1.2.3, VERIFIED):
```
                     DProN_L DProN_R MesoLN_L MesoLN_R MetaLN_L MetaLN_R ProAN_L ProAN_R ProLN_L ProLN_R VProN_L VProN_R  All
(blank)                    3       3       64       52      108       77       0       0      90     120       2       3   522
campaniform sensilla       0       0        2        2        2        2       0       0       0       2       0       0    10
chordotonal organ          0       0       54       90       81       91       0       0      23      57       0       0   396
hair plate                 4       3       12       20        9       25       5       5       4       8       2       4   101
mechanosensory bristle    13      11      304      375      328      395       0       0     218     194       4       5  1847
taste bristle              0       0       93      104      137      153       0       0     160     136       0       0   783
(v1.0 leftovers)           0       0        7        3        6        4       0       0       1       3       0       0    24
```
**Note the big gap: `campaniform sensilla` in the LEGS is only 10 neurons (the TrCS
only).** All other leg CS are unidentifiable and sit in the 522 blank-subclass +
`SNppxx` pool. The 564 `campaniform sensilla` total is dominated by wing and haltere.

## Complete sensory systematic-type inventory, MANC v1.2.3

Prefix counts: `SAch01`–`SAch02` + `SAchxx`; `SApp01`–`SApp23` + `SAppxx`;
`SAxx01`,`SAxx02`,`SAxxxx`; `SNch01`–`SNch12` + `SNchxx`; `SNpp01`–`SNpp63` + `SNppxx`;
`SNta01`–`SNta45` (with 15,16,17 absent) + `SNtaxx`; `SNxx01`–`SNxx33` + `SNxxxx`.
Plus `DNut035`/`DNxn051` which carry `modality=proprioceptive` but are DESCENDING
(`DNx02`, `DNx01` = antennal campaniform sensilla descending into the VNC via CvC).

Leg-nerve systematic types worth naming:
- **chemosensory (taste bristle):** `SNch05 SNch06 SNch07 SNch09 SNch10 SNch11` (serial, all legs),
  `SNch08` T1-only (male-specific fru+ pheromone; its `type` field splits into
  `SNch08/SNch13/SNch14/SNch15/SNch16`), `SNch01` abdominal, `SNch02/03/04/12` wing (ADMN).
  Ascending: `SAch01`, `SAch02` (SAch02 = sweet gustatory), `SAchxx`.
- **proprioceptive, leg:** FeCO/hair-plate/TrCS as tabulated above, plus `SNppxx` (152 total)
  as the catch-all.
- **tactile, leg:** the `SNta##` series; largest are `SNta29` (242), `SNta37` (164),
  `SNta20` (141), `SNta38` (118). `SNta22`/`SNta33` intersegmental, `SNta42` bilateral,
  `SNta41` unusually direct onto MNs.
- **unknown, leg:** `SNxx29` = ppk+/Gr28b.d+ **heat nociceptors** (n=23, `synonyms="ppk heat nociceptive"`);
  `SNxx33` (n=95, probably the single mechanosensory cell of each taste bristle);
  `SNxx30` (n=6, likely proprioceptive); `SNxx32` (n=2, one per MesoLN, midline);
  `SAxx02` (n=12, ascending, associated with SNxx29). Abdominal `SNch01`-associated
  ppk nociceptors carry `synonyms="ppk nociceptive"` (n=36).

## Practical neuPrint queries (camelCase!)

Cypher, on `neuprint.janelia.org`, dataset `manc:v1.2.3`:

```cypher
// ALL leg proprioceptors
MATCH (n:Neuron)
WHERE n.class IN ['sensory neuron','sensory ascending']
  AND n.modality = 'proprioceptive'
  AND n.entryNerve =~ '(ProLN|ProAN|VProN|DProN|MesoLN|MetaLN)_[LR]'
RETURN n.bodyId, n.type, n.systematicType, n.subclass, n.synonyms, n.entryNerve, n.target

// FeCO only, split by subtype
MATCH (n:Neuron)
WHERE n.subclass = 'chordotonal organ' AND n.synonyms STARTS WITH 'FeCO'
RETURN n.synonyms AS feco_subtype, n.systematicType, count(*) ORDER BY feco_subtype

// hair plates
MATCH (n:Neuron) WHERE n.subclass = 'hair plate' RETURN n.systematicType, n.entryNerve, count(*)

// everything with an SN/SA systematic type
MATCH (n:Neuron) WHERE n.systematicType =~ 'S[NA](ch|pp|ta|xx).*' RETURN n
```

neuprint-python equivalent:
```python
from neuprint import Client, NeuronCriteria as NC, fetch_neurons
c = Client('neuprint.janelia.org', dataset='manc:v1.2.3', token=TOKEN)
nrn, roi = fetch_neurons(NC(class_='sensory neuron', modality='proprioceptive'))
# or by systematicType regex:
nrn, roi = fetch_neurons(NC(systematicType='SNpp.*', regex=True))
```

`malevnc` (R/natverse) is the friendliest path and knows the DVID node aliases:
```r
natmanager::install(pkgs="malevnc")
library(malevnc)
m <- manc_meta()                       # all annotations
subset(m, class=='sensory neuron' & modality=='proprioceptive')
```

Field-name gotchas:
- **Clio/DVID uses `snake_case`; neuPrint uses `camelCase`.** `entry_nerve` ↔ `entryNerve`,
  `systematic_type` ↔ `systematicType`, `soma_neuromere` ↔ `somaNeuromere`.
- In neuprint-python, `class` is reserved → `NeuronCriteria(class_=...)`.
- `somaNeuromere`, `somaSide`, `hemilineage` are **empty for sensory neurons**. Use
  `entryNerve` and `rootSide`.
- `exitNerve` is for motor/efferent neurons only.
- `class` value is the string `"sensory neuron"` (lowercase, with the space), plus the
  separate `"sensory ascending"`, `"Sensory TBD"` (capital S!), `"sensory descending"`.
  Any query using only `class="sensory neuron"` silently drops the 535 ascending ones.
- `synonyms` is a free-text string; match with `=~` / `STARTS WITH`, not equality, if you
  want to be safe (values like `"FeCO club"` are clean here, but `"NA"` appears as a
  literal string in 258 rows).

## Leg neuropil ROI names (VERIFIED, from `all_ROIs.txt` in the v1.0 neuprint export)

`LegNp(T1)(L)` `LegNp(T1)(R)` `LegNp(T2)(L)` `LegNp(T2)(R)` `LegNp(T3)(L)` `LegNp(T3)(R)`
`mVAC(T1)(L/R)` `mVAC(T2)(L/R)` `mVAC(T3)(L/R)`
`Ov(L/R)` `ANm` `IntTct` `LTct` `CV` `GF(L/R)`
`NTct(UTct-T1)(L/R)` `WTct(UTct-T2)(L/R)` `HTct(UTct-T3)(L/R)`
plus every nerve as its own ROI: `ADMN(L/R)` `PDMN(L/R)` `DMetaN(L/R)` `DProN(L/R)`
`PrN(L/R)` `ProCN(L/R)` `ProAN(L/R)` `ProLN(L/R)` `VProN(L/R)` `MesoAN(L/R)` `MesoLN(L/R)`
`MetaLN(L/R)` `CvN(L/R)` `AbN1..4(L/R)` `AbNT`.
In the `target` annotation field the same regions appear without brackets:
`LegNpT3_R`, `mVACT2_L`, `Ov_L`, `ANm`, `UTct_R`, `multi`, dot-joined for multiples.
