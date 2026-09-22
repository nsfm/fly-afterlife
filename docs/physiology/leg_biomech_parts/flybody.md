# flybody (Janelia / Turaga lab) — verified survey

Status: **complete**. Sections 1–9, 11, 12 VERIFIED from the repo/MJCF (model compiled
with mujoco 3.13.0). Section 10 is web-search based and explicitly marked second-hand.

Everything below marked VERIFIED was read directly out of the cloned repo at
`git rev-parse HEAD = d015e9bfe441bd90ae431bac24c55cb74bdbce26` ("Update paper reference.",
2025-07-30), or computed by compiling the MJCF with `mujoco 3.13.0`.
Local clone path (scratch): `.../scratchpad/flybody`.
Upstream: https://github.com/TuragaLab/flybody

---

## 1. Citation

VERIFIED from `README.md` (BibTeX block in the "Citing `flybody`" section):

```bibtex
@article{flybody,
  title = {Whole-body physics simulation of fruit fly locomotion},
  author = {Roman Vaxenburg and Igor Siwanowicz and Josh Merel and Alice A Robie and
            Carmen Morrow and Guido Novati and Zinovia Stefanidi and Gert-Jan Both and
            Gwyneth M Card and Michael B Reiser and Matthew M Botvinick and
            Kristin M Branson and Yuval Tassa and Srinivas C Turaga},
  journal = {Nature}, volume = {643}, pages = {1312--1320}, year = {2025},
  doi = {https://doi.org/10.1038/s41586-025-09029-4},
  url = {https://www.nature.com/articles/s41586-025-09029-4},
}
```

- Title, journal (Nature), **volume 643, pages 1312–1320, 2025**, DOI **10.1038/s41586-025-09029-4** —
  all VERIFIED as written in the repo README. The DOI the requester had is correct.
- Preprint: bioRxiv, VERIFIED from README link target
  `https://www.biorxiv.org/content/10.1101/2024.03.11.584515v2` → **DOI 10.1101/2024.03.11.584515** (v2).
- CAUTION: flygym 2.1.0 cites the same DOI under a *different* title
  ("A whole-body model of *Drosophila* with precise neuromuscular connectivity",
  `flygym/src/flygym/compose/fly/flybody.py` docstring). The flybody README title is the
  authoritative one; flygym's docstring title is wrong/stale.
- Supplementary data DOI (figshare): **10.25378/janelia.25309105**
  (VERIFIED, `flybody/download_data.py` module docstring).

## 2. License

VERIFIED: `LICENSE` is the verbatim **Apache License 2.0** boilerplate
(SPDX: `Apache-2.0`). The appendix still contains the unfilled template line
`Copyright [yyyy] [name of copyright owner]` — i.e. **no copyright holder is named
anywhere in the LICENSE file**. `pyproject.toml` has `license = {file = "LICENSE"}` and
authors Roman Vaxenburg (HHMI), Gert-Jan Both (HHMI), Yuval Tassa (Google),
Zinovia Stefanidi (Tübingen).

## 3. Physics engine / pins

VERIFIED from `pyproject.toml` (there is no setup.py / requirements.txt):

- core deps: `numpy==1.26.4`, `dm_control` (**unpinned** — mujoco comes in transitively
  through dm_control, so **there is no explicit mujoco pin at all**), `h5py`, `pytest`, `mediapy`.
- `requires-python = ">=3.10"`.
- extra `[tf]`: `dm-acme[tf,envs,jax]`, `nvidia-cudnn-cu11==8.9.*`, `tensorflow==2.8.0`,
  `tensorflow-probability==0.16.0`, `dm-reverb==0.7.0`, `protobuf==3.20.*`.
- extra `[ray]`: `flybody[tf]` + `ray[default]`. `[dev]`: ruff, jupyterlab, tqdm.
- The model compiles cleanly under mujoco 3.13.0 (I did this) — no version-specific XML features.

## 4. DoF counts (computed, not guessed)

VERIFIED by compiling `flybody/fruitfly/assets/fruitfly.xml` with mujoco 3.13.0:

```
nq=109  nv=108  nu=78  na=0  njnt=103  nbody=68  ngeom=159  nsite=15  ntendon=8  nsensor=15
```

- **103 joints = 1 free joint (`name="free"`, on body `thorax`) + 102 hinge joints.**
  Zero slide, zero ball. So 102 actuated-or-passive internal DoFs + 6 root DoFs = **108 DoF total**.
