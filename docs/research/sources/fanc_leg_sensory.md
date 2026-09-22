# FANC (Female Adult Nerve Cord) — leg sensory / proprioceptor reconstructions

## Phelps et al. 2021 — the FANC EM volume

Phelps JS, Hildebrand DGC, Graham BJ, Kuan AT, Thomas LA, Nguyen TM, Buhmann J,
Azevedo AW, Sustar A, Agrawal S, Liu M, Shanny BL, Funke J, Tuthill JC, Lee W-CA (2021).
*Reconstruction of motor control circuits in adult Drosophila using automated transmission
electron microscopy.* **Cell 184(3):759–774.e18.** DOI **10.1016/j.cell.2020.12.013**.
PMID 33400916, PMCID PMC8312698. — citation VERIFIED via Europe PMC core record.

- **507 motor neurons** controlling the limbs, all reconstructed. (VERIFIED from the abstract.)
- The leg sensory finding: "a specific class of leg sensory neurons synapses directly onto
  motor neurons with the largest-caliber axons on both sides of the body, representing a
  unique pathway for fast limb control." That class is the **bilateral campaniform
  sensillum (bCS) neurons = the trochanter campaniform sensilla (TrCS)**, which MANC calls
  `SNpp53`. Marin et al. note two TrCS per leg nerve except the left prothoracic,
  "consistent with previous reports (Phelps et al., 2021)."
- FANC has **no systematic sensory naming scheme** comparable to MANC's `SNxx##`. Leg
  sensory axons in FANC are labelled ad hoc, per-study, mostly by organ name.

## Azevedo et al. 2024 — the FANC connectome paper

Azevedo A, Lesser E, Phelps JS, Mark B, Elabbady L, Kuroda S, Sustar A, Moussa A,
Khandelwal A, Dallmann CJ, Agrawal S, Lee S-YJ, Pratt B, Cook A, Skutt-Kakaria K,
Gerhard S, Lu R, Kemnitz N, … Seung HS, Tuthill JC, Lee W-CA (2024).
*Connectomic reconstruction of a female Drosophila ventral nerve cord.*
**Nature 631(8020):360–368.** DOI **10.1038/s41586-024-07389-x**.
PMID 38926570, PMCID PMC11348827. — citation VERIFIED via Europe PMC + PMC full text.

VERIFIED counts (from the abstract and Extended Data Fig. legends in the PMC full text):
- **~45 million synapses; ~14,600 neuronal cell bodies** in the VNC.
- Somata-bearing classes: **interneurons n = 12,468; ascending neurons n = 1,668;
  motor neurons n = 485.**
- Motor neuron breakdown: **leg MNs (T1+T2+T3) n = 371**, wing MNs (ADMN + PDMN + MesoAN)
  n = 58, haltere MNs n = 32, neck MNs n = 24.
- **Sensory neurons are NOT in the 14,600.** Their somata are peripheral and were excised
  in sample prep; FANC's sensory content is only the axons entering the volume, and those
  were only sparsely proofread. This is the single biggest structural difference from MANC,
  which explicitly reconstructed and typed ~6,500 sensory axons.
- ~30% of non-sensory neurons were community-proofread at the time of publication.

## Lesser et al. 2024 — premotor networks (FANC)

Lesser E, Azevedo AW, Phelps JS, Elabbady L, Cook A, Syed DS, Mark B, Kuroda S, Sustar A,
Moussa A, Dallmann CJ, Agrawal S, Lee S-YJ, Pratt B, Skutt-Kakaria K, … Tuthill JC (2024).
*Synaptic architecture of leg and wing premotor control networks in Drosophila.*
**Nature 631(8020):369–377.** DOI **10.1038/s41586-024-07600-z**. PMID 38926579,
PMCID PMC11356479. — citation VERIFIED via Europe PMC.

