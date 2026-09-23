# walking: what the literature knows about a fly cord that steps

Written 2026-09-22 for the leg row (`docs/SEAM.md` "the legs, per muscle" onward; `docs/WALKING.md`). Does not repeat
`leg_motor.md` or `leg_biomech.md`. Marks: **(M)** measured in *Drosophila*; **(C)** measured in another insect, animal named;
**(E)** estimate; **(D)** derived from MaleCNS v1.0 in this project. "Not known" is said plainly where it is the answer.


## 0. the two papers that change the plan (read these first)

**Pugliese et al. 2026** (Pugliese SM, Chou GM, Abe ETT, Turcu D, Lancaster JK, Tuthill JC, Brunton BW, "Connectome simulations
identify a central pattern generator circuit for fly walking", bioRxiv 10.1101/2025.09.12.675944 v2, 2026-04-30; PMC13142387;
preprint, not peer reviewed; our note `docs/research/sources/pugliese_2026_connectome_cpg.md`). Read again today for the engine:

- **the model** is a rate model, not spiking: tau_i dr_i/dt = r_max tanh(a_i [r_max I_i + b sum_j w_ij r_j - theta_i]) - r_i,
  b = 0.03 per synapse, sign from predicted transmitter (ACh +, GABA/Glu -), 5-synapse floor, tau ~ N(20, 2) ms, r_max ~ N(200, 10) Hz,
  theta ~ N(7.5, 0.6), gain a ~ N(1, 0.1), **gain and threshold scaled per cell by neuron size** (volume / surface area), redrawn each
  of 1,024 replicates. the front-leg subnetwork: 1,318 DNs + 144 leg MNs + 3,142 premotor cells (MANC).
- **DNg100 (tonic step) drives rhythmic leg MN output in the full front-leg network**, in MANC, FANC, MaleCNS and BANC. rhythm ~7-15 Hz,
  rising with the drive; linearised minimal circuit ~14 Hz.
- **the rhythm generator is a three-cell loop**: E1 = **IN17A001** (cholinergic) -> E2 = **INXXX466** (cholinergic) -> I1 =
  **IN16B036** (GABA/Glu) -| E1. only E1 receives DNg100 directly. "oscillations arise entirely from synaptic connectivity" (one
  complex-conjugate eigenvalue pair); no intrinsic bursting, no adaptation. an alternative inhibitor I2 = IN19A007 serves in FANC.
  the loop was "necessary and sufficient" for rhythm across all six legs in four datasets.
- **what oscillated**: coxa promotor vs remotor, with a reliable within-leg phase offset. **"the main tibia flexors ... were either
  silent or non-rhythmic in our simulations."** that is this project's result at the knee, in their model too.
- **what did not**: left vs right promotors had no consistent phase; no tripod. "descending drive from DNg100 alone is sufficient to
  generate within-leg motor coordination but not realistic interleg coordination."
- **size normalisation was necessary**: "without adjusting a and theta for size, the network does not produce robust oscillations in
  response to DNg100 input." a uniform-threshold network (ours) is the configuration they say fails.
- **a LIF version** reproduced rhythmic spiking **on the three-cell circuit only** (tau_m 20 ms, refractory 2.2, delay 1.8, weight
  0.275 mV, threshold -45 mV: Shiu-family constants at the 0.275 weight). the whole-network LIF was not reported.
- validation: DNg100 activation in **headless** flies on a ball raises forward velocity and step frequency with light intensity;
  DNb08 in headless flies gives rhythmic front/mid-leg "searching" movements, better off the ball.

