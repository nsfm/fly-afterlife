# Wang N, Babski H, Perdomo JE, McMahan SB, Ramakrishnan A, Biswas T, Bhandawat V (2025)
**"Passive muscle forces in Drosophila are large but insufficient to support a fly's weight."**
**PREPRINT** - bioRxiv 2025.04.29.651225 (v2); deposited in PMC as PMC12324252, PMID 40766569.
CC-BY. Drexel University + Janelia. Read in full via PMC.

**This is the only direct measurement of passive joint stiffness in a Drosophila leg that I found.**
Everything else in the fly-modelling literature either imports it from bigger insects or hand-tunes it.

## Method
`VGlut-Gal4; UAS-GtACR1` - all motor neurons are glutamatergic in *Drosophila*, so green light
silences the entire motor pool. A tethered fly is rotated through five body angles (-30° to +30°)
with a precision rotational drive; a small weight is waxed to one leg to make the gravitational
torque measurable; two cameras + DLT give the 3-D leg configuration. Since only gravity and passive
forces remain, the equilibrium angle at each body orientation gives one (torque, angle) point.
Linear regression of torque vs angle -> spring constant K and rest angle theta_0.
Control: silencing octopaminergic neurons as well changed nothing.

## Result: passive torque is a LINEAR angular spring
Verbatim: *"the passive torques are well approximated by a linear spring, i.e., the passive torques
linearly increase with angular deviation from the rest angle"* and *"the passive torques in each
joint is well described as a linear spring over a relatively large range of motion that extends over
40 degrees on each side of the rest position"*.

Four DoFs measured on each of the three right legs: thorax-coxa **retraction-protraction** and
**pronation-supination**, coxa-trochanter **levation-depression**, and femur-tibia
**extension-flexion**. (Tibia-tarsus not measured.)

## Table 1 - median stiffness, transcribed exactly as published
Caption reads "Median stiffness for each of the measured joints in **mN/°**", but the Discussion
gives the same numbers as **Nm/°**: *"The median stiffness of all the joints we investigated lie
within a 7-fold range from 8X10^-9 Nm/° for the levation-depression in the mesothoracic leg to
6X10^-8 Nm/° for the retraction-protraction in the metathoracic leg."*
**The two unit strings disagree; I could not resolve which is correct.** I re-read the bioRxiv v2
full text as well as the PMC version - the same contradiction appears in both (table caption "mN/º",
discussion "Nm/°"), and the figure axis labels are not extractable from the HTML. Numbers as printed:

| leg | Lev-Dep (CTr) | Ret-Pro (ThC) | **Ext-Flex (FTi)** | Pro-Sup (ThC) |
|---|---|---|---|---|
| prothoracic (T1) | 1.5e-8 | 1.9e-9 | **1.7e-8** | 1.5e-8 |
| mesothoracic (T2) | 8.6e-9 | 1.1e-8 | **2.5e-8** | 1.0e-8 |
| metathoracic (T3) | 2.7e-8 | 5.6e-8 | **1.7e-8** | 4.7e-8 |

If the unit is **N·m/deg**, the T1 femur-tibia value converts to **9.7e-7 N·m/rad ≈ 1 µN·m/rad**.
If the unit is really N·m/rad, T1 FTi = **1.7e-8 N·m/rad = 17 nN·m/rad**.

**My consistency check (do this before using the number).** Azevedo et al. 2020's force probe had
k = 0.2234 N/m at a 417 µm lever arm, i.e. an equivalent rotational stiffness of
k·L² = 0.2234 x (417e-6)² = **3.9e-8 N·m/rad ≈ 39 nN·m/rad**. In that prep a single fast-MN spike
(4.2 nN·m of joint torque) deflected the tibia ~7°, so the *total* load (probe + joint) was
≈ 35 nN·m/rad - which means the fly's own passive FTi stiffness there must have been **at most a few
tens of nN·m/rad**. That is compatible with the "N·m/rad" reading (17 nN·m/rad) and is ~25x too
soft for the "N·m/deg" reading (970 nN·m/rad). I lean to the smaller value but flag it as unresolved.
Also note Azevedo's flies were intact, so their "passive" joint carried slow-MN tonic tone, which
should make it *stiffer*, not softer - which sharpens the contradiction rather than explaining it.

Spread: interquartile range implies ~2-fold variation across flies (~30% either side of median).
Calibration/reconstruction error contributes <5%; the rest is biological.
Across legs: *"The spring constant for the prothoracic legs are about 50% larger than the stiffness
of the mesothoracic legs except for the retraction-protraction axis ... The spring constants for the
metathoracic leg is much higher."*

## Headline conclusion
Passive torques are **much bigger than the leg's own gravitational torque** (so the leg's rest
posture is gravity-independent, as in stick insect) but **~70x (their OpenSim model says ~100x)
too small to hold the fly up.** In simulation with the measured stiffness the fly falls in ~20 ms,
close to free-fall; a **40-fold uniform increase** in passive stiffness was needed before the
modelled fly could support itself.

## Active-force decay time constant (useful for a muscle model!)
- From silencing experiments in freely standing flies they estimate **active forces decay with a
  time constant of ~100 ms**, and separately *"it takes about 350 milliseconds for the active forces
  to decay"* in the tethered prep (they model the stiffness decaying exponentially).
  These two numbers are quoted in different places in the paper; treat the ~100 ms as the modelled
  decay constant and the ~350 ms as the observed settling time. Both include GtACR1 silencing
  latency, so they are upper bounds on muscle relaxation.
- Same fly stands at very different heights on different trials; time-to-fall increases with height.

## Table 2 - body and leg geometry used in their OpenSim model, "Ellipsoid radii (µm)"
| body | major | median | minor |
|---|---|---|---|
| head | 650 | 600 | 360 |
| thorax | 800 | 640 | 630 |
| abdomen | 1080 | 700 | 700 |
| T1 coxa | 339.7 | 120 | 120 |
| T1 femur | 538.1 | 119 | 119 |
| T1 tibia | 452.4 | 68.3 | 68.3 |
| T1 tarsus | 571.4 | 39.8 | 39.8 |
| T2 coxa | 137.2 | 120 | 120 |
| T2 femur | 670 | 119 | 119 |
| T2 tibia | 603.6 | 68.3 | 68.3 |
| T2 tarsus | 698.6 | 39.8 | 39.8 |
| T3 coxa | 173.8 | 120 | 120 |
| T3 femur | 667.2 | 119 | 119 |
| T3 tibia | 605.9 | 68.3 | 68.3 |
| T3 tarsus | 761.4 | 39.8 | 39.8 |
**Caveat on these too:** called "radii", but if taken as semi-axes the T2 femur would be 1.34 mm
long and 238 µm thick, which is about twice a real fly. Read as **full segment length and diameter**
they match published *Drosophila* leg dimensions well. Treat as lengths, flag the ambiguity.
(This is nonetheless the cleanest per-leg-pair, per-segment geometry table I found.)

## Comparative context the paper itself gives
- Passive FTi forces previously measured only in **large insects**: locust, stick insect, false stick
  insect (their refs 1, 3-7, incl. Ache & Matheson 2013). Linearity here matches the locust.
- **Hysteresis**: in locust, stick insect and false stick insect there is a ~10° difference in rest
  position depending on the direction of approach. (Their ref 4 = locust; 1 = stick insect; 5.)
