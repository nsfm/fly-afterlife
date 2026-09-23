# review: the walking-body pipeline's baseline hookups (09-22, independent read)

scope: the cord (build_cord.py, world/cord.py, world/fastlif.py, flysim.py), the receptor registry, the body map (body_signs.py,
body_six.py, body_loop.py), the analysis (gait.py, gait_score.py). question: is there a bug in signs, units, indexing, timing or the
sensory/motor mapping that would explain a cord that never alternates as well as biology would. test scripts live in the session
scratchpad (/tmp/claude-1000/...), none in the repo; no project file other than this one was changed.

status: complete (09-22). verdict at the end.

## findings, ranked by how much they would change the conclusions

### F0. the stance tonus and co-contraction stand-ins do not add to the cord's drive: they replace it. with both on, the cord controls no coxa, trochanter or knee muscle at all (HIGHEST)

`experiments/body_loop.py:100-118`. `--slow-set stance_all` puts every motor neuron of the five stance types (sternotrochanter,
Tr extensor, Ti extensor, pleural remotor, sternal posterior rotator) into a registry row, `--cocon F` puts every motor neuron of
the six swing types (Tr flexor, acc. Tr flexor, Ti flexor, acc. Ti flexor, promotor, sternal anterior rotator) into another, and
line 118 marks every registry row's cells driven:

    for rc in REG.classes: M.driven[rc.cells] = True

a driven cell's spikes are *overwritten* by its Poisson draw every step (`fastlif._drive_gate`: `spk[i] = (r < thr) and free[i]`,
or False at rate 0); its membrane, and so every synapse the cord sends it, is ignored. counted on brain_cord.npz: of the 259 leg
MNs mapped to a joint, `stance_all` makes 73 into load-scaled Poisson sources and `--cocon` another 161; **with both on, 234 of 259
are puppets and the 25 left to the cord are 9 Ta depressors, 5 Ta levators, 5 MNml81 / MNhl65 (tarsus) and 6 sternal adductors.**
no coxa, trochanter or knee torque in those arms comes from the cord. the flexor and extensor rates reported for them are the
stand-in's own: 0.2 x 60 Hz x load and 60 Hz x load, compressed by F5.

the SEAM's own tables show it without the code: under the stance tonus the extensors read 24.9 / 25.9 / 25.9 Hz per cell with
DNg100 100 Hz / no command / 400 Hz (09:08); under tonus + co-contraction + pads the flexors read 11.7 / 12.0 / 10.3 and the
extensors 49.1 / 50.1 / 44.4 for DNg100 / no command / 400 Hz (17:24); the descending playback reads 10.7 / 45.6 against the
control's 11.7 / 49.1 (17:37). four-fold changes of the command and a whole recorded descending population leave the muscle
rates flat because those cells no longer listen to the cord. the SEAM read 17:12's "the file's own flexors fire at 5 Hz under
it" as the cord waking the swing side; they are the co-contraction row's spikes.

**consequence.** every standing-body arm with `--slow-set stance_all` (the stance tonus from 09:08 on) has the cord's stance side
disconnected; every arm with `--cocon` (17:12 on: the pads, MDN with pads, the descending playback, graded premotor units on the
body) has the cord disconnected from the whole proximal leg. "the brain's descending population does not make the cord step
either" and "graded premotor pools do not make him step ... on this body" (SEAM 17:37, 17:55) are not tests of the cord: the joints
that step were being driven by the load signal alone. only the pre-tonus arms (lying down, tethered, reduced gravity: 01:22-09:08)
had the cord in control of the proximal leg, and those have F1.

**fix.** make the stand-in additive: give the chosen motor neurons an external current (`M._ext[cells] = k x load`, mV, on the
membrane path, like `--adapt` / `--rebound`), or an extra Poisson *input* onto them (a synthetic presynaptic source), never mark
motor neurons driven. then the cord's excitation and inhibition still reach them and the tonus only biases. (the same trap is
available to `--drive TYPE:HZ` in cord.py if it is ever pointed at an interneuron or motor type: it silences the cell's own
computation. it has only been used on sensory and descending types.)

### F1. the knee position code has lost its 90-degree centre: the extension claw never fires, and the loop that was run is positive feedback (HIGH)

`experiments/body_loop.py:184`:

    state[f"claw_e_{leg}"] = args.claw_hz * clip((-k) / 60, 0, 1); state[f"claw_f_{leg}"] = args.claw_hz * clip(k / 60, 0, 1)

