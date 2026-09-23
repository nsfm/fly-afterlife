# force per spike by motor neuron class (09-23)

why: `docs/SEAM.md` "the small flexors' current on the body" put the fold of the leg on the muscle map: "every motor neuron spike moves
the joint by the same 42 nN.m". this file sources force per spike by class, says what the body loop did before, and proposes (and
`experiments/body_loop.py --mn-force azevedo` implements) a per-motor-neuron factor. legend: **(M)** measured in *Drosophila*, **(C)**
measured in another insect, **(D)** read or derived from a published figure, **(E)** ours.

## 1. the one measurement

Azevedo AW, Dickinson ES, Gurung P, Venkatasubramanian L, Mann RS & Tuthill JC 2020, "A size principle for recruitment of *Drosophila*
leg motor neurons", **eLife 9:e56754** (DOI 10.7554/eLife.56754; the bioRxiv 730218 preprint was "A size principle for leg motor control
in *Drosophila*"). it is eLife, not Nature. re-read against the article page 09-23; the fuller extraction is `leg_biomech_parts/B_activation.md`.

conditions: female, front (T1) leg, **tibia flexor motor neurons only**, whole-cell in vivo; force read at the tibia tip on a calibrated
probe (k = 0.22 uN/um, lever arm 417 +- 7 um), not as joint torque. fast / intermediate driven optogenetically (their somata cannot fire
the axon), slow by somatic current. **the extensors (FETi, SETi) were not measured mechanically**, in this paper or anywhere else in the fly.

| class | driver | cells in the pool (M, anatomy) | force per spike | tip movement per spike | source in the paper |
|---|---|---|---|---|---|
| fast | R81A07 | 1 | **~10 uN** (one body weight) | ~50 um | fig 4A, text (M) |
| intermediate | R22A08 | 2-5 | **~1 uN** | ~5 um | fig 4B, text (M) |
| slow | R35C09 | 8-9 | **< 0.1 uN** (abstract); **0.013 uN per spike**, the linear slope of peak force on spike count | ~1 um, slow | fig 4C-D (M / D) |

per-cell spread (fig 4D, D): fast single spike 5-16 uN, saturating 20-30 uN; intermediate 0.25-0.7 uN, saturating 1.5-3 uN.
whole joint: close to **100 uN** at the tibia tip (fig 1F, M). torque = force x 417 um, so one fast spike ~ **4.2 nN.m** (E, arithmetic).

