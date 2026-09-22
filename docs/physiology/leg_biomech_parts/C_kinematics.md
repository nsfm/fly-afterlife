# C. Walking kinematics — what a "walking-shaped" leg motor pattern must look like

Scope: the quantitative target a leg controller has to hit before anyone should call its
output walking. Everything here is *Drosophila melanogaster* unless a line says otherwise.

Markers used on every number:
- **(M)** measured in *Drosophila*
- **(E)** estimate / model parameter / fitted value, not a direct measurement
- **(C) [taxon]** comparative — imported from another insect, labelled with the taxon

Verification flags: **[V]** = read in the paper's own text (PDF / full text); **[V-fig]** = read
from a figure legend or table only; **[V-fetch]** = extracted from the publisher's page by a
single automated read, not cross-checked against the PDF; **[2nd]** = second-hand.

---

## C.0 The one-paragraph answer

A fly walks between roughly **0 and 35 mm/s** (≈0–15 body lengths/s), with the modal moving
speed around **15–20 mm/s**. Speed is set almost entirely by **shortening stance**, not by
lengthening the step: stance duration scales as **v∥^−1.03**, swing stays near **30 ms** at all
speeds, and step amplitude stays near **0.5 body length**. Step frequency therefore runs from
about **5 Hz at slow walk to ~16–20 Hz at top speed**, and duty factor slides from about
**0.83 (wave-like) down to ~0.5** where swing and stance equalise. Contralateral leg pairs are in
antiphase (**Δφ = 0.5**) at *every* speed; ipsilateral neighbours drift from **Δφ ≈ 0.2 at 3 BL/s to
≈0.4–0.45 at ≥10 BL/s**, and the phase *variance* falls monotonically with speed. There is no
discrete tripod↔tetrapod switch — the honest description is one continuum whose coordination
tightens with speed. Turning is not a change of gait: it is limb-specific modulation, with the
inside fore-leg rotating its **stance direction by up to ~45°** while stepping frequency changes
only ~25% at the highest yaw rates.

---

## C.1 Speed, frequency, stance and swing

### C.1.1 Speed envelope

| Quantity | Value | Source |
|---|---|---|
| WT freely-walking speed range (M) | 7.2 – 44.7 mm/s | Mendes 2013 [V] |
| WT forward velocity, 2.5–97.5 pct (M) | −1.3 to 30.4 mm/s | DeAngelis 2019 [V] |
| Modal moving speed (M) | ~17.5 mm/s (peak of v∥ pdf, second peak at 0 = stopped) | DeAngelis 2019 [V] |
| "Most representative" speed (M) | 28 mm/s | Mendes 2013 [V] |
| Forward velocity range, behaviour-space study (M) | −6 to +32 mm/s | Katsov 2017 [V-fetch] |
| Max running speed, 800 fps whole-body (M) | up to 40 mm/s | Ispizua 2026 [V-fetch] |
| Per-strain ranges (M) | wtCS 11–32 mm/s (5–16 BL/s); wtBerlin 11–34 (5–15); w1118 4–31 (2–15); w1118,Tbh^nM18 3–14 (1.5–7) | Wosnitza 2013 [V-fetch] |
| Predicted static-stability ceiling (E) | ~15 BL/s | Szczecinski 2018 [V-fetch] |
| Body length used as scale (E) | 2.5 mm (b.l.u.); 2.8 mm in NeuroMechFly | Isakov 2016 [V]; Lobato-Rios 2022 [V-fetch] |

Sideslip: **|v⊥| < 9.4 mm/s** (M) [Katsov 2017, V-fetch].

### C.1.2 Step frequency

- Step period asymptotes to **~60 ms at the fastest speeds ⇒ ~16 Hz** (M) [Mendes 2013, V].
- Stride frequency fitted from freely walking WT video: **ω = 11.4 ± 1.8 strides/s** (M) at a
  speed of ~0.65 BL/stride (≈18.5 mm/s) [Isakov 2016 Table 1, V].
- **"Stepping frequencies exceed 20 Hz"** at top running speed (M) [Ispizua 2026, V-fetch].
- Speed is controlled *almost exclusively* via step frequency, not amplitude (M)
  [Wosnitza 2013, V-fetch].

Working range for a controller: **~5 Hz (slow) to ~16–20 Hz (fast)**.

### C.1.3 Stance duration

- **τ_stance ∝ v∥^(−1.025), R² = 0.59** (M) [DeAngelis 2019, V]. This is the single most useful
  scaling law in the whole brief.
- Equivalently, Szczecinski's model form (E): **f_step = V_body/s + 1/T_sw**, with
  **V_body = s / T_stance** and s = step amplitude [Szczecinski 2018, V-fetch].
- Stance duration inversely proportional to speed, confirmed independently (M)
  [Mendes 2013, V; Chun 2021, V-fetch].

### C.1.4 Swing duration — the near-invariant

| Value | Context | Source |
|---|---|---|
| **31 ms** (M) | global mean across all legs, used as a speed-independent constant | Szczecinski 2018 [V-fetch] |
| **20–40 ms** (M) | typical observed range | Wosnitza 2013 [V-fetch] |
| **~30 ms** (M, inferred) | swing = stance at the 60 ms minimum period | Mendes 2013 [V] |
| "roughly constant" (M) | increases *slightly* with speed; small next to stance change | DeAngelis 2019 [V] |
| R² = 0.37 vs cycle period (M) | swing is only moderately coupled to period | Wosnitza 2013 [V-fetch] |

**Verdict: swing ≈ 30 ms is a defensible speed-invariant constant, but "invariant" is an
idealisation — DeAngelis 2019 and Chun 2021 both see a small positive speed dependence.**
Use 30 ms ± 10 ms.

### C.1.5 Step length / amplitude

- Step amplitude ≈ **0.5 body length** (≈1.25 mm) for wtCS and wtBerlin; slightly under 0.5 BL
  for w1118. Correlation with speed weak, **R² = 0.03–0.17** (M) [Wosnitza 2013, V-fetch].
