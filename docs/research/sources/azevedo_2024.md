# Azevedo A, Lesser E, Phelps JS, Mark B, Elabbady L, Kuroda S, Sustar A, Moussa A, Khandelwal A, Dallmann CJ, et al. (2024)
**"Connectomic reconstruction of a female Drosophila ventral nerve cord."**
*Nature* **631**(8020):360-368 (2024). doi:10.1038/s41586-024-07389-x. PMID 38926570.
Dataset = **FANC** (Female Adult Nerve Cord). Code: github.com/tuthill-lab/Azevedo_Lesser_Phelps_Mark_2024.

Companion paper (confirm which is which - the brief asked):
**Lesser E, Azevedo AW, Phelps JS, Elabbady L, Cook A, Syed DS, Mark B, Kuroda S, Sustar A,
Moussa A, et al. (2024) "Synaptic architecture of leg and wing premotor control networks in
Drosophila." *Nature* **631**(8020):369-377.** doi:10.1038/s41586-024-07600-z.
So: **Azevedo = the connectome + motor neuron atlas, 360-368. Lesser = the premotor networks, 369-377.**
Confirmed against the Özdil et al. 2025 reference list and Nature's own article pages.

Nature full text is paywalled; abstract read directly. The motor-neuron-per-muscle counts below come
from the **freely available Supplementary Methods / Motor Neuron ID Appendix** (46 pp, 20 MB),
https://faculty.washington.edu/tuthill/docs/azevedo24_appendix.pdf - read in full with pdftotext.

## Headline numbers (verified)
- VNC: **~45 million synapses, 14,600 neuronal cell bodies** (abstract, verbatim:
  "the fly VNC contains roughly 45 million synapses and 14,600 neuronal cell bodies").
  Extended Data: 17,076 putative nuclei -> 14,621 neurons (85.6%), 2,030 glia, 410 false positives.
- **Front (T1) leg motor neurons: 69 in left T1, 70 in right T1** (appendix, verbatim:
  "The FANC dataset establishes the number of MNs in the T1 neuropils: 69 T1L, 70 in right T1.")
  This **supersedes the "53 MNs per leg" figure** quoted in Azevedo et al. 2020 (which came from
  Baek & Mann 2009 / Brierley 2012 lineage work).
- Nerve split of the 69 left-T1 MNs: **ProAN 12, DProN 4, ProLN 42, VProN 11**.

## Motor units per muscle, front (T1) leg - Table A4 of the appendix (VERIFIED, transcribed)
| muscle (their updated name) | action | FANC MNs | axons in X-ray (XNH) |
|---|---|---|---|
| tergopleural promotor + pleural promotor | promote coxa | **4** | 1-4, DProN |
| pleural remotor & abductor | remote + abduct coxa | **2** | 2, ProAN |
| sternal anterior rotator | anterior coxa movement | **2** | 2, VProN |
| sternal posterior rotator | posterior coxa movement | **4** | 4, ProAN |
| sternal adductor | adduct coxa | **1** | 1, ProAN |
| tergotrochanter extensor | extend Co-Tr | **4** | 4, VProN |
| sternotrochanter extensor | extend Co-Tr | **2** | 2, VProN |
| trochanter extensor | extend Co-Tr | **2** | 2, ProLN |
| trochanter flexor | flex Co-Tr | **8** | 8 (5 ProAN, 3 VProN) |
| accessory trochanter flexor | flex Co-Tr | **3** | ? |
| femur reductor | unknown | **6** (2 very small) | 6, ProLN |
| **tibia extensor** | extend F-Ti | **2** (= FETi + SETi) | 2, ProLN |
| **tibia flexor** | flex F-Ti | **5** | 4 (possibly a 5th with the fast flexor), ProLN |
| **accessory tibia flexor** | flex F-Ti | **10** (5 anterior, 5 posterior) | 10, ProLN |
| long tendon muscle 2 (femur) | pull long tendon | **4** | 4 |
| long tendon muscle 1 (tibia) | pull long tendon | **4** | 4 |
| tarsus depressor | extend Ti-Ta | **6** | uncertain (volume cut off) |
| tarsus retro depressor | - | (not counted) | uncertain |
| tarsus levator | flex Ti-Ta | (not counted) | ProLN |

**Femur-tibia joint totals: 2 extensor MNs vs 15 flexor MNs (5 tibia flexor + 10 accessory tibia
flexor).** That 15 matches Azevedo et al. 2020's "approximately 15 motor neurons" for tibia flexion.

## Mapping Azevedo 2020's three cells onto FANC IDs (from appendix figure legends)
- Tibia flexor muscle = **MNs 41-45**. *"The largest MN by volume in left T1 is the Fast tibia
  flexor (MN #45, Azevedo et al. 2020)."* Force production was measured for **#41, #44 and #45**.
- Accessory tibia flexor muscle = **MNs 46-55**. The R35C09-GAL4 "slow" cell of Azevedo 2020 is one
  of the posterior group (MNs 46-49); MNs 50-55 run in a separate, more anterior tract.
  *"Baek and Mann reported 9 acc. tibia flexor neurons ... We found 10 neurons ... that resembles the
  morphology of the slow tibia flexor in Azevedo et al. 2020."*
- Tibia extensor = **MNs 39 & 40 = SETi and FETi**. *"The SETi innervates the distal fibers of the
  muscle with are more pinnate. ... The distal fibers are more pinnate, suggesting less mechanical
  advantage, perhaps a mechanism underlying the smaller forces produced by spikes in the SETi."*
  (i.e. the fly has the same FETi/SETi pair as locust/stick insect, and the size-principle gradient
  at the extensor is partly a **moment-arm / pennation** effect, not only a neuron-size effect.)

## Nomenclature they fixed (matters when reading older papers)
They rename Soler et al. 2004's **"tibia reductor" (tirm)** to **accessory tibia flexor** -
they argue Soler misidentified it. They rename **"tibia levator" (tilm)** to **tibia extensor**
and **"tibia depressor" (tidm)** to **tibia flexor**. Azevedo 2020's "slow MN innervating the
reductor" is therefore an **accessory tibia flexor** MN.

## Lesser et al. 2024 - the one number that matters for a recruitment model
Abstract, verbatim: *"Within most leg motor modules, the synaptic weights of each premotor neuron
are proportional to the size of their target MNs, establishing a circuit basis for hierarchical MN
recruitment. By contrast, wing premotor networks lack proportional synaptic connectivity."*
i.e. the connectome confirms Henneman-style recruitment is **wired in** at the leg, and a shared
premotor drive scaled by MN size is a defensible modelling assumption for the leg (not the wing).
Full text paywalled - I could not verify any per-neuron synapse counts.

## Also worth knowing
- Özdil et al. 2025, citing Azevedo 2024 + Lesser 2024 + Soler 2004, state the leg has
  **"at least seven DoFs across five joints ... approximately 19 muscles ... approximately 69 motor
  neurons."** Second-hand but consistent with the appendix.
- X-ray (XNH) leg volume with muscle-fibre annotations is public:
  https://www.lee.hms.harvard.edu/resources
