# two open minecraft connectome mods, read and run

audit, 2026-09-19 (nyx), from nate's question about how the two open-source minecraft fly mods get
their speed and how accurate they are. both cores turn out to be pure-java packages with no minecraft
imports, so i compiled each standalone (jdk 26 `javac --release 21`) and ran their own benches
headless here at two threads. numbers marked **measured** are mine, on this box; *reported* ones are
theirs.

## what each engine is

**(a) blendi-remade/fly-brain-minecraft** (fabric 1.21.1, MIT) runs MaleCNS v1.0: 176,422 neurons,
6,287,749 connections at >= 5 synapses carrying 90.3 M of the dataset's 125 M, in a 23 MB gzip `FLYB`
file that loads in 0.3 s into CSR arrays with 16-bit counts. one `LifNetwork` per fly on its own
daemon thread, 50 ms of brain per game tick.

**(b) AshtonLong/fruitfly-brain-mod** runs FlyWire FAFB v783 exactly as shiu distributes it: 138,639
neurons, 15,091,983 directed rows, unpruned, weights taken straight from the
`Excitatory x Connectivity` column and multiplied by `.275f` at load. one static single-thread
executor for the whole mod, queue 24, `AbortPolicy` — requests are dropped when it saturates.

## the neuron model

(a) is the closest thing to shiu-in-java i have read. `LifConfig` ships tau_m 20, tau_syn 5,
v_rest = v_reset -52, threshold -45, refractory 2.2, delay 1.8, 0.275 mV per synapse — and the
integrator is the **exact** linear solution, not euler:

```java
this.synDecay = (float) Math.exp(-dt / tau);
if (Math.abs(tm - tau) < 1e-9) this.synCoupling = (float) ((dt / tm) * Math.exp(-dt / tm));
else this.synCoupling = (float) ((tau / (tm - tau)) * (Math.exp(-dt / tm) - Math.exp(-dt / tau)));
```

that matches shiu's brian2 `method='linear'`, and it is why they can run dt = 0.5 ms in game without
a fidelity cost. two real deviations. first, the free gain: `gain = 0.65`, so the effective weight is
0.179 mV, recalibrated because the male graph carries more synapses per neuron than the FlyWire graph
the 0.275 was fitted on. they document the sweep (0.55 too weak, 0.75 tips grooming into runaway with
kenyon cells at 39 Hz) and their own `FOLLOWUPS.md` records an independent brian2 replication arguing
for 0.45. second, **quantisation**: `refractorySteps() = round(2.2/0.5) = 4` and
`delaySteps() = round(1.8/0.5) = 4`, so the shipped configuration actually runs a 2.0 ms refractory
and a 2.0 ms delay, not 2.2 and 1.8.

(b) is forward euler at dt = 1 ms, and the whole engine is nine lines:

```java
voltage[i] += (-52 - voltage[i] + conductance[i]) * .05f;
conductance[i] *= .8f;
if (voltage[i] > -45) { voltage[i] = -52; conductance[i] = 0; refractory[i] = 3; ... }
```

`.8f` is tau_syn = 4.48 ms, not 5. refractory is 3 ms, not 2.2. the delay ring has three slots and
delivers at `(clock+2)%3`, so 2 ms, not 1.8. sensory drive is not a poisson synapse but a bernoulli
voltage kick: `if (random.nextFloat() < probability) voltage[i] += 68.75f`, which from rest is 94x
the 7 mV gap to threshold. `docs/BIOLOGY.md` states every one of these as an approximation, which is
more than most of the hobby layer does.

neither has noise or spontaneous activity; a silent brain is 0 spikes in both, confirmed. signs come
from the neurotransmitter call in both (ACh/dopamine/octopamine/serotonin/unclear excitatory,
GABA/glutamate/histamine inhibitory) — 116,390 / 60,032 in (a).

## why they run at the speed they do

**(a): dt 0.5 and an active set.** propagation is an event-driven scatter down each spiking neuron's
CSR row into a delay ring; integration walks an *active list* of neurons away from rest, refractory,
or holding pending input, dropping each back out when it settles. under the feeding stimulus that
list grows from 15 k to ~91 k of 176,422, so about half the brain is skipped. per simulated
millisecond: 2 steps x 91 k = 182 k membrane touches against 120 spikes x 35.7 out-degree = ~4,300
scatter writes. membrane-bound, like ours.

