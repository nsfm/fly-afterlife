# E. Leg proprioceptors: what they are, what they encode, and how to compute them from a body model

Numbers for driving sensory sources from a joint-level physics body (joint angles, angular velocities,
ground contact forces). Every figure is attributed. Anything from a non-*Drosophila* insect is tagged
**[other insect]**. Anything with no direct measurement is tagged **[not measured — inferred]**.
Each subsection ends with **→ how to compute it**, the rule to implement.

**Status: FeCO, campaniform sensilla and connectome labels complete. Hair plates, tarsal afferents
and prior encoder models are summarised here and covered in full in the sibling files
`hair_plates_bristles_tarsal_sensilla.md` and `proprioceptor_encoder_models.md`.**

---

## E.0 The inventory, in one table

Per leg, front (T1) unless noted.

| Organ | Count (per leg) | Modality | Physical input | Source |
|---|---|---|---|---|
| Femoral chordotonal organ (FeCO) | **152** cell bodies (X-ray); **135** by earlier confocal count | joint angle, movement direction, vibration | femur–tibia angle θ, dθ/dt, and µm-scale vibration | Mamiya et al. 2023 *Neuron* 111, DOI 10.1016/j.neuron.2023.07.009; Mamiya et al. 2018 *Neuron* 100:636–650 |
| — claw subgroup | 20 labelled by `R73D10-Gal4` | **tonic femur–tibia ANGLE** | θ | Mamiya 2018 |
| — club subgroup | 30 labelled by `R64C04-Gal4` | bidirectional movement + **vibration** | \|dθ/dt\|, and 100–2000 Hz vibration | Mamiya 2018 |
| — hook subgroup | 3 labelled by `R21D12-Gal4` (flexion only) | **directional movement** | sign(dθ/dt) | Mamiya 2018 |
| — hook-extension | separate split-Gal4, count not given | directional movement, **extension** | sign(dθ/dt) | Chen et al. 2021 *Curr Biol* 31:5163–5175, DOI 10.1016/j.cub.2021.09.035 |

The current taxonomy is **five FeCO subtypes**: claw-flexion, claw-extension, hook-flexion,
hook-extension, club (Lee et al. 2025). The 2018 three-way split (claw / hook / club) is superseded.
| Campaniform sensilla | **42** (T1, T2); **41** (T3), in 11 named groups | cuticular strain → load | contact force and its derivative | Dinges et al. 2021 *J Comp Neurol* 529(4):905–925, DOI 10.1002/cne.24987 |
| Hair plates | **37** in **8** plates (front leg); 214 in 42 plates over six legs | joint position at the **limits** of range | θ near end-stop, thorax–coxa / coxa–trochanter / femur–tibia only | Kuan et al. 2020 *Nat Neurosci* 23:1637–1643, DOI 10.1038/s41593-020-0704-9; Pratt et al. 2026 *Nat Commun* 17:2664 |
| Tibial chordotonal organ (tCO) | count not established here | joint/vibration, distal tibia | — | see `hair_plates_bristles_tarsal_sensilla.md` |
| Tarsal / ground-contact afferents | Ta1G 2, Ta3G 2, Ta5G 4, Ta1S 1 (CS); plus bristles | touch, load | contact boolean + force | Dinges et al. 2021 |
| Tactile bristles | **~400+** per front leg (409 reconstructed in FANC) | touch | deflection | Elabbady et al. 2026; Kuan et al. 2020 |
| Stretch + strand receptors | 2 + 1 | — | — | Kuan et al. 2020 |
| **all leg mechanosensory neurons** | **~630–650** per front leg, of which **~225 proprioceptors** | | | Kuan 2020 / Pratt 2026 |

There is **no tarsal chordotonal organ** and **no subgenual organ** in *Drosophila*; the FeCO club
population is the substrate-vibration detector instead.

The two FeCO totals are not a contradiction to paper over: **135** is the 2018 confocal nuclear count
and **152** is the 2023 X-ray reconstruction of the front leg. Prefer **152** as the anatomical number
and cite 135 as the earlier estimate. Note also that the three Gal4 lines above *together label fewer
than half* the organ (Mamiya 2018 says so explicitly), so **20 + 30 + 3 = 53 is a driver-line count,
not a subclass census.** There is no published clean breakdown of all 152 into claw / hook-flexion /
hook-extension / club. **[not measured]**

The connectome gives a fourth, independent set of numbers, and they do **not** reconcile with the
anatomy — flag this before trusting either. MANC v1.2.x annotates **95 claw + 188 club + 65 hook =
348 FeCO neurons**, which across six legs is **~58 per leg** against an anatomical count of **152 per
leg**. Some of the shortfall is presumably sitting in the **152-neuron `SNppxx` "proprioceptive,
type unassigned" bucket**, and some in incomplete reconstruction. **Do not treat the MANC per-subtype
counts as a census of the organ.** Use 152/leg for the periphery and the MANC types for identifying
which reconstructed cells to wire.

Lee et al. 2025 (*Nat Commun* 16, DOI 10.1038/s41467-025-59302-3) explain the gap outright:
**leg sensory axons degrade during dissection and are the hardest neurons to reconstruct in every VNC
connectome dataset.** In **FANC** they reconstructed **80 FeCO axons from the front left leg**, which
they estimate is *"~50 % of the T1L axons of each subtype"*; **MANC v1.2.1 had only 22 T1L FeCO axons
reconstructed, many incomplete.** So the shortfall is a reconstruction artefact, not biology.

Two structural facts that simplify the model a lot:

- **Only 3–4 FeCO cells per leg project directly to the brain** (Mamiya 2018, citing Tsubouchi et al.
  2017). Everything else terminates in the VNC leg neuropil. The proprioceptive loop is a cord loop.
- **The FeCO has no efferent innervation** — Mamiya et al. 2023 looked for it and found none, and
  found no connection to surrounding muscles. There is **no gamma-motor analogue**: unlike a mammalian
  muscle spindle, FeCO gain cannot be set centrally at the periphery. (Presynaptic inhibition of the
  axon terminals *in the cord* is a separate and very real mechanism — see §E.1.4c.)

**All Drosophila FeCO physiology in the primary literature is calcium imaging, at 8.01 Hz frame rate
(Mamiya 2018, Mamiya 2023, Agrawal 2020). There are no published spike rates for FeCO afferents.**
Anyone writing a spikes/s number for claw, hook or club is importing it. **[not measured]**

---

## E.1 Femoral chordotonal organ

The FeCO sits in the proximal femur and monitors the femur–tibia (FT) joint only. It does not sense
the other leg joints. It is the fly's only well-characterised leg proprioceptor and it is the one
worth implementing first.

### E.1.1 The mechanical front end — you can model this as a linkage

Mamiya et al. 2023 reconstructed the periphery by X-ray holographic nano-tomography and this is the
part that matters for a physics sim, because it says **the three subtypes are not three different
transducers, they are one transducer fed by a mechanical filter bank.**

Each pair of FeCO neurons is wrapped in a scolopale cell that attaches to a sensory tendon via an
actin-rich cap cell. There are **two** sensory tendons. Claw and hook attach to the **medial tendon**;
club attaches to the **lateral tendon**. The claw/hook tendons merge **100 µm** distal to the organ.
Both tendons converge on the **arculum**, a tooth-shaped sclerite in the distal femur coupled to the
tibia-extensor tendon and the tibia joint.