- Step length in the *camera (stationary) frame* increases roughly linearly with forward speed
  (M) [Mendes 2013, V; DeAngelis 2019, V]. These two statements are compatible: leg amplitude
  relative to the body is near-constant, while the ground-frame footfall spacing grows with speed.

### C.1.6 Duty factor

Measured per-leg duty factors, WT pre-amputation, 60 Hz video (M) [Isakov 2016 Table 1, V]:

| Leg | L-front | L-mid | L-hind | R-front | R-mid | R-hind |
|---|---|---|---|---|---|---|
| δ (fraction of stride in stance) | 0.62 | 0.70 | 0.66 | 0.65 | 0.70 | 0.68 |
| ± SD | 0.07 | 0.06 | 0.06 | 0.07 | 0.06 | 0.06 |

So at ~18 mm/s, **duty factor ≈ 0.65, midlegs highest (0.70), forelegs lowest (0.62–0.65)**.

Envelope across speed:
- **~0.83** at 2.5 BL/s (wave gait, duty cycle 5/6) (E) [Szczecinski 2018, V-fetch]
- **~0.65** at ~7 BL/s (M) [Isakov 2016, V]
- **→0.5** at the ~60 ms minimum period where swing = stance (M) [Mendes 2013, V]

Wosnitza 2013 did **not** compute duty factor [V-fetch].

### C.1.7 Footfall geometry (AEP / PEP)

Qualitative but well-established (M) [Mendes 2013, V]:
- At higher speed, **AEP shifts anteriorly and PEP shifts posteriorly for all six legs** —
  the stance sweep lengthens at both ends.
- Midlegs additionally shift **laterally** at higher speed; hindlegs move **closer to the body**.
- **AEP is more tightly clustered than PEP in 61/71 videos (86%)** — touchdown is more precisely
  targeted than lift-off. A controller that gets AEP precision wrong is visibly wrong.
- Stance traces straighten with speed (stance linearity index falls), plateauing above ~34 mm/s.

**Could not verify** absolute AEP/PEP coordinates in mm from Mendes 2013 — the paper normalises
footprint geometry to body size and prints no mm coordinates in text or figure legends. Nearest
substitute: Isakov 2016's fitted relaxed leg endpoints and attachment points (§C.6 table).

---

## C.2 Inter-leg phase relations by speed

Convention: Δφ in cycles; 0 = in phase, 0.5 = antiphase.

### C.2.1 The numbers that exist

**DeAngelis 2019 (M) [V]** — best-sampled, 114 flies, 150 fps:
- **Contralateral pairs (L1-R1, L2-R2, L3-R3): ⟨Δφ⟩ ≈ 0.5, constant at *every* forward speed.**
  Antiphase is the one rock-solid invariant.
- **Ipsilateral neighbours** (fore-mid, mid-hind): ⟨Δφ⟩ ≈ **0.4** pooled across speeds — not the
  0.5 a canonical tripod requires. **Not constant across speed**; approaches tripod-like coupling
  only at the fastest speeds.
- **Ipsilateral fore-hind (e.g. L3-L1): ⟨Δφ⟩ ≈ 0.85** — not in phase (canonical tripod wants 0).
- Angular deviation of **all** pairwise phases **decreases monotonically with speed**. The real
  speed-dependent change is variance, not mean configuration.
- Joint distribution over (L2-R2, L3-L1) is **unimodal**, peak nearest canonical tripod. No
  tetrapod mode.

**Szczecinski 2018 (E) [V-fetch]** — static-stability optimum, same trend:
- φ_I ≈ **0.2** at ~3 BL/s → φ_I ≈ **0.4** at ~10 BL/s, converging on 0.5.
- φ_C = **0.5** at all speeds.

**Isakov 2016 (M) [V]** — fitted directly from WT video, swing onset relative to left-front:

φ = [0, 0.58, 0.17, 0.48, 0.13, 0.60] ± [0, 0.07, 0.07, 0.06, 0.07, 0.09] cycles
(L-front, L-mid, L-hind, R-front, R-mid, R-hind)

Derived pairwise offsets: contralateral **0.48 / 0.55 / 0.43** (antiphase within noise ✓);
ipsilateral fore-mid **0.58**, mid-hind **0.59**, fore-hind **0.17**. Same non-canonical signature.

**Wosnitza 2013 (M) [V-fetch]** — tripod coordination strength:
- **TCS = t₂/t₁** where t₁ = earliest-swing-onset to latest-swing-termination within a tripod
  group and t₂ = the window where all three swing together. TCS = 1 is perfect tripod.
- Above **10 BL/s**: TCS up to **0.85**. Below 10 BL/s: **0.02–0.8**, highly variable.
- Tetrapod/wave coordination emerges below ~**5 BL/s**.
- Within a high-speed tripod: front leads midleg by ~**15 deg** of cycle (≈0.042), midleg leads
  hindleg by ~**15 deg** again — a real, small metachronal lag inside the "simultaneous" tripod.

**Godesberg, Bockemühl & Büschges 2024 (M) [V-fetch]** — *J Exp Biol* 227:jeb247878,
DOI 10.1242/jeb.247878. The largest single-lab fly gait dataset: **103 flies recorded, 88 analysed,
36,942 straight-walking step cycles** (median 242 per fly), camera **200 Hz**, 33.3 px/mm,
inclusion ≥2 BL/s, main band 5–7 BL/s.
- **TCS is "predominantly found in the range between 0.5 and 0.75"** over 30,216 instances of two
  consecutive tripod cycles. This is the better central estimate for ordinary walking; Wosnitza's
  0.85 is the ceiling at >10 BL/s.
- Kinematic variability needs **five principal components for ~80%** of the variance:
  **PC1 30.9%, PC2 14.7%, PC3 12%, PC4 11%, PC5 9.5%**. Useful counterweight to the
  "gait is one-dimensional" framing — one dimension dominates, but not overwhelmingly, and a good
  chunk of the rest is between-individual.

