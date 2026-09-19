# where the simulate runner spends its time

measured 2026-09-18 17:00 PDT (nyx), from nate's question about the runner. `docs/TODO.md` §6 listed
three performance items on intuition; this replaces the intuition with numbers. no repo code was
changed to produce it: every variant below was prototyped in a scratch copy against the real objects.

**the caveat, first.** the box was running three other 120 s jobs plus an oracle check throughout,
load average 8-13 on 8 physical cores, so absolute milliseconds are inflated, probably 2-3x (the
09-17 note in `docs/SEAM.md` measured 0.31 ms per LIF step at 8 threads idle; the same step measures
3.8-4.7 ms here at 2 threads). what survives the contention is **shares**, **ratios between variants
timed back to back**, and **bit-identity**. estimates are labelled as such.

method: cProfile on `world/pair.py --seconds 15` (garden and room, alone and with her,
`NUMBA_NUM_THREADS=2`) for the call graph, plus a harness that runs `pair.py`'s real setup, intercepts
`Episode.run`, and times each piece of forty real chunks. the numbers below are the harness's.

## where the time goes

ms per simulated second:

| component | garden, alone | room, alone | garden, both brains |
|---|---|---|---|
| LIF steps, 1,000 x 1 ms (`world/fastlif.py`) | 3,862 (80.8%) | 4,666 (87.6%) | 5,566 (81.1%) |
| `Eye.render`, 100 frames (`seam/omma.py`) | 562 (11.8%) | 224 (4.2%) | 834 (12.1%) |
| flyvis chunk, 10 x 2 eyes (`frontend.py`) | 247 (5.2%) | 347 (6.5%) | 313 (4.6%) |
| `Registry.apply`, 100 frames (`receptors.py`) | 58 (1.2%) | 71 (1.3%) | 80 (1.2%) |
| world fields + per-frame state dict | 46 (1.0%) | 12 (0.2%) | 59 (0.9%) |
| effectors, logging, smells, readout counts | 5 | 7 | 7 |
| **total** | **4,781** | **5,327** | **6,865** |

the garden's raytrace costs 2.5x the room's (4.50 ms of shader per frame against 1.22): every ray
tests thirty grass cylinders, three leaf discs, a floor texture and a sun on top of the walls and
spheres. and **the flyvis chunk is no longer the largest single cost** — `docs/TODO.md` §3 and §6
still say it is, from the 09-17 note. at 25-29 ms per chunk it is 5-7% of the loop against the step's
81-88%. her brain adds 44% to the step bucket, not 100% (her step alone is 1.49 ms against his 4.93),
so §6's two-brains-in-threads item is done and it worked.

## inside the LIF step

| piece | ms at 2 threads | share of the step | scales with threads? |
|---|---|---|---|
| `_membrane`, one pass over 162,517 cells | 3.86 | ~84% | yes |
| the driven-cell Poisson draw (25,973 cells, ~10,400 live) | 0.89-1.07 | ~22% | no, serial numpy |
| `_propagate_into`, 7,000-9,000 edges walked | 0.11-0.18 | ~3% | no, serial by design |
| `np.flatnonzero(spk)`, delay-line pop/append | 0.04 | ~1% | no |
| `last_spikes = spk.astype(float32)` + `spk.copy()` | 0.08 | ~2% | no |

(the pieces overrun the measured step by ~8%; that is the noise floor here.)

this inverts the obvious guess. the synaptic propagation — six million synapses, the
expensive-looking thing — is **3% of the step**, because only ~100 of 162,517 cells fire per
millisecond and the CSC walk touches ~8,000 edges. the cost is the unavoidable O(N) membrane pass,
then the Poisson draw, which the tonic floor made large: 25,973 cells are receptors now, 16% of the
brain. the delay line is cheap for the same reason — it carries ~100 int64 indices per slot, and its
`pop(0)` / `append` on a two-element Python list does not register above the noise. leave it alone.

