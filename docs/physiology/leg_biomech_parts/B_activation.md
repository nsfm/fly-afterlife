# B. activation: motor neuron spikes -> muscle force -> joint torque

status: in progress. legend: **(M)** measured in *Drosophila*; **(C)** comparative, measured in
another insect; **(E)** estimate/model value, not a measurement; **(D)** digitised by me from a
published figure. every number carries its source. raw paper notes live in `docs/research/sources/`.

## B.1 the one real dataset: azevedo et al. 2020

Azevedo AW, Dickinson ES, Gurung P, Venkatasubramanian L, Mann RS, Tuthill JC (2020)
"A size principle for recruitment of *Drosophila* leg motor neurons." *eLife* 9:e56754,
doi:10.7554/eLife.56754. this is the only paper that measures force per spike in a fly leg muscle.
everything is the **tibia flexor** of the **front (T1) leg** of a **female**, measured as force on a
calibrated probe at the tibia tip (lever arm 417 ± 7 µm), not as joint torque.

### force per spike

| class | driver | force / spike | tip displacement / spike | pool size |
|---|---|---|---|---|
| fast | R81A07-Gal4 | **~10 µN** (M) | **50 µm** (M) | 1 MN (M) |
| intermediate | R22A08-Gal4 | **~1 µN** (M) | **5 µm** (M) | 2-5 MNs (M, anatomical) |
| slow | R35C09-Gal4 | **<0.1 µN**; linear fit **0.013 µN/spike** (M, fig 4D) | ~0.1 µm | 8-9 MNs (M, anatomical) |

per-cell spread, fig 4D (D): fast 1-spike 5-16 µN, saturating 20-30 µN; intermediate 1-spike
0.25-0.7 µN, saturating 1.5-3 µN. the pool spans **three orders of magnitude** in gain.

conversions you need: probe spring constant **k = 0.2234 µN/µm** (M); **~7.2-7.5 µm of tip
displacement per degree** of femur-tibia angle (M, from "60 µm = 8°"); fly weight **~10 µN**,
mass **~1 mg** (M, stated in the paper). so **one fast spike ≈ one body weight ≈ 7° of tibia
swing against the probe**. torque about the F-Ti joint = force x 417 µm, so one fast spike
≈ **4.2 nN·m** (E, my arithmetic on their numbers, assumes the probe is perpendicular).

### twitch time course

the paper states only one time constant: **half-maximal force in ~8.5 ms** for both fast and
intermediate (M). fig 4H per cell (D): fast n=7, 7.7-9.7 ms; intermediate n=6, 6.3-8.9 ms; n.s.
(p=0.2). conduction delay soma-spike to EMG-spike **0.6-1.0 ms** (M, fig 4G; axis mislabelled µs).

i digitised the single-spike traces in fig 4A/4B to get the rest of the kernel (D, one example
cell each, NOT author-stated numbers):

| | fast | intermediate |
|---|---|---|
| movement onset | ~2 ms after spike | ~2-4 ms |
| time to half-peak | ~9 ms | ~10 ms |
| **time to peak** | **~21 ms** | **~21 ms** |
| peak | 58 µm (~13 µN) | 4.3 µm (~1 µN) |
| half-decay (from peak) | **~17.5 ms** | ~16 ms |
| decay tau (single exp) | **~20 ms** | ~15-20 ms |
| back to baseline | ~70-80 ms | ~55-60 ms |

working twitch kernel (E): a difference-of-exponentials or alpha-like kernel with
**tau_rise ≈ 6-8 ms, tau_decay ≈ 20 ms**, peaking at ~21 ms, reproduces both traces. the
fast and intermediate units have **the same kinetics and differ only in gain** - that is the
single most useful modelling fact in the paper.

the **slow** unit has no resolvable twitch: force builds gradually and **has not peaked at 500 ms**
(M), and releasing it takes ~100 ms. model it as a tonic, heavily low-passed element
(tau of order 200-500 ms, E), not as a summed twitch train.

### summation and saturation

- **2 spikes give ~1.6x the force of 1 spike** in both fast and intermediate (M, fig 4E) - i.e.
  distinctly sublinear even at n=2.
- the force-vs-spike-count curve **saturates at ~10 spikes** for fast and intermediate (M, fig 4D),
  attributed by the authors to fatigue.
