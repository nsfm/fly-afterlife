# Wang-Chen et al. 2024 — NeuroMechFly v2

**Citation.** Wang-Chen S, Stimpfling VA, Lam TKC, Özdil PG, Genoud L, Hurtak F, Ramdya P.
"NeuroMechFly v2: simulating embodied sensorimotor control in adult *Drosophila*."
*Nature Methods* (2024). DOI 10.1038/s41592-024-02497-y.
Preprint: bioRxiv 2023.09.18.556649. Code archive: Zenodo record 12973000 (not fetched).

**Read.** The EPFL author postprint PDF,
https://www.epfl.ch/labs/ramdya-lab/wp-content/uploads/2024/08/NMF2_postprint.pdf
(6.2 MB, extracted to text with `pdftotext -layout`, 1934 lines). Plus the source repo.

**Repo.** https://github.com/NeLy-EPFL/flygym · docs https://neuromechfly.org
Licence: **Apache-2.0** (LICENSE = verbatim Apache License 2.0, 201 lines;
`pyproject.toml` declares `license = "Apache-2.0"`). VERIFIED.
Clone checked: HEAD `38c8ec61034cd59bc5ba0de20688d4a3c0000d60` (2026-06-29), package version 2.1.0.
Paper-era API: tag **v1.2.1**, also fetched and read.

## Model geometry (VERIFIED by counting the MJCF)

File: `flygym/data/mjcf/neuromechfly_seqik_kinorder_ypr.xml` @ tag v1.2.1.

- 70 `<body>`, **87 `<joint>`, all `type="hinge"`** (so 87 internal DoFs). No free joint in the
  fly XML; the 6-DoF free joint is added on attachment to an arena → **93 DoFs for a free fly**.
- Breakdown of the 87:
  - 66 leg joints = **11 per leg × 6**
  - 3 neck/head: `joint_Head` (pitch), `joint_Head_roll`, `joint_Head_yaw`
  - 18 antennal = 9/side: `{L,R}{Pedicel,Funiculus,Arista}` × {pitch (bare name), `_roll`, `_yaw`}
  - 0 wing / haltere / abdomen / proboscis joints (fused; compiler `fusestatic: true`)
- Two other MJCF variants at v1.2.1: `neuromechfly_deepfly3d_kinorder_ryp.xml`,
  `neuromechfly_seqik_kinorder_ypr_capsuletarsus.xml`.

## Leg DoF names (VERIFIED, `flygym/preprogrammed.py` @ v1.2.1)

```python
all_leg_dofs = [
    f"joint_{side}{pos}{dof}"
    for side in "LR" for pos in "FMH"
    for dof in ["Coxa","Coxa_roll","Coxa_yaw","Femur","Femur_roll","Tibia","Tarsus1"]
]
```
= **42 actuated DoFs, 7 per leg**. `Tarsus2..Tarsus5` exist but are passive (4×6 = 24).

| MJCF suffix | anatomical | axis |
|---|---|---|
| `Coxa` / `Coxa_roll` / `Coxa_yaw` | ThC (thorax–coxa) | pitch / roll / yaw |
| `Femur` / `Femur_roll` | CTr (coxa–trochanter); trochanter+femur is one rigid link | pitch / roll |
| `Tibia` | FTi (femur–tibia) | pitch |
| `Tarsus1` | TiTa (tibia–tarsus) | pitch |

Axis convention (flygym 2.1.0 `flygym/anatomy.py`, `class RotationAxis`):
`pitch → y (0,1,0)`, `roll → z (0,0,1)`, `yaw → x (1,0,0)`.
Euler composition order is explicit and selectable (`AxisOrder` enum, 6 permutations); the default
MJCF is `kinorder_ypr` (yaw–pitch–roll).

flygym 2.1.0 renames links to `coxa`, `trochanterfemur`, `tibia`, `tarsus1..5` and DoFs to
`{parent}-{child}-{axis}` (e.g. `lf_coxa-lf_trochanterfemur-pitch`). Computed from `anatomy.py`:
68 anatomical joints, 69 segments, 126 rotational DoFs in `ALL_BIOLOGICAL`, 66 of them leg DoFs
(11/leg). Presets `LEGS_ONLY` / `LEGS_ACTIVE_ONLY` reproduce the 66 / 42 split.