`k` is the FTi pitch in the body's joint coordinate times the measured flex sign, i.e. degrees of flexion *from a straight leg*
(NeuroMechFly's zero). the one-leg loop (leg_loop.py, SEAM 23:36) centred the code "60 deg either side of 90"; this port dropped the
90. measured on the body (scratchpad `body_build.py`): neutral k = 78 (front), 103 (mid), 101 (hind); the limited range is
k = 8-148 (front), 31-173 (mid/hind). **k is never negative anywhere in the reachable range, so `claw_e` (SNpp50) is structurally 0 Hz
in every loop arm ever run**, and `claw_f` (SNpp51) is k/60 x 100 Hz, i.e. 50-100 Hz whenever the knee is bent more than 30 deg.
from the saved runs (scratchpad `knee.py`, after the warm-up):

| run | signed knee median per leg (lf lm lh rf rm rh) | claw_e mean Hz | claw_f mean Hz |
|---|---|---|---|
| cocon02 (tonus + co-contraction 0.2) | 20 33 34 7 37 31 | 0.1 0 0 0 0 0 | 44 56 64 13 71 56 |
| g03_stance60 (the standing control) | 6 32 129 6 33 31 | 0 all | 10 54 83 10 57 52 |
| adh_g100_c02 (pads) | 10 33 31 6 32 30 | 0 all | 25 58 54 10 54 52 |

against Mamiya 2018 (docs/physiology/mechanosensation.md:41, leg_biomech.md:494: extension-tuned claw active at femur-tibia angle
90-180 deg, flexion-tuned 18-90, silent near 90; the FT angle is 180 - k here), a knee at k = 30 (angle 150, well extended, which is
where the mid and hind knees sit: at their extension limit, 31-33) should put the extension claw near full rate and the flexion claw
at 0. the code does the reverse: the leg reads "flexed" at 50 Hz while it is pinned straight.

**what this does to the loop's sign.** the wiring (scratchpad `claw.py`, brain_cord.npz, signed two-step reach onto the tibia MNs):
SNpp51 -> flexor MNs +438k / extensor MNs -523k (direct: 329 synapses onto flexors, 0 onto extensors; it is the claw type that
carries the 576 synapses onto IN21A004); SNpp50 -> extensors +139k / flexors -1,279k (its largest target IN13A002, a flexor
inhibitor). as run, claw_f rises with flexion over the whole operating range and SNpp51 drives flexion: **the position loop is
positive feedback** (more flexion -> more flexion drive). the hooks as mapped are positive too: SNpp39 (fed flexion velocity) drives
the flexors (+194k flex / -206k ext), SNpp41 (fed extension velocity) drives the extensors (+60k ext). a joint under net positive
feedback latches at a limit; it cannot oscillate, whatever the cord does. every knee in the standing runs sits at or within 2 deg of
its extension limit (medians above), which is what a latch looks like.

**and the corrected code may not fix it.** with the centre restored (claw_e = clip((90 - k)/60), claw_f = clip((k - 90)/60)) and the
labels as they are (SNpp50 = extension-tuned), an extended leg drives SNpp50, which drives extension: still positive feedback, now
on the extension side. the labels are unsourced: `E_table_male.md:43-44` asserts "SNpp50 extension-tuned / SNpp51 flexion-tuned" with
no citation, and the MaleCNS annotation's `synonyms` field only says "FeCO claw" for both. the one physiological anchor in the
briefs (Agrawal 2020, mechanosensation.md:208: extension-tuned claw -> 13Balpha -> femur-tibia *flexion*, a resistance reflex) says
the extension-tuned type should drive flexion; in the table SNpp50 drives extension (though it does carry most of the claw -> 13B
synapses: 2,082 against SNpp51's 248, which is the argument *for* the current label). so either the labels are swapped (and the
fixed code gives a resistance reflex) or the table's claw reflex is assistive at rest, which contradicts Agrawal 2020.

**consequence for the conclusions.** the SEAM results "the loop moves the cord: the flexors wake 0.00 -> 0.5-0.7" and "the resistance
reflex, with the sign life has it" (SEAM 01:22) are a tonic 50-60 Hz on SNpp51 on every leg, not position feedback; the knee's position
signal never reached the extension claw; and every body arm from 01:22 on (the stance tonus, co-contraction, pads, the unloading term,
the moonwalker, the descending playback, graded units on the body) was run with the knee loop as a positive-feedback latch. none of
those arms tested whether a *negative*-feedback proprioceptive loop plus the cord can alternate. the negative results on the body
do not stand until this is fixed.

**fix.** centre the code on 90 (or on the neutral k, (E)), as leg_loop.py had it; pick the claw and hook labels from a source (Mamiya
2018 / Agrawal 2020 / Dallmann 2025 driver-line matches, or the FANC / MANC FeCO subtype papers) rather than from `E_table_male.md`;
then run the body arms twice, once per label assignment, and report the open-loop sign (d(flex - ext drive)/dk) per leg before any
arm is read. a two-minute check to add as a guard: with the body held at k = 30 and at k = 150, print claw_e / claw_f per leg.

### F2. "he stands" is two thirds of his weight on his sternum: the feet carry a third, and the load rows read it (HIGH for the body arms)

the SEAM's standing criterion is thorax height 0.70-0.72 mm ("0.7 = standing"). the thorax's centre at 0.70 has its ventral geom on
the floor. measured: a copy of body_loop.py with a per-segment ground-force log (scratchpad `body_loop_instr.py`, the `cocon02`
configuration: stance tonus 60 x load, co-contraction 0.2, set down standing, DNg100 100 Hz, measured springs, 8 s):

| world-z ground force after the warm-up (uN) | lf | lm | lh | rf | rm | rh | six feet | **thorax** | abdomen | weight |
|---|---|---|---|---|---|---|---|---|---|---|
| cocon02, re-run 8 s | 0.59 | 0.14 | 0.83 | 0.68 | 0.15 | 0.87 | 3.26 | **5.69** | 0.97 | 10.05 |

the saved 20 s runs agree: the six feet's mean force sums to 2.7 uN (cocon02) of a 10.05 uN fly. for reference, the same body set
down with no torque holds its thorax at 0.76-0.78 with nothing but feet and the abdomen tip on the floor (feet 8.5-9.9 uN, abdomen
tip 1.6), so 0.70 is below clear standing, not at it. (the "he stands at 0.71" arms at full gravity are therefore a fly resting on
its sternum with the front legs propping; the `--gravity 0.3` arms, e.g. g03_stance60, are a separate case.)

consequences: (1) every load row runs at 15 Hz x F / F_stand with F about a tenth to a half of F_stand on the mid legs (0.14-0.15 uN
against 1.67), so the load reflex the SEAM relies on for "stance loads the leg, unloading releases swing" sees legs that are
barely loaded to begin with, and the stance tonus (60 Hz x the same ld) is mostly off on the mid legs; (2) a leg cannot be unloaded
by lifting when it was never carrying weight: the thorax takes the weight whichever leg lifts, so the load-derivative arms
(`--load-deriv`) had no unloading event to report; (3) "the feet tap" (SEAM 09:14: back four feet off the ground 66-92 % of the time)
is a body lying on its sternum waving its back legs, not a standing fly's feet lifting. the negative result "standing, he does not
step" should be restated as "resting on the thorax, he does not step".

fix: report the thorax's (and abdomen's) ground force alongside the height in every body arm (`sim.get_bodysegment_contact_forces`
over all segments; 3 lines); call a body standing only when the non-leg ground force is under ~10 % of weight; then re-derive the
stance-tonus rate that gets the weight onto the feet (the SEAM's 60-120 Hz x load was chosen by height, which F2 shows is the wrong
criterion).

