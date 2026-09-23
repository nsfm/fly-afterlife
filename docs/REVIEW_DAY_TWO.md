# review: day two (09-22 evening to 09-23 noon), the engine terms, the body's senses, and the lift / bout reads

scope: `git log --since="2026-09-22 20:00"`: world/fastlif.py (--syn-tau, --syn-rev / --syn-rev-hold, --pic, `_noise_scale`), world/cord.py,
src/fly_afterlife/size.py, src/fly_afterlife/leg_senses.py, scripts/build_leg_senses.py, experiments/body_loop.py (--senses v2, --log-x,
--freeze-mn, --silence, --mn-force), experiments/lift_read.py, the three engine tests, and docs/SEAM.md from "the movement senses on his own
lifts" to the end. docs/REVIEW_BODY_LOOP.md (first and second pass) was read first and is not repeated. no project file other than this one
was changed. checks live in the session scratchpad, `rv2/` (feet.py: foot heights from the saved joints; cnt.py, bouts.py, surr.py: lift and
bout statistics; lif_iso.py: the isolated cell; run_off.sh: three 8 s body runs).

status: complete (09-23).

## findings, ranked by how much they would change a recorded conclusion

### R1. with the load loop off, the body script never reads the feet's contact force, so "no lifts" in the loop-off, position-only and hooks-only arms is true by construction. by foot height, all three step in the same bouts (HIGHEST)

`experiments/body_loop.py:275`:

    F = leg_forces() if (use_load or args.slow_hz > 0 or args.slow_mv > 0) else np.zeros(6)

