# knobs: measured numbers for campaign items 2-5

Written 2026-09-22 for `docs/CAMPAIGN.md` items 2 (synaptic kinetics), 3 (intrinsic properties), 4 (plateaus, rebound),
5 (neuromodulation), with 6 (senses) and 7 (gap junctions) as short sections. It does not repeat `walking_review.md`,
`leg_biomech.md`, `leg_motor.md`, `mechanosensation.md` or `rate_model_control.md`; where those already hold the number, this file
points at them.

Marks, as in `walking_review.md`: **(M)** measured in *Drosophila*, with the preparation named (adult central / larva /
culture); **(C)** measured in another insect, animal named; **(D)** derived here from MaleCNS v1.0 or by arithmetic on
cited numbers; **(E)** estimate or modelling prior. Every row also says how far it transfers to **adult VNC neurons**:
*direct* (adult VNC cell of the kind in question), *near* (adult fly central neuron elsewhere), *far* (larva, culture,
or another insect). "not found" means I searched and there is no number, not that I didn't look.

The engine these numbers feed (`ref/flybrain/scripts/flysim.py`, `world/fastlif.py`): current-based LIF,
dv/dt = (g - v)/tau_m, dg/dt = -g/tau_syn, a spike adds sign x w x 0.275 mV to g; tau_m 20 ms, tau_syn 5 ms (one for
every transmitter), threshold 7 mV above rest, reset to rest, refractory 2.2 ms, delay 1.8 ms. These are Shiu et al. 2024's.

---

## 1. synaptic kinetics per transmitter

### 1a. what Shiu and Pugliese assumed, and where it came from

Shiu PK et al. 2024, *Nature* 634:210-219, DOI 10.1038/s41586-024-07763-9, Methods (read in PMC11446845):

| parameter | value | their source | what the source is |
|---|---|---|---|
| V_rest / V_reset | -52 mV | Kakaria & de Bivort 2017, *Front Behav Neurosci* 11:8 | a spiking model of the protocerebral bridge |
| V_threshold | -45 mV | Kakaria & de Bivort 2017 | same model |
| R_m, C_m | 10 kOhm cm2, 2 uF/cm2 (tau_m = 20 ms) | Kakaria & de Bivort 2017 | same model |
| refractory | 2.2 ms | Kakaria 2017; Lazar et al. 2021 (FlyBrainLab) | models |
| **tau_syn** | **5 ms, all transmitters** | **Jurgensen et al. 2021, *Neuromorph Comput Eng* 1:024008** | **a neuromorphic model of the larval olfactory system** |
| delay | 1.8 ms | Paul et al. 2015, *Front Cell Neurosci* 9:29 | **larval NMJ glutamate release** |
| W_syn | 0.275 mV | fitted, the single free parameter | |