**measured**, 2 threads: the feeding bench reproduces their published `VALIDATION.md` table
*exactly* — same active counts, spike counts and MN9 rates tick for tick, which says good things
about their seeding — at 0.91 s wall for 600 ms, **1,517 ms per simulated second**. the same stimulus
over 300 ms costs 1.22 s at dt 0.1, 0.38 s at 0.5, 0.24 s at 1.0, so dt is worth 5x across that
range; and their README's claim that dt 0.1 "changes no fixed point because the integrator is exact
per step" is true of the membrane and false of the trajectory — total spikes were 15,279 / 20,840 /
16,398.

the active set is not free: the list is kept in activation order and compacted in place, so every
touch is a gather from six arrays rather than a streaming pass — roughly 20 ns per active neuron-step
per thread.

**(b): it does not run.** `advance()` steps 25 x 1 ms and `FruitFly.customServerAiStep` calls it
`if (tickCount % 10 == 0)` — 25 ms of neural time per 500 ms of wall clock, one twentieth of real
time, by design. within a window it is a dense pass over all 138,639 neurons, no active set.
**measured**: the silent pass is 6.55 ms per 25 steps = 262 us per step = **1.9 ns per neuron**, a
clean streaming loop. under drive their `BrainBenchmark` reports **47.0 ms per 25 ms window**
single-threaded (**1,880 ms per simulated second**); the extra 40 ms is propagation, because ~23,700
spikes per window is a 6.7 Hz whole-brain mean rate and at out-degree 108.9 that is ~105,000 random
scatter writes per simulated millisecond. (b) is the only one of the three that is propagation-bound,
because it is the only one that spikes that hard.

## senses and actions

| | (a) fly-brain-minecraft | (b) fruitfly-brain-mod | ours |
|---|---|---|---|
| connectome | MaleCNS v1.0, 176,422 / 6.29 M edges (>=5 syn) | FlyWire v783, 138,639 / 15.09 M rows, unpruned | MaleCNS v1.0, 162,517 |
| dt, integration | 0.5 ms, exact linear | 1 ms, forward euler | 1 ms, forward euler |
| refractory / delay actually run | 2.0 / 2.0 ms | 3.0 / 2.0 ms | 2.2 / 1.8 ms |
| w_syn | 0.275 x gain 0.65 = 0.179 mV | 0.275 mV literal | 0.275 (0.185 under review) |
| propagation | event-driven CSR scatter + delay ring | event-driven CSR scatter + 3-slot ring | event-driven CSR scatter |
| membrane pass | active set, ~50 % of cells | dense, 100 % | dense, 100 % |
| threads | ForkJoin over the active list; 1 brain per fly | none; one worker for the whole mod | 2 (numba prange) |
| neural time per wall second | 0.24-0.66x (measured, 2 thr) | 0.05x by construction | ~0.21x |
| noise | none | none | optional |
| driven cells | ORN by glomerulus+side, GRN by type, JO auditory/wind/groom, BM bristles by entry nerve, haltere + hair plates, TRN/HRN, photoreceptors by column, L1/L2/L3 by injected current, ON/OFF transients on L2/L3 and Mi1 | six scalar groups: olfactory L/R (1,116/1,133), sugar/water (129), sensory visual (10,855), mechanosensory (2,656), hygrosensory (74) | ~43 receptor rows |
| eye | 1,769 real hex columns, bundled measured per-column directions, ~160 coarse rays, half raycast per tick, luminance = light x (0.3 + 0.7 albedo) | none; a scalar `looming` flag | ray-traced ommatidia + flyvis |
| readout | 21 channels, 25 weighted DN/MN terms, per-channel tau, priority ladder with hysteresis | 3 numbers over 2, 6 and 1,299 neurons | DN populations |
| hand-set numbers | ~150 (32 encoder, 25x2 motor terms, 21 taus, 13 arbitration, 27 config) | ~15 | ~unknown, many |
| validation | 7 headless scenarios + 56 junit tests, published with failures | none claimed | probe suite |