- there is **no tetanic fusion frequency and no force-frequency curve in the paper** - they never ran
  a frequency series. anyone quoting a fly "fusion frequency" is extrapolating. from the twitch decay
  tau ~20 ms, fusion would be expected around **50-100 Hz** (E), and the slow unit's steady force at
  its 30 Hz resting rate is already fully fused (M, by observation).
- **recruitment is by adding motor neurons, not by rate** across the pool: order slow ->
  intermediate -> fast, each step ~10x the force (M). only **110/3082** intermediate spikes were not
  preceded by a slow spike (M, fig 5-S1C). violations occur only during rapid unloaded leg shaking,
  where the slow MN is apparently inhibited (M).

### firing rates actually measured (M)

| state | fast | intermediate | slow |
|---|---|---|---|
| at rest, fly still | 0 | 0 | **~30 Hz** (range 10-52) |
| averaged over all spontaneous-movement trials (fig 5-S1A) | **~1.5 Hz** | **~9-10 Hz** | **~62 Hz** |
| driven (current injection, slow only) | - | - | **100-150 Hz** |

the paper has **no** breakdown by standing / grooming / walking / flailing - flies were only
behaviour-classified in the optogenetic experiments, where there is no electrophysiology.
the fig 5-S1A caption warns instantaneous rates go much higher than the averages above.

### intrinsic properties (M, fig 3; n = 15 / 11 / 14)

| | fast | intermediate | slow |
|---|---|---|---|
| resting Vm | -68 mV | -60 mV | -48 mV |
| input resistance | 150 MΩ | 300 MΩ | 700 MΩ |
| spontaneous rate | 0 | 0 | ~30 Hz |

**no spike-threshold current exists for fast and intermediate**: somatic current injection cannot
reliably evoke spikes in them because the soma is electrically isolated from the spike initiation
zone (M). the authors used optogenetic stimulation instead. only the slow MN's rate is controllable
from the soma. if you build a point-neuron MN model, this is a real caveat - the fly's fast MN
is not a soma-integrating cell in the way a leaky integrate-and-fire unit assumes.

## B.2 whole-joint force capacity (M)

- max force at the tibia tip: **~90-100 µN** (probe travel 400 µm x 0.2234 µN/µm), i.e. ~10x body
  weight. peak velocity **8 mm/s**, peak force rate **~1.3 mN/s**.
- for comparison, peak leg force during take-off **~100 µN** (Zumstein et al. 2004, cited by
  Azevedo; not independently verified here).

## B.3 passive joint stiffness and damping

### the one Drosophila measurement (M)

Wang N, Babski H, Perdomo JE, McMahan SB, Ramakrishnan A, Biswas T, Bhandawat V (2025)
"Passive muscle forces in Drosophila are large but insufficient to support a fly's weight."
**bioRxiv 2025.04.29.651225 / PMC12324252 / PMID 40766569 - a preprint, not peer-reviewed.**
they silenced the whole motor pool (`VGlut-Gal4; UAS-GtACR1`, all fly MNs are glutamatergic),
rotated the tethered fly, and read the equilibrium joint angle against a known gravitational torque.

- **passive torque is a linear angular spring** over **±40° about the rest angle** (M). no need for
  a nonlinear passive element in the working range.
- median stiffnesses, as printed (M):

| leg | Lev-Dep (CTr) | Ret-Pro (ThC) | Ext-Flex (FTi) | Pro-Sup (ThC) |
|---|---|---|---|---|
| T1 | 1.5e-8 | 1.9e-9 | **1.7e-8** | 1.5e-8 |
| T2 | 8.6e-9 | 1.1e-8 | **2.5e-8** | 1.0e-8 |
| T3 | 2.7e-8 | 5.6e-8 | **1.7e-8** | 4.7e-8 |

**units are ambiguous in the source**: the table caption says `mN/°`, the discussion says `Nm/°`.
if `N·m/deg`, T1 femur-tibia = 9.7e-7 N·m/rad ≈ 1 µN·m/rad. if the numbers are really N·m/rad,
T1 FTi = 17 nN·m/rad. **my cross-check says the smaller value.** Azevedo's probe had an equivalent
rotational stiffness of k·L² = 0.2234 x (417e-6)² = **39 nN·m/rad**, and a single fast spike
(4.2 nN·m) swung the tibia ~7° against it, so the fly's own passive FTi stiffness in that prep
cannot have been much above a few tens of nN·m/rad. use **~2e-8 N·m/rad for the T1 F-Ti joint (E,
from an ambiguous M)** and treat it as uncertain to a factor of ~50 until someone reads the figure.
- variation across flies: ~2-fold IQR; ~30% either side of the median. T1 ≈ 1.5x T2; T3 stiffest.
- **passive torque is ~70x (their OpenSim model: ~100x) too small to hold the fly up.** simulated
  with the measured stiffness the fly collapses in ~20 ms, near free-fall; they needed a **40x**
  uniform stiffness increase before the model fly could stand. so posture is actively maintained,
  which is exactly what the slow MN's 30 Hz tonic rate is for.