**Mendes 2013 (M) [V]** — metachronal lag regression:
- slow flies: **HLag_F = 0.505 × Period + 27.6 ms** (tetrapod-like)
- fast flies: **HLag_F ≈ Period** (tripod)

### C.2.2 Occupancy vs speed (two incompatible framings — say which you use)

Mendes 2013 gait-class occupancy, % of frames (M) [V-fig]:

| Gait | slow ≤19.9 mm/s | medium 20–33.9 | fast ≥34 mm/s |
|---|---|---|---|
| Tripod | 31.37 | 51.63 | 64.98 |
| Tetrapod | 25.45 | 15.90 | 7.26 |
| Pentapod | 30.15 | 14.37 | 13.33 |

DeAngelis 2019 feet-down configuration optima (M) [V]: **5-feet-down peaks at 7 mm/s,
4-feet-down at 13 mm/s, 3-feet-down at 24 mm/s**. But: at slow speed a canonical configuration
can last a single frame (~6.7 ms), and above the slow tercile virtually all tetrapod and wave
configurations are **transient**.

**The disagreement, stated plainly.** Mendes 2013 and Wosnitza 2013 describe a speed-dependent
*transition* between named gaits. Szczecinski 2018 and DeAngelis 2019 argue there is a single
continuum and the named gaits are bins we drew on it. Chun 2021 goes further: flies use a
**modified tripod at all speeds**, changing only marginally, and control speed by changing tripod
*geometry* (L/r_m between 1 and 2, where L = fore-aft tripod spread and r_m = CoM height at
mid-stance) rather than leg stiffness (M) [V-fetch]. Ispizua 2026 adds that flies are doing
**grounded running across the whole speed range with no discrete gait transitions** — CoM height
and forward speed peak *in phase* at both alternating-tripod peaks, and there is **no floating
phase with all six tarsi off the ground** (M) [V-fetch].

**For a simulator: do not hard-code a canonical tripod, and do not hard-code a switch.** Target
φ_C = 0.5 fixed, φ_I sliding 0.2→0.45 with speed, and phase *variance* falling with speed.

---

## C.3 Joint angle ranges per joint, per leg

### C.3.1 The measured ROM table — Haustein et al. 2024

**This is the source to use.** Haustein M, Blanke A, Bockemühl T, Büschges A (2024),
*Front Bioeng Biotechnol* 12:1357598, DOI 10.3389/fbioe.2024.1357598.
(Frequently mis-cited as a Dallmann/Tuthill paper — it is the Büschges lab, Cologne.)

Method: 6-camera motion capture at **400 Hz**, µCT-derived leg model with yaw axes taken from the
real **joint condyles** (oblique, not orthogonalised). **12 flies (5F/7M)**, mean walking speed
**14.7 ± 4.0 mm/s**, **n = 2,250 steps**, 6 mm spherical treadmill. ROM = max − min observed angle
per DOF over forward walking, mean ± SD across the 12 flies.

Convention per joint: **yaw** = the main condylar rotation axis; **roll** = along the long axis of
the distal segment; **pitch** = cross product of yaw and roll. Joints: ThCx (thorax-coxa),
CxTr (coxa-trochanter), TrFe (trochanter-femur), FeTi (femur-tibia), TiTar (tibia-tarsus).

**Measured ROM during forward walking (M) [V]:**

| Motion (DOF) | Front T1 | Middle T2 | Hind T3 |
|---|---|---|---|
| Coxa promotion / remotion (protraction/retraction) | **40.87° ± 5.21°** | **26.48° ± 4.58°** | **18.60° ± 3.85°** |
| Coxa adduction / abduction | **8.24° ± 2.74°** | **7.63° ± 2.85°** | **8.85° ± 2.98°** |
| ThCx-roll (coxa long-axis rotation) | **40.87° ± 5.21°** ⚠ | **4.91° ± 2.67°** | **11.27° ± 3.01°** |
| CxTr-yaw (trochanter flexion / extension) | **91.24° ± 9.54°** | **22.51° ± 3.38°** | **56.34° ± 9.00°** |
| FeTi-yaw (tibia flexion / extension) | **96.55° ± 7.65°** | **21.52° ± 5.43°** | **84.11° ± 9.94°** |
| Femur-tibia *plane* rotation (midlegs only) | — | swing median **42.6°** (IQR 10.7°); stance median **40.7°** (IQR 6.5°) | — |

⚠ The front-leg value for promotion/remotion and the front-leg value for ThCx-roll are **both
printed as 40.87° ± 5.21°** in two separate sentences of the paper. One of them is probably a
copy-paste error. Flagged, not silently corrected.

**Which DOF drives which motion (M) [V]** — note the midlegs swap the assignment:

| | Front T1 | Middle T2 | Hind T3 |
|---|---|---|---|
| promotion/remotion driven by | ThCx-**pitch** | ThCx-**yaw** | ThCx-**pitch** |
| adduction/abduction driven by | ThCx-**yaw** | ThCx-**pitch** | ThCx-**yaw** |

**Step-phase signs (M) [V]** — this is the part a naive CPG usually gets wrong:
- Promotion in **swing**, remotion in **stance**, in all three leg pairs.
- **Front legs: the leg extends during swing and flexes during stance.**
- **Hind legs: the opposite — flexes during swing, extends during stance.**
- **Middle legs: idiosyncratic.** Trochanter flexes in swing / extends in stance; tibia flexion
  runs through almost the whole swing *and* the first half of stance, with extension only in the
  second half of stance; the midleg tibia flexion is abrupt at early stance, not gradual.
- Front-leg TrFe-roll: lateral rotation of the femur-tibia plane in the first half of swing,
  continued into the first half of stance, then switching to medial rotation.
