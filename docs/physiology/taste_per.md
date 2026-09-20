# Tarsal taste to proboscis extension: what is known, what our table carries, and where the path dies

**2026-09-19. Written by an opus research agent for nyx.**

Scope: the five questions, answered against (a) the literature, (b) Shiu et al.'s own code and
supplementary tables (their repo is checked out at `ref/Drosophila_brain_model`), (c) FlyWire v783
annotations at `data/flywire/neuron_annotations.tsv`, and (d) the MaleCNS v1.0 tables in `data/`.
Marks: **(M)** measured and published; **(ours)** read out of our own data files; **(I)** my
inference; **(?)** could not verify.

---

## 0. Three findings that change the question

1. **We have been holding sugar on the wrong leg cells.** `world/pair.py:127` selects
   `LgLG*` plus `claw_tpGRN`, 719 cells. Those 669 `LgLG*` cells are
   `superclass = vnc_sensory`: leg-bristle GRNs whose axons stay in the leg neuropils. The male
   CNS also contains **`LgAG1`..`LgAG9`, 76 cells, `class = gustatory`, `subclass = leg bristle`,
   `superclass = sensory_ascending`**, entering by ProLN/MesoLN/MetaLN, `mancType` SAch01/SAch02
   (ours). Those are the **ascending** tarsal gustatory neurons, and they are not in our drive
   set. In the animal that split is Thoma et al. 2016's atGRNs (ascending, required for feeding
   initiation) versus stGRNs (segmental, mediate sugar-dependent suppression of locomotion). We
   have been driving the locomotion class and reading the feeding readout. **(ours + M)**

2. **The 719-cell set is also 50 labellar cells.** `claw_tpGRN` is `superclass = cb_sensory`,
   `subclass = taste peg`, `entryNerve = MxLbN` (the proboscis nerve) (ours). And **every one of
   the 212 direct synapses from the 719-cell set onto GNG014/GNG125/GNG271/GNG391 comes from
   those 50 taste-peg cells; the 669 `LgLG*` cells make zero** (ours, §4.1). The "second-synapse
   wall" for the leg path is mis-stated: at MN9 and DNg105 there is no first synapse to be gained.

3. **A sugar label for the legs does exist, published this year, and our own type column already
   carries it.** Tastekin et al. (2026, *Cell* 189:5527-5551.e5) built the pan-CNS gustatory
   connectome on this very dataset and assigned molecular identity to the MaleCNS GRN types by
   registering GAL4 lines onto the EM projection fields. **`LgLG4` (43 cells, `mancType` SNch11)
   is the tarsal sugar GRN: Gr64f plus Ir56b.** `LgAG2` (11, Gr61a) is the ascending appetitive
   class and `LgAG1` (25, Gr33a) the ascending bitter one. On the labellum the same paper splits
   FlyWire's undifferentiated `sugar/water` into **LB3a = ppk28 water, LB3b = Ir56b low salt,
   LB3c = Gr64f sugar, LB3d = Ir47a aversive** (§2). So the question "drive only a
   sugar-labelled subset" has a concrete answer for both organs, today, with no body-ID mapping
   needed.

---

## 1. Shiu et al. 2024: what they actually did for proboscis extension

**Citation.** Shiu, P. K., Sterne, G. R., Spiller, N., Franconville, R., Sandoval, A., Zhou, J.,
Simha, N., Kang, C. H., Yu, S., Kim, J. S., Dorkenwald, S., Matsliah, A., Schlegel, P., Yu, S.-C.,
McKellar, C. E., Sterling, A., Costa, M., Eichler, K., Bates, A. S., Eckstein, N., Funke, J.,
Jefferis, G. S. X. E., Murthy, M., Bidaye, S. S., Hampel, S., Seeds, A. M., Scott, K. (2024).
"A *Drosophila* computational brain model reveals sensorimotor processing." *Nature*
634(8032):210-219. doi:10.1038/s41586-024-07763-9. PMC11446845.
Preprint bioRxiv 2023.05.02.539144. Code github.com/philshiu/Drosophila_brain_model
(ours: `ref/Drosophila_brain_model`). Simulation output doi:10.17617/3.CZODIW. **(M)**

### 1.1 Which GRNs

**Labellar sugar GRNs, 21 cells, one hemisphere.** Not tarsal, and not bilateral. The 21 FlyWire
v630 root IDs are in `neu_sugar` in `figures.ipynb` (ours) and as rows `sugar_l_1..sugar_l_21` in
their Supplementary Table 1A. Companion sets: **bitter 21, Ir94e 18, water 18**, all unilateral.
**(M)**

A trap worth writing down: their Methods say they activated the **left** hemisphere because
reconstruction there is more complete, while the code names everything `sugarR` / "right
hemisphere". FAFB was found to be left-right inverted; the paper reports the true biological side.
Same 21 neurons either way. **(M)**

They never activated tarsal GRNs, and could not have: FlyWire is a brain without a ventral nerve
cord, so leg GRN somata are absent. The only leg-derived gustatory cells in FlyWire are the 74
that ascend through the cervical connective (`cell_sub_class = SA_VTV_pro_meso_meta`, types
`SA_VTV_1..10`, nerve CV), and they carry no modality label (ours). **(M/ours)**

### 1.2 How they selected the sugar GRNs

Their Methods, "Classification of GRNs", verbatim in the relevant part: bitter and Ir94e GRNs were
identified previously by distinctive morphology (their ref 23 = **Engert, Sterne, Bock & Scott
2022, *eLife* 11:e78110**, doi:10.7554/eLife.78110, which reconstructed 87 labellar gustatory
projections on the right and 57 on the left and clustered them into six groups). Water and sugar
GRNs were likewise identified by morphology; Shiu et al. then re-clustered GRNs hierarchically on
their connectivity onto second-order neurons (cosine distance), got three clusters, and assigned
cluster 2 = sugar and cluster 3 = water by which second-order cells each drives (G2N-1 and FMIn
respond exclusively to sugar; Usnea exclusively to water). Cluster 1 they speculate is
Ppk23-glut / salt. The 21 is deliberately small: *"As a conservative measure, we chose to examine
only those sugar GRNs that fully correspond between the GRN to second-order clustering and the
zero-order to GRN clustering."* **(M)**

### 1.3 Rates, duration, readout, and the actual numbers

| parameter | value |
|---|---|
| drive | Poisson input, weight `w_syn * f_poi`, `f_poi = 250` (**code only**, not in the paper) |
| sugar sweep (Fig 1D) | 10-200 Hz in 10 Hz steps |
| water sweep (Fig 4) | 20-260 Hz in 20 Hz steps |
| silencing screen | 50-120 Hz in 10 Hz steps |
| downstream activation screen (Fig 1E) | 25, 50, 75, 100, 125, 150, 175, 200 Hz |
| trial | 1,000 ms, 30 trials, averaged |
| readout | **MN9**, FlyWire 720575940660219265 (contra) and 720575940645521262 (ipsi) |

**MN9 firing rate versus sugar GRN rate** (their Supplementary Table 1A, mean of 30 trials, Hz):

| sugar GRN Hz | 10 | 20 | 30 | 40 | 50 | 60 | 70 | 80 | 100 | 150 | 200 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MN9 contra | 0 | 0 | **0.33** | 4.83 | 19.43 | 36.40 | 50.03 | 58.13 | **65.70** | 83.67 | 93.23 |
| MN9 ipsi | 0 | 0 | 0.20 | 3.67 | 15.97 | 27.13 | 37.20 | 42.60 | 49.67 | 60.10 | 62.90 |

**MN9 first fires at 30 Hz of sugar GRN drive**, and the steep part is 40-70 Hz. **Our held-taste
stimulus was 24 Hz, which is below Shiu's own PER threshold even at his 0.275 mV.** That is worth
holding onto before blaming the constant. **(M)**

Other motor neurons they report activated: **MN6, MN8, MN9 and MN11**. MN8 is the earliest to
fire (1.10 Hz already at 20 Hz drive). **MN12 is never mentioned in the paper.** **(M)**

They also state the contralateral MN9 is driven more strongly than the ipsilateral one by
unilateral activation, matching the behavioural observation that unilateral **leg** taste evokes
a curved proboscis extension toward the food. **(M)**

Scale: of 127,400 modelled neurons, 45 respond to 10 Hz sugar and 455 to 200 Hz. A shuffled
connectome activates MN9 in 1 of 100 simulations versus 100 % for the real one. **(M)**

### 1.4 Constants, and where 0.275 mV came from

Stated in the paper's Methods: V_resting = -52 mV, V_reset = -52 mV, V_threshold = -45 mV
(a 7 mV span), R_mbr = 10 kOhm cm^2, C_mbr = 2 uF cm^-2 (so T_mbr = RC = 20 ms, **derived, the
literal "20 ms" appears only in the code**), tau = 5 ms, T_refractory = 2.2 ms, T_delay = 1.8 ms,
**W_syn = 0.275 mV, explicitly "the single free parameter"**. `f_poi = 250` is code only; at
0.275 mV that makes each Poisson event 68.75 mV, ten times threshold, which is why driven GRNs
track their commanded rate nearly 1:1. **(M)**

The calibration sentence, verbatim: *"We chose Wsyn such that activation of sugar GRNs at 100 Hz
resulted in roughly 80% of maximal MN9 firing"*, citing Dahanukar et al. 2007 and Inagaki et al.
2012 for 100 Hz being a near-maximal physiological sugar GRN rate. **So the free parameter was set
by the PER dose-response itself.** (Their own Supp Table 1A gives 65.70 / 93.23 = 70 % at 200 Hz,
and the curve has not plateaued, so the criterion is not exactly reproducible from the published
data.) **(M, with the inconsistency flagged.)**

