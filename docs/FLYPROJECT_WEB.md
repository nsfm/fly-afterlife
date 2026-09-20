# the browser fly: what flyproject.io actually runs

audit 2026-09-19 (an opus agent for nyx), from the served code

nate's question: does the in-browser sandbox at https://flyproject.io/ suffer the same faults as
the Minecraft mod we audited this morning (`docs/MINECRAFT_FLYPROJECT.md`), and is there any lick
of truth in it we could learn from.

the short answer to the first half: **it is the same brain, the same data file, the same
constants, and a weaker script.** the connectome binary the browser downloads is bit-identical in
its statistics to the one unpacked from the jar. the worker that steps it is a line-for-line
JavaScript transliteration of `WholeBrain.java`. the source comments say so themselves, in the
third person: `brain_worker.js` refers to the mod twenty-one times as "the reference
implementation".

the answer to the second half is longer and it is at §5. there are three things here worth taking.

everything below is from files served to a visitor, saved under `ref/flyproject_web/`. the site is
not a bundle: the whole app is one unminified 2,572-line ES module inlined in `index.html`, plus a
separate worker. nothing needed un-minifying. where i ran their code, i ran it in node against the
file they serve, and i checked that port against the live page through a headless browser (§6 says
how far that check goes).

**licence: none.** no `LICENSE` at the root (404), no licence text in the page, no credits block,
no repository link. `robots.txt` is Cloudflare's content-signals boilerplate with **zero
directives** in it: no `User-agent`, no `Disallow`, no `Content-Signal` line
(`ref/flyproject_web/raw/` and the probe transcript). the jar carried CC BY 4.0. the web app
carries nothing. i fetched only what the page itself fetches, once.

---

## 1. what is actually loaded

### the connectome

`raw/brain_worker.js:77` fetches `assets/fullbrain.bin.gz`, 9,511,864 bytes on the wire, inflated
in the browser through `DecompressionStream('gzip')` to 25,959,620 bytes. the header is two
int32s and then four flat arrays (`brain_worker.js:83-90`):

```js
N = dv.getInt32(0, true); nEdges = dv.getInt32(4, true);
indptr  = new Int32Array(ab, off, N + 1);
indices = new Int32Array(ab, off, nEdges);
data    = new Float32Array(ab, off, nEdges);
sensory = new Uint8Array(ab, off, N);
dnclass = new Uint8Array(ab, off, N);
```

parsed (`bench/harness.mjs`, run1.out):

| | browser | minecraft jar |
|---|---|---|
| N | 158,262 | 158,262 |
| nEdges | 3,126,254 | 3,126,254 |
| implied synapses (sum \|w\|x100) | 18,597,660 | 18,597,660 |
| mean \|w\| | 0.059489 | 0.0595 |
| negative edges | 1,102,409 (35.26%) | 35% |
| inhibitory sources | 34,074 (21.53% of cells) | 34,074 (28.4% of sources) |
| sources with mixed sign | 0 | 0 |
| distinct \|w\| magnitudes | 413 | 413 |
| cells with no edges either way | 8,594 | 8,594 |
| mean out-degree | 19.754 | 19.75 |
| the anomalous 3-synapse bin | 822,775 at 3 vs 286,684 at 2 | same |

it is the same export. the CSR layout is different (the jar shipped its own format) but every
statistic matches, including the 3-synapse anomaly that the jar audit could not explain. i still
cannot explain it.

annotations: `sensory` marks 16,557 cells; `dnclass` marks 651 left and 665 right descending
neurons and nothing else. that 651/665 split matters and comes back in §4.

### the sensory and region tables

- `assets/brain_channels.json`, 146,420 bytes, **13 channels**, 20,019 cell entries
  (heating 6, cooling 41, humid 20, dry 35, gust_sugar 540, olf_food 1,655, olf_co2 91,
  tactile 7,188, auditory 1,188, aversive 226, pheromone 689, visual 7,548, wind 792).
  the jar had 39 channels and 26,578 entries. this is a **subset** of the mod's bus.
- `assets/brain_regions.json`, 1,066,037 bytes, 7 regions, 146,064 of 158,262 cells assigned:
  optic lobe 80,375, central brain 31,782, sensory 17,086, nerve cord 12,851, ascending 1,849,
  descending 1,316, motor 805. **the optic lobe is 50.8% of the simulated network.** §4 shows
  what it does.
- `assets/brain_dots.bin`, 1,424,812 bytes: soma positions for all 158,262 neurons, 146 colour
  groups, 157,478 (99.50%) with a drawable coordinate. visualisation only. this is the good part;
  see §5.

### the escape circuit

`circuit/escape.json`, 161,179 bytes, fetched on the main thread (`module_0.js:1207`): **429
nodes, 981 edges**, cell types LPLC2 181, LPLC1 124, LC4 114, DNp01 2, DNp02 2, DNp11 2, PSI 2,
TTMn 2; roles sensory 419, descending 6, motor 4. weights are raw synapse counts, 1 to 13, all
positive. this is exactly the jar's `circuit.json` (429 cells / 981 edges, same three LC
populations at the same counts).