**Sapkal et al. 2026** (Sapkal N, Kumar DS, Sunke S, Mancini N, Pitchford J, Murakami K, Bidaye SS, "Central versus peripheral
neural control of a coordinated walking pattern in Drosophila", bioRxiv 10.64898/2026.04.29.721658 v2, 2026-05-05; preprint). from the
abstract: "each leg is governed by its own CPG module with an inherent cycle period that is unmasked when proprioceptive feedback is
reduced"; "contact driven load inputs and descending brain inputs are critical for coordinating the intra-leg movements"; "central
coupling pathways underlie inter-leg coordination"; co-stimulation of specific DNs speeds the rhythm; a connectome search gives
"putative neural-circuit motifs" (a five-neuron motif repeated per leg, directly upstream of the MNs, per The Transmitter's report,
2026-04). decapitated flies, on slippery surfaces, suspended and with legs amputated, walked (moved the stumps) under DN activation.

## 1. the Drosophila leg CPG: what is known

**the rhythm is central in the fly (M, 2024-2026).** until 2024 the fly evidence for a leg CPG was indirect (stick insect and locust
pilocarpine preparations carried the argument; Bässler & Büschges 1998, *Brain Res Rev* 27:65, (C)). it is now direct:

| source | preparation | DN | result |
|---|---|---|---|
| Bidaye et al. 2014, *Science* 344:97, DOI 10.1126/science.1249964 | decapitated | MDN | backward walking without the brain (M) |
| Feng et al. 2020, *Nat Commun* 11:6166, DOI 10.1038/s41467-020-19936-x | decapitated, tethered | MDN | backward stepping; hind legs carry it; amputating legs *raises* the remaining legs' step frequency; two VNC effectors: LBL40 (T3; hind tibia flexion in stance via the tibia-reductor MN) and LUL130 (segmental; leg lift, swing onset), called possible CPG members, (M) |
| Sapkal et al. 2024, *Nature* 634:191, DOI 10.1038/s41586-024-07854-7 | decapitated | BDN2 (= DNg100), oDN1 (= DNg97) | "even decapitated oDN1 and BDN2 activated flies initiated robust forward walking"; BDN2 silencing lowers forward velocity; BDN2 activity tracks forward, not angular, velocity (M) |
| Braun et al. 2024, *Nature* 630:686, DOI 10.1038/s41586-024-07523-9 | decapitated | DNp09, MDN, aDN2 | "DNp09 stimulation in headless animals did not elicit forwards walking"; MDN headless walks backward (P = 0.265 vs intact); DNp09 and aDN2 need the brain's DN network (M) |
| Pugliese et al. 2026 (§0) | decapitated, ball | DNg100, DNb08 | DNg100: velocity and step frequency rise with light; DNb08: rhythmic "searching" of front/mid legs (M) |
| **Sapkal et al. 2026** (§0) | decapitated; ball / slippery glass / suspended in air / legs amputated mid-femur / FeCO silenced (iav>GtACR1) | DNg100, DNg97, MDN, co-activations | see below (M) |

**Sapkal 2026, the deafferentation result** (bioRxiv 10.64898/2026.04.29.721658; details as extracted from the v1 full text by a
fetch tool; figure-level numbers not checked by eye, treat single numbers as approximate):

- DNg100 in the headless fly drives stepping on all six legs in every condition. **air-stepping (no load: the campaniform sensilla see
  nothing) is faster, ~11 Hz, and more tripod-like (tripod coordination strength ~0.8, the highest of the four conditions)** than
  walking on the ball; the amputated stumps (FeCO gone; only the proximal hair plates left, which the authors state) still oscillate,
  a little slower; silencing the FeCO in intact legs drops air-stepping to the amputated frequency. so **the FeCO tunes the frequency
  and the coordination; it does not make the rhythm.**
- left-right antiphase (180 deg) on all leg pairs under DNg100 "across all conditions", including amputated. ipsilateral neighbours
  antiphase, tripod partners in phase. **the tripod is central.** under MDN: no left-right coupling in any pair.
- without load, the joint traces become symmetric, near-sinusoidal, duty cycle ~0.5; with load, long stance / short swing. **load
  shapes the step's asymmetry; the alternation is there without it.** the order in which joints move is conserved across conditions;
  FTi oscillation persists with the proximal front-leg joints glued.
- DNg100 + DNg97 co-activation raises velocity and step frequency toward BPN levels; + DNg75 raises step frequency; + DNg55 degrades
  coordination; + DNg16 no speed-up.
- coupling pathways named: 19B commissural -> 19A local for left-right alternation; 19A intersegmental -> 19A local for ipsilateral
  antiphase.
- **the connectome search** (MANC, shared outputs of DNg100 and DNg97 in the front neuromeres, replicated in two more datasets) gives a
  five-cell motif per leg neuromere, recurrently connected (5-481 synapses per edge), downstream of proprioceptors and directly upstream
  of leg MNs (tibia, coxa, trochanter): **IN17A001, IN03A006, INXXX464, IN12B003, IN09A002**; an expanded motif adds INXXX466 and
  IN19A007. it shares IN17A001 / IN03A006 / INXXX464 / INXXX466 / IN19A007 with Pugliese's candidates; IN12B003 and IN09A002 are new.
  IN12B003 is described as morphologically like the stick insect's non-spiking inhibitory "neuron-i4" and the cockroach's "neuron-i".

**what this means for the leg row (D).** two cells the row has already met are in the published motif: **IN09A002**, the GABAergic
flexor inhibitor that DNg100 excites directly (+1,026 synapses) and that runs tonically at 50-60 Hz in every arm, and **IN12B003**,
an inhibitor of the flexor exciter IN03A004. in the fly these are rhythm-generator members; in the LIF they are a tonic brake. and
the row's working reading since 09-21 ("the rhythm in life is closed through the leg and shaped from above"; `SEAM.md`, "the switch,
at the end of the hunt") is **contradicted by Sapkal 2026**: DNg100 makes a headless fly with no load input and no FeCO step in a
tripod. the rhythm and the tripod are in the cord. a cord model that needs the body to alternate is missing something the cord has.

**citation fixes.** `WALKING.md` credits "Bidaye 2020, on the same neuron we drive, DNg100" for headless walking. Bidaye et al. 2020
(*Neuron* 108:469, DOI 10.1016/j.neuron.2020.07.032) is the P9 / BPN paper; its bioRxiv v1 (10.1101/798439) has no headless
experiment. the headless BDN2 (DNg100) result is **Sapkal et al. 2024** (*Nature*), with frequency and coordination in **Sapkal et
al. 2026**. Chen et al. 2018 (*Nat Commun* 9:4390, DOI 10.1038/s41467-018-06857-z) is the VNC two-photon imaging method in walking
tethered flies, not a headless study.

**what the literature does not know.** no adult fly leg MN or premotor IN has been recorded intracellularly during headless DN-driven
stepping. no one has shown the five-cell motif or the three-cell loop is *necessary* in the animal (Sapkal and Pugliese both call
them putative). the DN rate that produces walking is unknown in spikes/s: all activation is optogenetic, graded by light.

## 2. graded premotor cells, and which hemilineages are CPG candidates

**measured in the fly (M), all whole-cell, all front leg, all at rest or under passive movement:**

| cell | hemilineage, transmitter | spikes? | source |
|---|---|---|---|
| 13Bα | 13B, GABA | **no detectable action potentials**; Vm is a tonic, non-adapting, hysteretic readout of FTi angle; TTX abolishes, MLA / atropine only dent it (gap junctions onto claw axons suggested) | Agrawal et al. 2020, *eLife* 9:e60299, DOI 10.7554/eLife.60299 |
| 10Bα | 10B, ACh | "no reliable spikes (occasional spike-like events)"; mixed chemical + electrical input from club (Chen 2021) | Agrawal 2020; Chen et al. 2021, *Curr Biol* 31:5163, DOI 10.1016/j.cub.2021.09.035 |
| 9Aα, 9Aα2 | 9A, GABA | spiking | Agrawal 2020 |
| leg MNs (tibia flexor fast / intermediate / slow) | | spiking; see §5 | Azevedo et al. 2020, *eLife* 9:e56754 |

that is the whole list. **no fly recording exists for 13A, 19A, 21A, 20A/22A, 03A, 12B, 16B, 17A, 14A premotor cells**: spiking or
graded is unknown for every cell the leg row's switch hunt touched. the claim "non-spiking local interneurons are the substrate of insect
leg pattern generation" is stick insect and locust (Büschges 1995, *J Neurobiol* 27:488, DOI 10.1002/neu.480270405; Burrows 1996, *The Neurobiology of an
Insect Brain*, OUP) **(C)**. Pugliese 2026 state "many neurons in the insect VNC, including premotor neurons active during walking, are
nonspiking" without a fly citation. Sapkal 2026 note only that IN12B003 *looks like* the stick insect's non-spiking i4. the one fly
cell known to be graded (13Bα) is a sensory relay onto a posture reflex, not a rhythm cell. **(E):** the row's graded sweep chose 13A /
13B / 21A as a guess; the published rhythm candidates are 17A, 03A, 12B, 09A, 16B, 19A and the unlabelled INXXX466 / INXXX464.