### F3. the pads saturate the load rows and the stance tonus of every stuck foot (MEDIUM; the pads arms and everything after 17:24)

`body_loop.py:180-200`: `leg_forces()` is the norm of the leg's net contact force (flygym's contact sensor, reduce = netforce, over the
leg's subtree), and with `--adhesion contact --adhesion-gain 20` the adhesion actuator's pull is inside that force. a static test
(scratchpad `h5.py`: measured springs, a constant extension + depression torque of 3, pads on at gain 20): **six feet at 19.5-21.4
uN each, 123 uN in total, for a 10 uN fly.** so an adhered foot reads 12 x F_stand and the load row and stance tonus clip at 2 x
F_stand (30 Hz / 120 Hz) whatever the leg is doing. from the saved pads runs (scratchpad `latch.py`, after the warm-up), the fraction
of time each foot's load term is pinned at the clip:

| run | lf | lm | lh | rf | rm | rh |
|---|---|---|---|---|---|---|
| adh_g100_c02 (DNg100, pads, co-contraction) | 0.56 | 0.00 | 0.28 | 0.20 | **0.94** | 0.29 |
| adh_mdn_c02 (MDN, pads, co-contraction) | 0.32 | 0.00 | 0.15 | 0.18 | **0.92** | 0.26 |
| cocon02 (no pads, the control) | 0.04 | 0.01 | 0.04 | 0.05 | 0.01 | 0.04 |