The arculum works as a **slider–crank**: it converts the linear pull of the joint tendon into rotation,
and because the medial and lateral tendons attach at different roots, that rotation moves them along
**orthogonal** axes. Their finite-element model (COMSOL, four tendons as springs with
`k = E_resilin · A / L₀`) gives the geometry:

| Tendon | L₀ (µm) | Cross-section A (µm²) |
|---|---|---|
| Joint tendon | 72 | 295.3 |
| Femoral (tibia-extensor) tendon | 225 | 295.3 |
| Medial tendon (→ claw, hook) | 268 | 50.9 |
| Lateral tendon (→ club) | 283 | 57.2 |

Driven by a periodic **10 µN** force along the femur long axis, which they state "approximates force
levels known to be produced by *Drosophila* muscles". The model is linear-Hookean, so the response
scales linearly with applied force — useful, because it means you can rescale to whatever force your
body model produces without re-solving.

The two regimes come out of this cleanly, and they are the design of the encoder:

- **Macroscopic, low frequency** — arculum translates **1–50 µm** during ordinary tibia flexion and
  extension. Both tendons move together. **Claw and club are both excited.** This is walking.
- **Microscopic, high frequency** — **<1 µm** at 100–1600 Hz. The arculum *rocks*. The lateral tendon
  is pushed and pulled along its sensitive axis (club fires); the medial tendon is moved
  perpendicular to its sensitive axis, **"reducing on-axis movements by as much as 30×"**, so claw
  does not fire.

That 30× geometric attenuation, plus the fact that club cell bodies are anchored in stiffer tissue
(they move **<2 µm** across the whole joint range, versus claw cells which slide distally with
flexion), is the stated explanation for the measured sensitivity gap: **the mechanosensory threshold
of claw neurons is more than 10× higher than that of club neurons** (Mamiya 2023 citing Mamiya 2018).

Cutting the medial tendon makes claw cells and cap cells retract proximally — so **claw dendrites are
held under resting tension**, and without that pre-tension the angular map is destroyed.

**→ how to compute it.** Two channels from one joint. Low-pass the FT joint angle θ(t) for the
claw/hook path and band-pass the same signal (or, better, the residual after removing the smooth
component) for the club path, with a **~30× lower gain on the claw path for high-frequency content**.
If your body model has no sub-micron vibration content at all — most rigid-body sims don't — then the
club vibration channel has no physical input and you should either drive it from substrate/contact
transients or leave it silent and say so, rather than faking it from dθ/dt.

### E.1.2 Claw — tonic joint angle

Position-tuned, non-adapting, cholinergic. Each claw axon splits into three branches (X, Y, Z) and
each branch into a flexion- and an extension-encoding sub-branch — but a single claw neuron innervates
**all three** branches and all three encode the same thing (Mamiya 2018, n = 3 traced cells). The
tri-partite arbor is not a coordinate system; treat one claw neuron as one scalar output.

**Population tuning (Mamiya 2018, calcium, `R73D10-Gal4`, n = 10 flies):**

