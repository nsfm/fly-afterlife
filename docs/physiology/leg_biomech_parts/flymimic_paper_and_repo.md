# FlyMimic — the Ozdil et al. Drosophila musculoskeletal (Hill-type) leg model

Status: **complete** (agent: flymimic deep-dive, 2026-09-21). Open items listed in §9.
Tags: **[V]** = I read it in the primary artifact (arXiv full text, GitHub API, raw repo
file, Crossref). **[2nd]** = reported by a secondary page/search result, unchecked.
**[?]** = could not verify.

Full extracted source notes live in:
- `docs/research/sources/ozdil_2026_flymimic.md` (paper)
- `docs/research/sources/gizemozd_flymimic_repo.md` (repo)

---

## 1. Citation [V]

Özdil PG*, Ning C*, Phelps JS, Wang-Chen S, Elisha G, Blanke A, Ijspeert A, Ramdya P.
**Musculoskeletal simulation of limb movement biomechanics in *Drosophila melanogaster*.**
arXiv:2509.06426 [q-bio.NC], v1 8 Sep 2025 / v2 11 Sep 2025.
DOI (arXiv-issued, the only one that exists): **10.48550/arXiv.2509.06426**.
23 pages, 11 figures. HTML full text is CC BY 4.0. (* equal contribution.)

Venue: **ICLR 2026** — stated in the repo's own BibTeX ("The Fourteenth International
Conference on Learning Representations", 2026) and on the first author's homepage. [V]
OpenReview forum id `6lEjX1getx` [2nd, from mlanthology.org; OpenReview served a
bot-check page]. Acceptance type (poster/spotlight/oral) **[?]**.

Author-count discrepancy worth knowing: **arXiv v2 has 8 authors including Alexander
Blanke (Univ. Bonn); the repo BibTeX and the author's homepage list 7 and omit Blanke.** [V]

---

## 2. What the model actually is [V]

- **15 Hill-type muscle-tendon units (MTUs) on ONE foreleg**: 7 thorax, 6 coxa, 2 femur.
  That covers **12 of the 19 leg muscle groups** in their anatomical data.
- Actuates **7 DoFs across 3 joints**: thorax–coxa (yaw/pitch/roll), coxa–trochanter
  (yaw/pitch/roll), femur–tibia (pitch).
- Deliberately excluded: tibia-housed muscles (tibia only partly in the X-ray volume) and
  trochanter muscles ("function remains unclear", citing Soler 2004). In the femur only
  the **fast tibia flexor + extensor** are modelled (Azevedo 2020 eLife size principle).
- Mid/hind legs: **anatomically annotated only** — 7 MTUs per midleg, 8 per hindleg
  (Supp. §A.1, Fig. S1/S2). Not optimized, not driveable.
- The paper claims to be **the first** 3D data-driven musculoskeletal model of fly legs,
  in **both OpenSim and MuJoCo**.
- Background numbers it asserts (§2.3): each fly leg ≈ 7 DoF over 5 joints, ~19 muscles,
  ~69 motor neurons.

### 2.1 Exact muscle names (from the MJCF actuator list) [V]

Left-front only. Thorax/coxa group (`LFC_*`): `tergopleural_promotor_a`,
`tergopleural_promotor_b`, `pleural_remotor_and_abductor` (= "Pra"), `pleural_promotor`,
`sternal_anterior_rotator` (= "Sar"), `sternal_posterior_rotator`, `sternal_adductor`
(= "Sa"). Coxa/trochanter group (`LFF_*`): `trochanter_flexor_a`, `trochanter_flexor_b`,
`accesory_trochanter_flexor` (sic), `trochanter_extensor`,
`sterno-tergo-trochanter_extensor_a`, `sterno-tergo-trochanter_extensor_b`.
Femur: `LFTibia_flex_93434`, `LFTibia_extensor_93932`.

### 2.2 The "Miller" numbering [V for the mapping, [?] for the citation]

The Miller labels live in the MJCF **site (attachment point) names**, not the actuator
names, and only on the seven thoracic muscles:

| site prefix | muscle |
|---|---|
| Miller28a | tergopleural promotor a |
| Miller28b | tergopleural promotor b |
| Miller29 | pleural remotor and abductor |
| Miller30 | pleural promotor |
| Miller31 | sternal anterior rotator |
| Miller32 | sternal posterior rotator |
| Miller33 | sternal adductor |