**CPG candidates named in the connectome papers.** Cheong et al. (*eLife* 13:RP96084) and Lesser et al. 2024 (*Nature* 631:369, DOI
10.1038/s41586-024-07600-z) name no rhythm generator; Lesser's result is module structure and size-proportional premotor weights (§5).
Takemura 2024 and Azevedo 2024 are dataset papers. the named candidates are only:
- Pugliese 2026: **IN17A001 -> INXXX466 -> IN16B036 -| IN17A001** (alt. inhibitor IN19A007).
- Sapkal 2026: **IN17A001, IN03A006, INXXX464, IN12B003, IN09A002** (+ INXXX466, IN19A007); left-right via 19B commissural -> 19A
  local; ipsilateral neighbours via 19A intersegmental -> 19A local.
- 13A / 13B: Syed, Ravbar & Simpson 2026 (*eLife* 14:RP106446): pulsed 13A activation drives rhythmic leg movement near 7 Hz;
  sustained activation locks the leg in flexion or extension; 13B acts mostly by disinhibiting 13A. a grooming paper; it shows 13A
  can pace a leg when driven phasically, not that it generates the rhythm (already in `leg_motor.md` §5).
- Feng 2020 (MDN): LBL40 and LUL130, "possible CPG components".
- Harris et al. 2015 (*eLife* 4:e04493): hemilineage-wide activation in headless flies gives hemilineage-specific leg movements;
  semi-autonomous patterned output per hemilineage.

**(D) for this project:** the leg row's "flexor-side / extensor-side" pools (IN21A004, IN03A004, IN20A.22A009, IN03A031 against
IN21A002, IN16B016, IN09A002, IN13A...) are the tibia's *reflex / module* premotor cells. the published rhythm cells sit one layer up
and project to several modules. the first thing to read in the male is what IN17A001, INXXX466, INXXX464, IN16B036, IN03A006, IN12B003
and IN19A007 do in the cord under DNg100: rates, and whether any of them ever changes.

## 3. gap junctions in the leg circuits

- **no connectome has them.** MANC, FANC, MaleCNS and BANC are chemical-synapse maps; FANC's authors state its resolution could not
  resolve gap junctions (Chen 2021; Lee 2025). Marin 2024 note shakB is expressed through the VNC but gap junctions were not annotated.
- **anatomy (M):** Ammer, Vieira, Fendl & Borst 2022, *Curr Biol* 32:2022, DOI 10.1016/j.cub.2022.03.040: immunohistochemical map
  of all innexins in the fly CNS; ShakB is the most widely expressed neuronal innexin, present through the VNC neuropils. cell-level
  assignment in the leg neuropil: not done.
- **function in leg circuits (M), fragments only:** mixed electrical + chemical transmission club -> 10Bα (MLA reduces but does not
  abolish, and slows the rise; Chen 2021); 13Bα's claw drive survives nicotinic and muscarinic block, gap junctions suggested
  (Agrawal 2020); club -> 9Bα purely chemical (Chen 2021). the giant fibre -> TTMn (jump) and -> PSI are the classical shakB synapses
  (Phelan et al. 1996, *J Neurosci* 16:1101), outside walking.
- **the closest CPG evidence is larval (M, different circuit):** Matsunaga et al. 2017, *J Neurosci* 37:2045, DOI
  10.1523/JNEUROSCI.1453-16.2017: motor neurons feed back onto the crawling CPG through gap junctions (shakB in MNs, ogre in
  interneurons); silencing MNs in one segment slows the fictive wave, activating them speeds it, in a deafferented cord.
- **electrical coupling among adult leg MNs or premotor INs: not measured. no quantitative estimate exists** (no count, no coupling
  coefficient, no list of coupled types). anything the project adds is (E) in both location and strength.
- **(E) what it would do here:** coupling within a pool synchronises it and shares its drive (it would help a silent pool that has one
  active member), and MN -> premotor coupling (the larval result) is a feedback route the chemical table lacks. neither is a switch by
  itself; both change which side wins a winner-take-all.

## 4. neuromodulation of walking

- **serotonin (M):** Howard et al. 2019, *Curr Biol* 29:4218 (PMID 31786064; preprint DOI 10.1101/753624): serotonergic VNC neurons
  (5-HT_VNC) slow walking in every context tested; silencing them makes flies walk faster, before and after a startle; all five fly
  5-HT receptors are GPCRs. a brake on speed, not a gate on rhythm.
- **octopamine / tyramine (M):** Tβh mutants have flight-initiation and maintenance deficits (Brembs et al. 2007, *J Neurosci*
  27:11122, DOI 10.1523/JNEUROSCI.2704-07.2007); adult walking in them is not reported as abolished. octopaminergic descending neurons
  (Babski et al. 2024, *Heliyon*, DOI 10.1016/j.heliyon.2024.e29952): ~15 OA-DNs in three clusters, recorded in behaving flies; VPM1 /
  VPM2 fire tonic single spikes that rise during locomotor bouts; the VUMd cells fire at 4.1 ± 3.1 Hz, "unchanged during fly
  locomotion bouts"; VL1 (DNd02) / VL2 (DNd03) rise with leg movement; VPM1, VL1, VL2 arborise near the leg neuropils. **these are cut
  in a headless fly, and the headless fly still walks under DNg100 (§1).** larval: ~40 VNC Tdc2 cells suffice to trigger crawling;
  hyperpolarising Tdc2 cells suppresses or abolishes fictive rhythms (larval; bioRxiv 10.64898/2026.08.04.742787, *J Neurophysiol*
  2026, not read beyond the abstract).
