# the walking command: what it is in the fly, and how to give it to the headless cord as a population

Written 2026-09-23 for `docs/CAMPAIGN.md` (the command as one tonic DNg100 at 100 Hz lays the honest body down; `docs/SEAM.md`
"the body on the standing senses", 00:00 09-23). Does not repeat `walking_review.md` (Sapkal 2024 / 2026, Pugliese 2026, Braun 2024's
headless result, Feng 2020's MDN effectors are there, §0-1) or `octopamine_state.md` (DNp68). Marks as in those files: **(M)** measured
in *Drosophila*, preparation named; **(C)** another insect; **(D)** derived here from MaleCNS v1.0 or from this project's own runs;
**(E)** estimate or modelling choice. "Not measured" is said where it is the answer.

**the answer in six lines.**
1. walking engages a large share of the descending population (the largest single class in the one population-imaging study), but
   that study never saw the gnathal (DNg) cells, and the population's variance during walking is mostly **turning, less speed**.
2. **no walking DN has a published absolute spike rate during walking.** the only numbers: DNa02's step-locked ripple ~15 spikes/s
   (~10 % of its range, so a range near 150 spikes/s, inferred), DNg13 driven past 100 spikes/s by current. every forward-command rate
   (DNg100, DNg97) is calcium or light intensity.
3. at the step timescale the command is **tonic**: sustained through a bout, modulated over 100s of ms; the one step-locked DN (DNa02) is
   locked by ascending input, which the headless cut removes. the decapitated fly steps in a tripod under a tonic optogenetic drive.
4. in the file (D), **DNg100 is extension-favouring** at two synapses, and so are DNg97, DNg75, DNa13, DNb08, DNg13. the DNs whose output
   favours the tibia flexors are DNg95, DNge038, DNge035, DNg16, DNa01 (mild), and DNge049 (barely): **none but DNa01 has a walking
   phenotype in the literature**.
5. models: every VNC model drives one DN at a fixed rate; Pugliese's combinatorial screen found rhythm **rarer** when drive is spread
   across many DNs. no published model uses a phasic command.
6. so the first arm is the forward-walking population at matched total drive, and the prediction written before it runs is that
   **it is still extension-biased** (§4).

---

## 1. which descending neurons are active during walking

### 1a. the population (M)

**Aymanns, Chen & Ramdya 2022** (*eLife* 11:e81527, DOI 10.7554/eLife.81527, PMC9605690). two-photon GCaMP6s of DN axons in the
thoracic cervical connective, tethered on a ball, 9 min recordings; **5 flies, 75-95 hand-labelled ROIs each** (95 / 86 / 75 / 81 / 79).
the driver is "brain only" (otd-FLP; R57C10) and **"lacks expression in the subesophageal zone ... a region known to house at least 41
DNs"**: the GNG DNs, which include DNg100, DNg97, DNg13 and every DNge, are not in this sample. results:
- "the largest fraction (~60%) of DNs encode walking"; ~15 % head grooming; very few resting; none front-leg rubbing. (a fraction of
  the imaged ROIs, not of all ~1,100 DNs.)
- restricted to walking epochs, population activity uniquely explains **~60 % of turning variance and ~30 % of speed variance**; turn
  DNs are spatially clustered and lateralised, speed DNs are "a more distributed set" that "weakly encode walking speed".
- the first two PCs explain >60 % of population variance during walking. onset vs sustained is not separated as a class; the
  analysis treats walking DN activity as elevated through the epoch and modulated within it (GCaMP6s; no step-scale resolution).

**Chen et al. 2018** (*Nat Commun* 9:4390, PMC6197219), the VNC imaging method. two named DNs: **MDN** active before backward
rotations of the ball (900 left + 900 right events, 3 flies, 7,790 s); **DNa01 ("A1")** linked to forward walking, left and right
weakly correlated, each with ipsilateral turning (1,644 / 1,651 events). (M, calcium.)

**Braun et al. 2024** (*Nature* 630:686, PMC11186778). optogenetic DNp09 recruits many DNs across the whole dorsal-ventral connective,
"the largest fraction" active "in a similar manner" to spontaneous forward walking, with a small medial subset active only under
stimulation. in the female brain connectome DNp09 has **32 downstream DNs** (aDN2 23, MDN 14); DNa01 25, DNb02 20, DNa02 18. DNp09 and
DNb02 do nothing in headless flies; MDN, DNg14, DNg11 do. (M.)

**the count.** MANC has 1,328 DNs (Cheong 2024); Pugliese's MANC table 1,318; our MaleCNS census 1,306 cells / 481 types
(`world/record/dn_census_0922`).

### 1b. the named walking DNs

"rate" means a measured spike rate; there are almost none. the last column is **our own whole-fly LIF** during the 60 s census
(walking 70 % of the time), **(D), a model output, not a measurement**, given because it is what `--dn-playback` replays.

| DN (alias) | walking-time activity (M) | tonic / phasic | perturbation (M) | census, Hz per cell (D) |
|---|---|---|---|---|
| **DNg100 (BDN2)** | calcium "strongly correlated to forward (but not angular) velocity", 3 flies (Sapkal 2024). no spike rate | tracks velocity over a bout | activation initiates forward walking, strongest of the tested; **headless: walks** (Sapkal 2024), stepping frequency rises with light (Pugliese 2026); silencing **lowers forward velocity** | 48 (p10/p90 0 / 90) |
| **DNg97 (oDN1)** | not imaged in walking | - | activation initiates walking, weaker than BDN2; headless: walks; **silencing: no effect** on velocity (Sapkal 2024); + DNg100 raises speed and step frequency toward BPN levels (Sapkal 2026) | 0.2 |
| **DNp09 (P9)** | **"not active during spontaneous walking"** (calcium; Bidaye 2020); active in courtship pursuit | - | unilateral: forward walking with ipsilateral turns; bilateral: walking with turns both ways (Bidaye 2020, *Neuron* 108:469); running then freezing (Cande 2018); **headless: nothing** (Braun 2024) | 0.0 |
| **DNa01** | whole-cell, n = 10 cells: rises before ipsilateral turns, **sustained**, low-gain; weakly related to forward velocity (Rayshubskiy 2025) | slow, sustained | bilateral silencing **lowers forward velocity** and sideways speed, not rotation (Rayshubskiy); activation: global locomotor increase (Cande 2018), in-place turning (Braun) | 0.1 |
| **DNa02** | whole-cell, n = 13: **transient**, high-gain steering, leads DNa01 (Rayshubskiy 2025); **stride-locked modulation ~15 spikes/s, "approximately 10% of the cell's dynamic range", consistent across recordings** (Yang 2024) | phasic at turns; the only DN with a step-locked component, attributed to ascending input | unilateral: shortens inside steps (Yang 2024), small ipsilateral bias (Rayshubskiy); silencing: rotation unchanged; bilateral activation raises locomotion (Cande 2018) | 8.9 |
| **DNg13** | whole-cell: rate rises before contralateral stride lengthening; **not step-locked**; current injection drives it **>100 spikes/s** (Yang 2024) | sustained | lengthens contralateral stride in both phases (Yang 2024) | 0.1 |
| DNb05 / DNb06 | calcium correlates with ipsiversive / contraversive rotation (Yang 2024; n = 7 / 7) | - | - | 194 / 60 |
| DNa03 -> DNa11 | steering hierarchy with LAL013; DNa11 changes stepping direction of all six legs, saccadic turns (Feng et al. 2024, bioRxiv 10.1101/2024.06.27.601106) | - | activation turns in walking and flight | 8.9 / 14.6 |
| DNb02 | - | - | turning; headless: none (Braun 2024) | 1.6 |
| **MDN** | calcium before backward events (Chen 2018) | bout-level | backward walking, **headless too** (Bidaye 2014; Braun 2024: P = 0.265 vs intact) | **10.2** (see note) |
| DNb08 | - | - | headless: rhythmic front / mid-leg "searching" (Pugliese 2026) | 0.4 |
| DNg75 / DNg55 / DNg16 | - | - | with DNg100 in headless flies: + DNg75 raises step frequency; + DNg55 degrades coordination; + DNg16 no speed-up (Sapkal 2026; figure-level numbers unchecked, `walking_review.md` §1) | 6.1 / 1.4 / 0.0 |

note on the census column: MDN at 10 Hz and DNb05 at 194 Hz during forward walking are our whole-fly model's, and MDN in the animal is
silent outside backward events. the playback replays these as they are.

**what is not known.** no spike rate for DNg100, DNg97, DNp09 or MDN in a walking fly. no DN recorded in a headless walking fly (all
headless drive is CsChrimson). no study of how the forward DNs co-vary with each other on a single-step timescale.

### 1c. tonic or phasic

- **bout scale (M):** walking DNs are elevated across a bout and track speed and turning over 100 ms to seconds (Aymanns; Rayshubskiy;
  Sapkal 2024). a bout's onset is a ramp in the calcium, which is what `--walk-ramp` already stands for.
- **step scale (M):** one DN, DNa02, carries a step-locked ripple of ~15 spikes/s; Yang et al. attribute it to ascending neurons from
  the VNC, which DNg13 does not share and is not locked. that loop runs cord -> ascending neuron -> brain -> DN -> cord. **in a headless
  preparation it does not exist.**
- **the headless animal (M):** DNg100 under steady (66 Hz pulsed, population-synchronous) light steps all six legs, tripod-coupled, in
  air, on a ball and as stumps (Sapkal 2024, 2026). the step rhythm is not in the command.

so a step-locked envelope on the DNs is a puppet in the headless cord: it would be the rhythm put in from outside. **the only
legitimate step-scale modulation of a DN in this project is the whole fly's own ascending loop** (brain present, `dn_census`-style runs).
in the headless arms the command is tonic, with at most a bout-level ramp.

---

## 2. what the DNs do at the leg

### 2a. the literature

- **direct DN -> MN synapses are rare**; DNs act through premotor INs (Cheong et al. 2024, *eLife* 13:RP96084, PMC13384506). Cheong
  name the leg-coordination sets: GABAergic 09A / 19A sets (IN09A002, IN09A010, IN19A022, IN19A016) onto the **stance** coxa MNs
  (pleural remotor / abductor, sternal posterior rotator); IN19A004 and a 19A GABA set with cholinergic IN19B012, IN01A015, IN03A010,
  IN21A012, IN21A017 upstream of the **trochanter flexor and tibia extensor**. **DNg100 is not analysed there by name.**
- **DNa02:** GABAergic IN19A003 and IN08A006 onto ipsilateral rotator MNs (stride shortened inside the turn), cholinergic IN07B006 to all
  three contralateral leg neuropils; **DNg13:** sequential cells T1 -> T2 -> T3 (Cheong). **MDN and DNa13** share targets in the
  trochanter-flexor and tibia-extensor circuits; MDN's strongest hind-leg path is LBL40 (Cheong; Feng 2020).
- **Sapkal 2026:** the DNg100 / DNg97 shared targets give the five-cell motif IN17A001, IN03A006, INXXX464, IN12B003, IN09A002
  (`walking_review.md` §1). **Sapkal 2024:** BRK (VNC brake) cells act only on legs in stance and recruit the accessory tibia flexors;
  swing initiation under BDN2 or MDN happens inside a Fe-Ti angle window (their "SIZ"), i.e. **the leg's own angle gates swing**.
- **Lesser et al. 2024** (*Nature* 631:369): premotor modules and size-ordered premotor weights; no DN-to-side analysis.
- **nobody has published which DNs favour the flexion vs extension side of the tibia.** the table below is ours.

### 2b. (D) the file: every candidate's output, MaleCNS v1.0, edges >= 5 synapses

direct output by target, and a disynaptic reach onto the tibia MN pools: for each DN output fraction to intermediate k times k's output
fraction onto Ti flexor (incl. accessory) or Ti extensor MNs, split by k's transmitter (ACh = E; GABA / Glu = I), x 1000. "ext set" =
synapses onto the 11 cells last night's hunt found holding the flexors down (IN13A001/002/005, IN12B003, IN19A002/004/015, IN09A002,
IN21A002/003, IN16B016); "flx set" = onto the flexor excitors and releasers (IN21A004, IN03A004, IN03A031, IN03A039, IN20A.22A009/010,
IN17A016, IN13B019, IN13A006, IN13A015, AN06B002, IN12A001, IN20A.22A007, IN01A012). scripts in the session scratchpad; queries only.