Suffixes `_p1 / _p296 / _p396` are origin / via / insertion points. The remaining
muscles use ad-hoc site names (`LFF_roll_f_p1`, `lff_thco_stta_p1`, …).

The Miller reference is **not cited anywhere in the FlyMimic paper** (no "Miller" string
in the full text). The near-certain source is the classic Drosophila internal-anatomy
monograph:
**A. Miller (1950), "The internal anatomy and histology of the imago of *Drosophila
melanogaster*", in M. Demerec (ed.), *Biology of Drosophila*, Wiley, pp. 420–534**
(FlyBase reference report FBrf0007735 confirms author, volume and page range) [V].
The Drosophila VNC-connectome literature states it "adopted the muscle nomenclature from
Miller (1950)". **I could NOT verify that Miller's numbers 28–33 are exactly these six
thoracic muscles** — one WebFetch returned a Miller citation that looks fabricated, so
treat any numeric mapping claim as unconfirmed until someone reads Miller or the
Azevedo 2024 / Lesser 2024 extended data directly. **[?]**

Tell-tale leftover: the two femoral MTUs' site names are
`LFTibia_extensor_93932_bifemlh_r-P1/P2` — `bifemlh_r` is *biceps femoris long head,
right* from a standard OpenSim human gait template. The femur muscles were clearly
built by editing a human template muscle. [V]

---

## 3. Hill-type: yes, native MuJoCo muscle actuators [V]

MJCF `<default class="muscle">` carries **`dyntype="muscle" gaintype="muscle"
biastype="muscle"`**, `ctrllimited="true" ctrlrange="0 1"`,
`dynprm="0.01 0.04 0 …"`, `gainprm=biasprm="0.75 1.05 -1 200 0.5 1.6 1.5 1.3 1.2 0"`.
Each `<general>` actuator overrides with per-muscle values written by MyoConverter
(`dynprm="0.0001 0.0004 0 …"`, i.e. τ_act = 0.1 ms, τ_deact = 0.4 ms; `ctrlrange="0.0001 1"`).

