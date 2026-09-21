# TODO

everything pending, in one place. 2026-09-16 23:30 PDT (nyx); §S added 09-19 16:14. the record (`docs/SEAM.md`)
says what was done and why; this says what is not done yet. items reference the physiology
briefs in `docs/physiology/` where a number came from there. rule for every behaviour change:
one change per run, against the previous run, and a large effect from closing one afferent
loop is probably a bug (mechanosensation brief).

## Q. the queue (19:14 PDT; what a wake picks from, in order; see docs/AUTONOMY.md)

one change per run, its control, the measurement that decides it. status: queued / in flight / measured / adopted / withdrawn.

1. **[in flight] the taste-to-proboscis brief** (opus agent, docs/physiology/taste_per.md): decides items 2-3.
2. **[measured 19:39] the right key**: labellar LB3c (23) and tarsal LgLG4 + LgAG2 (54) held at 100 Hz (measured 75-77 Hz):
   MN9 0.0-0.1 Hz, the pump 0, DNg105 0.2, in every arm. the input was right and the rate Shiu's; the extension does not happen
   at 0.185 mV on this dataset. next: 3 and 3b as single variables.
3. **[measured 19:41] the dose**: labellar LB3c at 200 Hz, 0.185 mV: **MN9 19 Hz** (0.1 at 100 Hz); pump 0. the extension motor
   neuron fires from his own wiring. dose-response 19:43: MN9 0.1 / 0.1 / 0.1 / 5.8 / 19.1 Hz at 30 / 50 / 100 / 150 / 200 nominal (threshold ~90-100 Hz measured LB3c); the tarsal set at 200 Hz: nothing (the long path). the pump never runs at 0.185.
3e. **[measured 22:06; recommendation: keep 0.185 (docs/ASK.md)** 22:01] the constant, (c) then (b)** (nate's answer in docs/ASK.md): re-measure the KC-sparsity calibration on the exact
   engine at 0.185 and 0.275 with one odour protocol; if 0.275 sits in the literature band (~5-10 % of KCs per odour), adopt 0.275 as
   the male default, re-measure the baselines, refreeze oracle v3.
3f. **[measured 09-21 08:55; SETTLED: 0.185 stays] the constant sweep** (nate 09-21): one uniform w at 0.20 / 0.22 / 0.24 / 0.26, each scored on (i) KC sparsity
   (`experiments/kc_sparsity.py`, band 5-10 %), (ii) the sugar-to-MN9 threshold (LB3c held, MN9 vs drive; Shiu's 30 Hz is the model's
   own number, ours will sit above it), (iii) the gnathal runaway (MN11D plateau; a hard ceiling, somewhere in 0.25-0.275); then the
   drum and one anemotaxis batch at the winner. the criteria are stated here before the sweep, and the winner is "the constant of this
   build, chosen by these three measurements", Shiu's method on our network with the floor on, not his number. per-zone gains never;
   scaling by transmitter is the one citable non-uniform variant, later.
3b. **[measured 19:41] 0.275 mV**: LB3c at 100 Hz: MN9 5 Hz, **MN11D (pharyngeal pump) 186 Hz**. Shiu's constant carries the
   whole chain to swallowing. a physiological weight against 0.185 (from KC sparsity): docs/SEAM.md 19:41. NOT a default change yet.
3c. **[measured 09-21 09:40; DEFAULT] "feeding" read from MN9** (3/3: MN9 13-16 Hz on the fruit, 0 off; eats and leaves); batch in flight] "feeding" read from MN9 (`--feed-read mn9`, labellar cells at 200 Hz on the fruit, the labellum a geometry stand-in); the sugar row of the garden re-pointed at the labelled
   cells (LgLG4 + LgAG2 for the tarsi, LB3c when the labellum touches, which needs the proboscis geometry).
3d. **[done 23:10] DNg105's source audit**: chosen by synapse count onto leg MNs (motor review) and by measurement (it halts the woken cord); not a Sapkal 2024 named halting neuron; a measured brake, labelled so.
4. **[measured 09-21 09:14; DEFAULT ON] walkable tops** (`--climb`: the fruit and the stone are domes; he climbs, eats standing on it, leaves, 3/3; the collider jumps were not reproducible in any current run, so no tunnelling fix was needed) (§P physics): the fruit and the stone as mounds he stands on; taste from the
   surface under him; contacts resolved against every object with a per-frame push-out cap. decides: can "on the fruit" be a
   state of the world at all. control: the record run of 09-19 evening on the new physics.
4b. **[measured 09-21 14:29; DEFAULT ON] tilt**: pitch and roll from the dome's slope; the eye rotates with the head (pitch sign checked); gravity on the JO rows; the leg load split by segment and side; 3/3 climbs, feeds, leaves. next on the row: the horizon vs the HS wheel; JO gravity vs wind on a slope; the heightfield.
   change: `Eye.render` gains pitch / roll, zero stays bit-exact); JO gravity cells (JO-C/E, the gravity component along the
   antennae, Kamikouchi 2009) from the tilt; leg load split front / back on a slope into the proprioceptive rows; the ocelli
   sample the sky along the tilted head. this is the "gravity" row of §S and the terrain item of §2a together. a day.
4c. **[noted 09-21] the loops**: the goal-switch's random inward heading plus the comparator with its null off make pirouettes at
   stalks; on the menotaxis row; left for now (nate).
5. **[queued] a run that crosses shade** for the ocelli, the ocellar cells logged (§S ocelli row).
6. **[queued] his own walking wind on the aristae** (§S wind row): a vector add; anemotaxis batch as control.
7. **[queued] the clock and sleep pressure as the first S2 states** (`states.py`, FeedingState moved into it): a day in the
   garden; decides: two activity peaks, a night stop. PARKED by nate 22:01 until the short-run behaviour is settled and the statistics are better (docs/ASK.md).