### what is *not* loaded

the jar's second hand-curated circuit, `steering_circuit.json` (739 cells / 9,129 edges), is not
served: `circuit/steering.json`, `circuit/steering_circuit.json`, `assets/brain_outputs.json`,
`assets/brain_circuit_gains.json` all 404. `module_0.js` contains exactly one `fetch` for a
circuit. so there is no steering circuit, **no 56-population readout table, and no circuit-gain
table** in the browser. the jar's `kc_mbon` depression rule, its `compass_loop` x2 and its
`aggr_out` x25 do not exist here. the browser has one real circuit and one whole brain.

`catalog.json` nonetheless advertises `steering` with `roster.neurons = 739`, and `memory` with
4,964. neither number corresponds to anything that runs.

### the weight of it

first visit, uncompressed byte counts as served:

| file | bytes |
|---|---|
| assets/fly_rigged.glb | 23,269,956 |
| assets/predator.glb | 15,283,384 |
| assets/fullbrain.bin.gz | 9,511,864 |
| assets/brain_dots.bin | 1,424,812 |
| assets/brain_regions.json | 1,066,037 |
| assets/wall.glb | 439,348 |
| assets/cake.glb | 432,360 |
| index.html (app + all CSS + the 156 KB module) | 186,685 |
| circuit/escape.json | 161,179 |
| assets/brain_channels.json | 146,420 |
| assets/melon.glb | 51,404 |
| catalog.json | 13,525 |
| brain_worker.js | 13,405 |
| assets/escape_index.json | 11,709 |

the fly model alone is 2.4x the connectome.

---

## 2. the engine and its constants

`brain_worker.js:20-66`. every one of these is the jar's value:

```js
const TAU_M = 20, V_TH = 1, V_RESET = 0, T_REFRAC = 2, TAU_SYN = 5;
let DRIVE_RATE = 0.001; const DRIVE_AMP = 10;
let DN_DRIVE_RATE = 0.004;
let SYN_MULT = 2.2;
let ADAPT_INC = 0.4, ADAPT_TAU = 250, INH_MULT = 1.1, ADAPT_SENS = 0;
let SENS_MULT = 4.0;
const BUS_RATE = 0.05;
const DT = 1.0;
```

the step (`brain_worker.js:131-165`) is the jar's step with the loops fused:

```js
for (let i = 0; i < n; i++){ const isy = Isyn[i] * DECAY; Isyn[i] = isy;
  const a = A[i] * ad; A[i] = a; V[i] += K * (isy - a - V[i]); }
...
const G = sensory[i] ? SYN_MULT * SENS_MULT : SYN_MULT, GI = G * INH_MULT;
for (let q = s; q < e; q++){ const w = data[q]; Isyn[indices[q]] += w > 0 ? w * G : w * GI; }
```

so: no synaptic delay (a spike lands in `Isyn` in the same step), no voltage floor, no
short-term plasticity, no learning rule of any kind, spike-frequency adaptation that Shiu 2024
does not have, a refractory index ring of depth 2, and a flat x1.1 on every inhibitory synapse.
dense loops over all 158,262 cells twice per step, no event-driven skipping.

the derived quantities, exactly:

- one background kick (`Isyn += 10`) integrates to `(1/20) x 10 / (1 - exp(-0.2)) = 2.7583`
  thresholds. **a kick is a guaranteed spike.**
- one single-synapse connection (w = 0.01) from a non-sensory cell is worth `0.006068`
  thresholds, 0.61% of threshold. from a sensory cell, x4, `0.024273`.
- background kicks per step: `16,557 x 0.001 = 16.557` sensory plus `1,316 x 0.004 = 5.264`
  descending, **21.821 in total**, before any stimulus.

the tuning knobs are all live-adjustable from the browser console (`module_0.js:1237-1241`:
`window.__tuneBrain`, `__synGain`, `__bgDrive`, `__tune`) which is, to be fair, more honest
exposure than most projects manage. it also means every constant is admitted to be a dial.

---

## 3. how the world reaches the neurons, and how behaviour leaves them

### in

`module_0.js:1375-1394` is the whole sensory model. eighteen prop types, each a dict:

```js
lava:     {effect:'repel',  range:5.5, gain:1.6, contact:1.4, flee:true,
           ch:'Gr28a thermosensors (heat)', act:'recoils from the heat'},
cake:     {effect:'attract',range:9.0, gain:1.3, contact:0.8, consume:true, eat:2.0,
           ch:'Gr5a sweet + ORNs (odor)', act:'feeds'},
```

each frame (`module_0.js:1914-1933`) a prop's distance becomes `prox = max(0, 1 - d / info.range)`
and that scalar is written into one bus channel:

