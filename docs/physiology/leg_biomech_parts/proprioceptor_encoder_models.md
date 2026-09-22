# Proprioceptor encoder models (FeCO, campaniform sensilla, hair plates)

Scope: existing published models that map leg kinematics / forces -> proprioceptor
activity, for implementation as encoders in a physics-based whole-fly sim driven by
joint angles q, joint angular velocities q̇, and ground contact forces F.

Status: substantially complete, compiled 2026-09-21. Open gaps listed in §5.

Verification key: **[V]** = I read the primary source text myself (PDF/HTML) and the
number/equation is quoted from it. **[S]** = second-hand (abstract, index page, another
paper's citation). **[?]** = could not verify.

---

## 1. Campaniform sensilla — Szczecinski, Dallmann, Quinn & Zill 2021 (THE one to implement)

**Citation.** Nicholas S Szczecinski, Chris J Dallmann, Roger D Quinn, Sasha N Zill (2021).
"A computational model of insect campaniform sensilla predicts encoding of forces during
walking." *Bioinspiration & Biomimetics* **16**(6):065001.
DOI: 10.1088/1748-3190/ac1ced. Received 31 Mar 2021, accepted 12 Aug 2021,
published 7 Sep 2021. Code: https://github.com/nss36/campaniformSensillaModeling  **[V]**

Species: cockroach *Periplaneta americana* (proximal tibial CS group) and stick insect
*Carausius morosus* (tibial groups 6A, 6B). **Not Drosophila.** **[V]**

### 1.1 The model (verbatim equations)

Two states. `u` = stimulus force applied to tibia (mN). `y` = discharge (AP/s).
`x` = internal adaptive variable (same units as u).

```
y = max(0, a·(u − x) + c·u + d)                         (eq 1)
τ·ẋ = f(u − x)                                          (eq 2)
f(z) = sign(z)·|z|^b                                     (eq 8)
```

so the implementable ODE is

```
ẋ = (1/τ)·sign(u − x)·|u − x|^b
y = max(0, a·(u − x) + c·u + d)
```

`f` must increase monotonically with f(0)=0, so the only equilibrium is x=u; at
equilibrium the discharge relaxes to the tonic level y = c·u + d. **[V]**

### 1.2 Why it works (derived in the paper) **[V]**

- For a ramp input u = (A/T)·t, x steady-state lags u by Δt:
  `x_ss = u(t − Δt) = (A/T)·(t − Δt)` (eq 3), so `y_ss = a·(u(t) − u(t−Δt))` (eq 4),
  a finite-difference approximation of u̇ when a = 1/Δt. Rate sensitivity is emergent,
  there is no explicit u̇ term.
- `Δt = (T/A)·f⁻¹(τ·A/T)` (eq 5) ⇒ `y_ss = a·f⁻¹(τ·A/T)` (eq 6) = `a·f⁻¹(τ·u̇)` (eq 7).
  With f(z)=sign(z)|z|^b and b = 1/k, this gives the empirical power law y ∝ u̇^k.
- Step/adaptation response is an exact power law in time:
  `x(t) = B·((t + Δt)/τ)^s` (eq 11) with
  `s = 1/(1 − b)` (eq 16), `B = (b − 1)^(1/(1−b))` (eq 17),
  `Δt = τ·x0^(1−b)/(b − 1)` (eq 18), where x0 = x(t=0).
  Requires s < 0 and Δt > 0. So power-law adaptation comes out of a **first-order**
  (integer-order) nonlinear ODE — no fractional derivatives needed.

### 1.3 Fitted parameters (Table 2, verbatim) **[V]**

| Parameter | Cockroach prox. tibia | Stick insect 6A | Stick insect 6B |
|---|---|---|---|
| a — amplitude of adaptive term (Hz·mN⁻¹) | 707.6 | 265.0 | 605.0 |
| b — exponent of adaptive term (unitless) | 2.262 | 1.675 | 3.325 |
| c — amplitude of proportional term (Hz·mN⁻¹) | 54.29 | 17.75 | 5.750 |
| d — amplitude of bias term (Hz) | −41.16 | −22.50 | 10.50 |
| τ — adaptive time constant (ms) | 3.859 | 9.678 | 1.659 |

Fitting: cockroach params by gradient-based MSE minimisation (MATLAB `fmincon`) against
a single ramp-and-hold discharge; stick-insect 6A/6B by genetic algorithm then gradient
refinement. Simulated with MATLAB `ode15s`. Discharge rate computed from spikes in a
moving window, typically 20 ms. **[V]**

Note b > 1 for all three fits, so s = 1/(1−b) < 0 as required. Cockroach: s = 1/(1−2.262)
= −0.7924 (my arithmetic from their fitted b, not printed in the paper).

### 1.4 Benchmark against a fractional-derivative model **[V]**

Alternative model: `y = max(0, a·D^b u(t))` (eq 19), D^b = bth fractional derivative.
Fitted to cockroach fig 3(a): **a = 40.6, b = 0.631**.
MAE comparison (AP/s), selected rows of Table 3:
fig 3(a) nonlinear 4.85 vs fractional 5.56; fig 3(b) (naturalistic joint-torque waveform
from Dallmann et al 2016, *not* used for tuning) nonlinear 9.87 vs fractional 16.22.
Across 18 trials the nonlinear model wins in 12.

### 1.5 Power-law rate exponents (animal vs model) **[V]**

Peak discharge vs ramp rate, log-log slope k (Ridgel et al 2000 cockroach data):
- varying stimulus **amplitude**: animal k ∈ [0.28, 0.57]; model k ∈ [0.27, 0.46].
- varying tonic **offset**: animal k ∈ [0.34, 0.43]; model k ∈ [0.25, 0.38].

### 1.6 Implementation notes for the sim

- Input `u` is a scalar **force/strain proxy per CS group**, in mN. In the source
  experiments it is the bending force applied at the distal tibia with the FTi joint
  pinned. For a whole-fly sim the natural drive is the leg-segment load: either the
  ground reaction force projected onto the group's preferred bending axis, or the joint
  torque on the proximal joint of that segment.
- CS groups come in **antagonistic pairs** encoding bending in opposite directions
  (Ridgel et al 1999; Zill et al 2012). The paper's two-group inversion feeds group B
  the sign-flipped stimulus (−u). So a natural encoder is two units per site:
  y⁺ = model(u), y⁻ = model(−u). **[V]**
- Units of a and c are Hz·mN⁻¹, so u must be in mN. FlyGym returns forces in mN
  already (meshes at 1000× scale) — convenient.
- Integrate x with a stiff-capable integrator or small dt: τ is 1.7–9.7 ms and the
  |·|^b nonlinearity with b>1 is stiff near x≈u.

### 1.7 Earlier conference version **[S]**

Szczecinski, Dallmann, Quinn, Zill (2020). "Modeling the Dynamic Sensory Discharges of
Insect Campaniform Sensilla." *Conference on Biomimetic and Biohybrid Systems
(Living Machines 2020)*, LNAI, Springer, pp. — DOI 10.1007/978-3-030-64313-3_33.
Cited by the 2021 paper as "a preliminary model and results". PDF at
par.nsf.gov/servlets/purl/10202934. **Parameters extracted — see §12 below.** Note its
letters mean different things than the 2021 paper's; do not mix them up.

---

## 2. NeuroMechFly v2 — what it actually exposes

**Citation.** Sibo Wang-Chen, Victor Alfred Stimpfling, Thomas Ka Chung Lam,
Pembe Gizem Özdil, Louise Genoud, Femke Hurtak, Pavan Ramdya (2024).
"NeuroMechFly v2: simulating embodied sensorimotor control in adult *Drosophila*."
*Nature Methods*. DOI: 10.1038/s41592-024-02497-y. Published 12 Nov 2024.
PMID 39533006. Volume/pages: **could not verify** from the postprint; the postprint is
the accepted manuscript (46 pp) at
epfl.ch/labs/ramdya-lab/wp-content/uploads/2024/08/NMF2_postprint.pdf. **[V for content,
? for volume:pages]**

### 2.1 Answer to "does it model FeCO / CS / hair plates?" — **No.**

There is **no explicit proprioceptor model** anywhere in NeuroMechFly v1 or v2, and none
in flygym. Nothing named campaniform, chordotonal, FeCO, or hair plate exists in the
flygym source (I grepped the v1.1.0 and current main trees; the only hits are the words
"proprioceptive"/"mechanosensory" in prose and in example-script names). What the
simulator provides is **raw MuJoCo joint and contact sensors**, which the papers then
call "proprioceptive and tactile signals" and feed directly (standardised, or binarised)
to downstream MLPs. Implementing FeCO/CS/hair-plate encoders on top of these signals is
exactly the gap. **[V]**

(The one anatomical mention: "The neck is located ventral to the hair plate behind the
head" — descriptive only, no model. **[V]**)

### 2.2 Observation space, verbatim (Supplementary Note 3) **[V]**

Action space:
- Joint actuation signals: target angle, angular velocity, or torque (user choice) of the
  n actuated joint DoFs (by default **all 42 leg DoFs**), ℝⁿ.
- Adhesion on/off signals (if enabled): {0,1}⁶.

Observation space (per fly):
- **Joint states**: the angle, velocity, and force at each of the n actuated joint DoFs
  (default all 42 leg DoFs), ℝ^{3×n}.
- **Fly state**: linear (x,y,z) position, linear velocity, angular (pitch-roll-yaw)
  position, and angular velocity of the thorax in the global frame, ℝ^{4×3}.
- **Fly orientation**: unit vector along the anterior-posterior axis, ℝ³.
- **Ground reaction forces**: 3-D ground reaction forces on m body segments (default the
  tibia and all 5 tarsal segments of all legs ⇒ m = 36) in the global frame, ℝ^{m×3}.
- **Visual inputs** (if vision enabled): 721 ommatidia per eye, ℝ^{2×721×2};
  70% yellow-type, 30% pale-type; only one of the two channels non-zero per ommatidium.
- **Odor inputs** (if olfaction enabled): ℝ^{k×4} (2 antennae + 2 maxillary palps).

Units: meshes configured at **1000× scale in MuJoCo so observations are in mm and mN**. **[V]**

### 2.3 Contact-force thresholds used as "tactile" signals **[V]**

Both the path-integration and head-stabilisation models binarise stance from contact force:
`F_thr,front = 0.5 mN`, `F_thr,middle = 1 mN`, `F_thr,hind = 3 mN`.
Path integration time window `τ = 0.64 s` (chosen by sensitivity analysis).
Ground contact per leg = sum of force magnitudes over all tarsal segments of that leg,
then thresholded.

Stumbling rule in the hybrid controller triggers when the tibia or the two most proximal
tarsal segments have contact force **> 1 mN** opposing the fly's heading during swing.
Overstretch rule triggers when a leg tip is **> 0.05 mm** lower along z than the third
most extended leg. Rule persistence 0.002 s; correction capped after 0.008 s; swing-phase
gain piecewise-linear, max **+0.8** at swing midpoint, min **−0.1** at stance midpoint. **[V]**

### 2.4 Head stabilisation = the closest thing to a proprioceptive decoder **[V]**

Input: **48-dimensional** = 7 DoF angles per leg × 6 legs (42) + 6 binary contact
variables. Joint angles standardised (z-scored) against the distribution during forward
walking on flat terrain. Output: 2-D (target neck roll and pitch).
MLP: 2 hidden layers × 32 units, ReLU; MSE loss; Adam, lr η = 0.001, batch 256, 30 epochs,
train/val 8:2. Deployed with a PD controller on neck joint angle, **gain 500**.
Naming gotcha they flag: the neck **roll** DoF is named `joint_Head_yaw` in the model file.

### 2.5 Path-integration proprioceptive signal (Supplementary Note 6) **[V]**

Per leg L: claw position relative to body x_L(t); stance flag p_L(t) = 1 iff ground
contact force magnitude > F_thr; heading unit vector ĥ(t) = [cos h, sin h]ᵀ;
ε_L(t) = ‖ĥ(t)·x_L(t)‖ (projection of claw position onto heading).

```
d_L(t) = ∫₀ᵗ p_L(t')·ε̇_L(t') dt'                               (Supp. 7)
d_L[0] = 0;  d_L[i] = d_L[i−1] + p_L[i]·(ε_L[i] − ε_L[i−1])     (Supp. 8,9)
δ_pos = d_pos,left − d_pos,right ;  σ_pos = d_pos,left + d_pos,right
                                    pos ∈ {front, middle, hind}  (Supp. 10,11)
```
Linear regression from Δδ, Δσ over window τ to Δ heading and Δ forward displacement.

### 2.6 CPG network (for completeness, Supplementary Note 4) **[V]**

```
θ̇ᵢ = 2πνᵢ + Σⱼ rⱼ w_ij sin(θⱼ − θᵢ − φ_ij)          (Supp. 1)
ṙᵢ = αᵢ(Rᵢ − rᵢ)                                     (Supp. 2)
ψ_{i,DoF} = Ψ_{i,DoF}[0] + rᵢ(Ψ_{i,DoF}[κ] − Ψ_{i,DoF}[0])   (Supp. 3)
κ = ⌊(θᵢ/2π)·dur(Ψ_{i,DoF})⌋                          (Supp. 4)
```

### 2.7 Terrain / sim constants **[V]**

Joint position gain k_p = 45; adhesion force 40 mN (Methods, benchmarking).
Gapped terrain: 1 mm blocks, 0.3 mm gaps, 2 mm deep. Blocks terrain: 1.3 × 1.3 mm,
half raised 0.35 mm.

---

## 3. flygym API — exact observation keys and shapes **[V]**

Source read: flygym v1.1.0 tag source (`flygym/fly.py`, `flygym/preprogrammed.py`,
`flygym/simulation.py`, `doc/source/api_ref/mdp_specs.rst`) from
github.com/NeLy-EPFL/flygym. Docs site: neuromechfly.org.

### 3.1 Spaces (`Fly._define_observation_space`, verbatim)

| key | gym space | shape | notes |
|---|---|---|---|
| `joints` | Box(−inf, inf) | `(3, n_actuated_joints)` | rows = **angle, angular velocity, force**; column order = `Fly.actuated_joints` |
| `fly` | Box(−inf, inf) | `(4, 3)` | rows: xyz pos, xyz vel, orientation about xyz, d(orientation)/dt |
| `contact_forces` | Box(−inf, inf) | `(n_contact_sensor_placements, 3)` | one per segment in `Fly.contact_sensor_placements` |
| `end_effectors` | Box(−inf, inf) | `(6, 3)` | xyz of most distal tarsus link; leg order LF, LM, LH, RF, RM, RH |
| `fly_orientation` | Box(−inf, inf) | `(3,)` | **deprecated**; use `cardinal_vectors` "forward" |
| `cardinal_vectors` | Box(−1, 1) | `(3, 3)` | rows = forward, left, up; cols = x,y,z |
| `vision` (if `enable_vision`) | Box(0, 255) | `(2, num_ommatidia_per_eye, 2)` | eye (L,R) × ommatidium × channel (yellow, pale); docs say intensities on a [0,1] scale |
| `odor_intensity` (if `enable_olfaction`) | Box(0, inf) | `(arena.odor_dimensions, n_antennae_sensors)` | default 4 sensors (2 antennae, 2 maxillary palps) |

Action space: `joints` Box shape `(n_actuated_joints,)`; `adhesion` Box(0,1) shape `(6,)`
if `enable_adhesion`.

Extra keys in examples: `stride_diff_unmasked` `(6,3)` (PathIntegrationController);
`nn_activities_arr` `(2, num_cells_per_eye)` (RealisticVisionFly).

### 3.2 How the joint row is actually produced (`Fly._add_joint_sensors`, `get_observation`)

For each actuated joint MuJoCo sensors are added: `jointpos`, `jointvel`, and
`actuatorfrc` (on `actuator_{control}_{joint}`). For monitored-but-not-actuated joints:
`jointpos`, `jointvel`, and a site `torque` sensor whose 3-vector is reduced by
`np.linalg.norm` over components 1:5. Then:

```python
joint_obs[2, :] *= 1e-9   # convert to N
```

⚠ So the **third row of `joints` is scaled by 1e-9** — with the 1000× mesh scaling this
is the code's own unit bookkeeping. Treat the raw number with care; verify empirically
before using it as a torque in physical units.

`contact_forces` come from `physics.named.data.cfrc_ext[placements][:, 3:]`, i.e. the
**translational** half of MuJoCo's external body wrench (first three components are
rotational and are dropped). When adhesion is on, the adhesion force
(`adhesion_force * contact_normal`) is **subtracted back out** of `contact_forces`.

### 3.3 DoF list and defaults **[V]**

`preprogrammed.all_leg_dofs` = 42 = {L,R} × {F,M,H} × 7 DoFs, the 7 being:
`Coxa, Coxa_roll, Coxa_yaw, Femur, Femur_roll, Tibia, Tarsus1`
(joint names `joint_{side}{pos}{dof}`, e.g. `joint_LFTibia`).
`leg_dofs_3_per_leg` = 18 = `Coxa` (front) or `Coxa_roll` (mid/hind), `Femur`, `Tibia`.
`all_tarsi_links` = 30 = 5 tarsus segments × 6 legs (default `contact_sensor_placements`,
⇒ `contact_forces` is (30,3) by default in v1.1.0).
`default_leg_sensor_placements` = 36 = Tibia + Tarsus1..5 × 6 legs (the (36,3) variant
matching the paper's "tibia and all 5 tarsal segments").

`Fly.__init__` defaults: `control="position"`, `init_pose="stretch"`,
`spawn_pos=(0,0,0.5)` mm, `joint_stiffness=0.05`, `joint_damping=0.06`,
`non_actuated_joint_stiffness=1.0`, `non_actuated_joint_damping=1.0`,
`neck_stiffness=10.0`, `actuator_gain=45.0`, `actuator_forcerange=65.0`,
`tarsus_stiffness=7.5`, `tarsus_damping=1e-2`,
`friction=(1.0, 0.005, 0.0001)` (slide, torsion, roll),
`contact_solref=(2e-4, 1e3)`,
`contact_solimp=(9.99e-1, 9.999e-1, 1.0e-3, 5.0e-1, 2.0)`,
`vision_refresh_rate=500` Hz, `adhesion_force=40`.
`Simulation.timestep` default **1e-4 s (10 kHz)**.

**No `proprioception` or `mechanosensory` module exists.** The only modules touching
these signals are `flygym/examples/head_stabilization/` and
`flygym/examples/path_integration/`, both of which consume raw `joints` + `contact_forces`.

---

## 4. Femoral chordotonal organ (FeCO) — Mamiya, Tuthill and colleagues

### 4.1 Mamiya, Gurung & Tuthill 2018 **[V]**

**Citation.** Akira Mamiya, Pralaksha Gurung, John C. Tuthill (2018). "Neural Coding of
Leg Proprioception in *Drosophila*." *Neuron* **100**(3):636–650.e6.
DOI: 10.1016/j.neuron.2018.09.009. (Volume:pages **[S]** from the running head
"Neuron 100, 1–15.e1–e6, November 7, 2018" in the in-press PDF — page range 636–650
itself not verified.)

**There is no fitted encoding equation in this paper.** It is population two-photon
calcium imaging (GCaMP6f) of FeCO axons; tuning is reported as ΔF/F curves, not as a
parametric model. What it gives you is the *functional taxonomy and the stimulus ranges*:

- **Claw** neurons: tonic, encode **femur-tibia joint position**; split into
  flexion-activated and extension-activated sub-branches; "activity increased as a
  relatively linear function" of joint angle; strong **movement-history dependence**
  (hysteresis) in steady-state ΔF/F at a given angle.
- **Club** neurons: phasic, respond to **both** flexion and extension (bidirectional),
  and to **low-amplitude vibration**. Vibration amplitudes tested include **0.9 µm** and
  **0.054 µm**; vibration frequencies **100–1600 Hz**.
- **Hook** neurons: **directionally selective** (flexion-selective for R21D12); response
  roughly constant across the whole speed range tested.

Stimulus parameters (Methods):
- Joint driven between **180° (full extension) and 18° (flexion)**; could not flex past 18°.
- Swing-motion trials at **360 °/s**; velocity series at **180, 360, 720, 1440 °/s**.
  Elsewhere they report a speed series of **100–800 °/s** for club and hook comparison.
- Ramp-and-hold: **18° steps** at **240 °/s**, 3 s hold between ramps, acceleration
  **72 000 °/s²**.
- Club calcium-signal slope **peaked around 400 °/s** and decayed slightly above that.
- Motor: SilverMax QCI-X23C-1, max 24 000 °/s, position resolution 0.045°;
  pin glued 1.5 mm from joint centre; pin-magnet distance ≈ 300 µm.
- Cited biological context: cockroach mesothoracic FTi excursion ≈ 60°, fly tethered
  walking max excursion ≈ 80° (their unpublished obs.), giving mean swing speeds of
  ~2400–3200 °/s and stance ~2000–2670 °/s; cockroach FTi angular velocity 0–800 °/s
  (Watson & Ritzmann 1998).

### 4.2 Mamiya, Sustar, Siwanowicz, … Li, Mhatre, Tuthill 2023 **[V]**

**Citation.** Akira Mamiya, Anne Sustar, Igor Siwanowicz, … Hongjie Li, Natasha Mhatre,
John C. Tuthill (2023). "Biomechanical origins of proprioceptor feature selectivity and
topographic maps in the *Drosophila* leg." *Neuron* **111**:1–14.e1–e14, October 18, 2023.
DOI: 10.1016/j.neuron.2023.07.009. (In-press PDF; final page range **[?]**.)

This is the FeCO **biomechanical** model. It is a **finite-element model in COMSOL**, not
a closed-form transfer function — so it cannot be dropped into a sim as an equation. But
it gives the mechanism and the geometry constants you'd need to fit a reduced model.

**Architecture.** Tibia rotation → **joint tendon** → **arculum** (a cuticular link in the
proximal femur) → splits into **medial tendon** (→ claw + hook, group 2/3 compartments)
and **lateral tendon** (→ club, group 1). The arculum acts like a **slider-crank linkage**,
decomposing linear tibia-driven motion into two orthogonal vectors. The medial tendon
"reduces on-axis movements by as much as **30×**" relative to the lateral tendon. Claw
mechanosensory threshold is **>10× higher** than club's (ref. to Mamiya 2018).

**Arculum FE model (COMSOL 5.5, structural mechanics, linear elastic / Hooke).**
- Mesh: tetrahedral, "extremely fine"; min element **0.63 µm**, max **3.5 µm**;
  **>35 000 elements**.
- Density **1200 kg/m³** (insect cuticle); Poisson's ratio **0.3**;
  Young's modulus of arculum **3.6 MPa** (= 2× resilin, resilin taken as **1.8 MPa**);
  isotropic damping loss factor **0.5** on arculum and on the spring foundations.
- Four tendon boundary conditions, each a spring with
  ```
  k = E_res · A / L0          (E_res = 1.8 MPa resilin Young's modulus)
  ```
  | tendon | equilibrium length L0 (µm) | cross-section A (µm²) |
  |---|---|---|
  | joint tendon | 72 | 295.3 |
  | femoral (extensor) tendon | 225 | 295.3 |
  | medial tendon | 268 | 50.9 |
  | lateral tendon | 283 | 57.2 |

  (Computing k = E·A/L0 with E = 1.8 MPa: joint 7.38 N/m, femoral 2.36 N/m,
  medial 0.342 N/m, lateral 0.364 N/m — **my arithmetic, not printed in the paper**.
  The medial tendon's spring constant was then **halved** to represent a soft proximal
  coupling.)
- Joint, medial, lateral tendons modelled parallel to the femur long axis (x);
  extensor tendon at **45°** between x and z.
- Load: periodic **10 µN** force at the joint-tendon attachment along x ("approximates
  force levels known to be produced by *Drosophila* muscles"). Linear Hookean ⇒ response
  scales linearly with force. Frequency-domain sweep **2 Hz to 80 kHz** (2nd eigenfrequency
  of the system observed at the top end); 20 or 5 frequency steps per decade.
  The specific eigenfrequency values are **[?]** — not stated in the text I read.

**Claw/FeCO 2D FE model (COMSOL 6.1, truss + solid mechanics).**
- Medial tendon: 250 µm long cable, circular cross-section radius **2 µm**.
- Fibrils (tendon → cap cell): radius **0.2 µm**, radiating from a single tendon endpoint,
  angular gradient **16° to 180°** relative to the tendon long axis.
- Dendrites: **50 µm** long, radius **0.2 µm**; **20 dendrites** at **16°** to the medial
  tendon axis, plus **3 dendrites parallel** to it (most proximal claw cells).
- Cells as point masses, spheres of density 1200 kg/m³, radius **4 µm** (claw cell) and
  **2 µm** (cap cell).
- Surrounding tissue: solid, thickness **10 µm**, length **660 µm**, width **80 µm**,
  Young's modulus **1 kPa** (tested 100 Pa – 2 kPa; 1 kPa reproduced observed cell motion).
  Trade-off noted: 100 µm thickness ⇒ 100 Pa to match.
- Young's moduli: medial tendon and fibrils **1.8 MPa** (resilin); claw-cell ciliated
  dendrites **178 kPa** (published ciliary estimate). Poisson 0.3 everywhere.
  Isotropic loss factor **0.8** on truss and solid.
- Mesh: 20 edge elements per truss; solid min element **0.08 µm**, max **24.4 µm**;
  **6717 triangle elements + 1589 edge elements**.

**Kinematic driving of the FeCO model (the bit you'd use for a joint-angle → strain map).**
- Measured arculum centre-of-mass motion from **flexion to extension, 12° → 176°, at
  3.28 °/s over 50 s**.
- Tendon-cut experiments: with tibia flexed, the most distal cap cell moved a maximum of
  **35 µm** to its equilibrium position; at full extension it sat **9 µm** from equilibrium.
  The model was pre-tensioned to reproduce the 35 µm, then driven with the measured
  arculum trajectory.
  ⇒ Implied distal-cap-cell excursion ≈ **26 µm over 164°** ≈ **0.159 µm/deg**
  (**my arithmetic**, and it is cap-cell displacement, *not* tendon displacement; the
  paper does not print a µm-per-degree tendon figure).
- Model protocol: neutral 0–3.5 s, tensioning 3.5–6.5 s, equilibration 6.5–10 s, then
  displacement with the measured dynamics; only steady state analysed.

**Result to encode.** Dendritic strain is **highest in the most distal dendrite and decays
proximally**; strain **peaks when the tibia is flexed** and falls as it extends. Three
ingredients are necessary: fan-like fibril array, soft surrounding tissue, tendon/dendrite
stiffer than tissue. This is the mechanistic basis of the **goniotopic map** — the
position-tuned claw cells are ordered along the proximal-distal femur axis.

Vibration psychophysics in the same paper: tibia vibrated **100–1600 Hz** (piezo,
Thorlabs open-loop; command sine power drops above 2000 Hz; 10 kHz sampling; 4 s
vibration × 2, 8 s ISI). Club response center shifts with frequency; response amplitude
**plateaus around 800 Hz**.


### 4.3 Agrawal, Dickinson, Sustar, Gurung, Shepherd, Truman & Tuthill 2020 **[V]**

**Citation.** Sweta Agrawal, Evyn S Dickinson, Anne Sustar, Pralaksha Gurung, David
Shepherd, James W Truman, John C Tuthill (2020). "Central processing of leg
proprioception in *Drosophila*." *eLife* **9**:e60299. DOI: 10.7554/eLife.60299.

This is about the **downstream** VNC circuit (13Ba, 9Aa, 10Bc cell types), not about
encoding from kinematics. It identifies three second-order cell types receiving input
from FeCO subtypes encoding tibia position, movement and vibration. 13Ba neurons encode
femur-tibia joint position. **No fitted encoder equation.** Useful only as the target of
an FeCO encoder (i.e. what the sim's encoder output would project to).
**Checked the full PDF for any fitted encoder: there is none.** No linear-nonlinear model,
no GLM, no sigmoid/Boltzmann fit, no regression. Responses are reported as whole-cell
membrane-potential and spike-rate traces. Grep for "encoding model", "sigmoid", "GLM",
"regression", "tuning curve fit" returns nothing.

Facts worth keeping (verbatim/near-verbatim) **[V]**:
- Abstract: "**13Ba** neurons **encode femur-tibia joint angle** and mediate postural changes
  in tibia position. **9Aa** neurons also drive changes in leg posture, but encode a
  **combination of directional movement, high frequency vibration, and joint angle**.
  Activating **10Ba** neurons, which **encode tibia vibration at specific joint angles**,
  elicits pausing in walking flies."
- "13Ba neurons encode tibia position via **tonic changes in membrane potential**."
  Steady-state activity measured "during the middle second of each 3 s step" of a
  ramp-and-hold protocol, plotted separately for flexion and extension ⇒ **hysteresis**,
  same as the claw afferents.
- "every **9Aa** cell was maximally depolarized by **1600–2000 Hz** vibrations, and response
  magnitude increased at higher vibration amplitudes." Some 9Aa cells were *inhibited* by
  lower-frequency vibration (sharper frequency tuning); cells varied in adaptation rate.
  Vibration response abolished by MLA (nicotinic block) ⇒ cholinergic input from FeCO club
  neurons; inhibitory low-frequency responses abolished by picrotoxin.
- Motor: max speed **533,333 °/s**, max acceleration **83,333.33 °/s²**, position resolution
  **0.045°** (QuickSilver Controls). Imaging at 8.01 Hz; ephys filtered 10 kHz, digitised at
  20 kHz (Axon Digidata 1400A).

Useful as the *target* of an FeCO encoder (what the encoder output should project to), and
as a cross-check that a claw-like position channel must be tonic with hysteresis and a
club-like channel must peak above 1.6 kHz.

---

## 4b. Hair plates — Pratt et al 2026 (Nature Communications)

**Citation.** Brandon G. Pratt, Chris J. Dallmann, Grant M. Chou, Igor Siwanowicz,
Sarah Walling-Bell, Andrew Cook, Anne Sustar, Anthony Azevedo, John C. Tuthill (2026).
"Proprioceptive limit detectors contribute to sensorimotor control of the *Drosophila*
leg." *Nature Communications* **17**:2664. DOI: 10.1038/s41467-026-69333-z.
Received 25 Jul 2025, accepted 28 Jan 2026. **[V]**

**No encoder equation either** — calcium imaging (GCaMP7f + tdTomato) of CxHP8 axons in
the VNC with simultaneous DeepLabCut/Anipose 3D joint tracking. But it gives the
*functional form* to implement for hair plates: a **limit detector / threshold-nonlinearity
on joint angle**, tonic, not phasic.

- Organ: **CxHP8**, a hair plate at the **thorax-coxa joint**, anterior position;
  8 cells per leg; the CxHP8-GAL4 line labels 6/8 on front legs, 3/8 on middle legs.
- Encoded variables: thorax-coxa **rotation** and **adduction** angle (and, more weakly
  and with greater variability, **flexion**). Increasing rotation = coxa rotating inward;
  increasing adduction = coxa translating medially.
- Tuning: calcium activity **peaks when the coxa is inwardly rotated and adducted**,
  i.e. at the **anterior extreme of leg movement**. Explicit statement: "we found no
  evidence for phasic tuning" ⇒ model as a position-threshold (sigmoid/ReLU on angle),
  no velocity term.
- Connectivity (for downstream wiring, not encoding): CxHP8 axons put **75% of output
  synapses (2279 ± 482 synapses per axon)** onto premotor (58%) and motor (17%) neurons.
  Wired to **excite posterior leg movement and inhibit anterior leg movement** —
  a negative-feedback limit reflex.
- Behavioural bout classification thresholds used (Methods): forward walking = ball
  translational velocity > 5 mm/s and rotational velocity < 25 °/s; left turns
  rotational velocity < −25 °/s and > −50 °/s; right turns > 25 °/s and < 50 °/s;
  video at 200 fps; calcium images Gaussian-filtered σ = 3 px, 5×5 px.
- They explicitly flag the missing piece: coupling hair-plate signalling to the
  open-source **Janelia fly body Blender model** to "simulate hair plate signaling"
  is future work. So: no existing hair-plate encoder implementation.

---

## 4c. Second-order leads worth chasing (from Szczecinski's WVU publication list) **[V that these exist]**

Verified by reading https://nicholasszczecinski.faculty.wvu.edu/publications (fetched
2026-09-21). Verbatim entries:

- **Saltin BD, Goldsmith CA, Haustein M, Bueschges A, Szczecinski NS, Blanke A (2025)
  "A parametric finite element model of leg campaniform sensilla in *Drosophila* to study
  campaniform sensilla location and arrangement." *J. R. Soc. Interface* 22:20240559.**
  DOI 10.1098/rsif.2024.0559. PMC12056673. ← **most Drosophila-specific CS mechanics paper
  that exists.** See §11 below.
- Dinges GF, Kudyba IM, Szczecinski NS (2026) "Resin models of *Drosophila* strain sensors
  highlight mechanical pre-filtering of sensory inputs." *Bioinspir. Biomim.*
  DOI 10.1088/1748-3190/ae5e11.
- Dinges GF, Zyhowski WP, Lucci A, Friend J, Szczecinski NS (2024) "Mechanical modeling of
  mechanosensitive insect strain sensors as a tool to investigate exoskeletal interfaces."
  *Bioinspir. Biomim.* 19. DOI 10.1088/1748-3190/ad1db9.
- **Harris CM, Szczecinski NS, Bueschges A, Zill SN (2022) "Sensory signals of unloading in
  insects are tuned to distinguish leg slipping from load variations in gait." *J
  Neurophysiol* 128:790–807.** DOI 10.1152/jn.00285.2022, PMC9529259. **[V]** — reuses the
  2021 CS model verbatim (same y and τẋ equations, quoted below) and shows it reproduces
  unloading responses and viscoelastic "creep" of cuticle. It adds no new parameter table.
  Its framing of x is useful: "The low-pass filtered force variable x functions like a
  **dynamic threshold**". It also notes the model is **descriptive, not mechanistic** —
  "none of the model parameters (a, b, c, d) relate to specific mechanical or
  electrochemical processes".
- **Zill SN, Dallmann CJ, Zyhowski WP, Chaudhry H, Gebehart C, Szczecinski NS (2024)
  "Mechanosensory encoding of forces in walking uphill and downhill: force feedback can
  stabilize leg movements in stick insects." *J Neurophysiol* 131:198–215.**
  DOI 10.1152/jn.00414.2023, PMC11286306.
- **Zill SN, Dallmann CJ, Szczecinski NS, Büschges A, Schmitz J (2021) "Evaluation of force
  feedback in walking using joint torques as 'naturalistic' stimuli." *J Neurophysiol*
  126:227–248.** DOI 10.1152/jn.00120.2021, PMC8424542.
- Goldsmith CA, Haustein M, Bueschges A, Szczecinski NS (2024) "A biomimetic fruit fly
  robot for studying the neuromechanics of legged locomotion." *Bioinspir. Biomim.* 19.
  DOI 10.1088/1748-3190/ad80ec.
- Zyhowski WP, Zill SN, Szczecinski NS (2023) "Adaptive load feedback robustly signals
  force dynamics in robotic model of *Carausius morosus*." *Front. Neurorobot.*
  (the page lists DOI 10.3390/biomimetics7040226, which looks like a copy-paste error on
  their site — **could not verify** the correct DOI).
- **Zadokha B, Szczecinski NS (2024) "Encoding 3D Leg Kinematics Using
  Spatially-Distributed, Population Coded Network Model." Living Machines 2024.**
  DOI 10.1007/978-3-031-72597-5_22. ← a chordotonal-style population encoder for 3D leg
  kinematics. **Not retrieved — paywalled Springer chapter, no preprint found.**
- Conference version of the CS model, full citation confirmed from Harris 2022's reference
  list: **Szczecinski NS, Zill SN, Dallmann CJ, Quinn RD (2020) "Modeling the dynamic
  sensory discharges of insect campaniform sensilla." In: Biomimetic and Biohybrid Systems,
  Living Machines 2020, LNCS vol. 12413, pp. 342–353. Springer, Cham.**
  DOI 10.1007/978-3-030-64313-3_33. **[V]**

---

## 5. Open gaps (things I could not get)

- **Zill et al 2025 blow fly (*Calliphora*) CS model equations and fitted parameters** —
  §6. Publisher-only, Cloudflare-blocked, no PMC, no preprint. This is the single most
  valuable missing number for a fly-scale CS encoder.
- **Saltin et al 2025 numeric parameter tables** — §11. Read second-hand from the bioRxiv
  preprint; the authoritative COMSOL 5.6 files are on Zenodo (zenodo.org/records/14870197)
  and should be opened directly.
- **Zadokha B, Szczecinski NS (2024) "Encoding 3D Leg Kinematics Using
  Spatially-Distributed, Population Coded Network Model", Living Machines 2024,
  DOI 10.1007/978-3-031-72597-5_22** — a chordotonal-style population encoder for 3D leg
  kinematics. Paywalled Springer chapter, no preprint found.
- **Bässler's stick-insect FT-joint transfer functions** — §14. Widely referred to as a
  weighted position + velocity + acceleration sum, but I could not find a published
  closed-form equation with numeric gains. Primary sources are 1970s–80s, partly German.
- **Hofmann, Koch & Bässler 1985 (JEB 114:207–223) quantitative fCO sensitivities** —
  paywalled; the qualitative classification is in §14.
- **NeuroMechFly joint angular limits / ranges of motion** — §7.3. Not in the v1 preprint
  text; read them off the MJCF in `flygym/data/mjcf/` or the v1 URDF.
- **Cocatre-Zilgien & Delcomyn 1999** CS model (hyperbolic tonic + power-law adaptation) —
  cited by van der Veen 2025 but not retrieved; would be the third independent CS encoder.
- **Dean 1985** trochanteral hair-field phasic-tonic f(joint angle) — same, not retrieved.
- **Gollin & Dürr 2018** "Estimating body pitch from distributed proprioception in a
  hexapod" (Living Machines; also cited by NeuroMechFly v2 as ref [49]) — analog response
  function plus stochastic spike generator; not retrieved.

---

## 6. Campaniform sensilla in blow flies — Zill, Chaudhry, Chaudhry & Szczecinski 2025

**Citation (verified via NCBI eutils / PubMed record, 2026-09-21).** Zill SN, Chaudhry S,
Chaudhry H, Szczecinski N (2025). "Force sensing in small animals: recording response
properties and modeling of tibial campaniform sensilla in blow flies."
*J Neurophysiol* **133**(6):1749–1760. DOI: 10.1152/jn.00044.2025. PMID 40331748.
Epub 7 May 2025, issue 1 Jun 2025. **[V for citation]**

**Species: blow fly *Calliphora vicina*, hindleg tibial CS group — NOT *Drosophila*.**
(Closest dipteran data to a fruit fly that exists for CS, but a much larger fly.)

Verbatim from the abstract:
- Forces applied as **ramp-and-hold** with joint movements resisted "elicited discharges
  that reflected both the force magnitude and rate of change of forces."
- "sensory signals showed **hysteresis** and firing was **strongly inhibited by small
  phasic decreases** when forces were applied as waveforms that gradually increased to
  reach a level (**asymptotic exponential functions**)."
- "These results were also tested in **a mathematical model of force encoding by
  campaniform sensilla in larger insects**, which successfully reproduced the receptor
  responses." ⇒ i.e. they reused the Szczecinski et al. 2021 model (§1), they did not
  introduce a new one.
- Conclusion: "force detection **scales to body weight**".

**Model equations and fitted parameters for the blow fly: COULD NOT VERIFY.** The paper
is "bronze" OA only on journals.physiology.org, which is behind Cloudflare and returns
403/challenge to both WebFetch and curl. There is no PMC record, no Europe PMC full text,
no preprint I could find. If someone can get the PDF, the thing to pull is whether Table-2-
style (a, b, c, d, τ) values were re-fitted for *Calliphora* — those would be the closest
available starting parameters for a fly-scale CS encoder, since the cockroach/stick-insect
values in §1.3 are calibrated to mN forces from animals orders of magnitude heavier.

---

## 7. NeuroMechFly v1 — Lobato-Rios et al 2022

**Citation.** Victor Lobato-Rios, Shravan Tata Ramalingasetty, Pembe Gizem Özdil,
Jonathan Arreguit, Auke Jan Ijspeert, Pavan Ramdya (2022). "NeuroMechFly, a
neuromechanical model of adult *Drosophila melanogaster*." *Nature Methods*
**19**:620–627. DOI: 10.1038/s41592-022-01466-7. PMID 35545713.
(Volume:pages and author list verified via Europe PMC metadata. **[V]**
Content below read from the bioRxiv v3 preprint, doi 10.1101/2021.04.17.440214,
posted 11 Nov 2021 — so text may differ slightly from the published version. **[V, preprint]**)

### 7.1 Sensor signals — again, no proprioceptor model

v1 runs in **PyBullet** (not MuJoCo; the MuJoCo/flygym rewrite is v2). It gives access to
"collisions, reaction forces, and torques". The pitch is explicitly that you can *infer*
"otherwise unmeasured torques and contact reaction forces" — "quantities that remain
technically challenging to measure in small animals" — and the paper frames these as
"a readout of an animal's proprioception and mechanosensation". But there is **no FeCO,
campaniform-sensillum or hair-plate model**; the output is raw joint torques, ground
reaction forces (GRFs), and tactile contacts.

### 7.2 Degrees of freedom (Table 1, verbatim)

| Body part | Segment | Parent | DoF |
|---|---|---|---|
| Abdomen | A1A2 / A3 / A4 / A5 / A6 | chain from Thorax | 1 each (5) |
| Head | Head capsule | Thorax | 3 |
| Head | Eyes (×2) | | 0 |
| Head | Antennae (×2) | Head | 1 each |
| Head | Rostrum | Head | 1 |
| Head | Haustellum | Rostrum | 1 |
| Legs | Coxa (×6) | Thorax | 3 |
| Legs | Trochanter/Femur (×6) | Coxa | 2 |
| Legs | Tibia (×6) | Femur | 1 |
| Legs | Tarsus1 (×6) | Tibia | 1 |
| Legs | Tarsus2–5 (×6 each) | chain | 1 each |
| Thorax | Halteres (×2) | Thorax | 3 each |
| Thorax | Wings (×2) | Thorax | 3 each |
| Thorax | Thorax | — | 0 |

⇒ **7 actuated DoFs per leg** = ThC (3: yaw/pitch/roll, i.e. elevation-depression,
protraction-retraction, rotation) + CTr (2: pitch + **roll**) + FTi (1) + TiTa (1)
= **42 leg DoFs total**, carried straight into v2/flygym.

The central methodological result of v1: the six previously reported leg DoFs are **not
enough** — adding a **coxa-trochanter (CTr) roll** DoF significantly and uniquely reduced
forward-kinematics discrepancy, whereas CTr yaw, FTi roll, FTi yaw, TiTa roll and TiTa yaw
did not (Table 2 p-values; e.g. Base vs Base&CTr-roll p = 0.00, Base vs Base&TiTa-roll
p = 9.95e-01 i.e. no difference). So 7 DoF/leg is an empirical finding, not a convention.

### 7.3 Simulation and controller constants **[V, preprint]**

- Physics: PyBullet, **time step 0.5 ms** for kinematic replay; CPG ODEs integrated with
  an explicit **Runge-Kutta 5th order, time step 0.1 ms**.
- Position control error law: `error = Kp·(θr − θa) + Kd·(ωr − ωa)` (their eq 5).
  Gain sweep Kp, Kd ∈ [0.1, 1.0] step 0.1 (100 sims); **chosen Kp = 0.4, Kd = 0.9**.
  Joint angular velocities computed with a **Savitzky-Golay** filter, first-order
  derivative, time step 0.5 ms.
- Segment masses: head **0.125 mg**, thorax **0.31 mg**, abdomen **0.45 mg**,
  wings **0.005 mg**, legs **0.11 mg**.
- PyBullet contacts by penetration depth; contact parameter 0.02 length units (1 unit =
  1 m SI) ⇒ they **dynamically rescale** the model so bodies exceed 0.02 units.
- CPG intrinsic frequency ν treated as open parameter in **6–10 Hz**; duty factor
  constrained to [0.4, 0.9].
- Fixed (non-actuated) leg joint angles during optimisation (Table 5, deg):
  front TiTa −39, middle TiTa −54, hind TiTa −45; middle ThC yaw ±7.45, ThC pitch −5;
  hind ThC yaw ±3.45, ThC pitch 6.2; front ThC roll ±10; CTr roll 0 for all.
- X-ray µCT for the mesh: Hamamatsu L10711/-01 source, 40 kV.

**Published joint limits / ranges of motion: could not verify.** The preprint mentions
"joint ranges of motion" as a modelled property but I found no table of per-DoF angular
limits in the preprint text. The authoritative source would be the URDF/SDF in
github.com/NeLy-EPFL/NeuroMechFly, or the MJCF in `flygym/data/mjcf/` for v2.

---

## 8. Karashchuk et al 2025 — proprioceptive feedback + sensorimotor delays

**Citation.** Lili Karashchuk, Jing Shuang Li, Grant M Chou, Sarah Walling-Bell,
Steven L Brunton, John C Tuthill, Bingni W Brunton (2025). "Sensorimotor delays constrain
robust locomotion in a 3D kinematic model of fly walking." *eLife* **13**:RP99005.
DOI: 10.7554/eLife.99005 (version of record DOI 10.7554/eLife.99005.3, published
2025-05-15). PMID 40372779. bioRxiv 10.1101/2024.04.18.589965. **[V]**

### 8.1 Proprioceptive feedback used **[V, quoted]**

> "Proprioceptive feedback consists of **joint angles and angular velocities**
> (Mamiya et al., 2018)."

That is the whole sensory channel — **no force/load feedback, no CS, no hair plates,
no spike-rate encoder**. The controller consumes (θ, θ̇) delayed by the sensory delay.

### 8.2 Delay values — the key numbers **[V, quoted]**

> "All simulations used a **sensory delay of 10 ms and a motor delay of 30 ms**, based on
> values measured experimentally with electrophysiology from leg sensory and motor
> neurons/muscles (Tuthill and Wilson, 2016b; Azevedo et al., 2020)."

Physiological estimates and their provenance, verbatim:
- **Sensory delay 5–15 ms** — "based on the measured delay from spike initiation in a
  mechanosensory neuron in the *Drosophila* femur to the peak of an excitatory
  postsynaptic potential in a postsynaptic VNC neuron (Tuthill and Wilson, 2016b)."
- **Motor delay 20–40 ms** — "based on the time between spike initiation in a tibia motor
  neuron cell body to the onset of muscle force production, measured with a force probe
  (Azevedo et al., 2020)."

Robustness limits found:
> "the model maintained realistic walking (KS > −1.6) up to about **30 ms of motor delay
> and 10 ms of sensory delay** ... When we allowed both motor and sensory delay to vary,
> the model maintained realistic walking when **the sum of the delays was no more than
> about 45 ms**."

Delay grids swept: motor 10/20/30/40 ms, sensory 0/5/10/15 ms **[S — these specific grid
values came from a page-reading summary, not from text I extracted myself; the 0 ms and
5 ms sensory points are corroborated by a verbatim sentence "even at low values of
sensory delay (0 ms, 5 ms)" **[V]**]**.

### 8.3 Architecture and rates **[V, quoted]**

Three layers: trajectory generator (learned from data, runs at **300 Hz**) → optimal
controller per leg (**600 Hz**) → phase coordinator (Kuramoto, all-to-all, the only
inter-leg information). "We run the full model at 600 Hz. At each time step, we first
update the phases of the legs φᵢ ... Every 2 timesteps, we update the target joint angles."

Phase coupling (MathML stripped in the source I could extract, so reconstructed shape):
`φ̇ᵢ = Fᵢ(θᵢ, θ̇ᵢ, v, φᵢ) + α · Σ_{j≠i} sin(φⱼ − φᵢ − φ̄ᵢⱼ)`, all-to-all coupling,
`φ̄ᵢⱼ` = steady-state phase offset estimated as the circular mean of pairwise phase
differences in real walking data, modelled as speed-independent.
**Coupling strength α = 6.5 [S]** — reported by a page-reading pass; the number sits
inside MathML that I could not extract verbatim, so treat as unconfirmed.

Leg dynamics: link-and-joint model, Denavit-Hartenberg table, Euler-Lagrange
`τ = M(θ)θ̈ + C(θ,θ̇)θ̇ + F θ̇ + G(θ)` (their eq 4, symbol names verified: "inertia,
Coriolis, and friction matrices, and G is the gravity vector"), linearised about mean
joint angles, then LQR/LQG with delay compensation by prediction.

Joints modelled per leg (Table 1; text verified): femur rotation included **only for
middle and hind legs** because front legs show near-constant femur rotation. So the
per-leg joint set is 3 (front) vs 4 (middle/hind) **[S for the exact 3/4 split, from a
page-reading summary; the "femur rotation for middle and hind only" rationale is [V]]**.

Data: tethered fly on a frictionless air-suspended ball, 6 Basler acA800-510µm cameras at
**300 Hz**, Anipose, **30 keypoints** = 5 per leg (body-coxa, coxa-femur, femur-tibia,
tibia-tarsus joints + tarsus tip). 3049.7 s of walking = 914,909 frames.
Markerless 3D tracking uncertainty **5.56 degrees** (Karashchuk et al. 2021).
Default forward speed 12 mm/s; perturbation strength 1.875 rad/s.
Statement worth keeping: "Each fly leg has **five joints that move through seven
mechanical degrees of freedom**" (citing Karashchuk 2021 and Lobato-Rios 2022), actuated
by ~18 muscles innervated by ~70 motor neurons (Azevedo et al. 2024).

---

## 9. Spiking proprioceptor encoder — van der Veen, Cohen, Chicca & Dürr 2025 (best off-the-shelf kinematics→spikes model)

**Citation.** Thomas van der Veen, Yonathan Cohen, Elisabetta Chicca, Volker Dürr (2025).
"A spiking neural network model for fractional proprioceptive encoding of limb posture and
movement in insects." *Biological Cybernetics*. DOI: 10.1007/s00422-025-01032-2.
PMID 41762245, PMC12950026. Open access (CC BY). Code:
https://zenodo.org/doi/10.5281/zenodo.13827523 (Python/Jupyter; experimental data under
`sim_data`). A **companion paper** (van der Veen et al. 2025) extends to 2nd/3rd-order
interneurons. **[V]**

This is the closest thing that exists to a drop-in "joint angle → afferent spike train"
encoder for insect legs, and it is explicitly designed for hair fields but argued to
transfer to the FeCO ("mechanosensory neurons of the femoral chordotonal organ ... share
important encoding features with mechanosensory neurons of proprioceptive hair fields,
such as sensitivity to joint angle, joint angle velocity (Hofmann et al. 1985), and range
fractionation (Matheson 1992; Ache and Dürr 2013)"). Species: afferent dynamics fitted to
**cockroach (*Periplaneta americana*) antennal scapal hair plate** data (Okada & Toh
2001); downstream decoding evaluated against **stick insect (*Carausius morosus*)** whole-
body motion capture (Theunissen & Dürr 2013; Vicon MX10, 8 IR cameras, 200 fps, walkway
40 × 490 mm, 9 specimens).

### 9.1 Layer 1 — joint angle → per-hair deflection angle

Each hair has a receptive field; the array tiles the joint's working range with overlap.
Hair deflection assumed **linearly proportional to joint angle**, clipped to [0°, 90°].

Standard orientation (their eq 1) and opposing orientation (their eq 4), as rendered:

```
θ_hair,i,j = clip( (θ_joint − θ_lower^j) / (θ_upper^j − θ_lower^j) × 90°, 0°, 90° )
θ_hair,i,j = clip( (θ_neutral − θ_joint) / (θ_neutral − θ_lower^j) × 90°, 0°, 90° )
```
**[S — equations transcribed by a page-reading pass; the MathML did not survive my own
XML extraction, so the exact index conventions are unconfirmed. The surrounding prose IS
verified: linear proportionality, clipping, per-hair receptive fields set from the min/max
joint angles attained by that joint, uniform receptive-field size and spacing within a
field, an overlap parameter equal across hair fields, outer hairs' receptive fields set
manually.]**

Hair fields are **bi-directional**: modelled as opposing pairs (as in the antennal
(Krause et al. 2013) and coxal (Wendler 1964) hair fields of stick insects). **[V]**

### 9.2 Layer 1 — deflection → current → spikes (AdEx)

Transduction, verbatim: "the hair angles calculated in Eqs. (1) and (4) were multiplied by
**10–150 [pA/degree]**, yielding **currents in the nA range**." **[V for the 10–150 range
and the nA statement; the pA/degree unit label is [S].]**

AdEx (Brette & Gerstner 2005):
```
C·dV/dt  = −g_L (V − E_L) + g_L Δ_T exp((V − V_T)/Δ_T) − w + I
τ_w·dw/dt = a (V − E_L) − w
on spike (V ≥ V_spike):  V → V_reset ,  w → w + b
```

**Table 1 parameter values, verbatim from the article's Table 1 markup [V]:**

| neuron | model | C | (g_L or a) | Δ_T | a | τ_w | b | τ_m | w_syn |
|---|---|---|---|---|---|---|---|---|---|
| Sensory | AdEx | 200 pF | 2 nS | 2 mV | 2 nS | 50 ms | 264 pV | – | – |
| Position IN | LIF | – | – | – | – | – | – | 120 ms | 1 mV |
| Velocity IN | LIF | – | – | – | – | – | – | 5 ms | 10.8 mV |

⚠ The table's column headers are images in the source, so the mapping of the two "2 nS"
columns to g_L vs a is from a page-reading pass, not from markup I could read. Also
`b = 264 pV` is printed with voltage units where spike-triggered adaptation is normally a
current (pA) — reproduce with care. Additional values reported by the page-reading pass
but **not** visible in the table markup: `E_L = −70 mV`, `V_T = −50 mV`,
`V_reset = −70 mV` (AdEx), `V_T = −50 mV` (both LIFs). **[S]**

### 9.3 Layer 2 — first-order interneurons

Two LIF interneuron types per hair field pair, both giving "a linear relation between an
input current and output spike rate":
- **Position INs**: long membrane time constant (τ_m = 120 ms), small synaptic weight
  (w_syn = 1 mV) ⇒ integrator, encodes joint angle across the whole working range.
- **Velocity INs**: short τ_m = 5 ms, large w_syn = 10.8 mV ⇒ high-pass/coincidence
  detector, **spike rate increases linearly with angular velocity**, direction-selective.
  Note in the text: "Strong linearity was achieved only when [w_syn] equalled [threshold
  distance]. At this synaptic strength, [one EPSP] marginally exceeded [threshold],
  allowing spikes from small phasic fluctuations to transmit through the high-pass filter."

### 9.4 Simulation and performance **[V for the performance numbers]**

- Python 3.9, backward-difference solver. Time step reported as **Δt = 0.1 ms [S]**
  (the value is an image in the XML).
- Architecture scale: 3 joint angles × 6 legs = **18 joints**, "3 sets of two hair field
  implementations per leg", each hair field with N_h hairs, bidirectional. N_h = 50 per
  field (100 per joint) **[S]**.
- Position IN accuracy (Table 2, normalised MSE ± SD, **[V]**):
  front 0.0317 ± 0.0071, middle 0.0310 ± 0.0105, hind 0.0296 ± 0.0060; by joint type
  0.0266 ± 0.0046, 0.0389 ± 0.0075, 0.0268 ± 0.0047. Leg-type × joint-type interaction
  F(2, 69) = 11.11, p = 4.90e-?? (exponent lost in extraction).
- Velocity IN treated as a binary (direction) classifier, confusion matrix **[V]**:
  TP 1 627 811, FN 155 707, FP 155 167, TN 1 689 086 ⇒ **accuracy 0.914, TPR 0.913,
  TNR 0.916**.

### 9.5 Its own literature review = the map of prior proprioceptor encoders **[V, quoted]**

Worth keeping verbatim, because it is the most compact survey of exactly what this task
was asking for:

> "Cocatre-Zilgien and Delcomyn (1999) modeled the afferent spike rate of **campaniform
> sensilla** by means of a **two-stage stimulus-response function**, where the first stage
> captured the tonic component as a **hyperbolic function of strain** (in analogy to
> vertebrate mechanoreceptors: Loewenstein 1961), and the second stage implemented phasic
> adaptation by means of a **power law**, as previously proposed for mechanoreceptor
> adaptation in cockroaches (Chapman and Smith 1963; French 1984). Applying a similar
> approach to hair fields, 'total afferent activity' of the stick insect **trochanteral
> hair field** has been simulated using a **phasic-tonic function of spike rate on joint
> angle** (Dean 1985). In contrast, sensory array models involve multiple parallel receptor
> models. For example, **Ache and Dürr (2015) applied cascaded low-pass and high-pass
> filter blocks** to model different stages of proprioceptive encoding of antennal position
> and velocity in stick insects. Similarly, **Szczecinski et al. (2021)** modeled
> phasic-tonic changes in a strain-sensitive campaniform sensillum. While this kind of
> analog stimulus-response functions may be combined with **stochastic spike generators**
> to generate time sequences of spike time events (e.g., **Gollin and Dürr 2018**), there
> is a lack of a spiking proprioceptor model that generates spike trains directly through
> subthreshold membrane potential dynamics."

So the complete set of named prior encoders is:
1. Cocatre-Zilgien & Delcomyn 1999 — CS, hyperbolic tonic + power-law adaptation.
2. Dean 1985 — hair field, phasic-tonic f(joint angle).
3. Ache & Dürr 2015 — antennal hair field array, cascaded LP/HP filter blocks
   (PLoS Comput Biol 11(7):e1004263, "A Computational Model of a Descending Mechanosensory
   Pathway Involved in Active Tactile Sensing"). **Fully extracted — see §10.**
4. Szczecinski et al. 2021 — CS, §1 above.
5. Gollin & Dürr 2018 — analog response function + stochastic spike generator.
6. van der Veen et al. 2025 — this paper, AdEx spiking.

---

## 10. Hair-field afferent encoder — Ache & Dürr 2015 (filter-cascade, fully specified)

**Citation.** Jan M Ache, Volker Dürr (2015). "A Computational Model of a Descending
Mechanosensory Pathway Involved in Active Tactile Sensing." *PLoS Computational Biology*
**11**(7):e1004263. DOI: 10.1371/journal.pcbi.1004263. Published 9 July 2015. Open access.
**[V — read the printable PDF]**

Organ: stick insect (*Carausius morosus*) **antennal scape-pedicel (Sc-Pd) hair fields**;
afferent parameters tuned to match **cockroach antennal hair field sensilla** recordings
(their ref [20]). Not a leg organ and not *Drosophila* — but it is the cleanest fully
specified joint-angle → spike-train encoder in the literature, and the structure ports
directly to leg hair plates.

### 10.1 Structure (verbatim description)

1. Two hair rows, one on each side of the joint (dorsal, ventral). **20 hairs per row**
   ("a conservative estimate of the average number of hairs in the stick insect"), so
   **2 × 20 = 40 mechanosensory afferents**.
2. "The spacing of hairs was assumed such that the **number of deflected hairs varied
   linearly with antennal joint angle**." Dorsal hairs deflected only for Sc-Pd angle > 0°,
   ventral only for < 0°. At rest (0°) no hairs deflected ⇒ no afferent activity.
3. "the deflection angle of each hair ... was assumed to **vary linearly with the Sc-Pd
   joint angle within the hair's sensitivity range**."
4. Activation = **LPF(hair angle)·w_LP + HPF(hair angle)·w_HP**, then normalise, then
   subtract a constant Offset. "The resulting activation function can be viewed as the
   hypothetical membrane potential of the sensory afferent."
5. Filters: "linear **first-order** high- and low-pass filters with the time constant (tau)
   as the only variable."
6. Noisy spike generator (their unnumbered equation, verbatim):

```
spike(t) = 1  if  act(t) · dS · Rmax > rand ;   otherwise spike(t) = 0
```
   with rand ~ U(0,1). "dS was kept fixed at 1 ms, only Rmax was adjusted."
   "Spikes cannot be elicited at activation levels below zero. For activation levels
   between zero and one, the likelihood of a spike to be elicited at a given Rmax rises
   linearly." Each model afferent had an **absolute refractory period of 3 ms**.

### 10.2 Table 1 — hair field afferent parameters (verbatim) **[V]**

| N (hairs) | Range | Deflect. | LPF (tau/w) | HPF (tau/w) | Offset | Norm. | Rmax | dS |
|---|---|---|---|---|---|---|---|---|
| 20 | 2.5° | slope 1 | 10 ms / 2 | 30 ms / 20 | 35 | 100 | 300 1/s | 0.001 s |

Interpretation: each hair's sensitivity range spans **2.5°** of joint angle; 20 hairs × 2.5°
= 50° per row, matching a ±50° working range. The high-pass branch is weighted **10×** the
low-pass branch (20 vs 2), which is what makes the afferent phasic-tonic with a strong
velocity component.

Validated behaviour (Fig 4): "the **transient activity** of the sensory afferents during
ramp-and-hold stimuli was **proportional to the deflection velocity**, while the
**sustained activity** was **proportional to the deflection amplitude**." Deflection
velocities tested: **25, 50, 90, 150, 250 °/s**.

### 10.3 Table 2 — descending interneuron (DIN) variants (verbatim) **[V]**

Downstream of the afferents; included because it shows how to read a position and a
velocity channel out of the same afferent population.

| DIN type | LPF 1 (tau) | Wd | Wv | LPF 2 (tau/w) | HPF (tau/w) | Offset | rectify | Norm. | Rmax |
|---|---|---|---|---|---|---|---|---|---|
| SP v/d (simple position) | 5 ms | 0/1 | 1/0 | — | — | — | — | 4 | 10 |
| Ex.DP (dynamic extreme position) | 5 ms | 1 | 1 | 50/2 | 40/20 | −0.2 | — | 20 | 100 |
| ON (velocity, ON-type) | 5 ms | 1 | 1 | 50/2 | 40/20 | −0.2 | abs | 20 | 120 |
| DP v/d (dynamic position) | 5 ms | 0/1 | 1/0 | 50/2 | 40/20 | −0.2 | abs | 20 | 100 |
| OFF (velocity, OFF-type) | 5 ms | 1 | 1 | 50/2 | 40/20 | +1 | −abs | 40 | 30 |

(Wd, Wv = weights on dorsal and ventral hair field afferent pools. LPF2/HPF taus in ms.)

### 10.4 Why this is the best template for a sim encoder

- Inputs are exactly what a physics sim gives you: a scalar joint angle per DoF.
- Cost is trivial: two first-order filters and a Bernoulli draw per afferent.
- It gives you a graded *population* (range fractionation) rather than one number, which is
  what the FeCO claw array and the hair plates actually are.
- The van der Veen 2025 SNN (§9) is the direct successor: "In comparison with an earlier
  model (Ache and Dürr 2015), our present model **replaces filter blocks by a SNN**."

---

## 11. Drosophila-specific campaniform sensilla FE model — Saltin et al 2025

**Citation.** Brian D Saltin, Clarus Goldsmith, Moritz Haustein, Ansgar Büschges,
Nicholas S Szczecinski, Alexander Blanke (2025). "A parametric finite element model of leg
campaniform sensilla in *Drosophila* to study campaniform sensilla location and
arrangement." *J. R. Soc. Interface* **22**(226):20240559. DOI: 10.1098/rsif.2024.0559.
PMC12056673 (not open in Europe PMC). bioRxiv preprint 10.1101/2023.07.24.550300.
Dataset (COMSOL 5.6 model files, CAD geometry, MATLAB code, raw data):
https://zenodo.org/records/14870197. **[citation V via search + PMC metadata; content
below from a page-reading pass of the bioRxiv full text — treat as [S] and re-verify
against the Zenodo COMSOL files, which are the authoritative source.]**

What it is: a **parametric FE model of the femoral CS field on the *Drosophila* hind leg**,
with **12 general parameters for the CS field and 7 CS-specific parameters per sensillum**.
Driven with real kinematics + ground reaction forces for forward stepping.

Numbers reported by the page-reading pass **[S]**:
- Femur length **720.68 µm** (SEM triangulation); morphology sampled at 20 points × 10
  repeat measurements.
- Sensillum sub-elements modelled: cap, upper collar, lower collar, middle part, dome with
  attached nerve.
- Loading: **1/3 of 8.963 × 10⁻⁶ N** (i.e. ~2.99 µN, a third of body weight) applied in
  **7.5° increments** about the Y and Z axes; stance-phase force direction spans azimuth
  **5.31°–19.66°** and elevation **144.58°–65.57°**.
- Material: **linear elastic**, Young's modulus from Skordos (2002); anisotropy and
  viscosity omitted "due to lack of reliable experimental data".
- Main result: displacements at the CS field near the **trochanter-femur joint are small**
  and material-property changes have little influence.

**Crucially, the paper states there is no strain → spike mapping:** "it remains unknown at
which displacement/stress levels CS ... are activated." So this gives you a mechanical
front end (leg loading → cap strain, per sensillum, with directional selectivity from the
cap's elliptical orientation) but **no transducer**. Pair it with §1 (Szczecinski 2021) for
the transducer, using cap strain (or a scalar projection of it) as the `u` in
`y = max(0, a(u−x) + cu + d)`.

Related from the same group, worth a look for the strain front end:
- Dinges GF, Zyhowski WP, Lucci A, Friend J, Szczecinski NS (2024) *Bioinspir. Biomim.*
  19, DOI 10.1088/1748-3190/ad1db9 — mechanical modelling of insect strain sensors.
- Dinges GF, Kudyba IM, Szczecinski NS (2026) *Bioinspir. Biomim.*,
  DOI 10.1088/1748-3190/ae5e11 — "Resin models of *Drosophila* strain sensors highlight
  **mechanical pre-filtering** of sensory inputs" — i.e. the cuticle around the cap does
  part of the filtering before transduction.

---

## 12. The CS model's earlier conference version (different parameterisation!)

**Citation.** Szczecinski NS, Zill SN, Dallmann CJ, Quinn RD (2020). "Modeling the Dynamic
Sensory Discharges of Insect Campaniform Sensilla." In: *Biomimetic and Biohybrid Systems,
Living Machines 2020*, LNAI/LNCS vol. **12413**, pp. **342–353**. Springer, Cham.
DOI: 10.1007/978-3-030-64313-3_33. PDF at par.nsf.gov/servlets/purl/10202934. **[V]**

Note the **letters mean different things** here than in the 2021 journal paper — do not
mix the two parameter sets up:

```
y = max(0, a·(u − x) + b·u + c)                (their eq 11)
τ·ẋ = sign(u − x)·|u − x|^d                    (their eq 12)
```
"y is the instantaneous firing frequency (Hz) of afferent nerves from a population of CS;
u is the instantaneous loading (mN) of the limb segment in the CS population's [receptive
field]".

**Table 1 (verbatim) [V]** — cockroach *Periplaneta americana* tibial CS:

| Parameter | Description | Value |
|---|---|---|
| a | Adaptation term scale | 1088 |
| b | Proportional term scale | 40.45 |
| c | Constant offset | −52.84 |
| d | Exponent in low-pass filter function, f(z) = z^d | 2.369 |
| τ | Time constant for ẋ | 2.668 × 10³ |

⚠ τ = 2.668 × 10³ is printed with **no unit**. The 2021 journal fits give τ in
**milliseconds** and of order 1.7–9.7 ms, so 2.668 × 10³ is almost certainly
2.668 × 10⁻³ s = 2.668 ms (or a µs figure), but I am reporting exactly what the table
says. **Use the 2021 Table 2 values (§1.3), not these.**

Stimulus protocol used for tuning **[V]**: hold amplitude **1.66 mN** for all stimuli;
ramp durations **0.125, 0.224, 0.456, 0.915 s**; each applied **11 times**; ramp phase split
into **20 bins**, spikes counted per bin → mean afferent firing frequency; so each dataset =
20 time points × 20 frequency samples averaged over 11 repetitions. Naturalistic
force waveforms from freely walking insects also applied (Dallmann et al 2016).

Derivation shown there (same as 2021 but stated more compactly):
`Δt = (T/A)·f⁻¹(τ·A/T)`, `x(t) = u(t − Δt)`, `y = a·f⁻¹(τ·u̇)`.
Special case f(z) = z ⇒ f⁻¹(z) = z ⇒ Δt = τ, a pure fixed lag independent of ramp rate;
the nonlinearity d > 1 is what makes Δt rate-dependent and produces the power law.

---

## 13. fCO in a neuromechanical joint model — Goldsmith, Szczecinski & Quinn 2020

**Citation.** Clarissa A Goldsmith, Nicholas S Szczecinski, Roger D Quinn (2020). "Response
of a Neuromechanical Insect Joint Model to Inhibition of fCO Sensory Afferents."
*Living Machines 2020*, LNCS **12413**:141–152. Springer.
DOI: 10.1007/978-3-030-64313-3_15. PDF: par.nsf.gov/servlets/purl/10202932. **[V]**

Relevant because it is the only place I found where fCO afferents are given an explicit
place in a closed-loop neuromechanical simulation (stick insect FTi joint, targeted at
Drosophibot, a *Drosophila*-modelled robot).

**The honest, important negative result, verbatim [V]:**

> "As the exact conversion between **fCO stretch and injected current has not been
> characterized**, we arbitrarily chose a stimulus strength of **5 nA** applied to the
> sensory neurons over 3.25 seconds. The stimulus ramps up to and down from the hold
> current over a period of 0.25 seconds."

So: **there is no published, calibrated joint-angle → fCO-afferent-activity function.**
Everyone either injects a hand-chosen current, or uses a filter cascade fitted to a
*different* organ (hair fields, §9–10), or stops at the mechanics (§4.2, §11).

Structure they do commit to **[V]**:
- fCO sensory neurons split into **four groups**: flexion-position, flexion-velocity,
  extension-position, extension-velocity (half of the afferents respond to fCO elongation
  = flexion, half to relaxation = extension).
- Each sensory neuron has an **arbitrary tonic noise of 0.01 mV**.
- Six spiking interneurons mediate delayed inhibition from the velocity neurons onto the
  non-spiking interneurons (NSI).
- NSIs are **non-spiking leaky integrators**:
  `C_m dV/dt = I_leak + I_syn + I_app`, `I_leak = G_m·(E_r − V)`.
- Sensory neurons and motor neurons are **integrate-and-fire**: same eq plus
  `if V = θ then V(t) ← E_r`; synaptic conductance jumps to G_max on a presynaptic spike
  then decays as `τ_s dG_s/dt = −G_s`.
- Muscle-fibre analog neuron: leaky integrator with time constant **2000 ms**.
- Limb mechanics: `J·θ̈ = τ_ext + τ_flex − k_spring·θ`.

---

## 14. Classical FeCO physiology (the data any encoder must fit) — no equations published

- **Hofmann T, Koch UT, Bässler U (1985).** "Physiology of the femoral chordotonal organ in
  the stick insect, *Cuniculina impigra*." *J Exp Biol* **114**(1):207–223. **[S]**
  Units classified as (a) **position**, (b) **position + velocity**, (c) **velocity**;
  "nearly all transitional forms exist between the position and velocity receptors";
  elongation-sensitive, relaxation-sensitive and bidirectional units; some position
  receptors peak at a joint extreme, others near mid-range; velocity units either span the
  whole working range or are **range-fractionated**. The quantitative sensitivities
  (imp/s per degree, per degree/s) are behind a paywall — **could not verify**.
- A **weighted position + velocity + acceleration transfer function** for fCO afferents is
  frequently attributed to Bässler's stick-insect FT-joint control-loop work, and FeCO
  neurons are described as encoding "position and the speed, acceleration and direction of
  joint rotation". **I could not verify any published closed-form weighted-sum equation
  with numeric gains.** If it exists it is in Bässler's German-language monographs /
  *Biol Cybern* papers from the 1970s–80s, which I could not retrieve. Treat the
  "P + V + A weighted sum" as folklore until someone puts eyes on the primary source.

---

## 15. Campaniform sensilla experimental references (source of the data the models fit)

Citations verified against Crossref (2026-09-21). **[V for bibliographic data only]**

- **Ridgel AL, Frazier SF, DiCaprio RA, Zill SN (2000).** "Encoding of forces by cockroach
  tibial campaniform sensilla: implications in dynamic control of posture and locomotion."
  *J Comp Physiol A* **186**:359–374. DOI 10.1007/s003590050436.
  ← the dataset behind the cockroach parameters in §1.3 and the power-law exponents in §1.5.
- **Zill SN, Moran DT (1981).** "The Exoskeleton and Insect Proprioception. I. Responses of
  Tibial Campaniform Sensilla to External and Muscle-Generated Forces in the American
  Cockroach." *J Exp Biol* **91**:1–24. DOI 10.1242/jeb.91.1.1.
- **Zill SN, Schmitz J, Büschges A (2004).** "Load sensing and control of posture and
  locomotion." *Arthropod Structure & Development* **33**(3):273–286.
  DOI 10.1016/j.asd.2004.05.005. (Review — no encoder equations.)
- **Zill SN, Büschges A, Schmitz J (2011).** "Encoding of force increases and decreases by
  tibial campaniform sensilla in the stick insect, *Carausius morosus*."
  *J Comp Physiol A* **197**:851–867. DOI 10.1007/s00359-011-0647-4.
  ← source of the stick-insect group 6A/6B data fitted in §1.3.
- **Zill SN, Büschges A, Schmitz J et al (2012).** "Force encoding in stick insect legs
  delineates a reference frame for motor control." *J Neurophysiol* **108**:1453–1472.
  DOI 10.1152/jn.00274.2012.
- **Dallmann CJ, Dürr V, Schmitz J (2016).** "Joint torques in a freely walking insect
  reveal distinct functions of leg joints in propulsion and posture control."
  *Proc R Soc B* **283**:20151708. DOI 10.1098/rspb.2015.1708.
  ← the "naturalistic" joint-torque waveform used as the held-out test stimulus in §1.4.
- **Dallmann CJ, Hoinville T, Dürr V, Schmitz J (2017).** "A load-based mechanism for
  inter-leg coordination in insects." *Proc R Soc B* **284**:20171755.
  DOI 10.1098/rspb.2017.1755. (Behavioural/mechanistic, not an afferent encoder.)

---

## 16. Bottom line for implementation

**Nothing off the shelf does what the whole-fly sim needs. The pieces exist and have to be
assembled.** Concretely:

### 16.1 Campaniform sensilla — implement Szczecinski et al. 2021 (§1)

Best-supported, cheapest, and the only CS encoder with published fitted parameters.
Per CS group, two units (antagonistic pair, feed u and −u):

```python
# state: x  (mN);  input: u (mN);  output: y (Hz)
dx = (1.0/tau) * math.copysign(abs(u - x)**b, u - x)
x += dx * dt
y  = max(0.0, a*(u - x) + c*u + d)
```
Start from the stick-insect 6A row (a = 265.0, b = 1.675, c = 17.75, d = −22.50,
τ = 9.678 ms) or the cockroach row (707.6 / 2.262 / 54.29 / −41.16 / 3.859 ms).
**Caveat:** both are calibrated to mN forces in animals hundreds to thousands of times
heavier than a fly. Zill et al 2025 (§6) found force detection "scales to body weight" in
*Calliphora*, so a and c almost certainly need rescaling by the ratio of body weights /
typical leg loads. The *Calliphora* refit in §6 is the missing number.

Drive `u` from the sim's `contact_forces` (mN in flygym) projected onto each CS group's
preferred bending axis, or from joint torque on the proximal joint of the segment
(Szczecinski 2021 explicitly validated against a joint-torque "naturalistic" waveform).

### 16.2 FeCO — no published encoder; build a hair-field-style array

Nothing maps *Drosophila* FTi angle to claw/club/hook activity in closed form. Options in
increasing fidelity:
1. **Ache & Dürr 2015 filter cascade (§10)** applied to the FTi angle, with a
   range-fractionated array (claw = position, tuned across the range; hook = directional
   velocity; club = bidirectional velocity/vibration). All parameters published, trivial to
   run, wrong organ but right functional class.
2. **van der Veen et al 2025 AdEx SNN (§9)** — same idea with spiking dynamics and
   published parameters; the authors explicitly argue it transfers to the FeCO.
3. **Mamiya et al 2023 FE geometry (§4.2)** if you want the strain gradient to come out of
   mechanics — but it is COMSOL, not a transfer function, and would need reducing.

Anchor the tuning to Mamiya 2018 (§4.1): FTi range 18°–180°, claw roughly linear in angle
with hysteresis, club phasic-bidirectional and vibration-tuned (100–1600 Hz, amplitudes
down to 0.054 µm), hook directionally selective, club velocity response peaking ~400 °/s.

### 16.3 Hair plates — threshold/limit detector on joint angle

Pratt et al 2026 (§4b): tonic, **no phasic component**, activity rises toward the
**extreme of the joint's range**. So a monotone saturating nonlinearity (sigmoid or ReLU)
on the relevant DoF angle, one unit per hair, tiled over the last part of the range, with
no velocity term. For *Drosophila* CxHP8 specifically: thorax-coxa rotation and adduction,
peaking at inward rotation + adduction (anterior extreme). Ache & Dürr's linear-tiling
scheme (§10.1, 2.5° per hair, 20 hairs per row, two opposing rows) is a ready-made
geometry.

### 16.4 Delays

Karashchuk et al 2025 (§8), measured in *Drosophila*: **sensory delay 10 ms** (range
5–15 ms, from femur mechanosensory spike to peak EPSP in a postsynaptic VNC neuron),
**motor delay 30 ms** (range 20–40 ms, motor neuron spike to muscle force onset), and the
system breaks when the **sum exceeds ~45 ms**. Put the 10 ms on the encoder output.

### 16.5 Simulator interface

flygym/NMFv2 gives `joints` (3 × 42: angle, angular velocity, force) and `contact_forces`
((30 or 36) × 3, mN, translational part of `cfrc_ext`, with adhesion force subtracted
back out). Units are mm and mN throughout because the meshes are at 1000× scale.
Stance thresholds already in use by the Ramdya lab: 0.5 / 1 / 3 mN for front / middle /
hind legs.

---

*Compiled by a research subagent, 2026-09-21. Every number above is tagged [V] (read in the
primary source), [S] (second-hand / page-reading summary), or explicitly marked "could not
verify". Nothing here was invented.*
