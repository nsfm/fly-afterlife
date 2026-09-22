# The flight gate: what holds the wing power motor down in a standing fly

*2026-09-21. Written by an opus research agent for nyx.*

A literature and data brief on the cells that run our standing fly's flight motor: the descending
neurons DNp31, DNb05 and DNg33, the cord premotor pair IN19B043 / IN19B067, the self-exciting node
IN19B040, and the three GABAergic classes IN06B066 / IN03B089 / IN11B013 that should be braking the
DLM and DVM motor neurons and are not. Everything below is marked established (published result),
inferred (my reading), or our data (a query against the MaleCNS v1.0 tables in `data/`, run for this
brief). Type names are exactly as they appear in
`body-annotations-male-cns-v1.0-minconf-0.5.feather`.

---

## 1. DNp31, DNb05, DNg33, and the visual cells that feed them

### DNp31

**What is established.** DNp31 is one of the descending neurons named in the Namiki et al. (2018)
atlas, in the DNp (posterior soma) cluster. Our annotation table gives it subclass `ut`, upper
tectulum, which is the VNC region holding the neck, wing and haltere motor neurons. Namiki et al.
found roughly 29 DN types innervating the wing neuropil and concluded there is "separate descending
control of the power and steering muscle systems". No paper recording or activating DNp31 by itself
exists that I could find. The one functional claim in print is connectomic: in the MANC premotor
analysis (Cheong et al., eLife 2024/2025), "DNa08 and DNp31 further excites IN06B066 group 16779,
which may form an inhibition-stabilized [network] with Tect INs to limit runaway excitation", where
the Tect INs are the 42 tectular intrinsic neurons that "contribute the bulk of upstream connectivity
of the power MNs". So the literature's reading of the exact motif we are sitting inside is an
inhibition-stabilized network, not a half-centre oscillator.

**Our data.** DNp31 is 2 cells, cholinergic, `hemibrainType` = `flywireType` = `mancType` = DNp31.
Its top presynaptic types (36,126 input synapses total) are given in section 5. Its outputs: DLMn c-f
(1,128), MNwm36 (722), IN06B066 (720), ps1 MN (593), DVMn 1a-c (461), IN19B043 (337), DVMn 3a,b
(320), IN06B013 (303), DVMn 2a,b (296). It excites power motor neurons, the excitatory premotor, and
the inhibitory class IN06B066, all at once, which is exactly the Cheong reading.

**Are LLPC2, LPLC4, LPC2 and LC36 known inputs?** In our table, yes and they are large: LLPC2 2,591
(7.2 % of DNp31's input, 250 cells), LPLC4 2,022 (5.6 %, 97 cells), LPC2 776 (154 cells), LC36 663
(32 cells), all cholinergic. I could not find a published paper naming any of these as DNp31 inputs;
the connectome is the source.

**What those visual types encode.** LPC and LLPC types were described anatomically by Wu et al.
(2016). Their tuning follows their lobula plate layer: LPC1 takes T4b/T5b input and carries
back-to-front motion (confirmed by calcium imaging); LPC2 takes T4c/T5c and is expected to encode
upward motion; LLPC1 responds to front-to-back motion with arbors in Lop1 and Lop3; LLPC2 and LLPC3
are the same cell shape with T4/T5 input in Lop3 and Lop4. So LLPC2 and LPC2 are wide-field optic
flow cells reading a single motion direction each, not loom detectors. LPLC4 is different: the optic lobe
anatomy literature describes it as having processes in all lobula plate layers plus Lo2, Lo4 and Lo6,
and notes that arbors spanning several lobula plate layers could support responses to stimuli
combining different motion directions, such as a loom, while grouping LPLC4 apart from the
demonstrated looming detectors LPLC1 and LPLC2. I read that in a secondary summary and did not open
the primary figure, so treat the layer list as unverified. Klapoetke et al. (2017) showed LPLC2 is the
ultra-selective loom detector (radial motion opponency) and that LC4 and LPLC2 are the major inputs
to the giant fiber, LC4 coding angular velocity and LPLC2 angular size. LPLC4 loom selectivity is
therefore *inferred from anatomy, not measured*. LC36 is one of Wu et al.'s lobula columnar types
with no published tuning I could find.

**Would a standing fly in a lit, textured world drive DNp31?** Inferred: yes, partly. T4/T5 drive
their lobula plate columnar targets whenever the retinal image moves, and a standing or walking fly
generates optic flow with every head turn, body turn and step; nothing in the optic lobe waits for
flight. But the gain is state-dependent in the direction that matters here: Maimon et al. (2010)
showed VS cell responses roughly double in flight compared with rest, and Suver et al. (2012) showed
that octopaminergic neurons projecting to the optic lobe become active in flight and are necessary
and sufficient for that boost. So in life the visual drive into these DNs at rest is the *low-gain*
case, not the high one, and the model runs it at full strength with no modulation at all.

### DNb05

**Established.** Namiki et al. (2018) singled it out: "One of the DNs, DNb05 is unusual in that it
innervates both optic glomeruli and olfactory glomeruli." That is exactly the mixed input our table
shows. Yang et al. (2024, Cell) imaged DN populations in walking flies and found DNb05 among five DN
types whose right-left activity difference was consistently correlated with the body's rotational
velocity during steering, with the ipsiversive sign (right-soma cell more active during right turns),
and among the DN types with increased activity during walking bouts compared with non-walking epochs.
So **DNb05 firing in a walking fly is established**, and it is a steering signal.

**Is DNb05 a thermosensory / VP3-driven descending neuron?** Not in the literature I could find. No
paper assigns DNb05 a thermosensory role. The *motif* is established though: Marin et al. (2020,
Current Biology) traced first-, second- and third-order thermosensory and hygrosensory neurons in the
brain and found VP projection neurons converging on descending neurons, noting that the large VP4
(dry) PN input to DNp44 "might represent the shortest known Drosophila brain circuit from sensory
periphery to descending motor control (two synapses)". A VP3 cold PN to DN connection is the same
shape. In our table DNb05's direct sensory input is modest by synapse count (VP3+_l2PN 627, HRN_VP5
503, TRN_VP3a 428, out of 36,551), and it is the *rate weighting* that makes the cooling pathway
dominant in the standing brain (60,840 synapse-spikes/s/cell from VP3+_l2PN). That is a statement
about our input rates, not about anatomy.