```js
if (p.type === 'lava') bus.heating = Math.max(bus.heating, d < 1.5 ? 1 : prox);
else if (p.type === 'predator') bus.olf_co2 = Math.max(bus.olf_co2, prox);
else if (p.type === 'cake' || p.type === 'melon') bus.olf_food = Math.min(1, bus.olf_food + prox * 0.7);
```

the bus is posted to the worker at 10 Hz (`module_0.js:1970`: `busPostT = 0.1`), and there each
channel at value `v` makes `5% x v` of its cells fire per millisecond
(`brain_worker.js:142-147`), flat: no receptor model, no adaptation, no plume, no Weber-Fechner,
no resting rate, no bilateral difference. **there is no eye.** "visual" is proximity to a lamp.
"auditory" is proximity to a speaker. compare `docs/SENSES.md` and `seam/omma.py`.

the loom disc is the one exception and it is genuinely different. `module_0.js:1745-1751` grows
the disc at constant *angular* rate, computes subtended angle `theta = 2*atan(radius/dist)` and
its time derivative, and feeds those two signals into the escape network as separate
angular-velocity and angular-size channels. that is a real transduction with the right variable.

### out

one readout, posted every 66 ms (`brain_worker.js:188-193`):

```js
turnBias: tot > 0 ? (dnR - dnL) / (tot + 8) : 0,
walkDrive: tot / accSteps,
```

`dnL`/`dnR` are the spike counts of **all 651 left and all 665 right descending neurons**. not
DNa02, not a named population; the whole descending bundle. the worker comment cites Rayshubskiy
2024 on DNa02 asymmetry as its justification for a readout that does not use DNa02.

that is consumed in exactly one place in the entire app (`module_0.js:2036-2041`):

```js
smTurn += (loco.turnBias - smTurn) * Math.min(1, dt * 1.6);
u.tgtYaw += smTurn * BRAIN_TURN * dt;              // BRAIN_TURN = 6.5
let sp = Math.min(BRAIN_SPEED_CAP, Math.max(0, loco.walkDrive * BRAIN_WALK));   // 0.5, cap 3.0
```

and `escapeNet` produces one more readout: `ttmn > 0` triggers `flyJump` (`module_0.js:1786-1789`).

**that is all.** two neural readouts in the whole application: a turn/walk pair used only when
nothing is happening, and a jump trigger used only for the loom disc.

### the arbitration chain

`module_0.js:1993-2050` is a ten-branch `if / else if` priority chain. in order:

| # | branch | condition | driven by |
|---|---|---|---|
| 1 | flee | `flee && domRepel` | geometry: face away from the repeller |
| 2 | sleep | `night` | a button, `setDayNight` |
| 3 | lunge at rival | `rivalD < 2.8` | geometry |
| 4 | path integration | `homeReturn` | a timer: `homeT`, 5 s out / 12-20 s back |
| 5 | shelter | `roof` | geometry |
| 6 | wait out rain | `rainOn && sheltered` | geometry |
| 7 | feed | `feed` | geometry + a health counter |
| 8 | approach / avoid | `senseMag > 0.12` | geometry: summed `1/(1+d^2/6)` gradients |
| 9 | anemotaxis | `fanUp` | geometry: a cone test |
| 10 | **roam** | `loco` | **the connectome** |

the brain is the fallback. every labelled behaviour on the site is a branch above it. the labels
are confident: branch 4 says `'heading home — path integration (ellipsoid-body compass)'` while
being a `setTimeout`; branch 3 says `'lunges at the rival — aggression (pC1 / tachykinin)'` while
being `atan2`.

---

## 4. the puppet test

method: their worker's `step()` ported verbatim into node (`bench/harness.mjs`,
`bench/harness2.mjs`), run against the served `fullbrain.bin.gz`, seeded RNG, 300 windows of 66
steps after 30 windows of warm-up, identical seed across conditions. the port was validated
against the live page: their own `window.__escTest(0)` returns `totalTtmn: 190, firstJumpDist:
1.27` in the browser and my port returns `TTMn 190, firstJump d=1.27`; the live page's resting
region rates match the port's within the sampling noise (`probe/live_probe2.out`).

### 4a. the roam, with all 3,126,254 synapses set to zero

`bench/run2.out`:

| condition | turn mean | turn SD | turn p5 | turn p95 | walkDrive | speed |
|---|---|---|---|---|---|---|
| rest, synapses **ON** | 0.0095 | 0.0580 | -0.0867 | 0.1095 | 4.429 | 2.215 |
| rest, synapses **OFF** | 0.0097 | 0.0580 | -0.0879 | 0.1053 | 4.335 | 2.168 |

the turn distribution is identical to three decimal places. walkDrive differs by 2.1%, which at
`BRAIN_WALK = 0.5` under a cap of 3.0 is a speed difference of 0.047 units/s. **delete the entire
connectome and her roaming is the same roaming.**

### 4b. where the descending drive comes from

| condition | walkDrive | speed |
|---|---|---|
| rest, synapses ON, DN kick ON | 4.429 | 2.215 |
| rest, synapses ON, **DN kick OFF** | 0.080 | 0.040 |
| rest, synapses OFF, DN kick OFF | 0.000 | 0.000 |
| rest, synapses ON, **sensory background OFF** | 4.338 | 2.169 |