and the adhesion switch is `F > 0.05` on that same force (line 200): a foot in contact is adhered, and an adhered foot reads 20 uN,
so the switch is a latch that only a pull stronger than two body weights can open, while the stance drive of that leg sits at its
maximum. the right mid foot is on the ground 94-96 % of the time in these arms, which the SEAM read as "the feet that are down stay
down". the author flagged the first half of this (SEAM 17:37, "noted, not fixed"); the second half (the latch on the stance drive)
means the pads arms, the playback-with-pads arms and the graded-units-on-the-body arms (all run on "tonus + co-contraction + pads")
had legs that could not report unloading by construction.

fix: feed the load rows the ground *reaction* net of adhesion (the contact normal force minus the adhesion actuator's force,
`d.actuator_force` on the adhesion actuators, or the normal component only with the adhesion's contribution subtracted), and switch
the pads on the loaded-leg state from the previous frame's net-of-adhesion force, with a release threshold that a leg's own levation
torque can reach.

### F4. every knee is pinned at its limit; the knee "range" was set about a neutral pose, not the fly's (MEDIUM)

`body_loop.py:128-135` (and body_six.py): the knee's range is neutral +- 70 deg, i.e. signed flexion 8-148 (front) and 31-173 (mid,
hind) from straight. in the saved standing arms the mid and hind knees' medians sit at 30-37 deg against extension limits of 31-33
(cocon02, adh_g100_c02; the left hind knee of g03_stance60 at 129 is the exception) and the front knees at 6-20 against a limit of
8; the joint limit, not a muscle, sets most of the posture (the SEAM saw this for the front legs at 17:12; it holds for the mid and
hind legs too). with F1's positive feedback this is where a latch ends. fix with F1;
and use the brief's measured ranges (leg_biomech.md §C1, Karashchuk 2021) instead of +-70 about NeuroMechFly's neutral.

### F5. a driven cell's rate is not the rate it is asked for: the Poisson gate loses ~3 ms after every spike (LOW-MEDIUM; relabels every dose)

`fastlif._drive_gate` draws `r < hz x dt / 1000` only while the cell is `free`, and a spike sets `refrac` = 2.2 ms, which at dt = 1
keeps the cell unfree for 3 steps. the delivered rate is hz / (1 + 3 ms x hz) rather than hz. measured (world/cord.py, DNg100
logged, scratchpad): **nominal 100 Hz -> 81 / 73 Hz; nominal 400 Hz -> 184 / 180 Hz.** so the dose sweep "50 / 100 / 200 / 400 Hz"
is really about 43 / 77 / 125 / 182 Hz (the SEAM already saw 77 Hz for a "100 Hz" brake at 21:46 without naming the cause); the
stance tonus at "120 Hz x load 2" is ~140 Hz, not 240; and the descending playback under-delivers the loud cells it copies from the
whole fly (DNb05 recorded at 194 Hz of real spikes is replayed at about 123), since the recording's rates were spike counts and the
replay treats them as Poisson intensities. no qualitative conclusion turns on this, but every "x Hz" on a driven row is a nominal
number. fix: either invert the dead time when setting the rate (hz / (1 - 3 ms x hz), capped) or label the rows as intensities.

### F6. the synaptic delay is 3 ms at the record's 1 ms tick, not 1.8 (LOW)

`flysim.reset`: `n_dly = round(1.8 / dt)` = 2 slots, and the step appends the *previous* step's spikes before popping, so a spike
first moves its target's membrane three steps later. measured on a two-cell toy network (scratchpad): **latency 3.0 ms at dt 1.0,
1.9 ms at dt 0.1.** the same holds for the graded emission (it rides the same line). this is part of what the 09-22 tick arms
(`--dt`) measured and found shape-neutral in the cord alone; in the body loop it adds 3 ms to every reflex arc (sensor ->
interneuron -> MN is ~6-9 ms of synaptic delay before the 7 ms twitch rise), which is still well inside a 100 ms step cycle. noted,
not a cause.

### F7. the "load" rows drive every leg proprioceptor that is not a claw or hook, including position and vibration sensors (LOW-MEDIUM)

`body_loop.py:86`: `load = cells[~isin(type, [SNpp50, SNpp51, SNpp39, SNpp41])]`. on the mid legs that is 127 - 43 = 84-101 cells, of
which (world/legs.npz by type, L2 / R2): hair plates SNpp45 12 / 11 and SNpp52 10 / 11 (coxa / trochanter position sensors; the
annotation brief says SNpp45 projects onto the remotor / rotator / abductor MNs and SNpp52 onto the promotors), FeCO club cells
SNpp40 / 43 / 47 / 58 / 60 and SApp23 (~40, vibration), and SNpp53 trochanter campaniforms. only the campaniforms and part of
SNppxx are load sensors. so "load" also pushes load-correlated drive straight onto the coxa's protractor and retractor MNs through
the hair plates, which is a coxa reflex nobody chose. and in the cord-alone arms the floor holds *all* of these, claws of both
tunings and hooks of both directions included, at 15 Hz at once (receptors.py:276), where the hooks should be near silent at rest
(Mamiya 2018). fix: split the row by modality (campaniform + SNppxx -> load; hair plates -> the coxa / trochanter angle; clubs ->
0 or vibration; hooks -> velocity only), and give the floor per-modality resting rates.

