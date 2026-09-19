# TODO

everything pending, in one place. 2026-09-16 23:30 PDT (nyx). the record (`docs/SEAM.md`)
says what was done and why; this says what is not done yet. items reference the physiology
briefs in `docs/physiology/` where a number came from there. rule for every behaviour change:
one change per run, against the previous run, and a large effect from closing one afferent
loop is probably a bug (mechanosensation brief).

## 0. in flight tonight

- [x] approach test: 10 seeds x {her dark 0.1, her invisible 0.5} x 120 s (`world/approach/`).
      in the record 23:50: left-side effect was an artefact; right-side turn toward her survives
      (8/10, p 0.02) plus 1.8x time near her. re-run pre-registered after the steering fix.
- [x] corrected synapse constants, first minute (`world/pair_w185.npz`): in the record 00:00.
      standing baselines all zero; leg MN halves; he still finds her. PACE READOUT DEGENERATE
      (standing = 0 saturates it): fix in effectors with an absolute reference + MN class weights.
- [x] oracle runs (`world/oracle/`, `scripts/oracle_check.sh`).

## 1. the refactor (`docs/ARCHITECTURE.md`), before any new receptor

- [x] oracle runs: current room, `--deterministic`, 30 s, seeds 3 and 4, at old and corrected
      constants (four npz). the ported room must reproduce them bit for bit. (00:32: pass)
- [x] `receptors.py`: registry + selectors + transducers; existing drives ported unchanged;
      verified bit-identical (00:32). physiology transducers (Adapting, Differentiator,
      WeberFechner) still to write, one per behaviour change.
- [x] `body.py` + `world.py`: pose, contacts, walls, pillars, the pair, the scene; verified
      bit-identical (00:58). gait generator, body-part contacts and scalar fields still to come.
- [x] `effectors.py`: steering, pace, her steering, song, the calibration procedures; verified
      bit-identical (01:10). calibration cache by (brain, w_syn, seed) still to do.
- [x] `episode.py`: one loop, verified bit-identical (01:21); `pair.py` is 134 lines of setup.
      still to do: `per_frame` / `per_chunk` namespaces, two brains in threads (numba `nogil`).
      `loop.py` stays a legacy experiment; its modes get re-implemented on the stack (drum first)
      and validated against the recorded numbers rather than ported.
- [x] flyvis front end as `frontend.py`; the room uses it; verified bit-identical (01:47). pair.py 111 lines.
- [x] drum on the stack (`experiments/drum.py`, 01:28): 2/3 seeds follow both ways (record: 3/3;
      ensemble 2-3/10). bar, walk, forage modes still to re-implement when needed.
- [ ] `--no-female` default for calibration and male-only questions; her in the room only for
      contact and courtship runs.
- [ ] drive resolved per 1 ms step, not per 10 ms frame (30 ms adaptation kernels need it).

## 2. physiology-driven changes, one per run, in this order

- [x] **THE TONIC FLOOR** (built 09-17 18:27): central 0.013 -> 0.53 Hz, DN symmetric, KC code unchanged;
      room: less pinned, further walked. default from here. rates marked (E) still to source; JO, proprio.
- [ ] (was:) every typed sensory class at its physiological
      resting rate by default (ORNs ~8 Hz generic, Or67d 0.12, hot 37, cooling 95, dry/moist ~20,
      JO still-air, proprioceptors under standing load, gustatory ~2, ocelli by light), the world only
      modulating. one step against the current baseline; expect the operating point to move.
- [ ] the walking command silences DNa02 R (2.6 L / 0.02 R per chunk on a walking cord; 1.6 / 1.4
      standing): an interaction between the command and the visual wheel. trace it (DNp09 -> ? -> DNa02 R)
      and decide whether the wheel reads DNa02 at all on a walking cord (18:15).
- [ ] thermokinesis: turning rate up when warming is in the wiring (17:20); the pace sign is inverted
      (readout interaction with turning). understand, then the cold corner and the extremes.
