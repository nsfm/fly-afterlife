# Azevedo, Dickinson, Gurung, Venkatasubramanian, Mann & Tuthill (2020)
**"A size principle for recruitment of Drosophila leg motor neurons."** *eLife* 9:e56754.
DOI: 10.7554/eLife.56754 (verified from article page). PMID 32490810.
Preprint: bioRxiv 730218 ("A size principle for leg motor control in Drosophila").
Source data: Dryad doi:10.5061/dryad.76hdr7stb ; Zenodo record 4552511.

Read directly from https://elifesciences.org/articles/56754 (full text + figure captions)
and by pixel-digitising the figure images from https://iiif.elifesciences.org/lax/56754%2F...
All items below marked **[V-text]** = verified by reading the paper's own words,
**[V-fig]** = verified by measuring the published figure image, **[calc]** = my arithmetic on their numbers.

## System
- Fly leg: **14 muscles, 53 motor neurons per leg** [V-text] (their citation: Baek & Mann 2009;
  Brierley et al. 2012; Maniates-Selvin et al. 2020; Soler et al. 2004).
- Tibia flexor pool: **~15 MNs** [V-text, Discussion "Organization of motor pools"].
  - **fast** = 1 unique MN (R81A07-Gal4), embryonically born, only MN innervating the large
    mid-femur flexor fibers.
  - **intermediate** = R22A08-Gal4, one of **2-5** MNs innervating proximal femur fibers.
  - **slow** = R35C09-Gal4, one of **8-9** MNs innervating distal femur fibers ("reductor" region);
    among the weakest of that group.
- Comparison they draw: locust metathoracic tibia flexor = **9 MNs**, also split fast/intermediate/slow
  (Burrows & Hoyle 1973; Phillips 1981; Sasaki & Burrows 1998) [V-text]. NOT a Drosophila number.
- Drosophila (holometabolous) leg muscles have **no inhibitory (GABAergic) motor neurons** [V-text].
- Polyneural innervation: a fiber may be innervated by >1 MN, so motor units overlap [V-text].

## Force probe (the measuring instrument - needed to interpret every twitch number)
- Spring constant **k = 0.2234 µN/µm** (= 0.2234 N/m) [V-text, Methods + Fig1-S2A].
- Effective mass **m = 0.1702 mg**, drag **c = 0.1377e-3 kg/s** (text says "0.1377 kg/s",
  Fig1-S2B caption says "c = 0.14E-3 kg/s" - the figure caption value is the credible one) [V-text].
- Probe slightly underdamped: **relaxation tau = 2.5 ms, oscillation period 5.8 ms** [V-text].
  => Probe dynamics are FAST relative to the twitch (~20 ms) - twitch shape is muscle, not probe.
- Lever arm (probe tip to F-Ti joint) **417 ± 7 µm s.d., n = 8 flies** [V-text].
- Angle conversion: **60 µm probe travel = 8° F-Ti angle**; also -150 µm = -21°, 75 µm = 10°.
  => **~7.2-7.5 µm probe displacement per degree** [V-text, calc].
- Video 170 Hz; 1 px = 1.03 µm.

## Whole-joint force capacity
- Probe moved up to **400 µm**, i.e. **~90-100 µN at the tibia tip**; peak speeds **8 mm/s**;
  force rates **~1.3 mN/s** [V-text].
- "F ~ 85 µN" is the saturation hotspot in the Fig 1F 2-D histogram [V-text].
- **Fly mass ~1 mg, weight ~10 µN** [V-text]. So the F-Ti joint can pull ~10x body weight.
- For comparison they cite take-off peak leg force **~100 µN** (Zumstein et al. 2004) [V-text, second-hand].

