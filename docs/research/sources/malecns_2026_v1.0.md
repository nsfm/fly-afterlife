# MaleCNS v1.0 — how it handles VNC leg sensory neurons

## Citation / provenance

- Dataset: **MaleCNS v1.0**, released **2026-06-08** (v0.9 was 2025-10-03/05). neuPrint
  dataset name **`male-cns:v1.0`**. CC-BY 4.0. FlyEM (HHMI Janelia) + Univ. Cambridge +
  MRC LMB + Google Research. — VERIFIED (fetched male-cns.janelia.org and /release/).
- Preprint: *Sexual dimorphism in the complete connectome of the Drosophila male central
  nervous system*, bioRxiv **10.1101/2025.10.09.680999**, v1 posted 2025-10-09, v2
  2025-10-30. — VERIFIED (search result + male-cns.janelia.org confirms a bioRxiv v2).
- Journal version: **Cell**, published 2026-09-03, title *"Sexual dimorphism in the
  complete Drosophila male central nervous system connectome"*, article
  `cell.com/cell/fulltext/S0092-8674(26)00942-6`. **Volume/pages and journal DOI: could
  not verify** (I did not open the Cell page).
- Headline numbers (**REPORTED SECOND-HAND from search snippets, not verified in source**):
  166,691 (or 166,700) neurons across brain + optic lobes + VNC; ~125 M synaptic
  connections; 11,691–11,710 cell types, of which 8,069 isomorphic, 138 sexually dimorphic,
  289 male-specific, 71 female-specific.

## What I DID verify: the actual annotation table

Downloaded the public flat file (no auth):
```
https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/body-annotations-male-cns-v1.0-minconf-0.5.feather   # 14 MB
```
→ **211,577 rows × 36 columns.** Columns:
```
assignedOlHex1 assignedOlHex2 birthtime bodyId class dimorphism entryNerve exitNerve
flywireType fruDsx group hemibrainType instance itoleeHl mancBodyid mancGroup mancSerial
mancType matchingNotes mcnsSerial receptorType rootSide serialMotif somaLocation
somaNeuromere somaSide status statusLabel subclass superclass supertype synonyms
tosomaLocation trumanHl type vfbId
```

**Key structural change vs MANC: MaleCNS adds a `superclass` field above `class`, and
`class` now carries the MODALITY, where MANC used a separate `modality` field.**
There is **no `systematicType` and no `modality` column in MaleCNS** — the MANC systematic
name has been promoted into `type` (and preserved in `mancType`).

### `superclass` values relevant to the VNC (VERIFIED counts)

| superclass | n |
|---|---|
| `vnc_intrinsic` | 13,161 |
| **`vnc_sensory`** | **6,370** |
| `ascending_neuron` | 1,846 |
| `descending_neuron` | 1,314 |
| `vnc_motor` | 708 |
| **`sensory_ascending`** | **537** |
| `vnc_efferent` | 94 |
| `vnc_tbc` | 38 |
| **`vnc_sensory_tbc`** | **36** |
| `vnc_endocrine` | 22 |
| **`sensory_descending`** | **12** |
| `efferent_ascending` / `efferent_descending` | 8 / 4 |

(Other superclasses are brain: `ol_intrinsic` 89,403, `cb_intrinsic` 32,164,
`visual_projection` 9,201, `ol_sensory` 6,098, `cb_sensory` 4,868, `cb_motor` 107, …)

**VNC sensory total = 6,370 + 537 + 36 + 12 = 6,955** (vs 6,526 in MANC v1.2.3 — MaleCNS
recovered ~430 more).

### `class` = modality, for VNC sensory neurons (VERIFIED)

| class | n (VNC sensory) |
|---|---|
| `mechanosensory_tactile` | 2,558 |
| `unknown_sensory` | 1,613 |
| **`mechanosensory_proprioceptive`** | **1,453** |
| `gustatory` | 1,153 |
| (blank) | 120 |
| `chemosensory` | 58 |

So MANC `modality="proprioceptive"` ⇒ MaleCNS `class="mechanosensory_proprioceptive"`;
`tactile` ⇒ `mechanosensory_tactile`; `chemosensory` ⇒ `gustatory` (or `chemosensory`);
`unknown` ⇒ `unknown_sensory`. Whole-dataset `class` also has `mechanosensory` (1,733,
mostly brain/JO), `mechanosensory_tbc` (11), `olfactory`, `visual`, `hygrosensory`,
`thermosensory`, etc.

### `subclass` = sensillum, for VNC sensory (VERIFIED)

`mechanosensory bristle` 2,206 · `abdomen` 1,143 · `leg` 872 · `leg bristle` 768 ·
**`campaniform sensilla` 426** · **`chordotonal organ` 425** · `wing bristle` 385 ·
`notum` 230 · `haltere` 205 · **`hair plate` 113** · `taste bristle` 70 · `wing` 46 ·
`neck` 2 · blank 64.

Same sensillum vocabulary as MANC, but MaleCNS also uses body-region values
(`leg`, `abdomen`, `notum`, `haltere`, `wing`) in the same field where MANC had left them blank.

### `entryNerve` — NO SIDE SUFFIX (VERIFIED)

