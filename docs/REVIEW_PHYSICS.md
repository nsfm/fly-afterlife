# review: the body's physics (09-23, independent read)

question (nate, on `world/body/loop/state_pop_s12.mp4` and `state_dose60_s11.mp4`): are the forces right, is gravity right, is his
weight right? he looks heavy. and why do the hind legs never lift, in thirty-plus runs?

read: `docs/CAMPAIGN.md`, `docs/physiology/leg_biomech.md` (B1-B7), `force_per_spike.md`, `leg_biomech_parts/B_activation.md`,
`docs/research/sources/wang_2025_passive.md`, `docs/REVIEW_BODY_LOOP.md`, `experiments/body_loop.py`, `experiments/body_six.py`, the scratchpad
`body_build.py`, `results/body_dof_signs.json`, flygym 2.1's `compose/fly/base_fly.py`, `compose/world/base_world.py`, `compose/physics.py`,
`simulation.py`, `assets/model/neuromechfly/{mujoco_globals,rigging}.yaml`. checks are scripts in the session scratchpad (`scratchpad/phys/`:
`model.py`, `settle.py`, `limits.py`, `contacts.py`, `geom.py`, `sweep.py`, `lift.py`, `lift2.py`, `torques.py`, `clips.py`, `pitch.py`), each
building the body with `body_build.build()` (the loop's own construction). no project script changed.

both clips ran with `stiffness None` (**flygym's springs, 10**, not the 0.14 arm), `--adhesion contact --adhesion-gain 1`, `--mn-force azevedo`,
`--senses v2`, `--claw-labels 50flex`, full gravity. `state_pop_s12`: the recorded DN population, seed 12. `state_dose60_s11`: DNg100 at 60 Hz.

## verdict in one paragraph

gravity, units, mass and the spike-to-torque conversion are right. **the "heavy" look is real and is physics, but it is not gravity or mass.**
three things put him low: flygym's springs (10) cannot hold NeuroMechFly's neutral pose, so he sinks 0.6 mm (thorax 1.39 -> 0.78 mm)
until his **hind coxae hit the floor**; the loop's "body on the floor" number counts thorax, abdomen and head only, so the coxae's share
(45 % of his weight at rest) is invisible to it and is counted as leg load instead; and the hind coxa's pitch, the joint that carries the
body's sinking onto the hind legs, has **no motor neuron mapped to it**, only the spring. the hind legs never lift because **their levator
pool is silent** (0.00-0.20 nN.m mean against the ~4-8 nN.m it takes to lift a hind foot), and if one does lift, the leg's load sensor still
reads the coxa on the floor, so the load reflex holds it in stance.

## findings, ranked by how much they change what the clips mean

### P1. "1-6 % of his weight on the floor" leaves out the coxae. on flygym's springs he rests 45 % of his weight on his hind coxae (HIGHEST)

- **the statistic.** `body_loop.py:269`: `NONLEG = segments not prefixed by a leg name`: thorax, abdomen, head. the coxae are leg segments, so
  a coxa lying on the floor counts as the leg's load (line 255 reads the leg's contact sensor) and not as the body on the floor.
- **the sensor.** flygym builds one contact sensor per leg on the **subtree of the leg's most proximal ground-contact segment**, the coxa,
  against the floor, `reduce netforce` (`base_world.py:313-345`, `intprm [119, 3, 1]`). so `leg_force` is the whole leg's ground force
  (coxa, trochanter-femur, tibia, five tarsal segments), as a vector norm that includes friction, not the foot's.
- **measured, no muscles, flygym's springs, pads off** (`contacts.py`, per-geom normal force after 5 s): rh coxa 1.9-4.2, lh coxa 1.7-2.2,
  hind tarsi 1.2 + 1.2, mid tarsi (tarsus3, not the tip) 0.7-0.9, front tarsi 0.6-0.8 uN, of 10.05. `sweep.py` (mean of the last 0.5 s of 2 s):
  **feet 5.69, coxae 4.50, body 0.00 uN.** the loop's statistic would read this fly as 0 % on the floor.
- **in the clips** (`geom.py`: each saved frame re-posed from the logged joints and thorax pose, every segment's lowest mesh vertex):
  `state_pop_s12` lh coxa within 10 um of the floor on **78 %** of frames, rh coxa 45 %, abdomen tip 31 %; `state_dose60_s11` rm coxa **75 %**,
  rm trochanter-femur 64 %, the rostrum 27 %. the mid legs touch with tarsus3, not the tip, much of the time (19-60 %).
- **the hind foot test** (`lift2.py`): lift the left hind foot with a levation torque of 16 nN.m: the foot rises 0.47 mm and the **lh coxa
  takes 6.08 uN**; the lh `leg_force` reads 5.5 uN before and after (`lift.py`), never under the 0.05 threshold. a lifted hind foot reads
  loaded.
- consequence: the F2 fix of the first review counts only half of what it was for; "he stands on his feet" in any flygym-springs arm
  includes a squat on the hind coxae; the load rows (campaniform + untyped at 15 Hz x F / F_stand, clipped at 2) and `pad_on` are fed
  coxa contact.
- **fix.** foot load = the ground force on tarsus1-5 only (`sim.get_bodysegment_contact_forces("nmf", [f"{leg}_tarsus{i}" ...])`, world-z,
  summed per leg), for the load rows, `pad_on`, and `FL`. the standing statistic: every non-tarsal segment's ground force, coxae and
  femur-tibia included, under ~10 % of weight. log the coxa share separately in every arm.

### P2. he sits 0.6 mm below the model's neutral stance because flygym's springs are soft for this body; the neutral pose is not a six-foot stance (HIGH)

- **neutral pose** (`geom.py`, joints at `KinematicPosePreset.NEUTRAL`, thorax level): the lowest points are the hind tarsi; the thorax
  would sit **1.392 mm** up with the hind feet touching, the mid feet 0.155 mm and the front feet ~0.30 mm in the air. the hind coxae hang
  0.724 mm below the thorax origin, the abdomen 0.545.
- **settled on flygym's springs** (`settle.py`, 3 s, no cord, no torque): thorax **0.777 mm** (pads off), 0.763 (pads on contact), pitch
  -4.5 deg. every joint deflects 2-10 deg toward sinking (`limits.py`: hind coxa pitch +10, hind trochanter-femur -10, hind knee -7, mid
  coxa roll -7, mid trochanter -7); along a ~1.4 mm leg that adds up to the 0.6 mm drop. spring torques at that pose 0.3-1.8 nN.m per joint
  (largest: hind coxa pitch -1.75, hind trochanter-femur +1.77, hind knee +1.31); **no joint limit is engaged** (0 limit rows): the limits
  are not holding him.
- **the stiffness sweep** (`sweep.py`, where the weight rests after 2 s, uN):

| stiffness (nN.m/rad) | thorax z (mm) | tarsi | tibia + femur | coxae | thorax / abdomen / head |
|---|---|---|---|---|---|
| 0.14 (the "measured" arm) | 0.763 | 0.45 | 0.00 | 7.88 | 1.70 |
| 1 | 0.754 | 0.68 | 0.83 | 8.52 | 0.00 |
| 3 | 0.701 | 2.05 | 0.00 | 7.99 | 0.00 |
| **10 (flygym's; the clips)** | **0.777** | **5.69** | 0.00 | **4.50** | 0.00 |
| 20 | 0.850 | 10.02 | 0 | 0 | 0 |
| 50 | 1.093 | 9.73 | 0 | 0 | 0 |
| 700 | 1.198 | 10.05 | 0 | 0 | 0 |
| 10, gravity x0.3 | 1.029 | 3.05 | 0 | 0 | 0 |
| 10, gravity x0.1 | 1.146 | 1.02 | 0 | 0 | 0 |

  so this body needs ~20 to stand on its feet alone and ~50+ to stand near its neutral height. the clips' 0.752 (pop) and 0.658 (dose60)
  are at or below the passive squat; the command pulls him lower (as the second review found: 0.92 -> 0.68).
- **settling:** from the spawn he falls ~1 mm, touches at ~12 ms, and is within 10 um of his final height by 640 ms (pads off) / 89 ms
  (pads on); at 0.14, 655 ms, ending on the coxae and abdomen.
- **fix.** decide what "standing" is tested against: either run the standing arms on a stiffness that holds the neutral pose (>= 50), as
  a labelled prop the way `--gravity` is, or accept that on any honest stiffness he must stand on muscle (P3) and measure it on tarsal load.
  either way, **a spawn pose that is a six-foot stance** (the neutral pose puts the front feet 0.3 mm up and loads the hind legs first,
  which is part of why the hind legs carry the most) would remove a bias toward the hind legs.

### P3. the "measured" stiffness 0.14 is not a measurement; the sourced numbers contradict each other by 140x on this body (HIGH, for every 0.14 arm)

- 0.14 = flygym's 10 / 70 (SEAM 5128: "Wang 2025: ~70x weaker"): Wang's ratio (passive torque is ~70x short of holding the fly up)
  applied to flygym's default. but flygym's 10 does not hold this fly up either (P1-P2), so the ratio was applied to the wrong reference.
- `leg_biomech.md` B5 says "use ~2 x 10^-8 N.m/rad for T1 femur-tibia". in model units (g mm^2 s^-2 = nN.m) that is **20**, and Wang's
  table spans 9-56 nN.m/rad on that reading. on this body 20 stands him on his feet with no muscle (the sweep), which contradicts the
  paper's own headline that passive force cannot. the other reading (N.m/deg) is 55x stiffer and contradicts it harder. so the unit
  question does not resolve in favour of either printed number on this body; the headline ratio is the only usable anchor.
- a derivation from the headline on this body: it needs ~20 to stand on its feet; Wang's fly needs 40x (their simulation) to 70x (their
  estimate) more than it has, so **0.3-0.5**, labelled (E). 0.14 is in the same regime (he lies on his coxae and abdomen at 0.14, 1 and 3
  alike), so no 0.14 result changes; the label "measured" should.
- **fix.** relabel `--stiffness 0.14` as "derived, (E): flygym x 1/70"; if a number is wanted, 0.3-0.5 by the derivation above; correct B5's
  "use 2e-8" with this body's check.

### P4. the hind leg's coxa pitch and roll have no motor neuron; the weight sinks through them (HIGH for the hind legs)

- `results/body_dof_signs.json`: the hind legs' `protract` and `adduct` both map to **coxa yaw** (k 16 / 37, signs -1 and +1: the
  adductor is a second retractor, as the first review noted). the body-signs measurement chose yaw over pitch by a hair (forward
  displacement 0.393 vs 0.367 mm per unit), but hind coxa **pitch** moves the foot **0.505 mm up** per unit (the largest vertical lever of
  any hind joint). on the front and middle legs pitch is `protract` and roll is `adduct`; on the hind legs coxa pitch, coxa roll and
  trochanter-femur roll get **no cord torque** at all; the actuator exists and receives 0.
- that is the joint the body sinks through: at rest the hind coxa pitch deflects **+10 deg** on flygym's springs, **+32 deg** at 0.14,
  +33 at 0 (`limits.py`), more than any other joint, and positive hind coxa pitch is foot-up / body-down. no motor neuron can resist it.
- **fix.** map the hind promotor / remotor classes (and MNhl62, P5) to coxa pitch, or split them by the measured action (pitch for the
  vertical and fore-aft component, yaw for the rest), with the choice recorded in the json; re-measure body signs with the vertical
  component reported beside the forward one.

### P5. why the hind legs never lift: the levators are silent, and a lifted hind foot would still read loaded (the answer)

- **the torque it takes** (`lift.py`, flygym springs, pads on contact, a step of levation torque on the trochanter-femur pitch after 1 s of
  settling, other muscles 0): the left hind foot does not leave the floor at 1, 2 or 4 nN.m and rises 0.28-0.55 mm at 8-60. **threshold
  between 4 and 8 nN.m**; the middle foot has the same threshold (lifts from 8).
- **the torque the cord gives** (`torques.py`: each clip's 10 ms spike frames through body_loop's own map: ROLE, the json, f_w =
  (S / S_max)^1.2, `--mn-force azevedo`, K, sat 10, gain 42), mean after the warm-up, nN.m:

| leg | levation (Tr flexor + acc.) mean / p95 | depression (sternotrochanter + Tr extensor) mean | protraction / retraction mean |
|---|---|---|---|
| lh, pop / dose60 | **0.00 / 0.00**, **0.00 / 0.00** | 0.25, 3.59 | 2.43 / 0.72, 1.50 / 0.91 |
| rh, pop / dose60 | **0.20 / 1.46**, **0.01 / 0.00** | 0.47, 3.56 | 1.50 / 2.58, 1.33 / 1.37 |
| lm, pop / dose60 | 1.32 / 7.23, 0.34 / 2.22 | 0.26, 0.54 | 3.44 / 1.63, 1.27 / 3.63 |
| rm, pop / dose60 | **5.16 / 17.89**, **3.67 / 12.12** | 0.32, 0.06 | 4.01 / 1.35, 1.53 / 0.84 |

  the middle legs' levators cross the ~8 nN.m line in bursts (p95 7-18); the hind legs' never approach it.
- **the pools** (per-cell rates, both clips): hind `Tr flexor MN` lh **1 cell** (the mid legs have 7), 0.0 Hz; rh 5 cells, 0.0-0.5 Hz;
  hind `Acc. tr flexor MN` 8 / 4 cells, 0.0 Hz. the hind depressors are the busy side: `Sternotrochanter MN` 8.8 / 9.0 Hz per cell
  (dose60). the most active hind motor neurons are **MNhl62** (15.7-33 Hz pop, 6-8 dose60) and **MNhl59** (7-11 Hz), which `ROLE` does
  not map (`body_loop.py:182-186` maps MNml81 and MNhl65 only), nor MNhl01 / MNhl02 (1-4.5 Hz); `leg_biomech.md` A2 assigns MNhl62 to
  the promotor / anterior rotator class (high confidence), MNhl59 to it tentatively, MNhl01/02 to trochanter depression. none is a
  levator, so mapping them would not lift the foot; it is still the hind leg's largest motor output thrown away.
- **the senses are not the difference** (`world/leg_senses.npz`, per leg lf lm lh rf rm rh): campaniform + untyped 12 / 24 / 23 / 7 / 27 / 18,
  claw_50 1 / 14 / 18 / 0 / 12 / 17, hair plates 11 / 22 / 14 / 8 / 22 / 20: the hind legs have what the middle legs have.
- **the load is.** the hind legs carry the most: 38-68 % of the summed leg force in the last thirty full-gravity runs (pop_s12 68 %,
  dose60 38 %; the passive body 65 % on the two hind legs' subtrees, coxae included), the hind feet read loaded 73-100 % of the time, and their load
  rows sit at the clip (F >= 2 F_stand = 3.3 uN) for long stretches, which by the campaign's own lift read (the load reflex: campaniform
  rows drive stance) holds the depressors on. P1 makes that load partly the coxa's, and P1's lift test shows a hind leg cannot report
  unloading by lifting its foot while its coxa is down.
- **so:** in thirty runs the hind legs never lift because (1) their levator motor neurons never fire, and a leg carrying 2-4 uN cannot
  be lifted by 0.2 nN.m when it takes 4-8; (2) they carry the largest share of the weight, partly on the coxae, so their load rows (and
  the load reflex) stay in stance; (3) the joint that lets the body sink onto them (coxa pitch) has no muscle. (1) is the cord; (2) and
  (3) are this body and its sensor.
- **fix, in order:** P1 (tarsal load), P4 (hind coxa pitch mapped), a six-foot spawn pose (P2); then read the hind levators again. if they
  are still silent with the hind leg's load honest, the silence is the cord's.

### P6. mass: right to ~5 % for a female, ~15-25 % heavy for a male; the distribution matches (LOW)

- `rigging.yaml` masses in grams, compiled total **1.0243 mg** (`model.py`: `m.body_mass.sum()`); flygym's `mujoco_globals.yaml` bounds every
  body at `boundmass 1e-6` g, which raises the distal tarsal segments from ~0.1 to 1.0 ug each (+0.02 mg in all; 2 %).
- by part (the head is fused into `c_thorax` because `LEGS_ONLY` gives it no joint: 0.0946 of the thorax body's 0.4016 mg): **head 0.150,
  thorax 0.307, abdomen 0.450, legs 0.109 (0.017-0.020 per leg, hind heaviest), wings + halteres 0.008 mg.** against Vaxenburg 2025's
  weighed females (`leg_biomech.md` B7): 0.15 / 0.34 / 0.38 / 0.097 / 0.016, total 0.983. NeuroMechFly's split is Szczecinski 2018's
  (0.125 / 0.31 / 0.45 / 0.11). the model is a female-sized fly; the connectome is a male, and males are the smaller sex (~12 % by the end
  of pupal development, Testa et al. 2013, PMC3610704; female wet mass 1-1.5 mg on the same source). a male of ~0.8-0.9 mg would be
  15-25 % lighter: from the gravity sweep, a 20 % lighter fly sits ~0.05 mm higher on these springs. not what makes him look heavy.
- "10.0 uN" / "weight 10.05": **computed**, `body_loop.py:248`: `weight = m.body_mass.sum() * abs(m.opt.gravity[2])` = 1.0243e-3 g x 9810
  mm/s^2 = 10.05 g.mm/s^2 = 10.05 uN. the "10 uN" in `body_six.py`'s `--gain` help is Azevedo's round body weight, used only in the derivation.
- inertia: the compiled thorax body (with the head) 0.40 mg, principal inertia (7.1, 6.7, 3.1) x 10^-5 g.mm^2; leg joint-space inertia
  2.6-15 x 10^-6 g.mm^2 at coxa-tibia, of which the armature (1e-6) is 7-40 %; at the tarsal joints the armature is ~100 %. under the joint
  damping (P8) the leg's inertial time constant is ~2 x 10^-5 s, so neither matters to anything at 1 ms.
- fix (optional): scale the rigging masses by ~0.85 for a male, labelled.

### P7. adhesion: 1 uN per foot is a tenth of his weight, it does not hold him up, and nothing sources it (LOW for these clips)

- `add_leg_adhesion(gain=1.0)` (`body_build.py`, `body_loop.py:201`): a MuJoCo adhesion actuator on each tarsus5, control 0-1, force =
  gain x control in uN pulling the pad into its contacts. measured (`settle.py`, flygym springs, all pads on contact): the floor's vertical
  reaction on the legs rises from 10.20 to **16.07 uN** = weight + 6 x 1.0. on a flat floor the pull is internal to the foot-floor pair: it
  holds nothing up, adds 1 uN to what a levator must beat to peel a foot, and raises the normal force (so friction). he is not standing on
  his pads.
- `leg_force` net of pads = `max(|F| - gain x pad_on, 0)` (`body_loop.py:276`): a scalar subtracted from a vector norm that includes
  friction; right when the contact is vertical, approximate otherwise. the chatter the second review found is unchanged.
- sources: the repo's "a fly's pads hold several body weights" (`--adhesion-gain` help) has no citation; a search this pass found fly pad
  mechanics for *Musca* / *Calliphora* (attachment and detachment kinematics) and no *Drosophila* per-pad force. the number is (E).
- fix: label gain 1 as (E); feed the pads from tarsal load (P1).

### P8. joint damping 0.5 is unsourced and sets every leg speed (LOW-MEDIUM; not the heaviness)

- `add_joints(damping=0.5)` (flygym default, `base_fly.py:353`), unchanged by `--stiffness`. with inertia negligible, each joint is a first-
  order system: speed = torque / 0.5 rad/s per nN.m, relaxation time damping / stiffness = **50 ms at 10, 3.6 s at 0.14**. one fast spike's
  peak (4.2 nN.m) moves a free joint at <= 8.4 rad/s. no damping has been measured in a fly leg (B5); flybody's leg damping is 1e-9 N.m.s/rad
  (= 1 model unit). this is where the "slow, heavy" feel of a swing comes from if anything in the dynamics does; worth one arm at 0.1.

## what I checked and found sound

- **units.** flygym's NeuroMechFly is built at `SCALE = 1000` (mesh metres -> mm), masses in g (`rigging.yaml`), time in s: force
  g.mm.s^-2 = **uN**, torque g.mm^2.s^-2 = **nN.m**, stiffness nN.m/rad, damping nN.m.s/rad.
- **gravity.** `mujoco_globals.yaml`: `option.gravity [0, 0, -9810]` "in mm/s^2" = 9.81 m/s^2; compiled `m.opt.gravity = (0, 0, -9810)`
  (`model.py`). the only override is `body_loop.py:205`, `m.opt.gravity[2] *= args.gravity` (1.0 in both clips); `body_six.py` and
  `body_build.py` have none. applied once, correctly signed. at rest the vertical ground reactions sum to the weight (10.02-10.20 of 10.05
  in every arm of the sweep; 3.05 of 3.01 at x0.3).
- **the muscle torque's units.** `add_actuators(..., ActuatorType.MOTOR, forcerange=(-60, 60))`: motor, gear 1, gain 1, joint transmission,
  so the input is a joint torque in nN.m and the actuator clips at +-60 nN.m (and `body_loop.py:314` clips the same). `--gain 42` is nN.m
  per unit activation: a spike at f_w = 1 peaks at 42 x 1 / 10 = 4.2 nN.m = 10 uN x 0.417 mm, Azevedo's fast tibia flexor spike. consistent.
  the +-60 is 1.4x Azevedo's whole-joint tibia maximum (~100 uN at the tip = 42 nN.m); no other joint has a number. note: `--sat 10` is a
  divisor, not a saturation: activation sums linearly until the per-dof clip, where Azevedo's force saturates near 2-3 single-spike forces
  per fast cell (20-30 uN); at 100 Hz a fast cell holds ~15 nN.m in the model against ~10 measured. small.
- **timestep.** `option.timestep 1e-4` s, Euler, Newton, 100 iterations, 5 noslip iterations, pyramidal cone; the loop steps
  `round(0.001 / 1e-4)` = **10 physics steps per 1 ms neural step**, torque held across them (`body_loop.py:251, 318`). fine at these time
  constants.
- **contacts.** 55 explicit floor pairs (legs, thorax, abdomen, head; `LEGS_THORAX_ABDOMEN_HEAD`), friction sliding 1.0 / torsional 0.02 /
  rolling 1e-4, solref (0.2 ms, 1.0) = 2 timesteps (MuJoCo's floor for a stable soft contact), solimp (0.98, 0.99, 1e-5 mm), margin 1 um
  (`physics.py` defaults, compiled values in `model.py`). no self-collision (geom contype 0). no penetration seen.
- **joint limits.** `limit_joints` (+-70 knee, +-50 trochanter pitch, +-45 coxa and trochanter roll, +-40 tarsus, about neutral) with solref
  2 ms / solimp 0.99-0.999 (ours, labelled): **not engaged at rest** on any stiffness tested; they do not carry weight.
- **the knee does not sag.** the clips' knees sit 2-19 deg on the *extension* side of neutral (`clips.py`); the sinking is in the coxa and
  trochanter joints (P2, P4).
- **settling with no muscles:** checked (P2); **the ground reaction equals the weight** when still (vertical); the clips' 10.57 / 10.72 uN
  "total" exceeds 10.05 because `leg_force` is a norm that includes friction and motion.

## what would change the clips' reading, in order

1. P1: load and standing from tarsal contact only; report the coxa share. the clips' "1-6 % on the floor" becomes roughly "a third to a
   half on the coxae and body" (P1's passive 45 %, the clips' 45-78 % of frames with a coxa down).
2. P4: a muscle on the hind coxa's pitch.
3. P2 / P3: say which springs a clip stands on; relabel 0.14 as derived; a six-foot spawn pose.
4. then P5's question again: do the hind levators fire when the hind leg can report unloading?

not reviewed: the cord; the body-signs measurement beyond the hind coxa's axis choice; the video renderer (the camera is a tracking camera
on the thorax, so height is read from the floor texture's parallax; nothing here depends on it).