Robustness, from their Methods: W_syn -30 % keeps 90.2 % of predictions and 85 % accuracy but
**water GRNs largely lose the ability to activate MN9**; +30 % keeps 95 % and 88 %. They did not
test v_rest, v_th, t_mbr, t_dly or t_rfc, arguing that scaling W_syn is equivalent to scaling the
rest-to-threshold distance. **That argument is the one that licenses our 0.185 mV as a legitimate
knob, and it also says a 33 % cut is at the edge of where their own water result broke.** **(M,
with the last sentence (I).)**

Integration: Brian2 `method='linear'` on `dv/dt = (v_0 - v + g)/t_mbr`, `dg/dt = -g/tau`,
`g += w` on spike, with `w` = synapse count x (+1/-1 from the Eckstein et al. 2024 neurotransmitter
predictions) x W_syn. That is exactly what `world/fastlif.py::_membrane_exact` reproduces. **(M)**

### 1.5 Depth

The paper never states a hop count in prose. Three converging sources:

- Their **Fig 1b** lays the circuit out in labelled tiers: sugar GRNs -> second order (Zorro,
  G2N-1, Usnea, Clavicle, Rattle, FMIn) -> third order (Sternum, Bract 1, Bract 2, Fdg) ->
  premotor (Roundup, Roundtree, Rounddown) -> MN9. Four synapses on the canonical path, with
  second-order-to-premotor skip connections drawn.
- Their **Supplementary Table 3** has a "shortest path" column: Roundup = 1 synapse from MN9;
  G2N-1, Clavicle, Fdg, Bract, Rattle, FMIn, Fudog, Phantom = 2; Usnea = 3.
- Shiu et al. 2022's abstract says the circuit connects GRNs to proboscis MNs "through three
  intermediate layers".

**In our own table the shortest anatomical path from a labellar sugar GRN to MN9 is two synapses**
(no monosynaptic GRN -> MN9 connection exists; 552 two-hop synapses via ~250 intermediates)
(ours). Gordon & Scott (2009) showed the absence of direct GRN-to-MN contact experimentally
(GRP/split-GFP negative), which is why the interneuron hunt happened at all. **(M/ours)**

### 1.6 Validation

- **Retrospective**: of ten cell types previously shown to respond to sugar and be sufficient for
  PER, the model predicts all ten respond and eight are sufficient to drive MN9. Phantom and
  Usnea fail; they explain Phantom as an inhibitory cell whose effect cannot show in a model with
  zero basal firing, and they tested the Usnea failure prospectively by knocking down
  *amontillado* (PC2), which phenocopied the Usnea silencing phenotype.
- **Unbiased optogenetic screen** (their Fig 2): 106 of the 138 SEZ split-GAL4 cell types of
  **Sterne, Otsuna, Dickson & Scott 2021, *eLife* 10:e71679** matched into FlyWire, crossed to
  CsChrimson, scored blind for rostrum extension. 101/106 = 95.3 %.
- **Headline**: 150 of 164 testable predictions, **91 %**; excluding the split-GAL4 screen,
  49/58 = **84 %**. The weakest category is "required for sugar feeding initiation",
  **6/10 = 60 %**.
- **Novel and confirmed**: Ir94e activation is aversive and blocks PER to 50 mM but not 1 M
  sucrose (bitter blocks both); 5 of 6 predicted water-silencing phenotypes confirmed; calcium
  imaging of Fudog and Zorro; silencing sugar GRNs reduces PER to water. **(M)**

---

## 2. Labels: does a sugar / bitter / water identity exist, and can we transfer one?

### 2.1 FlyWire v783 / Codex: yes, for the labellum

Read directly from `data/flywire/neuron_annotations.tsv` (ours):

| `cell_sub_class` | n | `cell_type` | nerve |
|---|---|---|---|
| `sugar/water` | 129 | `LB3` (122), `LB2d` (7) | MxLbN |
| `bitter` | 65 | `LB1e` (23), `LB1c` (18), `LB1a,LB1d` (17), `LB1b` (7) | MxLbN |
| `low-salt` | 19 | `LB2a-b` (8), `LB2c` (7), `LB4a` (4) | MxLbN |
| `taste peg` | 71 | `claw_tpGRN`, `dorsal_tpGRN` | MxLbN |
| `SA_VTV_pro_meso_meta` | 74 | `SA_VTV_1..10` | CV |
| pharyngeal groups | 50 | | aPhN, PhN |

Three things follow. **Sugar and water are not separated** in FlyWire; the class is `sugar/water`.
**Taste pegs carry no modality label.** And the 74 leg-derived ascending gustatory axons - the
ones that matter for tarsal taste reaching the brain - **carry no modality label either**; they
are typed only by morphology (`SA_VTV_1..10`, from Stürner et al. 2025, *Nature* 643:158-172,
doi:10.1038/s41586-025-08925-z). **(M/ours)**

Provenance: the modality values are Engert's, and the `LB*` type strings are Schlegel's. **Engert,
Sterne, Bock & Scott (2022), *eLife* 11:e78110** reconstructed 87 labellar GRN axons on the right
and 57 on the left in FAFB (CATMAID, not FlyWire auto-segmentation) and clustered them into six
groups, *named "group 1".."group 6"* - the LB nomenclature is not in that paper. Group assignment:
1 and 2 bitter, 3 low salt, 4 sugar, 5 high salt (tentative, by elimination), 6 water. It covers
**no taste pegs and no leg GRNs**. The `LB1a..LB4a` strings come from the supplementary annotation
table of **Schlegel et al. (2024), *Nature* 634:139-152**, whose Methods attribute the modality to
Engert. Underlying salt biology: **Jaeger et al. 2018, *eLife* 7:e37167**; Ir94e and male genital
presentation: Taisz et al. 2023, *Cell* 186:2556-2573.e22. **(M)**

Two cautions before joining on FlyWire types. **`LB4b` does not exist in v783**; it is a MaleCNS
type. And FlyWire assigns its `LB4a` cells to a different set than MaleCNS `LB4a` does. So a join
through `flywireType` collapses distinctions the MaleCNS typing already makes, and in one place
mismatches. Use the MaleCNS `type` column instead (§2.4). **(M)**

### 2.2 The hemibrain

Cropped above the SEZ; contains no gustatory sensory neurons. Consistent with that,
`hemibrainType` is null for all 719 cells in our leg set, for all 76 `LgAG*` and for all `LB*`
cells (ours). **(M/ours)**

### 2.3 What our MaleCNS table carries for the legs, and what Tastekin et al. 2026 assigns

The MaleCNS v1.0 annotation is the carrier; the identities are from **Tastekin, de Haan Vicente,
Beresford, Morris, Beckett, Schlegel, Gkantia, Marin, Costa, Jefferis & Ribeiro (2026). "The
complete gustatory connectome of adult *Drosophila* reveals how taste guides feeding, foraging,
and social behavior." *Cell* 189(18):5527-5551.e5, doi:10.1016/j.cell.2026.08.016** (preprint
bioRxiv 2025.08.25.671814). That paper types every GRN from labellum, pharynx, all six legs and
the wing margins in this volume, cross-matched to MANC and FAFB-FlyWire, and assigns molecular
identity by registering GAL4 driver confocal stacks onto the EM projection fields plus
shared-downstream-partner logic. The dataset release itself is **Berg, Beckett, Costa, Schlegel
et al. (2026), *Cell* 189(18):5504-5526.e15, doi:10.1016/j.cell.2026.08.015**. **(M)**

| MaleCNS `type` | n (ours) | `mancType` | `receptorType` (ours) | Tastekin et al. identity |
|---|---|---|---|---|
| LgLG1a | 136 | SNch05 | `putative_ppk23` | VGlut- / fru+ / ppk23+ / ppk25- pheromone |
| LgLG1b | 134 | SNch05 | `putative_ppk25` | VGlut+ / fru+ / ppk23+ / ppk25+ pheromone |
| LgLG2 | 130 (129 gust.) | SNch06 | `putative_IR52b` | fru- / Ir52a+ / Ir52b+ pheromone |
| LgLG3 | 162 | SNch07 / SNch09 | none | **no molecular identity assigned** |
| **LgLG4** | **43** | **SNch11** | none | **Gr64f + Ir56b: the tarsal SUGAR GRN (+ appetitive low salt)** |
| LgLG5 / LgLG8 | 13 / 14 | SNch16 / SNch13 | `putative_ppk25` | male foreleg pheromone, ppk23+/ppk25+ |
| LgLG6 / LgLG7 | 16 / 21 | SNch15 / SNch14 | `putative_ppk23` | male foreleg pheromone, ppk23+/ppk25- |
| **LgAG1** | **25** | **SAch02** | none | **Gr33a: ascending tarsal BITTER** |
| **LgAG2** | **11** | **SAch01** | none | **Gr61a: ascending tarsal SUGAR / appetitive** |
| LgAG3/4/8 | 7 / 8 / 9 | SAch01 | none | mid- and hindleg only |
| LgAG5/6/7/9 | 4 / 4 / 5 / 3 | SAch01 | none | foreleg-restricted |
| claw_tpGRN / dorsal_tpGRN | 50 / 10 | none | none | claw and dorsal taste pegs (labellar) |
| LB1a-d | 38 | | | **Gr33a bitter** |
| LB1e | 19 | | | Ir94e (aversive) |
| **LB3a** | **17** | | | **ppk28: water** |
| **LB3b** | **11** | | | **Ir56b: low salt, overlapping sugar** |
| **LB3c** | **23** | | | **Gr64f: sugar** |
| **LB3d** | **26** | | | **Ir7c / ppk23 / Ir47a: high salt, aversive** |
| LB4a / LB4b | 4 / 8 | | | new in MaleCNS, uncharacterised |