- Midleg femur-tibia plane rotation is reproduced almost completely (residual **−0.8° ± 1.1°**
  swing, **−1.4° ± 0.9°** stance) by combining the two most proximal **yaw** DOFs, ThCx-yaw +
  CxTr-yaw. ThCx-yaw alone leaves a 17.9°/16.2° shortfall; ThCx-pitch alone −35.1° ± 0.9°;
  ThCx-roll alone −33.0° ± 0.9°. **The midlegs need no TrFe roll DOF** (the forelegs do).

**Model joint limits (E) [V]**, Table 1 of the same paper (right legs; invert sign for left legs
on yaw and roll but not pitch). These are *constraints*, not observed ROM:

| Leg | Joint | yaw min/max | pitch min/max | roll min/max |
|---|---|---|---|---|
| front | ThCx | −70 / 70 | −33 / 147 | −160 / 50 |
| front | CxTr | −20 / 160 | −108 / 72 | −120 / 120 |
| front | TrFe | −90 / 90 | −108 / 72 | −90 / 90 |
| front | FeTi | −20 / 145 | −75 / 75 | −90 / 90 |
| front | TiTar | −60 / 120 | −75 / 75 | n.a. |
| middle | ThCx | −90 / 60 | −40 / 140 | −90 / 90 |
| middle | CxTr | −140 / 10 | −54 / 126 | −90 / 90 |
| middle | TrFe | −110 / 110 | −123 / 57 | −110 / 90 |
| middle | FeTi | 0 / 170 | −90 / 90 | −90 / 90 |
| middle | TiTar | −10 / 140 | −64 / 116 | n.a. |
| hind | ThCx | −90 / 60 | −39 / 141 | −100 / 100 |
| hind | CxTr | −110 / 30 | −121 / 59 | −90 / 110 |
| hind | TrFe | −90 / 90 | −54 / 126 | −90 / 90 |
| hind | FeTi | 10 / 180 | −103 / 77 | −90 / 90 |
| hind | TiTar | −5 / 90 | −85 / 95 | n.a. |

Model fit error (summed Euclidean distance over CxTr/TrFe/FeTi/TiTar/tarsus tip): front
342 ± 61 → 560 ± 80 µm; middle 100 ± 34 → 136 ± 46 µm; hind 126 ± 47 → 154 ± 49 µm (M) [V].
The forelegs are the hardest to model — worth knowing before blaming your controller.

### C.3.2 Anipose (Karashchuk et al. 2021)

Karashchuk P, Rupp KL, Dickinson ES, Walling-Bell S, Sanders E, Azim E, Brunton BW, Tuthill JC
(2021), *Cell Reports* 36:109730, DOI 10.1016/j.celrep.2021.109730.

- **6 cameras at 300 Hz**; 1 px ≈ 0.0075 mm; **5 keypoints per leg × 6 legs = 30** (body-coxa,
  coxa-femur, femur-tibia, tibia-tarsus, tarsus tip) (M) [V-fetch].
- **8 angles per leg = 1 abduction + 3 rotation + 4 flexion** (M) [V-fetch].
- Accuracy: >90% of poses within 20 µm in segment length and **1°** in angle (M) [V-fetch].
- Dataset: **39 flies, 1,480 s of walking** (M) [V-fetch].
- **Headline result: middle legs are driven primarily by femur rotation; front and hind legs by
  femur-tibia flexion** (M) [V-fetch]. Haustein 2024 (§C.3.1) later showed this midleg "femur
  rotation" is produced kinematically by ThCx-yaw + CxTr-yaw, not by a dedicated roll DOF.
- Physiological femur-rotation range in walking estimated **~70°** (E) [V-fetch].
- Downstream markerless 3D tracking uncertainty quoted by the same lab: **5.56°**
  [Karashchuk 2025 eLife, V].
- **Could not verify** explicit per-joint numeric ROM in degrees from Anipose — Figure 7B is
  probability densities with no printed ranges.

### C.3.3 NeuroMechFly v1 (Lobato-Rios et al. 2022)

*Nature Methods* 19:620–627, DOI 10.1038/s41592-022-01466-7.
- **7 DOF per leg**: ThC ×3 (pitch = elevation/depression, yaw = protraction/retraction, roll =
  rotation), CTr ×2 (pitch + roll), FTi ×1 (pitch), TiTa ×1 (pitch) ⇒ **42 actuated leg DOFs**
  (E) [V-fetch]. 65 rigged body segments. (Repo audit in `docs/research/sources/lobatorios_2022.md`
  counts 11 revolute joints per leg in the SDF, of which 7 actuated.)
- Body length **2.8 mm** (E); model mass **1 µg** distributed head 0.125 / thorax 0.31 /
  abdomen 0.45 / legs 0.11 / wings 0.005 µg (E) [V-fetch]. **Cross-check before using for force
  scaling** — a real fly is ~1 mg; Isakov 2016 uses body mass unit = **0.25 mg** (E) [V] and
  Karashchuk 2025 uses **m = 0.7 × 10⁻⁶ kg = 0.7 mg** (E) [V].
- Timestep **1 ms**, PyBullet, treadmill Ø 10 mm (E) [V-fetch].
- **Joint ranges set to −180°…180°** because "there are no reported angles for these variables";
  kinematic-replay bounds were per-joint **mean ± 1 SD** of the recorded walking data, never
  enumerated (E) [V-fetch]. **NeuroMechFly v1 is therefore not a source of measured joint ROM.**
- Angles computed from DeepFly3D as dot products of vectors sharing an origin; CTr-roll obtained
  by de-rotating the tibia-tarsus joint by the inverse coxa and femur angles and measuring against
  the A-P axis in the dorsal plane (E) [V-fetch].

### C.3.4 NeuroMechFly v2 (Wang-Chen et al. 2024)

