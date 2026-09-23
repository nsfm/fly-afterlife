# interleg: the neural coupling between legs (09-23)

the lift read left six five-hertz reflex oscillators, one per leg, each closed through its own senses and the cord, and uncoupled
(`SEAM.md`, "the movement senses on his own lifts" and "the control"). this file is the next question as data: what the literature
knows about the cells that couple legs, which cells in our file would carry one leg's signal to another, and the read on the body
that would say whether they do. no run here.

tags: **(M)** measured in the fly; **(I)** inferred in the fly from a connectome or a model; **(C)** another insect; **(D)** ours.

PART1_PLACEHOLDER

## 2. the census: cells in our file that carry one leg to another (D)

`scripts/interleg_census.py` (reproducible, prints the table; `uv run python scripts/interleg_census.py`), `world/interleg.csv`
(one row per cell: type, bodyId, hemilineage, side, nt, sign, from_legs, to_legs, interleg_syn, leg_out_syn, mn_direct_syn,
total_out_syn, frac_interleg, contra / ipsi / diag syn, top_pairs, class).

**method.** the file is `brain_cord.npz`. legs of the 373 leg motor neurons from `world/legmn.npz`; legs of 3,567 sensory cells from
`world/leg_senses.csv`. a **premotor** cell is any non-sensory, non-motor cell with >= 10 synapses onto leg MNs (5,384); it belongs to
a leg only if >= 80 % of its MN output is on that leg (4,639 such leg-local cells). every other cell's leg neuropil is inferred only
from which leg's MNs, premotor cells and sensory cells its synapses touch. for each intrinsic cell X:

- out[j] = synapses onto leg-j MNs + synapses onto leg-j premotor cells
- in[i] = synapses from leg-i sensory cells + from leg-i premotor cells
- flow[i -> j] = in[i] / sum(in) x out[j]; **interleg = the flow with i != j** (synapses of X's leg output that carry another leg's input)
- pairs: **contralateral** = same segment, other side (lf-rf, lm-rm, lh-rh); **ipsilateral** = same side, other segment; **diagonal** =
  both. a cell or type is contralateral / ipsilateral when >= 70 % of its interleg flow is that kind, else "both".

the multi-leg premotor cells (745) carry no leg of their own: letting them carry their mixed leg vector smears everything downstream
into "interleg" (the first pass did; `--pm-local 0` reproduces it; IN17A001, a per-segment rhythm cell, came out 8th). the ranking
is stable at 0.6 / 0.8 / 0.9: the same top 12 in a slightly different order.

**the whole.** 9,096 ranked cells, 1.68 M interleg synapse-units: **ipsilateral 49 %, contralateral 30 %, diagonal 22 %.** by
hemilineage the split is as the developmental classes predict: **19A 85 % ipsilateral, 03A 79 %, 09A 72 %, 20A/22A 71 %; 14B 69 %
contralateral, 19B 56 %, 18B 46 %**; 07B and 08B carry the most diagonal (41 %, 47 %). the coupling is mostly onto premotor cells, not
motor neurons: of the top 40 types, all but three (IN12A001 27 %, IN19A010 40 %, IN03A001 23 %) put < 20 % of their leg output directly on MNs.

**top 40 types by interleg synapses** (n = cells of the type in the file; sign from the file's transmitter; frac out = interleg /
all output; frac leg = interleg / leg output; MN % = direct MN share of leg output; pairs = the per-cell top pairs, mirrored,
with the number of cells showing each):