## Actuation (VERIFIED, `flygym/fly.py` @ v1.2.1 + postprint)

`Fly(control="position")` default; `"velocity"`, `"torque"` also accepted. Constructor defaults:

| param | default |
|---|---|
| `actuator_gain` (MuJoCo `kp`) | **45.0** |
| `actuator_forcerange` | **65.0** |
| `joint_stiffness` / `joint_damping` | 0.05 / 0.06 |
| `non_actuated_joint_stiffness` / `_damping` | 1.0 / 1.0 |
| `neck_stiffness` | 10.0 |
| `tarsus_stiffness` / `tarsus_damping` | 7.5 / 1e-2 |
| `friction` | (1.0, 0.005, 0.0001) |
| `contact_solref` | (2e-4, 1e3) |
| `adhesion_force` | 40 |
| `enable_adhesion` | False |

Postprint Methods, verbatim: *"We used a joint position gain kp of 45 and an adhesion force of
40 mN for all controllers."*

**No muscle or tendon actuators in the NeuroMechFly body.** flygym 2.1.0's `ActuatorType` enum does
include `MUSCLE` and `TENDON`, but those serve the separate FlyMimic model.

## Adhesion (VERIFIED)

Postprint, verbatim: *"Leg adhesion was added using built-in MuJoCo actuators. Adhesion takes the
form of an artificial force injected normal … [when] multiple contacts occur with external objects
and the adhesion actuated body, the force is equally divided between these."* And: *"We controlled
adhesion in a binary fashion but it is possible to use a gradient of adhesion forces by modulating
the input to the adhesion actuator at every time step."*

6 MuJoCo `adhesion` actuators, one on each leg's `tarsus5` geom, `ctrl ∈ [0,1]`
(`base_fly.add_leg_adhesion()` in 2.1.0). `get_observation` subtracts the adhesion contribution
back out of the reported contact forces.

## Sensors and observations (VERIFIED)

MuJoCo sensors added by `Fly._add_joint_sensors()`: per actuated joint `jointpos`, `jointvel`,
`actuatorfrc`; per non-actuated monitored joint pos/vel + a 4-component torque reduced to its norm.
Plus body `framepos`/`framelinvel`/`framequat`/`frameangvel` and per-body `force` sensors at the
contact-sensor placements (default = tibia + tarsus1–5 on all 6 legs = 36 bodies).

Gym observation space (`Fly._define_observation_space`):

| key | shape | contents |
|---|---|---|
| `joints` | (3, 42) | row 0 angle (rad), row 1 velocity (rad/s), row 2 joint force (`actuatorfrc`, ×1e-9 → N) |
| `fly` | (4, 3) | thorax position, linear velocity, (pitch,roll,yaw) extrinsic ZYX, angular velocity, global frame |
| `fly_orientation` | (3,) | unit vector on the A–P axis |
| `cardinal_vectors` | (3, 3) | body-frame axes |
| `contact_forces` | (36, 3) | ground reaction force per contact body |
| `end_effectors` | (6, 3) | tarsus5 tip positions |
| `vision` (opt) | (2, 721, 2) | 721 ommatidia/eye, 70% yellow / 30% pale |
| `odor_intensity` (opt) | (k, 4) | 2 antennae + 2 maxillary palps |

Action space: `joints ∈ R^42`, `adhesion ∈ {0,1}^6`.

SI Note 3, verbatim: *"Joint states: The angle, velocity, and force at each of the n actuated joint
DoFs (by default all 42 leg DoFs), R^{3×n}."*

flygym 2.1.0 replaces the dict with getters on `Simulation`: `get_joint_angles`,
`get_joint_velocities`, `get_actuator_forces(fly, ActuatorType)`, `get_body_positions`,
`get_body_rotations`, `get_site_positions`, `get_ground_contact_info` (returns a 6-tuple
`found (6,), force (6,3), torque (6,3), pos (6,3), normal (6,3), tangent (6,3)`),
`get_bodysegment_contact_forces`, `get_raw_vision`, `get_ommatidia_readouts`;
setters `set_actuator_inputs`, `set_leg_adhesion_states`, `set_tendon_actuator_inputs`.