OpenSim side: **`Millard2012EquilibriumMuscle`** for all 15 (Millard et al. 2013,
*J Biomech Eng* 135(2):021005). Rigid tendon (`ignore_tendon_compliance = true`),
**pennation angle = 0 for every muscle** (set to zero "for compatibility across
simulation engines", with Fmax scaled to compensate). Buffer elasticity omitted.

### 3.1 Per-muscle parameters as shipped (read from `flymimic/assets/models/opensim/best_combined.osim`) [V]

Units caveat: the file declares `<length_units>m</length_units>` and
`<force_units>N</force_units>`, but `<gravity>` is `0 -9806.65 0`, i.e. **mm/s²** — so
lengths are millimetres and the declared force unit is not trustworthy (most likely µN
given a 28 mN/mm² specific tension times fly-scale PCSA). Numbers are raw file values.

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

All 15 share `activation_time_constant = 1e-4`, `deactivation_time_constant = 4e-4`,
`min_control = 1e-4`, `max_control = 1`.

### 3.2 Where the parameters came from [V]

- **Max isometric force** = (fixed base specific tension) × (optimized scale 0.3–3) ×
  **PCSA measured from the CT/X-ray scans**. Specific tension **28 mN/mm²**, chosen
  between Drosophila **jump muscle 37 mN/mm²** (Eldred 2010, *Biophys J* 98(7):1218)
  and **indirect flight muscle 9 mN/mm²** (Swank 2012, *Methods* 56(1):69).
- **Max contraction velocity**: base value estimated from an **X-ray video of muscle
  contraction during leg movement**, scaled by an optimized factor 0.4–2.4.
- **Optimal fiber length & tendon slack length**: ratios observed in the CT data, scaled
  0.8–1.2, capped at 95% of total MTU length.
- **Attachment points / muscle paths**: initialized from the annotated X-ray fibers, then
  allowed to move within a 5–10 µm cube.
- **Pennation, activation/deactivation constants, F-L and F-V curves**: fixed or left at
  OpenSim defaults. The paper is explicit that *no measured Drosophila F-L/F-V curves
  exist*, so OpenSim's human-derived default curves were assumed to approximate reality.
- **Fitting**: **NSGA-II** (multi-objective GA, `geatpy`) around an OpenSim
  **static-optimization → forward-dynamics** loop. Objectives = MSE + (negative)
  correlation of joint angles vs reference, summed across **antennal grooming and
  locomotion** to avoid overfitting. 6-dim search per MTU (9-dim with a via point);
  each joint optimized independently. Curriculum: 5–10 warm-up generations then 5–10
  exploratory generations. NSGA-II table: thorax 200 gen/120 pop/mut .7/cross .5;
  coxa 200/40/.7/.5; femur 200/300/.5/.3. §3.2 separately says a 3-DoF joint took ~8 h
  with 200 individuals × 40 generations and the whole foreleg ≈ 20 h sequential on an
  i9-14900/64 GB. The best set was **mirrored to the right leg** (in OpenSim).

### 3.3 Anatomy sources [V]

Three X-ray datasets: **Dinges et al. 2021** *J Comp Neurol* 529(4):905–925
(doi:10.1002/cne.24987 — the campaniform-sensilla paper, used here purely as a thorax
X-ray volume), **Kuan et al. 2020** *Nat Neurosci* (X-ray holographic nano-tomography,
doi:10.1038/s41593-020-0704-9) for the rest of the leg, plus **one custom synchrotron
µCT dataset** collected for this study, used to cross-validate attachments across
different foreleg postures. Functional grouping followed Azevedo 2024 and Soler 2004.

They also **replaced NeuroMechFly's foreleg meshes with the X-ray meshes** and argue the
coxa–trochanter joint has **3 DoF, not 2** — with 3 DoF the ThC-roll range during antennal
grooming shrinks from [-95°, 50°] to [-30°, -7°], removing unnatural thorax-coxa rotation
(Supp. §A.2). That is the `cvt3` in the MJCF filenames.

---

## 4. Validation [V]

Kinematic only. Tethered flies on an air-supported spherical treadmill; 2D tracking with
**DeepLabCut** (per-camera models), 5 cameras calibrated with a ChArUco board, 3D with
**Anipose** (Viterbi + spatiotemporal regularization), joint angles by IK with
**SeqIKPy** (Özdil et al., JOSS 2026, doi:10.21105/joss.08557; Zenodo
10.5281/zenodo.12601317). Recorded at 100 Hz, interpolated to 500 Hz for stability.
Two behaviors: **forward walking** and **antennal grooming**.

Metrics: range-normalized RMSE and squared Pearson correlation between simulated and
reference joint angles over 7 DoFs; plus a **moment-arm plausibility check** (flexor and
extensor moment arms have opposite signs; the predicted dominant contributors to ThC and
CTr yaw/pitch/roll and FTi pitch match known functional roles).

**No** X-ray force validation, **no** EMG/calcium muscle-activity validation, **no**
optical-flow validation. X-ray video is used only to estimate v_max.

Scientific result: NMF of the static-optimization activations gives **3 muscle primitives
explaining >90% of variance** (the first alone >80%); `Sar` and `Sa` load consistently
across all synergies and both behaviors (task-invariant), while coxal flexors/extensors
specialize per synergy during grooming but not locomotion.

---

## 5. Controller, sensors, connectome [V]

- **OpenSim**: no learned controller. Static optimization infers activations from
  reference joint angles; forward dynamics replays them.
- **MuJoCo**: **imitation learning of motion capture with PPO** (Stable-Baselines3,
  task built on dm_control). MLP actor+critic, hidden **[512, 512, 256]**, ReLU, Adam,
  lr **1e-5**, γ 0.99, batch 64, n_steps 2048, 10 epochs/update, **15 M steps**,
  control **500 Hz**, physics **10 kHz** (`timestep=1e-04`). Episodes start at a random
  mocap frame. Action = per-muscle excitation in [0,1], which the paper explicitly calls
  "motor neuron activities". Reward
  `r_t = (1/3)[exp(-w_p·d_xpos) + exp(-w_p·d_qpos) + exp(-w_v·d_qvel)]`, clipped to [0,1],
  `w_p = 5` (the velocity weight is printed as `w_v` in the formula and `w_e = 3` in the
  prose — an inconsistency in the paper). Init joint noise variance 0.02. ~96 h to train
  on an i7-12700/128 GB. Note the shipped Hydra configs say `tot_ts: 30000000`, twice the
  paper's 15 M.
- Passive-property ablation (Fig. 5): armature always on (0.0005); stiffness (0.4) and
  damping (0.02) toggled → 4 MJCF variants. **Stiffness + damping learns fastest and
  ends highest**; final kinematics look the same across conditions but muscle-activation
  time courses differ.

### 5.1 Proprioception / sensory modelling: NONE [V]

Searching the full text for *propriocep*, *sensill*, *chordotonal*, *FeCO*, *hair plate*
returns exactly one hit: the **title of the Dinges 2021 reference** in the bibliography.
There is no FeCO, no campaniform sensilla, no hair plates, no bristles, no sensor
elements in the MJCF. The RL observation vector (read from
`flymimic/tasks/fly/mocap_tracking_muscle.py`) is: `qpos`; `qvel/10` clipped ±10;
Cartesian `xpos` of LFFemur, LFTibia, LFTarsus1, LFTarsus5(claw); muscle length
(`data.actuator_length`), velocity (`data.actuator_velocity`, clipped ±100), activation
(`data.act`), force (`data.actuator_force`/1000, clipped ±10); and time remaining in the
clip. **The only "proprioception" is raw muscle state handed to the policy.**

### 5.2 Motor-neuron / connectome drive: discussed, not implemented [V]

The paper cites FlyWire (Dorkenwald 2024), the female VNC connectome (Azevedo 2024,
doi:10.1038/s41586-024-07389-x), the FANC reconstruction (Phelps 2021) and the leg/wing
premotor network paper (Lesser 2024, doi:10.1038/s41586-024-07600-z), and argues that
connectivity alone cannot predict muscle activity — the muscle model is pitched as the
missing bridge between motor neuron activity and joint movement. But **no
connectome-derived motor neuron pool, no size principle, no MN→muscle mapping is built
or simulated.** The 15-dim policy output is simply *called* motor neuron activity.

### 5.3 Authors' stated limitations [V]

(1) physiological parameters (Fmax, v_max) are estimated/optimized, not measured;
(2) **contact forces are omitted entirely** — no body–body or body–environment
interaction, so activations may not reflect untethered locomotion demands.

---

## 6. Repository (github.com/gizemozd/FlyMimic) [V]

**Exists, public, Apache-2.0** (SPDX `Apache-2.0`, standard Apache 2.0 LICENSE text).
created 2025-08-09, last push 2026-03-27, ~5 stars, default branch `main`.
Homepage https://gizemozd.github.io/fly_mimic/ .

Pinned stack (`pyproject.toml`): **`mujoco==3.3.2`, `dm_control==1.0.30`**, plus
stable-baselines3, torch, hydra-core, lxml, tensorboard, wandb (unpinned). Python ≥ 3.10.

MJCF files, all under `flymimic/assets/models/`:
`best_combined_arm_cvt3.xml` (armature only), `best_combined_arm_damping_cvt3.xml`,
`best_combined_arm_stiff_cvt3.xml`, `best_combined_arm_damping_stiff_cvt3.xml`,
`best_combined_cvt3.xml` (all 15-muscle), and `best_combined_cvt3_torque.xml`
(7 `<motor>` joint-torque actuators, `gear=0.5`, no muscles). The OpenSim sources ship
too: `models/opensim/best_combined.osim`, `best_combined_full.osim`, plus a PDF.
~70 whole-body STL meshes (NeuroMechFly's) under `models/meshes/stl/`.

**Only one leg is muscled** [V]: every actuator and tendon is `LF*`. The right foreleg's
7 joints are welded by `<equality>` joint constraints named `joint_RF*_locked`
(`polycoef="0 0 0 0 0"`). Mid/hind legs and wings are rigid mesh bodies with no joints.
Model units are **mm** (`gravity="0 0 -9801"`, mesh `scale="1000 1000 1000"`).

Gym env: `flymimic/envs/dmcontrol_wrapper.py` → `DMControlGymWrapper(gym.Env)`, a
**gymnasium** adapter that flattens a dm_control obs dict into a Box. The task itself is
a dm_control `base.Task` (`mocap_tracking_muscle.py`, `mocap_tracking_torque.py`).
Default controller: **PPO / Stable-Baselines3**, Hydra configs in `flymimic/config/`,
entrypoints `scripts/train_muscle.py`, `scripts/eval_rollout.py`, pretrained
`logs/demo_model.zip` (~10 MB); more checkpoints on Dropbox per README.

Mocap data shipped: `assets/mocap/{qpos,qvel,xipos,xivel}/{0001,0002}.npy` — two clips.

**Missing piece**: the README points at
`https://github.com/gizemozd/neuromechfly-muscles` for "the original muscle model
development and parameter optimization in OpenSim". **That repo 404s** (also checked
`NeLy-EPFL/neuromechfly-muscles` and `NeLy-EPFL/NeuroMechFly-muscles`). So the
X-ray→OpenSim construction pipeline and the NSGA-II optimizer are **not public**; only
the resulting `.osim` and converted MJCF are.

### 6.1 Relationship to flygym [V]

`flygym`'s `src/flygym/assets/model/musculoskeletal/best_combined_arm_damping_stiff_cvt3.xml`
is **byte-identical** (md5 `f3a2e237212dbccb05645865ae7de53b`) to the FlyMimic repo's
copy of that file. flygym vendors the FlyMimic MJCF unchanged.

---

## 7. Predecessors and siblings from the Ramdya lab [V, DOIs Crossref-verified]

- Lobato-Rios V, Tata Ramalingasetty S, **Özdil PG**, Arreguit J, Ijspeert AJ, Ramdya P.
  *NeuroMechFly, a neuromechanical model of adult Drosophila melanogaster.*
  **Nature Methods** 19(5):620–627, 2022. **doi:10.1038/s41592-022-01466-7**.
  (v1 used simplified antagonistic spring-damper "muscles" in PyBullet — not Hill-type.)
- Wang-Chen S, Stimpfling VA, Lam TKC, **Özdil PG**, Genoud L, Hurtak F, Ramdya P.
  *NeuroMechFly v2: simulating embodied sensorimotor control in adult Drosophila.*
  **Nature Methods**, 2024. **doi:10.1038/s41592-024-02497-y**. (MuJoCo; position/torque
  actuators, multimodal sensing — still no muscles.)
- **Özdil PG**, Arreguit J, Scherrer C, Hurtak F, Ijspeert AJ, Ramdya P.
  *Centralized brain networks controlling antennal grooming coordination.*
  **Nature Communications**, 2026. **doi:10.1038/s41467-026-72152-x**.
  Preprint: *Centralized brain networks underlie body part coordination during grooming*,
  bioRxiv 2024-12-17, **doi:10.1101/2024.12.17.628844**. Code:
  github.com/NeLy-EPFL/antennal-grooming. ← this is the "sensory feedback / behavioral
  constraints" predecessor; it is a **neural-circuit + kinematics** paper, not a muscle paper.
- **Özdil PG**, Wang-Chen S, Ning C, Ijspeert A, Ramdya P. *SeqIKPy: a Python package for
  inverse kinematics in insects.* **JOSS**, 2026. **doi:10.21105/joss.08557**.
  Zenodo 10.5281/zenodo.12601317. Code: NeLy-EPFL/sequential-inverse-kinematics.
- Özdil's PhD thesis, *"An integrative computational modeling approach for Drosophila
  motor control"*, EPFL 2025 **[2nd — from a search summary, not checked on Infoscience]**.

There is **no earlier Ozdil paper on fly leg muscle anatomy or X-ray tomography of leg
muscles**. The X-ray muscle anatomy in FlyMimic comes from Kuan 2020 / Dinges 2021 plus
the new custom synchrotron scan; the FlyMimic paper is the lab's first muscle model. [V]

Adjacent anatomy/kinematics work cited by FlyMimic and worth having:
- Haustein M, Blanke A, Bockemühl T, Büschges A. *A leg model based on anatomical
  landmarks to study 3D joint kinematics of walking in Drosophila melanogaster.*
  **Front Bioeng Biotechnol** 12:1357598, 2024. **doi:10.3389/fbioe.2024.1357598**
  (kinematic joint-axis model, no muscles).
- Azevedo AW, Dickinson ES, Gurung P, Venkatasubramanian L, Mann RS, Tuthill JC.
  *A size principle for recruitment of Drosophila leg motor neurons.* **eLife** 9:e56754, 2020.
- Ache JM, Matheson T. *Passive joint forces are tuned to limb use in insects and drive
  movements without motor activity.* **Curr Biol** 23(15):1418–1426, 2013.
  (the justification for the stiffness/damping story).

---

## 8. Is there any OTHER Drosophila / insect Hill-type musculoskeletal model? [V — essentially no]

Searched arXiv/Crossref/GitHub/MyoHub. Findings:

- **Nothing else for Drosophila.** The claim "the first 3D, data-driven musculoskeletal
  model of Drosophila legs" holds as far as I can check. The other whole-fly models are
  all torque/position actuated:
  - **flybody** — Vaxenburg R, Siwanowicz I, Merel J, Robie AA, Morrow C, Novati G,
    Stefanidi Z, Both G-J, Card GM, Reiser MB, et al. *Whole-body physics simulation of
    fruit fly locomotion.* **Nature**, 2025. **doi:10.1038/s41586-025-09029-4**.
    (MuJoCo, no Hill-type muscles.)
  - **NeuroMechFly v1/v2** — see §7. v1 has antagonistic spring-damper actuators; v2 has
    position/torque actuators.
- **Closest non-fly insect model**: Guo S, Lin J, Wöhrl T, Liao M. *A Neuro-Musculo-Skeletal
  Model for Insects With Data-driven Optimization.* **Scientific Reports** 8:2129, 2018.
  **doi:10.1038/s41598-018-20093-x**. Desert ant (*Cataglyphis fortis*); Hill-type muscles
  with customized F-L/F-V curves; **Bullet** physics engine, C++; 3 DoF per leg × 6 legs,
  18 joints, antagonistic muscle pairs (6 pairs per leg). Not OpenSim, not MuJoCo.
  FlyMimic cites it as ref [42].
- **MyoSuite / MyoHub: no insect models at all.** The `MyoHub/myo_sim` README model table
  lists only human models — MyoLeg (29 DoF / 80 muscles), MyoArm (38/63), MyoTorso-MyoBack
  (18/210), MyoHand (23/39), MyoFullBody (123/416), MyoLeg26 (18/26), plus legacy
  MyoFinger and MyoElbow. `myosuite/envs/` contains only `myo`. **[V]**
  MyoHub's contribution here is **MyoConverter**, the OpenSim→MuJoCo tool FlyMimic used
  (the MJCF header comment names it explicitly and licenses the converted model Apache 2.0).
- `NeLy-EPFL/neuromechants` ("Trying to build body models for AntScan in MuJoCo?", last
  push 2026-03-22, no license) exists but is a body-model experiment, not a muscle model.
  **[V for existence; contents not inspected]**

Conclusion: **FlyMimic is the only Hill-type musculoskeletal Drosophila model that
exists**, and one of only two insect ones (the other being the 2018 ant model in Bullet).

---

## 9. Unverified / open

- Miller numbering 28–33 ↔ the six thoracic muscles. **[?]** See §2.2.
- ICLR 2026 acceptance type. **[?]**
- Force units in the `.osim` (declared N, almost certainly µN). **[?]**
- The project page claims the trained policy "transfers to ground locomotion without
  retraining" — **not present in arXiv v2**; possibly new in the ICLR camera-ready. **[2nd]**
- Why the repo/homepage author list drops Blanke. **[?]**

---

## 10. How flygym 2.1.0 exposes FlyMimic [V — read from local flygym source]

Module `flygym/compose/fly/musculoskeletal.py`, marked **"Experimental"** in its own
docstring, which states outright: *"only the left-front leg is muscle-driven in the
current model"* and *"Not all features available for the default `NeuroMechFly` model
are currently supported (e.g. per-leg ground-contact sensors)."*

Design note from the docstring: unlike `NeuroMechFly` / `FlyBody`, which compose a body
from meshes + YAML rigging via `BaseFly`, FlyMimic is a **pre-authored self-contained
MJCF** shipping its own floor, lighting, 15 Hill-type muscles, 15 spatial tendons and
passive joint properties. flygym therefore *switches the body model* rather than
overlaying muscles: it loads the MJCF into a `mujoco.MjSpec` (flygym's editing backend
since the v2.1.0 PyMJCF→MjSpec migration) and wraps it so `flygym.Simulation` works.

Public API (`__all__`):
`MusculoskeletalFly`, `MUSCULOSKELETAL_MODEL_DIR`, `MUSCULOSKELETAL_MESH_DIR`,
`DEFAULT_MUSCULOSKELETAL_XML`, `DEFAULT_SCENE_CAMERA`,
`build_musculoskeletal_simulation`, `MjWarpCompatibilityReport`,
`check_mjwarp_compatibility`, `build_musculoskeletal_gpu_simulation`.

- `MusculoskeletalFly(BaseCompositionElement)` — **not** a `BaseFly` subclass. Exposes
  `mjcf_root`, `name`, `get_bodysegs_order()`, `get_jointdofs_order()`,
  `get_actuated_jointdofs_order(actuator_type)`, `get_sites_order()`,
  `get_legs_order()`, `muscle_names` (property → `get_actuated_jointdofs_order(
  ActuatorType.MUSCLE)`), `add_vision(...)`, plus dicts `bodyseg_to_mjcfbody`,
  `bodyseg_to_mjcfgeom`, `jointdof_to_mjcfjoint`, `jointdof_to_mjcfactuator_by_type`,
  `leg_to_adhesionactuator`, `anatomicaljoint_to_mjcfsites`,
  `eyecameraname_to_mjcfcamera`.
- Everything is keyed by **FlyMimic's own MJCF strings** (`"LFFemur"`,
  `"joint_LFCoxa_yaw"`, `"LFTibia_flex_93434"`), because FlyMimic's topology does not
  map 1:1 onto flygym's `BodySegment` names.