Three things about `receptorType` (ours): it takes exactly three values across the whole male CNS
(`putative_ppk23` 269, `putative_ppk25` 257, `putative_IR52b` 226; 752 cells, all `vnc_sensory`,
leg bristles 463 and wing bristles 288 = WG1/WG3/WG4); **there is no sugar, bitter, water or salt
value in it**; and the `ppk23` versus `ppk25` split encodes ppk25- versus ppk25+, since all six
types are ppk23+. The column is used *only* for the pheromone assignments, so a sugar subset has
to come from the `type` column, not from `receptorType`.

The pheromone biology behind those labels: Thistle et al. 2012, *Cell* 149:1140-1151;
Lu et al. 2012, *PLoS Genet.* 8:e1002587 (which states plainly that these bristles are distinct
from the feeding-gustatory ones and that disrupting ppk23 does not alter gustatory responses);
Toda et al. 2012, *Cell Rep.* 1:599-607; Starostina et al. 2012, *J. Neurosci.* 32:4665-4674;
Vijayan et al. 2014, *PLoS Genet.* 10:e1004238; Kallman, Kim & Scott 2015, *eLife* 4:e11188 (which
defines the four marker-combination populations and their shared target PPN1). **(M)**

**One label to be sceptical of: `putative_IR52b`.** Koh et al. (2014, *Neuron* 83:850-865) detected
no expression at all from an Ir52b-GAL4 driver; the male foreleg receptors they established are
**IR52c and IR52d**. The connectome label rests on Luo, Talross & Carlson (2024, *Curr. Biol.*
34:5395-5408.e6) plus downstream-partner inference. If we ever need a defensible peripheral
receptor for LgLG2 / SNch06, Ir52a is on firmer ground than Ir52b. **(M)**

**Independent confirmation from our own data.** Tastekin et al. name PPN1 (= `AN05B102a` in
MaleCNS) as the shared target of the ppk23/ppk25 populations, and say LgLG3 is "Dandelion-
connected" with no identity assigned. In our table AN05B102a receives 13,483 leg-GRN synapses of
which 8,017 are LgLG1a and 5,354 LgLG1b, and `AN13B002 [Dandelion]` receives 8,770 of its 12,547
leg-GRN synapses from LgLG3 (ours). Both match exactly, which is a good check that we are reading
the same table they annotated.

### 2.4 The labels, exactly how to apply them

Select on the MaleCNS `type` column. Do **not** route through `flywireType`: it folds LB3a-d back
into one `LB3`, has no `LB4b`, and disagrees with MaleCNS about which cells are `LB4a`.

```python
# tarsal, Tastekin et al. 2026
SUGAR_LEG      = np.flatnonzero(mty == "LgLG4")                       # 43, Gr64f + Ir56b, local
SUGAR_LEG_ASC  = np.flatnonzero(mty == "LgAG2")                       # 11, Gr61a, ascending
BITTER_LEG_ASC = np.flatnonzero(mty == "LgAG1")                       # 25, Gr33a, ascending
PHEROMONE_LEG  = np.flatnonzero(np.isin(mty, ["LgLG1a","LgLG1b","LgLG2",
                                              "LgLG5","LgLG6","LgLG7","LgLG8"]))   # 364
# labellar
SUGAR_LAB      = np.flatnonzero(mty == "LB3c")                        # 23, Gr64f
WATER_LAB      = np.flatnonzero(mty == "LB3a")                        # 17, ppk28
LOWSALT_LAB    = np.flatnonzero(mty == "LB3b")                        # 11, Ir56b
AVERSIVE_LAB   = np.flatnonzero(np.isin(mty, ["LB3d","LB1a","LB1b","LB1c","LB1d","LB1e"]))  # 83
```

The coarser FlyWire-compatible set, if we want to match Shiu et al.'s `sugar/water` class rather
than the finer split, is `flywireType in {"LB3","LB2d"}` = 91 cells (ours), which is LB3, LB3a-d,
LB4b and LB2d together.

### 2.5 What is still missing for the legs

- **FlyWire has nothing.** `flywireType` is empty for all 669 `LgLG*` and 75 of 76 `LgAG*` cells;
  the one exception carries `SA_VTV_8` (ours). FlyWire has no VNC, and its 74 `SA_VTV_*` ascending
  gustatory axons carry no modality.
- **MANC has modality but not quality.** `mancBodyid` is filled for 18,715 cells overall but only
  40 of the 719 leg gustatory cells, so the join is by **`mancType`**, one line (ours). In the
  MANC nomenclature `SN` = sensory neuron, `SA` = sensory ascending, and the second component is
  the modality, drawn from exactly four values: chemosensory / tactile / proprioceptive / unknown
  (Marin et al. 2024, *eLife* 13:RP97766). So `SNch11` is "chemosensory type 11"; the fact that it
  is sugar comes from Tastekin, not from MANC. **(M)**
- **FANC** (Azevedo et al. 2024, *Nature* 631:360-368) has no GRN typing at all.
- **LgLG3, the largest leg class (162 cells), still has no molecular identity** in any paper,
  ours included. It is also the class that supplies essentially all the leg drive onto AN04A001
  (1,449 of 1,459), DNge153 (4,164 of 4,212), DNpe029 (2,784 of 3,564) and Dandelion (8,770 of
  12,547) (ours). It is the single largest unknown in the tarsal taste path and it is doing most
  of the work in our runs. **(M/ours)**

---

## 3. The circuit in life: tarsal sugar to proboscis, and to stopping

### 3.1 The split at the sensory neuron, which is the thing to know

**Thoma, Knapek, Arai, Hartl, Kohsaka, Sirigrivatanawong, Abe, Hashimoto & Tanimoto (2016).
"Functional dissociation in sweet taste receptor neurons between and within taste organs of
Drosophila." *Nature Communications* 7:10678. doi:10.1038/ncomms10678.** Two anatomically and
functionally distinct sweet GRN classes in the leg:

- **atGRNs** (ascending tarsal): axons project to the brain / gnathal ganglion. **Required for
  feeding initiation** - blocking them impairs PER to tarsal sucrose.
- **stGRNs** (segmental tarsal): terminate in the thoracic neuromere. Mediate **sugar-dependent
  suppression of locomotion**.

**(M.)** That is the single most load-bearing paper for our question, and Tastekin et al. 2026
draw the same line in this connectome: **lgAGRNs** ascend through the cervical connective to the
SEZ (our `LgAG1..LgAG9`, 76 cells) and **lgLGRNs** terminate in the T1/T2/T3 leg neuropils (our
`LgLG1a..LgLG8`, 669 cells). **We drove the local class and measured PER.**

Sharper still, now that the molecular identities exist: the tarsal **sugar** GRN of the local
class is `LgLG4` (43 cells, Gr64f + Ir56b) and the ascending appetitive class is `LgAG2` (11
cells, Gr61a). So Thoma's stGRN maps to LgLG4 and his atGRN to LgAG2, and **the entire tarsal
appetitive population in this connectome is 54 cells, not 719.** Tastekin et al. also note that
LgLG4 routes toward pharyngeal pumping through `AN05B106` and needs about **seven hops** to reach
maximum effective connectivity onto the feeding motor neurons, which is a direct warning about
what a two-synapse read of our table will and will not show. **(M)**

The named ascending interneuron is **TPN1**: Kim, Kirkhart & Scott (2017), *eLife* 6:e23386,
doi:10.7554/eLife.23386 - two somata in the metathoracic neuromere, dendrites overlapping sweet
GRN axons in each leg ganglion, axons ascending to the SEZ, sugar-selective, activation increases
PER, silencing does not abolish it. TPN2/TPN3 go to SLP and lateral horn for taste learning, not
to the motor path. **I could not find a `TPN1` type in our table** (`TPN` matches only `tpn MN`,
unrelated) (ours, **?**).

What does not exist in the literature: any traced tarsal-GRN -> named ascending neuron -> named
SEZ cell -> MN9 chain. Chen et al. 2023 (*Nat. Neurosci.* 26:682-695) show ascending neurons carry
behavioural state, not taste. Walker, Peña-Garcia & Devineni 2025 (*Sci. Rep.* 15:5278) restrict
their connectomic taste analysis to labellar GRNs and call leg input speculative. **(M/?)**

### 3.2 The SEZ feeding chain and the motor map

- **MN9 = rostrum lifting / protraction**, the E49-GAL4 pair, necessary and sufficient for
  rostrum extension: Gordon & Scott (2009), *Neuron* 61:373-384,
  doi:10.1016/j.neuron.2008.12.033.
- The full proboscis motor map: **Schwarz, Bohra, Liu, Reichert, VijayRaghavan & Pielage (2017),
  *eLife* 6:e19892**, doi:10.7554/eLife.19892. One bilateral MN pair per movement step:
  **MN9 rostrum protraction, MN2 haustellum extension, MN6 labellar extension, MN8 labellar
  spreading, MN1 active retraction, and MN5/MN10/MN11/MN12 the pharyngeal pump.** Recruitment is
  **not** feed-forward; a central command circuit recruits each MN independently.
  **So our `MN11D`/`MN12D` are pump motor neurons, not haustellum**, and reading them as "the
  pump" in the 19:02 table was right. Geometry and per-muscle drivers: McKellar, Siwanowicz,
  Dickson & Simpson (2020), *eLife* 9:e54978. **(M)**
- **Fdg**: a single pair, command-like for the whole feeding motor program. Flood, Iguchi,
  Gorczyca, White, Ito & Yoshihara (2013), *Nature* 499:83-87, doi:10.1038/nature12208. **(M)**
- **IN1** - and this is a correction to the brief's framing: Yapici, Cohn, Schusterreiter, Ruta &
  Vosshall (2016), *Cell* 165:715-729, doi:10.1016/j.cell.2016.02.061. Twelve cholinergic local
  interneurons connecting **pharyngeal** sugar GRNs to ingestion drive. They gate meal-bout
  structure, not PER, and they are downstream of the proboscis already being in the food. **IN1 is
  not on the tarsal-to-PER path.** **(M)**
