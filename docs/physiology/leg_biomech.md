# Leg biomechanics: muscles, joints, twitch, gait, bodies, proprioceptors

Scope: what stands between a leg motor-neuron spike and a leg moving, and what the movement
should look like if it is walking. This extends `docs/physiology/leg_motor.md`, which covered
MN-type→muscle for the front leg, the turning biomechanics and the descending neurons. It does
not repeat them. Written 2026-09-21 for three builds, in order:

1. read all 373 leg MNs per 10 ms frame, grouped by leg and muscle, and ask whether the pattern
   is walking-shaped (§C says what "walking-shaped" means);
2. rebuild the effector from the muscles up, joint by joint (§A gives the muscle→joint map for
   all three legs, §B the muscle model, §D the body it drives);
3. give him proprioception from those legs (§E).

Marks, extending `leg_motor.md`'s: **(M)** measured in *Drosophila*; **(C)** measured in another
insect and imported, with the animal named; **(E)** an estimate from adjacent data, a modelling
prior and not a fact; **(D)** derived here, on 2026-09-21, from MaleCNS v1.0's own annotation and
connectivity tables — our inference from his wiring, not anybody's published result.

Two citation corrections to the brief that commissioned this, of the same kind `leg_motor.md`
opened with:

1. **Azevedo et al. 2024, *Nature* 631:360–368, is the FANC dataset paper**, "Connectomic
   reconstruction of a female *Drosophila* ventral nerve cord" (DOI 10.1038/s41586-024-07389-x).
   The fast/intermediate/slow recruitment atlas is **Azevedo et al. 2020, *eLife* 9:e56754**.
2. **Lesser et al. 2024, *Nature* 631:369–377 is FANC, not MANC** — "Synaptic architecture of
   leg and wing premotor control networks in *Drosophila*" (DOI 10.1038/s41586-024-07600-z),
   the *female* front leg. The MANC papers are Takemura et al. 2024 (*eLife* 13:RP97769, the
   dataset), Marin et al. 2024 (*eLife* 13:RP97766, the systematic names `MNfl##`/`MNml##`/
   `MNhl##`) and Cheong et al. (*eLife* 13:RP96084, DOI 10.7554/eLife.96084; reviewed preprint
   2024, version of record 2026, the leg MN muscle assignments).

---

## A. Muscle → joint → motion, all three legs

**in life.** Cheong et al. (*eLife* 13:RP96084): "The musculature of the *Drosophila* leg consists
of 13 muscle groups confined within the proximal leg segments, and another five in the thorax
that insert in the leg." Lesser et al. 2024 count **18 muscles / 69 MNs** in the front leg with
**2–8 motor units per muscle**; Azevedo et al. 2020 count "14 muscles innervated by just 53 motor
neurons" for the leg proper. All three are the same anatomy counted with different boundaries.
The underlying atlas is Miller A (1950), "The internal anatomy and histology
of the imago of *Drosophila melanogaster*", in Demerec M (ed.), *Biology of Drosophila*, Wiley,
pp. 420–534 (FlyBase FBrf0007735) — still the ground truth, and the model in §D carries Miller's
muscle numbers in its actuator names — and Soler et al.
2004, *Development* 131:6041–6051 (DOI 10.1242/dev.01527), with the muscle targets of individual
MNs established by X-ray holographic nanotomography plus driver lines in Azevedo et al. 2024.

Joints, proximal→distal, with their actuated degrees of freedom:

| Joint | DoF | Motions | Notes |
|---|---|---|---|
| **thorax–coxa (ThC)** | 3 in T1, 2 actuated in T2/T3 | promotion/remotion (protraction/retraction), abduction/adduction, long-axis rotation | Özdil et al. 2025 (arXiv:2509.06426) actuate 3 DoF for the foreleg only |
| **coxa–trochanter (CTr)** | 1 principal (pitch), with roll/yaw in the 3-DoF model | **levation / depression** of the whole distal leg | the body-support joint |
| **trochanter–femur (TrF)** | ~0, fused in the adult | femur "reduction"/rotation only, via the femur reductor | Soler et al. 2004; reduction lowers the foot toward the substrate |
| **femur–tibia (FTi)** | 1 (pitch) | flexion / extension | the one joint with measured MN forces (Azevedo et al. 2020) |
| **tibia–tarsus (TiTa)** | 1 (pitch) | levation / depression of the tarsus = release / grip | plus intra-tarsal flexion via the long tendon muscle |

Levation/depression at CTr and promotion/remotion at ThC are the two motions that carry the step;
FTi sets where the foot lands; TiTa decides whether thrust reaches the ground at all.

**in the table.** The male carries **373 leg MNs** — 133 front (68 L / 65 R), 116 mid (58/58), 124
hind (63/61) **(D)**. MANC has 392 (142 T1, 119 T2, 131 T3), so his set is 95 % of MANC's and the
old "699 leg MNs" worry from `leg_motor.md` §1 is closed: the filter is right now.

Of those 373, **45 cells in 19 types carry a bare systematic name and no muscle** — 24 mid-leg
cells (MNml29, MNml76–83) and 21 hind-leg cells (MNhl01, MNhl02, MNhl29, MNhl59, MNhl60, MNhl62,
MNhl64, MNhl65, MNhl87, MNhl88) **(D)**. That is **12 % of his leg motor output carrying weight
0** in `legs.py`, because `muscle_weight()` returns 0.0 on no substring match.

**The gap is inherited, and it is a naming gap, not an anatomical one.** MANC assigned muscles to
T2/T3 leg MNs by serial homology to T1, and Cheong et al. say exactly where that failed:

> "We could not identify serially repeating homologs (in T2 and T3) for the Tarsus levators and
> depressor MNs as well as the Tergopleural/Pleural promotor MNs."
>
> "For the tarsus targeting MNs, this was mainly due to their reconstruction state in T1 which
> made them hard to distinguish."

So the unnamed mid/hind types should be, mostly, **the tarsus levators and depressors and the
promotors of the middle and hind legs**. That is a prediction, and his own tables test it.

### A1. Resolving the unnamed types from his own wiring **(D)**

Three independent signals in MaleCNS v1.0, none of them a published muscle assignment:

1. **Serial-homology fields.** `mancSerial` **13036** contains the front leg's **`Ta levator MN`**,
   **`MNml81`** and **`MNhl65`** — a three-segment serial set that names itself. `mancSerial`
   **12196** contains **`MNml29`** and **`MNhl29`**, a mid/hind pair with no front partner.
2. **Premotor-input profile.** For every MN type, the distribution of its input synapses over
   presynaptic *cell types* (MANC interneuron types recur across T1/T2/T3, so the profiles are
   comparable between segments). Cosine similarity of the normalised profiles, computed over
   147,242 edges and 1,195,044 synapses onto the 373. This is the connectome version of Lesser
   et al.'s premotor-module clustering, run across segments.
3. **Exit nerve** and **Truman hemilineage**, both in the annotation table. Leg MNs come from
   **13 lineages** (Brierley, Rathore, VijayRaghavan & Williams 2012, *J Comp Neurol*
   520:1629–1649, DOI 10.1002/cne.23003), so a hemilineage is weak evidence on its own, but it is
   a good tie-breaker: the male's `MNml76`–`MNml83` are almost all **15B**, and `MNml29`/`MNhl29`
   are **24B.25B** — the two classical leg-MN lineages.

