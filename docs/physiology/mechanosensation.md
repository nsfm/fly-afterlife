# Drosophila mechanosensation: drive parameters for Poisson sensory sources

Scope: what each mechanosensory receptor class in the MaleCNS connectome encodes, and at what
rate it should be driven per 10 ms frame. Every number is cited. **Species marks: all entries are
*Drosophila melanogaster* unless tagged `[stick insect]`, `[locust]`, `[cockroach]`, `[blowfly]`,
`[crane fly]`.** Insect-comparative numbers are used only where fly data does not exist.

A hard caveat that shapes everything below: **almost no fly mechanoreceptor class has published
spike-rate-vs-time curves.** Drosophila mechanosensory physiology since ~2015 is overwhelmingly
GCaMP ΔF/F, not extracellular spike trains. Rates given as "evoked Hz" are therefore of three
kinds, marked per row: **(M)** measured in fly spikes/s, **(C)** measured in a comparative insect
in spikes/s, **(E)** estimated by me from ΔF/F kinetics + comparative rates. Treat (E) as a
modelling prior, not a fact.

---

## 1. Per-class encoding table

### 1a. Bristle afferents (`mechanosensory_tactile`, 2,503 cells)

One cholinergic sensory neuron per bristle; ~500 tactile bristles per leg, ~120 on the tibia alone
(Schubiger & Hadorn 1968, via Sustar & Tuthill 2023, *eLife*). Directionally selective: each
responds to deflection in one preferred direction set by hair-socket asymmetry (Tuthill & Wilson
2016, *Cell*).

| Property | Value | Source |
|---|---|---|
| Encodes | Deflection direction + velocity of a single hair; exteroceptive touch, dust, grooming targets | Tuthill & Wilson 2016, *Cell* 164:1046 |
| Rest Hz | **0** (no spontaneous activity reported in any fly bristle recording) | Corfas & Dudai 1990, *J Neurosci* 10:491 |
| Evoked Hz | Burst on deflection onset; **~100–300 Hz peak (E)**, decaying to a maintained plateau | Corfas & Dudai 1990 |
| Phasic/tonic | **Slowly adapting** — fly work has found *only* slowly-adapting bristles; high-threshold rapidly-adapting bristles have not been shown in Drosophila | Tuthill & Wilson 2016, *Curr Biol* 26:R1022 |
| Adaptation τ | Firing rate decays during sustained deflection ("typical of a slowly adapting mechanoreceptor"); **τ ≈ 20–50 ms (E)** to a low plateau | Corfas & Dudai 1990 |
| Fatigue | Second, slower process: response *magnitude* falls with repeated stimulation, depends on stimulus duration and repetition rate, recovers with rest, cAMP-dependent (reduced in *rut*, faster in *dnc*) | Corfas & Dudai 1990 |
| Velocity threshold `[locust]` | Two classes: high-threshold phasic, 21.1 ± 4.2 °/s, adapts out after **~11 cycles at 5 Hz**; low-threshold phaso-tonic, <3 °/s, still firing after **200 cycles at 5 Hz** (C) | Newland 1991, *JEB* 155:487 |
| Central latency | Single bristle spike → EPSP in VNC 2nd-order neuron at **3 ms**, trial SD <1 ms, monosynaptic | Tuthill & Wilson 2016, *Cell* |

### 1b. Leg chordotonal — femoral chordotonal organ (FeCO), 152 neurons/leg

