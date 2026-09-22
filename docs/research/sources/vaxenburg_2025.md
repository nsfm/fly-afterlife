# Vaxenburg et al. 2025 — flybody

**Whole-body physics simulation of fruit fly locomotion.**
Roman Vaxenburg, Igor Siwanowicz, Josh Merel, Alice A Robie, Carmen Morrow, Guido Novati,
Zinovia Stefanidi, Gert-Jan Both, Gwyneth M Card, Michael B Reiser, Matthew M Botvinick,
Kristin M Branson, Yuval Tassa, Srinivas C Turaga.
*Nature* **643**, 1312–1320 (2025). DOI **10.1038/s41586-025-09029-4**.
PMID 40267984 (per PMC listing, second-hand).
Preprint: bioRxiv **10.1101/2024.03.11.584515** (v2).
Supplementary data: figshare DOI **10.25378/janelia.25309105**.
Code: https://github.com/TuragaLab/flybody — Apache-2.0.

Citation block VERIFIED verbatim from the repo README at commit
`d015e9bfe441bd90ae431bac24c55cb74bdbce26` (2025-07-30).

Note: flygym 2.1.0 miscites this DOI under the title "A whole-body model of *Drosophila*
with precise neuromuscular connectivity" (`compose/fly/flybody.py` docstring). The Nature
title is the one above.

Model facts extracted from the released MJCF (see
`docs/physiology/leg_biomech_parts/flybody.md` for the full derivation):
nq=109, nv=108, nu=78; 1 free joint + 102 hinges; 66 leg DoF (11/leg, 8 actuated);
70 position-servo `general` actuators + 8 `adhesion`; **no muscle actuators**;
15 sensors (3 IMU-ish on thorax, 6 tarsal force, 6 claw touch); MJCF timestep 1e-4 s,
CGS units (gravity −981).

---

# Related, connectome side

- **FlyGM** — Jin, Zhu, Zhang, Sui. "Whole-Brain Connectomic Graph Model Enables Whole-Body
  Locomotion Control in Fruit Fly." arXiv **2602.17997** (2026-02-20; v3 2026-06-14).
  FlyWire FAFB v783 connectome as a graph controller → **flybody**; efferent states →
  learned decoder → 59-dim walking action / 12-dim flight action; PPO after imitation
  pretraining. Project page https://lnsgroup.cc/research/FlyGM. (Second-hand, from arXiv HTML.)
- **Pugliese et al.** "Connectome simulations identify a central pattern generator circuit
  for fly walking." bioRxiv **10.1101/2025.09.12.675944** (2025-09-12). VNC connectome
  dynamics; minimal CPG = 1 inhibitory + 2 excitatory interneurons; optogenetic validation.
  Embodiment unconfirmed. (Second-hand, abstract page only.)
- **Wang-Chen & Ramdya.** "The embodied brain: Bridging the brain, body, and behavior with
  biorealistic neuromechanical models." arXiv **2601.08056** (2026). Review. (Second-hand.)
- **FlyMimic** — "Musculoskeletal simulation of limb movement biomechanics in *Drosophila
  melanogaster*", arXiv **2509.06426**, ICLR 2026. Hill-type muscle fly; vendored in
  flygym 2.1.0 as `compose/fly/musculoskeletal.py` (15 muscles + 15 spatial tendons,
  left front leg only — VERIFIED locally). Not flybody.

---

## (appended by the MN->force/torque physiology pass) mass, geometry and MJCF joint parameters

Crossref-verified citation: *Nature* **643**:1312-1320, doi:10.1038/s41586-025-09029-4, 2025-07-31.
Preprint title differs: "Whole-body simulation of realistic fruit fly locomotion with deep
reinforcement learning", bioRxiv 2024.03.11.584515.

### body mass - MEASURED by weighing flies (bioRxiv methods, verbatim)
> "The components representing head, thorax, abdomen, wings and legs were assigned densities based
> on average values from weighing 2 groups of 30 and 22 disassembled wild type female flies:
> head - 0.15 mg, thorax - 0.34 mg, abdomen - 0.38 mg, legs (each) - 0.0162 mg, wings (each) -
> 0.008 mg. This corresponds to total fly mass of 0.983 mg. The full body length of the model is
> 0.297 cm, wing span 0.604 cm."

head 0.15 / thorax 0.34 / abdomen 0.38 / **each leg 0.0162** / each wing 0.008 mg; **total 0.983 mg**;
body length 2.97 mm; wingspan 6.04 mm; adult wild-type female.
**No per-segment or per-leg-pair (T1/T2/T3) mass breakdown is published** - one number for all six
legs. Verified absent.

### units of the MJCF
`<option timestep="0.0001" gravity="0 0 -981" density="0.00128" viscosity="0.000185">` =>
**cm, g, s** (gravity 981 cm/s²; air density 1.28e-3 g/cm³; air viscosity 1.85e-4 poise).
So 1 force unit = 1 dyne = **10 µN**; 1 torque unit = 1 dyne·cm = **1e-7 N·m**.
Tissue densities: body 0.478, head 0.713, abdomen 0.555, **legs 1.18 g/cm³**.

### leg joint stiffness / damping / armature (read from fruitfly.xml in mujoco_menagerie)
| parameter | MJCF | SI |
|---|---|---|
| leg joint stiffness (default) | 0.01 | 1e-9 N·m/rad |
| leg joint damping (coxa, femur) | 0.01 | 1e-9 N·m·s/rad |
| tibia joint damping | 0.004 | 4e-10 N·m·s/rad |
| tarsus (`extend_tarsus`) | stiffness 0.1, damping 0.002 | 1e-8 N·m/rad, 2e-10 N·m·s/rad |
| armature (all body joints) | 1e-06 | 1e-13 kg·m² |
others: head stiffness 0.03 / damping 0.001; wing 0.01 / 0.0005; abdomen 0.05 / 0.01;
antenna damping 0.0003; haltere `springdamper="0.005 0.1"`.

### actuation: position servos, not muscles
`biastype="affine"`, coxa/femur `gainprm="0.8"`, tibia/tarsus `gainprm="0.4"` (dyne·cm/rad).
Methods, verbatim:
> "8 actuators in each leg (coxa: 3, femur: 2, tibia: 1, tarsus: 2), using desired angle (position)
> semantics, with gains chosen so that a force of approximately one body weight can be applied at
> the end-effector at the base pose."
> "6 adhesion actuators at the claws which can apply a force up to 1× body weight."

### provenance warning
The methods describe fitting **only the wing** actuator gain and wing joint damping (against a
hovering wing trajectory from Dickson et al. 2008), then the MuJoCo fluid coefficients. Grepping the
full methods for "damping" turns up nothing about legs. **The leg stiffness/damping values are
hand-chosen and are not traceable to any measurement** - do not cite them as fly passive-joint data.
Leg `springref` rest angles were fitted to images of *flying* (leg-retracted) flies.
For measured *Drosophila* passive joint stiffness see `wang_2025_passive.md`; flybody's leg
stiffness sits ~20x below even the low reading of that measurement.

### not in this paper (checked)
no muscle model, no motor neurons, no force-per-spike, no twitch, no measured passive joint torque.
