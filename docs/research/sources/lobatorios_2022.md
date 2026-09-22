# Lobato-Rios et al. 2022 — NeuroMechFly v1

**Citation** (VERIFIED — copied from the repo README's own BibTeX block):
Lobato-Rios V, Tata Ramalingasetty S, Özdil PG, Arreguit J, Ijspeert AJ, Ramdya P.
"NeuroMechFly, a neuromechanical model of adult *Drosophila melanogaster*."
*Nature Methods* **19**(5):620–627 (2022). DOI **10.1038/s41592-022-01466-7**.

**Repo.** https://github.com/NeLy-EPFL/NeuroMechFly
Clone: HEAD `6fdc6212bcf5b71fcd47bca119876c92092c2cd6` (2024-10-11).
README banner, verbatim: *"This GitHub repository contains documentation for legacy code … NeuroMechFly
has since been updated, and this repository is no longer actively maintained."*

**Licence.** **Apache-2.0** — `LICENSE` is verbatim Apache License 2.0; `setup.py` has
`license='Apache 2.0'`. VERIFIED.

**Physics.** **PyBullet**, unpinned (`setup.py` `install_requires` contains bare `'pybullet'`).
Also depends on `farms_container` and a Cython extension
`NeuroMechFly/simulation/bullet_sensors.pyx`. VERIFIED.

**Body file.** SDF, not MJCF/URDF: `data/design/sdf/neuromechfly_noLimits.sdf`
(variants: `neuromechfly_noLimits_ground.sdf`, `neuromechfly_locomotion_optimization.sdf`,
`neuromechfly_frontleg_cylinder_antenna_normal.sdf`,
`neuromechfly_frontleg_antenna_cylinder.sdf`). VERIFIED.

**DoFs, counted from `neuromechfly_noLimits.sdf`** (VERIFIED):
- 96 `<link>`, 95 `<joint>` — **92 revolute, 1 continuous, 2 prismatic**. The continuous +
  2 prismatic are the tether rig (`joint_revolute_support_1`, `joint_prismatic_support_1`,
  `joint_prismatic_support_2`), so the fly itself has **92 revolute DoFs**.
- Per leg, **11 revolute joints**: `joint_{L,R}{F,M,H}` +
  `Coxa`, `Coxa_roll`, `Coxa_yaw`, `Femur`, `Femur_roll`, `Tibia`, `Tarsus1`–`Tarsus5`
  → 66 leg joints.
- Non-leg joints present (which v2 later dropped): `joint_A1A2`, `A3`, `A4`, `A5`, `A6`
  (abdomen), `joint_LWing`/`_roll`/`_yaw` and right ditto (6), `joint_LHaltere`/`_roll`/`_yaw`
  and right ditto (6), `joint_Head`/`_roll`/`_yaw` (3), `joint_Haustellum`, `joint_Rostrum`,
  `joint_LEye`, `joint_REye`, `joint_LAntenna`, `joint_RAntenna`.
  Note v1 has a **single** antennal joint per side; v2 splits the antenna into
  pedicel/funiculus/arista with 3 DoFs each (9/side).

**The "7 DoFs per leg" claim.** The model has 11 joints per leg; **7 are actuated**
(`Coxa`, `Coxa_roll`, `Coxa_yaw`, `Femur`, `Femur_roll`, `Tibia`, `Tarsus1`), the 4 distal tarsal
joints passive. The joint *names* are VERIFIED from the SDF; the 7-actuated split is confirmed for
v2 by its SI (*"42 actuated leg degrees of freedom (DoFs, 7 per leg)"*) and v1 uses the same set —
but I did **not** read v1's own actuation config, so treat the v1 split as second-hand.

**Actuation.** Per-joint **position control** in PyBullet. **No muscles, no tendons, no Hill-type
actuators.** (Second-hand — inferred from the paper and the v2 lineage; I did not read
`NeuroMechFly/simulation/*.py`.)

**Proprioceptive feedback.** v1 exposes joint and contact sensors through the Cython
`bullet_sensors` extension and the paper's optimisation used ground-contact and joint state. No
campaniform / chordotonal / hair-plate model. Second-hand — extension declared in `setup.py`, not read.

**Default controller.** CPG network optimised by evolutionary search (the repo ships
`data/locomotion_network/` and `data/config/network/`), plus kinematic replay from
`data/joint_tracking/{walking,grooming}`. Second-hand from the README's experiment list.

**Verdict for this project.** Do not use. Unmaintained, PyBullet, superseded by flygym, and no
muscle model.
