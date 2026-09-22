# Leg mechanosensation: hair plates, tactile bristles, tarsal structures, firing rates

Scope: Drosophila leg **hair plates**, **tactile bristles**, **tarsal sensory structures**, total
**leg mechanosensory neuron counts**, and **firing-rate / timing data**.
Campaniform sensilla counts (Dinges 2021) and connectome annotations are another agent's topic;
CS numbers appear here only where a source I read gives them incidentally.

**Verification key**
- **[V]** I read the source myself this session (PDF / full text / rendered figure).
- **[Vfig]** read off a rendered figure rather than quoted text — approximate.
- **[2nd]** reported second-hand via a paper that cites it; I did not open the original.
- **[CNV]** could not verify — I tried and failed to get the source.
- **[INF]** my own inference/arithmetic, labelled as such.

⚠ Species flags are explicit throughout. **Drosophila** unless marked otherwise.

---
---

# 1. HAIR PLATES

## 1.1 Complete inventory — one Drosophila FRONT leg [V]
Source: **Kuan et al. 2020, Nat. Neurosci. 23:1637–1643, Supplementary Data Table 3**
(X-ray holographic nano-tomography of an intact adult front leg, 50–75 nm voxels).

| Cluster | Joint | Sensory neurons | Nerve into VNC |
|---|---|---|---|
| CoHP3 (=CxHP3) | thorax–coxa | **3** | dorsal prothoracic (DProN) |
| CoHP4 (=CxHP4) | thorax–coxa | **4** | prothoracic accessory (ProAN) |
| CoHP8 (=CxHP8) | thorax–coxa | **8** | ventral prothoracic (VProN) |
| TrHP1 | coxa–trochanter | **1** | main leg nerve (ProLN) |
| TrHP5 | coxa–trochanter | **5** | ProLN |
| TrHP6 | coxa–trochanter | **6** | ProLN |
| TrHP7 | coxa–trochanter | **7** | ProLN |
| TiHP3 | **femur–tibia** | **3** | ProLN |
| **TOTAL** | | **37 neurons in 8 hair plates** | |

**The numeral in each hair plate's name is its sensory-neuron count.** Verified independently in two
papers (Kuan 2020 Table S3; Pratt 2026 Fig. S5E gives CxHP4(4), CxHP3(3), CxHP8(8), TrHP5(5),
TrHP6(6), TrHP7(7) = 33 axons, matching their stated n = 33).

**Joints with hair plates: thorax–coxa, coxa–trochanter, femur–tibia.**
**No hair plate on the proximal femur** in either source. **None on the tarsus.**
(The brief asked about "proximal femur" — I found none; the distal-most Drosophila leg hair plates
are TiHP2/TiHP3 at the femur–tibia joint. [explicit negative finding])

⚠ Naming clash: Kuan writes **Co**HP, Pratt writes **Cx**HP, for the same organs.

## 1.2 Per-leg distribution and whole-animal totals
**214 hair plate mechanosensory neurons in 42 hair plates across all six legs** — Pratt et al. 2026,
Nat. Commun. 17:2664, verbatim, citing Schubiger 1968, Hodgkin & Bryant 1979, Kuan et al. 2020. [V]

Plate complement per leg, from Pratt et al. 2026 Fig. S1A [Vfig]:
| Leg | Hair plates present | # plates | # neurons (by the naming rule) |
|---|---|---|---|
| Front (T1) | CxHP3, CxHP4, CxHP8, TrHP1, TrHP5, TrHP6, TrHP7, TiHP3 | 8 | 37 |
| Middle (T2) | CxHP4, CxHP8, TrHP3, TrHP5, TrHP6, TrHP7, TiHP2, TiHP3 | 8 | 38 |
| Hind (T3) | CxHP4, CxHP8, TrHP5, TrHP6, TrHP7 | 5 | 30 |
| **per side** | | **21** | **105** |
| **×2 sides** | | **42 ✓** | **210** |

Plate count reproduces Pratt's 42 exactly. Neuron sum gives **210 vs their stated 214** — a 4-neuron
gap. Either I misread a schematic label or one plate departs from the naming rule. **Flagged, not
papered over.** [INF]

**Recommended sim values:** front 37, middle 38, hind 30 hair-plate neurons per leg
(front leg is the one with actual measurement behind it).

## 1.3 What hair plates encode [V]
Only ONE Drosophila hair plate has ever been recorded from: **CxHP8** (Pratt et al. 2026, calcium
imaging, GCaMP7f, N = 10 flies, front left leg passively moved on a 3-axis platform).

- **Function: limit detector of ANTERIOR leg movement.** Maximal when the thorax–coxa joint is
  simultaneously **inwardly rotated and adducted**; also elevated when the coxa is extended.
- **TONIC. No phasic component found.** Verbatim: *"we found no evidence for phasic tuning among
  CxHP8 axons – calcium signals remained sustained when the leg was held at an extreme position.
  It is possible that all hair plate neurons in the fly have tonic encoding properties."*
  ⚠ **This is a calcium result.** GCaMP7f low-passes hard; a phasic spike burst could be invisible.
  The authors say more work is needed. **There is no electrophysiology from any Drosophila hair
  plate neuron.** [explicit negative finding]
- **No presynaptic gating**: hair-plate calcium is NOT suppressed during self-generated leg movement
  (unlike FeCO hook neurons, which are — Dallmann et al. 2025 Nature 647:445–453).
- Active during rest, walking and grooming; **peak activity during front-leg grooming**, because the
  legs extend forward and the CxHP8 hairs stay continuously deflected.

