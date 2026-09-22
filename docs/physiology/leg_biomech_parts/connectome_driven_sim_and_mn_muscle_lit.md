# Lit scan: connectome-driven body sim, MN→muscle mapping, proprioception, insect Hill muscle

Compiled 2026-09-21. Every entry labelled **VERIFIED** (I fetched the paper/repo/API record
myself) or **SECOND-HAND** (only seen in search snippets / another page's description).
Crossref API used for all DOI/volume/page checks unless noted.

---

## A. Connectome-driven / motor-neuron-driven body simulation

### A0. Baseline body models (for reference)

- **VERIFIED** Lobato-Rios V, Ramalingasetty ST, Özdil PG, Arreguit J, Ijspeert AJ, Ramdya P.
  "NeuroMechFly, a neuromechanical model of adult *Drosophila melanogaster*."
  *Nature Methods* **19**, 620–627 (2022). DOI `10.1038/s41592-022-01466-7`.
  (Preprint: bioRxiv `10.1101/2021.04.17.440214`.)
- **VERIFIED** Wang-Chen S, Stimpfling VA, Lam TKC, Özdil PG, et al. (7 authors)
  "NeuroMechFly v2: simulating embodied sensorimotor control in adult *Drosophila*."
  *Nature Methods* **21**, 2353–2362 (2024). DOI `10.1038/s41592-024-02497-y`.
  Preprint bioRxiv `10.1101/2023.09.18.556649`.
  Repo: https://github.com/NeLy-EPFL/flygym
- **VERIFIED (repo README)** FlyGym **2.x** API landed **March 2026** — complete rewrite,
  *not backward compatible*. Claims ~10x CPU speed-up (~2x real-time) and ~300x GPU speed-up
  via **Warp / MJWarp** (~60x real-time). FlyGym 1.x was moved to
  https://github.com/NeLy-EPFL/flygym-gymnasium .
- **VERIFIED, OPERATIONAL WARNING** `https://neuromechfly.org/` is, as of 2026-09-21,
  serving a **GoDaddy parking lander** (every path returns a 114-byte JS stub redirecting to
  `/lander`; `window._trfd.push({ap:"parking"})`). `gymnasium.neuromechfly.org` does not
  resolve/connect at all (curl exit, 000). So the official docs site is **down right now**.
  Use the repo `docs/` + tagged `doc/source/` trees instead (URLs below).

### A1. The connectome-constrained vision demo in flygym — exact location

- **VERIFIED** The demo is the **`advanced_vision`** tutorial, titled
  **"Connectome-constrained visual system model"**, authors **Thomas Ka Chung Lam,
  Sibo Wang-Chen**. Verified by fetching the raw doc source at
  `https://raw.githubusercontent.com/NeLy-EPFL/flygym/v1.1.0/doc/source/tutorials/advanced_vision.rst`.
  Verbatim summary line: *"In this tutorial, we will (1) simulate two flies in the same arena,
  and (2) integrate a connectome-constrained visual system model (Lappalainen et al., 2024)
  into NeuroMechFly."*
  - Notebook: `notebooks/advanced_vision.ipynb` at tag `v1.1.0`
    (https://github.com/NeLy-EPFL/flygym/blob/v1.1.0/notebooks/advanced_vision.ipynb)
  - Fuller implementation: `flygym/examples/vision/` (doc page
    `doc/source/api_ref/examples/vision.rst`); gallery entry
    `doc/source/gallery/video_14_fly_follow_fly.rst` ("fly following") and
    `video_9_visual_taxis.rst`.
  - Canonical (now-dead) doc URL was `https://neuromechfly.org/tutorials/advanced_vision.html`.
  - **VERIFIED** the v1.1.0 tutorial toctree order: gym_basics_and_kinematic_replay, cpg_controller,
    rule_based_controller, hybrid_controller, turning, vision_basics, olfaction_basics,
    path_integration, head_stabilization, **advanced_vision**, advanced_olfaction.
  - **VERIFIED** In FlyGym **2.x** (`main`) the tutorial set is much smaller —
    `tutorials/1a,1b,2,3,4a_cpg,4b_rule_based,4c_hybrid,4d_turning,5a,5b_using_flybody_model.ipynb`
    plus `docs/tutorials/6_muscle_imitation.md`, `7_performance_profiling.md`.
    **There is no vision/connectome tutorial in flygym 2.x main.** It lives only in 1.x /
    flygym-gymnasium.
- **VERIFIED** Lappalainen JK, Tschopp FD, Prakhya S, McGill M, et al. (10 authors)
  "Connectome-constrained networks predict neural activity across the fly visual system."
  *Nature* **634**, 1132–1140 (2024). DOI `10.1038/s41586-024-07939-3` — **the DOI in the brief
  is correct**. Preprint bioRxiv `10.1101/2023.03.11.532232`.
  Code: https://github.com/TuragaLab/flyvis (**SECOND-HAND**: search result describes it as
  "a connectome-constrained deep mechanistic network (DMN) model of the fruit fly visual system
  in PyTorch"; I have not yet fetched the README).
- **SECOND-HAND** (search snippet, from NMF-v2 material): the flygym coupling uses the following
  fly's visual input, takes activity of **T1–T5, all Tm and all TmY** neurons to do object
  detection, and **modulates the descending turning signal** into the hybrid controller.
  i.e. the connectome network does *not* drive motor neurons — it drives a 2-D descending drive.
  → Important for your brief: the existing flygym connectome demo is **sensory-side only**.

### A2. Connectome → motor-neuron → body work (2025–2026)

**Headline: nobody has published a peer-reviewed connectome-MN→muscle→body loop. The closest
peer-reviewed work stops one step short in each direction.**

#### A2.1 The strongest citation — a MANC/mCNS motor simulation that explicitly names embodiment as the missing piece

**VERIFIED (PMC full text read first-hand)** Pugliese SM, Chou GM, Abe ETT, Turcu D, Lancaster JK,
Tuthill JC, Brunton BW. "**Connectome simulations identify a central pattern generator circuit for
fly walking.**" bioRxiv `10.1101/2025.09.12.675944`, **v2 2026-04-30**. PMID 42094485, PMC13142387.
**Preprint, not peer reviewed.**

- **MANC front-leg subnetwork: 4,604 neurons = 1,318 DNs + 144 leg MNs + 3,142 premotor**,
  **3,817,772 synapses**; 57% of front-leg-neuropil cells, 20% of the whole dataset. Replicated on
  **Male CNS (mCNS)** through neuPrint.
- **Firing-rate model** (rectified tanh), not spiking. Sign rule: `+` if presynaptic neuron
  predicted **cholinergic**, `−` if **GABAergic or glutamatergic** (`predictedNt`),
  **5-synapse floor**.
- Finds a **three-neuron CPG** (1 inhibitory + 2 excitatory interneurons), necessary and sufficient
  for rhythm across all six legs in four connectome datasets; predicts **DNb08**, confirmed
  optogenetically.
- **The negative result:** no tripod interleg coordination emerges; they conclude
  *"proprioceptive feedback, biomechanical coupling, or other neural pathways may be necessary"*,
  and name *"couple VNC connectome [simulations to a body]"* as the path forward — with the caveat
  that *"training artificial neural network components to fit parameters in connectome-body
  interfaces carries risks for biological interpretability."*
- Full notes + verbatim quotes: `docs/research/sources/pugliese_2026_connectome_cpg.md`.

#### A2.2 arXiv:2602.17997 — the ID in the brief is REAL

**VERIFIED (arXiv abs + HTML)** Jin Z, Zhu Y, Zhang C, Sui Y. "**Whole-Brain Connectomic Graph
Model Enables Whole-Body Locomotion Control in Fruit Fly.**" **arXiv:2602.17997**, submitted
2026-02-20, v3 2026-06-14. Model name **FlyGM**. (The brief guessed Jin/Zhu/Zhang/Sui — correct.)

- Body: **flybody** (MuJoCo). Connectome: **FlyWire FAFB v783**, instantiated as a
  graph-structured neural controller and trained by deep RL.
- Verbatim: walking — *"Actions remain 59-dimensional, actuating adhesion, head/abdomen motion,
  and all leg joints"*; flight — *"12 control signals: instantaneous wing torques, head/abdomen
  angles, and Wing-Pattern Generator (WPG) frequency modulation."*
- Tasks: gait initiation, straight walk 3 cm/s, turn (3 cm/s + 10 rad/s yaw), flight 20 cm/s.
  Claim: better sample efficiency than graph and non-graph baselines.
- Project page https://lnsgroup.cc/research/FlyGM ; videos https://sites.google.com/view/flygm
- **Caveat:** connectome-as-architecture, weights learned by RL. Output is **joint/actuator
  commands**, not per-muscle drives, and there are no identified motor neurons in the loop.

#### A2.3 Two hobby repos doing almost exactly this project — both days old, neither reviewed

- **VERIFIED (README + GitHub API)** **Fly.exe** — https://github.com/Ibtisam-Mohammad/Fly.exe
  (GPL-2.0-or-later; created 2026-09-12; 19 stars at time of check).
  *"Runs the complete released Drosophila male CNS connectome (165,122 neurons, 25.5M edges)
  inside a physical fly body, in closed loop, on one GPU."*
  - **MaleCNS v1.0**, "Traced" neurons: **165,122 of 166,700 bodies**, and
    *"every one of the 25,563,197 edges between them."*
  - Body: **NeuroMechFly v2 / FlyGym**, **133 generalized coordinates / 132 mechanical DOF**,
    **MuJoCo 3.9**, per-leg adhesion switching.
  - **Coupling interval 15 ms; 150 neural steps per interval; 0.015× biological real time.**
    ← the closest published analogue to this project's 10 ms frame.
  - **Does NOT do MN→muscle:** uses *"a published pattern generator"* for gait; motor commands come
    from *"two descending population rates read out of their own network."*
- **VERIFIED (README + GitHub API)** **flybody-connectome** —
  https://github.com/jamesbiederbeck/flybody-connectome (MIT; created **2026-09-19**; 0 stars).
  *"A Drosophila body in MuJoCo driven by the MaleCNS v1.0 connectome."*
  - Loop: FlyGym eye cameras → **721 ommatidia/eye** → registered onto connectome columns →
    NativeBrain (**166,700 neurons, 25,582,938 edges**) → **DNp20 right-minus-left + DNpe017 rate**
    → wingbeat frequency + steering → wing actuators on top of a wingbeat pattern generator.
    Brain ~30 Hz, WPG + physics 10 kHz, `Brain.dt` 0.1 ms.
  - **The measured negative result, which this project should replicate before trusting its own
    MN rates** (author's own table, after 2 s of retinal drive):
    R1–R6 photoreceptors 3,335/3,335 spiking; lamina 5,299/7,114; DNp20 2/2; DNpe017 2/2;
    DNa02/DNp09/MDN 0/8; **all VNC motor neurons 0 of 708**; wing muscle MNs (`subclass=wm`)
    0 of 67; DLM power MNs 0/10; b1/b2/hg1 steering MNs 0/6.
    > *"Vision reaches the descending neurons and stops there. Not one of the 708 VNC motor neurons
    > fires from retinal input."*
    Motor neurons only fire when haltere afferents are current-injected (~8 → 340 of 708 VNC MNs
    active), and that response is **non-monotonic** in injected current.
  - Also documents that the MuJoCo model has **`nsensor == 0`** — no sensors at all — so
    "proprioceptive stimulation" there is an engineered stand-in derived from thorax angular
    velocity, not a measurement.
  - **Treat as an unreviewed one-person project**; useful as a hazard list, not as a result.
- Other repos in this genre (**SECOND-HAND**, titles/descriptions only): `zhengxuyu/nfly`
  (MaleCNS as an RNN playing Gymnasium games), `Ma-Dan/fly-brain` (FlyWire v783, 138,639 neurons,
  in NeuroMechFly v2), `Recluse/FLY-lab`, `IONOFIELD/FLYCNS`, and the curated list
  https://github.com/cobanov/awesome-fly. None peer-reviewed; none verified by me.

#### A2.4 Baseline bodies these all sit on

- **VERIFIED** Vaxenburg R, Siwanowicz I, Merel J, Robie AA, Morrow C, Novati G, Stefanidi Z,
  Both G-J, Card GM, Reiser MB, Botvinick MM, Branson KM, Tassa Y, Turaga SC.
  "**Whole-body physics simulation of fruit fly locomotion.**" *Nature* **643**, 1312–1320 (2025).
  DOI `10.1038/s41586-025-09029-4`. Preprint bioRxiv `10.1101/2024.03.11.584515`.
  Repo https://github.com/TuragaLab/flybody (Apache-2.0, Google DeepMind + HHMI Janelia).
  **VERIFIED from README:** walking action dimension is **59**; tasks include walk imitation,
  flight, vision-guided flight; DMPO agent, Ray-parallel training. **Torque/position actuators,
  no muscles.**

### A5. MIMIC-MJX

- **VERIFIED (arXiv page)** **arXiv:2511.20532** — *"MIMIC-MJX: Neuromechanical Emulation of
  Animal Behavior."* First author **Charles Y. Zhang** + 43 co-authors (Harvard, Salk, MIT, …).
  Submitted 2025-11-25; latest version 2026-08-04. **The ID in the brief is correct.**
  Project page: https://mimic-mjx.talmolab.org . Also on PMC: PMC12676414.
  - Pipeline (**SECOND-HAND**, from search snippets of the HTML/PMC version): input = reference
    pose-tracking data + a **MuJoCo-compatible** body model (kinematic chain, actuators, optional
    sensors e.g. touch); **stac-mjx** does IK to joint angles; **track-mjx** trains a neural
    controller to reproduce them; runs on **MJX** with thousands of parallel envs on one GPU.
  - **Fly content: NOT CONFIRMED.** The abstract I fetched does not name Drosophila. The demo
    highlighted in search results is a **mouse forelimb** reaching task (companion paper
    arXiv:2511.21848, "Massively Parallel Imitation Learning of Mouse Forelimb Musculoskeletal
    Reaching Dynamics", PMID 41356073). Treat "MIMIC-MJX includes a fly" as **unverified**.

### A4. Whole-brain LIF and whether it touches a body

- **VERIFIED** Shiu PK, Sterne GR, Spiller N, Franconville R, … Scott K (28 authors).
  Journal version title is **"A Drosophila computational brain model reveals sensorimotor
  processing"**, *Nature* **634**(8032), 210–219 (2024-10-03). DOI `10.1038/s41586-024-07763-9`.
  The *"A leaky integrate-and-fire computational model based on the connectome of the entire adult
  Drosophila brain reveals insights into sensorimotor processing"* wording is the **bioRxiv
  preprint title** (`10.1101/2023.05.02.539144`, PMID 37205514) — so the brief's title is the
  preprint's, not the Nature paper's.
  Code: https://github.com/philshiu/Drosophila_brain_model (**SECOND-HAND**, not fetched).
  **No body model** — it stops at motor-neuron / behaviour-proxy readout. (in progress: confirm)
- **VERIFIED** Berg S, et al. (111 authors). "Sexual dimorphism in the complete *Drosophila* male
  central nervous system connectome." *Cell* **189**, 5504–5526.e15 (2026-09).
  DOI `10.1016/j.cell.2026.08.015`. ← the MaleCNS reference paper.
- **VERIFIED (arXiv page)** Wang-Chen S, Ramdya P. "The embodied brain: Bridging the brain, body,
  and behavior with biorealistic neuromechanical models." **arXiv:2601.08056**; review, published
  in *Current Opinion in Neurobiology* (2026). Submitted 2026-01-12, final 2026-07-20.
  Useful as the framing citation for the whole brief.

---

## B. Motor neuron → muscle mapping ground truth

### Connectome resources (all VERIFIED via Crossref)

| Ref | Cite | DOI |
|---|---|---|
| Azevedo AW, Dickinson ES, Gurung P, Venkatasubramanian L, Mann RS, Tuthill JC (2020) | "A size principle for recruitment of *Drosophila* leg motor neurons." *eLife* **9**:e56754 (2020-06-03) | `10.7554/eLife.56754` |
| Phelps JS, Hildebrand DGC, Graham BJ, Kuan AT, et al. (15 auth., 2021) | "Reconstruction of motor control circuits in adult *Drosophila* using automated transmission electron microscopy." *Cell* **184**, 759–774.e18 | `10.1016/j.cell.2020.12.013` |
| Azevedo A, Lesser E, Phelps JS, Mark B, et al. (35 auth., 2024) — **FANC** | "Connectomic reconstruction of a female *Drosophila* ventral nerve cord." *Nature* **631**, 360–368 | `10.1038/s41586-024-07389-x` |
| Lesser E, et al. (33 auth., 2024) — **FANC premotor** | "Synaptic architecture of leg and wing premotor control networks in *Drosophila*." *Nature* **631**, 369–377 | `10.1038/s41586-024-07600-z` |
| Takemura S, et al. (84 auth., 2024) — **MANC** | "A Connectome of the Male *Drosophila* Ventral Nerve Cord." *eLife* reviewed preprint | `10.7554/eLife.97769` |
| Marin EC, et al. (2024) — **MANC annotation** | "Systematic annotation of a complete adult male *Drosophila* nerve cord connectome reveals principles of functional organisation." *eLife* | `10.7554/eLife.97766` |
| Cheong HSJ, et al. (16 auth.) — **MANC premotor** | VOR title **"Organization of circuits linking descending input to motor output in the *Drosophila* Male Adult Nerve Cord connectome"**, *eLife* **13** (2026-07-20). The brief's "Transforming descending input into behavior: …" is the **2024 reviewed-preprint title**, same DOI stem. PMID 42474298; PMC13384506 | `10.7554/eLife.96084` |
| Berg S, et al. (111 auth., 2026) — **MaleCNS** | "Sexual dimorphism in the complete *Drosophila* male central nervous system connectome." *Cell* **189**, 5504–5526.e15 | `10.1016/j.cell.2026.08.015` |

### Motor-neuron counts, all VERIFIED first-hand from full text

| dataset | leg MNs | breakdown | source |
|---|---|---|---|
| **FANC** (female) | **371** (T1+T2+T3) | **69 left T1, 70 right T1** (extra right cell = a second tarsus levator MN); also 32 haltere, 24 neck, 58 wing MNs | Azevedo 2024, PMC11348827 |
| **MANC** (male) | **392** | **142 T1, 119 T2, 131 T3**; all 142 T1 assigned via FANC/NBLAST matching, **198 of 252** T2+T3 assigned by serial-homolog matching | Cheong et al., elifesciences.org/articles/96084 |
| **MANC front-leg subnetwork used for CPG sim** | **144** leg MNs | inside a 4,604-neuron network | Pugliese 2026 |
| this project | 373 | — | — |

→ **373 is in the right range and needs no alarm**, but it matches neither FANC's 371 nor MANC's
392 exactly. MaleCNS v1.0 annotation is a third, later revision of the same anatomy. Pin your
grouping to the connectome's own `target` / `subclass` annotation fields rather than to a count.

**MANC annotation schema (VERIFIED, verbatim from Cheong et al.)** — this *is* the grouping key
this project wants:
> "…systematic type … (wing muscle, **wm**; haltere, **hm**; front leg, **fl**; middle leg, **ml**;
> hind leg, **hl**; abdominal, **ad**; unknown, **xm**) and a two-digit number … we annotated
> **'target'** and **'subclass'** fields for each MN, where **target is the exact muscle target
> name if known**, while **subclass is their two-letter abbreviation for broad muscle category**."
> "Each *Drosophila* MN is identified by the single muscle it innervates."

Scale of the muscle set (Cheong et al., citing Azevedo 2024 and Brierley 2012):
> "The musculature of the *Drosophila* leg consists of **13 muscle groups confined within the
> proximal leg segments, and another five in the thorax that insert in the leg** … estimated to be
> innervated by **around 70 MNs in each leg**, that originate from **~15 hemilineages** … the
> muscles of the T1 legs differ in the number of MNs innervating each muscle **by as much as an
> order of magnitude**."
→ **18 muscle groups total (13 intrinsic + 5 thoracic)**, which is close to this project's
12-ish muscle-target list; check which of the 18 you are collapsing.

**Gaps MANC could not resolve** (verbatim): "We could not identify serially repeating homologs (in
T2 and T3) for the **Tarsus levators and depressor MNs** as well as the **Tergopleural/Pleural
promotor MNs**." → those two of this project's channels are the least reliable in T2/T3.

Method used to build the atlas: EM (FANC) + **X-ray holographic nanotomography (XNH)** of the leg
(Kuan et al., *Nat Neurosci* **23**, 1637–1643, 2020) + sparse **MCFO genetic driver lines**
(Meissner et al., *eLife* **12**:e80660, 2023). Corroborated by an 8 µm-voxel synaptic-density
UMAP (**1,891 voxels × 69 MNs**). **Supplementary Table 1 of Azevedo 2024 has Neuroglancer links
for the leg MNs.** Full notes: `docs/research/sources/azevedo_2024_fanc.md`.

### Canonical leg-muscle nomenclature

- **VERIFIED as a real reference** (FlyBase reference report FBrf0007735,
  https://flybase.org/reports/FBrf0007735.htm):
  **Miller A (1950). "The internal anatomy and histology of the imago of *Drosophila
  melanogaster*." In: Demerec M (ed.), *Biology of Drosophila*, Wiley, New York, pp. 420–534.**
  The brief's guess is correct.
- **VERIFIED, strongest single piece of evidence:** the FlyMimic MuJoCo model *uses Miller's
  numbering directly in its site names* — `LFC_Miller28a`, `Miller28b`, `Miller29`, `Miller30`,
  `Miller31`, `Miller32`, `Miller33` map onto tergopleural promotor a/b, pleural remotor-and-
  abductor, pleural promotor, sternal anterior rotator, sternal posterior rotator, sternal
  adductor. (Parsed by me from
  `flymimic/assets/models/best_combined_arm_damping_stiff_cvt3.xml`.)
  Full muscle list + Hill parameters: `docs/research/sources/ozdil_2026_flymimic.md`.
- **VERIFIED** Soler C, Daczewska M, Da Ponte JP, Dastugue B, Jagla K. "Coordinated development of
  muscles and tendons of the *Drosophila* leg." *Development* **131**, 6041–6051 (2004).
  DOI `10.1242/dev.01527`. (Also Soler, Laddada & Jagla, *Front Physiol* **7**:22, 2016,
  DOI `10.3389/fphys.2016.00022`, a follow-up review of leg muscle/tendon development.)

---

## C. Proprioceptors in simulation

### Fly proprioceptor physiology (all VERIFIED via Crossref)

- Mamiya A, Gurung P, Tuthill JC. "Neural Coding of Leg Proprioception in *Drosophila*."
  *Neuron* **100**, 636–650.e6 (2018). DOI `10.1016/j.neuron.2018.09.009`. ← claw/hook/club FeCO
  subtypes. The brief's citation is correct.
- Mamiya A, Sustar A, Siwanowicz I, Qi Y, et al. (14 auth.). "**Biomechanical** origins of
  proprioceptor feature selectivity and topographic maps in the *Drosophila* leg."
  *Neuron* **111**, 3230–3243.e14 (2023). DOI `10.1016/j.neuron.2023.07.009`.
  (Preprint title drops "Biomechanical": bioRxiv `10.1101/2022.08.08.503192`.)
- Dallmann CJ, Luo Y, Agrawal S, Mamiya A, et al. (9 auth.). "**Selective presynaptic inhibition
  of leg proprioception in behaving *Drosophila*.**" *Nature* **647**, 445–453 (2025-09-17).
  DOI `10.1038/s41586-025-09554-2`. ← this is the "2025 Nature paper by Dallmann" the brief asks
  about. (Preprint bioRxiv `10.1101/2023.10.20.563322`.)
- Pratt B, Dallmann CJ, Chou G, Siwanowicz I, et al. (9 auth.). "Proprioceptive limit detectors
  **contribute to** sensorimotor control of the *Drosophila* leg." *Nature Communications* **17**
  (2026-02-12). DOI `10.1038/s41467-026-69333-z`. (Preprint `10.1101/2025.05.15.654260`, whose
  title says "mediate" not "contribute to". PMID 40475590 is the preprint/earlier record.)
- Dallmann CJ, Karashchuk P, Brunton BW, Tuthill JC. "A leg to stand on: computational models of
  proprioception." *Current Opinion in Physiology* **22**, 100426 (2021).
  DOI `10.1016/j.cophys.2021.03.001`. ← the review to cite for "how do you model a proprioceptor".
- **SECOND-HAND** Agrawal S, Dickinson ES, Sustar A, Gurung P, et al. "Central processing of leg
  proprioception in *Drosophila*." bioRxiv `10.1101/2020.06.04.132811`; journal version believed
  *eLife* 2020 — not yet verified.

### Campaniform sensilla / load sensing models

- **VERIFIED** Saltin BD, Goldsmith C, Haustein M, Büschges A, et al. (6 auth.). "A parametric
  finite element model of leg campaniform sensilla in *Drosophila* to study campaniform sensilla
  location and arrangement." *J. R. Soc. Interface* **22** (2025-05). DOI `10.1098/rsif.2024.0559`.
  (Preprint `10.1101/2023.07.24.550300`.) ← FE model, not a real-time sim sensor.
- **VERIFIED** Cocatre-Zilgien JH, Delcomyn F. "Modeling stress and strain in an insect leg for
  simulation of campaniform sensilla responses to external forces." *Biological Cybernetics*
  **81**, 149–160 (1999). DOI `10.1007/s004220050551`. ← the classic CS-from-strain model.

### The "does NeuroMechFly model proprioceptors?" question — **answer: no, joint angles only**

**VERIFIED** from the FlyGym docs source (`doc/source/api_ref/mdp_specs.rst` @ v1.1.0) and the
current `docs/index.md` / `README.md` on `main`.

Current README, verbatim:
> "**Mechanosensory feedback:** The user has access to **joint angles, actuator forces, contact
> forces, and user-defined anatomical joint-site positions**."

Observation space of the default `Simulation` (verbatim from the MDP spec page):
- `"joints"` — shape `(3, num_actuated_joints)`: **angle, angular velocity, force** per DoF.
- `"fly"` — `(4,3)`: position, velocity, orientation, orientation rate.
- `"contact_forces"` — `(num_contact_sensor_placements, 3)`.
- `"end_effectors"` — `(6,3)`, most distal tarsus link per leg.
- `"vision"` — `(2, num_ommatidia_per_eye, 2)` if enabled; `"odor_intensity"` if enabled.

**There is no FeCO, no claw/hook/club subtype, no campaniform sensillum, no hair plate** anywhere
in the observation space or the docs. Searching the docs for `chordotonal`, `campaniform`,
`proprioceptor`, `hair plate` returns nothing. The word "proprioception" in FlyGym means
**joint angle + velocity + actuator force**, full stop.

Two hierarchy notes that are useful anyway:
- FlyGym explicitly supports splitting the controller into brain and VNC halves with a
  **descending / ascending interface** between them — the natural seam for this project.
- The **FlyMimic musculoskeletal** model is the exception in the other direction: it *drops*
  per-leg ground-contact sensors, and `flybody-connectome`'s author measured `nsensor == 0` on the
  raw flybody MJCF.

So: modelling FeCO claw/hook/club or campaniform load channels is **work this project would have
to originate.** Nothing off the shelf provides it.

### Leg kinematics / models

- **VERIFIED** Haustein M, Blanke A, Bockemühl T, Büschges A. "A leg model based on anatomical
  landmarks to study 3D joint kinematics of walking in *Drosophila melanogaster*."
  *Frontiers in Bioengineering and Biotechnology* **12** (2024-06-26). DOI `10.3389/fbioe.2024.1357598`.
  **CORRECTION for the brief:** this is **Büschges lab (Haustein et al.)**, *not* Dallmann/
  Karashchuk/Tuthill.
- **VERIFIED** Karashchuk P, Rupp KL, Dickinson ES, Walling-Bell S, et al. "Anipose: A toolkit for
  robust markerless 3D pose estimation." *Cell Reports* **36**, 109730 (2021).
  DOI `10.1016/j.celrep.2021.109730`.
- **VERIFIED (Crossref record for the reviewed preprint)** Karashchuk L, Li J, Chou G,
  Walling-Bell S, et al. "Sensorimotor delays constrain robust locomotion in a 3D kinematic model
  of fly walking." *eLife* reviewed preprint, DOI `10.7554/eLife.99005.1` (2024-08-27). ← directly
  relevant: proprioceptive-delay-constrained fly walking model. VOR DOI not yet checked.

---

## D. Hill-type muscle in insects

### **The one that matters most: a *Drosophila* Hill-muscle leg model already exists.**

Özdil PG, Ning C, Phelps JS, Wang-Chen S, Elisha G, Blanke A, Ijspeert A, Ramdya P (2026).
"Musculoskeletal simulation of limb movement biomechanics in *Drosophila melanogaster*."
**ICLR 2026**, **arXiv:2509.06426**. Repo https://github.com/gizemozd/FlyMimic (Apache-2.0),
shipped inside FlyGym 2.x. **VERIFIED.** Full notes, muscle list, and the actual MJCF Hill
parameters in `docs/research/sources/ozdil_2026_flymimic.md`.
Caveat: **left-front leg only** (15 muscles), thorax tethered, other legs locked/passive.

### Stick insect

- **VERIFIED** Blümel/Hooper/Guschlbauer/Büschges trilogy, *Biological Cybernetics* **106** (2012),
  all *Carausius morosus* extensor tibiae:
  1. Blümel M, Hooper SL, Guschlbauer C, White WE, Büschges A. "Determining all parameters
     necessary to build Hill-type muscle models from experiments on single muscles."
     pp. 543–558. DOI `10.1007/s00422-012-0531-5`.
  2. Blümel M, Guschlbauer C, Daun-Gruhn S, Hooper SL, Büschges A. "Hill-type muscle model
     parameters determined from experiments on single muscles show large animal-to-animal
     variation." pp. 559–571. DOI `10.1007/s00422-012-0530-6`.
  3. Blümel M, Guschlbauer C, Hooper SL, Büschges A. "Using individual-muscle specific instead of
     across-muscle mean data halves muscle simulation error." pp. 573–585.
     DOI `10.1007/s00422-011-0460-8`.
  → Use these for **parameter priors and for the animal-to-animal variance envelope**.
- **VERIFIED** Naris M, Szczecinski NS, Quinn RD. "A neuromechanical model exploring the role of
  the common inhibitor motor neuron in insect locomotion." *Biological Cybernetics* **114**, 23–41
  (2019/2020). DOI `10.1007/s00422-019-00811-y`. ← AnimatLab-style Hill muscle + CI motor neuron.
- **SECOND-HAND** AnimatLab 2 uses a Hill muscle with series spring, parallel spring, parallel
  damper and an active element; Szczecinski/Quinn (Case Western / WVU) also published
  "Using AnimatLab for Neuromechanical Analysis: Linear Hill Parameter Calculation"
  (Springer LNAI, Living Machines 2020, DOI `10.1007/978-3-030-64313-3_38`) and
  "Response of a Neuromechanical Insect Joint Model to Inhibition of fCO Sensory Afferents"
  (DOI `10.1007/978-3-030-64313-3_15`). DOIs taken from search-result URLs — **not Crossref-
  verified yet**.

### Fly-shaped robots (Quinn/Szczecinski lab)

- **VERIFIED** Goldsmith C, Szczecinski NS, Quinn RD. "Drosophibot: A Fruit Fly Inspired Bio-Robot."
  *Lecture Notes in Computer Science* (Living Machines 2019), pp. 146–157.
  DOI `10.1007/978-3-030-24741-6_13`.
- **VERIFIED (Crossref preprint record)** Goldsmith C, Haustein M, Büschges A, Szczecinski NS.
  "A biomimetic fruit fly robot for studying the neuromechanics of legged locomotion."
  bioRxiv `10.1101/2024.02.22.581436` (2024-02-27); journal version in *Bioinspiration &
  Biomimetics* (an author-response DOI `10.1088/1748-3190/ad80ec/v2/response1` exists, so the
  article DOI stem is `10.1088/1748-3190/ad80ec`). ← Drosophibot II.

### Things that do NOT exist, as far as I can find

- **No Hill-type *Drosophila* larva muscle model.** Searched Crossref and the web. What exists is
  kinematic/continuum-mechanical, not Hill-type:
  - **VERIFIED** Loveless J, Webb B. "A Neuromechanical Model of Larval Chemotaxis."
    *Integrative and Comparative Biology* (2018). DOI `10.1093/icb/icy094`.
  - **VERIFIED (preprint record)** Sun X, Liu Y, Liu C, Mayumi K, et al. "A neuromechanical model
    for *Drosophila* larval crawling based on physical measurements."
    bioRxiv `10.1101/2020.07.17.208611` (2020).
  Neither is Hill-type. If the brief claims otherwise, it is wrong.
- **No cockroach or locust Hill-type whole-leg musculoskeletal model** surfaced in Crossref search.
  What exists for those animals is motor-pool physiology, not a transferable muscle model:
  Sasaki & Burrows, *J Exp Biol* **201**, 1885–1893 (1998), DOI `10.1242/jeb.201.12.1885`
  (nine excitatory MNs in the locust flexor tibiae); Hoyle, *J Exp Biol* **73**, 205–233 (1978),
  DOI `10.1242/jeb.73.1.205` (locust jumping-muscle fibre types). Both **VERIFIED via Crossref**.
  → The stick insect (Blümel et al.) remains the only insect with a fully parameterised Hill model,
  and *Drosophila* now has its own (Özdil et al.), so the stick-insect transfer is a fallback, not
  the main route.
- **No published peer-reviewed work driving a fly body from identified connectome leg motor
  neurons through muscles.** A2 above is the complete state of the art.

---

## Additional verified references worth having

- **VERIFIED** Brierley DJ, Rathore K, VijayRaghavan K, Williams DW. "Developmental origins and
  architecture of *Drosophila* leg motoneurons." *Journal of Comparative Neurology* **520**,
  1629–1649 (2012). DOI `10.1002/cne.23003`. ← the leg-muscle-group / hemilineage source MANC cites.
- **VERIFIED** Brierley DJ, Blanc E, Reddy OV, VijayRaghavan K, Williams DW. "Dendritic Targeting
  in the Leg Neuropil of *Drosophila*: The Role of Midline Signalling Molecules in Generating a
  Myotopic Map." *PLoS Biology* **7**, e1000199 (2009). DOI `10.1371/journal.pbio.1000199`.
  ← the **myotopic map**: MN dendrite position in the neuropil predicts muscle target.
- **VERIFIED** Baek M, Mann RS. "Lineage and Birth Date Specify Motor Neuron Targeting and
  Dendritic Architecture in Adult *Drosophila*." *J. Neuroscience* **29**, 6904–6916 (2009).
  DOI `10.1523/JNEUROSCI.1585-09.2009`.
- **VERIFIED (preprint/assessment records)** Karashchuk L, Li J, Chou GM, Walling-Bell S, et al.
  "Sensorimotor delays constrain robust locomotion in a 3D kinematic model of fly walking."
  *eLife* reviewed preprint `10.7554/eLife.99005`, versions `.1` (2024-08-27), `.2` (2025-03-20),
  `.3` (2025-05-15). Same UW group as Pugliese et al. ← the delay/proprioception-constrained
  walking model to compare against.
- **VERIFIED** Wang-Chen S, Ramdya P. "The embodied brain: Bridging the brain, body, and behavior
  with biorealistic neuromechanical models." *Current Opinion in Neurobiology* (2026);
  **arXiv:2601.08056**. ← framing review.

---

## Corrections to the source brief

| brief said | actual |
|---|---|
| arXiv:2602.17997 "may be bogus" | **Real.** Jin/Zhu/Zhang/Sui, FlyGM, FlyWire→flybody, Feb 2026. |
| arXiv:2511.20532 MIMIC-MJX "includes a fly?" | Real paper (Zhang CY + 43, Nov 2025 / Aug 2026). **Fly content unconfirmed**; the showcased demo is a mouse forelimb. |
| Shiu 2024 Nature "A leaky integrate-and-fire computational model…" | That is the **bioRxiv title**. The *Nature* title is "**A Drosophila computational brain model reveals sensorimotor processing**", **634**:210–219, DOI `10.1038/s41586-024-07763-9`. No body model. |
| Cheong 2024 eLife "Transforming descending input into behavior…" | That is the **2024 reviewed-preprint title**. VOR (2026-07-20) is "**Organization of circuits linking descending input to motor output…**", *eLife* **13**, DOI `10.7554/eLife.96084`. |
| Azevedo "eLife 2020?" size principle | Correct: *eLife* **9**:e56754 (2020), DOI `10.7554/eLife.56754`. |
| Dallmann/Karashchuk/Tuthill "A leg model based on anatomical landmarks…" | Wrong lab. It is **Haustein M, Blanke A, Bockemühl T, Büschges A**, *Front. Bioeng. Biotechnol.* **12** (2024), DOI `10.3389/fbioe.2024.1357598`. |
| "any 2025 Nature paper by Dallmann" | **Dallmann CJ et al., *Nature* 647:445–453 (2025)**, "Selective presynaptic inhibition of leg proprioception in behaving *Drosophila*", DOI `10.1038/s41586-025-09554-2`. |
| Mamiya et al. 2023 | Journal title includes "**Biomechanical** origins…", *Neuron* **111**:3230–3243.e14, DOI `10.1016/j.neuron.2023.07.009`. |
| Miller 1950 in Demerec | **Correct**, FlyBase FBrf0007735, pp. 420–534. And it is the live nomenclature: FlyMimic's MJCF literally encodes `Miller28a…Miller33` in its site names. |
| "Hill-type muscle models in OTHER insects that could be transferred to a fly" | **A *Drosophila* one already exists** — Özdil et al., ICLR 2026, arXiv:2509.06426, shipped in FlyGym 2.x. Start there, not from the stick insect. |
| flygym connectome-vision tutorial URL | `advanced_vision` ("Connectome-constrained visual system model"), FlyGym **1.x only**. `neuromechfly.org` is currently a **parked GoDaddy lander**; use the repo tag `v1.1.0` or `NeLy-EPFL/flygym-gymnasium`. |