- Joint-count by group (names read straight out of the XML):
  - head/neck: 3 — `head_abduct` (z), `head_twist` (y), `head` (x)
  - proboscis/mouth: 5 — `rostrum`, `haustellum_abduct`, `haustellum`, `labrum_left`, `labrum_right`
  - antennae: 6 — `antenna_abduct_{left,right}`, `antenna_twist_{left,right}`, `antenna_{left,right}`
  - wings: 6 — `wing_{yaw,roll,pitch}_{left,right}`
  - abdomen: 14 — `abdomen_abduct`, `abdomen`, then `abdomen_abduct_2..7`, `abdomen_2..7`
    (7 segments × {abduct(z), extend(x)})
  - halteres: 2 — `haltere_left`, `haltere_right` (passive; class `haltere`,
    `springdamper="0.005 0.1"`, range ±0.2; **no actuator**)
  - legs: 66 = 6 legs × 11 (assertion `len(self._leg_joints) == 66  # 11 joints per leg`
    at `flybody/tasks/base.py:357`)
  - 3+5+6+6+14+2+66 = 102 ✓

### One leg, exact names and convention (front-left, T1 left)

```
coxa_abduct_T1_left    axis 0 0 1   range -1    0.7     (ThC abduction)
coxa_twist_T1_left     axis 0 1 0   range -0.8  0.8     (ThC rotation/twist)
coxa_T1_left           axis 1 0 0   range -0.2  1.7     (ThC extension/protraction)
femur_twist_T1_left    axis 0 1 0   range -1    1       (TrF twist)
femur_T1_left          axis 1 0 0   range -0.15 2       (CTr/femur extension)
tibia_T1_left          axis 1 0 0   range -1.35 1.3     (FTi flexion)
tarsus_T1_left         axis 1 0 0   range -0.7  1.2     (TiTa)
tarsus2_T1_left        axis 1 0 0   range -0.36 0.36    (tarsomere 1→2)
tarsus3_T1_left        "     "      "                   (tarsomere 2→3)
tarsus4_T1_left        "     "      "                   (tarsomere 3→4)
tarsus5_T1_left        "     "      "                   (tarsomere 4→5)
```

