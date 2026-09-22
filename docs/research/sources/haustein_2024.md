# Haustein, Blanke, Bockemühl & Büschges 2024

**Citation.** Haustein M, Blanke A, Bockemühl T, Büschges A (2024). "A leg model based on anatomical landmarks to study 3D joint kinematics of walking in *Drosophila melanogaster*." *Frontiers in Bioengineering and Biotechnology* **12**:1357598. Published 26 June 2024. DOI 10.3389/fbioe.2024.1357598.
PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC11233710/ · PDF read in full (pdftotext -layout).

⚠ **Naming trap.** This paper is often mis-attributed to Dallmann/Karashchuk/Brunton/Tuthill. It is the **Büschges lab, Cologne** (Haustein, Blanke, Bockemühl, Büschges). Cite it correctly.

**Method.** Multi-camera motion capture at **400 Hz**, 896 × 540 px; **12 flies (5 females, 7 males)**; walking on a **6 mm** spherical treadmill; mean walking speed **14.7 ± 4.0 mm/s, n = 2,250 steps**. Leg model built from a µCT scan with **yaw rotational axes derived from the positions of the joint condyles** (oblique, anatomical) rather than orthogonalised to the segments.

**Convention.** Per joint: **yaw** = the main condylar rotational axis; **roll** = along the leg-segment vector controlled by the joint (longitudinal rotation); **pitch** = cross product of yaw and roll. Joints: ThCx, CxTr, TrFe, FeTi, TiTar. ROM = max − min observed angle per DOF, mean ± SD over the 12 flies. Sign convention: values are for right legs; invert yaw and roll (not pitch) for left legs.

## Measured ROM during forward walking — verbatim sources

> "Although the ThCx-roll DOF was used by all three leg pairs, it was most extensively used by the front legs (ROM: 40.87° ± 5.21°) and only to a lesser amount by the hind (ROM: 11.27° ± 3.01°) and middle (ROM: 4.91° ± 2.67°) legs."

> "the ROM observed for the individual leg pairs differed with 40.87° ± 5.21°, 26.48° ± 4.58°, and 18.60° ± 3.85° for the front, middle, and hind legs, respectively" [promotion/remotion of the coxa]

> "While the ROM was comparable for all leg pairs (front legs: 8.24° ± 2.74°, middle legs: 7.63° ± 2.85°, hind legs: 8.85° ± 2.98°)" [adduction/abduction]

> "These movements were generally more pronounced in the front and hind legs than in the middle legs (ROM of CxTr/FeTi for front, middle, and hind legs: 91.24° ± 9.54°/96.55° ± 7.65°, 22.51° ± 3.38°/21.52° ± 5.43°, 56.34° ± 9.00°/84.11° ± 9.94°)."

Collated:

| Motion | Front T1 | Middle T2 | Hind T3 |
|---|---|---|---|
| coxa promotion/remotion | 40.87 ± 5.21° | 26.48 ± 4.58° | 18.60 ± 3.85° |
| coxa adduction/abduction | 8.24 ± 2.74° | 7.63 ± 2.85° | 8.85 ± 2.98° |
| ThCx-roll | 40.87 ± 5.21° ⚠ | 4.91 ± 2.67° | 11.27 ± 3.01° |
| CxTr-yaw (trochanter flex/ext) | 91.24 ± 9.54° | 22.51 ± 3.38° | 56.34 ± 9.00° |
| FeTi-yaw (tibia flex/ext) | 96.55 ± 7.65° | 21.52 ± 5.43° | 84.11 ± 9.94° |

⚠ Front-leg promotion/remotion and front-leg ThCx-roll are printed with the **same value** (40.87 ± 5.21) in two separate sentences. Likely a copy-paste error in the paper for one of them. Not corrected here.

## Which DOF drives which motion
> "In the front and hind legs, promotion and remotion of the coxa was mainly driven by the ThCx-pitch DOF, while the ThCx-yaw DOF performed that movement in the middle legs. ... In contrast, adduction and abduction was governed by the yaw DOF in the front and hind legs and by the pitch DOF in the middle legs."

## Step-phase signs — the part most models get wrong
> "extension and flexion of the leg were performed during swing and stance phase, respectively, in the front legs. In contrast, in the hind legs flexion of the leg was performed in the swing phase, while extension of the leg was observed in the stance phase."

> "For the middle legs, however, flexion and extension of the trochanter occurred in swing and stance phase, but flexion of the tibia was observable almost during the entire swing phase and continued in the first half of the stance phase, while extension of the tibia occurred mainly in the second half of the stance phase. Additionally, flexion of the tibia in the middle legs was not gradual as compared to the front and hind legs, but it was more prominent at the early stance phase."

> "promotion and remotion occurred in all leg pairs during the swing and stance phase, respectively."

Front-leg TrFe-roll: lateral rotation of the femur-tibia plane in the first half of swing, continued through the first half of stance, then medial rotation for the remaining stance.

## Femur-tibia plane rotation in the middle legs (the "femur rotation" Anipose saw)
- Full model: median rotational range **42.6° (IQR 10.7°)** in swing, **40.7° (IQR 6.5°)** in stance. n = 238 swing / 215 stance phases.
- Reductions when only selected DOFs are updated (mean difference ± 95% CI, swing/stance):
  - ThCx-pitch only: **−35.1° ± 0.9° / −32.9° ± 1.0°**
  - ThCx-roll only: **−33.0° ± 0.9° / −31.1° ± 1.1°**
  - ThCx-yaw only: **−17.9° ± 0.4° / −16.2° ± 0.4°**
  - CxTr-yaw only: **−24.2° ± 0.8° / −26.3° ± 0.6°**
  - **ThCx-yaw + CxTr-yaw: −0.8° ± 1.1° / −1.4° ± 0.9°** — almost complete recovery.
- Conclusion: the two most proximal **yaw** DOFs produce the midleg femur-tibia plane rotation; **no TrFe roll DOF is needed for the midlegs** (the front legs do need one).

## Table 1 — model joint DOF angle constraints (right legs; degrees)

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

Note in the table: "values indicate constraints for joint DOFs, of the right legs. The sign had to be inverted to obtain values for yaw and roll DOFs, of the left legs, but not for pitch DOFs." The paper also states "ROMs of joint DOFs in *Drosophila* are not known" as the reason these limits are generous.

## Model error
Summed Euclidean distance over CxTr, TrFe, FeTi, TiTar and tarsus tip vs tracked positions:
- front legs **342 ± 61 µm to 560 ± 80 µm** (n swing/stance 232/213)
- middle legs **100 ± 34 µm to 136 ± 46 µm** (238/215)
- hind legs **126 ± 47 µm to 154 ± 49 µm** (239/224)
Orthogonalising the joint axes increased relative mean error by up to **102% (front), 83% (middle), 56% (hind)** — anatomical oblique axes matter.

## Verified / could not verify
All the above read directly from the PDF. **Could not verify**: leg segment lengths in µm/mm (not printed); explicit joint-axis orientation angles in degrees.
