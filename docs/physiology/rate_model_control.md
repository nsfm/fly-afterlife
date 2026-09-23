# the positive control: Pugliese 2026's rate model on our cord file

Started 2026-09-22. Script: `experiments/rate_model.py` (the equation, every parameter and its source in its docstring). Question: does
Pugliese et al.'s rate model (bioRxiv 10.1101/2025.09.12.675944 v2; PMC13142387; `docs/research/sources/pugliese_2026_connectome_cpg.md`,
`walking_review.md` §0, §7) oscillate on `brain_cord.npz`? If yes, the wiring is cleared and the spiking engine is the variable; if no, the
difference is in our cut or our signs.


## what was taken from the paper (Methods, PMC full text, read 2026-09-22)

- equation: tau_i dr_i/dt = max(r_max,i tanh(a_i (r_max,i I_i + b sum_j w_ij r_j - theta_i)), 0) - r_i. rectified.
- tau ~ N(0.020, 0.002) s, r_max ~ N(200, 10) Hz, theta* ~ N(7.5, 0.6), a* ~ N(1, 0.1), truncated at zero, redrawn per cell per replicate.
- **size scaling form: a_i = a*_i / s_i, theta_i = theta*_i * s_i**, s_i = median-normalised size (volume in MANC / mCNS). larger cell =
  less excitable. our file has no volume: **substitution, s = input synapse count** (from `brain_whole.npz`, so the DNs keep the brain inputs
  the headless cut removed) (`--size insyn`), or in + out (`--size total`), or none.
- b = 0.03 for all; "increasing bACh to 0.045 still produced viable oscillatory dynamics, but larger deviations resulted in either runaway
  network activity or insufficient neuron recruitment."