### F8. the analysis (gait.py, gait_score.py) is sound for what it measures (LOW)

a synthetic perfect tripod written into a real cells.npz (swing pools on half of an 8 Hz cycle, stance pools the other half, L1 R2
L3 against R1 L2 R3, Poisson; scratchpad) scores antag -0.73, legs -0.81, beat 326 at 7.8 Hz: the measures would have seen a gait
in MN spikes had there been one. caveats: `legs` and `antag` start at 0.0 and take a minimum, so they can only report negatives
(+0.00 means "no negative pair", not "zero correlation"); the inter-leg signal is each leg's summed MN count, which mixes stance
and swing pools and would weaken if the two were of equal size (they are not in this file, so it did not matter); and in the body
arms with the stand-ins the measures read the stand-in's spikes (F0), so the body arms' `flex`, `ext`, `antag` and `legs` columns
do not describe the cord.

## checked and clean so far

- H1 (the muscle -> joint map): clean. a synthetic push through the ROLE table and `results/body_dof_signs.json` on the loop's own
  body (measured springs, limited hinges, zero gravity, 30 ms at half a fast spike's peak torque, minus a zero-torque baseline;
  scratchpad `h1b.py`), per leg lf lm lh rf rm rh: tibia flexor shortens tip-to-coxa by +0.03 / +0.07 / +0.08 mm and the tibia
  extensor lengthens it by the same; trochanter flexor lifts the foot +0.16 and the sternotrochanter lowers it -0.15; promotor
  moves it forward +0.08-0.11 and the remotor back; tarsal levator lifts, depressor lowers. every antagonist pair acts on the same
  dof with opposite sign on all six legs, left and right identical. `set_actuator_inputs` order equals `dofs` (checked:
  `fly.get_actuated_jointdofs_order(MOTOR) == dofs`, 42), the json's dof list equals the run's, `get_joint_angles` is documented and
  used in `get_jointdofs_order()` order and `all_idx` is built from that list, and the contact sensor's leg order is `anatomy.LEGS`
  = lf lm lh rf rm rh = LEG6. the knee sign: flex.sign = +1 on all six legs, so + torque = + angle = flexion, and `knee_sign`
  reads the angle in the same sense. (one real quirk: on the hind legs the sternal adductor is mapped to coxa yaw with sign +1,
  which is exactly the remotor's action, -0.10 mm fwd, identical to the pleural remotor: the hind "adductor" is a second
  retractor. small: those cells are few.)

- H2 (driven-cell marking): the 5,029 cells marked driven by `SENSORY_CLASSES` in brain_cord.npz are all of sensory superclass
  (vnc_sensory 4,529, sensory_ascending 500); zero interneurons, motor neurons or descending cells are silenced by it. the floor's
  `mechanosensory_proprioceptive` selection is a subset of those. (1,117 sensory-superclass cells of other classes, `unknown_sensory`
  SNxx*, `chemosensory`, are NOT driven and run as ordinary LIF cells on their synaptic input: harmless but worth knowing.)
- graded double counting (H4, part): `acc[M.last_idx] += 1` in cord.py and `idx = M.last_idx` in body_loop.py read `last_idx` after
  `step()` has reassigned it to `flatnonzero(spk)`; the graded concatenation only mutates it at the top of the *next* step. no
  double count. `reset()` does not rebuild `v_th`, so the graded cells' 1e6 threshold survives `M.reset()`.