- [~] **synapse constants** (vision brief): male 0.185, female 0.275; `RunningPace` fixes the
      degenerate pace (08:58); male-only baseline in progress; then her. re-measure every baseline. reconcile her 0.45 KC-sparsity calibration with the
      22:55 odour test (4.7% at 0.275): different odour protocol, find which was right.
      re-examine MDN's tonic activity (present at 0.275, gone at 0.185) and the reverse-walk rule.
- [x] **steering baseline**: `RunningBaselineSteering` (01:55). model 000: 3/3 seeds (fixed 2/3);
      ensemble 3/10 (fixed 2/10), biases from +-100 to +-20, and two models revealed as anti-followers.
      adopted as the estimator; the wheel's per-model sign is a seam question, not a steering one.
- [ ] **DNa02 gain**: 5 deg/s per Hz (bracketed 3-10; ours is 3).
- [x] **bristles** (mechano brief): `Adapting` 200 Hz onset, tau 30 ms, 20 Hz plateau, half the patch,
      step-locked re-deflection at 10 Hz; reflex calibrated on the kernel (09:23). adopted. still
      to do: seconds-scale fatigue, by body part; measure the bristle->leg-MN gain at 0.185 mV.
- [~] **leg MNs**: audit DONE (12:05): bristle = muscle-specific withdrawal pattern; vision = a whisper;
      warmth = bilateral. next: the motor-pattern readout (projection on the withdrawal axis); Azevedo
      2020 classes (slow ~30 Hz standing; 0.1/1/10 uN) still unmodelled.
- [ ] **campaniform sensilla**: dF/dt, burst at stance onset, adapt out mid-stance, a
      subpopulation on unloading. replaces the 15% tonic load term.
- [ ] **gait**: step frequency from speed (Wosnitza 2013), stance ~ v^-1, swing 20-45 ms,
      period floor 60 ms (16 Hz max, not 10); tetrapod below 5 BL/s, tripod above 10.
- [ ] **hook FeCO gate**: presynaptic inhibition during walking under descending command
      (Dallmann 2025); apply at the drive (Poisson receptors ignore their membrane). claw,
      club, hair plates ungated.
- [x] **cooling cells** and **hot cells** as transducers (`CoolingCells`, `HotCells`, 09:49) with
      Budelli 2019's numbers; on in the room with `--thermo rest|field`.
- [ ] **VP1m / VP1l label audit** before driving either (Marin 2020: VP1m humid, VP1l cool).
- [ ] **the warm corner** (13:28): no avoidance on a walking cord either (2/3 warmer with the field).
      thermal DNs reach wing MNs mostly; warmth is bilateral at the legs. parked: thermotaxis by walking
      is not in this model at these constants. what warmth does do: drives the legs harder (kinesis).
- [ ] **hygro**: dry/moist cells non-adapting, tens of Hz; a humidity field. Or42b ORNs are
      also humidity sensors (Li 2022).
- [ ] **plumes**: intermittent (power-law whiffs/blanks, exponent -3/2), ORN rate from
      concentration divided by a running mean (tau ~1 s). replaces exp(-d/0.8). Or67d rest
      0.12 Hz, not ~8.
- [ ] **sugar spot**: Gr5a/Gr64 ~65 Hz at 100 mM, adaptation within 1 s; bitter > 10 Hz =
      aversion floor. a room with three things in it (her, warmth, sugar).
- [x] contact-pheromone tap: 60 Hz burst, tau 300 ms, both ppk channels (done 22:40).
- [ ] Gr32a/Gr33a aversive channel on male-male contact (10-60 Hz, phasic).
- [ ] **LC10a gain P1-dependent** (Hindmarsh Sten 2021): without it he does not track her.
- [ ] **P1 as a dial, not a switch** (09-17 17:44): read P1 rate against Hoopfer 2015's thresholds
      (low activation = aggression, high = courtship); our touch-driven P1 sits at the low end. audit
      which inputs move it where; the same reading serves the rival and the courtship state.