| DN | cord out (syn) | ext set | flx set | E->flex | E->ext | I->flex | I->ext | **net flex / net ext** | reads as |
|---|---|---|---|---|---|---|---|---|---|
| **DNg100** | 21,469 | **2,580** | 259 | 1.9 | 2.5 | 3.8 | 1.8 | **-1.9 / +0.7** | **extension** |
| DNg97 | 7,703 | 1,120 | 191 | 4.1 | 8.7 | 4.1 | 3.5 | 0.0 / +5.2 | extension |
| DNg75 | 8,011 | 611 | 99 | 0.6 | 1.3 | 2.5 | 0.8 | -1.9 / +0.5 | extension |
| DNa13 | 17,169 | 998 | 52 | 3.8 | 10.1 | 2.0 | 5.1 | +1.8 / +5.0 | extension |
| DNb08 | 6,936 | 885 | 31 | 2.9 | 11.2 | 2.3 | 0.8 | +0.6 / +10.4 | extension |
| DNg13 | 8,314 | 117 | 22 | 1.4 | 3.9 | 1.4 | 0.5 | 0.0 / +3.4 | extension |
| MDN | 9,551 | 479 | 13 | 5.3 | 6.6 | 1.0 | 0.8 | +4.3 / +5.8 | both, ext a little |
| DNa02 | 9,240 | 12 | 0 (483 onto IN13B001, an inhibitor of the 13B side, not counted) | 0.5 | 0.4 | 1.3 | 0.4 | -0.8 / 0.0 | little tibia reach (rotators) |
| DNp09 | 4,377 | 0 | 0 | 1.2 | 0.6 | 0.4 | 0.9 | +0.8 / -0.3 | little cord reach: a brain broadcaster |
| **DNa01** | 9,807 | 1,063 | 283 | 11.1 | 6.7 | 7.5 | 5.1 | **+3.6 / +1.6** | flexion, mild |
| **DNg16** | 8,391 | 198 | 20 | 10.6 | 5.7 | 3.0 | 4.5 | **+7.6 / +1.2** | flexion |
| **DNge035** | 16,265 | 2,477 | 1,282 | 20.9 | 5.8 | 10.4 | 1.6 | **+10.5 / +4.2** | flexion |
| **DNg95** | 3,891 | 42 | 468 | 46.2 | 0.3 | 4.0 | 40.0 | **+42.2 / -39.7** | flexion, strongly |
| **DNge038** | 4,399 | 47 | 187 | 9.0 | 0.1 | 2.0 | 9.1 | **+7.0 / -9.0** | flexion (35 % of its output is onto MNs) |
| DNge049 | 13,069 | 1,648 | 699 | 10.1 | 5.2 | 9.3 | 6.3 | +0.8 / -1.1 | flexion, barely |

