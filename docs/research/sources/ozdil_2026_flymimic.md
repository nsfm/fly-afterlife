# Özdil et al. 2026 — FlyMimic / Drosophila musculoskeletal leg model

**VERIFIED** (arXiv abs page fetched, repo READMEs fetched, MJCF downloaded and parsed 2026-09-21).

> Özdil PG, Ning C, Phelps JS, Wang-Chen S, Elisha G, Blanke A, Ijspeert A, Ramdya P.
> "Musculoskeletal simulation of limb movement biomechanics in *Drosophila melanogaster*."
> **ICLR 2026** (The Fourteenth International Conference on Learning Representations).
> **arXiv:2509.06426** (v1 2025-09-08, v2 2025-09-11).

Repos:
- https://github.com/gizemozd/FlyMimic (Apache-2.0) — MuJoCo models converted from OpenSim,
  mocap, dm_control tasks, PPO imitation learning.
- https://github.com/gizemozd/neuromechfly-muscles — referenced by FlyMimic's README as the home
  of "the original muscle model development and parameter optimization in OpenSim".
  **NOTE: raw README fetch returned 404** — repo may be private/renamed. Unverified.
- Integrated into **FlyGym 2.x** as `flygym.compose.MusculoskeletalFly` /
  `MusculoskeletalWorld` / `build_musculoskeletal_simulation`, demo module
  `flygym_demo.muscle_imitation`. Tutorial: `docs/tutorials/6_muscle_imitation.md`.

## Abstract (verbatim excerpt)

> "Despite the availability of near-complete reconstructions of the *Drosophila melanogaster*
> central nervous system, musculature, and exoskeleton, anatomically and physically grounded
> models of fly leg muscles are still missing. These models provide an indispensable bridge
> between motor neuron activity and joint movements. Here, we introduce the first 3D,
> data-driven musculoskeletal model of *Drosophila* legs, implemented in both OpenSim and
> MuJoCo simulation environments. Our model incorporates a Hill-type muscle representation
> based on high-resolution X-ray scans from multiple fixed specimens."

Also: muscle-actuated behavioural replay in OpenSim across walking and grooming; predicts
"coordinated muscle synergies"; imitation-learning ablation finds **damping and stiffness
facilitate learning**.

## Scope / limitations (from the FlyGym tutorial, verbatim)

> "Support for the FlyMimic musculoskeletal body model is **experimental**. … Only the
> left-front leg is muscle-driven in the current model; other legs are passive or locked."

