# the minecraft fly: what connectome-fly 1.0.0 actually runs

audit 2026-09-19 (nyx), from the shipped jar
(`ref/flyproject/connectome-fly-1.0.0.jar`, 19 MB, CC BY 4.0, flyproject.io), decompiled with
CFR 0.152 into `ref/flyproject/src/`, data unpacked into `ref/flyproject/data/`. nate asked how
one CPU core carries "158,262 neurons and about 3.1 million synapses, stepped 1000 times a
second", and how accurate it is. one core is not the surprising part. what the core is stepping
is.

## the two engines

there are two, and the mod is honest about neither being the other.

**the whole brain** (`neural/WholeBrain.java`) is a float32 LIF over the full graph, one
`java.lang.Thread` per fly, daemon, priority 4, free-running against `System.nanoTime()` and
capped at `MAX_STEPS_PER_LOOP = 120` per wake. `maxBrains` is
`clamp(availableProcessors() / 2, 2, 16)`. only females get one: `if (this.whole == null &&
!this.isMale() && WholeBrain.running() < maxBrains)`. males never run a connectome at all.

**the reflex engine** (`neural/LifNetwork.java` + `EscapeCircuit`, `SteeringCircuit`) is a
double-precision LIF over two small hand-curated circuits, run on the server tick thread by
every fly, 100 steps of `dt = 0.5 ms` per game tick. `circuit.json` is 429 cells / 981 edges
(LPLC2 181, LPLC1 124, LC4 114 -> DNp01/02/11, PSI, TTMn). `steering_circuit.json` is 739 cells
/ 9,129 edges, mostly VNC interneurons and named leg muscles' motor neurons. these are proper
LIF: real `refracTimer`, signed weights, and one frank hack —

```java
private static double gapJunctionBoost(String preType, String postType) {
    if ("DNp01".equals(preType) && "TTMn".equals(postType)) return 50.0;
```

the escape jump and the flee turn come from this engine, not from the connectome.

## the whole-brain step

```java
for (int i = 0; i < n; ++i) {
    float ai, is;
    I[i] = is = I[i] * DECAY;          // DECAY = exp(-dt/tau_syn) = exp(-0.2)
    A[i] = ai = A[i] * ADECAY;         // ADECAY = exp(-0.004), tau 250 ms
    V[i] = V[i] + 0.05f * (is - ai - V[i]);     // K = dt/tau_m = 0.05
}
```

| | connectome-fly | ours (Shiu 2024 / `flysim.py`) |
|---|---|---|
| state per neuron | `v`, `isyn`, `a`, float32 (12 B) | `v`, `g`, `refrac`, float32 |
| tau_m / tau_syn / dt | 20 / 5 / 1 ms | 20 / 5 / 1 ms |
| threshold, reset | 1.0 (arbitrary), 0.0 | 7.0 mV, 0.0 |
| refractory | index ring of depth 2; `V[spiked] = 0` for 2 further steps | 2.2 ms timer, gates integration |
| voltage floor | none | `-v_thresh` |
| synaptic delay | **none**: a spike lands in `I` in the same step | 1.8 ms delay line |
| adaptation | `A += 0.4` per spike, tau 250 ms, subtracted from dv | none |
| noise | sparse: `nSens * 0.001` and `nDN * 0.004` random cells get `I += 10` | per-neuron gaussian |

weights are float32 CSR, sign strictly per source neuron (0 of 158,262 sources have mixed-sign
out-edges), so the sign convention is neurotransmitter-based; 34,074 sources (28.4%) are
inhibitory. the propagation is a per-spike scatter over out-edges with a two-value gain:

```java
float g = sensory[i] != 0 ? 8.8f : 2.2f;      // SYN_MULT 2.2, SENS_MULT 4.0
float gi = g * 1.1f;                          // INH_MULT
I[indices[q]] += (ww > 0.0f ? ww * g : ww * gi);
```

no delays, no short-term plasticity, no vector API, no fixed point, no event-driven skipping of
silent cells — both passes are dense loops over all 158,262 cells. the one learning rule is a
20-step-batched multiplicative depression of 4,085 KC->MBON synapses gated by PAM and PPL1.

## why one core is enough (and why it is generous)

