# Karashchuk et al. 2025 — layered 3D kinematic walking model

**Citation.** Karashchuk L, Li JS, Chou GM, Walling-Bell S, Brunton SL, Tuthill JC, Brunton BW (2025). "Sensorimotor delays constrain robust locomotion in a 3D kinematic model of fly walking." *eLife* **13**:RP99005, 15 May 2025. DOI 10.7554/eLife.99005. PMID 40372779. PMC12081000. bioRxiv 10.1101/2024.04.18.589965.
(Same first author as the 2021 Anipose paper, published there as Pierre Karashchuk.)
URL: https://elifesciences.org/articles/99005 · PDF also held locally in the session scratchpad.

## Anatomy framing (useful stated facts)
> "Each fly leg has five joints that move through 7 mechanical degrees of freedom and are actuated by approximately 18 muscles that are innervated by approximately 70 motor neurons."

Joints tracked: **5 keypoints per leg** — body-coxa, coxa-femur, femur-tibia, tibia-tarsus, tarsus tip.
Model joint set (Table 1): front legs — body-coxa flexion, coxa-femur flexion, femur-tibia flexion; middle/hind legs — coxa-femur flexion, femur rotation, femur-tibia flexion, plus coxa rotation.

## Dataset
- Training kinematics from Karashchuk et al. 2021 (Anipose), tracked at **300 Hz**.
- **3,473 walking bouts from 45 flies**; mean bout **0.877 s (263 frames)**; **3,049.7 s / 914,909 frames** of walking total.
- Bout inclusion: ≥0.5 s (150 frames) **and** left-front femur-tibia flexion range **≥30°**.
- Fly size in the images: ~300×300 to 700×500 px.

## Model parameters
- Per-leg optimal controller at **600 Hz**; learned pattern generator at **300 Hz**; Kuramoto phase coordinator for inter-leg coupling.
- Simulated forward speeds: **8, 10, 12 and 14 mm/s**. Data showed a sustained peak roughly **4–10 mm/s**.
- Body mass used: **m = 0.7 × 10⁻⁶ kg (0.7 mg)**; leg radius r = 0.0015 m.
- Perturbations: Poisson process, mean rate 10 Hz; simulations 1,800 timesteps at 600 Hz.
- Signal conditioning: Butterworth bandpass, 3–60 Hz.

## The delay result
- **Sensory delay 5–15 ms** (from mechanosensory measurements); **motor delay 20–40 ms** (motor-neuron spike to muscle force onset).
- The model maintains realistic walking (KS > −1.6) up to about **30 ms motor delay and 10 ms sensory delay** — i.e. the fly operates near the temporal limit at which it can detect and respond to perturbations.
- Model-vs-data angle discrepancy "less than 6 degrees", compared against the markerless tracking uncertainty of **5.56 degrees**.

## Data availability
> "Code is available at https://github.com/lambdaloop/layered-walking/. The data used in this study will be released publicly upon publication and privately by request."

## Could not verify
Per-joint angle ranges in degrees — this paper reports trajectories and phase relationships, not ROM tables. Step frequency in Hz is not stated.