| # | type | hl | n | sign | interleg | frac out | frac leg | MN % | class | pairs |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | IN07B002 | 07B | 6 | +ACh | 26,078 | 0.66 | 0.83 | 17 | both | h->m ipsi, h->m diag, f->h diag |
| 2 | IN12B002 | 12B | 6 | -GABA | 25,047 | 0.39 | 0.80 | 2 | both | m->h ipsi, m->h diag, m<->m contra |
| 3 | IN19A006 | 19A | 4 | +ACh* | 16,678 | 0.79 | 0.89 | 1 | ipsi | f->m, m->h |
| 4 | IN12A001 | 12A | 4 | +ACh | 16,057 | 0.62 | 0.76 | 27 | both | m<->m contra, m->h diag, m->h ipsi |
| 5 | IN07B006 | 07B | 6 | +ACh | 15,862 | 0.66 | 0.84 | 16 | both | m->h diag, h<->h contra, f->h diag |
| 6 | IN07B001 | 07B | 4 | +ACh | 15,559 | 0.58 | 0.91 | 7 | both | m->h diag, m<->m contra, f->h diag |
| 7 | IN07B007 | 07B | 6 | -Glu | 12,180 | 0.51 | 0.88 | 3 | both | h<->h contra, h->m ipsi, h->m diag |
| 8 | IN01A009 | 01A | 4 | +ACh | 12,091 | 0.77 | 0.88 | 3 | ipsi | f->m, m->h, f->h |
| 9 | IN19A010 | 19A | 4 | +ACh* | 11,318 | 0.83 | 0.98 | 40 | ipsi | f->m, m->h |
| 10 | IN02A003 | 02A | 4 | -Glu | 11,311 | 0.66 | 0.97 | 7 | ipsi | h->m, m->f |
| 11 | IN19A012 | 19A | 4 | +ACh* | 10,599 | 0.76 | 0.89 | 13 | ipsi | f->m, m->h |
| 12 | IN03A001 | 03A | 4 | +ACh | 9,721 | 0.67 | 0.96 | 23 | ipsi | h->m, m->f |
| 13 | IN03A009 | 03A | 4 | +ACh | 9,650 | 0.65 | 0.70 | 1 | ipsi | m->h, f->m |
| 14 | IN00A002 | 00A | 3 | -GABA | 9,570 | 0.55 | 0.78 | 2 | both | h->m diag, h->m ipsi, h<->h contra |
| 15 | IN17A007 | 17A | 6 | +ACh | 9,531 | 0.42 | 0.52 | 9 | ipsi | m->h, f->m |
| 16 | IN01A010 | 01A | 4 | +ACh | 9,276 | 0.58 | 0.95 | 1 | ipsi | m->h, f->m |
| 17 | IN11A003 | 11A | 8 | +ACh | 9,146 | 0.75 | 0.84 | 9 | ipsi | f->m, m->h, h->m |
| 18 | IN19A009 | 19A | 4 | +ACh* | 8,936 | 0.69 | 0.93 | 7 | ipsi | m->h, f->m |
| 19 | IN19B021 | 19B | 4 | +ACh | 8,772 | 0.59 | 0.72 | 5 | contra | h<->h |
| 20 | IN06B008 | 06B | 6 | -GABA | 8,568 | 0.44 | 0.78 | 4 | both | h<->h contra, h->m ipsi, h->m diag |
| 21 | IN19A014 | 19A | 4 | +ACh* | 8,539 | 0.72 | 0.85 | 8 | ipsi | h->m, m->f |
| 22 | IN17A001 | 17A | 6 | +ACh | 8,532 | 0.16 | 0.20 | 1 | both | m->h ipsi, h<->h contra |
| 23 | IN19B010 | 19B | 2 | +ACh | 8,271 | 0.74 | 0.99 | 10 | both | f->h diag, f->m diag, f<->f contra |
| 24 | IN19A019 | 19A | 4 | +ACh* | 8,187 | 0.60 | 0.69 | 6 | ipsi | h->m, m->f |
| 25 | IN01A002 | 01A | 2 | +ACh | 8,103 | 0.78 | 0.94 | 3 | both | f->h ipsi, f->h diag, f->m diag |
| 26 | IN14B005 | 14B | 4 | -Glu | 7,825 | 0.76 | 0.95 | 9 | contra | h<->h, f<->f |
| 27 | IN12A003 | 12A | 4 | +ACh | 7,790 | 0.67 | 0.87 | 13 | ipsi | m->h, f->m, f->h |
| 28 | IN19B011 | 19B | 4 | +ACh | 7,581 | 0.69 | 0.98 | 12 | both | f->m diag, f->h diag, f->h ipsi |
| 29 | IN01A005 | 01A | 4 | +ACh | 7,313 | 0.58 | 0.81 | 2 | ipsi | f->m, m->h |
| 30 | IN18B021 | 18B | 6 | +ACh | 7,262 | 0.53 | 0.65 | 6 | contra | h<->h |
| 31 | IN09A004 | 09A | 4 | -GABA | 7,048 | 0.59 | 0.67 | 16 | ipsi | h->m, m->f |
| 32 | IN07B012 | 07B | 4 | +ACh | 6,863 | 0.69 | 0.93 | 9 | both | m->h diag, f->h diag, f->m diag |
| 33 | IN09A009 | 09A | 4 | -GABA | 6,847 | 0.74 | 0.88 | 1 | ipsi | h->m, m->f |
| 34 | INXXX062 | ? | 4 | +ACh | 6,838 | 0.64 | 0.88 | 1 | both | h->f ipsi, h->m ipsi, h->f diag |
| 35 | IN08B004 | 08B | 4 | +ACh | 6,625 | 0.38 | 0.79 | 9 | both | m<->m contra, m->h diag, m->h ipsi |
| 36 | IN07B009 | 07B | 4 | -Glu | 6,527 | 0.66 | 0.94 | 5 | both | h->m diag, h<->h contra, m<->m contra |
| 37 | IN19A001 | 19A | 6 | -GABA | 6,405 | 0.18 | 0.19 | 2 | ipsi | m->h, m->f, h->m |
| 38 | INXXX003 | ? | 2 | -GABA | 6,348 | 0.52 | 0.90 | 3 | both | f->m ipsi, f->h diag |
| 39 | GFC2 | - | 10 | +ACh | 6,251 | 0.38 | 0.60 | 8 | contra | m<->m contra, m->f, m->h |
| 40 | IN19A018 | 19A | 2 | +ACh* | 6,238 | 0.73 | 0.89 | 1 | ipsi | h->m, h->f |