harness: `ref/flyproject/bench/Harness.java` calls their real `WholeBrain.data()` loader and
their private `step()` through reflection, JDK 17 (the jar is class file 61; java 11 cannot load
it), `taskset -c 3`, load average 2.7 on 16 cores.

| bus | spikes/step | ms/step |
|---|---|---|
| silent (noise only) | 26-47 | 0.64-0.72 |
| a plausible awake set (11 channels, 0.1-0.5) | 272-280 | 0.51-0.60 |
| every channel at 1.0 | 1,193 | 0.90-0.98 |

so 1,000 steps/s costs 0.5-1.0 of a core, and their thread simply drops steps when it cannot
keep up (`Loco.stepsPerSec` reports the real rate). the arithmetic: the membrane pass streams
12 bytes read and 12 written per neuron, 3.8 MB/step, plus a second scan of `v`; that is the
whole cost. the 3.1 M-edge scatter is nearly free because almost nothing fires — 272 spikes x
19.75 mean out-degree = 5,400 random writes per step.

two details worth keeping. **the silent brain is slower than the awake one.** after 20,000
silent steps, 23,570 of 316,524 `v`/`isyn` entries are subnormal floats (`v` decays x0.95 per
step, `isyn` x0.819), and the x86 subnormal penalty costs more than the spikes saved. and
**1,000 Hz buys nothing behaviourally**: the game writes the sensory bus every 2 ticks (10 Hz)
and reads a `Loco` snapshot every 66 ms (15 Hz), then smooths it with alpha 0.35 and again with
alpha 0.04. the brain is sampled through a ~66 ms spike-count window.

## the number that decides the audit

at the awake operating point the drive injects, per millisecond: 16.6 random sensory kicks
(`16,557 x 0.001`), 5.3 random descending kicks (`1,316 x 0.004`), and `sum(len(chan) x 0.05 x
value)` = about 273 bus kicks. each kick is `I += 10`, worth `0.05 x 10 / (1 - 0.819) = 2.76`
thresholds — a guaranteed spike. total kicks ~295; measured spikes 272.

**the network contributes approximately zero spikes of its own.** cross-check from the graph:
272 spikes x 19.75 edges x mean |w| 0.0595 x gain, netted for the 35% inhibitory fraction,
delivers ~185 current units spread over 158,262 cells — a mean steady-state depolarisation of
0.65% of threshold. loop gain is far below 1. the connectome is loaded, indexed, and stepped,
and it is almost entirely inert; what you see is the injection pattern, filtered.

this is what the gains are for. only three of the seven entries in `brain_circuit_gains.json`
are applied at all (`if (gain == 1.0f) continue;`): `compass_loop` x2 on 4,569 edges,
`kc_mbon` x20 on 4,085 edges, `aggr_out` x25 on 41 edges. the credits name all three, plus the
x50 giant fiber. those four numbers are the circuits that do anything.

## senses in, behaviour out

39 channels in `brain_channels.json` (26,578 cell entries), every one driven by a hand-written
rule in `FlyMind.tick` over blocks and entities scanned within 8 blocks. a channel at value `v`
makes 5% x `v` of its cells fire per millisecond, i.e. 50 Hz x `v` per cell, flat — no receptor
model, no adaptation, no plume, no rest rate.

| channel group | cells | driven by |
|---|---|---|
| tactile | 7,188 | distance below a per-block contact radius |
| visual | 7,548 | proximity to a "visual" block kind |
| motion_prog/reg L/R | 4,343 | yaw rate x 0.25 plus the `OptomotorDrum` static |
| small_object L/R (LC11/LC10a) | 365 | angular speed of nearby entities' bearings |
| landmark L/R (LC15/LC17) | 439 | a 16-ray horizon raycast, twice per second |
| auditory | 1,188 | speaker blocks, and 0.25 flat when a suitor exists |
| olf_food / olf_fruit / olf_co2 | 1,746 | `prox` to food blocks, plus a wind-cone plume |
| taste (5 channels) | 535 | what block she is standing on or eating |
| pheromone, song, song_pc1 | 1,161 | other flies within range |
| heating/cooling/humid/dry/wind | 894 | lava, snow, water, fans, biome temperature |
| clock, light, sleep_pressure | 49 | time of day, a scripted pressure integrator |
| reward / punishment / nutrient | 310 | scripted event timers |

