# Dallmann et al. 2025 — Selective presynaptic inhibition of leg proprioception in behaving Drosophila

**Citation.** Dallmann CJ, Luo Y, Agrawal S, Mamiya A, Chou GM, Cook A, Sustar A, Brunton BW,
Tuthill JC (2025). "Selective presynaptic inhibition of leg proprioception in behaving *Drosophila*."
*Nature* **647:445–453** (published 2025-09-17). DOI **10.1038/s41586-025-09554-2**. PMC13070307.
**VERIFIED** by reading the PMC author-manuscript full text. Volume/pages from OpenAlex metadata
(second-hand); everything else below is from the text itself.

Method: two-photon calcium imaging (GCaMP6f/7f) of FeCO **axon terminals** in the VNC of tethered
flies walking and grooming on an air-supported ball, with 3D leg tracking; plus connectomic analysis
of FeCO axons in **FANC** (female adult nerve cord EM volume); plus snRNA-seq receptor expression.

## Why this paper matters for a body-model-driven encoder

**It breaks the assumption that proprioceptor output is a function of joint kinematics.**
The movement-encoding **hook** axons are suppressed during **self-generated** leg movements
(walking, grooming) but not during **passive** movements. The same joint trajectory produces
different afferent output depending on whether the fly caused it.

Direct quote: *"the movement-encoding hook axons, but not the position-encoding claw axons, are
suppressed during walking and grooming."*

So if your sim computes hook activity from dθ/dt alone, it will be **systematically wrong during
locomotion — the very regime you care about.** You need a behavioural-state gate on the hook channel.

## What is and is not gated (VERIFIED)

| Subtype | Suppressed during active movement? |
|---|---|
| **hook** (movement/direction) | **YES** — strongly suppressed during walking and grooming |
| **claw** (position) | **NO** — "faithfully signaled joint position across behavioral contexts" |
| **club** (vibration) | **NO** — not suppressed; *baseline* activity was **elevated when the legs contacted the treadmill**, consistent with an exteroceptive substrate-vibration role |

That last point is a useful independent confirmation that **club should be driven by ground contact,
not by joint velocity.**

## Circuit (VERIFIED, with numbers)

Connectomic analysis of claw and hook axons from the left front leg in FANC:

- Input synapses are present on **all axon branches, spatially intermingled with output synapses** —
  i.e. axo-axonic input throughout the arbor, not at a single gating site.
- Presynaptic partners of claw and hook axons are **primarily GABAergic**. snRNA-seq: **all claw and
  hook neurons strongly express `Rdl`** (the GABA_A receptor gene). `Lcch3` also appears (noted as
  forming inhibitory channels).
- Input source: **claw 100 %, hook 95 % from VNC interneurons**, essentially none from descending
  neurons directly.
- **Hook axons receive more presynaptic input than claw axons** on average.
- **"presynaptic neurons target either claw axons or hook axons, but not both"** — which is the
  structural reason the suppression can be selective.
- **83 %** of GABAergic input onto hook axons comes from local **9A hemilineage** interneurons.
- **One "chief" 9A neuron alone provides 57 % of presynaptic input to hook axons**, and **63 % of
  that neuron's own output goes to hook axons.** (Elsewhere quoted as 58 % of output synapses onto
  hook axons, with only 13 % onto other sensory axons — the two figures refer to slightly different
  populations of chief 9A neurons.) It takes dendritic input in the **dorsal** VNC and outputs to
  hook axons in the **ventral** VNC.
- Claw axons' GABAergic input comes mostly from **19A** neurons instead, which themselves receive
  proprioceptive input. Function unknown; the authors speculate lateral inhibition to sharpen
  receptive fields, protection from habituation, or **reduction of hysteresis**.

## Where the gating signal comes from (VERIFIED)

- The GABAergic 9A neurons are **active during self-generated but not passive leg movements**, and
  **receive little direct sensory input** — so they are not a feedback loop, they are a
  **feedforward corollary-discharge-like gate**.
- Chief 9A receives most of its input from **descending neurons**. Walking and grooming descending
  neurons together provide **31 % of synaptic input to chief 9A** (**18 %** walking, **13 %**
  grooming; the grooming one is named **DNg12**).
- The strongest *inhibitory* descending input is the GABAergic **DNg74 ("web")**, which in the VNC
  targets primarily interneurons (**80 %** of its output synapses), including chief 9A (**2 %**).
  DNg74 itself receives input from brain-central neurons (**59 neurons, 48 %** of input synapses),
  ascending neurons (**74 neurons, 27 %**) and descending neurons (**37 neurons, 25 %**); **61 %** of
  the brain input comes from the **gnathal ganglia**. DNg74 appears to **disinhibit** its VNC targets
  during self-generated leg movement.
- They built a **connectome-constrained computational model** simulating recruitment of chief 9A in
  left front/middle/hind neuromeres by activating descending neurons at **50 Hz, 150 Hz, 150 Hz**.

Presynaptic hemilineages listed as inputs to claw/hook axons (Fig 4a grouping):
**13B, 19A, 3A, 9A, 13B, 19A, 8A, 1A, 8B, 18B, 22A**, plus hook axons themselves, a **hair plate
axon**, and unknown.

## Mechanism
Canonical presynaptic inhibition: GABA opens chloride channels on the sensory axon via GABA_A
receptors, shunting the terminal.

## What I could not verify
- The **magnitude** of hook suppression (percent or fold) and its **latency in ms** relative to
  movement onset — these are figure quantities in Figs 2–3 and I did not extract numeric values.
- Neuron counts for the 9A population (how many chief 9A neurons per neuromere).
- FANC body IDs / MANC systematic types for the chief 9A neuron.
