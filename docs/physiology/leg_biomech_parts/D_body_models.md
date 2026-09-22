# D. Rigged body models: driving a fly from per-muscle motor-neuron output

Scope: which existing, scientifically grounded *Drosophila* body models can (i) visualise
attempted movement driven by our per-muscle motor-neuron drives, and (ii) serve as the physics
behind proprioception.

Companion files. Deep dives in this folder: `flybody.md`, `flymimic_paper_and_repo.md`,
`connectome_driven_sim_and_mn_muscle_lit.md`. Per-source notes with verbatim passages in
`docs/research/sources/`: `lobatorios_2022.md`, `wangchen_2024.md`, `vaxenburg_2025.md`,
`ozdil_2026_flymimic.md`, `gizemozd_flymimic_repo.md`, `azevedo_2020.md`, `azevedo_2024.md`,
`azevedo_2024_fanc.md`, `cheong_2024.md`, `lesser_2024.md`, `marin_2024_manc_annotation.md`,
`mamiya_2018.md`, `mamiya_2023.md`, `pugliese_2026_connectome_cpg.md`.

Everything below was checked against the actual repo, XML or paper unless marked "(2nd)" for
second-hand or "(E)" for estimate. The NeuroMechFly, flybody and FlyMimic numbers come from
clones made on 2026-09-21: `flygym` @ `38c8ec61` (v2.1.0) and tag `v1.2.1`,
`flybody` @ `d015e9bf`, `NeuroMechFly` @ `6fdc6212`, `FlyMimic` @ HEAD.

---

## D.1 The one-paragraph answer

There are three usable bodies and they are not interchangeable. **NeuroMechFly v2 / flygym**
(Apache-2.0, MuJoCo) is a six-legged walking fly with 42 actuated leg DoFs, adhesion, vision,
olfaction and a mature Gym-style sensor API — but it is driven by **joint position servos**, so our
per-muscle drives have to be collapsed into joint setpoints before they touch it. **flybody**
(Apache-2.0, MuJoCo) is a slightly richer whole-body fly with wings and flight, 8 leg actuators per
leg, also position servos, also no muscles. **FlyMimic** (Özdil et al., ICLR 2026; Apache-2.0,
MuJoCo, and already vendored inside flygym 2.1.0) is the only model with **Hill-type muscles** —
15 muscle–tendon units whose names are, almost literally, our muscle groups — but it covers **one
leg**, the left front, on a tethered thorax, with no adhesion and no contact sensors.

So: FlyMimic is the only model that can take our drive vector *as a drive vector*. It cannot walk.
NeuroMechFly v2 can walk and can be read for proprioception, but only after we throw away the
per-muscle structure. The honest architecture is to use both, for different claims.

### D.1.1 Side by side

| | NeuroMechFly v1 | **NeuroMechFly v2 / flygym** | **flybody** | **FlyMimic** |
|---|---|---|---|---|
| paper | Lobato-Rios 2022, *Nat Methods* 19:620–627 | Wang-Chen 2024, *Nat Methods* 21:2353–2362 | Vaxenburg 2025, *Nature* 643:1312–1320 | Özdil, ICLR 2026, arXiv:2509.06426 |
| DOI | 10.1038/s41592-022-01466-7 | 10.1038/s41592-024-02497-y | 10.1038/s41586-025-09029-4 | — (arXiv) |
| repo | `NeLy-EPFL/NeuroMechFly` | `NeLy-EPFL/flygym` | `TuragaLab/flybody` | `gizemozd/FlyMimic` (+ vendored in flygym) |
| licence | Apache-2.0 | Apache-2.0 | Apache-2.0 (no holder named) | Apache-2.0 |
| engine | PyBullet (unpinned) | MuJoCo `>=3.9,<3.10` | MuJoCo (unpinned, via dm_control) | MuJoCo (via flygym) |
| total DoFs | 92 revolute (+3 tether) | **87 hinge** (+6 free = 93) | **108** (1 free + 102 hinge) | 7 driven (LF leg), rest locked/passive |
| DoFs per leg | 11 (7 actuated) | **11 (7 actuated)** | **11 (8 actuated)** | 7, all muscle-driven |
| leg joint names | `joint_{L,R}{F,M,H}{Coxa,Coxa_roll,Coxa_yaw,Femur,Femur_roll,Tibia,Tarsus1-5}` | same | `<seg>[_abduct\|_twist]_T{1,2,3}_{left,right}` | `joint_LF{Coxa,Trochanter}_{yaw,pitch,roll}`, `joint_LFTibia_pitch` |
| trochanter | fused into femur | fused (`trochanterfemur`) | fused (`femur_twist`) | **separate body** |
| actuation | position | position servo, kp 45, forcerange 65 | position servo, kp 0.8 coxa/femur, 0.4 tibia/tarsus | **15 Hill-type muscles**, ctrl ∈ [0,1] |
| muscles | none | none | none | **yes** (`dyntype=muscle`, spatial tendons) |
| adhesion | no | 6 MuJoCo adhesion actuators, force 40 | 6 claw + 2 labrum, gain 0.985 | **none** |
| joint angle / velocity out | yes | yes (`jointpos`/`jointvel` sensors) | yes (via `qpos`/`qvel`, no MJCF sensors) | yes (via `qpos`/`qvel`) |
| load / contact out | contact | per-leg contact force/torque/normal/tangent; 36-body GRF | 6 tarsal `force` + 6 claw `touch`, nothing proximal | none |
| campaniform / chordotonal / hair plate | no | **no** | **no** | **no** |
| physics timestep | — | 1e-4 s | 1e-4 s (tasks 2e-4 walking) | 1e-4 s |
| shipped control rate | — | any (controllers run per physics step) | 500 Hz walking, 5 kHz flight | 500 Hz |
| 10 ms frames? | — | yes, step 100× | yes, but gains tuned at 2 ms | yes, step 100× |
| default controller | CPG optimised by evolution | CPG / rule-based / hybrid / turning, all → joint angles | DMPO (acme+TF+Ray) imitation policies | PPO imitation of mocap by muscle activation |
| walks? | yes | **yes** | **yes** (+ flies) | **no** — tethered single leg |

---

## D.2 NeuroMechFly v1 (2022, PyBullet) — superseded, do not use

Lobato-Rios, Tata Ramalingasetty, Özdil, Arreguit, Ijspeert, Ramdya, *Nature Methods* 19(5):620–627
(2022), doi:10.1038/s41592-022-01466-7. Repo `NeLy-EPFL/NeuroMechFly`, licence **Apache-2.0**
(verbatim Apache 2.0 `LICENSE`; `setup.py` `license='Apache 2.0'`). Physics **PyBullet**, unpinned.
Repo README itself says it is legacy and unmaintained.

Body is an **SDF**, `data/design/sdf/neuromechfly_noLimits.sdf`: 96 links, 95 joints — 92 revolute,
1 continuous and 2 prismatic (the last three being the tether rig). Per leg **11 revolute joints**:
`Coxa`, `Coxa_roll`, `Coxa_yaw`, `Femur`, `Femur_roll`, `Tibia`, `Tarsus1`–`Tarsus5` (66 across six
legs). The commonly quoted **"7 DoFs per leg"** refers to the seven that are *actuated* —
ThC pitch/roll/yaw, CTr pitch/roll, FTi pitch, TiTa pitch — with the four distal tarsal joints
passive. Joint names verified from the SDF; the actuated/passive split is confirmed explicitly for
v2 and inherited (2nd for v1).

v1 has joints v2 later dropped: abdomen A1A2–A6, wings (3 DoF/side), halteres (3 DoF/side),
proboscis (rostrum, haustellum), and one lumped antennal joint per side.

Actuation: per-joint PyBullet position control. No muscles, no tendons (2nd). Sensing goes through
a Cython `bullet_sensors` extension; joint state and ground contact only, no campaniform or
chordotonal model (2nd).

**Verdict: no.** Unmaintained, wrong engine, strictly dominated by v2.

---

## D.3 NeuroMechFly v2 / flygym (MuJoCo) — the walking body

Wang-Chen, Stimpfling, Lam, Özdil, Genoud, Hurtak, Ramdya, *Nature Methods* (2024),
doi:10.1038/s41592-024-02497-y. Repo `NeLy-EPFL/flygym`, docs neuromechfly.org.
Licence **Apache-2.0** (verbatim `LICENSE`; `pyproject.toml` `license = "Apache-2.0"`).
Engine **MuJoCo**; current main (package version **2.1.0**) pins `mujoco>=3.9,<3.10`, optional
`mujoco_warp>=3.9,<3.10` for a batched GPU path. The 2.1.0 release migrated model editing from
dm_control PyMJCF to MuJoCo's native `MjSpec`, and renamed most of the API — the paper-era API is
tag **v1.2.1** and that is what the published figures used.

### D.3.1 Degrees of freedom — the "87 joints" figure is real

Counted directly from the paper-era MJCF `flygym/data/mjcf/neuromechfly_seqik_kinorder_ypr.xml`
at tag v1.2.1: **70 bodies, 87 joints, every one `type="hinge"`**. There is no free joint inside
the fly XML; the 6-DoF free joint is added when the fly is attached to an arena, so a freely
spawned fly has **93 DoFs**.