**98.2% of the descending drive is `DN_DRIVE_RATE`, a uniform random draw over 1,316 neurons.**
turn off the background noise into the 16,557 sensory cells and locomotion changes by 2.1%. turn
off the noise into the descending cells and she stops. she walks on `Math.random()`.

and the constant rightward drift is arithmetic, not biology. the draw is uniform over 1,316
descending neurons of which 665 are right and 651 are left, so the expected window imbalance is
`5.264 x 66 x 14 / 1316 = 3.695` spikes against `tot + 8 = 301`, i.e. a turnBias of **+0.01228**
forever. measured +0.0095 over 300 windows. at `BRAIN_TURN = 6.5` that is **0.0617 rad/s, 3.54
degrees per second of permanent rightward yaw**, produced by the annotation being 14 cells
lopsided.

### 4c. does the stimulus bus ever reach the readout

| condition | spikes/step | walkDrive | turn SD |
|---|---|---|---|
| all 13 channels at 1.0, synapses ON | 1026.32 | 8.805 | |
| all 13 channels at 1.0, synapses OFF | 861.44 | 4.322 | |
| pheromone 1.0, ON | 86.63 | 4.530 | |
| pheromone 1.0, OFF | 56.36 | 4.341 | |
| weak bus 0.1 on all channels, ON | 4.750 | 4.750 | 0.0545 |
| weak bus 0.1 on all channels, OFF | 4.327 | 4.327 | 0.0555 |

at full drive on every channel at once the network does double the descending rate. that is real
propagation. **but it never happens**, because the bus only goes above ~0.1 when a prop is close,
and when a prop is close, branch 1-9 has already taken the wheel and `loco` is not read.

exactly: for the lamp (`light`, range 13, gain 1.1) branch 8 fires at `senseMag > 0.12`, i.e. at
`d = 7.00`, where `bus.visual = 1 - 7/13 = 0.462`. so a lamp between 7.00 and 13.0 units away
drives the visual channel while `loco` still steers; nearer than 7.00 and the script takes over.
in that overlapping shell the whole 3.1-million-synapse network buys a walkDrive change of
+9.8% and a turn-SD change of -1.8%. for the cake the crossover is `d = 7.68` with
`bus.olf_food = 0.103`.

she is a puppet in the strict sense: **every visible behaviour survives silencing every neuron it
claims to read**, except one.

### 4d. the exception: the jump

`bench/run3.out`, their `EscapeNet` ported verbatim, front-on loom at bearing 0:

| lesion | LPLC1 | LC4 | LPLC2 | DNp01 | DNp11 | DNp02 | TTMn |
|---|---|---|---|---|---|---|---|
| intact | 23,530 | 22,150 | 11,422 | 162 | 300 | 23 | **190** |
| synaptic gain x0 | 23,480 | 21,727 | 10,980 | 0 | 0 | 0 | **0** |
| gap-junction boost 50 -> 1 | 23,530 | 22,150 | 11,422 | 162 | 300 | 23 | **0** |

zero the 981 edges and TTMn never fires: the jump is genuinely a product of the wiring. **this is
the one behaviour on the site that passes the puppet test.**

the caveat is the second row. the jump depends entirely on a hand-inserted x50 multiplier on one
edge type (`module_0.js:1156`):

```js
const boost = (this.cellType[i]==='DNp01' && this.cellType[j]==='TTMn') ? 50.0 : 1.0;  // GAP_JUNCTION_BOOST
```

with DNp01 firing its full 162 spikes, TTMn fires 0 without it. the giant-fibre synapse is
electrical in life so a boost is defensible in principle; the number 50 has no source anywhere in
the served code. PSI is in the circuit and fires 0 spikes in every condition i ran.

the second caveat is the blind spot. the code comment (`module_0.js:1114-1116`) says:

> The rear blind spot is REAL: a stimulus behind the fly gets visual_field_gain 0, so the sensory
> neurons receive no current, never spike, and TTMn never fires. The blind spot emerges from the
> neurons — there is no "if behind: don't jump".

there is, however, an `if behind: drive = 0`, thirty lines above (`module_0.js:1138-1146`):

```js
if (b <= 140) return 1.0;
if (b >= 165) return 0.0;
return (165 - b) / 25;
```

measured sweep (`run3.out`): bearings 0 through 140 all give **identical** TTMn 190 and identical
first-jump distance 1.27; 150 gives 65, 155 gives 14, 160 and beyond give 0. the receptive-field
structure is a piecewise-linear function of bearing applied to the input current, not anything the
429 neurons compute. the flat 0-to-140 plateau is the giveaway: 114 LC4 and 124 LPLC1 cells with
real left/right `side` labels, and the model gives them one shared scalar. and the *threshold*
for jumping is a dial: `SIZE_GAIN` 0.6 -> 1.2 -> 2.4 moves the jump from theta 77.5 deg to 50.7
deg to 27.5 deg.

