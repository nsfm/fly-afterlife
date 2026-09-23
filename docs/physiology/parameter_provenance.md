# parameter provenance: where the published fly models got their numbers

Written 2026-09-22 for the owner's question: *"We're shy to produce undocumented constants. I'm curious how Shiu et al produced
their numbers - was it physical measurement? analytical? simulation toward expected results? Can we use their methodology when it
comes to filling the gaps?"*

Scope: provenance and method only. The measured biophysics themselves (per-type thresholds, kinetics) are in `knobs.md` (sibling
agent). Classes used throughout:

- **measured**: a number read off a recording, with the preparation named.
- **inherited**: copied from an earlier model; the chain is followed back to a measurement where one exists.
- **analytical**: set by an argument (units, scaling, a derivation), not by data.
- **chosen / swept**: set by hand, then tested for robustness over a stated range.
- **fitted-to-physiology**: optimised against measured neural quantities (rates, phases, tuning).
- **fitted-to-task / function**: optimised until the model does the thing (a bump, optic flow, a rhythm).

Sources were read first-hand unless marked *(not re-read)*. Shiu: PMC11446845 (Methods, "Computational model", "Neurotransmitter
predictions", "Assessment of model robustness", "Computational modelling limitations"), plus the reference code in
`ref/Drosophila_brain_model/model.py`. Pugliese: PMC13142387 v2 Methods + Extended Data Fig. 2, plus `ref/pugliese_cpg`.

---

## 1. Shiu et al. 2024 (Nature 634:210), the whole-brain LIF on FlyWire

### 1.1 what they say about their own method

> "All parameters are taken from previous Drosophila modelling or electrophysiology efforts [18,19,61,62], from the synaptic weights
> from the Flywire connectome (public materialization v.630) [18,19], or from the neurotransmitter predictions [3,63], except for
> Wsyn, the single free parameter of the model ... We chose Wsyn such that activation of sugar GRNs at 100 Hz resulted in roughly 80%
> of maximal MN9 firing [64,65]."

So the short answer: **every biophysical constant is inherited** (mostly through one earlier model, Kakaria & de Bivort 2017),
**one constant is chosen by simulation toward a target** (Wsyn), and **none was fitted to the behaviours they then validated on**
beyond that one calibration point.

Refs as numbered in the paper: [18] Kakaria & de Bivort 2017 *Front Behav Neurosci* 11:8; [19] Churgin et al. eLife RP90511;
[59] Lazar et al. 2021 eLife 10:e62362 (FlyBrainLab); [61] Jürgensen et al. 2021 *Neuromorph Comput Eng* 1:024008;
[62] Paul et al. 2015 *Front Cell Neurosci* 9:29; [3] Eckstein et al. 2024 *Cell* 187:2574; [64] Dahanukar et al. 2007 *Neuron*
56:503; [65] Inagaki et al. 2012 *Cell* 148:583; [66] Liu & Wilson 2013 *PNAS* 110:10294.

### 1.2 the equations (Methods, verbatim in substance)

    dv_i/dt = (g_i - (v_i - V_rest)) / T_mbr
    dg_i/dt = -g_i / tau
    g_i <- g_i + w_ji on a spike from j (after T_dly);   w_ji = (synapse count j->i) x (+1 or -1) x W_syn

Brian2, `method='linear'` (exact integration of the linear ODE between events); `defaultclock` is never set in `model.py`, so
**dt = Brian2's default 0.1 ms** (the paper does not state it). 30 trials x 1,000 ms per condition. All 127,400 proofread v630
neurons (the repo also ships v783).

### 1.3 parameter by parameter

| parameter | value | Shiu cites | where the number actually comes from | class |
|---|---|---|---|---|
| V_rest | -52 mV | [18] | Kakaria cites Rohrbough & Broadie 2002 (larval CNS neurons) and Sheeba et al. 2008 (adult l-LNv clock neurons) *(not re-read)* | inherited <- measured, other cells |
| V_reset | -52 mV | [18] | Kakaria has **no reset parameter**: it pastes a spike template whose undershoot is -72 mV (Nagel et al. 2015). Shiu's reset-to-rest is their simplification, attributed to [18] | chosen (attributed as inherited) |
| V_threshold | -45 mV | [18] | Kakaria cites Sheeba 2008 and Gouwens & Wilson 2009 | inherited <- measured |
| R_mbr, C_mbr | 10 kOhm cm^2, 2 uF cm^-2 | [18] | Kakaria: "Cm ... 0.002 uF in all neurons, assuming a surface area of 10^-3 cm^2; Gouwens and Wilson, 2009", "Rm ... 10 MOhm; Gouwens and Wilson, 2009". Shiu restated them per unit area. Gouwens & Wilson fitted compartmental models to adult antennal-lobe DM1 PNs: **Rm 8.3-20.8 kOhm cm^2, Cm 0.8-2.6 uF cm^-2** across three cells | inherited <- fitted-to-physiology in one cell type |
| T_mbr | 20 ms | "definition ... in a resistor-capacitor circuit" | analytical: Rm x Cm. Neither Kakaria nor Shiu states "20 ms"; Pugliese: "The membrane time constant was not specifically mentioned in [Shiu], so we computed it". Within Gouwens & Wilson's fitted range (~7-54 ms from their Rm, Cm extremes) | analytical from inherited |
| T_refractory | 2.2 ms | [18], [59] | Lazar 2021: "a refractory period of 2.2 ms as suggested in [Kakaria and de Bivort, 2017]". **2.2 does not appear in Kakaria's text**; the nearest number is its 2 ms spike-template length (Gouwens & Wilson 2009; Gaudry et al. 2013). The extra 0.2 ms is untraced (possibly in Kakaria's MATLAB, not checked) | inherited, chain partly broken |
| tau (synaptic decay) | 5 ms | [61] | Jürgensen 2021 is a larval mushroom-body model on neuromorphic hardware: tau_e = 5 ms, **tau_i = 10 ms**; no measurement cited for either that we could find (paper table, and code `nawrotlab/DrosophilaOlfactorySparseCoding`). Shiu uses 5 ms for **both** signs. Independently, Kakaria used a PSC decay **half-life** of 5 ms from Gaudry 2013 (ORN->PN; a half-life of 5 ms is an e-fold tau of 7.2 ms) | inherited from a model with no stated measurement |
| T_dly | 1.8 ms | [62] | Paul et al. 2015, focal macropatch at the **larval neuromuscular junction** (muscles 6/7), 18 C, 1 mM Ca: wild-type synaptic delay "1.8 +- 0.3 ms" (brp null 2.27). A real measurement, of a glutamatergic NMJ, applied to every central synapse | inherited <- measured, other synapse |
| W_syn | 0.275 mV | free | "chosen such that activation of sugar GRNs at 100 Hz resulted in roughly 80% of maximal MN9 firing [64,65]". [64]/[65] are sugar-GRN / PER papers; the 80%-of-maximum target is **model-internal** (MN9's own ceiling in the model), not a measured MN9 rate | chosen by simulation toward one target |
| sign | +1 / -1 per neuron | [3], [66] | Eckstein 2024 per-synapse predictions, cleft score >= 50, neuron inhibitory if > half of its presynapses are GABA or Glu; DA / OA / 5-HT counted excitatory; Glu inhibitory "consistent with previous experimental work" (Liu & Wilson 2013, GluCl in the antennal lobe) | measured-by-proxy (classifier) + assumption |
| E vs I magnitude | equal | [18] | "Consistent with previous Drosophila computational modelling efforts, we assume that excitatory and inhibitory synapses have the same magnitude" | inherited assumption, swept (below) |
| weight per edge | raw synapse count | FlyWire | **no synapse floor**: in the repo's `Connectivity_783.parquet` / v630 file the minimum is 1 and 82% of edges are < 5 synapses | measured (EM) |
| input drive | Poisson spikes added straight to v at 250 x W_syn = 68.75 mV; stimulated cells' refractory set to 0 | code | code comment: "250 is sufficient to cause spiking": every Poisson event forces a spike, so the stimulated cell fires at the requested rate | engineering choice |
| noise / baseline | none; 0 Hz baseline | - | stated as a limitation: "we assume a basal firing rate of 0 Hz ... inhibitory connections to an inactive neuron have no effect" | chosen |

A small derived fact the table implies (ours, not theirs): with these kinetics a single synapse's PSP peaks at
W_syn x (1/3) x (0.25^(1/3) - 0.25^(4/3)) = **0.157 mV** (at ~9 ms), not 0.275 mV, so about **45** synchronous synapses, not 26,
take a cell from rest to threshold. (`vision_motor_courtship.md` §5 uses the 26 figure.)

### 1.4 what they swept, and what they declined to sweep

From "Assessment of model robustness", tested on the 164 experimentally checked predictions (Supplementary Table 11):

- **W_syn +-30%**, with the sensory input rate re-adjusted to compensate. -30%: 90.2% of predictions unchanged, accuracy 85%;
  notable loss: water GRNs no longer drive MN9 well. +30%: 95% unchanged, accuracy 88%. Default accuracy 91%.
- **inhibitory:excitatory ratio +-50%**: 95% / 96% of predictions unchanged; accuracy 88% / 89%.
- **glutamate sign flipped to excitatory**: most predictions held, but the bitter and Ir94e inhibition of feeding disappears and the
  split-GAL4 false-positive rate goes 1% -> 16%.
- **connectome shuffle** (weights permuted, distribution kept): sugar at 100 Hz drives MN9 in 100% of real-connectome runs, 1 of 100
  shuffled.
- **not swept, with their reasons (quoted):** "Because scaling Wsyn essentially results in scaling the 'distance' between the resting
  potential and the firing threshold potential, we did not test the robustness of the model to changes to the resting potential or
  firing threshold. Additionally, because changes to the membrane time constant, as well as Tdly ... and the refractory period ...
  generally simply change overall firing rates by permitting more (or less) firing, we did not subject these to robustness checks as
  we already vary the input firing rates." (An analytical argument, not a test. It holds for a uniform change; it does not cover
  per-type differences, which is exactly our campaign item 3.)