*Nature Methods* 21:2353–2362, DOI 10.1038/s41592-024-02497-y.
- Same 7 DOF/leg × 6 legs [2nd].
- CPG controller drives a reduced set: **front legs ThC-pitch, CTr-pitch, FTi-pitch;
  mid and hind legs ThC-roll, CTr-pitch, FTi-pitch** [2nd].
- **Could not verify** measured joint-angle ranges in degrees for v2 — supplementary tables not
  retrievable through the paywall. Open item. (See `docs/research/sources/wangchen_2024.md`,
  written by another pass, for the repo-side audit.)

### C.3.5 Özdil et al. 2025 — musculoskeletal foreleg

Özdil PG, Ning C, Phelps JS, Wang-Chen S, Elisha G, Blanke A, Ijspeert A, Ramdya P (2025),
"Musculoskeletal simulation of limb movement biomechanics in *Drosophila melanogaster*",
arXiv:2509.06426 (CC BY 4.0).
- Foreleg: 7 DOF — ThC roll/pitch/yaw, CTr roll/pitch/yaw, FTi pitch [V-fetch].
- **CTr-roll does not move during locomotion** (it is a grooming DOF) (M) [V-fetch].
- ThC roll range ≈ **[−95°, +50°]** during grooming; narrower during locomotion; with the 3-DoF
  model the grooming ThC-roll range narrows to ≈ **[−30°, −7°]** (M) [V-fetch].
- **15 muscle-tendon units per foreleg** (7 thoracic, 6 coxal, 2 femoral); 7 MTUs per midleg and
  8 per hindleg from anatomy only (M) [V-fetch].
- Specific tension **28 mN/mm²** PCSA, bracketed by *Drosophila* jump muscle **37 mN/mm²** and
  flight muscle **9 mN/mm²** (E) [V-fetch].
- **Could not verify** a systematic per-DoF walking ROM table or numeric moment arms from the
  accessible text. Figure S3D holds the distributions.

### C.3.6 Karashchuk et al. 2025 — the model that consumes all this

*eLife* RP99005 (2025), "Sensorimotor delays constrain robust locomotion in a 3D kinematic model
of fly walking", PMC12081000.
- Training data: **3,473 walking bouts from 45 flies**; mean bout 0.877 s (263 frames);
  **3,049.7 s / 914,909 frames** of walking, tracked at **300 Hz** with Anipose (M) [V-fetch].
- Bout inclusion criterion: ≥0.5 s and **left front femur-tibia flexion range ≥30°** (M) [V-fetch].
- Joints in the model (Table 1): front legs — body-coxa flexion, coxa-femur flexion, femur-tibia
  flexion; mid/hind legs — coxa-femur flexion, femur rotation, femur-tibia flexion, plus coxa
  rotation for mid/hind (E) [V-fetch].
- Simulated forward speeds **8, 10, 12, 14 mm/s** (E); data sustained peak ~4–10 mm/s (M) [V-fetch].
- **Sensory delay 5–15 ms; motor delay 20–40 ms** (from mechanosensory measurements and from MN
  spike to muscle force onset). Realistic walking is maintained up to **~30 ms motor delay and
  ~10 ms sensory delay** — i.e. the fly sits right at the edge (E/M) [V-fetch].
- Leg controller runs at 600 Hz, pattern generator at 300 Hz, Kuramoto phase coordinator (E) [V].
- Body mass used **m = 0.7 mg**; leg radius r = 1.5 mm (E) [V].
- **Could not verify** joint-angle ROM in degrees from this paper — it reports trajectories, not
  ranges.

---

## C.4 Turning

### C.4.1 DeAngelis et al. 2019 — the quantitative core (M) [V]

Restricted to **forward speed 15–20 mm/s** to decouple turning from speed.

| Limb | swing duration | stance duration | step length | step direction |
|---|---|---|---|---|
| inside fore | ↑ slightly | ↓ | **not significantly modulated** | **rotated by up to ~45°** |
| inside mid | **↓** | **↑** | ↓ | shifted |
| inside hind | **↓** | **↑** | ↓ | — |
| outside fore | ↑ slightly | ↓ | ↑ | shifted |
| outside mid | ↑ slightly | ↓ | ↑ | — |
| outside hind | ↑ slightly | ↓ | ↑ | — |

- **Net modulation of stepping frequency at the highest yaw rates: ~25%.**
- The path-length differential between the two forelegs is achieved **mainly by rotating the
  inside foreleg's stance direction (up to ~45°)**, not by changing its step length or frequency —
  the two forelegs show nearly identical stepping-frequency modulation.
- **Turns are phase-locked.** Yaw-rate extrema occur at preferred limb phases, significantly
  different from the time-invariant distribution (**p < 10⁻⁵ for all six limbs**). At yaw extrema
  the tripod containing the inside foreleg sits near a preferred spatial configuration.
- Architecture claim: forward speed is essentially a **one-dimensional** command acting on stance
  duration; turning is a set of asymmetric, **limb-specific** modulations along several further
  dimensions.
- Optogenetic control: Moonwalker (VT-050660-Gal4 > UAS-Chrimson) slowing acts by **increasing
  stance duration in all six limbs over hundreds of ms** — the same axis as spontaneous speed
  change (M) [V].

### C.4.2 Yaw-rate envelope

**Citation correction.** The paper is **Katsov AY, Freifeld L, Horowitz M, Kuehn S, Clandinin TR
(2017), *eLife* 6:e26410, DOI 10.7554/eLife.26410** (verified against the NCBI record). The
commonly quoted "Katsov, Cohen, Shofer, Clandinin" author list is wrong.


- **|v_R| < 450 °/s** in freely walking flies, binned at 25 °/s (M) [Katsov 2017, V-fetch].
- High yaw rates concentrate at **slow-to-moderate** forward speeds (M) [DeAngelis 2019, V].
- **Inter-peak interval between successive rotational-velocity peaks: 250 ± 110 ms** — the natural
  saccade cadence (M) [Katsov 2017, V-fetch].