**Does a 95 Hz cooling-cell rest driving a DN to 217 Hz have a physiological analogue?** No, and the
literature says why. Budelli et al. (2019) named the arista cells "cooling cells" precisely because
they are *phasic*: they have a basal firing rate, respond transiently to mild cooling, and return to
their original steady-state frequency. Their resting discharge is the zero point of the signal, not a
command. The second-order representation is likewise built around transients (Frank et al., 2015;
Gallio et al., 2011). A model that feeds the baseline through non-adapting, fixed-weight synapses
into a LIF turns "nothing is happening, the temperature is constant" into the largest excitatory
drive in the brain. In life the missing pieces are, in decreasing confidence: receptor and PN
adaptation (established), short-term synaptic depression at a high-rate tonic synapse (general,
established for tonic sensory synapses), and downstream gain control (inferred). **This is a
modelling artifact, not a fly.**

### DNg33

**Could not find anything.** No functional paper, no hemibrain name (our table has `flywireType` and
`mancType` = DNg33, `hemibrainType` empty). It is not in the Namiki 2018 atlas text I could search.

**Our data on the recurrence.** DNg33 is 2 cells, cholinergic. The 1,496 recurrent synapses are
**not autapses**: they are 773 from body 13317 onto 13442 and 723 in the reverse direction, a clean
reciprocal pair. It is 18.4 % of DNg33's own input by raw synapse count (and 82 % by rate weighting
in the standing brain, because almost everything else upstream is quiet). Its largest outputs are
AN09A005 (2,939), AN27X013 (1,619), itself (1,496), IN09A005 (1,321), and only 186 onto IN19B040.

**How a real pair with 1,500 mutual synapses avoids locking.** Inferred from general principles, no
DNg33-specific evidence: spike-frequency adaptation (Ca-dependent and Na-activated K currents, M-type
Kv7), synaptic short-term depression at a synapse driven to hundreds of hertz, and the inhibitory
input the pair does receive (our measurement: 896 synapse-spikes/s of inhibition against 181,313 of
excitation, so inhibition is not the answer here). A leaky integrate-and-fire neuron with no
adaptation, no depression and a fixed quantal weight has none of these, and a reciprocally-coupled
pair with that much weight is a latch by construction. The same shape produced the gnathal runaway
already recorded in SEAM.

---

## 2. What gates the flight motor in life, and what of it exists in our table

**The power muscles are silent on the ground; this is not in dispute.** The mechanisms, and their
representation in MaleCNS v1.0:

| mechanism | status in life | in our table |
|---|---|---|
| giant fiber escape takeoff | established | **DNp01**, 2 cells, cholinergic, subclass `lt` |
| jump muscle motor neuron | established | **TTMn**, 2 cells, glutamate, subclass `wm`; also STTMm (4) |
| peripherally synapsing interneuron | established | **PSI**, 2 cells, superclass `vnc_efferent`, NT unclear |
| GF-coupled cord neurons | connectome | GFC1 (3), GFC2 (10), GFC3 (13), GFC4 (8), all cholinergic |
| looming escape direction DNs | established | **DNp02** (2), **DNp04** (2), **DNp11** (2), all cholinergic |
| landing DNs | established | **DNp07** (2), **DNp10** (2), cholinergic |
| octopaminergic flight modulation | established | 101 octopaminergic cells: OA-VUMa1-a6, OA-VPM3/4, OA-ASM1-3, OA-AL2i1-i4, and **mesVUM-MJ** (1 cell, `vnc_efferent`) |
| flight-motor DN population | established | **DNg02_a** through **DNg02_g**, 29 cells total, cholinergic |