- **muscarinic (C):** the classical insect fictive-walking preparation is pilocarpine (muscarinic agonist) on the deafferented cord
  (Büschges 1995; Bässler & Büschges 1998, *Brain Res Rev* 27:65, DOI 10.1016/S0165-0173(98)00006-X). in the fly, acetylcholine acts on
  both nicotinic and muscarinic receptors (mAChR-A excitatory, mAChR-B inhibitory, both slow). every connectome model, this one and
  Pugliese's, treats ACh as fast excitation.
- **is a modulatory tone required? not in any way the literature can show.** the headless fly (no brain OA-DNs, no brain 5-HT or DA
  descending cells) steps in a tripod under DNg100 alone (Sapkal 2024, 2026). what the headless fly keeps and the model lacks is the
  cord's own aminergic cells (VNC VUM / Tdc2, 5-HT_VNC) and slow cholinergic signalling; no one has silenced them during headless
  DN-driven walking. (E): modulation is unlikely to be the missing switch, because Pugliese's rate model steps (within-leg) with none.
- **the sign of glutamate** (not modulation, but a similar silent assumption): glutamate is inhibitory at GluClα synapses and
  excitatory at ionotropic GluR / NMDA synapses in the fly; the hemilineage rule "21A / 16B / 14A = inhibitory" (Lacin et al. 2019,
  *eLife* 8:e43701) is a prior, not a per-synapse fact. both the row and Pugliese use it; Pugliese's I1 (IN16B036) is glutamatergic.

## 5. motor neuron intrinsic properties

**measured (M), front-leg tibia flexor MNs, Azevedo et al. 2020 (*eLife* 9:e56754):**

| | fast | intermediate | slow |
|---|---|---|---|
| resting Vm | **-68 mV** | **-60 mV** | **-48 mV** |
| input resistance | 150 MΩ (80-190) | 300 MΩ (190-440) | 700 MΩ (420-900) |
| spontaneous rate, fly still | 0 | 0 | ~30 Hz (28 Hz, 486 MΩ, in one line) |
| somatic current injection | does not reliably evoke spikes (soma electrically remote from the spike initiation zone) | same | 100-150 Hz at +25 to +100 pA |

