# DeAngelis, Zavatone-Veth & Clark 2019

**Citation.** DeAngelis BD, Zavatone-Veth JA, Clark DA (2019). "The manifold structure of limb coordination in walking *Drosophila*." *eLife* 8:e46409. DOI 10.7554/eLife.46409.
URL: https://elifesciences.org/articles/46409 · PDF read in full (pdftotext -layout).

**Method.** Planar arena, flies illuminated from above, filmed in silhouette from below at **150 fps**. Groups of 12–15 female flies loaded per run. Aggregate wild-type free-walking dataset merged from recordings totalling **114 flies**. Optogenetic datasets: 96 flies (visual/Moonwalker), 44 flies (backlit). Wild-type strain "+; +; +" from Gohl et al. 2011.

## Body kinematics
- Forward velocity v∥: **−1.3 to 30.4 mm/s** (2.5th and 97.5th percentiles). Distribution has peaks at **0 mm/s** and **~17.5 mm/s**.
- Locomotion inclusion threshold: v∥ > 0.5 mm/s (excludes stopping and grooming).
- Speed terciles used throughout: **slow 0–10.2, medium 10.2–19, fast >19 mm/s**.
- "Flies turn at a broad range of yaw rates across many forward speeds"; the highest |v_r| occurs at slow-to-moderate forward speeds. No numeric yaw range printed.

## Limb kinematics
- Swing/stance classification: frame-to-frame limb displacement above ~**0.13 mm** in the camera frame ⇒ swing.
- Step length in the stationary camera frame increases roughly linearly with v∥.
- **"Stance duration was approximately inversely proportional to forward walking speed (τ_stance ~ v∥^−1.025; R² = 0.59)."** — verbatim.
- **"Across walking speeds, swing duration increased, but this modulation is small in comparison to the change in stance duration."** — verbatim. So swing is *near*-invariant, not invariant.
- Consistent with "walking speed differences are dominated by changes in stance duration, while swing duration remains relatively constant."

## Gait configurations
- Probability maxima by number of feet in stance: **5-foot-down at 7 mm/s, 4-foot-down at 13 mm/s, 3-foot-down at 24 mm/s**.
- At slow speeds (v∥ ≤ 10.2 mm/s), many canonical configurations are transient — as short as one frame (**~6.7 ms**) — though longer durations exist for tripod, tetrapod and wave configurations.
- **"Tetrapod and wave gait configurations are predominantly transient in all but the slowest walking condition."**

## Phase relations (Figure 3)
- **Contralateral pairs: ⟨Δφ⟩ ≈ 0.5, "constant at 0.5 cycles across all walking speeds."**
- **Ipsilateral mid-fore and hind-mid: ⟨Δφ⟩ ≈ 0.4** — "not on average in antiphase", unlike a perfect tripod.
- **Ipsilateral hind-fore: ⟨Δφ⟩ ≈ 0.85** — not in phase.
- Mean ipsilateral phases are **not** constant across speed and "approach a tripod-like coupling at the fastest forward walking speeds."
- **"All pairwise relative phases exhibit a monotonic decrease in angular deviation as forward [velocity increases]"** — the real speed effect is variance, not mean.
- Joint distribution of (L2-R2, L3-L1) phases is **unimodal**, peak closest to canonical tripod, "no peaks in the distribution at locations [of tetrapod/wave]".
- Conclusion: **"the spontaneously walking fruit fly uses a single continuum of limb relative phases"**, with "no evidence for discrete preferred patterns".

## Manifold
- Segments of **100 ms** at 150 fps: **31 frames × 6 limbs × 2 spatial coords = 372 dimensions**; 10⁵ randomly sampled segments embedded with UMAP.
- Result: a **bell-shaped manifold in three dimensions**. The axial dimension is parameterised by **mean stepping frequency**; the circumference is the phase. Distribution along the axis is unimodal.
- **No PCA variance decomposition and no "number of PCs" is reported.** Anyone quoting a PC count for this paper is inventing it.

## Turning (Figure 6, restricted to v∥ 15–20 mm/s)
Verbatim: *"On average, the swing durations of the inside mid- and hind-limbs decrease as a function of turning rate, while their stance durations increase. The swing and stance durations of the remaining limbs are oppositely modulated. At the highest yaw rates, the net modulation of stepping frequency is about 25%. The step length of the inside forelimb is not significantly modulated during turning. The step lengths of the outside limbs increase with yaw rate while step lengths of the inside midlimb and hindlimb decrease with increasing turning rate."*

Verbatim on step direction: *"The remaining path length differential between [the fore]limbs is achieved through modulation of the stance direction of the inside forelimb, which is modulated more dramatically than that of other limbs, by up to about 45˚."* Also: *"Our measurements of the two forelimbs show nearly identical modulations of stepping frequency and modest differences in step length modulations."*

Turn timing: yaw-rate extrema occur at preferred limb phases, differing from the time-invariant distribution with **p < 10⁻⁵ for all limbs** (Table 4). "The tripod containing the inside forelimb is in nearly its [preferred configuration]".

## Perturbation
Moonwalker (+; +; VT-050660-Gal4 / UAS-Chrimson, from Bidaye et al. 2014; n = 8 in the strain table) optogenetic slowing: transient **increase in stance duration in all six limbs over hundreds of milliseconds**. Control n = 91 random-trigger trials. Speed perturbation acts along the same axis as spontaneous speed change.

## Verified / could not verify
Everything above read from the eLife PDF. **Could not verify**: a numeric yaw-velocity range in °/s (the paper plots it without printing bounds); explicit swing-duration values in ms (only the trend is stated); a PCA dimensionality.