The exit nerves alone separate intrinsic from thoracic muscles cleanly **(D)**:

| Segment | Nerve | Carries |
|---|---|---|
| T1 | **ProLN** | intrinsic leg: tibia flexor/extensor, acc. tibia flexor, tarsus levator + depressor, ltm/ltm1/ltm2, femur reductor |
| T1 | **ProAN** | coxal: pleural remotor/abductor, sternal posterior rotator, sternal adductor, most trochanter flexors |
| T1 | **VProN** | thoracic: sternal anterior rotator, sternotrochanter, tergotrochanter |
| T1 | **DProN** | **tergopleural/pleural promotor only** (8 cells) |
| T2 | **MesoLN** | all 116, without exception |
| T3 | **MetaLN** | 116 of 124 |
| T3 | **AbN1** | 8 cells: `Tergotr. MN` (2), **MNhl01** (2), **MNhl02** (2), **MNhl62** (2) |

The T3 AbN1 group is the tell. The hind leg's thoracic muscles are reached by the first abdominal
nerve, and the three unnamed types that travel with the hind tergotrochanteral MN are therefore
thoracic-muscle MNs, not intrinsic leg MNs.

### A2. Assignment table for the 45 unnamed cells **(D)**

`cos` = cosine similarity of the premotor-type input profile to the named type given.
Confidence is mine.

| Type | n | Assigned muscle group | Joint | Action | Phase | Evidence | Conf. |
|---|---|---|---|---|---|---|---|
| **MNml29** | 2 | coxa **remotor** group (sternal posterior rotator / pleural remotor class) | ThC | remotion | **stance** | serial set 12196 with MNhl29; cos 0.78 to `Sternal posterior rotator MN` (T2), 0.59 to `Pleural remotor/abductor MN`; hemilineage 24B.25B | **high** |
| **MNhl29** | 2 | same, hind leg | ThC | remotion | **stance** | serial set 12196; cos 0.69 to `Sternal posterior rotator MN` (T3), 0.48 to `Pleural remotor/abductor MN` | **high** |
| **MNml81** | 2 | **tarsus levator** | TiTa | levation (release grip, lift tarsus) | **swing** | serial set **13036** with front `Ta levator MN` and MNhl65 | **high** |
| **MNhl65** | 3 | **tarsus levator** | TiTa | levation | **swing** | serial set **13036** | **high** |
| **MNml77** | 2 | tarsus levator | TiTa | levation | swing | cos 0.54 to MNml81, 0.45 to MNml83, 0.31 to front `Ta levator MN` | medium |
| **MNml83** | 1 | tarsus levator | TiTa | levation | swing | cos 0.78 to MNml81 | medium |
| **MNhl62** | 2 | coxa **promotor** / anterior-rotator class | ThC | promotion | **swing** | cos **0.79** to `Sternal anterior rotator MN` (T3), 0.59 to the T2 one; exits **AbN1** = thoracic muscle | **high** |
| **MNhl01** | 2 | trochanter **depressor** group (tergotrochanteral / sternotrochanteral) | CTr | depression | stance / escape | cos **0.92** to `Tergotr. MN` (T3), 0.66 to `Sternotrochanter MN`; exits AbN1 with them | medium-high |
| **MNhl02** | 2 | same | CTr | depression | stance / escape | cos 0.81 to `Tergotr. MN`, 0.81 to `Sternotrochanter MN`, 0.66 to `Tr extensor MN` | medium-high |
| **MNml76** | 1 | tarsus **depressor** / retro-depressor | TiTa | depression = **grip** | **stance** | cluster with MNml78/80/82 (cos 0.62–0.67); best front match `Ta depressor MN` | medium |
| **MNml78** | 6 | tarsus depressor | TiTa | depression | **stance** | cos 0.75 to MNml80, 0.40 to front `Ta depressor MN`; best within-T2 match `ltm MN` (0.23), the known tarsal synergist | medium |
| **MNml80** | 6 | tarsus depressor | TiTa | depression | **stance** | cos 0.75 to MNml78, 0.71 to MNml82 | medium |
| **MNml82** | 2 | tarsus depressor | TiTa | depression | **stance** | cos 0.71 to MNml80; but 7,122 input synapses/cell, an order above the front tarsal MNs — may be a distinct large tarsal or accessory-flexor unit | low-medium |
| **MNhl60** | 2 | tarsus depressor (E) | TiTa | depression | stance | weak (cos 0.33 to `Tergotr. MN`); assigned by elimination and by size (772 syn/cell) | **low** |
| **MNhl64** | 2 | tarsus depressor (E) | TiTa | depression | stance | weak (cos 0.41 to MNml79, 0.31 to front `Sternal adductor MN`) | **low** |
| **MNml79** | 2 | unresolved; best within-T2 match `ltm MN` (0.37); 6.0 % of its input is sensory, the highest of any T2 leg MN | — | — | — | **none** |
| **MNhl59** | 2 | anterior-rotator class (E); the **largest hind-leg MN** at 8,353 input synapses/cell; 4.2 % sensory, its 4th-largest single input is `SNta03` (tarsal sensory, 512 syn) | ThC (E) | promotion (E) | swing (E) | cos 0.36 to `Sternal anterior rotator MN` | **low** |
| **MNhl87** | 2 | unresolved | — | — | — | cos 0.88 to MNhl88 and **≤ 0.01 to every named leg MN type**; premotor input disjoint from the leg modules (top: IN03B056, DNg03, IN07B090, IN17A060); 13 % descending; hemilineage **06A**, unusual for a leg MN but not disqualifying — Brierley et al. 2012 find **13 lineages** contribute leg motoneurons (*J Comp Neurol* 520:1629–1649, DOI 10.1002/cne.23003) | **none** |
| **MNhl88** | 2 | unresolved | — | — | — | cos 0.88 to MNhl87; 18 % descending | **none** |

**Recommended action for the effector.** Weight MNml29/MNhl29 as remotors (**+1.0**, they are
stance propulsors and currently count for nothing); MNml81/83/77 and MNhl65 as tarsus levators;
MNml76/78/80/82 and MNhl60/64 as tarsus depressors; MNhl62 as a promotor (**−0.6**); MNhl01/02
with the trochanter depressors. Leave MNml79, MNhl59, MNhl87, MNhl88 at 0 and **label them
unresolved in code**, not silently zero — 8 cells. That converts 37 of the 45 dead cells into
signed drive, and it adds the T2/T3 **grip** and **swing-release** channels that the effector
currently does not have at all.

### A3. What differs between the three legs **(D, with Cheong et al. for the cause)**

- **Tarsus levator and depressor MNs are named only in T1.** 9 depressor + 5 levator cells. The
  mid and hind legs' equivalents are the numbered types above. Before this brief the model had
  **no tarsal grip term for four of the six legs**; §C shows grip is a stance-phase requirement,
  so thrust from T2/T3 was being computed without the muscle that transmits it.
- **`Tergopleural/Pleural promotor MN` exists only in T1** (8 cells, and the only users of
  **DProN**). It is a thoracic muscle. The mid and hind legs promote the coxa with the
  **sternal anterior rotator** (4 cells each) plus, for the hind leg, MNhl62. So all three legs
  do have a swing-phase ThC muscle; the front leg simply has a dedicated extra pool, consistent
  with the front leg's larger MN complement overall (MANC: 142 vs 119 and 131).