- **DNg100 input: "Istim = 250 in MANC, 150 in FANC, and 400 in the two CNS datasets"** (MaleCNS: 400), onset at 20 ms, 1 s runs, r(0) = 0,
  Dopri5. as written the input enters as r_max * I, so anything above ~0.1 (size off) or ~1.1 (size on: DNg100's s ~ 27, theta ~ 205)
  saturates DNg100; we swept I over decades anyway.
- network: front-leg MNs + every non-DN cell presynaptic to them ("premotor") + every DN presynaptic to a premotor cell. MANC: 4,604 cells.
  **ours (`--subnet front`): 3,109 cells = 1,026 DNs + 133 front MNs + 1,950 premotor, 98,941 edges.**
- rhythmicity score: from MN autocorrelations, peaks with prominence 0.05; exact formula not given in the text read; ours is an approximation.

## the three-cell loop is in our file

DNg100 -> IN17A001 (E1; contralateral: DNg100 L drives the R-side E1s, 100-167 synapses) -> INXXX466 (E2, 328-527) -> IN16B036 (I1, 27-129)
and IN19A007 (I2, 129-234) -| IN17A001 (I1: 439-847; I2: 228-408). three E1 / E2 / I1 / I2 per side (T1-T3). E2 -> I2 is stronger than
E2 -> I1 in our file (the paper: I2 is the FANC alternative). **the right T1 IN16B036 is not in the front subnetwork** (no >= 5-synapse
edge onto a front MN), so the paper's construction on our file leaves the right loop with I2 only.

## results

All runs: Heun, dt 0.5 ms, readout after 0.5 s, DNg100 both sides unless said, b = 0.03, I = 400 (the paper's CNS value) unless said.
"pro" / "rem" = summed rate of the front-leg promotor / remotor pool. "sat" = cells above 150 Hz after 250 ms.

### 1. the paper's front-leg network on our file (`--subnet front`, 5 s, seeds 0-2): no rhythm, size on or off

| size | cells active / sat (of 3,109) | coxa pools, 5-20 Hz peak / 1-40 Hz global peak | pro-rem xcorr | E1 IN17A001 L / R | E2 INXXX466 L / R | I1 IN16B036 L | I2 IN19A007 L / R | IN09A002 L / R |
|---|---|---|---|---|---|---|---|---|
| insyn | 1,592-1,782 / 1,249-1,470 | peaks sit at the 5 Hz band edge under a 1-3 Hz global peak; one pool of each leg typically **silent** (0 Hz) and the other **tonic** (sd/mean 0.00-0.5) | no consistent extremum (-0.47..+1.00, lags scattered over +-150 ms; +-1.00 = a flat pool) | 201 / 130 (s0), 130 / 17 (s1), 187 / 0 (s2) | 210 / 196, 0 / 28, 0 / 0 | **0** in all seeds | **0 / 0** in all seeds | 185-204 / 198-212 (pinned) |
| total | 1,609-1,642 / 1,355-1,491 | same: global peaks 1-4 Hz | -0.79..+0.95, scattered | 185 / 5, 163 / 51, 66 / 104 | 15 / 6, 0 / 55, 20 / 115 | 0-4 | 0 / 0 | pinned ~200 |
| none | 1,587-1,609 / 1,448-1,489 | same: global peaks 1-4 Hz | -0.36..+0.30, scattered | 7 / 151, 119 / 89, 73 / 73 | 1 / 154, 78 / 102, 13 / 77 | 0 | 0 / 0 | pinned ~200 |

(mean rates in Hz; the E1 / E2 rates are means of slow 1-3 Hz switching, sd 25-90 Hz, not a rhythm.) the autocorrelation rhythmicity score
(our approximation) is 0.00-0.21 everywhere. DNg100 on one side only (L, the paper's screen condition): the same picture (seeds 0-1).
the state is a runaway: **about half the network is pinned at r_max and the rest is silent**, and it stays there. the three-cell loop is
caught on the wrong side of it: the two excitors (and IN09A002) pinned or slowly switching, **both inhibitors silenced** (IN16B036 L gets
-1,531 of inhibition against +318 of excitation, mostly from IN19A002; IN19A007 gets -5,900..-11,586 against +2,000..+3,500, from
IN19A002 / IN19A005 / IN19A008 / IN26X001, all themselves pinned).

### 2. the sweeps that did not rescue it (front subnet, 3 s, seed 0 unless said)

- **DNg100 input** 0.01, 0.03, 0.1, 1, 1.2, 2, 400 x size none / insyn / total: silent below the DNg100 threshold (0.1 without size, ~1.1
  with size); every suprathreshold value falls into the same runaway, whose cell count does not depend on I (the kick matters, not its
  size). with size off, the runaway even survives DNg100 being silenced by the other DNs (DNge129, DNge099 inhibit it) after the kick.
- **b** 0.003, 0.005, 0.01, 0.015, 0.02, 0.03 (size insyn and none, I 0.1 / 1 / 400): 900-1,800 cells active at every b; at b = 0.003 fewer
  cells are pinned but the pools are still silent-or-tonic.
- **a separate inhibitory b** (0.045, 0.06, 0.09, 0.15 against b_ACh 0.03; 2 seeds): 1,350-1,690 active; no in-band pool peak.
- **size proxy**: MaleCNS body-stats PSD counts (all partners, no floor) correlate r = 0.97 (log) with our input-synapse proxy, so they
  would change nothing; a compressive proxy (insyn^0.5, insyn^0.75, as a stand-in for volume growing slower than synapse count): same
  runaway.
- **cutting the DN recurrence**: no inputs to any DN (DNs as pure inputs, the headless reading): 899 active / 763 pinned, loop inhibitors
  still 0; only DNg100's outputs kept among the DNs: 1,210 / 1,063. the runaway lives in the cord's interneurons, not in the DNs.
- **the whole cord** (`--subnet all`, 23,074 cells, seeds 0-2, size insyn / total / none): 9,900-11,000 active, 8,900-9,900 pinned; here
  the loop's inhibitors are the ones pinned (IN16B036 80-190 Hz, IN19A007 50-190) and the excitors low; every loop cell's spectral peak
  is 1.2-4.4 Hz (slow switching), none in 5-20 Hz; coxa pools the same.

### 3. the loop itself oscillates on our weights

The loop cells cut out of the front subnetwork (sizes still normalised to the subnetwork's median; DNg100 both sides; 3 s):

| cells | size | I | result |
|---|---|---|---|
| DNg100 x2 + E1 x2 + E2 x2 + I1 (L only) | insyn | 1, 400 | **left loop oscillates at 15.2-15.6 Hz**: E1 9 +- 7, E2 16 +- 14, I1 107 +- 34 Hz; right loop (no I1) pinned at ~195 |
| same | none | 0.1, 1, 400 | left loop 15.2 Hz, same rates (so their size-off negative control does not apply to the bare loop) |
| + I2 (IN19A007) both sides | insyn | 400 | **both loops oscillate**: left 10.0-10.4 Hz, right 17.6 Hz (I2 108 +- 20 / 126 +- 31 Hz) |
| + I2, + the 22 front coxa promotor / remotor MNs | insyn | 400 | loops at 17.2 Hz; the lf promotor pool is modulated at 17.2 Hz (404 +- 25, spectral ratio x1,984); the remotor pool is pinned |
| + I2 | none | 0.1-400 | right loop 18-18.8 Hz, left pinned (I2 L at 198) |

the paper's linearised minimal circuit gives ~14 Hz and its network 7-15 Hz; ours gives 10-18 Hz from the same three types.

**growing outward** (loop + its k strongest partners in the front subnetwork, by synapses to / from the loop, size insyn, I 400, seeds 0-2):
E1 keeps an in-band peak (7-20 Hz) at k = 0, 5, 10, 20, 40, 80 in all three seeds; at k = 160 it is gone in all three (74 of 169 cells
pinned); k = 320 one seed of three; k = 640, 1,280, all: none. the partners added between 80 and 160 include the coxa MNs and a run of
19A / 13B / 14A / 17A / 01A interneurons and DNs (IN19A016, IN19A005, IN19A008, INXXX468, IN17A025, IN13B078, IN14A009, DNg97, DNge042).

## verdict

**On our wiring file, Pugliese's rate model does not oscillate in the network they simulate** (front-leg DNs + MNs + premotor, or the
whole cord), with size scaling on or off, over three decades of DNg100 input, b from 0.003 to 0.03, inhibition up to 5x, and three
seeds: the network falls into a runaway where about half its cells are pinned at r_max, the loop's inhibitors are silenced (front) or
pinned (whole cord), and the coxa pools are silent or tonic with only 1-4 Hz wander. **But the rhythm generator is in our file and works**:
DNg100 -> IN17A001 -> INXXX466 -> IN16B036 / IN19A007 -| IN17A001, cut out with our weights and signs, oscillates at 10-18 Hz under
their equation and parameters, drives the lf promotor pool at 17 Hz, and survives the addition of its 80 strongest partners before the
embedding swamps it. So the question "wiring or engine?" does not get the clean answer the control was meant to give: the loop's wiring
and signs are cleared, the spiking engine is not the only variable, and the failure is in how the rest of our cut embeds the loop under
this model. Not separable from here: (a) our size proxy (synapse counts) against their volume, which is the paper's stated necessary
ingredient and which we cannot reproduce without the MaleCNS volumes (not in the public flat-connectome files; body-stats has only
synapse counts); (b) their subnetwork being larger (MANC 4,604 cells / 3.8 M synapses against our 3,109 / 2.0 M: our file at the same
5-synapse floor has 1,950 front premotor cells, the raw MaleCNS edges 2,201 at >= 5 and 3,527 at >= 3, MANC 3,142), which the paper's
MaleCNS replication would also have faced; (c) an implementation detail their text does not give (the input scaling r_max * I, which
saturates DNg100 at any I they list). Pugliese report a MaleCNS replication with I = 400, so on the same dataset their pipeline found a
rhythm where ours finds a runaway; until their code or the volumes are in hand, the difference is (a), (b) or (c), not our signs.

## with their sizes and their table

Added 2026-09-22, after their code and data landed at `ref/pugliese_cpg` (github smpuglie/Pugliese_cpg_2025). Everything above this
section was run with the equation **as the preprint prints it**; this section supersedes its verdict.

### what their code does that the preprint's equation does not say

`src/simulation/vnc_sim.py: rate_equation_half_tanh`:

    activation = max(fr_cap * tanh((a / fr_cap) * (I + W_weighted @ R - threshold)), 0);  dR/dt = (activation - R) / tau

- the gain inside the tanh is **a / r_max**, not a: the slope at threshold is a Hz per unit input (about 1), where the printed form
  gives a * r_max (about 200). the printed form is a 200x higher-gain network, and that is the runaway reported above.
- the input is **I, not r_max * I**: DNg100 at I = 400 is not saturated (15-20 Hz with their sizes).
- W is their signed synapse-count matrix, rows presynaptic; `reweight_connectivity` transposes it and multiplies positive entries by
  `excitatoryMultiplier` 0.03 and negative by `inhibitoryMultiplier` 0.03 (`configs/neuron_params/default.yaml`; tau 0.02 +- 0.002 s,
  a 1 +- 0.1, threshold 7.5 +- 0.6, frcap 200 +- 10). the optional glutamate multiplier is not set in the default config.
- `sim_utils.py: set_sizes`: size / nanmedian(size), NaN and 0 -> the median; a = a / size, threshold = threshold * size (as the text says).
- sim config: T 2 s, stimulus from 20 ms, Dopri5 rtol 2e-6; the MANC DNg100 config stimulates **one** DNg100 (`stimNeurons: [31]`, I 250).

`experiments/rate_model.py` now takes `--form code` (default: their code's activation) or `--form paper` (the printed one), `--wiring
ours|theirs` (their `W_20260210_vncRoisOnly.csv` + `wTable_...csv`, 4,310 MaleCNS front-leg cells), `--subnet theirs` (our cord table
on their bodyIds) and `--size theirs` (their `size` column, voxel volume, median ~1.0e9, bodyId-matched).

### (a) and (b): their equation, their sizes, I = 400, 3 s, seeds 0-2

| wiring | DNg100 driven | cells active / pinned | front MNs active | rhythm (loop cells and coxa pools) | promotor-remotor xcorr |
|---|---|---|---|---|---|
| **theirs** (4,310 cells) | L | 74-83 / 0 | **3-5**, all right leg (2 promotors, Tr flexor, +remotor / Fe reductor) | **11.6-14.8 Hz**: IN17A001 R 2.0-2.3 +- 1.4, INXXX466 R 5.1-5.5 +- 3.7, IN16B036 R 1.0-1.7, IN19A007 R 3.3-5.2 +- 3, IN09A002 R 4.2-5.0 +- 2; rf promotor pool 6-11 Hz summed, modulated at the same frequency | remotor mostly silent; where active (s1) -0.84 @ 18 ms / +0.95 @ 63 ms |
| theirs | R | 99-129 / 0 | **7-9**, left leg (2 promotors, remotor, 4 Tr flexors, +Sternal anterior rotator) | **10.8-11.2 Hz**, left loop (mirror of the above) | **-0.73..-0.86 at 65-118 ms, +0.97 at 75-109 ms**: antiphase-offset promotor / remotor |
| theirs | both | 183-197 / 0 | 10-12 | lf 10.8-11.2 Hz, rf 11.6-15.2 Hz | lf -0.73..-0.87 / +0.97 |
| **ours on their 4,242 bodyIds** | L | 111-138 / 0 | 4-5 (rf 2 promotors, remotor, Tr flexor; s0 two lf Tergotr.) | **14.0-14.4 Hz**: IN17A001 R 2.1-2.3 +- 1.4, INXXX466 R 5.0-5.8 +- 3, IN16B036 R 0.9-1.7, IN19A007 R 6.2-6.7 +- 2.5, IN09A002 R 6.4-9.3 +- 3; rf promotor pool 11-14 Hz summed | -0.77..-0.80 / +0.87..+0.90 where the remotor is on |
| ours on their bodyIds | R | 102-125 / 0 | 7-8, left leg (same types as theirs) | **12.0-13.2 Hz**, left loop | **-0.76..-0.88 at 53-65 ms, +0.97..+0.98 at 60-104 ms** |
| ours on their bodyIds | **both** | **2,063-2,128 / 604-619** | 61-69 | **none**: 1.2-2 Hz switching; IN16B036 pinned 160-196, both DNg100 driven to 0 | - |

**(b): their model on their table oscillates in our numpy port**: 11-15 Hz, 74-197 cells active of 4,310, none pinned, 3-12 front MNs
active (the paper's 0-7 is per single-DNg100 run: ours 3-5 driving L, 7-9 driving R), coxa promotors and one remotor rhythmic with an
antiphase-offset cross-correlation, Tr flexors among the recruited, tibia flexors silent (as the paper says).

**(a): our wiring oscillates too, once the equation is their code's and the sizes are theirs**: with one DNg100 driven, our cord table on
their cells gives the same loop, the same frequencies (12-14.4 Hz, a touch faster than theirs), the same recruited MN types and the same
promotor / remotor offset. the difference: **with both DNg100s driven, our table runs away** (half the network active, 600 pinned) where
theirs stays sparse and rhythmic.

### controls (their code's equation, I = 400, one DNg100 (L), seeds 0-1)

- **size off**, their table: 1,093-1,370 active, 266-383 pinned, 71-84 MNs, 1-8 Hz switching. our table on their cells: 2,077-2,080
  active, 786-794 pinned. **their own negative control reproduces on both tables**: without size scaling, no robust rhythm.
- **the printed equation on their table** (`--form paper`, their sizes): 1,618-1,771 active, 1,351-1,576 pinned, 90-100 MNs, 1-6 Hz.
  **this is the whole of the failure reported in the sections above**: it was the equation as printed, not our wiring.
- **our synapse-count proxy** (`--size insyn`) under their equation, on their cells or our front subnetwork: near silent (8-9 cells;
  DNg100 4-7 Hz, the loop off). the proxy correlates with their volume (log r = 0.87) but overstates big cells 2-3x (DNg100 34.7 vs 16.4;
  IN17A001 15.1 / 10.3 vs 4.7; IN19A007 10.4 / 7.1 vs 4.6; IN09A002 11.6 / 8.7 vs 4.4; IN16B036 1.4 / 0.9 vs 1.3), so the loop's
  excitors are too unexcitable to start. synapse count is not a usable stand-in for volume here.

### (c) the two tables, diffed on the same cells

- **cell set**: their 4,310 cells; 4,242 are in our cord table. the 68 missing are all untyped in their table (35 vnc_sensory, 29
  vnc_intrinsic, 3 DNs, 1 MN): fragments our `brain_whole` build does not carry. our own front construction (3,109 cells) is smaller
  because our file has no untyped / sub-threshold bodies and our 5-synapse floor is on whole-body counts.
- **edges** (on the 4,242 common cells): ours 142,504 edges / 2.76 M synapses; theirs 117,583 / 2.17 M. **117,347 edges are shared, with
  the same weights (median ratio 1.00; 1.8 % of them larger in ours, all DN / AN edges) and identical signs (0 sign disagreements)**; 236 edges are theirs only
  (3,342 synapses, mostly interneuron -> interneuron fragments' partners). **25,157 edges are ours only, and they are almost all onto
  descending neurons: DN -> DN 18,329 edges / 411,969 synapses, AN -> DN 5,156 / 121,686**, plus DN -> AN 396 / 2,560; on shared edges ours
  also carries 37,349 more DN -> DN and 12,197 more AN -> DN synapses. in all, 623 k synapses onto DNs from DNs and ANs.
- **why**: their W counts only synapses inside the VNC ROIs (`W_20260210_vncRoisOnly`); `scripts/build_cord.py` keeps every edge whose
  two cells are both kept, **wherever the synapses are**, so the DN-DN and AN-DN synapses that lie in the brain (GNG and above) came
  along. in a decapitated fly those synapses are gone with the head. **this is a bug in our headless cut**, and it is the only systematic
  difference between the tables.
- **the loop cells and IN09A002**: input synapses identical in both tables (IN17A001 L +4,710 / -3,487, R +2,973 / -2,663; INXXX466 L
  +1,627 / -1,389, R +1,022 / -1,047; IN16B036 L +477 / -295, R +309 / -205; IN19A007 L +2,882 vs 2,875 / -2,699, R +1,821 / -2,020 vs
  -2,021; IN09A002 L +4,334 / -1,999, R +3,184 / -1,583). **DNg100 differs**: ours +2,302 / -3,865 (L, 109 partners) and +2,093 / -3,948
  (R, 102), theirs +0 / -84 (8) and +12 / -32 (5): the brain-side inputs.
- **sign convention**: the same (ACh +, GABA / Glu -), and no cell has opposite output sign between the tables. their table signs 18 +
  6 'unclear' cells ours leaves at 0 (as their consensus transmitter); 32 of our signed cells have no outputs inside their W.
- **the fix, tested**: our table on their cells with the 25,829 DN <- DN / AN edges dropped (623 k synapses), **both DNg100s driven**:
  177-202 active, 0 pinned, 10 MNs, both loops at 12.0-14.4 Hz, lf promotor / remotor -0.76..-0.89 / +0.97. one side driven: 87-118
  active, 4-8 MNs, 12.0-14.0 Hz. the runaway under bilateral drive is exactly those synapses.

## verdict (supersedes the one above)

**Our wiring oscillates under Pugliese's model.** The earlier negative was the preprint's printed equation, which puts r_max inside the
tanh gain and multiplies the input by r_max; their code does neither, and with the printed form their own table runs away the same way
ours did. With their code's equation and their volumes, our cord table on their 4,242 cells gives the DNg100 -> IN17A001 -> INXXX466 ->
IN16B036 / IN19A007 rhythm at 12-14.4 Hz, 4-8 coxa and trochanter MNs active per driven DNg100, promotor-remotor in antiphase offset,
tibia flexors silent: the same as their table in the same code (11-15 Hz, 3-9 MNs). Two things in our pipeline were wrong, neither of
them the signs: (1) **the headless cut keeps 623 k brain-side synapses onto DNs** (DN -> DN, AN -> DN), which makes bilateral DNg100
drive run away; drop edges onto DNs whose synapses are outside the VNC (or all DN <- DN / AN edges, as tested) and it stops; (2)
**synapse count is not a volume proxy** for this model (it overstates the big premotor cells 2-3x and silences the loop); the real
volumes are in their table for their 4,310 cells only. So the wiring is cleared (after the cut is fixed), and the spiking engine is the
variable, with the caveat that the spiking engine also runs on the cut that has the brain-side DN synapses in it.