`--loop off`, `--loop position` and the hooks-only arm (`--loop position --claw-hz 0 --hp-hz 0`) have no `load` in `--loop`, and the bouts
arm has slow-hz / slow-mv 0. so F is zeros every ms, and it is what gets logged (`FL[ms] = F`, line 296, saved as `leg_force`). every lift
statistic (lift_read.py and the ad-hoc reads) takes a lift as smoothed F <= 0.05, so in these arms every foot is "off the ground 100 % of the
time, 0 lifts" whatever the legs do. the saved `leg_force` of `lift_s11_nosense`, `loop_position` and `loop_hookonly` is identically 0 (max 0.00
on all six legs); the arms with load in the loop have 4-50 uN maxima. the end-of-run line still says "contact forces read" (`force_ok` starts
True, line 268, and only a NaN clears it), which is why this was not caught. a second effect: with `--adhesion contact`, `pad_on = F > 0.05`
(line 316), so in these arms the pads never engage either (the first review's D arm noted this for loop off).

verified two ways:
- **foot height from the saved joints and thorax pose** (`rv2/feet.py`, mujoco forward kinematics of every tarsus5 every 10 ms; the method of
  the first review's Q2). calibrated on the arms where F is read, the height mask (z above lift_s11's 5th percentile + 0.05 mm) agrees with the
  F mask on 82-97 % of frames and gives the same counts (lift_s11: lf 35 / lm 75 by height against 30 / 72 by F). in the arms read as "no lifts":

  | arm (30 s, seed 11) | lf off / lifts / in-bout gap | lm | lh | rm |
  |---|---|---|---|---|
  | all senses (lift_s11), by height | 21 % / 35 / 120 ms | 69 % / 75 / 200 | 6 % / 11 | 59 % / 90 / 190 |
  | **position only** (loop_position) | 32 % / 54 / 200 | 74 % / 55 / 240 | 7 % / 11 | 58 % / 92 / 190 |
  | **hooks only** (loop_hookonly) | 56 % / 33 / 140 | 83 % / 31 / 175 | 30 % / 27 / 140 | 41 % / 67 / 180 |
  | **no senses** (lift_s11_nosense, `--loop off`) | 58 % / 37 / 230 | 86 % / 30 / 190 | 35 % / 35 / 180 | 38 % / 73 / 180 |

  the median foot height in `loop_position` is 0.044 mm on lf (lift_s11: 0.041): the foot is on the ground most of the time, not held up.
- **a direct run.** `rv2/run_off.sh`: the bouts arm with `--loop off`, 8 s, twice: as recorded (`off_ctl`, reproduces `lift_s11_nosense` to
  max |thorax diff| 0) and with `--slow-mv 1e-9` added, which only makes line 275 read the force (a 1e-9 mV current on the slow set; it also
  turns the pads on). with the force logged: the feet carry 7.6 uN of his 10.0 (the recorded arm printed 0.0), and in 6 s after the warm-up lf
  lifts 5 times, lh 7, rm 4, at ~200 ms in-bout gaps.

**what this changes:** the 11:33 "the loop opened: no senses, no lifts; the reflex needs both halves", the 11:56 sufficiency table's
position-only, hooks-only and none rows, "position and movement senses alone make none (he holds all six feet up)", "the load reflex is the
oscillator", and CAMPAIGN lines 85-89 ("named: the load reflex", "a per-leg reflex oscillation through the leg's senses"). the lifts and
their ~200 ms in-bout gaps survive with every sensory row gone. what stands: the freeze (R4), the one-at-a-time ablations (all read F), and
the load and load-only arms (read F). the correct reading of the day's arms: the bouts need the cord's motor output and do not need sensory
feedback from the body; they persist open loop.

fix: read the contact force every ms regardless of `--loop` and log it; gate the load rows on `use_load` and not the reading; take the pads'
switch from the raw contact force, not from a force that is only read in some arms; make `force_ok` report "not read" when F is zeroed. then
re-run loop off / position / hooks-only on seed 11 and 12 and re-read.

### R2. the bout statistics do not show an oscillator: the "five hertz, regular" interval is what a lift's duration plus a memoryless touchdown gives, and the middle legs' clustering is at chance once the Poisson rate is taken over time on the ground (HIGH)

two statistics carried the "bouts" and "five hertz, regular" claims (SEAM, "the movement senses on his own lifts"). recomputed with the same
lift rule (smoothed F <= 0.05 for >= 50 ms, after 2.1 s; `rv2/bouts.py`, `rv2/surr.py`), on lift_s11, lift_s12, lift_s11_ext:

- **"the next lift within 300 ms of the last one's end: 0.59 / 0.72 against Poisson's 0.27 / 0.40."** reproduced (0.59 vs 0.28, 0.72 vs 0.40
  on lf). but the Poisson rate there is lifts per second of the whole run, and a leg can only start a lift while it is on the ground. with the
  rate over time on the ground: lf 0.59 vs 0.34, 0.72 vs 0.50 (an excess remains on the front leg); **the middle legs, which carried "the
  middle legs more so", sit exactly at chance:** lm 0.93 vs 0.92, 0.90 vs 0.93; rm 0.76 vs 0.75, 0.84 vs 0.82.
- **"inside a bout the gap is 160-200 ms with a cv of 0.25-0.46."** an in-bout gap is onset to onset under 300 ms, i.e. one lift's duration
  (median 85-177 ms here) plus one stretch on the ground, truncated at 300. two nulls with no oscillator in them give the same numbers:
  lift durations and on-ground gaps shuffled independently (serial structure destroyed), and on-ground gaps drawn exponential at their
  observed mean:

  | run, leg | observed median / cv | shuffle null median / cv [90 % range] | exponential-gap null median / cv [90 %] |
  |---|---|---|---|
  | s11 lm | 194 / 0.32 | 196 / 0.31 [0.27, 0.34] | 193 / 0.33 [0.28, 0.38] |
  | s11 rm | 166 / 0.29 | 168 / 0.30 [0.27, 0.34] | 187 / 0.33 [0.27, 0.39] |
  | s12 lf | 190 / 0.25 | 184 / 0.30 [0.25, 0.35] | 192 / 0.31 [0.22, 0.41] |
  | s12 lm | 193 / 0.24 | 191 / 0.29 [0.25, 0.33] | 193 / 0.32 [0.27, 0.38] |
  | s12 rm | 201 / 0.26 | 192 / 0.29 [0.25, 0.32] | 193 / 0.32 [0.27, 0.37] |
  | s11 lf | 126 / 0.46 (n = 11) | 144 / 0.36 | 188 / 0.32 |

  a cv near 0.3 is also what a uniform interval over [70, 300) gives (0.36): the truncation makes it. the n behind the front leg's cv is
  5-22.
- the motor side agrees: the leg motor pools' spike counts (10 ms bins) have no 5 Hz peak in any of lift_s11 / loop_position / nosense
  (peaks 1-15 Hz, x7-13 over the median, different per leg and arm). what the lifts do line up with is the levators: the leg's Tr flexor MN
  count leads the foot's upward velocity by 20 ms at r 0.34-0.56 in every arm, open loop included.

so the record has lifts that come from levator bursts, last 100-180 ms, and are followed by a return whose timing is indistinguishable from
memoryless; not a 5 Hz oscillator. the "in every arm with an unloaded leg" constancy of 150-240 ms is the constancy of the lift's duration
under the same springs (flygym's stiffness 10, the first review's Q1) and the same 120 ms twitch kernel.

fix: report the onset-to-onset interval distribution untruncated, against a renewal null built from the observed durations and a
memoryless gap (or the hazard of lift onset against time since touchdown); put the Poisson rate on time on the ground; read a rhythm only
from a spectral peak in the motor pool that the foot follows.

### R3. the slow / intermediate / fast labelling ranks the 37 tibia flexors of all six legs together: the left front and left middle legs have no slow cells, so the tone, the plateau and Azevedo's force are on four legs and not symmetric (HIGH for the body's left-right reads; MEDIUM otherwise)

`fastlif.py:371-374` (`--pic smallflex`), `body_loop.py:233-236` (`--mn-force azevedo`) and the graded CSV all take thirds of the whole
'Ti flexor MN' pool by input synapses (checked: the three give the same 13 small cells). by leg (`world/legmn.npz`):

| third | lf | lm | lh | rf | rm | rh | input synapses |
|---|---|---|---|---|---|---|---|
| small (slow: 3 mV, x2.3, plateau, 0.0013 force) | **0** | **0** | 5 | 3 | 2 | 3 | 13-180 |
| middle (15 mV, x0.47) | 3 | 3 | 2 | 1 | 0 | 3 | 227-451 |
| large (23 mV, x0.30) | 2 | 2 | 2 | 1 | 3 | 2 | 902-8,167 |

(the smallest cells, 13-111 synapses, are more likely under-traced fragments than a size class, and they cluster on the hind and right legs.)
every body arm since 09-23 00:06 therefore puts the slow cells' tone and the plateau only on lh / rf / rm / rh, and on the left front and middle
legs gives the tibia flexors only 15 and 23 mV thresholds. the day's replicated asymmetry, "he leans right, the left legs are off the ground
20-97 % of the time and the right 0-13 %", and the left front / left middle co-lifting, are on exactly the two legs that were given no slow
flexors. not tested here (a per-leg labelling needs a script change), but it is a labelling asymmetry sitting under a postural asymmetry.

fix: thirds within each leg (or by size within each leg's pool, with a floor on "too few synapses to be traced"); re-run the lean.

### R4. the small flexors' rest is the noise term's arithmetic: an isolated cell at 3 mV with the noise x2.33 fires 0.8 Hz; "Azevedo's ordering" is the thresholds put in (MEDIUM; relabels item 3)

`fastlif.py:440` scales the pooled noise per cell (0.15 mV per step x `_noise_scale`). an isolated LIF with the engine's step (tau_m 20,
1 ms, reset 0, 3 steps refractory, floor -7) and no synapses (`rv2/lif_iso.py`, 2,000 s each):

| noise per step | threshold 3 mV | threshold 7 mV | membrane sd |
|---|---|---|---|
| 0.15 (x1) | 0.00 Hz | 0.00 | 0.48 mV |
| 0.35 (x2.33, k = 1) | **0.80 Hz** | 0.00 | 1.1 |
| 0.81 (x5.4, k = 2) | **13.6 Hz** | 0.77 | 2.0-2.5 |

the SEAM's cord arms: k = 1 at rest 1.15 / 1.18 / 1.30 Hz, k = 2 14.05 Hz; on the body at rest 0.68 / 0.75. so nearly all of the small third's
rate is the cell alone at the chosen threshold and noise, and the three-of-three replication replicates noise draws. the middle and
large thirds are silent because they were given 15 and 23 mV thresholds; the ordering is the input. the SEAM's 23:58 entry says "about 0.7
Hz ... is their own noise", which is right; the CAMPAIGN item 3 line ("the small third fires at rest ... Azevedo's ordering") and the 00:06
entry read it as a result.

and the one CSV couples two things that Azevedo gives separately. `flex_graded_abs.csv` carries 0.4286 / 2.1429 / 3.2857 for the three
thirds and every other cell 1.0 (so S_med is exactly 1.0: the normalisation is what was intended, unlike the flexor-only CSV that put the
slow third at 1.4 mV). `size.py` uses the same ratio for the threshold (x ratio), the synapses (/ ratio) and the noise (/ ratio). for the
slow third that is 3 mV and x2.33 (700 / 300 MOhm), as stated; for the middle and large thirds it is x0.47 and x0.30 on synapses and noise,
where the resistances named (300 and 150 against the population's 300) give x1.0 and x0.5. the "intermediate" cells get half their
stated drive on top of a 15 mV threshold.

fix: label the ordering as imposed and the rate as the noise's; give threshold and resistance separate CSVs (or columns) in `size.py`.

### R5. the tactile onset burst re-fires on the net force's chatter: 20-74 "touchdowns" per second per leg, and the 5x burst covers 31-93 % of the time on the ground (MEDIUM)

`body_loop.py:290-292`: touch is on while `F > 0.05`, with 5x the rate for 30 ms after each off-to-on edge, and F is the contact force net of
the pad (line 276). the first review's second pass found that net force flickering (the pad switching ~70 times a second); it is still
there, and touch now rides it. in lift_s11 the raw F crosses 0.05 upward 46 / 51 / 22 / 49 / 74 / 22 times per second (lf ... rh), and the
onset burst is on for 80 / 93 / 31 / 76 / 89 / 38 % of each leg's time on the ground. so the tactile rows run near 100 Hz through most of
stance on the front and middle legs where the flag says 20. the load rows ride the same chatter (15 x F / F_stand switching between 0 and
its value tens of times a second). the touch ablation ("touch and the hair plates hold the foot down") and any reading of the load rows'
rate inherit it.

fix: debounce contact (hysteresis on the raw contact force, a minimum off time before a new onset), take the pad from the raw force or
the adhesion actuator's force (the second pass's fix, still open), then re-run the touch arms.

### R6. "the load rows" are 12 % campaniform; and in the position-only and loop-off arms the same cells stay on at the full standing rate (MEDIUM-LOW)

- the load row is `campaniform + untyped` (`body_loop.py:126, 133`): per leg 2-3 named campaniform and 5-25 untyped, 13 + 98 of 111. the
  map (`docs/physiology/leg_senses_map.md:46`) gives untyped as SNppxx / SNxxxx / SNpp55 / SNta21 and says SNppxx holds most leg CS **and extra
  hair plates**. the tables say "campaniform + untyped"; the headline ("campaniform rows alone make the bouts", "the load reflex") does not.
- the load-only arm itself is clean of the named position senses: with `--loop load` the claw, hook and hair-plate rows are never
  registered; the v2 floor was moved onto campaniform + untyped (line 129), so the claws and hair plates are in no row and stay at
  drive_hz 0; the quiet row holds clubs / hooks / unclassified at 0; `--tactile-hz 0` zeroes touch; there is no tactile floor.
- but the floor keeps the same 111 cells at `--leg-load-hz` 15 Hz whenever the per-leg load rows are absent (the rows later in the registry
  override it only when registered, `receptors.py:249-254`). so `--loop position` is "position + a constant full-standing load on every leg",
  and `--loop off` is "a constant full-standing load", not "no senses". with R1 fixed this matters for any sufficiency read.

fix: say campaniform + untyped wherever the row is named; for a position-only or no-sense arm also pass `--leg-load-hz 0`.

### R7. the freeze is a valid control for "the muscles are needed" and cannot tell a reflex from a central drive; it also stops the motor spike log (LOW)

- valid as far as it goes: after `--freeze-mn`, `torque[:, ms] = _hold_t` every ms (lines 303-306) overrides the twitch-kernel tail already
  written into later columns, so the torque is exactly constant; grip is held in the dict, but the arm ran `--adhesion contact`, where the
  pads follow F (line 316) and not `grip`. it does not matter: by foot height the whole body is still after the freeze (z sd 0.000 mm on all
  six feet from 15 s; before it the same run as lift_s11 frame for frame), so nothing is left to chatter.
- the cord and the senses keep running (the sensory rows are computed from the still body); with the body still they see a constant pose.
  what the control shows is that the lifts need the cord's motor output. with R1, it no longer pairs with "no senses, no lifts", so it
  does not separate a reflex from a drive the cord makes on its own.
- `hit = np.zeros(0)` in the freeze branch skips `spk[...] += 1` (line 311), so the leg motor neurons' frames are 0 after the freeze: the cord's
  motor output after 15 s cannot be read from the cells file (`x_ms` for `--log-x` types is logged before the branch and continues), and the
  end-of-run "leg MN Hz / flexors / extensors" of a freeze run averages in the frozen half as zeros.

fix: log the spikes in the freeze branch and only skip the torque; say "the motor output is necessary" rather than "the bouts are neural".

### R8. the lift detector: onsets 7-8 ms late, the docstring's 100 ms on-ground rule not applied, and the both-off baseline without an interval (LOW)

- `lift_read.py:21` smooths with a centred 21 ms boxcar; the smoothed force crosses 0.05 a median 7-8 ms (10th-90th percentile 3-10) after
  the raw force does. at 20 ms bins this moves "the 20 Hz subnet bursts ... coincident with it (cross-correlation peaks at +20 ms)" to about
  +10 ms after the true unloading; direction unchanged.
- the docstring says a lift counts "after >= 100 ms on the ground"; the code keeps only `a >= 2100`. on-ground stretches between counted
  lifts go down to 16-31 ms, so a lift with a brief touch in it counts twice and adds a short interval.
- the both-off statistic uses the product of the two legs' off-fractions. a circular-shift null (2,000 random lags > 1 s) agrees with the
  product and gives the missing interval: seed 11's middle-leg deficit was real within that run (0.80 % vs null [1.18, 3.96], 1.34 % vs
  [2.02, 9.20]), so withdrawing it because the other seeds have only one stepping middle leg is right. the population arm's "exactly as
  independence" (29.6 vs 32.2) is at the null's lower edge (29.65 vs [29.61, 35.10], p 0.03). the left front / left middle co-lift is above
  its null on both runs checked (18.2 vs [12.5, 17.3]; 78.3 vs [71.7, 74.2]).