- **The named taste-circuit cells**: Shiu, Sterne, Engert, Dickson & Scott (2022),
  ***eLife* 11:e79887**, doi:10.7554/eLife.79887 - **not *Current Biology*.** Layers as reported:
  second order G2N-1, Clavicle, FMIn, Zorro, Usnea, Phantom, Rattle (+ Scapula, Cleaver); third
  order Fdg, Bract 1/2, Billiards, Dandelion, Fuchs, Quasimodo, Specter, Sternum, Fudog; premotor
  Roundup, Rounddown, Roundtree, **Buster**. Skip connections from G2N-1, Zorro and FMIn straight
  to premotor. Hunger acts at exactly two nodes: the GRNs themselves and two second-order cells;
  the downstream layers are not hunger-modulated. **(M, with the per-neuron layer assignment at
  about 90 % confidence per my source.)**
- **Serotonergic branch**: Yao & Scott (2022), *Neuron* 110:1036-1050.e7,
  doi:10.1016/j.neuron.2021.12.028. SEL = the **lateral subesophageal 5-HT cluster**. Sugar-SELs
  are activated by proboscis sugar and *suppress* feeding via insulin; bitter-SELs drive crop
  contractions. A parallel endocrine limb, not the PER motor limb. **(M)**

### 3.3 All of these are in our table, under `synonyms`

Exact, from `data/body-annotations-male-cns-v1.0-minconf-0.5.feather` (ours). Grep `synonyms`,
**not** `type`: `Fdg` matches no type, and `IN1` prefix-matches 4,522 unrelated VNC interneurons.

| published name | MaleCNS `type` | n | note (ours) |
|---|---|---|---|
| Fdg | **GNG588** | 2 | |
| G2N-1 | **GNG232** | 2 | 566 / 511 synapses from labellar sugar (33-36 % of input) |
| Roundup | **GNG108** | 2 | **381 synapses onto MN9** |
| Roundtree | **GNG120** | 2 | **443 onto MN9** |
| Rounddown | **DNge080** | 2 | **219 onto MN9** |
| Phantom | GNG229 | 2 | 633 / 552 from labellar sugar (38-40 %) |
| Zorro | GNG215 | 2 | 541 / 441 (29 %) |
| Usnea | GNG175 | 2 | 887 / 725 (37 %) |
| Quasimodo | GNG042 | 2 | 1,003 / 914 (25 %) |
| Specter / Billiards | GNG038 | 1 + 1 | 1,271 / 1,076 (34-35 %) |
| Clavicle | ANXXX462a | 2 | 878 / 752 (35 %) |
| Dandelion | **AN13B002** | 2 | **GABAergic**; 12,547 synapses from the leg set; see §3.5 |
| Fudog | DNg67 | 2 | 447 (33 %) |
| FMIn | GNG197 | 2 | |
| Fuchs | GNG230 | 2 | |
| Rattle | GNG132 | 2 | also the top taste-peg target |
| Scapula | GNG087 | 3 | **777 synapses from the ascending leg GRNs** |
| Sternum | GNG585 | 3 | |
| Cleaver | GNG528 | 1 | |
| Bract 1 / Bract 2 | DNge174 / DNge173 | 2 / 2 | |
| Sugar-SEL PN | GNG540, GNG550 | 2 + 2 | |
| Sugar-SEL LN | GNG056 | 2 | |
| Bitter-SEL | DNg28 | 4 | |

MN9's own top inputs (ours; 6,991 synapses onto the pair): DNge062 556, GNG015 478,
**GNG120 [Roundtree] 443**, GNG095 436, GNG117 413, GNG130 409, **GNG108 [Roundup] 381**,
GNG234 362, GNG180 288, GNG184 275, DNge051 231, **DNge080 [Rounddown] 219**. The published
"round-" premotor family is exactly where it should be, one synapse from MN9. **(ours)**

### 3.4 Halting on sugar

**Sapkal, Mancini, Kumar, Spiller, Murakami, Vitelli, Bargeron, Maier, Eichler, Jefferis, Shiu,
Sterne & Bidaye (2024). "Neural circuit mechanisms underlying context-specific halting in
*Drosophila*." *Nature* 634(8032):191-200. doi:10.1038/s41586-024-07854-7.** Two mechanisms:

- **walk-OFF, the feeding-context one**: **Foxglove (FG)** and **Bluebell (BB)**, GABAergic SEZ
  neurons with short descending processes reaching only the anterior tip of the nerve cord. FG
  inhibits oDN1 and BDN2 and halts the forward component; BB inhibits the P9 downstream DN
  population (oDN1, DNa01, DNa02) and hits turning.
- **brake, the grooming-context one**: **BRK**, six ascending cholinergic neurons, one soma per
  leg neuromere, which override all walking commands including MDN backward walking and raise leg
  joint resistance.

The sugar link is direct and tested: FG and BB are connected to **Fdg**; Gr5a>CsChrimson
activation with GCaMP7b recruits **FG strongly** (more so in starved flies) and BB weakly; and in
a two-choice arena with a 2 M sucrose-soaked floor, **FG-silenced flies fail to stay on the sugar
side**. The paper states the halting pathway diverges from the proboscis-extension pathway
downstream of the shared sugar input. **(M)**

Caveat, and it is ours to carry: a fly on soaked filter paper is tasting with its tarsi, so this
is functionally tarsal-sugar-drives-halting, but the paper never says tarsal, and Gr5a labels both
labellar and leg sweet GRNs (and per Thoma 2016, Gr5a in the leg preferentially marks the
*segmental* class). **How tarsal sugar reaches Foxglove is not established.** **(M/?)**

**DNg105 is not a published halting neuron.** It exists (2 cells in FlyWire and in our table;
`xl` subclass in the Namiki et al. 2018 DN nomenclature, *eLife* 7:e34272), but I found no paper
characterising it, and it is not one of Sapkal's. In our table it has ~15,000 input synapses per
cell dominated by CL259, GNG113, GNG574, GNG299, CL311 and **pIP1** - a courtship-flavoured input
profile - and it receives **zero synapses from the entire 719-cell leg set** and 194 two-hop
synapses from the labellar sugar set (ours). Note also a discrepancy: FlyWire predicts DNg105
cholinergic, our MaleCNS table predicts **GABA**. Our use of DNg105 as "the halt" is a modelling
choice with no published identification behind it, and §P is right to list it. **(ours + (I))**

Behavioural background, all confirmed: peripheral sugar GRN activation alone stops the fly and
triggers idiothetic local search - **Corfas, Sharma & Dickinson (2019), *Current Biology*
29:1660-1668.e4**, doi:10.1016/j.cub.2019.03.004 (not *J. Exp. Biol.*); the path integrator is
re-zeroed at the patch centre - Behbahani, Palmer, Corfas & Dickinson (2021), *Current Biology*
31:4534-4546.e5, doi:10.1016/j.cub.2021.08.006; and the second-order dissociation between feeding
and locomotor suppression - **Jacobs, Wang, Nguyen et al. (2024), *Cell Reports* 43:114782**,
doi:10.1016/j.celrep.2024.114782, which finds that **Rattle, FMIn, G2N-1, Zorro** (second order)
and **Fdg** (third order) drive **locomotor suppression**, while essentially all tested types drive
PER. All five of those are in our table (GNG132, GNG197, GNG232, GNG215, GNG588). **(M/ours)**

### 3.5 Where the leg GRNs we drive actually go

Top postsynaptic partners of the 719-cell set, by total synapses (ours):

| target | synapses from the set | share of its input | what it is |
|---|---|---|---|
| LgLG1a / LgLG1b | 21,667 / 14,853 | - | axo-axonic among the pheromone GRNs |
| AN05B102a | 13,483 | 34.5 % | ascending, VNC |
| IN05B011a | 13,368 | 35.6 % | VNC interneuron |
| **AN13B002 [Dandelion]** | **12,547** | **31.9 %** | ascending, **GABAergic**, a Shiu 2022 named cell |
| IN05B002 | 11,123 | - | |
| AN05B023b | 7,971 | 46.0 % | |
| DNge153 | 4,212 | 41.0 % | descending; almost all LgLG3 |
| DNpe029 | 3,564 | 52.6 % | descending; mostly LgLG3 |
| AN04A001 | 1,459 | 4.9 % | the cell that moved at 19:02 |

Dandelion takes 12,547 synapses from the leg set (8,770 from LgLG3) **and** 489 from the labellar
sugar set, so it is a genuine leg/labellar convergence point. It is GABAergic, and its outputs are
entirely within the VNC (AN09B004, ANXXX027, AN17A015, IN23B*, IN13A004). **(ours)** That is
exactly the shape Thoma 2016 predicts for the segmental class: leg taste inhibiting the cord,
not extending the proboscis.

And the ascending class we never drove (`LgAG*`, 76 cells, 207,826 out-synapses) goes somewhere
quite different (ours): AN05B023a 3,902, **GNG016 3,364**, **GNG195 2,227**, AN27X021 1,943,
ANXXX470 1,850, AN09B033 1,452, **GNG087 [Scapula] 777**, DNg103 635, DNpe007 592. Per cell, the
top targets cross our 7 mV threshold at **3.7-9.7 Hz** (§4.5). Two hops from `LgAG*` reaches
GNG014 (951 synapses), MN12D (315), MN11D (288), **DNg105 (146)** and MN9 (15).

---

## 4. Convergence: the arithmetic

### 4.1 What the 719-cell set actually delivers

Direct synapses onto the four relays and MN9, by presynaptic type - the whole crosstab (ours):

| presynaptic | GNG014 | GNG125 | GNG271 | GNG391 | MN9 |
|---|---|---|---|---|---|
| claw_tpGRN (50 labellar taste-peg cells) | 134 | 30 | 6 | 42 | 0 |
| LgLG1a..LgLG8 (669 leg-bristle cells) | **0** | **0** | **0** | **0** | **0** |
| total | 134 | 30 | 6 | 42 | **0** |