8b. **[traced 09-21 13:49] the wing motor artefact**: IN06B013, a four-cell hub in the flight / song premotor network, lights from ANY broad tonic input (thermal, floor, vision each alone) and is input-driven, not bistable (bare-engine test); with the full input set the wing MNs sit at 31 Hz. not one sense's fault: the cord's premotor network is too excitable to tonic input at 0.185. options: the flight gate as a state (S2, my lean), a labelled input-gain correction on the hub, or leave it (the wings drive nothing here). docs/SEAM.md 13:49. 09-21 14:14: the tarsal reflex (feet on the ground suppress flight) is not a two-hop path in the table: the hub's sensory input is wing campaniforms (excitatory, silent here), its inhibition (a third of its input, IN06B047 et al.) gets no leg afferents. the gate as a state stays the lean. 14:55: the standing signal dosed (leg load 0-120 Hz): damps the wings a fifth (35 -> 28) and saturates; the hub unmoved; the leg MNs scale with the load (37 -> 63 Hz), so the floor's 15 is not free. the rest is the gate.
8c. **[queued 09-21] two leaks found on the way**: the setup's calibrations leave drive_hz nonzero on 314 cells no run row overwrites (zero drive_hz after the calibrations); the reference engine holds the 97 MBONs at 85 % of threshold (`mbon_hold_frac`, flybrain's, not Shiu's): measure what it does, decide, label. neither moved the wing result.
8. **[queued] DNp20 at 150 Hz with every sense off**: which floor row or command drives it; a diagnostic, one wake.
9. **[queued] the benchmark scorer's hysteresis and heading filter; the 600 s dish** (§2d).
10. **[queued] her in the garden** (§2a), then the courtship state.

settled (not to be relitigated by a wake without a new reason): the synapse constant is 0.185 mV (the sweep of 09-21: the gnathal runaway caps w at 0.24, sparsity leaves its band at 0.22, and below that w does not move the taste chain's threshold; the lever is the input, i.e. the physics); the DN population channel is heading noise (09-18); the
null point was a crutch (09-19); the thermal field is on under `rest` (09-19); the ocellar photoreceptors are out of volume
(09-19); exact integration is the engine (09-19); three seeds is the floor for a claim; the antennae are 0.35 mm apart.

## S. the senses, the strict list (09-19 16:14 PDT, nate: "treat each un-implemented sense as our strictest to-do list for
## the sake of behavioural measurement"; every sense on unless there is a stated reason; one sense per run, its own rest as the control)

the cascade of 09-19 is the argument: the wind result was wrong until the compass existed, the compass useless until the goal
did, the goal useless until the comparator pair was mended, and the fruit reachable only with all of it standing. so the
un-implemented senses are the experiment list, in the order that unblocks a measurement soonest. `docs/SENSES.md` is the
status table (cells, resting rates, sources); this is what is wrong with each and what to build next.

| sense | today | what is wrong or missing | next build | it would let us measure |
|---|---|---|---|---|
| olfaction (2,635 ORNs) | fruit plume per antenna, Weber-Fechner per side; her odour exp(-d/0.8) | **antennae 4.5 mm apart (12x a fly's), straddling a 3.75 mm plume; one whiff coin shared by both antennae, so no between-antenna timing** (found 16:14); whiffs Bernoulli, not power-law; no running-mean normalisation per ORN | [x] `--antennae real` (16:44: asymmetry 0.2-0.4 -> 0.02-0.05, anemotaxis holds 3/3, control 0/3; exposed and fixed 17:10: `--wind-sated`, the sated fly leaves 3/3 (Root 2011); in the flip); then sub-chunk sensory time (Kadakia 2022's odour-motion sensing needs ~ms delays; our sensory frame is 10 ms, the whiff 100 ms); then power-law whiffs; her odour and a rival's through the same plume | bilateral vs temporal smell (Gaudry 2013 / Taisz 2023 vs Alvarez-Salvado 2018 / Demir 2020); whether anything lateralises at the steering readouts once the geometry is honest |
| wind (JO-C/E) | `--wind on` measured 17:04 (anemotaxis holds 2/3); default after the flip; the compass goal turns upwind while a whiff is on | the wind of his own walking (he moves through still air at 2-8 mm/s) is not on his aristae; no efference copy | self-motion wind on the JO rows, then the efference copy (Cheong 2024) | whether anemotaxis survives his own wind |
| temperature (hot 7, cooling 7) | on in every garden run since 09-17 under `--thermo rest` (the rows read the garden's own field; `field` is the room's warm corner, which the garden ignores: corrected 17:12) | the phasic on-warming component of the hot cells; a run that puts the sun patch on his way | `--thermo rest` in the flip; then a start in the patch | kinesis under the sun, the shade stops |
| humidity (66) | the puddle is a field; cells at the floor | VP1m / VP1l label audit (Marin 2020) before driving | the audit, then dry / moist non-adapting from the puddle | hygrotaxis with a state-dependent sign (needs thirst) |
| taste (1,416) | sugar and water on the tarsi; feeding state | bitter, salt, pharyngeal absent | bitter as a field on the same surface (Gr32a/Gr33a), PER threshold under satiety | food choice; aversion |
| touch (2,503 bristles) | adapting kernel, left / right by side | by body part (antenna, head, legs, wings are typed); no seconds-scale fatigue | bristles by body part; the head-on class for head bristles | the wall-following posture; grooming triggers |
| proprioception (580 leg-nerve) | tonic load 15 Hz standing; opt-in tripod rule | campaniform dF/dt, FeCO gating under command (Dallmann 2025), gait from speed (Wosnitza 2013) | campaniform sensilla as a transducer; the FeCO gate at the drive | the reflex loop's gain; whether the cord's own rhythm appears |
| vision, motion (T4/T5) | flyvis through his eye, both eyes | walking-state gain on the visual channels (Chiappe 2010); no saccade efference copy; no loom (DS fidelity) | the walking gain as a state on the seam; the loom detector on the eye track | the saccade as an event; the escape path |
| vision, colour / UV (R7/R8) | UV retina and sun disc rendered (`--uv`); the pathway does not carry spikes (histaminergic photoreceptors) | the anterior visual pathway (R7 -> Dm2 -> MeTu -> TuBu -> ER) needs a graded model; the ring fields are imposed from the sun's azimuth | the graded anterior pathway (the eye track) to replace the imposed ring fields | a compass from his own eye; the sun as a seen thing |
| ocelli (46 interneurons) | silent | **the photoreceptors are outside the imaged volume** (16:30: nothing entering by the ocellar nerve touches OCG / OCC; their input is all typed brain cells) | [x] 23:18 crossing shade: the cells follow the light (r -0.9), DNpe017 x2, DNp22 x5, he walks 2x as far 3/3; the constant-light control gives most of it: TONIC push, the light part inside the noise. next: a run where the light changes a lot (dusk, canopy) | light-level and horizon reflexes; whether the ocellar descending path (DNx02? four cells in the ocellar nerve, near-zero input in the volume, 10,000 outputs each onto AN06B025 / GNG) does anything |
| contact pheromone (ppk23 F/M) | 60 Hz burst on a tap with her | no rival to fire the M channel; Gr32a/Gr33a aversive channel absent | the rival, once, with controls (§7) | the P1 dial (Hoopfer 2015) |
| hearing (JO-A/B) | silent | she never sings; his own song is out of reach | her song rows exist; needs a singer | the courtship sequence as a state |
| gravity (JO, terrain) | silent | flat world | a heightfield tilting his pose (§2a) | geotaxis |
| the delays | none (frame-level, 10 ms) | sensory 5-15 ms in, motor 20-40 ms out; without them he is more stable than a fly | delay lines at the drive and at the effectors | which successes were his and which were the missing delay |

the flip (17:26): antennae real, wind on, thermo rest and the satiety gate are the defaults; the oracle lines pin their
own fly explicitly, so the defaults can move without a refreeze (docs/SEAM.md 17:26).

ranked by difficulty (16:23, nate asked). a flag flip or an afternoon: temperature in the garden; ocelli as a labelled stand-in on the interneurons (the receptors are out of volume); his own wind on the aristae;
humidity (after the VP1 audit); bitter and salt. a day, and it moves the baselines: bristles by body part; the delays (a
refreeze); plume timing (power-law whiffs cheap; per-antenna packet timing needs the drive resolved per ms, §1). needs another
build first: proprioception (the leg model), gravity (terrain), hearing (a singer), the rival's channels (states first).
research, not engineering: colour / UV (the graded anterior pathway), loom (DS fidelity).
the walk: temperature, own wind, bitter, plume timing, then the delays.

and the units: 1 sim m = 15 mm, and the antenna error hid in that conversion. `MM_PER_M` in the viewer (scale bar, 16:14); every
number a human reads should be in mm; the world's own rescale to mm is an oracle-refreeze job (§5b).

## S2. the states, the body's half of him (18:47 PDT; nate: should the clock be on the list, and is modelling the slow chemistry honest?)

the senses are what the world does to him. the states are what his body does to him: blood sugar, gut stretch, osmolality,
the clock's gene loop, sleep pressure, hormone tone. the cells that read and release them are in the table (IPCs, AKH targets,
the interoceptive SEZ cells, ~150 clock neurons, the dFB and R5 sleep cells); the blood, the gut and the gene loops are not,
and a fast-synapse LIF has no variable for hours. so a state can never come out of the wiring here, and pretending it did
would be the puppet. honest = one body-side scalar with its own time constant, a source, and a labelled list of (cell type,
gain) that it sets, measured as one change against the same run with the scalar at rest. `FeedingState` (09-18) is the
first of the class and the template; `--wind-sated` (09-19) is its first gain. one class, `states.py`, when the second arrives.