- **The hind leg is flexor-heavy, the mid leg levator-heavy.** `Ti flexor MN`: 10 / 10 / **17**
  cells (front/mid/hind); `Acc. tr flexor MN`: 6 / 4 / **12**; but `Tr flexor MN`: 15 / **14** / 6.
  The hind leg has half the trochanter flexors and twice the accessory ones.
- **`Tergotr. MN` is 8 cells in T1, 2 in T2, 2 in T3.** Only the T2 pair is the giant escape MN
  driving the tergotrochanteral jump muscle; T1 and T3 are serial homologues of it moving ordinary
  thoracic muscles. `leg_motor.md` §6 drops all `Tergotr.` cells from the walking readout — that
  is right for T2 and probably wrong for T1 and T3, which should be trochanter depressors.
- **The front leg is under-traced in this volume.** Input synapses per cell, same type, front vs
  mid vs hind: `Sternotrochanter MN` 6,519 / 10,205 / 12,208; `ltm MN` 200 / 773 / 327;
  `Acc. ti flexor MN` 748 / 1,102 / 336; largest `Ti flexor MN` cell 3,351 / 9,039 / 7,513 **(D)**.
  Any size-derived force must be normalised **within segment**, never across the whole set. This
  matches the note in project memory that the front legs are under-traced (L1 35 / R1 17 nerves).

### A4. The consequence for the size-to-force proxy **(D)** — likely the single biggest number here

`legs.py` computes `f = clip(S/S_ref, 0.2, 5.0) ** 2.5`, i.e. it clips the size span to 25× and
then raises it to 2.5, on the reasoning in `leg_motor.md` §6 that "the size span across that pool
is only ~3–5×". That premise is wrong in this volume. Within the **tibia flexor** pool — the one
pool where forces are measured — the input-synapse span per cell is:

| Segment | n | largest | smallest | span |
|---|---|---|---|---|
| front | 10 | 3,351 | 66 | **51×** |
| mid | 10 | 9,039 | 242 | **37×** |
| hind | 17 | 7,513 | 82 | **92×** |

Azevedo et al. 2020 give a fast:slow force ratio of **~100:1** (10 µN vs <0.1 µN per spike) across
that same pool. With a measured size span of ~50×, the exponent that reproduces 100× output is

> **alpha = ln(100) / ln(50) ≈ 1.18, call it 1.2 (E)** — not 2.5, and **with no clipping**, because
> the clip is removing exactly the spread that carries the class information.

Cross-check at the top end: FETi, the fast tibia extensor, has the most input synapses of any
front-leg MN in FANC (14,904 — reported in Azevedo et al. 2024's summary, not verified against a
figure). In our male the largest `Ti extensor MN` cells are 11,065 (front), 9,303 (mid), 13,706
(hind), and `Ti extensor MN` is 4 cells per leg, so the FETi/SETi pair plus two more — the
ordering survives. Lesser et al. 2024's 0.45 synapses/µm² (r = 0.94, p < 10⁻³³) is what licenses
reading synapse count as surface area as force class at all.


---

## B. Activation: from MN spikes to joint torque

Full working, digitised figure panels and every source note: `leg_biomech_parts/B_activation.md`.

**in life.** There is exactly **one** dataset that measures force per spike in a fly leg muscle:
Azevedo, Dickinson, Gurung, Venkatasubramanian, Mann & Tuthill 2020, *eLife* 9:e56754
(DOI 10.7554/eLife.56754). It is the **tibia flexor of the female front leg**, measured as force on
a calibrated probe at the tibia tip (lever arm **417 ± 7 µm**, probe **k = 0.2234 µN/µm**), not as
joint torque. Everything else in this section is either derived from it, imported, or absent.

### B1. Per-spike force and twitch kinetics **(M)**

| Class | Driver | Force / spike | Tip displacement / spike | Pool |
|---|---|---|---|---|
| fast | R81A07 | **~10 µN** | **50 µm** | 1 MN |
| intermediate | R22A08 | **~1 µN** | **5 µm** | 2–5 MNs |
| slow | R35C09 | **<0.1 µN**; fitted slope **0.013 µN/spike** | ~0.1 µm | 8–9 MNs |

One fast spike ≈ **one body weight** (fly ~10 µN, ~1 mg) ≈ **4.2 nN·m** of FTi flexion torque
**(E, arithmetic on their numbers)**. Whole-joint capacity: max ~**90–100 µN** at the tibia tip,
peak velocity 8 mm/s.

**The twitch.** The paper states one time constant — **half-maximal force in ~8.5 ms**, the same
for fast and intermediate. The rest is digitised from their fig. 4A/B **(D)**:

| | fast | intermediate |
|---|---|---|
| latency to movement onset | ~2 ms (+0.8 ms conduction) | ~2–4 ms |
| **time to peak** | **~21 ms** | **~21 ms** |
| half-decay from peak | ~17.5 ms | ~16 ms |
| decay tau | **~20 ms** | ~15–20 ms |
| back to baseline | ~70–80 ms | ~55–60 ms |

> **Fast and intermediate units have identical kinetics and differ only in gain.** That is the most
> useful modelling fact in the paper: one kernel, three gains.

Working kernel **(E)**: difference-of-exponentials, **τ_rise ≈ 7 ms, τ_decay ≈ 20 ms**, peak ~21 ms.
The **slow** unit has no resolvable twitch — force has **not peaked at 500 ms** and takes ~100 ms to
release. Model it as a first-order low-pass, **τ of order 200–500 ms (E)**, not a summed twitch train.

### B2. Summation, saturation, recruitment **(M)**

- **2 spikes give 1.6× the force of 1** — sublinear at n = 2 already.
- Force vs spike count **saturates at ~10 spikes** (the authors attribute it to fatigue).
- **There is no tetanic fusion frequency in the fly.** No frequency series was run. Anyone quoting
  one is extrapolating; from τ_decay ≈ 20 ms, fusion would land near **50–100 Hz (E)**.
- **Recruitment is by adding motor neurons, not by rate**, order slow → intermediate → fast, each
  step ~10× the force. Only **110 of 3,082** intermediate spikes were not preceded by a slow spike.
- Intrinsic properties, n = 15/11/14: R_in **150 / 300 / 700 MΩ**, V_rest **−68 / −60 / −48 mV**.
- **No spike-threshold current exists for fast and intermediate**: somatic injection cannot evoke
  their spikes, because the soma is electrically isolated from the spike-initiation zone. A
  point-neuron LIF is a poor model of the fly's fast MN, and that is worth knowing before reading
  its spike counts as force.

### B3. Firing rates **(M)**

| State | fast | intermediate | slow |
|---|---|---|---|
| at rest, fly still | 0 | 0 | **~30 Hz** (10–52) |
| averaged over spontaneous movement | ~1.5 Hz | ~9–10 Hz | ~62 Hz |
| driven (slow only, current injection) | — | — | 100–150 Hz |

**There is no published breakdown by standing / walking / grooming / flailing**, in this or any
other paper — checked against Gorko 2024, Dallmann 2025, Pratt 2024 and the Tuthill list. This is a
real gap and our sim cannot be validated against it.

### B4. Motor units per muscle **(M)**