Per postsynaptic cell (ours):

| cell | bodyId | total input synapses | from the set | from n presyn cells | fraction |
|---|---|---|---|---|---|
| GNG014 | 10864 | 9,295 | 71 | 29 | 0.76 % |
| GNG014 | 555296 | 9,641 | 63 | 20 | 0.65 % |
| GNG125 | 12258 | 3,947 | 8 | 3 | 0.20 % |
| GNG125 | 16048 | 4,427 | 22 | 8 | 0.50 % |
| GNG271 | 30373 / 32404 / 518776 | 804 / 725 / 646 | 0 / 6 / 0 | 0 / 4 / 0 | 0 / 0.83 / 0 % |
| GNG391 | 13709 / 15855 / 16374 / 18087 | 2,363 / 2,710 / 2,485 / 2,047 | 4 / 28 / 6 / 4 | 4 / 9 / 3 / 4 | 0.17-1.03 % |
| MN9 | 10331 / 16949 | 6,358 / 633 | **0 / 0** | 0 | **0 %** |
| MN11D (3 cells) | | 24,609 | 0 | 0 | 0 % |
| MN12D (4 cells) | | 12,686 | 0 | 0 | 0 % |
| DNg105 (2 cells) | | 30,711 | 0 | 0 | 0 % |
| AN04A001 (6 cells) | | 30,095 | 1,459 | 125 | 4.85 % |
| AN08B032 (2 cells) | | 4,663 | 166 | 82 | 3.56 % |

AN04A001's six cells individually: **336, 169, 175, 221, 281, 277** synapses from the set.

### 4.2 How many synapses are needed

Our engine (`world/fastlif.py` on `ref/flybrain/scripts/flysim.py`): `v_thresh = 7.0` mV above
rest, `tau_m = 20` ms, `tau_syn = 5` ms, `refractory = 2.2` ms, `dt = 1` ms, membrane noise
0.15 mV per step, `w = 0.185` mV per synapse for the male.

**Sustained drive.** `g` decays with `tau_syn` and `v` settles to `g`, so a presynaptic population
firing at `f` Hz through `n` synapses gives

```
v_ss = n * w * (f / 1000) * tau_syn            [mV]
```

Setting `v_ss = 7 mV`:

```
n * f = 7 / (0.185 * 5 / 1000) = 7,568  synapses x Hz     (w = 0.185)
n * f = 7 / (0.275 * 5 / 1000) = 5,091  synapses x Hz     (w = 0.275)
```

**Single coincident volley.** For one isolated volley of `n` synapses, the response peaks at
`t* = ln(tau_m/tau_syn) / (1/tau_syn - 1/tau_m) = 9.24` ms, with peak fraction
`|A| * (e^(-t*/tau_m) - e^(-t*/tau_syn)) = 0.1575`, where `A = tau_syn/(tau_syn - tau_m) = -1/3`.
So one volley needs

```
n = 7 / (0.1575 * 0.185) = 240 coincident synapses      (162 at 0.275 mV)
```

The naive "7 / 0.185 = 38 synapses" is wrong by 6.3x: only about 16 % of an injected conductance
ever appears as depolarisation at these time constants.

### 4.3 Does our 24 Hz on 719 cells supply it?

`v_ss` at 24 Hz, per cell, `w = 0.185`, threshold 7 mV (ours):

| cell | synapses from the set | v_ss at 24 Hz | % of threshold | rate needed for 7 mV |
|---|---|---|---|---|
| AN04A001, best cell | 336 | **7.46 mV** | **107 %** | 23 Hz |
| AN04A001, median | ~250 | 5.6 mV | 80 % | 30 Hz |
| AN04A001, weakest | 169 | 3.75 mV | 54 % | 45 Hz |
| AN08B032, best | 94 | 2.09 mV | 30 % | 81 Hz |
| GNG014, best | 71 | 1.58 mV | 23 % | 107 Hz |
| GNG391, best | 28 | 0.62 mV | 9 % | 270 Hz |
| GNG125, best | 22 | 0.49 mV | 7 % | 344 Hz |
| GNG271, best | 6 | 0.13 mV | 2 % | 1,261 Hz |
| **MN9, MN11D, MN12D, DNg105** | **0** | **0.00 mV** | **0 %** | **never** |

**That is the whole 19:02 result in one table.** AN04A001's best-connected cell sits at 107 % of
threshold on leg-GRN input alone, which is exactly why it is the one cell that doubled. Everything
else is at 0-30 %, and MN9, the pump and DNg105 are at *identically zero* because there is no
synapse to drive them through.

Two hops does not rescue it. Restricting to the 1,498 intermediates that receive at least 20
synapses from the set, the two-hop total onto {MN9, GNG014, GNG125, GNG271, GNG391, DNg105} is
4,254 synapses, of which **MN9 gets 33** (ours).

At `w = 0.275` the picture improves for AN04A001 (11.1 mV, suprathreshold on 4 of 6 cells) and
changes **not at all** for MN9, MN11D, MN12D and DNg105, which are zero for any `w`.

> **The "0.185 mV wall at the second synapse" is the right description for AN08B032 and for the
> gnathal relays fed by the taste pegs. It is the wrong description for MN9 and DNg105: those are
> not blocked by the constant, they are not connected to the cells we drove.**

### 4.4 What the labellar sugar set would deliver

`v_ss` at 24 Hz, `w = 0.185`, monosynaptic targets of the 91-cell labellar sugar set (ours):

| target | synapses from LB sugar | share of its input | v_ss at 24 Hz | crosses 7 mV at |
|---|---|---|---|---|
| GNG038 [Specter] | 1,271 | 35.3 % | 28.2 mV | **6.0 Hz** |
| GNG038 [Billiards] | 1,076 | 34.1 % | 23.9 mV | 7.0 Hz |
| GNG042 [Quasimodo] | 1,003 / 914 | 25 % | 22.3 / 20.3 mV | 7.5 / 8.3 Hz |
| GNG175 [Usnea] | 887 / 725 | 37 % | 19.7 / 16.1 mV | 8.5 / 10.4 Hz |
| ANXXX462a [Clavicle] | 878 / 752 | 35 % | 19.5 / 16.7 mV | 8.6 / 10.1 Hz |
| GNG229 [Phantom] | 633 / 552 | 39 % | 14.1 / 12.3 mV | 12.0 / 13.7 Hz |
| GNG232 [G2N-1] | 566 / 511 | 33 % | 12.6 / 11.3 mV | 13.4 / 14.8 Hz |
| GNG215 [Zorro] | 541 / 441 | 29 % | 12.0 / 9.8 mV | 14.0 / 17.2 Hz |
| DNg67 [Fudog] | 447 | 33 % | 9.9 mV | 16.9 Hz |
| AN13B002 [Dandelion] | 489 | 2.5 % | 10.9 mV | 15.5 Hz |

Direct labellar-sugar synapses onto MN9 and the relays: **0**. Two-hop: **13,808** synapses, of
which GNG014 3,447, MN11D 3,388, MN7 2,228, MN12D 1,429, **MN9 552**, GNG125 698, GNG391 619,
GNG271 313, DNg105 194 (ours). That is **17x** the leg set's two-hop total and **17x** its MN9
count.

### 4.5 What the ascending leg set would deliver

`v_ss` at 24 Hz, `w = 0.185`, monosynaptic targets of the 76-cell `LgAG*` set (ours):

| target | synapses | share of its input | v_ss at 24 Hz | crosses 7 mV at |
|---|---|---|---|---|
| AN05B023a | 2,037 / 1,865 | 31 / 25 % | 45.2 / 41.4 mV | **3.7 / 4.1 Hz** |
| GNG016 | 1,894 / 1,470 | 21 / 17 % | 42.1 / 32.6 mV | 4.0 / 5.1 Hz |
| GNG195 | 1,117 / 1,110 | 52 / 51 % | 24.8 / 24.6 mV | 6.8 Hz |
| AN27X021 | 1,021 / 922 | 30 / 27 % | 22.7 / 20.5 mV | 7.4 / 8.2 Hz |
| ANXXX470 | 964 / 886 | 51 / 47 % | 21.4 / 19.7 mV | 7.9 / 8.5 Hz |
| AN09B033 | 783 | 41 % | 17.4 mV | 9.7 Hz |

Two-hop onto the proboscis set: GNG014 951, MN12D 315, MN11D 288, **DNg105 146**, GNG391 99,
GNG271 63, GNG125 37, MN9 15, MN6 10, MN8 10 (ours).

### 4.6 What the labelled sugar subsets would deliver

The sets from §2.4, `v_ss` at 24 Hz, `w = 0.185` (ours):

| set | n | top monosynaptic targets (synapses, % of input, v_ss, crossing rate) |
|---|---|---|
| **LB3c** (labellar sugar, Gr64f) | 23 | GNG038 [Specter] 641, 17.8 %, 14.2 mV, **11.8 Hz**; GNG038 [Billiards] 508, 11.3 mV, 14.9 Hz; GNG042 [Quasimodo] 455/435, ~10 mV, 17 Hz; GNG215 [Zorro] 396/370, ~8.5 mV, 19-21 Hz; GNG175 [Usnea] 286, 6.4 mV; GNG132 [Rattle] 281; GNG232 [G2N-1] 280 |
| **LB3b+LB3c** (sugar + appetitive low salt) | 34 | GNG038 [Specter] 772, 17.1 mV, **9.8 Hz**; Billiards 628; Quasimodo 477/459; Clavicle 396/388; Zorro 398/373; Usnea 363 |
| **LgAG2** (ascending tarsal, Gr61a) | 11 | AN27X021 871/781, 26/23 %, 19.3/17.3 mV, **8.7/9.7 Hz**; DNg103 250/228, 5.6/5.1 mV; GNG266 220, 39 %, 4.9 mV |
| **LgLG4** (local tarsal sugar, Gr64f+Ir56b) | 43 | DNg103 319, 8 %, 7.08 mV, **23.7 Hz**; AN05B106 310/236/234, 16-21 %, 5.2-6.9 mV; AN01B004 255/180/176; AN13B002 [Dandelion] 201 |
| **LgAG1** (ascending tarsal bitter, Gr33a) | 25 | AN05B023a 1760/1630, 27/22 %, 39.1/36.2 mV, **4.3/4.6 Hz** (GABAergic); ANXXX470 955/873, 50 %, 21.2/19.4 mV |

