# Mamiya, Gurung & Tuthill 2018 — Neural coding of leg proprioception in Drosophila

**Citation.** Mamiya A, Gurung P, Tuthill JC (2018). "Neural Coding of Leg Proprioception in Drosophila."
*Neuron* 100(3):636–650.e6. DOI **10.1016/j.neuron.2018.09.009**. PMID 30293823.
VERIFIED by reading the full in-press PDF (faculty.washington.edu/tuthill/docs/mamiya_2018.pdf),
which paginates as "Neuron 100, 1–15" — page range 636–650 taken from PubMed metadata (second-hand).

Method: in vivo 2-photon GCaMP6f calcium imaging of FeCO axons in the prothoracic (T1) leg neuropil
of the VNC, with a servo/magnet system moving a pin glued to the right front tibia. **All physiology
is calcium imaging, not spikes.** No spike rates for FeCO neurons are reported anywhere in this paper.

## Counts (VERIFIED, direct quotes)

| Quantity | Value | Note |
|---|---|---|
| FeCO cell bodies per leg | **135** | "a femoral chordotonal organ (FeCO) that contains 135 cell bodies" |
| FeCO axons projecting directly to brain | **3–4 cells per leg** | rest arborize in VNC neuropil; cites Tsubouchi et al. 2017 |
| `iav-Gal4` coverage | **~80%** of the 135 | previously assumed to be all FeCO neurons; it is not |
| claw (`R73D10-Gal4`) | **20 cell bodies** | blade-shaped strip along long axis of femur |
| club (`R64C04-Gal4`) | **30 neurons** | two clusters at proximal part of FeCO |
| hook (`R21D12-Gal4`) | **3 neurons** | along FeCO ventral edge; flexion-selective only |
| Johnston's organ, for scale | 500 vs 135 | "The JO is also much larger (500 versus 135 neurons)" |

Caveat the paper states itself: "these three Gal4 lines label less than half of the total FeCO neuron
population". So 20/30/3 are **driver-line counts, not subclass sizes.** The extension-selective hook
population exists (seen in population imaging, orange cluster) but **no Gal4 line was found for it.**
Use Mamiya 2023 (152 cells, X-ray) for anatomical totals.

## Functional subclasses (VERIFIED)

Five basic response subclasses in population imaging with `iav-Gal4`: **2 tonic (non-adapting) +
3 phasic (adapting)**.

Direction selectivity index (DSI), mean ± SEM, population imaging (`iav-Gal4`):
- bidirectional phasic (club-like): **DSI = 0.222 ± 0.027**, n = 29 clusters / 22 flies
- flexion-selective phasic (hook-like): **DSI = 0.494 ± 0.039**, n = 19 clusters / 17 flies
- extension-selective phasic: **DSI = 0.493 ± 0.036**, n = 29 clusters / 22 flies

DSI with subclass-specific drivers (cleaner, less contamination):
- club `R64C04`: **DSI = 0.117 ± 0.022**, n = 25 regions / 15 flies
- hook `R21D12`: **DSI = 0.811 ± 0.028**, n = 37 regions / 23 flies
- single club neurons: **DSI = 0.179 ± 0.042**, n = 13 cells / 9 flies

### claw = tonic femur–tibia ANGLE
- Each claw axon branch (X, Y, Z) splits into a flexion-encoding and an extension-encoding sub-branch.
  A single claw neuron innervates **all three** branches (n = 3 traced cells / 3 flies), so X/Y/Z all
  encode the same stimulus — the tri-partite arborization is not a coordinate system.
- Population tuning: **extension-tuned pixels active 90°–180°; flexion-tuned pixels active 90°–18°.
  Neither group active near 90°.** Activity increases "as a relatively linear function of the
  femur–tibia joint angle".
- **Hysteresis** (this matters for any decoder): flexion-activated branch has larger steady-state
  activity at a given angle (0°–90°) when arriving by flexion than by extension; extension-activated
  branch larger over 90°–180° when arriving by extension. Peak hysteresis magnitude ≈ ±0.2–0.4
  normalized units (Fig 5E; read off the figure, **not** a quoted number — treat as approximate).
  No directional hysteresis in club or hook.
- **Single claw neurons are narrowly tuned to specific angles** (range fractionation): one cell peaked
  at **70°**, another at the most flexed position **20°** (n = 5 cells / 5 flies). Each single cell
  responds to flexion **or** extension, never both.
