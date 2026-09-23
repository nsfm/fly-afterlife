# octopamine as a state: a design for campaign item 5

Written 2026-09-22 for `docs/CAMPAIGN.md` item 5 ("neuromodulation as a state"). Builds on `knobs.md` §4. Nothing in the engine
has changed. This file is the census, the biology with marks, the proposed term and its first arm, and where the line runs.
Marks are the same as in `knobs.md`: **(M)** measured in *Drosophila* (with the preparation named), **(C)** measured in another
insect (animal named), **(D)** derived here from MaleCNS v1.0, **(E)** our estimate or modelling prior.

The census is reproducible: `uv run python experiments/oa_census.py` (add `--brain brain_cord_all.npz` for every edge, `--unclear`
for the EN/EA efferents whose transmitter the prediction leaves `unclear`). The script only reads the npz and runs no simulation.

---

## 1. the cells (D)

### 1a. who they are

`brain_cord.npz` has **50 cells whose consensus transmitter is octopamine**: 49 `vnc_efferent` and 1 `efferent_ascending`. All
are unpaired midline cells (side `M`, the DUM/VUM plan). The engine gives every one of them **sign 0**, so the 208 output
synapses they make in the file deliver nothing, and their action in the model is zero today. By exit nerve (the annotation
table's `exitNerve`), they fall into three groups:

| group | types (cells) | exit | in (synapses per cell) | out |
|---|---|---|---|---|
| **leg** | **EN00B008** (3: one per neuromere) | 816918 ProLN, 813264 MesoLN, 813201 MetaLN | 400 / 1,212 / 1,046 | 49 / 129 / 30, almost all onto other OA efferents |
| dorsal thoracic (wing, neck, notum) | EN00B001 (1, ADMN), EN00B011 (2, ADMN+MesoAN), EN00B015 (3, ADMN / DProN), EA00B022 (1, CvN), mesVUM-MJ (1, PDMN), EA00B006 (1, no exit) | | 755-4,483 | 0-65, all onto OA cells |
| abdominal | EN00B002, 003, 004, 010, 012, 013, 016, 017, 018, 019, 020, 023, 024, 025, 026, 027 (38 cells) | AbNT / AbN1-4 | 313-10,477 | 0-25 |

The 32 `unclear` EN/EA cells (`--unclear`) are left/right pairs, not midline cells (EN21X001 on DProN, ENXXX226 on ADMN / DMetaN,
EAXXX079, EA27X006). None exits a leg nerve. **The only octopaminergic cells in the leg nerves are the three EN00B008.**

**Two corrections to `knobs.md` §4a** (not edited there; flagged here): the input counts 1,046 / 1,212 / 400 are, in that order, the
**Meta- / Meso- / Pro**thoracic cells, not Pro / Meso / Meta. And DNg100's synapses land on the **T3 and T2** cells (32 and 23);
the T1 cell gets 7.

### 1b. their inputs

**EN00B008**, the three cells pooled (2,658 synapses): **DNp68** 716 (ACh, +, 26.9 %), **IN05B003** 576 (GABA, -, 21.7 %), IN03B054
255 (GABA, -), IN18B012 109 (ACh), **DNge135** 106 (GABA, -), INXXX216 94 (ACh). DNg100 comes lower on the list.

Other thoracic OA types for comparison: EN00B015 has DNp68 574, IN03B088 504 (GABA), IN03B054 494 (GABA), DNg32 304. EN00B001 has IN03B054
1,105 (GABA), IN18B026 663, DNp48 630, DNg03 362. mesVUM-MJ has IN19B057 601 and IN06B085 392 (GABA). The abdominal cells are dominated by
INXXX149 (ACh, 4,855 synapses across eight types) and DNpe034 (ACh, 3,591 onto four types).

### 1c. the descending neurons onto them

Out of 71 DN types that make >= 5-synapse edges onto OA cells, these are the largest: **DNpe034** 3,591 (abdominal cells), **DNp68** 2,455,
DNp48 1,395, DNp13 1,236, DNge172 728, DNg03 693, DNg32 525.

| DN | onto EN00B008 | edges (DN side -> cell's neuromere) | share of that DN's cord output going to OA cells |
|---|---|---|---|
| **DNp68** (ACh) | **716** | L->T2 295, L->T3 217, L->T1 89, R->T3 54, R->T2 32, R->T1 29 | **2,455 of 5,691 = 43 %**. Its other large target is INXXX008 (1,027) |
| **DNg100** (ACh, the walking command) | **62** (66 in `_all`) | R->T3 25, L->T2 13, R->T2 10, L->T1 7, L->T3 7 (+ R->T1 4 below the floor) | **62 of 21,469 = 0.3 %** |
| DNge135 (GABA) | 106 | | |
| DNge050 / DNp46 / DNge049 / DNg27 | 66 / 62 / 32 / 32 | | |

So the file has a DN whose job looks like "recruit the thoracic OA cells": DNp68 sends almost half its cord output to them.
The same DN is reported to take input in the brain from pC1d and aIPg (the arousal / aggression circuit) and from a song-responsive pC2l
cell (the sexual-dimorphism connectome paper, PMC12259084; female FlyWire, D, not checked in MaleCNS). The walking command touches
the leg OA cells with a fraction of a percent of its output.

**A probe run of the cells in the engine** (`world/cord.py`, seed 11, 8 s, the default floor with the load at 15 Hz, `--log-v`;
run for this file and not in the record):

| drive | EN00B008 membrane (re rest; threshold 7 mV) | EN00B008 rate |
|---|---|---|
| none (the cord at rest) | 0.00 mV | 0.0 Hz |
| DNg100 at 100 Hz (78 Hz delivered) | +1.45 mV | **0.0 Hz** |
| DNg100 at 400 Hz | +3.40 mV | 0.33 Hz |
| DNg100 + DNp68, both at 100 Hz | +3.0 mV (sd 1.45) | **59 Hz** (EN00B015 47, EN00B017 71) |

**Under the walking command alone, the leg OA cells in this engine are silent.** If the state is computed from them, it is zero in
every arm the record has run. That is the most important fact for the design (§3d).

---

## 2. the biology

### 2a. Drosophila, measured (M)

- **Octopamine's effect on an adult fly leg motor neuron or premotor interneuron has never been recorded.** Not in mV, not as a
  percentage (`knobs.md` §4b; I searched again and found nothing).
- **The one direct fly measurement of OA on a motor neuron is null.** In larval RP2 motor neurons, OA at 1 and 10 µM "had no effect on MN
  responses to current injection". Tyramine at 10 µM increased the delay to the first spike and lowered the firing rate, through the
  honoka receptor and L-type Ca²⁺ current, with no change in threshold or input resistance (Schützler et al. 2019, *PNAS* 116:3805,
  PMC6397572). Larva, far. It is the only number, and it points against an "MN excitability up" term.
- **Octβ2R sits on larval glutamatergic motor neurons.** It drives activity-dependent NMJ growth through cAMP/CREB over hours, and it
  is also the autoreceptor on the OA terminals (Koon et al. 2011, *Nat Neurosci* 14:190, PMC3391700). This is a structural and
  plastic action, not a millisecond gain.
- **At the larval muscle**, exogenous OA lowers muscle input resistance, raises EJP amplitude, and increases contraction force and
  duration (Ormerod et al. 2013, *J Neurophysiol* 110:1984). This acts on the muscle side, where the body lives, not in the LIF.
- **Adult OA/TA terminals reach skeletal muscles all over the body, including the legs, and the leg sense organs** (Pauls et al. 2018,
  *Sci Rep* 8:15314, anatomy). This matches EN00B008 exiting the leg nerves.
- **Receptor expression by cell type in the adult VNC:** all five OA receptors are expressed broadly in the VNC, and all five in the
  Tdc2 cells themselves, so autoreception is general (McKinney et al. 2020, *J Comp Neurol* 528:2174, MiMIC-Gal4). The VNC scRNA atlas
  lists amine receptors as cluster markers but gives no OA receptor per hemilineage (Allen et al. 2020, *eLife* 9:e54074). **Which of the
  13A / 13B / 19A / 12B hemilineages or leg motor pools express Oamb / Octβ1R / Octβ2R is not known.** I found no source.
- **Behaviour:** flies without octopamine (TβH nulls) walk. In Buridan's paradigm their walking speed changes, the phenotype depends on
  gene dose, and OA and TA receptor mutants take part in it (Damrau, Colomb & Brembs 2021, *PLoS Biol* 19:e3001228). They fly, but start
  and sustain flight worse (Brembs et al. 2007, *J Neurosci* 27:11122). Octopamine is necessary and sufficient for
  starvation-induced hyperactivity (Yang et al. 2015, *PNAS* 112:5219). Adult Tdc2 nulls, with neither OA nor TA, have reduced
  activity (Tdc2 RO54; Crocker & Sehgal 2008, *J Neurosci* 28:9377). **OA modulates how much and how fast a fly walks. It is not a gate on stepping.**
- **Timescale, the only fly number:** in the larval VNC, a 2 s CsChrimson drive of Tdc2 cells releases 0.22 ± 0.03 µM OA, and it
  clears with **t50 = 1.4 ± 0.1 s**. DAT and SERT blockers do not change that, and no OA transporter is known (Pyakurel, Privman Champaloux
  & Venton 2016, *ACS Chem Neurosci* 7:1112, PMC4988909). If the decay is exponential (our assumption), tau ≈ 2.0 s. The time from
  receptor to effect (GPCR, cAMP) has not been measured in the fly VNC.
- **Firing of fly OA cells:** the OA-DNs VUMd fire 4.1 ± 3.1 Hz and do not change during locomotion. VPM and VL cells rise with leg
  movement (Babski, Codianni & Bhandawat 2024, *Heliyon*, PMC11064449). Adult, whole-cell, but these are brain cells that the headless
  cut removes. **No one has recorded EN00B008 or any thoracic leg DUM cell in the fly.**
- **What the fly uses to gate leg proprioception during walking is GABA, not OA:** the movement-encoding FeCO axons (hook) are
  presynaptically inhibited during walking and grooming by GABAergic interneurons driven by descending pathways. The position-encoding
  (claw) axons stay active (Dallmann et al. 2025, *Nature* 647:445). That circuit is in the wiring already.

### 2b. borrowed (C), with sign and rough size

| effect | animal, preparation | sign | size | source |
|---|---|---|---|---|
| **resistance reflex of the femur-tibia joint suppressed** at the motor-neuron level while the "active reaction" (reflex reversal) is spared or facilitated | stick insect (*Carausius*), OA injected into haemolymph, or topical on the desheathed mesothoracic ganglion | gain down | injection: activation for 3.5-12 min, then loop gain **0** for 15-20 min. topical: complete suppression, dose-dependent, **from 5 mM** | Büschges, Kittmann & Ramirez 1993, *J Neurobiol* 24:598 |
| **flexor tibiae motor neurons depolarised and more excitable**. FETi→flexor EPSP reduced (slow flexors at 1 mM, both at 10 mM). FETi spike broadened, AHP reduced. More synaptic input onto the tibial MNs. **Rhythmic flexor activity and reciprocal flexor/extensor activity** can appear | locust (*Schistocerca*) metathoracic ganglion, bath or ionophoresis | excitability up | mM, pharmacological. mV not in the abstract | Parker 1996, *J Comp Physiol A* 178:243 |
| walking tonic depolarisation of motor neurons **increased** by OA and **decreased** by mianserin, **through premotor neurons, not the MN** (in vitro, OA *reduces* the ACh current on the MN soma) | stick insect, single-leg treadmill, ganglion-restricted bath | tonic drive up | tonic depolarisation is <= 5 mV in total (`knobs.md`); the OA share is not given | Westmark, Oliveira & Schmidt 2009, *J Neurophysiol* 102:1049 |
| **tonic position-sensitive FeCO afferents** fire more at every position; velocity and acceleration sensitivity unchanged | stick insect (*Cuniculina*), fCO nerve and single afferents | position gain up | threshold **5 x 10⁻⁷ M**, dose-dependent | Ramirez, Büschges & Kittmann 1993, *J Comp Physiol A* 173:209 |
| tonic firing up **only in afferents tonic at flexed angles**, not extended. Phasic spiking unaffected. **Tonic presynaptic inhibition of the terminals up** too, which partly cancels the extra spikes | locust metathoracic feCO | flexion-position gain up, then partly cancelled centrally | threshold 10⁻⁶ M | Matheson 1997, *J Exp Biol* 200:1317 |
| descending DUM (OA) spikes **increase load-evoked reflex responses** in retractor coxae MNs (positive feedback). Mixed effects on extensor tibiae. Often with reflex reversal. The desDUM cells are driven in stance by leg load sensors, not by the CPG | stick insect, treadmill, desDUM from the gnathal ganglion | load feedback up | not given in the abstract | Stolz et al. 2019, *J Neurophysiol* 122:2388 |
| thoracic efferent DUM cells **tonically depolarised during stepping**, with extra stance-coupled depolarisation. Multimodal. Never hyperpolarised | stick insect, mesothoracic DUMs, single-leg stepping | | 6-8 efferent DUMs per segment | Mentel, Weiler, Büschges & Pflüger 2008, *J Insect Physiol* 54:51 |
| only 3 of 20 metathoracic DUMs spike during a kick, **bursts up to 25 Hz, 3-15 spikes**, locked to the co-contraction phase. The others are inhibited or sporadic | locust | | | Burrows & Pflüger 1995, *J Neurophysiol* 74:347 |
| **plateau potentials and endogenous bursting induced** in flight and respiratory interneurons and some MNs | locust | conditional plateaus on | pharmacological | Ramirez & Pearson 1991, *Brain Res* 549:332; *J Neurophysiol* 66:1522 |
| DUMETi (OA, leg DUM onto the extensor tibiae) slows the muscle's myogenic rhythm | locust, muscle | muscle side | | Evans & O'Shea 1978, *J Exp Biol* 73:235 |

**What the table licenses.** Every magnitude comes from bath application at 10⁻⁶ to 10⁻² M, or from injection. None is a physiological
release. The signs agree across two insects on three points:
1. the resistance-reflex pathway is turned down, centrally;
2. tonic, position-coding afferents are turned up;
3. motor output in the active state is supported (tonic drive up through premotor cells; flexor MNs more excitable in the locust).

The motor-neuron sign conflicts with the only fly measurement (§2a, larval RP2: no effect). Nothing I found says octopamine
weakens *inhibitory* premotor output. The "13A inhibition down" target named in the brief has **no source**. Where it would come
from, if anywhere, is item 1 above: the pathway from the position sense to the extensor-favouring inhibitors is the resistance reflex.

**A conflict with our target.** In our file, the 13A winners are driven by the claw afferents (SNpp50: 5,517 synapses onto the four
tonic inhibitors) and by the rest of the position sense. Borrowed effect 2 (afferents up) applied to *all* claw cells therefore
**strengthens** the cells that hold the flexors silent. Borrowed effect 1 (the central pathway down) weakens them. The net sign on
IN13A002 is not known in advance. Only Matheson's locust asymmetry (flexion-tuned tonic afferents up, extension-tuned not) points
in the direction the campaign wants: the 13B side's live sensory input is SNpp51 (2,084 synapses, `docs/SEAM.md` "the 13B side").
Which of SNpp50 / SNpp51 is the flexion-tuned one is ledger row 1, so any claw target runs under both labellings.

---

## 3. the design

### 3a. the state, from the real cells

One slow variable per run, computed from the spikes of the named source cells. The default source is the three EN00B008. It is
computed each engine step, in two stages:

    r   += (1000 * n_spk / (N_src * dt) - r) * dt / tau_c        # Hz: low-passed mean rate of the source cells (release + clearance)
    a_in = r / (r + R50)                                          # 0..1: receptor occupancy, a saturating map (E)
    a   += (a_in - a) * dt / tau_e                                # 0..1: the second-messenger lag (E)

- `tau_c` = **2000 ms** by default: the larval VNC's OA clearance, t50 1.4 s, read as exponential (M, far + E). Sweep 1000-4000.
- `tau_e` = **10,000 ms** by default, swept 1-30 s. It has no fly number. The stick-insect minutes are drug kinetics after injection
  and cannot be used. A 30 s cord run with a 2 s warm-up sees at most about a tau of 10 s, so longer values need longer runs.
- `R50` = **10 Hz** by default, swept 3-30. There is no rate for EN00B008. The anchors are fly OA-DNs at 4 Hz tonic and locust
  DUM kick bursts up to 25 Hz (E).
- **per neuromere** as an option (`--oa-seg`): each EN00B008 sets the state for its own neuromere, and targets take the state of their
  soma neuromere (motor neurons from their fl/ml/hl subclass, interneurons from the annotation table's soma neuromere). Leg DUMs release
  into their own ganglion and nerve, and DNg100 favours the T3 and T2 cells (32 / 23 synapses vs 7). The global mean is the first
  version.
- Source spikes come from the ordinary LIF. EN00B008 is not a driven cell, so it integrates its synapses. Its sign-0 outputs stay at
  zero: the state is the only route octopamine has into the model.
- `--oa-clamp A` holds `a` at a constant and ignores the source. It is the open-loop control.

### 3b. the targets, each labelled

Each target has a gain `G` and is applied as `1 + G * a`, or as `G * a` mV for a bias. One target per run first, as the working
habit asks. Confidence: **low** means the sign is borrowed and a fly measurement contradicts it or none exists. **medium** means two
insects agree on the sign and the magnitude is only pharmacological.

| target | what it scales | cells, defined by the sense or by class, never by the result | sign, ceiling | source | confidence |
|---|---|---|---|---|---|
| `resist` | synapses from the leg proprioceptive afferents onto cord interneurons, x (1 - G a), G in [0, 1] | pre `SNpp*` (all), or `claw` only (SNpp50/51), post `IN*`: 25,826 edges, 396,697 synapses (all SNpp->IN) | down, to 0 at full dose | Büschges 1993 | **medium** on sign (the pathway), **low** on locus: the stick insect does not name the central site, so "SNpp onto INs" is our reading of "the resistance-reflex pathway" |
| `claw` | the tonic rate of the claw (position) afferents' stand-in, x (1 + G a) | the floor stand-in's claw rows (`cord.py` REG). On the body, the proprioceptor encoder's position channel | up. G <= 1 (E) | Ramirez 1993 (all position afferents), Matheson 1997 (flexion-tuned only) | **medium**. Variants `claw` (both types) and `claw_flex` (the flexion-tuned type only, **both labellings**) |
| `mn` | a depolarising bias on leg motor neurons, G a mV, on the ext path | vnc_motor, subclass fl / ml / hl | up. G <= 5 mV (the stick-insect walking tonic depolarisation, the whole of it) | Parker 1996 (locust flexors), Westmark 2009 (via premotor) | **low**: the one fly measurement is null (Schützler 2019) |
| `plateau` | gates the plateau term (item 4, not built) on the cells it names | as item 4 names them | on / off with a | Ramirez & Pearson 1991 | **low**, and waits on item 4 |
| `loadfb` | load-sensor (campaniform) -> coxa retractor MN pathways, x (1 + G a) | | up | Stolz 2019 | **not for the headless arm**: the source there is descending DUMs from the gnathal ganglion, cut in our preparation. Listed so nobody wires it to EN00B008 |
| (muscle) | twitch force and relaxation, myogenic rhythm | the body's muscles | | Ormerod 2013, Evans & O'Shea 1978, Pauls 2018 | physics side. Not in the LIF |

**There is deliberately no `13A` target.** Scaling the output of IN13A002 because it is IN13A002 would tune the one neuron we are
reading to get the answer we want. The campaign's line calls that a puppet. The 13A cells are read as outcomes of `resist` and `claw`.

### 3c. what it takes in `world/fastlif.py` (described, not implemented)

- **A parser, `set_oa(spec)`**, the same shape as `set_syn_tau` / `set_syn_rev`: one parser shared by `world/cord.py` and
  `experiments/body_loop.py`, returning a line for the log, off by default.
  Flags: `--oa TARGET:GAIN[,TARGET:GAIN...]` (e.g. `resist:0.5` or `mn:2,resist:0.5`), `--oa-src TYPES` (default `EN00B008`),
  `--oa-tau TAU_C:TAU_E` in ms (default `2000:10000`), `--oa-r50 HZ` (default 10), `--oa-clamp A`, `--oa-seg`.
- **The state update** goes after `last_idx` is known in `step()`, next to the adaptation and depression updates: three float
  operations on a scalar (or three, per neuromere). It adds no RNG draws, so **a = 0 must reproduce the control bit for bit**. That is
  the oracle for this term, and it can be checked cheaply.
- **`mn`** goes on the ext path the way `adapt` / `rebound` do (`ext = ext + bias_mask * G * a`). The compiled membrane kernels are not
  touched.
- **`resist`** keeps a copy `w0` of the masked `_out_w` entries and rewrites `_out_w[mask] = w0 * (1 - G a)` **once per 10 ms frame**,
  not per step (a moves on seconds; 25,826 edges is one vector multiply). It composes with `--syn-tau` / `--syn-rev`, because those
  read `_out_w` on each arrival, and with `--size-gain` / `--edge-scale` / the mirror, which edit `_out_w` before the run: take `w0`
  after those. Under `--std` the per-emission scale multiplies on top, which is as it should be.
- **`claw`** is not an engine term. The stand-in's rate lives in `cord.py`'s `Registry`, so the frame loop multiplies the claw rows'
  `transducer.hz` by `(1 + G a)`, reading `a` from the engine. On the body it goes where the proprioceptor encoder sets rates.
- **Logging:** `a` and `r` per frame into `<out>.cells.npz` (`oa_a`, `oa_r`), so every arm reports the state it actually reached.

### 3d. the first arm and its controls

Cord, `brain_cord.npz`, seeds 11 and 12, 30 s, `--integrate exact`, load 15 Hz, `--log-ms`. The logged set is IN13A002, IN13A005,
IN13B019, IN13A006, AN06B002, IN21A004, IN03A004, the tibia flexor and extensor MNs, EN00B008 (with `--log-v`), and Pugliese's
subnet for the 20 Hz line.

**Block A, the walking command alone (the brief's arm).**
- A0: DNg100 100 Hz, OA off.
- A1: A0 + `--oa resist:1` (then `claw`, `claw_flex` both ways, `mn:2`, one per run).
- A2: A1 + `--silence EN00B008`.

The prediction, made before the run from §1c: EN00B008 sits at +1.45 mV under the command, `a` stays near 0, and **A1 = A2 = A0**,
bit for bit. That result is worth having as it stands: **the headless walking command does not recruit the leg OA cells in this
engine.** DNg100 400 Hz (0.33 Hz from EN00B008) is the dose check.

**Block B, the OA cells recruited through their own DN.**
- B0: DNg100 100 Hz + DNp68 at a rate, OA off. This is a new control: DNp68 has other outputs (INXXX008, 1,027 synapses; MNhl59,
  113), so A0 is **not** its control.
- B1: B0 + OA on, one target per run.
- B2: B1 + `--silence EN00B008`. Only the state's source is removed; DNp68's other outputs stay.
- B3: B2 + `--oa-clamp` at B1's mean `a`. Open loop: the level of the state without the cells' dynamics.
- DNp68 is swept at 10 / 30 / 100 Hz so that the state runs through its range. It is a labelled second command: a DN that exists,
  whose brain inputs are arousal cells, standing in for the brain the headless preparation does not have. It gets a ledger row if
  it is kept.

Read in each arm: IN13A002 and IN13B019 rates, tibia flexor rate per cell, the 20 Hz line (frequency and height), `a` over time,
and the cord's mean rate. The last one shows whether a target dims or brightens everything, the way item 2 did.

### 3e. what would falsify it

- **The mechanism is not there**: B1 (or any target inside its ceiling) leaves IN13B019 under ~1 Hz and the flexors under ~0.5 Hz, and
  the 20 Hz line stays at 17-23 Hz. Then item 5 is not the switch, as items 2 and 3 were not, and that is a statement about the file.
- **The cells are not the cause**: B2 (the source silenced) shows the same effect as B1. Then the change came from DNp68's other outputs,
  and the state is decoration.
- **The story does not reach**: the effect appears only under `--oa-clamp` at values of `a` that EN00B008 never produces under any DN
  drive. The cells cannot make the state that works, so the working state is ours and not theirs.
- **It becomes a gate**: if stepping appears *only* with the state on, the model now says flies without octopamine cannot step. TβH
  nulls walk (slower), and Tdc2 nulls are only less active (§2a). A model that needs OA to step contradicts every null mutant. OA may
  change how fast and how often. It must not be what makes a step possible.
- **It works only through `mn`**: then it rests on a borrowed locust sign, against the only fly measurement. Report it as that.
- **In the fly** (not ours to run, and the most useful to find): silence the Tdc2 VNC cells during headless DNg100 walking (Bidaye's
  preparation). The design predicts at most a change in speed or step frequency, not loss of stepping. Nobody has done it (`knobs.md` §4d).

---

## 4. where the line runs

The source side of this state passes the campaign's test outright. The three EN00B008 are real cells, one per leg neuromere, exiting
the leg nerves. The file's walking command and an arousal-fed DN both synapse onto them. A state computed from their spikes, with a
clearance time measured in the fly's own cord, is a signal generator with a biological story. The target side is thinner. No fly
measurement says which leg cells carry which OA receptor, or what octopamine does to them, and the one fly motor-neuron recording
says it does nothing. What we can apply is stick-insect and locust sign, measured under bath application, onto target sets that we
define: "SNpp onto interneurons" as our reading of "the resistance-reflex pathway". That is honest if every target stays defined by
a sense or a cell class, gets its sign from a paper, and holds its gain inside the pharmacological ceiling, with the result read off
the 13A / 13B cells and never tuned on them. It becomes an algorithm around puppet neurons at three points:

- a `13A` target;
- a gain chosen because it wakes IN13B019;
- a state clamped at a value the cells cannot reach.

And the probe already says what the brief's own arm will find: under DNg100 alone the leg OA cells are silent, so the honest state
is zero, and any octopamine effect in the headless cord has to come from DNp68 or from a brain we cut off. That limit is a finding
about the headless preparation, not a reason to force the state on.

---

## sources opened for this file, not already in `knobs.md`

Schützler et al. 2019 (PNAS, full text via PMC6397572); Koon et al. 2011 (abstract); Ormerod et al. 2013 (abstract via search);
Pauls et al. 2018 (abstract); McKinney et al. 2020 (abstract + full text, PMC7998515); Pyakurel, Privman Champaloux & Venton 2016
(full text, PMC4988909); Damrau, Colomb & Brembs 2021 (abstract); Yang et al. 2015 (abstract); Crocker & Sehgal 2008 (via search, not opened); Dallmann et al. 2025 (abstract);
Parker 1996 (abstract via search; full text paywalled, no mV); Ramirez, Büschges & Kittmann 1993 (abstract via search); Matheson 1997
(abstract); Westmark, Oliveira & Schmidt 2009 (abstract); Mentel et al. 2008 (abstract); Burrows & Pflüger 1995 (abstract);
Ramirez & Pearson 1991 x2 (abstracts); the DNp68 input note from the sexual-dimorphism connectome paper (PMC12259084, via search,
not opened). Not reached: Parker 1996 and Ramirez 1993 full texts (the mV and % numbers), Sombati & Hoyle 1984 (local OA release
into locust neuropil).