The free Motor Neuron ID Appendix to Azevedo et al. 2024 (*Nature* 631:360–368) gives the per-muscle
table: **69 MNs in T1**, superseding the older "53". Tibia extensor is **2 MNs (FETi + SETi)**
against **15 flexor** (5 tibia flexor + 10 accessory). Most muscles carry **2–8 motor units**
(Lesser et al. 2024). Note the standing discrepancy: Azevedo 2020 says 14 muscles / 53 MNs per leg
(after Baek & Mann 2009); Lesser 2024 and Karashchuk 2025 say **18 muscles / ~69–70 MNs**. The
difference is body-wall muscles and accessory subdivisions, not a disagreement about anatomy.

### B5. Passive stiffness — measured, small, and unit-ambiguous

Wang, Babski, Perdomo, McMahan, Ramakrishnan, Biswas & Bhandawat 2025, "Passive muscle forces in
*Drosophila* are large but insufficient to support a fly's weight", **bioRxiv 2025.04.29.651225 /
PMC12324252 — a preprint**. They silenced the whole motor pool (`VGlut>GtACR1`) and read equilibrium
joint angle against a known gravitational torque.

- Passive torque is a **linear angular spring over ±40°** about rest **(M)** — no nonlinear element
  needed in the working range.
- Medians are printed for 4 DoFs × 3 leg pairs; T3 is stiffest, T1 ≈ 1.5 × T2; across-fly spread
  ~2-fold.
- **The units contradict themselves**: the table caption says `mN/°`, the discussion says `Nm/°`.
  Cross-checking against Azevedo's probe (equivalent rotational stiffness k·L² = **39 nN·m/rad**,
  against which one fast spike swung the tibia ~7°) favours the smaller reading: use
  **~2 × 10⁻⁸ N·m/rad for the T1 femur–tibia joint (E, from an ambiguous M)**, uncertain to ~50×.
- **No damping has been measured in any fly leg joint**, ever.
- The paper's own headline is the one to keep: **passive force is ~70× too weak to hold the fly up.**
  Standing must come from tonic slow-MN drive. A body that stands with its muscles silent is wrong.

### B6. What the simulators use instead **(E, all hand-tuned)**

None of NeuroMechFly v1/v2, flybody or FlyMimic uses a measured fly stiffness. flybody's leg
stiffness (1e-9 N·m/rad) is ~20× below even the low reading above; its methods describe fitting
**wing** damping only. FlyMimic ships τ_act ≈ **0.1 ms** — **~85× faster** than the measured 8.5 ms
half-rise — because its input is a continuous activation, not spikes. See §F.7.

### B7. Body mass and geometry **(M)**

flybody weighed real flies: head 0.15 / thorax 0.34 / abdomen 0.38 / **each leg 0.0162** / wing
0.008 mg, **total 0.983 mg**, body length **2.97 mm**. Per-segment leg masses do not exist.

---

## C. What "walking-shaped" means

Full tables, per-paper verification marks and the stick-insect import: `leg_biomech_parts/C_kinematics.md`.

**The one paragraph.** A fly walks between roughly **0 and 35 mm/s**, modal moving speed
**15–20 mm/s**. Speed is set almost entirely by **shortening stance**: τ_stance ∝ **v∥^−1.025**
(R² = 0.59; DeAngelis, Zavatone-Veth & Clark 2019, *eLife* 8:e46409). Swing stays near **31 ms** at
all speeds and step amplitude near **0.5 body length**. Step frequency therefore runs **~5 Hz slow
to ~16–20 Hz fast**, and duty factor slides from about **0.83 down to ~0.5**. Contralateral leg
pairs are antiphase (**Δφ = 0.5**) at *every* speed; ipsilateral neighbours drift from **Δφ ≈ 0.2 at
3 BL/s to ≈0.4–0.45 at ≥10 BL/s**, and ipsilateral fore–hind sits at **≈0.85, not 0**. There is
**no discrete tripod↔tetrapod switch**: the joint phase distribution is unimodal and what actually
changes with speed is the phase *variance*, which falls monotonically.

**Hard per-leg numbers to test a pattern against** (Isakov et al. 2016, *J Exp Biol* 219:1760–1771,
Table 1, WT, freely walking — the best duty-factor measurement in the literature and it is buried
in an amputation paper):

- duty factor δ = **[0.62, 0.70, 0.66, 0.65, 0.70, 0.68]** (L-front, L-mid, L-hind, R-front, R-mid,
  R-hind) — **midlegs highest, forelegs lowest**;
- swing-onset phase φ = **[0, 0.58, 0.17, 0.48, 0.13, 0.60]** cycles;
- stride frequency ω = **11.4 ± 1.8 strides/s**.

### C1. Joint angle ranges — one source has them

The usual citations do **not** publish per-joint degree ranges: NeuroMechFly sets every joint to
±180° and says so. The source that does is **Haustein, Blanke, Bockemühl & Büschges 2024**,
*Front Bioeng Biotechnol* 12:1357598 (DOI 10.3389/fbioe.2024.1357598) — 12 flies, 6-camera motion
capture at **400 Hz**, µCT joint axes taken from the real **condyles**, **2,250 steps** at
14.7 ± 4.0 mm/s. (It is routinely mis-cited as a Dallmann/Tuthill paper; it is the Büschges lab.)

ROM during forward walking **(M)**:

| Motion | Front T1 | Middle T2 | Hind T3 |
|---|---|---|---|
| coxa promotion / remotion | **40.9° ± 5.2°** | **26.5° ± 4.6°** | **18.6° ± 3.9°** |
| coxa adduction / abduction | 8.2° ± 2.7° | 7.6° ± 2.9° | 8.9° ± 3.0° |
| trochanter flexion / extension (CxTr-yaw) | **91.2° ± 9.5°** | **22.5° ± 3.4°** | **56.3° ± 9.0°** |
| tibia flexion / extension (FeTi-yaw) | **96.6° ± 7.7°** | **21.5° ± 5.4°** | **84.1° ± 9.9°** |

The paper prints **40.87° ± 5.21°** for two different front-leg DoFs in two separate sentences —
probably a copy-paste error, flagged and not silently corrected. Model joint limits per leg and
joint are in Table 1 of the same paper and reproduced in the part file.

**The middle leg barely moves its distal joints** — 22° of trochanter and 21° of tibia against the
front leg's 91° and 97°. It walks almost entirely from the thorax–coxa joint.

### C2. Step-phase signs — and why a global sign vector is wrong

Also Haustein et al. 2024, measured **(M)**:

- promotion in **swing**, remotion in **stance**, in all three leg pairs;
- **front legs extend during swing and flex during stance**;
- **hind legs do the opposite — flex during swing, extend during stance**;
- middle legs are idiosyncratic: trochanter flexes in swing / extends in stance, but tibia flexion
  runs through nearly the whole swing *and* the first half of stance.

The classic insect prior (Rosenbaum, Wosnitza, Büschges & Gruhn 2010, *J Neurophysiol* 104:1681,
`[stick insect]`, verified verbatim: depressor 93 ms **before** touchdown, flexor 9 ms after,
retractor 35 ms after; levator / extensor / protractor 100 / 67 / 37 ms before liftoff, and
**backward walking reverses only the coxal pair**) therefore **contradicts the measured fly
kinematics for two of three leg pairs**. Use the stick insect only where no fly measurement exists,
and port its latencies as cycle fractions — a 93 ms lead is longer than an entire fly swing.

**There is no phase-resolved EMG or muscle-imaging map of the *Drosophila* step cycle.** Azevedo
2020 explicitly does not break firing down by swing vs stance. Özdil et al. 2025 give *predicted*
activations from static optimisation **(E)**: pleural remotor/abductor active at stance onset,
promotors elevated at the stance→swing transition, trochanter flexor and extensor in antiphase
during locomotion (co-active in grooming).