- Behaviour structure: **15 submodes** (iterative ICA) grouped into **5 modes** by Markov
  modelling; first-order Markov dependence ρ = 0.271, second order negligible (ρ₂ = 0.015);
  predictive horizon τ_P = **4.3 ± 0.55 s** vs ~1 s velocity autocorrelation decay (M) [V-fetch].
- **Could not verify** a per-saccade amplitude in degrees from Katsov 2017.

### C.4.3 Isakov et al. 2016 — which legs make yaw torque (M/E) [V, read in full]

*J Exp Biol* 219:1760–1771, DOI 10.1242/jeb.133652. Right foreleg amputated between mid-femur and
the femur-tibia joint; Canton-S plus TRPV proprioceptive mutants **nan³⁶ᵃ** (BDSC 24902) and
**iav³⁶²¹** (BDSC 24768).

Turning bias, µ score (µ = 0 unbiased; negative = counter-clockwise):

| Strain | pre-amp | day 0 | day 3 |
|---|---|---|---|
| wild type | **−0.006** | **−0.410** | **−0.031** (P = 0.372 vs pre — recovered) |
| *inactive* | −0.026 | −0.247 | **−0.129** (P < 0.001 — half recovery) |
| *nanchung* | — | — | **−0.250** (P < 0.001 — no recovery; day 3 ≈ day 1) |

Recovery timescale **~3 days** in WT. Speed dropped **34% (WT) / 14% (inactive) / 56% (nanchung)**
immediately post-amputation and never returned to baseline in any strain (WT slope positive,
P = 0.001; inactive P = 0.741; nanchung P = 0.116). Tripod ("3-leg") frequency collapses to ~0
in all genotypes and **never recovers** (P > 0.060) — gait does not come back, the bias does.

**Torque model (E).** Six excitable CPG modules; leg i applies force only while its neuron is
sub-threshold; torque about the body **m_i = (x_i − X)·f_iy − f_ix·(y_i − Y)**, forces rotated
into world frame by R_Θ. Fitted from WT video: ω = 11.4 ± 1.8 strides/s, δ and φ as in §C.1.6 and
§C.2.1. Geometry in body-length units (b.l.u. = **2.5 mm**, b.m.u. = **0.25 mg**):

| | front | mid | hind |
|---|---|---|---|
| attachment point p_y (b.l.u.) | +0.20 | 0 | −0.11 |
| relaxed leg length ℓ* (b.l.u.) | 0.59 | 0.66 | 0.42 |
| relaxed leg length (mm) | 1.48 | 1.65 | 1.05 |
| relaxed leg angle θ* (rad) | 1.19 | 0.33 | 0.69 |

(p_x = ±0.05 b.l.u.; signs on θ* and the relaxed endpoints degraded in PDF extraction.)
Body width 0.34 b.l.u.; inertia 0.01 b.m.u.·b.l.u.²; translational and rotational damping 1.5
(over-damped); leg and neuron relaxation constants **τ_L = τ_N = 10 ms**; threshold 0.9; max
stretch ratio 2; h = 0.001. Steady state **~0.65 body lengths per stride** ⇒ ≈7.4 BL/s ≈ 18.5 mm/s.

**The result the brief asked for:**
- With per-leg forces **held constant**, no genotype recovers turn bias at all — "if anything, all
  three lines exhibited increased bias with time."
- With the left/right force ratio tuned by simulated annealing (1.5 × 10³ steps), the recovery
  trajectory is reproduced to **mean discrepancy < 1%**.
- Sweeping force one leg at a time: **the middle leg needs the smallest force change to hit a given
  turn-bias target, then the hind leg, then the front leg.** Per unit force, **midlegs have the
  greatest yaw leverage**. Required right/left force ratio spans roughly **0.7–1.0** over recovery.
- Recovery significant for all legs in WT (P < 0.038, F-test); in mutants, only the *inactive*
  front leg has a significantly positive slope (P < 0.001).
- Leg **placement** cannot explain it: the WT front-leg centroid distance changed **< 1%** between
  day 0 and day 3.
- The paper explicitly tests and rejects the cockroach division of labour (C) [cockroach]
  (Mu & Ritzmann 2005: forelegs steer, hindlegs propel) as sufficient for the fly.

---

## C.5 Which muscles fire in stance vs swing

### C.5.1 What is actually measured in *Drosophila*

**Honest summary: nobody has published a phase-resolved EMG or muscle-imaging map of all the
leg muscles across the *Drosophila* step cycle.** The pieces that exist:

- **Azevedo et al. 2020**, *eLife* 9:e56754, "A size principle for recruitment of *Drosophila* leg
  motor neurons" (M). The fly leg has **14 muscles innervated by 53 motor neurons**; tibia flexion
  alone is driven by **~15 MNs**. ⚠ Karashchuk et al. 2025 instead state **"approximately 18
  muscles ... approximately 70 motor neurons"** per leg. The counts differ; Azevedo's 14/53 traces
  to Baek & Mann 2009, the 18/70 is the later post-connectome figure. Say which you are using.
  Three classes: **fast ~10 µN/spike, R_in 150 MΩ, V_rest −68 mV,
  silent at rest; intermediate ~1 µN/spike, 300 MΩ, −60 mV, silent; slow <0.1 µN/spike, 700 MΩ,
  −48 mV, tonically firing ~30 Hz at rest**. Recruitment strictly slow→intermediate→fast. Slow MN
  firing rate responds to a **1° (even 0.8°, 6 µm) tibia movement**. **The paper does not break
  firing rate down by swing vs stance** — flies were categorised only as stationary / walking-
  turning / grooming / other. Details in `docs/research/sources/azevedo_2020.md`.
- **Özdil et al. 2025** (arXiv:2509.06426) — *predicted* activations from static optimisation
  against measured walking kinematics, not recorded activity (E):
  - **Pleural remotor abductor (Pra): active at stance onset**, consistent with initiating stance.
  - **Tergopleural promotor and pleural promotor: elevated at the stance→swing transition**,
    driving the coxa forward.
  - **Trochanter flexor and extensor: antiphase during locomotion** (co-active in grooming).
  - Fast tibia flexor and extensor dominate force at the femur-tibia joint.