- LF leg muscle-driven; RF locked at 0; LM/LH passive; thorax **tethered to the world**.
- Per-leg ground-contact sensors absent in this model.
- 73 bodies, **15 Hill-type muscle actuators**, **15 spatial tendons**.
- Model file: `assets/model/musculoskeletal/best_combined_arm_damping_stiff_cvt3.xml`
  (FlyGym) = `flymimic/assets/models/best_combined_arm_damping_stiff_cvt3.xml` (FlyMimic).
  Converted from OpenSim with **MyoConverter** (https://github.com/MyoHub/myoconverter).
- Variants in FlyMimic: `best_combined_cvt3` (baseline), `_arm_`, `_damping_`, `_stiff_`,
  `_arm_damping_stiff_`, and a torque-actuated control `best_combined_cvt3_torque.xml`.
- Control 500 Hz over a 10 kHz physics timestep. Action = 15 muscle activations in [0,1].
- Kinematic chain differs from stock NeuroMechFly: FlyMimic has a **separate trochanter body**
  (`LFCoxa → LFTrochanter → LFFemur → LFTibia → LFTarsus1..5`), whereas stock NeuroMechFly fuses
  `trochanterfemur`. ← relevant if you want per-muscle drive on the stock model.

## The 15 muscles (VERIFIED — parsed from the MJCF actuator/tendon/site names)

Site names embed **Miller** muscle numbers, confirming Miller's nomenclature is the anatomical
ground truth used.

| # | MuJoCo actuator name | Miller no. (from site names) | Acts on |
|---|---|---|---|
| 1 | `LFC_tergopleural_promotor_a` | Miller 28a | coxa |
| 2 | `LFC_tergopleural_promotor_b` | Miller 28b | coxa |
| 3 | `LFC_pleural_remotor_and_abductor` | Miller 29 | coxa |
| 4 | `LFC_pleural_promotor` | Miller 30 | coxa |
| 5 | `LFC_sternal_anterior_rotator` | Miller 31 | coxa |
| 6 | `LFC_sternal_posterior_rotator` | Miller 32 | coxa |
| 7 | `LFC_sternal_adductor` | Miller 33 | coxa |
| 8 | `LFF_trochanter_flexor_a` | (site `LFF_flexa`) | trochanter |
| 9 | `LFF_trochanter_flexor_b` | (site `lff_thco_flexb`) | trochanter |
| 10 | `LFF_accesory_trochanter_flexor` [sic] | (site `LFF_roll_f`) | trochanter |
| 11 | `LFF_trochanter_extensor` | (site `LFF_roll_e`) | trochanter |
| 12 | `LFF_sterno-tergo-trochanter_extensor_a` | (site `lff_thco_stta`) | trochanter |
| 13 | `LFF_sterno-tergo-trochanter_extensor_b` | — | trochanter |
| 14 | `LFTibia_flex_93434` | — (id looks like a segment/mesh id) | tibia |
| 15 | `LFTibia_extensor_93932` | — | tibia |

**Not present**: femur reductor, tarsus levator/depressor, long tendon muscle (LTM). So a
drive vector using the full canonical muscle list has **no actuator target** for those in
this model as shipped.

## Muscle parameters (VERIFIED — raw MJCF strings)

All 15 share `ctrlrange="0.0001 1"` and `dynprm="0.0001 0.0004 0 …"`
(→ activation τ ≈ **0.1 ms**, deactivation τ ≈ **0.4 ms**).
`gainprm == biasprm` for every muscle (MuJoCo muscle convention).

MuJoCo's documented `gainprm` ordering for `gaintype="muscle"` is
`range[0], range[1], force, scale, lmin, lmax, vmax, fpmax, fvmax` — reading the numbers under
that ordering (my interpretation, flagged) gives, for all 15: `scale=1, lmin=0, lmax=2,
vmax=10, fvmax=1.4`, with per-muscle `range`, `force`, `fpmax`:

| actuator | lengthrange (tendon) | range(L0 lo,hi) | force | fpmax |
|---|---|---|---|---|
| LFC_tergopleural_promotor_a | 0.157941 0.213637 | 0.774703 1.39095 | 14.2319 | 0.358728 |
| LFC_tergopleural_promotor_b | 0.339805 0.361902 | 0.944598 1.01483 | 67.764 | 4.08279 |
| LFC_pleural_remotor_and_abductor | 0.216122 0.299608 | 0.743435 1.72008 | 28.7481 | 0.353216 |
| LFC_pleural_promotor | 0.0912448 0.135751 | 0.859265 1.59552 | 30.6427 | 0.283134 |
| LFC_sternal_anterior_rotator | 0.126048 0.202925 | 0.185296 1.73386 | 10.5807 | 3.11328 |
| LFC_sternal_posterior_rotator | 0.0715242 0.147229 | 0.610817 1.40821 | 157.429 | 0.0752654 |
| LFC_sternal_adductor | 0.0972302 0.259683 | 0.244283 1.48664 | 12.9 | 0.446817 |
| LFF_trochanter_flexor_b | 0.272991 0.32626 | 0.537008 1.04625 | 77.9856 | 2.85222 |
| LFF_sterno-tergo-trochanter_extensor_a | 0.280895 0.337649 | 0.727951 1.5069 | 159.153 | 0.239629 |
| LFF_sterno-tergo-trochanter_extensor_b | 0.24007 0.320078 | 0.84831 1.43402 | 124.303 | 0.0988153 |
| LFF_accesory_trochanter_flexor | 0.203418 0.262616 | 0.638661 1.51365 | 24.8598 | 0.210106 |
| LFF_trochanter_extensor | 0.0912131 0.1283 | 0.90157 1.19258 | 40.5728 | 0.706553 |
| LFF_trochanter_flexor_a | 0.34225 0.413396 | (truncated in my fetch) | | |
| LFTibia_flex_93434 | (not captured) | | | |
| LFTibia_extensor_93932 | (not captured) | | | |

(Units of `force` not stated in the file; model lengths are in the model's own scale — do not
assume µN or mm without checking the paper. **UNVERIFIED units.**)

## LF joints and limits (VERIFIED from MJCF)

| joint | axis | range (rad) |
|---|---|---|
| `joint_LFCoxa_yaw` | 1 0 0 | -0.597 0.2745 |
| `joint_LFCoxa_pitch` | 0 1 0 | -0.5783 0.7375 |
| `joint_LFCoxa_roll` | 0 0 1 | 0.1436 0.6236 |
| `joint_LFTrochanter_yaw` | 1 0 0 | -1.196 0.2745 |
| `joint_LFTrochanter_pitch` | 0 1 0 | -3.242 -1.217 |
| `joint_LFTrochanter_roll` | 0 0 1 | -0.2745 1.384 |
| `joint_LFTibia_pitch` | 0 1 0 | 0.4789 2.502 |

(RF joints exist but are ±π and locked.)
Mocap clip `0002`: 225 frames, 7 joint DoF, 500 Hz; arrays `qpos (T,J) rad`, `qvel (T,J) rad/s`,
`xipos (T,4,3) mm`, `xivel (T,4,3) mm/s`; tracked bodies `LFFemur, LFTibia, LFTarsus1, LFTarsus5`.

---

# ADDENDUM — full-text + OpenSim-source pass (2nd agent, 2026-09-21)

Complementary to the above, not a replacement. Deep-dive with paper methods, validation,
controller, sensor/connectome status and repo audit lives in
`docs/physiology/leg_biomech_parts/flymimic_paper_and_repo.md`.
Everything below was read directly from the arXiv HTML full text (v2), the `.osim` file
in the FlyMimic repo, or the GitHub API. **VERIFIED** unless marked otherwise.

## Corrections / confirmations to the notes above

- **`gizemozd/neuromechfly-muscles` does not exist publicly.** GitHub API returns
  "Not Found" for `gizemozd/neuromechfly-muscles`, `NeLy-EPFL/neuromechfly-muscles` and
  `NeLy-EPFL/NeuroMechFly-muscles`. The X-ray→OpenSim construction pipeline and the
  NSGA-II optimizer are therefore **not public**. Only the resulting `.osim` files are —
  and they ship *inside* FlyMimic at `flymimic/assets/models/opensim/best_combined.osim`
  and `best_combined_full.osim` (plus a PDF render).
- flygym's `best_combined_arm_damping_stiff_cvt3.xml` is **byte-identical** to FlyMimic's
  (md5 `f3a2e237212dbccb05645865ae7de53b`). flygym vendors it unchanged.
- **The Miller citation is not in the paper.** Searching the full text for "Miller"
  returns zero hits — the numbering survives only in MJCF site names. The near-certain
  source is A. Miller (1950), "The internal anatomy and histology of the imago of
  *Drosophila melanogaster*", in M. Demerec (ed.), *Biology of Drosophila*, Wiley,
  pp. 420–534 (FlyBase FBrf0007735 confirms author/volume/pages). **I could not verify
  that Miller's numbers 28–33 are these six thoracic muscles** — treat the numeric
  mapping as unconfirmed.
- Leftover naming tell: the two femoral MTUs' sites are
  `LFTibia_extensor_93932_bifemlh_r-P1/P2` — `bifemlh_r` = *biceps femoris long head,
  right* from a stock OpenSim human gait template.
- Author-list discrepancy: arXiv v1 and v2 both list **8** authors including
  **Alexander Blanke** (Univ. Bonn); the repo BibTeX and the first author's homepage
  list **7** and omit him.
- Only DOI that exists for this work: **10.48550/arXiv.2509.06426**. No publisher DOI.
  ICLR acceptance type (poster/spotlight/oral) **could not verify** (OpenReview forum
  `6lEjX1getx` served a bot-check page).

## Resolves the "UNVERIFIED units" flag above — the OpenSim source parameters

`flymimic/assets/models/opensim/best_combined.osim` holds all 15 as
**`Millard2012EquilibriumMuscle`** with explicit physiological parameters. The file
declares `<length_units>m</length_units>` and `<force_units>N</force_units>`, but
`<gravity>0 -9806.65 0</gravity>` means the length unit is really **mm** — so the
declared force unit is not trustworthy (most plausibly µN, given a 28 mN/mm² specific
tension at fly-scale PCSA). Raw file values:

| muscle | Fmax | l_opt | l_tendon_slack | v_max | pennation |
|---|---|---|---|---|---|
| LFC_tergopleural_promotor_a | 9.319 | 0.1653 | 0.008698 | 42.09 | 0 |
| LFC_tergopleural_promotor_b | 46.20 | 0.2756 | 0.02774 | 29.58 | 0 |
| LFC_pleural_remotor_and_abductor | 16.07 | 0.1750 | 0.06470 | 62.17 | 0 |
| LFC_pleural_promotor | 16.32 | 0.08605 | 0.03354 | 24.81 | 0 |
| LFC_sternal_anterior_rotator | 50.19 | 0.06355 | 0.1550 | 48.71 | 0 |
| LFC_sternal_posterior_rotator | 98.17 | 0.1066 | 0.01468 | 19.06 | 0 |
| LFC_sternal_adductor | 9.080 | 0.1462 | 0.05637 | 13.62 | 0 |
| LFF_trochanter_flexor_a | 27.45 | 0.3495 | 0.01839 | 92.22 | 0 |
| LFF_trochanter_flexor_b | 66.94 | 0.1960 | 0.1719 | 8.515 | 0 |
| LFF_accesory_trochanter_flexor | 15.18 | 0.07356 | 0.1631 | 56.51 | 0 |
| LFF_trochanter_extensor | 25.78 | 0.1014 | 0.01773 | 71.74 | 0 |
| LFF_sterno-tergo-trochanter_extensor_a | 92.63 | 0.2009 | 0.09143 | 49.19 | 0 |
| LFF_sterno-tergo-trochanter_extensor_b | 70.48 | 0.1858 | 0.1073 | 12.25 | 0 |
| LFTibia_flex_93434 | 41.53 | 0.4001 | 0.05946 | 75.64 | 0 |
| LFTibia_extensor_93932 | 154.1 | 0.4236 | 0.1410 | 24.79 | 0 |

All 15: `pennation_angle_at_optimal = 0`, `ignore_tendon_compliance = true` (rigid
tendon), `activation_time_constant = 1e-4`, `deactivation_time_constant = 4e-4`,
`min_control = 1e-4`, `max_control = 1`. Pennation was set to zero deliberately "for
compatibility across simulation engines", with Fmax scaled to compensate (Supp. §A.3).

## Where those numbers came from (paper §3.2, §A.5)

- **Fmax** = fixed base specific tension × optimized scale ∈ [0.3, 3] × **PCSA measured
  on the X-ray/CT scans**. Specific tension **28 mN/mm²**, picked between Drosophila
  **jump muscle 37 mN/mm²** (Eldred 2010, doi:10.1016/j.bpj.2009.11.051) and **indirect
  flight muscle 9 mN/mm²** (Swank 2012, doi:10.1016/j.ymeth.2011.10.015).
- **v_max**: base value estimated from an **X-ray video of muscle contraction during leg
  movement**, × optimized scale ∈ [0.4, 2.4].
- **l_opt, l_tendon_slack**: ratios from the CT data, × optimized scale ∈ [0.8, 1.2],
  capped at 95% of total MTU length.
- **Muscle paths**: annotated insertions, allowed to move within a 5–10 µm cube.
- **F-L / F-V curves**: OpenSim defaults. The paper says explicitly that no measured
  Drosophila muscle curves exist, so human-derived defaults were assumed to approximate
  physiology.
- **Fitting**: **NSGA-II** (`geatpy`) wrapped around an OpenSim
  static-optimization → forward-dynamics loop; objectives = MSE + negative correlation of
  joint angles vs reference, summed over **antennal grooming + locomotion**; each joint
  optimized independently; 6-dim per MTU (9-dim with a via point); curriculum of 5–10
  warm-up then 5–10 exploratory generations. Table 3: thorax 200 gen/120 pop/mut .7/
  cross .5; coxa 200/40/.7/.5; femur 200/300/.5/.3. §3.2 separately quotes ~8 h for a
  3-DoF joint at 200 individuals × 40 generations, ≈20 h for the whole foreleg
  (i9-14900, 64 GB). Best set **mirrored to the right leg** — in OpenSim only; the MJCF
  keeps the right foreleg locked.

## Anatomy sources (paper §3.1)

Three X-ray datasets: **Dinges et al. 2021** (*J Comp Neurol* 529(4):905–925,
doi:10.1002/cne.24987 — the campaniform-sensilla paper, used purely as a thorax X-ray
volume) for thoracic muscles; **Kuan et al. 2020** (*Nat Neurosci*,
doi:10.1038/s41593-020-0704-9, X-ray holographic nano-tomography) for the rest of the
leg; plus **one custom synchrotron-radiation µCT dataset** collected for this study, used
to cross-validate attachment points across different foreleg postures. Functional
grouping followed Azevedo 2024 and Soler 2004.

## Coverage: 12 of 19 muscle groups; what is missing and why (§3.2, §A.1)

15 MTUs = 7 thorax + 6 coxa + 2 femur, covering **12 of the 19** muscle groups in the
datasets. **Tibia-housed muscles excluded** (tibia only partly inside the X-ray volume).
**Trochanter muscles omitted** ("their function remains unclear", citing Soler 2004). In
the femur only the **fast tibia flexor + extensor** were modelled (Azevedo 2020 eLife
size principle). Mid/hind legs were annotated but **not optimized**: 7 MTUs per midleg,
8 per hindleg (Fig. S1/S2), anatomy only, since a single dataset gave no way to
cross-validate.

## Also worth knowing from the full text

- The `cvt3` in the filenames: they argue from attachment points and joint condyles that
  the **coxa–trochanter joint has 3 DoF, not NeuroMechFly's 2**; with 3 DoF the ThC-roll
  range during antennal grooming shrinks from [-95°, 50°] to [-30°, -7°] (Supp. §A.2).
  They also replaced NeuroMechFly's foreleg meshes with the X-ray meshes.
- **Validation is kinematic only**: DeepLabCut 2D → 5-camera ChArUco calibration →
  Anipose 3D → SeqIKPy IK (doi:10.21105/joss.08557); 100 Hz recording interpolated to
  500 Hz; forward walking + antennal grooming; normalized RMSE and r² per DoF, plus a
  moment-arm sign/dominance sanity check. No force, EMG, calcium or optical-flow
  validation.
- **Result**: NMF on the static-optimization activations gives **3 muscle primitives
  explaining >90%** of variance (first alone >80%). `Sar` and `Sa` are task-invariant;
  coxal flexors/extensors specialize per synergy during grooming but not locomotion.
- **No proprioception or sensory modelling anywhere.** Full-text search for *propriocep*,
  *sensill*, *chordotonal*, *FeCO*, *hair plate* hits only the title of the Dinges 2021
  reference. The RL observation is qpos, qvel/10 clipped ±10, xpos of LFFemur/LFTibia/
  LFTarsus1/LFTarsus5, muscle length/velocity/activation/force, and time-remaining.
- **Connectome is framing, not mechanism.** FlyWire, FANC, the female VNC connectome and
  the leg/wing premotor paper are all cited, and the paper says ~19 leg muscles are
  driven by ~69 motor neurons — but **no connectome-derived motor-neuron drive is built**.
  The 15-dim policy output is merely *called* "motor neuron activities".
- Controller: PPO (Stable-Baselines3) on a dm_control task. MLP [512,512,256], ReLU,
  Adam, lr 1e-5, γ 0.99, batch 64, n_steps 2048, 10 epochs/update, **15 M steps**,
  control 500 Hz over 10 kHz physics. Reward
  `r = (1/3)[exp(-w_p·d_xpos) + exp(-w_p·d_qpos) + exp(-w_v·d_qvel)]` clipped to [0,1],
  `w_p = 5` (velocity weight printed inconsistently as `w_v` in the formula and `w_e = 3`
  in the prose). Init joint noise variance 0.02. ~96 h on an i7-12700/128 GB.
  The shipped Hydra configs say `tot_ts: 30000000`, twice the paper's 15 M.
- Stated limitations (§6): (1) Fmax and v_max are estimated/optimized, not measured;
  (2) **contact forces are omitted entirely** — no body–body or body–environment
  interaction, so activations may not reflect untethered locomotion.
- **[2nd, unconfirmed]** The project page https://gizemozd.github.io/fly_mimic/ claims
  the trained policy "transfers to ground locomotion without retraining". That sentence
  is **not in arXiv v2** — possibly new in the ICLR camera-ready.