**The giant fiber path is present but cannot work in our engine.** Established anatomy: the GF
(DNp01) forms electrical and chemical synapses with TTMn, which extends the mesothoracic femur, and
with the PSI, which innervates the DLM motor neurons; the GF-evoked DLM spike is one synchronized
depressor contraction for the takeoff downstroke, not flight maintenance (Hummon and Costello, 1989;
Card and Dickinson, 2008). Our data: DNp01 makes 90 synapses onto TTMn and 16 onto PSI, and PSI makes
449 onto DLMn (43 to DLMn a,b and 406 to DLMn c-f). Those chemical weights are small because the
pathway is largely *electrical*, and MaleCNS chemical weights plus a chemical-only LIF carry none of
it. **Inference: our model has no escape takeoff and no giant fiber, whatever the type names say.**

**The tarsal reflex.** Established, old, and cross-species: wing movement is inhibited while the
tarsi contact a substrate, and flight is released when contact is lost; a voluntary takeoff raises
the wings and extends the mid-legs to break that contact (Fraenkel's classical work; Binns, 1977, in
aphids; ground-contact flight inhibition characterised in cockroach, Elson/Wendler-era literature).
This is also the standard laboratory manipulation: tethered flies fly when the tarsi are free and
stop when handed a ball or a card. **I could not find an identified Drosophila cell type carrying
this inhibition.** If we wanted it in the model we would be inventing the cell, which is worse than
leaving the gate unrepresented.

**Octopamine.** Established: octopamine mediates initiation and maintenance of flight (Brembs et al.,
2007), acting centrally on the flight CPG and peripherally by sensitising sensory receptors, altering
muscle contraction kinetics and enhancing flight muscle glycolysis; and the flight-induced visual
gain boost is octopaminergic (Suver et al., 2012). Our data: mesVUM-MJ, the octopaminergic
mesothoracic efferent, makes **1** synapse onto the power motor neurons in the connectome, and
OA-VUMa1/a2/a3 make **0**. Its action is on the muscle and by volume release, both outside a
synaptic LIF. **The entire neuromodulatory state axis is absent from our model by construction, and
that axis is the one that carries "flying" in life.**

**Flight termination.** Established: landing is driven by DNp07 and DNp10; silencing impairs visually
evoked landing, activation drives it, spike rate sets leg extension amplitude (Ache et al., 2019).
And the sentence in that paper is the one this whole brief turns on: *"Visual responses of both DNs
are severely attenuated during non-flight periods, effectively decoupling visual stimuli from the
landing motor pathway when landing is inappropriate."* The mechanism differs between the two: for one
it is octopaminergic (bath octopamine mimics flight), for the other it is probably feedback from the
flight motor circuits. **So the literature's answer to "what gates a visual descending neuron in a
standing fly" is: the visual-to-DN coupling itself is turned down, not the motor neurons braked.**

---

## 3. The flight CPG in the VNC, and what our three GABA classes are

**Firing rates.** Established: DLM and DVM are asynchronous, stretch-activated muscles; their motor
neurons fire single spikes at 5 to 20 Hz during flight, roughly every 10th to 20th wingbeat, entirely
decoupled from the ~200 Hz wingbeat (Harcombe and Wyman, 1977; Gordon and Dickinson, 2006). Our
standing fly runs DLMn a,b at 119 Hz and DVMn 1a-c at 116 Hz. **That is not a flying fly either: it
is 6 to 20 times the rate of a fly in flight.** Worth stating plainly, because "the flight motor is
running" undersells it. Nothing in the fly's repertoire fires these cells at 119 Hz.

**Is there reciprocal / antagonist inhibition of the power MNs?** The best current answer is no, and
that the pattern comes from somewhere else. Hürkey et al. (2023, Nature) showed the Drosophila power
motor neuron network is a CPG built from *electrical* synapses between motor neurons that, against
doctrine, **desynchronize**: the network "translates unpatterned premotor input into stereotyped
neuronal firing with fixed sequences of cell activation that ensure stable wingbeat power", splayed
in time rather than synchronized, and the mechanism is conserved across species. So in life the
premotor input to the power MNs is expected to be tonic and unpatterned, and the sequencing is
intrinsic. Our model has no gap junctions, so it cannot produce the splay at all, and there is no
published half-centre among the power MNs for the brakes to be part of.

**But our tables show the GABA classes are muscle-group specific**, which is our data and, I think,
new to this project:

| source (GABA) | onto DLMn a,b | DLMn c-f | DVMn 1a-c | DVMn 2a,b | DVMn 3a,b | bias |
|---|---|---|---|---|---|---|
| IN06B066 (25 cells) | 1,565 | 4,198 | 321 | 256 | 305 | **DLM, 6.5:1** |
| IN03B089 (18) | 1,747 | 4,565 | 541 | 272 | 292 | **DLM, 5.7:1** |
| IN11B013 (10) | 9 | 118 | 2,456 | 1,394 | 2,003 | **DVM, 46:1** |
| IN12B015 (2) | 120 | 864 | 4 | 1 | 1 | DLM, 164:1 |
| IN06B013 (4) | 55 | 622 | 20 | 5 | 32 | DLM, 12:1 |