| Subtype | Encodes | Rest | Evoked | Phasic/tonic | Adaptation | Source |
|---|---|---|---|---|---|---|
| **claw** (~25/leg) | Femur–tibia *position*; population encodes deviation from ~80°; split into flexion-tuned (0–90°) and extension-tuned (90–180°) subgroups, individual cells narrowly tuned | Nonzero — some claw cells active at any angle | **~5–80 Hz (E)**, monotonic in angle | **Tonic, non-adapting** | None over seconds | Mamiya et al. 2018, *Neuron* 100:636; Dallmann et al. 2025, *Nature* |
| **hook** | Directional tibia *movement*; flexion- or extension-selective (DSI 0.811 ± 0.028); velocity-graded, tested 180–1440 °/s | 0 | **~50–300 Hz (E)** scaled by |ω| | **Phasic**, strictly directional | Decays rapidly; **no tonic activity during hold** | Mamiya et al. 2018 |
| **club** | Bidirectional movement transients + **tibia vibration**, 100–2000 Hz, best ~400 Hz at 0.9 µm, ~800 Hz at 0.054 µm amplitude; dendrites carry a tonotopic map; single cells tuned 200 Hz → 1600 Hz; response plateaus ~800 Hz | 0 | **~50–200 Hz (E)**, entrainable to vibration | **Phasic** | Rapid | Mamiya et al. 2018; Mamiya et al. 2023, *Neuron* |
| Thresholds | Claw mechanical threshold **>10×** club's | | | | | Mamiya et al. 2023 |
| `[stick insect]` fCO | 80 of ~500 afferents sense position/velocity/acceleration; vibration sensitivity 10 Hz–4 kHz, max 200–800 Hz; **hysteresis**: rate-vs-angle depends on movement history | | | | | Field & Pflüger, via Tuthill & Wilson 2016 *Curr Biol* |

Note: club neurons are functionally **exteroceptive** — their signal is pooled across legs and sent
to brain mechanosensory regions, not to local motor circuits (Lee et al. 2025, *Nat Commun*).

### 1c. Campaniform sensilla (CS) — leg

| Property | Value | Source |
|---|---|---|
| Encodes | Cuticular strain = **load**; each dome directionally selective by its long axis | Tuthill & Wilson 2016, *Curr Biol* |
| Counts | ~1200 CS over all legs, wings, halteres, antennae of the fly; leg CS mapped per segment (Tr/Fe/Ti/Ta1–5) | Dinges et al. 2021, *J Comp Neurol* 529:905 |
| Subtypes | Rapidly-adapting and slowly-adapting classes; groups share directional sensitivity | Tuthill & Wilson 2016, *Curr Biol* |
| Rest Hz | ~0 unloaded | Zill et al. 2024, *J Neurophysiol* `[stick insect]` |
| Evoked Hz `[cockroach]` | Recording axes in the canonical figure run to **100/200/400 spikes/s** (C) | Tuthill & Wilson 2016, *Curr Biol* Fig. 3 |
| Phasic/tonic | **Strongly rate-sensitive (dF/dt).** Discharge maximal and largely confined to the *rising* phase of force; adapts hard during hold. Regression of rate on force rate R² = 0.78 level / 0.71 uphill / 0.69 downhill | Zill et al. 2024, *J Neurophysiol* `[stick insect]` |
| Unloading channel | A separate subgroup (6A-type) fires only on force **decrease**; maximal at complete unloading, minimal or absent under large sustained load — tuned to distinguish slipping from normal gait unloading. Rate falls with offset load, slope **−13.7** `[cockroach]` | Harris, Szczecinski, Büschges & Zill 2022, *J Neurophysiol* 128:790 |
| Swing | No CS activity reported during swing | Zill et al. 2024 |

### 1d. Hair plates

| Property | Value | Source |
|---|---|---|
| Counts | **214 hair-plate neurons in 42 hair plates** across the six legs; one neuron per hair | Pratt et al. 2026, *Nat Commun* 17 (s41467-026-69333-z) |
| Encodes | **Joint limit detection.** CxHP8 (front-leg thorax–coxa) fires at extremes of coxa inward rotation + adduction, i.e. anterior leg limits | Pratt et al. 2026 |
| Rest / evoked | 0 inside the working range; **tonic** ramp once the hairs are deflected near the limit | Pratt et al. 2026 |
| Phasic/tonic | **Tonic** in the fly. `[cockroach]`/`[locust]` hair plates come in both rapidly-adapting (phasic) and slowly-adapting (tonic) types; no phasic tuning found among fly hair plates so far | Pratt et al. 2026; Tuthill & Wilson 2016, *Curr Biol* |
| Output | 75% of CxHP8 output synapses (2279 ± 482 per axon) go to leg motor/premotor circuits; excites posterior movers, inhibits anterior movers | Pratt et al. 2026 |

### 1e. Haltere campaniforms (`dorsal metathoracic nerve`, 396 cells ≈ 2 × ~140 CS + other)