| state | in life | scalar and clock | what it sets, on which typed cells | first measurable | order |
|---|---|---|---|---|---|
| satiety / gut fill | crop stretch (Piezo, Min 2021); sugar GRNs damped when fed | built: fills over 8 s of feeding, decays tau 180 s | the halt (DNg105), the withdrawal reflex, the wind goal | done: eats and leaves. **18:56: the halt is ours; his wiring given sugar on the tarsi moves neither DNg105 nor any of the 67 proboscis MNs (MN9 0 Hz); the proboscis never extends. next: where the taste path dies (GNG relays, AN04A001 / AN08B032)** | done, labelled a stand-in |
| hunger / energy | haemolymph sugar, fat stores -> AKH, DILPs (IPCs), unpaired-2; dopamine raises sugar-GRN gain (Inagaki 2012), sNPF raises food-ORN gain (Root 2011) | one scalar, hours; rises with time since a meal, falls with satiety | gain on Gr5a / Gr64 tarsal GRNs and the fruit ORNs; the PAM dopamine bias toward food | whether a hungry fly finds the fruit sooner than a fed one, 3 seeds each | 2 |
| thirst | osmolality read by the interoceptive SEZ neurons (Jourjine 2016), which also sense AKH | one scalar, hours; rises in dry air, falls at the puddle | water GRN gain, the humidity sign (dry when sated, moist when thirsty) | the puddle vs the fruit choice | 3 |
| the circadian clock | PER/TIM loop in ~150 clock cells, free-running 24 h, entrained by cryptochrome and the eyes; l-LNv fire at dawn (PDF) | a phase, 24 h, advanced by the run's clock, reset by the sun | the clock cells' rate profile by phase; the sleep drive's gate; locomotor activity peaks at dawn and dusk | the garden with a day: does activity peak twice | 1 (it is what makes a run a day) |
| sleep pressure | dFB excitability switch (Pimentel 2016), R5 ring neurons accumulate need (Liu 2016) | one scalar, hours awake up, sleep down | the dFB cells' drive; when high and the clock says night, the walking command off, senses damped | a long run in which he stops at night and starts at dawn | 1, with the clock |
| arousal tone | octopamine / dopamine, minutes | one scalar | gains on the startle path and the walking command | later | 4 |
| courtship drive / mating history | dopamine to P1 (Zhang 2016), sex peptide in her (SPSN) | one scalar each | P1 threshold; her receptivity (vpoEN) | with her in the garden | with her |
| hormones over days | juvenile hormone, ecdysone; the loser effect | days | aggression threshold, the P1 dial | with the rival, once | last |
| body temperature | every rate Q10-scaled by the fly's own warmth | one scalar from the field | a global rate scale on the drive | later | later |