## Timestep (VERIFIED)

`Simulation(timestep: float = 0.0001)` @ v1.2.1.
`assets/model/neuromechfly/mujoco_globals.yaml` @ 2.1.0:
`option: {gravity: [0,0,-9810] (mm/s²), timestep: 1e-4, integrator: Euler, solver: Newton,
iterations: 100, noslip_iterations: 5, flag: {multiccd: enable, energy: enable}}`;
`compiler: {angle: radian, eulerseq: XYZ, fusestatic: true, boundmass: 1e-6, boundinertia: 1e-12}`.
Control rate is independent of the physics rate — 10 ms control = hold ctrl and step 100×.

## Proprioception (VERIFIED — there is no such observation by that name)

What the paper calls *ascending motor feedback* is concretely **leg joint angles + ground-contact
flags** into an MLP. SI feature table: *"Shown in examples: Leg stride lengths for path
integration; Leg joint angles and ground contacts for head stabilization."* Main text: *"we
designed a controller in which leg joint angles (i.e., proprioceptive …)"* and *"ascending feedback
concerning multiple degrees of freedom appears to [matter]"*. Extended Data note: *"Note that
ground contact information is always [used]"*.

**No campaniform sensilla, chordotonal organ or hair-plate sensor exists anywhere in the model.**
The only occurrence of "hair plate" in the paper is anatomical prose about neck placement:
*"The neck is located ventral to the hair plate behind the head."*

## Muscles — explicitly future work (VERIFIED)

Discussion, verbatim: *"careful measurements and analyses of the Drosophila musculoskeletal system
(i.e., tendons and muscles) could improve the interface between neural network controllers and the
biomechanical embodiment."*

SI feature table, "Behavioral kinematics → Future potential", verbatim:
*"Inclusion of motor neurons and muscle models [20, 21]"*, where the SI reference list gives
[20] Kuan AT et al., "Dense neuronal reconstruction through X-ray holographic nano-tomography",
*Nature Neuroscience* (year not captured), and
[21] Azevedo AW et al., "A size principle for recruitment of *Drosophila* leg motor neurons",
*eLife* **9**, e56754 (2020).

Same table, "Currently supported": *"Each walking step: 42 actuated leg degrees of freedom (DoFs,
7 per leg) playing out pre-programmed stepping sequences"*.

## Controllers shipped (VERIFIED)

CPG (coupled oscillators adapted from a salamander model — SI Note 4, Supp. eqs 1–4), rule-based
(Walknet lineage; Schilling, Hoinville, Schmitz & Cruse cited), **hybrid** (CPG + phase-dependent
corrective rules; the one used for most demos), and a turning controller taking a 2-vector "DN
drive" with DNmin = 0.2, DNmax = 1. All output **target joint angles** from a preprogrammed step
cycle scaled by CPG amplitude. Repo tutorials `4a`–`4d`.

## Connectome link (VERIFIED, partial)

Methods software list names **"FlyVision commit 056e4aa for connectome-constrained visual system
simulation"** and "SeqIKPy 1.0.0 for inverse [kinematics]". Figure 5 reports *"Object detection
score and activity patterns of 34 putative output columnar neuron types (of 65 total)"*.
This is the connectome-constrained **vision** demo. No motor-side connectome drive.

## Verified vs not

- VERIFIED: 87-joint count and full breakdown; 42/7-per-leg actuation; joint names and axis
  convention; kp=45, forcerange=65 and all the stiffness/damping defaults; adhesion mechanism and
  force; full observation and action spaces; 1e-4 s timestep and all `option`/`compiler` settings;
  absence of muscles/tendons in the body model; absence of any campaniform/chordotonal/hair-plate
  sensor; the FlyVision commit hash; licence Apache-2.0.
- NOT verified: the Nature Methods page itself (I read the author postprint, not the journal PDF);
  the Zenodo record contents; whether the published version's page/volume numbers differ.