| Property | Value | Source |
|---|---|---|
| Counts | **~140 campaniform sensilla per haltere** (vs <50 on the wing); fields dF1, dF2, dF3, vF1, vF2 with orthogonal row orientations | Sharma, Sustar, Omoto & Dickinson 2026, *JEB* 229:jeb250431; Verbe et al. 2024, *Curr Biol* 34 |
| Encodes | Strain from haltere oscillation ± Coriolis/lateral deflection during body rotation | Verbe et al. 2024 |
| Firing | **One action potential at a fixed phase per stroke cycle** (Drosophila wingstroke ≈ 4–5 ms, so ~200–250 Hz *in flight*) | Tuthill & Wilson 2016, *Curr Biol*; Fayyazuddin & Dickinson 1996, *J Neurosci* 16:5225 |
| Phase precision `[crane fly]` | Vector strength 0.81–1.0, median 0.97 ± 0.05; activation thresholds 93 ± 57 Hz / 140 ± 26° (self-generated) vs 14 ± 9 Hz / 26 ± 24° (motor-driven); follows oscillation up to ~150 Hz | Yarger & Fox 2018, *Proc R Soc B* 285:20181759; Fox & Daniel 2008 |
| Adaptation | Not adapting in the usual sense — it is a **1:1 phase clock**, not a rate code | Fayyazuddin & Dickinson 1996 |

### 1f. Wing campaniforms and wing sensilla (`accessory dorsal mesothoracic nerve`, 237 cells)

**490 sensory axons** in the left wing nerve: ~53 campaniform sensilla (~36 proximal, ~17 distal),
tegula chordotonal ~14, radius chordotonal ~24, tegula hair plate ~5, and ~364 margin bristles
(Lesser et al. 2026, *eLife* 14:RP107867). Wing CS also fire **one spike per wingstroke at a
characteristic phase**; tegula CS synapse directly onto the b1 steering motor neuron, which itself
fires one phase-locked spike per cycle (Fayyazuddin & Dickinson 1996). No electrophysiology during
flight exists — "prohibitively challenging" (Lesser et al. 2026).

### 1g. Johnston's organ (JO), 672 cells in connectome; **477 ± 24 JONs per antenna**

Counts: Kamikouchi, Shimada & Ito 2006, *J Comp Neurol*; JO-D ≈ 40 cells. JO-F is a sixth,
ventrally-projecting zone (Hampel et al. 2020, *eLife* 9:e59976).

| Subgroup | Encodes | Best frequency | Phasic/tonic | Source |
|---|---|---|---|---|
| **JO-A** | Vibration / sound, high frequency | peak **~400 Hz** | phasic (vibration-locked) | Matsuo et al. 2014, *Front Physiol* 5:179 |
| **JO-B** | Vibration / sound, low frequency; courtship song | **<100 Hz** preference; most sensitive band of the whole organ ~100–300 Hz | phasic | Matsuo et al. 2014; Kamikouchi et al. 2009, *Nature* 458:165 |
| **JO-C** | Static antennal deflection (wind, gravity), directional (anterior vs posterior) | n/a | **tonic** | Yorozu et al. 2009, *Nature* 458:201; Matsuo et al. 2014 |
| **JO-D** | Both vibration and anterior deflection | **100–200 Hz** | tonic to vibration + deflection | Matsuo et al. 2014 |
| **JO-E** | Static deflection (wind, gravity), opposite direction preference to JO-C | n/a | **tonic** | Yorozu et al. 2009 |
| **JO-F** | Unknown selectivity — does *not* respond to push/pull or to tested vibration frequencies; drives antennal grooming + backward locomotion | unknown | unknown | Hampel et al. 2020 |

