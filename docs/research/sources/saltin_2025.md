# Saltin et al 2025 — parametric FE model of Drosophila leg campaniform sensilla

**Citation.** Saltin BD, Goldsmith CA, Haustein M, Büschges A, Szczecinski NS, Blanke A
(2025). "A parametric finite element model of leg campaniform sensilla in *Drosophila* to
study campaniform sensilla location and arrangement." *Journal of the Royal Society
Interface* **22**(226):20240559. DOI 10.1098/rsif.2024.0559. PMC12056673 (not open in
Europe PMC). bioRxiv preprint: 10.1101/2023.07.24.550300.
**Dataset (COMSOL 5.6 model files, CAD geometry of the leg and sensilla, MATLAB code, raw
data): https://zenodo.org/records/14870197** ← the authoritative source; re-verify numbers
against it.

Citation and existence verified. **Content below is from a page-reading pass of the bioRxiv
full text, not from text I extracted myself — treat all numbers as second-hand.**

## What it is

A **parametric finite element model of the femoral CS field on the *Drosophila* hind leg**,
with **12 general parameters for the CS field** and **7 CS-specific parameters per
sensillum**. Driven with real kinematics plus ground reaction forces to simulate forward
stepping, to ask what CS placement and arrangement buy the animal.

## Reported numbers (second-hand)

- Femur length **720.68 µm**, from SEM triangulation; morphology sampled at 20 points, each
  measured 10×.
- Sensillum sub-elements modelled: cap, upper collar, lower collar, middle part, dome with
  attached nerve.
- Loading: **1/3 of 8.963 × 10⁻⁶ N** (≈ 2.99 µN, a third of body weight), applied in
  **7.5° increments** about the Y and Z axes; stance-phase force direction spans azimuth
  **5.31°–19.66°** and elevation **144.58°–65.57°**.
- Material: **linear elastic**, Young's modulus from Skordos (2002); anisotropy and
  viscosity omitted "due to lack of reliable experimental data".
- Main result: displacements at the CS field near the **trochanter-femur joint are small**,
  and material-property changes have little influence.

## The gap it leaves

The paper states outright that there is **no strain → spike mapping**:
"it remains unknown at which displacement/stress levels CS ... are activated."

So this gives a mechanical front end (leg loading → per-sensillum cap strain, with
directional selectivity from the cap's elliptical orientation) but **no transducer**.
Pair with Szczecinski et al. 2021 for the transducer, using cap strain (or a scalar
projection of it) as the `u` in `y = max(0, a(u−x) + cu + d)`.

## Related, same group, on the strain front end

- Dinges GF, Zyhowski WP, Lucci A, Friend J, Szczecinski NS (2024). "Mechanical modeling of
  mechanosensitive insect strain sensors as a tool to investigate exoskeletal interfaces."
  *Bioinspir. Biomim.* **19**. DOI 10.1088/1748-3190/ad1db9.
- Dinges GF, Kudyba IM, Szczecinski NS (2026). "Resin models of *Drosophila* strain sensors
  highlight **mechanical pre-filtering** of sensory inputs." *Bioinspir. Biomim.*
  DOI 10.1088/1748-3190/ae5e11. — i.e. the cuticle around the cap does part of the filtering
  before transduction.