- extension-tuned pixels active over **90°–180°**
- flexion-tuned pixels active over **90°–18°** (18° was the mechanical limit of their rig, not the
  fly's)
- **neither group active near 90°**, and activity rises "as a relatively linear function of the
  femur–tibia joint angle"

**Single cells are narrowly tuned** — range fractionation. One cell peaked at **70°**, another at the
most flexed position **20°** (n = 5 cells / 5 flies). No cell tuned near 90° was found, though the
sample is tiny and they say so.

**Hysteresis is real and is the main nuisance for a decoder.** Steady-state activity at a given angle
is larger when the joint arrived there moving in the cell's preferred direction. The flexion branch
shows it over 0°–90°, the extension branch over 90°–180°. Mamiya 2018 note this "would introduce
ambiguity for downstream circuits that rely on a stable readout of tibia angle", and suggest combining
claw with the direction-selective hook to disambiguate. Peak magnitude is roughly ±0.2–0.4 in
normalised units, read off their Figure 5E — **treat as approximate, it is not a quoted number.**
Club and hook show **no** directional hysteresis.

**The goniotopic map (Mamiya 2023) is the encoding rule, and it is simple.** Imaging cell bodies in
the femur during slow flexion at **6 °/s**, they found a **linear relationship between a claw cell's
position along the proximal–distal axis of the femur and the tibia angle at which it reaches 50 % of
its maximum activity.** Recruitment order:

- flexion-selective claw: **proximal cells first, at more obtuse angles; distal cells later, at more
  acute angles**
- extension-selective claw: **distal cells first at more acute angles; proximal cells at more obtuse**

The mechanism from their FE model: dendritic strain rises as the tibia flexes, and strain is **always
higher in more proximal cells, with the gap widening with flexion.** A *uniform* activation threshold
across all cells, applied to that graded strain, produces the angular map.

**→ how to compute it.** You do not need 20 independent tuning curves. Give claw cell *i* a position
parameter `p_i ∈ [0,1]` (proximal→distal) and use one shared threshold:

```
strain_i(θ)  = g(θ) · (a + b·(1 - p_i))        # g increasing as θ flexes; proximal ⇒ larger
r_i(θ)       = f( strain_i(θ) - T )             # f = rectifier/sigmoid, T shared across cells
```

Half-activation angle is then **linear in p_i**, which is exactly what they measured. Spread the
flexion-selective cells' half-activation angles over roughly **20°–90°** and the extension-selective
cells' over roughly **90°–180°**, with a **dead zone around 90°**, and intermingle the two
populations spatially (Mamiya 2023 found them interleaved in the array). Add hysteresis as a
direction-dependent offset on T, not as a separate state variable.

One consequence worth carrying: with the tibia resting near **90°** in a standing fly, and walking
excursions quoted as **40°–120°** (Mamiya 2018, cited as *unpublished data*), the paper's own
prediction is that **claw neurons are largely silent in a stationary fly** and rhythmically active in
walking. If your sim has claw cells firing hard at rest, the tuning is wrong.

### E.1.3 Hook — directional movement

Phasic, direction-selective, rapidly decaying, **never tonic during hold** (Mamiya 2018).

- Direction selectivity index **DSI = 0.811 ± 0.028** (n = 37 regions / 23 flies) with the specific
  driver `R21D12-Gal4`, which labels flexion-selective hook only. Compare the population-imaging
  flexion cluster at DSI 0.494 ± 0.039 — the population figure is contaminated by non-selective axons.
- **An extension-selective hook population exists** (clearly seen in `iav-Gal4` population imaging,
  DSI 0.493 ± 0.036, n = 29 clusters / 22 flies) but **no Gal4 line was found for it in 2018**, so it
  is anatomically and functionally under-described. Mamiya 2023 places hook-extension cells in
  group 2, distal to the claw array, attached to a branch of the medial tendon, and they *move*
  distally during flexion — whereas hook-flexion cells sit in group 3 and do not move.
- **Velocity: essentially flat.** The slope of the calcium signal was "similar across the entire speed
  range we tested" (**100–800 °/s**). Hook signals *direction*, not speed, over the walking range.
- Slightly weaker at fully extended positions.
- **Does not respond to vibration** at all (100–2000 Hz, 0.9 and 0.054 µm).

**→ how to compute it.** A half-wave rectified, fast-adapting derivative:

```
r_hook_flex(t) = adapt( relu( -dθ/dt ) )      # flexion-selective
r_hook_ext(t)  = adapt( relu( +dθ/dt ) )      # extension-selective
```

with **saturating (near velocity-independent) gain above ~100 °/s** and adaptation fast enough that
nothing survives into a static hold. Do **not** make hook rate proportional to speed — that is the
one thing the data say it isn't. Adaptation time constant is **[not measured]**; the 8 Hz imaging
rate cannot resolve it.

### E.1.4 Club — bidirectional movement and vibration

Phasic to movement in both directions, plus the fly's tibial vibration detector.

**Movement.** DSI **0.117 ± 0.022** (n = 25 regions / 15 flies) — genuinely bidirectional.
Responses are "slightly larger around 90° and smaller at full extension (180°)".
**Velocity tuning: the calcium-signal slope peaks around 400 °/s** and decays slightly above that
(tested 100–800 °/s). This is the one FeCO subtype with a real velocity optimum.

**Vibration (Mamiya 2018).** Sinusoidal tibia vibration, peak-to-peak **0.9 µm or 0.054 µm**,
**100–2000 Hz**. Club responded significantly at every frequency tested.

- **0.9 µm amplitude → population peak at 400 Hz**
- **0.054 µm amplitude → population peak at 800 Hz**
- claw and hook: no response

The 2000 Hz ceiling is an **apparatus limit** — their piezo output fell off sharply above ~2 kHz and
they say so. Do not quote 2 kHz as the biological upper bound.

Mamiya 2023, imaging dendrites in the femur (n = 17 flies, 0.9 µm, 100–1600 Hz), found response
amplitude rising with frequency and **plateauing around 800 Hz** — a slightly different shape from
the 2018 axonal peak at 400 Hz, presumably compartment and indicator differences.

**Tonotopy.** Club is frequency-mapped twice over. In the **axon terminals** (VNC) the response
centre-of-mass moves anterolateral → posteromedial as frequency rises (Mamiya 2018), and in the
**dendrites** (femur) it moves distal/lateral → proximal/medial over 200–1600 Hz (Mamiya 2023).
**Single club neurons are narrowly tuned**: one cell peaked at **200 Hz**, another at **1600 Hz**
(n = 12 cells / 7 flies). Where two club axons were labelled in the same leg, the more posterior was
tuned lower.

The **mechanism of the tonotopy is unresolved**. Mamiya 2023 explicitly tested and **rejected**
tendon-length resonance (neither longitudinal nor transverse modes differ enough between cells).
Remaining candidates they list: per-dendrite stiffness, cap-cell mass, or electrical resonance
(they note `slo` is highly expressed). So there is **no published transfer function** from tendon
geometry to a club cell's best frequency. **[not measured]**

**Club is not purely proprioceptive.** Mamiya 2018 propose club as a substrate-vibration detector,
noting male courtship abdominal vibrations fall in the club band (quoted as 200–2000 Hz, attributed
to "C. Fabre, personal communication" — **unpublished, do not treat as a hard number**). Agrawal 2020
then showed club's downstream partner 10Bα drives **pausing**, an exteroceptive response. Wiring club
straight into a body-state estimator would be a mistake.

**→ how to compute it.**

```
r_club_move(t) = adapt( bandpass_gain(|dθ/dt|) )    # unsigned, peak gain near 400 °/s
r_club_vib(t)  = Σ_k w_k · |BP_k( x_tibia(t) )|     # filter bank, BF_k log-spaced 100–1600 Hz
```

The movement channel is the one your rigid-body sim can actually drive. For the vibration channel,
lay a **log-spaced filter bank of ~30 channels with best frequencies from 100 to 1600 Hz**, ordered
along a spatial axis so the tonotopy is preserved for anything downstream that cares, and give the
whole population a **response magnitude that saturates around 800 Hz**. Feed it from substrate
contact transients, not from joint velocity.

### E.1.4b The subtype list grew: hook-extension (2021)

Chen et al. 2021 (*Curr Biol* 31:5163–5175, DOI 10.1016/j.cub.2021.09.035) built intersectional
split-Gal4 lines for each subtype and found *"a new FeCO subtype that responds to tibia extension in a
directionally tuned manner … we refer to this new FeCO subtype as 'hook (extension)' and flexion-tuned
hook neurons as 'hook (flexion)'."* This is the population Mamiya 2018 had seen in `iav-Gal4`
population imaging (DSI 0.493 ± 0.036) but could not target.

**So the 2021 list is club / claw / hook-flexion / hook-extension** — and Lee et al. 2025 split claw
into flexion and extension too, giving the current **five** (see §E.1.4d). Mamiya 2023
then separates them anatomically: hook-**extension** sits in FeCO group 2, distal to the claw array,
on a branch of the medial tendon, and its cell bodies *move* distally during flexion; hook-**flexion**
sits in group 3 and does not move. Different mechanics, so expect different dynamics — implement them
as two populations, not as a sign flip on one.

Chen et al. also quantified the downstream fan-out of each subtype, which is a useful weighting when
deciding how much each channel should matter:

| Subtype | postsynaptic cells (*trans*-Tango) | postsynaptic cells (functional connectivity) |
|---|---|---|
| claw | **566** | **443** |
| club | **216** | **147** |
| hook (extension) | **197** | **89** |
| hook (flexion) | **74** | **21** |
| total | **1,053** | **700** |

Both are stated by the authors to be **underestimates**. The headline: **claw's fan-out is roughly
2.6× club's**, despite comparable peripheral numbers. Joint angle is the channel the cord reads out
most heavily.

Downstream classes: *"8 classes of VNC neurons from 6 lineages … 8Aa; 8Ba; 9Ba; 10Ba; 13Ba; 13Bb;
19Aa; and 19Ab"*. Only **9Ba and 10Ba** respond to club; the other six respond to claw and hook.

One result from that paper changes how adaptation should be modelled: **picrotoxin (10 µM) reduced
adaptation in 10Ba and 13Bb**, and 13Ba did not adapt at all over 30 s of claw stimulation. So the
adaptation seen in second-order cells is **circuit-level GABAergic/glutamatergic inhibition, not an
intrinsic property of the afferents.** If you put strong adaptation into the sensory encoder you will
be double-counting.

### E.1.4c The gating problem: hook output is not a function of kinematics

This is the single most important caveat for the whole exercise, so it goes before the encoder
equations rather than after.

Dallmann CJ, Luo Y, Agrawal S, Mamiya A, Chou GM, Cook A, Sustar A, Brunton BW, Tuthill JC (2025),
"Selective presynaptic inhibition of leg proprioception in behaving *Drosophila*", *Nature*
**647:445–453**, DOI 10.1038/s41586-025-09554-2. Calcium imaging of FeCO **axon terminals** in flies
walking and grooming on a ball, plus FANC connectomics.

**The movement-encoding hook axons are suppressed during self-generated leg movements — walking and
grooming — but not during passive movements. Claw and club are not suppressed.**

So the same joint trajectory produces **different afferent output** depending on whether the fly
caused it. Every FeCO tuning curve in §E.1 was measured with a **passive, externally imposed** tibia
movement. Applying those curves unmodified to a walking sim will overestimate hook output in exactly
the regime that matters.

The mechanism is axo-axonic GABAergic presynaptic inhibition, and it is structurally selective:

- Input synapses sit on **all** FeCO axon branches, intermingled with outputs — a distributed gate,
  not a single switch.
- **All claw and hook neurons strongly express `Rdl`** (GABA_A). Claw and hook axons get input
  **100 % / 95 %** from VNC interneurons, essentially none direct from descending neurons.
- **"presynaptic neurons target either claw axons or hook axons, but not both"** — that is why the
  suppression can be subtype-selective.
- **83 %** of GABAergic input to hook axons comes from local **9A** interneurons, and **one "chief"
  9A neuron supplies 57 % of it**, sending **63 %** of its own output to hook axons.
- Claw axons instead get their GABAergic input from **19A** neurons. Purpose unknown; the authors
  speculate lateral inhibition, habituation protection, or **hysteresis reduction** — worth noting
  given how much trouble claw hysteresis causes a decoder.
- The 9A gate is **feedforward, not feedback**: 9A neurons receive little sensory input and are driven
  by descending neurons. Walking and grooming descending neurons supply **31 %** of chief 9A's input
  (**18 %** walking, **13 %** grooming, the latter **DNg12**); the GABAergic **DNg74 ("web")**
  disinhibits VNC targets during self-generated movement.

One more result from the same paper, which supports the club wiring recommended in §E.1.4:
**club axon baseline activity was elevated when the legs contacted the treadmill**, consistent with
club acting as a substrate-vibration exteroceptor. Drive club from ground contact, not from dθ/dt.

**→ how to compute it.** Gate the hook channel on a locomotor/grooming state variable your controller
already has:

```
r_hook(t) = adapt( relu( ∓dθ/dt ) ) · (1 - g·active(t))     # active = self-generated movement flag
```

Leave claw and club ungated. **The value of g is not published** — the suppression magnitude and its
latency relative to movement onset are figure quantities I did not extract. **[not measured here]**
Take `g` near 1 during vigorous walking as a first cut and treat it as a fitted parameter.

### E.1.4d The reflex sign rule, and the proprioceptive/exteroceptive split

Lee S-YJ, Dallmann CJ, et al., Tuthill JC (2025), "Divergent neural circuits for proprioceptive and
exteroceptive sensing of the *Drosophila* leg", *Nat Commun* 16, DOI 10.1038/s41467-025-59302-3,
PMC12048489. FANC connectomics of all 80 reconstructed T1L FeCO axons and their postsynaptic partners
(≥4-synapse threshold).

**The taxonomy is now five subtypes: claw-flexion, claw-extension, hook-flexion, hook-extension,
club.** Reconstructed counts in T1L were **8, 13, 9, 13, 37** (80 total, ~50 % of the real axons).

**Where each subtype's output goes:**

| Subtype | Predominant postsynaptic targets |
|---|---|
| claw, hook-extension | **local VNC interneurons and leg motor neurons** |
| hook-flexion | roughly equal local and intersegmental |
| **club** | **>50 % onto intersegmental neurons**, high output onto **ascending** neurons, and **no direct synapses onto leg motor neurons at all** |

Club connects to motor output only indirectly and weakly — to the long tendon muscle (substrate grip)
and to the PSI (wing power muscles at takeoff). **This is the strongest evidence yet that club is not
a proprioceptor in the motor-control sense.** Confirms the recommendation in §E.1.4: drive club from
substrate contact, and do not route it into leg posture control.

Also: flexion- and extension-tuned partners of the same subtype have **almost zero** cosine similarity
in their downstream connectivity — the opposing populations are read out by disjoint circuits, so
implement them as genuinely separate channels rather than one signed variable.

**The reflex sign rule, quoted directly** — this is the most directly implementable result in the
whole literature:

> "Claw and hook **flexion** axons provide **excitatory feedback to motor neurons that extend the
> tibia** and **inhibitory feedback to motor neurons that flex the tibia**. Claw and hook
> **extension** axons provide **excitatory feedback to motor neurons that flex the tibia** and
> **strong inhibitory feedback to motor neurons that extend the tibia**. Claw extension axons also
> provide excitatory feedback to other motor modules, such as the motor neurons that move the coxa
> forward (coxa promotor) and extend the trochanter."

A **negative-feedback resistance reflex**: sensed flexion commands extension and vice versa. It is
consistent with Agrawal et al. 2020's optogenetics — activating 13Bα, which is driven by
extension-claw, produced femur–tibia **flexion**. Premotor neurons downstream of the FeCO are
**largely dedicated**, each relaying one FeCO subtype to one motor module rather than mixing.

Two structural notes for the encoder: FeCO axons have **pre- and postsynaptic sites intermingled with
no distinct zones**, and there is **no functional specialisation across the X/Y/Z sub-branches** of
claw or hook — most postsynaptic neurons receive input from multiple branches. One afferent, one
scalar output. Caveat from the authors: **FANC resolution could not resolve gap junctions**, and
mixed electrical/chemical synapses are known to exist here, so electrical coupling is invisible in
this dataset.

### E.1.5 Adaptation and repeatability

Across three repetitions of the same swing at 5 s intervals, response ratios (2nd/1st and 3rd/2nd)
sat between **0.89 and 1.18** depending on subclass (Mamiya 2018, full table in their methods).
So **little run-down over seconds; roughly ±10 %.** Within-movement adaptation time constants for
phasic subtypes are **[not measured]** — 8 Hz imaging cannot resolve them.

### E.1.6 Stimulus parameters used in the source experiments

Useful when matching a sim's stimulus protocol to the data you are fitting.

- Joint range probed: **18° (flexed) to 180° (extended)**; 18° was a rig limit (pin fouled the abdomen).
- Swing: **360 °/s** standard; velocity series at **180, 720, 1440 °/s**.
- Ramp-and-hold: **18° steps at 240 °/s**, **3 s holds**, motor acceleration **72,000 °/s²**.
- Goniotopy: slow flexion at **6 °/s**.
- Imaging **8.01 Hz**; leg tracking 180–200 Hz.

### E.1.7 Natural kinematics — handle with care

Mamiya 2018 state: tibia rests **~90°** when standing; during straight walking it **flexes to 40° and
extends to 120°** — cited as **(unpublished data)**. Maximum FT excursion in tethered walking flies
**~80°**, also their unpublished observation. Foreleg swing duration **~25–45 ms**, stance
**~30–140 ms** (Mendes et al. 2013; Wosnitza et al. 2013, second-hand via Mamiya 2018).

From those they *derive* max average joint speeds of **2400–3200 °/s in swing** and
**~2000–2670 °/s in stance**. This is an excursion-over-duration calculation in their methods, **not a
measurement**, and it sits ~3× above the measured cockroach mean joint angular velocity of
**0–800 °/s** **[other insect: Watson & Ritzmann 1998]**. Prefer measured *Drosophila* kinematics when
driving the body model; do not adopt 3000 °/s as a target.

---

## E.2 Second-order targets in the VNC — what the sensory layer has to feed

From Agrawal et al. 2020, *eLife* 9:e60299, DOI 10.7554/eLife.60299. Whole-cell recordings, T1
segment. Useful as an acceptance test: if your FeCO encoder is right, these three should fall out.

| Cell type | Hemilineage / transmitter | Input | Encodes | Spikes | Reflex on optogenetic activation |
|---|---|---|---|---|---|
| **13Bα** | 13B, GABAergic | extension-tuned **claw** | tonic FT **angle**; rises only past **~90° extension**; hysteretic like claw | **none detectable** | coxa–femur extension **+ femur–tibia flexion** |
| **9Aα** | 9A, GABAergic | flexion **hook** + club | **flexion direction and speed**; max at 1600–2000 Hz vibration | yes | small **extension** of femur–tibia and tibia–tarsus |
| **10Bα** | 10B, cholinergic | **club** | bidirectional movement + vibration, **gated by joint position** | no (occasional spike-like events) | **walking flies slow or stop after ~200 ms** |
| **9Aα2** | 9A, distinct type | claw-like | tonic **flexed** positions | yes, spikes **>2 mV** | not tested |

Three things to carry into the model:

1. **13Bα is the posture loop.** It senses extension and commands flexion — negative feedback on the
   FT joint. Its responses are "remarkably tonic (non-adapting) at steady state". Pharmacology is odd:
   TTX abolishes it, but MLA and atropine only subtly affect it, suggesting **gap junctions** onto
   claw axons alongside chemical transmission. Picrotoxin has no effect, and current-injection
   experiments show the flexion-evoked hyperpolarisation is a **withdrawal of excitation**, not
   inhibition. So 13Bα ≈ a sign-inverted, low-pass copy of extension-claw drive.
2. **9Aα is heterogeneous on purpose.** Two 9Aα cells in the *same fly* respond differently. The only
   consistent properties are direction and speed tuning (peak firing significantly higher at
   **720 °/s** than **240 °/s**, p < 0.005). Absolute spikes/s are figure-only — **could not verify a
   number.**
3. **10Bα multiplexes position into a vibration channel.** The same 20° oscillation produces a
   different response depending on whether the tibia started flexed or extended (n = 9, p < 0.005;
   oscillation velocities 40–320 °/s). So club→10Bα is not a clean vibration line.

**The latency budget.** Agrawal et al. frame the problem as: "in nimble-footed animals like flies,
central circuits may have **less than 30 ms** to process proprioceptive information in between
successive steps." That is the number to design the sim's sensorimotor loop against. Note that
neither Agrawal 2020 nor Mamiya 2018/2023 measures a synaptic latency from FeCO to a central neuron
in ms. **[not measured]**

Neuron counts per central cell type are **unknown and the authors say so**: "we still lack
quantitative data on the numbers of cells or cell types within each hemilineage."

---

## E.3 Campaniform sensilla — load and cuticular strain

CS are cuticular strain gauges: an ellipse of thin cuticle in the exoskeleton that is compressed when
the segment is loaded, squeezing the dendrite of a single bipolar sensory neuron. They are the fly's
load sensors, and they are the ones your ground-contact forces should drive.

### E.3.1 Complete inventory (Dinges et al. 2021)

Dinges GF, Chockley AS, Bockemühl T, Ito K, Blanke A, Büschges A (2021), *J Comp Neurol*
**529(4):905–925**, DOI 10.1002/cne.24987. SEM of **female** flies, whole body. Verified by reading
the OA PDF on the Cologne repository (Wiley 403s; use
`kups.ub.uni-koeln.de/25156/1/Blanke%20in%20Dinges%202020.pdf`).

**Whole body: "over 680 sensilla arranged in 26 fields, 54 groups, and 34 single CS."**

Naming scheme, which is the one to adopt: `<segment><F|G|S><position><leg>`, where `F` = field,
`G` = group, `S` = single, position ∈ {p, a, d, v}, and the leg suffix is **F = front (T1),
M = middle (T2), R = rear (T3)**. (The letter F is overloaded — "field" in slot 2, "front leg" as the
suffix.) So `TiGvF` = ventral tibial group, front leg.

| Group | Location | T1 front | T2 middle | T3 rear |
|---|---|---|---|---|
| **TrFp** | dorsal trochanter, posterior subfield | **8** (7 in 1/8) | **8** (8/9) | **8** (5/9) or **7** (4/9) |
| **TrFa** | dorsal trochanter, anterior subfield | **5** (always) | **5** (9/10) | **5** (always) |
| **FeF** | proximal **ventral femur**, 3 columns | **10** (3/5) or **11** (2/5) | **11** (8/9) | **11** (4/5) |
| **TrG** | posterior trochanter | **3** | **3** | **3** |
| **TiGd** | dorsal tibia, posterior end | **2** | **2** | **2** |
| **TiGv** | ventral tibia, posterior end | **3** | **3** (2 in 1/12) | **3** |
| **Ta1G** | dorsal distal tarsomere 1 | **2** | **2** | **2** |
| **Ta3G** | dorsal distal tarsomere 3 | **2** | **2** | **2** |
| **Ta5G** | ventral distal tarsomere 5 | **4** (3 in 1/5) | **4** | **4** |
| **FeS** | single, dorsal femur | **1** | **1** | **1** |
| **Ta1S** | single, ventral tarsomere 1 | **1** | **1** | **1** |
| **Cx** coxa | — | **0** | **0** | **0** |

**Totals: 42 CS on the front leg, 42 on the middle, 41 on the rear** — measured on the three legs
(one per pair, out of 14 flies) that had no SEM occlusions. Call it **~42 per leg, ~250 across six
legs.**

Two facts worth building around:

- **The coxa has no campaniform sensilla.** Direct quote: *"In spite of its large volume no CS was
  observed on the Coxa (Cx)."* So coxal load is not sensed by CS; if your model needs coxal load
  sensing, it has to come from the trochanteral fields just distal to it, or from hair plates.
- **Variability is real but bounded.** *"numerical variability was higher when there were larger
  numbers of sensilla, and little numerical variability if any was seen for groups with fewer than
  four sensilla."* The two singles, the three 2-CS groups and TrG never varied. TrFp had 7 in **6 of
  28** samples; FeF had 10 or 12 in **5 of 20**. Only four locations varied at all, always by ±1.
  So a fixed wiring diagram of 42 per leg is a defensible simplification.

Geometry that matters for directional tuning: CS caps are **ellipses**, and an elongated cap is
compressed selectively by strain perpendicular to its long axis. Dinges et al. report eccentricity
qualitatively — all trochanteral-field CS are elongated (eccentricity "closer to 1"); in FeF,
**3 of the ~11 are markedly less eccentric than the other 8**; in TiGv the middle CS is consistently
the smallest and least eccentric of the three. Cap diameters are not tabulated numerically
(SEM scale bars are 15 µm, so caps are of order a few µm). **[not measured]**

This paper contains **no physiology whatsoever** — no rates, no thresholds, no adaptation. It is
morphology only.

### E.3.1b Independent cross-check against Kuan et al. 2020

Kuan AT et al. 2020 (*Nat Neurosci* 23:1637–1643), Supplementary Data Table 3, counts front-leg CS
from an X-ray holographic nano-tomography leg volume — a completely different method from Dinges'
SEM, and a useful validation. Its naming embeds the count in the name (`FeCS11` = the 11-CS femoral
field):

| Kuan name | count | Dinges equivalent |
|---|---|---|
| `TrCS3` | 3 | TrGF |
| `TrCS5` | 5 | TrFaF |
| `TrCS8` | 8 | TrFpF |
| `FeCS1` | 1 | FeSF |
| `FeCS11` | 11 | FeFF |
| `TiCSd2` | 2 | TiGdF |
| `TiCSv1` + `TiCSv2` | 1 + 2 = 3 | TiGvF (Dinges' 3, split into two subgroups) |
| **subtotal** | **33** | — |
| plus tarsomere 1 | **3** (2 dorsal-distal + 1 proximal-ventral) | Ta1GF (2) + Ta1SF (1) |

**The two methods agree exactly on every group.** Kuan reports no CS in the distal tibia, ta2 or
proximal ta3, and its volume does not extend to Ta3G/Ta5G — which accounts for the whole difference
between Kuan's 36 and Dinges' 42 (the missing 6 are Ta3G's 2 and Ta5G's 4). Two independent
techniques, same answer. **Treat the ~42/leg figure as solid.**

Note also the naming clash: Kuan uses `TrCS`/`FeCS`/`TiCS` and embeds the count; Dinges uses
`TrG`/`TrF`/`FeF`/`TiG` plus a leg suffix. MANC uses a third scheme again (`SNpp53`, `subclass =
"campaniform sensilla"`, `synonyms = "TrCS"`). Pick one and keep a mapping table.

**A number NOT to use.** Tuthill & Wilson 2016 (*Curr Biol* 26:R1022–R1038) states there are
**"~1200 campaniform sensilla"** over the legs, wings, halteres and antennae of "the fly". Its
citation for that is **Gnatzy, Grünert & Bender 1987, *Zoomorphology* 106:312–319, which is
*Calliphora*, not *Drosophila*** **[other insect: blow fly]**. Drosophila's verified whole-body
figure is Dinges' **"over 680 sensilla in 26 fields, 54 groups and 34 single CS."**

### E.3.2 What CS encode

Nothing in *Drosophila* yet, at the level of a measured transfer function. **[not measured]**

The one relevant *Drosophila* modelling result is from the parametric FE model of the femoral field
(Heepe/Blanke et al., bioRxiv 2023.07.24.550300; published *J R Soc Interface* 22(226):20240559,
2025), which used Dinges' numbering of the **11 femoral CS in three columns — anterior 1–3, middle
4–7, posterior 8–11, each numbered distal→proximal.** Its conclusion is a caution for us:
at the proximal femoral field, **the leg bending produced by ordinary walking ground-reaction forces
is probably too small to be the stimulus**, and **muscle tensile forces are likely the more relevant
input**. They also conclude a single CS "has most likely no sensing capacity for different force
directions at the femoral–tibia joint". So a naive "femoral CS rate ∝ ground reaction force" mapping
is the wrong physics for the *proximal* fields, though it may be right for the distal tibial and
tarsal groups.

**There is now one Drosophila CS physiology paper, as a preprint.** Custodio RD, Gorostiza EA,
Pierzchlinska A, Haustein M, Godesberg V, Duebbert M, Bockemühl T, Büschges A (2026), "Role of leg
campaniform sensilla sensory feedback in *Drosophila melanogaster* adaptive walking", bioRxiv,
DOI 10.64898/2026.07.22.740025, posted 2026-07-27. **Abstract verified via the bioRxiv API; full text
could not be retrieved (biorxiv returned 429/1015 repeatedly), so no numbers from it are verified.**
It reports **a genetic line labelling all campaniform sensilla**, shows by two-photon imaging that
**CS activation induces activity in many leg muscles**, and shows that transient optogenetic **CS
inhibition reduces walking speed**, via **shorter stance amplitudes of longer duration**, together
with loss of interleg coordination and postural control. That phenotype is the classic load-feedback
signature — CS discharge during stance signalling load, and its decay gating the stance→swing
transition — now reproduced in *Drosophila*. **Re-fetch this paper; it is the one that will supply
real numbers.**

The functional story imported from larger insects **[other insect: stick insect, cockroach]** is that
leg CS signal **loading at stance onset and unloading at swing onset**, and that their discharge
tracks **force rate (dF/dt)** rather than force itself, with strong adaptation. The quantitative
version of this — the Zill/Szczecinski encoding models, and the 2025 blow-fly tibial CS recordings —
is being pulled separately. *(in progress)*

**→ how to compute it.** *(provisional, pending the encoding models)* Per-CS-group, take the strain
proxy available from the body model — for the distal groups, the ground contact force on that leg
resolved onto the group's sensitive axis; for the proximal trochanteral and femoral fields, the
muscle/joint torque rather than the contact force — then apply a rectified adaptive high-pass:

```
S(t)      = projection of load onto the CS group's sensitive axis   # cap long axis ⟂ sensitive axis
r(t)      = relu( a·dS/dt + b·S )        with a >> b                 # rate-dominant, small tonic term
```

Group them as **11 populations per leg** matching the table (TrFp, TrFa, FeF, TrG, TiGd, TiGv, Ta1G,
Ta3G, Ta5G, FeS, Ta1S) rather than as 42 independent units — the fields are functionally columns with
shared orientation. **The values of a and b are not measured in Drosophila.** [not measured]

## E.4 Hair plates — the cheapest proprioceptor to implement

Full treatment in the sibling file `hair_plates_bristles_tarsal_sensilla.md`; source notes in
`pratt_2026.md` and `kuan_2020.md`. Summary sufficient to build from:

A hair plate is a patch of short bristles sited so the adjacent segment deflects them only near the
**end of a joint's range**. They are **limit detectors**, and because you already know your joint
limits, they are nearly free to add.

### E.4.1 Inventory (VERIFIED, two independent sources)

**The numeral in each plate's name is its neuron count** — confirmed independently in Kuan et al. 2020
Supplementary Table 3 and Pratt et al. 2026 Fig S5E. One neuron per hair.

Front leg (Kuan AT et al. 2020, *Nat Neurosci* **23:1637–1643**, DOI 10.1038/s41593-020-0704-9):

| Plate | Neurons | Joint |
|---|---|---|
| CoHP3 / CxHP3 | 3 | thorax–coxa |
| CoHP4 / CxHP4 | 4 | thorax–coxa |
| CoHP8 / CxHP8 | 8 | thorax–coxa |
| TrHP1 | 1 | coxa–trochanter |
| TrHP5 | 5 | coxa–trochanter |
| TrHP6 | 6 | coxa–trochanter |
| TrHP7 | 7 | coxa–trochanter |
| TiHP3 | 3 | femur–tibia |
| **total** | **37 in 8 plates** | |

Per-leg complement (Pratt et al. 2026 Fig S1A): **front 8 plates, middle 8, hind 5** = 21 per side,
**×2 = 42 plates**, matching the paper's stated total. Middle leg adds TrHP3, TiHP2; hind leg has only
CxHP4, CxHP8, TrHP5/6/7.

**There is no proximal-femur hair plate.** The distal-most are TiHP2/TiHP3 at the femur–tibia joint.
So hair plates cover the **thorax–coxa, coxa–trochanter and femur–tibia** joints only.

Pratt et al. 2026 (*Nat Commun* 17:2664, s41467-026-69333-z) state **214 hair plate mechanosensory
neurons in 42 hair plates** across six legs. **Summing the naming rule over their own per-leg
complement gives 210, not 214 — a 4-neuron discrepancy neither source resolves.** Flagged rather than
smoothed over; use 42 plates and ~210–214 neurons.

Naming clash to watch: **Kuan writes `CoHP`, Pratt writes `CxHP`** for the same organs.

### E.4.2 Encoding — and the number that does not exist

**Only one Drosophila hair plate has ever been recorded: CxHP8, and calcium only.** It is a **tonic**
limit detector of anterior coxa movement, firing maximally at combined inward rotation plus adduction.
No phasic component was found, though the authors note one could be hidden by the indicator. No
saturation is described.

**There is no published activation threshold in degrees, anywhere in the paper or its supplement.**
Tuning exists only as figures. **[not measured in numeric form]** For real tuning curves, the Dryad
deposit is `doi:10.5061/dryad.fxpnvx153`.

What *is* usable — the thorax–coxa joint conventions and measured ranges (Pratt Fig S1C):

| DoF | Convention | Measured range |
|---|---|---|
| Rotation | posterior = 0/360°, lateral = 90°, anterior = 180°, medial = 270° | **[30, 229]°** |
| Adduction | ventral = 0°, lateral = −90°, medial = +90° | **[−43, +43]°** |
| Flexion | ventral = 0°, anterior = −90°, posterior = +90° | **[0, 54]°** |

Peak CxHP8 calcium density sits near **adduction ≈ 0–15°** and **rotation ≈ 160–180°** (Fig S1F) —
i.e. at the anterior extreme of the measured rotation range, as a limit detector should.

**→ how to compute it.** One-sided rectifier per plate, tonic, no velocity term:

```
r_HP(t) = k · relu( θ_j(t) - θ_limit )        # or relu(θ_limit - θ_j) at the other end
```

Zero across the working range, rising only in the last few degrees. Place θ_limit from the measured
ranges above where you have them, and from your model's own joint limits elsewhere; treat the
sharpness `k` as a free parameter, because the real threshold is unpublished.

### E.4.3 Connectivity — hair plates are a short reflex arc

CxHP8 (Pratt et al. 2026, FANC): **2279 ± 482 output synapses per axon**, of which **~75 % go to
premotor (58 %) and motor (17 %) neurons**. All 8 CxHP8 axons primarily target the **coxa-posterior
motor module**. Context: **69 motor neurons in the left front leg, 14 motor modules** (Lesser et al.
2024 definitions). Hair plate axons **do not project intersegmentally**. They also synapse onto glia.
There are **recurrent 19A premotor → CxHP8 axon** connections, i.e. hair plates get presynaptic input
too — though unlike hook, hair plate activity is **not** suppressed during self-generated movement.

Predicted per-plate function (Fig 5F), and the rule is clean: **each plate drives movement away from
the limit it detects.** CxHP4 → anterior, CxHP8 → posterior, TrHP5 → posterior, TrHP6 → anterior,
TrHP7 → posterior, CxHP3 → stabilisation.

Behavioural effect of silencing: shifts in anterior and posterior extreme positions (AEP/PEP) during
walking and in grooming joint angles, all strongly significant (e.g. AEP lateral p = 5.87 × 10⁻²¹⁰),
but **effect sizes are plotted on ~±10° axes and never stated numerically.** No latency in ms is
reported. **[not measured]**

---

## E.5 Tarsal and tibial afferents, ground contact

### E.5.1 There IS a tibial chordotonal organ — and no tarsal one

Correcting a common assumption: *Drosophila* has a **tibial chordotonal organ (tCO)** in the distal
tibia, distinct from the FeCO. It has **no tarsal chordotonal organ** — confirmed by a negative
scRNA-seq result in Hopkins et al. 2023. Flies also **lack a subgenual organ**; the substrate-vibration
detector is the **club FeCO population** instead (which is consistent with §E.1.4d showing club wired
to intersegmental and ascending neurons rather than leg motor neurons).

### E.5.2 What actually touches the ground

Distal CS groups, from §E.3 — these are what your contact forces should drive:

- **Ta5G (4 CS)** on the **ventral distal fifth tarsomere** — the best ground-contact/load candidate
- **Ta1G (2)**, **Ta1S (1)** on tarsomere 1; **Ta3G (2)** on tarsomere 3
- **TiGv (3)** and **TiGd (2)** on the tibia

Kuan's X-ray volume found **3 CS in ta1 and none in the distal tibia, ta2 or proximal ta3** — a useful
negative.

### E.5.3 Bristles — many, but not a reflex arc

~**400+ tactile bristles per front leg** (Held 1991 via Elabbady et al. 2026); **409 bristle axons
reconstructed in FANC**. Kuan's per-segment partial count (tarsus unimaged): **coxa 13, trochanter 10,
femur 113, tibia 97**. One mechanosensory neuron per bristle.

The structurally important finding: **most bristles make zero synapses onto motor neurons.** There is
no monosynaptic tactile reflex arc — unlike hair plates, which put **17 %** of their output straight
onto MNs. So bristles are exteroceptive and centrally processed; hair plates are proprioceptive and
locally reflexive. Do not model them the same way.

### E.5.4 Totals per front leg (VERIFIED, useful sanity check)

| Class | Neurons |
|---|---|
| FeCO | 152 |
| Campaniform sensilla | 33 (Kuan's imaged range) – 42 (Dinges, whole leg) |
| Hair plates | 37 |
| Stretch receptors | 2 |
| Strand receptor | 1 |
| **proprioceptors subtotal** | **~225** — matches Pratt's "over 200" |
| Tactile bristles | ~400+ |
| **all leg mechanosensory neurons** | **~630–650** |

---

## E.5b Firing rates across all leg proprioceptors — a negative result, stated plainly

**There is essentially no spike electrophysiology from any adult *Drosophila* leg proprioceptor.**
FeCO: calcium only. Hair plates: calcium only. Leg campaniform sensilla: no spike data at all.
Any spikes/s figure for these cells is imported from another species or another body part.

The few hard numbers that do exist:

- **Conduction: 3 ms from a femur bristle spike to the VNC EPSP over ~850 µm ⇒ 0.28 m/s**
  (Tuthill & Wilson 2016, *Cell* **164:1046–1059**, Fig S6A). This is the one measured latency in the
  whole leg-mechanosensory literature.
- Hair plate axons are **thick**: CoHP3 **1380 ± 20 nm**, CoHP4 **1140 ± 240 nm**, CoHP8
  **1030 ± 90 nm**, versus bristle and chordotonal axons too thin to trace at **150–200 nm** (Kuan
  2020). So hair plates are the **fast** channel — but no conduction velocity was measured for them.
  **[not measured]**
- Second-order VNC touch neurons: **5–15 spikes/s**.
- The only chordotonal spike rates in the fly are **larval abdominal lch5**:
  **46.6 ± 15.3 spikes/s spontaneous, 2.36 ms latency** — **not adult, not leg.** Use with care.
- Hair-plate threshold, **[other insect: locust]**: hairs deflected only at femoro-tibial angles
  **< 90°**.

---

## E.6 Connectome labels (MANC / MaleCNS)

From Marin et al. 2024, "Systematic annotation of a complete adult male *Drosophila* nerve cord
connectome reveals principles of functional organisation", *eLife* **13:RP97766**,
DOI 10.7554/eLife.97766.1 (preprint bioRxiv 10.1101/2023.06.05.543407). Verified against the paper
and against the live v1.2.3 annotation table. Full detail, per-nerve tables and neuprint queries in
`docs/research/sources/marin_2024_manc_annotation.md`.

### The naming grammar — and the trap in it

Systematic sensory type names are **`[SN|SA][ch|pp|ta|xx]NN`**. Verbatim from the paper:

> "Final sensory cell types were assigned a prefix indicating whether they ascend to the neck
> connective (SA) or not (SN) and an abbreviation based on their inferred modality — 'ch' for
> chemosensory, 'pp' for proprioceptive, 'ta' for tactile, or 'xx' for unknown. Each distinct type
> within a modality was given a unique number; neurons that could not be classified as a specific
> type were assigned 'xx' as their number."

**The obvious readings of these codes are all wrong.** `ch` is **chemosensory, not chordotonal**.
`ta` is **tactile, not tarsal**. `pp` is **proprioceptive**, and it is a single bucket covering
chordotonal organs, campaniform sensilla, hair plates and strand receptors together. There is **no
`hp` code and no `cs` code.**

- `SN` = sensory, terminates in the cord. `SA` = sensory **ascending** to the neck connective.
- The **number is arbitrary** — an index of a connectivity cluster from their clustering pipeline,
  with no anatomical meaning. Serially repeating leg types keep the same number across T1/T2/T3.
- `xx` in the **number** slot (`SNppxx`, `SNtaxx`, `SNchxx`, `SNxxxx`) means "this modality, but not
  assignable to a specific type". **`SNppxx` is 152 neurons** and is where unidentifiable leg
  campaniform sensilla and surplus hair plates end up.

Actual sensillum identity lives in the separate **`subclass`** field, whose values include
`chordotonal organ`, `campaniform sensilla`, `hair plate`, `mechanosensory bristle`, `taste bristle`,
`strand receptor`. Query on `subclass`, not on the type name, if you want "all campaniform sensilla".

### FeCO subtypes are separable — via the `synonyms` field

| FeCO subtype | systematic types | neurons | `synonyms` value |
|---|---|---|---|
| hook | `SNpp39`, `SNpp41` | **65** | `FeCO hook` |
| claw | `SNpp50`, `SNpp51` | **95** | `FeCO claw` |
| club | `SApp23`, `SNpp40`, `SNpp43`, `SNpp47`, `SNpp56`, `SNpp57`, `SNpp58`, `SNpp59`, `SNpp60` | **188** | `FeCO club` |
| leg hair plate | `SNpp45`, `SNpp52` | **101** (incl. some `SNppxx`) | `hair plate` |
| neck / prosternal hair plate | `SNpp19` | **29** | `neck hair plate` |
| trochanteral campaniform | `SNpp53` | **10** | `TrCS` |

Note that **club alone spans nine systematic types** — consistent with the frequency-tuned diversity
in the physiology, and a useful hook for mapping a tonotopic filter bank onto identified cells.
Note also that `SApp23` is an **ascending** club type, matching the 3–4 FeCO cells per leg that
Mamiya 2018 reported projecting to the brain.

### Hair plates and CS in the connectome — a caveat

Pratt et al. 2026 state that specific hair plate axons **"could not be identified in MANC due to poor
reconstruction quality"**, and re-reconstructed them in FANC instead, assigning peripheral identity
from driver lines, morphology and Kuan's X-ray leg dataset. **CxHP8 is identifiable because it is the
only hair plate entering via `VProN`** (ventral prothoracic nerve). Nerve routing per plate:
**CxHP3 → dorsal prothoracic nerve, CxHP4 → prothoracic accessory nerve, CxHP8 → VProN, all
trochanteral and tibial plates → the main leg nerve.**

This is the same reconstruction-quality problem that undercounts FeCO axons in MANC (§E.0). For leg
sensory neurons generally, **FANC is the better volume; MANC is the better annotation vocabulary.**

### Version warning — this one will bite

**MANC v1.0 and v1.2.x use different sensory type numbers.** The paper states sensory neurons were
"systematically retyped" between releases. `SNpp50` / `SNpp51` / `SNpp52` / `SNpp53` **do not exist in
v1.0**. If your data contains `SNpp51` or `SNpp52`, you are on **v1.2.x** and the numbers above apply.
Do not mix a v1.0 mapping with v1.2.x data.

Field-name casing differs by service: Clio/DVID uses snake_case (`entry_nerve`, `systematic_type`),
neuPrint serves the same fields camelCase (`entryNerve`, `systematicType`).

---

## E.7 Existing models — see `proprioceptor_encoder_models.md`

The sibling file `proprioceptor_encoder_models.md` holds the published encoder models with their
equations and fitted parameters. The one to implement for campaniform sensilla is:

**Szczecinski NS, Dallmann CJ, Quinn RD, Zill SN (2021). "A computational model of insect campaniform
sensilla predicts encoding of forces during walking." *Bioinspiration & Biomimetics* 16(6):065001.
DOI 10.1088/1748-3190/ac1ced.** Code at github.com/nss36/campaniformSensillaModeling.
**Species: cockroach *Periplaneta americana* and stick insect *Carausius morosus* — not Drosophila.**
**[other insect]**

For the body-model side (what a simulator actually exposes — joint angles, velocities, torques,
contact forces), see `D_body_models.md` and `flybody.md` in this directory, plus NeuroMechFly v2
(Wang-Chen et al. 2024, *Nature Methods*) and flygym.

---

## E.8 Summary: what to implement, in order of confidence

1. **Hair plates → joint limits.** Cheapest and best-defined. One rectifier per plate, tonic, no
   velocity term. **37 neurons in 8 plates on the front leg**, covering thorax–coxa, coxa–trochanter
   and femur–tibia. Each drives movement *away* from the limit it detects, with 17 % of output
   straight onto motor neurons — a genuine short reflex arc. Only caveat: **the threshold angle is
   unpublished**, so it is a fitted parameter.
2. **Claw → joint angle.** Best-grounded encoding. One shared threshold plus a proximal–distal strain
   gradient reproduces the goniotopic map; you do not need per-cell tuning curves. Silent near 90°,
   hysteretic, non-adapting. Reflex sign: sensed extension → commanded flexion.
3. **Hook → movement direction, gated by behavioural state.** Rectified derivative, near
   velocity-independent over 100–800 °/s, fast-adapting, and **suppressed during self-generated
   movement** (§E.1.4c). Implement flexion and extension as separate channels — their downstream
   connectivity has almost zero overlap.
4. **Campaniform sensilla → load.** ~42 per leg in 11 groups, cross-validated by two independent
   methods. Right physics (dF/dt-dominant, rectified), wrong species for every parameter — use
   Szczecinski et al. 2021 and flag it. Drive the **distal** groups (Ta5G, Ta1G/S, TiGv/d) from ground
   contact and the **proximal** ones (TrFp/TrFa/FeF) from joint torque, not contact force.
5. **Club → vibration.** Drive from substrate contact, not dθ/dt. Filter bank 100–1600 Hz, saturating
   near 800 Hz. It forms **no direct synapses onto leg motor neurons**, so do not route it into
   posture control. If your rigid-body sim has no sub-micron vibration content, say so rather than
   faking it from joint velocity.
6. **Bristles → touch.** ~400+ per front leg, but **mostly no synapses onto motor neurons** — central
   processing, not a reflex arc. Model differently from hair plates.

### The numbers to design the loop around

| | |
|---|---|
| FeCO neurons per leg | **152** |
| Campaniform sensilla per leg | **~42** in 11 groups (**0 on the coxa**) |
| Hair plate neurons per leg | **37** in 8 plates (front) |
| All proprioceptors per front leg | **~225** |
| All leg mechanosensory neurons per front leg | **~630–650** |
| Processing time between successive steps | **< 30 ms** (Agrawal et al. 2020) |
| Measured afferent conduction | **3 ms over ~850 µm = 0.28 m/s** (bristle; Tuthill & Wilson 2016) |

### The three things most likely to make a naive implementation wrong

1. **Applying passively-measured tuning curves to active movement.** Hook is gated off during walking.
2. **Treating club as a proprioceptor.** It is wired as an exteroceptor and touches no leg motor neuron.
3. **Quoting spike rates.** There are none for any adult Drosophila leg proprioceptor. All the
   physiology is calcium imaging at 8 Hz.