Sensitivity: behavioural startle threshold **1.2 × 10⁻⁴ m/s** particle velocity (65 dB SVL);
antennal-nerve field-potential threshold **5.7 × 10⁻⁵ m/s**; that corresponds to **74 nm**
displacement of the arista lever, a rotation of **5 × 10⁻⁴ rad**. JON spike → giant-fibre current
in **<300 µs**. Antennal resonance **160–300 Hz** at low intensity. Adaptation to a step recovers
**within 27 ms** (Lehnert et al. 2013, *Neuron* 77:115). Stimulus amplitudes used in the subgroup
imaging: ~10 µm vibration, ~25 µm static deflection at the arista midpoint (Matsuo et al. 2014).
Most scolopidia pair **one vibration-sensitive with one deflection-sensitive JON** (Ishikawa et al.
2020, *Front Physiol* 10:1552) — so a scolopidium is a two-channel, not one-channel, unit.

No single-unit JON spike rates are published. All JO drive rates below are (E).

---

## 2. Walking biomechanics for a gait model

| Quantity | Value | Source |
|---|---|---|
| Forward speed range | 7.2–44.7 mm/s (most flies ~28 mm/s); another dataset −1.3 to 30.4 mm/s (2.5–97.5 pct), modes at 0 and ~17.5 mm/s | Mendes et al. 2013, *eLife* 2:e00231; DeAngelis et al. 2019, *eLife* 8:e46409 |
| Speed in body lengths | 11–32 mm/s = **5–16 BL/s** (wtCS); *w1118* 4–31 mm/s = 2–15 BL/s | Wosnitza et al. 2013, *JEB* 216:480 |
| Step frequency | Speed is controlled **almost exclusively by step frequency**, not step amplitude (step amplitude R² ~0.03–0.16 vs speed); stance trajectory ≈ 0.5 BL regardless of speed | Wosnitza et al. 2013 |
| Step period | Falls hyperbolically with speed (R² = 0.76), **plateaus at ~60 ms ⇒ ~16 Hz** at max speed | Mendes et al. 2013; Wosnitza et al. 2013 |
| Stance duration | τ_stance ∝ v‖^**−1.025** (R² = 0.59, fit a = 932.8 ms at v₀ = 1 mm/s); range **30–140 ms** | DeAngelis et al. 2019; Mamiya et al. 2018 methods citing Mendes/Wosnitza |
| Swing duration | Approximately **constant, 20–45 ms** across speeds (modulation small relative to stance) | Wosnitza et al. 2013; DeAngelis et al. 2019; Mendes et al. 2013 |
| Gait vs speed | <20 mm/s (<5 BL/s): tetrapod and undefined patterns dominate. 20–34 mm/s (5–10 BL/s): mixed. >34 mm/s (>10 BL/s): tripod dominant, tripod coordination strength ≈ 0.85. Transitions are **gradual, not discrete** | Mendes et al. 2013; Wosnitza et al. 2013 |
| Manifold view | There are no discrete gaits: a single continuum, symmetric variability driven by one parameter (stance duration) | DeAngelis et al. 2019 |
| Phases | Contralateral pairs: 0.5 cycles at all speeds. Ipsilateral mid–fore ≈ 0.4, hind–fore ≈ 0.85. Within a tripod, front leg swings first, mid lags ~15°, hind a further ~15° | DeAngelis et al. 2019; Wosnitza et al. 2013 |
| Joint kinematics | Femur–tibia angular velocities during walking estimated at **2400–3200 °/s swing, 2000–2670 °/s stance**; but joint excursion is only ~60° in fast-walking `[cockroach]`, not the full 0–180° | Mamiya et al. 2018 methods |
| **Sensory delay** | **5–15 ms** (spike in leg periphery → central effect); model uses 10 ms | Karashchuk et al. 2025, *eLife* RP (reviewed preprint) |
| **Motor delay** | **20–40 ms**; model uses 30 ms | Karashchuk et al. 2025 |

**Who fires when.** Swing: hook and club (movement transients), claw tracking the angle trajectory,
hair plates only at the two ends of the excursion. Stance: claw tonic at the loaded angle; **CS burst
at stance onset** on the rising force phase and adapt out during mid-stance; the unloading CS
subgroup fires at the stance→swing transition; hair plate CxHP8 is engaged near the swing-to-stance
transition and silencing it shifts that transition medially (Pratt et al. 2026). CS+hair-plate
silencing impairs step kinematics and inter-leg coordination **especially at fast walking speeds**
(Pratt et al. 2026, citing their earlier work).

---

## 3. Halteres and wings in a *walking* fly