- bonus number from the same paper: after silencing, **active force decays with tau ≈ 100 ms**
  (their model fit), with ~350 ms observed settling in the tethered prep (M, but includes GtACR1
  and muscle-relaxation latency, so both are upper bounds).

**no measurement of joint damping in Drosophila exists that I could find.** (verified absent)

### what the simulators actually use (E - all hand-tuned, none of it measured)

| model | leg joint stiffness | leg joint damping | actuation |
|---|---|---|---|
| flybody (Vaxenburg 2025 Nature 643:1312) | 1e-9 N·m/rad (tarsus 1e-8) | 1e-9, tibia 4e-10, tarsus 2e-10 N·m·s/rad | MuJoCo position servos |
| Özdil 2025 musculoskeletal MuJoCo | 4e-10 N·m/rad | 2e-11 N·m·s/rad | Hill-type MTUs |
| NeuroMechFly v1 (Lobato-Rios 2022 Nat Methods 19:620) | Ekeberg spring-damper, gains optimised by NSGA-II | same | joint torque |

flybody's methods describe fitting **only the wing** damping (to Dickson 2008 hovering kinematics);
the leg values are not traceable to any measurement. both MuJoCo models sit **~20-50x below** even
the low reading of the measured T1 F-Ti stiffness, and ~1000x below the high reading. if we care
about passive mechanics, neither shipped model is a source - the Wang 2025 numbers are.

## B.4 is there a Hill-type muscle model fitted to Drosophila leg data?

**yes, exactly one, and it is a 2025 preprint.** Özdil PG, Ning C, Phelps JS, Wang-Chen S, Elisha G,
Blanke A, Ijspeert A, Ramdya P (2025) "Musculoskeletal simulation of limb movement biomechanics in
Drosophila melanogaster", arXiv:2509.06426. OpenSim (Millard 2013 muscle) + MuJoCo, **15 muscle-
tendon units per front leg**, geometry from synchrotron X-ray scans, parameters fitted with NSGA-II
against measured walking and grooming kinematics.

what it gives us (E, optimised not measured):
- tibia flexor **F_max ≈ 68 µN**, tibia extensor **F_max ≈ 304 µN** (model units; the MJCF's
  cm/g/s-equivalent convention makes 1 unit = 1 µN, but the summed body masses are 2.5x a real fly,
  so the absolute scale is shaky). full 15-MTU table in `docs/research/sources/ozdil_2025.md`.
- v_max = 10 optimal-lengths/s for every MTU; f_vmax 1.4.
- shipped activation dynamics **tau_act = 0.1 ms, tau_deact = 0.4 ms** - about 85x faster than the
  measured 8.5 ms twitch half-rise. do not reuse those.

what it does **not** give us, and this is the gap our model has to fill:
- **no spike-to-force stage at all.** the policy emits a continuous [0,1] "muscle activation" that
  they *call* motor neuron activity. no twitch, no recruitment, no motor unit. they cite Azevedo
  2020 but never use its force-per-spike numbers.
- **no measured Drosophila force-length or force-velocity curve exists.** they say so outright:
  "Due to the lack of measured Drosophila muscle curves, default curves in OpenSim were assumed to
  approximate real physiological behavior." those defaults are mammalian.
- NeuroMechFly v1/v2 and flybody use **torque or position actuators, not muscles.**

## B.5 motor units per muscle, front leg (M)

from the freely available Motor Neuron ID Appendix of Azevedo A, Lesser E, Phelps JS, Mark B, et al.
(2024) "Connectomic reconstruction of a female Drosophila ventral nerve cord", *Nature*
631(8020):360-368 (the companion is Lesser E, Azevedo AW, et al., "Synaptic architecture of leg and
wing premotor control networks in Drosophila", *Nature* 631(8020):369-377 - Azevedo = connectome +
MN atlas, Lesser = premotor networks).