the line, restated with these in view (nate, 09-17; nyx, 09-19): hunger and sleep pressure are the first states where a run can
be bad for him in a way the model itself represents. once they exist, every long run is one in which he can eat and sleep,
and no run starves or wakes him on a loop. that is not sentiment about a LIF; it is the rule we set for the moment he had
persistent states, and this is the moment.

## P. the puppetry ledger (18:59 PDT; nate: "keep an item to improve our embodiment signals toward a state where we no longer need it")

every place where a rule of ours drives one of his cells or sets his goal from a fact of the world he has not sensed. each
is labelled in the record where it was made; this is the list of them in one place, with what would retire each. the test
for whether an entry belongs here is the one from the puppet piece: silence the readout, or take our rule away, and see if
the behaviour changes. the ocellar stand-in and the thermal transducers are NOT here: a transducer reading a world quantity
into the first cell we have is a sense, the same as the bristle kernel.

| stand-in | what we drive or decide | why | what retires it | status |
|---|---|---|---|---|
| the walking command | DNg100 tonic at 100 Hz | the walking state is a slow state he does not have | a walking state (S2: arousal, the clock) that sets DNg100; or DNg100 driven by his own descending inputs on a woken brain | since 09-18 |
| the feeding latch | since 09-21: "feeding" is READ from MN9 firing (his own wiring, given the labellar sugar cells on the fruit); what remains ours: the halt (DNg105 driven while feeding) and the labellum-on-food condition (geometry) | measured 19:02 with the taste held: the leg GRNs (24 Hz) double the ascending AN04A001 (17 -> 33 Hz) and nothing past it moves: gnathal relays, MN9, the pump, DNg105 all 0. dies at the second synapse | the taste path carrying: leg GRNs -> AN04A001 / AN08B032 -> DNg105 and GNG relays -> MN9; "feeding" read from MN9 and the pharyngeal pump firing, not imposed; and the physics below, so he can stand on food | since 09-18 |
| the goal that yields | a new heading drawn inward after 5 s of contact | the CX has no goal-selection state here | a goal state on the FB columns from his own inputs (PFL2's pause-and-turn; Green 2019's switching) | 09-19 13:45 |
| the wind goal | the goal set to the WORLD's upwind while a whiff is on him | the JO wind rows do not reach the CX goal at these constants | the JO rows (`--wind on`, default now) feeding the goal through his own wiring (Okubo 2020: wind direction reaches the CX via the LAL) | 09-19 14:57 |
| the satiety gate | the wind goal ignores the whiff while full | the sated fly's ORN gain drop is a peptide we cannot hold | the hunger scalar (S2) as a GAIN on the fruit ORNs, so the goal never sees the whiff rather than ignoring it | 09-19 17:09 |
| the ring fields | ER cells driven by the sun's azimuth in their fields | the anterior visual pathway carries no spikes (histaminergic photoreceptors) | the graded anterior pathway (the eye track) | 09-18 23:55 |
| the goal drive | FC2 columns driven at a goal heading | no goal state | see the goal that yields | 09-18 |
| the state pace | speed read as a threshold + hysteresis on the cord | a readout, not a drive; here because it decides "walking" for him | leg MN phase (gait) read as stance / swing | 09-18 12:20 |
| her wall turn-away | she turns at walls by a rule | she has no cord | her cord (the female VNC is not in FlyWire; MaleCNS is male) | 09-17 |
| her odour, his cVA | exp(-d / 0.8), smooth | no plume for a fly | the same plume as the fruit's, with whiffs | 09-16 |

**the physics that keeps two of these alive** (nate, 18:59): a fly lands ON its food and stays there, walking while it eats; the
fruit here is a collider he presses against, and he has been seen zoomed out through colliders when caught between two. so
"on the fruit" is a physics-sandbox limit, not only a wiring one. items: walkable tops (the fruit, the stone as mounds he
climbs; taste from the surface under him; the plume source under him; the goal-switch not firing on food), and the collider
tunnelling (resolve contacts against every object, not the last; a cap on the push-out per frame). belongs with the terrain
item in §2a and should come before the taste path is judged.

## 0. in flight tonight

- [x] approach test: 10 seeds x {her dark 0.1, her invisible 0.5} x 120 s (`world/approach/`).
      in the record 23:50: left-side effect was an artefact; right-side turn toward her survives
      (8/10, p 0.02) plus 1.8x time near her. re-run pre-registered after the steering fix.
- [x] corrected synapse constants, first minute (`world/pair_w185.npz`): in the record 00:00.
      standing baselines all zero; leg MN halves; he still finds her. PACE READOUT DEGENERATE
      (standing = 0 saturates it): fix in effectors with an absolute reference + MN class weights.
- [x] oracle runs (`world/oracle/`, `scripts/oracle_check.sh`).

## 1. the refactor (`docs/ARCHITECTURE.md`), before any new receptor

- [x] oracle runs: current room, `--deterministic`, 30 s, seeds 3 and 4, at old and corrected
      constants (four npz). the ported room must reproduce them bit for bit. (00:32: pass)