**Drosophila does not oscillate its halteres while walking** — measured directly across fly taxa;
by contrast *Sarcophaga* does. Haltere ablation has no effect on the proportion of Drosophila
climbing or falling (Hall et al. 2015, *Biol Lett* 11:20150845). Consequences:

- No wingstroke ⇒ **no phase-locked haltere or wing CS spikes** during walking. The 1-spike-per-cycle
  code (§1e, §1f) simply does not run.
- Residual drive should come only from body accelerations and substrate perturbation, and there is
  no Drosophila measurement of that. `[crane fly]`: leg movements drive haltere oscillations in
  *standing* crane flies and haltere input stabilises standing posture against perturbations
  (*Current Biology*, 2026) — so a nonzero low-rate haltere channel during standing/walking is
  biologically plausible in *some* flies, but is **not** established in Drosophila.
- Related: haltere removal alters gravity responses in standing flies (Kathman & Fox 2018,
  *JEB* 221:jeb181719).
- Wing sensors during walking: wingbeat-driven activity absent. Margin bristles (~364 of the 490
  wing axons) are ordinary tactile afferents and will fire on wing contact during grooming or
  folding. Tegula/radius chordotonals encode wing position and will be near-static.
- Redundancy warning: silencing up to **40 of the 140** haltere campaniforms produced effects on
  equilibrium-reflex phase "very close to zero" (Sharma et al. 2026). Do not expect this channel to
  be individually load-bearing in a simulation either.

---

## 4. Johnston's organ: wind, gravity, sound, and self-generated airflow

**Wind vs sound are different intrinsic channels in the same organ.** Sound-sensitive JONs are
**phasically** activated by small bidirectional aristal displacements; wind-sensitive JONs are
**tonically** activated by unidirectional, static, larger-magnitude deflections (Yorozu et al. 2009,
*Nature* 458:201). Gravity: the distal antennal segment moves detectably with gravitational
orientation; JO-C/E are the gravity channel (Kamikouchi et al. 2009, *Nature* 458:165).

**Wind direction.** A single antenna's displacement is *ambiguous* with respect to azimuth; the
**left-minus-right displacement difference** is the linear code. Second-order AMMC neurons inherit
the single-antenna ambiguity and are driven mainly by the ipsilateral antenna; novel wedge
projection neurons (WPNs) integrate across antennae, pooling ≥3 classes of second-order neuron, to
linearise the azimuth code (Suver et al. 2019, *Neuron* 102:828).

**Sound / courtship song.** Pulse song: ~35 ms inter-pulse interval, carrier in the JO-B band; sine
song ~160 Hz. Fly hearing is confined to ~**100–300 Hz** and to the *particle-velocity* component,
so it is a near-field channel only. JO-B ≲100 Hz, JO-A ~400 Hz, JO-D 100–200 Hz (§1g).

**Self-generated airflow ("wing wash").** In *flight*, most JO classes respond strongly to antennal
oscillation **at the wingbeat frequency** — the fly's own wingbeat mechanically drives its antennae
(Mamiya & Dickinson 2015, *J Neurosci* 35:7977). Antennal mechanoreception provides a fast airspeed
estimate that stabilises the slower vision-based groundspeed controller against gusts (Fuller et al.
2014, *PNAS* 111:E1182). **For a walking fly this channel is absent** — no wingbeat, no wing wash.
What remains is ambient wind plus self-motion-induced airflow at walking speeds (≤45 mm/s), which is
small: antennal position shifts only **+1.45° per 50 cm/s** of wind laterally, and **−0.80° per
50 cm/s** medially in darkness (Mamiya et al. 2011, *J Neurosci* 31:6900).

**Active antennal control.** Flies make both slow adaptive and fast flicking antennal movements in
response to wind-induced deflection — but **not** to attractive odour. Driving the antennal motor
neurons/muscle adjusts the **gain and acuity** of wind-direction encoding (Suver, Medina & Nagel
2023, *Curr Biol* 33:780). The antennal transfer function is therefore state-dependent, not fixed.

---

## 5. VNC reflexes these afferents close

