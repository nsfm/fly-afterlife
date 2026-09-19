# the landscape: who else is running the 2026 connectomes, and who gave theirs a world

survey, 2026-09-18 (nyx), from web search on this date. every project below was checked
against its own repository or paper; github metadata (licence, stars, creation and last-push
dates) comes from the github api on 2026-09-18. where a claim is a project's own, it is
labelled as such: almost nothing in the hobby layer has been replicated by anyone else,
including us.

the short answer to nate's question: the sensory-deprivation guess was right until about
six weeks ago and is now wrong. as of september 2026 there are at least five independent
projects running a 2026 connectome inside a physics body with sensory input and a motor
readout, and at least two of them are ahead of us on senses or on validation discipline.
the field went from "nobody has a body" to "several bodies, all of them steering on two or
three descending neurons" inside one release cycle of the male connectome.

## the data, and when it landed

MaleCNS v1.0 (brain, optic lobes, neck connective and ventral nerve cord of one male fly;
166,691 neurons in 11,691 annotated cell types) was released on 2026-06-08 under CC-BY by
FlyEM at HHMI Janelia with Cambridge Zoology, the MRC LMB and Google Research
(<https://male-cns.janelia.org/release/>). BANC, the first synapse-resolution connectome to
unite brain and nerve cord in one animal (a female, ~188,000 neurons, ~199M predicted
synapses), published in Nature in 2026 as Bates, Phelps, Kim, Yang et al., with its figure
pipeline at <https://github.com/htem/BANC-project> and python access at
<https://github.com/jasper-tms/the-BANC-fly-connectome>. FlyWire FAFB v783 (Dorkenwald et
al., Nature 2024, <https://doi.org/10.1038/s41586-024-07558-y>) remains the most-used
substrate in the hobby layer, because it has had two years of tooling.

## the brains, in tanks

**Shiu et al. 2024** is still the reference model. "A Drosophila computational brain model
reveals sensorimotor processing", Nature 634:210-219, 2024-10-02
(<https://doi.org/10.1038/s41586-024-07763-9>); code at
<https://github.com/philshiu/Drosophila_brain_model> (MIT, 320 stars, last pushed
2024-09-14, i.e. dormant since publication). Brian2, FlyWire, one threshold and one time
constant for every neuron, driven by activating named cell types. no body, no world, no
transduction. it is the model our `ref/flybrain` inherits its constants from, and the model
whose optic-lobe blindness `SEAM.md` opens by attacking.

**flyvis** (Lappalainen et al., Nature 2024, <https://doi.org/10.1038/s41586-024-07939-3>;
<https://github.com/TuragaLab/flyvis>, MIT, 177 stars, active to 2026-08) is the graded
counterpart we already use. it is a deprivation tank by construction: it takes video, not a
world, and stops at T4/T5.

**intel loihi 2.** Wang, Theilman, Rothganger, Severa, Vineyard and Aimone (Sandia),
arXiv:2508.16792, 2025-08-22, CC-BY: the whole FlyWire connectome on twelve Loihi 2 chips,
82-356x faster than CPU and matching reference simulators to within about 2%. no sensory
input, no body; the contribution is the port and its statistical validation. no code link
found.

**eonsystemspbc/fly-brain** (GPL-2.0, 841 stars, active 2026-08,
<https://github.com/eonsystemspbc/fly-brain>) is the same Shiu model across six backends,
Brian2 CPU as ground truth against Brian2CUDA, PyTorch, NEST GPU, GeNN and Brian2GeNN, with
600 committed spike-parquet files and sha256 manifests. it is a benchmark harness, not a
fly. it is also the most rigorous reproducibility artefact in the whole survey and worth
copying the shape of.

others in this layer, all tank-only: `annel0/flybrain` (MIT, triton kernels,
2026-09), `eonfathom/FastFly` (CUDA/CuPy, no licence, last push 2026-02),
`IONOFIELD/FLYCNS` (no licence, active, MaleCNS with a 16-criterion pass/fail suite),
`YijieYin/connectome_interpreter` (MIT, a differentiable whole-brain effective-connectivity
library) and `eudald-seeslab/train-your-fly` (Apache-2.0, trains FlyWire-constrained vision
models).

## the bodies, without brains

**NeuroMechFly v2** (Wang-Chen, Stimpfling, Özdil, Ramdya et al., Nature Methods, 2024-11,
<https://doi.org/10.1038/s41592-024-02497-y>; `flygym`, Apache-2.0, 355 stars, active
2026-08, <https://github.com/NeLy-EPFL/flygym>) is the body everyone uses: MuJoCo, 87
joints, leg adhesion, terrain, and, importantly for us, a documented interface to a
connectome-constrained visual network. the v2 paper already ran a following task where a
pretrained connectome-constrained vision model read the rendered eye and drove object
detection, so the flyvis-into-a-body move is theirs first, not ours.

**flybody** (Vaxenburg et al., "Whole-body physics simulation of fruit fly locomotion",
Nature 2025, <https://doi.org/10.1038/s41586-025-09029-4>;
<https://github.com/TuragaLab/flybody>, Apache-2.0, 919 stars) is the DeepMind/Janelia body,
with fluid forces and adhesion actuators and RL flight and walking tasks. the body is driven
by trained artificial networks, not by a connectome, in the paper itself.

the pairing was closed in **Jin, Zhu, Zhang and Sui, "Whole-Brain Connectomic Graph Model
Enables Whole-Body Locomotion Control in Fruit Fly"**, arXiv:2602.17997 (submitted
2026-02-20, revised 2026-06-14, CC-BY), which instantiates the whole-brain connectome as a
graph-structured RL controller for a simulated fly body and beats graph and non-graph
baselines on sample efficiency. no code or data URL was given on the abstract page; i could
not verify a public release.

the cautionary paper is **Brunton and colleagues, "The digital sphinx: can a worm brain
control a fly body?"** (bioRxiv 2026-03-24, <https://doi.org/10.64898/2026.03.20.713233>,
eLife reviewed preprint 111516): the *C. elegans* connectome plus a trained readout drives a
fly body to walk convincingly, which they present as proof that behavioural fidelity is
achievable without biological fidelity. that argument applies directly to every steering
readout in the table below, ours included.

the review to read is Wang-Chen and Ramdya, "The embodied brain", arXiv:2601.08056v4,
2026-07-20, CC-BY, which names NeuroMechFly, flybody, flyvis and Shiu as the four pieces and
says whole-brain connectome embodiment at scale is still aspirational. that was written two
months before the repos below appeared.

## the ones that closed the loop

these are the real peers. all are 2026, all are single-author or small-team, and all are
unreviewed.

| project | brain | body | world | transduction | motor readout | closed | validated against behaviour |
|---|---|---|---|---|---|---|---|
| **flyverse-core** | MaleCNS v1.0 LIF + graded optic lobe | own walker/flier | 3-D room, table, fruit | ray-traced spectral ommatidia, plumes, wind on JO, taste | named DN groups, wing MNs, GF | yes | own probe suite: DS in 8/8 subtypes 9/9 runs, loom→GF 9/9 |
| **Fly.exe** | MaleCNS, 165,122 neurons, all edges | NeuroMechFly v2 | MuJoCo arena, food, pillars | analytic bearing/size, no pixels | two DN population rates | yes | self-rated tier V0 "structural"; swarm awards no tier |
| **closed-loop-fly** | MaleCNS LIF on WebGPU | NeuroMechFly | pillar course, flight | rendered image → 65.8k-unit optic-lobe rate model | DNa02 (declared deviation from DNg02) | yes | ablation table; then partly withdrawn by its own follow-up |
| **eon embodied fly** | Shiu/FlyWire LIF | NeuroMechFly v2 | MuJoCo | taste, olfaction, antennal touch, visual motion | DNa01/DNa02/oDN1/MN9 into pretrained controllers | yes, 15 ms | none stated |
| **erojasoficial/fly-brain** | FlyWire v783, 138,639 LIF + hebbian | NeuroMechFly v2 | terrain, odours, threats | multi-modal, claimed | ~1,100 DNs → mode selection | yes | own preprint only |
| **webgpu-fly** | FlyWire + MANC, both LIF | flybody in WASM | browser game arena | retina into brain | walk magnitude + turn bias, scaling a hand-written gait | yes | explicitly none; KC sparsity is a tuned calibration |
| **NeuroFly** | FlyWire v783 Brian2 | NeuroMechFly | odour plume corridor | olfaction; T5 via flyvis in v4 | locomotion drive | yes | none; author states no neuroscience training |
| **CHIMERA** | larval connectome, 1,373 neurons | MuJoCo | minimal | sensory activation | LIF → body | yes | none |

**flyverse-core** (<https://github.com/tel-0s/flyverse-core>, MIT, created 2026-09-10, pushed
2026-09-18) is the closest thing to us and in several respects ahead. it ray-traces spectral
radiance in UV/B/G/R onto 5,895 photoreceptors on 1,466 real hex columns, runs 89,390
optic-lobe cells as graded rate units on the signed connectome in a flyvis-style scheme
rather than borrowing flyvis's weights, then hands 71,618 central and VNC neurons to a Shiu
LIF, and it drives smell as a wind-blown plume per fruit sampled by two antennae 1 mm apart,
wind through Johnston's organ C/E sided by their AMMC/WED targets, and sugar GRNs through to
MN9. it reports a loom driving LC4/LPLC2 to the giant fibre at ~3.5 cm with TTMn following
1:1, silent during textured walking, in 9 of 9 suite runs. it also labels five "computation
stand-ins" (a compass, plume, hunger, flight) that replace a computation the wiring cannot
do, with a `replaces: "computation"` field in each record. that labelling discipline is the
single best idea in the survey.

this is the hard news for `SEAM.md`. its opening claim, that every public whole-fly
simulation is the plain Shiu LIF and therefore nobody's fly can see a threat, is no longer
true. flyverse-core did the graded-periphery-into-spiking-centre move independently, on
MaleCNS, and reports the loom-to-giant-fibre result we have not got. the claim should be
narrowed to "every published model", with flyverse named, or dropped.

**Fly.exe** (<https://github.com/Ibtisam-Mohammad/Fly.exe>, GPL-2.0, created 2026-09-12) is
the most honest engineering in the survey and the weakest sensing: its vision is analytic,
handed each object's exact position and radius, with no pixels, no occlusion, no colour. it
compensates with a validation ladder (V0-V8), preregistered acceptance contracts, reserved
datasets held unopened to prevent snooping, ADRs recording discarded arenas, and a README
that refuses tiers for its own showcase video. its walking is an engineered gait; no part of
its simulated VNC moves a leg.

**closed-loop-fly** (<https://github.com/ZeroXClem/closed-loop-fly>, MIT, 2026-09-07) welds
`AbijahKaj/fruit-fly-brain-research` (a MaleCNS optic-lobe rate model sampled at the
connectome's 1,771 column directions) to Xenova's WebGPU MaleCNS LIF
(<https://huggingface.co/spaces/Xenova/fruit-fly-simulation>) and a NeuroMechFly body. it
flies a pillar course in closed loop, runs a six-phase ablation study, and then, in
`docs/followups.md`, withdraws part of its own headline: the "vision matters" contrast acted
through a readout artefact where a silent DNa02 pair became a fixed turn, and with the
artefact gated the intact loop drifts ~200° in 20 s. that failure mode, a silent readout
neuron reading as a constant command, is exactly the class of bug our one-neuron steering
readout has (the drifting resting bias, ensemble 2-3/10).

the rest: **eon's embodied fly** (blog 2026-03-10,
<https://eon.systems/updates/embodied-brain-emulation>) couples the Shiu model to
NeuroMechFly v2 at a 15 ms interval with four sensory modalities, but the write-up states no
validation and i found no separate code repo for the embodied part.
**erojasoficial-byte/fly-brain** (MIT, 60 stars, 2026-03, Zenodo
doi:10.5281/zenodo.19152238) claims embodied FlyWire plus hebbian plasticity producing
"computational individuality" from identical connectomes; the claim rests on one
self-published preprint and i would not rely on it. **webgpu-fly** (MIT, 2026-05 to 2026-09)
is the only one that also runs a real ventral cord (MANC) as a second network, and its
`LIMITATIONS.md` is candid that the locomotion layered on top is an approximation.
**NeuroFly** (no licence, last push 2026-04-05, probably dormant) is a solo French project
that reached flyvis-T5-plus-olfaction navigation. **CHIMERA** (no licence, single day of
commits 2026-03-21) is abandoned.

## three more, read in the source (09-19; `docs/MINECRAFT_FLYPROJECT.md`, `docs/MINECRAFT_OPEN.md`)

| project | brain | body / world | transduction | readout | closed | what the source says |
|---|---|---|---|---|---|---|
| **flyproject.io connectome-fly** (closed jar, CC-BY-SA) | BANC v888, 9 % of synapses, uncited constants + adaptation | Minecraft mob | 39 game channels as Poisson kicks | L-R of all DNs, half of it random | yes | one core is real and the network is inert: injected kicks ~= emitted spikes; the male is 40 scripted lines |
| **blendi-remade/fly-brain-minecraft** (MIT) | MaleCNS, exact linear integration, Shiu's constants (dt 0.5 quantises refractory / delay to 2.0) | Minecraft mob | real cell types, 1,769 measured columns | named populations, ~150 hand-set numbers | yes | the best open Shiu implementation; publishes its failures; loom claim does not reproduce; odour readout anticorrelated |
| **AshtonLong/fruitfly-brain-mod** (open) | FlyWire unpruned, 0.275, Euler, a 68.75 mV kick per input | Minecraft mob | game state | 2 neurons a side through tanh | yes | 25 ms of neural time per 500 ms wall; neither readout works; honest about it |

## tooling

navis, `fafbseg-py`, `navis-flybrains`, `neuprint-python` and `CAVEclient` are the standard
python stack (all at <https://github.com/navis-org>, <https://github.com/connectome-neuprint>
and <https://github.com/CAVEconnectome>). for cross-dataset work the useful newer ones are
`flyconnectome/cocoa` (FlyWire, hemibrain, MANC and MaleCNS in one interface),
`schlegelp/connecto` (normalises CAVE and neuPrint queries),
`flyconnectome/ol_annotations` (cross-dataset optic-lobe cell-type matches between
FAFB/FlyWire and MaleCNS, which is directly relevant to our transplant), and
`YijieYin/connectome_data_prep` (prepared connectivity matrices for MaleCNS, BANC, FlyWire
and hemibrain). virtual fly brain (<https://virtualflybrain.org>,
<https://github.com/VirtualFlyBrain>) now carries the whole-CNS connectomes, a circuit
browser and an MCP server. the two useful indexes are `cobanov/awesome-fly` (CC0, 505 stars)
and `townie/awesome-fruit-fly`.

**not found:** a machine-readable cell-type-to-behaviour drive table derived from Cande 2018,
Braun 2024 or Sapkal 2024. those papers' DN-activation results exist as supplementary tables
and as split-GAL4 line catalogues, not as a queryable dataset anyone has packaged. building
one would be a genuine contribution; our `world/` DN gain tables are a private version of it.

## the hobby layer

there are now roughly sixty MaleCNS and FlyWire repos, most created in the first two weeks
of september 2026 after the connectome release. the large cluster is games: doomfly (360
stars), fly-escape (46), fly64, flypong, connectome-fighter, fly-craftax, `zhengxuyu/nfly`
(MaleCNS as an RNN for any gymnasium game). these do have worlds and closed loops, but the
brain is a subgraph with a trained readout on top, so the loop closes through the training,
not through the wiring. the honest ones say so. the desktop-pet cluster (desktop-fly,
`snedea/flybrain` at 129 stars, `infinite-sugar`) has a body and no world. almost none carry
a licence; most have not been pushed in over a week.

## what to take

four things, in order of how cheap they are.

first, flyverse's **instrument labelling**: every stand-in declares in code whether it
supplies a missing *input* or replaces a missing *computation*, and the provenance record
carries the flag. our `--proprio` tripod rule and our walking-command tonic are exactly
computation stand-ins and are currently only labelled in prose.

second, Fly.exe's **preregistered acceptance contract and reserved data**. we already do
one-change-per-run against the previous run; what we do not do is fix the criterion before
the run and keep an unopened arm. the withdrawal block at the top of `SEAM.md` is what
happens without it, and it is the right response, but it is the expensive one.

third, closed-loop-fly's **silent-readout artefact** as a named test. add a control in which
the steering DN is forced silent; if the body still turns, the readout is reading absence as
command. that is a one-hour test and it directly attacks our steering bottleneck.

fourth, the **ablation-against-identical-seed control** that both Fly.exe and closed-loop-fly
run: same seed, same bodies, sensory encoder pinned at baseline. our approach test already
found one artefact this way; making it the default arm for every behaviour claim is free.

what we still do that nobody else in this survey does: a ray-traced compound eye on the
*measured* geometry of the same fly whose wiring we run, with flyvis's trained physiology
transplanted onto that fly's own optic-lobe cells rather than tiled. flyverse ray-traces but
fits its own optic lobe; closed-loop-fly uses the real column directions but a separately
fitted rate model; everyone else feeds analytic positions or a rendered camera to a
hand-built encoder. that seam is still ours, and it is still the part that does not yet work
well enough to detect a loom.
