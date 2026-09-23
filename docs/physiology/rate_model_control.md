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
