# the claw's two classes and the 13A inhibitors: which SNpp type is which, pinned by the reflex's phase

written 2026-09-23 for ledger row 1 ("claw labels reported both ways") and the SEAM entry "the cord listens to a walking leg".
tags: (M) measured in the fly, (D) read from the male file (MaleCNS v1.0, minconf 0.5, synapses summed over the type, all legs),
(I) inferred, (C) comparative (other insects). the file's queries were run for this page; the query is at the bottom.

## the answer

- **SNpp50 is the flexion-tuned claw and SNpp51 the extension-tuned claw** (the body's `--claw-labels 50flex`). the reverse of
  `leg_biomech_parts/E_table_male.md`, of `leg_senses_map.md`'s old gloss and of `body_loop.py`'s default (`50ext`).
- **how sure: probable, not measured.** no paper names the tuning of a MANC / MaleCNS claw type. the call rests on three wiring
  matches between the file and two FANC papers that name claw-flexion / claw-extension axons (Lee 2025, Syed 2026), plus Marin 2024's
  effective connectivity, plus a weak count ratio. the one counter-indicator (13B) does not survive a look at where those 13B cells
  go. i'd put it near 85-90 %.
- **13A in a walking fly: not measured by anyone.** no calcium or patch recording of a 13A neuron exists during walking, grooming or
  imposed tibia movement. what is measured: 13A activation / silencing changes grooming and walking kinematics (Syed 2026), and the
  step-phase kinematics per leg (Haustein 2024). the inference: the flexor-inhibiting 13As should fire in the leg's extension
  phase, which is **stance in the hind legs** (and late stance in the middle legs), swing in the front legs.
- **so the body should run `50flex`.** in it the 13A flexor-inhibitors lock to the imposed stance, the resistance reflex has the
  measured sign, and it is the arm in which he stood. `50ext` is positive position feedback at every knee; it is the arm in which the
  extensors ran away (13-16 Hz) and he splayed.

---

## 1. the claw cells

### what is measured about the two classes (M)

- **Mamiya, Gurung & Tuthill 2018** (*Neuron* 100:636, DOI 10.1016/j.neuron.2018.09.009; `research/sources/mamiya_2018.md`):
  claw = tonic femur-tibia angle, two populations. extension-tuned pixels active 90-180 deg, flexion-tuned 90-18 deg, neither near 90;
  hysteretic; single cells range-fractionated (one peaked at 70 deg, one at 20 deg), each responds to flexion **or** extension. front leg
  only, GCaMP6f at 8 Hz, driver line R73D10 (both classes together).
- **anatomy of the two classes:** "each claw branch is divided into two sub-branches that are specialized for encoding flexion or
  extension of the tibia" (Mamiya 2018, Discussion; the X, Y, Z branches each carry both; one claw neuron innervates all three).
  **the text does not say which sub-branch lies where** (anterior / posterior, medial / lateral); the positions are only in the images
  of Fig. 4A. this is the anatomical handle that could settle row 1 (§3), and nobody has written it down.
- **Mamiya et al. 2023** (*Neuron* 111:3230, DOI 10.1016/j.neuron.2023.07.009): flexion- and extension-selective claw cell bodies are
  intermingled in the femur; opposite recruitment gradients along the array; snRNA-seq cannot separate the two claw classes.
- **Chen et al. 2021** (*Curr Biol* 31:5163): claw drives 13Ba, 13Bb, 19Aa, 19Ab, 8Aa, 8Ba (claw line stimulated as a whole, not per class).
- **Dallmann et al. 2025** (*Nature* 647:445, DOI 10.1038/s41586-025-09554-2): claw axons are **not** presynaptically suppressed in
  walking or grooming (hook axons are); one claw line, classes not separated, no step-phase analysis of the claw.

### the connectomes

- **Lee, Dallmann, Cook, Tuthill & Agrawal 2025** (*Nat Commun* 16:4105, DOI 10.1038/s41467-025-59302-3), FANC, front left leg: 80
  FeCO axons sorted "based on axon morphology and comparison with light microscopy images" into claw-extension 8, claw-flexion 13,
  hook-extension 9, hook-flexion 13, club 37. **the reflex rule, verbatim:** "Claw and hook flexion axons provide excitatory feedback to
  motor neurons that extend the tibia and inhibitory feedback to motor neurons that flex the tibia. Claw and hook extension axons provide
  excitatory feedback to motor neurons that flex the tibia and strong inhibitory feedback to motor neurons that extend the tibia." no MANC
  names, no 13A named.
- **Syed, Ravbar & Simpson 2026** (*eLife* 14:106446; bioRxiv 10.1101/2024.06.05.597468), FANC, front right leg, the 13A / 13B
  hemilineages (62 13A, 64 13B), proprioceptors from the Tuthill-lab reconstructions. verbatim: "multiple connections from
  flexion-sensing claw and hook neurons onto the main neurite of 13A-10f-α, which targets tibia flexor MNs. Similar connections were
  observed onto 13A-10e-δ, –9d-γ." "Flexion-sensing proprioceptors send direct excitatory feedback to tibia extensor MNs and indirect
  inhibitory feedback to flexor MNs. Thus, flexion-sensing proprioceptors could activate primary 13 A neurons to inhibit tibia flexor
  MNs, while directly activating extensor MNs." and: "Extension position and motion sensing proprioceptors ... connect to tibia flexor MNs
  ... and two 13 A neurons (13As-ii group) ... that inhibit tibia extensor MNs." their primary (flexor-inhibiting) 13As also inhibit the
  extensor-inhibiting 13As ("inhibit flexor MNs and disinhibit extensor MNs by inhibiting other 13As"). no MANC names.
- **Marin et al. 2024** (*eLife* 13:RP97766), MANC: names SNpp50 and SNpp51 only as "FeCO claw" (synonyms); **no tuning.** effective
  connectivity (their Fig. 59D, via `research/sources/marin_2024_manc_annotation.md`): SNpp51 "activates tibia flexor + acc. tibia
  flexor; inhibits tibia extensor via two glutamatergic serial types"; SNpp50 "activates tibia extensor directly and via two cholinergic
  serial types; weakly disinhibits flexors with delay." and "one FeCO claw type -> 13A".
- **searched and silent on the mapping:** Cheong et al. 2024 (MANC premotor), Azevedo et al. 2024 (FANC), Lesser et al. 2024
  (*Nature* 631:369; FANC premotor, 13A / 13B as inhibitory premotor, no claw-class split), Dallmann 2025, Pugliese et al. 2026
  (bioRxiv 10.1101/2025.09.12.675944; names 13A / 13B only as future work: "integrate the DNg100 pathway with inputs to the 13A and 13B
  neuron classes ... [which] receive proprioceptive feedback"), Sapkal et al. 2026 (bioRxiv 10.64898/2026.04.29.721658; no 13A, no
  phase assignment of its motif). **no paper maps SNpp50 / SNpp51 to claw-extension / claw-flexion.**

### the file against the two FANC motifs (D)

| motif (FANC, the paper's words) | if SNpp50 = flexion, SNpp51 = extension | the file |
|---|---|---|
| flexion claw -> tibia extensor MNs, direct excitation (Lee; Syed) | SNpp50 -> Ti extensor | **470**; SNpp51 -> Ti extensor 5 |
| extension claw -> tibia flexor MNs, direct excitation (Lee; Syed) | SNpp51 -> Ti flexor | **360** (+ acc. 59); SNpp50 -> Ti flexor 18 (+ acc. 78) |
| flexion claw -> primary 13As that inhibit the tibia flexors (Syed) | SNpp50 -> flexor-inhibiting 13As | **IN13A002 4,612, IN13A009 1,179, IN13A005 940, IN13A001 299**; SNpp51 -> IN13A002 24, IN13A005 27 |
| those 13As -> flexor MNs, and -> the extensor-inhibiting 13As (Syed) | IN13A002 -> Ti flexor and -> IN13A006 | **900** and **1,178**; IN13A005 -> Ti flexor 1,020; IN13A001 -> Ti flexor 857 |
| extension claw -> two 13As that inhibit the tibia extensor (Syed) | SNpp51 -> extensor-inhibiting 13As | **IN13A006 906**, IN13A014 290, IN13A015 256; IN13A006 -> Ti extensor **2,261**; SNpp50 -> IN13A006 small |
| counts, front left leg (Lee 2025: flex 13, ext 8, ratio 1.6) | SNpp50 : SNpp51 should be > 1 | 62 : 32 in MaleCNS (1.9), 62 : 27 in MANC; weak (both datasets undercount) |

every row reads the same way. under the printed labels (SNpp50 = extension) every row inverts: an extended knee would excite its own
extensor and silence its own flexors through IN13A002, which is Lee's rule backwards.

**the counter-indicator, checked (D).** Agrawal et al. 2020 (*eLife* 9:e60299) call 13Bα an extension-claw target, and SNpp50 feeds
13B four times more than SNpp51 does. but (i) Agrawal's "extension-tuned claw" input is inferred from 13Bα's tuning (depolarises past
~90 deg of extension), not from an identified synapse; (ii) the 13B types SNpp50 feeds most (IN13B005 895, IN13B013 766) send their
output to 23B, AN and 14A / 19A interneurons, not to tibia motor neurons (top targets: IN23B028 4,478, AN04B001 2,096; IN14A005 893,
IN23B009 631), so they are not the 13Bα whose activation flexes the tibia; (iii) Marin 2024 already found the FeCO -> 13B mapping
disagreeing with Agrawal for the hook. a weak, unidentified indicator against five named wiring matches.

**caveats.** Lee and Syed are the female FANC front legs (T1L, T1R); the file is male and the body's claw rows are almost all middle
and hind (front: 1 / 0 SNpp50, 3 / 1 SNpp51). the assumption is that the reflex motif is conserved across sexes and segments; Marin's
effective-connectivity signs, from the male, agree. none of this is a recording of an SNpp cell.

---

## 2. the 13A cells in a walking fly

### measured (M)

- **no recording of 13A exists** during walking, grooming or imposed tibia movement (searched: Agrawal 2020, Chen 2021, Dallmann 2025,
  Syed 2026, Lesser 2024, Pugliese 2026, Sapkal 2026). Agrawal 2020 recorded 13Bα, 9Aα, 10Bα; Chen 2021 imaged 8A, 8B, 9B, 10B, 13B,
  19A classes; **no 13A class was imaged in either.**
- **Syed 2026, perturbation:** activating 13A + 13B (R35G04 ∩ GAD) continuously "reduces front leg rubbing and head sweeps and induces
  unusual leg extensions" (and front-leg extension in headless flies); pulsed activation (70 ms on / off) gives alternating grooming-like
  movements. silencing 13As in grooming reduced the front legs' FTi separation and "decreased the frequency of extension-flexion cycles";
  in walking, silencing "did not affect the frequency of extension–flexion cycles" but reduced the tarsal-tip and TiTa distances. **no
  phase is reported.** the extension on activation fits primary 13As silencing flexors (and disinhibiting extensors).
- **Agrawal 2020:** 13Bα tonic, depolarised with extension past ~90 deg, non-spiking; activation -> CTr extension + **FTi flexion**
  (a negative-feedback posture loop). 9Aα spiking, flexion-direction and speed tuned; activation -> small FTi / TiTa extensions.
- **the step's kinematics** (Haustein et al. 2024, *Front Bioeng Biotechnol* 12:1357598; `research/sources/haustein_2024.md`): "extension
  and flexion of the leg were performed during swing and stance phase, respectively, in the front legs. In contrast, in the hind legs
  flexion of the leg was performed in the swing phase, while extension of the leg was observed in the stance phase." middle legs: tibia
  flexion through swing and the first half of stance, extension in the second half.
- **no phase-resolved EMG or MN recording of the fly's tibia muscles in walking exists** (`leg_biomech.md` §C2); Azevedo 2020 does not
  split flexor firing by phase.

### comparative (C)

- stick insect middle leg: motoneurons in walking get "a depolarizing input followed by a hyperpolarizing input in the inter-burst
  interval ... Hyperpolarizations were in synchrony with activity in the antagonistic motoneurons" (Schmidt, Fischer & Büschges 2001,
  *J Neurophysiol* 85:354). **the flexor MNs are inhibited while the extensor bursts**: whoever carries that inhibition fires in the
  extension phase.
- the FTi pathways run through parallel nonspiking interneurons that "support both 'resisting' and 'assisting' responses" (Büschges &
  Wolf 1995, *J Neurophysiol* 73:1843); in the active animal the same fCO stimulus can reverse to the "active reaction" (Driesang &
  Büschges 1996, *J Comp Physiol A* 179:45; Bässler & Büschges 1998). a reflex reversal has not been shown in *Drosophila*
  (`walking_review.md` §6). the stick insect's middle-leg stance is flexion, so its phases port to the fly's front leg, not the hind.

### the inference (I)

a flexor-inhibiting 13A should fire in the phase where the flexor is silent and the extensor is active: **stance in the hind legs,
late stance in the middle legs, swing in the front legs.** sources: the step kinematics (M), the reciprocal wiring (D, Syed's motif),
the stick insect's antagonist-phased MN inhibition (C). confidence moderate: it is what the wiring is for, but no one has watched a 13A
cell do it.

---

## 3. the inference for row 1

### the cord's result, with the clip's angles under it

the SEAM run (`--kin-drive`, 30 s, seed 11): IN13A002 on lh / lm / rh / rm **locks to the imposed stance** under `50flex` (VS 0.2-0.44)
and **to the swing** under `50ext` (VS to 0.81). why, from the clip's own femur-tibia angle (180 = straight, Mamiya's convention; from
`world/body/loop/kd_a_walk.npz`, the knee through the model's neutral, 10 bins per step from swing onset, swing = the first ~35-42 %):

| leg | FTi through the step (swing ... stance) | most flexed | most extended |
|---|---|---|---|
| lh | 104 92 83 78 **74** 76 83 89 98 104 | touchdown / early stance | late stance / lift-off |
| rh | 92 79 67 60 **59** 61 67 74 85 94 | touchdown / early stance | late stance / lift-off |
| lm | 94 87 81 74 **74** 76 77 81 86 92 | touchdown / early stance | late stance / lift-off |
| lf | 79 87 102 116 **119** 111 99 90 83 79 | lift-off | touchdown |

the claw is a position code, so on the middle and hind legs the flexion class peaks at touchdown and early stance, the extension class
at lift-off and early swing. the recorded fly is Haustein's fly: the hind tibia flexes in swing and extends through stance.

- **`50flex`:** the flexed knee at touchdown drives SNpp50 -> IN13A002 / 005 / 001 -> the tibia flexors off, the extensor excited
  directly and disinhibited through IN13A006. the flexors are silenced as stance (extension) begins: **the 13As fire when §2 says they
  should,** and IN13A006 (the extensor-inhibitor, fed by SNpp51) locks to the swing, when the hind extensor should be off. both halves
  agree with the fly's phases.
- **`50ext`:** the extended knee at lift-off drives SNpp50 -> IN13A002 -> the flexors silenced at swing onset, exactly when the hind leg
  must flex to swing. the 13As would fight the step, and the whole knee loop is positive feedback (Lee's rule inverted).

**conclusion: SNpp50 = flexion-tuned, SNpp51 = extension-tuned; run `50flex`.** two lines, independent of each other: the wiring
(§1: five named matches to FANC's identified claw classes; probable) and the phase (§2 + the table: the 13A lock lands in the phase a
flexor-inhibitor belongs to only under `50flex`; an inference, moderate). neither is a measurement. the phase argument has a hole: a
position code locks wherever the joint's extremes fall, and an active-reaction-like reversal in the walking fly (unshown) could
change which phase wants the flexors held.

### what would settle it

1. **a claw recording by type.** a split line for one claw class (the FANC claw-flexion / claw-extension axons are identified, Lee 2025;
   lines exist for the claw as a whole, R73D10, and the Tuthill lab's intersectional claw lines, Chen 2021) imaged or patched under
   imposed tibia movement, its axon matched to SNpp50 or SNpp51 by morphology (NBLAST against MaleCNS / MANC).
2. **anatomy, cheaper.** Mamiya 2018 Fig. 4A shows where the flexion and extension sub-branches sit in each claw branch; Lee 2025 has
   both classes as FANC skeletons. compare the SNpp50 and SNpp51 axons in MaleCNS against either (the sub-branch side, or a FANC ->
   MANC NBLAST of the 8 + 13 claw axons). a day's work with the skeletons; it would turn "probable" into "identified".
3. **the reflex's phase in the fly.** a 13A recording (a line for 13A-10f-α, Syed's primary flexor-inhibitor; its MANC match is
   unknown, IN13A002 is the file's candidate by its inputs and outputs) during tethered walking with leg tracking, or during imposed
   flexion: under `50flex` it depolarises when the tibia is flexed and fires at touchdown / early stance in the hind leg.

### what each labelling means for the body clips of 09-22 / 09-23

- **`50flex` (SNpp50 flexion-tuned; the SEAM's "claw labels swapped"):** negative position feedback at every knee: a flexed knee
  excites the extensor and silences the flexors through the 13As; an extended knee does the reverse through SNpp51 and IN13A006. the
  measured resistance reflex (Azevedo 2020; Lee 2025). **these are the arms where he stood** (the corrected cut: 2 % of his weight on
  the floor, feet carrying 10.3 uN; the full stack: 0 %, 10.7 uN) and where the left front leg stepped under the ring (the x8 loop
  fit). they are the
  sourced sign, and their results stand as the model's.
- **`50ext` (SNpp50 extension-tuned; "as printed"):** positive position feedback at every knee. a standing fly's knee drifts extended,
  SNpp50 fires, the extensor is excited and the flexors are held off by IN13A002, so the knee extends further:
  **the runaway, the extensors at 13-16 Hz, the legs splayed, 64 % of his weight on the floor.** these arms are a wiring-sign error,
  not a result about his muscles or his command. keep them as the control only.
- **for the ledger:** row 1 can move from "unknown" to "inferred from the wiring (Lee 2025's rule and Syed 2026's 13A motif, five
  matches in the file), not measured", with `50flex` as the arm of record. row 7's "flexion-tuned claw (as labelled) at 40 Hz" was
  SNpp51, which on this reading is the extension-tuned class: the cord arms of 09-22 in which the flexors first fired "from a sensory
  story alone" (SNpp51 40 Hz + touch: flexors 2.3 Hz, IN13A006 21 Hz) told a flexed standing knee that it was extended. the same
  arm under `50flex` (SNpp50 at 40 + touch) gave IN13A002 85 Hz, extensors 13.8, flexors 0.00: a flexed knee pushed back toward
  extension: the resistance reflex's sign (whether a standing fly's flexors should then be silent is not measured). `body_loop.py`'s default (`50ext`) and the tuning column of
  `E_table_male.md` / `leg_senses_map.md` are the owner's to change; nothing was edited here.

---

## the query (D)

`data/connectome-weights-male-cns-v1.0-minconf-0.5.feather` joined to the `type` column of
`data/body-annotations-male-cns-v1.0-minconf-0.5.feather`, weights summed per (pre type, post type) over all legs and segments; the
whole release (no 5-synapse floor). SNpp50 62 cells, SNpp51 32. the clip's angles: `kd_a_walk.npz` `knee` + `kin_swing`, FTi = 180 -
(knee_neutral + knee) with knee_neutral 78 / 103 / 101 deg (front / middle / hind), as `body_loop.py` computes the claw's null.

## sources

- Mamiya A, Gurung P, Tuthill JC (2018) *Neuron* 100:636. DOI 10.1016/j.neuron.2018.09.009 (PDF read)
- Mamiya A et al. (2023) *Neuron* 111:3230. DOI 10.1016/j.neuron.2023.07.009
- Lee S-YJ, Dallmann CJ, Cook A, Tuthill JC, Agrawal S (2025) *Nat Commun* 16:4105. DOI 10.1038/s41467-025-59302-3 (PMC12048489, read)
- Syed DS, Ravbar P, Simpson JH (2026) Inhibitory circuits control leg movements during *Drosophila* grooming. *eLife* 14:106446
  (https://elifesciences.org/articles/106446; PMC12844901; preprint PMC11185647, read)
- Marin EC et al. (2024) *eLife* 13:RP97766
- Agrawal S et al. (2020) *eLife* 9:e60299. DOI 10.7554/eLife.60299
- Chen C et al. (2021) *Curr Biol* 31:5163. DOI 10.1016/j.cub.2021.09.035
- Dallmann CJ et al. (2025) *Nature* 647:445. DOI 10.1038/s41586-025-09554-2 (PMC13070307, read)
- Lesser E et al. (2024) *Nature* 631:369. DOI 10.1038/s41586-024-07600-z
- Pugliese et al. (2026) Connectome simulations identify a central pattern generator circuit for fly walking. bioRxiv
  10.1101/2025.09.12.675944 v2 (PMC13142387, read)
- Sapkal N et al. (2026) Central versus peripheral neural control of a coordinated walking pattern in *Drosophila*. bioRxiv
  10.64898/2026.04.29.721658 (read)
- Haustein M, Blanke A, Bockemühl T, Büschges A (2024) *Front Bioeng Biotechnol* 12:1357598. DOI 10.3389/fbioe.2024.1357598
- Schmidt J, Fischer H, Büschges A (2001) *J Neurophysiol* 85:354. DOI 10.1152/jn.2001.85.1.354 (abstract)
- Büschges A, Wolf H (1995) *J Neurophysiol* 73:1843. DOI 10.1152/jn.1995.73.5.1843 (abstract)
- Driesang RB, Büschges A (1996) *J Comp Physiol A* 179:45. DOI 10.1007/BF00193433 (abstract via search)
- Bässler U, Büschges A (1998) *Brain Res Rev* 27:65 (as cited in `walking_review.md`)