Naming convention (VERIFIED): `<segment>[_<dofkind>]_<T1|T2|T3>_<left|right>`, where
`T1/T2/T3` = pro/meso/meta-thoracic, dofkind ∈ {`abduct` (z axis), `twist` (y axis),
bare name = extension/flexion (x axis)}. Segments: `coxa`, `femur`, `tibia`, `tarsus`,
`tarsus2..5`. **There is no separate trochanter body/joint** — the trochanter is fused
into the femur, and the trochanter's twist DoF appears as `femur_twist_*`. The model does
NOT use the ThC/CTr/FTi/TiTa nomenclature in joint names (flygym's re-parse does, see §12).
Angles are radians (`<compiler angle="radian">`); lengths are cm (gravity `-981`, i.e. CGS).

Actuated leg DoFs per leg = **8**, not 11: the three distal tarsomeres are slaved to
`tarsus2_*` by a fixed tendon (§5).

## 5. Actuation

VERIFIED from the `<actuator>` block of `fruitfly.xml` (78 actuators total):

- **70 `<general>`** actuators + **8 `<adhesion>`**. No `<motor>`, `<position>`, `<muscle>`,
  no `dyntype="muscle"`, `na=0` in the raw XML. **There is no muscle model of any kind.**
- The 70 general actuators are **position servos** in the shipped XML:
  `gaintype=fixed`, `biastype="affine"`, `biasprm="0 -kp"`, `gainprm="kp"`,
  `ctrllimited="true"` with `ctrlrange` equal to the joint range (so ctrl = target angle in rad).
  Per-class kp (from `<default>`):
  | class | gainprm (kp) | biasprm | forcerange |
  |---|---|---|---|
  | head (neck, rostrum, haustellum) | 0.1 | 0 −0.1 | ±0.1 |
  | labrum | 0.01 | 0 −0.01 | ±0.01 |
  | antenna | 0.01 | 0 −0.01 | ±0.01 |
  | abdomen (both tendon acts) | 0.1 | 0 −0.1 | — |
  | coxa, femur | 0.8 | 0 −0.8 | — |
  | tibia, tarsus | 0.4 | 0 −0.4 | — |
  | wing yaw / roll / pitch | 3 / 2 / 1 | *none* | — (ctrlrange −1..1) |
  Wings are the exception: **no biastype ⇒ pure force/torque actuators**, ctrlrange [−1,1].
- **Transmission**: 62 act on a joint, **8 act on a fixed tendon** —
  `abduct_abdomen` (sums all 7 `abdomen_abduct_*`, coef 1), `abdomen` (sums all 7
  `abdomen_*`, coef 1), and one per leg `tarsus2_T{1,2,3}_{left,right}`
  (`tarsus2` coef 1 + `tarsus3,4,5` coef 0.5 each). That is how 14 abdominal DoFs collapse
  to 2 commands and 4 tarsomere DoFs to 1 per leg.
- **ADHESION: yes, 8 `<adhesion>` actuators.** 6 on the tarsal claws
  (`adhere_claw_T{1,2,3}_{left,right}`, class `adhesion_claw`, `ctrlrange="0 1"`,
  `gain="0.985"`) and 2 on the labrum (`adhere_labrum_{left,right}`, class
  `adhesion_labrum`, `ctrlrange="0 1"`, `gain="1"`). See §11.
- **Runtime modifications** (`flybody/fruitfly/fruitfly.py`):
  - `force_actuators=True` strips `biastype`/`biasprm`/`ctrlrange` from every non-adhesion
    actuator and sets a global `ctrlrange=(-1,1)` → the whole body becomes torque-controlled
    with gains unchanged (`fruitfly.py:308-327`).
  - `joint_filter` (default 0.01 s) sets `dyntype="filter"` (or `filterexact` if
    `dyntype_filterexact=True`) + `dynprm=(joint_filter,)` on all non-adhesion actuators;
    `adhesion_filter` (default 0.007 s) does the same for adhesion (`fruitfly.py:328-339`).
    With filters on, `na>0` and the activation state becomes an observable
    (`actuator_activation`).
  - Unused body parts are *removed*, not just ignored: `use_legs/use_wings/use_mouth/
    use_antennae` delete the joints, actuators, tendons and sensors of that group and set
    the bodies to their retracted `springref` pose (`fruitfly.py:203-280`).
  - Default walking action dim = **59** = 48 legs (6 × 8) + 6 claw adhesion + 3 head + 2
    abdomen. Asserted in `tests/test_core.py` (`assert n_act == (59,)`) and in the README
    example. Mouth (5+2 adhesion) and antennae (6) are off by default; wings (6) are
    retracted for walking tasks.

## 6. Sensors

VERIFIED, the whole `<sensor>` block is 15 elements, total sensordim 33:

- 1 `accelerometer` (site `thorax`), 1 `gyro` (thorax), 1 `velocimeter` (thorax)
- 6 `force` — `force_tarsus_T{1,2,3}_{left,right}`, on the **tarsus5 sites** (3-vector each)
- 6 `touch` — `touch_claw_T{1,2,3}_{left,right}`, on the claw sites (scalar each)
- **No `jointpos`/`jointvel`/`actuatorfrc`/`torque`/`framequat`/`framepos`/`rangefinder`
  sensors in the MJCF at all.** Joint angle and velocity ARE exposed, but through
  dm_control observables reading `qpos`/`qvel` directly (`joints_pos`, `joints_vel` from
  `legacy_base.WalkerObservables`), not through MuJoCo sensors.
- Campaniform-sensilla stand-in: the closest thing is the 6 tarsal `force` sensors (3-axis
  contact force at the distal tarsus) plus the 6 binary-ish `touch` sensors at the claws.
  There is **no strain/load sensor anywhere proximal** (no femoral or tibial load channel,
  nothing on coxa/trochanter), and no `jointpos`-style hair-plate/chordotonal analogue in
  the XML — joint angle only via qpos. Adding `<jointpos>`/`<jointvel>`/`<actuatorfrc>` or
  more `<force>` sites would be a trivial XML edit.
- Two eye cameras exist (`eye_right`, `eye_left`, fovy set to 150° by the walker,
  32×32 px default) for the vision-guided flight task.

## 7. Observables (exact dm_control keys)

VERIFIED from `tests/test_core.py` and `tests/test_walking_env.py`, which assert the full
observation_spec key list.

`template_task()` (10 keys):
```
walker/accelerometer        walker/actuator_activation  walker/appendages_pos
walker/force                walker/gyro                 walker/joints_pos
walker/joints_vel           walker/touch                walker/velocimeter
walker/world_zaxis
```
`walk_imitation()` adds 2 tracking keys → 12:
```
walker/ref_displacement     walker/ref_root_quat
```
Other observables defined in `FruitFlyObservables` (`flybody/fruitfly/fruitfly.py:594-753`)
but disabled unless a task enables them: `thorax_height`, `abdomen_height`,
`world_zaxis_hover`, `world_zaxis_abdomen`, `world_zaxis_head`, `self_contact`,
`left_eye`, `right_eye` (vision flight enables the eyes and adds `walker/task_input`);
`walk_on_ball` adds `walker/ball_qvel`.
Groupings: `vestibular = [gyro, accelerometer, velocimeter, world_zaxis]`,
`proprioception = [joints_pos, joints_vel, actuator_activation]` — both enabled for every
task at `tasks/base.py:169-175`.
`appendages_pos` = egocentric xyz of the 6 claw sites + `head` site (see `appendages`
property), i.e. 21 numbers.

## 8. Timesteps

VERIFIED:
- MJCF: `<option timestep="0.0001" gravity="0 0 -981" density="0.00128" viscosity="0.000185"
  cone="elliptic" noslip_iterations="3"/>` → **physics dt = 1e-4 s in the raw XML** (CGS units,
  air density/viscosity set for the fluid model).
- Task constants (`flybody/tasks/constants.py`):
  - walking: `_WALK_PHYSICS_TIMESTEP = 2e-4`, `_WALK_CONTROL_TIMESTEP = 2e-3` → **500 Hz control,
    5 kHz physics, buffer_size 10**
  - flight: `_FLY_PHYSICS_TIMESTEP = 5e-5`, `_FLY_CONTROL_TIMESTEP = 2e-4` → 5 kHz control,
    20 kHz physics (wingbeat base freq 218 Hz, `_WING_PARAMS`)
- **10 ms control interval (100 Hz): yes, mechanically possible** — `physics_timestep` and
  `control_timestep` are plain constructor args threaded to `composer.Task.set_timesteps`
  (`tasks/base.py:168`), and control_timestep only has to be an integer multiple of
  physics_timestep (it also sets the observable averaging `buffer_size =
  round(control_timestep/physics_timestep)`, `fruitfly.py:170`). Caveat, not verified
  empirically: the shipped position-servo gains and the 0.01 s actuator filter were tuned
  at 2 ms; at 10 ms the trained policies will not transfer and leg control may be unstable.
  Nothing in the code forbids it.

## 9. Shipped policies / training

VERIFIED from `flybody/download_data.py` (figshare DOI 10.25378/janelia.25309105), four
downloadable bundles:
| key | figshare file id |
|---|---|
| `trained-policies` | 44815195 |
| `walking-imitation-dataset` | 51196868 |
| `flight-imitation-dataset` | 51196859 |
| `controller-reuse-checkpoints` | 51196886 |

Tasks shipped (`flybody/fly_envs.py`): `walk_imitation` (tracks a mocap "ghost" fly,
time_limit 10 s, 64 future reference steps), `flight_imitation` (tracks a flight
trajectory, wingbeat pattern generator, time_limit 0.6 s, 5 future steps),
`vision_guided_flight` (bumps or trench arena, eye cameras, time_limit 0.4 s),
`walk_on_ball` (tethered fly on a floating ball, time_limit 2 s), `template_task` (no-op).

Algorithm: **distributed DMPO** (distributional Maximum a-posteriori Policy Optimisation)
built on DeepMind **acme** + TensorFlow/sonnet, parallelised with **Ray**
(`flybody/train_dmpo_ray.py`, `flybody/agents/ray_distributed_dmpo.py`,
`agents/agent_dmpo.py`, `agents/learning_dmpo.py`, `agents/losses_mpo.py`). Policies are
TF/sonnet networks (`agents/network_factory.py`, `network_factory_vis.py`) — you need the
`[tf]` extra to load a checkpoint.

## 11. Tarsal adhesion — how

VERIFIED. Adhesion is MuJoCo's native `<adhesion>` actuator, not sticky contacts:
- 6 claw adhesion actuators, `body="claw_T{1,2,3}_{left,right}"`, `ctrlrange="0 1"`,
  `gain="0.985"` (class `adhesion_claw`); 2 more on the labrum with `gain="1"`.
- They act on the geoms of that body that are in contact; the relevant geoms/sites are in
  class `adhesion-collision`, which sets `friction="0.6"`, `margin="0.0005"`,
  `gap="0.0005"` — the `margin`/`gap` pair is what gives the adhesion actuator a
  near-contact band to pull across without generating normal force.
- The claw collision geoms are capsules `tarsal_claw_T*_collision` (r ≈ 0.002 cm) and the
  touch-sensor sites `claw_T*` are co-located capsules ~10 % longer.
- At runtime `adhesion_filter=0.007` s wraps them in a first-order filter
  (`dyntype="filter"`), so adhesion has ~7 ms on/off dynamics rather than instant grip;
  `Walking(adhesion_gain=...)` lets a task override the 0.985 gain (`tasks/base.py:392-395`).
- Adhesion is part of the action vector (6 of the 59 walking actions), so the policy
  actively decides when each foot sticks.

## 12. flygym 2.1.0 vendored copy vs upstream

VERIFIED by canonical XML comparison (both parsed, element-by-element).
`flygym/src/flygym/assets/model/flybody/fruitfly.xml` vs upstream `fruitfly.xml`:
- **Same model.** Identical element counts: 102 hinge joints + freejoint, 67 bodies,
  159 geoms, 15 sites, 8 tendons, 70 general + 8 adhesion actuators,
  6 force + 6 touch + accelerometer + gyro + velocimeter sensors.
  **No sensors added, no adhesion added, no DoFs added.**
- Only 7 attribute-level differences, all cosmetic/ housekeeping:
  1. `<compiler>` gains `meshdir="assets"`.
  2. `<visual>` and `<statistic meansize="0.02">` blocks deleted (flygym sets its own).
  3. The six touch-sensor sites `claw_T{1,2,3}_{left,right}` have their `fromto` shortened
     to exactly match the claw collision capsule (upstream they are ~10 % longer). Tiny
     reduction in touch-sensor volume; nothing else.
  Plus pure line-rewrapping throughout (the 667-line diff is ~99 % whitespace).
- IMPORTANT: flygym's actual `FlyBody` class does **not** load this XML. It rebuilds the
  model from parsed YAML (`assets/model/flybody/{rigging,joints,actuators,visuals,vision,
  all_geom_suffixes}.yaml`) via `src/flygym/flybody/parse_flybody.py`, in **mm** units
  (SCALE=1.0; lengths ×10, gravity −981 cm/s² → −9810 mm/s², torque-valued quantities ×100
  — stated in the `FlyBody` class comment, `compose/fly/flybody.py:105-112`). Differences
  that matter if you use flygym's FlyBody rather than the raw XML:
  - Joint naming is rewritten to flygym's own scheme:
    `c_thorax-lf_coxa-{pitch,roll,yaw}`, `lf_coxa-lf_trochanterfemur-{pitch,roll}`,
    `lf_trochanterfemur-lf_tibia-pitch`, `lf_tibia-lf_tarsus1-pitch`,
    `lf_tarsus1-lf_tarsus2-pitch` … (legs lf/lm/lh/rf/rm/rh). Axis convention
    `FlyBodyRotationAxis`: pitch=x, roll=y, yaw=z (wings swap: pitch=y, roll=x).
  - Gains are the upstream ones ×100 (`actuators.yaml`: head kp 10, antenna/labrum 1,
    abdomen 10, coxa-femur 80, tarsus-tibia 40, wing yaw/roll/pitch 300/200/100).
  - Adhesion is **not** in the rebuilt model by default; you call
    `FlyBody.add_leg_adhesion(add_labrum=...)` which creates `<tarsus5>-adhesion`
    actuators (`compose/fly/flybody.py:709-760`).
  - flygym 2.1.0 pins `mujoco>=3.9,<3.10` (and optional `mujoco_warp>=3.9,<3.10`) —
    a different engine pin from flybody, which pins nothing.
  - flygym's docstring miscites the paper title (see §1).

## 10. Has anyone driven flybody from a connectome / spiking network?

**Short answer: one real academic paper (FlyWire → flybody, but with a *learned decoder*,
not motor neurons), and a cluster of 2026 hobbyist GitHub projects most of which use
flygym/NeuroMechFly rather than flybody. Nobody has published a MANC/FANC leg-motor-neuron
→ flybody leg-actuator mapping.** Sources below are second-hand (web search + page fetch),
not repo-verified, except where noted.

### The one peer-reviewable paper
**"Whole-Brain Connectomic Graph Model Enables Whole-Body Locomotion Control in Fruit Fly"**
(FlyGM) — Zehao Jin, Yaoye Zhu, Chen Zhang, Yanan Sui. arXiv **2602.17997** (v1 submitted
2026-02-20; v3 by 2026-06-14). DOI 10.48550/arXiv.2602.17997. Project pages
`https://lnsgroup.cc/research/FlyGM`, `https://sites.google.com/view/flygm`. Reported
second-hand from the arXiv HTML:
- Uses **flybody** (explicitly, "a biomechanical model of the fruit fly implemented in
  MuJoCo") + the **FlyWire FAFB v783** whole-brain connectome, as a graph-structured
  controller. PyTorch + PyTorch Geometric.
- Neurons partitioned into "afferent, intrinsic, and efferent sets". Output is **not** a
  motor-neuron→actuator mapping: "The updated efferent states H_{t+1}[V_e] are flattened
  and mapped to continuous motor actions by a decoder Dec_φ" — i.e. a **learned readout**.
- Tasks: gait initiation, straight-line walking, turning (walking action dim **59**,
  "joint actuators and adhesion controls" — matches §5 exactly), and flight (action dim 12:
  wing torques, pattern-generator modulation, body joints).
- Algorithm: **PPO**, two-stage (imitation then RL fine-tune). Baselines: degree-preserving
  rewired connectome, Erdős–Rényi graph, 4×512 MLP, and a spiking net.
- No direct source-code repo URL found.

### Adjacent but NOT flybody-embodied
- Pugliese et al., **"Connectome simulations identify a central pattern generator circuit
  for fly walking"**, bioRxiv **10.1101/2025.09.12.675944** (posted 2025-09-12). Dynamic
  simulation of the *Drosophila* VNC connectome; identifies a minimal CPG (1 inhibitory +
  2 excitatory interneurons), validated optogenetically. **I could not confirm any
  biomechanical embodiment** — the fetched abstract page gives no body model. Treat as
  neural-only until checked against the full text.
- Wang-Chen & Ramdya, **"The embodied brain: Bridging the brain, body, and behavior with
  biorealistic neuromechanical models"**, arXiv **2601.08056** (2026) — review. Abstract
  fetched; did not confirm flybody-connectome coverage.
- **FlyMimic**, "Musculoskeletal simulation of limb movement biomechanics in *Drosophila
  melanogaster*", arXiv **2509.06426**, ICLR 2026 (second-hand). This is the Hill-type
  muscle fly now vendored in flygym (`compose/fly/musculoskeletal.py`, VERIFIED locally:
  15 Hill-type muscles + 15 spatial tendons on the **left front leg only**,
  `dyntype=mjDYN_MUSCLE`). **It is a different body, not flybody.**

### 2026 GitHub projects (hobbyist / unreviewed — flag as such)
- `jamesbiederbeck/flybody-connectome` — "A Drosophila body in MuJoCo driven by the MaleCNS
  v1.0 connectome". MIT, 0 stars, experimental. Uses **flygym's experimental FlyBody**,
  MaleCNS v1.0 (166,700 neurons / 25.6M synapses), spiking, brain at ~30 Hz vs physics at
  10 kHz. Crucially its own README admits the motor seam is unsolved: motor commands are
  decoded from **descending neurons (DNp20, DNpe017)**, not motor neurons, because
  "Vision reaches the descending neurons and stops there"; the 708 VNC motor neurons get no
  retinal drive, and "The loop is closed, but there is no visual information in it yet."
- `Ibtisam-Mohammad/Fly.exe` — MaleCNS v1.0 (165,122 neurons, 25.5M edges), GeNN/CUDA LIF,
  GPL-2.0, ~19 stars. **Explicitly says flybody was "consulted … and not used"** — the body
  is NeuroMechFly v2 / FlyGym 2.1.0, and "The gait is a published pattern generator, not
  the simulated ventral nerve cord."
- `abgnydn/webgpu-fly` — WebGPU/WASM, FlyWire + MANC + "a Flybody body", explicitly
  "approximate motor mappings".
- Others in `cobanov/awesome-fly`: `seven-monarchs/NeuroFly`, `erojasoficial-byte/fly-brain`,
  `Ma-Dan/fly-brain`, `anupamme/fly-brain` (+ mirrors), `freewangfei/digitalfly` — these are
  FlyWire/maleCNS → **NeuroMechFly**, not flybody.

### Bottom line for the transplant
The specific thing — **VNC leg motor neurons (MANC/FANC/BANC) driving flybody's 48 leg
actuators, one motor-neuron pool per joint** — appears to be **unoccupied**. Every existing
attempt either (a) learns a decoder on top of the graph (FlyGM), (b) stops at descending
neurons and hands off to a pattern generator (Fly.exe, flybody-connectome), or (c) uses a
different body. The blocker everyone hits is the same: flybody has **no muscles** (§5), so
there is no anatomical target for a motor neuron to innervate; you must invent the
MN-pool → joint-torque map yourself.