**ratios, fast = 1:** fast **1** : intermediate **0.1** : slow **0.0013** (0.013 / 10; the abstract's bound gives slow <= 0.01).
each class step is ~10x; the pool spans three orders of magnitude (M).

### how force sums over spikes (M unless marked)

- **twitch:** fast and intermediate have the same kinetics (half-maximal force ~8.5 ms, peak ~21 ms (D), decay tau ~20 ms (D)) and differ
  only in gain. one kernel, per-class gain.
- **summation:** 2 spikes give ~1.6x the force of 1 (fig 4E), sublinear at n = 2.
- **saturation:** force vs spike count saturates at ~10 spikes for fast and intermediate (fig 4D; the authors put it to fatigue).
- **fusion / tetanus:** **not measured.** no frequency series, no force-frequency curve, no tetanic force in the paper. a fusion frequency
  quoted for the fly is an extrapolation (from tau ~20 ms: 50-100 Hz, E).
- **the slow unit has no resolvable twitch:** force rises gradually and has not peaked at 500 ms; release takes ~100 ms (fig 4C). "the
  resting spike rate of slow motor neurons maintains constant force on the probe"; MLA (nicotinic block, lowering the slow cells' rate)
  cut the resting force by **~1.5 uN** (M).
- recruitment by adding cells, slow -> intermediate -> fast (110 of 3,082 intermediate spikes without a preceding slow spike) (M).

### a consistency check on the slow number (D / E)

read as "0.013 uN per spike accumulated over the ~0.5 s the force takes to build", a slow cell at its 30 Hz rest holds 0.013 x 30 x 0.5
~ 0.2 uN, and the 8-9 slow cells ~1.6 uN: the size of the MLA cut. so the slow slope is consistent with a slow integrator of tau of
order 0.2-0.5 s, **not** with a 20 ms twitch at 0.0013 of the fast one. under the body loop's twitch kernel (area 35 ms of peak per spike)
a factor of 0.0013 gives a slow cell at 30 Hz 0.014 uN steady, **~10x under** that; the kernel-equivalent steady factor is
0.0013 x tau / 35 ms = **0.007-0.018** for tau 0.2-0.5 s (E). the implementation below uses the per-spike 0.0013 as sourced and keeps
the kernel; the steady-equivalent bracket is the upper bound, and the slow kernel itself is the next change if this matters.

## 2. everything else (searched 09-23)

- **other fly leg pools:** no force per spike, twitch or tetanic force is published for any other *Drosophila* leg motor neuron
  (searched: web, the Tuthill-lab list, the sources in `leg_biomech.md`). **not found.**
- **Azevedo et al. 2024, *Nature* 631:360** (FANC connectome + the motor neuron atlas; its Motor Neuron ID appendix): motor neurons per
  muscle (T1: tibia flexor 5, accessory tibia flexor ~10, tibia extensor 2 = FETi + SETi, 69 per leg) and input synapse counts
  (FETi 14,904, the most of any T1 MN). anatomy, no force. (M, anatomy)
- **Lesser et al. 2024, *Nature* 631:369:** input synapses linear in MN surface area (r ~ 0.94); premotor weights proportional to MN size.
  what licenses reading synapse count as size at all. no force. (M, EM)
- **FlyMimic / Özdil et al. 2025 (arXiv 2509.06426):** Hill-type MTUs, F_max tibia flexor ~68, extensor ~304 (model units ~uN), fitted
  by optimisation to kinematics, mammalian force-length / velocity defaults; **no spike-to-force stage and no motor units.** (E, not a source
  for per-spike force)
- **NeuroMechFly v2 / flygym:** torque or position actuators per joint, no muscle or motor-unit parameters. (E)
- **the extensor, comparative (C):** in the locust (Burrows and colleagues) the extensor tibiae has one fast (FETi) and one slow (SETi)
  motor neuron: one FETi spike gives a large rapid extension, single SETi spikes usually no visible movement, trains of >= 10 Hz graded
  slow extension. a fast:slow ordering of the same kind, no fly number.

## 3. what the body loop did before this (checked in the code, 09-23)

`body_loop.py` (as `body_six.py`): each spike adds `gain x f_w x K / sat` to its joint, `gain` 42, `sat` 10, `K` a 7 / 20 ms
difference of exponentials of peak 1: so a spike at f_w = 1 peaks at 4.2 nN.m, Azevedo's fast spike. **f_w is not uniform:** f_w =
(S / S_max)^1.2, S the file's input synapses, S_max the largest in the cell's (leg, role, side of the joint) group. the exponent was
derived (`leg_biomech.md` A4) so a ~50x synapse span gives Azevedo's ~100x force ratio. the small third of the tibia flexors already
had f_w **0.003-0.06** (median ~0.01) of the largest flexor on its leg: a slow spike pulled like a hundredth of a fast one, not like a
fast one. the SEAM entry's "the same 42 nN.m per spike" is the gain, not the per-cell torque. (the implication for the fold is in the
report of the arms, not here.)

## 4. the proposal (implemented as `--mn-force azevedo`)

per mapped leg motor neuron *j*, the per-spike increment `gain x f_j x K / sat`, with