- **Wang-Chen, Stimpfling, Azcorra & Ramdya 2026** (bioRxiv 10.64898/2026.03.11.711180) —
  closed-loop tracking plus muscle imaging in freely behaving flies; behaviour at 330 Hz, muscle
  imaging at 33 Hz. Recorded the **long-tendon muscles** (in the femur, controlling distal claw via
  tendon). Activity tied to perturbation/posture maintenance; **no stance-vs-swing breakdown
  published** (M) [V-fetch].
- **Mechanosensory-bristle paper, *Current Biology* 2024** — used muscle-GCaMP at the femur-tibia
  joint to read **tibia levator and depressor** activity as a contraction proxy, in a local motor
  response rather than during steady walking [2nd, not read].

**So the fly-specific stance/swing muscle assignment is currently an inference, not a measurement.
Label it as such in the brief.**

### C.5.2 The classic insect assignment — **(C) [stick insect]**

Rosenbaum P, Wosnitza A, Büschges A, Gruhn M (2010). "Activity patterns and timing of muscle
activity in the forward walking and backward walking stick insect *Carausius morosus*."
*J Neurophysiol* **104**(3):1681–1695. DOI 10.1152/jn.00362.2010.
Middle leg; EMG from three antagonist pairs, with electrical touchdown/liftoff detection.
Verified from the NCBI abstract record [V].

| Muscle | Phase (forward walking) | First-spike latency |
|---|---|---|
| **depressor trochanteris** | **stance** | begins **93 ms before touchdown** |
| **flexor tibiae** | **stance** | begins **9 ms after touchdown** |
| **retractor coxae** | **stance** | begins **35 ms after touchdown** |
| **levator trochanteris** | **swing** | begins **100 ms before liftoff** |
| **extensor tibiae** | **swing** | begins **67 ms before liftoff** |
| **protractor coxae** | **swing** | begins **37 ms before liftoff** |

Verbatim: *"Forward walking stance phase muscle (depressor, flexor, and retractor) activities were
tightly coupled to touchdown, beginning on average 93 ms prior to and 9 and 35 ms after touchdown,
respectively. Forward walking swing phase muscle (levator, extensor, and protractor) activities
were less tightly coupled to liftoff, beginning on average 100, 67, and 37 ms before liftoff,
respectively."*

- **Backward walking reverses only the protractor/retractor pair**: retractor becomes a swing
  muscle, protractor a stance muscle. Levator/depressor and flexor/extensor keep their phasing.
  This is the cleanest statement anywhere that the coxal pair carries direction and the distal
  pairs carry the step cycle.
- Changing body height (⇒ changing leg-joint load) altered the **intensity but not the timing** of
  depressor activity.
- Other stick-insect work adds **retractor unguis** (tarsal claw retractor) to the stance set,
  correlated with touchdown (C) [stick insect] [2nd].

**Caveat on importing this.** Stick insect step cycles are an order of magnitude slower than fly
ones — a 93 ms *pre*-touchdown lead is longer than an entire fly swing phase (~30 ms). Scale the
latencies by cycle fraction, not in ms, if you port them.

**Canonical mapping (C) [stick insect / cockroach], to be used as a prior only:**

| Joint | Stance muscle | Swing muscle |
|---|---|---|
| thorax-coxa | retractor (remotor) coxae | protractor (promotor) coxae |
| coxa-trochanter | depressor trochanteris | levator trochanteris |
| femur-tibia | flexor tibiae | extensor tibiae |
| tibia-tarsus / claw | retractor unguis (tarsal depressor) | levator/depressor tarsi |

⚠ **This prior contradicts the measured fly kinematics for two of the three leg pairs.**
Haustein 2024 (M) shows front legs *extend* in swing and *flex* in stance, hind legs do the
opposite, and midlegs flex the tibia through swing and into early stance. So a blanket
"flexor = stance, extensor = swing" rule is wrong for the fly hind leg at minimum. Use the
measured per-leg-pair phase signs in §C.3.1 and treat the stick-insect table as the fallback where
no fly measurement exists.

---

## C.6 Public *Drosophila* walking-kinematics datasets

| Dataset | Content | URL | Licence |
|---|---|---|---|
| **Anipose (Karashchuk et al. 2021)** — "Fly and mouse tracking models and kinematics related to Anipose toolkit paper" (Karashchuk, Walling-Bell, Sanders, Azim, Rupp, Dickinson, Brunton, Tuthill; deposited 2021-11-28) | 3D joint positions **and joint angles** from **39 wild-type Berlin flies** during locomotion; trained DeepLabCut models; original videos with Anipose output. Files: `flyangles-dataset.zip` (4 GB), `fly-anipose.zip` (8.43 GB), `deeplabcut-fly-model.zip` (2.95 GB), plus mouse data. Total 19.35 GB. | https://doi.org/10.5061/dryad.nzs7h44s4 | Not displayed on the landing page. Dryad's default is CC0 1.0 — **could not verify** directly. Anipose the toolkit is CC-BY. |
| **Ispizua et al. 2026, whole-body 3D kinematics** | 50-keypoint whole-body 3D kinematics at 800 fps; 53 flies, 2,213 running bouts (~654,000 frame-sets); tracking error 18.2 ± 8.5 µm | download link given in the preprint as https://bit.ly/3UWoXBF ; code https://github.com/elliottabe/3d_tracking_ik , https://github.com/elliottabe/3d_tracking_dataset , https://github.com/moments-behavior | not stated in the accessible text — **could not verify** |
| **Karashchuk et al. 2025 (layered-walking model)** | code only; the underlying walking data is the 2021 Anipose set | https://github.com/lambdaloop/layered-walking | paper says data "will be released publicly upon publication and privately by request" [V] |
| **NeuroMechFly v2 (Wang-Chen et al. 2024)** | model + kinematic replay data | https://zenodo.org/records/12973000 ; https://github.com/NeLy-EPFL/flygym | see `docs/research/sources/wangchen_2024.md` |
| **NeuroMechFly v1 (Lobato-Rios et al. 2022)** | `data/joint_tracking/{walking,grooming}` in the repo | https://github.com/NeLy-EPFL/NeuroMechFly | Apache-2.0 (verified in that repo audit) |

