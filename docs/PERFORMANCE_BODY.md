# where the body loop spends its time, and what is faster without changing a bit

measured 09-23 evening (nyx, a review agent in a worktree, branch `perf-review`), while the solver `s1` ran four body runs at four numba
threads each on the same laptop (i9-10885H: **8 physical cores, 16 hardware threads**; load average 10-13 throughout). the rule of
`docs/PERFORMANCE.md` holds here too: **absolute seconds are inflated and drift with the solver's generations; the shares, and the
ratios between two variants run side by side at the same moment, are what to read.** every A/B below was two processes started
together. nothing here is a result; the test candidate is the solver's best vector so far (`SOLVER_s1_best.csv`, g029_c03, seeds 11 / 12).

method: cProfile for the call graph; then an instrumented copy of `experiments/body_loop.py` (perf_counter around each block of the per-ms
loop, fastlif's kernels wrapped, MuJoCo's own `d.timer`) for the shares, because cProfile cannot see inside a numba kernel and charges
numpy's small-call overhead at Python-call rates; a microbenchmark of the membrane kernel alone; an option bench of `mj_step` from a
mid-walk state.

## 1. the shares

### the body (`experiments/body_loop.py`, the solver's stack, 5 s, per millisecond of simulated time)

| block | before, 1 thread | after, 1 thread | before, 4 threads |
|---|---|---|---|
| MuJoCo, 10 substeps (`sim.step()` x10) | 2,167 us (40 %) | 2,362 us (52 %) | 2,263 us (44 %) |
| the LIF step, `M.step()` | 1,514 us (28 %) | 1,367 us (30 %) | 939 us (18 %) |
| &nbsp;&nbsp;of which the membrane kernel | 1,169 us | 989 us (the unrolled kernel, section 4) | 555 us |
| &nbsp;&nbsp;the plateau (`_pic_step`: numpy on 13 cells, a copy of ext) | 69 | 78 | 75 |
| &nbsp;&nbsp;the Poisson draw (`_count_live` + rng + `_drive_gate`) | 70 | 76 | 77 |
| &nbsp;&nbsp;propagation (`_propagate_into_nt`) | 37 | 39 | 39 |
| &nbsp;&nbsp;`exact_kg` x4, reset, and the rest of step()'s Python | ~170 | ~185 | ~190 |
| segment contact forces (`get_bodysegment_contact_forces`, every ms) | 613 us (11 %) | 231 us (5 %) | 647 us (13 %) |
| the senses' per-leg loop (39 scalar `np.clip` per ms) | 391 us (7 %) | 99 us (2 %) | 418 us (8 %) |
| spike select + MN log (`np.isin(idx, LEGMN)` and a Python loop) | 255 us (5 %) | 20 us (0.4 %) | 297 us (6 %) |
| `REG.apply` (~55 rows) | 100 us (2 %) | 120 us (3 %) | 109 us (2 %) |
| thorax pose + the 10 ms `BODYF` segment read | 99 us (2 %) | 58 us (1 %) | 102 us (2 %) |
| load smoothing / leg sensor / joint angles / actuators + pads | 66 + 48 + 37 + 53 us | 72 + 53 + 41 + 55 us | 73 + 52 + 42 + 61 us |
| the torque kernel adds (per spike, a 120-sample slice) | 42 us (0.8 %) | 48 us (1 %) | 49 us (1 %) |
| `--log-x` (134 cells) | 34 us (0.6 %) | 38 us (0.8 %) | 39 us (0.8 %) |
| **loop, per simulated ms** | **5.43 ms** | **4.57 ms** | **5.10 ms** |
| of which neither the LIF step nor MuJoCo | 1.74 ms (32 %) | 0.84 ms (18 %) | 1.90 ms (37 %) |

"before" and "after" at 1 thread are one pair started together (the unmodified script and engine against the branch); the 4-thread
column is the unmodified code in an earlier run. in this pair the branch's process drew the slower core (its MuJoCo, which nothing here
changed, ran 9 % slower), so its loop ratio, 1.19x, is the low end; three pairs gave 1.19-1.29x. **what the loop is now: half MuJoCo, a
third the LIF step, a sixth everything else.**

**MuJoCo, inside** (`d.timer`, per 0.1 ms substep, 224 us): the constraint solve 94 us (Newton, 8.0 iterations on average, 15 at most,
`noslip_iterations` 5 on top), position 95 us (collision 27 with 55 explicit pairs and multi-CCD, projection 21, kinematics 19, make 15,
inertia 14), integration 12, velocity 9, sensors and the rest ~10. the model: 72 DOF, 48 actuators, 3.5 contacts and 16 constraint rows
on average (13 / 55 at most); timestep 1e-4 s, so 10 substeps per ms and 200,000 per 20 s run. per substep the cost is the solver, not
Python: flygym's `Simulation.step()` is one `mj_step` call.