- H3 (the flexors' excitatory premotor cells silent for a wiring-file reason): no. IN21A004, IN03A004, IN20A.22A009, IN03A031
  receive exactly the same excitatory synapses per cell in brain_cord.npz as in brain_whole.npz (2,421 / 3,584 / 609 / 799): the
  cut removed none of their input, and `build_cord.py` preserves type, class, superclass, side, nt and sign for all 23,074 cells
  (checked against brain_whole by bodyId: zero mismatches). their excitation comes 70-87 % from cord interneurons, 4-22 % from
  descending neurons (IN20A.22A009 22 %: silent in the headless cord unless driven, by design), 2-8 % from ascending neurons, and
  1-6 % from driven sensory cells. their silence is the network's, not the file's. (one attribution error in the SEAM: the 576
  claw synapses onto IN21A004 are from SNpp51, not SNpp50; SEAM 21:49 had it right and 22:32 / 22:34 swapped it. the SNpp51 arm
  was also run and was also null, so no conclusion changes.)
- H4 (graded emission): the graded indices and scales are appended to `last_idx` before the delay-line append and after the std
  scale is built from the spikes alone (so a graded cell's std resource is never consumed, correct for a non-spiker); the emission
  is computed from the post-update membrane and enters the same delay line as a spike from that step, so it has the same latency;
  `_reset` only touches spikers and graded cells never spike (threshold 1e6, preserved by `reset()`). scale = gain x clip(v / V1).
  no double count in the logs (above). clean, apart from F6's delay which it shares with spikes.
- units: the model's mass is in grams (body_mass sum 1.02e-3), length mm, time s, so force = uN and torque = uN mm = nN m, as the
  author states; 4.2 nN m per fast spike is 4.2 model units.

## verdict

**the headless cord's negatives stand; the body's negatives do not.**

- **the cord alone (world/cord.py, ~40 arms):** no bug found that would stop a cord from alternating. signs come from the per-cell sign
  array as the reference engine has it; the driven marking touches only sensory-superclass cells; the cut keeps every synapse onto
  the flexors' premotor cells; the graded, adaptation, rebound and depression terms are wired where they say; the logs count spikes
  once. what needs relabelling: every driven rate is delivered at hz / (1 + 3 ms x hz) (F5: "400 Hz" is 182), the synaptic delay is
  3 ms at the 1 ms tick (F6), and the floor holds claws of both tunings and hooks of both directions at 15 Hz together (F7). none
  of these is plausibly the difference between a posture and a rhythm; "a tonic command on this wiring in this LIF holds a posture"
  survives the review.
- **the body loop (experiments/body_loop.py, ~25 arms):** three hookup errors each invalidate the reading "the loop is closed and
  nothing steps". F0: from 09:08 on, the stance tonus replaces the cord's control of every stance motor neuron, and from 17:12 on
  co-contraction replaces the swing side too, leaving the cord in charge of the tarsus and the adductor only; every standing-body arm
  after that (the pads, MDN, the descending playback, graded units on the body) measured the load signal driving the legs, not the
  cord. F1: in every loop arm, the knee position code has no centre, so the extension claw never fired, the flexion claw fired at
  50-60 Hz on a straight knee, and the knee loop was positive feedback (as were the hooks), which latches a joint at its limit. F2:
  "standing" at 0.70 mm is the thorax on the floor carrying 57 % of the weight, so the load rows never saw a loaded leg to unload.
  F3 then pins the load rows of adhered feet at their clip. so the body side has not yet tested the question it was built for (does a
  negative-feedback proprioceptive loop, through a cord that is in control of the legs, alternate), and "every lever on the body's
  side has now been pulled once" should be withdrawn until it has.
- **the order i would fix and re-run them:** F0 (make the stand-ins additive currents, no motor neuron driven), F1 (centre the claw
  code; then run it twice, once per claw / hook label assignment, and print the open-loop sign per leg before reading any arm), F2
  (log the non-leg ground force; call it standing only with the weight on the feet; re-derive the tonus rate on that criterion), F3
  (load net of adhesion; pads not latched on it), F7 (split the load row by modality). then the SEAM's body arms, starting with
  the plain command on a body that stands on its feet with the cord in control, before any of the day's other levers.

not reviewed: pair.py and the whole-fly configuration, the mirror normalisation (`wiring.py`), leg_loop.py beyond its claw centre,
and the physiology of the muscle-role vocabulary beyond checking that each type moves its joint in the direction its name says.

## second pass (09-22 evening): the fixes, and "he stands on his feet and the left front leg steps at 9 Hz"

read: SEAM from "## the review" to the end; `git diff d078f04 HEAD` of experiments/body_loop.py, world/cord.py, world/fastlif.py.
re-ran the record arm and three controls, 20 s each, seed 11, no video (scratchpad `p2/run.sh`; analysis `p2an.py`, `lifts.py`).
every arm uses flygym's springs, pads (contact, gain 20), claw labels 50flex and the 12 ms cell delay on IN17A001 / INXXX466 / IN16B036:

| arm | body on floor (% weight) | thorax z | lf coxa pitch: sd, spectral peak | autocorr 60 / 110 ms | lf promotor pool: Hz/cell, peak | coherence (promotor - remotor count, coxa angle) at the peak | lf foot lifts > 50 ms (by foot height) | forward during lifts |
|---|---|---|---|---|---|---|---|---|
| **B: the record** (DNg100 100 Hz, loop x8, position+load) | 1.9 | 0.68 | 14.6 deg, **8.9 Hz x123** | -0.20 / +0.42 | 15.9, 8.9 Hz x115 | **0.95** | 124 | 0.65 |
| A: loop x1 (the ring removed), else the same | **50** | 0.73 | 13.0, 2.6 Hz (wander) | +0.45 / +0.16 | 4.3, no peak | (0.86 at 2.3 Hz) | 19 | 0.53 |
| C: no command (`--walk 0`), loop x8 | **3.8** | **0.92** | **0.3**, none | | 0.0 | | 0 | |
| D: x8, **sensory loop off** (`--loop off`; the pads never engage either, F reads 0) | 8.2 | 0.66 | 16.0, **9.5 Hz x247** | -0.27 / +0.39 | 14.6, 9.5 Hz x205 | **0.98** | 107 | 0.74 |

B reproduces the saved `ld_100_x8_springs` to the digit (deterministic). the saved seeds 10 / 12 give the same picture (coherence
0.97 / 0.96, peak 9.6 / 9.1 Hz).

### Q1. the standing judgement: the statistic is right; the standing is the springs'

- the F2 statistic is read correctly: `get_bodysegment_contact_forces(...)[NONLEG, 2]` is the world-z column; the sign is thrown
  away by `abs` per segment, which is fine for a magnitude; NONLEG is every segment not prefixed by a leg (thorax, abdomen, head, and
  segments that never touch). it agrees with my own per-segment log from the first pass.
- but **C, no command at all, stands better than the record: 3.8 % on the body, thorax 0.92.** flygym's joint springs (stiffness 10,
  ~70x the measured passive stiffness) hold NeuroMechFly's neutral pose with no muscle; my first-pass static test gave the same (feet
  9.9 of 10.05 uN with zero torque). the command lowers him (0.92 -> 0.68) and, without the ring (A), puts half his weight on the
  floor. so "1-2 % on the body" is honest as a number and is not the cord's achievement: it is the springs, which the cord's ring
  happens not to knock over. on measured springs with the tonus current the same arm is 77 % on the floor (SEAM 19:34). the record
  should say "on springs that stand him with no drive".

