# the solver (campaign ledger row 31; `experiments/solver/`)

**NOTHING THE SOLVER PRODUCES IS A RESULT.** every file it writes and every line it logs carries `SOLVER` and the run's name. a fitted cord
is a puppet by construction; the solver's use is the best vector, read as a map of where the file's weights sit farthest from walking.
nate, on why to build it at all: *"it gives us another comparison point, like the puppet or the live-fly motion."*

## what it optimises

CMA-ES (pycma 4.5, `uv add cma`) over nine numbers, each a scalar on a named set of cell types or a named knob, searched in a unit cube.
per candidate: a size CSV, a 10 s cord-only prefilter (`world/cord.py`), then the honest body (`experiments/body_loop.py`, 20 s) on seeds
11 and 12, scored from the saved arrays with the readers' own rules; the score is the mean over the two seeds. the solver edits no engine,
no body and no reader: every term it moves already exists as a flag or as the size path.

## the parameter set

| # | name | cells (types; count in `brain_cord.npz`) | range | the file's value | ledger |
|---|---|---|---|---|---|
| 1 | lift | IN03A004, IN17A028, IN21A022, IN21A010 (30) | x0.25-16, log | x1 | 28 |
| 2 | release | IN14A008, IN13B013, IN13B006, IN13B004 (24) | x0.25-16, log | x1 | 30 |
| 3 | hold13A | IN13A002, IN13A005, IN13A003 (18) | x0.25-16, log | x1 | 31 |
| 4 | cmdinh | IN12B003, IN19A004 (12) | x0.25-16, log | x1 | 31 |
| 5 | levinh | IN16B016, IN19A008 (14) | x0.25-16, log | x1 | 31 |
| 6 | subnet | IN17A001, INXXX466, IN16B036, IN19A007, IN09A002, INXXX464 (36) | x0.25-16, log | x1 | 31 |
| 7 | levMN | Tr flexor MN, Acc. tr flexor MN (57) | x0.25-16, log | x1 | 31 |
| 8 | pic_g | the small tibia flexors' plateau, `--pic smallflex:G:3:3:50` | G 0-1 | 0.58 (the arms of record) | 9 |
| 9 | dng100_hz | DNg100's rate, `--walk` | 30-150 Hz | 100 | 0 (the command) |

fixed, not searched: the tibia flexors' graded thresholds (the base CSV, ledger 5 / 17), the reversal hold (`each`, ledger 18), every other
flag of the honest stack. `--slow-tau` and the other extras are out. the start is the file's own vector (every gain 1, G 0.58, 100 Hz);
CMA's first step is 0.2 of the cube (1.2 octaves of gain, 0.2 of G, 24 Hz).

**the brief asked for "16 parameters"; the sets it named come to nine.** nothing was added to reach sixteen. the obvious next seven, if a
bigger vector is wanted: split the subnet (six types) and the lift set (four) into their types, or give each set a per-segment gain.