So **none of the engine's synaptic constants is a measurement of a central fly synapse**; tau_syn and delay are borrowed
from a larval model and a neuromuscular junction. Shiu did not test robustness to tau_syn ("changes to the membrane time
constant ... T_dly ... and the refractory period generally simply change overall firing rates").

Pugliese SM et al. 2026 (bioRxiv 10.1101/2025.09.12.675944 v2, PMC13142387; `research/sources/pugliese_2026_connectome_cpg.md`):
a rate model with **no synaptic kinetics at all**. One per-cell tau ~ N(20, 2) ms, which they say they computed from Shiu's
R_m x C_m; b = 0.03 for every synapse; GABA and glutamate inhibitory, ACh excitatory. Their stated reason for a rate
model is that "many neurons in the insect VNC ... are nonspiking", citing cockroach, locust, stick insect and Agrawal 2020.

### 1b. measured kinetics

| transmitter / receptor | preparation | rise | decay tau | amplitude | conditions | source | transfer |
|---|---|---|---|---|---|---|---|
| ACh, nicotinic (alpha-BTX, curare sensitive) mEPSC | **adult Kenyon cells, isolated whole brain, in situ** | 1.23-1.53 ms | **4.45-6.73 ms** | 3-12 pA, mean 4.0-4.9 pA | -75 mV hold, room temp; KC R_in 1.00-1.13 GOhm, V_rest -60.9 +/- 1.7 mV | Gu & O'Dowd 2006, *J Neurosci* 26:265, DOI 10.1523/JNEUROSCI.4109-05.2006 (M) | near |
| ACh, nicotinic mEPSC | cultured **pupal** KCs, 3-21 DIV | 0.43 +/- 0.05 ms | **1.4 +/- 0.1 ms** | 22.1 +/- 2.1 pA | -75 mV, room temp; KC C 3.6 pF | Su & O'Dowd 2003, *J Neurosci* 23:9246, DOI 10.1523/JNEUROSCI.23-27-09246.2003 (M) | far |
| ACh, nicotinic mEPSC | cultured **embryonic** neurons, 3-9 DIV | 0.61 +/- 0.05 ms | **2.1 +/- 0.2 ms** | 24.8 +/- 1.4 pA | -75 mV, 23-25 C | Lee & O'Dowd 1999, *J Neurosci* 19:5311, DOI 10.1523/JNEUROSCI.19-13-05311.1999 (M) | far |
| ACh, ORN -> PN unitary | **adult antennal lobe in vivo** | "similar across glomeruli", not extracted | two-phase decay, values not extracted | **uEPSC 29.0 +/- 2.6 pA; uEPSP 6.19 +/- 0.45 mV**; q = 1.05 pA, N = 51 +/- 8 release sites, p = 0.79 | -65 mV, 25 C, mecamylamine-blocked | Kazama & Wilson 2008, *Neuron* 58:401, PMC2429849 (M) | near |
| ACh, PN -> LHN unitary | adult lateral horn in vivo, matched to hemibrain | time to peak **7.1-11.9 ms** (somatic uEPSP) | not extracted | **uEPSP 0.4-6.6 mV** across connection types, CV 0.35 | | Liu, Davoudian, Lizbinski & Jeanne 2022, *Curr Biol* 32:559, DOI 10.1016/j.cub.2021.11.056 (M) | near |
| GABA, Rdl (picrotoxin, Cl-) mIPSC | cultured embryonic neurons | ~1 ms (10-90 %) | **~5-6 ms at 2 DIV, falling 1.5-2x by 8 DIV** | 9.9 +/- 0.3 pA (5.5-22) | 0 mV hold, room temp, measured E_rev -41.5 mV (24 mM Cl- internal) | Lee, Su & O'Dowd 2003, *J Neurosci* 23:4625, DOI 10.1523/JNEUROSCI.23-11-04625.2003 (M) | far |
| GABA, picrotoxin-sensitive mIPSC | cultured pupal KCs | 0.80 +/- 0.20 ms | **3.7 +/- 0.9 ms** | 24.6 +/- 3.8 pA | 0 mV hold | Su & O'Dowd 2003 (M) | far |
| GABA-A + GABA-B | adult antennal lobe PNs in vivo | | two conductances: fast (picrotoxin) shapes the early odour response, slow metabotropic (CGP54626) the late phase; LN -> PN paired IPSPs "slow" | not extracted | | Wilson & Laurent 2005, *J Neurosci* 25:9069, DOI 10.1523/JNEUROSCI.2070-05.2005 (M, qualitative only; full text not reachable) | near |
| **glutamate, GluCl (picrotoxin, Cl-)** onto **motor neurons** | **larval VNC**, RP2 / RP3 MNs, optogenetic drive of glutamatergic premotor "looper" INs (~300 ms light) | not reported | **compound IPSC, single-exp tau ~250-350 ms control** (Fig. 9E/G, read off bars), half-width ~400 ms; doubles with Eaat1 block (TBOA or RNAi) | ~10-20 pA (read off traces) | -60 mV hold; reverses at -80 mV (their Cl-) | MacNamee et al. 2016, *J Comp Neurol* 524:1979, DOI 10.1002/cne.24016, PMC4861170 (M) | far, and **not unitary**: it is a train response, so it bounds the unitary decay from above |
| glutamate, GluCl alpha | adult antennal lobe | | **not reported**: glutamate hyperpolarises all AL cell types, blocked by picrotoxin or GluCl-alpha RNAi | | | Liu & Wilson 2013, *PNAS* 110:10294, DOI 10.1073/pnas.1220560110 (M, no kinetics) | near |
| GABA and glutamate, reversal | larval VNC MNs (mostly identified MNs) | | | both inhibitory responses **"reversed near normal resting potential"** (rest -50 to -60 mV) | | Rohrbough & Broadie 2002, *J Neurophysiol* 88:847, DOI 10.1152/jn.2002.88.2.847 (M) | far |
| ACh, muscarinic (mAChR-A excitatory, mAChR-B inhibitory) | | | slow, GPCR; **no VNC kinetics found** | | | | |

**unitary PSP per synapse (mV per synapse), the thing W_syn stands for:**

- ORN -> PN: ~23 synapses per unitary connection (Tobin, Wilson & Lee 2017, *eLife* 6:e24838, PMC5440167, EM) and a
  ~5-6 mV uEPSP (Kazama & Wilson 2008) give **~0.2-0.27 mV peak per synapse at the soma (D)**. By release sites instead
  (N = 51) it is ~0.12 mV. This is a high-release-probability (p = 0.79) synapse, the strongest in the fly literature.
- PN -> LHN: uEPSP scales **linearly with synapse density (synapses per um2 of postsynaptic membrane)**, not synapse count
  (Liu et al. 2022). Their fitted passive model: R_m 17.2 kOhm cm2, C_m 0.6 uF/cm2 (so **tau_m ~10 ms, D**), R_i 350 Ohm cm,
  **0.055 nS peak conductance per synapse**, E_ACh -10 mV, rest -55 mV, spike threshold "15 mV above rest at the SIZ"
  (their citation: Fisek & Wilson 2014; Jeanne & Wilson 2015). This is Pugliese's stated source for size scaling.
- PN passive properties (Gouwens & Wilson 2009, *J Neurosci* 29:6239, PMC2709801): R_in 598 +/- 69 MOhm, R_m 8.3-20.8 kOhm cm2,
  C_m 0.8-2.6 uF/cm2 (so tau_m ~7-54 ms, D), rest -55 to -60 mV, a dendritic uEPSP decays to 10 % by the soma.
- **no unitary PSP has been measured onto any adult VNC neuron, for any transmitter.** not found.
- inhibitory: no unitary IPSP amplitude per synapse in any fly central neuron. not found.

**what the engine gives, for comparison (D, arithmetic on the engine's equation):** peak PSP per synapse =
W_syn x tau_s/(tau_s - tau_m) x (e^(-t/tau_s) - e^(-t/tau_m)) at its maximum.

| tau_syn | tau_m 10 | tau_m 20 | tau_m 30 | charge (area / W_syn) |
|---|---|---|---|---|
| 2 ms | 0.134 W | 0.077 W | 0.055 W | 2 ms |
| 5 ms | 0.250 W | **0.157 W = 0.043 mV** | 0.116 W | 5 ms |
| 10 ms | | 0.250 W | 0.192 W | 10 ms |
| 20 ms | 0.500 W | | 0.296 W | 20 ms |
| 50 ms | 0.669 W | 0.543 W | 0.465 W | 50 ms |

Two consequences for item 2's engine term:

1. **in this engine the charge a synapse delivers is W_syn x tau_syn.** Changing ACh from 5 to 2 ms at fixed W cuts every
   excitatory synapse's drive by 60 %; changing GluCl from 5 to 50 ms multiplies inhibition by 10. The term has to say what
   it holds fixed (peak, or charge), and the choice is itself a knob. Holding W fixed and changing tau is not "just kinetics".
2. the engine's peak per synapse (0.043 mV) is ~5x below the ORN -> PN per-synapse value (~0.2 mV). ORN -> PN is an unusually
   strong synapse, so this is a ceiling, not a target; it says the fitted W_syn is not implausibly large.

**chloride reversal.** GABA-A (Rdl) and GluCl are both Cl- channels. The only fly central measurement of where they reverse
(larval MNs) puts it near rest. A current-based engine lets inhibition hyperpolarise without limit; in life these synapses
are closer to shunting at rest and hyperpolarising only when the cell is depolarised. (The engine's v_floor is the only
thing standing in for this.)

**what this licenses in the model.** ACh (nicotinic) tau_syn **1.5-7 ms** (adult central in situ 4.5-6.7 ms at room
temperature, culture 1.4-2.1 ms); GABA-A fast tau_syn **3-6 ms**, with a slow GABA-B component allowed but unquantified;
**GluCl has no unitary measurement anywhere in the fly**: the only number is a larval train response decaying at ~300 ms,
so any GluCl tau between the GABA-A value and ~300 ms is a named gap, not a measurement (E), and the campaign's bet that
"glutamate is slower" rests on that one compound trace. Per-synapse peak somewhere in 0.04-0.25 mV is inside what is measured
for adult central cholinergic synapses; nothing constrains inhibitory amplitude.

---

## 2. intrinsic properties of adult leg motor neurons

The full Azevedo et al. 2020 extraction is in `research/sources/azevedo_2020.md`, `leg_biomech.md` §B and `walking_review.md` §5.
The numbers the item needs, in one place:

Azevedo AW, Dickinson ES, Gurung P, Venkatasubramanian L, Mann RS & Tuthill JC 2020, *eLife* 9:e56754, DOI 10.7554/eLife.56754.
Female front leg, tibia flexor MNs, whole-cell in vivo, fly still, V corrected for a -13 mV junction potential.

| | fast (R81A07, 1 MN) | intermediate (R22A08, 2-5 MNs) | slow (R35C09, 8-9 MNs) | mark / transfer |
|---|---|---|---|---|
| resting Vm | **-68 mV** (-63..-73) | **-60 mV** (-65..-56) | **-48 mV** (-37..-59) | (M) direct |
| input resistance | **150 MOhm** (80-190) | **300 MOhm** (190-440) | **700 MOhm** (420-900) | (M) direct |
| spontaneous rate, fly still | 0 | 0 | **~30 Hz** (10-52) | (M) direct |
| rate averaged over spontaneous movement | ~1.5 Hz | ~9-10 Hz | ~62 Hz | (M/D) from their data, `leg_biomech.md` §B3 |
| rate under somatic current | cannot be driven from the soma | cannot be driven from the soma | 100-150 Hz at +25..+100 pA | (M) direct |
| spike threshold | **not measured** | **not measured** | **not measured** (fires at rest, so threshold at the SIZ sits near or below its -48 mV rest as seen from the soma) | |
| membrane time constant, capacitance | **not reported** | **not reported** | **not reported** | |
| force per spike | ~10 uN | ~1 uN | ~0.013 uN | (M) |
| n cells | 15 | 11 | 14 | |

- other flexor MNs (their Fig. 4-S1): one at -67 mV silent; one at -55 mV silent; one at -53 mV firing 12 Hz; one
  (R81A04) at -51 mV, 28 Hz, 486 MOhm. **the pool is a continuum, not three bins (M).**
- **recruitment order** slow -> intermediate -> fast; only 110 of 3,082 intermediate spikes were not preceded by a slow
  spike (M).
- **the slow MN's resting firing is partly synaptic:** 1 uM MLA (nicotinic block) lowered its spontaneous rate and cut resting
  force by ~1.5 uN (M). So "slow cells fire with no input" is wrong in the fly: they fire with little input, and the
  standing cholinergic input is part of it.
- sensory drive: passive extension of 8 deg gives an **~8 mV compound EPSP** in a flexor MN; sensory delays similar in fast and
  intermediate (M).
- **anatomy:** soma, primary neurite and axon diameter all ordered fast > intermediate > slow (p < 0.01), no absolute values
  in the text (M).
- **size -> input (Lesser et al. 2024, *Nature* 631:369; `research/sources/lesser_2024.md`):** leg MN input synapse count is
  linear in MN surface area, **0.34 or 0.45 synapses/um2** (the preprint contradicts itself), r = 0.94-0.95; within a
  module each premotor cell's weights onto the MNs are proportional to MN size (PC1 > 80 % of variance), for excitatory
  and inhibitory premotor cells alike (M, EM). Insect MN somata receive almost no synapses.
- **extensors (SETi, FETi), other joints, other legs: no fly recording exists.** not found. Driver lines for the tibia
  extensors exist (Venkatasubramanian et al. 2019) but no physiology.
- **nearest adult VNC motor-neuron physiology outside the leg:** flight MN1-5 (DLM), Hurkey et al. 2023, *Nature* 618:118,
  DOI 10.1038/s41586-023-06099-0: rest ~-60 mV, tonic firing, f-I nearly linear over ~2-30 Hz, homoclinic spike onset
  set by Shab (Kv2) density (M, near: adult VNC MNs, different pool).
- **Pugliese's size scaling:** a_i = a*_i / s_i, theta_i = theta*_i x s_i, s = volume / median volume. The *form* is sourced:
  Liu et al. 2022 (PSP proportional to synapses per unit area) plus their stated assumption that volume scales roughly
  with surface area. The *magnitudes* (theta* ~ N(7.5, 0.6), a* ~ N(1, 0.1), r_max 200 Hz) are not physiological
  measurements; they are chosen ranges. Our `rate_model_control.md` found synapse count a poor proxy for their volume
  (log r = 0.87 but big cells overstated 2-3x).

**derived (D):** at equal synaptic current the slow MN depolarises 700/150 = **4.7x** as far as the fast MN. If each MN's
input scales with its area (Lesser) and its R_in with 1/area, the per-synapse PSP is size-independent and recruitment
order comes from rest and threshold, which is where Azevedo's 20 mV rest gradient sits.

**what this licenses in the model.** Per-class resting potential offsets are measured: slow -48, intermediate -60, fast
-68 mV (a 20 mV spread, with ~10 mV spread inside each class), and R_in ratios 4.7 : 2 : 1 are measured; spike threshold
and tau_m for any leg MN are not, so how the 20 mV splits between "rest" and "threshold" in an LIF is free (E). A shared
threshold near -45 mV (Shiu's value, not a fly MN measurement) would put slow cells ~0-8 mV from threshold, intermediate
~15 mV and fast ~23 mV. tau_m for any fly central neuron is measured at 7-54 ms (PNs), fitted at ~10 ms (LHNs); 10-40 ms is
the honest range for MNs, per class unconstrained. Anything per-cell for the tibia extensors or other joints is (E).

---

## 3. interneuron intrinsic properties: plateaus, rebound, graded release

### 3a. Drosophila, measured

- **premotor / second-order leg cells (adult, front leg, whole-cell):** 13B-alpha (GABA) **no action potentials**, tonic,
  non-adapting, hysteretic readout of FTi angle; 10B-alpha (ACh) **no reliable spikes**; 9A-alpha (GABA) spiking
  (Agrawal et al. 2020, *eLife* 9:e60299; table in `walking_review.md` §2) (M, direct). **no recording exists for 13A, 19A,
  21A, 20A/22A, 03A, 12B, 16B, 17A, 14A premotor cells.**
- adaptation in second-order cells is circuit-level: picrotoxin (10 uM) reduced it in 10B-alpha and 13B-beta, and 13B-alpha did not
  adapt over 30 s (Agrawal 2020; `leg_biomech_parts/E_proprioceptors.md`) (M, direct).
- **plateau potentials in any adult fly VNC neuron: not found.** persistent inward currents in adult leg MNs: not found
  (`walking_review.md` §5 agrees).
- **post-inhibitory rebound, fly VNC, indirect only:**
  - adult VNC song circuit: "mutual inhibition and rebound excitability" between pulse- and sine-driving nodes, inferred from
    behaviour after optogenetic offset (rebound sine after pIP10, rebound pulse after TN1, both in headless males) plus
    two-photon calcium imaging of Dsx+ VNC neurons, and a model; **no membrane recording of rebound**
    (Roemschied et al. 2023, *Nature* 622:794, DOI 10.1038/s41586-023-06632-1, PMC10600009) (M, behaviour/imaging; wing
    neuropil, not leg).
  - larva: A02l cholinergic interneurons are tonically active, transiently suppressed (hyperpolarised, by voltage imaging)
    and rebound during each wave (Date et al. 2026, bioRxiv 10.64898/2026.01.19.700243, preprint) (M, larva, far).
  - larva: hyperpolarising Tdc2+ neurons suppresses fictive rhythms and gives a "short-lasting, post-inhibitory rebound in
    fictive activity" (Smith, Hibbard & Pulver 2026, bioRxiv 10.64898/2026.08.04.742787, preprint) (M, larva, network level, far).
- larval MNs carry a persistent Na current modulated by DmNav splicing (Lin et al. 2012, *J Neurosci* 32:7267, PMC3400946);
  magnitudes not extracted (M, larva, far).

### 3b. borrowed from larger insects (C, far)

| property | animal, cells | number | source |
|---|---|---|---|
| graded release without spikes | locust metathoracic nonspiking local interneurons -> leg MNs | some release tonically at rest; others need **~2 mV** depolarisation to release; Vm fluctuates **up to 15 mV** during leg movement; single PSPs up to **5 mV** | Burrows & Siegler 1978, *J Physiol* 285:231, DOI 10.1113/jphysiol.1978.sp012569 |
| rhythm in nonspiking premotor cells | stick insect mesothoracic, deafferented, pilocarpine | **83 % of 67** nonspiking INs oscillate with the motor rhythm; current injection **resets** the rhythm | Büschges 1995, *J Neurobiol* 27:488, DOI 10.1002/neu.480270405 |
| walking-state tonic depolarisation of MNs | stick insect middle-leg MNs during front-leg stepping | tonic depolarisation **<= 5 mV**, reversing at **-32 to -47 mV**, with ~**12 %** fall in membrane resistance | Ludwar et al. 2005, *J Neurophysiol* 94:2772, DOI 10.1152/jn.00493.2005 |
| alternation mechanism | stick insect tibial MNs, deafferented | bursts shaped by **phasic inhibition on a tonic depolarising drive**; alternation in ~25 % of trials | Büschges et al. 2004, *Eur J Neurosci* 19:1856, DOI 10.1111/j.1460-9568.2004.03312.x |
| sag (I_h-like), a rebound substrate | stick insect MNs during walking/searching | **only fast flexor MNs** show a depolarising sag after hyperpolarisation; all MNs show spike-frequency adaptation | Schmidt, Fischer & Büschges 2001, *J Neurophysiol* 85:354, DOI 10.1152/jn.2001.85.1.354 |
| MN plateau potentials | cockroach fast coxal depressor Df | soma plateaus immediately after dissection, spikes after 1-4 h; L-type Ca (nifedipine-blocked, Cd-insensitive); charybdotoxin converts plateau to spikes; plateaus can be synaptically driven and drive axonal bursts | Mills & Pitman 1997, *J Neurophysiol* 78:2455; 1999, 81:2253; Hancox & Pitman 1991, *Proc R Soc B* 244:33; 1993, *J Exp Biol* 176:307 |
| plateau levels | cockroach Df | threshold ~**-51 mV**, plateau level ~**-37 mV** | attributed to Hancox & Pitman by a search-engine summary; **full text not reached, not verified** |
| conditional plateaus / bursting | locust flight interneurons and some MNs | appear **only under octopamine**; plateaus terminated by hyperpolarising pulses; bursts **50-75 ms**, endogenous bursting **4-16 Hz** | Ramirez & Pearson 1991, *J Neurophysiol* 66:1522 and *Brain Res* 549:332 |

The insect pattern across these: leg-motor plateaus and bursting are **conditional** (on octopamine, on a K-current state,
on time since dissection), and walking-state MN drive is a small tonic depolarisation carved by phasic inhibition.

**what this licenses in the model.** In the fly: graded (non-spiking) output is measured for 13B-alpha and 10B-alpha only;
rebound is measured only at the level of behaviour, calcium or fictive network output, never as a membrane property of a
named leg cell, so every rebound or plateau on a named fly leg cell is (E). If one is added, the borrowed envelope is a
plateau of ~10-15 mV above a ~-51 mV threshold (unverified numbers), bursts 50-75 ms, conditional on a modulator; a
walking-state tonic depolarisation of <= 5 mV on MNs; graded release starting ~2 mV above rest.

---

## 4. neuromodulation of walking

### 4a. what the male file carries (D, MaleCNS v1.0 consensus_nt, `brain_cord.npz`)

- **101 octopaminergic cells** in the whole MaleCNS; in the cord file **50**, all efferents (49 `vnc_efferent`, 1
  `efferent_ascending`, types EN00B001-027, EA00B006/022, mesVUM-MJ). **No descending neuron is predicted octopaminergic**:
  Babski's OA-DNs VL1 (DNd02) and VL2 (DNd03) come out `unclear` and `glutamate`. OA prediction is known to be the weakest
  transmitter class, so treat the DN side as unlabelled, not as absent.
- **the leg-nerve octopamine cells: EN00B008, one per thoracic neuromere** (exit ProLN, MesoLN, MetaLN). By position and
  target they are the fly's candidate homologues of the locust DUMETi-type leg DUM neurons (E).
  - inputs: 1,046 / 1,212 / 400 synapses. Top partners: **DNp68** (ACh, 118-327), **IN05B003** (GABA, 102-261), IN03B054
    (GABA), and **DNg100, the walking command, at 23-32 synapses** onto the T1/T2 cells.
  - outputs (edges >= 5): 208 synapses total, almost all onto other octopaminergic efferents. **They make no chemical
    synapses onto leg MNs or premotor cells in the file.** Their action in life is by release in the periphery (muscle,
    sense organs) and paracrine release in the neuropil, neither of which a synapse table can show.
- serotonin: 24 cells in the cord file.

### 4b. Drosophila, measured

- **no measurement of octopamine's effect, in mV or percent, on any adult fly leg MN or premotor interneuron.** not found.
- OA-DNs (adult, whole-cell, behaving): VPM1/VPM2 fire tonic single spikes that rise during locomotor bouts; VUMd cells fire
  **4.1 +/- 3.1 Hz, unchanged during locomotion**; VL1/VL2 rise with leg movement (Babski, Codianni & Bhandawat 2024,
  *Heliyon* 10:e29952, PMC11064449) (M, near). these are cut in the headless cord.
- Tbh mutants: flight initiation and maintenance deficits; walking not reported abolished (Brembs et al. 2007, *J Neurosci*
  27:11122) (M).
- octopamine drives starvation hyperactivity centrally, via SEZ OA neurons (Yu et al. 2016, *eLife*; `chemo_thermo_hygro.md`) (M).
- serotonergic VNC neurons slow walking in every context; silencing them speeds it (Howard et al. 2019, *Curr Biol*
  29:4218) (M, direct; a brake on speed, not a rhythm gate).
- VNC Tdc2 neurons are all Tbh+ (octopaminergic, not tyramine-only); 80 % of biogenic-amine receptor genes are cluster
  markers in the adult VNC single-cell atlas (Allen et al. 2020, *eLife* 9:e54074, PMC7173974) (M, direct). which leg MN
  or premotor type expresses which OA receptor (Oamb, Oct-alpha2R, Oct-beta1-3R): not extracted, and I found no
  cell-type-resolved map for leg circuits.
- larva, isolated CNS: Tdc2+ activity is coupled to MN bursts across fictive behaviours; depolarising Tdc2+ cells
  increases root bursting and biases to forward waves; hyperpolarising them suppresses or abolishes fictive rhythm, with
  rebound (Smith, Hibbard & Pulver 2026 preprint); OA and TA modulate program competition (Smith & Pulver 2025,
  *J Neurophysiol*, DOI 10.1152/jn.00564.2025) (M, larva, far).

### 4c. borrowed (C)

- **stick insect, octopamine on the femur-tibia loop:** injected octopamine first mimics the active state (3.5-12 min),
  then abolishes the resistance reflex (gain to zero, 15-20 min) while active movements remain; topical on the ganglion,
  suppression of the resistance reflex at the MN level is **dose-dependent from 5 mM**; it suppresses resistance-reflex
  pathways and spares or facilitates active-state responses (Büschges, Kittmann & Ramirez 1993, *J Neurobiol* 24:598,
  DOI 10.1002/neu.480240506).
- **stick insect descending DUM (desDUM) OA neurons:** stance-coupled excitation from leg load sensors, not from the CPG;
  their spikes **increase** load-evoked reflex responses in retractor MNs (positive feedback), have mixed effects on extensor
  tibiae reflexes, and often accompany reflex reversal (Stolz et al. 2019, *J Neurophysiol* 122:2388, DOI 10.1152/jn.00196.2019).
- octopamine raises FeCO gain only in tonic position-coding afferents (stick insect) and acts on afferent presynaptic
  inhibition (locust) (`mechanosensation.md` item 9).
- **locust DUMETi:** octopaminergic leg DUM onto the extensor tibiae; slows the muscle's myogenic rhythm; ~0.1 pmol OA in the
  soma (Evans & O'Shea 1978, *J Exp Biol* 73:235). a peripheral, muscle-side action.
- locust flight: octopamine induces plateaus and 4-16 Hz bursting in interneurons (§3b).

### 4d. DN-driven vs state-driven initiation

The headless fly walks under DNg100 alone (Sapkal 2024, 2026; `walking_review.md` §1), so no brain modulator is required.
What the headless cord keeps and the model lacks: the EN00B008 cells (driven by DNg100 in the file), the other VNC OA and
5-HT cells, and slow cholinergic signalling. Nobody has silenced the cord's own OA cells during headless DNg100 walking.

**what this licenses in the model.** A modulatory state computed from cells that exist is natural here: the EN00B008 rate
is driven by DNp68 and DNg100 in the file and could set an octopamine level (D). What that level does is borrowed in sign
only: suppress resistance-reflex pathways (gain from 1 toward 0), facilitate active-state and load-feedback pathways
(gain >= 1), raise tonic afferent gain, and possibly unlock conditional plateaus (stick insect, locust). No fly
measurement fixes a magnitude, a time constant or which receptor on which cell, so every gain value is (E) and should be
logged as such; seconds-to-minutes kinetics are the only borrowed timescale, and those are pharmacological.

---

## 5. leg sensory populations with numbers

Mostly already written: `leg_biomech.md` §E, `leg_biomech_parts/E_proprioceptors.md`, `E_table_male.md`,
`hair_plates_bristles_tarsal_sensilla.md`, `proprioceptor_encoder_models.md`, `mechanosensation.md` §1. The short version,
with completeness against the file:

| population | per leg in life | in the male file (D, `E_table_male.md`) T1 / T2 / T3 | tuning (M) | spike rates |
|---|---|---|---|---|
| FeCO (claw + hook + club) | **152** cell bodies (Mamiya 2023, X-ray) | claw SNpp50+51: **5 / 41 / 48**; hook SNpp39+41: **11 / 28 / 22**; club: **no type named** | claw tonic angle, hysteretic, silent near 90 deg; hook directional, velocity-flat 100-800 deg/s, fast adapting, **presynaptically suppressed during walking** (Dallmann 2025); club vibration 100-2000 Hz | **none measured in the adult fly**: all calcium imaging at ~8 Hz |
| hair plates | **214 neurons in 42 plates over six legs** (~36 per leg) (Pratt et al. 2026, *Nat Commun* 17:2664) | SNpp45+52: **19 / 44 / 33** (T1 counts include VProN 12 and DProN 6) | tonic limit detectors, 17 % of output onto MNs; threshold angle unpublished | none measured |
| campaniform sensilla | **42 front and middle, 41 hind, 11 groups**, none on coxa (Dinges 2021) | only SNpp53 (trochanter CS) named: **4 / 4 / 4**; the rest are in SNppxx/untyped | force and dF/dt | none in *Drosophila*; blow fly tibial CS recorded (Zill et al. 2025, *J Neurophysiol* 133:1749), parameters not reached; cockroach/stick insect model parameters in Szczecinski et al. 2021 (C) |
| bristles | 400+ front leg (409 reconstructed in FANC) | SNta: 292 / 800 / 801 | touch; mostly zero synapses onto MNs | larval lch5 chordotonal: 46.6 +/- 15.3 spikes/s nerve, 24.6 Hz single unit (M, larva) |

- reconstruction completeness: the front-leg deficit (FeCO 16 of 152, 5 claw) is a tracing artefact. FANC has 80 T1L FeCO
  axons (~50 %), MANC v1.2.1 had 22 (Lee et al. 2025, *Nat Commun*) (M/D). FANC is the better source for T1 afferents.
- the one leg-mechanosensory latency measured: **3 ms over ~850 um (0.28 m/s)** for a femur bristle (Agrawal 2020).
- adaptation seen downstream is GABAergic circuit adaptation, not afferent adaptation (§3a).
- the first *Drosophila* CS physiology (a genetic line for all CS) is a 2026 preprint whose body I could not read
  (Custodio et al., bioRxiv 10.64898/2026.07.22.740025; `research/sources/custodio_2026.md`).

**what this licenses in the model.** Tuning shapes (tonic angle, directional velocity, limit, load) are measured in the fly;
every spike rate for an adult fly leg proprioceptor is (E) or (C), since none has been recorded. Populations: T2/T3 FeCO and
hair plates are close to complete in the file; T1 needs a declared stand-in or FANC; campaniform fields beyond the trochanter
and all club cells are missing by type and would be declared populations.

---

## 6. gap junctions in the adult VNC

`walking_review.md` §3 has the anatomy (Ammer et al. 2022, *Curr Biol* 32:2022: ShakB is the most widespread neuronal innexin,
through the VNC neuropils, no cell-level assignment in leg neuropil), the leg-circuit fragments (club -> 10B-alpha mixed electrical
and chemical; 13B-alpha claw drive survives nicotinic and muscarinic block) and the larval result (Matsunaga, Kohsaka & Nose
2017, *J Neurosci* 37:2045: MNs signal back to the crawling CPG through shakB in MNs and ogre in interneurons). Added here:

- **the only coupling coefficients measured between adult fly VNC motor neurons:** flight MN1-5 (DLM), paired whole-cell,
  **CC = 0.023 +/- 0.003 for MN1-MN2 and MN3-MN4, 0.010 +/- 0.003 for other pairs**; the spike AHP passes at CC 0.042 and the
  overshoot at 0.010; ShakB-mediated (shakB RNAi removes detectable coupling); **weak coupling splays the MNs' firing
  apart, ShakB overexpression synchronises them** (synchrony index 0.56 -> 0.84); models need CC < 0.05 to reproduce it
  (Hurkey et al. 2023, *Nature* 618:118, PMC10232364) (M, near: adult VNC MNs, wing pool).
- giant fibre circuit: newly identified electrically coupled neurons (Kennedy & Broadie 2018, *eNeuro* 5:ENEURO.0346-18.2018, PMC6325540) (M,
  escape circuit).
- **leg MNs or leg premotor interneurons: no coupling measurement, no dye-coupling result, no cell-type innexin map.** not found.
  No connectome resolves gap junctions.

**derived (D):** for weak coupling CC ~ G_c x R_in(post). With leg MN R_in 150-700 MOhm and the flight-MN CC range
0.010-0.023, G_c ~ **0.014-0.15 nS** per coupled pair.

**what this licenses in the model.** Electrical coupling inside a leg motor pool is (E) in existence and location; if added,
the only adult VNC measurement says weak (CC 0.01-0.02, <= 0.05), which in an adult MN pool desynchronises rather than
synchronises. MN -> premotor coupling is a larval result (far). Any leg gap junction is a ledger row.

---

## the knobs in one table

| knob | honest range | mark |
|---|---|---|
| tau_syn ACh (nicotinic) | 1.5-7 ms (adult central in situ 4.5-6.7 ms) | M near / far |
| tau_syn GABA-A | 3-6 ms (culture); slow GABA-B component exists, unquantified | M far; M near qualitative |
| tau_syn GluCl | no unitary value; only a larval compound IPSC at ~250-350 ms | gap (E) |
| inhibitory reversal | near rest (larval MNs): shunting, not free hyperpolarisation | M far |
| per-synapse peak PSP | 0.04-0.25 mV for adult central cholinergic synapses; engine gives 0.043 mV | M near / D |
| MN resting Vm | slow -48, intermediate -60, fast -68 mV (spread ~10 mV each) | M direct |
| MN input resistance | 700 / 300 / 150 MOhm | M direct |
| MN threshold, tau_m | not measured; tau_m 10-40 ms from other fly central neurons | E |
| slow MN rest firing | ~30 Hz (10-52), partly cholinergic-driven | M direct |
| plateau / rebound on named leg cells | none measured in the fly; borrowed plateau ~10-15 mV, bursts 50-75 ms, conditional on OA | C / E |
| walking-state tonic MN depolarisation | <= 5 mV | C |
| octopamine state | driven by EN00B008 (1 per leg neuromere, DNg100 among inputs); sign borrowed, magnitude none | D / C / E |
| leg proprioceptor spike rates | none in adult fly | E / C |
| leg MN gap junctions | CC 0.01-0.023 (flight MNs), G_c ~0.01-0.15 nS | M near / D |

## sources opened for this file, not already in `research/sources/`

Gu & O'Dowd 2006; Su & O'Dowd 2003; Lee & O'Dowd 1999; Lee, Su & O'Dowd 2003; Kazama & Wilson 2008; Tobin, Wilson & Lee 2017;
Liu, Davoudian, Lizbinski & Jeanne 2022; Gouwens & Wilson 2009; MacNamee et al. 2016 (Fig. 9 read as an image);
Liu & Wilson 2013; Rohrbough & Broadie 2002 (abstract); Shiu et al. 2024 Methods and reference list; Pugliese et al. 2026
Methods and reference list; Burrows & Siegler 1978, Büschges 1995, Büschges 2004, Ludwar 2005, Schmidt 2001, Mills & Pitman
1997/1999, Ramirez & Pearson 1991 x2, Büschges/Kittmann/Ramirez 1993, Stolz 2019, Evans & O'Shea 1978 (abstracts);
Roemschied 2023, Hurkey 2023, Allen 2020 (full text, grepped); Smith/Hibbard/Pulver 2026 and Date 2026 (preprint abstracts).
Not reached: Wilson & Laurent 2005 full text (GABA-A/B numbers), Hancox & Pitman 1991/1993 full text (plateau numbers),
Hofmann, Koch & Bässler 1985 (stick insect FeCO rates), Zill 2025 full text.