### Q2. the step: cord-generated, not a mechanical resonance; but it is one pool pulsing against a spring, and the loop is not in it

- **not a resonance.** remove the ring (A: loop x1) and the 9 Hz is gone (2.6 Hz wander, 19 lifts); remove the command (C) and the
  leg does not move (sd 0.3 deg). the frequency also follows the delay the author set (SEAM: 8 ms -> 11.1 Hz on the body, 12 ms -> 8.8),
  which a body resonance would not. the promotor pool's spike count per 10 ms leads the coxa angle with coherence 0.95-0.98 at the
  peak, and (promotor - remotor) correlates -0.76 with the coxa's pitch velocity (negative pitch = forward, below). the 9 Hz is
  the cord's ring arriving at the muscle.
- **the sensory loop, the claw labels and the pads are not part of it.** D, the same arm with `--loop off` (no claw, no hook, no load,
  and so no pads), steps at 9.5 Hz x247, 107 lifts, forward 0.74, coherence 0.98, and the right front coxa joins it (9.5 Hz x165).
  so the SEAM's "the swap matters, and it is the review's F1 in action" does not apply to this arm: at 100 Hz x8 the ring drives the
  front coxa feed-forward. (the swap may matter in the 400 Hz x3 arm; I did not re-run that.)
- **what the step is, mechanically.** the promotor pool (6 cells, 15.9 Hz/cell) carries the cycle at x115; the remotor pool (5.0 Hz/cell)
  barely (x13), and promotor vs remotor counts correlate only -0.14 at +20 ms, +0.09 at +60 ms (10 ms bins): a weak counter-phase, not
  a half-centre. in this body the front leg's coxa protraction also *lifts* the foot (first-pass `h1b.py`: lf promotor torque moves
  the tarsus +0.09 mm forward and +0.12 mm up; the trochanter levators stay at 0 Hz), so "lifted and forward in the air" is one pool's
  twitch train, and "back on the ground" is the spring (stiffness 10) returning the coxa. the foot is off the ground 67 % of the time
  (reconstructed foot height from the saved joint angles and thorax pose: 10th percentile 0.027 mm, 124 lifts > 0.05 mm for > 50 ms;
  the F_net = 0 mask used by the record agrees on 92 % of frames): a leg mostly in the air. three of the six coxae move (lf, and rf in
  D) and the mid and hind legs wander at 2-3 Hz.
