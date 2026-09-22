# Karashchuk et al. 2021 — Anipose

**Citation.** Karashchuk P, Rupp KL, Dickinson ES, Walling-Bell S, Sanders E, Azim E, Brunton BW, Tuthill JC (2021). "Anipose: a toolkit for robust markerless 3D pose estimation." *Cell Reports* **36**(13):109730. DOI 10.1016/j.celrep.2021.109730.
PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC8498918/

Extraction: automated read of the PMC full text **[V-fetch]**.

## Fly setup
- **Six cameras at 300 Hz** (Basler acA800-510µm, Computar MLM3X-MP zoom lenses), evenly distributed around the fly.
- **1 pixel ≈ 0.0075 mm.**
- **5 keypoints per leg × 6 legs = 30 tracked points** — body-coxa, coxa-femur, femur-tibia, tibia-tarsus joints and the tarsus tip.
- **8 angles per leg = "1 abduction, 3 rotation, 4 flexion."**
- Dataset: **39 flies, 1,480 total seconds of walking.**

## Accuracy
- "More than 90% of poses estimated by Anipose had an error of less than **20 µm** in length and **1 degree** in angle."
- Position error "less than 18 pixels ... in over 90% of frames" (≈0.14 mm).
- The Tuthill lab's later papers quote **5.56°** as the uncertainty of markerless 3D fly joint tracking (Karashchuk et al. 2025 eLife, verified in that paper).

## The kinematic result
> "the middle legs are primarily driven by femur rotation, in contrast to the front and hind legs, which are driven primarily by femur-tibia flexion."
> "[the distribution of] femur-tibia flexion angles is broader for the front and rear legs, whereas the distribution of femur rotation angles is broader for the middle legs."

Estimated physiological femur-rotation range in walking *Drosophila*: **~70°** (an estimate from comparative insect anatomy, not a measurement).

**Note.** Haustein et al. 2024 later showed this midleg "femur rotation" is produced by the two most proximal yaw DOFs (ThCx-yaw + CxTr-yaw), not by a dedicated roll/rotation DOF.

## Could not verify
**Explicit per-joint numeric ROM in degrees.** Figure 7B presents probability distributions with no printed numeric ranges in the text or legend. For numbers, use Haustein et al. 2024.

## Data
Dryad deposit **https://doi.org/10.5061/dryad.nzs7h44s4** — "Fly and mouse tracking models and kinematics related to Anipose toolkit paper", deposited 2021-11-28. Contents: fly 3D joint positions and angles from **39 wild-type Berlin flies**; trained DeepLabCut models; original videos with Anipose tracking.

| File | Size |
|---|---|
| deeplabcut-fly-model.zip | 2.95 GB |
| deeplabcut-mouse-model.zip | 3.03 GB |
| fly-anipose.zip | 8.43 GB |
| **flyangles-dataset.zip** | **4 GB** |
| mouse-anipose.zip | 942 MB |
| README.txt | 5.51 KB |
| total | 19.35 GB |

**Licence: not displayed on the Dryad landing page.** Dryad's default for data is CC0 1.0; the Anipose *toolkit* is CC-BY. **Could not verify the deposit's licence directly.**