- [ ] **the courtship sequence as a state** (promoted 09-17 13:59): a persistent state (pCd, minutes)
      that holds the brake (AN19A018) at her and drives following; her stop or receptivity (vpoEN);
      P1 threshold-graded (Hoopfer 2015). the song relay (P1 -> pIP10) stays blocked; mAL gate measured.
      --stop-at-her (brake on contact frames) did nothing: contact is too brief and she walks away.
- [ ] walking-state gain on visual channels (Chiappe 2010; Suver 2012).
- [ ] efference copy onto JO-A/B (Cheong 2024); JO wind/gravity; the wing-wash loop when he flies.
- [ ] ocelli: light level; find his OCC/OCG cells (hers are typed, 63).

## 2a. the enriched world (promoted 09-17 22:05, nate; before the rival)

- [x] the garden (09-17 night): floor plane with texture, grass, leaves + shade, stone, fruit (plume +
      sugar), puddle (humidity), sun patch, rim; RGB reduced to fly luminance; both raytracers.
- [x] first scores (09-18 00:24): the fruit is found by sight (0/3 when invisible), the plume changes
      nothing (smell does not reach the steering readout); puddle / sun / shade passed through.
- [ ] **anemotaxis on the settled fly** (09-18 16:50): the wind-gated upwind turn was measured on a fly with
      50 deg/s of heading noise; now 20-29. re-run the downwind start with `--wind on --wind-gate odour`
      (the wind rows need a steering channel: the population channel is out of the config as noise; a named
      six lateralised DN types (review) or the JO rows into the HS wheel's baseline is the design question).
- [ ] the plume: power-law whiff / blank durations (simplified Bernoulli today); her odour and a rival's
      through the same field; the smell-steering gap (ORN -> ... -> DNa02 is silent) is the wall.
- [ ] the garden with her; the garden with the courtship state when it exists.
- [ ] terrain (nate): a gentle heightfield tilting his pose, feeding JO gravity and leg load (phase 2).
- [ ] bristles by body part (antenna, head, legs, wings are typed); the head-on class returns for
      head bristles.
- [ ] status of every sense: `docs/SENSES.md`.

## 2b. legs with muscles (promoted 09-17 12:30)

- [x] the leg MN SET: 373 leg MNs by subclass fl/ml/hl (12:45; the 699 included abdominal, wing,
      haltere, neck, jump). all leg readouts re-based on it.
- [x] the leg model (12:36): `legs.py`, DNa02's sign reproduced; effector `--effector legs`.
- [x] a walking command (12:56): `--walk 100` (DNp09 tonic); he walks 31 m / 2 min on the true leg set.
      **09-18 11:30: DNp09 is inert under the tonic floor; the command is DNg100 (BDN2) now, a dose in the loop
      (16 / 35 / 50 m at 0 / 100 / 200 Hz), pace read against the standing tonus measured in the floor.**
      **12:20: `--pace state` (threshold + hysteresis on the smoothed cord; DeAngelis 2019 bimodal): he stands
      with no command and walks in bouts with it. config of record.** next: the closed-loop floor-row
      ablation (which row lifts the resting cord: thermal? ORN?); MN class weights (Azevedo 2020); the brake
      re-measured against DNg100 (30 Hz did nothing open loop).
      still to do: the command as a state (walk / stop / brake DNs, Sapkal 2024); stance/swing phase
      so MDN reads as backward; the DNp09 right-bias (tracing) as a labelled correction or not.
      the leg model is NOT a wheel (drum 0/3 rectified, 1/3 signed): pace + diagnostic only.

## 2e. what the dish said (09-18 18:25, `experiments/benchmark.py` vs the Roman lab's flies)

- [~] **menotaxis, in stretches** (09-19 11:26): the graded PFL3 readout (`--goal-wheel-v 20 --goal-ema 5`, the null point with
      the bump present) holds a goal heading 41 % / 34 % of a run within 30 deg, in 20-40 s stretches, lost at the rim and at
      the 180 deg saddle. next: the dish (no rim detours); a slowly adapting null; PFL2 as the forward drive when aligned
      (in life he pauses and turns when far off the goal); then the saccade as an event on top.
- [~] **the compass, stand-in built** (09-18 23:55): `--ring` forms a bump that tracks his heading from the sun (r 0.99;
      `docs/figures/compass_bump.png`), sensory-driven (PEN silent); `--goal` makes PFL3 compare with the right sign
      (r -0.68 with the error) and reach the LAL; `--goal-wheel` does NOT hold a heading (PFL3 3.6 Hz across 24 cells:
      shot noise 5x the signal). all three stand-ins are opt-in and tuned. NEXT, graded: (a) a graded PFL3 / LAL readout
      (rate from membrane, not spikes) or the goal drive raised until PFL3's L-R is above noise, labelled; (b) the
      anterior visual pathway graded (the eye track) to replace the imposed ring fields with seen ones; (c) the ring's
      persistence (EPG-PEN recurrence at 0.185 mV).
- [ ] **the compass needs a graded build** (09-18 late): the UV retina, the sun disc and the columns exist (`--uv`), but the
      anterior visual pathway (R7 -> Dm2 -> MeTu -> TuBu -> ER) does not carry spikes at these constants (photoreceptors
      are histaminergic: light inhibits; Dm2's excitation is two synapses' worth; at gain 1,000 the ring neurons still
      sit at 0). and the ring's bump is tonic excitation shaped by inhibition, which silent LIF cells cannot do. options:
      (a) a graded model of the anterior pathway + the ring (a flyvis-like extension: the eye track); (b) a labelled
      stand-in: ring neurons driven by the sun's azimuth (their receptive fields tile azimuth in life), with the EPG
      ring given a tonic floor (ExR1 / PEN at rest) so ER inhibition can shape it; test with `experiments/compass.py`.
- [ ] **the compass is dark** (09-18 night): EPG / PEN / Delta7 / PFL all 0.00 Hz with vision on, and the ring does not
      hold a kicked bump. FIRST: the anterior visual pathway into the seam: flyvis Mi15 onto his Mi15 cells by column
      (Mi15 / Dm2 -> MeTu -> TuBu -> ER; the R7/R8 pathway, a luminance stand-in, labelled) + a sun disc in the sky
      (a few degrees, clipped white; the eye's acceptance angle is the bloom). score: EPG rates, a bump vs shuffle,
      phase vs heading (`experiments/compass.py`). THEN: bump persistence in darkness (the EPG-PEN loop at 0.185 mV).
- [ ] **the saccade.** he never turns sharply: every 40 ms heading change under 30 deg (life: 60 %); inter-turn
      interval 1.0-1.4 s (life 0.25). look in the wiring first: do DNa02 / DNa01 / DNb06 / DNg13 burst on the
      woken brain, and can a burst be read as an event (a fixed-size turn) on top of the smooth HS wheel
      (Rayshubskiy 2020: DNa02 bursts precede spontaneous turns). a stand-in only after, labelled.
- [ ] **the spontaneous stop.** he never stops in the dish (0 % vs 21 %); bouts end only when something halts the
      cord. do the halting types (DNg105, the Sapkal 2024 set) fire on their own on the woken brain?
- [ ] **reversing along the wall.** circling bias exactly +/-1; both of the above should fix it; score it.
- [ ] the scorer: hysteresis on the walking threshold; a heading filter for tracked centroids; the 5.0 cm dish
      as the second condition (`--arena-radius 1.67`).
- [ ] the viewers: draw the ring for `world == "arena"`.

## 2c. what the fly asked for (09-18 01:02, `docs/SCENARIOS.md`; the unmet items, in his order)

- [~] **persistent internal states** (09-18 14:15: the FIRST one is built: `FeedingState`, sugar latches feeding,
      holds the halt on DNg105, silences withdrawal; satiety fills and releases; he eats and leaves. the rest:)
      as scalars with decay constants: hunger, thirst, satiety, arousal,
      sleep pressure, aggression threshold, the loser effect. modelled as what they do (gains on
      food receptors, thresholds on outputs, a drive on the walking command), labelled; the engine has
      fast synapses only, so driving the peptide cells does nothing (SEAM 00:54). breaks six of his
      twenty scenarios by itself. the next build.
- [ ] the plume with power-law whiff / blank durations (see 2a) and the wind that carries it also
      deflecting his aristae (done: `--wind on`).
- [ ] **bitter as a field** on the same surface as sugar, non-adapting, Gr32a/Gr33a; the PER threshold
      under the satiety state. (sugar, water: done.)
- [ ] **the escape path**: loom -> giant fibre -> jump, outside the deliberative loop, both take-off
      modes; needs a loom detector the eye track does not have yet (§3).
- [ ] **sensory and motor delays** (5-15 ms in, 20-40 ms out): without them he is more stable than a
      fly and we cannot tell which successes came from that. frame-level today (10 ms).
- [ ] **humidity with a state-dependent sign** (sated: dry; desiccated: moist, faster in dry air): one
      field, one sign, from the thirst scalar above.
- [ ] **a compass with drift** (menotaxis: sky direction, updated by his own turns, holdable at an
      offset for minutes): the central complex has it; a sun in the garden already; measure whether
      EPG / PEN bump exists in him before building anything.
- [ ] **luminance- and temperature-dependent bandwidth** (eye Q10 6.5; dusk): a gain on the eye
      front end, later.
- [ ] **efference copy into the wide-field visual channels** at saccade onset (with the JO one in §2).
- [ ] declined by him, agreed: no wings, no oscillating halteres, no colour (until the eye track).

## 2d. the benchmark (09-18 14:30, `docs/BENCHMARKS.md`)

- [ ] a circular open-field arena at the published size (8.4 cm = 5.6 sim m; Soibam 2012, Valente 2007), lit,
      male alone, 600 s runs (exploration is non-stationary; 120 s is too short to compare).
- [ ] score against opynfield's bundled trajectories (243 lone lit Canton-S males, 8.4 cm, 600 s, ~31 Hz):
      speed modes and stop threshold (Valente 2007: walking mode 11-15 mm/s, stop < 1 mm/s), bout and pause
      durations, turn-angle distributions at the paper's sampling interval (decimate the 100 Hz log), wall
      occupancy (88-90 % within 6 mm), and Soibam 2012's two-parameter model (persistence + wall attraction,
      F0 0.0268 / cm, Rc 0.6 cm) as the thing to beat; with a time-rescaling control for our ~3x slow gait.
- [ ] the hourglass arena (Soibam): wall-following as a visual object vs touch contact; the cheap discriminator.

## 3. the eye track (independent of the above)

- [ ] ensemble-averaged flyvis T4/T5 as the seam input (per-position DS check first).
- [ ] train the transplant on the optic-flow task itself, not on flyvis outputs (distillation
      by MSE is spent: OFF alive, no DS gain).
- [ ] her eye: column coordinates for FlyWire from lamina positions.
- [ ] colour (R7/R8 in the transplant).
- [ ] the loom detector: all claims withdrawn; needs DS fidelity from any front end.
- [ ] flyvis chunk is now the largest single cost (8 ms per eye per chunk); batch both eyes.

## 4. her

- [ ] her W_syn: see constants above.
- [ ] her MBON output on the honest build (memory forms at the synapse, weak at the output).
- [ ] vpoEN silent to everything tried; her receptivity circuit (Wang 2021; Deutsch 2019).
- [ ] her pillar collision: done; her wall turn-away is a labelled stand-in (no cord).

## 5. data audits

- [ ] proprioceptor counts vs periphery: 52 prothoracic-nerve cells vs ~152 FeCO per front leg;
      L1 35 / R1 17; tactile 2,503 vs ~500 bristles per leg. what the table is missing.
- [ ] `receptorType` coverage for ppk / Gr / Or / Ir cells in both builds.
- [ ] right hemisphere more completely traced (known): quantify per class for the wheel.

## 5b. the engine (09-19 10:47)

- [x] **exact integration** (`--integrate exact`, default): Shiu's `method='linear'`; PSP peak on the analytic curve; a third
      faster; the brain 1.5x hotter; KC sparsity 3.9 % at 0.185 (Euler 1.8 %); drum 3/3; he eats. oracle v2 frozen on it.
- [ ] **g frozen during the refractory period** (Shiu's "(unless refractory)" on dg/dt): the second difference from the
      paper; opt-in, measure, adopt with oracle v3 if it holds.
- [ ] re-measure on the exact engine what the record measured on Euler: the floor's tonus by row, the DN L/R table, the
      walking dose, the reflex gain, her at 0.275, the room baselines; then the dish benchmark.
- [ ] the divide -> multiply in `_membrane` is moot (the exact kernel has none); interleave the state arrays (1.16x).
- [ ] the sparse Poisson drive (count-then-scatter) from flyproject; a bitmap active set only if it stays contiguous.

## 6. performance (`docs/PERFORMANCE.md`, 09-18 17:00: measured, an opus agent)

- [x] two brains in threads (numba nogil): done 09-17.
- [ ] **the LIF step is 81-88 % of the loop; flyvis 5-7 %** (TODO §3's "largest single cost" is stale). inside the
      step: the membrane pass over 162,517 cells ~84 %, the driven-cell Poisson draw ~22 % (25,973 receptor
      cells since the floor), synaptic propagation 3 %.
- [ ] **fold the Poisson draw into one nogil kernel** (prototyped in the agent's scratchpad; keeps the rng.random
      call so the draw order holds): step 1.216x faster, 500/500 steps spike-for-spike identical. ~25 lines;
      oracle-checked. the one measured, bit-identical win.
- [ ] **thread budget:** the step scales 1.86x from 1 to 6 threads and nothing from 2 to 6 under contention;
      run_many with 3 jobs x 4 threads oversubscribes 8 cores. jobs, not threads: 3-4 jobs at 2 threads.
- [ ] the membrane pass is the ceiling on CPU; a GPU port of the step (CuPy / torch) is the only large gain
      left, at the cost of bit-identity (opt-in, its own oracle).
- [ ] hoist the redundant ray rotation in Eye.render (1.07x on the render; batching ten frames is slower).
- [ ] per-ms drive without per-ms Python: Registry.apply is 1.2 %; not worth it now.
- [ ] deterministic mode only for oracles and regression; flyvis is non-deterministic call to call (3e-7).

## 7. situations

- [ ] the pi: laptop as brain, pi + wide-angle webcam as the eye; resample frames onto the
      1,764 columns; real time for the male alone. glass walls.
- [ ] fpga / Loihi 2 note: 30 MB edge table, event-driven; Loihi 2 is the natural fit.
- [ ] the room with three things in it.
- [ ] **the rival** (09-17 17:44, nate): two male brains in the room (two instances of him, different seeds).
      the M-responsive ppk23 channel already bursts on a tap and in life it reads another male's cuticle
      and drives aggression through P1 (Kallman 2015). readouts: P1 rate (low = fight, high = court;
      Hoopfer 2015), the aIPg types, octopamine / serotonin cells, LC10a pursuit, lunges as body events
      (fast approach + contact). needs the tonic floor and a persistent state first (the loser effect is
      a state, hours, on the modulators; nothing in him persists yet). run once, with controls, not on
      loop: if he has states that persist and are bad for him, that is the line we agreed on.
- [ ] flight: DLMn/DVMn in the cord; halteres (silent while walking) come alive; JO wing wash.

## 8. the record

- [ ] approach test table (see 0).
- [ ] `docs/SEAM.md` is 1,400 lines; split by track (eye, behaviour, her, physiology) with
      the STATUS block as the index, once the refactor lands.
- [ ] `results/` index: one line per file saying which section produced it.
