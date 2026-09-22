# Lesser E, Azevedo AW, Phelps JS, Elabbady L, Cook A, Syed DS, Mark B, Kuroda S, Sustar A, Moussa A, Dallmann CJ, Agrawal S, Lee S-YJ, Pratt BG, Skutt-Kakaria K, Gerhard S, Lu R, Kemnitz N, Lee K, Halageri A, Castro M, Ih D, Gager J, Tammam M, Dorkenwald S, Collman FC, Schneider-Mizell CM, Brittain D, Jordan CS, Macrina T, Dickinson MH, Lee W-CA, Tuthill JC (2024)
**"Synaptic architecture of leg and wing premotor control networks in Drosophila."**
*Nature* **631**(8020):369-377. doi:10.1038/s41586-024-07600-z.
Companion: **Azevedo et al. 2024, Nature 631(8020):360-368** (the connectome + MN atlas).
Code: github.com/tuthill-lab/Lesser_Azevedo_2023.

Nature version paywalled. Numbers below read from the **open bioRxiv preprint**,
https://www.biorxiv.org/content/10.1101/2023.05.30.542725v1.full ("Synaptic architecture of leg and
wing premotor control networks in Drosophila", bioRxiv 2023.05.30.542725). Preprint-vs-published
numbers may differ slightly; flagged where the preprint contradicts itself.

## The leg premotor connectome (verified, preprint Results)
- **69 leg MNs** (left front leg) receiving **220,747 synapses** from **1,411 premotor neurons**.
  Wing side for contrast: **30 wing/thorax MNs**, 151,030 synapses, 1,787 preMNs.
- **On average each MN receives 3,883 input synapses from 256 preMNs; each preMN synapses onto 5 MNs**
  (3-synapse threshold).
- *"Eighteen distinct muscles actuate the leg joints, each innervated by between 1 and 10 MNs. The
  fly's front leg is innervated by a total of up to 70 MNs."*
- Leg has 5 segments, 5 joints, **7 mechanical degrees of freedom** (3 at the most proximal joint,
  1 at each other joint), citing Lobato-Rios 2022.

## MN size -> synaptic input (the scaling law we can exploit)
- Leg MN **input synapse count scales linearly with MN surface area**:
  text says **r = 0.94, p<1e-33, slope 0.45 synapses/µm²**; the Figure 1G legend in the same
  preprint says **r = 0.95, p<1e-34, slope 0.34 synapses/µm²**. **The preprint is internally
  inconsistent - check the published Nature version before using the slope.**
  Either way: *"approximately 3X more synapses per unit area than reported for vertebrate MNs"*
  (their comparison: Örnung et al. 1998).
- Wing power MNs slope 0.24 syn/µm² (r=0.98); tension MNs 0.49 (r=0.84); steering MNs 0.21 (r=0.83,
  excluding the enormous b1 MN).
- Leg and wing MN size varies substantially **even among MNs controlling the same joint**.
- Insect MN somata mostly **do not receive synaptic input**, unlike vertebrates - size here means
  dendrite+axon surface, not soma.

## Proportional connectivity - the recruitment result
Published abstract, verbatim: *"Within most leg motor modules, the synaptic weights of each premotor
neuron are proportional to the size of their target MNs, establishing a circuit basis for
hierarchical MN recruitment. By contrast, wing premotor networks lack proportional synaptic
connectivity."*
Preprint detail: *"each preMN provides the same output weight onto all the MNs within the extensor
and flexor modules. Specifically, the preMN output weights onto each MN are proportional to the
overall synaptic input to each MN. This is true regardless of total preMN synapses, which can range
over 100-fold."* PCA: the **first principal component explains >80%** of module connectivity variance.
This holds for **both excitatory and inhibitory** local leg preMNs.

## Motor modules relevant to the femur-tibia joint
- **Tibia Extend module** = SETi + FETi (the 2 tibia extensor MNs). Every example preMN makes more
  synapses onto FETi than onto SETi, in proportion to size.
- **"Tibia Flex A" module** = **4 accessory tibia flexor MNs + the 5 main tibia flexor MNs + 1
  synergist tarsus MN** (10 MNs). Fraction of preMN output onto the largest MN (the fast flexor) is
  significantly greater than onto the smaller ones (Kruskal-Wallis p<1e-4; pairwise p<1e-28).
- Their Figure 4B replots Azevedo et al. 2020's force-at-the-tibia-tip for two of these motor units.

## What this licenses in a model (my reading, not their claim)
A single scalar premotor drive **d(t)**, delivered to every MN in a flexor module with weight
**w_i ∝ (MN surface area)_i**, combined with an excitability threshold that falls with MN size
(Azevedo 2020: Rin 700 / 300 / 150 MΩ for slow / intermediate / fast) and a force-per-spike that
rises with MN size (0.013 / ~1 / ~10 µN), reproduces the observed recruitment order **and** its
force range without any extra machinery. That is a connectome-supported architecture for the leg
specifically - the wing would need something else.
Missing piece: to extend force-per-spike to all 15 flexor MNs you need the per-MN volumes/surface
areas, which are plotted in their Extended Data Figure 1B/D but not tabulated in the text.
They come from the FANC data release (Supplemental Table 1 links MNs grouped by module).

## Other context numbers from the same preprint
- *Drosophila* beat their wings at **~220 Hz**; power muscles are asynchronous/stretch-activated,
  12 steering muscles attach to 4 sclerites. (Not leg, but useful scale context: leg MNs are
  synchronous, wing power muscles are not.)