### 4e. what the whole brain actually does while it is not being read

the live page, arena empty, sampled every 3 s (`probe/live_probe2.out`), spikes per step by
region:

| region | cells | typical | during a burst |
|---|---|---|---|
| sensory | 17,086 | 16.5-17.2 | 17.2 |
| descending | 1,316 | 4.28-4.93 | 4.93 |
| central brain | 31,782 | **0.13-0.62** | 11.4 / 58.6 / 64.9 / 85.1 / 88.1 |
| nerve cord | 12,851 | 0.10-0.35 | 0.64 |
| ascending | 1,849 | 0.04-0.11 | 0.22 |
| motor | 805 | 0.00-0.05 | 0.09 |
| **optic lobe** | **80,375** | **0.000** | 0.017 |

two things fall out of this.

**the optic lobe, 50.8% of the network, is silent.** not nearly silent: 0.000 spikes per step in
8 of 10 sampled windows, 0.017 in the other two. half the simulated brain is stepped 1000 times a
second and never fires, because nothing drives it (the `visual` channel's 7,548 cells are counted
in `sensory`) and no recurrent activity reaches it.

**the central brain is bistable.** the median window is 0.32 spikes/step across 31,782 cells and
about one window in five ignites to 10-90 spikes/step. the bursts co-occur with the 41-cell
`cooling` population jumping from 0.01-0.1 to 0.6-1.09 spikes/step; `cooling` is annotated
sensory, so it collects the x4 `SENS_MULT`, and the loop re-ignites through it. that is an
artefact of the gain structure, not a feature. and it changes nothing: walkDrive during the
biggest burst (88.1 central spikes/step) was 4.858 against a resting 4.36. **the avalanche does
not reach the descending readout.**

the same sample shows something the live brain panel is designed to hide: with the arena
completely empty, `chanSpikes` reports tactile 6.78, visual 1.95, olf_food 1.52, auditory 1.18,
pheromone 0.79, gust_sugar 0.61 spikes/step. every sense is firing all the time from the
background noise. `applyBrainSpikes` (`module_0.js:2192-2207`) subtracts each neuron's own learned
resting rate before lighting its dot, so the panel shows a shimmer instead of a lie. the
normalisation is doing a lot of work.

### 4f. the realtime budget

- nominal: `DT = 1.0`, i.e. 1,000 steps/s, capped at 120 steps per wake
  (`brain_worker.js:174`).
- measured on the live page, headless Chrome 144 with software GL on this machine:
  `stepsPerSec` of 179.0, 196.4, 204.2, 216.9, 226.6, 272.4, 284.4, 298.8, 317.8, 329.1, 346.3,
  350.9, 396.3, 405.1, 412.2, 416.5, 447.8. **mean 294.2 over the ten resting samples.**
- my node port of the same step: **1.19 ms/step** at rest, 1.62 ms/step with all 13 channels at
  1.0 (run1.out), i.e. an 840 steps/s ceiling on one core of this laptop.

pure scalar JS. no WASM, no SIMD, no WebGPU, no GPU compute anywhere; the only GPU work is
three.js drawing the fly. the brain never reaches its nominal rate and simply drops steps. this
does not change the decode, because `walkDrive = tot / accSteps` is per step, not per second. the
fly does not slow down; her brain does, silently.

---

## 5. licks of truth

four, and one of them is genuinely good.

**1. the live-brain panel.** `module_0.js:2149-2245` plus `assets/brain_dots.bin`. every one of
the 158,262 simulated neurons drawn at its real curated soma position in the frontal plane, 146
functional colour groups, and **dot `i` is neuron `i` of the simulation**. the worker sends one
`Uint8Array(N)` per 66 ms window and transfers the buffer rather than copying it
(`brain_worker.js:187, 193`: `spiked = sampleSpiked.slice(); ... postMessage(..., [spiked.buffer])`).
the resting silhouette is painted once to an offscreen canvas (`paintRestLayer`, `module_0.js:2220`)
and each frame only the dots that fired are redrawn as 2-px rects. and the "what's different from
rest" normalisation (`module_0.js:2192-2207`) tracks a fast rate and a per-neuron resting baseline
learned only while nothing is placed, then shows `(rate - base) / (1 - base + 0.05)`. that is a
real, honest, cheap whole-brain raster and it is the best thing on the site.

*transfers to us:* directly. our viewer (`world/replay_app.py`) shows "the neurons that matter";
this is the argument for a whole-population panel instead. the three tricks that make it cheap are
all portable: one byte per neuron per readout window, a painted-once resting layer, and the
per-neuron baseline subtraction so the tonic floor does not wash out the picture. the last one is
the one we need most, because *our* floor holds every typed sense at its resting rate by design
(`docs/SENSES.md`), so a raw raster of ours is mostly floor.

