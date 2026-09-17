# TODO

everything pending, in one place. 2026-09-16 23:30 PDT (nyx). the record (`docs/SEAM.md`)
says what was done and why; this says what is not done yet. items reference the physiology
briefs in `docs/physiology/` where a number came from there. rule for every behaviour change:
one change per run, against the previous run, and a large effect from closing one afferent
loop is probably a bug (mechanosensation brief).

## 0. in flight tonight

- [ ] approach test: 10 seeds x {her dark 0.1, her invisible 0.5} x 120 s (`world/approach/`).
      write the table into the record; it decides whether "he turns toward her" is a claim.
- [ ] corrected synapse constants, first minute (`world/pair_w185.npz`): male 0.185, female
      0.275. compare baselines (rest offset, standing leg MN, reflex gain, pace) to the old.

## 1. the refactor (`docs/ARCHITECTURE.md`), before any new receptor

- [ ] oracle runs: current room, `--deterministic`, 30 s, seeds 3 and 4, at old and corrected
      constants (four npz). the ported room must reproduce them bit for bit.
- [ ] `receptors.py`: registry + annotation-table selectors (class / type / entryNerve /
      rootSide / receptorType) + transducer models (Tonic, Adapting, Differentiator,
      WeberFechner, Gait) with citations. port existing drives unchanged. verify.
- [ ] `body.py` + `world.py`: pose, gait generator, six legs, contacts by body part; scene +
      scalar fields (odour, temperature, humidity, airflow, light). verify.
- [ ] `effectors.py`: steering, pace, reflex, song; calibration phases cached by (brain, w_syn,
      seed). verify.
- [ ] `episode.py`: one loop; `per_frame` / `per_chunk` namespaces in the npz; deterministic
      switch; two brains in threads (numba `nogil`). `pair.py` and `loop.py` become thin.
- [ ] `--no-female` default for calibration and male-only questions; her in the room only for
      contact and courtship runs.
- [ ] drive resolved per 1 ms step, not per 10 ms frame (30 ms adaptation kernels need it).

## 2. physiology-driven changes, one per run, in this order

- [ ] **synapse constants** (vision brief): male 0.185 (0.275 / 1.49, Plaza 2025), female
      0.275. re-measure every baseline. reconcile her 0.45 KC-sparsity calibration with the
      22:55 odour test (4.7% at 0.275): different odour protocol, find which was right.
      re-examine MDN's tonic activity (present at 0.275, gone at 0.185) and the reverse-walk rule.
- [ ] **steering baseline**: running per-side DNa02 baseline (~2 s) before differencing
      (Rayshubskiy: zero difference = zero turn). the still/plateau offsets tried were fixed,
      not running. re-test the drum both ways across the ensemble.
- [ ] **DNa02 gain**: 5 deg/s per Hz (bracketed 3-10; ours is 3).
- [ ] **bristles** (mechano brief): 200 Hz onset burst, tau ~30 ms, 10-25 Hz plateau,
      direction-gated (about half a contact patch fires), seconds-scale fatigue. by body part.
- [ ] **leg MNs**: slow MNs fire ~30 Hz standing (Azevedo 2020); force per spike 0.1/1/10 uN
      by class. type MN classes if the annotations allow; weight the pace readout.
- [ ] **campaniform sensilla**: dF/dt, burst at stance onset, adapt out mid-stance, a
      subpopulation on unloading. replaces the 15% tonic load term.
- [ ] **gait**: step frequency from speed (Wosnitza 2013), stance ~ v^-1, swing 20-45 ms,
      period floor 60 ms (16 Hz max, not 10); tetrapod below 5 BL/s, tripod above 10.
- [ ] **hook FeCO gate**: presynaptic inhibition during walking under descending command
      (Dallmann 2025); apply at the drive (Poisson receptors ignore their membrane). claw,
      club, hair plates ungated.
- [ ] **cooling cells**: ~95 Hz rest regardless of T, fire to -dT/dt only, peak 0.65 s, adapt
      (Budelli 2019). **hot cells**: tonic, exponential in T (37 Hz at 25 C, Q10 4.4). the
      posterior antennal lobe has been missing a 95 Hz tonic input in every run.
- [ ] **VP1m / VP1l label audit** before driving either (Marin 2020: VP1m humid, VP1l cool).
- [ ] **the warm corner**: a temperature field in the room; thermotaxis readout.
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
- [ ] **pCd persistence** readout; P1 threshold-graded (aggression low, song high; Hoopfer 2015).
      the song relay (P1 -> pIP10) stays blocked in this LIF; mAL gate measured.
- [ ] walking-state gain on visual channels (Chiappe 2010; Suver 2012).
- [ ] efference copy onto JO-A/B (Cheong 2024); JO wind/gravity; the wing-wash loop when he flies.
- [ ] ocelli: light level; find his OCC/OCG cells (hers are typed, 63).

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

## 6. performance

- [ ] two brains in threads (numba nogil); then a profile.
- [ ] per-ms drive without per-ms Python (vectorise transducers over cells).
- [ ] deterministic mode only for oracles and regression; it is 40% slower.

## 7. situations

- [ ] the pi: laptop as brain, pi + wide-angle webcam as the eye; resample frames onto the
      1,764 columns; real time for the male alone. glass walls.
- [ ] fpga / Loihi 2 note: 30 MB edge table, event-driven; Loihi 2 is the natural fit.
- [ ] the room with three things in it.
- [ ] flight: DLMn/DVMn in the cord; halteres (silent while walking) come alive; JO wing wash.

## 8. the record

- [ ] approach test table (see 0).
- [ ] `docs/SEAM.md` is 1,400 lines; split by track (eye, behaviour, her, physiology) with
      the STATUS block as the index, once the refactor lands.
- [ ] `results/` index: one line per file saying which section produced it.