- **DNg100 favours extension, as the file showed.** its largest cord targets: IN09A002 (GABA) 1,026, IN17A001 (ACh, the loop cell) 818,
  **IN12B003 (GABA) 771**, IN01A015 743, IN19A006 441, the pleural remotor / abductor MNs 440, IN16B016 (Glu) 422, IN19A016 (GABA) 379.
  46 % of its output lands on inhibitory cells; to the tibia it is inhibition onto the flexors, excitation onto the extensors. this
  matches SEAM's two-synapse census of 09-22 (0.09 / 0.20 flexor / extensor reach) by a different metric.
- **the whole forward-command family is extension-side**: DNg97, DNg75 and DNb08 too. DNp09 hardly touches the cord and instead
  drives the other DNs: DNg100 212, DNg97 126, DNg75 149, DNa11 222 synapses (D), the connectome form of Braun's "broadcaster".
- **flexion-side DNs**: DNg95, DNge038, DNge035, DNg16, DNa01. four of the five have **no walking phenotype on record** (DNg16 was
  co-activated with DNg100 by Sapkal 2026 with no speed-up; Braun excluded its line for lacking a phenotype). DNa01 is the only
  flexion-leaning DN measured during walking.
- **reading (E).** this is what a stance command should look like: the descending drive for forward walking supports the power stroke
  (tibia extension, coxa remotion) and leaves swing to the cord. the fly's swing comes from the rhythm generator and the leg's angle
  (Sapkal's swing window), not from a flexion DN. **so the population will not by itself supply the flexion half-cycle**, and a model
  that needs flexion DNs to swing is using the command where the fly uses the cord.
- caveats: the reach metric ignores disinhibition (a GABA cell inhibiting a flexor inhibitor counts as I onto nothing), the third synapse,
  and the pool sizes; it ranks DNs against each other, not in mV. the claw-label question (ledger 1) does not touch it (no sensory cells
  in the path).

---

## 3. how models drive the cord, and with what

| model | command | rate / amplitude | why |
|---|---|---|---|
| **Pugliese et al. 2026** (rate, MANC / FANC / MaleCNS / BANC) | one DNg100 (left), sustained step | `stimI` 250 in their equation r = 200 tanh((a/200)(I + sum w r - theta)): **~165 Hz on the DN** at a = 1, theta = 7.5 (E, computed from `configs/experiment/DNg100_Stim.yaml`; per-cell a and theta are size-scaled, so it varies). their LIF: DN at a constant 0.15 nA, **68 Hz** | the only DN "known to function as descending command neurons for walking", headless-proven. **their screen: all 933 excitatory DNs one at a time** (I = 128, auto-halved or doubled up to 10 times to keep 5-1,500 cells active and <= 100 above 100 Hz): DNg100 and DNb08 top; 332 of 859 scored 0. **combinatorial screen**, 60-80 k runs per grid point, input split by a Dirichlet over all 1,318 DNs: "the median motor rhythmicity score for all values in this grid is low, but for moderate levels of input to small numbers of DNs, there are some choices that give high scores"; 14 of the top 29 contributors were single-screen hits |
| **Shiu et al. 2024** (whole-brain LIF, FlyWire) | sensory: sugar GRNs, Poisson | **100 Hz** per input cell | the weight was set so 100 Hz sugar gives ~80 % of the model's max MN9 rate (`parameter_provenance.md`); no VNC |
| **Sapkal et al. 2024** (Shiu's model) | P9 or BPN with sugar GRNs, rates swept | a range of rates, read out as oDN1 / BDN2 firing | the only model that produces a **DN population's rates from a walking-initiation input**; brain only, stops at the DNs |
| Lappalainen et al. 2024 (visual, trained, connectome-constrained) | - | - | no cord analogue found |
| NeuroMechFly v2 (Wang-Chen et al. 2024, *Nat Methods*) | a two-number "descending" drive (left, right) scaling abstract CPG oscillators | continuous | turning by asymmetry; no connectome on the motor side |
| flybody (Vaxenburg et al. 2025) | steering / speed commands into a trained policy | continuous | not connectome |
| **this project** | one DNg100 pair at 100 Hz (record); the flexor set; MDN; `--dn-playback` (1,306 DNs at the whole fly's rates, chunk by chunk) | 100 Hz; census rates | Bidaye / Sapkal headless; the playback is the whole fly's own output |

**no published VNC model uses a DN population with measured rates, or a phasic command.** the field drives one DN at a rate chosen to
give a working network (Pugliese's `adjustStimI` makes this explicit), and Pugliese's combinatorial result says spreading drive over
many DNs makes rhythm less likely, not more.

---

## 4. the design: the command as a population, for the headless cord

**what the population is for.** not to make the rhythm (§1c: the command is tonic and the animal's rhythm is in the cord) and not to
make the flexion half-cycle (§2b: the forward DNs are extension-side). it tests one thing: **is the body lying down because one DN
carries the whole command, or because the whole forward command is extension-side in this wiring?** the reads are last night's:
weight on the floor, extensors, the tibia flexors by size third, IN13A002 / IN12B003 / IN19A004, IN13B019 / IN13A006, IN17A001's line,
coxa promotor / remotor autocorrelation (the published rhythm), antagonist and inter-leg columns. never "did he walk".

**the arms** (cord, 30 s, seeds 11-13; then the body, `--senses v2`, both claw labellings; one change per arm). drive is matched to
the record: sum over cells of rate x cord synapses = DNg100's 21,469 x 100 Hz, every type in an arm at one common rate. all are runnable
today with `--walk RATE --walk-dn A,B,C` in `world/cord.py` and `experiments/body_loop.py` (one rate for the list).

| arm | DNs | rate | predicted net onto Ti flexor / extensor pools (D, the §2b metric x rate, arbitrary units) |
|---|---|---|---|
| A0 control (record) | DNg100 | 100 Hz | -6,120 / +2,255 |
| **A1 the forward population (first arm)** | **DNg100, DNg97, DNg75, DNa01, DNa02** (10 cells, both sides) | **38.2 Hz** | -2,440 / **+4,647** |
| A2 A1 without the extension-favouring commands | DNg75, DNa01, DNa02 | 79.3 Hz | -216 / +2,009 |
| A3 A1 + the file's flexion set (labelled: no walking source) | A1 + DNge035, DNg95, DNge038, DNge049 | 22.9 Hz | +9,081 / -1,490 |
| A4 the recorded population | `--dn-playback world/record/dn_census_0922` | the whole fly's, chunked | (exists; ran 09-22 on the old floor, re-run on `--senses v2`) |
| A5 null | 10 random excitatory DN cells | matched | - |

- **A1 is the first arm.** its membership is inherited: DNg100 and DNg97 initiate walking in headless flies (Sapkal 2024); DNg75 raises
  step frequency with DNg100 (Sapkal 2026); DNa01 and DNa02 are active during forward walking (Chen 2018; Rayshubskiy; Yang) and are
  given bilaterally so their steering cancels. DNp09 is left out on purpose: it needs the brain (Braun 2024) and barely reaches the
  cord (D). **prediction written before the run:** less inhibition onto the flexors than A0 (by 2.5x) and **twice the extensor
  drive**; the body still lies down, or lies down faster. if it stands, the metric is wrong about the 13A route and that is a finding.
- **A2** asks whether the lying-down is DNg100's alone; its prediction is near-neutral on the flexors and the same extensor drive as A0.
- **A3** is the flexion supply the literature does not give; if it stands the body, it is a posture from DNs with no walking record
  (ledger row), not a result about walking. SEAM 09-22 already has the non-matched version: co-contraction (0.57 / 8.6 Hz).
- **A4** is the population the whole brain actually made in this project (its rates are the model's, §1b), and the only arm in which DNs
  have a time course of their own. it replays the chunked rates; a step-locked component cannot be in it (100 ms chunks).
- **tonic, with a bout ramp only.** `--walk-ramp 1` on every arm (a bout's onset, Aymanns / Sapkal calcium). **no step-locked envelope
  on any headless arm**: that would be the rhythm supplied from outside, the sine on the motor neurons in another place. the one natural
  step-locked DN signal (DNa02, ~15 spikes/s) needs ascending neurons and a brain; it belongs to the whole fly, where it already can arise.
- **one engine-free addition worth logging, not running yet:** a per-type rate list (`--walk-dn DNg100:48,DNa02:9,...`) so A1 can take
  the census's relative rates instead of equal ones. equal is the null while no absolute rate is measured.

**measured, inherited, chosen.**
- measured (M): which DNs initiate and modulate walking and what silencing does (§1b); DNg100's velocity tuning (calcium); DNa02's
  ~15 spikes/s step ripple and DNg13's >100 spikes/s under current; that the headless fly steps under a tonic drive; the ~60 % / ~30 %
  turning / speed variance split (not the GNG DNs).
- inherited: DNg100 as the command and the matched-drive frame (Pugliese; Sapkal); the membership of A1 (§1b sources); the census rates
  for A4 (this project's whole fly, (D)).
- chosen (E): **every absolute rate** (none is measured; 38.2 Hz comes only from matching 100 Hz x DNg100); equal rates within an arm;
  matching on synapse count x rate rather than on effect; the §2b sets and metric; bilateral DNa01 / DNa02; the ramp length.
- what would settle the rates: a whole-cell or calcium-to-rate calibration of DNg100 during walking (none exists), or Sapkal's
  light-intensity-to-step-frequency curve used as the target for the matched drive (frequency, not gait: a measured thing).

---

## sources opened for this file

Aymanns, Chen & Ramdya 2022 *eLife* 11:e81527 (PMC9605690, full text); Chen et al. 2018 *Nat Commun* 9:4390 (PMC6197219); Braun et al.
2024 *Nature* 630:686 (PMC11186778); Sapkal et al. 2024 *Nature* 634:191 (PMC11446846); Bidaye et al. 2020 *Neuron* 108:469 (PMC9435592,
via summary); Cande et al. 2018 *eLife* 7:e34275 (PMC6031430); Rayshubskiy et al. 2025 *eLife* 102230 (PMC12279373; no absolute spike rate
in the text: n = 13 DNa02, 10 DNa01); Yang et al. 2024 *Cell*, "Fine-grained descending control of steering in walking Drosophila"
(PMC12778575); Feng et al. 2024 bioRxiv 10.1101/2024.06.27.601106 (abstract level); Cheong et al. 2024 *eLife* 13:RP96084
(PMC13384506); Pugliese et al. 2026 (PMC13142387, and their code `configs/`, `src/simulation/vnc_sim.py`). the (D) tables: MaleCNS v1.0
`connectome-weights-...-minconf-0.5.feather`, `body-annotations`, `body-neurotransmitters` (consensus_nt), edges >= 5; census rates from
`world/record/dn_census_0922.cells.npz`.
