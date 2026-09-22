# Custodio et al. 2026 — Role of leg campaniform sensilla feedback in Drosophila adaptive walking

**Citation.** Custodio RD, Gorostiza EA, Pierzchlinska A, Haustein M, Godesberg V, Duebbert M,
Bockemuehl T, Bueschges A (2026). "Role of leg campaniform sensilla sensory feedback in *Drosophila
melanogaster* adaptive walking." bioRxiv, posted **2026-07-27**, DOI **10.64898/2026.07.22.740025**.
Corresponding author Ansgar Büschges, University of Cologne. Preprint, version 1, licence cc_no.
**Not peer reviewed.**

**Verification status: metadata and abstract VERIFIED** via the bioRxiv API
(`https://api.biorxiv.org/details/biorxiv/10.64898/2026.07.22.740025`).
**Full text NOT read** — biorxiv.org returned HTTP 429 / Cloudflare error 1015 on every attempt, and
the JATS source XML was not served. **No numbers from the body of this paper are verified.**
Retry later at `https://www.biorxiv.org/content/10.64898/2026.07.22.740025v1.full`.

## Why it matters

This is, as far as I can find, **the first Drosophila leg campaniform sensilla physiology paper**.
Everything else on CS in this fly (Dinges 2021, the FE models) is morphology or simulation. It also
reports a genetic tool that did not previously exist.

Verbatim from the abstract:

> "With the newly uncovered access to **a genetic line labeling all campaniform sensilla in
> *Drosophila melanogaster*** and the many insights gathered from larger insects, we analyzed the
> distribution and patterning of this class of proprioceptors throughout the fly nervous system and
> studied CS function in motor control.
>
> We demonstrate via **two-photon calcium imaging** microscopy that **campaniform sensilla activation
> induces activity in many leg muscles**, showing that these proprioceptive stimuli can influence
> motor neuron activity. We then dissected how the lack of these proprioceptive stimuli influence
> walking behavior, leg kinematics, and interleg coordination in freely-walking flies using
> **transient optogenetic inhibition** and video tracking with high spatiotemporal resolution.
> We show that **CS inhibition robustly affects *Drosophila melanogaster*'s ability to reach their
> typical walking speeds**. Detailed analysis of leg kinematic suggests that **shorter stance
> amplitudes characterized by their long-lasting duration** were behind the speed deficits.
> Dissecting this phenotype also revealed **the inability to maintain coordinated interleg stepping
> patterns as well as postural control** in absence of proprioceptive force and load feedback."

## What to extract when the full text becomes reachable

1. The name/genotype of the pan-CS driver line — this is the tool that makes CS work tractable.
2. Any quantitative CS response data (thresholds, force–response relation, adaptation).
3. Effect sizes: walking speed reduction (mm/s or %), stance amplitude (mm or degrees), stance
   duration (ms), interleg phase coordination metrics.
4. Which CS groups the line labels, and whether it distinguishes proximal (trochanteral/femoral) from
   distal (tibial/tarsal) fields — the FE modelling work predicts these have different stimuli.
5. Whether they map CS onto the connectome (MANC `subclass = "campaniform sensilla"`, `SNpp53` = TrCS).

## Reading of the result, given what else is known

The phenotype — shorter, longer stance and loss of interleg coordination — is the classic
**load-feedback** signature from stick insect and cockroach work **[other insect]**: CS discharge
during stance signals load, and its decay gates the stance→swing transition. That this reproduces in
*Drosophila* with a pan-CS silencing is the first direct evidence the same rule holds here.