Two-hop reach onto {MN9, MN6, MN8, MN1, MN11D, MN12D, MNx01, GNG014/125/271/391, DNg105,
AN04A001}, total synapses (ours):

| set | two-hop total | MN9 | MN11D | MN12D | GNG014 | DNg105 | AN04A001 |
|---|---|---|---|---|---|---|---|
| LB3c (23 cells) | **9,320** | **313** | 3,294 | 1,254 | 2,400 | 149 | - |
| LB3b+LB3c (34) | 10,000 | 326 | 3,295 | 1,279 | 2,713 | 178 | - |
| all 91 labellar sugar/water | 13,808 | 552 | 3,388 | 1,429 | 3,447 | 194 | - |
| LgAG2 (11) | 484 | 1 | 166 | 117 | 15 | 1 | 55 |
| LgLG4 (43) | 924 | 5 | 0 | 0 | 6 | 24 | **881** |
| LgLG4 + LgAG2 (54) | 1,348 | 5 | 166 | 117 | 17 | 24 | 883 |
| 719-cell set we drive now | 4,254 | 33 | 0 | 0 | 2,144 | 344 | - |

Read that table slowly. **The labelled tarsal sugar set, 54 cells, reaches MN9 with 5 two-hop
synapses. The labellar sugar set, 23 cells, reaches it with 313.** Tarsal sugar in this connectome
does not go to the proboscis in two hops by any route; what it does is drive AN04A001 (881 of
LgLG4's 924 two-hop synapses land there), which is a VNC-output ascending neuron. That is
consistent with Tastekin's seven-hop figure and with Thoma's functional split, and it means a
two-synapse failure in our runs is **the expected anatomy**, not a broken constant.

**Prediction, stated before the run.** At 0.185 mV the labellar sugar set (LB3c) carries through
its first synapse at 12 Hz and has 313 two-hop synapses onto MN9, so if MN9 stays at 0 with LB3c
held at 50-100 Hz, the wall is real and general. The tarsal sets carry through their first
synapse too (LgAG2 at 9 Hz, LgLG4 at 24 Hz) but have almost nothing pointed at the proboscis, so
a null there says nothing about the constant. **(I)**

### 4.7 Signs

Predicted transmitters (ours, `data/body-neurotransmitters-male-cns-v1.0.feather`): acetylcholine
for LgLG1a/2/3/4, **LgAG1-LgAG7**, claw_tpGRN, LB3c/LB3d, AN04A001, AN08B032, GNG014, GNG271,
GNG232, GNG108, GNG120, GNG588, DNge080 and MN9; **glutamate for LgAG8 and LgAG9**; **GABA for
GNG125, GNG391, DNg105 and AN13B002 [Dandelion]**; "unclear" for LgLG1b and LB2d. The `v_ss`
figures above are magnitudes: two of the four gnathal relays are inhibitory, Dandelion is
inhibitory, and for those "carrying" means suppressing. Shiu et al.'s own robustness test found
that flipping glutamate to excitatory destroyed their aversive-taste result and raised their false
positive rate from 1 % to 16 %, so the sign of LgAG8/LgAG9 matters. **(ours + M)**

---

## 5. Recommended experiments

One change per run, each with its control, in order.

1. **Split the drive set. (No new physics; one confirming run.)** In `world/pair.py:127`, replace
   the single `LEG_GRN` with three: `LEG_GRN_SEG` (669 `LgLG*`, `vnc_sensory`),
   `LEG_GRN_ASC` (76 `LgAG*`, `sensory_ascending`), `TASTE_PEG` (50 `claw_tpGRN`, which is
   labellar). Control: rerun the 19:02 held-taste pair with the three logged separately. Decides:
   whether the 0.1 Hz twitch on MN9 and everything at the gnathal relays was a *labellar* signal
   we had labelled tarsal, and confirms that the ascending class was never driven.

2. **Drive the labelled sugar GRNs instead of all 719, held, standing, at 26 Hz.** Three arms,
   one control (nothing held), all else identical:
   **(a)** `LB3c`, 23 cells, the labellar Gr64f sugar GRNs;
   **(b)** `LgLG4` + `LgAG2`, 54 cells, the tarsal appetitive set;
   **(c)** the present 719-cell set, as the reference arm.
   Log: GNG038 [Specter/Billiards], GNG042 [Quasimodo], GNG215 [Zorro], GNG175 [Usnea],
   GNG232 [G2N-1], GNG132 [Rattle], ANXXX462a [Clavicle]; then GNG108 [Roundup],
   GNG120 [Roundtree], DNge080 [Rounddown], GNG588 [Fdg]; then MN9, MN6, MN8, MN11D, MN12D,
   MNx01, DNg105; plus AN27X021, DNg103, AN05B106, AN13B002 [Dandelion], AN04A001 for the tarsal
   arm. **This is the "sugar subset" item in the queue, and the label now exists (§2.4).**
   §4.6 says arm (a) must carry through its first synapse at 12 Hz and arm (b) at 9-24 Hz; if
   they do not, the engine or the drive is wrong, not the connectome.

3. **A dose-response on arm (a): {10, 25, 50, 75, 100, 150, 200} Hz, MN9 as the readout.**
   Control: 0 Hz. Two reasons this is the real replication of Shiu et al. Figure 1D. First,
   **his MN9 threshold is 30 Hz of GRN drive and our 24 Hz is below it**, so every held-taste run
   so far has been under-driven by his own calibration. Second, he set `w_syn = 0.275` precisely
   so that 100 Hz sugar gives ~80 % of maximal MN9; the same sweep at 0.185 tells us in one curve
   how much of the male recalibration the taste path can absorb. Report MN9 Hz versus GRN Hz
   against his table in §1.3.

4. **0.275 mV as a single-variable test (`--wsyn-m 0.275`) on arm (a).** NOT a default change.
   §4.3 and §4.6 say it cannot rescue MN9 from any tarsal set (5 two-hop synapses), so run it
   where there is something for it to act on. Shiu's own robustness sweep found -30 % on `w_syn`
   is where his water result broke, which is about where our 0.185 sits relative to his 0.275.

6. **Read MN9 as "feeding", instead of imposing it.** Add a readout `feeding = MN9 over
   threshold` (optionally with MN6/MN8 for the labellar steps and MNx01 for the pump), logged in
   every run, driving nothing yet. Control: the existing `FeedingState` latch left on, so
   imposed-versus-read can be compared frame by frame in the same run. This is the item that
   retires the latch in §P, and a readout that never fires is still a correct readout.

7. **Halting, as a separate question from PER.** Log `GNG132 [Rattle]`, `GNG197 [FMIn]`,
   `GNG232 [G2N-1]`, `GNG215 [Zorro]` and `GNG588 [Fdg]` in every arm of 2, with the walking
   command on and no latch, and watch pace. Jacobs et al. 2024 found exactly those five drive
   locomotor suppression while nearly everything drives PER, and Sapkal et al. 2024 put Foxglove
   downstream of Fdg. If pace drops, the halt we have been imposing through DNg105 is in his own
   wiring, through different cells than we guessed. Worth adding `AN05B023a` (GABAergic, the
   ascending bitter target) and `DNg103` to the log while we are there.

(If only three fit: 1, 2, 6.)

**A note on rates for whoever runs these.** The current `Hold(26.0)` on all 719 cells was sourced
as "65 Hz at 100 mM sugar times ~40 % of tarsal GRNs being sugar-tuned" - a fudge that existed
*because* we were driving every leg GRN at once. With a labelled subset that fudge should go: the
sugar GRNs themselves should carry the full physiological rate. Dahanukar et al. 2007 and Inagaki
et al. 2012, cited by Shiu et al. for exactly this, put ~100 Hz at the top of the physiological
range. So arms 2-4 should run at 50-100 Hz on the labelled subset, not 26 Hz on everything.

---

## 6. What is established, what is inferred, what could not be found

### Established

- Shiu et al. 2024 activated **21 labellar sugar GRNs of one hemisphere** (biologically left; the
  code says "R" because FAFB is left-right inverted), at 10-200 Hz Poisson, 1 s trials, 30 trials,
  reading **MN9**. Companion sets: bitter 21, Ir94e 18, water 18. No tarsal GRN was activated.
- **MN9 first fires at 30 Hz of sugar GRN drive** (0.33 Hz), reaches 65.70 Hz at 100 Hz drive and
  93.23 Hz at 200 Hz (their Supp Table 1A). They also report MN6, MN8 and MN11 activated; MN12 is
  not mentioned in the paper.
- Their constants, from the paper: -52 mV rest and reset, -45 mV threshold (7 mV span),
  R = 10 kOhm cm^2 and C = 2 uF cm^-2 (so tau_m = 20 ms, derived), tau_syn = 5 ms, refractory
  2.2 ms, delay 1.8 ms, **W_syn = 0.275 mV, "the single free parameter"**. `f_poi = 250` is code
  only. W_syn was chosen so that 100 Hz sugar gives ~80 % of maximal MN9 firing.
- Their accuracy: 150/164 = **91 %** overall, 49/58 = **84 %** excluding the split-GAL4 screen;
  the weakest category, "required for sugar feeding initiation", is **6/10**.
- The GRN modality assignment traces to **Engert et al. 2022, *eLife* 11:e78110** (87 right and 57
  left labellar axons in FAFB, six groups, no LB names, no taste pegs, no leg GRNs). The `LB*`
  strings and the `cell_sub_class` values in FlyWire come from the supplementary annotation table
  of **Schlegel et al. 2024, *Nature* 634:139-152**.
- FlyWire v783 has modality labels for **labellar** GRNs only: `sugar/water` (129), `bitter` (65),
  `low-salt` (19). Sugar and water are not separated. The 74 leg-derived ascending gustatory axons
  (`SA_VTV_*`) and the taste pegs carry no modality.
- **Tastekin et al. (2026), *Cell* 189:5527-5551.e5, assigns molecular identity to the MaleCNS GRN
  types, tarsal ones included.** `LgLG4` (43, SNch11) = Gr64f + Ir56b, the tarsal sugar GRN;
  `LgAG2` (11) = Gr61a, ascending appetitive; `LgAG1` (25) = Gr33a, ascending bitter; `LB3a` =
  ppk28 water, `LB3b` = Ir56b low salt, `LB3c` = Gr64f sugar, `LB3d` = aversive; `LB1a-d` bitter,
  `LB1e` Ir94e. `LgLG3` (162) has no assigned identity. Those names are already in our `type`
  column, so the selection needs no join.
- Our `receptorType` column has exactly three values across the whole male CNS
  (`putative_ppk23`/`putative_ppk25`/`putative_IR52b`, 752 cells), none of them a food taste; all
  three are pheromone channels in the published literature, and the ppk23/ppk25 split encodes
  ppk25- versus ppk25+ since all six types are ppk23+.
- Two independent checks that we are reading the same table Tastekin et al. annotated: PPN1 =
  `AN05B102a` receives 8,017 LgLG1a and 5,354 LgLG1b synapses (their ppk23/ppk25 target), and
  `AN13B002 [Dandelion]` receives 8,770 of its 12,547 leg-GRN synapses from LgLG3 (their
  "Dandelion-connected" class) (ours).
- **The labelled tarsal sugar set reaches MN9 with 5 two-hop synapses; the labellar sugar set
  LB3c reaches it with 313** (ours). Tastekin et al. independently report that LgLG4 needs about
  seven hops to reach maximum effective connectivity onto the feeding motor neurons.
- **The male CNS has 76 `LgAG*` cells: `class = gustatory`, `subclass = leg bristle`,
  `superclass = sensory_ascending`, `mancType` SAch01/SAch02. They are not in our drive set.**
- **The 669 `LgLG*` cells make zero synapses on GNG014, GNG125, GNG271, GNG391, MN9, MN11D, MN12D
  and DNg105.** All 212 direct synapses from our 719-cell set onto the four relays come from the
  50 labellar taste-peg cells.
- AN04A001's best-connected cell receives 336 leg-GRN synapses, giving 7.46 mV against a 7 mV
  threshold at 24 Hz and 0.185 mV: 107 %. The measured doubling, explained.
- **Thoma et al. 2016** split leg sweet GRNs into ascending (feeding initiation) and segmental
  (locomotion suppression) classes.
- **Sapkal et al. 2024** identify Foxglove and Bluebell as the sugar-context halting neurons,
  connected to Fdg; **DNg105 is not among them and has no published function.**
- **Schwarz et al. 2017**: MN9 rostrum protraction, MN2 haustellum, MN6 labellar extension, MN8
  labellar spreading, MN1 retraction, MN5/10/11/12 pharyngeal pump.
- All 22 Shiu 2022 named cells and the Yao & Scott SEL cells are in our table under `synonyms`
  (§3.3). Roundup = GNG108, Roundtree = GNG120 and Rounddown = DNge080 are among MN9's top inputs.

### Inferred (mine)

- **Thoma's stGRN maps to `LgLG4` and his atGRN to `LgAG2`.** The ascending/local split is stated
  by both Thoma 2016 and Tastekin 2026; pinning the sweet subtype to each side is my join of the
  two, not a sentence in either paper.
- **DNg105 as the halt is a modelling choice**, not an identification. It is also a transmitter
  discrepancy: FlyWire predicts cholinergic, our MaleCNS table predicts GABA.
- All threshold-crossing rates in §4.3-§4.6 are arithmetic from the steady-state formula, not
  measurements.
- The reading that MaleCNS's `receptorType` stops at the pheromone channels *because* those are
  the ones with a morphological signature.
- That a two-synapse read of our table understates the tarsal path, given Tastekin's seven-hop
  figure. We have not computed effective connectivity at depth.

### Could not find

- Independent confirmation of `putative_IR52b`. Koh et al. 2014 detected **no** expression from an
  Ir52b-GAL4 driver; the established male foreleg receptors are IR52c and IR52d. Treat LgLG2's
  receptor label as the weakest link in the chain.
- Any molecular identity for **LgLG3** (162 cells), the largest leg gustatory class and the one
  doing most of the work in our runs.
- Any traced tarsal-GRN -> named ascending neuron -> named SEZ cell -> MN9 chain with functional
  evidence at every step. Tastekin et al. give the anatomy; nobody has closed the loop
  physiologically.
- How tarsal sugar reaches Foxglove. Sapkal et al. used a pan-sweet Gr5a driver and a floor assay,
  with no leg-specific manipulation, and per Thoma 2016 leg Gr5a preferentially marks the
  *segmental* class.
- **TPN1** (Kim, Kirkhart & Scott 2017) as a type in our table. `TPN` matches only `tpn MN`.
  Worth a morphology-based hunt among the `LgAG*` targets: TPN1's soma is in the metathoracic
  neuromere and its axon terminates in the SEZ.
- The exact MN9 rates are now in hand (§1.3), but the per-cell CSVs behind Shiu et al.'s Fig 1E/1F
  silencing screen are only in the archive at doi:10.17617/3.CZODIW, not in `ref/`.
- The provenance, in Shiu's code or README, of the specific 21 sugar GRN root IDs (their Methods
  describe the procedure; the IDs are not annotated in the notebook).