## the ceiling

**inherently serial:** the 1 ms step of one brain. spikes at t reach membranes at t + 1.8 ms through
the delay line, so there is no pipelining across milliseconds, ever.

**parallel within a step:** `_membrane`, and nothing else.

| numba threads | step | `_membrane` | Poisson | loop total, ms per sim s |
|---|---|---|---|---|
| 1 | 7.13 | 5.66 | 1.05 | 9,300 |
| 2 | 4.60 | 3.86 | 0.89 | 4,781 |
| 6 | 3.83 | 1.93 | 1.36 | 4,823 |

`_membrane` scales 2.9x from one thread to six, the step 1.86x, and the loop total not at all from 2
to 6 on a box that already has jobs on it. amdahl: at six threads the serial numpy tail is ~45% of
the step, so threads cannot take it below ~2.5 ms however many cores you give it. and the kernel is
memory-bound: `_membrane` streams ~5.9 MB per step (v, g and refrac read and written, ext, noise and
v_th read, spk and free written) and the whole step ~8.5 MB, on a laptop that realises maybe
25 GB/s. so under contention extra threads buy nothing, and the right unit of parallelism is the
**job**, not the thread.

**embarrassingly parallel:** whole episodes (`world/run_many.py`); the two brains within a chunk
(done). **batchable:** the ten frames of a chunk in the eye, the two eyes in flyvis, the ten frames
of receptor drive.

## what to change, ranked

**1. the driven-cell Poisson draw, into a kernel.** `fastlif.step` ends with eight numpy temporaries
over the driven cells (`hz > 0`, `di[live]`, `hz[live]`, `free[sub]`, `di[~live]`, two scatters).
replace with a count pass, the same `rng.random(n_live)` call, and one `nogil` kernel that walks `di`
once doing the comparison and the `free` gate in place. measured: the tail 1.071 -> 0.580 ms, the
step 4.663 -> 3.835, a factor 1.216, timed interleaved so load drift hit both. the step is 80.8% of
the loop, so 1 - (0.192 + 0.808/1.216) = **14% of the run**.
*effort small, ~25 lines. bit-identity: checked — **500 of 500 steps spike-for-spike identical**,
`max |v_A - v_B| = 0.0` after 500 steps; the rng keeps its call order and size. changes results: no.*

**2. more jobs, fewer threads each, in run_many.** `run_many.py` pins `OMP_NUM_THREADS=1` but lets
`NUMBA_NUM_THREADS` inherit from the shell, so `--jobs 3` at 4 threads puts 12 numba threads on 8
physical cores. set it in the job environment and size it `jobs x threads <= physical cores`: 2 -> 6
threads bought nothing under load while 1 -> 2 bought 1.9x, so 4 jobs x 2 threads should beat 3 x 4.
**estimated ~1.3x jobs per hour, not measured** — an honest measurement needs a quiet box. the GPU
caps it too, at ~0.8 GB of the 1650 Ti's 4 GB per flyvis process.
*effort one line. bit-identity: thread count does not touch the arithmetic. changes results: no.*

**3. hoist the ray rotation out of the frame loop.** heading is constant across the ten frames of a
chunk — steering is applied per chunk in `Episode.run`, after `render_and_move` — but `Eye.render`
recomputes `rays0.reshape(-1,3) @ R.T`, 42,336 rays and a 1 MB float64 array, ten times with
identical input. rotate once per chunk and build the `Scene` once. measured 80.56 -> 68.23 ms of
rendering per chunk, a factor 1.18: 11.8% x (1 - 1/1.18) = **1.8%** of the run in the garden.
*effort small; it adds a `render_chunk` or changes `Eye.render`'s signature. bit-identity: checked,
`np.array_equal` on the full chunk. changes results: no.*