## Intrinsic properties (Fig 3; fast n=15, intermediate n=11, slow n=14; measured while fly still)
| | fast | intermediate | slow |
|---|---|---|---|
| resting Vm (mean, text) | **-68 mV** | **-60 mV** | **-48 mV** |
| Vm spread (Fig 3C) [V-fig] | -63..-73 (cluster ~-67) | -65..-56 (+1 outlier at -41) | -37..-59, cluster -45..-55 |
| spontaneous rate (text) | 0 (silent) | 0 (silent) | **~30 Hz** |
| spont. rate spread (Fig 3D) [V-fig] | all at 0 | all at 0 | 10-52 Hz, cluster 22-30 |
| input resistance (text) | **150 MΩ** | **300 MΩ** | **700 MΩ** |
| Rin spread (Fig 3E) [V-fig] | ~80-190 MΩ | ~190-440 MΩ | ~420-900 MΩ |
- Vm corrected for a **-13 mV liquid junction potential** [V-text, Fig 2D caption].
- Rin measured from **-5 pA** hyperpolarising steps before each trial [V-text]; Fig 3B example traces use -40 pA.
- **Somatic current injection does NOT reliably evoke spikes in fast or intermediate MNs**
  (soma electrically isolated from spike initiation zone; they cite Sasaki & Burrows 1998).
  Only the slow MN's rate is controllable from the soma. [V-text] -> this is why they used
  optogenetics (Chrimson) for fast/intermediate and current injection for slow.
  **No spike-threshold current is reportable for fast/intermediate.**
- Anatomical gradient (Fig 3A): soma, primary neurite and axon diameters all fast > intermediate > slow
  (p<0.01). No absolute diameters given in the caption.
- Other flexor MNs sampled (Fig 4-S1) [V-fig/caption]: R81A06 cell at -67 mV; another at -55 mV, no
  spontaneous spiking; another at -53 mV with **12 Hz** spontaneous; R81A04 cell at -51 mV,
  **28 Hz** spontaneous, **Rin 486 MΩ**.

## Force per spike (Fig 4)
- **fast: ~10 µN per spike, 50 µm probe displacement** [V-text]. Fig 4A caption states "50 µm = 11 µN".
- **intermediate: ~1 µN per spike, 5 µm displacement** [V-text]. Fig 4C caption "5 µm = 1.1 µN".
- **slow: <0.1 µN per spike**; linear fit slope **m = 0.013 µN/spike** [V-fig, printed on Fig 4D].
- Fig 4D per-cell spread [V-fig]: fast 1-spike force **~5-16 µN**, saturating at **~20-30 µN**;
  intermediate 1-spike **~0.25-0.7 µN**, saturating **~1.5-3 µN**; x-axis is #spikes, log 1-60.
- **Sublinear summation: 2 spikes give ~1.6x the force of 1 spike** (fast and intermediate) [V-text, Fig 4E].
- **Force-per-spike curves saturate at ~10 spikes** for fast and intermediate; they attribute this to
  fatigue of the fast/intermediate fibers [V-text]. **This is the closest thing in the paper to a
  tetanic-fusion measurement - they did NOT do a frequency-fusion series.** No fusion frequency is
  reported anywhere in the paper. [verified absent]
- Slow MN: spontaneous rate maintains a steady resting force. **1 µM MLA** (nAChR antagonist) cut the
  spontaneous rate and reduced resting probe force by **~1.5 µN (~15% of body weight)** [V-text].
- Hyperpolarising the slow MN lets the tibia extend (fly "lets go"), max effect in **~100 ms** [V-text].
- Fig 4C: slow MN driven with **+25 / +50 / +100 pA** produced 100-150 spikes/s and only
  **~1 µm** (control) up to ~10 µm probe movement, building over **>500 ms without reaching peak** [V-text/V-fig].

## TWITCH TIME COURSE (the key numbers for a twitch kernel)
- Paper text: "the effect of a spike in the fast and intermediate motor neurons reached
  **half maximal force in ~8.5 ms**" [V-text].