and the excitatory premotor is not: IN19B043 gives 10,061 to the DLMns and 4,658 to the DVMns,
IN19B067 gives 9,409 and 2,677, both hitting everything. **Inference: the inhibition in this circuit
is antagonist-specific and the excitation is common.** That is the wiring signature of DLM-versus-DVM
phase control, which is reading (a) from SEAM, but it is equally consistent with independent gain
control of the two muscle groups, and Hürkey et al. argue the phase itself does not need it. I would
not claim more than "the inhibition is organised by muscle group".

**What are these cells called in the literature?** Their names *are* the literature names: our
`mancType` column equals `type` exactly for IN19B043, IN19B067, IN19B040, IN06B066, IN03B089,
IN11B013, IN12B015, IN06B013 and for all five power MN types, i.e. these are the MANC systematic
names carried into MaleCNS unchanged. Beyond that:

- **IN19B043 / IN19B067 / IN19B040**: hemilineage 19B, which Lacin et al. (2019) establish as
  cholinergic (its sibling 19A is GABAergic), consistent with our NT table (9, 14 and 4 cells, all
  acetylcholine). Cheong et al. report that wing motor neurons and upper tectulum DNs "share stronger
  connectivity with hemilineages 6A, 7B, 2A, 19B, 12A, and 3B", and that 42 tectular intrinsic
  neurons ("Tect INs") carry the bulk of power MN upstream connectivity. **Inference: IN19B043 and
  IN19B067 are almost certainly among those Tect INs, but no paper names them individually or calls
  them "wing power premotor".** I could not find IN19B040 anywhere in print.
- **IN06B066**: the one that *is* named, in the sentence quoted in section 1, as the target of DNa08
  and DNp31 that "may form an inhibition-stabilized [network] with Tect INs to limit runaway
  excitation". If that reading is right, IN06B066 is not a flight-state brake at all: it is the
  stabilising inhibition of a recurrent excitatory pool, driven *by* the pool. Which is what our
  numbers show in miniature (it is the only one of the three that fires at all, 3.2 Hz, membrane at
  +24 % of threshold, and it is reciprocal with IN19B067).
- **IN03B089, IN11B013, IN12B015, IN06B013**: could not find any of them in print.

**Walking versus flight.** Established: DNg100 is a walking-promoting descending neuron (used as a
walking command in recent connectome-simulation work). Established in the other direction: leg motor
signals are suppressed during flight. **I could not find a named VNC interneuron implementing
walking-suppresses-flight in Drosophila.** Our IN06B013 motif (DNg100 drives IN06B013, GABA, 4 cells,
which puts 1,756 and 1,301 synapses onto IN19B043 / IN19B067 and 734 onto the power MNs) is a
connectome-level hypothesis of ours, and a decent one, supported by the map arm where the power MNs
sat at 75 Hz with the walking command on and 93 to 109 Hz without it. It is not in the literature.

---

## 4. How to represent "not flying" honestly

The short version: **the fix is upstream, and the first two arms of it are not about flight at all.**

**Against option (a), a tonic inhibitory state on the brake classes.** Three reasons. (i) The cells
are under-driven, not held back, so "turn them on" means inventing a source; the `brake_drivers.py`
sweep already showed no real presynaptic class can do it. (ii) The literature's reading of IN06B066
is an inhibition-stabilized network, where inhibition follows excitation rather than gating it, so
driving it externally models the circuit backwards. (iii) The muscle-group split above says these
cells are phase or gain machinery for DLM versus DVM, not a state switch, and a state switch built
out of them would be an invention wearing their names. If we ever do it, it should be labelled a
knob, not a cell.

**For option (b), removing drive that should not be there.** Ranked by how defensible each is:

1. **The cooling baseline.** Established physiology says the cooling cells' 95 Hz rest is the zero of
   a phasic code (Budelli et al., 2019). Feeding it through non-adapting synapses into a LIF is the
   single clearest artifact in the chain, and it is the largest rate-weighted input to DNb05
   (60,840 synapse-spikes/s/cell from VP3+_l2PN alone), which then feeds DNp31, IN12B015 and
   IN06B013. Fixing this is not a flight-state decision, it is a sensory-encoding correction, and it
   should be made whether or not the wings quiet down.
2. **The DNg33 latch.** A 2-cell pair with 1,496 reciprocal synapses and no adaptation is a numerical
   failure mode, the same one as the gnathal runaway. Fixing it (adaptation, or a refractory
   conductance, or short-term depression) is a fix to the engine, not to the fly.
3. **The flight gate proper, as a gain on the visual-to-DN synapses.** This is the one that is
   literature-shaped: Ache et al. (2019) found the visual responses of the landing DNs "severely
   attenuated during non-flight periods", by octopaminergic modulation in one case and by flight
   motor feedback in the other, and Maimon (2010) and Suver (2012) give the same sign for the whole
   visual pathway. So: a multiplicative gain (not a silencing lesion) on LPLC4, LLPC2, LPC2 and LC36
   inputs to DNp31 and DNb05, labelled `flight_state=0`, with the gain going to 1 when we ever have a
   flight state. That is a modulatory mechanism represented as a modulatory parameter, which is as
   honest as this engine allows.