### Joint-angle conventions and measured ranges (Pratt 2026 Fig. S1C) [Vfig] — usable directly in a sim
Thorax–coxa joint of the front leg:
| Angle | Convention | Measured range |
|---|---|---|
| **Rotation** | posterior = 0/360°, lateral = 90°, anterior = 180°, medial = 270° | **[30, 229]°** |
| **Adduction** | ventral = 0°, lateral = −90°, medial = +90° | **[−43, 43]°** |
| **Flexion** | ventral = 0°, anterior = −90°, posterior = +90° | **[0, 54]°** |

CxHP8 tuning plots span rotation 80–220°, adduction −30 to +30°, flexion 0–60°. The peak-calcium
joint-angle distributions (Fig. S1F) sit near **adduction ≈ 0–15°** and **rotation ≈ 160–180°**,
shifted high relative to the all-frames distribution. [Vfig]

**⚠ NO numeric activation threshold in degrees is stated anywhere in the paper or supplement**, and
no half-activation angle, no saturation point, no gain. Tuning is published as figures only. To
parameterise a sim you would need to digitise Fig. 1G/1H or pull the Dryad deposit
(**doi:10.5061/dryad.fxpnvx153**). [CNV for a numeric threshold]

## 1.4 Hair plate → motor circuit [V] (Pratt et al. 2026, FANC female nerve cord)
- **CxHP8: 2279 ± 482 output synapses per axon; 75% onto premotor (58%) + motor (17%) neurons.**
- Per-axon mean output synapses for the other plates (Fig. S5B, y-axis 0–6000): CxHP3 ≈ 4000,
  CxHP4 ≈ 3800, TrHP5 ≈ 2700, TrHP6 ≈ 2200, TrHP7 ≈ 1800. [Vfig, approximate]
- **69 motor neurons** control the left front leg, in **14 motor modules** (Lesser et al. 2024,
  Nature 631:369–377).
- **Hair plate axons do NOT project intersegmentally.** Majority of di-synaptic connectivity also
  lands on motor neurons of the same leg.
- Hair plate axons synapse **onto glia** (EM micrograph with vesicles + putative T-bar, Fig. S5C).
- Analysis threshold: ≥4 synapses on average per neuron from an upstream cell class.
- Premotor hemilineages contacted, by the figure's own excitatory/inhibitory grouping:
  **excitatory** 1A, 3A, 4B, 7B, 17A, 19B, 20A, 22A, 23B;
  **inhibitory** 6A, 8A, 9A, 12B, 13A, 13B, 14A, 16B, 19A, 21A. [Vfig]
- Recurrent structure: premotor→premotor and premotor→CxHP8 connections exist, incl. **19A premotor
  neurons synapsing back onto CxHP8 axons** (Fig. S2B).

**Predicted reflex action per hair plate** (motor impact score, Fig. 5F / S5E):
| Plate | Predicted function |
|---|---|
| CxHP3 | stabilization (reinforces both directions) |
| CxHP4 | drives **anterior** leg movement |
| CxHP8 | drives **posterior** leg movement ✅ confirmed behaviourally |
| TrHP5 | drives **posterior** |
| TrHP6 | drives **anterior** |
| TrHP7 | drives **posterior** |

Each limit detector drives movement **away from the joint limit it detects** — a negative-feedback
limit reflex. CxHP8 (anterior limit) → strongest monosynaptic excitation of the **coxa posterior**
motor module; CxHP4 (antagonistically positioned) → **coxa rotate**, driving anterior movement.

## 1.5 Behavioural effects of CxHP8 manipulation [V]
- **Activation** (ChrimsonR): in standing flies, outward rotation + lateral movement + flexion of the
  stimulated front leg ⇒ posterior and lateral tarsus displacement. Joint-angle plots on ±10° axes;
  no single numeric effect size in text; **no latency in ms reported.**
- **Silencing** (GtACR1 acute, Kir2.1 chronic): medial **overshoot at the swing-to-stance
  transition**; AEP and PEP shift; more splayed resting tarsi.
  Linear mixed-effects p-values: AEP longitudinal 5.96e−10, AEP lateral 5.87e−210, PEP longitudinal
  3.95e−21, PEP lateral 1.24e−52. Grooming thorax–coxa angles: rotation 9.185e−8, adduction
  5.88e−27, flexion 2.43e−10. Right turns significant, left turns n.s. Body height / body angle n.s.
  Resting tarsus polygon area larger when silenced, p = 0.0275.
- Genetics: **CxHP8-GAL4 = R48A07-AD ∩ R20C06-DBD**, labels 6/8 front-leg and 3/8 middle-leg cells.
  Authors state **no genetic line yet labels all hair plates, or even all neurons in one hair plate.**
- Flies: adult **males**, 2–5 d post-eclosion. The connectome (FANC) is **female**.

## 1.6 Axon calibre — conduction speed proxy [V] (Kuan et al. 2020)
| Axon class | Diameter |
|---|---|
| CoHP3 | **1380 ± 20 nm** |
| CoHP4 | **1140 ± 240 nm** |
| CoHP8 | **1030 ± 90 nm** |
| coxa motor axons (n=5) | 1140 ± 130 nm |
| thorax motor axons (n=2) | 1880, 2150 nm |
| chordotonal + bristle axons | too narrow to trace at 150–200 nm |

*"signals … from coxal hair plates and trochanteral campaniform sensilla are conducted to the VNC
faster or more reliably than others."* ⇒ **hair plate + trochanteral CS = fast channel; chordotonal
and bristle = slow channel.** No m/s measured here.