- Fig 4H (T½, ms), per cell [V-fig]: **fast n=7: 7.7-9.7 ms (cluster 8.0-8.7, mean ~8.2)**;
  **intermediate n=6: 6.3-8.9 ms (mean ~7.7)**. Not significantly different (p=0.2, rank sum).
- Fig 4G conduction delay soma-spike -> EMG spike: **~0.6-1.0 ms** (n=5 intermediate; axis is
  mislabelled "Conduction (µs)", the values are certainly ms) [V-fig]. fast vs intermediate p=0.6.
- Fig 4I max tibia velocity from a single spike [V-fig]: **fast 2.0-8.5 mm/s (median ~4)**,
  **intermediate ~0.2-0.8 mm/s**, p=0.0012.

### Digitised single-spike twitch, fast MN (Fig 4A example cell) [V-fig, my pixel digitisation]
Calibration used: 20 ms scale bar = 71 px; 50 µm scale bar = 124 px; t=0 at the grey spike-onset line.
| t after somatic spike | probe displacement |
|---|---|
| ~2 ms | movement onset |
| 4.9 ms | 13 µm |
| 9.2 ms | 31 µm (≈ half-peak; matches their 8.5 ms T½) |
| 13.4 ms | 47 µm |
| 21.3 ms | **58.5 µm = peak** (≈13 µN at k=0.2234) |
| 28.9 ms | 52 µm |
| 35.9 ms | 37 µm |
| 38.7 ms | 29 µm (≈ half-decay) |
| 50.0 ms | 14 µm |
Derived: **time-to-peak ≈ 21 ms**, **half-decay ≈ 17.5 ms after peak (≈39 ms after spike)**,
decay to 25% ≈ 28 ms after peak, **single-exponential decay tau ≈ 20 ms** [calc from the digitised points].
Caveat: this is ONE example cell in a figure, digitised by me, not a number the authors state.

### Digitised single-spike twitch, intermediate MN (Fig 4B example cell, ~30 overlaid trials) [V-fig]
Calibration: 20 ms = 70 px; 5 µm = 56 px.
peak **~4.3 µm (≈1 µN) at ~21 ms**; half-rise ~10-11 ms; half-decay ~16 ms after peak;
back to baseline by **~55-60 ms**. Same ballpark as fast: **rise ~8-10 ms, decay tau ~15-20 ms**.

### Slow MN
No twitch resolvable. Force builds **gradually and does not peak within 500 ms** [V-text].
Treat the slow unit as a near-tonic, low-pass element, not a twitch generator.

## Firing rates actually measured
- Spontaneous, fly at rest: fast 0, intermediate 0, slow ~30 Hz [V-text, Fig 3D].
- **Fig 5-figure supplement 1A**, average ("effective") spike rate over ALL spontaneous-leg-movement
  trials [V-fig]: **fast ≈ 1.5 spikes/s, intermediate ≈ 9-10 spikes/s, slow ≈ 62 spikes/s**.
  Caption explicitly warns "instantaneous spike rates could be much higher".
- Slow MN during current injection reached **100-150 spikes/s** (Fig 4C) [V-fig].
- **The paper does NOT break firing rate down by standing / grooming / walking / flailing.**
  Flies were categorised as Stationary / Walking-turning / Grooming / Other only in the
  *optogenetic behaviour* experiments (no electrophysiology there). [verified absent]

## Recruitment
- Order **slow -> intermediate -> fast**, by *sequential recruitment of additional MNs*, and each
  new MN adds ~an order of magnitude more force. Three orders of magnitude spanned by the pool [V-text].
- Paired recordings (Fig 5G): a neuron lower in the hierarchy is already firing before the
  higher one spikes. Only **110/3082** intermediate EMG spikes were NOT preceded by a slow spike
  [V-fig, Fig 5-S1C].
- Violations occur only during rapid unloaded leg shaking/waving, where the slow MN appears to be
  actively inhibited (compare cat paw-shake, zebrafish escape) [V-text, Fig 5-S1D].
- Comparison window used throughout: probe force/velocity in the **25 ms following a spike**.