### R9. small things

- `size.py:33`: with `--size-from`, `_neur = _have & _neur`; a CSV that lists only some cells (the flexor-only CSV) takes S_med over those
  cells alone and scales nothing else. the `_abs` CSVs (every cell, 1.0 by default) do what was meant. worth an assertion or a printed S_med.
- the `--log-v` trace is the mean over every cell of the named type (and includes a spiking cell at its reset 0), so "the small cells sit at
  -0.5 to -0.7 mV re rest (sd 0.2-0.3)" is the sd of a population mean, not of one cell (one cell's is ~1.1 mV at x2.33, above).
- `--pic` at `v_half +3, k 3` on cells whose threshold is 3 has m_inf(rest) = 0.27, so the cell is a pacemaker by construction and g sets the rate
  directly (g 0.58 puts the steady state at 3.1 mV, the threshold). the record says g is bracketed, not pinned; fine, but "Azevedo's 30 falls
  between the first two" is a statement about g.
- the hair plates in v2 fire for coxa excursion either way from neutral (`body_loop.py:289`), both hair-plate types alike; labelled
  unsourced, noted.

## checked and found sound

- **the engine terms.** `_membrane_nt*` and `_membrane_*_rev`: each class row decays with its own tau; the reversal term's sign and scale
  (kap = sign / E_ach or sign / |E_c|; a GABA row's negative weight times a negative kap is a positive conductance; the driving force uses
  the step-start v in both integrators; phi(x) caps a large conductance at its reversal); `exact_kg`'s tau_s = tau_m limit. no cell in
  brain_cord.npz has a sign that disagrees with its transmitter class (0 / 0 / 0), so no negative conductance reaches phi. all three engine
  tests pass as committed (`syn_tau_test`, `syn_rev_test`, `pic_test`, run today).
