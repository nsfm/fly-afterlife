# Mamiya et al. 2023 — Biomechanical origins of proprioceptor feature selectivity

**Citation.** Mamiya A, Sustar A, Siwanowicz I, Qi Y, Lu T-C, Gurung P, Chen C, Phelps JS, Kuan AT,
Pacureanu A, Lee W-CA, Li H, Mhatre N, Tuthill JC (2023). "Biomechanical origins of proprioceptor
feature selectivity and topographic maps in the *Drosophila* leg." *Neuron* 111(20):3230–3243.e14
(published online 2023-08-09). DOI **10.1016/j.neuron.2023.07.009**. PMID 37562405.
VERIFIED by reading the full in-press PDF (faculty.washington.edu/tuthill/docs/mamiya_2023.pdf),
which paginates as "Neuron 111, 1–14" + methods e1–e14. Exact page range 3230–3243 is second-hand
from indexing services — **could not verify page numbers from the PDF I read.**

Methods used: X-ray holographic nano-tomography of the front leg (dataset from Kuan et al.),
split-Gal4 lines for club/claw/hook, single-nucleus RNA-seq, transcuticular 2-photon and 3-photon
imaging of cell bodies and dendrites *in the leg*, and COMSOL finite-element modelling.

## Counts (VERIFIED)

- **"We identified 152 total cell bodies in the FeCO"** (X-ray reconstruction of the front leg).
  This **supersedes the 135 figure from Mamiya 2018** (which was a confocal nuclear count).
  When citing a per-leg FeCO number, prefer **152 (M, anatomical, front leg)** and note 135 as the
  earlier estimate. Neither paper gives a verified per-subtype breakdown of all 152.
- FeCO organised into **three anatomical compartments ("scoloparia")**:
  - **group 1** = largest, most dorsal = **club** (vibration / bidirectional movement)
  - **group 2** = linear array along the long axis of the femur = **claw** (static joint angle);
    **hook-extension** neurons sit distal to the claw neurons, also in group 2
  - **group 3** = smaller, more lateral = **hook-flexion**
- snRNA-seq resolved **three** transcriptional clusters (club / claw / hook). It could **not**
  separate flexion- vs extension-tuned claw, nor flexion- vs extension-tuned hook.
- Nuclei came from **666 dissected fly legs** (FACS, 10x).

## Mechanical wiring (VERIFIED)

- Each *pair* of FeCO neurons is ensheathed by a scolopale cell attached to a sensory tendon via an
  actin-rich **cap cell**.
- **Two sensory tendons.** Groups 2+3 (claw, hook) → **medial tendon**; group 1 (club) → **lateral
  tendon**. Claw/hook tendons "merge and fuse **100 µm** distal to the FeCO"; club's stays separate.
- Both converge on the **arculum**, a tooth-shaped structure in the distal femur (name borrowed from
  beetle anatomy). Medial tendon → arculum's medial root; lateral tendon → arculum's lateral root.
  Arculum is coupled to the base of the tibia-extensor tendon and to the tibia joint.
- **No efferent innervation of the FeCO was observed**, and no connection to surrounding muscles
  (contra an earlier report). → for a sim, FeCO is a pure afferent, no gamma-motor analogue.

### The arculum as a slider–crank (this is the key modelling idea)

- FE model (COMSOL): arculum suspended by 4 springs (tibia-joint tendon, tibia-extensor/femoral
  tendon, lateral FeCO tendon, medial FeCO tendon), spring constant `k = E_res * A / L0`.
- **Tendon geometry table (VERIFIED, quoted directly):**

| Tendon | Equilibrium length L0 (µm) | Cross-sectional area A (µm²) |
|---|---|---|
| Joint tendon | 72 | 295.3 |
| Femoral (tibia-extensor) tendon | 225 | 295.3 |
| Medial tendon | 268 | 50.9 |
| Lateral tendon | 283 | 57.2 |

  `E_res` = Young's modulus of resilin; medial tendon's k was **halved** to represent a soft proximal
  coupling. Isotropic loss factor **0.5** for the spring foundations.
- **Drive force: a periodic 10 µN force applied along the femur long axis at the joint-tendon
  attachment, "approximat[ing] force levels known to be produced by Drosophila muscles".**
  Model is linear-Hookean, so response scales linearly with force.
- Frequency sweep **2 Hz to 80 kHz** (2nd eigenfrequency of the system found at the top end).
- Result: the arculum **rocks**, decomposing linear tibia motion into two orthogonal vectors.
  Lateral root moves mostly **along** the femur long axis (→ club); medial root moves mostly
  **orthogonal** to it (→ claw).
  **"the medial FeCO tendon transmits primarily off-axis movements to the claw neurons, reducing
  on-axis movements by as much as 30×."**
- This 30× attenuation + the club cells' firmer anchoring is offered as the explanation of the
  earlier finding that **"the mechanosensory threshold of claw neurons is more than 10 times higher
  than that of club neurons"** (attributed to Mamiya 2018 ref 5).
