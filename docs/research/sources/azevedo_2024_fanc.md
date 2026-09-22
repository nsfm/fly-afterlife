# Azevedo et al. 2024 — FANC, and the MN→muscle atlas

**VERIFIED**: passages below extracted first-hand from the open PMC full text
(PMC11348827) on 2026-09-21. Quotes are verbatim from that text.

> Azevedo A, Lesser E, Phelps JS, Mark B, et al. (35 authors).
> "Connectomic reconstruction of a female *Drosophila* ventral nerve cord."
> ***Nature* 631, 360–368 (2024).** DOI `10.1038/s41586-024-07389-x`. PMID 38926570.
> Corresponding: Wei-Chung Allen Lee, John C. Tuthill.

## Dataset scale

> "the fly VNC contains roughly **45 million synapses and 14,600 neuronal cell bodies**."

Efferent counts (from an Extended Data legend):
- **leg motor neurons, all T1+T2+T3: n = 371**
- haltere MNs: n = 32 · neck MNs: n = 24 · wing MNs (ADMN, PDMN, MesoAN): n = 58
- ascending neurons n = 485 (for the comparison in that panel)

Per-front-leg: **"69 in left T1, 70 in right T1"**. The extra right-side cell
> "appears to be a second tarsus levator MN. Supernumerary MNs have been described in the
> locust leg motor system … but—to our knowledge—have not been described in flies."

## How the MN→muscle map was actually made (the method to copy)

Three imaging modalities fused:
1. EM (FANC) — proofread all MNs innervating T1.
2. **X-ray holographic nanotomography (XNH)** of the front leg (Kuan et al., *Nat Neurosci*
   23:1637–1643, 2020) — trace motor nerves/axons into their target muscles.
3. **Sparse genetic driver lines** (MCFO screen over Meissner et al. *eLife* 12:e80660, 2023)
   — image GFP in the leg to read each MN axon's muscle target, then match dendritic morphology
   back to the FANC reconstruction.

Effort focused on the **left** T1 because the left prothoracic leg nerve (ProLN) is more intact.

Independent quantitative corroboration: T1 neuromere diced into 8 µm cubic voxels, synaptic
density per MN per voxel (**1,891 voxels × 69 MNs**), UMAP → "clear clusters of MNs that
innervate synergistic muscles."
**Supplementary Table 1 contains Neuroglancer links for the leg motor neurons.** ← the practical
handle if you need per-MN muscle labels.

## Muscle-target abbreviations used in Fig. 4c (verbatim legend)

> "Acc, accessory; Fe, femoral; Pl, pleural; Sternotr., sternotrochanter; Ta, tarsal;
> Tergotr., tergotrochanter; Ti, tibial; Tr, trochanter."

Fig. 4c is the figure this project actually wants: MNs "grouped by leg segment (rows) and by
**muscle target** (each square)", with each MN coloured **orange = swing** vs **blue = stance**
("muscle groups that drive the leg to swing forward or reach (orange) versus muscles that push
the body forward (blue)"), against joint angles from a fly on a spherical treadmill.
→ A ready-made swing/stance sign convention per muscle group, straight from the connectome paper.

## Specific facts that bear on a muscle-drive mapping

- **Femur reductor**: "we found that **six MNs innervate the femur reductor muscle in the
  trochanter**." The paper flags these as *"the femur reductor MNs that target the trochanter,
  whose function is unknown"* (red square in Fig. 4c). It was previously assumed the *Drosophila*
  trochanter and femur are functionally fused; FANC says the trochanter has its own MNs and
  musculature.
- **Long tendon muscle (LTM)**: multi-joint, fibres in both femur (**ltm2**) and tibia (**ltm1**)
  inserting on one long tendon (**retractor unguis**) that runs femur→claw and **controls the
  tarsal claw**. "**four LTM MNs** have extensive medial branches; **two target ltm2, two target
  ltm1**. The specific targets of **four smaller LTM MNs** cannot be resolved from the XNH volume."
  → LTM is one drive channel that moves *two* joints; do not model it as a single-joint torque.
- **Polyneuronal innervation** (one muscle fibre, several MNs) confirmed from XNH in: the **LTM**,
  the **proximal fibres of the trochanter flexor**, and the **femur reductor**.
  → Summing MN rates within these muscle groups is not obviously the right pooling rule.
- Tibia motor pool named cells: **SETi** (slow extensor tibiae) and **FETi** (fast extensor
  tibiae); "main tibia flexor MNs (Fast flexor)"; "pleural coxa promotor MNs".
- XNH femur cross-section colour key: tibia extensor fibres, tibia flexor fibres, LTM fibres,
  and the **femoral chordotonal organ** — i.e. the FeCO sits inside the femur alongside those.

## Companion paper

Lesser E, et al. (33 authors). "Synaptic architecture of leg and wing premotor control networks
in *Drosophila*." *Nature* **631**, 369–377 (2024). DOI `10.1038/s41586-024-07600-z`. **VERIFIED
via Crossref.** (Same issue; the premotor-side analysis of the same atlas.)

## Nomenclature warning (from Azevedo et al. 2020 eLife 56754, fetched first-hand)

The naming chain is **Snodgrass 1935 → Miller 1950 → Soler et al. 2004 → Baek & Mann 2009 /
Brierley et al. 2012**, and it is *not* self-consistent:

> "Soler et al. in turn based their nomenclature on Miller, 1950. There appears to be a
> **discrepancy** between the two: the muscle named the **tibia reductor** muscle by Soler et al.
> is described as **one of two depressor muscles by Miller, muscles 40 and 41**. Miller applied the
> nomenclature of Snodgrass, 1935 to *Drosophila* leg muscles."

and

> "For clarity, however, we refer to muscles of the femur as **flexors or extensors**, rather than
> as depressors or levators, which refer to the natural stance of the insect."

> "The muscle fibres in this distal region have been collectively referred to as the **reductor**
> muscle (Baek and Mann, 2009; Brierley et al., 2012; Soler et al., 2004), but their alignment and
> attachment points suggest they **control flexion of the tibia**."

→ Practical consequence for this project: a label like "femur reductor" is ambiguous across
sources. Pin the mapping to **FANC/MANC MN identity**, not to a muscle name string.