- [x] `receptors.py`: registry + selectors + transducers; existing drives ported unchanged;
      verified bit-identical (00:32). physiology transducers (Adapting, Differentiator,
      WeberFechner) still to write, one per behaviour change.
- [x] `body.py` + `world.py`: pose, contacts, walls, pillars, the pair, the scene; verified
      bit-identical (00:58). gait generator, body-part contacts and scalar fields still to come.
- [x] `effectors.py`: steering, pace, her steering, song, the calibration procedures; verified
      bit-identical (01:10). calibration cache by (brain, w_syn, seed) still to do.
- [x] `episode.py`: one loop, verified bit-identical (01:21); `pair.py` is 134 lines of setup.
      still to do: `per_frame` / `per_chunk` namespaces, two brains in threads (numba `nogil`).
      `loop.py` stays a legacy experiment; its modes get re-implemented on the stack (drum first)
      and validated against the recorded numbers rather than ported.
- [x] flyvis front end as `frontend.py`; the room uses it; verified bit-identical (01:47). pair.py 111 lines.
- [x] drum on the stack (`experiments/drum.py`, 01:28): 2/3 seeds follow both ways (record: 3/3;
      ensemble 2-3/10). bar, walk, forage modes still to re-implement when needed.
- [ ] `--no-female` default for calibration and male-only questions; her in the room only for
      contact and courtship runs.
- [ ] drive resolved per 1 ms step, not per 10 ms frame (30 ms adaptation kernels need it).

## 2. physiology-driven changes, one per run, in this order

- [x] **THE TONIC FLOOR** (built 09-17 18:27): central 0.013 -> 0.53 Hz, DN symmetric, KC code unchanged;
      room: less pinned, further walked. default from here. rates marked (E) still to source; JO, proprio.
- [ ] (was:) every typed sensory class at its physiological
      resting rate by default (ORNs ~8 Hz generic, Or67d 0.12, hot 37, cooling 95, dry/moist ~20,
      JO still-air, proprioceptors under standing load, gustatory ~2, ocelli by light), the world only
      modulating. one step against the current baseline; expect the operating point to move.
- [ ] the walking command silences DNa02 R (2.6 L / 0.02 R per chunk on a walking cord; 1.6 / 1.4
      standing): an interaction between the command and the visual wheel. trace it (DNp09 -> ? -> DNa02 R)
      and decide whether the wheel reads DNa02 at all on a walking cord (18:15).
- [ ] thermokinesis: turning rate up when warming is in the wiring (17:20); the pace sign is inverted
      (readout interaction with turning). understand, then the cold corner and the extremes.
- [~] **synapse constants** (vision brief): male 0.185, female 0.275; `RunningPace` fixes the
      degenerate pace (08:58); male-only baseline in progress; then her. re-measure every baseline. reconcile her 0.45 KC-sparsity calibration with the
      22:55 odour test (4.7% at 0.275): different odour protocol, find which was right.
      re-examine MDN's tonic activity (present at 0.275, gone at 0.185) and the reverse-walk rule.
- [x] **steering baseline**: `RunningBaselineSteering` (01:55). model 000: 3/3 seeds (fixed 2/3);
      ensemble 3/10 (fixed 2/10), biases from +-100 to +-20, and two models revealed as anti-followers.
      adopted as the estimator; the wheel's per-model sign is a seam question, not a steering one.
- [ ] **DNa02 gain**: 5 deg/s per Hz (bracketed 3-10; ours is 3).
- [x] **bristles** (mechano brief): `Adapting` 200 Hz onset, tau 30 ms, 20 Hz plateau, half the patch,
      step-locked re-deflection at 10 Hz; reflex calibrated on the kernel (09:23). adopted. still
      to do: seconds-scale fatigue, by body part; measure the bristle->leg-MN gain at 0.185 mV.
- [~] **leg MNs**: audit DONE (12:05): bristle = muscle-specific withdrawal pattern; vision = a whisper;
      warmth = bilateral. next: the motor-pattern readout (projection on the withdrawal axis); Azevedo
      2020 classes (slow ~30 Hz standing; 0.1/1/10 uN) still unmodelled.
- [ ] **campaniform sensilla**: dF/dt, burst at stance onset, adapt out mid-stance, a
      subpopulation on unloading. replaces the 15% tonic load term.
- [ ] **gait**: step frequency from speed (Wosnitza 2013), stance ~ v^-1, swing 20-45 ms,
      period floor 60 ms (16 Hz max, not 10); tetrapod below 5 BL/s, tripod above 10.
- [ ] **hook FeCO gate**: presynaptic inhibition during walking under descending command
      (Dallmann 2025); apply at the drive (Poisson receptors ignore their membrane). claw,
      club, hair plates ungated.
- [x] **cooling cells** and **hot cells** as transducers (`CoolingCells`, `HotCells`, 09:49) with
      Budelli 2019's numbers; on in the room with `--thermo rest|field`.
- [ ] **VP1m / VP1l label audit** before driving either (Marin 2020: VP1m humid, VP1l cool).
- [ ] **the warm corner** (13:28): no avoidance on a walking cord either (2/3 warmer with the field).
      thermal DNs reach wing MNs mostly; warmth is bilateral at the legs. parked: thermotaxis by walking
      is not in this model at these constants. what warmth does do: drives the legs harder (kinesis).
- [ ] **hygro**: dry/moist cells non-adapting, tens of Hz; a humidity field. Or42b ORNs are
      also humidity sensors (Li 2022).
- [ ] **plumes**: intermittent (power-law whiffs/blanks, exponent -3/2), ORN rate from
      concentration divided by a running mean (tau ~1 s). replaces exp(-d/0.8). Or67d rest
      0.12 Hz, not ~8.
- [ ] **sugar spot**: Gr5a/Gr64 ~65 Hz at 100 mM, adaptation within 1 s; bitter > 10 Hz =
      aversion floor. a room with three things in it (her, warmth, sugar).
