# Vision, motor control and courtship physiology — numbers for the whole-fly sim

Scope: firing rates and response magnitudes that constrain (a) the LIF readouts (DNa02 steering, leg-MN
walking speed, P1/pIP10 courtship), (b) the flyvis→LIF drive rules, and (c) the male-vs-female calibration
problem. Confidence tags: **[H]** measured and quoted directly; **[M]** measured but only approximately
recoverable (figure-read or derived); **[L]** inference/extrapolation, treat as a prior not a fact.

---

## 1. Firing rates during walking

### DNa02 / DNa01 (the steering pair)

Both were recorded whole-cell in flies walking on a spherical treadmill (Rayshubskiy et al., 2020,
bioRxiv 2020.04.04.024703; peer-reviewed as Rayshubskiy et al., 2025, *eLife* 13:RP102230). The paper is
frustratingly figure-based: **it reports essentially no absolute spike rates in text.** What is stated:

- Rotational velocity is **linearly related to the right−left DNa02 firing-rate difference "through its
  entire dynamic range"**, consistently across paired bilateral recordings (n=4 flies) **[H]**. This is the
  single most important result for our readout — the left−right difference rule is the right functional form.
- DNa02 is **high-gain and transient**; DNa01 is **low-gain and sustained**. The regression slope of
  rotational velocity on firing rate differs significantly between cell types, DNa02 steeper (Fig. 2e) **[H]**.
- Neural activity leads behavior by **~150 ms** **[H]** (also confirmed in Yang et al., 2024, *Cell* 187:6459:
  "firing rate changes in these DNs preceded changes in rotational velocity and stride length by about 150 ms").
- DNa02 predicts trial-to-trial turn magnitude: R²=0.51 (p=3×10⁻³) for compass-directed turns; R²=0.16–0.40
  (p<0.005) for stimulus-directed turns **[H]**.
- DNa02 encodes **the laterality of the action, not of the stimulus**: higher ipsilateral to an attractive
  fictive odor (Orco-CsChrimson), higher *contralateral* to an aversive fictive heat stimulus (Gr28b.d) **[H]**.
- Translational velocity is only weakly related to DNa01/DNa02 activity; when DNa01 is more hyperpolarized
  than DNa02 the fly tends to walk backward **[H]**.
- Rotational-velocity prediction plots are drawn on axes spanning **±800 °/s** (Fig. 3d,e legend) **[H]**.