4. **What not to do:** silence DNp31 or DNb05 as a default. DNb05 is *established* to be active in
   walking flies (Yang et al., 2024) and DNp31 has no recording at all; deleting a cell we know fires
   in life to fix a rate problem would be trading an honest artifact for a dishonest one. Lesions are
   fine as experiments, which is what `--silence` is for.

**The target number, for whatever we do.** "Not flying" is DLMn and DVMn at or near 0 Hz. "Flying"
is 5 to 20 Hz per motor neuron, splayed, not the wingbeat frequency, and not our 119 Hz. Any arm that
lands the power MNs at 40 Hz has not fixed it.

### Recommended experiments, in order, one change per run

1. **Control (no change).** Standing default, 30 s, 3 seeds, logging DNb05, DNg33, DNp31, IN19B040,
   IN19B043, IN19B067, IN06B066, IN03B089, IN11B013, IN12B015, IN06B013 and the five power MN types
   **separately** (DLM and DVM apart, so the muscle-group split is visible). This is the baseline all
   later arms diff against, and it is also the first run that reports DLM and DVM as different
   things.
2. **Cooling row at its true zero.** Drive TRN_VP3a at 0 Hz instead of 95 Hz, everything else on.
   Prediction: DNb05 falls hard, DNp31 and IN12B015 with it, power MNs drop. If they drop to single
   digits, the "flight gate" was a thermosensory baseline artifact all along and questions 1 and 3
   are moot.
3. **Adaptation instead of ablation on the same pathway.** Cooling row back at 95 Hz, but short-term
   depression or a spike-frequency adaptation term on VP3+_l2PN and VP5+VP3_l2PN outputs (or,
   cheaper, a scalar gain on those synapses tuned so DNb05 sits at a plausible tens of hertz). Same
   prediction as 2 but with a mechanism that survives a real cooling transient, which arm 2 does not.
4. **DNg33 de-latched.** Adaptation on DNg33 only, or the DNg33 to DNg33 weight scaled to 0.25, with
   arm 2 or 3 in place if either worked. Prediction: DNg33 falls from 200 Hz, IN19B040 falls from
   116 Hz, and the cord's gain-of-fifteen amplifier loses its core. Tests whether the amplifier is
   self-sustaining or descending-driven.
5. **The flight-state visual gain.** Scale LPLC4, LLPC2, LPC2 and LC36 synapses onto DNp31 and DNb05
   by 0.25, labelled `flight_state=0`, everything else on, with vision driven. This is the Ache 2019
   arm and the only one that claims to be the gate. Run it after 2 to 4 so its effect is measured
   against a chain that is no longer artifact-dominated.
6. **Only if 1 to 5 leave the wings up: the labelled brake state.** Drive IN06B066, IN03B089 and
   IN11B013 at 10 to 20 Hz as an explicit, documented, non-physiological "not flying" knob, and check
   two things: the power MNs go to 0, and the DLM and DVM groups fall differently (IN11B013 should
   take the DVMs down, IN06B066 and IN03B089 the DLMs). If they do not fall differently, the brake
   knob is not touching the circuit the way its wiring says it should.

---

## 5. Table queries, verbatim results