- **the slow MN rests ~20 mV more depolarised than the fast one and fires tonically with no command.** a uniform-rest,
  uniform-threshold LIF gives every MN the same 7 mV to threshold, so the small cells (the row's 93 cells with ~26 excitatory synapses
  each) cannot fire. **the "slow units are not in the file" finding (`SEAM.md`, the night's wall) is at least partly an engine
  property: in life, the slow units are the ones that need almost no synaptic input.** the resting potentials are measured; the
  thresholds are not (E), so the size rule on rest or threshold is a fitted scaling.
- **persistent inward currents, plateaus, bistability in adult fly leg MNs: not measured.** no voltage-clamp study of adult leg MNs
  exists that I can find. larval MNs carry persistent Na (para) and I_h; adult flight MN5 has been characterised for K currents
  (Duch lab) but not for plateaus relevant to walking. (E).
- **does the LIF misrepresent them in a way that matters for alternation?** the MN is the readout, not the oscillator (§1, §7): the
  rhythm is premotor in both the fly and Pugliese's model. what matters for the row: (a) the size-graded excitability, which sets which
  units carry standing tonus and which fire on the first premotor spikes (Lesser 2024: premotor weights proportional to MN size, so a
  uniform threshold turns the size principle into "big cells only"); (b) Pugliese found size-scaled gain and threshold necessary for
  the *premotor* network to oscillate. both are the same engine change.

## 6. the reflex reversal, and the claw result

**in the fly (M):** the resistance reflex is measured: passive tibia extension gives EPSPs in all three tibia flexor MN classes,
largest in slow (Azevedo 2020); extension-claw -> 13Bα activation gives FTi **flexion** in headless flies (Agrawal 2020); the wiring
rule (Lee et al. 2025, *Nat Commun* 16:4105, DOI 10.1038/s41467-025-59302-3): **flexion-sensing afferents excite tibia extensors
and inhibit flexors; extension-sensing afferents do the reverse.** reflex reversal: Azevedo 2020 saw it "occasionally" in the
tethered fly, not quantified. hook afferents (movement) are presynaptically suppressed during walking and grooming, via 9A, fed
forward from descending neurons (Dallmann et al. 2025, *Nature* 647:445, DOI 10.1038/s41586-025-09554-2); claw is not. **a Drosophila
reflex reversal has not been demonstrated.**

**in the stick insect (C):** the "active reaction" is movement-dependent: fCO signals of *flexion* during active flexion assist
flexion, then at a flexed position switch to extensor excitation (Bässler 1976-1988; Bässler & Büschges 1998); it depends on load
(Akay & Büschges 2006, *J Neurophysiol* 96:3532, DOI 10.1152/jn.00625.2006) and on the task, present for forward and absent for backward
walking, set by intersegmental signals (Hellekes et al. 2012, *J Neurophysiol* 107:239, DOI 10.1152/jn.00718.2011). it is carried by
velocity signals and non-spiking interneurons, and it needs the walking motor state, which is what the model lacks.

**is "claw extension answered with more extension = the assistance reflex" defensible? no, for three reasons.**
1. the stimulus: a claw held at a constant rate is a *position* signal with no movement; the active reaction is a response to
   movement during an ongoing active movement, and it hands over at a position threshold. a steady position answered with a steady
   posture is a static gain, not a reversal.
2. the fly's measured wiring says the opposite sign (Lee 2025; Azevedo 2020). an extension signal should excite flexors.
3. **(D): the claw labels are uncertain, and the direct wiring says they may be inverted.** Marin et al. 2024 (*eLife* 13:RP97766)
   name SNpp50 and SNpp51 only as "claw"; the extension / flexion tuning in `leg_biomech_parts/E_table_male.md` is this project's
   assignment, not Marin's. checked today in MaleCNS v1.0 (minconf 0.5, synapses summed over the type):

   | | SNpp50 (62 cells, labelled extension) | SNpp51 (32, labelled flexion) |
   |---|---|---|
   | -> Ti extensor MN, direct | **470** | 5 |
   | -> Ti flexor MN / acc. flexor MN, direct | 18 / 78 | **360** / 59 |
   | -> IN21A004 / IN03A004 (flexor exciters) | 8 / small | **577 / 439** |
   | -> IN13A002 (flexor inhibitor) | **4,612** | small |
   | -> 13B cells, all | **2,280** | 511 |

   by the MN-level rule (Lee 2025; Azevedo 2020: extension sensed -> flexors excited), **SNpp51 behaves as the extension-sensing claw
   and SNpp50 as the flexion-sensing one**, the reverse of the project's labels. against that, SNpp50 feeds 13B four times more than
   SNpp51 does, and Agrawal's 13Bα is an extension-claw target. so: two indicators disagree; the MN-level one is the functional one for
   a reflex model. (and `SEAM.md` "the command as a population" says SNpp50 sits on IN21A004 with 576 synapses; the file says that is
   SNpp51, as the earlier paragraph there had it.) if the labels are swapped, (a) the claw arms of 09-21 drove a flexion signal and got
   extension: the resistance reflex, correct; (b) the body loop has run **positive** position feedback at every knee, and its "flexors
   wake with the knees flexed" is assistance, not resistance. resolving it: match SNpp50 / SNpp51 to FANC's morphologically identified
   claw-extension / claw-flexion axons (Lee 2025 reconstructed ~50 % of each subtype in T1L), or to Mamiya 2023's position-along-femur
   map. until then, run the loop both ways and label it.

## 7. models that step, and what each added to the wiring

| model | wiring | neuron | what was added | result |
|---|---|---|---|---|
| **Pugliese et al. 2026** | MANC / FANC / MaleCNS / BANC front-leg subnetworks, signed by predicted transmitter, 5-synapse floor | rate, tanh, tau 20 ms | **per-cell gain and threshold scaled by neuron size** (stated necessary); per-cell random parameters (gain, threshold, r_max, tau; ~10 % spread) redrawn per replicate; a tonic DNg100 input | within-leg rhythm 7-15 Hz, coxa promotor / remotor phase-offset; tibia flexors silent or arrhythmic; no left-right or tripod coupling; LIF (0.275 mV, tau 20, ref 2.2, delay 1.8) reproduces the 3-cell loop's rhythm |
| Sapkal et al. 2026 | MANC + two datasets, searched not simulated | none | nothing (a motif search constrained by DN co-targets) | a candidate 5-cell motif per leg; 19A / 19B coupling candidates |
| NeuroMechFly v1 / v2 (Lobato-Rios et al. 2022, *Nat Methods* 19:620, DOI 10.1038/s41592-022-01466-7; Wang-Chen et al. 2024, *Nat Methods*, DOI 10.1038/s41592-024-02497-y) | **none** | abstract coupled phase oscillators (salamander-derived), Walknet-type rules, or hybrid | the oscillators are the CPG; intrinsic frequency constrained to 6-10 Hz (v1) | tripod walking in the body; no connectome on the motor side |
| Goldsmith, Szczecinski & Quinn 2020, *Bioinspir Biomim* 15:065003, DOI 10.1088/1748-3190/ab9e52 (Drosophibot); Szczecinski, Hunt & Quinn 2017, *Front Neurorobot* 11:37 | hand-built from insect anatomy, not a connectome | non-spiking leaky integrators; spiking sensory and MNs | per-joint CPGs and reflex networks designed by function; the lineage's CPG unit is a half-centre of non-spiking cells with a persistent-sodium-type slow current (Daun-Gruhn, Rubin & Rybak 2009, *J Comput Neurosci* 27:3, DOI 10.1007/s10827-008-0124-4) (E: lineage recalled, the 2020 paper's CPG equations not re-read) | robot and simulation walking; not connectome-derived |
| Jin, Zhu, Zhang & Sui 2026, arXiv 2602.17997 | FlyWire brain graph | graph model | a **learned decoder** from brain to flybody | locomotion by training; no MN identity (already in `leg_biomech.md` §D) |
| NeuroMechFly + flyvis, flybody (Vaxenburg et al. 2025) | vision only / none on the motor side | | trained controllers | not comparable |

**no published model steps a six-legged body from connectome-derived VNC wiring alone.** the one connectome motor model that gets rhythm
(Pugliese) gets it within a leg, in a rate model with size-scaled excitability, and does not get inter-leg coordination; its authors
name proprioceptive feedback, biomechanical coupling or other pathways as the missing piece, and Sapkal 2026 shows the animal has the
coupling centrally (19A / 19B).

## 8. what to build next, ranked, and what a fair negative would need

every item is on the headless cord first (5 s of wall clock per 30 s arm), DNg100 at the record's dose, the same scoring.

1. **read the published rhythm cells in the male cord (a table query and one logged arm; no engine change).** the eight cells:
   IN17A001, INXXX466, IN16B036, IN19A007 (Pugliese); IN03A006, INXXX464, IN12B003, IN09A002 (Sapkal). their synapse counts along the
   loop (DNg100 -> IN17A001; IN17A001 -> INXXX466 -> IN16B036 -| IN17A001), their rates and ISI structure under DNg100, and which MNs
   they reach. Pugliese used MaleCNS and found the loop there, so the cells exist in this file (D, to confirm by name). **prediction
   (E): IN09A002 at 50-60 Hz tonic is the loop's inhibition winning outright, and IN17A001 is silent or tonic.** also rescore the coxa:
   the row's only gait-shaped number is coxal antagonists anti-correlated at a 30 ms lag (-0.16 to -0.41); a 14 Hz within-leg rhythm
   puts antiphase at ~35 ms. compute the promotor and remotor pools' autocorrelation at 50-150 ms lags and the spectrum at 1 ms bins
   before calling "no rhythm" (the 10 ms frame is a seventh of a 70 ms cycle; the "beat" measure has a known tonic-cell blind spot).
   **(D, checked today against `data/*male-cns-v1.0*.feather`, minconf 0.5, synapses summed over all cells of each type):** all
   eight types exist, **6 cells each** (one per hemineuromere); transmitters as published (IN17A001, INXXX466, INXXX464, IN03A006
   ACh; IN16B036 Glu; IN19A007, IN12B003, IN09A002 GABA). the loop: DNg100 -> IN17A001 **818**; IN17A001 -> INXXX466 **2,733**;
   INXXX466 -> IN16B036 **445** (the weak edge); IN16B036 -| IN17A001 **3,705**; IN16B036 -| INXXX466 1,261. the second ring:
   INXXX464 <-> IN19A007 2,193 / 2,156; IN19A007 -| IN17A001 2,046; INXXX464 -> IN17A001 1,677; IN03A006 -> INXXX464 1,685.
   **IN09A002 is the motif's sink**: IN16B036 -| 1,397, IN19A007 -| 1,345, IN17A001 -> 888, and **DNg100 -> IN09A002 1,026, more than
   DNg100 -> IN17A001 (818)**; IN09A002 sends almost nothing back into the motif (<= 24 per edge). so under a tonic DNg100 the command
   feeds the motif's output inhibitor harder than its rhythm cell, and at one uniform weight the loop's weak edge (445) has to carry the
   ring. whether it rings at 0.185 mV is a logged arm away.