Input rates were always swept rather than fixed: sugar 10-200 Hz, water 20-260 Hz, JONs 20-220 Hz, candidate interneurons 25-200 Hz.
They read **direction of change and identity of recruited cells**, not absolute rates: "the absolute firing rates of the model are
unlikely to be accurate. Rather, we prefer to interpret broad differences in firing rates between different conditions."

### 1.5 validations (known behaviour and new experiments)

- sugar GRNs -> proboscis MNs 6, 8, 9, 11 (MN9, MN11 known sugar-responsive in vivo); contralateral MN9 > ipsilateral, matching the
  curved PER toward a unilateral stimulus.
- the known feeding-initiation cell types recovered as sugar-responsive and as required (in-silico silencing: MN9 <= 80% of control).
- **SEZ split-GAL4 screen, run for this paper:** 106 cell types activated in silico at 50 Hz and optogenetically in flies; 11 predicted
  to drive MN9, 10 of 11 did; most of the 95 predicted negatives were negative.
- sugar and water share a pathway (5 shared cells confirmed by calcium imaging: Clavicle, Fudog, Phantom, Rattle, Zorro); water
  silencing phenotypes tested behaviourally.
- bitter and Ir94e inhibit PER; Ir94e predicted aversive and confirmed (fails to block PER to 1 M sucrose).
- **antennal grooming (a circuit not used for calibration):** JON activation recovers aBN1, aBN2, aDN1, aDN2; JO-CE vs JO-F onto aBN1
  checked by calcium imaging.