| group | count | notes |
|---|---|---|
| leg joints | **66** | 11 per leg × 6 |
| neck/head | 3 | `joint_Head` (pitch), `_roll`, `_yaw` |
| antennae | 18 | 9 per side: pedicel, funiculus, arista × pitch/roll/yaw |
| wing, haltere, abdomen, proboscis | **0** | fused rigid (`fusestatic: true`) |
| **total** | **87** | + 6 free-joint DoFs when spawned free |

Of the 66 leg joints, **42 are actuated (7 per leg)** and 24 are passive tarsal joints
(`Tarsus2`–`Tarsus5`, stiffness 7.5, damping 1e-2). The SI states it flatly: *"Each walking step:
42 actuated leg degrees of freedom (DoFs, 7 per leg) playing out pre-programmed stepping
sequences."*

### D.3.2 Leg DoF names and conventions

Paper-era names (`flygym/preprogrammed.py`, `all_leg_dofs`):
`joint_{L,R}{F,M,H}{Coxa, Coxa_roll, Coxa_yaw, Femur, Femur_roll, Tibia, Tarsus1}`.

| MJCF suffix | anatomical joint | axis | our motor pools that act on it |
|---|---|---|---|
| `Coxa` | ThC (thorax–coxa) | pitch | coxa promotor / remotor |
| `Coxa_roll` | ThC | roll | coxa abductor, sternal adductor |
| `Coxa_yaw` | ThC | yaw | sternal anterior/posterior rotators |
| `Femur` | CTr (coxa–trochanter) | pitch | trochanter flexor / extensor, sternotrochanter |
| `Femur_roll` | CTr | roll | femur reductor |
| `Tibia` | FTi (femur–tibia) | pitch | tibia flexor / extensor |
| `Tarsus1` | TiTa (tibia–tarsus) | pitch | tarsus levator / depressor, **long tendon muscle** |

Axis convention, `flygym/anatomy.py` `class RotationAxis`: `pitch → y (0,1,0)`,
`roll → z (0,0,1)`, `yaw → x (1,0,0)`. Euler composition order is explicit and selectable
(`AxisOrder`, six permutations); the default MJCF is `kinorder_ypr`, yaw–pitch–roll. This matters
if we ever compare our joint angles against published kinematics, which are usually expressed in a
different order.

Note the model fuses trochanter and femur into one link — flygym 2.1.0 names it
`trochanterfemur` outright. FlyMimic does **not** fuse them; it has a separate `LFTrochanter` body.
So the two models' kinematic chains differ at exactly the joint where our trochanter muscle pools
act.

flygym 2.1.0 renames DoFs to `{parent}-{child}-{axis}`, e.g. `lf_coxa-lf_trochanterfemur-pitch`,
and re-adds abdomen/wing/haltere/proboscis joints: computed from `anatomy.py`, the `ALL_BIOLOGICAL`
preset now gives 68 anatomical joints, 69 segments and 126 rotational DoFs, still 66 of them leg
DoFs and still 42 under `LEGS_ACTIVE_ONLY`.

### D.3.3 Actuation — position servos, definitively not muscles