- Any documentation of `receptorType` on Janelia's MaleCNS site. The column is in the data file
  but not in the docs; cite Tastekin et al. 2026 for the assignments and the v1.0 release for the
  carrier.

---

## 7. References

Azevedo, A. et al. (2024). Connectomic reconstruction of a female Drosophila ventral nerve cord.
*Nature* 631:360-368. doi:10.1038/s41586-024-07389-x

Berg, S., Beckett, I. R., Costa, M., Schlegel, P., Januszewski, M., Marin, E. C., Nern, A.,
Preibisch, S., Qiu, W., Takemura, S. et al. (2026). Sexual dimorphism in the complete Drosophila
male central nervous system connectome. *Cell* 189(18):5504-5526.e15.
doi:10.1016/j.cell.2026.08.015. Preprint bioRxiv 2025.10.09.680999. Dataset: MaleCNS v1.0,
male-cns.janelia.org

Behbahani, A. H., Palmer, E. H., Corfas, R. A., Dickinson, M. H. (2021). Drosophila re-zero their
path integrator at the center of a fictive food patch. *Current Biology* 31:4534-4546.e5.
doi:10.1016/j.cub.2021.08.006

Bidaye, S. S., Laturney, M., Chang, A. K., Liu, Y., Bockemühl, T., Büschges, A., Scott, K. (2020).
Two brain pathways initiate distinct forward walking programs in Drosophila. *Neuron*
108:469-485.e8. doi:10.1016/j.neuron.2020.07.032

Bidaye, S. S., Machacek, C., Wu, Y., Dickson, B. J. (2014). Neuronal control of Drosophila walking
direction. *Science* 344:97-101. doi:10.1126/science.1249964

Chen, C.-L. et al. (2023). Ascending neurons convey behavioral state to integrative sensory and
action selection brain regions. *Nature Neuroscience* 26:682-695. doi:10.1038/s41593-023-01281-z

Cheong, H. S. J., Eichler, K., Stürner, T. et al. (2024). Transforming descending input into
behavior: the organization of premotor circuits in the Drosophila male adult nerve cord
connectome. *eLife* 13:RP96084. doi:10.7554/eLife.96084

Corfas, R. A., Sharma, T., Dickinson, M. H. (2019). Diverse food-sensing neurons trigger idiothetic
local search in Drosophila. *Current Biology* 29:1660-1668.e4. doi:10.1016/j.cub.2019.03.004

Dahanukar, A., Lei, Y.-T., Kwon, J. Y., Carlson, J. R. (2007). Two Gr genes underlie sugar
reception in Drosophila. *Neuron* 56:503-516. doi:10.1016/j.neuron.2007.10.024

Dorkenwald, S. et al. (2024). Neuronal wiring diagram of an adult brain. *Nature* 634:124-138.
doi:10.1038/s41586-024-07558-y

Eckstein, N. et al. (2024). Neurotransmitter classification from electron microscopy images at
synaptic sites in Drosophila melanogaster. *Cell* 187:2574-2594.e23. doi:10.1016/j.cell.2024.03.016

Engert, S., Sterne, G. R., Bock, D. D., Scott, K. (2022). Drosophila gustatory projections are
segregated by taste modality and connectivity. *eLife* 11:e78110. doi:10.7554/eLife.78110

Flood, T. F., Iguchi, S., Gorczyca, M., White, B., Ito, K., Yoshihara, M. (2013). A single pair of
interneurons commands the Drosophila feeding motor program. *Nature* 499:83-87.
doi:10.1038/nature12208

Gordon, M. D., Scott, K. (2009). Motor control in a Drosophila taste circuit. *Neuron* 61:373-384.
doi:10.1016/j.neuron.2008.12.033

Inagaki, H. K. et al. (2012). Visualizing neuromodulation in vivo: TANGO-mapping of dopamine
signaling reveals appetite control of sugar sensing. *Cell* 148:583-595.
doi:10.1016/j.cell.2011.12.022