**4. cache the calibrations.** every run pays 56-88 s before the first chunk: torch import, the
flyvis network build (18-46 s of it inside `get_scatter_indices`, which iterates a pandas-arrow
column 9.2 million times), the brain loads, then 7,500 LIF steps and 400 renders of warm-up and
calibration. those scalars depend only on (brain file, w_syn, seed, floor rows);
`docs/ARCHITECTURE.md` already says to cache them and `docs/TODO.md` §1 still has it open. the
calibration work is ~7.5 simulated seconds, ~36 s here: **8-15% of a 120 s run's wall, over half of a
15 s check's** — estimated from the step counts, not measured end to end.
*effort medium. bit-identity: the cached scalars must be byte-identical or the loop diverges. changes
results: no, if the key is complete.*

**5. flyvis: batch both eyes; leave the precision alone.** `FlyvisFrontEnd.chunk` calls
`net.simulate` twice at `batch_size` 1. measured batched: 29.62 -> 21.28 ms per chunk, a factor 1.39,
so **1.5% of the run**. harder than it looks — the eyes carry independent state between chunks, so
the batched call needs their `AutoDeref` states concatenated along the batch dimension and split
again; my prototype passed `initial_state=None`, so it establishes the timing, **not** numerical
equivalence. transfer is not the problem: 0.12 ms per eye goes host-to-device, and slicing the output
on the card before the return bought 1.03x (below). half precision would halve the card's traffic,
but the 1650 Ti has no tensor cores, the network is latency-bound at batch 1 anyway, and fp16 would
move T4/T5 activity far more than the gain is worth. don't.
*effort medium. bit-identity: **flyvis is already non-deterministic call to call** — the same
luminance chunk from the same carried state, run twice, differs by 3.0e-7, which is the 1e-6
`--deterministic` exists to suppress, and it flips downstream Poisson draws. so any change here is
checkable only under `--deterministic`, and needs the frozen oracle re-made. put it behind a flag.
changes results: within the front end's existing noise, yes.*

**6. vectorise the receptor rows and the world fields.** `Registry.apply` loops 43 rows in Python per
frame (0.455 ms, of which 0.380 is the stimulus closures and the transducers, only 0.108 the numpy
writes); the fields are five scalar calls per frame, and `Garden.odour` builds a fresh `default_rng`
on every one. the poses for all ten frames are known before `drive_and_step`, so both could be done
once per chunk over an array of ten. today that is worth at most **2%**. the reason to do it is §1 of
`docs/TODO.md`: drive resolved per 1 ms, which the 30 ms adaptation kernels need — done naively that
multiplies the Python by ten, to **18% of the loop**. a prerequisite for a correctness change, not a
speedup.
*effort medium-large; it touches every transducer. bit-identity: numpy's vectorised `exp` can differ
from the scalar path by 1 ulp, and moving the `default_rng` changes the whiff stream outright —
re-frozen oracle either way. changes results: yes, at the last bit.*

**7. the membrane's memory traffic, and the two brains in one kernel.** three ideas that keep the
arithmetic, all **estimated, not measured**. (a) the 25,973 driven cells are Poisson sources whose
`v` and `g` are read by nothing — only `refrac` matters, for the `free` gate — so 16% of the membrane
pass is dead, ~13% of the step; skipping it without a gather wants those cells contiguous, i.e.
renumbering the brain and every index set and oracle npz pointing into it. (b) interleaving `v`, `g`,
`refrac` into one (N,3) array so the kernel walks one stream instead of three: a prefetch effect,
plausibly 10-20% of `_membrane`, mechanical. (c) one `_membrane` over both brains' 301,765 cells
instead of two nested parallel regions, rngs and delay lines kept separate: her brain costs 1,704 ms
per simulated second where stepping her alone costs 1,486, so ~5% of a two-fly run should come back.
*effort: (b) medium, (a) and (c) large. bit-identity preserved in principle for all three — the
membrane is elementwise, no edge crosses between the brains — but nobody should believe (a) or (c)
without the oracle. changes results: no, if done correctly.*

