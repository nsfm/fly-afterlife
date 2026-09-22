# Agrawal et al. 2020 — Central processing of leg proprioception in Drosophila

**Citation.** Agrawal S, Dickinson ES, Sustar A, Gurung P, Shepherd D, Truman JW, Tuthill JC (2020).
"Central processing of leg proprioception in *Drosophila*." *eLife* 9:e60299.
DOI **10.7554/eLife.60299**. PMC7752136.
VERIFIED by reading the PMC full text (https://pmc.ncbi.nlm.nih.gov/articles/PMC7752136/).
Data also at Dryad doi:10.5061/dryad.k3j9kd55t and Zenodo record 4307018 (not inspected).

This is the **second-order** layer: what FeCO signals become inside the VNC. Relevant to a body-model
sim mostly as (a) confirmation of what the sensory layer must deliver, (b) the reflexes that close
the loop, (c) the only whole-cell recordings in this literature.

## The three cell types

Found by screening hemilineage-specific split-Gal4 lines for dendrites overlapping FeCO axons.
All three are **prothoracic (T1)** recordings. "Each of the three cell types is comprised of multiple
neurons per VNC segment" — **the paper does not give neuron counts per type** ("we still lack
quantitative data on the numbers of cells or cell types within each hemilineage"). Could not verify
any count.

| Type | Hemilineage | Transmitter | Presumed FeCO input | Encodes | Spikes? |
|---|---|---|---|---|---|
| **13Bα** | 13B | GABAergic | extension-tuned **claw** | tonic femur–tibia **angle** | **no detectable action potentials** |
| **9Aα** | 9A | GABAergic | flexion-tuned **hook** (+ club) | **flexion direction + speed**, and 1600–2000 Hz vibration | **yes**, spikes |
| **10Bα** | 10B | cholinergic | **club** | bidirectional movement + vibration, **position-dependent** | no reliable spikes (occasional spike-like events) |
| **9Aα2** | 9A (distinct type) | — | claw-like | tonic **flexed** positions | yes, **spikes >2 mV**, larger than 9Aα |

### 13Bα — linear position readout
- Membrane potential is "a continuous readout of tibial position": **depolarises on extension,
  hyperpolarises on flexion.** Responses are "remarkably tonic (i.e. non-adapting) at steady state",
  apart from a small transient depolarisation just after extension.
- **Activity increases only when the tibia is extended past ~90°** — matches extension-tuned claw.
- Shows **hysteresis** comparable in magnitude to claw neurons: steady-state Vm at a given angle is
  higher when the angle was reached by extending.
- Pharmacology: TTX abolishes it. MLA (nicotinic antagonist) and atropine (muscarinic) each only
  *subtly* affect it and never abolish it → either gap junctions onto claw axons, or partial block.
  Picrotoxin (GABA_A / GluCl) has **no effect** → no fast inhibitory input; the hyperpolarisation on
  flexion is a **withdrawal of excitation**, confirmed by current-injection driving-force experiments.
- **Reflex: optogenetic activation (CsChrimson, 720 ms) → slow extension of the coxa–femur joint and
  flexion of the femur–tibia joint**, in headless flies both loaded (on ball) and unloaded.
  So: claw→13Bα is a **negative-feedback posture loop on the FT joint** (senses extension, commands
  flexion).

### 9Aα — directional/velocity, heterogeneous
- Every cell responds with both Vm changes and spikes. **Consistent properties: direction and speed
  tuning — subthreshold and spiking activity largest during fast flexing swings.** Peak firing rate
  significantly higher for fast than slow flexion (p<0.005), compared at **720 °/s vs 240 °/s**.
  (Figure 4F plots peak firing rates; **the actual spikes/s values are only in the figure, not the
  text — could not verify a number.**)
- Everything else is heterogeneous cell-to-cell: some inhibited by extension, some excited, some
  tonically depolarised when held flexed. Two 9Aα cells in the *same* fly differ → real cell-type
  diversity, not fly-to-fly variance.
- **Vibration: every 9Aα cell was maximally depolarised by 1600–2000 Hz**, response grows with
  amplitude. Adaptation rate varies across cells (some sustained, some fast-adapting). Since hook
  neurons are vibration-insensitive, this implies convergent **club** input.
- Pharmacology: TTX blocks; **MLA blocks** (so genuinely cholinergic FeCO-driven, unlike 13Bα);
  picrotoxin removes the extension-evoked hyperpolarisation → GABAergic inhibition carries extension.
- **Reflex: activation → small extensions of the tibia–tarsus and femur–tibia joints** (loaded,
  headless). Confirmed with a second split-Gal4 (9Aα-L2-Gal4).
- **Activating 9Aα had no effect on walking velocity** despite its vibration sensitivity.

### 10Bα — vibration + position gating, drives pausing
- Transient depolarisation to extension, flexion and vibration.
- **Position-dependence is the distinctive feature**: the response of a single 10Bα cell to the *same*
  20°-amplitude oscillation differs depending on whether the tibia started extended or flexed; the
  phase of maximal depolarisation shifts (n = 9, p<0.005). Oscillation velocities tested
  **40, …, 320 °/s**.
- Vibration stimulus **0.1 µm**; cells differ in frequency tuning.
- Each 10Bα innervates **multiple VNC segments**, and a subset projects to the brain (**AMMC**).
- **Behaviour: activating 10Bα in walking flies makes them slow or stop after about 200 ms**,
  regardless of stimulus length (tested 0 / 360 / 720 ms). Stopping threshold defined as
  velocity < 0.3 cm/s.
- Interpretation offered: club→10Bα is partly an **exteroceptive** substrate-vibration channel, while
  club→9Aα is proprioceptive. So club output is **not purely proprioceptive** — worth remembering
  before wiring club straight into a body-state estimator.

## Timing / stimulus parameters (VERIFIED)
- Framing constraint quoted in the intro: **"in nimble-footed animals like flies, central circuits may
  have less than 30 ms to process proprioceptive information in between successive steps."**
  This is the number to design sensorimotor latency budgets against.
- 10Bα pausing latency **~200 ms** (behavioural, from stimulus onset).
- Optogenetic stimulus lengths used: 0, 30, 60, 90, 180, 360, 720 ms. Laser 532 nm, pulsed 1200 Hz,
  66 % duty, 87 mW/mm².
- Electrophysiology: whole-cell current clamp, 8–12 MΩ pipettes, low-pass 5 kHz, digitised 20 kHz,
  liquid junction potential **−12 mV**. Calcium imaging at **8.01 Hz**.
- Swing speeds used: 240 °/s (slow) and 720 °/s (fast). Ramp-and-hold as in Mamiya 2018.
- Treadmill ball diameter 9.46 mm; behaviour cameras 300 Hz; ball tracking 30 Hz.

## What I could not verify
- Any absolute firing rate in spikes/s for 9Aα or 9Aα2 (figure-only).
- Neuron counts per cell type (paper explicitly says these are unknown).
- Synaptic latency FeCO→central neuron in ms (not measured here).