there is no rendering. no eye, no ommatidia, no image — "vision" is block proximity and entity
bearing-rate. compare `seam/omma.py` + flyvis.

the readout is 56 populations in `brain_outputs.json` (real, correctly labelled cell sets:
DNp01, MDN, oviDN, DNa01/02, PFL3, EPG, 281 PAM, leg MNs by segment and side). each is a spike
count over the 66 ms window compared with its own slow running baseline:

```java
private boolean active(WholeBrain brain, String name, float ratio, float floor) {
    float[] v = this.out(brain, name);
    return v != null && v[0] > Math.max(v[1] * ratio, floor);
}
```

locomotion does not use DNa02. it uses every descending neuron:

```java
new Loco(tot > 0L ? (float)(dnR - dnL) / (float)(tot + 8L) : 0.0f, (float)tot / (float)accSteps, ...)
```

`turnBias` is the left/right imbalance of all 1,316 DNs; `walkDrive` is their total rate. walk
vs rest is `walkDrive` z-scored against its own running mean and variance, thresholded at
`k = -0.65 + satiety`. yaw is `smTurn * 2.4` rad/s. since 5.3 of the ~4.4-9.4 DN spikes per
millisecond are the uniform random `DN_DRIVE_RATE` kick, **she walks and turns on the
`SplittableRandom`, shaped by a z-score.** the 651/665 left/right split in that uniform draw
even gives a constant rightward bias of about +0.01 in `turnBias`.

## emergent vs scripted

`FlyMind.tick` is a 1,160-line if/else-if priority chain. the mod labels its own speech
`[brain]` or `[model]`, which is more honesty than most. the split:

- **from the network, genuinely**: the sleep/wake switch (R5 channel rate vs l-LNv rate,
  a real ratio of two read populations), the compass bump (EPG spike-weighted circular mean,
  fed by a 0.15-amplitude cosine-tuned drive — the ring is driven, then read back), MBON
  approach-minus-avoid valence and its KC->MBON depression, pC1 receptivity gating
  `acceptMate`, and the threshold crossings that trigger jump, take-off, backward walking,
  proboscis extension, grooming and egg-laying.
- **scripted, with the network as a gate at most**: the flee turn and the jump (reflex engine),
  every navigation decision (`walkTo`, `homeReturning` on a 8 s / 12-20 s timer, excursions with
  a random yaw), foraging (block scan, `face()`, `drive()`), hazards, the lunge, and the
  saccade schedule.
- **not neural at all**: the entire male. `maleTick` is 40 lines — find the nearest female,
  face her, walk in, `setSinging(true)`. the label reads "P1 courtship decision (MaleCNS)" and
  "pIP10 -> song CPG -> 52 wing motor neurons". no male connectome data ships in the jar;
  `grep -rn MaleCNS` finds two string literals and nothing else. courtship does not emerge; it
  is a distance test. mating is one real thing: her pC1 rate gates acceptance.

## accuracy verdict

the wiring is real and the bookkeeping around it is careful. the numbers:

| | claimed | in the file |
|---|---|---|
| neurons | 158,262 | 158,262 (BANC v888 publishes ~188,000) |
| "synapses" | ~3.1 million | 3,126,254 **connections**, carrying 18,597,660 synapses (weights are exact multiples of 0.01, max 8.02 = 802) |
| vs BANC's ~199 M predicted synapses | — | ~9% retained |

so "3.1 million synapses" is the connection count; the loader itself prints
`nEdges + " synapses"`. 8,594 cells (5.4%) have no edges in either direction and are stepped
anyway.

what would make behaviour a product of tuning rather than wiring, ranked:

1. **the drive is the activity.** spikes ≈ injected kicks. nothing downstream of the receptors
   is carrying signal, so the graph's topology is close to irrelevant to the output.
2. **per-synapse strength is 0.62x ours and uniform.** their single-synapse EPSP integrates to
   `0.2758 x 0.01 x 2.2 = 0.0061` of threshold; Shiu at `w_syn = 0.275 mV` over 7 mV gives
   0.0098. a sensory presynapse gets x4 (`SENS_MULT`), so 2.5x ours. inhibition gets a flat
   x1.1. none of these three has a citation.