| Pathway | Effect | Latency / magnitude | Source |
|---|---|---|---|
| extension-tuned **claw** → 13Bα (GABAergic, non-spiking) | Tonic membrane-potential code of joint angle; active only when tibia extended past **~90°**; ~20% hysteresis between extension and flexion pathways. Optogenetic activation → **femur–tibia flexion** (postural resistance reflex) | seconds-scale postural | Agrawal et al. 2020, *eLife* 9:e60299 |
| **hook** + **club** → 9Aα (GABAergic) | Prefers fast flexing swing movements; maximal to **1600–2000 Hz** vibration. Activation → tibia–tarsus and femur–tibia **extension** (smaller than 13Bα effect) | — | Agrawal et al. 2020 |
| **club** → 10Bα (cholinergic) | Transient bidirectional; vibration sensitivity **gated by tibia position**. Activation makes walking flies **pause/freeze**, at **~200 ms** and for ~200 ms *regardless of stimulus duration* (0/90/360/720 ms all gave the same pause) | 200 ms | Agrawal et al. 2020 |
| **club** ascending | Pooled across legs → brain mechanosensory areas: exteroceptive vibration sense, not local motor control | — | Lee et al. 2025, *Nat Commun* |
| **hair plate CxHP8** → premotor/motor | Excites posterior leg movers, inhibits anterior movers; activation drives posterior postural reflex; silencing shifts the **swing-to-stance transition** medially | — | Pratt et al. 2026, *Nat Commun* |
| **bristle** → 3 parallel VNC classes | Intersegmental (pools bristles along whole leg), midline local (same-limb spatial comparison), midline projection (bilateral comparison). One bristle diverges onto all three ⇒ **parallel, not hierarchical**. Drives aimed grooming and local avoidance | 3 ms monosynaptic | Tuthill & Wilson 2016, *Cell* |
| **fCO → motor neurons** `[stick insect/locust]` | Classic **resistance reflex**: joint movement excites antagonist MNs to oppose it; reliable across initial angle, direction, velocity | — | Tuthill & Wilson 2016, *Curr Biol* |
| **reflex reversal** `[stick insect]` | During active movement the fCO reflex flips sign to *assist*. Crucially **task-specific**: reversal occurred during ipsilateral front-leg stepping but not contralateral; during forward but not backward walking; when turning toward the manipulated leg but not away | — | Hellekes et al. 2012, via Tuthill & Wilson 2016, *Curr Biol* |
| **CS load feedback** `[stick insect]` | Load signals and fCO movement signals converge on the same premotor networks controlling the femur–tibia joint; CS encode step timing that could drive the stance↔swing transition | — | Tuthill & Wilson 2016, *Curr Biol*; Chen et al. 2021, *Curr Biol* 31:5163 |

Prediction for closing these loops in the connectome: with sensory delay 10 ms and motor delay 30 ms
(§2), the total loop is ~40 ms — comparable to one whole swing phase. A model that closes
proprioceptive loops without those delays will be *more* stable than a fly, and robustness
degrades sharply once delays exceed physiological values (Karashchuk et al. 2025).

---

## 6. Surprises and interactions

1. **Movement feedback is deleted exactly when a modeller would use it.** Hook (movement-encoding)
   axons are presynaptically inhibited during walking and grooming; claw (position) and club
   (vibration) axons are **not**. Hook prediction-vs-measurement correlation drops to r = 0.64
   during self-generated movement vs 0.86 during passive movement; claw stays at 0.91.
   (Dallmann et al. 2025, *Nature*.)
2. **The inhibition is top-down, not reafferent.** A single "chief" 9A GABAergic interneuron supplies
   **57%** of presynaptic input to hook axons; 9A cells supply **83%** of hook GABAergic input; they
   are driven by walking descending neurons (DNg100, DNg97, DNg75, DNa02 — 18%) and grooming DNs
   (DNg12 — 13%), and disinhibited by GABAergic DNg74 which correlates with rest (r = 0.94).
   They are active during walking/grooming and **silent during passive movement**, and recruitment is
   leg-specific. (Dallmann et al. 2025.)
3. **…and silencing it does nothing visible.** Leg-specific optogenetic silencing of 9A neurons in
   walking flies did not affect leg kinematics. The motor system is robust to losing this channel.
   (Dallmann et al. 2025.)