- No single claw neuron tuned near 90° was found in this (small) sample.

### hook = directional movement
- Phasic, flexion-only for `R21D12` (DSI 0.811). Responses decay rapidly; **never tonic during hold.**
- Slightly weaker at fully extended positions.
- **Velocity:** slope of calcium signal was "similar across the entire speed range tested"
  (100–800 °/s) → hook is comparatively velocity-independent over that range.
- Does **not** respond to vibration (100–2000 Hz, 0.9 / 0.054 µm).

### club = bidirectional movement + vibration
- Phasic to both flexion and extension; responses "slightly larger around 90° and smaller at full
  extension (180°)".
- **Velocity:** calcium-signal slope **peaks around 400 °/s** and decays slightly at higher speeds
  (tested 100–800 °/s).
- **Vibration:** sinusoidal tibia vibration, peak-to-peak amplitude **0.9 µm or 0.054 µm**, frequencies
  **100–2000 Hz**. Club responded significantly at *all* frequencies tested.
  - **0.9 µm amplitude → peak at 400 Hz**
  - **0.054 µm amplitude → peak at 800 Hz**
  - Claw and hook did not respond to vibration at all.
- **Tonotopic map in club axon terminals**: response centre-of-mass shifts anterolateral →
  posteromedial as frequency increases, consistent across flies and both amplitudes.
- **Single club neurons are narrowly frequency-tuned**: one cell peaked at **200 Hz**, another at
  **1600 Hz** (n = 12 cells / 7 flies for vibration). Where two club axons were labelled in one leg,
  the more posterior axon was tuned lower.
- 2000 Hz was the upper limit because the piezo stimulus amplitude fell off sharply above ~2000 Hz —
  i.e. **the 2 kHz ceiling is an apparatus limit, not a biological one.**
- Behavioural relevance claimed: male courtship abdominal vibrations are 200–2000 Hz
  (cited as "C. Fabre, personal communication" — **unpublished, do not treat as a hard number**).

## Stimulus / kinematics parameters (VERIFIED, useful for driving a sim)

- Joint range used: **18° (flexed) to 180° (extended)**; couldn't go below 18° (pin hit abdomen).
- Swing stimulus: **360 °/s**; velocity series also at **180, 720, 1440 °/s**.
- Ramp-and-hold: **18° steps at 240 °/s**, **3 s hold** between ramps, motor acceleration **72,000 °/s²**.
- Imaging rate **8.01 Hz** (256×120 or 128×240 px) — so the temporal resolution of all this data is
  ~125 ms. **Do not read fast dynamics out of this paper.**
- Leg-tracking camera at 180 Hz (ramp-hold) / 200 Hz (swing); 4000 Hz for piezo calibration.
- Repeat-adaptation across 3 stimulus repeats was small: ratio of 2nd/1st response ≈ **0.89–1.18**
  depending on subclass (full table in methods) — i.e. **little run-down; ~±10%.**

## Natural-kinematics statements (VERIFIED as claims in this paper; several are *unpublished*)

- "When a fly is standing still, the tibia of the front leg rests ~90° relative to the femur; during
  straight walking, the tibia flexes to 40° and extends to 120°" — cited as **(unpublished data)**.
  → predicted consequence: **claw neurons are largely silent in a stationary fly.**
- Foreleg swing duration **~25–45 ms**, stance duration **~30–140 ms** (Mendes et al. 2013;
  Wosnitza et al. 2013) — second-hand via this paper.
- Maximum femur–tibia excursion in tethered walking Drosophila **~80°** (their unpublished obs);
  cockroach mesothoracic leg ~60° (Watson & Ritzmann 1998).
- Derived max average joint speed: **2400–3200 °/s swing, ~2000–2670 °/s stance.** This is a
  back-of-envelope derivation in the methods (excursion/duration), **not a measurement.**
  Contrast: cockroach measured mean joint angular velocity **0–800 °/s** (Watson & Ritzmann 1998).
  The two disagree by ~3×; prefer measured Drosophila kinematics (e.g. Karashchuk/DeepLabCut work)
  over this derivation when driving a sim.

## Other

- FeCO neurons are **cholinergic** (stated here; used by Agrawal 2020).
- No efferent/centrifugal innervation of the FeCO is discussed here; Mamiya 2023 explicitly looked and
  found none.