3. **no synaptic delay.** every loop in the brain closes within one 1 ms step. our 1.8 ms delay
   line is the reason our recurrent circuits have a timescale at all.
4. **spike-frequency adaptation that Shiu does not have** (`ADAPT_INC 0.4`, tau 250 ms),
   applied to every non-sensory cell, no source given.
5. **the readouts are self-calibrating ratio detectors.** `outBase` drifts at 0.02 per window
   toward whatever the population is doing, so every population is permanently near its own
   threshold and a x1.8-x12 excursion is the event. this manufactures events out of noise.
6. **the reflex engine's fudges**: `SENSORY_GAIN 8.0`, `SIZE_GAIN 3.2`, `SYN_GAIN 0.03`/`0.1`,
   `RIGHT_SIDE_BOOST 2.0` for right-side descending and VNC cells, and a per-neuron
   `NeuronJitter` that is `0.9 + 0.2 * (CRC32(id) % 1000) / 1000`.

the credits screen is better than the front page: it lists the x2/x20/x25/x50 boosts by name,
says "neuron time constants, thresholds and gains are ours", and under NEVER CLAIMED says "full
consciousness, real biological timing". the claim that does not survive the jar is the male
courtship circuit.

## what we should steal

**faster, no change to results:**

- **the sparse Poisson drive.** they draw `n x rate` indices and scatter, instead of drawing a
  uniform per driven cell. our Poisson tail is 0.89-1.07 ms of a 4.6 ms step over 25,973 driven
  cells (`docs/PERFORMANCE.md`); at our rates the count-then-scatter form is the same
  distribution with ~1/20 the RNG calls. this is a stronger version of PERFORMANCE.md item 1.
- **the refractory index ring instead of a per-neuron timer.** they keep two int arrays of
  spiked indices and re-zero `v`; we carry a float `refrac` per neuron through the membrane
  pass. PERFORMANCE.md already notes `v` and `g` are read by nothing in that pass and only
  `refrac` gates it — a depth-3 index ring removes one float stream from 5.9 MB/step.
- **one packed output mask.** `long[] neuronOutMask` gives each neuron a 64-bit set of the
  readout populations it belongs to, accumulated during the spike scan with
  `Long.numberOfTrailingZeros`. our readout counts are a separate pass per population.
- **flush subnormals.** their pathology is ours too: our `g` and `v` decay geometrically toward
  zero on the same schedule. numba honours `-ffast-math` only under `fastmath=True`, which we
  refuse for bit-identity, so the fix is an explicit `if abs(g[i]) < 1e-30: g[i] = 0.0` in
  `_membrane`. **this changes results** at the 1e-30 level; worth measuring before adopting.

**would change results, do not steal:** the two-value synaptic gain, `SENS_MULT`, the missing
delay line, the adaptation term, the self-calibrating readout baselines, and taking `turnBias`
from all descending neurons rather than DNa02 with a running per-side baseline.

**worth stealing as design**, not code: the `[brain]` / `[model]` label on every action. we have
the same boundary in `receptors.py` and `effectors.py` and no discipline for saying, per event,
which side produced it.

## what i could not determine

- whether `weight = synapse_count / 100` is exactly right. it fits (all 413 distinct magnitudes
  are multiples of 0.01) but no code reads the count back, and 18.6 M is only 9% of BANC's
  published ~199 M. that gap could be their threshold, or the published figure counting every
  predicted synaptic site rather than proofread neuron-to-neuron connections. i could not check
  against BANC directly.
- why the 3-synapse bin is anomalous: 822,775 edges at 3 synapses against 286,684 at 2. it looks
  like two sources merged, one thresholded at >= 3, but nothing in the jar says so.
- whether the whole brain ever really reaches 1,000 steps/s in a live server. the pacing loop
  decompiles with `lastWall = now` placed before `now - lastWall` is read, which would pin steps
  at zero; that is almost certainly a CFR reordering artifact of the loop condition, but i could
  not run the mod to confirm.
- what fraction of runtime the reflex engine costs on the server tick thread. `SteeringCircuit.drive(0.0)`
  runs 100 steps over 739 cells for every fly every tick, fleeing or not, and i benchmarked only
  the whole brain.