**Best single choice for joint-angle time series: the Anipose Dryad `flyangles-dataset.zip`**
(39 flies, 1,480 s of walking, 300 Hz, 8 angles per leg). For whole-body including CoM height,
the Ispizua 2026 set.

---

## C.6a Full citations for everything used here

| Short | Full |
|---|---|
| Mendes 2013 | Mendes CS, Bartos I, Akay T, Márka S, Mann RS. *eLife* 2:e00231. DOI 10.7554/eLife.00231 |
| Wosnitza 2013 | Wosnitza A, Bockemühl T, Dübbert M, Scholz H, Büschges A. *J Exp Biol* 216(3):480–491. DOI 10.1242/jeb.078139 |
| Szczecinski 2018 | Szczecinski NS, Bockemühl T, Chockley AS, Büschges A. *J Exp Biol* 221:jeb189142. DOI 10.1242/jeb.189142 |
| DeAngelis 2019 | DeAngelis BD, Zavatone-Veth JA, Clark DA. *eLife* 8:e46409. DOI 10.7554/eLife.46409 |
| Chun 2021 | Chun C, Biswas T, Bhandawat V. *eLife* 10:e65878, 3 Feb 2021. DOI 10.7554/eLife.65878. PMID 33533718 |
| Karashchuk 2021 | Karashchuk P, Rupp KL, Dickinson ES, Walling-Bell S, Sanders E, Azim E, Brunton BW, Tuthill JC. *Cell Reports* 36(13):109730. DOI 10.1016/j.celrep.2021.109730 |
| Haustein 2024 | Haustein M, Blanke A, Bockemühl T, Büschges A. *Front Bioeng Biotechnol* 12:1357598. DOI 10.3389/fbioe.2024.1357598 |
| Godesberg 2024 | Godesberg V, Bockemühl T, Büschges A. *J Exp Biol* 227(22):jeb247878. DOI 10.1242/jeb.247878. PMID 39422060 |
| Katsov 2017 | Katsov AY, Freifeld L, Horowitz M, Kuehn S, Clandinin TR. *eLife* 6:e26410, 25 Jul 2017. DOI 10.7554/eLife.26410. PMID 28742018 |
| Isakov 2016 | Isakov A, Buchanan SM, Sullivan B, Ramachandran A, Chapman JKS, Lu ES, Mahadevan L, de Bivort B. *J Exp Biol* 219(11):1760–1771. DOI 10.1242/jeb.133652 |
| Azevedo 2020 | Azevedo AW, Dickinson ES, Gurung P, Venkatasubramanian L, Mann RS, Tuthill JC. *eLife* 9:e56754. DOI 10.7554/eLife.56754 |
| Lobato-Rios 2022 | Lobato-Rios V, Tata Ramalingasetty S, Özdil PG, Arreguit J, Ijspeert AJ, Ramdya P. *Nat Methods* 19(5):620–627. DOI 10.1038/s41592-022-01466-7 |
| Wang-Chen 2024 | Wang-Chen S, et al., Ramdya P. *Nat Methods* 21:2353–2362. DOI 10.1038/s41592-024-02497-y |
| Karashchuk 2025 | Karashchuk L, Li JS, Chou GM, Walling-Bell S, Brunton SL, Tuthill JC, Brunton BW. *eLife* 13:RP99005, 15 May 2025. DOI 10.7554/eLife.99005. PMID 40372779 (same first author as Karashchuk 2021, published there as Pierre Karashchuk) |
| Özdil 2025 | Özdil PG, Ning C, Phelps JS, Wang-Chen S, Elisha G, Blanke A, Ijspeert A, Ramdya P. arXiv:2509.06426, CC BY 4.0 |
| Ispizua 2026 | Ispizua JI, Abe ETT, Yan J, Othayoth R, Sawtelle S, Atkins F, Shiozaki HM, Meier NR, Wong J, Tran T, Mori C, Voigts J, Stern DL, Brunton BW, Tuthill JC, Johnson RE. bioRxiv, DOI 10.64898/2026.05.03.722293. PMID 42146626 |
| Wang-Chen 2026 | Wang-Chen S, Stimpfling VA, Azcorra M, Ramdya P. bioRxiv, DOI 10.64898/2026.03.11.711180 |
| Rosenbaum 2010 **(C) stick insect** | Rosenbaum P, Wosnitza A, Büschges A, Gruhn M. *J Neurophysiol* 104(3):1681–1695. DOI 10.1152/jn.00362.2010. PMID 20668273 |

---

## C.7 Open items

1. **NeuroMechFly v2 per-joint measured angle ranges** — supplementary tables unreachable. [§C.3.4]
2. **Absolute AEP/PEP coordinates in mm** for the six legs — not published by Mendes 2013;
   check Ispizua 2026's tarsus-tip distributions or extract from the Anipose Dryad set. [§C.1.7]
3. **The Haustein 2024 front-leg duplicate (40.87° for two different DOFs)** — needs the figure
   or the authors to resolve. [§C.3.1]
4. **A phase-resolved fly leg muscle activity map** — does not appear to exist yet. [§C.5.1]
5. **Wosnitza 2013 numbers** were taken from a single automated read of the JEB page; re-verify
   against the PDF before any of them go into a figure. [§C.1, §C.2]
6. **Licence of the Anipose Dryad deposit** — assumed CC0, not confirmed. [§C.6]