(a)'s sensing is the most serious thing outside our own eye: it casts half of ~160 coarse rays per
tick through the real block world onto columns read out of `assignedOlHex1/2`, using a bundled
`column_directions.csv` matched to a µCT ommatidium map — the same move as our seam, at lower
resolution. odour is exponential falloff to glomeruli from an item/block table with a bilateral gain
`1 ± 0.3 sin(bearing)`; taste separates tarsal from labellar contact gated on the proboscis; other
flies emit cVA on DA1/DL3 or VA1v/VA1d by sex. (b)'s sensing is six floats.

## emergent versus scripted

(a) is honest in its README table and mostly right. **emergent**: sugar GRNs to G2N-1 to
Fudog/Rounddown to MN9 (measured, 30-90 Hz); bitter GRNs to Scapula silencing MN9 (exactly 0 for a
whole run with sugar present); JO to aDN1/aDN2 (~200/~150 Hz). **not emergent**: everything visual.
their `VALIDATION.md` §6.1 reports lamina cells behaving correctly (~35 Hz dark, ~10 Hz light — the
sign-inverting histaminergic synapse works) and Mi1, Tm1-3, T4 and T5 never firing in any phase, so
LC4/LPLC2/LC11/LC18/LC10a/HS/VS are painted analytically from an object list and the
loom-to-giant-fibre result rides on a hand-built detector.

their `FOLLOWUPS.md` §2 claims looming escape *does* emerge from L2/L3 OFF drive alone with the
painted channels off. **measured**, it does not: `visionBench scene=loom objectChannels=false` gives
T5 at 0 Hz throughout, T4 non-zero only in the first tick, LC4 0, LPLC2 0, DNp01 0, and the decoder
never leaves IDLE. §6.1 is right and §2 is stale.