2. **a positive control: Pugliese's rate model on this project's cord table** (their equation and parameter distributions, the
   5-synapse floor, size from MaleCNS volume or surface area, a tonic DNg100 input). if it oscillates on our file, the wiring is
   cleared and the LIF is the variable; if it does not, the difference is in our cut or our signs, and that is found before any engine
   change. a day of code (E); the published parameters are enough to write it.
3. **size-scaled excitability in the LIF** (engine change, labelled): per-cell threshold (or synaptic gain, the Rin equivalent)
   scaled by cell size, the way Pugliese scale a and theta. sources: Pugliese 2026 (necessary for rhythm in their network); Azevedo 2020
   (MN rest -68 / -60 / -48 mV and Rin 150 / 300 / 700 MΩ across fast / intermediate / slow); Lesser 2024 (premotor weights proportional
   to MN size, which only yields ordered recruitment if excitability falls with size). it also bears on the standing tonus: the small
   MNs that "have no wiring" are the ones that in life sit near threshold. constants (E); sweep the exponent. add Pugliese's ~10 %
   per-cell heterogeneity at the same time only as a second arm, one variable each.
4. **resolve the claw labels before more loop arms** (encoder, not engine): §6. if SNpp50 is flexion-tuned, the body loop has run
   positive position feedback at every knee.
5. **the loop cells at Pugliese's LIF weight (0.275 mV) alone**, the rest of the cord at 0.185: the row's 0.275 arm ran away because
   it was global. a targeted weight is a stand-in with a source (their LIF), and says whether the loop can ring inside this engine.
