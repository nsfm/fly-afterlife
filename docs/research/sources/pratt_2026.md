# Pratt et al. 2026 — Proprioceptive limit detectors (Drosophila leg HAIR PLATES)

**Citation:** Pratt BG, Dallmann CJ, Chou GM, Siwanowicz I, Walling-Bell S, Cook A, Sustar A,
Azevedo A, Tuthill JC (2026). *Proprioceptive limit detectors contribute to sensorimotor control of
the Drosophila leg.* **Nature Communications 17:2664.** doi:10.1038/s41467-026-69333-z
Received 2025-07-25, accepted 2026-01-28. PubMed 41680191. PMC13009157.
Preprint: bioRxiv 2025-05-15 (PMC12139860), titled "…mediate sensorimotor control…".
Data: Dryad doi:10.5061/dryad.fxpnvx153. Code: not noted.
**Status: VERIFIED — main-text PDF and Supplementary PDF (6 pp) read in full; Figures S1 and S5
rendered and read as images.**

## Headline counts
- **214 hair plate mechanosensory neurons, in 42 hair plates, across all six legs.**
  Verbatim: "The six *Drosophila* legs have 214 hair plate mechanosensory neurons that are clustered
  into 42 hair plates (Supplementary Fig. S1A)^40–42."
  Their sources for that number: Schubiger 1968 (Wilhelm Roux' Arch. Entwickl. 160:9–40);
  Hodgkin & Bryant 1979 (SEM of the adult of Drosophila melanogaster, Genet. Biol. Drosophila 2);
  Kuan et al. 2020 (Nat. Neurosci., doi:10.1038/s41593-020-0704-9). I did NOT open those three.
- "The fruit fly's **front leg contains over 200 proprioceptive sensory neurons**, including hair
  plates, campaniform sensilla, and chordotonal neurons" (cites Kuan et al. 2020).
- "The more proximal coxa and trochanter joints contain **similar numbers of campaniform sensilla
  and hair plates**."

## FULL HAIR-PLATE INVENTORY (Figure S1A, read from the rendered figure — VERIFIED visually)
Labels present in the schematics of front / middle / hind legs:

| Leg | Anterior view | Posterior view |
|---|---|---|
| **Front (T1)** | CxHP3, CxHP8, TrHP6, TrHP7, TrHP1, **TiHP3** | CxHP4, TrHP5 |
| **Middle (T2)** | CxHP8, TrHP6, TrHP7, TrHP3 | CxHP4, TrHP5, **TiHP3**, **TiHP2** |
| **Hind (T3)** | CxHP8, TrHP6, TrHP7 | CxHP4, TrHP5 |

Distinct named plates seen: CxHP3, CxHP4, CxHP8 (coxa); TrHP1, TrHP3, TrHP5, TrHP6, TrHP7
(trochanter); **TiHP2, TiHP3 (TIBIA)**. So Drosophila hair plates are on **coxa, trochanter, and
tibia** — I saw **no femoral hair plate** in this figure. Naming is positional (Cx/Tr/Ti + number),
not exhaustive per leg: the set differs between front, middle and hind legs.

## NEURONS PER HAIR PLATE (Figure S5E, number in parentheses beside each hair plate — VERIFIED)
| Hair plate | Sensory neurons | Nerve it enters the VNC through (Fig. S5A) |
|---|---|---|
| CxHP3 | **3** | DProN (dorsal prothoracic nerve) |
| CxHP4 | **4** | ProAN (prothoracic accessory nerve) |
| CxHP8 | **8** | VProN (ventral prothoracic nerve) |
| TrHP5 | **5** | ProLN (prothoracic leg nerve) |
| TrHP6 | **6** | ProLN |
| TrHP7 | **7** | ProLN |
| **total reconstructed** | **33** | matches "n = 33" in Fig. 5C |

⚠ **Strong inferred pattern (mine, not stated by the authors):** the number in each hair plate's
name equals its neuron count (CxHP3→3, CxHP4→4, CxHP8→8, TrHP5→5, TrHP6→6, TrHP7→7).
If that holds, TrHP1 = 1 neuron, TiHP2 = 2, TiHP3 = 3, TrHP3 = 3. **INFERENCE, not verified.**
Main text also says CxHP8 "consists of 8 cuticular hairs located on the coxa" (Fig. S1B legend),
i.e. **1 sensory neuron per hair** — consistent with Tuthill & Wilson 2016's statement that each
sensillum in a hair plate is innervated by a single sensory neuron.
Sum of the 6 characterized front-leg plates = 33 of the 214 total.

## ENCODING (CxHP8, front leg) — calcium imaging, N = 10 flies
Method: 2-photon GCaMP7f + tdTomato in CxHP8 axons, left front leg passively moved on a
manual 3-axis platform; DeepLabCut + Anipose 3D joint tracking.
- CxHP8 = **limit detector of anterior leg movement**. Max activity at the **combination of inward
  rotation + adduction** of the thorax-coxa joint; also higher when the coxa was extended.
- **Thorax–coxa joint angle conventions and measured ranges (Fig. S1C — VERIFIED):**
  - **Rotation**: posterior = 0/360°, lateral = 90°, anterior = 180°, medial = 270°.
    Measured range **[30, 229]°**.
  - **Adduction**: ventral = 0°, lateral = −90°, medial = +90°. Measured range **[−43, 43]°**.
  - **Flexion**: ventral = 0°, anterior = −90°, posterior = +90°. Measured range **[0, 54]°**.
  - Fig. 1G plot axes: Rotation 80→220°, Adduction −30→+30°, Flexion 0→60°.
    Fig. 1H (2-D tuning): Coxa Rotation 80→220° (y), Coxa Adduction −30→+30° (x).
    Representative trial (Fig. 1F) traces span Rotation 140–190°, Adduction −25 to +25°,
    Flexion 10–40°; peak normalized Ca²⁺ 0.79.
  - Fig. S1F: joint-angle probability density during peak-calcium events peaks near
    **adduction ≈ 0–15°** and **rotation ≈ 160–180°**, shifted toward higher values relative to the
    all-frames distribution. (Read off the figure; **no numeric activation threshold in degrees is
    stated anywhere in the text or supplement.**)
- **TONIC, no phasic component detected.** Verbatim: "we found no evidence for phasic tuning among
  CxHP8 axons – calcium signals remained sustained when the leg was held at an extreme position. It
  is possible that all hair plate neurons in the fly have tonic encoding properties."
  ⚠ This is **calcium, not electrophysiology**. GCaMP7f low-passes; a phasic spike component could
  be invisible. The authors flag this ("More work is needed…").
- **NO spike rates, NO latencies in ms, NO adaptation time constants are reported.** Explicit
  negative finding — this paper has no electrophysiology at all.
- Active across rest, walking, and grooming; peak calcium largest during **front-leg grooming**.
- No presynaptic-inhibition-style suppression of hair-plate calcium during self-generated movement
  (contrast: FeCO hook neurons ARE presynaptically inhibited — Dallmann et al. 2025 Nature).

## CONNECTIVITY (FANC female adult nerve cord; all 8 CxHP8 axons reconstructed)
- CxHP8 output: **2279 ± 482 synapses per axon**; **75% of output onto premotor (58%) + motor (17%)**.
  (Fig. S5B, read off figure: mean output synapses per axon roughly CxHP3 ≈ 4000, CxHP4 ≈ 3800,
  TrHP5 ≈ 2700, TrHP6 ≈ 2200, CxHP8 ≈ 2300, TrHP7 ≈ 1800; y-axis 0–6000. APPROXIMATE, figure-read.)
- Hair plate axons **do not project intersegmentally**; majority of di-synaptic connectivity also
  onto motor neurons of the same leg.
- Hair plate axons also synapse **onto glia** (Fig. S5C shows an EM micrograph of a hair-plate→glia
  synapse with vesicles and a putative T-bar) — speculated injury-signalling role.
- **69 motor neurons** control the left front leg, in **14 motor modules** (module definitions from
  Lesser et al. 2024 Nature 631:369–377).
- CxHP8 → strong monosynaptic excitation of the **coxa posterior** motor module (Fig. S2A: all 8
  CxHP8 axons primarily synapse onto coxa-posterior MNs); indirect excitation/inhibition reaching
  every other leg segment. Recurrent premotor→premotor and premotor→CxHP8 connections exist
  (Fig. S2B), including 19A premotor neurons synapsing back onto CxHP8 axons.
- Analysis threshold used: only premotor/motor neurons receiving **≥4 synapses on average per
  neuron** from an upstream cell class (for CxHP8: 8 cells × 4 synapses = 32 synapse floor).
- Premotor hemilineages contacted (Fig. S5D), grouped by the figure's own excitatory/inhibitory bar:
  **excitatory**: 1A, 3A, 4B, 7B, 17A, 19B, 20A, 22A, 23B;
  **inhibitory**: 6A, 8A, 9A, 12B, 13A, 13B, 14A, 16B, 19A, 21A.
- Motor modules named in Fig. S5E with cell counts (varies by which MNs pass threshold):
  Coxa Rotate (3), Coxa Promote (4), Coxa Posterior (3–6), Trochanter Flex (8–10),
  Trochanter Extend (7–8), Femur Reduct (2–5), Tibia Flex A (6–9), Tibia Flex B (2–4),
  Tibia Flex C (1–2), Tibia Extend (2), Tarsus Depress M. (1), Tarsus Depress V. (1),
  Tarsus LTM (2–3).

## PREDICTED REFLEX FUNCTION PER HAIR PLATE (Fig. 5F / S5E, motor impact score)
| Hair plate | Predicted function |
|---|---|
| CxHP3 | **stabilization** (reinforces both anterior and posterior movement) |
| CxHP4 | **anterior** leg movement |
| CxHP8 | **posterior** leg movement (VERIFIED behaviourally) |
| TrHP5 | **posterior** leg movement |
| TrHP6 | **anterior** leg movement |
| TrHP7 | **posterior** leg movement |

Motor impact score = weighted sum of signed mono- and di-synaptic connection strengths, sign set by
the intervening interneuron's hemilineage-inferred neurotransmitter (method from Lee et al. 2025).

## BEHAVIOUR / EFFECT SIZES
- Optogenetic **activation** (ChrimsonR, 6 cameras, DeepLabCut+Anipose): standing flies show
  outward rotation, lateral movement and flexion of the stimulated front leg → **posterior and
  lateral tarsus displacement**. (Effect sizes are plotted in degrees in Fig. 3C-E; axis shown
  around ±10°. No single numeric effect size in text. **No latency in ms is reported.**)
- Optogenetic **silencing** (GtACR1) during forward walking → medial overshoot at the
  swing-to-stance transition. Chronic silencing (Kir2.1) on a linear treadmill, statistics:
  AEP longitudinal **p = 5.96e−10**; AEP lateral **p = 5.87e−210**; PEP longitudinal **p = 3.95e−21**;
  PEP lateral **p = 1.24e−52** (linear mixed-effects model).
  Front-leg grooming, thorax-coxa angles with CxHP8 silenced: Rotation **p = 9.185e−8**;
  Adduction **p = 5.88e−27**; Flexion **p = 2.43e−10**.
  Left turns: n.s. (p > 0.05). Right turns: significant. Body height and body angle: n.s.
  Resting tarsus polygon area significantly larger when silenced (**p = 0.0275**, two-sided t-test).
- Behaviour classification thresholds used: forward walking = ball forward velocity > 5 mm/s and
  |rotational velocity| < 25 °/s; turns = |rotational velocity| > 25 °/s; treadmill forward walking
  = body forward velocity > 5 mm/s and |heading| < 15°.
- Flies: adult **males**, 2–5 days post-eclosion, 25 °C, 14:10 LD.
  (Note the connectome is FANC = adult **female** nerve cord.)

## Genetic tools
- **CxHP8-GAL4 = R48A07-AD ∩ R20C06-DBD** split-GAL4 (Bloomington #69841 and #71070, from Moon Lab,
  Yonsei). Labels **6 of 8** CxHP8 cells in the front leg, **3 of 8** in the middle leg.
- Controls: R52A01-DBD alone, R48A07-AD alone, R39B11-AD alone.
- Table S1 screens 12 split-GAL4 combinations against front/middle/hind leg proprioceptors. Columns
  present: CxHP4, CxHP3, CxHP8, TrHP5, TrHP6, TrHP7, TrHP1, TrCS3 (TrG), TrCS5 (TrFa), FeCS11
  (front leg); CxHP4, CxHP8, TrHP5, TrHP6, TrHP7, TrCS3, TrCS2 (middle); same set (hind).
- Authors state explicitly: **no genetic means yet exists to label all hair plates, or even all
  sensory neurons within a single hair plate.**

## FANC/MANC annotation notes
- MANC v.? — "Some hair plate axons were previously reconstructed in an electron microscopy dataset
  of a male adult nerve cord (MANC)^22 [Marin et al. 2024 eLife 13, doi:10.7554/eLife.97766.1.sa3].
  However, **specific hair plate axons could not be identified in MANC due to poor reconstruction
  quality**." So the authors re-reconstructed in FANC.
- Peripheral identity of each hair-plate axon in FANC was assigned by combining genetic driver
  lines, axonal morphology, and the **Kuan et al. 2020 X-ray holographic nano-tomography dataset of
  the fly leg**. CxHP8 is identifiable because it is the only hair plate whose axons enter the VNC
  through the **VProN**.
- **No specific FANC/MANC cell-type string names for hair plate neurons appear in the paper text or
  the supplement I read — could not verify those.**

## Forward-looking note relevant to a whole-fly sim
"we have added all of the hair plates characterized in this study to the open-source **Janelia fly
body Blender model**" (their ref 60) — Supplementary Video 2 animates which hairs deflect at each
phase of the step cycle.
