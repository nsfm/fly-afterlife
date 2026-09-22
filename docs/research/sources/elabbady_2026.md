# Elabbady et al. 2026 — central somatotopic map of the fly leg (BRISTLES)

**Citation:** Elabbady L, Chou GM, Sustar A, Cook A, Collman F, Tuthill JC (2026). *A central
somatotopic map of the fly leg supports spatially targeted grooming.* **Current Biology
36:2192–2206.e4.** doi:10.1016/j.cub.2026.03.045. PMID 41966690.
Preprint: bioRxiv doi:10.64898/2026.02.27.708590.
Code: https://github.com/tuthill-lab/elabbady_bristles_2026
**Status: VERIFIED — bioRxiv full text read (journal version paywalled).**

## Bristle counts
- **"The front leg of Drosophila melanogaster is covered by more than 400 mechanosensory bristles,
  with the highest density on the more distal leg segments"** — citing **Held LI Jr (1991),
  BioEssays 13:633–640** (not opened by me).
- **409 bristle axons reconstructed** from the front left leg in FANC:
  **394 via the leg nerve, 8 via the ventral prothoracic nerve (VProN), 7 via the dorsal prothoracic
  nerve (DProN)**. A further **<20** could not be reconstructed (segmentation errors).
- **1 mechanosensory neuron per bristle**; bristles respond to deflections **<100 nm** (Walker,
  Willingham & Zuker 2000, Science 287:2229–2234).

## Bristle axon synaptic budget
- **~550 output synapses** and **~77 input synapses** per bristle axon (means, automated synapse
  predictions).
- Output share by postsynaptic class: **local 63%, ascending 22%, intersegmental 12%,
  descending <2%, other sensory ~1%.**
- **"most bristles make ZERO synapses onto motor neurons"** ⇒ **no monosynaptic bristle→MN reflex.**
- Postsynaptic partner counts: local **296**, ascending **94**, intersegmental **74**,
  descending **21**.

## The somatotopic map (the sim-relevant geometry)
Derived by intersecting a bristle GAL4 line (R38B08-LexA) with developmental patterning genes:
| Axis | Leg marker | VNC projection |
|---|---|---|
| Proximo-distal | *dac* → proximal; *rn*, *ap* → distal | **concentric rings**: distal bristles at the CENTRE of the leg neuropil, proximal at the OUTER edge |
| Antero-posterior | *hh* → posterior | **binary compartment**: posterior leg → posterior VNC; anterior → anterior (axon arches accordingly on entry) |
| Dorso-ventral | *mid* → ventral | graded |

Mapping rules used to place each of the 409 FANC axons on the leg: A/P from the direction the axon
arches on entering the VNC; P/D from mean synaptic distance to a centre reference point.
The predicted distribution reproduces the known non-uniform anatomical bristle density along the leg.

## Downstream: hemilineage 23B
- **59 23B cells** (56 strictly local to the front leg neuropil), cholinergic/excitatory.
- 23B receives on average **25% of each bristle axon's output** — the single strongest target.
- 23B neurons draw **40% of total input from sensory axons, 85% of that from bristles**.
- **13 subtypes** by axonal projection target (contralateral T1, contralateral T2, ipsilateral wing,
  etc.). Only **17%** of a 23B cell's output synapses are on its axonal projection.
- 23B receptive fields **imbricate** the leg map — overlapping fields of different shapes and sizes;
  some cells get input exclusively from proximal or exclusively from distal bristles.
- Second-strongest bristle target: **inhibitory hemilineage 1B**.

## Behaviour
- Optogenetic activation of **proximal-sensing 23B (SS04746)** → grooming targeting the
  **proximal/mid femur**; **distal-sensing 23B (R21B10)** → grooming targeting the
  **tibia and tarsus / tibia–tarsus joint**.
- N: SS04746 11 flies / 98 trials; R21B10 8 flies / 73 trials; empty-splitGAL4 control 10 flies /
  80 trials. SPARC sparse labelling n=21 (SS04746) and n=17 (R21B10) VNCs.
- Stimulus: 638 nm laser, 1200 Hz pulse rate, 30% duty cycle, aimed at the thorax–coxa joint of the
  left front leg.
- The bristle→23B structure is preserved in **MANC** (male nerve cord) as well as FANC.

## No firing rates in this paper. No hair plate or campaniform counts.