steering is worse than either document says. in their own `apple` scenario the odour bearing is +40°
(the fly's right) for 3 s then 0, and **measured**, `yaw` sits at -0.76 to -0.87 throughout: a hard
*left* command, anticorrelated with the stimulus and near full scale even with the odour dead ahead.
that is the artefact class `docs/LANDSCAPE.md` took from closed-loop-fly, with a consequence they
missed — `FlyBody`'s reflex chemotaxis only engages when
`fwd < 0.05 && Math.abs(yaw) < 0.05 && bwd < 0.05`, so a loudly wrong yaw locks the fallback out
instead of deferring to it.

(b) is scripted end to end and says so. `sniff()` picks a target, a flee vector handles players, a
random walk fills the gaps; the brain contributes `direction.yRot(output.turn() * .45f)` — at most
±25.8° — and a speed of `0.075 + 0.065 * locomotion + 0.025 * escape`, while fright sets 0.24
outright and bypasses it. **measured**, neither readout carries information: odour hard left gives
turn -0.703, hard right -0.802, symmetric -0.556 — the sign never flips — and full-strength looming
gives escape = 0.000 in twelve consecutive windows. the turn pool is two neurons a side through
`tanh(2x)`, so one spike of difference saturates it; the `escape` group is `DNp01` *and* `MDN`, the
backward-walking command neuron.

## accuracy verdict

**(a): the best open implementation of the shiu model i have read outside brian2, with a vision claim
its own bench refutes.** exact integrator, right constants up to the dt quantisation, no noise, no
spontaneous activity, both ends attached to real cell types through a spec grammar, every rejected
alternative kept as a live `LifConfig` option with the rejection written down, and a validation
document that publishes its own failures. the feeding, bitter and grooming results are real results
about the male connectome; the escape result is real *given* a hand-built loom detector; the walking,
turning and chemotaxis are not from the wiring at all.

**(b): faithful in the graph, unfaithful in everything after it, and candid about the gap.** the data
handling is good — whole FlyWire, no pruning, literal weight, sha256 provenance, a benchmark that
asserts no fabricated spikes. the engine then changes the integration scheme, three of the four time
constants, the drive mechanism and the time base, and reads out through three numbers over 2, 6 and
1,299 neurons with no validation; measured, both named behaviours fail. what a player sees is
minecraft AI with a 138,639-neuron jitter source attached. `BIOLOGY.md` says nearly that itself,
which is the reason to respect the project.

## what ours should steal

**1. kill the division in `_membrane`.** both mods precompute their decay constants; ours does
`(-v[i]/tau_m)*dt` per cell, a float divide in the dependent chain. **measured** on our real kernel,
N = 162,517, 2 threads: 8.65 ns/cell as written, **5.31 ns/cell** with `-v[i]*b`, `b = float32(dt/tau_m)`
— **1.63x on `_membrane`**, which is ~84 % of the step and the step ~81 % of the loop, so **~26 % of
the run**. bigger than `docs/PERFORMANCE.md` item 1 and the same afternoon of work. *changes results:
yes, at the last bit — max |Δv| after one step 1.9e-6. needs a re-frozen oracle.*

**2. the exact linear integration, as (a) does it.** shiu's model.py is `method='linear'`; ours is
forward euler at dt = 1 ms. **measured** PSP peak per unit synaptic jump: analytic 0.15749,
exact-step 0.15744 at every dt, euler 0.15506 at dt 0.1, 0.14517 at 0.5, **0.13228 at dt 1.0**. the
total charge is preserved (the discrete sum telescopes to tau_syn/tau_m exactly) but the peak is 16 %
low, and spiking is a threshold on the peak — so our engine is systematically ~16 % less
synaptically efficacious than the paper at the same w_syn. that bears directly on the 0.275-vs-0.185
question. *changes results: yes, everywhere. it is also cheaper than what we run now: three
precomputed multiplies, no divides.*

**3. interleave the state, drop the dead reads.** **measured**: current 8-array kernel 10.28 ns/cell;
dropping the all-zero `ext`/`noise` reads and the `v_th` gather 9.25; an interleaved `(N,3)` state
array 8.85 — **1.16x**, and it composes with item 1. `PERFORMANCE.md` item 7(b) estimated 10-20 % of
`_membrane`; measured 16 %. *bit-identical for the interleave and for dropping additions of 0.0f;
not for the scalar `v_th`, which is genuinely non-uniform — keep the array.*

(a)'s `FOLLOWUPS.md` §3 also names the subnormal-`g` flush java has no FTZ for — the same fix that
landed in `world/fastlif.py` on 09-19, after my baseline timings were taken, so the 10.28 ns/cell
figure above is the pre-flush kernel.

**4. do not steal (a)'s active set.** at our ~100 spikes/ms over 162,517 cells it looks free, but the
list is in activation order, so it converts a streaming pass into a gather: (a) pays ~20 ns per active
neuron-step against (b)'s 1.9 ns per dense one. if we ever want it, the set has to stay sorted or be
a bitmap so the pass stays contiguous.

**5. steal the spec grammar.** `PopulationIndex` resolves `prefix:ORN_DM1`, `class:gustatory`,
`subclass:wm`, `body:10783`, `DNa02/L` and `&`-intersections against annotation columns we already
load — precisely the selector `docs/ARCHITECTURE.md`'s `receptors.py` registry wants, in ~120 lines.
*changes results: no.*

**6. run the silent-readout control.** both mods fail it in different directions — (b)'s turn is
sign-independent of the stimulus, (a)'s yaw is anticorrelated with it — and neither runs it. it is
the one-hour test `docs/LANDSCAPE.md` already named, and it now has two more scalps waiting.

## what i could not determine

- whether (a)'s *reported* 25-60 ms per tick at 8 threads reproduces here. i ran 2 threads only, and
  never in-game.
- (a)'s `docs/research/gaps/gap-1.md`, an independent brian2 replication over 300+ full-network runs
  recommending W_syn ≈ 0.125 mV on the >= 5 graph. it bears on our own synapse-constant question and
  i did not read or re-run it.
- why (b)'s turn is always negative: a real left/right asymmetry in FlyWire's DNa01/DNa02, a side
  mislabel in the annotation join, or an artefact of the 68.75 mV kick. four neurons, one afternoon,
  and i did not spend it.
- whether (a)'s medulla silence is the uniform LIF's fault or the lamina drive law's. i falsified
  `FOLLOWUPS.md` §2 at the shipped defaults but did not try their proposed
  "sustained 0.3·(1−L) + transient" rate law in place of the injected tonic current.
- our kernel numbers come from a microbenchmark with uniform state — no refractory branches, no
  spikes. the real branch mix could move the 1.63x either way; nobody should believe it until it is
  timed inside `pair.py` against the oracle.