- Regime split stated explicitly:
  - **macroscopic: 1–50 µm arculum movement, low frequency** — tibia flexion/extension during
    walking. Both tendons move similarly → excites claw *and* club.
  - **microscopic: <1 µm, 100–1600 Hz vibration** — arculum rocks; lateral tendon excited (club),
    medial tendon moves perpendicular (claw not excited).

### Cell-body motion in the femur (VERIFIED)

- Club and hook-**flexion** cell bodies move **<2 µm** across the full flexion/extension range →
  anchored in stiffer tissue.
- Claw and hook-**extension** cell bodies move **distally during tibia flexion**, proximally during
  extension. Distal cells move more than proximal cells; displacement is a **linear function of the
  cell's position along the proximal–distal axis**.
- Cutting the medial tendon makes claw cells and cap cells **retract proximally** → claw cells are
  held under **resting tension**, and without it the goniotopic map is destroyed.

## Topographic maps (VERIFIED)

### Goniotopic map (claw) — directly usable as an encoding rule
- Slow flexion at **6 °/s**, GCaMP7f, per-cell tracking in the femur.
- **Linear relationship between a claw cell's proximal–distal position and the tibia angle at which
  it reaches 50 % of its maximum activity.**
- Flexion-selective claw: **proximal cells recruited first, at more obtuse angles (<90° during
  flexion); distal cells recruited later, at more acute angles.**
- Extension-selective claw: **distal cells first at more acute angles (>90° during extension);
  proximal cells at more obtuse angles.**
- Mechanism from the FE model: dendritic strain increases as the tibia flexes, and **strain is always
  higher in more proximal cells, with the gap widening as the tibia flexes.** A *uniform* activation
  threshold across cells on top of that strain gradient yields the angular map (their Fig 5E).
  → **Modelling implication: one shared threshold + a position-graded gain reproduces claw range
  fractionation. You do not need 20 independent tuning curves.**
- Flexion- and extension-selective claw neurons are **intermingled** in the array.
- Open puzzle they flag: extension-selective claw cells appear to respond to a *decrease* in dendritic
  strain, which fits force-from-filament (tip-link-like tethering) rather than force-from-lipid.

### Tonotopic map (club)
- Vibration **100–1600 Hz at 0.9 µm** amplitude, imaging **dendrites** in the femur (dendritic signal
  larger than somatic), n = **17 flies**.
- **Response amplitude increases with frequency and plateaus around 800 Hz.**
- Centre of the calcium response shifts **distal/lateral → proximal/medial as frequency rises over
  200–1600 Hz**; significant across flies.
- Mechanism of the tonotopy is **unresolved**: tendon-length resonance was tested by a simple
  mechanical model and **rejected** (neither longitudinal nor transverse modes differ enough).
  Candidates left open: per-dendrite stiffness / cap-cell mass; electrical resonance (they note `slo`
  is highly expressed).

### Ion channels
- snRNA-seq found **no differential expression of known mechanosensitive channels** (nor of
  voltage-gated Na/K channels) across club/claw/hook. Marker genes that *do* differ:
  club **AstA-R1**, claw **Dop2R**, hook **Ca-alpha1T**.
  → feature selectivity is **biomechanical, not molecular**, as far as this assay can tell.

## FE model of the claw array — full parameter set (VERIFIED, for reimplementation)

Geometry (2D, COMSOL 6.1, truss + solid mechanics, linear elastic, Hooke):
- Medial tendon: cable, length **250 µm**, circular cross-section radius **2 µm**.
- Fibrils from tendon to cap cells: radius **0.2 µm**; radiating array with angular gradient
  **168° → 180°** relative to the tendon long axis.
- Dendrites: length **50 µm**, radius **0.2 µm**. **20 dendrites** modelled parallel at **168°** to
  the medial tendon, plus **3 dendrites** parallel to the tendon (most-proximal claw cells).
- Real FeCO has **two** claw arrays lying in planes **~20° apart**; the model collapses them to one by
  symmetry.
- Cells as point masses: density **1200 kg/m³**, claw cell radius **4 µm**, cap cell radius **2 µm**.
- Surrounding tissue solid: thickness **10 µm**, length **660 µm**, width **80 µm**.
- Mesh: 20 edge elements per truss; min element **0.08 µm**, max **24.4 µm**; total **6717 triangle
  elements + 1589 edge elements**.

Material properties:
- Density **1200 kg/m³** throughout (insect cuticle range); Poisson's ratio **0.3** throughout.
- Medial tendon and fibrils: Young's modulus **1.8 MPa** (resilin estimate).
- Claw ciliated dendrites: **178 kPa** (literature estimate of ciliary Young's modulus).
- Surrounding tissue: swept **100 Pa – 2 kPa**; **1 kPa** chosen because it reproduced the measured
  cap/claw cell displacements. Tissue thickness and modulus trade off ~1:1 (100 µm thick ↔ 100 Pa).
- Material damping: isotropic loss factor **0.8** on both truss and solid (viscous damping of small
  structures in fluid).
- Anisotropy and viscoelasticity deliberately ignored.

## What I could not verify
- Exact published page range (3230–3243.e14) — my PDF is the in-press version.
- Per-subtype neuron counts summing to 152; the paper does not give a clean table of
  club/claw/hook-flexion/hook-extension counts in the main text I read.