- totals: "Across 164 predictions we were able to test empirically, 91% were consistent"; 84% excluding the split-GAL4 screen.
  Stated failures: cells that are inhibitory (Tentacular, Phantom) or neuromodulatory (Usnea), attributed to the 0 Hz baseline.

### 1.6 the lineage in one line

Gouwens & Wilson 2009 (compartmental fits to adult DM1 PNs), Sheeba 2008, Rohrbough & Broadie 2002, Gaudry 2013, Nagel 2015 ->
**Kakaria & de Bivort 2017** (ring attractor, 60 PB neurons) -> Lazar 2021 FlyBrainLab (refractory 2.2 ms "as suggested in"
Kakaria) and Churgin (AL model, "as in Kakaria") -> **Shiu 2024**, plus Jürgensen 2021 (tau) and Paul 2015 (delay) grafted on ->
Pugliese 2026's LIF check, and every FlyWire LIF since (including ours). Kakaria's own framing of these values: "chosen to reflect
generic neuronal properties (Hodgkin and Huxley, 1952) ... but these values are consistent with various Drosophila measurements."

---

## 2. Pugliese et al. 2025/2026 (bioRxiv 10.1101/2025.09.12.675944 v2), the VNC rate model

Equation: tau_i dr_i/dt = max(r_max,i tanh(a_i (r_max,i I_i + b sum_j w_ij r_j - theta_i)), 0) - r_i. "The form of this equation is
modified from a standard formulation of a rate model [Dayan & Abbott]." Defaults in `ref/pugliese_cpg/configs/neuron_params/default.yaml`
match the paper.