## 1.7 Hair plates in OTHER INSECTS — ⚠ NOT Drosophila
- **Two physiological types** generically: rapidly adapting (phasic, respond to hair movement) and
  slowly adapting (tonic, respond to maintained deflection) — Tuthill & Wilson 2016 review,
  cited to locust work. [V for the review statement, 2nd for the originals]
  ⚠ Pratt 2026 found **no** phasic type in Drosophila CxHP8.
- **Locust (Schistocerca gregaria) tibial hair plate** — Newland PL, Watkins B, Emptage NJ, Nagayama T
  (1995) *J. Exp. Biol.* 198:2397–2404, PMID 7490573. [2nd, abstract only]
  - **~11 hairs**, all trichoid sensilla, all polarised with tips toward the dorsal tibia.
  - **Hair lengths 90–140 µm.**
  - Located on the proximal anterior face of the **pro- and mesothoracic** tibiae; **absent from the
    metathoracic leg.**
  - **"The hairs are deflected by the coverplate only at femoro-tibial angles of less than 90°."**
    ← the one concrete threshold angle I found for any insect hair plate.
  - Two neuron types: **phasic (velocity-sensitive)** and **phasotonic (velocity + tonic)**; both
    **directionally sensitive**.
  - Development: absent through the first four larval stages; **3 hairs in fifth instar**; full
    complement after the final moult.
  - **[CNV] firing rates in spikes/s — full text paywalled.**
- **Cockroach (Periplaneta) trochanteral hair plate** — Wong RK & Pearson KG (1976) *J. Exp. Biol.*
  64:233–249, doi:10.1242/jeb.64.1.233, PMID 1270992. [2nd, abstract only]
  - Sensilla split into **type I** (respond to **dynamic** displacement only) and **type II**
    (respond to **dynamic AND static** displacement).
  - Normally excited by **phasic flexion of the femur near the end of leg protraction**.
  - Short-latency **excitation of the slow femur-extensor motoneurone**, **inhibition of femur
    flexor motoneurones**.
  - **Removal of the trochanteral hair plate in one leg causes that leg to overstep** due to
    exaggerated femur flexion.
  - **[CNV] firing rates, threshold degrees, latency in ms — full text not retrievable.**
- Companion paper: Pearson KG, Wong RKS, Fourtner CR (1976) *Connexions between hair-plate afferents
  and motoneurones in the cockroach leg.* J. Exp. Biol. 64:251–266, PMID 5571. Monosynaptic
  excitation of trochanteral extensor MNs; indirect inhibition of flexor MNs. [2nd]
- **Locust thoraco-coxal hair plate central connections** — Kuenzi F & Burrows M (1995) J. Exp. Biol.
  198:1589–1601. [2nd, not opened]
- **Locust hind-leg coxo-trochanteral proprioceptors** — Bräunig P & Hustert R (1985) J. Comp.
  Physiol. A 157:83–89. [2nd, not opened]
- **Stick insect**: ablating middle-leg hair plates produces nonlinear, larger shifts in the anterior
  extreme position of the **ipsilateral hind leg** (intersegmental effect). [2nd, via Pratt 2026 ref 58]
- **Cockroach antennal hair plates** are **exteroceptive** — object-guided tactile orientation
  (Okada J & Toh Y 2000, J. Comp. Physiol. A 186:849–857). [2nd]
- ⚠ **Fly neck, not leg**: two ventral neck hair plates form the **prosternal organ**, encoding head
  rotation about all three axes; shaving one side makes the fly roll its head toward that side. [V]

---
---

# 2. TACTILE BRISTLES

## 2.1 Counts — per leg and per segment
**Per-segment counts for one Drosophila front leg** — Kuan et al. 2020 Supplementary Data Table 3.
This is the only per-segment bristle table I could find; Kuan's own note says
*"Total numbers could not be found in previous reports."* [V]

| Segment | Bristles |
|---|---|
| Coxa | **13** |
| Trochanter | **10** |
| Femur | **113** |
| Tibia | **97\*** |
| Tarsus | **not imaged** |
| **imaged total** | **233 (LOWER BOUND)** |

\* excludes bristles on the distal half of the tibia, which was outside the imaged volume.
**The tarsus was not imaged at all — and the tarsus has the highest bristle density on the leg.**

**Whole-leg counts** [V]:
- **"The front leg of Drosophila melanogaster is covered by more than 400 mechanosensory bristles,
  with the highest density on the more distal leg segments"** — Elabbady et al. 2026, Curr. Biol.
  36:2192–2206.e4, citing **Held LI Jr (1991) BioEssays 13:633–640** [Held not opened, 2nd].
- **409 bristle axons reconstructed** from the left front leg in FANC: **394 via the leg nerve,
  8 via the ventral prothoracic nerve, 7 via the dorsal prothoracic nerve**; **<20** further axons
  could not be reconstructed due to segmentation errors. — Elabbady et al. 2026. [V]

**⇒ Use ~400–430 tactile bristle neurons per front leg.** Kuan's 233 is a partial-volume count, not
a contradiction.

The canonical per-segment morphology source is **Hannah-Alava A (1958). Morphology and chaetotaxy of
the legs of Drosophila melanogaster. J. Morphol. 103:281–310, doi:10.1002/JMOR.1051030205** — cited
by Tuthill & Wilson 2016, Hopkins et al. 2023 and Elabbady et al. 2026 for bristle position and
density. **[CNV — I could not obtain this 1958 paper; its actual per-segment tables remain unread.]**

