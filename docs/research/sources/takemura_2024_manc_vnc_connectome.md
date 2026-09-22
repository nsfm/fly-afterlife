# Takemura et al. 2024 — A Connectome of the Male Drosophila Ventral Nerve Cord

## Citation

Takemura S†, Hayworth KJ†, Huang GB†, Januszewski M†, Lu Z†, Marin EC†, Preibisch S†,
Xu CS†, Bogovic J, Champion AS, Cheong HSJ, Costa M, Eichler K, Katz W, Knecht C, Li F,
Morris BJ, Ordish C, Rivlin PK, Schlegel P, Shinomiya K, Stürner T, Zhao T, … Rubin GM,
Scheffer LK, Funke J, Saalfeld S, Hess HF, Plaza SM, Card GM, Jefferis GSXE, Berg S (2024).
*A Connectome of the Male Drosophila Ventral Nerve Cord.* **eLife 13:RP97769.**
(† equal contribution.)

- eLife reviewed-preprint DOI **10.7554/eLife.97769.1**, Reviewed Preprint v1 posted **2024-05-23** — VERIFIED (fetched elifesciences.org/reviewed-preprints/97769 and /97769v1).
- Underlying preprint: bioRxiv **10.1101/2023.06.05.543757**, v1 posted 2023-06-06 — VERIFIED (downloaded the cover PDF and read the author list off it).
- Corresponding: Gwyneth.Card@columbia.edu, jefferis@mrc-lmb.cam.ac.uk, bergs@janelia.hhmi.org.
- I could NOT obtain the full body text PDF of either version (bioRxiv served only a 4-page
  cover; the eLife PDF endpoint returned empty). Numbers below are from the eLife
  reviewed-preprint web page — **VERIFIED by fetching that page**, but not by reading a
  methods table, so treat the rounded ones as rounded.

## Counts (VERIFIED off the eLife RP page)

| quantity | value |
|---|---|
| traced neurons, total | ~23,000 ("roughly 23 thousand traced neurons") |
| descending neurons | ~1,300 |
| motor neurons | ~700 |
| descending + motor, stated total | 2,065 |
| sensory + intrinsic (i.e. everything that is not DN/MN) | 21,683 |
| TBars (presynaptic sites) | 10 million |
| PSDs (postsynaptic densities) | 74 million |
| total neuronal cable | 44 m |

2,065 + 21,683 = 23,748 bodies. Cross-checking against the companion annotation paper
(Marin et al.) and the live v1.2.3 annotation table gives the finer split:
DN 1,322 / MN 733 / sensory 6,526 / intrinsic 13,066 / ascending 1,865 / efferent 92+9 / glia 349.

**Sensory count: ~6,500** (the same number Marin et al. give; 6,462 typed in v1.2.1,
6,526 sensory-class bodies in v1.2.3). — the "over 5,000 linked to a sensory modality"
figure quoted by secondary sources is consistent with 6,526 − 1,430 unknown = 5,096.
**REPORTED SECOND-HAND, could not verify the exact "over 5,000" phrasing in the source.**

## Leg neuropil ROI definitions

The connectome's ROI hierarchy (VERIFIED from `all_ROIs.txt` shipped in the public
`gs://flyem-manc-exports/v1.0/neuprint_manc_v1.0/` export):

- **`LegNp(T1)(L)`, `LegNp(T1)(R)`, `LegNp(T2)(L/R)`, `LegNp(T3)(L/R)`** — the six leg
  neuropils, one per leg. These are the ventral neuromere regions containing leg MN
  dendrites and leg sensory afferents.
- **`mVAC(T1)(L/R)`, `mVAC(T2)(L/R)`, `mVAC(T3)(L/R)`** — medial ventral association
  centres, one per hemineuromere; **this is where the FeCO club afferents terminate** and
  it is treated as a separate ROI from LegNp.
- `ANm` — abdominal neuromere (fused).
- Upper tectulum: `NTct(UTct-T1)(L/R)` neck tectulum, `WTct(UTct-T2)(L/R)` wing tectulum,
  `HTct(UTct-T3)(L/R)` haltere tectulum.
- `IntTct` intermediate tectulum, `LTct` lower tectulum, `Ov(L/R)` ovoid, `CV` cervical
  connective region, `GF(L/R)` giant fibre.
- Every nerve is also its own ROI: `ProLN(L/R) ProAN(L/R) VProN(L/R) DProN(L/R) PrN(L/R)
  ProCN(L/R) ADMN(L/R) PDMN(L/R) MesoAN(L/R) MesoLN(L/R) DMetaN(L/R) MetaLN(L/R)
  CvN(L/R) AbN1(L/R) AbN2(L/R) AbN3(L/R) AbN4(L/R) AbNT`.

In the DVID/Clio `target` annotation the same regions appear bracket-free and
dot-concatenated: `LegNpT3_R`, `mVACT2_L.LegNpT2_L`, `Ov_L`, `UTct_R`, `ANm`, `multi`.

## Companion papers in the MANC series

- Marin et al. 2024, eLife 13:RP97766, DOI 10.7554/eLife.97766.1 — annotation + sensory typing (see `marin_2024_manc_annotation.md`).
- Cheong, Eichler, Stürner et al. 2024, eLife 13:96084 — "Organization of circuits linking descending input to motor output in the Drosophila Male Adult Nerve Cord connectome", DOI 10.7554/eLife.96084 (preprint bioRxiv 10.1101/2023.06.07.543976). VOR exists (elifesciences.org/articles/96084).
- Insight: "Connectomes: Mapping the fly nerve cord", eLife 13:e99804 (PMC11233131).