**2. the loom transduction.** `module_0.js:1745-1751`. the disc grows at constant angular rate
(`LOOM_EXPAND * dist * dt`, so near and far drops both loom in ~1.5 s), and the network is fed two
separated channels: `rateSig = dtheta/dt` into LC4 + LPLC1, `sizeSig = theta` into LPLC2, with
LPLC2 gated off below a motion threshold (`sizeSig = rateSig > MOTION_EPS ? theta * gain : 0`).
that is the right physical variable, split the right way for the two LC classes, and it is the
only sense in the app with a time derivative in it.

*transfers to us:* yes, and `docs/SENSES.md` says we need it ("the eye cannot yet see a loom"). we
have a raytraced eye, so we can get theta and dtheta/dt from the rendered image rather than from
prop geometry, which is strictly better. the thing to steal is the two-channel split with the
expansion gate on the size channel, and the `theta`/`dtheta` pair as the drive to LPLC2 versus
LC4/LPLC1.

**3. gzip + `DecompressionStream` for the graph.** `brain_worker.js:76-82`: 9,511,864 bytes on
the wire become 25,959,620 in memory, inflated by the browser, with a plain-file fallback for
browsers without the API. a 2.73x saving for four lines of code, lossless, and the CSR arrays are
then created as views into the one `ArrayBuffer` with no copy.

*transfers to us:* marginally. our `.npz` is already compressed. the part that transfers is the
zero-copy view discipline, and the reminder that an int32/int32/float32 CSR plus two uint8
annotation arrays is all a whole-brain LIF needs on the wire.

**4. the count-then-scatter Poisson drive**, which is the same thing `docs/MINECRAFT_FLYPROJECT.md`
already flagged and which appears here in a tighter form (`brain_worker.js:137`):

```js
let nk = sensIdx.length * DRIVE_RATE; nk = (nk | 0) + (Math.random() < (nk - (nk | 0)) ? 1 : 0);
```

the fractional part carried as a Bernoulli trial, so the expectation is exact without a per-cell
draw. our Poisson tail is 0.89-1.07 ms of a 4.6 ms step over 25,973 driven cells
(`docs/PERFORMANCE.md`). this is a second, independent sighting of the same trick; it should move
up the list.

**and one that is not a lick of truth but is worth naming as design:** every behaviour string
carries the population it claims (`'lunges at the rival — aggression (pC1 / tachykinin)'`), and
`PROP_INFO` carries a receptor name per stimulus (`'Gr28a thermosensors (heat)'`,
`'ppk28 water receptors (thirst)'`, `'Or56a — geosmin (innate aversion)'`). the receptor
attributions are correct. the trouble is that the label is attached to a branch of geometry, so
the app reads as a claim that pC1 produced the lunge when pC1 was not consulted. the jar's
`[brain]` / `[model]` prefix, which we said we should steal, is **absent here**. that is a
regression from the mod, and it is the single change that would most improve the site.

**what not to steal:** all of it. the two-value synaptic gain, `SENS_MULT`, the missing delay
line, the adaptation term, the flat x1.1 inhibition, the x50 gap-junction boost, `visualFieldGain`
as a stand-in for a receptive field, `turnBias` from all 1,316 descending neurons, and
`BRAIN_TURN`/`BRAIN_WALK`/`BRAIN_SPEED_CAP` as free output gains.

**and one thing to actively avoid.** the `memory` circuit (catalog: 4,964 neurons) has no
scenario and falls through to the legacy demo engine (`module_0.js:673-677`):

```js
} else if (K === 'maze'){
  st.data = {trial: (st.data.trial||0)+1};
  const learned = st.data.trial > 3;
  say('trial ' + st.data.trial + (learned ? ' — it knows the way' : ' — trying...'));
  st.data.right = learned || Math.random()<0.35;
```

and on arrival (`module_0.js:759`) it says `'reward — synapses updated'`. no synapse is updated;
there is no mushroom body in the browser at all. this is the only outright false statement i found
in the served code, and it is worse than anything in the jar, which did ship a real KC->MBON
depression rule. the `#neurons` overlay has the same problem in milder form: "roster from real
data" (`module_0.js:813`) uses real *counts*, but the dot positions come from a sine hash
(`function hh(s){ let v=Math.sin(s*127.1)*43758.5; ...}`, `module_0.js:819`) and the glow is
`Math.random() < p*dt`. two visualisations, one real (the live brain panel) and one invented, in
the same app, both labelled as neurons.

---

## 6. the comparison