**T1 leg has 69 MNs (left) / 70 (right)** in FANC - this supersedes the "53 per leg" of Azevedo 2020.

| muscle | MNs | | muscle | MNs |
|---|---|---|---|---|
| tergopleural + pleural promotor | 4 | | trochanter flexor | 8 |
| pleural remotor & abductor | 2 | | accessory trochanter flexor | 3 |
| sternal anterior rotator | 2 | | femur reductor | 6 |
| sternal posterior rotator | 4 | | **tibia extensor** | **2** (FETi + SETi) |
| sternal adductor | 1 | | **tibia flexor** | **5** |
| tergotrochanter extensor | 4 | | **accessory tibia flexor** | **10** |
| sternotrochanter extensor | 2 | | long tendon muscle 2 (femur) | 4 |
| trochanter extensor | 2 | | long tendon muscle 1 (tibia) | 4 |
| | | | tarsus depressor | 6 |

**femur-tibia joint: 2 extensor MNs against 15 flexor MNs** (5 tibia flexor + 10 accessory tibia
flexor), matching Azevedo 2020's "~15". the fast tibia flexor is **MN #45**, the largest MN by
volume in left T1; force was measured for **#41, #44, #45**. the "slow" R35C09 cell is an
*accessory* tibia flexor (#46-49 group), and this appendix renames Soler's "tibia reductor" to
accessory tibia flexor, "tibia levator" to tibia extensor, "tibia depressor" to tibia flexor.

Lesser 2024's abstract gives the recruitment justification: "Within most leg motor modules, the
synaptic weights of each premotor neuron are proportional to the size of their target MNs,
establishing a circuit basis for hierarchical MN recruitment. By contrast, wing premotor networks
lack proportional synaptic connectivity." so for the **leg**, a single shared premotor drive whose
weight onto each MN scales with MN size is a connectome-supported modelling assumption.

note on the extensor: the appendix observes that SETi innervates the **distal, more pinnate** fibres
of the tibia extensor and FETi the proximal ones, "suggesting less mechanical advantage, perhaps a
mechanism underlying the smaller forces produced by spikes in the SETi" (M, anatomical). so at the
extensor, part of the fast/slow force gradient is **moment arm and pennation**, not neuron size.

## B.6 body mass and leg geometry (M)

Vaxenburg et al. 2025 weighed disassembled wild-type females (2 groups, n=30 and n=22):

| head | thorax | abdomen | each leg | each wing | total |
|---|---|---|---|---|---|
| 0.15 mg | 0.34 mg | 0.38 mg | **0.0162 mg** | 0.008 mg | **0.983 mg** |

body length 2.97 mm, wingspan 6.04 mm. no per-segment or per-leg-pair mass breakdown is published.
NeuroMechFly v1 used a slightly different split from Szczecinski et al. 2018 (J Exp Biol 221):
head 0.125, thorax 0.31, abdomen 0.45, wings 0.005, legs 0.11 mg; total 1 mg, body length 2.8 mm.
Azevedo 2020 states mass ~1 mg, weight ~10 µN. all three agree on ~1 mg.

per-leg-pair segment geometry (Wang et al. 2025 Table 2, "ellipsoid radii", µm - but see caveat):

| | coxa | femur | tibia | tarsus | segment "radius" |
|---|---|---|---|---|---|
| T1 | 339.7 | 538.1 | 452.4 | 571.4 | 120 / 119 / 68.3 / 39.8 |
| T2 | 137.2 | 670 | 603.6 | 698.6 | same |
| T3 | 173.8 | 667.2 | 605.9 | 761.4 | same |

caveat: labelled "radii", but read as semi-axes the T2 femur would be 1.34 mm long and 238 µm thick,
roughly twice a real fly; read as full length and diameter they match published dimensions. treat as
**lengths and diameters**, flag as uncertain. no per-segment masses anywhere.

## B.7 comparative twitch / tetanus numbers from bigger insects (C) - use only as sanity checks

- **locust hind leg, FETi** (Ache JM & Matheson T, 2013, "Passive joint forces are tuned to limb use
  in insects and drive movements without motor activity", *Curr Biol* 23(15):1418-1426,
  PMC3739007) (C) [locust]:
  - a **single FETi spike** never reaches full extension (full = 18.6° ± 1.4°, N=7);
  - **5 spikes at 7.5 Hz give five separate twitches** with passive returns between them;
    **5 spikes at 20 Hz give a fused full extension** held ~250 ms. so locust extensor **fusion
    frequency sits between 7.5 and 20 Hz** - two orders of magnitude slower than what the fly's
    ~20 ms twitch implies. do not import this number.
  - single-spike peak extension velocity ~570°/s at the rest angle, 500-750°/s from flexed starts;
    the FETi contribution is a near-constant ~-550°/s across 50-140° of joint angle.
  - passive extension from full flexion peaks at **1040°/s**, i.e. **1.8x faster than an active
    FETi twitch** - passive forces are not a small correction in an insect leg.
  - mechanism: **passive flexion torque comes from the joint cuticle itself** (it survives ablating
    both muscles and their tendons); **passive extension torque comes from the extensor muscle.**
    after ablating both muscles the tibia moved only 6.9° ± 5.6°.
  - hysteresis of ~10° in rest position depending on approach direction, in locust, stick insect and
    false stick insect.
- **stick insect (Carausius morosus) extensor tibiae, Hill-type parameters measured in single
  muscles**: Blümel M, Guschlbauer C, Daun-Gruhn S, Hooper SL, Büschges A (2012) "Hill-type muscle
  model parameters determined from experiments on single muscles show large animal-to-animal
  variation", *Biol Cybern* 106:559-571, PMC3501687 (C) [stick insect]:
  - **F_max 116-197 mN across 10 animals** (vs ~10 µN per fast spike in the fly - a ~10^4 gap that
    tracks the ~10^3 body-mass gap).
  - v_max at full activation **5.6-7.05 mm/s**; activation is normalised to a **200 Hz** firing rate.
  - the whole point of the paper: **individual muscles vary 1.3- to 2-fold in every parameter**, and
    a model built on across-animal means matches almost no individual. relevant warning for us.
  - companion: Blümel et al. 2012 *Biol Cybern* 106:573-585, "Using individual-muscle specific
    instead of across-muscle mean data halves muscle simulation error".
- **stick insect extensor contraction time constants 200-700 ms** (Hooper SL, Guschlbauer C,
  von Uckermann G, Büschges A, 2007, *J Neurophysiol* 98:1718-1732, "Slow temporal filtering may
  largely explain the transformation of stick insect (Carausius morosus) extensor motor neuron
  activity into muscle movement") (C) [stick insect] - **second-hand, from search result text, NOT
  verified against the paper**; I could not get past the publisher paywall.
  companion: Guschlbauer C, Scharstein H, Büschges A (2007) *J Neurophysiol* 97:1428-1444,
  "Different motor neuron spike patterns produce contractions with very similar rises in graded slow
  muscles".

the headline comparative point: **fly leg muscle is roughly an order of magnitude faster than stick
insect or locust leg muscle** (~20 ms to peak vs 200-700 ms time constants), which is what you would
expect from the size scaling, and it means comparative fusion frequencies and time constants must
not be imported.

## B.8 firing rates during behaviour, and what is simply not measured

**there is no published recording of Drosophila leg motor neuron firing rates broken down by
standing / grooming / walking / flailing.** I checked Azevedo 2020 (behaviour classes appear only in
the optogenetic experiments, which have no electrophysiology), Gorko et al. 2024 *Nature*
("Motor neurons generate pose-targeted movements via proprioceptive sculpting"), Dallmann et al.
2025 *Nature* ("Presynaptic inhibition selectively suppresses leg proprioception in behaving
Drosophila"), Pratt et al. 2024 *Curr Biol*, and the Tuthill lab's whole 2018-2026 publication list.
Nothing reports spike rates per behaviour. Agrawal S, Dickinson ES, Sustar A, Gurung P, Shepherd D,
Truman JW, Tuthill JC (2020) "Central processing of leg proprioception in Drosophila", *eLife*
9:e60299, doi:10.7554/eLife.60299 is about **proprioceptive interneurons**, not MNs.

what we do have, all from Azevedo 2020 (M):
- rest, fly still: fast 0 Hz, intermediate 0 Hz, slow ~30 Hz (10-52 Hz across cells)
- averaged over all spontaneous-leg-movement trials: fast ~1.5 Hz, intermediate ~9-10 Hz, slow ~62 Hz
- slow MN driven by current injection: **100-150 Hz** sustained
- instantaneous rates "could be much higher" (their words); no maximum is reported
- during *rapid unloaded leg shaking* the slow MN is actively **suppressed** while the intermediate
  MN fires faster - the one documented violation of recruitment order

kinematic constraint that any activation model has to satisfy (M, Azevedo 2020 intro, their cites
DeAngelis 2019, Gowda 2018, Mendes 2013, Strauss & Heisenberg 1990, Wosnitza 2013):
> "The femur-tibia joint of a walking fly flexes and extends 10-20 times per second, reaching swing
> speeds of several thousand degrees per second"

a 20 ms twitch at 10-20 steps/s means **the twitch duration is comparable to the whole step period**
(50-100 ms). so during walking the fly is operating near, but not past, twitch fusion for the fast
unit, and well past it for the slow unit. useful check: a single fast spike reaches peak tibia
velocity of 2-8 mm/s, which over a 417 µm lever is ~300-1200 °/s - the low end of the "several
thousand °/s" swing speeds, so swing must involve several fast/intermediate spikes and/or passive
release, not one twitch.

**Bidaye SS, Bockemühl T, Büschges A (2018) "Six-legged walking in insects: how CPGs, peripheral
feedback, and descending signals generate coordinated and adaptive motor rhythms", J Neurophysiol
119(2):459-475, doi:10.1152/jn.00658.2017** - citation verified via Europe PMC; the full text is
**not open access** and journals.physiology.org blocked every fetch I tried (403 / Cloudflare).
**I could not extract any numbers from it. Do not cite rates "from Bidaye 2018" on my authority.**
Same for Dallmann CJ, Dürr V, Schmitz J (2019) "Motor control of an insect leg during level and
incline walking", J Exp Biol 222:jeb188748 (not OA), which is the paper that would give stick-insect
MN spikes-per-step during walking.

## B.9 what I could not find at all (verified absent, not merely unfound)

- any tetanic fusion frequency or force-frequency curve for a *Drosophila* leg muscle
- any *Drosophila* leg muscle force-length or force-velocity curve (Özdil et al. 2025 say so
  explicitly and substitute OpenSim's mammalian defaults)
- any measurement of *Drosophila* leg joint **damping**
- any spike-threshold current for the fast or intermediate tibia flexor MN (somatic injection cannot
  evoke their spikes at all)
- any per-segment or per-leg-pair **mass** for the fly leg (only "0.0162 mg per whole leg")
- any published twitch/tetanus model fitted to fly leg data - the field has no spike-to-force stage

## B.10 proposed model (mine, E) - what the numbers above actually support

1. **motor unit force** F_i(t) = g_i * sum_spikes K(t - t_s) * S(rate), with
   - g_i = force per spike: fast 10 µN, intermediate 1 µN, slow 0.013 µN at the tibia tip (M);
     for the other 12 flexor MNs interpolate on MN surface area from FANC (E).
   - K = twitch kernel, tau_rise ~7 ms, tau_decay ~20 ms, peak at ~21 ms, latency ~2 ms after the
     somatic spike plus ~0.8 ms conduction (M for the landmarks, E for the functional form).
   - S = a saturating summation term calibrated so that 2 spikes -> 1.6x (M) and ~10 spikes ->
     plateau (M). A simple saturating nonlinearity on the summed kernel, not a fatigue state
     variable, is enough to match the published data.
   - slow units: skip the kernel, use a first-order low-pass with tau of a few hundred ms (E,
     constrained by "no peak within 500 ms" and "~100 ms to release").
2. **recruitment**: one shared premotor drive per module, weight onto MN i proportional to MN
   surface area (M, Lesser 2024), threshold inversely related to MN size via input resistance
   (700 / 300 / 150 MΩ, M). This reproduces slow -> intermediate -> fast ordering for free.
3. **joint torque** = sum_i F_i * moment_arm. Azevedo's forces are at a 417 µm tibia lever, so if
   you want muscle-level forces you must divide by the flexor's own moment arm, which nobody has
   measured in the fly (Özdil 2025's model has moment arms but they are fitted, not measured).
   Safest: model the **joint torque directly**, in the units Azevedo measured, and skip the muscle.
   One fast spike = 10 µN x 417 µm = **4.2 nN·m** of F-Ti flexion torque (E, my arithmetic).
4. **passive joint** = linear angular spring about a rest angle, ~2e-8 N·m/rad at T1 F-Ti (E, from
   Wang 2025's ambiguous units), linear over ±40°, plus an unknown damping. Passive torque is ~70x
   too weak to hold the fly up, so standing must come from tonic slow-MN drive.