**Absolute DNa02 dynamic range (derived):** Yang et al. (2024, *Cell*) report that DNa02's stride-locked
firing modulation is "only about **15 spikes/s (approximately 10% of the cell's dynamic range)**" — which
puts **DNa02 dynamic range ≈ 150 spikes/s** **[M]**. DNg13 (the other lateralized steering DN in that paper)
can be driven to **>100 spikes/s** by depolarizing current injection **[H]**. Baseline rate during straight
walking is not published; from the bilateral-difference plots it is clearly non-zero on both sides (the "both
cells firing zero spikes" condition is called out separately as the immobile state), so a **standing/straight
baseline of roughly 10–40 spikes/s per side** is the best available guess **[L]**.

**DNa02 → turning gain.** Not published as a number. Bracketing it: right−left difference spans at most
±150 Hz, and the rotational velocities being predicted span ±800 °/s at the extremes but sit mostly within
±200–400 °/s during ordinary walking. That gives **≈3–10 °/s per Hz of net left−right difference**, with
~5 °/s/Hz as the midpoint **[M/L]**. Our current rule (3° yaw per net spike per 100 ms chunk) equals
**3 °/s per Hz**, i.e. the conservative end of that bracket — defensible, arguably ~1.5× too shallow.
DNa01's gain is perhaps 2–3× shallower than DNa02's **[L]**.

### Other descending classes

- **DNp09** (= P9): one pair; drives forward walking with ipsilateral turning, receives input from
  courtship-promoting central neurons and VPNs, required for male pursuit (Bidaye et al., 2020, *Neuron*
  108:469). Also produces state-dependent running vs freezing (Zacarias et al., 2018, *Nat Commun* 9:3697).
  **No in vivo firing rates published** — treat as unconstrained **[H that it's unknown]**.
- **MDN** (moonwalker): 4 cells total. Symmetric activation → straight backward walking; asymmetric →
  backward turning (Bidaye et al., 2014, *Science* 344:97; Sen et al., 2017, *Curr Biol* 27:766; Feng et al.,
  2020, *Nat Commun* 11:6166). Driven by **LC16** for visually evoked retreat (Sen et al., 2017). No spike
  rates published.
- **DNg/DNb classes:** DNg13 as above (>100 sp/s under injection). DNb05/DNb06 correlate with rotational
  velocity in calcium imaging but have no published rates (Yang et al., 2024). Population imaging shows the
  **largest fraction of DNs encode walking**, fewer encode grooming or rest (Aymanns et al., 2022, *eLife*
  11:e81527), and command-like DNs co-recruit broad DN populations rather than acting alone (Braun et al.,
  2024, *Nature* 634:686).

### Leg motor neurons

Azevedo et al., 2020, *eLife* 9:e56754 (whole-cell, tibia flexor MNs):

- **Slow MN: resting spike rate ≈ 30 Hz while the fly stands still** **[H]**. This is the key number — the
  standing baseline is *not* zero.
- **Intermediate and fast MNs are silent at rest** **[H]**; recruited in order slow → intermediate → fast.
- Force per spike: slow **<0.1 µN**, intermediate **~1 µN**, fast **~10 µN** (≈ the fly's body weight) —
  three orders of magnitude **[H]**. Force-per-spike curves saturate at **~10 spikes** **[H]**.
- Slow MN firing rate is significantly modulated by a **1° change in tibia angle**; fast/intermediate are
  barely proprioceptively modulated **[H]**.
- ~15 MNs innervate the tibia flexor muscles **[H]**.
- Stepping frequency in walking flies ranges **<1 Hz to >18 Hz** (femur–tibia joint cycles 10–20×/s)
  (Azevedo et al., 2020; Agrawal et al., 2020, *eLife* 9:e60299) **[H]**.

Implication: total leg-MN output vs a standing baseline is a reasonable speed proxy, but the baseline is
dominated by tonic slow MNs, and the *interesting* signal (fast MN recruitment) is a small spike count on
top of a large tonic floor.

### How hot should a brain be? (population-rate calibration)

- **Olfactory PNs: 4.6 ± 4.2 spikes/s spontaneous (n=37)** (Turner, Bazhenov & Laurent, 2008,
  *J Neurophysiol* 99:734) **[H]**.
- **Kenyon cells: 0.1 ± 0.4 spikes/s spontaneous (n=71)**; a majority fired **zero** spontaneous spikes over
  an entire recording session **[H]**. Only **6 ± 5%** of KCs respond to a given odor vs **59 ± 14%** of PNs **[H]**.
- KC electrical constants from the same paper: resting **−57.8 mV**, spike threshold **−36.3 mV**
  (**Δ = 21.5 ± 5.6 mV**, n=17); unitary PN→KC EPSP **1.4 mV mean / 1.2 mV median**; spontaneous EPSP rate
  in KCs **32.6 ± 12.7 /s**; ~10 PNs converge per KC **[H]**.
- **P-EN** (compass/angular-velocity): rate rises by only **5.6 ± 3.7 Hz** for fast preferred- vs
  non-preferred-direction turns; angular-velocity bandwidth **145 ± 82 °/s**; spikes lag the rotational
  velocity peak by **123 ± 43 ms** (n=12) (Turner-Evans et al., 2017, *eLife* 6:e23496) **[H]**. E-PG absolute
  rates are not given in text; in-bump E-PG activity is generally in the tens of Hz **[L]**.

**Bottom line for "how hot":** the fly central brain is *sparse and slow*. A defensible target is a
**population mean of ~0.5–5 Hz** with a long tail — most neurons near-silent, a minority of tonic classes
(PNs, slow MNs, some DNs) in the 5–40 Hz band, and only driven sensory/motor lines above 50 Hz **[M]**.
Any whole-brain LIF whose population mean sits above ~10 Hz is running hot.

---

## 2. Visual projection neurons

- **LC10a** — the courtship-tracking channel. Tuned to objects **~15–30° in width and height**; by contrast
  LC9 prefers ~4.5° × ~2° and LC11 ~4.5° (Hindmarsh Sten et al., 2024, *Nature* 636:1102, and its preprint).
  A courted female subtends **~29° wide × ~16° high** on the male retina — squarely inside LC10a's preferred
  band **[H]**. LC10a is the *fru+* LC10 subtype (~60% of LC10-SS1 cells co-express *fru-LexA*; Ribeiro et al.,
  2018, *Cell* 174:607) and is necessary for directed tracking.
- **LC10a gain is state-gated by P1**: gain is selectively increased during courtship, and P1 activity tracks
  moment-to-moment fluctuations in pursuit intensity and continuously tunes LC10a gain; a network model of
  LC10a-with-P1-gain "almost fully specifies" the male's tracking of the female (Hindmarsh Sten et al., 2021,
  *Nature* 595:549) **[H, qualitative]**. Exact fold-change in gain not recoverable from open text **[gap]**.
  Right−left LC10a asymmetry is the steering variable.
- **LC11** — small dark objects (**<10°**, ~4.5° optimum), omnidirectional, excitatory-centre /
  inhibitory-surround sharpening from neighbouring LC11s, driven by T2/T3 (Keleş & Frye, 2017,
  *Curr Biol* 27:686; Keleş et al., 2020, *Cell Rep* 30:2115) **[H]**.
- **LC4 / LPLC2 → giant fiber.** **55 LC4 and 108 LPLC2 cells synapse on the GF lateral dendrite, via 2,442
  and 1,366 synapses respectively — 99.4% of the GF's direct optic-lobe input** (Ache et al., 2019,
  *Curr Biol* 29:1073) **[H]**. LPLC2 encodes **angular size**, LC4 encodes **angular velocity**; GF looming
  response = linear-in-velocity + Gaussian-in-size, and at peak depolarization typically produces a **single
  spike** sufficient to trigger the jump **[H]**. LPLC2 is ultra-selective for outward radial motion via
  motion opponency, strongly driven by dark looming across all tested speeds (Klapoetke et al., 2017,
  *Nature* 551:237) **[H]**.
- **LC16 / LC6** — looming-responsive; LC6 activation elicits jumping, **LC16 elicits backward walking via
  MDN** through an excitatory feedforward circuit (Sen et al., 2017, *Curr Biol* 27:766; Wu et al., 2016,
  *PNAS* 113:E2812) **[H]**.
- **HS / VS.** Graded, essentially non-spiking, resting **Vm ≈ −55 mV** (LJP-corrected; Schnell et al., 2010,
  *J Neurophysiol* 103:1646) **[H]**. Typical visual depolarizations are on the order of **5–15 mV** **[L]**.
  Walking increases HS response amplitude and **shifts the temporal-frequency optimum to higher speeds**, with
  amplification scaling with walking speed (Chiappe et al., 2010, *Curr Biol* 20:1470) **[H]**. Fujiwara et al.
  (2017, *Nat Neurosci* 20:72) show HS receives **three distinct non-visual locomotor signals** and encodes a
  quantitative estimate of the fly's own rotation **in complete darkness**; unbalanced HS activity across
  hemispheres biases walking direction **[H]**. Kim et al. (2015, *Nat Neurosci* 18:1247) show **saccade-related
  potentials** in HS that persist in blind flies (extraretinal → efference copy), with the correct sign and
  timing to cancel self-generated optic flow; visual direction-selective responses are attenuated during
  saccades **[H]**. Exact SRP amplitude in mV not recovered **[gap]**.

---

## 3. Photoreceptors and ocelli

- **R1–6**: graded, non-spiking. They compress **~10 log units** of ambient intensity into a **40–65 mV**
  voltage output range (Song & Juusola synthesis of Juusola & Hardie, 2001, *J Gen Physiol* 117:3) **[H]**.
- **Temporal response**: bandwidth is adaptation- and temperature-dependent, not fixed. Signal bandwidth
  broadens with mean luminance and with temperature; the commonly quoted **~100 Hz 3-dB corner applies to a
  bright-adapted photoreceptor at 25 °C**, falling to the low tens of Hz when dark-adapted (Juusola & Hardie,
  2001, *J Gen Physiol* 117:3 and 117:27) **[M]**. Q₁₀ for information capacity is **6.5** — the fly's visual
  bandwidth is strongly temperature-dependent **[H]**.
- **Adaptation**: raising mean intensity makes responses **larger, faster and more reliable for a given
  contrast** — i.e. the front end is a contrast encoder with luminance-set gain, not an intensity encoder
  (Juusola & Hardie, 2001) **[H]**. Our flyvis front end already assumes contrast input; this is consistent.
- **Ocelli**: three simple eyes, wide-field, unfocused, pointed at the sky. The ocellar ganglion contains
  **62 neurons: 15 local, OCG01 (n=12), OCG02 (n=8), DNp28 (n=2 descending), and 25 centrifugal/feedback**;
  in each ocellus **half the OCG01s are glutamatergic (likely inhibitory) and half cholinergic**;
  **DNp28 projects to the intermediate, haltere, wing and neck tectula** of the VNC (Dorkenwald et al., 2024,
  *Nature* 634:124, FlyWire whole-brain annotation) **[H]**. Functionally the ocellar pathway is a fast,
  low-latency luminance/horizon-tilt detector that feeds gaze- and head-stabilisation and converges with
  compound-eye motion signals on the same descending neurons (Parsons et al., 2006, *J Neurosci* 26:13531;
  Parsons et al., 2010, *J Neurophysiol* 103:1611) **[H, blowfly]**. Latency advantage over the compound eye
  is a few ms **[L]**.

---

## 4. Courtship

**What activates P1 in life.** Three convergent streams:
1. **Contact pheromone (dominant trigger).** *fru+*, **ppk23**-expressing tarsal gustatory neurons detect
   female cuticular hydrocarbons and drive P1 via an ascending VNC interneuron (vAB3); **Gr32a** neurons
   detect male pheromones and inhibit male–male courtship (Clowney et al., 2015, *Neuron* 87:1036;
   Kallman et al., 2015, *eLife* 4:e11188) **[H]**. Kohatsu et al. (2011, *Neuron* 69:498) showed a transient
   Ca²⁺ rise in P1 neurites after tarsal contact with a female in tethered males **[H]**.
2. **Vision.** Female-shaped moving object via LC10a, amplified by P1 itself (Ribeiro et al., 2018;
   Hindmarsh Sten et al., 2021). Motion cues plus P1 jointly control courtship (Kohatsu & Yamamoto, 2012,
   *PNAS* 109:12799) **[H]**.
3. **Suppression.** **cVA** (sensed by ppk23+ GRNs and Or67d ORNs) suppresses P1 excitation by female
   pheromone — the "she's already mated" brake (Clowney et al., 2015) **[H]**. **mAL** is the GABAergic
   inhibitory interneuron onto P1; it is activated by *both* male- and female-pheromone GRNs, so it acts as
   both a male-male veto and a **gain control** on the female-pheromone→P1 response (Kallman et al., 2015;
   Koganezawa et al.; Yamamoto lab) **[H]**.

**P1 activity.** No published in vivo P1 spike rates during natural courtship **[gap]**. Key facts instead:
- P1 activation is **threshold-graded**: low-intensity activation promotes aggression, higher intensity
  promotes wing extension/song (Hoopfer et al., 2015, *eLife* 4:e11346) **[H]**.
- **P1 neurons are not themselves persistently active**; the persistence lives in **pCd**, which is
  persistently active for minutes and is required for P1-evoked persistent courtship/aggression but is not
  sufficient alone (Jung et al., 2020, *Neuron* 105:322) **[H]**.
- Time-resolved ReaChR activation separates song control into a **probabilistic, persistent component (P1)**
  and a **deterministic, command-like component (pIP10)**; social isolation lowers the P1 activation threshold
  (Inagaki et al., 2014, *Nat Methods* 11:325) **[H]**.

**P1 → pIP10 → song.** P1 (pMP4) and pIP10 both elicit authentic song on thermogenetic activation; pIP10 is a
descending command-like neuron terminating in the mesothoracic ganglion; thoracic **dPR1, vPR6, vMS11** form
the pulse CPG (von Philipsborn et al., 2011, *Neuron* 69:509) **[H]**. Roemschied et al. (2023, *Nature*
622:794) refine this: a **sine network** (pIP10, TN1A, dMS2, vPR9) and a **pulse network** that additionally
recruits pMP2, dPR1, dMS9, vMS12; **pIP10 is active during both modes** and biases song choice
state-dependently **[H]**.

**Song structure.** Pulse song: trains of 2–50 pulses, **carrier 150–300 Hz**, **interpulse interval ~35 ms**
→ **pulse rate ≈ 29 Hz** (Coen et al., 2014, *Nature* 507:233; Bennet-Clark & Ewing) **[H]**. Sine song:
**fundamental 140–170 Hz** **[H]**. Song mode is driven by fast fluctuations in the male's visual and
self-motion signals — male slows and switches modes as a function of female distance and relative speed
(Coen et al., 2014) **[H]**.

**What the female hears.** Near-field particle velocity, transduced by the arista/antennal rotation into
**Johnston's organ** JO-A/JO-B neurons; *D. melanogaster* auditory sensitivity spans roughly **100–300 Hz**,
matching pulse-carrier and sine frequencies (Kamikouchi et al., 2009, *Nature* 458:165; Lai et al., 2012,
*PNAS* 109:2607) **[H]**.

**Female receptivity.** A single pair of **vpoDNs** drives vaginal plate opening; they are excited by
song-tuned auditory **vpoENs** and by **pC1** (which encodes mating status). **vpoDN — but not vpoEN — song
responses are attenuated after mating, and that attenuation is pC1-mediated** (Wang et al., 2021, *Nature*
589:577) **[H]**. Female pC1 comprises **7 cell types**; **pC1-α** drives minutes-long persistent shoving/
chasing and persistent activity across a recurrent pC1↔aIPg network (Deutsch et al., 2020, *eLife* 9:e59502) **[H]**.

---

## 5. Male-vs-female LIF calibration

**What Shiu 2024 actually assumed** (Shiu et al., 2024, *Nature* 634:210; parameters read from the reference
implementation `philshiu/Drosophila_brain_model/model.py`) **[H]**:

| parameter | value | source cited in code |
|---|---|---|
| resting = reset potential | **−52 mV** | Kakaria & de Bivort, 2017 |
| spike threshold | **−45 mV** (7 mV above rest) | Kakaria & de Bivort, 2017 |
| membrane time constant | **20 ms** (2 pF × 10 GΩ-equivalent: 0.002 µF × 10 MΩ) | " |
| synaptic (alpha) time constant | **5 ms** | Jürgensen et al., 2021 |
| refractory period | **2.2 ms** | Lazar et al., 2021 |
| synaptic delay | **1.8 ms** | Paul et al., 2015 |
| **weight per synapse** | **0.275 mV** | **free parameter** |
| Poisson drive to stimulated neurons | **150 Hz**, weight scaled ×250 | default |
| trial | 1000 ms × 30 runs | default |

Consequence: with no leak, **7 mV / 0.275 mV ≈ 26 coincident synapses** fire a neuron. For comparison, a real
KC needs **21.5 mV** of depolarization with **1.2–1.4 mV** unitary PN EPSPs → **~15–18 coincident inputs**
(Turner et al., 2008). Same order; 0.275 mV/synapse is a defensible per-synapse quantum, and our problem is
almost certainly in the **synapse counts**, not the per-synapse weight.

**The FIB-SEM vs ssTEM asymmetry — this is very likely the source of the 2× male/female discrepancy.**
A systematic comparison of synapse detection across the major fly EM volumes finds that **FIB-SEM
reconstructions detect ~1.49× more synapses than SS-TEM reconstructions** (geometric mean over pairwise
dataset comparisons; range **0.89–1.95**), driven by isotropic 8×8×8 nm FIB-SEM voxels versus anisotropic
4×4×40 nm ssTEM sections which miss synapses oriented perpendicular to the cutting plane
(Plaza, 2025, bioRxiv 2025.10.16.682869) **[H]**. The paper's specific male-CNS vs FAFB2 comparison gives
**1.49**, and it argues the missed synapses are approximately randomly distributed, so **a single constant
scaling factor is a reasonable correction** **[H]**. It also reports very different detection probabilities
for strong connections: **hemibrain ~70%, FAFB ~50%, BANC ~40%** **[H]**, with the caveat that "a completely
unambiguous comparison is not possible from the data given."

**MaleCNS and hemibrain are FIB-SEM; FlyWire/FAFB is ssTEM.** So every edge weight in our male connectome is
inflated ~1.5× relative to the FlyWire weights that `w_syn = 0.275 mV` was tuned against. Because LIF firing
rate is a superlinear function of drive near threshold, a 1.5× weight inflation easily produces a ~2×
population-rate inflation. **This predicts our exact symptom.**

Corroborating: Schlegel et al. (2024, *Nature* 634:139) find that **connections >10 unitary synapses or
>1% of a target's input are highly conserved** across hemispheres and brains, but **connection weights are
"surprisingly variable" within and across animals**; ~1 in 6 cell types differs in count between hemispheres
and ~1 in 3 across brains, though the mean per-type cell-count difference is small (**0.3 ± 1.8** within,
**0.8 ± 10** across) **[H]**. So topology transfers; weights do not.

---

## 6. Interactions a modeller would not expect

1. **Visual gain is not constant — it tracks locomotor state.** Walking raises HS response amplitude and
   shifts the temporal-frequency optimum toward higher speeds, scaled by walking speed (Chiappe et al., 2010).
   In flight the same boost on VS cells is **octopaminergic** and OA neurons are necessary *and* sufficient
   for it (Suver et al., 2012, *Curr Biol* 22:2294). A static optic-lobe→LIF gain is wrong by a
   state-dependent factor.
2. **P1 gates LC10a.** Sexual arousal multiplies the visual gain of the very pathway that drives pursuit
   (Hindmarsh Sten et al., 2021) — a positive feedback loop between internal state and sensory drive.
   The 2024 follow-up adds two more state motifs: **dendritic disinhibition** of selected feature detectors
   and a **toggle switch between two feature detectors** (LC10a vs LC9/LC11) (Hindmarsh Sten et al., 2024,
   *Nature* 636:1102).
3. **Corollary discharge in HS during saccades** — extraretinal, present in blind flies, timed and signed to
   cancel self-generated flow (Kim et al., 2015). Without it, a closed-loop sim will fight its own turns.
4. **HS carries a walking estimate in darkness** from three non-visual locomotor signals (Fujiwara et al.,
   2017) — "visual" neurons are partly motor neurons.
5. **DNa02 is multimodal and action-referenced**, not stimulus-referenced: ipsilateral for attractive odor,
   contralateral for aversive heat (Rayshubskiy et al., 2020/2025). It also sits **two synapses downstream of
   the compass** via PFL3 and receives input from reinforcement-learning centres.
6. **Halting is active, not "stop driving."** Sapkal et al. (2024, *Nature* 632:1092) describe two mutually
   exclusive mechanisms: a brain **"walk-OFF"** pathway of GABAergic neurons (**Foxglove** inhibits forward-walking
   DNs including BDN2; **Bluebell** inhibits turning DNs) used during feeding, and a VNC cholinergic
   **"Brake"** that arrests stepping and increases leg-joint resistance, used during grooming.
7. **Hunger/state gates approach.** Hunger restructures spontaneous behaviour and directed exploration of
   novel objects via dopaminergic modulation, and starvation bidirectionally modulates MBON responses through
   six DAN types (reviewed in Lin, Senapati & Tsao, 2019, *Open Biology* 9:180259) **[M — the specific link to
   visual object approach is weaker than the olfactory evidence]**.

---

## 7. Implications for our readouts and drive rules

1. **Male LIF calibration:** divide MaleCNS synapse counts by **1.49** (or set `w_syn = 0.275/1.49 ≈ 0.185 mV`
   for male runs) before anything else — FIB-SEM/ssTEM detection asymmetry is the most parsimonious cause of
   the 2× heat (Plaza 2025, bioRxiv 2025.10.16.682869).
2. **Population-rate sanity target:** central-brain population mean **0.5–5 Hz**, with >50% of neurons under
   1 Hz; treat >10 Hz mean as a calibration failure (Turner et al., 2008; Rayshubskiy et al., 2025).
3. **DNa02 steering gain:** keep the left−right difference rule (it is the published functional form), but
   adopt **5 °/s per Hz** of net difference rather than 3, i.e. ~**5° yaw per net spike per 100 ms chunk**,
   and cap at **±800 °/s**. Mark as a figure-derived estimate.
4. **DNa02 rightward lean:** enforce a **symmetric baseline** — subtract a running per-side baseline over
   ~2 s before differencing. A persistent lean is a bilateral-asymmetry artefact of the connectome, not a
   behaviour; real DNa02 drives zero net rotation at zero net difference (Rayshubskiy et al., 2025, Fig. 3c).
5. **DNa02 dynamic range:** clamp per-side rate to **0–150 Hz**; assume **10–40 Hz** at straight walking
   (derived from Yang et al., 2024).
6. **Motor lag:** insert a **150 ms** delay between DN spiking and applied yaw/stride change
   (Rayshubskiy 2020; Yang 2024).
7. **Leg-MN speed readout:** do **not** use zero as the standing baseline. Model slow MNs as tonically active
   at **~30 Hz** while standing, and weight MN classes by force-per-spike **(slow 0.1 : intermediate 1 :
   fast 10)** rather than counting spikes equally (Azevedo et al., 2020). Cap the walking-speed map at a
   stepping frequency of **~18 Hz**.
8. **flyvis → LIF T4/T5 drive:** the **150 Hz** Poisson cap is the same number as Shiu's default `r_poi`, so it
   is a model convention, not a measurement — T4/T5 are graded cells. Keep it, but note that **contrast, not
   luminance, is the correct input variable** (photoreceptor adaptation, Juusola & Hardie 2001), and add a
   **walking-state gain** (×1.3–2 on HS-projecting channels while walking; Chiappe et al., 2010; Suver et al., 2012).
9. **Ocelli:** if added, model as **2 DNp28 + 20 OCG01/02** wide-field luminance channels with a few-ms latency
   advantage, half of OCG01 inhibitory (Dorkenwald et al., 2024).
10. **P1 → pIP10 drive:** the "enormous drive" problem is expected — in life P1 is not a single-shot trigger.
    Add (a) **pCd-mediated persistence** (minutes-long integrator downstream of P1; Jung et al., 2020), and
    (b) **threshold-graded output** (low P1 → aggression-like, high P1 → song; Hoopfer et al., 2015). Drive P1
    as a slowly-integrating state variable, not a Poisson burst.
11. **P1 sensory drive rule:** P1 rate ∝ (ppk23 tarsal contact) + (LC10a-gated visual target in the **15–30°**
    size band) − (cVA) − (mAL GABA gain control) (Clowney et al., 2015; Kallman et al., 2015;
    Hindmarsh Sten et al., 2024).
12. **LC10a gain must be P1-dependent:** multiply LC10a→steering gain by a P1-derived factor; with fixed gain
    the male will not track (Hindmarsh Sten et al., 2021). Right−left LC10a difference is the courtship
    steering variable, feeding DNa02/DNp09.
13. **Song readout:** pIP10 above threshold → emit pulse train at **IPI 35 ms (≈29 Hz)**, carrier
    **150–300 Hz**; sine at **140–170 Hz**. Let pIP10 be active in both modes and let mode selection follow
    female distance/relative speed (Coen et al., 2014; Roemschied et al., 2023).
14. **Female-side hearing:** JO band-pass **100–300 Hz**; route to vpoEN → vpoDN, and gate vpoDN gain by pC1
    mating status (Wang et al., 2021).
15. **Efference copy:** subtract the commanded yaw from the optic-flow input to HS-equivalent channels with
    the sign that cancels self-motion, ~at saccade onset (Kim et al., 2015; Fujiwara et al., 2017).
16. **Halting:** implement stopping as **active inhibition of forward/turning DNs (walk-OFF)** plus a separate
    **VNC brake** that raises joint resistance — not as a drive going to zero (Sapkal et al., 2024).

### Known gaps (do not fabricate these)
- Absolute DNa02/DNa01 spike rates in Hz, and the published °/s-per-Hz slope — figure-only.
- DNp09 and MDN in vivo firing rates — never recorded.
- P1 firing rates during natural courtship — never recorded.
- LC10a gain fold-change from P1 — not in open text.
- HS saccade-related-potential amplitude in mV — not retrieved.