4. **Hair plates escape the gating.** No suppression of hair-plate calcium activity during
   spontaneous leg movement, unlike hook. (Pratt et al. 2026.)
5. **Proprioceptors gate touch.** Optogenetic activation of leg chordotonal neurons *hyperpolarises*
   VNC intersegmental touch neurons and suppresses bristle-evoked depolarisation and spiking. Hair
   plates and campaniforms do **not** do this. So a moving leg is a less touch-sensitive leg.
   (Tuthill & Wilson 2016, *Cell*.)
6. **Bristle–bristle lateral inhibition.** Proximal femur bristles suppress excitation from distal
   tibia bristles in midline local neurons; blocked by picrotoxin. Touch fields are centre-surround,
   not simply additive. (Tuthill & Wilson 2016, *Cell*.)
7. **Corollary discharge reaches the sensory neurons themselves.** Ascending histaminergic neurons
   (MsAHN/MtAHN) carry wing motor state up from the VNC; ~**5–10% of MtAHN output synapses land
   directly on JONs** (JO-A/B), and ~37% on auditory interneurons. MsAHN calcium rise **precedes
   flight initiation by a median of 37 ms**, and they are driven by DNg02. This is an efference copy
   onto the auditory periphery. (Cheong et al. 2024, *Curr Biol* 34.)
8. **The antenna's mechanical gain is under motor control.** Antennal motor neurons and muscle tune
   the gain and acuity of wind encoding; flies flick and re-position antennae in response to wind but
   not to odour. (Suver, Medina & Nagel 2023, *Curr Biol* 33:780.)
9. **Neuromodulation is subtype-specific.** Octopamine increases fCO firing gain **only in tonically
   firing position-encoding neurons**, not phasic ones `[stick insect]`; it can act directly or by
   modulating presynaptic inhibition of afferent terminals `[locust]`. (Ramirez et al. 1993; Matheson,
   via Tuthill & Wilson 2016, *Curr Biol*.)
10. **Presynaptic inhibition of chordotonal terminals is *rhythmic* within the step cycle** `[locust]`
    and can be driven by other proprioceptors in the same leg — a within-cycle gain schedule, not a
    static walk/rest switch. (Wolf & Burrows 1995; Burrows & Matheson 1994, via Tuthill & Wilson 2016.)
11. **Bristle responses fatigue over minutes.** Repeated monotonous stimulation reduces the response,
    changes adaptation kinetics, and recovers only after rest; the process is cAMP-dependent.
    A bristle in repeated contact during walking is not a stationary Poisson source.
    (Corfas & Dudai 1990.)
12. **Chordotonal hysteresis.** Rate-vs-angle depends on the preceding direction of movement; possibly
    compensating for muscle nonlinearity rather than being noise. (Tuthill & Wilson 2016, *Curr Biol*.)
13. **JO adaptation is very fast and recovers in 27 ms** — faster than one 10 ms frame's worth of
    slack allows you to ignore. (Lehnert et al. 2013, *Neuron* 77:115.)
14. **A scolopidium is two channels.** Most JO scolopidia pair one vibration-sensitive with one
    static-deflection-sensitive neuron, so the peripheral complexity is *neural*, not mechanical.
    (Ishikawa et al. 2020, *Front Physiol* 10:1552.)
15. **Vibration→freeze is duration-invariant.** 10Bα activation produces the same ~200 ms pause for
    90 ms and 720 ms stimuli — a triggered fixed-action output, not an integrator. (Agrawal et al. 2020.)

**Connectome bookkeeping caveat to audit before trusting per-class drive.** The reported entry-nerve
counts are hard to reconcile with peripheral anatomy: the prothoracic leg nerve carries only 52
`mechanosensory_proprioceptive` cells, but one front leg alone has ~152 FeCO neurons plus
>200 proprioceptive neurons total (Pratt et al. 2026; Mamiya et al. 2018). Meso/metathoracic counts
(260/268) are closer to a single leg's worth, not a pair's. Likewise 2,503 `mechanosensory_tactile`
against ~500 tactile bristles *per leg* (Schubiger & Hadorn 1968) implies heavy under-reconstruction
or different typing of leg bristle afferents. Scale any population-level drive by what is actually
present, not by peripheral anatomy.