`Fly(control="position")` by default; `"velocity"` and `"torque"` also accepted. The published
defaults, from the v1.2.1 constructor and confirmed verbatim in the Methods (*"We used a joint
position gain kp of 45 and an adhesion force of 40 mN for all controllers"*):

| parameter | value |
|---|---|
| `actuator_gain` = MuJoCo `kp` | **45.0** |
| `actuator_forcerange` | **65.0** |
| joint stiffness / damping (actuated) | 0.05 / 0.06 |
| non-actuated joint stiffness / damping | 1.0 / 1.0 |
| neck stiffness | 10.0 |
| tarsus stiffness / damping | 7.5 / 1e-2 |
| friction | (1.0, 0.005, 0.0001) |
| `contact_solref` | (2e-4, 1e3) |

There are no muscle or tendon actuators in the NeuroMechFly body. flygym 2.1.0's `ActuatorType`
enum does list `MUSCLE` and `TENDON`, and `Simulation` has `set_tendon_actuator_inputs()`, but
those exist to serve FlyMimic (§D.5), not this body. The paper says so itself, twice: the
Discussion asks for *"careful measurements and analyses of the Drosophila musculoskeletal system
(i.e., tendons and muscles) [to] improve the interface between neural network controllers and the
biomechanical embodiment"*, and the SI feature table lists **"Inclusion of motor neurons and
muscle models"** under *Future potential*, citing Kuan et al. (X-ray holographic nano-tomography)
and Azevedo et al., *eLife* 9:e56754. That is our project's exact gap, named by the authors as
unbuilt in 2024.

### D.3.4 Adhesion — yes, and it is controllable per-leg per-step

Six MuJoCo built-in `adhesion` actuators, one on each leg's `tarsus5` geom, `ctrl ∈ [0,1]`,
default force 40 (paper says 40 mN). Methods: *"Adhesion takes the form of an artificial force
injected normal … [when] multiple contacts occur … the force is equally divided between these"*,
and *"We controlled adhesion in a binary fashion but it is possible to use a gradient of adhesion
forces by modulating the input to the adhesion actuator at every time step."* The adhesion
contribution is subtracted back out of the reported contact forces, so the contact observation is
true ground reaction force.

### D.3.5 Sensors and observations — where proprioception would come from

MuJoCo sensors actually instantiated: per actuated joint `jointpos`, `jointvel`, `actuatorfrc`;
per monitored non-actuated joint pos/vel plus a 4-component torque reduced to its norm; body
`framepos`/`framelinvel`/`framequat`/`frameangvel`; and per-body `force` sensors at the
contact-sensor placements (default = tibia + tarsus1–5 on all six legs = 36 bodies).

Paper-era Gym observation space:

| key | shape | contents |
|---|---|---|
| `joints` | (3, 42) | angle (rad), angular velocity (rad/s), joint force (`actuatorfrc`, ×1e-9 → N) |
| `fly` | (4, 3) | thorax position, linear velocity, (pitch,roll,yaw) extrinsic ZYX, angular velocity |
| `fly_orientation` | (3,) | unit vector along the A–P axis |
| `cardinal_vectors` | (3, 3) | body-frame axes |
| `contact_forces` | (36, 3) | ground reaction force per contact body |
| `end_effectors` | (6, 3) | tarsus5 tip positions |
| `vision` (optional) | (2, 721, 2) | 721 ommatidia/eye, 70 % yellow / 30 % pale |
| `odor_intensity` (optional) | (k, 4) | 2 antennae + 2 maxillary palps |

Action space: `joints ∈ R^42`, `adhesion ∈ {0,1}^6`.

flygym 2.1.0 replaces the dict with explicit getters on `Simulation`: `get_joint_angles`,
`get_joint_velocities`, `get_actuator_forces(fly, ActuatorType)`, `get_body_positions`,
`get_body_rotations`, `get_site_positions`, `get_bodysegment_contact_forces`, and
`get_ground_contact_info(fly)` which returns a per-leg 6-tuple — `found (6,)`, `force (6,3)`,
`torque (6,3)`, `pos (6,3)`, `normal (6,3)`, `tangent (6,3)`. Setters: `set_actuator_inputs`,
`set_leg_adhesion_states`, `set_tendon_actuator_inputs`.

**There is no observation called "proprioception".** What the paper calls *ascending motor
feedback* is, concretely, leg joint angles plus ground-contact flags into an MLP: SI, *"Shown in
examples: Leg stride lengths for path integration; Leg joint angles and ground contacts for head
stabilization"*. That is the whole of it.

The docs use the word loosely to mean the same thing. Grepping the entire flygym repo for
"proprio" returns exactly two hits, both in the muscle-imitation tutorial, and the operative one is
a code comment: `sim.get_joint_angles(fly.name)   # proprioception, body kinematics, ...`.
So: **proprioception in flygym is `get_joint_angles`, plus whatever else you choose to read.**
Grepping for "campaniform", "chordotonal", "hair plate" and "sensilla" across the whole repo
returns nothing at all.

### D.3.6 Load and strain sensing — absent everywhere

**No campaniform sensilla, no chordotonal organ (femoral or otherwise), no hair plates** are
modelled in flygym, flybody or FlyMimic. I grepped all three. The phrase "hair plate" occurs once
in the NeuroMechFly v2 paper and it is anatomical prose about where the neck sits, not a sensor.

The nearest available substitutes, and what they would actually be standing in for:

| real organ | best proxy in NeuroMechFly v2 | fidelity |
|---|---|---|
| femoral chordotonal organ (claw/hook/club) | `jointpos` + `jointvel` on `joint_*Femur`/`*Tibia` | position and velocity yes; the club's vibration channel no |
| campaniform sensilla (cuticular strain) | per-leg contact force/torque from `get_ground_contact_info`, or `actuatorfrc` | wrong quantity — GRF at the tarsus, not strain distributed over the leg cuticle |
| tarsal/tibial hair plates | joint angle near its limit | crude; a hair plate is a threshold detector at an extreme of a joint's range, which joint angle can approximate with a sigmoid (E) |

If we want load sensing with any claim to realism, the honest options are (a) `actuatorfrc`, which
in a position-servo model is a *control* signal and not a mechanical load, or (b) MuJoCo
`<force>`/`<torque>` sensors added at sites on the leg segments, which we would have to insert
ourselves. Neither is a campaniform sensillum. FlyMimic's `actuator_force` on a Hill-type muscle is
much closer to a real tendon load, which is one more reason to keep FlyMimic in the loop.

flybody is the cheapest place to add proximal load sensing, because it already has the pattern:
six `force` sensors on the tarsus5 sites and six `touch` sensors on the claws. Adding a
`<force>`/`<torque>` sensor at a site on each femur and tibia is a few lines of XML.

If we ever want to do this properly rather than by proxy, the modelling literature exists:
- Saltin, Goldsmith, Haustein, Büschges et al., *"A parametric finite element model of leg
  campaniform sensilla in Drosophila"*, *J R Soc Interface* **22** (2025),
  doi:10.1098/rsif.2024.0559 — a finite-element strain model, not a real-time sensor, but it is the
  reference for what a campaniform sensillum actually measures.
- Cocatre-Zilgien & Delcomyn, *"Modeling stress and strain in an insect leg for simulation of
  campaniform sensilla responses to external forces"*, *Biol Cybern* **81**:149–160 (1999),
  doi:10.1007/s004220050551 — the classic, and closer to something we could run online.
- Dallmann, Karashchuk, Brunton & Tuthill, *"A leg to stand on: computational models of
  proprioception"*, *Curr Opin Physiol* **22**:100426 (2021), doi:10.1016/j.cophys.2021.03.001 —
  the how-to-model-a-proprioceptor review; read this before writing any FeCO model.
- Karashchuk, Li, Chou et al., *"Sensorimotor delays constrain robust locomotion in a 3D kinematic
  model of fly walking"*, *eLife* reviewed preprint doi:10.7554/eLife.99005 — directly about how
  much proprioceptive delay a fly-walking model can tolerate, which bears on our 10 ms frame.

### D.3.7 Timestep — 10 ms frames are fine

Physics timestep defaults to **1e-4 s**: `Simulation(timestep=0.0001)` at v1.2.1 and
`option: timestep: 1e-4` in `mujoco_globals.yaml` at 2.1.0, with `integrator: Euler`,
`solver: Newton`, `iterations: 100`, `noslip_iterations: 5`, `gravity: [0,0,-9810]` mm/s².
Control rate is independent of physics rate. A 10 ms control frame means holding the control vector
and calling `sim.step()` **100 times**. This is exactly how flygym's own controllers run.

10 ms is coarse relative to fly leg dynamics — a tripod step at 10 Hz is ~100 ms, so we get ~10
control updates per step cycle — but it is not absurd, and it is on the same order as the ~5–10 ms
smoothing you would need anyway to turn spike counts into a usable drive.

### D.3.8 Default controllers

CPG (coupled phase oscillators adapted from a salamander model; SI Note 4, Supp. eqs 1–4),
rule-based (Walknet lineage), **hybrid** (CPG plus stepping-phase-dependent corrective rules — the
one used for most of the paper's demos), and a turning controller taking a two-element "DN drive"
with DNmin = 0.2, DNmax = 1. All of them output **target joint angles** drawn from a preprogrammed
step cycle and scaled by CPG amplitude. Repo tutorials `4a`–`4d`.

This matters for us: every shipped controller produces joint setpoints. If we drive the model from
motor neurons we are replacing the entire control stack, not slotting into it.

### D.3.9 Connectome-driven precedent

The Methods software list names **"FlyVision commit 056e4aa for connectome-constrained visual
system simulation"**. The demo is the flygym **1.x** tutorial `advanced_vision`, titled
*"Connectome-constrained visual system model"* (Thomas Ka Chung Lam, Sibo Wang-Chen), verbatim:
*"we will (1) simulate two flies in the same arena, and (2) integrate a connectome-constrained
visual system model (Lappalainen et al., 2024) into NeuroMechFly."* Notebook
`notebooks/advanced_vision.ipynb`, code `flygym/examples/vision/`, gallery
`video_14_fly_follow_fly.rst`. The network reads T1–T5/Tm/TmY for object detection and **modulates a
descending turning signal** into the hybrid controller — sensory side only, it never touches motor
neurons. Figure 5 reports *"Object detection score and activity patterns of 34 putative output
columnar neuron types (of 65 total)"*.
Lappalainen et al., *Nature* **634**:1132–1140 (2024), doi:10.1038/s41586-024-07939-3;
code `TuragaLab/flyvis`, MIT.

Two operational warnings:
1. **flygym 2.x dropped the vision tutorials entirely.** The 2.1.0 tutorial list is
   `1a, 1b, 2, 3, 4a–4d, 5a, 5b, 6_muscle_imitation, 7_performance_profiling`. The 1.x docs and
   notebooks live at `NeLy-EPFL/flygym-gymnasium` and at tag `v1.1.0` of the main repo.
2. **`neuromechfly.org` was serving a GoDaddy parking page as of 2026-09-21** (a 114-byte JS stub
   redirecting to `/lander`); `gymnasium.neuromechfly.org` did not connect. Read the docs from the
   repo, e.g.
   `https://raw.githubusercontent.com/NeLy-EPFL/flygym/v1.1.0/doc/source/tutorials/advanced_vision.rst`.

On the motor side, see §D.6: nobody has published a connectome motor-neuron → actuator mapping for
any of these bodies.

---

## D.4 flybody (MuJoCo, Janelia) — the other whole-body fly

Vaxenburg, Siwanowicz, Merel, Robie, Morrow, Novati, Stefanidi, Both, Card, Reiser, Botvinick,
Branson, Tassa, Turaga, *Nature* **643**:1312–1320 (2025), doi:10.1038/s41586-025-09029-4
(DOI verified). Preprint bioRxiv doi:10.1101/2024.03.11.584515 v2, under a different title.
Data: figshare doi:10.25378/janelia.25309105.
Repo `TuragaLab/flybody`, HEAD `d015e9bf` (2025-07-30); mirrored in
`google-deepmind/mujoco_menagerie/flybody`; vendored in flygym 2.1.0.

Licence **Apache-2.0** (verbatim boilerplate, SPDX `Apache-2.0`) — but the appendix still carries
the unfilled template `Copyright [yyyy] [name of copyright owner]`, so **no copyright holder is
named anywhere in the repo**. Worth knowing before we redistribute anything derived from it.

Warning: flygym 2.1.0's docstring cites this DOI under a *wrong* title ("A whole-body model of
Drosophila with precise neuromuscular connectivity"). Do not copy that citation.

Dependencies (`pyproject.toml`, no setup.py or requirements.txt): `numpy==1.26.4`, `dm_control`
**unpinned**, h5py, mediapy, pytest; Python ≥3.10. **There is no mujoco pin at all** — MuJoCo
arrives transitively through dm_control. The `[tf]` extra pulls `dm-acme[tf,envs,jax]`,
`tensorflow==2.8.0`, `tensorflow-probability==0.16.0`, `dm-reverb==0.7.0`, `protobuf==3.20.*`.

Units are **cm, g, s** (gravity `0 0 -981`), unlike NeuroMechFly's mm — force unit dyne = 10 µN.

### D.4.1 Degrees of freedom — measured by compiling the model

Compiled with mujoco 3.13.0: `nq=109  nv=108  nu=78  na=0  njnt=103  nbody=68  ngeom=159
nsite=15  ntendon=8  nsensor=15`. That is **1 free joint + 102 hinges**, no slide or ball joints.

| group | DoFs |
|---|---|
| legs | **66** (11 per leg × 6) |
| abdomen | 14 (7 segments × abduct/extend) |
| wings | 6 |
| antennae | 6 |
| proboscis | 5 (`rostrum`, `haustellum_abduct`, `haustellum`, `labrum_left`, `labrum_right`) |
| head/neck | 3 |
| halteres | 2 (passive, no actuator) |
| free joint | 6 |
| **total** | **108** |

So flybody is a richer body than NeuroMechFly v2 — wings, abdomen, proboscis are all articulated
where v2 fuses them — but the **leg count is identical at 11 DoFs per leg**.

Front-left leg, exact joint names:
`coxa_abduct_T1_left`, `coxa_twist_T1_left`, `coxa_T1_left`, `femur_twist_T1_left`,
`femur_T1_left`, `tibia_T1_left`, `tarsus_T1_left`, `tarsus2_T1_left` … `tarsus5_T1_left`.
Convention `<segment>[_abduct|_twist]_<T1|T2|T3>_<left|right>`; **abduct = z axis, twist = y,
bare name = x** (extension/flexion). Radians.

flybody does **not** use ThC/CTr/FTi/TiTa nomenclature, and like NeuroMechFly it has **no
trochanter body** — the trochanter is fused into the femur and its rotation appears as
`femur_twist_*`. (flygym's re-parse of flybody renames everything into flygym's own scheme:
`c_thorax-lf_coxa-pitch`, `lf_coxa-lf_trochanterfemur-roll`, etc.)

### D.4.2 Actuation — position servos, 8 per leg, no muscles

78 actuators = **70 `<general>` + 8 `<adhesion>`**. `na=0`, no `dyntype="muscle"` anywhere:
**there is no muscle model**.

The 70 are position servos (`gaintype=fixed`, `biastype="affine"`, `biasprm="0 -kp"`,
`ctrlrange` = the joint's range, so `ctrl` is a target angle). kp by class: coxa/femur **0.8**,
tibia/tarsus **0.4**, head/rostrum/haustellum 0.1, abdomen 0.1, labrum and antenna 0.01.
**Wings are the exception** — no `biastype`, so pure torque, `gainprm` 3 / 2 / 1 for
yaw / roll / pitch, `ctrlrange ±1`.

Methods, verbatim: *"8 actuators in each leg (coxa: 3, femur: 2, tibia: 1, tarsus: 2), using
desired angle (position) semantics, with gains chosen so that a force of approximately one body
weight can be applied at the end-effector at the base pose"*, and *"6 adhesion actuators at the
claws which can apply a force up to 1× body weight."*

Transmission: 62 joint-transmission + **8 tendon-transmission**. `abduct_abdomen` and `abdomen`
each sum 7 joints (coef 1), collapsing 14 abdominal DoFs to 2 commands; one tendon per leg
(`tarsus2_T*_*`) couples tarsomere 2 (coef 1) to tarsomeres 3/4/5 (coef 0.5), collapsing 4 DoFs
to 1 per leg. That is why the leg has 11 DoFs but 8 actuators.

**Default walking action dimension 59** = 48 leg (6 × 8) + 6 claw adhesion + 3 head + 2 abdomen.

At runtime `force_actuators=True` strips `biastype`/`ctrlrange` and switches the whole model to
torque control — which is our lever if we want a torque mapping rather than a position mapping.
`joint_filter=0.01` / `adhesion_filter=0.007` add `dyntype="filter"` first-order actuator dynamics.

### D.4.3 Sensors — sparse, and no proximal load channel

**15 sensors, sensordim 33**: 1 accelerometer + 1 gyro + 1 velocimeter (all on the thorax site),
**6 `force`** (`force_tarsus_T{1,2,3}_{left,right}`, 3-vector, on the tarsus5 sites), and
**6 `touch`** (`touch_claw_*`, scalar, on claw sites).

There are **no `jointpos`, `jointvel`, `actuatorfrc`, `torque`, `framequat`, `framepos` or
`rangefinder` sensors in the MJCF at all**. Joint angle and velocity reach the observation via
dm_control observables reading `qpos`/`qvel` directly. This is a real difference from
NeuroMechFly, which does instantiate per-joint MuJoCo sensors.

Campaniform-sensillum stand-in: only the 6 distal tarsal force sensors. **Nothing proximal** — no
femoral, tibial or coxal load channel. Adding them is a trivial XML edit (a `<force>`/`<torque>`
sensor at a site on each segment), and if we want load feedback this is probably the cheapest
place in any of these models to get it.

### D.4.4 Observables — exact strings

`template_task()` spec, verified from the repo's own test assertions:
`walker/accelerometer`, `walker/actuator_activation`, `walker/appendages_pos`, `walker/force`,
`walker/gyro`, `walker/joints_pos`, `walker/joints_vel`, `walker/touch`, `walker/velocimeter`,
`walker/world_zaxis`.

`walk_imitation()` adds `walker/ref_displacement`, `walker/ref_root_quat`.
Vision flight adds `walker/task_input` plus eye cameras; `walk_on_ball` adds `walker/ball_qvel`.
Defined but off by default: `thorax_height`, `abdomen_height`, `world_zaxis_hover`,
`world_zaxis_abdomen`, `world_zaxis_head`, `self_contact`, `left_eye`, `right_eye`.
`appendages_pos` = egocentric xyz of the 6 claw sites + head site (21 numbers).

### D.4.5 Timesteps — 10 ms is mechanically fine, but the gains were not tuned for it

MJCF: `<option timestep="0.0001" gravity="0 0 -981" density="0.00128" viscosity="0.000185"
cone="elliptic" noslip_iterations="3"/>`.
Tasks (`tasks/constants.py`): walking physics 2e-4 s, control **2e-3 s (500 Hz)**;
flight physics 5e-5 s, control 2e-4 s.

Both are plain constructor arguments into `set_timesteps`; control only needs to be an integer
multiple of physics, and it also sets the observable-averaging `buffer_size = control/physics`.
So 10 ms control is a one-line change. **Caveat (unverified):** the actuator gains and the 0.01 s
joint filter were tuned at 2 ms, so the shipped policies will not transfer to 10 ms and leg
control may go unstable there.

### D.4.6 Adhesion

Native MuJoCo `<adhesion>`, not sticky contacts. 6 claw actuators
`adhere_claw_T{1,2,3}_{left,right}`, `ctrlrange="0 1"`, `gain="0.985"`, plus 2 labrum ones at
`gain="1"`. The `adhesion-collision` default class gives those geoms `friction="0.6"
margin="0.0005" gap="0.0005"` — the margin/gap band is what lets adhesion pull across a
near-contact with no normal force. `adhesion_filter=0.007` s gives ~7 ms grip on/off dynamics.
Adhesion is 6 of the 59 walking actions, so a policy sets per-foot stickiness.

### D.4.7 Controllers shipped

Tasks: `walk_imitation` (mocap ghost, 10 s), `flight_imitation` (0.6 s, with a wingbeat pattern
generator), `vision_guided_flight` (0.4 s), `walk_on_ball` (tethered, 2 s), `template_task`.
Algorithm: **distributed DMPO on DeepMind acme + TensorFlow/sonnet, parallelised with Ray**
(`train_dmpo_ray.py`, `agents/ray_distributed_dmpo.py`, `agents/losses_mpo.py`).
Four figshare checkpoint bundles are downloadable (`download_data.py`): `trained-policies`
(44815195), `walking-imitation-dataset` (51196868), `flight-imitation-dataset` (51196859),
`controller-reuse-checkpoints` (51196886). Checkpoints are TF/sonnet, so loading them needs the
`[tf]` extra with `tensorflow==2.8.0`.

### D.4.8 Passive parameters are not measurements

Leg joint stiffness and damping in the MJCF are **hand-chosen model values**. Only the *wing*
actuator gain and wing damping were fitted, against Dickson et al. 2008 hovering kinematics.
Do not cite flybody's leg stiffness/damping as fly biomechanics. (Verified by grepping the full
methods for "damping": only wing damping is discussed.)

Body mass, by contrast, is measured: head 0.15 mg, thorax 0.34 mg, abdomen 0.38 mg, each leg
0.0162 mg, each wing 0.008 mg, total **0.983 mg**; body length 2.97 mm, wingspan 6.04 mm; adult
wild-type female, from weighing two groups of 30 and 22 disassembled flies.

### D.4.9 flygym's vendored copy is the same model

Element-by-element comparison of `flygym/assets/model/flybody/fruitfly.xml` against upstream:
identical counts throughout (102 hinges + free joint, 67 bodies, 159 geoms, 15 sites, 8 tendons,
70 + 8 actuators, 6 force + 6 touch + 3 IMU sensors). **No sensors added, no adhesion added, no
DoFs added.** Seven cosmetic attribute diffs only (a `meshdir`, deleted `<visual>`/`<statistic>`
blocks, and six claw touch-sensor site capsules shortened ~10% to match the collision geoms).

But note: **flygym's `FlyBody` class does not load that XML.** It rebuilds the model from YAML
(`rigging.yaml`, `joints.yaml`, `actuators.yaml`, `visuals.yaml`, `vision.yaml`) via
`flygym/flybody/parse_flybody.py`, in **mm** — lengths ×10, gravity −9810, torque quantities ×100,
so `actuators.yaml` gains read 80 (coxa/femur), 40 (tibia/tarsus), 300/200/100 (wing), 10 (head).
Joints are renamed into flygym's scheme with pitch = x, roll = y, yaw = z (wings swap pitch/roll).
Adhesion is **not present by default** in flygym's FlyBody — you call
`FlyBody.add_leg_adhesion(add_labrum=...)`, which creates `<tarsus5>-adhesion` actuators.

## D.5 FlyMimic (Özdil et al., ICLR 2026) — the only Hill-type fly muscle model

Full parameter tables, the abstract and the repo details are in
`docs/research/sources/ozdil_2026_flymimic.md` and `gizemozd_flymimic_repo.md`. Summary here.

> Özdil PG, Ning C, Phelps JS, Wang-Chen S, Elisha G, Blanke A, Ijspeert A, Ramdya P.
> "Musculoskeletal simulation of limb movement biomechanics in *Drosophila melanogaster*."
> *ICLR 2026*. arXiv:2509.06426.

arXiv v1 8 Sep 2025 / v2 11 Sep 2025, 23 pp, 11 figures, **CC BY 4.0**.
The **only DOI that exists is 10.48550/arXiv.2509.06426** — there is no journal DOI as of
Sept 2026. ICLR 2026 is confirmed from the repo's own BibTeX (`@inproceedings{Ozdil2026}` in
flygym's `docs/tutorials/6_muscle_imitation.md`) and the first author's homepage; OpenReview id
`6lEjX1getx` (2nd); acceptance type not verified. Oddity: arXiv lists **8** authors, the BibTeX and
homepage list **7** and drop Blanke. Repo `gizemozd/FlyMimic`, **Apache-2.0**.

**Where the muscle parameters come from** (verified from the paper and the shipped `.osim`):
OpenSim side is `Millard2012EquilibriumMuscle` × 15 with a **rigid tendon** and
**pennation angle = 0 for every muscle** (zeroed deliberately for cross-engine compatibility, with
Fmax rescaled to compensate). Fmax = specific tension **28 mN/mm²** × PCSA measured from
synchrotron X-ray scans × an optimised scale factor in 0.3–3. That 28 sits between the *Drosophila*
jump muscle's 37 (Eldred 2010) and the indirect flight muscle's 9 (Swank 2012). v_max came from an
X-ray *video* of contraction; l_opt and tendon slack length from CT ratios. The force–length and
force–velocity curves are **OpenSim's human defaults** — the paper states plainly that no measured
fly curves exist. Fitting was **NSGA-II** (`geatpy`) wrapped around an OpenSim
static-optimisation → forward-dynamics loop, with objectives summed over walking and antennal
grooming. Validation is **kinematic only**: DeepLabCut → 5-camera ChArUco → Anipose → SeqIKPy IK,
100 Hz upsampled to 500 Hz, scored as normalised RMSE and r² per DoF plus a moment-arm sign check.
No force, no EMG, no calcium.

Per-muscle Fmax from `best_combined_full.osim` (file declares N but gravity is −9806.65, so lengths
are mm and the force unit is suspect — probably µN; treat as relative weights):
9.32, 46.20, 16.07, 16.32, 50.19, 98.17, 9.08, 66.94, 92.63, 70.48, 15.18, 25.78, 27.45, 41.53,
154.06 — a **16-fold spread**, which is why splitting one motor-pool drive equally across two
sub-branch actuators is not an equal force split.

**Stated limitations that bite us:** Fmax and v_max are estimated, not measured; and
**contact forces are omitted entirely** — no body–body or body–environment interaction. Also:
"motor neuron" appears in the paper as *framing*. FlyWire, FANC, the female VNC connectome and
Lesser 2024 are cited and ~19 muscles / ~69 MNs is asserted, but nothing connectome-derived is
built — the 15-dim policy output is simply *called* "motor neuron activities".
And proprioception: searching the paper for *propriocep / sensill / chordotonal / FeCO / hair
plate* returns exactly one hit, and it is the *title* of a bibliography entry (Dinges 2021).

Converted from an **OpenSim** model by **MyoConverter**; the MJCF header says so verbatim. Now
shipped inside flygym 2.1.0 as `flygym.compose.MusculoskeletalFly` / `MusculoskeletalWorld` /
`build_musculoskeletal_simulation()`, with a demo package `flygym_demo.muscle_imitation`
(PPO imitation learning of mocap by muscle activation) and a tutorial
`docs/tutorials/6_muscle_imitation.md`.

**What it gives us.** 15 MuJoCo `<general class="muscle">` actuators — `dyntype="muscle"`,
`gaintype="muscle"`, `biastype="muscle"`, i.e. genuine Hill-type — each pulling a `<spatial>`
tendon routed through 2–3 sites, all with `ctrlrange="0.0001 1"`. That control range *is* a
normalised per-muscle drive. Activation dynamics `dynprm="0.0001 0.0004 …"`, so τ_act ≈ 0.1 ms and
τ_deact ≈ 0.4 ms — twenty-five to a hundred times faster than our 10 ms frame, which means a
10 ms-held activation is fully resolvable and we are not fighting the model's own filter.

The actuator names are our muscle groups (site names embed the **Miller** thoracic-muscle numbers,
confirming Miller's nomenclature as the anatomical ground truth):

`LFC_tergopleural_promotor_a` (Miller 28a), `LFC_tergopleural_promotor_b` (28b),
`LFC_pleural_remotor_and_abductor` (29), `LFC_pleural_promotor` (30),
`LFC_sternal_anterior_rotator` (31), `LFC_sternal_posterior_rotator` (32),
`LFC_sternal_adductor` (33), `LFF_trochanter_flexor_a`, `LFF_trochanter_flexor_b`,
`LFF_accesory_trochanter_flexor` [sic], `LFF_trochanter_extensor`,
`LFF_sterno-tergo-trochanter_extensor_a`, `LFF_sterno-tergo-trochanter_extensor_b`,
`LFTibia_flex_93434`, `LFTibia_extensor_93932`.

**What it does not give us.** No femur reductor, no tarsus levator, no tarsus depressor, no long
tendon muscle. Left front leg only — the right front leg's seven joints exist but are pinned by
`<equality>` constraints with `polycoef="0 0 0 0 0"`. No adhesion (flygym's wrapper hard-codes
`leg_to_adhesionactuator = {}` and says so in the docstring). No per-leg ground-contact sensors
(`legpos_to_groundcontactsensors_by_fly = None`). **No `<sensor>` block at all** in the MJCF — joint
angles and velocities come straight out of `qpos`/`qvel` and muscle force out of `actuator_force`.
The thorax is anchored to the world: this is a tethered single-leg rig, not a walking fly.

Its seven LF joints, with the passive spring references that NeuroMechFly lacks:

```
joint_LFCoxa_yaw    axis (1,0,0)  range [-0.597 , 0.2745]  springref -0.11
joint_LFCoxa_pitch  axis (0,1,0)  range [-0.5783, 0.7375]  springref  0.35
joint_LFCoxa_roll   axis (0,0,1)  range [ 0.1436, 0.6236]  springref  0.5
joint_LFTrochanter_yaw    axis (1,0,0)  range [-1.196 , 0.2745]  springref -0.1
joint_LFTrochanter_pitch  axis (0,1,0)  range [-3.242 ,-1.217 ]  springref -2.8
joint_LFTrochanter_roll   axis (0,0,1)  range [-0.2745, 1.384 ]  springref  0
joint_LFTibia_pitch       axis (0,1,0)  range [ 0.4789, 2.502 ]  springref  2
```
Default joint class `armature=0.0005, stiffness=0.4, damping=0.02`. MJCF options
`timestep="1e-04"`, `gravity="0 0 -9801"` (mm/s²). Control is at 500 Hz over a 10 kHz physics
timestep in the shipped demo — so a 10 ms (100 Hz) frame is five times coarser than their own
control rate but perfectly steppable.

The tutorial's own comparison table (`docs/tutorials/6_muscle_imitation.md`), verbatim rows:

| aspect | FlyGym default | FlyMimic muscle model |
|---|---|---|
| LF-leg links | `coxa → trochanterfemur (fused) → tibia → tarsus1..5` | `LFCoxa → LFTrochanter → LFFemur → LFTibia → LFTarsus1..5` |
| Actuation | joint position/torque actuators | 15 Hill-type muscles (LF leg) via spatial tendons |
| Passive joints | spring/damper from config | `stiffness = 0.4` + per-joint spring reference angles |
| Other legs | all six actuated | LF muscle-driven; RF locked to 0; LM/LH passive |
| Base | thorax free-floating | thorax tethered (anchored to world) |
| Sensors | vision, contact, proprioception | proprioception + body kinematics; vision optional |

73 bodies, 15 Hill-type muscle actuators, 15 spatial tendons.

**Its observation vector is muscle-level, and that is unusual and useful.** The shipped
`flygym_demo.muscle_imitation` Gym env has
`action_space = Box(0, 1, shape=(n_muscles,))` — one activation per Hill-type muscle — and
`observation_space = Box(-inf, inf, shape=(2·n_tracked_joints + 2·n_muscles + 1,))`, laid out as
**tracked qpos ‖ tracked qvel ‖ muscle activations ‖ muscle forces ‖ time-left scalar**
(45-dim for the shipped clip: 2×7 tracked joints + 2×15 muscles + 1). So it already
gives back, per frame, both the joint-level proprioception we want *and* a per-muscle force
readout — which is the closest thing in this whole ecosystem to a tendon-organ or campaniform
signal, because it is an actual mechanical force in a tendon rather than a servo command.
The reward is FlyMimic's compound imitation reward, `clip((qpos_rew + xpos_rew + qvel_rew)/3, 0, 1)`.

**Repo details, verified by cloning `gizemozd/FlyMimic`** (2026-09-21):
licence **Apache-2.0**, verbatim boilerplate with the copyright line left as the unfilled template
`Copyright [yyyy] [name of copyright owner]` — same situation as flybody, so no holder is named.
Pins: `mujoco==3.3.2`, `dm_control==1.0.30`, `stable-baselines3`, `torch`, `hydra-core`, `wandb`,
Python 3.10+. Structure: `flymimic/{assets,envs,tasks,train,evaluation,utils}`, with
`tasks/fly/mocap_tracking_muscle.py` and `tasks/fly/mocap_tracking_torque.py`, and
`train/train_muscle.py` / `train/train_torque.py` (PPO, Stable-Baselines3).
README points at a second repo `gizemozd/neuromechfly-muscles` for *"the original muscle model
development and parameter optimization in OpenSim"* — that one returned 404 on a raw fetch, so it
may be private or renamed (unverified).

Six MJCF variants ship, all with **exactly the same 15 LF muscles**: `best_combined_cvt3`
(baseline), `_arm_`, `_arm_stiff_`, `_arm_damping_`, `_arm_damping_stiff_` (the one flygym
vendors), and **`best_combined_cvt3_torque.xml`**, which replaces the muscles with seven plain
`<motor>` actuators:

```xml
<motor name="mot_LFCoxa_yaw"        joint="joint_LFCoxa_yaw"        ctrlrange="-0.25 0.25" gear="0.5"/>
<motor name="mot_LFCoxa_pitch"      joint="joint_LFCoxa_pitch"      ctrlrange="-0.6  0.6"  gear="0.5"/>
<motor name="mot_LFCoxa_roll"       joint="joint_LFCoxa_roll"       ctrlrange="-0.1  0.1"  gear="0.5"/>
<motor name="mot_LFTrochanter_yaw"  joint="joint_LFTrochanter_yaw"  ctrlrange="-0.25 0.05" gear="0.5"/>
<motor name="mot_LFTrochanter_pitch" joint="joint_LFTrochanter_pitch" ctrlrange="-1 1"    gear="0.5"/>
<motor name="mot_LFTrochanter_roll" joint="joint_LFTrochanter_roll" ctrlrange="-0.1  0.1"  gear="0.5"/>
<motor name="mot_LFTibia_pitch"     joint="joint_LFTibia_pitch"     ctrlrange="-0.6  0.6"  gear="0.5"/>
```

**That torque variant is exactly the control we want for §D.7.** The same leg, the same mocap, the
same reward, once driven by 15 muscle activations and once by 7 joint torques: the authors have
already built the muscle-vs-joint comparison our per-muscle→per-joint collapse needs. Their own
ablation result — that damping and stiffness *facilitate* imitation learning — is the first hint
of what the collapse costs.

Control rate in both tasks is `control_timestep=0.002` (500 Hz) over the MJCF's 1e-4 s physics.
The middle and hind legs are *annotated* in the paper (reportedly 7 and 8 MTUs) but **no
middle- or hind-leg muscles exist in any released MJCF** — I checked all six.

MuJoCo-Warp (GPU) support is unverified even by the authors: flygym ships
`check_mjwarp_compatibility()` precisely because Hill-type actuators, spatial tendons and
joint-equality constraints may not be ported to mjwarp.

---

## D.6 Connectome-driven body simulation — who has actually done it

**Nobody has published a MANC / FANC / MaleCNS leg-motor-neuron → leg-actuator mapping.** That
seam is open. Everyone who has tried has stopped at the same wall, and for the same reason: none of
these bodies has muscles, so there is no anatomical target to innervate and the MN-pool → joint
command map has to be invented. Our project is being asked to invent exactly that.

What does exist (largely second-hand, from web search; repos read, papers mostly not):

- **arXiv:2602.17997 is real**, and its title is *"Whole-Brain Connectomic Graph Model Enables
  Whole-Body Locomotion Control in Fruit Fly"* — Zehao Jin, Yaoye Zhu, Chen Zhang, Yanan Sui;
  v1 2026-02-20, v2 2026-03-08, v3 2026-06-14 (verified: arXiv abstract page fetched). Abstract:
  they instantiate the connectome *"as a graph-structured neural controller for movements of a
  simulated biomechanical fruit fly via deep reinforcement learning"*, reporting stable locomotion
  and better sample efficiency than baselines. Body is **flybody**; connectome is FlyWire FAFB
  v783; PPO after imitation pretraining; 59-dim walking / 12-dim flight action spaces (2nd, from
  the full text via another agent). **No code or data availability statement appears on the arXiv
  abstract page and no GitHub link was found.**
  Crucially, the connectome→body link is **a learned decoder**, not an anatomical mapping: efferent
  states *"are flattened and mapped to continuous motor actions by a decoder Dec_φ"*. So it is a
  connectome-*shaped* network whose output is regressed onto joint commands. It does not use
  motor-neuron identity, muscle targets, or anything our project cares about — which means it does
  not scoop us, and also that it offers us no reusable mapping.
- `jamesbiederbeck/flybody-connectome` (MIT, MaleCNS v1.0, spiking, flygym's FlyBody) — **admits
  the seam is unsolved in its own README**: motor commands come from descending neurons DNp20 /
  DNpe017 because *"Vision reaches the descending neurons and stops there"*; its 708 VNC motor
  neurons get no drive at all.
- `Ibtisam-Mohammad/Fly.exe` (GPL-2.0, MaleCNS 165,122 neurons, GeNN/CUDA LIF) — states that
  flybody was **not** used (body is NeuroMechFly v2 / flygym 2.1.0) and that *"The gait is a
  published pattern generator, not the simulated ventral nerve cord."*
- `abgnydn/webgpu-fly` — "a Flybody body" with self-described *"approximate motor mappings"*.
  The rest of the 2026 hobbyist cluster (`NeuroFly`, assorted `fly-brain` forks, `digitalfly`)
  targets NeuroMechFly, not flybody.
- Neural-only, no embodiment confirmed: Pugliese et al., bioRxiv doi:10.1101/2025.09.12.675944,
  "Connectome simulations identify a central pattern generator circuit for fly walking".
- The **only** connectome→body link in a peer-reviewed fly paper is on the **sensory** side:
  NeuroMechFly v2's object-detection demo driven by FlyVision (commit 056e4aa), a
  connectome-constrained visual network.

**And there is a strong published "why".** Pugliese, Chou, Abe, Turcu, Lancaster, Tuthill &
Brunton, *"Connectome simulations identify a central pattern generator circuit for fly walking"*,
bioRxiv doi:10.1101/2025.09.12.675944 v2 (2026-04-30), PMC13142387 — preprint, not peer reviewed.
They build a firing-rate model of the MANC front-leg subnetwork (4,604 neurons = 1,318 DNs +
144 leg MNs + 3,142 premotor; 3,817,772 synapses), replicate it on MaleCNS, and find a 3-neuron CPG
that is necessary and sufficient across six legs in four datasets. **They cannot get tripod interleg
coordination.** Verbatim: *"proprioceptive feedback, biomechanical coupling, or other neural
pathways may be necessary."* Their stated next step is to *"couple VNC connectome"* to a body — with
the caveat that *"training artificial neural network components to fit parameters in
connectome-body interfaces carries risks for biological interpretability."*

That is our project described from the outside, by Tuthill and Brunton, as the missing piece — and
with a warning attached: do not learn the connectome↔body interface with a network. Which is an
argument for the anatomical, muscle-level mapping (FlyMimic) over the learned-decoder approach
(FlyGM).

The practical consequence: there is no reference implementation to copy, and also no prior claim
to contradict. If we build the per-muscle seam properly — even on one leg via FlyMimic — it is new.

## D.6b Anything else — searched, and the answer is mostly "no"

**Other *Drosophila* musculoskeletal models: none.** Searched arXiv, Crossref, GitHub and MyoHub.
FlyMimic and its own OpenSim ancestor are the only ones. flybody and both NeuroMechFlys are
torque/position throughout.

**Other insect Hill-type leg models: a handful, all worse for our purpose than FlyMimic.**
- Guo, Lin, Wöhrl, Liao (2018), *Scientific Reports* **8**:2129, doi:10.1038/s41598-018-20093-x —
  desert ant *Cataglyphis fortis*, Hill-type with custom force–length and force–velocity curves,
  antagonistic pairs, 3 DoF × 6 legs, in **Bullet** (C++). The antagonist-pair architecture is the
  right shape, but wrong species, wrong engine, far coarser.
- Naris, Szczecinski & Quinn, *"A neuromechanical model exploring the role of the common inhibitor
  motor neuron in insect locomotion"*, *Biol Cybern* **114**:23–41 (2020),
  doi:10.1007/s00422-019-00811-y — AnimatLab-style Hill muscle, stick insect.
- **Stick-insect Hill parameters are the one thing genuinely worth borrowing**, because FlyMimic's
  force–length and force–velocity curves are OpenSim *human* defaults. The Blümel / Guschlbauer /
  Hooper / Büschges trilogy, all *Biological Cybernetics* **106** (2012), all *Carausius morosus*
  extensor tibiae: doi:10.1007/s00422-012-0531-5 (determining all parameters from single-muscle
  experiments, 543–558); doi:10.1007/s00422-012-0530-6 (parameters show large animal-to-animal
  variation, 559–571); doi:10.1007/s00422-011-0460-8 (individual-muscle-specific data halves
  simulation error, 573–585). If anyone asks where a real insect force–velocity curve comes from,
  that is the answer.
- **No Hill-type *Drosophila* larva model exists** (Loveless & Webb, *Integr Comp Biol* 2018,
  doi:10.1093/icb/icy094, is kinematic/continuum), and no cockroach or locust whole-leg
  musculoskeletal model surfaced.
- Szczecinski and Quinn's fly work is a **robot**, not a muscle model: Drosophibot
  (doi:10.1007/978-3-030-24741-6_13) and Drosophibot II (*Bioinspir Biomim*, stem
  doi:10.1088/1748-3190/ad80ec).

**MyoSuite / MyoHub have no insect models at all.** `myo_sim`'s model table is human-only
(MyoLeg, MyoArm, MyoTorso, MyoHand, MyoFullBody, MyoLeg26, MyoFinger, MyoElbow). MyoHub's only role
here is **MyoConverter**, the OpenSim→MuJoCo tool FlyMimic used.
(`NeLy-EPFL/neuromechants` exists — MuJoCo ant body models for AntScan — but it is a body model,
not a muscle model; contents not inspected.)

**Özdil's other papers.** There is **no earlier Özdil fly-leg-muscle-anatomy or X-ray paper** —
FlyMimic is the Ramdya lab's first muscle model, and the X-ray anatomy it uses is borrowed from
Kuan et al. 2020 (doi:10.1038/s41593-020-0704-9) and Dinges et al. 2021
(doi:10.1002/cne.24987) plus one new synchrotron scan. Adjacent lab output: the antennal-grooming
paper, now *Nature Communications* 2026, doi:10.1038/s41467-026-72152-x (preprint
doi:10.1101/2024.12.17.628844); and SeqIKPy, the inverse-kinematics tool, doi:10.21105/joss.08557.
Adjacent kinematic leg model: Haustein et al. 2024, doi:10.3389/fbioe.2024.1357598.

**The "Miller" numbering.** The word "Miller" appears **nowhere in the FlyMimic paper** — the
labels live only in the MJCF *site* names. The citation is almost certainly
A. Miller (1950), "The internal anatomy and histology of the imago of *Drosophila melanogaster*",
in Demerec (ed.), *Biology of Drosophila*, Wiley, pp. 420–534 (FlyBase FBrf0007735 confirms author
and pages). **Not verified** that Miller's numbers 28–33 are the six muscles the site names assign
them to. Do not put that mapping in print without checking Miller directly.
(Amusing tell of the conversion pipeline: the femoral MTU attachment sites are named `bifemlh_r` —
biceps femoris long head, from a stock OpenSim *human* template.)

**Gaps I could not close:** whether the FlyGM code is public; MIMIC-MJX (arXiv 2511.20532);
the `.osim` force units; ICLR acceptance type.

## D.7 Converting a 10 ms per-muscle drive onto each model, and what is lost

Our input per frame: for each leg ℓ ∈ {T1,T2,T3} × {L,R} and each muscle group m, a scalar drive
d_{ℓ,m}(t) ∈ [0,∞) derived from motor-neuron firing rates over a 10 ms window.

### D.7.0 The mapping table — our motor pools against both models

FlyMimic's 15 MTUs are grouped by segment of origin: **7 thorax-origin** (`LFC_*`, inserting on the
coxa), **6 coxa-origin** (`LFF_*`, inserting on the trochanter), **2 femur-origin**
(`LFTibia_*`, inserting on the tibia). The paper says this covers **12 of the 19** muscle groups it
defines for a foreleg. The exclusions are deliberate and stated: muscles **inside the tibia** were
left out because the X-ray volume was partial, and muscles **inside the trochanter** because their
function was unclear.

| our motor pool | origin segment | FlyMimic MTU(s) | NeuroMechFly v2 joint | flybody joint |
|---|---|---|---|---|
| coxa promotor | thorax | `LFC_tergopleural_promotor_a`, `_b`, `LFC_pleural_promotor` | `Coxa` (ThC pitch) | `coxa_T*_*` |
| coxa remotor / abductor | thorax | `LFC_pleural_remotor_and_abductor` | `Coxa`, `Coxa_roll` | `coxa_*`, `coxa_abduct_*` |
| sternal rotators | thorax | `LFC_sternal_anterior_rotator`, `LFC_sternal_posterior_rotator` | `Coxa_yaw` (ThC yaw) | `coxa_twist_*` |
| (sternal adductor) | thorax | `LFC_sternal_adductor` | `Coxa_roll` | `coxa_abduct_*` |
| sternotrochanter | thorax | `LFF_sterno-tergo-trochanter_extensor_a`, `_b` | `Femur` (CTr pitch) | `femur_T*_*` |
| trochanter flexor | coxa | `LFF_trochanter_flexor_a`, `_b`, `LFF_accesory_trochanter_flexor` | `Femur` (CTr pitch) | `femur_T*_*` |
| trochanter extensor | coxa | `LFF_trochanter_extensor` | `Femur` (CTr pitch) | `femur_T*_*` |
| **femur reductor** | trochanter | **none** (trochanter muscles omitted) | `Femur_roll` (CTr roll) | `femur_twist_*` |
| tibia flexor | femur | `LFTibia_flex_93434` | `Tibia` (FTi pitch) | `tibia_T*_*` |
| tibia extensor | femur | `LFTibia_extensor_93932` | `Tibia` (FTi pitch) | `tibia_T*_*` |
| **tarsus levator** | tibia | **none** (partial X-ray volume) | `Tarsus1` (TiTa pitch) | `tarsus_T*_*` |
| **tarsus depressor** | tibia | **none** (partial X-ray volume) | `Tarsus1` (TiTa pitch) | `tarsus_T*_*` |
| **long tendon muscle** | femur + tibia | **none** | `Tarsus1` (+ passive `Tarsus2–5`) | `tarsus_*` + `tarsus2_*` tendon |

Read the table the other way and the picture is stark. **NeuroMechFly and flybody have a joint for
every one of our pools** — including the femur reductor, which maps cleanly onto `Femur_roll` /
`femur_twist_*`. They just cannot tell two antagonists apart. **FlyMimic can tell every muscle
apart but is missing four of our pools**, and the four it is missing are exactly the distal ones:
tarsal control and the long tendon muscle.

So the two models fail in complementary directions, which is the argument for running both.

### D.7.0b Four things that break a naive per-muscle mapping

These come from the connectome literature rather than the body models, but they land on the mapping,
so they belong here. Detail and citations are in
`connectome_driven_sim_and_mn_muscle_lit.md`; the short version:

1. **Muscle names are unreliable; motor-neuron identity is not.** The nomenclature chain
   Snodgrass 1935 → Miller 1950 → Soler 2004 → Baek & Mann 2009 / Brierley 2012 is internally
   inconsistent — Azevedo et al. 2020 record that *"the muscle named the **tibia reductor** muscle
   by Soler et al. is described as one of two depressor muscles by Miller, muscles 40 and 41"*.
   Pin our mapping to MANC/MaleCNS `target` and `subclass` fields, not to name strings. And do not
   assert the Miller-28–33 → muscle mapping in print: it is encoded in FlyMimic's site names but I
   could not verify it against Miller 1950 itself.
2. **Our 373 matches no published count.** FANC gives **371** leg MNs (69 left T1, 70 right T1 —
   the extra is a second tarsus levator MN); MANC gives **392** (142 T1, 119 T2, 131 T3). MaleCNS is
   a third annotation revision. Worth reconciling before quoting the number.
3. **There are ~18 muscle groups per leg, not ~12** — 13 within the proximal leg segments plus 5 in
   the thorax that insert on the leg, ~70 MNs per leg from ~15 hemilineages, with the number of MNs
   per muscle varying *by an order of magnitude*. Whatever our 12-ish channels are, they are a
   collapse of 18, and we should know which collapses we made.
4. **Polyneuronal innervation breaks simple pooling.** Confirmed in the **long tendon muscle**, the
   **proximal trochanter flexor fibres**, and the **femur reductor** (6 MNs, function described as
   unknown). Summing MN rates within a group is not obviously the right operation for these three.
   The LTM is also the multi-joint case: fibres in the femur (ltm2) and the tibia (ltm1) insert on a
   single long tendon (retractor unguis) controlling the tarsal claw.
   And MANC could not serially match **tarsus levator/depressor** or **tergopleural/pleural
   promotor** MNs outside T1 — so those channels are the least reliable for T2/T3, which is exactly
   where FlyMimic also has nothing.

### D.7.1 Onto FlyMimic — near-direct, and this is the point

For the left front leg, 12 of our muscle groups have a named actuator. The conversion is:

1. Normalise each pool's rate to an activation a ∈ [0,1]. The physiological anchor is the **size
   principle** (Azevedo et al., *eLife* 9:e56754): recruitment order and rate coding together set
   muscle force, so a reasonable first pass is
   `a = clip(Σ_i w_i r_i / F_max, 1e-4, 1)` with w_i a per-neuron weight rising with the neuron's
   size/threshold rank, and F_max a per-muscle normaliser (E).
2. Where our single pool maps to two or three FlyMimic actuators (`promotor_a`/`_b`,
   `trochanter_flexor_a`/`_b`/`accesory`, `sterno-tergo-trochanter_extensor_a`/`_b`), split the
   activation. Splitting equally is defensible only as a placeholder; the sub-branches have very
   different `force` parameters (e.g. promotor_a 14.2 vs promotor_b 67.8), so an equal split is
   *not* an equal force contribution. (E)
3. Write the 15-vector into `ctrl` via
   `sim.set_actuator_inputs(fly, ActuatorType.MUSCLE, a)` and step 100× per frame.
4. Read back `sim.get_joint_angles(fly)` / `get_joint_velocities(fly)` for the seven LF joints, and
   `sim.get_actuator_forces(fly, ActuatorType.MUSCLE)` for tendon force — the latter being the
   closest thing any of these models has to a campaniform-sensillum signal.

**What is lost, even here:** four muscle groups have no actuator (femur reductor, tarsus levator,
tarsus depressor, long tendon muscle); five of our six legs have nothing; the thorax is tethered so
there is no ground reaction force, no load feedback and no locomotion; and the a/b sub-branch split
is a guess. **What is preserved:** co-contraction, stiffness modulation, moment-arm change with
joint angle, force–length and force–velocity relations, and activation dynamics. That is the whole
reason to bother.

The long tendon muscle is the sharpest illustration. It sits in the femur but its tendon crosses to
the tarsus, so it is a genuinely multi-joint actuator. FlyMimic's spatial-tendon machinery is
exactly what would represent it correctly — and FlyMimic does not include it. On NeuroMechFly there
is no representation at all short of writing its effect into two joint setpoints by hand.

### D.7.2 Onto NeuroMechFly v2 (or flybody) — the lossy path

NeuroMechFly takes 42 joint **position** setpoints plus 6 adhesion values. Our 373-neuron,
per-muscle vector has to be collapsed to 42 numbers. Two defensible schemes:

**(a) Antagonist difference → position setpoint.** For each actuated DoF j, pick its agonist set A_j
and antagonist set B_j from the table in §D.3.2 and set

`θ_target,j = θ_neutral,j + k_j · (Σ_{m∈A_j} a_m − Σ_{m∈B_j} a_m)`

with k_j a per-joint gain in radians, tuned so that full one-sided activation sweeps the joint's
anatomical range. Then `sim.set_actuator_inputs(fly, ActuatorType.POSITION, θ_target)` and step
100×. This is the simplest thing that works and it is what "visualising attempted movement" really
means: the position servo (kp = 45, forcerange 65) will *try* to reach the setpoint, and where the
leg is loaded or blocked it will fall short, which is the visible "attempt".

**(b) Antagonist difference → torque.** Switch to `control="torque"` and set
`τ_j = g_j · (Σ_A a_m · r_{m,j} − Σ_B a_m · r_{m,j})`, with r_{m,j} a nominal moment arm. More
honest mechanically — a motor neuron commands force, not position — but the model has no passive
joint stiffness worth the name (0.05) and no muscle force–length curve, so a torque-driven
NeuroMechFly is floppy and hard to keep standing. Expect to need an added passive stiffness term.

**What is lost in both:**

- **Co-contraction.** Two antagonists both firing hard is, in the difference scheme, identical to
  both being silent. The animal is stiffening the joint; the model sees zero. This is not a detail
  — co-contraction is how insects set limb impedance during stance and during postural holds, and
  it is the single largest thing the mapping discards.
- **Stiffness modulation.** Same cause. In the position scheme the joint's effective stiffness is
  fixed at kp = 45 forever, regardless of drive. A partial rescue is to modulate kp per joint per
  frame from the *sum* rather than the difference — `kp_j = kp_0 · (1 + c · Σ_{A∪B} a_m)` (E) — which
  recovers a co-contraction signal at the cost of being a hand-built analogy rather than physics.
- **Multi-joint muscles.** The long tendon muscle crosses TiTa; the sterno-tergo-trochanter
  extensors originate on the thorax and act across ThC and CTr together. A per-joint mapping has to
  assign each of these to one joint, or split them by fiat. Either way the coupling — the fact that
  a tarsal command changes the femoral moment — is gone.
- **Force–length and force–velocity.** A position servo applies whatever torque it needs, up to
  forcerange, regardless of muscle length or shortening velocity. A real muscle at the end of its
  range, or shortening fast, produces far less force. Movements near joint limits and fast swings
  will therefore be systematically too strong.
- **Moment arms changing with joint angle.** Folded into the constant k_j or r_{m,j}.
- **Recruitment order.** Collapsing a pool to one scalar loses which neurons fired; the size
  principle means the same summed rate from small vs large units is a different force and a
  different fatigue profile.
- **Femur reductor.** Maps to `Femur_roll`, which exists in NeuroMechFly — so this one actually
  survives the NeuroMechFly mapping better than the FlyMimic one.

**What survives:** gross timing, phase relationships between legs, left–right asymmetry, and the
ordering of stance and swing. Which is enough to make the animation legible and to feed joint
angles back as proprioception.

### D.7.3 Reading proprioception back out

Either model gives joint angle and joint velocity directly (`get_joint_angles`,
`get_joint_velocities`). For NeuroMechFly, add `get_ground_contact_info` for per-leg contact and
GRF. Mapping those onto real proprioceptor classes:

| target | signal | caveat |
|---|---|---|
| FeCO claw (position) | `θ` of `Femur`/`Tibia` | direct |
| FeCO hook (directional movement) | `sign(θ̇)` gated on magnitude | direct |
| FeCO club (bidirectional movement / vibration) | `|θ̇|` | the club's high-frequency vibration channel needs oscillation the 10 ms frame cannot carry |
| campaniform sensilla (load) | contact force per leg, or muscle `actuator_force` on FlyMimic | GRF is not cuticular strain; strongly (E) |
| hair plates | sigmoid on `θ` near a joint limit | crude but cheap (E) |

---

## D.8 Recommendation

**(i) For visualising attempted movement: NeuroMechFly v2 / flygym.**
It is the only option that is a whole six-legged fly, walks, has adhesion, is actively maintained
(2.1.0 shipped mid-2026), is Apache-2.0, has a clean setter for control and a clean getter for
state, and steps happily at 10 ms control frames over its 0.1 ms physics. Use the antagonist-
difference-to-position-setpoint mapping (§D.7.2a), because "attempted" is exactly what a position
servo with a finite force range produces when the world pushes back. flybody is a reasonable
alternative and is better if wings ever matter, but it buys us nothing on the leg side (8 vs 7
actuators, same position-servo semantics) and its leg passive parameters are admittedly unfitted.

**(ii) For the physics behind proprioception: NeuroMechFly v2 as the working system, FlyMimic as
the validity check.**
Proprioception needs joint angle, joint velocity and load across all six legs during locomotion.
Only NeuroMechFly v2 supplies that, so it has to be the workhorse. But the per-muscle→per-joint
collapse is a real epistemic cost, and the honest way to pay it is to run the **left front leg** of
FlyMimic in parallel, driven by the *unreduced* per-muscle vector, and compare its seven joint
angles against the same leg's angles in NeuroMechFly. Where they agree, the collapse is harmless.
Where they diverge — and I expect divergence exactly during co-contraction and near joint limits —
we have a measured bound on what the mapping cost us, rather than a hand-wave.

Both are Apache-2.0, both are MuJoCo, and since flygym 2.1.0 vendors FlyMimic, both can live in one
process with one dependency. That is the deciding practical fact.

### D.8.1 The third option, if we ever want it

flygym 2.1.0 is a hair's breadth from letting us put muscles on a *whole* fly.
`flygym.utils.mjcf.add_actuator()` already accepts `tendon=` as a transmission target
(`mjTRN_TENDON`), `ActuatorType.MUSCLE` is a first-class enum value, `Simulation` has
`set_tendon_actuator_inputs()` and `get_actuator_forces(fly, ActuatorType.MUSCLE)`, and the whole
sensor stack works unchanged. What is missing is the **anatomy**: the spatial-tendon paths, the
attachment sites on each segment, and the Hill parameters for the other five legs. FlyMimic has all
of that for one leg, derived from X-ray scans.

So "port FlyMimic's 15 LF muscles onto the contralateral and homologous legs of the full
NeuroMechFly body" is a real, bounded engineering task — mirror the LF muscle set to RF, then
re-fit moment arms for T2 and T3 — rather than a research programme. It would give us the only
six-legged, walking, muscle-driven fly in existence. I am not proposing we do it now; I am flagging
that the scaffolding is already in the library, and that if the project's claim is "we drive a fly
from motor neurons", this is where that claim eventually has to land.

Two obstacles worth knowing up front: the two bodies' kinematic chains disagree at the trochanter
(FlyMimic separates it, NeuroMechFly fuses it into `trochanterfemur`) — so a port means either
adding a trochanter body to NeuroMechFly or collapsing FlyMimic's two trochanter DoFs. And
MuJoCo-Warp may not accept Hill-type actuators plus spatial tendons, so the GPU path would be lost.

One caveat to carry forward: FlyMimic covers 12 of the 19 foreleg muscle groups, on one leg. It
has no femur reductor, no tarsus levator or depressor, and **no long tendon muscle** — so the TiTa
joint, the one our tarsal and LTM pools act on, is precisely where the muscle-level cross-check
gives us nothing. If tarsal control matters to the claims we want to make, that gap has to be
stated, not papered over.

Second caveat, on citation hygiene: FlyMimic's only DOI is the arXiv one
(10.48550/arXiv.2509.06426) — there is no journal DOI. And do **not** copy flygym 2.1.0's
docstring citation of flybody: it attaches the correct DOI to a wrong title.