**8. a GPU port of the LIF step.** the step is ~8.5 MB of traffic and the 1650 Ti has ~192 GB/s
against this laptop's ~25 GB/s realised, so a resident membrane pass could be ~40 us against 1.9 ms
at 6 threads — but launch overhead and Python dominate unless a whole 10 ms frame runs inside one
kernel or a CUDA graph. **estimated 3-5x on the step, ~2.5-3.5x on the run; not measured.** the
fidelity cost is the real price: a GPU Poisson draw is curand, not PCG64, so the spike train differs
from step one, and a scatter-add propagation needs float32 atomics, whose summation order is not
reproducible even run to run on the same card. gathering by postsynaptic cell would fix that but
means walking six million edges per step instead of eight thousand, and the advantage evaporates. a
GPU engine is a **second engine**, like `--numpy-engine`, with its own oracle — build it when a 600 s
benchmark run (`docs/BENCHMARKS.md` §2d) is the bottleneck, not before.
*effort large. bit-identity: impossible by construction. changes results: yes.*

**not ranked: eye resolution.** `N_RAYS = 24` per column is the one dial that cuts the raytrace
linearly — 8 rays would be 3x fewer. it changes every luminance value and therefore every spike, so
it is a research choice (how much acceptance-cone sampling the T4/T5 seam needs), not a performance
one. if it is ever wanted, make it a flag with its own oracle.

## what was tried and did not pay

- **batching the ten frames of a chunk into one raytrace call.** a kernel with the frame loop inside
  and `prange` over all 423,360 (frame, ray) pairs, output verified identical (`max |diff| = 0.0`):
  72.78 ms per chunk against the current 80.56, where the rotation hoist alone gets 68.23. *slower
  than the simple fix* — 42,336 rays already saturate two threads.
- **slicing T4/T5 on the GPU before the transfer.** only 5,768 of 45,669 cells per frame are read
  downstream, so moving 12.6% of the bytes looked free. measured 28.78 against 29.62 ms: the 2.98 ms
  attributed to "stack + D2H" is almost all `torch.stack` building the tensor, not the transfer.
- **`v_th` as a scalar.** it is not uniform — `flysim` scales it on the Kenyon cells. premise wrong.
- **dropping the dead `last_spikes` and `spk.copy()`.** `last_spikes` costs a 650 KB allocation every
  step and is read by nothing here (only `flysim`'s plasticity path, which is off); `spk.copy()` is
  the return value, which only the calibrations use. removing both is spike-for-spike identical over
  400 steps — but it is 0.076 ms, ~2% of the step. a freebie alongside item 1, not its own change.

## profiling hygiene

every numba kernel is `cache=True`, so compilation is on disk after the first run of a signature and
`pair.py`'s warm-up covers the link cost — but a fresh venv or an edited kernel pays it again, and it
lands in whatever you measure next. warm before you time. **cProfile is not the problem here; the
other jobs are**: the same 15 s garden run took 112 s of loop profiled and 142 s unprofiled, purely
from contention — so measure on a quiet box, or measure ratios between variants run back to back. the
one thing cProfile distorts badly is that it counts flyvis's ~100,000 torch dispatch calls at
Python-call rates and cannot see inside a numba kernel at all, so it flatters the eye and the brain
against the front end; time anything inside a kernel directly. and `--deterministic` costs ~130 ms per
chunk and is the only mode in which a flyvis-side change can be checked at all: keep it for
`scripts/oracle_check.sh` and never quote a timing from it.

## the short version

do item 1: 14%, measured, bit-identical, an afternoon. then item 2, one line, and item 3, 2% and also
free. after that the loop is still 80% LIF step, and the only lever with an order of magnitude in it
is a GPU engine that cannot be the same fly. flyvis is no longer the problem; `docs/TODO.md` §3 and
§6 should say so.
