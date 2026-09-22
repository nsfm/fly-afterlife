# van der Veen, Cohen, Chicca & Dürr 2025 — spiking proprioceptor encoder (AdEx)

**Citation.** van der Veen T, Cohen Y, Chicca E, Dürr V (2025). "A spiking neural network
model for fractional proprioceptive encoding of limb posture and movement in insects."
*Biological Cybernetics*. DOI 10.1007/s00422-025-01032-2. PMID 41762245, PMC12950026.
Open access (CC BY). Code: https://zenodo.org/doi/10.5281/zenodo.13827523 (Python/Jupyter;
experimental data under `sim_data`). Companion paper: van der Veen et al. 2025 (2nd/3rd
order interneurons).
Read from the Europe PMC full-text XML; equations rendered as images there, so equation
transcriptions below are marked.

Afferent dynamics fitted to **cockroach (*Periplaneta americana*) antennal scapal hair
plate** data (Okada & Toh 2001). Downstream decoding evaluated against **stick insect
(*Carausius morosus*)** whole-body motion capture (Theunissen & Dürr 2013; Vicon MX10,
8 IR cameras, 200 fps, walkway 40 × 490 mm, 9 specimens, flat-surface trials).

The authors argue the hair-field model transfers to the FeCO: "mechanosensory neurons of
the femoral chordotonal organ, i.e., the sensory organ encoding the [FTi] joint angle,
share important encoding features with mechanosensory neurons of proprioceptive hair
fields, such as sensitivity to joint angle, joint angle velocity (Hofmann et al. 1985), and
range fractionation (Matheson 1992; Ache and Dürr 2013)." They applied the hair-field model
at all joints for this reason, even the one lacking real hair fields.

## Layer 1a — joint angle → per-hair deflection

Prose (verified): deflection is **linearly proportional to joint angle**, clipped to
[0°, 90°]; each hair has a receptive field; receptive-field size and spacing uniform within
a field; an overlap parameter equal across hair fields; outer hairs' fields set manually;
per-hair bounds taken from the min/max joint angles actually attained by that joint.
Hair fields are **bi-directional**, modelled as opposing pairs (as in the antennal, Krause
et al. 2013, and coxal, Wendler 1964, hair fields of stick insects).

Equations as transcribed by a page-reading pass (NOT independently verified — MathML did
not survive extraction):
```
eq 1 (standard):  θ_hair,i,j = clip( (θ_joint − θ_lower^j)/(θ_upper^j − θ_lower^j) × 90°, 0°, 90° )
eq 4 (opposing):  θ_hair,i,j = clip( (θ_neutral − θ_joint)/(θ_neutral − θ_lower^j) × 90°, 0°, 90° )
```

## Layer 1b — deflection → current → spikes (AdEx)

Verbatim: "the hair angles calculated in Eqs. (1) and (4) were multiplied by **10–150**
[pA/degree], yielding **currents in the nA range**."

AdEx (Brette & Gerstner 2005):
```
C·dV/dt   = −g_L(V − E_L) + g_L Δ_T exp((V − V_T)/Δ_T) − w + I
τ_w·dw/dt = a(V − E_L) − w
on spike (V ≥ V_spike): V → V_reset, w → w + b
```

## Table 1 — parameter values after optimisation (verbatim from the article's table markup)

| neuron | model | C | (nS) | Δ_T | (nS) | τ_w | b | τ_m | w_syn |
|---|---|---|---|---|---|---|---|---|---|
| Sensory | AdEx | 200 pF | 2 nS | 2 mV | 2 nS | 50 ms | 264 pV | – | – |
| Position IN | LIF | – | – | – | – | – | – | 120 ms | 1 mV |
| Velocity IN | LIF | – | – | – | – | – | – | 5 ms | 10.8 mV |

⚠ Column headers are images in the source; the mapping of the two "2 nS" columns to g_L vs
a is from a page-reading pass. `b = 264 pV` is printed with voltage units where
spike-triggered adaptation is normally a current. Also reported second-hand, not visible in
the markup: E_L = −70 mV, V_T = −50 mV, V_reset = −70 mV (AdEx); V_T = −50 mV (LIFs);
N_h = 50 hairs per field (100 per joint); Δt = 0.1 ms.

## Layer 2 — first-order interneurons

Both LIF, "providing a linear relation between an input current and output spike rate":
- **Position INs**: τ_m = 120 ms, w_syn = 1 mV ⇒ integrator, encodes joint angle across the
  whole working range.
- **Velocity INs**: τ_m = 5 ms, w_syn = 10.8 mV ⇒ high-pass/coincidence detector; spike
  rate **increases linearly with angular velocity**; direction-selective.
  "Strong linearity was achieved only when [w_syn] equalled [threshold distance]. At this
  synaptic strength, [one EPSP] marginally exceeded [threshold], allowing spikes from small
  phasic fluctuations to transmit through the high-pass filter."

## Performance (verbatim tables)

Table 2, position IN normalised MSE ± SD: front 0.0317 ± 0.0071, middle 0.0310 ± 0.0105,
hind 0.0296 ± 0.0060; by joint type 0.0266 ± 0.0046, 0.0389 ± 0.0075, 0.0268 ± 0.0047.
Leg × joint interaction F(2, 69) = 11.11.

Table 3, velocity IN as a binary direction classifier: TP 1 627 811, FN 155 707,
FP 155 167, TN 1 689 086 ⇒ **accuracy 0.914, TPR 0.913, TNR 0.916**.

Implementation: Python 3.9, backward-difference solver; 3 joint angles × 6 legs = 18 joints;
"3 sets of two hair field implementations per leg".

## Its literature review = the map of prior proprioceptor encoders (verbatim)

> "Cocatre-Zilgien and Delcomyn (1999) modeled the afferent spike rate of **campaniform
> sensilla** by means of a **two-stage stimulus-response function**, where the first stage
> captured the tonic component as a **hyperbolic function of strain** (in analogy to
> vertebrate mechanoreceptors: Loewenstein 1961), and the second stage implemented phasic
> adaptation by means of a **power law**, as previously proposed for mechanoreceptor
> adaptation in cockroaches (Chapman and Smith 1963; French 1984). Applying a similar
> approach to hair fields, 'total afferent activity' of the stick insect **trochanteral hair
> field** has been simulated using a **phasic-tonic function of spike rate on joint angle**
> (Dean 1985). In contrast, sensory array models involve multiple parallel receptor models.
> For example, **Ache and Dürr (2015) applied cascaded low-pass and high-pass filter
> blocks** to model different stages of proprioceptive encoding of antennal position and
> velocity in stick insects. Similarly, **Szczecinski et al. (2021)** modeled phasic-tonic
> changes in a strain-sensitive campaniform sensillum. While this kind of analog
> stimulus-response functions may be combined with **stochastic spike generators** to
> generate time sequences of spike time events (e.g., **Gollin and Dürr 2018**), there is a
> lack of a spiking proprioceptor model that generates spike trains directly through
> subthreshold membrane potential dynamics."

Complete set of named prior encoders: Cocatre-Zilgien & Delcomyn 1999 (CS: hyperbolic tonic
+ power-law adaptation); Dean 1985 (hair field: phasic-tonic f(joint angle));
Ache & Dürr 2015 (antennal hair field array, LP/HP filter cascade);
Szczecinski et al. 2021 (CS); Gollin & Dürr 2018 (analog response + stochastic spiking);
van der Veen et al. 2025 (AdEx spiking).