- **the plateau's step.** m advanced from the step-start v, then the current from the new m and the step-start v, on the ext path at
  tau_m x g m (70 - v) / 70, so dv = g m (70 - v) / 70 per ms to first order; `reset` zeroes m only with `:reset`; off is not run.
- **the noise scale and the pooled buffer.** `noise * self._noise_scale` makes a new array; the pool is never written; unset, the line is
  skipped. the scale does not change the pool's offsets or strides.
- **the defaults reproduce, by logic and by run.** v1 is the old code under an `if`; `--silence`, `--log-x`, `--log-v`, `--freeze-mn`, size and
  `--mn-force` are no-ops at their defaults; the tactile subset uses its own Generator (`[seed, 6, leg]`) and never touches the engine's
  rng. a rerun of the full-stack bouts arm without `--log-x` reproduces the saved `lift_s11` (run with it) to max |thorax diff| 0 and max |F diff| 0
  over 8 s, and the loop-off rerun reproduces `lift_s11_nosense` to 0.
- **`--log-x`.** `np.add.at(XMS[ms], ...)` writes into the row in place; a cell fires at most once a step; logged before the freeze branch.
- **the claw's 90-deg reference.** knee_sign is +1 on all six legs (`results/body_dof_signs.json`), so k = model angle - 90 and femur-tibia =
  180 - model angle: flexion past 90 is k > 0 and goes to the flexion class that `--claw-labels` names.
- **the v2 rows against the floor.** registration order is floor, quiet, then the per-leg rows, and a later row overwrites an earlier one on
  shared cells, so the per-leg load rows override the floor's 15 Hz when present (and only then, R6).
- **the small set is one set.** `--pic smallflex`, `--mn-force azevedo`'s slow class and the graded CSV's 0.4286 cells are the same 13 cells.
- **the dose, ablation and load / load-only arms** read the contact force and their lift numbers stand as computed (subject to R2's reading).

## verdict

the engine terms are correct and their defaults are the record. the day's biological headline does not survive: the "loop opened, no
lifts" and "position senses alone make none" arms measured a contact force the script was not reading, and by foot height the lifts and
their ~200 ms gaps are there with no senses at all; the "five hertz, regular" statistic is reproduced by a null with no oscillator in it;
and the slow flexors' tone is placed on four legs, not six, with the two left legs that hang given none. what the record can say today:
the lifts are the cord's levator bursts through the body, they need the motor output (the freeze), they do not need the leg's senses, and
their timing is not yet distinguishable from a lift's duration plus a memoryless return. the order to re-run: R1's fix (force always
read, pads from the raw force), then the loop-off / position-only arms by force, with R2's nulls beside every bout claim, with R3's
per-leg labelling.