Jacobs, R. V., Wang, C. X., Nguyen, L., Pruitt, T. J., Wang, P., Lozada-Perdomo, F. V., Deere,
J. U., Liphart, H. A., Devineni, A. V. (2024). Overlap and divergence of neural circuits mediating
distinct behavioral responses to sugar. *Cell Reports* 43:114782. doi:10.1016/j.celrep.2024.114782

Jaeger, A. H., Stanley, M., Weiss, Z. F., Musso, P.-Y., Chan, R. C. W., Zhang, H., Feldman-Kiss,
D., Gordon, M. D. (2018). A complex peripheral code for salt taste in Drosophila. *eLife*
7:e37167. doi:10.7554/eLife.37167

Kallman, B. R., Kim, H., Scott, K. (2015). Excitation and inhibition onto central courtship
neurons biases Drosophila mate choice. *eLife* 4:e11188. doi:10.7554/eLife.11188

Jürgensen, A.-M., Khalili, A., Chicca, E., Indiveri, G., Nawrot, M. P. (2021). A neuromorphic model
of olfactory processing and sparse coding in the Drosophila larva brain. *Neuromorphic Computing
and Engineering* 1:024008. doi:10.1088/2634-4386/ac3ba6

Kakaria, K. S., de Bivort, B. L. (2017). Ring attractor dynamics emerge from a spiking model of the
entire protocerebral bridge. *Frontiers in Behavioral Neuroscience* 11:8.
doi:10.3389/fnbeh.2017.00008

Kim, H., Kirkhart, C., Scott, K. (2017). Long-range projection neurons in the taste circuit of
Drosophila. *eLife* 6:e23386. doi:10.7554/eLife.23386

Koh, T.-W., He, Z., Gorur-Shandilya, S., Menuz, K., Larter, N. K., Stewart, S., Carlson, J. R.
(2014). The Drosophila IR20a clade of ionotropic receptors are candidate taste and pheromone
receptors. *Neuron* 83:850-865. doi:10.1016/j.neuron.2014.07.012

Ling, F., Dahanukar, A., Weiss, L. A., Kwon, J. Y., Carlson, J. R. (2014). The molecular and
cellular basis of taste coding in the legs of Drosophila. *Journal of Neuroscience*
34:7148-7164. doi:10.1523/JNEUROSCI.0649-14.2014

Lu, B., LaMora, A., Sun, Y., Welsh, M. J., Ben-Shahar, Y. (2012). ppk23-dependent chemosensory
functions contribute to courtship behavior in Drosophila melanogaster. *PLoS Genetics*
8:e1002587. doi:10.1371/journal.pgen.1002587

Luo, Y., Talross, G. J. S., Carlson, J. R. (2024). Function and evolution of Ir52 receptors in
mate detection in Drosophila. *Current Biology* 34:5395-5408.e6. doi:10.1016/j.cub.2024.10.001

Lazar, A. A., Liu, T., Turkcan, M. K., Zhou, Y. (2021). Accelerating with FlyBrainLab the discovery
of the functional logic of the Drosophila brain in the connectomic and synaptomic era. *eLife*
10:e62362. doi:10.7554/eLife.62362

Marin, E. C. et al. (2024). Systematic annotation of a complete adult male Drosophila nerve cord
connectome enables motor circuit analysis. *eLife* 13:RP97766. doi:10.7554/eLife.97766

McKellar, C. E. (2016). Motor control of fly feeding. *Journal of Neurogenetics* 30:101-111.
doi:10.1080/01677063.2016.1177047

McKellar, C. E., Siwanowicz, I., Dickson, B. J., Simpson, J. H. (2020). Controlling motor neurons
of every muscle for fly proboscis reaching. *eLife* 9:e54978. doi:10.7554/eLife.54978

Namiki, S., Dickinson, M. H., Wong, A. M., Korff, W., Card, G. M. (2018). The functional
organization of descending sensory-motor pathways in Drosophila. *eLife* 7:e34272.
doi:10.7554/eLife.34272

Paul, M. M. et al. (2015). Bruchpilot and Synaptotagmin collaborate to drive rapid glutamate
release and active zone differentiation. *Frontiers in Cellular Neuroscience* 9:29.
doi:10.3389/fncel.2015.00029

Sapkal, N., Mancini, N., Kumar, D. S., Spiller, N., Murakami, K., Vitelli, G., Bargeron, B.,
Maier, K., Eichler, K., Jefferis, G. S. X. E., Shiu, P. K., Sterne, G. R., Bidaye, S. S. (2024).
Neural circuit mechanisms underlying context-specific halting in Drosophila. *Nature*
634:191-200. doi:10.1038/s41586-024-07854-7

Scheffer, L. K. et al. (2020). A connectome and analysis of the adult Drosophila central brain.
*eLife* 9:e57443. doi:10.7554/eLife.57443

Schlegel, P. et al. (2024). Whole-brain annotation and multi-connectome cell typing of Drosophila.
*Nature* 634:139-152. doi:10.1038/s41586-024-07686-5

Schwarz, O., Bohra, A. A., Liu, X., Reichert, H., VijayRaghavan, K., Pielage, J. (2017). Motor
control of Drosophila feeding behavior. *eLife* 6:e19892. doi:10.7554/eLife.19892

Shiu, P. K., Sterne, G. R., Engert, S., Dickson, B. J., Scott, K. (2022). Taste quality and hunger
interactions in a feeding sensorimotor circuit. *eLife* 11:e79887. doi:10.7554/eLife.79887

Shiu, P. K., Sterne, G. R., Spiller, N. et al. (2024). A Drosophila computational brain model
reveals sensorimotor processing. *Nature* 634:210-219. doi:10.1038/s41586-024-07763-9.
Code: github.com/philshiu/Drosophila_brain_model. Data: doi:10.17617/3.CZODIW

Sterne, G. R., Otsuna, H., Dickson, B. J., Scott, K. (2021). Classification and genetic targeting
of cell types in the primary taste and premotor center of the adult Drosophila brain. *eLife*
10:e71679. doi:10.7554/eLife.71679

Stürner, T., Brooks, P., Serratosa Capdevila, L. et al. (2025). Comparative connectomics of the
descending and ascending neurons of the Drosophila nervous system. *Nature* 643:158-172.
doi:10.1038/s41586-025-08925-z

Starostina, E., Liu, T., Vijayan, V., Zheng, Z., Siwicki, K. K., Pikielny, C. W. (2012). A
Drosophila DEG/ENaC subunit functions specifically in gustatory neurons required for male
courtship behavior. *Journal of Neuroscience* 32:4665-4674.
doi:10.1523/JNEUROSCI.6178-11.2012

Takemura, S. et al. (2024). A connectome of the male Drosophila ventral nerve cord. *eLife*
13:RP97769. doi:10.7554/eLife.97769

Tastekin, I., de Haan Vicente, I., Beresford, R. J., Morris, B. J., Beckett, I., Schlegel, P.,
Gkantia, M., Marin, E. C., Costa, M., Jefferis, G. S. X. E., Ribeiro, C. (2026). The complete
gustatory connectome of adult Drosophila reveals how taste guides feeding, foraging, and social
behavior. *Cell* 189(18):5527-5551.e5. doi:10.1016/j.cell.2026.08.016. Preprint bioRxiv
2025.08.25.671814

Thistle, R., Cameron, P., Ghorayshi, A., Dennison, L., Scott, K. (2012). Contact chemoreceptors
mediate male-male repulsion and male-female attraction during Drosophila courtship. *Cell*
149:1140-1151. doi:10.1016/j.cell.2012.03.045

Thoma, V., Knapek, S., Arai, S., Hartl, M., Kohsaka, H., Sirigrivatanawong, P., Abe, A.,
Hashimoto, K., Tanimoto, H. (2016). Functional dissociation in sweet taste receptor neurons
between and within taste organs of Drosophila. *Nature Communications* 7:10678.
doi:10.1038/ncomms10678

Toda, H., Zhao, X., Dickson, B. J. (2012). The Drosophila female aphrodisiac pheromone activates
ppk23+ sensory neurons to elicit male courtship behavior. *Cell Reports* 1:599-607.
doi:10.1016/j.celrep.2012.05.007

Vijayan, V., Thistle, R., Liu, T., Starostina, E., Pikielny, C. W. (2014). Drosophila
pheromone-sensing neurons expressing the ppk25 ion channel subunit stimulate male courtship and
female receptivity. *PLoS Genetics* 10:e1004238. doi:10.1371/journal.pgen.1004238

Walker, S. R., Peña-Garcia, M., Devineni, A. V. (2025). Connectomic analysis of taste circuits in
Drosophila. *Scientific Reports* 15:5278. doi:10.1038/s41598-025-89088-9

Yao, Z., Scott, K. (2022). Serotonergic neurons translate taste detection into internal nutrient
regulation. *Neuron* 110:1036-1050.e7. doi:10.1016/j.neuron.2021.12.028

Yapici, N., Cohn, R., Schusterreiter, C., Ruta, V., Vosshall, L. B. (2016). A taste circuit that
regulates ingestion by integrating food and hunger signals. *Cell* 165:715-729.
doi:10.1016/j.cell.2016.02.061

**Local sources used**: `ref/Drosophila_brain_model/{model.py, figures.ipynb, example.ipynb}` and
the paper's Supplementary Tables 1A, 2, 3, 10; `ref/flybrain/scripts/flysim.py` and
`world/fastlif.py` for our constants; `data/body-annotations-male-cns-v1.0-minconf-0.5.feather`;
`data/connectome-weights-male-cns-v1.0-minconf-0.5.feather`;
`data/body-neurotransmitters-male-cns-v1.0.feather`; `data/flywire/neuron_annotations.tsv`
(FlyWire v783).