- verdict: the rhythm is real, cord-generated and replicated; calling it "a leg steps" oversells it. it is "the tuned ring drives the
  left front promotor pool at 9 Hz, and against flygym's springs that swings the foot up and forward and lets it fall back". no
  swing / stance alternation of antagonists, no levator, no coordination with another leg, and the frequency is set by a delay chosen
  for the band (the author says so).

### Q3. the sign of "forward": right

+x is anterior in this model (lf coxa at x = +0.34, lh coxa -0.29, abdomen segments increasingly negative), and setting lf coxa pitch
-0.3 rad moves the tarsus 1.14 mm ahead of the coxa against 0.67 at +0.3 (scratchpad `fwd.py`). so a negative pitch change is
protraction, as the json says. by foot height the lifts carry the coxa forward 65 % (B) / 70 % (seed 10) / 74 % (D) of the time,
mean -5 to -8 deg; the record's 0.80-0.83 used a different lift mask and window, same direction.

### Q4. the new code

- **F0 fix: right.** the stand-in is now `M._ext[cells] = slow_mv x ld` on the membrane path; the cells are no longer in any registry
  row, so not driven; the cord's synapses reach them. one footgun: `--slow-mv` uses `SLOW`, which defaults to `--slow-set size` (the
  93 smallest cells, the accessory flexors); every saved tonus arm passed `stance_all`, so no run is affected, but the default should
  change.
- **F1 fix: right.** `knee = (angle - neutral) x sign`, so the claw code is centred on the neutral pose (FT angle ~77-102), both claw
  types can fire, and `--claw-labels` swaps which one gets the extension rate. the hooks are unchanged (velocity, labels still
  unsourced).
- **F2 fix: right** (Q1).
- **F3 fix: works in the mean, chatters in time.** `F = max(F_raw - gain x pad_on, 0)` and `pad_on = F > 0.05` on that same net force:
  whenever the adhesion is not fully expressed in the contact (on landing, while peeling) the net force clips to 0, the pad turns
  off, the raw force drops, and the pad turns back on. the lf pad toggles 1,313 times in 18 s in the record (349 in A): ~70 switches
  a second. harmless to this result (D steps without pads), but it is a half-duty, kilohertz-flickering adhesion, not a pad. fix:
  switch the pad from the raw force with hysteresis, or subtract the adhesion actuator's actual force (`d.actuator_force`).
- **`--cell-delay` (fastlif.py:144-154): the bookkeeping is right.** a three-source test network (scratchpad): default cells arrive 3
  steps after the spike with or without `delay_on`; a 12 ms cell arrives 13 steps after (so "12 ms" is 13 effective where the rest is
  3: an extra 10); with depression on, the delivered scales are identical with and without the delay (7.57 then 3.97, below); a graded
  cell with a 12 ms delay arrives 13 steps after its emission as a spike would. scale arrays stay the same length as their index arrays
  in every slot.
- **`--edge-scale`: right, and wider than its name.** it scales all 44 synapses among the four types, including DNg100's onto all three
  loop cells, so x8 is also an 8-fold command into the ring. labelled in the SEAM; worth saying at every use.
- **new, pre-existing, both engines: depression under-delivers the first spike by U.** in the toy test with u 0.5 a fresh synapse
  delivered 7.57 instead of 15.15 (x0.5): the release scale is read from `_std_x` at the top of the step *after* the spike, and the
  spike's own decrement was applied at the end of the spiking step. flysim.py:860 has the same order despite the comment above
  `_dly_scale` saying it avoids exactly this. every `--std` arm ran with release x(1 - u) (8 % less at the engine's u 0.08; 50 % at the
  0.5 sweeps). it does not touch tonight's result (std off). fix: capture `_std_x[last_idx]` before the decrement, at the end of the
  spiking step.

### second-pass verdict

the four fixes are correct (F3 with a chatter to fix), the delay-line change is correct, and nothing in the new code fakes the
result. the result survives as **a cord rhythm**: the published loop, with its synapses x8 and a 13 ms delay, rings at 9 Hz and
drives the left front promotor pool hard enough to swing the coxa and lift the foot, three seeds of three, gone without the ring or
without the command, and **independent of the sensory loop** (it steps with `--loop off`). it does not survive as "he stands and a leg
steps": the standing is flygym's springs (the fly stands better with no command at all), and the "step" is one pool's twitch train
lifting the foot through the front coxa's geometry, with the spring doing the return. what would make it a step: the same arm on
measured springs with the additive tonus (currently 77 % on the floor), and a stance phase that is driven (remotor or depressor
bursts in antiphase) rather than passive.