**DNp31 top 20 presynaptic types** (2 cells, 36,126 input synapses; NT is the majority consensus_nt
of the presynaptic type's cells):

| type | synapses | % | cells | transmitter |
|---|---|---|---|---|
| LLPC2 | 2,591 | 7.2 | 250 | acetylcholine |
| LPLC4 | 2,022 | 5.6 | 97 | acetylcholine |
| IB008 | 1,002 | 2.8 | 2 | **gaba** |
| AN07B004 | 901 | 2.5 | 2 | acetylcholine |
| PLP025 | 839 | 2.3 | 12 | **gaba** |
| LPC2 | 776 | 2.1 | 154 | acetylcholine |
| LC36 | 663 | 1.8 | 32 | acetylcholine |
| PS117_b | 658 | 1.8 | 2 | glutamate |
| AOTU023 | 636 | 1.8 | 2 | acetylcholine |
| vCal1 | 619 | 1.7 | 2 | glutamate |
| GNG544 | 599 | 1.7 | 2 | acetylcholine |
| PS042 | 595 | 1.6 | 6 | acetylcholine |
| GNG126 | 580 | 1.6 | 2 | **gaba** |
| vCal3 | 576 | 1.6 | 2 | acetylcholine |
| PS238 | 540 | 1.5 | 2 | acetylcholine |
| PVLP144 | 503 | 1.4 | 6 | acetylcholine |
| PS117_a | 474 | 1.3 | 2 | glutamate |
| vCal2 | 455 | 1.3 | 2 | glutamate |
| PS058 | 410 | 1.1 | 2 | acetylcholine |
| PS138 | 407 | 1.1 | 2 | **gaba** |

Visual projection neurons are 6,052 synapses, 16.8 %, of the top 20 alone (the 26 % figure in SEAM
counts all VPN types).

**Existence checks** (all present unless noted; cells, consensus transmitter, subclass):

- **DNp01** 2, acetylcholine, `lt`. **TTMn** 2, **glutamate**, `wm`. **STTMm** 4, `wm`.
- **PSI** 2, NT unclear, superclass `vnc_efferent`. **GFC1** 3, **GFC2** 10, **GFC3** 13, **GFC4** 8,
  all acetylcholine, `vnc_intrinsic`.
- **DNp02** 2 (`lt`), **DNp04** 2, **DNp06** 2 (`lt`), **DNp07** 2 (`xn`), **DNp10** 2 (`xl`),
  **DNp11** 2 (`xn`), all acetylcholine.
- **DNg02**: not present under that exact name. Present as **DNg02_a** (10), **_b** (5), **_c** (4),
  **_d** (2), **_e** (2), **_f** (2), **_g** (4): 29 cells, all acetylcholine. They make 1,930
  synapses onto the power MNs and 1,628 onto IN19B043 + IN19B067. This is the Namiki et al. (2022)
  flight motor DN population and it is in our brain.
- **Octopaminergic**: 101 cells with consensus_nt octopamine, including OA-VUMa1 to OA-VUMa6,
  OA-VPM3, OA-VPM4, OA-ASM1-3, OA-AL2i1-i4, and **mesVUM-MJ** (1 cell, `vnc_efferent`). mesVUM-MJ
  makes 1 synapse onto the power MNs; OA-VUMa1/a2/a3 make 0.
- **DNg27** 2 cells and **glutamate**, subclass `ut` (so the second "flight command shaped" DN in
  SEAM is inhibitory-or-glutamatergic, worth noting; it puts 684 synapses on the premotor pair, 519
  on the brakes, 225 on the power MNs). **DNa08** 2, acetylcholine, `wt`, 1,505 onto power MNs.
  **DNg100** 2, acetylcholine, `xl`. **DNae009** 2, acetylcholine, `xn`.

**mancType**: for every cell of IN19B043, IN19B067, IN19B040, IN06B066, IN03B089, IN11B013,
IN12B015, IN06B013 and the five power MN types, `mancType` is identical to `type` and `hemibrainType`
and `flywireType` are empty (they are cord cells, absent from both brain datasets). For the three
DNs: DNp31 and DNb05 have `hemibrainType` = `flywireType` = `mancType` = their own name; DNg33 has
`flywireType` = `mancType` = DNg33 and **no hemibrain name**. Transmitters: IN19B043 (9 cells),
IN19B067 (14), IN19B040 (4) all acetylcholine; IN06B066 (25), IN03B089 (18), IN11B013 (10),
IN12B015 (2), IN06B013 (4) all gaba. DNp31, DNb05, DNg33 all acetylcholine, 2 cells each.

**DNg33 recurrence**: no autapses. Body 13317 to 13442, 773 synapses; 13442 to 13317, 723. Total
1,496, 18.4 % of its 8,110 input synapses. **IN19B040**: also no autapses; the "self-excitation" is
12 all-to-all edges among its 4 cells, 54 to 101 synapses each, 901 total.

---

## Established / inferred / could not find

**Established (published):**
- DLM and DVM are asynchronous stretch-activated muscles; their motor neurons fire 5 to 20 Hz in
  flight, decoupled from the ~200 Hz wingbeat (Harcombe and Wyman 1977; Gordon and Dickinson 2006).
- The power motor neuron network is a CPG of electrically coupled motor neurons that desynchronizes
  and converts *unpatterned* premotor input into a stereotyped splayed firing sequence (Hürkey et
  al. 2023).
- Visual responses of the landing descending neurons DNp07 and DNp10 are severely attenuated outside
  flight; one by octopaminergic modulation, one probably by flight motor feedback (Ache et al. 2019).
- Flight raises the gain of visual motion processing, and octopaminergic neurons are necessary and
  sufficient for that boost (Maimon et al. 2010; Suver et al. 2012).
- Octopamine mediates flight initiation and maintenance, centrally and peripherally (Brembs et al.
  2007).
- The giant fiber (DNp01) drives TTMn and, via the PSI, the DLM motor neurons, for escape takeoff;
  these are largely electrical synapses (Hummon and Costello 1989; Card and Dickinson 2008).
- The tarsal reflex: tarsal contact inhibits wing movement, and takeoff removes it (Fraenkel;
  Binns 1977).
- DNb05 is active in walking flies and its right-left difference tracks rotational velocity during
  steering (Yang et al. 2024); it innervates both optic and olfactory glomeruli (Namiki et al. 2018).
- DNg02 is a population of at least 15 pairs that regulates wingbeat amplitude by a population code
  and responds to visual motion during flight (Namiki et al. 2022).
- Cooling cells are phasic: basal firing, transient response to cooling, return to baseline
  (Budelli et al. 2019).
- Hemilineage 19B is cholinergic; its sibling 19A is GABAergic (Lacin et al. 2019).
- In MANC, 42 tectular intrinsic neurons carry the bulk of power MN upstream connectivity, and
  DNa08 and DNp31 excite the IN06B066 group, possibly an inhibition-stabilized network limiting
  runaway excitation (Cheong et al. 2024/2025).
- LPLC2 is the ultra-selective loom detector; LC4 codes angular velocity and LPLC2 angular size for
  the giant fiber (Klapoetke et al. 2017). LPC/LLPC types are direction-tuned optic flow cells
  (Wu et al. 2016).

**Inferred (mine, from the connectome plus the above):**
- IN19B043 and IN19B067 are the excitatory wing power premotor, very likely members of the Tect IN
  set, but not individually named in print.
- LPLC4 is loom-plausible from its multi-layer lobula plate anatomy, not loom-demonstrated.
- The GABAergic inhibition of the power motor neurons is antagonist-specific (IN06B066 and IN03B089
  DLM-biased at about 6:1, IN11B013 DVM-biased at 46:1) while the excitation is common to both muscle
  groups.
- DNg33 is a latch in our engine because a 2-cell pair with 1,496 mutual synapses and no adaptation
  has no way not to be.
- The cooling cells' resting rate being transmitted as a DN command is a sensory-encoding artifact,
  not a fly state, and it should be corrected independently of the flight question.
- IN06B013 receiving the walking command and inhibiting the flight premotor is a plausible
  walking-versus-flight motif, unsupported by any publication.
- Our DLMn / DVMn at 85 to 119 Hz is not just "flying while standing"; it is 6 to 20 times the rate
  of an actual flying fly.

**Could not find:**
- Any recording, activation or silencing experiment on DNp31 specifically.
- Any functional work on DNg33 at all, and no hemibrain name for it.
- Any assignment of DNb05 to the thermosensory system, or any report of a VP3-driven descending
  neuron by name (the closest is DNp44 from VP4 dry PNs, Marin et al. 2020).
- Published tuning for LPLC4 or LC36.
- Any paper naming IN03B089, IN11B013, IN12B015, IN06B013 or IN19B040.
- Any identified Drosophila cell type carrying the tarsal-contact inhibition of flight.
- Any named VNC interneuron implementing walking-suppresses-flight in Drosophila.

---

## References

- Ache, J.M., Namiki, S., Lee, A., Branson, K., Card, G.M. (2019). State-dependent decoupling of
  sensory and motor circuits underlies behavioral flexibility in Drosophila. *Nature Neuroscience*
  22, 1132-1139. https://doi.org/10.1038/s41593-019-0413-4
- Binns, E.S. (1977). Take-off and the 'tarsal reflex' in *Aphis fabae*. *Physiological Entomology*
  2, 97-102. https://doi.org/10.1111/j.1365-3032.1977.tb00083.x
- Brembs, B., Christiansen, F., Pflüger, H.J., Duch, C. (2007). Flight initiation and maintenance
  deficits in flies with genetically altered biogenic amine levels. *Journal of Neuroscience* 27,
  11122-11131. https://doi.org/10.1523/JNEUROSCI.2704-07.2007
- Budelli, G., Ni, L., Berciu, C., van Giesen, L., Knecht, Z.A., Chang, E.C., Kaminski, B.,
  Silbering, A.F., Samuel, A., Klein, M., Benton, R., Nicastro, D., Garrity, P.A. (2019). Ionotropic
  receptors specify the morphogenesis of phasic sensors controlling rapid thermal preference in
  Drosophila. *Neuron* 101, 738-747. https://doi.org/10.1016/j.neuron.2018.12.022
- Card, G., Dickinson, M.H. (2008). Performance trade-offs in the flight initiation of Drosophila.
  *Journal of Experimental Biology* 211, 341-353. https://doi.org/10.1242/jeb.012682
- Cheong, H.S.J., Eichler, K., Stürner, T., et al. (2024/2025). Transforming descending input into
  behavior / Organization of circuits linking descending input to motor output in the Drosophila Male
  Adult Nerve Cord connectome. *eLife* 13:RP96084. https://doi.org/10.7554/eLife.96084
- Dombrovski, M., Peek, M.Y., Park, J.-Y., et al., Card, G.M. (2023). Synaptic gradients transform
  object location to action. *Nature* 613, 534-542. https://doi.org/10.1038/s41586-022-05562-8
- Frank, D.D., Jouandet, G.C., Kearney, P.J., Macpherson, L.J., Gallio, M. (2015). Temperature
  representation in the Drosophila brain. *Nature* 519, 358-361.
  https://doi.org/10.1038/nature14170
- Gallio, M., Ofstad, T.A., Macpherson, L.J., Wang, J.W., Zuker, C.S. (2011). The coding of
  temperature in the Drosophila brain. *Cell* 144, 614-624.
  https://doi.org/10.1016/j.cell.2011.01.028
- Gordon, S., Dickinson, M.H. (2006). Role of calcium in the regulation of mechanical power in insect
  flight. *PNAS* 103, 4311-4315. https://doi.org/10.1073/pnas.0510109103
- Harcombe, E.S., Wyman, R.J. (1977). Cyclic firing sequences of identified Drosophila flight
  motoneurons / Reciprocal excitation between identified flight motor neurons in Drosophila.
  *Journal of Comparative Physiology A* 123, 271-279 and 124, 1-9.
  https://doi.org/10.1007/BF00656881 and https://doi.org/10.1007/BF00605020
- Hummon, M.R., Costello, W.J. (1989). Giant fiber activation of flight muscles in Drosophila:
  asynchrony in latency of wing depressor fibers. *Journal of Neurobiology* 20, 593-602.
  https://doi.org/10.1002/neu.480200606
- Hürkey, S., Niemeyer, N., Schleimer, J.-H., Ryglewski, S., Schreiber, S., Duch, C. (2023). Gap
  junctions desynchronize a neural circuit to stabilize insect flight. *Nature* 618, 118-125.
  https://doi.org/10.1038/s41586-023-06099-0
- Klapoetke, N.C., Nern, A., Peek, M.Y., Rogers, E.M., Breads, P., Rubin, G.M., Reiser, M.B., Card,
  G.M. (2017). Ultra-selective looming detection from radial motion opponency. *Nature* 551, 237-241.
  https://doi.org/10.1038/nature24626
- Tanaka, R., Clark, D.A. (2022). Identifying inputs to visual projection neurons in Drosophila
  lobula by analyzing connectomic data. *eNeuro* 9(2), ENEURO.0053-22.2022.
  https://doi.org/10.1523/ENEURO.0053-22.2022
- Lacin, H., Chen, H.-M., Long, X., Singer, R.H., Lee, T., Truman, J.W. (2019). Neurotransmitter
  identity is acquired in a lineage-restricted manner in the Drosophila CNS. *eLife* 8:e43701.
  https://doi.org/10.7554/eLife.43701
- Lesser, E., Azevedo, A.W., Phelps, J.S., et al., Tuthill, J.C. (2024). Synaptic architecture of leg
  and wing premotor control networks in Drosophila. *Nature* 631, 369-377.
  https://doi.org/10.1038/s41586-024-07600-z
- Maimon, G., Straw, A.D., Dickinson, M.H. (2010). Active flight increases the gain of visual motion
  processing in Drosophila. *Nature Neuroscience* 13, 393-399. https://doi.org/10.1038/nn.2492
- Marin, E.C., Büld, L., Theiss, M., et al., Jefferis, G.S.X.E. (2020). Connectomics analysis reveals
  first-, second-, and third-order thermosensory and hygrosensory neurons in the adult Drosophila
  brain. *Current Biology* 30, 3167-3182. https://doi.org/10.1016/j.cub.2020.06.028
- Namiki, S., Dickinson, M.H., Wong, A.M., Korff, W., Card, G.M. (2018). The functional organization
  of descending sensory-motor pathways in Drosophila. *eLife* 7:e34272.
  https://doi.org/10.7554/eLife.34272
- Namiki, S., Ros, I.G., Morrow, C., Rowell, W.J., Card, G.M., Korff, W., Dickinson, M.H. (2022). A
  population of descending neurons that regulates the flight motor of Drosophila. *Current Biology*
  32, 1189-1196. https://doi.org/10.1016/j.cub.2022.01.008
- Suver, M.P., Mamiya, A., Dickinson, M.H. (2012). Octopamine neurons mediate flight-induced
  modulation of visual processing in Drosophila. *Current Biology* 22, 2294-2302.
  https://doi.org/10.1016/j.cub.2012.10.034
- von Reyn, C.R., Breads, P., Peek, M.Y., Zheng, G.Z., Williamson, W.R., Yee, A.L., Leonardo, A.,
  Card, G.M. (2014). A spike-timing mechanism for action selection. *Nature Neuroscience* 17,
  962-970. https://doi.org/10.1038/nn.3741
- Wu, M., Nern, A., Williamson, W.R., Morimoto, M.M., Reiser, M.B., Card, G.M., Rubin, G.M. (2016).
  Visual projection neurons in the Drosophila lobula link feature detection to distinct behavioral
  programs. *eLife* 5:e21022. https://doi.org/10.7554/eLife.21022
- Yang, H.H., Brezovec, B.E., Serratosa Capdevila, L., Vanderbeck, Q.X., Adachi, A., Mann, R.S.,
  Wilson, R.I. (2024). Fine-grained descending control of steering in walking Drosophila. *Cell* 187,
  6290-6308. https://doi.org/10.1016/j.cell.2024.08.033

*Citations where I could not open the primary source (Fraenkel's original tarsal reflex work, the
cockroach ground-contact papers, Harcombe and Wyman's two 1977 papers, Gordon and Dickinson 2006,
von Reyn 2014, Lesser 2024) are given from secondary quotation and should be checked
before they go into anything citable.*