### C3. Turning

DeAngelis et al. 2019, at forward speeds 15–20 mm/s to decouple speed from yaw **(M)**:

- inside mid- and hind-limbs **lengthen stance, shorten swing**; the outside legs do the reverse;
- **step length** increases on the outside limbs, decreases on the inside mid/hind, and is **not
  significantly modulated on the inside foreleg**;
- instead the **inside foreleg rotates its stance direction by up to ~45°** — that is where the
  path-length differential comes from;
- net stepping-frequency modulation at the highest yaw rates is only **~25 %**;
- turns are **phase-locked** to the limb cycle (p < 10⁻⁵ for all limbs).

Envelope: |yaw| up to **~450 °/s** free walking, saccade cadence **250 ± 110 ms** (Katsov, Freifeld,
Horowitz, Kuehn & Clandinin 2017, *eLife* 6:e26410 — note the author list; the "Katsov, Cohen,
Shofer" form in circulation is wrong).

Isakov et al. 2016's fitted neuromechanical model adds the piece `leg_motor.md` §6 did not use:
sweeping force one leg at a time, **the middle legs need the smallest force change to produce a
given turn-bias change**, then hind, then front. Per unit force the yaw leverage is **T2 > T3 > T1**.
Force redistribution is necessary *and* sufficient to reproduce the 3-day recovery (<1 % mean
discrepancy) while gait itself never recovers. The paper explicitly declines the cockroach
assignment (Mu & Ritzmann 2005: front legs steer, hind legs propel) as insufficient in the fly.

**Newest result worth knowing.** Ispizua et al. 2026 (bioRxiv 10.64898/2026.05.03.722293; 53 flies,
7 cameras at 800 fps, 50 keypoints, 2,213 bouts): flies do **grounded running at all speeds** —
centre-of-mass height and forward speed peak in phase, no floating phase, no discrete gait
transitions. The strongest version yet of the gait-continuum argument.

---

## D. Rigged body models

Full DoF breakdowns, XML-level actuator and sensor lists, repo licences and the conversion maths:
`leg_biomech_parts/D_body_models.md`, plus `flybody.md` and `flymimic_paper_and_repo.md`.

**Three usable bodies, not interchangeable.**

| | NeuroMechFly v2 / flygym | flybody | FlyMimic |
|---|---|---|---|
| Paper | Wang-Chen et al. 2024, *Nat Methods* 21:2353–2362, DOI 10.1038/s41592-024-02497-y | Vaxenburg et al. 2025, *Nature*, DOI 10.1038/s41586-025-09029-4 | Özdil, Ning, Phelps, Wang-Chen, Elisha, Blanke, Ijspeert & Ramdya, ICLR 2026, arXiv:2509.06426 (**no journal DOI**) |
| Repo / licence | `NeLy-EPFL/flygym`, **Apache-2.0** | `TuragaLab/flybody`, **Apache-2.0** | `gizemozd/FlyMimic`, **Apache-2.0**, and **vendored inside flygym 2.1.0** |
| Engine | MuJoCo | MuJoCo | MuJoCo (converted from OpenSim by MyoConverter) |
| DoFs | 70 bodies, **87 hinges** (66 leg = 11/leg, 3 head, 18 antennal), +6 free = 93; **42 actuated, 7 per leg** | compiled **nq=109 nv=108 nu=78 njnt=103**; **8 leg actuators per leg**; wings | **7 DoF, left front leg only**, thorax tethered |
| Actuation | **joint position servos** (kp 45, forcerange 65) | **joint position servos** | **15 genuine Hill-type muscles** (`dyntype/gaintype/biastype=muscle`) on spatial tendons, `ctrlrange 0.0001–1` |
| Adhesion | yes, controllable per leg per step | yes | **no** |
| Sensors | joint angles, joint velocities, contact forces; **no "proprioception" observation exists** — the repo's only such reference is a comment, `sim.get_joint_angles(fly.name) # proprioception` | 15 sensors; **no `jointpos`/`jointvel` sensors in the MJCF at all** | **no `<sensor>` block at all**; read `qpos`/`qvel`/`actuator_force` |
| 10 ms frames | fine (0.1 ms physics, step 100×) | fine | fine (τ_act ≈ 0.1 ms, fully resolvable) |

**None of the three models a campaniform sensillum, a chordotonal organ or a hair plate.** Confirmed
by grep across all three repos.

**FlyMimic is the answer to "does a Drosophila Hill-type leg muscle model exist".** Its 15 actuator
names are our muscle groups verbatim — `LFC_tergopleural_promotor_a/b`,
`LFC_pleural_remotor_and_abductor`, `LFC_sternal_anterior_rotator`, `LFC_sternal_posterior_rotator`,
`LFC_sternal_adductor`, `LFF_trochanter_flexor_a/b`, `LFF_accesory_trochanter_flexor` [sic],
`LFF_trochanter_extensor`, `LFF_sterno-tergo-trochanter_extensor_a/b`, `LFTibia_flex_93434`,
`LFTibia_extensor_93932` — with site names carrying **Miller's** muscle numbers. Fitted F_max from
the shipped MJCF: tibia flexor **~68 µN**, tibia extensor **~304 µN**. Parameters came from PCSA ×
a specific tension of **28 mN/mm²** (between the fly's jump muscle at 37 and its indirect flight
muscle at 9) and were optimised by NSGA-II against measured walking and grooming kinematics. It has
**no spike-to-force stage** — activation is a continuous [0,1] they call MN activity — and the
authors state outright that no *Drosophila* force–length or force–velocity curves exist, so they use
OpenSim's mammalian defaults. Middle and hind legs are annotated (7 and 8 MTUs) but **not optimised**.

**What FlyMimic lacks:** femur reductor, tarsus levator, tarsus depressor, long tendon muscle; right
front leg pinned by `<equality>`; no adhesion; no ground contact. **94 of the male's 133 front-leg
MNs (71 %) map onto one of its actuators by name; the other 39 (29 %) are exactly the TrF and TiTa
muscles it does not model** (§F.4a).

**Precedent.** arXiv:2602.17997 (Jin, Zhu, Zhang & Sui) drives flybody from FlyWire, but through a
**learned decoder** with no motor-neuron identity. Pugliese, Chou, Abe, Turcu, Lancaster, Tuthill &
Brunton (bioRxiv 10.1101/2025.09.12.675944) build a MANC front-leg firing-rate model, find a
3-neuron CPG, and **cannot produce tripod coordination**, concluding that "proprioceptive feedback,
biomechanical coupling, or other neural pathways may be necessary" — while warning against learning
the connectome↔body interface with an ANN. That is an argument for the anatomical muscle mapping.

### D1. Recommendation

**(i) Visualising attempted movement: NeuroMechFly v2 / flygym.** The only whole six-legged walking
fly with adhesion, active maintenance, a clean state getter and a permissive licence. Map antagonist
difference → joint position setpoint; "attempted" is exactly what a finite-force position servo
produces when the world pushes back.

**(ii) Physics behind proprioception: NeuroMechFly v2 as the workhorse, FlyMimic as the validity
check.** Proprioception needs joint angle, velocity and load on all six legs during locomotion, and
only v2 supplies that. But the per-muscle → per-joint collapse is a real cost, and the way to pay it
honestly is to run FlyMimic's left front leg **in parallel on the unreduced per-muscle vector** and
compare the seven joint angles. FlyMimic even ships `best_combined_cvt3_torque.xml`, the same leg
with 7 plain `<motor>` actuators, so the muscle-vs-joint comparison is already built.

Both Apache-2.0, both MuJoCo, and flygym 2.1.0 vendors FlyMimic — **one dependency**. That is the
deciding practical fact.

**What the collapse destroys, and must be declared:** co-contraction vanishes entirely (two
antagonists at full drive is indistinguishable from silence), joint stiffness is pinned at `kp`
forever, multi-joint muscles like the long tendon muscle must be assigned to one joint by fiat, and
force–length / force–velocity are gone. The weakest point of the cross-check is the TiTa joint — the
one our tarsal and LTM pools act on — because FlyMimic does not model it.

---

## E. Proprioceptors per leg

Full encoding rules, tuning curves and per-group tables: `leg_biomech_parts/E_proprioceptors.md`,
`hair_plates_bristles_tarsal_sensilla.md`, `proprioceptor_encoder_models.md`,
`manc_leg_sensory_annotation.md`. The male's own inventory: `E_table_male.md`.

**in life**, per front leg: **~225 proprioceptors** inside **~630–650 mechanosensory neurons**.

| Organ | n per leg | Encodes | Physical input | Source |
|---|---|---|---|---|
| **FeCO** | **152** cell bodies (X-ray; 135 by earlier confocal count) | angle, movement direction, vibration | FTi angle θ, dθ/dt, µm vibration | Mamiya, Sustar, Siwanowicz, Qi, Lu, Tuthill et al. 2023, *Neuron* 111, DOI 10.1016/j.neuron.2023.07.009; Mamiya, Gurung & Tuthill 2018, *Neuron* 100:636–650, DOI 10.1016/j.neuron.2018.09.009 |
| — **claw** | 20 by driver line | **tonic angle**; extension-tuned active 90–180°, flexion-tuned 90–18°, **silent near 90°**; hysteretic, non-adapting | θ | Mamiya 2018 |
| — **hook** | 3 (flexion) + extension type | **directional movement**, DSI 0.811, **velocity-flat 100–800 °/s**, fast-adapting | sign(dθ/dt) | Mamiya 2018; Chen et al. 2021, *Curr Biol* 31:5163–5175 |
| — **club** | 30 by driver line | bidirectional movement (DSI 0.117), velocity peak 400 °/s; **vibration 100–2000 Hz**, peak 400 Hz @ 0.9 µm and 800 Hz @ 0.054 µm | substrate vibration | Mamiya 2018 |
| **Campaniform sensilla** | **42** front and middle, **41** rear, in **11 named groups**; **none on the coxa** | cuticular strain → load, dF/dt-dominant | contact force and its derivative | Dinges, Chockley, Bockemühl, Ito, Blanke & Büschges 2021, *J Comp Neurol* 529:905–925, DOI 10.1002/cne.24987 |
| **Hair plates** | **37 neurons in 8 plates** (front) | **joint position at the limits of range** | θ near end-stop | see below |
| **Bristles** | 400+ per front leg | touch; **mostly no synapses onto MNs** | contact | Tuthill & Wilson 2016 |

The three driver-line counts (20 + 30 + 3 = 53) are a **driver-line count, not a subclass census** —
Mamiya 2018 says the lines label "less than half" the organ. There is **no published breakdown of
all 152 by subtype**. Drosophila **has** a tibial chordotonal organ, **has no** tarsal chordotonal
organ and **has no** subgenual organ. Tuthill & Wilson 2016's "~1,200 campaniform sensilla" is a
***Calliphora*** number; the verified fly figure is **>680 whole-body**.

### E1. Four findings that change the encoder, not just its parameters

1. **Hook output is not a function of joint kinematics.** Dallmann et al. 2025, *Nature* 647:445–453:
   hook axons are **presynaptically suppressed during walking and grooming but not passive
   movement**; claw and club are not. 83 % of that GABAergic input comes from local **9A**
   interneurons, one "chief" 9A cell supplying 57 % of it, and the gate is **feedforward from
   descending neurons**, not sensory feedback. Every tuning curve in this literature was measured
   passively. Compute hook from dθ/dt alone and you are wrong in exactly the regime we care about.
2. **Club is not a proprioceptor in the motor sense.** Lee et al. 2025, *Nat Commun*,
   DOI 10.1038/s41467-025-59302-3: club forms **zero direct synapses onto leg motor neurons** and
   sends >50 % of its output intersegmentally. Drive it from **ground contact**, not dθ/dt, and do
   not route it into posture control.
3. **Claw needs one threshold, not twenty tuning curves.** Mamiya 2023's goniotopic map is linear in
   cell position along the femur and falls out of a graded dendritic strain gradient plus a
   **uniform** threshold.
4. **The FeCO has no efferent innervation** (Mamiya 2023 looked and found none). There is **no
   gamma-motor analogue**: peripheral gain cannot be set centrally. Presynaptic inhibition in the
   cord is a different, real mechanism.

**The reflex sign rule** (Lee et al. 2025), the most directly implementable result in the field:
**flexion-sensing afferents excite tibia extensors and inhibit flexors; extension-sensing afferents
do the reverse.** Negative feedback, with premotor neurons largely dedicated one-subtype-to-one-
motor-module. Compare Agrawal, Dickinson, Sustar, Gurung, Shepherd, Truman & Tuthill 2020,
*eLife* 9:e60299 (13Bα → resistance reflex; 10Bα halts walking), already in `leg_motor.md` §3.

**Hair plates are the cheapest thing to build.** One rectifier per plate, tonic, no velocity term;
each drives movement *away* from the limit it detects, with **17 % of output straight onto motor
neurons** — a genuine short reflex arc. `CxHP8` on the coxa detects the limit of anterior leg
movement, excites posterior movement and inhibits anterior; silencing it alters the swing-to-stance
transition in walking (*Nat Commun*, published 2026-02-12; preprint bioRxiv 2025.05.15.654260; data
at Dryad doi:10.5061/dryad.fxpnvx153). **The threshold angle is unpublished**, so it is a fitted
parameter **(E)**.

### E2. The negative result to state plainly

**There are no published spike rates for any adult *Drosophila* leg proprioceptor.** All of the
physiology is calcium imaging at ~8 Hz. Anyone quoting spikes/s for claw, hook or club is importing
from locust or stick insect. The only measured latency in the whole leg-mechanosensory literature is
**3 ms over ~850 µm (0.28 m/s)** for a femur bristle; the processing budget between successive steps
is **< 30 ms** (Agrawal et al. 2020).

### E3. The annotation labels **(D)** — and they are counter-intuitive

Marin et al. 2024, *eLife* 13:RP97766: **`pp` = proprioceptive**, **`ta` = tactile**,
**`ch` = chemosensory — not chordotonal**, `xx` = unknown. There is no `SNhp` and no `SNcs` code;
sensillum identity lives in the `subclass` field, and FeCO subtypes are separable via `synonyms`.
**Anything that filtered on "ch = chordotonal" has been reading the taste neurons.**

The male's leg nerves carry **3,976 sensory neurons** — ProLN 992, MesoLN 1,402, MetaLN 1,521, plus
61 in DProN/VProN/ProAN — of which **570 are `SNpp`**. He carries the named FeCO and hair-plate types
on all three leg pairs:

| Type | Class | ProLN | MesoLN | MetaLN |
|---|---|---|---|---|
| `SNpp50` / `SNpp51` | FeCO **claw** | 1 / 4 | 26 / 15 | 35 / 13 |
| `SNpp39` / `SNpp41` | FeCO **hook** | 8 / 3 | 17 / 11 | 14 / 8 |
| `SNpp45` / `SNpp52` | **hair plate** (52 may be campaniform) | 1 / 0 | 23 / 21 | 17 / 16 |
| `SNpp53` | **trochanter campaniform** | 4 | 4 | 4 |

`LgLG` (669 cells) is **leg gustatory** — the only leg types carrying `receptorType`
(173 `putative_ppk23`, 161 `putative_ppk25`, 130 `putative_IR52b`). Not proprioception.

**So step 3 needs no stand-in population** — but note two limits. There is **no club type named**,
so vibration would be a declared stand-in; and **the front leg is not usable**, carrying 1 `SNpp50`
against the middle leg's 26. Build the loop on T2/T3 and say so. The apparent shortfall against
152 FeCO cells per leg is a reconstruction artefact, not biology: leg sensory axons degrade during
dissection, FANC has 80 T1L axons (~50 % complete) and MANC v1.2.1 had 22 (Lee et al. 2025).

### E4. What to implement, in order of confidence

1. **hair plates → joint limits** (rectifier on θ near end-stop; threshold fitted);
2. **claw → joint angle** (one shared threshold + a proximal–distal gradient; sensed extension →
   commanded flexion);
3. **hook → movement direction, gated by a behavioural-state flag**, flexion and extension as
   separate channels (their downstream connectivity barely overlaps);
4. **campaniform → load** (rectified, dF/dt-dominant; distal groups from ground contact, proximal
   groups from joint torque). Right physics, **wrong species for every parameter** — the model to
   use is Szczecinski et al. 2021, *Bioinspir Biomim* 16:065001, `[cockroach / stick insect]`;
5. **club → vibration** from substrate contact. If the rigid-body sim has no sub-micron vibration
   content, say so rather than faking it from joint velocity;
6. **bristles → touch**, modelled separately from hair plates.

---

## F. What this changes in the build

Three builds were named. Here is what §§A–E say about each, and what should *not* be done.

### F.1 The probe (read 373 MNs per 10 ms frame and ask "is this walking?")

**The frame is the wrong length for an instantaneous readout, and right for a kernel.** A single
fast or intermediate tibia-flexor twitch peaks at **~21 ms** and decays with **tau ≈ 20 ms**,
back to baseline at 70–80 ms (Azevedo et al. 2020, digitised). At 10 ms frames a spike's force is
spread over the next **5–8 frames**. So the probe must convolve, not threshold: force in frame *t*
is a kernel over spikes in frames *t−8…t*, and the existing `1 − exp(−Δ/k)` per-frame saturation
is not that. It is also the wrong shape — measured summation is **2 spikes = 1.6 × 1 spike** and
saturation at **~10 spikes**, which an exponential-saturation curve fits only by accident.

**The slow units are a separate regime, not the bottom of the same one.** The slow tibia flexor
has no resolvable twitch: force is still rising at 500 ms and release takes ~100 ms. It fires
**~30 Hz at rest** (10–52 Hz) while fast and intermediate are silent, i.e. **3 spikes per 10 ms
frame from a single cell, standing still**. Baseline subtraction stays non-optional, and the slow
pool wants a tau of order 200–500 ms **(E)**, not a twitch kernel.

**Group by (leg × joint × antagonist pair), not by cell.** §A gives the map for all six legs.
The six grouped drives per leg are: ThC promotion vs remotion, CTr levation vs depression, TrF
reduction, FTi flexion vs extension, TiTa levation vs depression. That is the readout the probe
should print, per leg, per frame, against §C's phase expectations.

**Fix the 45 dead cells first.** §A2 assigns 37 of them. Until then, the mid and hind legs have
**no tarsal grip channel and no promotor channel in the readout at all**, and the probe would be
asking whether a pattern is walking-shaped while blind to the muscle that puts the foot down.

### F.2 The muscle-up effector

Replace `a_i = f_i * (1 - exp(-delta/k))` with, per MN *i*:

```
f_i      = f0 * (S_i / S_ref,segment) ** alpha      # alpha ~= 1.2 (E), NO clipping,
                                                    # S normalised WITHIN segment (A3, A4)
force(t) = f_i * sum_s K(t - t_s)                   # K: tau_rise ~ 7 ms, tau_decay ~ 20 ms,
                                                    # peak ~21 ms  (Azevedo 2020, digitised)
                                                    # slow class: K -> single exp, tau 200-500 ms (E)
```

with, where class labels exist, **10 / 1 / 0.1 µN per spike** for fast / intermediate / slow
directly, skipping the proxy. Three things that must not be done:

- **Do not clip the size span.** The current `clip(S/S_ref, 0.2, 5.0)` removes the very spread
  that carries the force class: within the tibia flexor pool the measured span in this volume is
  **37–92×**, and the measured force ratio across it is **100:1**.
- **Do not normalise size across segments.** The front leg is under-traced by 1.5–4× for the same
  muscle (§A3); a global `S_ref` makes every front-leg muscle weak for a tracing reason.
- **Do not fit anything to the behaviour.** The exponent falls out of two measured numbers
  (span ≈ 50×, ratio ≈ 100×); if it stops giving good walking, that is a result, not a knob.

Joint torque, not a body scalar: `torque_joint = sum over muscles of (sign × force × moment arm)`.
Moment arms exist for the front leg in FlyMimic (§D.5) and nowhere else; for T2/T3 they are **(E)**.

### F.3 Proprioception

§E's table says this can be built on real labelled cells: the male carries FeCO **claw**
(`SNpp50`, `SNpp51`), **hook** (`SNpp39`, `SNpp41`), **hair plate** (`SNpp45`, `SNpp52`) and
**trochanter campaniform** (`SNpp53`) afferents on all three leg pairs, with published tuning and
published downstream reflexes. Two constraints:

- **The front legs are not usable for this.** 1 `SNpp50` cell versus the middle leg's 26. Build
  the loop on T2/T3 and say so.
- **`SNch` is chemosensory, not chordotonal** (Marin et al. 2024). Anything that filtered on
  "ch = chordotonal" has been reading the taste neurons.

### F.4 Body

§D: **NeuroMechFly v2 / flygym** for the walking body and the proprioceptive physics;
**FlyMimic** (Özdil et al., ICLR 2026; arXiv:2509.06426; Apache-2.0, vendored inside flygym 2.1.0)
for the left front leg driven by the *unreduced* per-muscle vector, as the measurement of what the
per-muscle → per-joint collapse costs. Both Apache-2.0, both MuJoCo, one dependency.

Label the collapse as what it is. `docs/LANDSCAPE.md` takes flyverse-core's instrument-labelling
discipline as the first thing worth stealing: a stand-in declares in code whether it supplies a
missing **input** or replaces a missing **computation**. The antagonist-pair → position-setpoint
map in §D.7.2 replaces a *computation* (the muscle mechanics), and the T2/T3 moment arms supply a
missing *input*. Both should carry the flag.

#### F.4a The front-leg map onto FlyMimic's 15 actuators **(D)**

Our front-leg MN types against FlyMimic's actuator names (§D.5). This is the whole reason the
per-muscle drive is worth building: for the front leg it is not a mapping, it is an identity.

| Our MN type (n cells) | FlyMimic actuator(s) |
|---|---|
| `Tergopleural/Pleural promotor MN` (8) | `LFC_tergopleural_promotor_a`, `_b`, `LFC_pleural_promotor` |
| `Pleural remotor/abductor MN` (4) | `LFC_pleural_remotor_and_abductor` |
| `Sternal anterior rotator MN` (4) | `LFC_sternal_anterior_rotator` |
| `Sternal posterior rotator MN` (6) | `LFC_sternal_posterior_rotator` |
| `Sternal adductor MN` (2) | `LFC_sternal_adductor` |
| `Tr flexor MN` (15) | `LFF_trochanter_flexor_a`, `_b` |
| `Acc. tr flexor MN` (6) | `LFF_accesory_trochanter_flexor` |
| `Tr extensor MN` (4) | `LFF_trochanter_extensor` |
| `Sternotrochanter MN` (4) + `Tergotr. MN` (8) | `LFF_sterno-tergo-trochanter_extensor_a`, `_b` |
| `Ti flexor MN` (10) + `Acc. ti flexor MN` (19) | `LFTibia_flex_93434` |
| `Ti extensor MN` (4) | `LFTibia_extensor_93932` |
| **`Fe reductor MN` (10), `Ta depressor MN` (9), `Ta levator MN` (5), `ltm MN` (8), `ltm1-tibia MN` (3), `ltm2-femur MN` (4)** | **none** |

**94 of the male's 133 front-leg MNs (71 %) map onto a Hill-type actuator by name. The remaining
39 (29 %) are the TrF and TiTa muscles FlyMimic does not model** — the femur reductor, the whole
tarsal apparatus and the long tendon muscle. So the cross-check in §D.8 is strong for ThC, CTr and
FTi, and absent for the two joints that decide grip. Say that wherever the comparison is quoted.

### F.5 One correction to `leg_motor.md` §6's segment weights

`leg_motor.md` §6 sets `μ_T1 = −0.5, μ_T2 = +1.0, μ_T3 = +1.0` on the argument that front legs
brake. Isakov et al. 2016's neuromechanical model, fitted to the amputation-recovery trajectory to
within 1 % mean discrepancy, gives a per-leg sensitivity that the brief did not use: sweeping the
force in one leg at a time, **the middle legs need the smallest force change to produce a given
turn-bias change, then the hind legs, then the front legs, which need the largest.** Per unit
force the yaw leverage is **T2 > T3 > T1**, and the required right/left force ratio over recovery
sits in **0.7–1.0**.

So the magnitudes should not be `μ_T2 = μ_T3`. A sourced ordering is `|μ_T2| > |μ_T3| > |μ_T1|`
**(M, via a fitted model)**. The paper also explicitly declines the cockroach assignment
(Mu & Ritzmann 2005: front legs steer, hind legs propel) as insufficient in the fly — which is a
caution against the sign of `μ_T1`, not a confirmation of it. Keep `μ_T1` negative if you like,
but mark it **(E)** as before and note that the one fitted fly model does not require it.

### F.6 The muscle sign vector cannot be global — it flips between T1 and T3

`legs.py`'s `MUSCLE_W` is one signed weight per muscle, applied to all six legs. Haustein, Blanke,
Bockemühl & Büschges 2024 (*Front Bioeng Biotechnol* 12:1357598, DOI 10.3389/fbioe.2024.1357598;
12 flies, 400 Hz motion capture, 2,250 steps at 14.7 ± 4.0 mm/s) measured the step-phase signs
directly, and they are not the same in the three leg pairs **(M)**:

- promotion in **swing**, remotion in **stance**, in all three pairs — the ThC weights are safe;
- **front legs extend during swing and flex during stance**;
- **hind legs do the opposite — flex during swing, extend during stance**;
- middle legs are idiosyncratic: the trochanter flexes in swing and extends in stance, but tibia
  flexion runs through nearly the whole swing *and* the first half of stance, with extension only
  in the second half.

So `Ti flexor` is a **stance** muscle in T1 and a **swing** muscle in T3, and `Ti extensor` the
reverse. A single `w = +0.5` for the tibia flexor across all six legs has the sign **wrong for the
hind legs**, which are also the pair with the most tibia flexor motor neurons in this male (17,
against 10 front and 10 mid — §A3). `MUSCLE_W` has to become `MUSCLE_W[segment]`, at minimum for
the FTi and CTr pairs.

Two more numbers worth carrying into the effector from the same paper **(M)**. Range of motion
during forward walking, front / middle / hind:

- coxa promotion–remotion **40.9° / 26.5° / 18.6°**
- trochanter flexion–extension (CxTr-yaw) **91.2° / 22.5° / 56.3°**
- tibia flexion–extension (FeTi-yaw) **96.6° / 21.5° / 84.1°**

**The middle leg barely moves its distal joints** — 22° of trochanter and 21° of tibia against the
front leg's 91° and 97°. It walks almost entirely from the thorax–coxa joint. Any per-joint
effector that gives all three legs the same gain will over-drive the middle leg's knee by a factor
of four.

### F.7 Two traps in the body model

**Do not inherit FlyMimic's activation dynamics.** Its MJCF sets `dynprm` to τ_act ≈ 0.1 ms and
τ_deact ≈ 0.4 ms. The measured half-rise of a *Drosophila* leg-muscle twitch is **8.5 ms**
(Azevedo et al. 2020), with peak at ~21 ms — the shipped value is **~85× too fast**. It is a
fitting convenience, not a measurement, and it exists because their input is a continuous
activation, not a spike train. Our spike→force stage (§F.2) *is* the missing physiology; put the
20 ms kernel in front of the actuator and leave the actuator's own filter effectively transparent.

**Passive stiffness exists and it is small.** Wang, Babski, Perdomo, McMahan, Ramakrishnan,
Biswas & Bhandawat 2025 (bioRxiv 2025.04.29.651225; PMC12324252; **a preprint**) silenced the whole
motor pool and measured a **linear angular spring over ±40°** about the rest angle, for four DoFs ×
three leg pairs. Their own conclusion is the one to hold onto: **passive muscle force is large but
not enough to hold the fly up** — of order 70× short. So a body run with the muscles silent must
collapse, and if it stands up instead, the body's joint stiffness is doing work the fly's isn't.
Note the units in that paper are self-contradictory (`mN/°` in the table caption, `Nm/°` in the
discussion); §B derives ~2 × 10⁻⁸ N·m/rad for the T1 femur–tibia joint by cross-check against
Azevedo's probe stiffness, and marks it uncertain to a factor of ~50. **No damping has been
measured in any fly leg joint.**

---

## Appendix: the full working

Every section above is a distillation. The complete research, with verbatim passages, digitised
figure panels, per-paper verification marks and the tables that did not fit, is in
`docs/physiology/leg_biomech_parts/` (B_activation, C_kinematics, D_body_models, E_proprioceptors,
E_table_male, F_build, plus flybody, flymimic_paper_and_repo, hair_plates_bristles_tarsal_sensilla,
manc_leg_sensory_annotation, proprioceptor_encoder_models, connectome_driven_sim_and_mn_muscle_lit).
Per-paper source notes, one file per paper actually read, are in `docs/research/sources/`.
