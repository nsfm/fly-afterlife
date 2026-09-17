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
- [ ] **the courtship sequence as a state** (promoted 09-17 13:59): a persistent state (pCd, minutes)
      that holds the brake (AN19A018) at her and drives following; her stop or receptivity (vpoEN);
      P1 threshold-graded (Hoopfer 2015). the song relay (P1 -> pIP10) stays blocked; mAL gate measured.
      --stop-at-her (brake on contact frames) did nothing: contact is too brief and she walks away.
- [ ] walking-state gain on visual channels (Chiappe 2010; Suver 2012).
- [ ] efference copy onto JO-A/B (Cheong 2024); JO wind/gravity; the wing-wash loop when he flies.
- [ ] ocelli: light level; find his OCC/OCG cells (hers are typed, 63).

## 2b. legs with muscles (promoted 09-17 12:30)

- [x] the leg MN SET: 373 leg MNs by subclass fl/ml/hl (12:45; the 699 included abdominal, wing,
      haltere, neck, jump). all leg readouts re-based on it.
- [x] the leg model (12:36): `legs.py`, DNa02's sign reproduced; effector `--effector legs`.
- [x] a walking command (12:56): `--walk 100` (DNp09 tonic); he walks 31 m / 2 min on the true leg set.
      still to do: the command as a state (walk / stop / brake DNs, Sapkal 2024); stance/swing phase
      so MDN reads as backward; the DNp09 right-bias (tracing) as a labelled correction or not.
      the leg model is NOT a wheel (drum 0/3 rectified, 1/3 signed): pace + diagnostic only.

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