---

## 7. Implications for our drive rules

- **Bristle afferents (2,503):** replace 150 Hz-tonic-while-contacting with a phasic-tonic kernel —
  onset burst ~200 Hz for the first 20–30 ms, exponential decay τ ≈ 30 ms to a **10–25 Hz plateau**
  for as long as contact holds, 0 Hz otherwise; scale peak by deflection velocity and gate by the
  bristle's preferred direction (fire only ~half the bristles in a contact patch).
- **Bristle fatigue:** multiply each bristle's peak by a slow depression factor that decrements per
  contact and recovers with τ on the order of seconds — repeated contact during walking should not
  keep producing full-amplitude bursts (Corfas & Dudai 1990).
- **FeCO claw:** tonic, non-adapting, rate a monotonic function of femur–tibia angle around a ~80°
  set point, 5–80 Hz, **nonzero at rest** — drive it during standing, not just walking.
- **FeCO hook:** zero except during movement; rate ∝ |angular velocity| in the cell's preferred
  direction only; decay τ ≈ 30–50 ms after movement stops; then **multiply by a 0.2–0.5 suppression
  factor whenever the sim is in a self-generated-movement state (walking/grooming)**, gated by
  descending walk commands, not by leg movement itself (Dallmann et al. 2025).
- **FeCO club:** zero at rest; transient burst on every movement reversal; plus a vibration channel
  driven by substrate/self vibration with per-cell best frequency drawn 200–1600 Hz, saturating ~800 Hz.
- **Leg campaniform sensilla:** drive by **dF/dt**, not F — burst 100–300 Hz for ~20–40 ms at stance
  onset, adapt to near-zero through mid-stance even under sustained load, and give a *separate*
  unloading subpopulation a burst at the stance→swing transition scaled by how completely the leg
  unloads. Silent in swing.
- **Hair plates (214):** zero throughout the normal joint range; tonic 20–60 Hz once the joint enters
  the outer ~10–15% of its excursion; **do not apply the walking suppression factor** (Pratt et al. 2026).
- **Haltere campaniforms (396):** in a walking fly, **near-silent** — no oscillation, no phase code
  (Hall et al. 2015). Give a small rate (≲5 Hz) proportional to body angular acceleration, and flag
  it as unmeasured; do not port the flight 200 Hz phase-locked drive.
- **Wing campaniforms/sensilla (237):** silent baseline during walking; drive wing margin bristles as
  ordinary tactile afferents on wing contact (grooming, folding); drive tegula/radius chordotonals
  from wing joint angle as slow tonic.
- **JO-A (sound, high freq):** 0 at rest; drive from the 200–800 Hz band of any near-field acoustic
  input, peak ~400 Hz; phasic, re-adapting with τ ≈ 27 ms.
- **JO-B (sound, low freq):** same but tuned <100–300 Hz; this is the courtship-song channel — drive
  from pulse trains at ~35 ms IPI and ~160 Hz sine.
- **JO-C / JO-E (wind, gravity):** **tonic**, opposite direction preferences; drive from *static*
  antennal deflection = (ambient airflow + gravity vector), with the wind azimuth code built from
  **left-minus-right** deflection, not per-antenna magnitude (Suver et al. 2019). Nonzero baseline
  from gravity even in still air.
- **JO-D:** mixed — tonic deflection term plus a 100–200 Hz vibration term.
- **JO-F:** leave at rest unless you are modelling antennal grooming/backward walking; selectivity is
  unknown (Hampel et al. 2020).
- **Global:** apply a **10 ms sensory delay** between simulated mechanics and the Poisson rate, and a
  **30 ms motor delay** on the output side, before judging whether any closed loop is stable
  (Karashchuk et al. 2025).
- **Do not expect loop closure to change behaviour much.** Silencing 9A presynaptic inhibition, or
  40/140 haltere campaniforms, or CxHP8, each produced small or null kinematic effects
  (Dallmann et al. 2025; Sharma et al. 2026; Pratt et al. 2026). Redundancy is the rule; a
  connectome sim that shows a large effect from one afferent class is probably wrong.