**how a gain reaches its cells: the size path, as rows 28-30 used it.** the candidate CSV is the base CSV
(`flex_graded_abs.csv`, the scratchpad file; ledger 22) with `size = base / g` on every cell of a set, and the stack's `--size-gain 1
--size-thr 1 --size-noise 1 --size-clip 20` turn that into **inputs x g, threshold / g and membrane noise x g** on those cells, each clipped
to [1/20, 20]. so a "gain" is the size path's excitability, three terms at once, not a pure synaptic weight: x16 puts a cell's threshold at
0.44 mV with sixteen times the noise; x0.25 puts it at 28 mV. this is what rows 28 and 30 did (`ex_gain5.csv` is reproduced exactly by the
solver's writer at lift x5); a search that reads as "weights" needs a different path (`--edge-scale` on the inputs only), which is not built.

the flags every candidate runs (`experiments/solver/params.py`), the brief's honest stack plus `--walk-ramp 1`, which every row 28-30 body
arm ran:

    --adhesion contact --senses v2 --size-thr 1 --size-gain 1 --size-noise 1 --size-clip 20 --syn-rev 70:-5:-5 --syn-rev-hold each
    --mn-force azevedo --load-from tarsi --hind-map v2 --start-pose feet --stiffness sourced --claw-labels 50flex --no-video --walk-ramp 1
    --size-from <candidate csv> --pic smallflex:<G>:3:3:50 --walk <DNg100 Hz> --seed <11|12> --seconds 20 --log-x <the gained interneuron types>

the prefilter runs `world/cord.py` as rows 28-30's cord arms did: `--floor standing --drive SNpp50:40` (the pinned flexion claw of a flexed
standing tibia), the same size path, shunt, plateau and command, 10 s, seed 11, every leg motor neuron type and the gained types logged.

## the objective

from `experiments/solver/objective.py`, where the constants live (and are copied into each run's `config.json`). per seed, after the 2 s
warm-up:

- **standing** `stand` = feet / 10.05 uN, clipped to 0-1 (feet = tarsal_force summed, net of the pads, as body_loop.py prints it).
- **stepping** `step` = the mean over six legs of a lift-rate credit: lifts per second (the lift rule below, from 2.1 s) score rate / 5
  under 5 Hz, 1 from 5 to 11 Hz (the puppet's 5 to the replay's 11), 1 -> 0.5 from 11 to 15, 0.5 -> 0 from 15 to 20.
- **coordination** `coord` = the mean of four credits, for the middle pair (lm-rm) and the front pair (lf-rf), `leg_pairs.pair()`'s own
  numbers: both-off / independence (1 at <= 0.5, 0 at >= 1, linear) and the antiphase share (1 at >= 0.75, 0 at <= 0.5, x min(1, n / 20)).
  both credits of a pair x min(1, the pair's fewer lifts / 40) and 0 when either leg has fewer than 5 lifts (leg_pairs' own floor):
  rare lifts make both statistics noise.
- **progress** `prog` = forward speed along the heading (the puppet reader's `vf`), / 2 mm/s, capped at 1.
- raw = 0.20 stand + 0.25 step + 0.30 coord + 0.25 prog (0-1).
- **penalties, as a factor** (1 - min(0.9, sum)): the body (thorax / abdomen / head) on the floor with a mean > 1 uN: 0.5 (the hard one);
  0.2 x the fraction of leg motor neurons whose mean rate is outside 0.5-60 Hz; 0.1 per logged type (every leg MN type, every gained
  interneuron type) above 200 Hz per cell, capped at 0.3.
- **a fall** (body mean > 3 uN): the score is 0.02 x raw, whatever else.
- a candidate the prefilter rejects scores -0.25 to -0.6 (below any body score, ordered by how far outside 0.5-60 Hz the leg MNs sit, and
  -0.1 more for a runaway cord), and a failed or crashed body run scores -0.25 for that seed.

**the prefilter:** reject before the body if the leg motor neurons' pooled mean rate on the cord (per cell, after the warm-up) is under
0.5 or over 60 Hz, or the whole cord runs over 10 Hz per cell (the file's vector: 0.85 Hz per cell, leg MNs 2.4 Hz).

**the lift rule, the one thing to decide before the full solve.** the brief's rule is leg_pairs.py's (smoothed 21 ms, <= 0.05 uN for >= 50
ms), and it cannot see a real fly's swing, which lasts 36-42 ms: the kinematic replay (10.4 mm/s, an 11 Hz tripod) reads 0-2 lifts per
second per leg under it. `--lift-rule fine` uses the replay reader's rule (5 ms, >= 10 ms) instead. the yardsticks scored by this objective
(raw, before the physiology factor, which does not apply to scripted or replayed bodies):

| run | rule standard: raw (stand / step / coord / prog) | rule fine |
|---|---|---|
| the kinematic replay (`kin_replay`) | 0.51 (0.99 / 0.14 / 0.09 / 1.00) | **0.98** (0.99 / 0.96 / 0.95 / 1.00) |
| the puppet, 5 Hz, 50 / 25 (`puppet_5_sw50`) | **0.83** (0.77 / 0.70 / 1.00 / 0.80) | 0.87 (0.77 / 0.87 / 1.00 / 0.80) |
| the puppet, 8 Hz, 100 / 50 (`puppet_8`) | 0.82 | 0.84 |
| tripod2 at 11 Hz, 50 / 25 (`puppet2_11_sw50`) | 0.41 | 0.70 |
| the connectome, DNg100 (`i7_x1_s11`) | 0.25 (1.00 / 0.11 / 0.02 / 0.05) | 0.35 (1.00 / 0.46 / 0.08 / 0.05) |
| row 28, lift x5 (`gain_free_x5`) | 0.29 | 0.45 |
| row 30, lift x3 + release x5 (`comp_free_l3_r5`) | 0.27 | 0.36 |

under the standard rule the puppet outscores the living fly's own legs; under the fine rule the order is right (replay > puppet >
connectome), and the connectome's bouncing reads as a few hertz of "lifts" that the standard rule ignored. the default is the brief's
(standard); the recommendation is `--lift-rule fine`, so that the solve is aimed at the replay and not at the puppet's slow gait.

## cost, measured (09-23, `--time-one`, the file's vector, 2 slots, another batch of body runs sharing the box)

- the cord prefilter: 5 s (10 s simulated; 0.85 Hz per cell).
- one body run: 97-100 s for 20 s simulated (0.2x real time) with 4 numba threads.
- one evaluation (the prefilter, then two seeds in parallel): **106 s wall.**
- the box: 16 cores (`nproc`). default `--concurrent 4 --threads 4` (4 x 4 = 16; `world/fastlif.py` caps numba at 8 and says 8 beat 16).
- a 1,000-evaluation solve at 4 slots: 1,000 x (2 x ~100 + 5) / 4 = **~14 h** if four runs do not slow each other, ~18 h if they do by a
  third; 125 generations of 8, ~7 min each. prefilter rejections are cheaper (5 s) and shorten it.
- disk: ~6 MB of arrays per evaluation; `--keep-arrays 10` keeps the arrays and CSVs of the best ten and deletes the rest after each
  generation (the reads stay in `evals.jsonl`).

**the smoke test (09-23, `--name smoke --popsize 4 --generations 1 --hours 0.3 --concurrent 2`; SOLVER, not a result):** one generation,
417 s wall (8 body runs at 85-112 s, 4 prefilters at 12-15 s, 2 slots beside another batch's body run); all four passed the prefilter
(leg MNs 1.7-6.4 Hz, the cord 0.82-0.88 Hz per cell). the file's own vector (`--time-one`) scores +0.206 (stands on 10.0 uN, lifts only the
right middle leg, 0.1 mm/s).

| candidate | lift | release | hold13A | cmdinh | levinh | subnet | levMN | G | DNg100 | score | what the body did (s11 / s12) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| c00 | x3.86 | x0.60 | x0.64 | x0.41 | x2.05 | x0.28 | x4.27 | 0.43 | 108 | **+0.230** | feet 5.9 / 6.2 uN, coxae 3.0 / 2.6, body 1.0 / 1.0 (the touch penalty on s12); lifts 0.4-3.6 per s on every leg; +1.07 / +0.86 mm/s; 14-19 leg MNs over 60 Hz |
| c02 | x1.04 | x1.62 | x0.40 | x2.59 | x2.12 | x1.52 | x2.12 | 0.44 | 97 | +0.192 | stands (9.7 / 9.4); the right middle leg lifts, 2 per s; 0.1 mm/s |
| c01 | x0.81 | x3.37 | x0.25 | x0.76 | x0.73 | x2.57 | x0.40 | 0.55 | 79 | +0.170 | stands (10.0 / 9.9); no lifts |
| c03 | x0.46 | x0.80 | x1.55 | x0.56 | x0.72 | x0.56 | x0.50 | 0.45 | 100 | +0.003 | falls on both seeds (body 4.5 / 4.2 uN) |

the plumbing, checked: the CSV writer reproduces rows 28's `ex_gain5.csv` exactly at lift x5; a deadline kill leaves the generation
pending with no stray processes, and the resume re-runs only its unfinished candidates and tells CMA; the pruning keeps the best K.

## how to run it and resume it

    uv run python experiments/solver/run.py --name s1 --hours 16 --lift-rule fine           # the full solve: popsize 8, 4 slots x 4 threads
    uv run python experiments/solver/run.py --name s1 --hours 16 --lift-rule fine           # resume: the same line (the fixed settings are checked)
    uv run python experiments/solver/run.py --name t1 --time-one --concurrent 2             # one evaluation at the file's vector, timed

- `--hours` is a hard budget for the invocation: a generation that would not finish (by the mean of this invocation's generations) is not
  started, and one that overruns is killed at the deadline and left pending (`pending.json`); a resume re-evaluates only its unfinished
  candidates and tells CMA the same solutions (the post-ask state is pickled in `es.pkl`).
- `--generations N` stops after N generations in total; `--popsize`, `--sigma0`, `--seeds`, `--seconds`, `--cord-seconds`, `--lift-rule`,
  `--cord-runaway-hz`, `--cma-seed` are fixed per run name (a resume with other values refuses).
- it stops only the processes it started (its own subprocesses, on the deadline or Ctrl-C).
- outputs, in `experiments/solver/runs/<name>/` (git-ignored): `log.txt` (a line per evaluation with every read, `SOLVER <name> |`),
  `evals.jsonl` (every evaluation: the vector, the parameters, the cord reads, both seeds' reads and score components, the timings),
  `gen_NNN.json` (the population, its scores, CMA's mean and step), `SOLVER_<name>_best.csv`, `SOLVER_<name>_best_flags.txt` (the best
  vector's body command line), `best.json`, `config.json`, `es.pkl`, and `evals/<gNNN_cNN>/` (the CSV, the cord and body logs and arrays).

## reading the best vector (the point)

the vector is the answer, read against the file: each gain is how far the size path had to move that set's excitability, in octaves
(log2 g), for the body to score. read it as a map, not a fly:

- **a gain near 1 (|log2 g| < 0.5)** the file's weights are not what stands between this cord and the objective on that set.
- **a large gain on a set whose cells lock phase-correct and starved on the listening rig** (lift, release): the distance the file's
  weights sit from a step, in the units rows 28 and 30 used; compare with their x3 / x5 / x10.
- **a gain far below 1 on the hold side or the inhibitors** (hold13A, cmdinh, levinh): the solver is releasing the lid the day-two reads
  found (the levators' inhibitors, the 13A hold); how far is the size of the lid.
- **the pic and the command:** where G and DNg100's rate settle says whether the flexors' own tone and the command's strength matter.
- **a gain pinned at a bound (0.25 or 16):** the set wanted more than the search allows; the distance is at least that.
- then check the best vector the way every gain has been checked: the listening rig (`--kin-drive`: do the gained cells still lock in the
  right phase), the deaf twin, both claw labellings, a third seed, and the puppet's and the replay's numbers side by side. the best CSV and
  its body command line are in the run's directory for that.

## the caveat

a cord fitted until the body walks is a puppet by construction: the solver moves excitability on nine named sets until a score built from
the replay's and the puppet's numbers goes up, so whatever gait it finds was put there by the fit, not found in the file. its output is
never a result and is never reported as the connectome walking. what it can give is a comparison point beside the puppet and the replay:
the vector that got there, read set by set against the file's own weights (how far, which direction, which sets did not need to move), and
every gain it finds is checked on the listening rig before anything is said about it. the objective's weights, the lift rule and the size
path's three-terms-at-once are our choices, stated above, and each one shapes the answer.
