# Pugliese et al. — connectome simulations find a walking CPG (and say embodiment is what's missing)

**VERIFIED**: extracted first-hand from the open PMC full text (PMC13142387), 2026-09-21.
Quotes verbatim.

> Pugliese SM, Chou GM, Abe ETT, Turcu D, Lancaster JK, **Tuthill JC**†, **Brunton BW**†.
> "**Connectome simulations identify a central pattern generator circuit for fly walking.**"
> **bioRxiv preprint**, DOI `10.1101/2025.09.12.675944`, **version 2 dated 2026-04-30**.
> PMID 42094485 / PMC13142387. UW Seattle + Allen Institute.
> **Status: preprint, not peer reviewed** (PMC banner says so explicitly).

This is the closest published relative of a MaleCNS-motor-neuron-driven project, and it is the
best single citation for *why* embodiment matters.

## The model

- Built on **four published adult fly connectome datasets that include the VNC**; primary analysis
  on **MANC**, replicated in **Male CNS (mCNS)** via neuPrint's shared data infrastructure.
- **Front-leg subnetwork in MANC: 4,604 neurons** =
  **1,318 descending neurons + 144 leg motor neurons + 3,142 premotor neurons**
  (premotor defined as all non-DN neurons synapsing onto leg MNs), with
  **3,817,772 synapses**. That is **57% of all cells in the front leg neuropils** and
  **20% of cells in the entire connectome dataset**.
- **Firing-rate model, not spiking.** Rectified tanh activation. Four biophysical parameters per
  neuron, drawn **randomly at every simulation replicate** from fixed distributions; gain `a` and
  threshold `θ` scaled by cell size.
- **Sign rule (directly reusable):** weight `w_ij` **positive if presynaptic neuron j is predicted
  cholinergic**, **negative if predicted GABAergic or glutamatergic** (neuPrint `predictedNt`
  property). **Synapse-count floor of 5.**
- DN activation screen: each excitatory DN driven with tonic input; readout = **rhythmicity of leg
  motor neuron rates**, scored over **128 replicates** per DN.

## Results

- Synthetic pruning isolates "a minimal rhythm-generating circuit consisting of **one inhibitory
  and two excitatory interneurons**; this three-neuron circuit was **necessary and sufficient for
  motor rhythms across all six legs and in four connectome datasets**."
- Top-scoring DN types: **DNb08** and **DNg100**. DNb08's prediction was
  "confirmed experimentally using **optogenetics in behaving flies**."

## The negative result this project should read carefully

> "…did not produce the **tripod interleg coordination** pattern characteristic of hexapod walking.
> Several VNC neurons connect the left and right CPG circuits disynaptically, but their inclusion
> was **insufficient to couple the phase of the left and right legs**. This suggests that
> **proprioceptive feedback, biomechanical coupling, or other neural pathways** may be necessary to
> organize interleg coordination."

and

> "These results suggest that descending drive from DNg100 alone is sufficient to generate
> **within-leg** motor coordination but **not realistic interleg coordination**."

and, on next steps:

> "One promising path forward is to **couple VNC connectome** [simulations to a biomechanical body]"
> … "reinforcement learning may also help fine-tune connectome simulations to achieve more complex
> motor patterns and behavioral sequences **embodied in a biomechanical fly body model**…
> However, **training artificial neural network components to fit parameters in connectome-body
> interfaces carries risks for biological interpretability**."

→ i.e. Tuthill & Brunton's own conclusion is that the missing ingredient is exactly a body with
proprioceptive feedback, and their explicit caveat is against learning the connectome↔body
interface with an ANN. Worth quoting in the brief on both counts.

## Other refs surfaced from its bibliography (cite-worthy, Crossref-unverified)

- Zill S, Schmitz J, Büschges A. "Load sensing and control of posture and locomotion."
  *Arthropod Structure & Development* **33**, 273–286 (2004). ← campaniform sensilla / load.
- Syed DS, Ravbar P, Simpson JH. "Inhibitory circuits control leg movements during *Drosophila*
  grooming." *eLife* **14**, RP106446 (Jan 2026).