- `build_musculoskeletal_simulation(*, xml_path=DEFAULT_MUSCULOSKELETAL_XML,
  name="nmf", add_vision=False) -> tuple[Simulation, MusculoskeletalFly]` — CPU,
  single-world `flygym.Simulation`, **not** `flygym.warp.GPUSimulation`. GPU helpers
  `check_mjwarp_compatibility` / `build_musculoskeletal_gpu_simulation` lazily import
  `mujoco_warp` and need the `[warp]` extra.
- `MUSCULOSKELETAL_MESH_DIR = "neuromechfly_musculoskeletal_meshes_20260623a"` — meshes
  are **not** bundled with the MJCF; they are lazily downloaded
  (`flygym.utils.assets_lazy_loading.lazy_load_asset_dir`).
- `DEFAULT_SCENE_CAMERA = "scene"` — a name flygym assigns to FlyMimic's otherwise
  unnamed world camera.
- Pair with `MusculoskeletalWorld` from `flygym.compose.world.musculoskeletal`.
- Docs: tutorial "6. Muscle-based imitation learning" at
  https://neuromechfly.org/tutorials/6_muscle_imitation/ (JS-rendered; **[?]** contents
  not read).

## 11. DOI appendix (all Crossref-verified this session) [V]

| work | DOI |
|---|---|
| Ozdil et al. 2025/2026 FlyMimic (arXiv only) | 10.48550/arXiv.2509.06426 |
| NeuroMechFly v1 (Lobato-Rios 2022, Nat Methods) | 10.1038/s41592-022-01466-7 |
| NeuroMechFly v2 (Wang-Chen 2024, Nat Methods) | 10.1038/s41592-024-02497-y |
| flybody (Vaxenburg 2025, Nature) | 10.1038/s41586-025-09029-4 |
| flybody preprint (2024, bioRxiv) | 10.1101/2024.03.11.584515 |
| Ozdil grooming (2026, Nat Commun) | 10.1038/s41467-026-72152-x |
| Ozdil grooming preprint (2024, bioRxiv) | 10.1101/2024.12.17.628844 |
| SeqIKPy (2026, JOSS) | 10.21105/joss.08557 |
| VNC connectome (Azevedo 2024, Nature) | 10.1038/s41586-024-07389-x |
| Leg/wing premotor networks (Lesser 2024, Nature) | 10.1038/s41586-024-07600-z |
| X-ray holographic nano-tomography (Kuan 2020, Nat Neurosci) | 10.1038/s41593-020-0704-9 |
| Campaniform sensilla (Dinges 2021, J Comp Neurol) | 10.1002/cne.24987 |
| Haustein 2024 leg model (Front Bioeng Biotechnol) | 10.3389/fbioe.2024.1357598 |
| Millard 2013 muscle model (J Biomech Eng) | 10.1115/1.4023390 |
| Ache & Matheson 2013 passive joint forces (Curr Biol) | 10.1016/j.cub.2013.06.024 |
| Swank 2012 IFM/jump muscle mechanics (Methods) | 10.1016/j.ymeth.2011.10.015 |
| Eldred 2010 jump muscle properties (Biophys J) | 10.1016/j.bpj.2009.11.051 |
| Guo 2018 ant neuro-musculo-skeletal model (Sci Rep) | 10.1038/s41598-018-20093-x |

No DOI could be verified for: Miller 1950 (book chapter, FlyBase FBrf0007735);
Ozdil's PhD thesis; the ICLR 2026 proceedings entry.