| | flyproject.io (browser) | connectome-fly 1.0.0 (Minecraft) | fly-afterlife (ours) |
|---|---|---|---|
| connectome | BANC v888 female, 158,262 cells / 3,126,254 connections / 18,597,660 synapses | identical file | MaleCNS v1.0, 162,517 cells, ~6 M synapses; FlyWire v783 for her |
| engine | scalar JS in one Web Worker | Java float32, one thread per fly | numba-compiled, exact linear membrane |
| dt / tau_m / tau_syn | 1 / 20 / 5 ms | 1 / 20 / 5 ms | 1 / 20 / 5 ms (Shiu 2024) |
| threshold | 1.0 arbitrary | 1.0 arbitrary | 7.0 mV |
| synaptic delay | none | none | 1.8 ms delay line |
| adaptation | `ADAPT_INC 0.4`, tau 250 ms, no source | same | none (Shiu has none) |
| synaptic gain | `SYN_MULT 2.2`, `SENS_MULT 4.0`, `INH_MULT 1.1`, no sources | same | `w_syn` 0.185/0.275 mV, cited |
| learning | **none** | KC->MBON depression, 4,085 synapses | none |
| hand-curated circuits | 1 (escape, 429/981) | 2 (escape 429/981, steering 739/9,129) | none; the whole graph, plus labelled opt-in corrections (`wiring.py`) |
| circuit gain fudges | x50 DNp01->TTMn | x2, x20, x25, x50 | none; stand-ins labelled with a flag and a source |
| sensory channels | 13, 20,019 cells | 39, 26,578 cells | 21 typed senses, tonic floor on all, 9 world-driven |
| vision | proximity to a lamp prop | proximity to a "visual" block | raytraced compound eye on measured geometry -> flyvis -> his own T4/T5 |
| smell | `1 - d/range`, one scalar, both antennae | `prox` + a wind cone | plume field sampled at two antennae 0.35 mm apart |
| loom | theta and dtheta/dt into LC4/LPLC1 and LPLC2 | none | not yet (TODO §S) |
| readouts | 2: descending L/R, and TTMn | 56 populations with self-calibrating baselines | leg MNs, HS cells, DNg100/DNg105, P1, feeding state |
| readout baselines | none | running mean, drifts 0.02/window | fixed, from the run |
| locomotion source | 98.2% `DN_DRIVE_RATE` random kicks | same drive, same decode | leg motor neurons against standing tonus |
| the male | **not simulated**: 12 lines of geometry | not simulated: 40-line state machine | the model *is* male (MaleCNS); she is the second fly |
| measured rate | 294 steps/s (browser), 840/s (node, 1 core) | 1,000-2,000 steps/s on 0.5-1.0 core | ~4x realtime on a laptop |
| labels brain vs script | no | yes: `[brain]` / `[model]` | `receptors.py` / `effectors.py` boundary, no per-event label |
| licence | **none served** | CC BY 4.0 | MIT |

### the male question

worse than the jar. `makeMaleFly` (`module_0.js:1628-1638`) is *her rig, tinted darker and scaled
0.85*. his behaviour is twelve lines (`module_0.js:1810-1824`): face her, walk in at 1.7 units/s,
push off other males, `b.flapBoost = 0.5`, emit a ring every ~0.5 s, and on contact say
`'courtship — his wing song (pheromone)'`. no male connectome is served (`assets/malecns.bin`
404). `catalog.json` lists `courtship` as `specimen: "dual"` with `roster: 295` male neurons and
`roster2: 85` female, and the panel prints "Two brains: a male courtship circuit and a female BANC
brain" (`module_0.js:925`). those 295 neurons exist only as a *count* passed to `makeCloud`, which
draws sine-hashed dots. there are not two brains. there is one brain and a recoloured copy of the
female model.

her side has one thing the mod had and this does not: the jar gated `acceptMate` on a real pC1
rate. here nothing gates anything; the male arrives and the string is printed.

---

## 7. what i could not determine

- **whether the connectome file is byte-identical to the jar's**, as opposed to statistically
  identical. the two use different container formats, so i compared N, nEdges, the weight
  histogram, the sign structure, the degree distribution and the isolated-cell count, and all nine
  match exactly. i did not re-extract the jar's arrays to diff them element by element.
- **the 3-synapse anomaly**, again: 822,775 edges at 3 synapses against 286,684 at 2. the same
  discontinuity the jar audit found, in the same file, still unexplained by anything served.
- **whether 18,597,660 is 9% of BANC's ~199 M or whether the published figure counts something
  else.** unchanged from the jar audit; i could not check against BANC directly.
- **the real step rate on a machine with a GPU.** my 294 steps/s is headless Chrome with
  swiftshader, where the render thread competes badly. the worker is a separate thread and my node
  port of the same code costs 1.19 ms/step, so the true browser figure is somewhere in 294-840 and
  i would not report a single number. either way it is below the nominal 1,000.
- **how often a visitor actually lands in the `loco` branch.** it depends on how many props are
  placed and where, which is the user's doing. i established the geometry of the overlap shell
  (7.00 to 13.0 units for a lamp) but not a distribution over real sessions.
- **whether `catalog.json`'s `whole_brain: 158528` and `annotated: 24102` correspond to anything.**
  the loaded N is 158,262, a difference of 266, and the channel file holds 20,019 entries. both
  front-page numbers are larger than the files. i could not find their source.
- **what the 146 colour groups in `brain_dots.bin` are.** they are clearly functional labels from
  the BANC metadata table and the largest is 26,666 cells, but the file ships colours without
  names and no legend is served.