## Proprioceptive feedback (Fig 6) - relevant if you close a reflex loop
- Passive tibia **extension** -> EPSP in all three flexor MNs (resistance reflex). PSP amplitude
  slow > intermediate > fast [V-text].
- Slow MN firing rate is modulated by a **1° (and even 0.8°, 6 µm) tibia movement** [V-text, Fig 6F].
- Fast MNs: never observed a feedback-evoked spike. Intermediate: only ballistic stimuli evoke one [V-text].
- FeCO has **~150 mechanosensory neurons** (their cite: Mamiya et al. 2018) [V-text].
- Ramp stimuli: 60 µm (8°) at up to **123°/s**; reflex reversal seen occasionally.

## Driver lines / optogenetics
- **R81A07-Gal4** = fast tibia flexor MN. **R22A08-Gal4** = intermediate. **R35C09-Gal4** = slow.
- Also sampled: R81A06-Gal4, R81A04-Gal4 (other flexor MNs, Fig 4-S1).
- Muscle imaging: **MHC-LexA; 20XLexAop-GFP**, **MHC-Gal4; UAS-GCaMP6f**. Imaging at 50-60 Hz.
- Optogenetics: CsChrimson with 81A07; Chrimson88 with 22A08 (CsChrimson in 22A08 was toxic-ish:
  prevented wing straightening, bent front legs). 625 nm LED, 10-20 ms flashes (Fig 4A used 50 ms,
  ~2 mW/mm²). Behaviour: 532 nm laser, 1200 Hz pulsed 66% duty, **87 mW/mm²**, 90 ms or 720 ms.
  Silencing: gtACR1. Control: BDP-Gal4 / empty-Gal4. Pan-MN: OK371-Gal4.
- Calcium imaging clusters: k-means on pixel correlation; **Flexor 1 = fast MN unit**,
  **Flexor 2 = intermediate unit** (confirmed by simultaneous EMG). Flexor 1 recruited only for the
  fastest/most powerful movements; highest force+velocity only when Flexors 1 AND 2 co-active [V-text].
- Behaviour result: activating fast MN -> persistent flexion, walking interrupted; activating
  intermediate -> flies speed up / start walking; activating slow -> fly extends the tibia and stops.
  Silencing all MNs (OK371>gtACR1) -> paralysis.

## What is NOT in this paper (checked)
- No tetanic fusion frequency, no force-frequency curve, no explicit twitch tau, no fitted kernel.
- No force-length or force-velocity curve.
- No passive joint stiffness / damping / restoring torque for the F-Ti joint.
  (The only spring constant in the paper is the *measuring probe's*, 0.2234 µN/µm.)
- No firing rates split by behaviour class.

## Citation verification log (Crossref API, checked this session)
- Azevedo et al. 2020, eLife 9:e56754 — doi:10.7554/eLife.56754, published 2020-06-03. VERIFIED.
- Azevedo et al. 2024, Nature **631**:360-368, doi:10.1038/s41586-024-07389-x, 2024-07-11. VERIFIED.
- Lesser et al. 2024, Nature **631**:369-377, doi:10.1038/s41586-024-07600-z, 2024-07-11. VERIFIED.
- Vaxenburg et al. 2025, Nature **643**:1312-1320, doi:10.1038/s41586-025-09029-4, 2025-07-31. VERIFIED.
- Lobato-Rios et al. 2022, Nat Methods **19**:620-627, doi:10.1038/s41592-022-01466-7, 2022-05. VERIFIED.
- Wang-Chen et al. 2024, Nat Methods **21**:2353-2362, doi:10.1038/s41592-024-02497-y, 2024-12. VERIFIED.
- Bidaye, Bockemühl & Büschges 2018, J Neurophysiol **119**:459-475, doi:10.1152/jn.00658.2017.
  Citation VERIFIED via Europe PMC; **full text NOT accessible, no numbers extracted.**
