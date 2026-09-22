# Özdil PG, Ning C, Phelps JS, Wang-Chen S, Elisha G, Blanke A, Ijspeert A, Ramdya P (2025)
**"Musculoskeletal simulation of limb movement biomechanics in Drosophila melanogaster."**
arXiv:2509.06426 [q-bio.NC], v1 8 Sep 2025, v2 11 Sep 2025. doi:10.48550/arXiv.2509.06426.
23 pages, 11 figures. (Preprint - check for a journal version before citing as peer-reviewed.)

**This is the answer to "does a Hill-type muscle model fitted to Drosophila leg data exist?" -
yes, this one, and it is the first.** Read: arXiv HTML full text + the shipped MuJoCo model
(`flygym/src/flygym/assets/model/musculoskeletal/best_combined_arm_damping_stiff_cvt3.xml`
in https://github.com/NeLy-EPFL/flygym).

## What it is
- First 3D data-driven musculoskeletal model of *Drosophila* legs, in **both OpenSim and MuJoCo**.
- Muscle geometry from **high-resolution X-ray (synchrotron) scans of multiple fixed specimens**.
- **15 muscle-tendon units (MTUs) per front leg** (plus 7 per midleg, 8 per hindleg, anatomy only).
- Built on top of NeuroMechFly; foreleg meshes replaced with the X-ray-derived ones.
- Verbatim on the system: *"Each fly leg is a multi-jointed appendage with at least seven DoFs across
  five joints. These joints are actuated by approximately 19 muscles, which in turn are controlled by
  approximately 69 motor neurons."* (their refs: Azevedo 2024, Lesser 2024, Soler 2004)
- Claim their analysis suggests the **coxa-trochanter joint may have 3 DoFs, not 2**.

## The muscle model
Hill-type after Geijtenbeek 2013 / Lee 2018: CE + PE + SE, buffer elasticity omitted,
**rigid tendon assumed, pennation angle set to zero** and F_max rescaled accordingly.
`F_MT = (F_CE + F_PE + F_damper) cos(alpha) = F_SE` ; `F_CE = a(t) F_max f_l(l_CE) f_v(v_CE)`.
PE only active during elongation. In OpenSim they use the **Millard 2013** muscle.

**Crucially: no *Drosophila* force-length or force-velocity curves exist, so they used OpenSim's
default (mammalian) curves.** Verbatim: *"Due to the lack of measured Drosophila muscle curves,
default curves in OpenSim were assumed to approximate real physiological behavior."*

Parameter provenance (their §A.5):
- **Max isometric force = (fixed base tension from prior experimental work) x (optimised scale 0.3-3)
  x PCSA from CT scans.** The base-tension source is not named in the arXiv text I could read.
- **Max contraction velocity** = base value estimated from femur-tibia motion videos under X-ray,
  x optimised factor 0.4-2.4.
- Optimal fibre length and tendon slack length from CT ratios, x 0.8-1.2, capped at 95% of total.
- Muscle paths allowed to move within a 5-10 µm cube around annotated insertions.
- Fitted with **NSGA-II** against measured 3D kinematics (walking + antennal grooming) using an
  OpenSim static-optimisation / forward-dynamics pipeline.
- **Activation and deactivation time constants were FIXED, not optimised** (their Table 2). The
  numeric values are not given in the arXiv text.

## Actual numbers from the shipped MuJoCo model (left front leg, 15 MTUs)
Units: `<option gravity="0 0 -9801">` with mesh `scale="1000"` => length in **mm**, time in s,
and the masses imply **g**, so 1 model force unit = 1 g·mm/s² = **1 µN**, and
1 torque unit = 1 g·mm²/s² = **1 nN·m**. (Caveat: summing all `mass` attributes gives 2.49 mg,
which is ~2.5x a real fly, so treat the absolute force scale as uncertain.)

MuJoCo muscle `gainprm = (range0, range1, force, scale, lmin, lmax, vmax, fpmax, fvmax)`:

| MTU (left front leg) | F_max (model units ≈ µN) | operating range (L0) | fpmax | lengthrange (mm) |
|---|---|---|---|---|
| C tergopleural promotor a | 14.2 | 0.775-1.391 | 0.359 | 0.158-0.214 |
| C tergopleural promotor b | 67.8 | 0.945-1.015 | 4.083 | 0.340-0.362 |
| C pleural remotor & abductor | 28.7 | 0.743-1.720 | 0.353 | 0.216-0.300 |
| C pleural promotor | 30.6 | 0.859-1.596 | 0.283 | 0.091-0.136 |
| C sternal anterior rotator | 10.6 | 0.185-1.734 | 3.113 | 0.126-0.203 |
| C sternal posterior rotator | 157.4 | 0.611-1.408 | 0.075 | 0.072-0.147 |
| C sternal adductor | 12.9 | 0.244-1.487 | 0.447 | 0.097-0.260 |
| F trochanter flexor b | 78.0 | 0.537-1.046 | 2.852 | 0.273-0.326 |
| F sterno-tergo-trochanter extensor a | 159.2 | 0.728-1.507 | 0.240 | 0.281-0.338 |
| F sterno-tergo-trochanter extensor b | 124.3 | 0.848-1.434 | 0.099 | 0.240-0.320 |
| F accessory trochanter flexor | 24.9 | 0.639-1.514 | 0.210 | 0.203-0.263 |
| F trochanter extensor | 40.6 | 0.902-1.193 | 0.707 | 0.091-0.128 |
| F trochanter flexor a | 46.8 | 0.831-1.588 | 0.508 | 0.342-0.413 |
| **tibia flexor** (`LFTibia_flex_93434`) | **68.1** | 0.958-1.041 | 3.232 | 0.469-0.495 |
| **tibia extensor** (`LFTibia_extensor_93932`) | **303.9** | 0.907-1.525 | 0.183 | 0.533-0.587 |
All MTUs share `vmax = 10` (optimal-lengths per second) and `fvmax = 1.4`.

**Activation dynamics in the shipped file:** every MTU overrides the class default with
`dynprm="0.0001 0.0004 ..."`, i.e. **tau_act = 0.1 ms, tau_deact = 0.4 ms**. The `muscle` default
class in the same file carries MuJoCo's own default `dynprm="0.01 0.04"` = 10 ms / 40 ms.
The 0.1/0.4 ms values are ~100x faster than any measured fly muscle activation and ~85x faster than
Azevedo's 8.5 ms twitch half-rise. Flag as suspect if reused.

**Passive joint properties in the same file** (`<default class="main"><joint ...>`):
`armature="0.0005"` (g·mm² = 5e-13 kg·m²), **`stiffness="0.4"` (nN·m/rad)**,
**`damping="0.02"` (nN·m·s/rad = 2e-11 N·m·s/rad)**. Every leg joint also carries a `springref`
(rest angle), e.g. `joint_LFTibia_pitch range="0.4789 2.502" springref="2"`.
The filename `best_combined_arm_damping_stiff_cvt3` = their best condition (iii)
"armature + damping + stiffness". **These are tuned model values, not measurements** - the paper's
own framing is that they *tested* stiffness/damping as a learning aid, finding that
"the combination of stiffness and damping yields the fastest learning and the highest performance".

## Result headlines
- Static optimisation over measured walking and grooming kinematics -> predicted muscle activations;
  **NMF gives 3 muscle synergies explaining >90% of variance** (first alone >80%).
- Pleural remotor abductor (Pra) active at stance onset; tergopleural/pleural promotor at
  stance->swing. Trochanter flexor and extensor co-active in grooming, antiphase in locomotion.
- PPO imitation learning in MuJoCo at 500 Hz control / 10 kHz physics; ~96 h to train a 7-DoF,
  15-MTU leg.

## Honest limitations (their own words)
> "key properties such as the maximum isometric forces and contraction velocities were not directly
> measured but instead were estimated and optimized using a combination of anatomical and
> physiological data."
Also: no contact forces from body-body / body-environment interactions.

## What this does NOT give you
- No link to motor neurons: the policy outputs a continuous activation in [0,1] per muscle, which
  they *call* "motor neuron activities". **No spike-to-force stage, no twitch, no recruitment.**
  They cite Azevedo et al. 2020 (their ref [59]) but do not use its force-per-spike numbers.
- No measured *Drosophila* force-length or force-velocity curve (explicitly absent).
- No measured passive joint torque.