| cells | f_j | class from | mark |
|---|---|---|---|
| 'Ti flexor MN', the large third of the 37 by input synapses | **1.0** (today's 42 nN.m reference) | the file's input-synapse third over the pooled cord, the same ranking as `--pic smallflex` and the graded size CSV (`flex_graded_abs.csv`: 0.43 / 2.14 / 3.29 = small / middle / large), small = slow | factor (M), class (E) |
| the middle third | **0.1** | as above | factor (M), class (E) |
| the small third | **0.0013** | as above | factor (M / D), class (E) |
| every other mapped leg MN (accessory tibia flexors, tibia extensors, the other joints) | **f_w x 1.0**, the size proxy unchanged | no measurement: the stated default, counted at startup (222 cells) | (E) |
| the grip (ltm) MNs | unchanged | | (E) |

the measured factor **replaces** f_w on the classed cells rather than multiplying it: the proxy was the stand-in for exactly this
measurement, and multiplying would count size twice. the default elsewhere is "today's behaviour", not "a fast spike", so the unmeasured
pools do not move.

what is measured, inferred, borrowed:
- **measured:** the three per-spike forces and their 1 : 0.1 : 0.0013 ratio, on one pool (female T1 tibia flexor); the slow unit's slow
  kinetics; summation 1.6x at two spikes, saturation near ten.
- **inferred:** which of our male cells is which class. the thirds are a size rank over the pooled 37 cells of the cord; Azevedo's
  pool is ~1 fast : 2-5 intermediate : 8-9 slow per leg, so thirds overcount fast cells (each of 12 "fast" cells now pulls a full 4.2 nN.m
  per spike, where f_w gave 0.15-1.0) and undercount slow ones. pooled across legs, **the front and middle left legs get no slow cell and
  the left front none below "intermediate"** (the front leg is under-traced, `leg_biomech.md` A3); a within-leg ranking would differ.
  the male file's split of 'Ti flexor MN' vs 'Acc. ti flexor MN' does not map one-to-one onto Azevedo's ~15-cell flexor pool.
- **borrowed / ours:** applying a T1 female number to T2 / T3 and to the male; keeping the twitch kernel for the slow class (it has none);
  the default of 1.0 x f_w on every unmeasured pool; the extensor left on the proxy although the locust says it has a fast / slow pair.

next, if the numbers matter: the slow class on its own kernel (a first-order low-pass, tau 0.2-0.5 s) at 0.013 uN per spike, which is the
form the measurement actually has (section 1's check); a within-leg class ranking beside the pooled one; the extensor as FETi + SETi by
size within the leg, on a comparative (C) ratio, labelled.

## 5. first arms (09-23; the full stack + `--pic smallflex:0.58:3:3:50`, 20 s, seed 11, `--mn-force azevedo`)

| arm | on the floor (% weight) | flexors / extensors Hz | Ti flexor thirds S / M / L Hz | lf foot in air, lifts | knee mean (+ = flexion from neutral) lf lm lh rf rm rh |
|---|---|---|---|---|---|
| walk 100, 50flex | 8 (uniform: 55) | 5.29 / 2.17 | 34.2 / 0 / 0 | 66 % (uniform 87 %), 11 | -2 -10 -3 -6 -7 -12 |
| walk 100, 50ext | 26 (uniform: 30) | 5.52 / 7.68 | 35.7 / 0 / 0 | 1 % (uniform 1 %), 2 | +3 -60 -2 -0 -1 -12 |
| rest, 50flex | 0 (uniform: 0) | 5.45 / 0.11 | 35.2 / 0 / 0 | 0 %, 0 | -3 -5 -6 -3 -2 -7 |
| rest, 50ext | 0 (uniform: 0) | 5.50 / 0.02 | 35.6 / 0 / 0 | 0 %, 0 | -3 -3 -6 -4 -3 -7 |

the slow third's mean flexion torque falls from 0.13-0.37 to 0.01-0.03 nN.m per leg; no knee sits flexed in any arm, before or after.
the left front and left middle legs have no slow-labelled flexor, and the left middle knee's -60 (50ext) is its extensor (~10 nN.m mean).
so the fold in the SEAM entry was not the small flexors' force; one seed each, and the walking arms' differences are within what a
0.2 nN.m change can tip in a chaotic run.