**per pair** (the flow summed over cells for that pair only; the share is of all flow for the pair):

- **m <-> m (the pair that lifts most in the body):** 111 k (between f <-> f and h <-> h), and diffuse: no type carries more than
  4 %: GFC2 4,910, IN12B002 2,763, IN18B031 2,733, IN01A054 2,702, IN12A001 2,360, INXXX083 2,311, IN07B002 2,008.
- **f <-> f:** 92 k: INXXX036 4,012, IN14B011 3,282, IN19B005 2,397, IN01A040 2,267, IN14B005 2,038, IN14B010 1,834.
- **h <-> h:** 294 k, the thickest: IN19B021 7,685, IN18B021 6,475, IN07B006 5,341, INXXX115 5,181, IN14B005 4,774, IN19B004 4,308.
- **f <-> m ipsilateral:** 262 k: IN19A006 8,092, IN19A010 5,567, IN01A009 5,256, IN03A009 4,823, IN19A012 4,729, IN19A009 4,472.
- **m <-> h ipsilateral:** 449 k: IN19A006 8,230, IN03A001 6,351, IN12B002 6,149, IN02A003 6,143, IN01A009 5,765, IN19A010 5,390.

**where the coupling lands.** the published rhythm-loop cells (Pugliese 2026, Sapkal 2026; `walking_review.md` §0-1) take 4-11 % of
their input from top-40 cells whose main input is another leg: IN17A001 4.9 %, INXXX466 3.8 %, IN16B036 4.2 %, IN19A007 3.7 %,
IN03A006 4.8 %, INXXX464 4.7 %, **IN12B003 11 %, IN09A002 9.6 %**. the ipsilateral chain enters the neighbour's loop directly:
IN19A006 -> INXXX466 657, -> IN19A007 502, -> INXXX464 538, -> IN17A001 323 synapses. **IN19B003** (19B, ACh; by wiring leg-local,
so absent from the ranking) is a convergence node: IN12B002 1,219, IN19A006 1,168 and IN19B021 767 synapses in (10 % of its input from
other-leg top-40 cells), and it is the largest 19B input to the local 19A stance inhibitors (IN19B003 -> IN19A016 1,495, -> IN19A001
870, -> IN19A007 583; IN19B012 -> IN19A007 1,245). 19B -> 19A is 24,183 synapses in all (6 % of 19B output), 82 % of it onto
leg-local 19A premotor cells. **this is Sapkal 2026's "19B commissural -> 19A local" motif in our file, with named cells.**

**open signs.** the ipsilateral 19A intersegmental cells (IN19A006, 009, 010, 012, 014, 018, 019; 26 cells, marked * above) are
predicted **cholinergic at 0.95-0.97 confidence** (MaleCNS v1.0 `body-neurotransmitters`, no ground truth), while the leg-local 19A
cells are GABAergic with ground truth, and 19A is a GABAergic hemilineage (Lacin et al. 2019, *eLife* 8:e43701). either these cells
are misassigned to 19A, or they are a real exception, or the prediction is wrong. the sign of the strongest ipsilateral coupling in
the file turns on it. 44 of the file's 544 IN19A cells are ACh; these 26 are most of them.

**what could not be assigned.**
- 525 intrinsic cells with >= 20 synapses of leg output and **no leg input** (driven only by DNs, ANs, multi-leg premotor cells or
  sensory cells without a leg): 41,279 leg-output synapses. they could couple legs as relays of a shared drive, but the census cannot
  say from which leg.
- the 745 **multi-leg premotor cells** (< 80 % of MN output on one leg) carry no leg into the census; they are ranked themselves.
- **sensory cells with no leg:** 2,579 in `leg_senses.csv` (proprio 775, unknown 729, tactile 655, gustatory 385, chemo 35), mostly
  not in a leg nerve by annotation. their input to interneurons is not counted.
- **ascending neurons** are excluded as candidates (only `vnc_intrinsic` is ranked); they appear as premotor cells where they touch
  MNs. midline (side M) cells are ranked; "side" in the file is soma side and says nothing about neuropil.