6. **graded units on named cells, not hemilineages**: IN12B003 (Sapkal's putative non-spiking i4 homologue) and the Pugliese / Sapkal
   inhibitors. the 13A / 13B / 21A sweep had no fly source for which cells are graded; this one has a weak one. low priority.
7. **gap junctions: not yet.** no location, no strength, no count exists for fly leg circuits (§3); any arm would be a guess twice.
8. **neuromodulation: no.** the headless fly walks without the brain's modulatory DNs (§4); Pugliese steps without any.

**inter-leg coordination** is a separate question: Pugliese's model does not couple legs; Sapkal's 19B -> 19A / 19A -> 19A pathways are
the named candidates, and the row's cord already includes them. do not expect a tripod from items 1-3; expect, at best, a within-leg
coxa rhythm.

**a fair "this wiring cannot walk in a LIF" needs, at minimum:**
- the positive control (item 2): the same table oscillates in Pugliese's rate model. without it, a LIF null says nothing about the
  wiring, only about the engine. with it, the conclusion is about the neuron model.
- size-scaled excitability and per-cell heterogeneity tried (items 3, 5), since the only published connectome rhythm depends on them.
- the published loop cells read by name (item 1), with a mechanism for why they do not oscillate (e.g. the inhibitor saturates; the
  loop gain is below the ring threshold at one uniform weight).
- a rhythm measure validated on a planted 10-15 Hz oscillation in the same pools, at 1 ms bins, reading coxa promotor / remotor (where
  the published rhythm lives), not the tibia flexors (which are silent in the published model too).
- several seeds, the DNg100 dose swept (Pugliese: frequency rises with drive), and the 0.1 ms tick on the final arms.
- stated scope: "a LIF at Shiu 2024's uniform constants", not "a LIF", and not "the wiring". the literature today says the wiring
  generates a within-leg rhythm under DNg100 in a rate model (Pugliese 2026) and a tripod in the animal without leg feedback (Sapkal
  2026); the burden is on the engine.

## sources read for this review, not previously in `docs/research/sources/`

Sapkal et al. 2026 bioRxiv 10.64898/2026.04.29.721658 (v1 full text, by fetch tool; abstract via bioRxiv API); Sapkal et al. 2024
*Nature* 634:191 (PMC11446846); Braun et al. 2024 *Nature* 630:686 (PMC11186778); Feng et al. 2020 *Nat Commun* 11:6166 (PMC7710706);
Babski et al. 2024 *Heliyon* (PMC11064449); Howard et al. 2019 *Curr Biol* 29:4218; Matsunaga et al. 2017 *J Neurosci* 37:2045;
Ammer et al. 2022 *Curr Biol* (abstract level); Pugliese et al. 2026 (re-read for the model equations and the LIF). DOIs of the stick
insect papers checked on Crossref. numbers marked as from the fetch tool were not checked against figures.

## second pass (2026-09-22 evening; against `SEAM.md` "the literature review" to the end and `rate_model_control.md`)

new source read tonight: **Pugliese et al.'s code and data** (github.com/smpuglie/Pugliese_cpg_2025; simulation data on Zenodo 22260924).
their LIF (`src/lif_model/lif_dynamics.py`) and its input (`notebooks/Extended Data Figure 4.ipynb`) were run here, unmodified and in
variants (scratchpad, not in the project).

### A. what their spiking version of the circuit actually is, and what frequency it gives

- **the circuit simulated:** five cells from one hemisegment (MANC T1L, their 2024-11 table): BDN2 (DNg100), IN17A001 (E1), IN15A001
  (E2; INXXX466 in current naming), IN16B007 (I1; IN16B036 now), one tergopleural promotor MN. per-cell synapse counts, unnormalised:
  DN -> E1 187, E1 -> E2 539, **E2 -> I1 71** (the weak edge, as in ours), I1 -| E1 531. nothing else: no surround.
- **their constants:** rest and reset -52 mV, threshold -45 (7 mV), tau_m 20 ms, tau_syn 5 ms, **0.275 mV per synapse (x1.49 ours)**,
  delay 1.8 ms, refractory 2.2 ms, dt 10 us. the DN is driven by a constant 0.15 nA into 10 nS (15 mV above rest); it fires 68 Hz.
- **one non-standard line:** a cell's accumulated synaptic current is zeroed at each of its own spikes (`synaptic_input[current_spikes]
  = 0`). our engine does not do this. it matters at 0.275 (without it E1 goes tonic and only E2 bursts, at 19 Hz); at 0.185 without it
  the loop rings at 13.5 Hz again.
- **measured here (I1 fires one spike per cycle, so its interval is the period):**

  | their LIF, isolated loop | cycle |
  |---|---|
  | as published | **13.5 Hz** (cv 0.00); E1 41 Hz in bursts of 3, I1 13 Hz |
  | I1 -| E1 x0.5 / x1.5 / x2 | 16.9 / 11.3 / 11.3 Hz |
  | DN -> E1 x2 / x3; DN current x2 | 16.9 / 16.9; 12.7 Hz |
  | tau_syn 10 / 20 ms | 16.9 / 18.8 Hz |
  | delay 0.8 ms (for 1.8) | 13.5 Hz; delay 4 ms breaks the burst structure (tonic) |
  | **every loop synapse x3** | **26.1 Hz** (cv 0.51) |
  | loop x3, DN current x2.7 | 45 Hz, irregular |

- so **(question 2): their spiking circuit rings at ~13.5 Hz with the standard 1.8 ms delay**, in the band with no delay stand-in. its
  period is set by I1's single-spike IPSP (531 synapses x 0.275 mV, a ~146 mV-equivalent kick filtered by tau_syn and tau_m) and E1's
  recovery from it, not by conduction. **at x3 their own LIF rings at 26 Hz, the row's 25.0 Hz.** the row's fast ring is what this
  circuit does at triple gain, and the 12 ms delay is compensating for the gain, not for anything missing from the loop's timing.
  frequency falls with the inhibitory edge's strength and rises with total loop gain and drive. (their figure's frequency is not
  stated in the text; these numbers are from running their code.)
- **their full network is sparse.** in their published DNg100 run (MANC, 1,024 replicates; ED Fig. 5 notebook output) the number of
  active motor neurons per replicate is 0-7, mode 3 (438 of 1,024 replicates). "the full network oscillates" means a handful of
  MNs carrying the loop while the rest of the front-leg network sits near silent. our cord at 0.185 mV has 52+ leg MNs active and the
  rate-model control on our file runs away with half the cells pinned. **the regimes differ before any delay or gain is added**; the
  question for the row is why ours is dense where theirs is sparse (the cut, the size proxy, the DN inputs), not how to force the
  loop over the surround.

### B. question 1: are the two stand-ins physiology fits?

**the loop weight (x3-x8).** their LIF weight is x1.49; their rate model's b = 0.03 with "b_ACh 0.045 still viable, larger
deviations runaway or insufficient recruitment". nothing published supports x3, and x8 is five times the published LIF weight on 44
synapses chosen because they are the loop. it is a gain fit to make one named circuit win over its surround. defensible only as a
labelled diagnostic ("the loop rings if it dominates"), which §A shows is also true of their LIF; not as physiology.

**the 12 ms per-cell delay.** no conduction delay or axon length is published for any fly VNC premotor type. what exists:
- giant fibre, ~7 um axon: **1.15 m/s at 1 h post-eclosion, 2.07 m/s at 24 h** (Kadas, Duch & Consoulas 2019, *eNeuro*
  6:ENEURO.0181-19.2019, DOI 10.1523/ENEURO.0181-19.2019) (M).
- a femur bristle afferent: 3 ms over ~850 um, 0.28 m/s (Agrawal 2020) (M).
- unmyelinated velocity scales ~ sqrt(diameter): a 0.2-0.5 um premotor axon at ~0.3-0.5 m/s (E). the adult VNC is under 1 mm long
  and the three loop cells are, by their MANC names, leg-neuropil interneurons (IN17A001, IN16B036; INXXX466's hemilineage is
  unassigned); their axon path lengths are not tabulated here, and 0.1-0.6 mm (E) gives **0.2-2 ms per cell**. the engine already has 1.8 ms.
- **a 12 ms conduction delay is 5-50x anything axonal (E) and has no source.** it is a stand-in for slowness the LIF lacks at high
  drive: Pugliese's rate model has tau 20 ms per cell (three cells ~60 ms of integration round the loop); graded or slow synapses
  would do the same. the honest label: "a lumped per-cell latency standing in for integration time, chosen to put the ring in the
  band". SEAM's "a fit to physiology (the step frequency of a headless fly), not to the gait" is half right: it is a fit to a target
  frequency, which is a behavioural number.
- **the better-sourced route (E, ranked):** (1) run the loop at x1.0-1.5 and find what in the surround stops it (the rate-model
  control names IN19A002 / IN19A005 / IN19A008 / IN26X001 inhibiting the loop's inhibitors); their LIF at x1.49 rings at 13.5 Hz with
  no delay. (2) if a slowing term is needed, a longer tau_syn on the loop's inhibitory synapse is at least a synaptic parameter (fly
  GluCl / GABA-A IPSC decay is not tabulated for these cells, (E)) and in their LIF tau_syn 10-20 ms moves the ring only to 17-19 Hz,
  so it is not a frequency knob either. (3) keep the delay as a labelled diagnostic, not a default.

### C. question 3: the claw labels

nothing new settles SNpp50 / SNpp51 tuning. no paper maps MANC / MaleCNS claw types to extension / flexion; Lee 2025 identify claw
subtypes morphologically in FANC only. tonight's check in MaleCNS (>= 5 synapses): **direct** input to tibia MNs, SNpp50 ext 408 /
flex 49, SNpp51 flex 329 / ext 0, as in §6; a crude **disynaptic** sum (signed, each intermediate normalised by its output) is mixed
(SNpp50 net toward the flexors, SNpp51 toward both), so the argument rests on the monosynaptic sign plus Marin 2024's effective
connectivity (SNpp50 "activates tibia extensor directly and via two cholinergic serial types"). with the Lee 2025 rule that still
reads SNpp50 = flexion-sensing, and 13B targeting still reads the other way. **the stepping arm exists only under the swapped labels**
(unswapped: 2.1 Hz wander), so an unsourced label choice is now load-bearing for the headline. both labellings should be reported
beside every body result until a FANC-MaleCNS match (the claw axons' projection pattern; Mamiya 2023's position map) decides it.

### D. question 4: frequency and the other legs

- **frequency:** Sapkal 2026's ~11 Hz is DNg100 **air-stepping** in headless flies (the fetch-tool extraction; figure not checked);
  on the ball stepping is slower, with long stance. free walking spans ~5-12.5 Hz (DeAngelis et al. 2019), ~16 Hz at top speed
  (Mendes et al. 2013). 9 Hz is in the range. but **the match is not independent evidence**: the delay was chosen to put the ring in
  the band, so 9 Hz agreeing with 11 is the fit returning its target. the independent test is the frequency's dependence on the
  command: Pugliese (rate) and the animal both speed up with DNg100 drive; in their LIF the cycle barely moves with drive (12.7-16.9
  Hz for 1-3x). does the row's ring speed up with the dose at fixed delay and gain?
- **the other legs.** what the literature says interleg alternation needs: in the animal, nothing from the legs (Sapkal 2026:
  left-right antiphase on every pair under DNg100 in air and in stumps; candidate paths **19B commissural -> 19A local** for left-right
  and **19A intersegmental -> 19A local** for ipsilateral neighbours). in Pugliese's model, disynaptic left-right links were
  "insufficient to couple the phase". nobody has shown a model that couples them. **the honest next target is not a better front
  leg; it is six loops.** there is one loop per hemineuromere (6 cells per type, §8 D-check). first: does each of the six ring under
  the same arm, at what frequency each, and what are their pairwise phases, before any body? if all six ring, their phase relations
  (in-phase, antiphase, drifting) are the first test of the 19A / 19B coupling, a prediction Sapkal's data can falsify. if only the
  front loop rings, the reason (per-segment loop weights, surround, DN reach: DNg100 -> IN17A001 per segment) is the next table
  query.
- **the swing side is still empty.** a step needs trochanter levation and tibia flexion in swing; the tibia flexors and trochanter
  levators are 0.0 Hz in every leg under the ring. the "step" is coxa promotor / remotor alternation plus the springs and the pads.
  in Pugliese's model the tibia flexors were silent too, so this is a shared gap, not a regression, but it bounds what "steps" means.

### E. question 5: claims in the record that go past the sources

1. "**from the published loop at the published weight** with a conduction delay" (SEAM 19:07): the published LIF weight is x1.49; the
   arm is x3 (x8 in the standing arm). drop "at the published weight".
2. "Pugliese 2026's result ... **reproduced in the spiking engine**": theirs is 13.5 Hz at x1.49 with no added delay, isolated; ours
   needs x3, 400 Hz drive and a 12 ms delay, embedded. say "a coxa alternation at the band frequency with two labelled stand-ins".
3. "**at the frequency a headless fly steps**" (19:20, 19:39): circular while the delay is fitted to that band (§D).
4. "the rhythm generator **the field found**": two preprints, both calling the circuit putative; neither shows necessity in the animal.
5. "'the slow units are not in the file' **was the engine, not the map**. withdrawn": the review said "at least partly", and the
   size-scaled excitability arm then failed at 0.185 mV. the accurate form: "the resting-potential data say small MNs need little input;
   whether this file's small MNs are the slow units is unresolved."
6. "a leg steps ... **protraction in the air, three seeds of three**": true of the left front coxa on a body held by stiff springs and
   pads; the foot touches the ground 12 % of the time in the 400 Hz arm (the ground fraction of the x8 arm is not given); swing muscles
   silent. "the left front coxa alternates at 9 Hz and the foot lifts in phase with protraction, on springs" is what the data carry.
7. "the swapped claw labels, **the review's reading**": the review said the labels are uncertain and the indicators disagree (§6, §C).
8. "Sapkal 2026: ~11 Hz" everywhere: air-stepping, extracted by a fetch tool, figure not checked. quote it with the condition.
9. "the two engines agree on where the problem is: not the loop, the balance around it": fair, and it is the most useful sentence of
   the evening; add that Pugliese's own network is sparse (2-4 MNs active) where ours is dense, which the rate control did not
   reproduce.

### F. revised ranking (replaces §8's items 3-5 for tonight's state)

1. **six loops, logged together** under the stepping arm and under x1.49: per-segment ring frequency and pairwise phase. no engine change.
2. **why our cord is dense where theirs is sparse:** run their rate code (the repo is public; `vnc_sim.py`) on their own MANC T1 table
   (in `data/manc t1 connectome data/`) and on ours through the same code. that separates our cut / size proxy / signs from their
   pipeline, which `rate_model_control.md` could not.
3. **the loop at x1.49 with its surround trimmed by named cells** (IN19A002, IN19A005, IN19A008, IN26X001, IN09A002) one at a time, as
   diagnostics: which single surround cell, removed, lets the loop ring at the published weight. that names the balance.
4. **the frequency-vs-dose curve** at fixed gain and delay (a rhythm generator the animal uses speeds up with DNg100; Sapkal: DNg97
   co-activation speeds it further).
5. the claw labels reported both ways beside every body result.