**startup**, per body process: ~2.4 s of imports (numba, mujoco, flygym, pandas), ~1.9 s from `t0` to the loop (the brain, the size path,
flygym's compile, **the 0.5 s settle of `--start-pose feet`: 5,000 substeps, ~1.1 s**), 0.1 s to save. ~4.4 s of a ~90 s run, **~5 %**.
numba is already `cache=True` everywhere and the cache is hit (a cold cache costs ~5 s more per process, once per edit of an engine file).

### the cord (`world/cord.py`, 10 s, the brief's flags with `--log-ms`, 1 thread)

| piece | share of the run |
|---|---|
| `M.step()` | 92 % |
| &nbsp;&nbsp;the membrane kernel | 74 % (1.03 ms per step) |
| &nbsp;&nbsp;`_pic_step` / the Poisson draw / propagation / `exact_kg` | 4.3 / 4.2 / 0.9 / 0.7 % |
| &nbsp;&nbsp;the rest of step()'s Python | ~8 % |
| `REG.apply` (per 10 ms frame) | 0.3 % |
| `--log-ms`'s `np.isin` + `searchsorted` (before the fix) | ~20 % under cProfile; 18.1 -> 16.1 s wall measured |

**the solver's prefilter does not pass `--log-ms`** (`experiments/solver/params.py`: `CORD_STACK` has `--drive SNpp50:40` and no
`--log-ms`), so for the solver the cord is ~75 % one numba kernel and the `--log-ms` fix buys it nothing. at 1 thread under this load the
prefilter took 13.6 s for 10 s (the solver's `--time-one` quoted 5 s at 4 threads on a quieter box).

## 2. threads: the solver should run many single-threaded processes

measured, each pair started together (so the same load):

| run | 1 thread | 2 threads | 4 threads | 8 threads |
|---|---|---|---|---|
| body 5 s: wall / CPU seconds | 36.8-38.2 / 39-40 | 35.4 / 46 | 33.0 / 56 | |
| cord 10 s: wall / CPU seconds | 21.0 / 22.5 | 17.0 / 31.5 | 16.4 / 50.2 | 15.5 / 79.8 |
| body, two 1-thread runs pinned to the two hardware threads of one core / to two cores | 48.6 s each / 36.8 s each | | | |

- four threads buy a body run **~11 % of wall** over one thread and cost **~40 % more CPU**: only the membrane kernel is parallel (half
  the LIF step, a sixth of the loop at 4 threads); MuJoCo, the senses and the logging are one Python thread. the idle workers are not
  free: numba's threading layer here is TBB, and each solver process at 4 threads shows **~200 % CPU in `ps`** (a quarter to a third of
  its CPU time is system time) for ~120 % of useful work.
- two processes on the two hardware threads of one core run 1.32x slower each, i.e. **1.5x the throughput of that core**.
- a generation is 8 candidates x 2 seeds = 16 body runs (after 8 prefilters). with T1 = one single-thread 20 s body run on a core of its
  own (the 4-thread run is ~0.89 T1):