## 2.2 Bristle neuron properties
- **One mechanosensory neuron per bristle.** Verbatim: *"A single neuron resides at the base of each
  bristle."* — Tuthill & Wilson 2016, Cell 164:1046–1059. [V]
- **Directionally selective**: respond most strongly to deflection in one direction, set by the
  asymmetric orientation of the hair socket. Preferred direction = the one that reduces the acute
  angle between bristle and cuticle. [V]
- **Sensitivity: deflections < 100 nm** — Walker RG, Willingham AT & Zuker CS (2000), Science
  287:2229–2234 (NompC). [2nd, via Elabbady et al. 2026; original not opened]
- "Mechanical stimulation of the bristle can evoke **intense spiking activity**" — **no number
  given**. [V, but qualitative]
- **Adaptation**: slowly adapting, with sensory fatigue on repeated stimulation — **Corfas G &
  Dudai Y (1990), J. Neurosci. 10:491–499, doi:10.1523/JNEUROSCI.10-02-00491.1990, PMID 2154560.**
  Verbatim from abstract: *"responds with a burst of action potentials to deflection of the bristle
  towards the body wall. The decay of the firing rate upon sustained deflection is typical of a
  **slowly adapting** mechanosensory neuron. Upon repeated monotonous stimulation, the response
  decreases and the kinetics of adaptation change; the response recovers after rest."*
  ⚠ This is the **anteronotopleural bristle on the THORAX, not a leg bristle.**
  **[CNV — the paper's actual spikes/s and adaptation time constants; only a scanned PDF exists and
  every route to it (jneurosci.org, PMC6570162) was blocked.]**
- **Chemosensory taste bristles also carry ONE mechanosensory neuron** alongside their multiple
  gustatory receptor neurons — Hopkins et al. 2023. [V] So taste bristles report deflection too.
  ⚠ **Locust**: taste-hair mechanosensory neurons are **directionally selective and rapidly
  adapting**, with a **lower mechanical threshold than purely tactile hairs**; Tuthill & Wilson 2016
  state explicitly *"their response properties in Drosophila are not known."* [V]

## 2.3 Bristle → central circuits
Elabbady et al. 2026 (FANC, 409 bristle axons, front left leg) [V]:
- **~550 output synapses and ~77 input synapses per bristle axon** (means).
- Output distribution: **local 63%, ascending 22%, intersegmental 12%, descending <2%, other
  sensory ~1%; most bristles make ZERO synapses onto motor neurons.**
  ⇒ **There is no monosynaptic bristle→motor-neuron reflex arc.** Contrast hair plates, which put
  17% of output straight onto motor neurons.
- Postsynaptic partner counts: local n=296, ascending n=94, intersegmental n=74, descending n=21.
- Top target: **hemilineage 23B** (cholinergic/excitatory), **59 cells**, receiving on average
  **25% of each bristle axon's output**. 23B neurons draw **40% of their input from sensory axons,
  85% of that from bristles**. 13 subtypes defined by axon projection.