- This paper is about **premotor interneurons, not sensory typing.** It does **not**
  enumerate FeCO claw/hook/club. Its one relevant sensory number: the only MNs receiving
  >10% of synaptic input directly from sensory neurons are four tonic wing MNs —
  **iii3 = 18.5%, b1 = 17.3%, b3 = 13.5%, i2 = 11%** (VERIFIED from the PMC full text).
  Leg MNs do not cross that threshold.

## Lee, Dallmann, Cook, Tuthill, Agrawal 2025 — THE FANC FeCO paper (this is the one with claw/hook/club numbers)

Lee S-YJ, Dallmann CJ, Cook A, Tuthill JC, Agrawal S (2025).
*Divergent neural circuits for proprioceptive and exteroceptive sensing of the Drosophila leg.*
**Nature Communications 16:4105.** DOI **10.1038/s41467-025-59302-3**. PMID 40316553,
PMCID PMC12048489. — citation VERIFIED via Europe PMC; content VERIFIED by reading the
PMC full text.

**FeCO subtype scheme used here (5 functional subtypes, not 3):**
1. extension-encoding **claw** — tibia position
2. flexion-encoding **claw** — tibia position
3. extension-encoding **hook** — tibia movement
4. flexion-encoding **hook** — tibia movement
5. **club** — bidirectional tibia movement + low-amplitude (<1 µm) high-frequency vibration

"Claw, hook, and club neurons are named after the shape of their axons in the VNC."
FeCO total ≈ **~150 excitatory (cholinergic) sensory neurons** per leg.

**Reconstructed FANC counts — front-LEFT leg (T1L) only (VERIFIED, Fig. 1F legend):**

| subtype (in figure order) | n reconstructed |
|---|---|
| claw, extension | 8 |
| claw, flexion | 13 |
| hook, extension | 9 |
| hook, flexion | 13 |
| club | 37 |
| **total** | **80** |

→ claw 21, hook 22, club 37. The authors estimate this is **~50% of the T1L axons of each
subtype** (their Supplementary Table 2). 5 of the 37 club axons send an ascending
projection to the brain.

**Direct FANC-vs-MANC comparison, quoted verbatim from the paper:**
> "we reconstructed roughly half of the FeCO axons from the front left leg (80 total axons).
> For comparison, the other publicly available VNC connectome dataset, **MANC (v.1.2.1),
> had only 22 T1L FeCO axons reconstructed**, and many of these were incomplete and missing
> branches."

(My own count off the live MANC v1.2.3 table for ProLN_L gives 21 FeCO-tagged axons
— 10 club, 4 claw, 7 hook — which corroborates their 22 almost exactly.)

Why leg sensory reconstruction is bad in *every* VNC dataset, quoted:
> "Leg sensory neurons have consistently darker cytoplasm and more fragmented cell
> membranes, leading to poor automatic neuron segmentations and synapse predictions…
> likely due to rapid degeneration that begins when the legs are dissected away from the
> VNC during sample preparation."

The paper uses **FANC** for the VNC side and **FlyWire/FAFB** for the brain side.

## Lesser, Moussa, Tuthill 2026 — FANC wing proprioceptors

Lesser E, Moussa AJ, Tuthill JC (2026). *Peripheral anatomy and central connectivity of
proprioceptive sensory neurons in the Drosophila wing.* **eLife 14:RP107867.**
DOI **10.7554/eLife.107867**. PMCID PMC12975126. — citation VERIFIED via Europe PMC.
Reconstructs wing sensory axons from FANC and maps them to peripheral sensilla; identifies
a novel putative-proprioceptor population monosynaptic onto wing steering MNs. Reported
**490 sensory axons and 14 motor axons in the left ADMN** (REPORTED SECOND-HAND from a
search snippet; I did not verify this number in the source).

## FeCO size reference

The "~152 FeCO neurons in the proximal femur" figure that Marin et al. cite comes from
**Kuan AT et al. 2020** (X-ray holographic nano-tomography). Lee et al. 2025 give "~150".
Both are consistent; use ~150.