| `--concurrent x --threads` | waves of body runs | generation's body time | vs today |
|---|---|---|---|
| 4 x 4 (today) | 4 | 4 x 0.89 T1 = 3.6 T1 | 1 |
| 8 x 2 | 2 | ~2 x 1.0-1.1 T1 (the second threads land on the busy cores' siblings) | ~1.7x |
| 8 x 1 | 2 | 2 T1 | **~1.8x** |
| 16 x 1 | 1 | 1.32 T1 | **~2.7x** |

**recommendation: `--concurrent 16 --threads 1`** (so `NUMBA_NUM_THREADS=1`; fastlif's `set_num_threads(min(8, ...))` then gives 1).
the 16 x 1 figure is an estimate from pairs, not a measurement of sixteen processes (the solver held the box); memory is the one limit to
watch: ~0.75 GB resident per body process, 12 GB for sixteen, against ~21 GB available with the solver's four running. if memory or
the laptop's thermals push back, **8 x 1** is the safe step (~1.8x, and it leaves the hardware siblings free). the thread count does not
touch a bit of the result: a 4 s run at 1 thread and at 4 threads saved identical arrays (every one, `max |d| = 0`).

## 3. candidates, ranked by what they buy the solver

gains are per body evaluation at the recommended 1 thread unless said; "identical" means every saved array byte-identical.

| # | change | gain | status |
|---|---|---|---|
| 1 | **concurrency 16 x 1** (or 8 x 1) instead of 4 x 4 | **~2.7x (~1.8x) per generation**, estimated | identical (thread count does not enter the arithmetic; checked) |
| 2 | **the per-ms Python of the body loop** (the segment contact forces with their lookups built once; the scalar clips without numpy; `np.isin` / the per-spike log loop as tables) | **loop 1.29x** (31.95 -> 24.72 s per 5 s, side by side); ~1.2x on a whole 20 s run | **identical, prototyped** (below) |
| 3 | **the membrane kernel unrolled for the stack's layout** (four rows, class 0 a current, 1-3 on reversals) | **1.5x on the kernel alone** (695 -> 471 us at 1 thread, 277 -> 184 at 4, microbench, interleaved); in the loop's pair 1,169 -> 989 us per ms (1.18x), **~3-4 % of the loop** at 1 thread | **identical, prototyped** (engine change: oracle below) |
| 4 | the rest of `FastFlyBrain.step()`'s Python: `exact_kg` x4 and two `np.array` per step, `_pic_step`'s numpy on 13 cells plus a 23,074-cell copy of ext, `last_spikes = spk.astype(float32)` and `spk.copy()` (read by nothing here), `ascontiguousarray` / `noise * _noise_scale` temporaries | ~150-200 us/ms: **3-4 % of the loop** | identical if the float ops are kept (cache `exact_kg`; do `_pic_step`'s float64 arithmetic unchanged on the 13 cells without the full copy); engine change, oracle |
| 5 | skip the 0.5 s `--start-pose feet` settle: it is the same for every candidate (the model, the springs, no muscle, no pad); pickle the whole settled `MjData` once per body model and load it | ~1.1 s of ~90: **~1.2 %** | identical **only** if the full `MjData` is restored (the first ms reads contacts and sensor data computed inside the last settle step; `mj_setState` + `mj_forward` would recompute them at a different point and change the first reads) |
| 6 | `REG.apply`: re-write a row only when its value changed and no other row shares its cells | ~2 % | identical if the overlap rule is exact; touches `src/fly_afterlife/receptors.py`, which the oracle's `pair.py` also uses |
| 7 | MuJoCo's energy (on in flygym's `mujoco_globals.yaml`, read by nothing) off, and sensors computed only on the last of the 10 substeps | within the bench's noise (<= 5 % of the physics, <= 2.5 % of the loop) | identical in principle (neither enters the dynamics); not measurable on this box today |
| 8 | the 10 substeps as one `mj_step(m, d, nstep=10)` | < 0.5 % | identical |
| 9 | skip the 1 ms logging (`--log-x`, the MN frames) when not needed | < 1 % (36 + 20 us/ms) | identical for what is still saved; the solver reads `x_ms` (its type-rate penalty), so not for the solver |
| 10 | the torque kernel as a vectorised add or a running (IIR) state | the per-spike slice add is **46 us/ms, 0.9 %**: not worth it | a vectorised add of several spikes into one DOF at one ms sums them in a different order than the per-spike loop: **a summation-order change**; a two-state IIR of `e^-t/20 - e^-t/7` normalised by `K.max()` is not the 120-sample FIR bit for bit: **a result change at the last bit**, and it drops the kernel's 120 ms truncation |
| 11 | caching `leg_forces()` | 51 us/ms, one sensor read + a norm; the state changes every ms; the only reusable read is the 10 ms `BODYF` segment read, which equals the next ms's first read (~5 us/ms) | identical; not worth it |
| 12 | the delay line as a ring buffer | a pop(0) / append on a 2-element list of ~10 spikes: under 1 us per step | identical; not worth it |
| 13 | per-class rows only for classes that exist | all four exist in the cord (other 1,020, ACh 13,491, GABA 5,915, glu 2,648 cells) and the rows are per cell; nothing to skip. the layout gain is #3 | - |
| 14 | "float32 everywhere it already is" | **the reversal kernels are not float32 inside, and must not be made so silently**: the flush's literal `0.0` makes numba unify each `g` to float64, so `gg`, `gr`, `x` and the membrane update run in float64 and round once into the float32 `v`. writing `np.float32(0.0)` there changes spikes (tried: the unrolled kernel with float32 literals was 1.9x but not identical); it is a result change | result change |
| 15 | numba `error_model="numpy"` on the membrane kernel | none (848 vs 973 us at 1 thread, 460 vs 470 at 4) | identical, no gain |

### what would be a result change, and by how much

scored with the solver's own objective (`experiments/solver/objective.py`, the fine lift rule, 20 s, the g029_c03 vector; the seed-to-seed
difference of the baseline is 0.058):

| physics | wall per 20 s run (1 thread, same moment) | score s11 | score s12 |
|---|---|---|---|
| as run (timestep 1e-4, `noslip_iterations` 5) | 85-87 s | +0.597 | +0.539 |
| `noslip_iterations` 0 | 80-84 s (the option bench: physics x0.80) | +0.570 | +0.524 |
| timestep 2e-4 (5 substeps per ms) | 61-69 s (physics x0.63) | **+0.003: he falls** (body on the floor 8.7 uN, feet 1.0) | +0.590 |
| timestep 2e-4 and `noslip_iterations` 0 | 69 s | +0.584 | |

the half timestep is **not** a safe economy: one of two seeds turned from a walking fly into a fallen one, so the physics at 2e-4 is a
different body, not a coarser copy of the same one. the no-slip pass is cheaper to drop (~5-8 % of wall) and moved both seeds' scores
down by 0.015-0.027, a systematic shift a third to a half of the seed-to-seed difference: a result change a solver should not mix with
the runs of record; if it is wanted, it is a new baseline with every yardstick re-run. `tolerance 1e-6` bought nothing (the solver
converges in ~8 iterations); `jacobian` dense was 1.3x slower, sparse the same as the auto choice.

## 4. what was prototyped (branch `perf-review`)

1. **`experiments/body_loop.py`**: `seg_forces()` is flygym's `get_bodysegment_contact_forces` with its lookups built once (flygym builds
   one `BodySegment` object per segment, a geom dict and four `np.isin` on every call, 380,000 dataclass inits per 5 s); the same
   contacts, the same `mj_contactForce`, the same `frame.T @ f` and the same `-=` / `+=` on the same rows in the same order. `clip01()`
   replaces the 39 scalar `float(np.clip(x, 0, 1))` per ms with numpy's own rule for floats (nan passes; max against 0, then min against the
   top; -0.0 comes out +0.0). the motor-neuron hits and the log use tables (`ISLEG`, `LPOS`) in place of `np.isin` and a Python loop, and
   `--log-x` a fancy add in place of `np.add.at` (a step's spikes never repeat). `world/cord.py --log-ms` the same way.
2. **`world/fastlif.py`**: `_membrane_exact_nt_rev4`, the reversal kernel unrolled for four rows with class 0 a current and 1-3 on
   reversals, dispatched from `step()` only on that layout (`--syn-rev 70:-5:-5` and any other with all three reversals); every other
   layout runs the loop kernel as before. the same float ops in the same order at the same types (see #14 above).

**identity, verified** (every saved array, bytes and `max |d| = 0`):
- 4 s body runs against the unmodified script and engine, on four configurations: the solver's stack (A); the old default path (B:
  senses v1, the position+load loop, ltm pads, the leg sensor, `--slow-mv` / `--cocon`, `--log-v`, `--log-x`); the puppet on the solver's
  stack (C); tethered with `--mn-poisson` (D). and A at 1, 2 and 4 threads.
- **20 s body runs against the solver's own saved arrays** for g029_c03, seed 11 (the loop changes) and seed 12 (the loop and the kernel):
  identical to the files `experiments/solver/runs/s1` wrote with the unmodified code.
- the cord, 10 s, with the brief's flags (`--log-ms`) and with the solver's prefilter flags: identical `.npz` and `.cells.npz`
  (including `ms_counts`) before and after both changes.
- `scripts/oracle_check.sh` (the eight whole-fly configurations; they run the record's kernels, not the reversal one, so this checks that
  nothing else moved): **ORACLE CHECK PASS**, all eight, v1 69 and v2 82 arrays, none differing.

**measured gain** (side by side, 1 thread, the solver's stack, the unmodified script and engine against the branch, started together):

| pair | before | after | ratio |
|---|---|---|---|
| 20 s body run, the loop changes alone (seed 11) | 109.4 s wall | 92.4 s | 1.18x |
| **20 s body run, the loop and the kernel (seed 11)** | **130.7 s wall** (loop 128 s) | **102.7 s** (loop 100 s) | **1.27x** |
| 5 s instrumented, the loop changes alone | 31.95 s of loop | 24.72 s | 1.29x |
| 5 s instrumented, the loop and the kernel | 27.14 s of loop | 22.86 s | 1.19x (the branch drew the slower core: its MuJoCo ran 9 % slower) |

so **~1.2-1.3x per body run**, bit for bit (the 20 s pair's arrays identical to each other and to the solver's). with the concurrency
change on top, the estimate per generation is ~2.7x x ~1.2 = **~3x** (8 x 1: ~2.1x); the 16-process figure is the unmeasured part.

**merging**: `world/fastlif.py` changed, so the first process after the merge recompiles the kernels (~5 s, once; numba's cache writes
are atomic, sixteen processes racing is safe but each may pay it once). merge between solver runs, as asked; the solver's scores for
the same vector do not move (they are the same bytes).