- **Somatotopy**: proximo-distal leg axis maps to **concentric rings** in the leg neuropil
  (distal = centre, proximal = outer edge); antero-posterior axis is a **binary compartment**
  boundary; dorso-ventral is graded. Developmental TF correlates: *dac* → proximal, *rn*/*ap* →
  distal, *hh* → posterior, *mid* → ventral.
- Optogenetic activation of proximal-sensing vs distal-sensing 23B drives grooming targeted at the
  proximal femur vs the tibia–tarsus joint respectively.

Tuthill & Wilson 2016 Cell [V]:
- **Three classes** of second-order VNC neuron receive direct input from a single femur bristle:
  one compares touch within a limb, one across limbs (midline projection neurons: ipsilateral
  excitation + mixed contralateral excitation/inhibition), one compares touch against
  proprioception. Signals **diverge immediately**, in parallel, not hierarchically.
- **69 of 699** identifiable anterior-VNC somata responded to optogenetic bristle stimulation
  (calcium; authors call it a lower bound).
- **Chordotonal (FeCO) activation inhibits** the spike rate of central touch neurons — touch gain is
  modulated by leg position.
- Bristle axons terminate in the **most ventral layer** of the VNC neuropil; proprioceptive axons
  (hair plate, campaniform, chordotonal) terminate **dorsal to them**. Clean laminar separation.
- Stimulating **one or two bristles** is sufficient to trigger a complete grooming sequence. [V]

---
---

# 3. TARSAL AND DISTAL SENSORY STRUCTURES

## 3.1 Is there a tibial or tarsal chordotonal organ distinct from the FeCO? — **YES, a tibial one.**
> *"Two chordotonal organs (COs) are present outside of the tarsal segments… One is situated in the
> **proximal femur (FeCO)** and the other in the **distal tibia (tCO)**"*
> — Hopkins, Barmina & Kopp 2023, PLOS Biol. 21(6):e3002148, Fig. 1A legend, citing Mamiya et al.
> 2018 (Neuron 100:636–650) and **McKelvey et al. 2021, Curr. Biol. 31:3894–3904.e5**
> (*Drosophila females receive male substrate-borne signals through specific leg neurons during
> courtship*). [V for the Hopkins statement; **McKelvey not opened — [2nd]** for tCO neuron counts,
> which I could not obtain.]

**tCO size**: a secondary source states *"In Drosophila, the distal tibial chordotonal organ
contains **three scolopidial sensilla**"* — surfaced via search from a review of insect-leg vibration
receptors, **[2nd, LOW CONFIDENCE: I could not open the primary source to confirm]**. If each
scolopidium carries 2 neurons (as Kuan et al. found for the FeCO), tCO ≈ **6 neurons**. [INF]
Also reported: Nanchung and Piezo mediate vibration detection in **FeCO** scolopidia but are **not
expressed in the tCO**, and the **FeCO**, not the tCO, is what detects male courtship vibration.
[2nd, from search summary of McKelvey et al. 2021]

- **NO tarsal chordotonal organ.** *"chordotonal organs are not present in the upper tarsal
  segments"*, and their ta1 scRNA-seq recovered **zero** chordotonal clusters, while the whole-leg
  Fly Cell Atlas has **3 putative chordotonal clusters**. [V]
- Kuan et al. 2020's front-leg table lists chordotonal scolopidia **only in the femur** — but their
  imaged volume stopped at the first half of the tibia, so tCO would have been outside it. Not a
  contradiction. [V]

## 3.2 Tarsal campaniform sensilla [V] (Hopkins et al. 2023, nomenclature from Dinges et al. 2021)
- **Three CS in ta1**: two on the **dorsal distal end** (Ta1GF) and one on the **proximal ventral
  side** (Ta1SF).
- **No campaniform sensilla in the distal tibia, ta2, or proximal ta3.**
- Each CS = **4 cells** (neuron, thecogen/sheath, tormogen/socket, trichogen/dome) and is
  **singly innervated** — 1 neuron per CS.
- Tibial CS from Kuan's front-leg table: **TiCSd2 (2, dorsal), TiCSv1 (1, ventral), TiCSv2 (2,
  ventral)** = 5 on the proximal tibia. [V]

## 3.3 Tarsal bristles and the chemo/mechano split [V] (Hopkins et al. 2023)
- **ta1 has the highest concentration of mechanosensory bristles of any part of the leg.**
- Arrangement: **transverse rows on the ventral side** (thought to aid grooming); **longitudinal
  rows on the anterior, dorsal and posterior sides** (cites Hannah-Alava 1958).
- **Mechanosensory bristle = mono-innervated (1 neuron).**
  **Chemosensory taste bristle = poly-innervated: multiple GRNs + exactly 1 mechanosensory neuron.**
- **Chemosensory taste bristles in ta1: ~11 in males, ~7 in females** (cites Nayak & Singh 1983).
- **Sex comb** (males, foreleg ta1 only): the most distal transverse ventral bristle row is
  transformed — bristles become "teeth", thicker/longer/blunter/more melanised, and the **whole row
  rotates 90°**. These are still mechanosensory bristles.
- Canonical tarsal sensilla survey: **Nayak SV & Singh RN (1983). Sensilla on the tarsal segments
  and mouthparts of adult Drosophila melanogaster. Int. J. Insect Morphol. Embryol. 12:273–291,
  doi:10.1016/0020-7322(83)90023-5.** Males have more silver-staining (dendrite-bearing) bristles
  than females on the first 4 tarsal segments of the prothoracic legs. **[CNV — paywalled; I could
  not get the per-segment tables.]**

## 3.4 "Ground contact" detectors — what actually exists
There is **no dedicated ground-contact organ** in the Drosophila leg that I could find named as such.
The functional candidates are:
1. **Tarsal campaniform sensilla** (Ta1GF ×2, Ta1SF ×1) — cuticular strain during load-bearing.
2. **Ventral tarsal mechanosensory bristles** in transverse rows — direct substrate contact.
3. **Tibial campaniform sensilla** TiCSv1/TiCSv2 (ventral) and TiCSd2 (dorsal) — load.
4. **Club FeCO neurons** — substrate vibration (<1 µm amplitude, high frequency); Lee et al. 2025
   show these are **exteroceptive**, routed to the brain, not to local leg motor circuits.
5. **tCO in the distal tibia** — substrate-borne vibration during courtship (McKelvey et al. 2021).
6. ⚠ Flies **lack a subgenual organ**, the dedicated tibial vibration sensor other insects have.
   Verbatim, Lee et al. 2025: *"Many insect species also possess subgenual organs, specialized
   vibration sensors in the tibia, but flies lack these sensory structures."* [V]

## 3.5 Other internal receptors found only by XNH [V] (Kuan et al. 2020)
- **Stretch receptor neurons: 1 in the coxa (ventral nerve, NEW — not previously labelled) and
  1 in the femur (main nerve).** *"each major joint in the fly leg, and not only the distal joints,
  is monitored by a single stretch receptor neuron."*
- **Strand receptor: 1 in the coxa**, entering via the accessory nerve, with **no cell body in the
  leg — its soma is in the VNC.** Previously reported only in orthopteran insects. NEW for
  Drosophila, and they could not trace it back to its soma.

---
---

# 4. TOTAL MECHANOSENSORY NEURONS PER DROSOPHILA LEG

**Headline figure to quote:**
> *"The fruit fly's front leg contains over 200 proprioceptive sensory neurons, including hair
> plates, campaniform sensilla, and chordotonal neurons"* — Pratt et al. 2026, Nat. Commun. 17:2664,
> citing Kuan et al. 2020. [V]

**Full build-up from Kuan et al. 2020's front-leg table** [V data, [INF] arithmetic]:
| Class | Neurons (front leg) |
|---|---|
| Hair plates (8 plates) | 37 |
| Campaniform sensilla (8 clusters, coxa→proximal tibia) | 33 |
| FeCO (76 scolopidia × 2 neurons each) | **152** |
| Stretch receptors (coxa + femur) | 2 |
| Strand receptor (coxa) | 1 |
| **= proprioceptors** | **225** ✅ matches "over 200" |
| Bristles (imaged: coxa 13, tr 10, femur 113, tibia 97) | 233 (partial) |
| **= imaged total** | **458 (lower bound)** |

**Best whole-front-leg estimate**: **225 proprioceptors + ~409 bristles ≈ 630–650 mechanosensory
neurons per front leg**, plus unimaged tarsal campaniform sensilla and the tCO. ⚠ This mixes two
datasets and two individual flies — it is an estimate, not a measurement. [INF]

**FeCO neuron count — four values from four sources, all Drosophila:**
| Value | Source | Status |
|---|---|---|
| **152 neurons in 76 scolopidia** (2 neurons per scolopidium) | Kuan et al. 2020 Table S3 | [V] |
| **~150 excitatory (cholinergic) neurons**, 5 subtypes | Lee et al. 2025 Nat. Commun. 16:4105 | [V] |
| **135 neurons = 80% of total** (⇒ total ≈ 169) via iav-Gal4 | Mamiya et al. 2018 Neuron 100:636–650 | [V] |
| **100–138 neurons** (older range Kuan says they exceed) | Shanbhag, Singh & Singh 1992, Int. J. Insect Morphol. Embryol. 21:311–322 | [2nd] |

Mamiya et al. 2018 driver-line counts [V]: claw (R73D10-Gal4) **20 cell bodies**;
club (R64C04-Gal4) **30 neurons**; hook (R21D12-Gal4) **only 3 neurons**; iav-Gal4 **135**.
Five response subclasses: **2 tonic (non-adapting) + 3 phasic (adapting)**.

Lee et al. 2025 [V]: 5 FeCO subtypes — claw-extension, claw-flexion (tibia **position**),
hook-extension, hook-flexion (tibia **movement/direction**), club (bidirectional movement +
**<1 µm, high-frequency vibration**). 80 axons reconstructed from the front left leg in FANC
(~50% of each subtype); 5 club axons ascend to the brain; each FeCO neuron contacts
**21.1 ± 1.1** distinct postsynaptic partners. Claw/hook feed **local leg motor circuits**
(proprioceptive); club feeds **ascending, cross-leg, brain mechanosensory** circuits
(exteroceptive). Neurons postsynaptic to **claw and hook share more downstream partners with
campaniform and hair-plate neurons than with other FeCO subtypes**; club shares almost none.

**Whole-body campaniform count — SPECIES WARNING.** Tuthill & Wilson 2016 write
*"Approximately 1200 campaniform sensilla are distributed over the legs, wings, halteres, and
antennae of the fly"* — but their citation is **Gnatzy W, Grunert U & Bender M (1987), Campaniform
sensilla of *Calliphora vicina*, II. Topography. Zoomorphology 106:312–319**, i.e. a **BLOWFLY, not
Drosophila.** ⚠ Do not use 1200 as a Drosophila number. [V — I checked the reference list myself.]

---
---

# 5. FIRING RATES AND TIMING

## 5.1 The blunt summary
**There is essentially no spike-rate electrophysiology from Drosophila LEG proprioceptors.**
- Hair plates: **calcium only** (Pratt et al. 2026 explicitly; no ephys in the paper at all).
- FeCO: **calcium only** (Mamiya et al. 2018: *"the anatomy and physiology of FeCO neurons have not
  previously been investigated"*; they used population GCaMP6f imaging. Agrawal et al. 2020
  eLife 9:e60299 patched **second-order** neurons, not the sensory neurons).
- Campaniform sensilla in Drosophila legs: no spike-rate data found in anything I read.
- Bristles: spikes ARE recorded extracellularly (Tuthill & Wilson 2016) but **no rate is quoted** —
  only "intense spiking activity" and the note that spike amplitude grows at high firing rates.
Everything quantitative on insect proprioceptor firing rates in the literature is **locust, stick
insect, cockroach or blowfly**.

## 5.2 The one hard Drosophila timing number ⭐ [V]
Tuthill & Wilson 2016, Cell 164:1046–1059, Fig. S6A — paired recordings, femur bristle → VNC:
> *"we measured a consistent delay of about **3 ms** from the time of a femur bristle neuron spike
> in the periphery to the onset of an EPSP in the VNC… The distance from the femur bristle to the
> VNC is approximately **850 µm**, suggesting that the conduction velocity is **0.28 m/s**, assuming
> a negligible delay for synaptic transmission."*
> *"the axons of **tarsus bristle neurons can be over twice as long** as the axons of femur bristle
> neurons."* ⇒ **≳6–7 ms** for tarsal bristles.

**For a sim: use 0.28 m/s for thin (bristle/chordotonal) leg sensory axons.** Hair plate axons are
3–4× the diameter (1.0–1.4 µm vs untraceable <0.15 µm) so they should be substantially faster; Kuan
et al. 2020 say exactly this qualitatively but measure no velocity. [V + [INF] for the extrapolation]

## 5.3 Second-order VNC neuron firing rates [Vfig]
Tuthill & Wilson 2016, Cell — figure y-axes for spike rates of central touch neurons responding to
bristle stimulation top out at **5, 8, 10 and 15 spikes/s** across panels. ⇒ **downstream VNC touch
neurons operate in the single-digit to ~15 spikes/s range.** Read off axes, not quoted in text.
Agrawal et al. 2020 (eLife 9:e60299) [2nd, via fetch]: **13Bα cells lack detectable action
potentials entirely** (graded, ~20% hysteresis between flexion and extension); **10Bα** current
injection failed to evoke identifiable spikes; only **9Aα** fires spikes, and peak rates are plotted
but not stated numerically.

## 5.4 Reflex latency budget for insects — ⚠ mostly NOT Drosophila [V for the citation chain]
| Component | Value | Source |
|---|---|---|
| Whole reflex, stimulus → behavioural response | **20–30 ms** | Jindrich & Full 2002 (cockroach); Schaefer et al. 1994 |
| Mechanosensory transduction + axonal conduction | **6–8 ms** | Höltje & Hustert 2003; Ridgel et al. 2001 |
| Muscle force-production kinetics | **10 ms** | Ahn et al. 2006 |
| Drosophila femur-bristle → VNC EPSP | **3 ms** | Tuthill & Wilson 2016 ✅ Drosophila |
| Drosophila wingbeat cycle (for haltere/wing CS phase locking) | **4–5 ms** | Tuthill & Wilson 2016 ✅ Drosophila |

Wing and haltere campaniform sensilla each fire **exactly one action potential per wing-stroke
cycle**, at a cell-specific phase. [V]

## 5.5 Chordotonal firing rates — the only real spike data, but LARVAL and ABDOMINAL ⚠
Warren B & Göpfert MC (2024). *Mechanically evoked spike responses of pentascolopidial chordotonal
organs of Drosophila melanogaster larvae.* **J. Exp. Biol. 227(17):jeb246197**,
doi:10.1242/jeb.246197. PMC11418168. [2nd — fetched and summarised, not read line by line]
⚠ **Third-instar LARVAL lch5 in abdominal segments A2–A5. NOT an adult leg organ.** Use only as an
order-of-magnitude anchor for chordotonal neurons.
- **Spontaneous rate: 46.6 ± 15.3 spikes/s** (n = 20, whole lch5 nerve);
  **24.6 ± 23.2 Hz** per identified single unit (n = 34 units from 11 lch5), range **1.5–78.4 Hz**.
- **Response latency to a 7.5 µm step: 2.36 ± 0.68 ms** (n = 10).
- **Velocity thresholds 5–45 µm/s; acceleration thresholds 1.6–11.2 µm/s².**
- Responses are **transient**, confined to the velocity/acceleration phase of a ramp-and-hold —
  i.e. these are movement detectors, not position detectors.
- *iav¹* mutant spontaneous rate collapses to **4.2 ± 7.2 Hz**.

## 5.6 Adult FeCO stimulus parameters (calcium, but useful as input ranges) [V]
Mamiya et al. 2018: vibration amplitudes **0.9 µm and 0.054 µm**; frequencies **100, 200, 400, 800,
1600, 2000 Hz**; club axon terminals carry a **frequency map** along the axon. Lee et al. 2025: club
neurons respond to **<1 µm** amplitude, high-frequency tibia vibration.

---
---

# 6. SIM-READY SUMMARY TABLE (front leg, Drosophila)

| Organ | Location | # organs | # neurons | Encodes | Adaptation | Axon Ø |
|---|---|---|---|---|---|---|
| Hair plates | thorax–coxa (3), coxa–troch (4), femur–tibia (1) | **8** | **37** | joint limits (extremes of ROM), one direction each | **tonic** (Ca²⁺ evidence) | 1.0–1.4 µm |
| Campaniform sensilla | trochanter (16), femur (12), tibia (5), ta1 (3) | 9 clusters | **~36** | cuticular strain / load, directional | fast + slow types | (troch. large) |
| FeCO | proximal femur | 1 organ, 76 scolopidia | **152** | tibia position (claw), movement (hook), vibration (club) | 2 tonic + 3 phasic subclasses | thin |
| tCO | distal tibia | 1 (~3 scolopidia) | **~6? [2nd/INF, unconfirmed]** | substrate vibration | unknown | unknown |
| Stretch receptors | coxa, femur | 2 | **2** | joint stretch | unknown | unknown |
| Strand receptor | coxa | 1 | **1** (soma in VNC) | unknown | unknown | unknown |
| Tactile bristles | whole leg, densest on tarsus | ~400+ | **~400–430** | deflection <100 nm, directional | **slowly adapting** + fatigue | thin (<0.15 µm) |
| **TOTAL** | | | **≈630–650** | | | |

Signal routing: **bristles → ventral VNC layer → 23B local interneurons → grooming/avoidance
(no monosynaptic MN contact).** **Hair plates + campaniform + claw/hook FeCO → intermediate/dorsal
VNC layers → premotor + direct MN contact → local limit and load reflexes.** **Club FeCO → ascending
to brain, cross-leg integration → exteroception.**

---

# 7. FULL CITATION LIST
**Verified (read this session):**
- Pratt BG, Dallmann CJ, Chou GM, Siwanowicz I, Walling-Bell S, Cook A, Sustar A, Azevedo A,
  Tuthill JC (2026). *Proprioceptive limit detectors contribute to sensorimotor control of the
  Drosophila leg.* Nat. Commun. **17:2664.** doi:10.1038/s41467-026-69333-z. PMID 41680191.
  PMC13009157; preprint PMC12139860; data Dryad doi:10.5061/dryad.fxpnvx153.
- Kuan AT, Phelps JS, Thomas LA, Nguyen TM, Han J, Chen C-L, Azevedo AW, Tuthill JC, Funke J,
  Cloetens P, Pacureanu A, Lee W-CA (2020). *Dense neuronal reconstruction through X-ray holographic
  nano-tomography.* Nat. Neurosci. **23:1637–1643.** doi:10.1038/s41593-020-0704-9. PMC8354006.
- Lee S-YJ, Dallmann CJ, Cook A, Tuthill JC, Agrawal S (2025). *Divergent neural circuits for
  proprioceptive and exteroceptive sensing of the Drosophila leg.* Nat. Commun. **16:4105.**
  doi:10.1038/s41467-025-59302-3. PMC12048489.
- Elabbady L, Chou GM, Sustar A, Cook A, Collman F, Tuthill JC (2026). *A central somatotopic map of
  the fly leg supports spatially targeted grooming.* Curr. Biol. **36:2192–2206.e4.**
  doi:10.1016/j.cub.2026.03.045; preprint doi:10.64898/2026.02.27.708590. PMID 41966690.
- Tuthill JC, Wilson RI (2016). *Parallel transformation of tactile signals in central circuits of
  Drosophila.* Cell **164:1046–1059.** doi:10.1016/j.cell.2016.01.014.
- Tuthill JC, Wilson RI (2016). *Mechanosensation and adaptive motor control in insects.*
  Curr. Biol. **26:R1022–R1038.** doi:10.1016/j.cub.2016.06.070.
- Hopkins BR, Barmina O, Kopp A (2023). *A single-cell atlas of the sexually dimorphic Drosophila
  foreleg and its sensory organs during development.* PLOS Biol. **21(6):e3002148.**
  doi:10.1371/journal.pbio.3002148.
- Mamiya A, Gurung P, Tuthill JC (2018). *Neural coding of leg proprioception in Drosophila.*
  Neuron **100:636–650.e6.** doi:10.1016/j.neuron.2018.09.009.

**Cited but NOT opened (second-hand only):**
- Held LI Jr (1991). *Bristle patterning in Drosophila.* BioEssays 13:633–640. doi:10.1002/bies.950131203
- Hannah-Alava A (1958). *Morphology and chaetotaxy of the legs of Drosophila melanogaster.*
  J. Morphol. 103:281–310. doi:10.1002/JMOR.1051030205 ← **the per-segment bristle source; get this**
- Nayak SV, Singh RN (1983). Int. J. Insect Morphol. Embryol. 12:273–291. doi:10.1016/0020-7322(83)90023-5
- Corfas G, Dudai Y (1990). J. Neurosci. 10:491–499. doi:10.1523/JNEUROSCI.10-02-00491.1990
- Walker RG, Willingham AT, Zuker CS (2000). Science 287:2229–2234. doi:10.1126/science.287.5461.2229
- Shanbhag SR, Singh K, Naresh Singh R (1992). Int. J. Insect Morphol. Embryol. 21:311–322
- Murphey RK, Possidente D, Pollack G, Merritt DJ (1989). J. Comp. Neurol. 290:185–200
- Merritt DJ, Murphey RK (1992). *Projections of leg proprioceptors within the CNS of the fly Phormia…*
- Schubiger G (1968). Wilhelm Roux' Arch. Entwickl. Org. 160:9–40
- Hodgkin HM, Bryant PJ (1979). *SEM of the adult of Drosophila melanogaster.* Genet. Biol. Drosophila 2
- McKelvey EGZ et al. (2021). Curr. Biol. 31:3894–3904.e5. doi:10.1016/j.cub.2021.06.002 ← **tCO source**
- Gnatzy W, Grunert U, Bender M (1987). Zoomorphology 106:312–319 ⚠ *Calliphora*, not Drosophila
- Warren B, Göpfert MC (2024). J. Exp. Biol. 227(17):jeb246197. doi:10.1242/jeb.246197 ⚠ larval
- Agrawal S et al. (2020). *Central processing of leg proprioception in Drosophila.* eLife 9:e60299
- Dallmann CJ et al. (2025). *Selective presynaptic inhibition of leg proprioception in behaving
  Drosophila.* Nature 647:445–453
- Lesser E et al. (2024). *Synaptic architecture of leg and wing premotor control networks in
  Drosophila.* Nature 631:369–377
- Phelps JS et al. (2021). *Reconstruction of motor control circuits in adult Drosophila using
  automated transmission electron microscopy.* Cell 184:759–774 (FANC)
- Marin EC et al. (2024). eLife 13, doi:10.7554/eLife.97766.1.sa3 (MANC)
- Dinges GF, Chockley AS, Bockemühl T, Ito K, Blanke A, Büschges A (2021). J. Comp. Neurol.
  529:905–925. doi:10.1002/cne.24987 (other agent's topic)

**Non-Drosophila hair plate literature (all second-hand, abstract-level only):**
- Newland PL, Watkins B, Emptage NJ, Nagayama T (1995). J. Exp. Biol. 198:2397–2404. PMID 7490573 (locust)
- Kuenzi F, Burrows M (1995). J. Exp. Biol. 198:1589–1601 (locust)
- Wong RK, Pearson KG (1976). J. Exp. Biol. 64:233–249. doi:10.1242/jeb.64.1.233. PMID 1270992 (cockroach)
- Pearson KG, Wong RKS, Fourtner CR (1976). J. Exp. Biol. 64:251–266. PMID 5571 (cockroach)
- Bräunig P, Hustert R (1985). J. Comp. Physiol. A 157:83–89 (locust)
- Okada J, Toh Y (2000). J. Comp. Physiol. A 186:849–857 (cockroach antenna)
- Wendler G (1972). Verh. Dtsch. Zool. Ges. 214:219 (stick insect posture)
- Pringle JWS (1938). *Proprioception in insects I.* (the original hair plate / CS work)