- **whether the escape circuit's `side` annotation is used for anything.** every node carries
  `side: 'left'|'right'` and `visualFieldGain` returns one scalar for both, so as far as i can
  tell the labels are carried and ignored. i could not find a code path that reads `node.side`.

---

## in one paragraph

flyproject.io serves the *same* BANC connectome file as the Minecraft mod (158,262 neurons,
3,126,254 connections, 18,597,660 synapses, identical to nine statistics), stepped by a Web Worker
that is a line-for-line JavaScript port of the mod's `WholeBrain.java` with every constant
unchanged, and it inherits every fault we found there plus two new ones. the fatal number is this:
with **all 3,126,254 synapses set to zero**, her roaming is statistically indistinguishable from
the intact brain (turn SD 0.0580 both, walkDrive 4.429 against 4.335, a 2.1% difference), because
**98.2% of the descending drive is a uniform random kick into 1,316 neurons** and the 14-cell
left/right imbalance in that draw is the entire source of her 3.54 deg/s rightward yaw. and the
brain only steers her at all in the tenth and last branch of a ten-branch `if / else if` chain:
fleeing, feeding, aggression, "path integration", shelter and anemotaxis are all `atan2` on prop
coordinates, each wearing a correct receptor name it never consulted, with the jar's honest
`[brain]` / `[model]` prefix dropped. half the simulated network, the 80,375-cell optic lobe,
fires 0.000 spikes per step because nothing drives it; the central brain sits at 0.32 spikes/step
across 31,782 cells and occasionally avalanches to 88 without moving the readout; and the "memory"
circuit prints "reward — synapses updated" from a trial counter with no mushroom body loaded at
all. the male is a recoloured copy of the female mesh with twelve lines of chase logic, advertised
as a second connectome. **one thing survives the test**: the 429-neuron / 981-edge escape circuit
genuinely computes its jump, TTMn going from 190 spikes to 0 when the edges are zeroed, though it
also goes to 0 when a hand-inserted x50 giant-fibre multiplier is removed and its "emergent" rear
blind spot is a piecewise-linear function of bearing applied to the input current. what is worth
taking is not the neuroscience but the craft: the live-brain panel is a real whole-population
raster at true soma positions with one byte per neuron per window, a painted-once resting layer
and a per-neuron baseline subtraction, and it is better than what our viewer does today; the loom
transduction feeds theta and dtheta/dt to LPLC2 and LC4/LPLC1 as separate gated channels, which is
the right shape for the loom sense `docs/SENSES.md` says we lack; and the count-then-scatter
Poisson drive shows up again, which settles it. no licence is served with any of it.

---

## files saved under `ref/flyproject_web/`

`raw/` (as served, 2026-09-19, 12,692,355 bytes total)

| file | bytes | note |
|---|---|---|
| `index.html` | 186,685 | the whole app |
| `module_0.js` | 156,194 | the inline ES module, extracted, 2,572 lines, unminified as served |
| `headers_root.txt` | 525 | response headers for `/` |
| `brain_worker.js` | 13,405 | the whole-brain LIF |
| `catalog.json` | 13,525 | the 23 circuit entries |
| `circuit_escape.json` | 161,179 | `circuit/escape.json`, 429 nodes / 981 edges |
| `assets_escape_index.json` | 11,709 | escape-neuron -> dot index |
| `assets_fullbrain.bin.gz` | 9,511,864 | the connectome, inflates to 25,959,620 |
| `assets_brain_channels.json` | 146,420 | 13 channels, 20,019 cells |
| `assets_brain_regions.json` | 1,066,037 | 7 regions, 146,064 cells |
| `assets_brain_dots.bin` | 1,424,812 | 158,262 somas, 146 colour groups |

(the five `.glb` models, 39,476,452 bytes together, were size-probed with a `Range` request and
not downloaded.)

`bench/` (my node port of their code and its output)

| file | note |
|---|---|
| `harness.mjs` | `brain_worker.js` `step()` ported verbatim, seeded RNG, region accounting |
| `harness2.mjs` | the same, reporting per-66-step-window `turnBias` / `walkDrive` distributions |
| `escape.mjs` | `EscapeNet` + `visualFieldGain` + `__escTest` ported verbatim, lesionable |
| `run1.mjs`, `run1.out` | §4c: 8 bus conditions, spikes/step, region table, ms/step |
| `run2.mjs`, `run2.out` | §4a/4b: the silencing experiment, 300 windows per condition |
| `run3.mjs`, `run3.out` | §4d: bearing sweep, stage lesions, input-gain sensitivity |

`probe/` (the live page, headless Chrome 144.0.7559.132, stopped by its own PID)

| file | note |
|---|---|
| `README.txt` | how the probe was run |
| `cdp_probe1.py`, `live_probe1.out` | first contact; `__escTest(0)`=190/1.27 validated the port |
| `cdp_probe2.py`, `live_probe2.out` | the ten resting `window.__loco` samples: stepsPerSec, per-region spikes/step, `chanSpikes` with the arena empty |