MANC: `MetaLN_R`. **MaleCNS: `MetaLN`, with side in a separate `rootSide` field taking
`L`/`R` (not MANC's `LHS`/`RHS`).** Counts:

```
MetaLN 1521  MesoLN 1402  ADMN 1000  ProLN 991  AbN4 612  DMetaN 439  PDMN 282
AbN3 234  AbNT 208  AbN2 88  PrN 37  ProCN 37  DProN 32  VProN 19  ProAN 10
MxLbN 6  ON 4  AN 2  AbN1 2   (+29 blank)
```
Note the two new brain nerves `MxLbN` (maxillary-labial) and `ON`/`AN` — MaleCNS spans
the whole CNS so some SEZ nerves appear.

**Leg-nerve sensory neurons in MaleCNS v1.0 = 3,975** (ProLN 991 + ProAN 10 + VProN 19 +
DProN 32 + MesoLN 1,402 + MetaLN 1,521), vs 3,683 in MANC v1.2.3.
By side: L 1,956, R 2,019 — MaleCNS is much better balanced than MANC.
By class, leg nerves: tactile 1,903 · gustatory 768 · **proprioceptive 672** ·
unknown 523 · chemosensory 20.

### MANC types carry straight over into `type`

5,853 of 6,955 VNC sensory rows have a non-null `mancType`. The `type` field holds the
MANC systematic name verbatim (`SNta29`, `SNpp50`, `SApp23`, `SNppxx`, `SNxxxx`, …).
Two new wrinkles:
1. Some MaleCNS types are **comma-joined MANC types** where MANC's split did not hold up,
   e.g. `SNta02,SNta09` (241 neurons), `SApp09,SApp22` (74), `SNta04,SNta11` (53),
   `SApp23,SNpp56` (6). **Parse `type` by splitting on commas before matching `SN../SA..`.**
2. New MaleCNS-native leg types appear that have no MANC equivalent, notably
   **`LgLG1a` (136), `LgLG1b` (134), `LgLG2` (130), `LgLG3` (162)** and the wing
   `WG1`–`WG4` (96–97 each). `SApp` (148) appears as a bare prefix with no number.

### FeCO in MaleCNS v1.0 (VERIFIED, by mapping the MANC type list)

`synonyms` is **mostly unpopulated** in MaleCNS (only 15 `FeCO club`, 13 `FeCO claw`,
5 `FeCO hook`, 1 `hair plate`) — so you CANNOT use `synonyms` the way you can in MANC.
Instead match `type` against the MANC systematic-type list:

| FeCO subtype | MANC/MaleCNS types | n (MaleCNS v1.0) | per nerve |
|---|---|---|---|
| **club** | SApp23, SNpp40, SNpp43, SNpp47, SNpp56, SNpp57, SNpp58, SNpp59, SNpp60 | **207** | MetaLN 94, MesoLN 89, ProLN 23, ProAN 1 |
| **claw** | SNpp50, SNpp51 | **94** | MetaLN 48, MesoLN 41, ProLN 5 |
| **hook** | SNpp39, SNpp41 | **61** | MesoLN 28, MetaLN 22, ProLN 11 |
| **FeCO total** | | **362** | |

(MANC v1.2.3 gave 188/95/65 = 348. So MaleCNS ≈ MANC + ~14 for FeCO, still only ~60/leg
against the ~152/leg in the real animal.)

Hair plates: `subclass == 'hair plate'` → 113 neurons: `SNpp45` 52, `SNpp19` 35 (neck /
prosternal organ), `SNpp52` 26.
TrCS: `type` contains `SNpp53` → 13 neurons.

### Other useful MaleCNS fields

- `mancBodyid`, `mancType`, `mancGroup`, `mancSerial` — direct crosswalk back to MANC.
- `flywireType`, `hemibrainType` — crosswalk to FlyWire (female brain) and hemibrain.
- `dimorphism`, `fruDsx` — the sexual-dimorphism annotations that the Cell paper is about.
- `supertype` — a coarser grouping above `type`; **null for VNC leg proprioceptors**.
- `somaNeuromere` and `somaSide` are again **empty for sensory neurons**; use
  `entryNerve` + `rootSide`.
- `instance` = `type` + `_L`/`_R` (e.g. `SApp10_R`) — note this differs from MANC, where
  the sensory instance suffix was the *nerve*, e.g. `SNpp38_ProLN_R`.

### Query recipe (MaleCNS)

```cypher
// leg proprioceptors in male-cns:v1.0
MATCH (n:Neuron)
WHERE n.superclass IN ['vnc_sensory','sensory_ascending']
  AND n.class = 'mechanosensory_proprioceptive'
  AND n.entryNerve IN ['ProLN','ProAN','VProN','DProN','MesoLN','MetaLN']
RETURN n.bodyId, n.type, n.subclass, n.entryNerve, n.rootSide, n.mancType

// FeCO claw only
MATCH (n:Neuron) WHERE n.subclass='chordotonal organ'
  AND (n.type CONTAINS 'SNpp50' OR n.type CONTAINS 'SNpp51') RETURN n
```

Other MaleCNS download URLs (all public, VERIFIED from male-cns.janelia.org/download/):
```
gs://flyem-male-cns/v1.0/segmentation                                (8 nm segmentation)
gs://flyem-male-cns/rois/malecns-vnc-neuropil-roi-v0                 (VNC neuropil ROIs, 256 nm)
gs://flyem-male-cns/rois/fullbrain-roi-v4
gs://flyem-male-cns/v1.0/segmentation/skeletons-malecns/skeletons-swc/
.../flat-connectome/body-annotations-male-cns-v1.0-minconf-0.5.feather   13 MB
.../flat-connectome/connectome-weights-male-cns-v1.0-minconf-0.5.feather 1.1 GB
.../flat-connectome/syn-partners-male-cns-v1.0-minconf-0.5.feather       6.8 GB
.../flat-connectome/body-neurotransmitters-male-cns-v1.0.feather          42 MB
```
