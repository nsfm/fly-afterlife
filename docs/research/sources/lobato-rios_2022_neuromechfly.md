# NeuroMechFly v1 and v2 (Ramdya lab)

**v1:** Lobato-Rios V, Ramalingasetty ST, Özdil PG, Arreguit J, Ijspeert AJ, Ramdya P (2022)
"NeuroMechFly, a neuromechanical model of adult Drosophila melanogaster."
*Nature Methods* **19**:620-627. doi:10.1038/s41592-022-01466-7 (volume/pages verified via Crossref).
Preprint: bioRxiv 2021.04.17.440214 v3 - full methods read from there.
**v2:** Wang-Chen S, Stimpfling VA, Lam TKC, Özdil PG, Genoud L, Hurtak F, Ramdya P (2024)
"NeuroMechFly v2: simulating embodied sensorimotor control in adult Drosophila."
*Nature Methods* **21**:2353-2362, doi:10.1038/s41592-024-02497-y (volume, pages and December 2024
date VERIFIED via Crossref). Code = `flygym` (github.com/NeLy-EPFL/flygym).

## Body (v1, verbatim from methods)
> "The full body length and mass of the model are set to 2.8 mm and 1 mg ... these masses were:
> head (0.125 mg), thorax (0.31 mg), abdomen (0.45 mg), wings (0.005 mg), and legs (0.11 mg)."
Sourced (their ref 83) from **Szczecinski NS, Bockemühl T, Chockley AS, Büschges A (2018) "Static
stability predicts the continuum of interleg coordination patterns in Drosophila", J Exp Biol 221**
(I could not open that paper - JEB is behind Cloudflare - so the segment masses are second-hand).
Body separated into **65 segments**; 11 hinge joints per leg (multi-DoF joints modelled as unions
of hinges). Physics: PyBullet, timestep down to 0.1 ms.
Fig S1 of the preprint plots **measured leg segment lengths for real 1-3 dpe female flies vs the
model** as violin plots - numbers are not in the caption and I did not digitise them.

## Actuation (v1) - this is not a muscle model
Kinematic replay uses a **PD position controller**; they swept K_p and K_d from 0.1 to 1.0 and
**selected K_p = 0.4, K_d = 0.9**. They warn explicitly that estimated torques and ground-reaction
forces scale with the gains and there are no experimental data to validate them.

For the CPG-driven walking they used an **"Ekeberg-type" muscle model** - a torsional spring-damper,
torque as a linear function of antagonist flexor/extensor CPG activity:
parameters **alpha (gain), beta (stiffness gain), gamma (tonic stiffness), delta (damping
coefficient)** plus Delta-phi (offset from rest angle). 5 parameters per joint x 9 joints = 45 of the
63 free parameters, all set by **NSGA-II optimisation for walking speed + static stability**, not
measured. Bounds are in their Table 6 (not reproduced in the HTML I read).
Origin of the Ekeberg formulation: **Ekeberg Ö, Blümel M, Büschges A (2004) "Dynamic simulation of
insect walking", Arthropod Structure & Development 33:287-300** - a **stick insect** model.
Oscillator intrinsic frequency was constrained to **6-10 Hz**.

## Force scale sanity check they themselves make (verbatim, v1 preprint)
> "Associated leg and antennal contact forces ... reached magnitudes about three times the fly's
> weight. These fall within the range of previously observed maximum forces measured at the tip of
> the tibia (~ 100 µN) for ballistic movements"
i.e. NeuroMechFly's own forces are calibrated against **Azevedo et al. 2020's ~100 µN**.

## Other constraints they cite (all second-hand from them)
- slowest reported *Drosophila* walking speed **10 mm/s**, highest **34 mm/s**.
- joint angular velocity capped at **250 rad/s**, "a value measured from real fly experiments".
- duty factor range **0.4-0.9**.
- spherical treadmill: mass 54.6 mg, radius 5 mm, friction 1.3; leg friction raised 0.5 -> 1.0.

## Bottom line for us
NeuroMechFly (either version) contains **no motor neurons, no twitch, and no measured muscle
parameters**. It is a well-made body with torque/position actuators and optimised spring-damper
"muscles". The Özdil et al. 2025 Hill-type model (see `ozdil_2025.md`) is the muscle layer that was
later bolted onto it, and even that has no spike-to-force stage.