- [x] contact-pheromone tap: 60 Hz burst, tau 300 ms, both ppk channels (done 22:40).
- [ ] Gr32a/Gr33a aversive channel on male-male contact (10-60 Hz, phasic).
- [ ] **LC10a gain P1-dependent** (Hindmarsh Sten 2021): without it he does not track her.
- [ ] **P1 as a dial, not a switch** (09-17 17:44): read P1 rate against Hoopfer 2015's thresholds
      (low activation = aggression, high = courtship); our touch-driven P1 sits at the low end. audit
      which inputs move it where; the same reading serves the rival and the courtship state.
- [ ] **the courtship sequence as a state** (promoted 09-17 13:59): a persistent state (pCd, minutes)
      that holds the brake (AN19A018) at her and drives following; her stop or receptivity (vpoEN);
      P1 threshold-graded (Hoopfer 2015). the song relay (P1 -> pIP10) stays blocked; mAL gate measured.
      --stop-at-her (brake on contact frames) did nothing: contact is too brief and she walks away.
- [ ] walking-state gain on visual channels (Chiappe 2010; Suver 2012).
- [ ] efference copy onto JO-A/B (Cheong 2024); JO wind/gravity; the wing-wash loop when he flies.
- [ ] ocelli: light level; find his OCC/OCG cells (hers are typed, 63).

## 2a. the enriched world (promoted 09-17 22:05, nate; before the rival)

- [x] the garden (09-17 night): floor plane with texture, grass, leaves + shade, stone, fruit (plume +
      sugar), puddle (humidity), sun patch, rim; RGB reduced to fly luminance; both raytracers.
- [x] first scores (09-18 00:24): the fruit is found by sight (0/3 when invisible), the plume changes
      nothing (smell does not reach the steering readout); puddle / sun / shade passed through.
- [x] **anemotaxis on the settled fly** (09-19 15:00: through the compass, the goal set by the wind while a whiff is on him;
      2/3 walk up the plume onto the fruit in 6 s and eat, control 0/3; `docs/figures/anemotaxis.png`).