- **soma side is not neuropil side.** a commissural cell (19B, 18B, 14B) whose soma is on the left and whose whole arbor is on the
  right is leg-local by wiring (IN19B003). the census uses wiring, which is the right thing for coupling and the wrong thing for
  hemilineage-level anatomy.
- **sign is not effect.** a glutamatergic cell (02A, 14B, 07B-Glu) is assumed inhibitory (GluCl) by the file's sign; fly glutamate can
  be excitatory. an excitatory cell onto an inhibitory premotor cell of the other leg inhibits that leg. the table gives the first
  synapse's sign only.
- **GFC2** (10 cells; the name reads as MANC's giant-fibre-coupled class, not checked against the source) is the top m <-> m
  contralateral type: if it is escape-circuit wiring it is probably not walking coupling; kept in the table because the rule put it there.

## 3. the proposed read on the body (D)

**the question:** the six bouts are uncoupled. are the cells that would couple them **silent** (the coupling is in the file and not
running), **running but weak** (they fire, and the other leg does not follow), or **running and cancelling** (both signs arrive)?

**arm 1: the log (no change to the run).** the bouts arm of record (`lift_s11`: the full stack under the recorded DN population, 30 s,
seeds 11 / 12 labels swapped, 11 as printed) with
`--log-x IN07B002,IN12B002,IN19A006,IN12A001,IN07B006,IN07B001,IN07B007,IN01A009,IN19A010,IN02A003,IN19A012,IN03A001,IN19B021,IN14B005,IN18B021,IN19B003,GFC2,IN18B031,IN01A054`
plus the loop cells already logged in the lift read (IN17A001, INXXX466, IN09A002, IN13A002, ...). the read, as `lift_read.py`
does it but across legs (a new reader; `lift_read.py` is lf only and stays untouched):

- triggers on **lm** lifts (72 / 63 lifts, the most regular leg); read the logged cells split by bodyId into leg via
  `world/interleg.csv` (`from_legs` / `to_legs`): do the cells whose input is lm fire in lm's lift window (they carry the signal)?
  do the loop cells of **rm** (and of lh, lf) move in the 100 ms after an lm lift?
- the same triggered on lf (f -> m ipsilateral) and on rm (the mirror).
- the phase measures of the lift read on each pair: onset cross-correlation, the other leg's onsets in quarters of this leg's
  in-bout cycle, both-off fraction against independence.
- expected from the census, not claimed: IN19A006 / IN19A010 / IN19A012 are the f -> m and m -> h path, IN19B021 / IN18B021 the h <-> h
  path, and **m <-> m has no strong cell**; if any pair couples first it should be the hind or the ipsilateral neighbours, not the
  middle legs, which are the ones that lift.

**arm 2: silencing (`--silence`), only if arm 1 shows the cells firing and locked to the other leg.** if they are silent, silencing
them tests nothing (the legs are already uncoupled; a null is guaranteed) and the question becomes what would wake them.
- `--silence` (sets printed by the script, 51-56 cells each, no comma-named types):
  - **ipsi12:** IN19A006, IN01A009, IN19A010, IN02A003, IN19A012, IN03A001, IN01A010, IN03A009, IN11A003, IN19A009, IN19A019, IN19A014
  - **contra12:** IN19B021, IN14B005, IN18B021, INXXX115, GFC2, IN14B010, IN19B004, IN18B006, INXXX036, INXXX095, IN19B035, IN14B011
  - **top12:** IN07B002, IN12B002, IN19A006, IN12A001, IN07B006, IN07B001, IN07B007, IN01A009, IN19A010, IN02A003, IN19A012, IN03A001
  - **hub:** IN19B003 alone (6 cells), and IN19B003 + IN19B012 (the 19B -> 19A stance entry).
- **measure:** the pairwise phase measures above (the coupling), and **each leg's own bout** (lifts, in-bout gap, cv): a set that kills
  the per-leg bout confounds the arm, because `--silence` is by type and removes the cell in every hemineuromere, including its
  within-leg part (IN17A001 and IN12B002 have 20-80 % within-leg flow).
- **the control:** 12 intrinsic types drawn at random (seed 0) from types with >= 20 synapses of leg output and outside the interleg top
  200, matched to the top12 set in cell count (+- 4); three draws, printed by the script (`control0-2`, 57 cells each). a coupling claim
  needs the named set to move the phase measures and the three controls not to, at the same seeds.
- beside every arm: both claw labellings. `--freeze-mn` is not a control here: the bouts die with the muscles, so there is no rhythm
  left to have a phase. the central question (a coupling with no legs moving, as Sapkal 2026 find in the animal) needs a central rhythm
  first, and the cord alone has never shown one.