| parameter | value | provenance (their words) | class |
|---|---|---|---|
| tau | N(20, 2) ms per cell per replicate | "Since rmax and tau have direct biological interpretations, we used reasonable ranges for rate limits and time constants ... given experimental literature [Gouwens & Wilson 2009; Agrawal et al. 2020] and consistency with previous fly neuron simulation studies [Kakaria 2017; Shiu 2024]" | inherited (same chain as Shiu's 20 ms) |
| r_max | N(200, 10) Hz | same sentence | inherited / literature range |
| a* (gain) | N(1, 0.1) | "values of theta and a have no direct biological analogs"; set by "a hyperparameter search ... on a set of simple monosynaptic connections ... we chose ranges of values that produced consistent activity in downstream neurons when stimulated with input and ensured this activity also decayed to quiescence after input was removed" | chosen by a generic, circuit-agnostic criterion |
| theta* | N(7.5, 0.6) | same | same |
| b | 0.03, all transmitters | same grid; then swept per transmitter (Ext. Data Fig. 2e): "Increasing bACh to 0.045 still produced viable oscillatory dynamics, but larger deviations resulted in either runaway network activity or insufficient neuron recruitment ... At bACh = 0.03, a broad range of bGABA and bGlu values produced stable oscillatory outputs" | chosen, then swept against their result |
| size scaling | a = a*/s, theta = theta*.s, s = size / median size | s = **volume** (MANC, mCNS) or **mesh surface area** (FANC, BANC). Argument: "volume scales approximately linearly with surface area, which is the determining factor for input resistance." Code (`src/utils/sim_utils.py::set_sizes`) sets missing / zero sizes to the median. "without adjusting a and theta for size, the network does not produce robust oscillations ... even when this input is adjusted down" | analytical (input resistance ~ 1/area), then shown to be necessary |
| weight | synapse count, **floor of 5** in MANC / mCNS ("to remove very weak connections"); **no floor** in FANC / BANC | - | measured (EM) + a threshold choice |
| sign | + if predictedNt (MANC) / consensusNt (mCNS) is ACh; - if GABA or Glu. FANC: hemilineage, with 4 cells overridden to + because MANC's classifier said ACh with p > 0.81 | - | measured-by-proxy |
| I_stim (DN drive) | arbitrary units. Screen: auto-doubled / halved until 5 < active cells < 1,500. Fixed runs: DNg100 250 (MANC), 150 (FANC), 400 (CNS) "set to the same values that produced robust oscillations in [Figure 2]" | - | **chosen toward the studied result** (the one place this model tunes to its outcome) |
| solver | Dopri5, rtol 2e-6, atol 5e-9 "minimized both runtime and sum-squared error when compared to a reference run" | - | numerical |

Robustness: all four parameter SDs widened 3x (Ext. Data Fig. 2a-c): rhythmicity drops modestly, DNg100 and DNb08 stay near the top of
the DN screen; restoring one SD at a time shows **gain is the only sensitive parameter** ("the other 3 parameter distributions could be
increased by at least 3x and our DNg100 activation results were nearly unchanged"). Their stated philosophy: "This method of parameter
selection was designed to reveal dynamics that arise primarily from synaptic connectivity, without relying on special intrinsic
properties or fitted parameters."

Their LIF cross-check uses Shiu's numbers "without tuning or training specific to our circuit or validation against the physiology of
these cells" (dt 0.01 ms, input 0.15 nA).

Validations: frequency rises with DNg100 drive in the full network, confirmed optogenetically in behaving flies; DNb08 predicted from the
screen and confirmed optogenetically; the three-cell core replicates in four connectomes. They also name the next method themselves:
"Comparing simulated dynamics across datasets could support more principled approaches to parameter estimation, such as tuning the
synaptic scaling parameter b separately for each dataset or neuropil."

---

## 3. other connectome-constrained fly models, one paragraph each

**Kakaria & de Bivort 2017 (PB ring attractor, LIF, 60 cells).** Membrane constants inherited from measurements in other cells, as
generic values (§1.3). Synapse strengths are the free parameters and were **fitted to function**: "explored manually to identify the
baseline configuration", then Gaussian dithering (100%, 10%, 5% SD) of ~200 configurations "examined manually, and those producing the
best bump-like behavior were then iteratively refined". Sensitivity: 10,000 dithered networks plus single-class sweeps from -9x to 10x,
clustered by dynamics. Class: **inherited + fitted-to-function.**

**Pisokas, Heinze & Webb 2020 (eLife, fly and locust head-direction circuits).** Membrane values "set to the same values as used by
[Kakaria and de Bivort, 2017]". Synaptic efficacies (one per class) optimised by simulated annealing and particle swarm "based on the
goal that each of the circuits should yield a functional ring attractor", objective = heading error and bump width. Sensitivity by
Gaussian noise on membrane and synaptic parameters. Class: **inherited + fitted-to-function.**

**Huang et al. 2018 (Front Neuroinform, FlyCircuit whole brain, 20,089 LIF cells).** "we extensively reviewed the literature and estimate
the typical value for each parameter (Table S1)": V_rest -70, V_th -45, V_reset -55 mV, tau_m 16 ms, refractory 2 ms, uniform.
Capacitance **scaled by cell size**: 0.8 uF/cm^2 (mean of Gouwens & Wilson 2009 and Weir et al. 2014) times an area estimated from
skeleton length via Wilson & Laurent 2005's three reconstructed PNs. E/I balance tuned for stability: with I/E = 1 the network ran to
~100 Hz in 1 s; no I/E factor from 0.1 to 100 removed "seizure-like hyperactivity"; **short-term depression** did. Class:
**inherited-from-literature-review + analytical size scaling + tuned-to-stability.** (Directly relevant to our runaway in
`rate_model_control.md`: an earlier whole-brain LIF hit the same wall and needed a synaptic mechanism, not a gain.)

**Churgin et al. (eLife RP90511; hemibrain antennal lobe, 3,062 LIF cells; Shiu's ref 19).** The best template for campaign item 3:
**per-cell-type measured constants** (Table 2: ORN / LN / PN resting potential, threshold, spike width, Rm, Cm, each with its recording
paper: Dubin & Harris 1997, Seki et al. 2010, Jeanne & Wilson 2015, Huang et al. 2018). Then four class-wise input multipliers
(ORN, eLN, iLN, PN) were set by grid search so that (1) firing rates of each class match the literature and (2)-(4) known AL
computations hold (PN rates more uniform than ORN rates, better odour separation, sublinear ORN->PN transfer). Sensitivity: each
multiplier 1/4x to 4x, and joint log-normal perturbations, effect size < 0.9 SD throughout. Class: **measured per type +
fitted-to-physiology (rates and transfer functions), with sweeps.**

**Lappalainen et al. 2024 (Nature 634:1132; optic-lobe DMN, flyvis).** Non-spiking. Synapse counts and signs fixed from the connectome
and transcriptomics ("For a minority of cell types ... we used guesses of plausible transmitter phenotypes"). **734 free parameters**
(65 resting potentials, 65 time constants, 604 type-to-type scale factors) **fitted to a task** (optic flow on Sintel video), 50 models.
Initialisation: tau = 50 ms, resting potentials N(0.5, 0.05) a.u. Validation against **26 studies of measured neural activity that were
not in the loss** (contrast and direction selectivity per type). Class: **fitted-to-task, validated on held-out physiology.**

**Zarin et al. 2019 (eLife; larval premotor/motor network, rate model).** Weights initialised from TEM synapse counts (fraction of the
target's input, x 0.005), signs from transmitter where known; time constants, gains, biases, weights optimised by gradient descent to
reproduce **measured** motor-neuron recruitment sequences (their own muscle calcium imaging, forward and backward crawls). Predictions
about premotor phases then tested by new dual-colour calcium imaging (A31k, A06l, A23a); "accurately predicts many, but not all".
Class: **fitted-to-physiology, validated on held-out physiology.**

**Jürgensen et al. 2021 (larval MB on DYNAP-SE).** Source of Shiu's tau. Conductance-based AdEx-style neurons; tau_e 5 ms, tau_i 10 ms;
hardware parameters "fine-tuned using the on-chip bias generator, starting from the estimates provided by the software simulation".
We found no measurement cited for the synaptic time constants. Class: **chosen.**

**Eckstein et al. 2024 (Cell; the sign).** A classifier on EM synapse images trained on **356 cell types from 21 studies** with
transmitter identity known from RNA expression or immunohistochemistry: "accuracy of 87% for individual synapses, 94% for neurons, and
91% for known cell types". Failure modes they name: co-transmission, Kenyon cells called dopaminergic, some sensory neurons and AL LNs
called serotonergic; histamine, tyramine not predicted. The glutamate-is-inhibitory step is separate: an assumption from Liu & Wilson
2013 (GluCl). MANC's `predictedNt` comes from the same family of classifier applied to the VNC (Takemura et al. 2024) *(not re-read
here)*. Class: **measured-by-proxy, with published error rates.**

**Turner-Evans et al. (central-complex ring attractor models)**: not examined for this document.

---

## 4. what this licenses

In plain terms, Shiu's numbers came from **three places**: measurements in other fly cells passed down through one earlier model
(Kakaria 2017, whose own author called them "generic"), one analytical step (tau = Rm x Cm), and **one number found by simulation**
(W_syn, set so 100 Hz of sugar input gives ~80% of the model's maximal MN9). Nobody in this lineage measured a membrane time constant,
threshold or synaptic kinetics for the cells they simulate. What they did, and did honestly, was **say which number was free, sweep it,
and test the model on things it was not set on.** The methods we can borrow:

1. **inherit a measured constant with its citation, and say what was measured.** Shiu's delay is a larval NMJ at 18 C; its membrane
   constants are adult antennal-lobe PNs. Inheriting is fair; the ledger row names the preparation. Where a closer measurement exists
   (Azevedo 2020 for leg MNs, `knobs.md`), it beats the inherited generic value, and Churgin shows the per-type version is publishable.
2. **argue a constant analytically when the physics sets it.** tau = RmCm; Pugliese's size scaling from input resistance ~ 1/area. The
   argument is the citation. Our `--size insyn` proxy for volume is a substitution of this kind and belongs in the ledger as such.
3. **sweep a constant and report the range over which a result holds.** Shiu: W_syn +-30%, I:E +-50%, the glutamate sign. Pugliese:
   parameter SDs x3, b per transmitter, with the break points stated (b_ACh > 0.045 runs away). A result that holds across the range
   needs no defended value; one that holds only at a point is a claim about that point.
4. **fit to a measured physiological target, held out from what we then claim.** Churgin (class rates, transfer functions), Zarin (MN
   recruitment order), and the campaign's own list (Pugliese's 7-15 Hz, Azevedo's rates, Sapkal's phases). The target is a number from a
   paper, and the thing we then report is something else.
5. **the one we avoid: fit to the behaviour we want.** Kakaria and Pisokas tuned synapse strengths until a bump appeared, and say so;
   that is legitimate as an existence proof ("some parameters make a ring attractor") and carries no evidence that the fly's parameters do.
   Choosing constants until the body walks would make "it walks" the input, not the result. Pugliese's fixed DNg100 drive ("the same
   values that produced robust oscillations") is the one small instance of this in the papers we follow.

**How Shiu's validations differ from fitting.** One scalar was set on one calibration point (sugar at 100 Hz -> ~80% of the model's
MN9 maximum). The 164 checks were different quantities: *which* cells respond, which silencings abolish MN9, which of 106 split-GAL4
types extend the proboscis (an experiment run after the predictions), and a grooming circuit that played no part in setting anything.
A calibration fixes the scale; a validation asks something the calibration could not have answered. Our walking body can inherit the
same shape: set a scale on one measured quantity, then report walking as the held-out test.