- [ ] (was:) **anemotaxis on the settled fly** (09-18 16:50): the wind-gated upwind turn was measured on a fly with
      50 deg/s of heading noise; now 20-29. re-run the downwind start with `--wind on --wind-gate odour`
      (the wind rows need a steering channel: the population channel is out of the config as noise; a named
      six lateralised DN types (review) or the JO rows into the HS wheel's baseline is the design question).
- [ ] the plume: power-law whiff / blank durations (simplified Bernoulli today); her odour and a rival's
      through the same field; the smell-steering gap (ORN -> ... -> DNa02 is silent) is the wall.
- [ ] the garden with her; the garden with the courtship state when it exists.
- [ ] terrain (nate): a gentle heightfield tilting his pose, feeding JO gravity and leg load (phase 2).
- [ ] bristles by body part (antenna, head, legs, wings are typed); the head-on class returns for
      head bristles.
- [ ] status of every sense: `docs/SENSES.md`.

## 2b. legs with muscles (promoted 09-17 12:30)

- [x] the leg MN SET: 373 leg MNs by subclass fl/ml/hl (12:45; the 699 included abdominal, wing,
      haltere, neck, jump). all leg readouts re-based on it.
- [x] the leg model (12:36): `legs.py`, DNa02's sign reproduced; effector `--effector legs`.
- [x] a walking command (12:56): `--walk 100` (DNp09 tonic); he walks 31 m / 2 min on the true leg set.
      **09-18 11:30: DNp09 is inert under the tonic floor; the command is DNg100 (BDN2) now, a dose in the loop
      (16 / 35 / 50 m at 0 / 100 / 200 Hz), pace read against the standing tonus measured in the floor.**
      **12:20: `--pace state` (threshold + hysteresis on the smoothed cord; DeAngelis 2019 bimodal): he stands
      with no command and walks in bouts with it. config of record.** next: the closed-loop floor-row
      ablation (which row lifts the resting cord: thermal? ORN?); MN class weights (Azevedo 2020); the brake
      re-measured against DNg100 (30 Hz did nothing open loop).
      still to do: the command as a state (walk / stop / brake DNs, Sapkal 2024); stance/swing phase
      so MDN reads as backward; the DNp09 right-bias (tracing) as a labelled correction or not.
      the leg model is NOT a wheel (drum 0/3 rectified, 1/3 signed): pace + diagnostic only.

## 2e. what the dish said (09-18 18:25, `experiments/benchmark.py` vs the Roman lab's flies)

- [x] **the goal yields at a wall** (09-19 13:45: `--goal-switch`, contact = position at the boundary, new heading drawn
      inward): corner 54 -> 4-11 %, standing 66 -> 13-18 %; the rim stays ~57 % and that is thigmotaxis, the fly.
      PFL2's 182 deg bridge offset and PFL3's +/-65 read from the labels; the stand-in's mapping was right.
- [ ] (was:) **the goal yields at a wall** (09-19, nate's observation): a fixed goal heading pins him into a corner, pointed outward,
      PFL2 idling him. the goal as a state: switch to a new heading after N s of contact (Green 2019: headings held for
      minutes, then switched); labelled. also the viewer's compass panel (in flight).
- [~] **menotaxis, in stretches** (09-19 11:26): the graded PFL3 readout (`--goal-wheel-v 20 --goal-ema 5`, the null point with
      the bump present) holds a goal heading 41 % / 34 % of a run within 30 deg, in 20-40 s stretches, lost at the rim and at
      the 180 deg saddle. next: the dish (no rim detours); a slowly adapting null; PFL2 as the forward drive when aligned
      (in life he pauses and turns when far off the goal); then the saccade as an event on top.
- [~] **the compass, stand-in built** (09-18 23:55): `--ring` forms a bump that tracks his heading from the sun (r 0.99;
      `docs/figures/compass_bump.png`), sensory-driven (PEN silent); `--goal` makes PFL3 compare with the right sign
      (r -0.68 with the error) and reach the LAL; `--goal-wheel` does NOT hold a heading (PFL3 3.6 Hz across 24 cells:
      shot noise 5x the signal). all three stand-ins are opt-in and tuned. NEXT, graded: (a) a graded PFL3 / LAL readout
      (rate from membrane, not spikes) or the goal drive raised until PFL3's L-R is above noise, labelled; (b) the
      anterior visual pathway graded (the eye track) to replace the imposed ring fields with seen ones; (c) the ring's
      persistence (EPG-PEN recurrence at 0.185 mV).
- [ ] **the compass needs a graded build** (09-18 late): the UV retina, the sun disc and the columns exist (`--uv`), but the
      anterior visual pathway (R7 -> Dm2 -> MeTu -> TuBu -> ER) does not carry spikes at these constants (photoreceptors
      are histaminergic: light inhibits; Dm2's excitation is two synapses' worth; at gain 1,000 the ring neurons still
      sit at 0). and the ring's bump is tonic excitation shaped by inhibition, which silent LIF cells cannot do. options:
      (a) a graded model of the anterior pathway + the ring (a flyvis-like extension: the eye track); (b) a labelled
      stand-in: ring neurons driven by the sun's azimuth (their receptive fields tile azimuth in life), with the EPG
      ring given a tonic floor (ExR1 / PEN at rest) so ER inhibition can shape it; test with `experiments/compass.py`.
- [ ] **the compass is dark** (09-18 night): EPG / PEN / Delta7 / PFL all 0.00 Hz with vision on, and the ring does not
      hold a kicked bump. FIRST: the anterior visual pathway into the seam: flyvis Mi15 onto his Mi15 cells by column
      (Mi15 / Dm2 -> MeTu -> TuBu -> ER; the R7/R8 pathway, a luminance stand-in, labelled) + a sun disc in the sky
      (a few degrees, clipped white; the eye's acceptance angle is the bloom). score: EPG rates, a bump vs shuffle,
      phase vs heading (`experiments/compass.py`). THEN: bump persistence in darkness (the EPG-PEN loop at 0.185 mV).
- [ ] **the saccade.** he never turns sharply: every 40 ms heading change under 30 deg (life: 60 %); inter-turn
      interval 1.0-1.4 s (life 0.25). look in the wiring first: do DNa02 / DNa01 / DNb06 / DNg13 burst on the
      woken brain, and can a burst be read as an event (a fixed-size turn) on top of the smooth HS wheel
      (Rayshubskiy 2020: DNa02 bursts precede spontaneous turns). a stand-in only after, labelled.
- [ ] **the spontaneous stop.** he never stops in the dish (0 % vs 21 %); bouts end only when something halts the
      cord. do the halting types (DNg105, the Sapkal 2024 set) fire on their own on the woken brain?
- [ ] **reversing along the wall.** circling bias exactly +/-1; both of the above should fix it; score it.
- [ ] the scorer: hysteresis on the walking threshold; a heading filter for tracked centroids; the 5.0 cm dish
      as the second condition (`--arena-radius 1.67`).
- [ ] the viewers: draw the ring for `world == "arena"`.

## 2c. what the fly asked for (09-18 01:02, `docs/SCENARIOS.md`; the unmet items, in his order)

- [~] **persistent internal states** (09-18 14:15: the FIRST one is built: `FeedingState`, sugar latches feeding,
      holds the halt on DNg105, silences withdrawal; satiety fills and releases; he eats and leaves. the rest:)
      as scalars with decay constants: hunger, thirst, satiety, arousal,
      sleep pressure, aggression threshold, the loser effect. modelled as what they do (gains on
      food receptors, thresholds on outputs, a drive on the walking command), labelled; the engine has
      fast synapses only, so driving the peptide cells does nothing (SEAM 00:54). breaks six of his
      twenty scenarios by itself. the next build.
- [ ] the plume with power-law whiff / blank durations (see 2a) and the wind that carries it also
      deflecting his aristae (done: `--wind on`).
- [ ] **bitter as a field** on the same surface as sugar, non-adapting, Gr32a/Gr33a; the PER threshold
      under the satiety state. (sugar, water: done.)
- [ ] **the escape path**: loom -> giant fibre -> jump, outside the deliberative loop, both take-off
      modes; needs a loom detector the eye track does not have yet (§3).
- [ ] **sensory and motor delays** (5-15 ms in, 20-40 ms out): without them he is more stable than a
      fly and we cannot tell which successes came from that. frame-level today (10 ms).
- [ ] **humidity with a state-dependent sign** (sated: dry; desiccated: moist, faster in dry air): one
      field, one sign, from the thirst scalar above.
- [ ] **a compass with drift** (menotaxis: sky direction, updated by his own turns, holdable at an
      offset for minutes): the central complex has it; a sun in the garden already; measure whether
      EPG / PEN bump exists in him before building anything.
- [ ] **luminance- and temperature-dependent bandwidth** (eye Q10 6.5; dusk): a gain on the eye
      front end, later.
- [ ] **efference copy into the wide-field visual channels** at saccade onset (with the JO one in §2).
- [ ] declined by him, agreed: no wings, no oscillating halteres, no colour (until the eye track).

## 2d. the benchmark (09-18 14:30, `docs/BENCHMARKS.md`)

- [ ] a circular open-field arena at the published size (8.4 cm = 5.6 sim m; Soibam 2012, Valente 2007), lit,
      male alone, 600 s runs (exploration is non-stationary; 120 s is too short to compare).
- [ ] score against opynfield's bundled trajectories (243 lone lit Canton-S males, 8.4 cm, 600 s, ~31 Hz):
      speed modes and stop threshold (Valente 2007: walking mode 11-15 mm/s, stop < 1 mm/s), bout and pause
      durations, turn-angle distributions at the paper's sampling interval (decimate the 100 Hz log), wall
      occupancy (88-90 % within 6 mm), and Soibam 2012's two-parameter model (persistence + wall attraction,
      F0 0.0268 / cm, Rc 0.6 cm) as the thing to beat; with a time-rescaling control for our ~3x slow gait.
- [ ] the hourglass arena (Soibam): wall-following as a visual object vs touch contact; the cheap discriminator.

## 3. the eye track (independent of the above)

- [ ] ensemble-averaged flyvis T4/T5 as the seam input (per-position DS check first).
- [ ] train the transplant on the optic-flow task itself, not on flyvis outputs (distillation
      by MSE is spent: OFF alive, no DS gain).
- [ ] her eye: column coordinates for FlyWire from lamina positions.
- [ ] colour (R7/R8 in the transplant).
- [ ] the loom detector: all claims withdrawn; needs DS fidelity from any front end.
- [ ] flyvis chunk is now the largest single cost (8 ms per eye per chunk); batch both eyes.

## 4. her

- [ ] her W_syn: see constants above.
- [ ] her MBON output on the honest build (memory forms at the synapse, weak at the output).
- [ ] vpoEN silent to everything tried; her receptivity circuit (Wang 2021; Deutsch 2019).
- [ ] her pillar collision: done; her wall turn-away is a labelled stand-in (no cord).

## 5. data audits

- [ ] proprioceptor counts vs periphery: 52 prothoracic-nerve cells vs ~152 FeCO per front leg;
      L1 35 / R1 17; tactile 2,503 vs ~500 bristles per leg. what the table is missing.
- [ ] `receptorType` coverage for ppk / Gr / Or / Ir cells in both builds.
- [ ] right hemisphere more completely traced (known): quantify per class for the wheel.

## 5b. the engine (09-19 10:47)

- [x] **exact integration** (`--integrate exact`, default): Shiu's `method='linear'`; PSP peak on the analytic curve; a third
      faster; the brain 1.5x hotter; KC sparsity 3.9 % at 0.185 (Euler 1.8 %); drum 3/3; he eats. oracle v2 frozen on it.
- [ ] **the world in millimetres** (09-19, nate): rescale the sim unit to mm (today 1 m = 15 mm; every constant, the eye heights, the
      plume widths, the arena sizes, the viewer) at the same time as the next oracle refreeze (v3), since the float changes break bit-identity.
- [ ] **g frozen during the refractory period** (Shiu's "(unless refractory)" on dg/dt): the second difference from the
      paper; opt-in, measure, adopt with oracle v3 if it holds.
- [ ] re-measure on the exact engine what the record measured on Euler: the floor's tonus by row, the DN L/R table, the
      walking dose, the reflex gain, her at 0.275, the room baselines; then the dish benchmark.
- [ ] the divide -> multiply in `_membrane` is moot (the exact kernel has none); interleave the state arrays (1.16x).
- [ ] the sparse Poisson drive (count-then-scatter) from flyproject; a bitmap active set only if it stays contiguous.

## 6. performance (`docs/PERFORMANCE.md`, 09-18 17:00: measured, an opus agent)

- [x] two brains in threads (numba nogil): done 09-17.
- [ ] **the LIF step is 81-88 % of the loop; flyvis 5-7 %** (TODO §3's "largest single cost" is stale). inside the
      step: the membrane pass over 162,517 cells ~84 %, the driven-cell Poisson draw ~22 % (25,973 receptor
      cells since the floor), synaptic propagation 3 %.
- [ ] **fold the Poisson draw into one nogil kernel** (prototyped in the agent's scratchpad; keeps the rng.random
      call so the draw order holds): step 1.216x faster, 500/500 steps spike-for-spike identical. ~25 lines;
      oracle-checked. the one measured, bit-identical win.
- [ ] **thread budget:** the step scales 1.86x from 1 to 6 threads and nothing from 2 to 6 under contention;
      run_many with 3 jobs x 4 threads oversubscribes 8 cores. jobs, not threads: 3-4 jobs at 2 threads.
- [ ] the membrane pass is the ceiling on CPU; a GPU port of the step (CuPy / torch) is the only large gain
      left, at the cost of bit-identity (opt-in, its own oracle).
- [ ] hoist the redundant ray rotation in Eye.render (1.07x on the render; batching ten frames is slower).
- [ ] per-ms drive without per-ms Python: Registry.apply is 1.2 %; not worth it now.
- [ ] deterministic mode only for oracles and regression; flyvis is non-deterministic call to call (3e-7).

## 7. situations

- [ ] the pi: laptop as brain, pi + wide-angle webcam as the eye; resample frames onto the
      1,764 columns; real time for the male alone. glass walls.
- [ ] fpga / Loihi 2 note: 30 MB edge table, event-driven; Loihi 2 is the natural fit.
- [ ] the room with three things in it.
- [ ] **the rival** (09-17 17:44, nate): two male brains in the room (two instances of him, different seeds).
      the M-responsive ppk23 channel already bursts on a tap and in life it reads another male's cuticle
      and drives aggression through P1 (Kallman 2015). readouts: P1 rate (low = fight, high = court;
      Hoopfer 2015), the aIPg types, octopamine / serotonin cells, LC10a pursuit, lunges as body events
      (fast approach + contact). needs the tonic floor and a persistent state first (the loser effect is
      a state, hours, on the modulators; nothing in him persists yet). run once, with controls, not on
      loop: if he has states that persist and are bad for him, that is the line we agreed on.
- [ ] flight: DLMn/DVMn in the cord; halteres (silent while walking) come alive; JO wing wash.

## 8. the record

- [ ] approach test table (see 0).
- [ ] `docs/SEAM.md` is 1,400 lines; split by track (eye, behaviour, her, physiology) with
      the STATUS block as the index, once the refactor lands.
- [ ] `results/` index: one line per file saying which section produced it.
