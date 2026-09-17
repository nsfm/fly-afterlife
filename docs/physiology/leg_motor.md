# Drosophila leg motor control: from MN spike counts to a body command

Scope: how to convert per-type leg motor-neuron (MN) spike counts, read out of the MaleCNS LIF sim
every 100 ms, into a forward-speed and yaw command. Every claim is cited. Marks used throughout:
**(M)** measured in *Drosophila*; **(C)** measured in another insect (`[stick insect]`,
`[cockroach]`) and imported; **(E)** my estimate from adjacent data — a modelling prior, not a fact.

Two corrections to the brief before anything else:

1. **Azevedo et al. 2020 is *eLife* 9:e56754, not *Current Biology*.** ("A size principle for
   recruitment of Drosophila leg motor neurons.") Azevedo et al. 2024, *Nature* 631:360–368, is a
   different paper — the FANC female VNC connectome.
2. **`MNad##` is not a leg MN type.** In the MANC systematic nomenclature every MN is named
   `MN` + two-letter muscle-category code + number; `ad` = **abdominal** (Marin et al. 2024, *eLife*
   13:RP97766). `fl`/`ml`/`hl` = front/middle/hind leg; `wm` = wing, `hm` = haltere, `nm` = neck,
   `xm` = unknown. If `MNad##` types are inside your 699-cell "leg MN" set, the set is
   contaminated — see §6.

A third flag: MANC contains **392 leg MNs with assigned muscle targets (142 in T1, 119 in T2, 131 in
T3)** (Cheong et al. 2024, *eLife* 13:RP96084). Your 699 is ~1.8× that. Either the MaleCNS
annotation is more complete, or the filter is pulling in abdominal/neck/wing MNs and leg-neuropil
non-MNs. Resolve this against the `subclass` and `somaNeuromere` fields before trusting any
left−right scalar.

---

## 1. Leg MN atlas

Ground truth on muscle identity: 14 intrinsic leg muscles plus 3–5 body-wall (thoracic) muscles
move each leg (Miller 1950, in *Biology of Drosophila*; Soler et al. 2004, *Development* 131:6041).
Azevedo et al. 2020 (*eLife*) count "14 muscles innervated by just 53 motor neurons" for the leg
proper; Lesser et al. 2024 (*Nature* 631:369–377), reconstructing the whole left front leg in FANC,
count **18 muscles / 69 MNs**, the difference being body-wall muscles and accessory subdivisions.
Most muscles have **2–8 motor units** (Lesser et al. 2024).

Joints, proximal→distal: thorax–coxa (**ThC**), coxa–trochanter (**CTr**), trochanter–femur
(**TrF**, fused in adult), femur–tibia (**FTi**), tibia–tarsus (**TiTa**) (Soler et al. 2004).

### 1a. Leg MN types (MANC/MaleCNS names)

`Stance?` = does the muscle act during stance (propulsive/supportive, **S**) or swing
(protractive/levating, **W**)? Assignments for ThC and CTr follow insect EMG: retractor/depressor/
flexor active in stance, protractor/levator/extensor in swing (Rosenbaum et al. 2010,
*J Neurophysiol* 104:1681 `[stick insect]`; Bidaye, Bockemühl & Büschges 2018, *J Neurophysiol*
119:459).

| MANC name | Muscle | Joint | Action | Segment | Class / force per spike | Tonic Hz standing | Stance? |
|---|---|---|---|---|---|---|---|
| **Sternal anterior rotator MN** | sternal anterior rotator | ThC | rotation → **promotion** (protraction) | coxa | mixed, unmeasured | unmeasured | **W** |
| **Sternal posterior rotator MN** | sternal posterior rotator | ThC | rotation → **remotion** (retraction) | coxa | mixed, unmeasured | unmeasured | **S** |
| **Pleural remotor/abductor MN** | pleural remotor + abductor | ThC | **remotion + abduction** | coxa | mixed, unmeasured | unmeasured | **S (main propulsor)** |
| (sterno/tergopleural) **promotor MN** | coxa promotor, 4 MNs | ThC | **promotion** | coxa | mixed | unmeasured | **W** |
| (sternal) **adductor MN** | sternal adductor | ThC | adduction (pulls leg to midline) | coxa | mixed | unmeasured | postural |
| **Sternotrochanter MN** | sterno-trochanter (extensor) | CTr | **extension = depression** of trochanter/femur → body support + downstroke | trochanter | large, high-force (E) | unmeasured | **S (body support)** |
| **Tergotr. MN** (TTMn) | tergotrochanteral muscle (TTM) | CTr | very fast **depression** | trochanter | single giant MN, escape-class | **0** | escape/jump only |
| **STTMm** | TTM, *satellite* MN (T2; serial partners T1/T3) | CTr | depression | trochanter | — | — | escape |
| **Tr flexor MN** | trochanter flexor, 7 MNs | CTr | **flexion = levation** of femur → lift leg | trochanter | graded pool | unmeasured | **W** |
| **Tr extensor MN** | trochanter extensor, 8 MNs | CTr | **extension = depression** | trochanter | graded pool | unmeasured | **S** |
| (accessory Tr flexor MN) | acc. trochanter flexor | CTr | flexion | trochanter | small | unmeasured | W |
| **Fe reductor MN** | femur reductor | TrF | femur **rotation/reduction**; Miller called it a depressor (m40/41) | femur | small pool | unmeasured | postural |
| **Ti extensor MN** | tibia extensor: **FETi** (fast) + **SETi** (slow), 2 MNs | FTi | **extension** | tibia | **FETi fast; SETi slow** | SETi tonic (E) | mixed; extension in late stance & swing |
| **Ti flexor MN** | tibia flexor, ~15 MNs: 1 fast, 2–5 intermediate, 8–9 slow | FTi | **flexion** | tibia | **fast ≈10 µN, int ≈1 µN, slow <0.1 µN** (M) | **slow ≈30 Hz; fast & int silent** (M) | **S** (loading) / W (withdrawal) |
| (accessory Ti flexor MN, 4 MNs) | acc. tibia flexor | FTi | flexion | tibia | small | unmeasured | S |
| **Ta depressor / levator MNs** (6) | tarsus depressor, retro-depressor, levator | TiTa | **depression = grip**/levation | tarsus | small | unmeasured | **S (grip)** |
| **LTM MNs** (incl. DIP-α+) | long tendon muscle | crosses TiTa | tarsal flexion / claw grip | tibia→tarsus | small | unmeasured | S |
| **MNfl## / MNml## / MNhl##** | *systematic names*, front/middle/hind leg | — | resolve muscle via the `target` annotation | — | — | — | — |

Force and rate numbers in the tibia-flexor row are the only direct measurements in the fly: a
single **fast** MN spike produces **~10 µN** and moves the tibia ~50 µm; an **intermediate** spike
~**1 µN** / 5 µm; the **slow** MN produces **<0.1 µN** per spike and ~1 µm movements, and fires
tonically at **~30 Hz at rest** while fast and intermediate are silent (Azevedo et al. 2020,
*eLife*). Input resistance grades **150 MΩ (fast) / 300 (int) / 700 (slow)**. For scale, the fly
weighs **~10 µN** (mass ~1 mg) — so *one* fast flexor spike is a body-weight impulse. Recruitment is
size-ordered, **slow → intermediate → fast** (Azevedo et al. 2020). Driver lines: fast R81A07,
intermediate R22A08, slow R35C09.

**Size proxy for unmeasured pools.** Lesser et al. 2024 give a connectome-readable surrogate: leg MN
input-synapse count scales with surface area at **~0.45 synapses/µm² (r = 0.94, p < 10⁻³³)**, mean
**3,641 input synapses from 188 premotor neurons** per leg MN. So synapse count ≈ size ≈ force class.
Use it (§6) for every muscle where fast/slow labels don't exist.

### 1b. Names in your list that are **not** leg MNs

| Name | Actually | Evidence |
|---|---|---|
| **b1, b2, b3** | wing **basalare** steering muscles, 1 MN each | Lesser et al. 2024 |
| **i1, i2** | wing first-axillary steering | Lesser et al. 2024 |
| **iii1, iii3, iii4** | wing third-axillary steering | Lesser et al. 2024 |
| **hg1–4** | wing fourth-axillary (hg) steering | Lesser et al. 2024 |
| **tpn / tp1, tp2** | **tergopleural** tension muscles — set thorax stiffness, indirect wing control | Cheong et al. 2024 |
| **ps1, ps2** | **pleurosternal** tension muscles — thorax stiffness/resonance, indirect wing control | Cheong et al. 2024 |
| **hi1, hi2, hb1, hb2, hiii1–3, hDVM** | **haltere** MNs (i = first-axillary, b = basalare, DVM = power) | Cheong et al. 2024 |
| **DLMn, DVMn** | wing indirect power muscles (5 DLM, 7 DVM MNs) | Lesser et al. 2024 |
| **TTMn / STTMm** | tergotrochanteral — *does* move the leg (mid-leg depression) but is the **escape jump** muscle, giant-fibre driven; excluding it from a walking readout is correct | Cheong et al. 2024; Bacon & Strausfeld 1986 |
| **MNad##** | **abdominal** MNs | Marin et al. 2024 |

---

## 2. Walking biomechanics of a turn

**Baseline gait.** Forward velocity spans ~−1.3 to 30.4 mm/s (2.5th–97.5th pct), bimodal at 0 and
~17.5 mm/s; step frequency ~5–12.5 Hz (DeAngelis, Zavatone-Veth & Clark 2019, *eLife* 8:e46409).
Speed is set almost entirely by **stance duration**: τ_stance ∝ v^−1.03 (R² = 0.59), while swing
duration is nearly constant (DeAngelis et al. 2019; Wosnitza et al. 2013, *J Exp Biol* 216:480;
Mendes et al. 2013, *eLife* 2:e00231). Flies use a modified tripod at all speeds; speed is further
modulated by tripod *geometry* (anteroposterior spread / mid-stance height), not by per-leg
stiffness (Chun, Biswas & Bhandawat 2021, *eLife* 10:e65878). **At 10 Hz stepping, your 100 ms bin
is exactly one step cycle** — coarse enough that a phase-averaged, not phase-resolved, model is the
right choice.

**What changes in a turn** (DeAngelis et al. 2019, quantitative; all "inside" = the side the fly
turns toward):

- **Inside mid- and hind-limbs**: stance duration **increases**, swing duration decreases, step
  length **decreases** in proportion to yaw rate. Stepping-frequency change reaches **~25 %** at
  maximum yaw.
- **Outside limbs**: step length **increases** with yaw rate.
- **Inside foreleg**: step *length* barely changes. Instead its stance **direction rotates up to
  ~45° outward**. The foreleg steers by vectoring, not by amplitude.
- Turns are phase-aligned to the tripod oscillator rather than free-running.

**Sign, established behaviourally.** Both directions have been demonstrated by unilateral DN
perturbation (Yang et al. 2024, *Cell* 187:6290–6308): DNa02 **shortens strides in the three
ipsilateral legs** → turn toward that side; DNg13 **lengthens strides in the three contralateral
legs** → turn away from those legs. So:

> **Turning is toward the side with less stance excursion.** Equivalently, yaw toward the *weaker*
> side, away from the *stronger* side. Differential-drive, tank-style.

**The foreleg caveat, which is exactly your sign problem.** Isakov et al. 2016 (*J Exp Biol*
219:1760) amputated a foreleg and got a strong turn **away** from the amputated side (right-foreleg
amputation → counter-clockwise bias; bias index μ from −0.006 to −0.410, recovering over days and
failing to recover in proprioceptive mutants). A pure differential-thrust model predicts the
*opposite*. The resolution is that in insects **front legs decelerate and hind legs accelerate the
body** in stance (Full, Blickhan & Ting 1991, *J Exp Biol* 158:369 `[cockroach]`; Dallmann, Dürr &
Schmitz 2016, *Proc R Soc B* 283:20151708 `[stick insect]`, showing joint torques often opposed to
fore–aft force). Removing a *braking* right foreleg unloads the right side forward → left yaw.
Isakov's model maps per-leg ground force to torque about the COM and shows that rebalancing
left–right force magnitudes restores straightness — i.e. the same differential-drive algebra, but
**with a leg-pair-dependent sign on T1**.

Practical consequence: **weight T2 and T3 positively and T1 near zero or slightly negative.** This
is the single largest source of sign error in a naive all-leg-MN count.

---

## 3. Bristle touch: what it recruits, and whether the fly turns away

Each tactile bristle is innervated by one cholinergic mechanosensory neuron; leg bristle axons
terminate in the **ventral-most layer of the leg neuropil**, the layer that contains local premotor
circuitry, and drive VNC second-order neurons monosynaptically at **~3 ms** latency (Tuthill &
Wilson 2016, *Cell* 164:1046). Bristle deflection alone elicits precisely aimed grooming, i.e. a
somatotopic leg-targeting motor program (Tuthill & Wilson 2016, *Cell*).

Medeiros et al. 2024 (*Curr Biol* 34:2812–2830) is the direct result for your case: brief
stimulation of **leg mechanosensory bristles** triggers a fast, **sustained, directional motor
program that persists for seconds and requires only the VNC** — decapitated flies do it. Femoral
chordotonal stimulation, by contrast, needs the brain. The response is "fast but uncoordinated" and
is sufficient to initiate forward movement; the authors frame it as the substrate of a
sensory-evoked **avoidance** behaviour.

At the behavioural level, touch-evoked avoidance is real and directional: in groups, appendage touch
between flies drives cascades of escape walking, and blocking bristle mechanosensation abolishes the
collective avoidance (Ramdya et al. 2015, *Nature* 519:233).

**But the sign on the fast local reflex is genuinely unresolved.** What is established: the local
VNC reflex is **ipsilateral** to the stimulated leg and recruits a broad, muscle-specific pattern
including flexors. What is *not* established in the fly is whether the first 100–300 ms of that
pattern produces a turn toward or away from the touched side. Mechanically, ipsilateral flexion +
levation (Tr flexor, Ti flexor, Fe reductor) **unloads** that side → differential drive predicts a
turn **toward** the touched side, followed by a brain-mediated away-turn on a longer timescale. Mark
this **(E), low confidence**; §6 gives the experiment.

Related reflex signs that are measured: 13Bα interneurons, driven by FeCO **claw** (extension-tuned)
afferents, produce a **resistance reflex** — slow **extension of the CTr joint and flexion of the
FTi joint** on activation in headless flies (Agrawal et al. 2020, *eLife* 9:e60299). 9Aα (hook/club
input) gives smaller FTi/TiTa extension; 10Bα (club) **halts** walking rather than moving a joint.

---

## 4. Descending neurons that turn the fly

| DN | Turn sign | Axon crosses midline? | Leg targets | Source |
|---|---|---|---|---|
| **DNa01** | **ipsiversive** | **no** | all three ipsilateral leg neuromeres; mostly premotor | Rayshubskiy et al. 2025, *eLife* 13:RP102230 |
| **DNa02** | **ipsiversive** | **no** | all three ipsilateral leg neuromeres; more direct MN contacts than DNa01; also wing/haltere/neck MNs. Unilateral activation **shortens strides in all three ipsilateral legs**, specifically the return stroke; strongly inhibits coxa-anterior (promotor) MNs | Rayshubskiy et al. 2025; Yang et al. 2024, *Cell* |
| **DNb05** | ipsiversive | n.r. | — | Yang et al. 2024 |
| **DNb06** | **contraversive** | n.r. | — | Yang et al. 2024 |
| **DNg13** | **ipsiversive** | **YES** | **contralateral** legs; excites coxa-posterior (remotor), FTi flexor and CTr flexor MNs during power stroke, and coxa-anterior + extensors during return stroke while inhibiting flexors → lengthens both strokes. Stride-length change **~100 µm ≈ 5 % of body length** | Yang et al. 2024, *Cell* |
| **MDN** (moonwalker) | backward walking, bilateral | — | targets LIN156 (hindleg power stroke during stance) and LIN128 (leg lift at end of stance → swing initiation) | Feng et al. 2020, *Nat Commun* 11:6166 |
| **DNp09 / P9** | forward walking **+ ipsilateral turning**; courtship pursuit | — | via VNC premotor | Bidaye et al. 2020, *Neuron* 108:469 |
| **BPN** | straight fast forward walking, no turn | — | — | Bidaye et al. 2020 |
| **Brake (BRK)** | halt by **co-contraction** — cholinergic VNC neurons, raise leg-joint resistance, override all walking commands | — | leg MNs | Sapkal et al. 2024, *Nature* 634:191 |
| **Foxglove / Bluebell** | GABAergic brain neurons; FG inhibits forward-walking DNs, BB inhibits **turning** DNs | — | upstream of DNs | Sapkal et al. 2024 |

**The DNg13 result is the template for DNge125.** A DN that crosses and excites contralateral leg
power-stroke MNs produces an **ipsiversive** turn — i.e. the fly turns *away* from the legs being
driven, toward the DN's own soma side. This is the cleanest published fact for your problem.

**DNge125 / DNge037 specifically: no published functional characterisation.** `DNge` = descending
neuron of the gnathal ganglion (Virtual Fly Brain FBbt lineage of the Namiki et al. 2018, *eLife*
7:e34272 scheme, extended by EM typing). The full DN census is now ~1,300 cells / ~480 types in each
sex (Schlegel et al. 2025, *Nature*, comparative DN/AN connectomics). No paper assigns a behaviour
to DNge125. Also note Braun et al. 2024 (*Nature* 630:686): "command-like" DNs recruit **networks**
of other DNs, so an isolated DNge125 stimulation in a LIF sim is not equivalent to the in-vivo
behavioural effect. Treat any DNge125 sign you derive as connectome-inferred, not measured.

---

## 5. Premotor structure: how a DN asymmetry becomes an MN asymmetry

Direct DN→MN connections are **infrequent**; most descending drive passes through VNC intrinsic
neurons organised into communities (ventral = walking, dorsal = flight power/steering) (Cheong et
al. 2024, *eLife*). Leg MNs receive on average 188 premotor partners and ~3,641 synapses (Lesser et
al. 2024), with ~622 local premotor interneurons per leg neuropil.

**Hemilineage transmitters** (Lacin et al. 2019, *eLife* 8:e43701 — all neurons in a hemilineage
share one transmitter):

- **GABAergic (inhibitory):** 0A, 1B, 3B, 5B, 6A, 6B, **9A**, 11B, 12B, **13A**, **13B**, 19A
- **Glutamatergic (inhibitory in fly motor circuits via GluClα):** 2A, 8A, 9B, 14A, 15B, 16B, **21A**, 24B
- **Cholinergic (excitatory):** 1A, **3A**, 4B, 7B, 8B, 10B, 11A, **12A**, 17A, 18B, **19B**, 20A/22A, 23B

**Module structure.** Lesser et al. 2024 clustered leg MNs by shared premotor input and recovered
**single-joint modules** — trochanter flexor (+ accessory flexor), trochanter extensor, coxa
promotor, coxa rotator/adductor, tibia extensor, tibia flexor A (with synergist tarsus MNs), several
accessory tibia flexor clusters. Critically, **within a leg module each premotor neuron's synaptic
weight onto each MN is proportional to that MN's total synaptic input**, i.e. to MN size. That is
the circuit basis of the size principle: a single premotor drive signal automatically recruits
slow→intermediate→fast in order. **Wing steering modules lack this proportionality** — do not reuse
the leg model for wings.

**Inhibitory sculpting.** 13A: ~67 ± 6 neurons/hemisegment; 13B: ~47 ± 1. 13A splits into
*generalists* (broad axonal arbors across multiple leg segments — premotor synergies) and
*specialists* (a few MNs within one segment). 13A directly inhibits tibia flexors, tibia extensors,
sternotrochanter extensors and tarsus depressors; 13B mostly acts by **disinhibition**, synapsing
onto 13A rather than MNs. Pulsed 13A activation drives rhythmic leg movements near **~7 Hz**;
sustained activation locks the leg in extension or flexion depending on cell identity (Syed, Ravbar
& Simpson 2026, *eLife* 14:RP106446). Hemilineages are ipsilateral units with largely
semi-autonomous patterned motor output (Harris et al. 2015, *eLife* 4:e04493).

**Consequence for your model.** A unilateral DN asymmetry is delivered to *hemilineage-sized*
ipsilateral premotor pools, which then distribute it across an entire module in size-proportional
fashion. So the correct readout unit is **(module × side × segment)**, not individual MNs, and the
within-module weighting should be the size-proportional one the connectome already encodes.

---

## 6. Recommended model

**Notation.** For MN type *i* on side *s* ∈ {L,R} in segment *g* ∈ {T1,T2,T3}, let `n_{i,s,g}` be
the spike count in the 100 ms bin and `b_{i,s,g}` the count in a quiet-standing baseline bin.
Let `Δ = n − b` (baseline subtraction is **not optional**: the slow tibia flexor alone contributes 3
spikes/bin at rest — Azevedo et al. 2020).

**Step 0 — clean the set.** Keep only `subclass ∈ {fl, ml, hl}`. **Drop `MNad` (abdominal), `MNwm`,
`MNhm`, `MNnm`, `MNxm`, `tpn`, `ps1/ps2`, `b1–b3`, `i1/i2`, `iii*`, `hg*`, `h*` (haltere), DLMn,
DVMn.** Drop `TTMn`/`STTMm` (escape jump, not walking). Expect ~390–450 cells, not 699.

**Step 1 — per-MN effective force.**
```
f_i = f0 * (S_i / S_ref)^alpha        # S_i = total input-synapse count (size proxy)
```
Calibrate with the one measured pool: tibia flexor fast/intermediate/slow force ratio is
**100 : 10 : 1** (10 / 1 / <0.1 µN) while the size span across that pool is only ~3–5× (input
resistance 150/300/700 MΩ). So **alpha ≈ 2.5–3.0 (E)**, chosen so the fast:slow output ratio ≈ 100
across the observed synapse-count span. Where explicit fast/intermediate/slow labels exist, use
**10 / 1 / 0.1 µN per spike** directly (Azevedo et al. 2020) and skip the proxy.

**Step 2 — saturating transfer.** Muscle tension summates sublinearly. Use
`a_i = f_i * (1 - exp(-Δ_i / k))` with `k ≈ 5` spikes/bin (E, ~50 Hz), so a tonically firing slow MN
saturates and a fast MN's first spikes dominate.

**Step 3 — muscle sign vector.** Per-side, per-segment propulsive drive:
```
P_{s,g} = Σ_i w_i * a_{i,s,g}
```
with `w_i` from §1a's `Stance?` column:

| Muscle group | `w` | Rationale |
|---|---|---|
| Pleural remotor/abductor, Sternal posterior rotator | **+1.0** | ThC retraction = the propulsive stroke |
| Sternotrochanter, Tr extensor | **+0.8** | CTr depression = body support + push |
| Ta depressor/levator, LTM | **+0.4** | grip; no grip, no thrust transmission |
| Ti flexor (all classes) | **+0.5** | loads the leg in stance; also the withdrawal muscle — see below |
| Ti extensor (FETi/SETi) | **+0.2** | late-stance extension, mostly swing |
| Sternal anterior rotator, coxa promotor | **−0.6** | protraction = swing; opposes net thrust in-bin |
| Tr flexor, acc. Tr flexor | **−0.6** | levation = leg off the ground |
| Fe reductor, adductor | **0.0** | postural/rotational, ~no fore-aft component |

**Step 4 — segment weights.**
```
forward = c_f * Σ_{s,g} λ_g * P_{s,g}
yaw_left = c_y * Σ_g λ_g * μ_g * (P_{R,g} - P_{L,g})
```
with `λ_T1 = 0.3, λ_T2 = 1.0, λ_T3 = 1.0`, and **`μ_T1 = −0.5, μ_T2 = +1.0, μ_T3 = +1.0`**. The
negative T1 yaw sign is the Isakov 2016 / front-leg-braking correction from §2 — mark it **(E),
medium confidence**, and expose it as a tunable.

**Convention:** `yaw_left > 0` = counter-clockwise viewed from above. This is the **negative** of
your current left-minus-right scalar; a naive `L − R` positive value means *turn right*.

**Calibration to real units.** Set `c_y` so that a saturating one-sided asymmetry gives ~±500 °/s
(the top of the fly's yaw range) and `c_f` so full bilateral drive gives ~20 mm/s (DeAngelis et al.
2019). A useful cross-check: DNg13's whole behavioural effect is a **~100 µm (5 % body-length)**
stride-length change (Yang et al. 2024) — real turns are made of small asymmetries, so the model
should be steep near zero and saturate early.

### What the two cases predict

**(a) Unilateral leg bristle.** The recruited pattern is ipsilateral and flexor/levator-heavy
(Tr flexor, Ti flexor, Fe reductor) plus a broad sustained VNC program (Medeiros et al. 2024). With
the §3 weights, ipsilateral `P` **drops** (levators are negative, and the leg unloads) →
`P_R − P_L` favours the untouched side → **turn toward the touched leg** in the first bins. That
contradicts the behavioural avoidance story (Ramdya et al. 2015) — deliberately so: the model is
saying that the *first 100 ms local reflex* and the *behavioural avoidance* are different circuits
on different timescales, and the fast one is a withdrawal, not a steer. **Confidence: low.** If your
sim's bristle pattern is instead extensor-dominated on the ipsilateral side, the model flips to
turn-away, which would match Ramdya. Inspect which muscle groups actually moved before trusting it.

**(b) DNge125 driving contralateral legs.** By the DNg13 template (Yang et al. 2024) — the only
crossed steering DN with a measured sign — excitation of contralateral leg power-stroke MNs
lengthens strides on that side → **ipsiversive turn**, i.e. the fly turns *toward the DNge125 soma
side*, away from the driven legs. Under the model this falls out automatically: `P` rises on the
driven side, `P_R − P_L` points away from it. **Confidence: medium** — DNg13's sign is measured,
DNge125's identity as a steering DN is not.

Note that (a) and (b) can legitimately have opposite signs in the raw left−right count while both
being correct under the muscle-signed model, because (a) is levator-dominated and (b) is
remotor/extensor-dominated. **That is the whole reason to do §3's weighting rather than counting.**

### Experiments that would fix the signs

1. **Per-muscle yaw calibration (fixes `w`).** Unilateral optogenetic activation of single MN pools
   in a ball-tethered fly with high-speed leg tracking: FETi/SETi, Tr extensor, Pleural
   remotor/abductor, Tr flexor, tarsus depressor. Measure yaw and per-leg stride length. This is the
   DNa02/DNg13 protocol (Yang et al. 2024; Rayshubskiy et al. 2025) applied to MNs. Nothing else
   gives `w` directly.
2. **Segment sign (fixes `μ_T1`).** Per-leg ground reaction forces in *Drosophila* during straight
   and curved walking. Measured in cockroach (Full et al. 1991) and stick insect (Dallmann et al.
   2016) but **not in the fly** — this is a real gap. Failing that, repeat Isakov et al. 2016
   amputations for T1 vs T2 vs T3 and read the bias sign per segment.
3. **Bristle sign (fixes case a).** Single-bristle piezo deflection on one front leg (Tuthill &
   Wilson 2016 method) in a ball-tethered fly, with simultaneous leg tracking, in intact **and
   decapitated** preparations. The decapitated condition isolates the VNC reflex Medeiros et al.
   2024 describe and reads its yaw sign directly.
4. **DNge125 (fixes case b).** Split-GAL4 → unilateral CsChrimson, ball, yaw. Also patch or image
   DNge125 during spontaneous turns to check whether the right−left rate difference is linearly
   related to rotational velocity, as it is for DNa01/DNa02 (Rayshubskiy et al. 2025). Expect a
   ~150 ms lead of DN activity over rotational velocity (Yang et al. 2024) — a useful sanity check
   on your 100 ms bin.
5. **MN rates during turning.** No one has published leg MN spike rates during free turning. Patch
   the tibia flexor slow/fast pair bilaterally during ball-walking turns and measure the actual
   `Δ`-vs-yaw slope. This would replace every **(E)** in §6 with a number.
