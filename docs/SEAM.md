# the seam: a graded optic lobe driving a spiking whole-fly connectome

> **STATUS (2026-09-16 02:43 PDT, read from the clock) - read this before the sections below, several of
> which are superseded by later ones.**
>
> - **withdrawn:** every "loom-selective" number from the flyvis-driven seam (v2) and
>   the transplant seam (v3). the ensemble check (2 of 10 models) and the bright-ball
>   control (recede > loom in every model) showed LPLC2 in those runs was reading OFF
>   vs ON, not outward vs inward. the giant-fiber test used to pin FRONT_SIGN is
>   struck as evidence.
> - **stands, on anatomy alone:** the eye's orientation. dorsal from the R7d/R8d
>   dorsal-rim strip; front from the T4 Mi4/Mi9 input sides and from LPLC2's layer
>   layout (a behind, b ahead, c above, d below). FRONT_SIGN = -1. the HS image
>   convention is robust across the ensemble (8 of 10).
> - **stands:** the expansion-detection mechanism is in the wiring (LPLC2 table), and
>   the LIF can use it: with an IDEAL direction-selective T4/T5 pattern (`seam/
>   ideal_t4t5.py`, left eye only, no flyvis, no transplant) LPLC2 gives expand 99 /
>   contract 13 / flash 17 / static 0. the LIF side of the seam is sound.
> - **stands:** the transplant reproduces T4/T5 direction selectivity on the real
>   wiring with correct sign and laterality, at ~1/3 of flyvis's magnitude.
> - **behaviour (2026-09-16 daytime):** closed-loop optomotor following, bar approach, a walk with
>   approach to dark posts, and a bristle-driven collision reflex all work on flyvis model 000. across
>   the ensemble the sensory side is robust (HS 8/10) and the one-neuron steering readout is not
>   (both-way drum following 2-3/10, drifting resting bias). see the behaviour sections.
> - **the bottleneck, named (partly):** the direction selectivity of the T4/T5 activity handed
>   to the LIF - from any single flyvis model, and from the transplant - is not clean
>   enough per position for LPLC2's layout to read expansion; edge polarity and edge
>   energy dominate. next: (1) ensemble-averaged flyvis T4/T5 as the input; (2)
>   subtracting the non-directional component was tried and does NOT rescue it (see
>   ~02:42); (3) train the transplant's pair strengths on the real
>   wiring with flyvis's optic-flow task.

status: working draft, 2026-09-15 21:50 PDT. everything below is either measured
on this machine or labelled as a choice.

> paths: on 2026-09-16 23:30 PDT run outputs moved from `seam/` and `world/` to `results/`,
> figures to `docs/figures/`, superseded scripts to `attic/`, ensemble drivers to `scripts/ens/`.
> file names cited in sections older than that are the pre-move names; the files are where
> the README says.

## the claim we're testing

every public whole-fly simulation runs the shiu et al. 2024 leaky integrate-and-fire
model: one threshold, one time constant, one mV-per-synapse for all 162,517 neurons.
under that model the optic lobe (58% of the brain) computes nothing: the periphery is
graded in life and the LIF can't do ON/OFF contrast; CT1's compartments collapse into
one cell; the motion pathway (13,500 T4/T5) fires zero spikes to a loom. so nobody's
fly can see a threat.

> **[2026-09-18 14:12 PDT: no longer true as written.** it was true of every *published* model when
> this was written; since the MaleCNS release (2026-06-08) at least five projects have put a 2026
> connectome in a body with sensory transduction, and one of them (`tel-0s/flyverse-core`, MIT,
> created 2026-09-10) ray-traces spectral radiance onto 5,895 photoreceptors on real hex columns,
> runs the optic lobe as graded rate units on the signed connectome into a Shiu LIF for the rest,
> and reports loom -> LC4 / LPLC2 -> giant fibre in 9 of 9 runs: the result this record's eye track
> does not have. the survey is `docs/LANDSCAPE.md`; the repositories were checked by hand. what
> stays ours: the eye rendered on the measured geometry of the same fly whose wiring we run, with
> flyvis's trained physiology transplanted onto his own optic-lobe cells rather than tiled.]**

flyvis (lappalainen et al., nature 2024) is the opposite object: a graded model of ONE
optic-lobe column tiled 721 times, 65 cell types, 45,669 cells, per-type physiology
*learned* by training on optic flow. it stops at T4/T5. no projection neurons, no giant
fiber, no body.

the seam: run flyvis on video, take its per-column activity for cell types that also
exist in our fly, and drive those cells in the LIF as poisson spike sources at a rate
proportional to flyvis activity. everything downstream runs on the measured wiring of
one specific male fly. graded where the biology is graded, spiking where it spikes.

test: does a looming dark disc fire the giant fiber (DNp01) through the real
T4/T5 -> LPLC2 -> GF wiring, and do contraction / translation / static / flash NOT?

## pieces

| piece | where | what it is |
|---|---|---|
| male CNS v1.0 | `data/` (1.1GB), `brain_whole.npz` | 162,517 neurons, 6.1M edges (weight>=5) |
| LIF engine | `ref/flybrain/scripts/flysim.py` | TheMrRaGe's engine on shiu constants. read FINDINGS.md |
| flyvis | venv, pretrained in `flyvis_data/results/flow/0000/{000..049}` | 50-model ensemble; we use 000 |
| column map | `seam/columns.py` -> `t4t5_columns.npz`; `columns_all.py` -> `columns_all.npz` | a hex column for every flyvis-type cell in our fly |
| stimuli | `seam/run_flyvis.py` -> `flyvis_out.npz` | 5 stimuli x 65 types x 721 columns x 200 frames |
| seam | `seam/seam.py`, `orient.py`, `calib.py` | the drive + readouts, orientation calibration, stats |

## how the pieces fit

```
video (200x200 @100fps)
  -> flyvis BoxEye: 721-hex retina (extent 15)
  -> flyvis network 000 on cuda: activity[t, cell]         2.4 s per 200 frames
  -> per type: activity[t, column(u,v)]
  -> column map: our cell (hex1,hex2,side) -> flyvis (u,v)  [choice 1: orientation]
  -> rate = GAIN * clip(activity / A_REF, 0, 1)            [choice 2: gain]
  -> LIF: cell marked driven, fires poisson at that rate    (same path as receptors)
  -> real wiring: T4/T5 -> LPi, VS/HS, LPLC2, ... -> DNp01, DNs -> VNC motor
```

## measured so far

**column coordinates.** T4/T5 carry none. their inputs do (Mi1/Mi4/Mi9 for T4,
Tm1/Tm2/Tm9 for T5). home column = strongest hex-tagged input: 13,577 / 13,580 placed.
home column holds 35-45% of tagged input because T4/T5 dendrites span ~3 columns.
extended to all 55 flyvis types present in our build: 70,165 cells placed (self /
via input / via output, labelled per cell). absent from our build: Am, Mi3, Mi11,
Mi12, Tm28, TmY9, R7/R8 (named differently here).

**our eye vs theirs.** ours: ~880 columns per eye, hex1 1-36, hex2 1-39, a hexagon in
axial coords. theirs: 721, |u|,|v|,|u+v| <= 15. 83% of our T4/T5 land inside their
lattice; the rim gets no drive.

**flyvis on the 1650.** loads 20 s, 200 frames in 2.4 s, 794 MB vram. T4/T5 baseline
~0.03, loom peak 1.5, all four direction subtypes lit (expansion is motion in every
direction). works without prime-run: torch's cuda context isn't a render offload.

**seam v0 (T4/T5 only).** first run: VS/HS tangentials 0 -> 50 Hz (vision reaches the
lobula plate output for the first time in any of these sims). LPLC2 and GF respond.
but recede > loom on GF, 31 vs 2.

**the confound.** my recede stimulus was the loom reversed, so a full-size disc
APPEARED at frame 50: a flash, not a contraction. flash drives every OFF edge at
once. loom starts from a 2 px dot and has no onset. rebuilt: every stimulus holds
its pre-state for 1 s; flash is now its own control.

**orientation.** with clean stimuli, 12 hex symmetries x 2 eyes: loom > recede in
most maps, 2-4x in the best (+wu, +uw, -wv, -vu), GF fires for loom and almost never
for recede. counts are small (LPLC2 < 1 Hz), single runs. calib.py is the stats.

**LC4 is dead** under T4/T5-only drive: it reads Tm cells in the lobula, not T4/T5.
v1 drives every flyvis type. then LC4/LC6/LC11/LC16 get input.


**seam v1 (all 55 types, `seam_v1.py`).** LC4 comes alive (loom 0 -> ~900 spikes/s
with change-from-rest drive). but a STATIC dark disc holds LC4 at ~2,400 and the GF at
~100, and a flash matches. with every type driven, the lobula projection neurons read
sustained OFF-contrast from flyvis's Tm cells (Tm9 IS sustained in life) and the LIF has
no adaptation to make LC4 transient. two transforms, both labelled:
- change-from-rest (`--baseline`): rate ~ (act - act_grey)+. every grey pre-period
  becomes a clean 0. static still sustained. this is the shiu convention (0 Hz rest =
  no change) applied at the seam, and it stays on.
- short-term depression (`--std flyvis|all`, engine's tsodyks-markram, U=0.08):
  static and recede decay to ~0 during the window, i.e. sustained -> transient. but
  flash > loom on LPLC2 (75 vs 16) and GF (24 vs 16). a dark flash driving the GF is
  not crazy (lights-off is a classic GF trigger) but LPLC2 preferring flash to loom is
  not the biology. and depression at 150 Hz drive is strong enough to gut the rates.

**where that leaves it (22:05 PDT).** the T4/T5-only seam (v0) is the clean test of
the motion pathway: loom-selective through LPLC2 to the GF, weakly, stats pending in
calib.py. the all-types seam (v1) adds the lobula contrast pathway through LC4, and
that pathway needs temporal processing the LIF doesn't have. the depth of the seam is
a per-pathway question, not one number: T4/T5 for the lobula plate, and for the lobula
either drive Tm/TmY with a transient transform or accept that LC4 needs its own
graded/adapting model. open.


## the eye (added ~22:00 PDT, after nate asked about the geometry)

the first seam rendered one flat image and told both eyes it was in the middle of
their field. that is two objects, one per side. the real eye is an apposition eye:
each column is one pixel with a ~5 deg gaussian acceptance cone, ~880 of them per
eye on a hemisphere that points sideways and a bit up, meeting the other eye in a
10-15 deg frontal strip. so the honest renderer is a low-res spherical camera with
soft pixels, and per-ommatidium raytracing is the simplest way to build one.

**measured from the wiring:**
- hex convention: interior columns have six neighbours only if (+1,+1) is a
  neighbour, i.e. axial (q, r) = (hex1, -hex2). under that convention all three
  lattice axes span 36-39 columns: a regular hexagonal eye. (the other convention
  made it 1.7x elongated and wrapped it over the poles.)
- dorsal: the R7d/R8d photoreceptors (polarization vision; a thin strip along the
  dorsal margin of every fly eye) land on one rim of the grid in both eyes. dorsal =
  centroid -> DRA centroid. after the wrap they sit at 65-72 deg elevation.
- flyvis's direction convention (gratings): T4b prefers image-right, T4a image-left,
  T4c up, T5d down. biological T4a prefers FRONT-TO-BACK motion, so the front must
  sit at image-RIGHT (front-to-back then runs toward image-left, where flyvis's T4a
  lives). the column -> lattice map is DERIVED: our front -> flyvis image-right, our
  dorsal -> flyvis up. it is no longer a swept parameter. (first draft had front at
  image-left. HS came out on the wrong side under yaw, and a synthetic test - drive
  all T4a: HS 795 spikes; drive all T4b: HS 0, LPi21 250 - showed the LIF's HS is a
  clean layer-1 reader, so the image convention was the thing that was mirrored.)

**choices:** IOA 6.3 deg horizontal / 4.4 vertical (was 5 uniform; see the frontal-wedge note); azimuthal-equidistant wrap about an
optical axis at az 90 / el 15; FRONT_SIGN, which way in the sheet is the front.

**two signs, and which test can see which.** (1) the IMAGE convention: which side
of flyvis's image the front is on. HS tests this: a fly yawing left brings objects on
its left toward the front (back-to-front in the left eye, front-to-back in the
right), and HS prefers front-to-back on its own side, so yaw_left must give HS_R >
HS_L. measured with front at image-left: HS_L 501/505/506 vs HS_R 345/347/339 (3
seeds), the wrong side; fixed to image-right. (2) FRONT_SIGN, the ANATOMICAL sign:
which physical columns look forward. as implemented it moves the geometry and the
lattice map together, so flyvis's image is unchanged and HS cannot see it (measured:
HS identical to three digits across the flip). only circuits whose selectivity
depends on where a cell sits in the eye can - LPLC2's receptive-field layout in our
wiring. so the test for (2) is lateral loom vs lateral recede on LPLC2, both signs,
everything else identical (`v2_P.json`, `v2_M.json`).

**files:** `seam/eye_geom.py` (columns -> directions, `eye_geom.png`), `seam/omma.py`
(raytracer, `fly_sees.png`), `seam/world_flyvis.py` (scene -> both eyes -> flyvis per
eye), `seam/seam_v2.py` (per-eye seam; LPLC2/GF/DNa02/DNa/HS/DN per side + bins).

**a limit found on the way:** flyvis's lattice (721 hexes) is smaller than our eye
(~880): ~107 rim columns per eye, including the frontal rim, get no flyvis. flyvis's
parameters are per cell type, so a larger-extent network should be buildable from the
same weights. not done yet.

## orientation, decided (~22:35 PDT)

both signs, eleven scenes, three seeds, both eyes (`seam/v2_P.json`, `v2_M.json`;
spikes in the 1 s stimulus window, mean of 3 seeds):

| | loom_left L | recede_left L | loom_right R | recede_right R | GF loom_right | GF recede_right | yaw_left HS L/R |
|---|---|---|---|---|---|---|---|
| FRONT_SIGN +1 | 4 | 21 | 27 | 126 | 1.3 | 32.7 | 384 / 486 |
| FRONT_SIGN -1 | 13 | 18 | 32 | 27 | 11.0 | 1.3 | 370 / 477 |

- **image convention (HS): fixed.** yaw_left gives HS_R > HS_L under both signs, as
  the biology requires. front is at flyvis's image-right.
- **anatomical sign (GF): -1.** with +1 a receding ball on the right fires the giant
  fiber 25x more than a looming one: inverted. with -1 it is loom 11 vs recede 1.3.
  looms are lateralized cleanly under both (LPLC2 fires only on the seeing side).
- **caveat found and fixed.** at first LPLC2 was only ~1:1 loom:recede with real
  geometry. at the flyvis level the receding ball delivered 6x the T4/T5 drive of the
  looming one and stayed high after the ball was small: the change-from-rest transform
  used each stimulus's own pre-period as rest, and the recede's pre-period is a held
  74-deg dark ball; cells the dark interior suppresses sit at a low rest, so uncovering
  grey reads as drive. rest must be one thing for every stimulus: the network looking
  at an empty scene (`--rest empty`, `seam/worldM_empty.npz`).

**the result, FRONT_SIGN -1, common rest, 3 seeds (`seam/v2_M_rest.json`):**

| | LPLC2 loom | LPLC2 recede | LPLC2 static | GF loom | GF recede |
|---|---|---|---|---|---|
| left eye (ipsilateral) | 15 / 11 / 19 | 4 / 1 / 0 | 2 / 2 / 1 | 0 / 0 / 0 | 4 / 0 / 3 |
| right eye (ipsilateral) | 30 / 27 / 37 | 8 / 12 / 13 | 0 / 0 / 3 | 11 / 12 / 4 | 0 / 0 / 1 |

a lateral loom drives ipsilateral LPLC2 3-9x over a matched recede and ~10x over a
static ball of the same size; the contralateral LPLC2 stays at 0; the giant fiber
fires for a right-side loom (11/12/4) and not for a recede (0/0/1). HS: yaw_left
HS_R 488 > HS_L 314, yaw_right HS_L 515 > HS_R 286. DNa02 lateralizes against the
yaw (yaw_left: R 30 > L 14; yaw_right: L 37 > R 3) - the shape of an optomotor
response through the real wiring; not claimed yet. loom_ahead stays weak (LPLC2
~0.5, GF 2): the frontal columns fall outside flyvis's 721-hex lattice. that is the
transplant's job. the GF fires for right-side looms and not left-side ones: the
hemisphere-tracing bias, compare within side.

(the flat-image results in calib.py used no rest subtraction at all; the v1 all-types
runs used the loom's grey pre-period, which is a common rest. both stand as labelled.)

- also visible: DN_L > DN_R in every condition (the right hemisphere is more
  completely traced and the weight rebalance overcorrects or undercorrects; compare
  within side only). DNa02 lateralizes with the stimulated side.

## the transplant (next build)

flyvis's learned state is 65 time constants, 65 biases and 604 synapse strengths by
type pair (+604 signs); `weight = sign * syn_count * strength`, graded relu units.
dumped to `seam/flyvis_params.json`. our optic lobe has 64,373 cells of those types
(70% of ol_intrinsic; the missing 30% - Tm6, the Dm family - were not in flyvis
either) and 2.49M raw edges among them (`seam/ol_graph.npz`, no synapse threshold,
because flyvis's spec counts every synapse). per-pair synapse counts per target cell:
MaleCNS/flyvis median ratio 1.48, IQR 0.95-2.45, log-corr 0.61; flyvis's gap-filled
pairs (e.g. *->Lawf2 assumed 95) are the outliers. plan: run flyvis's dynamics with
its per-type parameters on the real per-cell wiring of each eye, with a labelled
per-pair count rescale, then ask whether T4/T5 direction selectivity survives the move
from the averaged column to the real one. if it does, the seam moves to the projection
neurons and the 721-hex lattice, the rim, and the per-eye rendering hack all go away.

## the transplant, first result (2026-09-15, ~23:00 PDT)

`seam/transplant.py`. flyvis's dynamics and learned physiology on the real per-cell
optic lobe of each eye: 62,977 real cells (51 types), 14,112 virtual photoreceptors
(R1-R8 per column - the retina is outside the imaged volume; only 13% of R axons are
traced), 3,528 CT1 compartments (M10/Lo1 per column, by partner type). 1.97M edges,
`weight = sign * count * strength * pair_rescale * gain`. 552k real edges over 1,713
type pairs dropped because flyvis has no parameters for them (T2a->T2a, Tm5Y->Tm5Y ...).

**what it took to make it run, in order found:**
1. **stability.** spectral radius of the signed weight matrix: flyvis tiled 1.76;
   transplant no rescale 4.39 (TmY4 runs away in 3 frames); per-pair rescale 2.19
   (L eye 1.89, R eye 2.19 - the tracing bias). gain 0.8 with pair rescale matches
   flyvis's radius: the one global fudge, and it is derived, not tuned.
2. **the medulla was dark.** side-by-side resting-input decomposition found the
   largest single difference: R8 -> Mi1 is +2.57 in flyvis and 0 here. flyvis's R7/R8
   feed the medulla directly with the tonic drive that holds the ON pathway at its
   operating point; the virtual retina had only R1-R6. added R7/R8: Mi1 modulation
   0.02 -> 0.42 (flyvis 0.46), Mi4 0.14 -> 0.82 (1.10).
3. **operating point.** with the retina complete, T4a rested at 2.08 (flyvis 0.09):
   two real differences (CT1 -> Mi1 is 1,145 synapses in the whole MaleCNS vs a
   large count in flyvis; Mi12 is absent from our typing) push the medulla up, and
   a relu unit far above threshold has no direction-selective mean shift. fix, the
   biological one: keep taus and strengths, re-derive the 65 biases so each type
   rests where it rests in flyvis (`--homeostat 12`, mean |error| 0.02 after 12
   iterations, largest shifts L1/L2/Mi1/Lawf2 ~ -1.1). nothing fit to our readout.

**result** (square-wave grating, 30 deg period, 60 deg/s; mean shift during-rest /
temporal modulation; +az is front-to-back on the LEFT eye, back-to-front on the RIGHT):

| | L +az | L -az | R +az | R -az | verdict |
|---|---|---|---|---|---|
| T4a | +0.055 / 0.55 | +0.036 / 0.37 | +0.038 / 0.43 | +0.081 / 0.67 | front-to-back, both eyes |
| T4b | +0.030 / 0.27 | +0.067 / 0.43 | +0.107 / 0.52 | +0.037 / 0.32 | back-to-front, both eyes |
| T4c (up vs down) | +0.044 / 0.47 vs +0.012 / 0.28 | | +0.075 / 0.61 vs +0.006 / 0.36 | | upward, both eyes |

direction selectivity survives the move from the averaged column to the real wiring:
correct sign, correct laterality, about a third of flyvis's magnitude on its own
lattice (flyvis on the same grating: T4b +0.27, T4c +0.22). T4d and the T5 (OFF)
pathway are weak here as they are in flyvis on this stimulus. and it is a third
independent circuit agreeing on the eye's orientation, using no map at all: only
the wiring and where each column looks.

**files:** `seam/transplant_params.py` -> `flyvis_params.json`; `seam/ol_graph.py` ->
`ol_graph.npz`, `pair_counts.csv`; `seam/flyvis_ref_grating.py` (reference on the
identical grating); `seam/flyvis_rest.json` (homeostat targets).

**seam v3: the transplant drives the LIF by bodyId** (`seam/scenes.py`, `transplant.py
--stims`, `seam/seam_v3.py`, results `seam/v3_results.json`; gain 150, A_REF 0.5, rest =
transplant on an empty scene). no column map: the transplant's T4a cell IS the LIF's
T4a cell. 3 seeds:

| | LPLC2 loom | LPLC2 recede | LPLC2 static | GF loom | GF recede |
|---|---|---|---|---|---|
| left eye | 2 / 0 / 2 | 35 / 37 / 37 | 0 / 0 / 1 | 0 / 0 / 0 | 4 / 5 / 8 |
| right eye | 104 / 108 / 108 | 240 / 243 / 263 | 243 / 248 / 241 | 5 / 49 / 26 | 100 / 99 / 43 |

**not loom-selective, and the reason is legible.** HS lateralizes cleanly (loom_left
HS 292/70; yaw_left HS_R 532 > HS_L 409) but LPLC2 prefers a receding dark ball, and on
the right a static ball drives it as hard as a receding one. two causes, both visible
in the chain tables above: (1) **the OFF pathway is weak.** T5 modulation is 0.11 in
the transplant vs 0.37-0.46 in flyvis; Tm2/Tm4/Tm9 run at about half of flyvis's
modulation, and T5 hovers at threshold. a dark ball looming is darkening edges moving
outward - T5's job. what is left is T4 (ON) answering the brightening edges, which a
dark ball makes when it recedes. so recede > loom is exactly what an ON-only eye should
say. (2) **sustained responses to static contrast** are larger relative to motion than
in flyvis, so a static ball holds LPLC2 up through change-from-rest. (3) the right eye
runs hotter than the left throughout (spectral radius 2.19 vs 1.89; LPLC2_R 240 vs
LPLC2_L 35 on matched stimuli).

**where that leaves the transplant (23:20 PDT).** direction selectivity survives the
move to real wiring with correct sign and laterality; the ON pathway matches flyvis's
operating point; the OFF pathway does not carry enough, and the whole-fly loom test
through the transplant fails for that reason, not for a wiring or orientation reason.
next, in order: (a) a second homeostatic target - match each type's response *gain*
(modulation under the reference grating) to flyvis by scaling its input strengths, the
way the biases were matched; still calibration to flyvis, nothing fit to our readout.
(b) bridge TmY9 -> TmY9a/TmY9b (exists under a split name); Mi12, Mi3, Am, Tm28 are
genuinely absent from the MaleCNS typing. (c) per-eye gain so the two eyes sit at the same radius. (d) then
re-run v3, with the flash control added.

## the transplant, calibrated (23:50 PDT)

`--homeostat` now per (type, eye); `--gainmatch`: each (type, eye)'s input is scaled
until its grating modulation matches flyvis's (`seam/flyvis_mod.json`), with a
divergence guard (revert + halve the step); every scene starts from the steady state of
its own first frame (3 s). saved in `seam/tx_calib.npz`. after 14 + 3 rounds: rests
match to 0.012; the OFF channel is on (T5a modulation 0.21 vs flyvis 0.27, was 0.11);
T4a/T5a front-to-back in both eyes, T4b back-to-front, T4c up. spectral radius after
calibration: L 1.80, R 1.94 (flyvis 1.76); further gain rounds diverge.

**the seam through it (`v3_calib2.json`, 3 seeds):** empty scene = 0 drive, every
scene perfectly lateralized (loom_left: LPLC2 L 4-5, R 0; HS L 226-267, R 0). but in
both eyes, both channels, at the transplant level: recede > static > flash > loom
(left T5: 7,916 / 4,194 / 3,966 / 2,325). the LIF rejects static (LPLC2 0) and passes
recede (66-78) over loom (4-5). the transplant's T4/T5 are edge detectors with weak
direction selectivity in mean rate; a receding ball has far more edge-time than a
looming one; flyvis's strong DS pattern is what carried the loom in v2.

**the mechanism is in the wiring, and it reads the orientation for a fourth time.**
synapse-weighted mean offset of each input type from the target's home column, in our
sheet coordinates (+front, +dorsal), both eyes agree to 0.05:

| target | Mi4 (null side) | Mi9 (preferred side) | prefers |
|---|---|---|---|
| T4a | -0.66 front (behind) | +0.73 front (ahead) | front-to-back |
| T4b | +0.78 (ahead) | -0.75 (behind) | back-to-front |
| T4c | +0.69 dorsal | -0.49 dorsal (ventral) | upward |
| T4d | -0.86 (ventral) | +0.68 (dorsal) | downward |
| T5a: Tm9 | | +0.52 front | front-to-back |
| T5b: Tm9 | | -0.45 front | back-to-front |

preferred-side input (Mi9 / Tm9) sits on the side motion comes from; null-side input
(Mi4) on the side it goes to. that is the textbook mechanism (Haag 2016, Shinomiya
2019), read straight out of the MaleCNS, and it agrees with the DRA dorsal axis and
FRONT_SIGN=-1 using no physiology at all. synapse counts per target match flyvis
(T4a <- Mi1 64-72 vs 59, Mi4 12-14 vs 15, Mi9 18-27 vs 23; right eye +15-40%). the
Mi4-Mi9 separation is 1.4 columns here vs ~1.9 in flyvis's spec (its Mi4 offset is
about twice ours), and our home column is defined by the Mi1 input, which zeroes the
Mi1 offset by construction. a smaller spatial baseline for the correlator is one
candidate for the weaker DS; the other is that flyvis's strengths were fit to its own
offsets. after calibration T4a's resting inputs match flyvis within ~25% per source.

**where the transplant stands.** it reproduces the direction-selectivity mechanism on
the real wiring with correct sign and laterality in both channels, at about a third of
flyvis's magnitude, and that third is not enough to carry a loom through LPLC2 against
the edge response. the flyvis-driven seam (v2, common rest) remains the working eye.
next for the transplant: fine-tune the 604 pair strengths on the real wiring with
flyvis's own optic-flow task (the "learn the 2026 physiology" path; GPU-hours, not
minutes), and a home-column definition from the T4/T5 dendrite itself.

## ENSEMBLE CHECK (2026-09-16 ~02:28 PDT) - the loom result does not generalize

everything above ran on flyvis model 000 of 50. overnight: models 000-009 through
the v2 seam (real geometry, common rest, 1 seed each; `seam/ens/SUMMARY.txt`):

| model | LPLC2 loom L | recede L | loom R | recede R | GF loom R | GF recede R | yaw_left HS L / R |
|---|---|---|---|---|---|---|---|
| 000 | 17 | 1 | 32 | 6 | 1 | 1 | 320 / 495 |
| 001 | 20 | 94 | 42 | 104 | 5 | 8 | 404 / 600 |
| 002 | 16 | 116 | 44 | 190 | 2 | 8 | 590 / 692 |
| 003 | 15 | 154 | 8 | 208 | 0 | 23 | 73 / 718 |
| 004 | 0 | 52 | 4 | 140 | 0 | 0 | 620 / 587 |
| 005 | 66 | 48 | 155 | 86 | 26 | 1 | 609 / 274 |
| 006 | 1 | 87 | 14 | 178 | 0 | 7 | 724 / 740 |
| 007 | 1 | 248 | 17 | 414 | 0 | 0 | 755 / 815 |
| 008 | 7 | 307 | 11 | 417 | 0 | 0 | 403 / 611 |
| 009 | 92 | 272 | 110 | 378 | 5 | 81 | 8 / 252 |

**loom > recede on ipsilateral LPLC2 in 2 of 10 models** (000, 005). median
loom:recede 0.12 left, 0.16 right. HS_R > HS_L under yaw_left in 8 of 10: the
front-to-back image convention is robust across the ensemble; the loom selectivity
is not. **the "3-9x" claim in the orientation section is a property of model 000 and
is withdrawn as a general result.** the orientation decision itself (FRONT_SIGN by GF
loom-vs-recede) was made on model 000 and has to be re-examined against the
ensemble: with most models inverting loom/recede, the GF test on 000 alone is not
enough to have pinned it. the DRA (dorsal) and the wiring-offset table (Mi4/Mi9
sides) do not depend on flyvis and stand.

next: measure each model's own T4/T5 direction convention on gratings (as
`flyvis_dirs.py` did for 000) and ask whether the two models where loom wins are the
ones whose T4/T5 tunings match the biology. lappalainen et al. report the ensemble
clusters by T4/T5 tuning and only some clusters match experiment. if loom-wins ==
biology-matches, this is model selection by an external criterion and the seam is
sound; if not, the seam is wrong somewhere.

**the model-selection hypothesis is refuted** (`seam/ens_dirs.py`, `seam/ens/dirs.json`):
each model's own T4/T5 preferred image directions on gratings, flagged against the
biology, next to its loom outcome:

| model | T4a T4b T4c T4d | T5a T5b T5c T5d | match | loom > recede |
|---|---|---|---|---|
| 000 | l* r* u* u | l* l u* d* | 6/8 | yes |
| 001 | l* r* u* d* | l* r* u* d* | **8/8** | **no** |
| 005 | r u d u | r r* r l | **1/8** | **yes** |
| 002/003/007/009 | mostly right | mostly right | 6-7/8 | no |

the biologically correct model loses; a model with T4a pointing the wrong way wins.
the LIF's LPLC2 is not reading outward-vs-inward from these inputs. **the likely
confound is polarity: the ball is dark.** a dark ball looming is darkening edges
moving outward (T5, OFF); receding, brightening edges (T4, ON). "loom vs recede" has
been "OFF vs ON" since the first night, and a model whose T5 answers harder than its
T4 wins the loom for the wrong reason. control: a bright ball, both directions, on
models 000 / 001 / 005. if LPLC2 is outward-selective, bright loom > bright recede;
if it is polarity, it flips.

**polarity control result (~02:33 PDT), models 000 / 001 / 005, ipsilateral LPLC2:**

| model | dark loom | dark recede | bright loom | bright recede |
|---|---|---|---|---|
| 000 L | 17 | 1 | 0 | 5 |
| 000 R | 32 | 9 | 2 | 15 |
| 001 L | 20 | 94 | 6 | 12 |
| 005 R | 172 | 77 | 73 | 169 |

**bright ball: recede > loom in every model, including 000.** the seam's LPLC2 was
reading OFF vs ON, never outward vs inward. every "loom-selective" number in this
document from v2 onward is a polarity result and is withdrawn as evidence of
expansion detection. that includes the giant-fiber loom-vs-recede test that decided
FRONT_SIGN: struck as evidence.

**what the orientation now rests on, and it is enough:** two pieces of pure anatomy.
(1) dorsal: the R7d/R8d dorsal-rim photoreceptors land on one rim of the grid.
(2) front: T4a's preferred-side input (Mi9, per Shinomiya 2019 / Haag 2016) sits
+0.73 columns toward the front and its null-side input (Mi4) 0.66 behind, only under
FRONT_SIGN = -1; under +1 the sides swap and contradict the biology. T4b/c/d agree.
no physiology, no flyvis, no LIF in either. the HS image convention is separately
robust across the ensemble (8 of 10). so: FRONT_SIGN = -1 stands, on wiring alone.

**what is not established:** that any LIF readout in this pipeline detects expansion.
the next measurement is anatomical again: does each LPLC2's dendrite sample layer a
(front-to-back) behind its centre, b ahead, c above, d below (Klapoetke 2017)? if the
wiring has that, the seam is failing to use it (candidates: LPi inhibition too weak at
0 Hz rest; T5 input outweighing T4; Tm5Y, LPLC2's largest input, undriven). if it
does not, no downstream readout could have worked.

**LPLC2's receptive field is in the wiring (~02:36 PDT).** synapse-weighted offset of
each T4/T5 subtype's input from each LPLC2 cell's own centre (centre = weighted mean of
all its T4/T5 input columns; +front, +dorsal; 185 cells, ~319 T4/T5 synapses over
~36 columns each):

| layer | subtype | L eye (front, dorsal) | R eye | Klapoetke 2017 |
|---|---|---|---|---|
| 1 front-to-back | T4a / T5a | -3.04, +0.91 / -3.40, +0.93 | -2.92 / -3.27 | behind |
| 2 back-to-front | T4b / T5b | +2.39, -1.06 / +2.19, -1.18 | +2.40 / +2.33 | ahead |
| 3 up | T4c / T5c | +0.67, +2.10 / +0.79, +2.50 | +2.11 / +2.57 | above |
| 4 down | T4d / T5d | -1.12, -2.38 / -0.76, -2.43 | -2.36 / -2.58 | below |

each layer samples the side of the field where its preferred motion is outward. that
is the loom detector's mechanism, read out of the MaleCNS, both eyes agreeing, under
FRONT_SIGN = -1. LPLC1 (134 cells) shows no such layout (all offsets < 0.7): correct,
it is not a loom detector. HS spans 540 columns with no offset structure: correct, it
is a wide-field integrator. fifth anatomical agreement on the orientation.

**so the mechanism exists and the seam does not use it.** next test is input-side vs
LIF-side: hand the LIF an IDEAL direction-selective T4/T5 pattern (expanding ring:
T4a/T5a fire behind the centre, b ahead, c above, d below; contracting ring: the
opposite; flash: all subtypes on the ring at once) and ask whether LPLC2 discriminates.

**ideal-input test (~02:38 PDT), `seam/ideal_t4t5.py`.** left eye's own T4/T5 cells
driven with a perfectly direction-selective pattern (expanding ring: T4a/T5a fire behind
the centre, b ahead, c above, d below, rate 150 * |cos|; contracting: mirrored; flash:
all subtypes on a fixed ring for 200 ms; static: nothing). LPLC2_L over the second:
**expand 99, contract 13, flash 17, static 0**; expand holds 8-13 per 100 ms for the
whole second, contract and flash die within 200 ms. LPi_L fires equally for expand and
contract (2238 / 2240), so the discrimination is the dendritic layout, not inhibition.
the LIF's expansion circuit works on this wiring. every failure tonight was input-side.

**DS-only drive does not rescue it (~02:42 PDT, `seam_v2.py --dsonly`).** subtracting
each subtype's sibling mean before driving (models 000 and 001, dark and bright, one
seed): 000 dark loom 7 / recede 1, bright 0 / 0; 001 dark 0 / 35, bright 10 / 18, right
4 / 30 and 27 / 54. the residual directional pattern from a single flyvis model is
too weak or too noisy at this eye's resolution for LPLC2's layout to read, and the
non-directional component was not the whole story. candidates for the morning:
edge speed (the ideal test fired at 150 Hz regardless; flyvis's T4/T5 have a speed
optimum and the ball's edge speed runs 0-100 deg/s over the second), ensemble-averaged
input, and per-position DS measured directly on the flyvis output for the ball
(does T4a fire behind the ball and T4b ahead, in flyvis's own numbers?).

## morning (2026-09-16 09:19 PDT): why no graded front end has carried the loom

**how much directional drive LPLC2 needs** (`ideal_t4t5.py`, ideal pattern mixed with a
non-directional one on the same ring): expand/contract ratio 5.3 at 0% noise, 4.3 at
25%, 2.9 at 50%, 1.3 at 75%, 1.0 at 100%. **at least half the drive has to be
directional.**

**what flyvis's own T4/T5 output for the ball contains** (`flyvis_pattern.py`: per
subtype, activity-weighted mean of its outward component around the ball centre; + =
expansion-consistent; models 000 / 001 / 005, left eye):

| model 000 | T4a | T4b | T4c | T4d | T5a | T5b | T5c | T5d |
|---|---|---|---|---|---|---|---|---|
| dark loom | -0.38 | -0.74 | -0.30 | -0.66 | +0.78 | +0.41 | +0.61 | +0.35 |
| dark STATIC | -0.59 | -0.73 | -0.32 | -0.70 | +0.77 | +0.59 | +0.68 | +0.42 |
| bright loom | +0.52 | +0.36 | +0.10 | +0.58 | -0.62 | -0.62 | -0.52 | -0.33 |

**a stationary dark object produces an expansion-shaped T5 pattern and a
contraction-shaped T4 pattern; a bright one the reverse; the loom adds ~0.1 on top.**
each subtype's receptive field is offset toward its preferred side (the Mi4/Mi9 and
Tm9 offsets measured above), so a static edge of one polarity excites the subtypes
asymmetrically around the object, and flyvis sustains that response on a held input
where a real T4/T5 is transient. this is the mechanism of the polarity confound, and
it is ~4x larger than the motion signal for a ball of 2-15 columns.

**temporal high-pass on the drive** (200 ms; T4/T5 are transient in life) reduces the
static pattern but does not remove it: mean outward component loom +0.06..+0.14,
recede -0.09..-0.16, per-subtype magnitudes still 0.3-0.6 and polarity-signed. seam
with high-pass, bright ball: loom 0 / 0 / 3 / 10 vs recede 4 / 13 / 19 / 25. no.

**conclusion for this line:** with any single flyvis model at this eye's resolution,
the T4/T5 output for a small looming object is dominated by a polarity-dependent
static pattern, and LPLC2 needs half the drive to be directional. expansion detection
through flyvis -> LIF is not reachable by transforms on the drive. it needs a front
end whose T4/T5 static-edge responses are transient (trained transplant, or a
different graded model), or the ensemble average if the static pattern is
model-specific (it is not: 000 and 001 agree in sign).

**what IS robust and usable now:** lateralized object presence (which eye, where) and
wide-field motion through HS/VS (correct side in 8 of 10 models), which is what
optomotor steering needs. DNa02 already lateralizes against a yaw. that is a fly that
can be put in a world and turn toward or away from things; it is not yet a fly that
can dodge.

**adaptation in the transplant (09:36 PDT, `--adapt-tau 300`).** one slow subtractive
variable per non-photoreceptor cell (dA/dt = (relu(v) - A)/300 ms, v gets -A). two
effects: (1) it stabilises the network - gain matching converges all 10 rounds with
no divergence and every modulation target is hit (T4a 0.48, T5a 0.27, Tm9 0.27);
(2) it halves the static-like pattern in the T4/T5 output (mean |per-subtype outward
component|: loom 0.40 -> 0.22, static 0.34 -> 0.23) but the pattern stays
polarity-signed and loom does not come out expansion-shaped (mean -0.12). seam v3 on
the adapted transplant: left loom 10 / recede 33 / static 1; right loom 110 / recede
70 / static 78 / flash 128. no. calibration saved as `seam/tx_calib_adapt.npz`; keep
adaptation on (it is the more physiological model and the stable one), but the
transplant's route to a loom detector is training its pair strengths, not tuning.

## he moves (11:13 PDT): closed-loop optomotor response

`world/closedloop.py`: a striped drum (30 deg period, 60 deg band, 0.2/0.8) around a fly
fixed at the origin. every 100 ms: both retinas rendered at his heading (omma), flyvis
per eye with state carried across chunks, the LIF driven at T4/T5 (v2 seam, rest from
a 1 s still-drum warm-up), and his heading updated from his own descending neurons:
yaw = 3 deg per net DNa02 spike (right minus left, smoothed over 300 ms; right DNa02 =
right turn, Rayshubskiy 2020), clipped at 120 deg/s. drum programme: still 2 s, left
30 deg/s 4 s, still 1 s, right 30 deg/s 4 s, still 1 s.

| | still | drum LEFT 30/s | still | drum RIGHT 30/s | still |
|---|---|---|---|---|---|
| seed 0 | -7.0 | **+22.0** | -15.5 | **-30.0** | -0.5 |
| seed 1 | -2.0 | **+15.7** | +4.7 | **-31.6** | -1.5 |
| seed 2 | -8.4 | **+18.2** | -7.5 | **-30.2** | +4.2 |

(his heading rate, deg/s, + = left.) he follows the drum in both directions, rightward
at the drum's own speed, leftward at half to two thirds. an optomotor response, closed
loop, through the real optic lobe's motion pathway and the real wiring of the steering
descending neuron. viewer: the "optomotor drum" artifact (human view + both retinas +
heading against drum angle).

**what it took.** the first wiring used the DNa *family* (330 cells) as the wheel,
because the flybrain findings report it as the stronger steering readout (d' 4.2). it
followed the drum left at 20 deg/s and not right at all, and listed left at rest. i
tried per-pathway hemisphere symmetrization (`seam/symmetrize.py`, `brain_sym.npz`:
L and R totals matched per (pre type, post type) pair): no change, so the list is not in
the synapse totals; shelved. DNa02 alone - one cell per side, the characterised turning
neuron - was symmetric and correctly lateralized in every run (drum left: L 1060 / R
760; drum right: L 710 / R 1710; rest 450 / 390). the family is a mixed-laterality
population and its sign flips between stimuli; DNa02 is the wheel.

**what's robust:** HS lateralization (8/10 flyvis models), DNa02 lateralization (every
run so far). **not yet checked across the flyvis ensemble:** the closed loop itself.

## the bar and the walk (11:44 PDT, `world/loop.py`)

**bar.** one dark vertical bar (15 deg wide, +-30 deg, 0.2 on 0.6) fixed in the world at
+60 or -60 deg from his starting heading, 20 s, DNa02 on the wheel as in the drum.
bar at +60 (left): he turns left, passes the bar through the front, and holds it at
-54 / -51 deg (seeds 0, 1) for the rest of the run. bar at -60: mirror, holds at +55 /
+68. a position response - he turns toward a dark bar - but not fixation: a real fly
centres it. centring needs the small-object position system (LC cells) which is not on
the wheel; only T4/T5 motion -> DNa02 is. labelled and left.

**walk.** the arena of eight dark posts and one bright ball, 0.3 m/s along his heading,
DNa02 steering, 20 s, three seeds; three blind controls (retina held at rest, heading
noise only). "hits" = frames inside a post (he passes through).

| | hits (frames) | path | mean turn | where he ends |
|---|---|---|---|---|
| walk s0/s1/s2 | 378 / 400 / 408 | 6.0 m | 25 / 24 / 30 deg/s | inside the arena, weaving |
| blind s0/s1/s2 | 205 / 160 / 131 | 6.0 m | 2.5 / 3.0 / 2.8 deg/s | straight into the far wall |

he turns constantly and hits MORE than a blind fly walking straight. with the bar result
this reads consistently: dark objects pull his heading toward them and he walks into
what he turns toward. no avoidance circuit is on the wheel (LPLC2 -> escape is not
wired to locomotion, and looms are not detected anyway). approach to dark verticals is
real fly behaviour; walking into them is what a fly with approach and no collision
avoidance does. viewer: "the walk" artifact.

**the frontal wedge, found by nate in the viewer (11:51 PDT).** the fly-sight panel had a
dark gap dead ahead and it was real: with a uniform 5 deg per column the most frontal
column at the equator sat at 17-18 deg on each side, a 35 deg blind wedge straight ahead
widening to 50 deg below the horizon, and the eyes met only above +30 deg elevation.
cause: a 30-column-wide sheet at 5 deg covers 150 deg of azimuth per eye; a real eye
covers ~190 deg with about the same number of columns, because the ommatidial lattice is
anisotropic in angle (horizontal spacing larger than vertical). fix, labelled:
IOA 6.3 deg horizontal, 4.4 deg vertical. now each eye reaches 3 deg past the midline at
the equator (a 7 deg binocular strip), down to about -10 deg elevation; a narrowing gap
below that, where the head and antennae are in life; elevation -58..+86; no column more
than 100 deg from its eye's axis. every run before this had the wedge; the drum and bar
results are unaffected in kind (they live at 60-90 deg), the walk was re-run.

## touch (12:59 PDT, `loop.py --touch`)

**diagnostic first** (LIF only, 150 Hz on the leg bristles for 1 s): DNa02 does not
respond to touch at all (0 / 0). the DNa family does, weakly and left-biased. the leg
motor neurons respond ipsilaterally: left bristles -> leg MN L 12,156 / R 9,978; right
bristles -> L 7,952 / R 8,722; both -> 12,714 / 12,311. leg touch is handled in the
ventral nerve cord, not by the brain's steering neuron, which is the anatomy.

**so the wheel gets a second term, labelled:** a fly turns by driving the legs on the
outside of the turn harder, so more left-leg drive = right turn. yaw_touch = 30 deg x
((legMN_R - legMN_L)/(legMN_R + legMN_L) - running rest asymmetry), applied only in
chunks where he is in contact; the rest asymmetry is a running mean over untouched
chunks (a fixed 0.5 s estimate was noise and sent one seed into a permanent spin).
posts are solid: he is held at the surface while in contact, and the bristles on the
contacted side (or both, if head-on) fire at 150 Hz.

| | contacts | mean frames per contact | longest | total stuck |
|---|---|---|---|---|
| reflex ON, seeds 0/1/2 | 6 / 5 / 2 | 70 / 117 / 106 | 116 / 153 / 137 | 4.2 / 5.8 / 2.1 s |
| reflex OFF (bristles fire, leg term 0) | 2 / 3 / 2 | 292 / 158 / 271 | 389 / 246 / 354 | 5.8 / 4.7 / 5.4 s |

with the reflex he frees himself in about a second per contact; without it, two and a
half, with vision alone eventually turning him. a collision reflex that emerges from
leg bristles -> VNC -> leg motor neurons in the real wiring, plus one motor mapping of
mine. viewer: "the walk, solid posts" (touches ringed in red on the map).

## behaviour across the flyvis ensemble (13:07 PDT, `world/ens_behaviour.sh`)

drum (12 s programme) and walk (20 s, ghost posts) on flyvis models 000-009, seed 0.

| model | still | drum LEFT | still | drum RIGHT | still | both ways? | HS L/R (left seg) | DNa02 L/R left seg / right seg |
|---|---|---|---|---|---|---|---|---|
| 000 | +10 | +11 | +3 | -23 | -18 | yes | 18600/12990 | 890/720 / 530/860 |
| 001 | +8 | +26 | +9 | +9 | +6 | no | 7480/2400 | 460/120 / 120/20 |
| 002 | +5 | +16 | +20 | +40 | +47 | no | 14280/9890 | 300/50 / 1070/510 |
| 003 | +5 | +10 | +4 | -11 | +2 | yes | 24950/2070 | 170/20 / 0/150 |
| 004 | -30 | -62 | -32 | -7 | -12 | no (inverted) | 12090/27330 | 900/1680 / 790/900 |
| 005 | +7 | -54 | -56 | +50 | +25 | no (inverted) | 6800/27820 | 210/960 / 780/80 |
| 006 | +3 | +3 | 0 | +1 | +2 | no (silent) | 6960/1760 | 40/30 / 20/10 |
| 007 | +10 | +28 | +2 | +7 | +33 | no | 16570/11050 | 400/20 / 490/340 |
| 008 | +15 | +19 | -5 | -6 | +7 | yes | 22690/15490 | 330/70 / 250/320 |
| 009 | +4 | +7 | +14 | -2 | +20 | no | 26650/20480 | 150/40 / 90/120 |

**follows both ways: 3 of 10. leftward: 7 of 10. rightward: 3.** 004 and 005 are the
two models with inverted T4/T5 tuning (last night's grating table) and turn the wrong
way in both directions - consistent. 006 barely responds. the rest have the correct HS
lateralization (8 of 10, as before) but drift LEFT on a still drum and fire DNa02 more
on the left at rest (8 of 10): a resting bias at the wheel that gives left turns a
head start and right turns a handicap. per-pathway symmetrization did not remove it
(DNa family was the readout then; DNa02's rest offset was not measured). fix tried
next: measure the DNa02 R-L offset on a still world for 2 s with visual drive and
subtract it at the wheel (`--rest-sub`), leaving the visual response untouched;
ensemble re-run in `drum2_m*.npz`. **until that lands, the optomotor claim is: robust
on the left, model-dependent on the right, with a known resting bias.**

walk across models (ghost posts): hits 90-564, mean turning 14-53 deg/s; every model
turns toward dark posts and walks into some. approach behaviour is the ensemble's;
its magnitude is the model's.

**resting-offset subtraction (13:18 PDT, `drum2_m*.npz`): moved the problem.** rightward
following 3 -> 7 of 10, leftward 7 -> 4, both ways still 3 (003, 007, 008; 000 lost).
still-drum drift got worse in several models (001 -35 deg/s, 005 -93). the offsets were
-0.35 to -1.5 spikes per chunk estimated from ~20 spikes: noise, and at 3 deg per spike
a half-spike error is 15 deg/s of drift. **diagnosis: the wheel is one neuron per side
at 100 ms resolution.** DNa02 fires 5-10 Hz; one spike of difference in a chunk is a
3 deg turn. the sensory side (HS: thousands of spikes, correct side in 8 of 10 models)
is robust; the motor readout is count-starved. options: integrate longer (keeps the
wheel on the named neuron) or read more cells (the DNa family's sign flips between
stimuli, so no). one more ensemble run with a 1 s smoothing window and a 10 s rest
estimate, nothing tuned to the drum: `drum3_m*.npz`.

**long integration (13:35 PDT, `drum3_m*.npz`, 1 s smoothing, 10 s rest estimate): no
better.** both ways 2 of 10 (000, 008); leftward 5, rightward 6. the still-drum drifts
are not noise now - they are steady: 002 drifts +30 deg/s in every segment, 004 +33 to
+49, 005 -74 to -89, 001 -28 to -40, regardless of what the drum does. a 10 s resting
estimate does not cancel them, so the DNa02 left-right offset is not stationary over a
run: it wanders on a slower timescale than the rest estimate (flyvis's slow state, the
LIF's, or both). a fixed offset cannot correct a drifting one.

**where the closed loop stands, honestly.** the sensory encoding of self-rotation is
robust across the flyvis ensemble (HS on the correct side, 8 of 10). the descending
readout - DNa02, one cell per side - carries the right sign in most models but with a
drifting resting bias of order one spike per 100 ms, which at any usable gain is tens
of degrees per second. the optomotor response is therefore: clean and symmetric on
model 000 (3 seeds), present in 2-3 of 10 ensemble models both ways, one-sided in most
of the rest, inverted in the two inverted-tuning models. the walk, the bar and the
touch reflex all ran on model 000 and inherit this caveat. the two inverted models are
excluded on external grounds (their T4/T5 tuning contradicts the fly); the drifting
offset is not explained. next steps that would not be tuning: find what drifts (LIF
state with flyvis held constant, vs flyvis state with the LIF reset), and a wheel with
more spikes on it that is still the animal's steering output (the descending
population that lateralizes consistently with DNa02 in yaw, chosen on the yaw runs
and then tested on the drum, not the reverse).

**nate's question: is the striped drum confusing him? (14:14 PDT, `spin_m*.npz`).** the
arena of posts revolving around him instead of stripes, same programme, same wheel:
both ways 2 of 10, leftward 7, rightward 3 - the same as the drum. and HS lateralizes
far LESS on the sparse scene (left segment, model 000: 15,270 / 11,980 vs 18,600 /
12,990 on the drum; 001: 22,680 / 22,820 vs 7,480 / 2,400): a periodic wide-field
pattern is the motion pathway's best stimulus, which is why the drum has been the
apparatus since 1956. so no: the drum is not the problem, the sparse scene is harder,
and the limit stays where the drum tables put it - at the one-neuron wheel and its
drifting offset.

## smell (14:53 PDT, `loop.py --mode forage`)

the nose is the part of this brain the LIF does best (antennal lobe, mushroom body,
verified plasticity), and we had not used it. plan: two invisible odour patches on the
ground, one with sugar; touch fires taste + PAM dopamine into the mushroom body with
KC->MBON plasticity on; memory carried between episodes; does he learn to find A?

**which steering cells hear smell, and from which side** (1 s, after settle): DNa02 -
none (0-5 spikes, like touch). the DNa family lateralizes to the stronger side at a
2.5:1 ratio: A left 1.0 / right 0.4 -> DNa L 153 / R 137; right-strong -> 37 / 84; B
left-strong 332 / 277, right-strong 219 / 321. KCs respond (500-2,200, right-heavy:
tracing), MBONs respond. so the family went on the wheel for smell, toward the
stronger side.

**in the world it did not steer him.** with landmark posts he orbits a post at 0.8 m
(the visual term wins; the family's odour response is ~16 spikes/s at full strength,
~5 deg/s on the wheel vs 25 deg/s of orbit). with no landmarks (sky and ground only)
he walks past both patches at gain 0.3 (heading +-20 deg in 40 s) and turns without
approaching at gain 1.0; steeper plume (lambda 0.25) no better. min distance ~1 m
every time.

**dose-response, the reason** (DNa L / R in 2 s, net (L-R) per 100 ms chunk):

| left | right | DNa_L | DNa_R | net |
|---|---|---|---|---|
| 1.00 | 0.40 | 370 | 348 | +1.1 |
| 0.40 | 1.00 | 87 | 207 | -6.0 |
| 0.50 | 0.40 | 114 | 185 | -3.6 |
| 0.40 | 0.50 | 101 | 169 | -3.4 |
| 0.30 | 0.27 | 132 | 136 | -0.2 |
| 0.27 | 0.30 | 147 | 138 | +0.5 |
| 0.10 | 0.15 | 343 | 205 | +6.9 |

the family's left-right difference does not track the odour difference except at the
extreme ratio; at plume-scale ratios it is the wrong sign as often as the right one,
and the resting right bias dominates. **bilateral odour comparison is not available
from this readout in this model.** the other route real walking flies use - temporal
comparison, turn more when it gets worse - needs a time derivative somewhere in the
brain; the engine's short-term depression on olfactory afferents is the physiological
place for one. tested next. learning itself (odour + PAM -> KC->MBON change) is not
in doubt (flybrain's conditioning4), but without a steering channel it cannot show as
a change in where he walks.

**temporal route (14:55 PDT): the antennal lobe has the derivative, the wheel does not.**
with the engine's short-term depression on the 2,635 olfactory receptors (U 0.08, tau
480 ms; flybrain's measured values), projection-neuron output (ALPN, spikes per 500 ms)
tracks concentration CHANGE: steady 0.3 -> 1838 then ~1120 (adapted); step up 0.1->0.5
-> 611 to 1890 then decaying; step down 0.5->0.1 -> 1433 to 344; rising and falling
ramps ramp. that is a physiological time derivative, free. but at the descending and
leg-motor level it does not survive: DNa per 500 ms under a STEADY odour goes 78, 110,
14, 1, 124, 9, 23, 105 - a bursty ~1 s cycle unrelated to the profile - and the one
large motor event (leg MN tripling to ~6,100 in the last 1.5 s of the falling ramp) is
a rebound that the step-down profile does not reproduce. no clean derivative code at
the wheel.

**smell, where it stands:** detection works (KCs, MBONs, PNs respond and adapt like
biology); steering does not, by either route, from the readouts this LIF offers -
bilateral comparison fails at plume-scale ratios, temporal comparison does not reach
the motor side cleanly. the learning experiment (odour + reward -> preference) is
blocked on steering, not on memory. options: a wheel closer to the antennal lobe (PN
or MBON laterality, which would be reading his perception rather than his decision,
labelled as such), or the full odour-conditioning readout in open loop, which
flybrain already demonstrated and which is memory without a body.

## the wheel screen (16:27 PDT, `world/dn_screen.py`, `world/dn_wheel.json`)

every descending type with cells on both sides (about 400) screened open loop, two
seeds, six conditions: world rotating left / right (yaw renders), odour stronger on the
left / right antenna (1.0 / 0.4), left / right leg bristles. a "turn-left index" per
modality = (L-R when the fly should turn left) - (L-R when it should turn right):
toward the world's motion, toward the smell, away from the touch.

**seven types agree in all three modalities, all ipsilateral** (more of it on the
left = turn left): DNp18 (vision +49, odour +18, touch +47), DNp20 (+36 / +4 / +22),
DNg49 (+3 / +2 / +122), DNg52 (+2 / +10 / +85), DNpe017 (+2 / +8 / +117), DNge006,
DNa06. ~270 spikes/s pooled, ten times DNa02, and they hear all three senses through
the wiring. DNa02 is not on the list because it hears neither smell nor touch. this is
selection on open-loop data by what a fly should do; nothing closed-loop was used.

**on the wheel it spun him** (+40 to +110 deg/s on a still drum, all seeds). the
pooled cells' left bias is multiplicative, ~3.5:1 in every condition, and any increase
in drive - including the motion he makes by turning - increases L-R, which turns him
left, which makes more motion. four corrections at the wheel, in order: a still-world
offset (underestimated 5:1 because the LIF takes seconds to reach plateau), a 10 s
plateau offset (a fixed number cannot cancel a ratio), per-side normalization against
the still plateau (the ratio is different once he moves: 2:1 driven vs 3.5:1 still),
per-side normalization against direction-averaged open-loop motion (2.8:1 there, 2:1
in the loop). global synaptic depression removed the spin and the response together.
**the lesson: a bias that lives in the hemisphere asymmetry of the model cannot be
fixed at the readout, because the readout's reference state depends on the fly's own
behaviour.** fix it at the source: per descending type, per side, scale the input so
left and right fire alike over a direction-balanced open-loop set (`dn_equalize.py`,
`dn_gains.json`), which is the calibration that held for the transplant.

**source-level equalization (16:35 PDT).** (a) the seven wheel types + DNa02, per type per
side, input gain iterated 4x on the direction-balanced set (`dn_equalize.py`): rates
balanced open loop (DNp18 104/100, DNg49 293/291); on the drum one seed followed both
ways (+25 / -24) with a +23 deg/s still-drum drift, the other did not, and the striped
drum still left a 100/57 offset - the bias is stimulus-dependent upstream of these
cells. (b) **whole-brain hemisphere homeostasis** (`brain_equalize.py`, `brain_gains.npz`):
every cell type with cells on both sides (10,977 types, 134k cells), input gain per
side, 6 iterations: median |L-R|/(L+R) over ~3,000 active types 0.31 -> 0.085. in the
closed loop: the pooled wheel's still-drum offset went UP (743 / 244), DNa02 followed
left only on both seeds (+25 / +4, +33 / -7). total descending activity rose ~70%
(raising the weaker side's gain feeds recurrent loops).

**closing the wheel arc.** the LIF's descending output on this connectome carries a
left-right asymmetry that is multiplicative, stimulus-dependent, behaviour-dependent
and slow-drifting. six corrections were tried - still offset, plateau offset, still-
normalized ratio, motion-normalized ratio, per-type source equalization, whole-brain
source equalization - plus global and central synaptic depression. none produced
symmetric drum following beyond model 000. the optomotor result therefore stands as:
symmetric on flyvis model 000 with the DNa02 wheel (3 seeds), one-sided or absent on
most other models, and this is a property of the LIF + connectome, not of the eye.
the wheel screen's seven multimodal types are a real anatomical finding independent of
this. what would change it: a model with adaptation at every synapse (the transplant
has it; the LIF does not), or the female FlyWire brain as a second specimen to
separate tracing asymmetry from model asymmetry.

**efference copy (17:08 PDT, `loop.py --efference`) - the correction that held.** HS cells in
Drosophila receive a copy of the turn command that cancels the expected visual
reafference of the fly's own rotation (Kim, Fitzgerald & Maimon 2015). implemented
at the wheel: open-loop calibration of each side's response per deg/s of world
rotation (yaw renders at 90 deg/s, above the still pre-period), then in the loop the
response his own last turn predicts is subtracted before steering. DNa02 calibration is
clean and correctly lateralized (world left: L +1.8, R +0.07 per chunk; world right:
L -0.4, R +2.8). drum, model 000: seed 0 still +1.0 / LEFT +17.7 / still -0.3 / RIGHT
-27.2 / still -11.7; seed 1 -2.2 / +9.4 / +9.6 / -8.5 / +7.8. both ways, both seeds,
the still segments near zero. on the pooled screened wheel it does not help (its
response to 90 deg/s rotation is suppression on both sides, more on the left; the linear
prediction is wrong for it). ensemble run with per-model calibration (`world/ens/eff_m*`, 17:26 PDT): **both ways 2 of 10** (008, 009), leftward 3, rightward 8; model 000 itself did not reproduce (LEFT +1.5, RIGHT -30). the two-seed result was fragile. the efference copy joins the list of corrections that do not hold; the wheel arc is closed.

## the second fly (17:16 PDT, `seam/build_flywire.py`, `brain_female.npz`)

the female FlyWire brain (FAFB, release 783; annotations from flyconnectome/flywire_
annotations, connectivity from zenodo 10676866), built into the same node-table format:
139,248 neurons, 2.65M edges at weight >= 5, no ventral cord. sides 69,956 L / 69,088 R
(the male: 6% uneven in neurons, 10% in synaptic weight). the LIF's constants (shiu et al.
2024) were fit on this dataset. descending cells 646 / 649, DNa02 1 / 1, KC 2,580 / 2,597.

**hemisphere symmetry of the descending output under symmetric drives** (1 s, no
hemisphere rebalance, seed 0; |L-R|/(L+R) of all descending spikes):

| drive | male DN L / R | male asym | female DN L / R | female asym |
|---|---|---|---|---|
| rest | 1835 / 1629 | 0.059 | 256 / 363 | 0.173 |
| odour, both antennae 1.0 | 1920 / 2991 | **0.218** | 338 / 326 | **0.018** |
| touch, both sides | 17214 / 16446 | 0.023 | 4789 / 4953 | 0.017 |
| sugar | 3713 / 4374 | 0.082 | 336 / 294 | 0.067 |

under a symmetric odour the male's descending output is 22% right-heavy and his Kenyon
cells fire 2.6x more on the right (1115 / 2958); hers are 1.8% and 1.6x. **the
asymmetry that sank every closed-loop correction is the male map's, not the model's.**
her resting asymmetry (0.17) is on tiny counts (256 / 363 vs his 1835 / 1629).

**she runs cold.** her descending output is ~5x his at rest and under odour, motor
output 0 at rest: the same W_syn on ~half the synapses per connection (54M synapses in
the release vs 125M in the male's). the corollary matters more: **the male is ~2x hotter
than the network the LIF constants were tuned on**, which is the likely origin of the
recurrent build-up and drift seen at his wheel. a W_syn rescale for the male (to match
her per-connection totals) is a labelled, principled experiment for the drift.

**not yet:** her eye. FlyWire annotations carry no column coordinates; columns would have
to come from lamina cell positions or the FlyWire optic-lobe column tables. smell and
touch loops need no eye and can run on her now.

**synaptic strength (17:20 PDT).** per central-brain cell the male carries 1,009 synapses
of input on average, the female 435 (ratio 0.43); mean synapses per edge 14.4 vs 11.7.
the male at the female's per-cell level (W_syn 0.275 -> 0.119) goes silent on the drum:
DNa02 0 / 60 spikes over 12 s, no following, the efference calibration reads zero. so
"match her totals" is not the normalization - at her level the T4/T5 drive of the seam
(150 Hz) no longer reaches the steering neuron. the honest statement is only that his
synaptic density is ~2x hers and the LIF's single strength constant was fit on hers; a
strength between the two would be tuning and was not run. **her sugar:** with only two of
the four sweet types matching his names (71 of 408 gustatory cells driven) seven of her
head motor neurons go from 0 to 4-44 Hz (CB0701 44 Hz). her proboscis circuit is live.

**where the side of a smell lives (17:43 PDT).** her steering family and DNa02 do not
lateralize with the odour side either (left-heavy for a smell on either antenna;
silent below ~0.4 because she runs cold). one layer earlier, the projection neurons:
his are right-heavy for a smell on either side (index -0.04 to -0.28, the right
antennal lobe is the better traced); hers lean a few percent toward the stronger
antenna at 2.5:1 (+0.055 vs -0.025) and lose it at plume ratios (0.3 vs 0.27: +0.061 vs
+0.049). consistent with the biology - fly ORNs project to both antennal lobes and the
surviving bilateral contrast is small (Gaudry et al. 2013). bilateral odour steering is
therefore weak at the PN level and absent at the DN level in both flies.

**her mushroom body was cut out by my build threshold.** `enable_plasticity` found 14
KC->MBON synapses in `brain_female.npz` (his: 33,496). her Kenyon cells make few
synapses each onto an output neuron and the >= 5 cut was chosen on his counts. rebuilt
at a lower threshold (`brain_female2.npz`); conditioning re-run below.

**her Kenyon cells were labelled dopaminergic (17:45 PDT).** the FlyWire per-neuron
transmitter predictions call 5,172 of her 5,177 Kenyon cells "dopamine"; the engine gives
modulatory cells sign 0 and drops their synapses, so her whole KC->MBON layer vanished.
the literature has them cholinergic (Barnstedt et al. 2016) and the annotation table's
`known_nt` column says so for 5,177 of them. the builder now takes `known_nt` where it
exists and forces KCs cholinergic, labelled. rebuilt at synapse count >= 2 (her KC->MBON
connections carry a median of 2 synapses; at >= 5 only 16,073 of 89,315 survive):
`brain_female2.npz`, 6.76M edges, **43,616 plastic KC->MBON synapses** (his 33,496).

**her first conditioning, open loop:** odour A + sugar + PAM dopamine x5, B unpaired.
KC->MBON weights 0.9993 of naive after five trials - a change of 0.07%. MBON response to
A 243 -> 208 (-14%), to B 210 -> 216; MBON28 / MBON05 / MBON20 most suppressed for A.
the sign is right (appetitive learning depresses the avoidance-driving MBONs) and the
size is far below anything that could steer her. same class of problem the flybrain
author hit on the male (see its FINDINGS: kc_normalise, trace scales, kc_thresh) and the
same cause is likely: a KC code too sparse and weak for the eligibility traces to
register. measured next: her KC activity per odour vs his and vs the biological ~5%.
also noticed: her descending neurons answer odour B (588 spikes) and not A (4) before
any training - the two synthetic odours are not equal to her.

**her mushroom body is starved at the LIF's constant (17:47 PDT).** same odour, 800 ms:

| | ORNs driven | PN mean rate | KCs active | KC spikes |
|---|---|---|---|---|
| male, W_syn 0.275 | 531 / 2635 | 21.3 Hz | 250 / 4064 = **6.2%** | 3,261 |
| female, W_syn 0.275 | 397 / 2282 | 7.0 Hz | 41 / 5177 = **0.8%** | 206 |

the biological Kenyon-cell sparsity is ~5% (Turner et al. 2008; Honegger et al. 2011).
his is there; hers is not, because her release counts fewer synapses per connection and
the single strength constant does not know that. sweep on her:

| W_syn | PN Hz | KC active | DN /s | motor /s |
|---|---|---|---|---|
| 0.275 | 7.0 | 0.8% | 5 | 0 |
| 0.35 | 7.8 | 1.5% | 41 | 0 |
| 0.45 | 8.7 | 3.8% | 819 | 1 |
| 0.55 | 9.5 | 6.3% | 4,799 | 199 |
| 0.70 | 10.4 | 10.3% | 7,406 | 1,539 |

**her strength is set to 0.50, calibrated to 5% KC sparsity** - to the animal, not to
him or to any readout of ours. (the corollary for him: at 0.275 his mushroom body is
already biological, so his "hotness" relative to her is her coldness, not his excess;
the W_syn-rescale idea for his drift is withdrawn.)

**she learns (17:52 PDT, W_syn 0.50, open loop; `world/condition_female.py`).** odour A +
sugar + PAM dopamine, eight pairings, B unpaired:

| | KC->MBON weights | synapses < 90% | MBON to A | MBON to B | DN to A | DN to B | DN A/B |
|---|---|---|---|---|---|---|---|
| before | 1.000 | 0 | 942 | 1173 | 1267 | 2296 | 0.55 |
| after 8 | 0.987 | 1,315 | 788 | 1039 | 2045 | 2230 | 0.92 |

the avoidance-side output neurons MBON05 and MBON03 fire about a third as much to the
rewarded odour as to the other afterward (33 vs 95, 24 vs 82). the rewarded odour's drive
to her descending neurons rose 61% while the unrewarded odour's did not move. memory
reaching the action bus, in the female, at the strength calibrated to her KC sparsity.
controls (reward B instead; seed 1; reward unpaired with any odour) follow - and
withdraw the descending-neuron part; see the next block.

**controls (17:52 PDT):**

| protocol | weights | synapses < 90% | MBON to A | MBON to B | DN to A | DN to B |
|---|---|---|---|---|---|---|
| reward A, seed 0 | 0.987 | 1,315 | 942 -> 788 (-16%) | 1173 -> 1039 (-11%) | 1267 -> 2045 | 2296 -> 2230 |
| reward A, seed 1 | 0.987 | 1,330 | 940 -> 810 (-14%) | 1115 -> 1056 (-5%) | 2674 -> 1408 | 2199 -> 2255 |
| reward B, seed 0 | 0.984 | 1,527 | 942 -> 861 (-9%) | 1173 -> 865 (**-26%**) | 1267 -> 2447 | 2296 -> 2215 |
| reward unpaired | 0.998 | 324 | 942 -> 941 (0%) | 1173 -> 1099 (-6%) | 1267 -> 1479 | 2296 -> 2295 |

**the MBON effect is real, specific and replicated:** the output neurons' response to the
REWARDED odour drops most (A rewarded: A -16 / -14%, B -11 / -5%; B rewarded: B -26%, A
-9%), and an unpaired reward changes almost nothing (324 synapses vs ~1,300). **the
descending-neuron effect is not:** DN drive to A rose 61% with A rewarded (seed 0), rose
93% with B rewarded, FELL 47% with A rewarded on seed 1, and rose 17% with no pairing at
all. the "memory reaches the action bus" line above is withdrawn; what reaches the bus in
these runs is run-to-run state, not the memory. memory forms at the mushroom-body
output, specifically and reproducibly; between MBON and DN the signal is not
recoverable from single 800 ms probes. (the flybrain findings report the same gap on
the male and closed it only with parameter changes at the KC threshold; not done here.)

## the room (18:09 PDT, `world/pair.py`)

two real brains in one arena: the male (MaleCNS, flyvis eye on model 000, touch, DNa02
wheel) and the female (FlyWire, W_syn calibrated, no eye, DNa02 + heading noise). he sees
her as a dark sphere and smells fly odour from her (Or47b/Or88a, bilateral, exp(-d/0.8));
she smells cVA from him (Or67d); contact drives bristles on both; a song bout (his pIP10
above its running mean + 2 sd within 0.4 m) drives her Johnston's organ at 100 Hz.
readouts: his pC1 (156 P1-type cells), pIP10, mAL, LC10a; her pC1a-e, vpoEN, DA1 PNs.
viewer: "the room" artifact (her in rose, distance in the map caption).

**first episode:** they met at 5 s (85 contact frames), then he wandered to ~2 m. his pC1
climbed 0 -> 210 spikes per 5 s over the run; pIP10 never fired; her pC1 7 -> 49.
**him alone, same room:** pC1 0, 0, 128, 111, 165, 184 - the same climb with no female.
open loop: his pC1 fires to touch (174 / s) and not to fly odour (0); so the climb is
his post-bumping. **his P1 activity in the room is not about her (yet).** pIP10 does not
follow P1 in this LIF (1 spike in 30 s). her cVA pathway was silent - and that was a
build bug, next.

**co-transmitter strings.** her `known_nt` values read "acetylcholine, sNPF" etc.; the
sign table looked up the whole string and gave 27,547 of her neurons sign 0 (his build:
3,070), which silently dropped their synapses - including every ORN_DA1 (cVA) and much
else. the builder now takes the first fast transmitter of a co-transmitter list. after
the rebuild (7.63M edges, 8,499 sign-0): cVA 1.0 -> her DA1 PNs 1,934 spikes, KCs
respond; song -> her pC1 cluster 10 spikes and DN 3,971. vpoEN still silent. **her
conditioning and sparsity numbers above were measured on the broken build and are
being redone.**

**when he flies (nate, 18:09):** Johnston's organ also senses wing-induced airflow during
visually driven turns and feeds the turn back positively (the antenna on the outside of
the turn moves into the wing wash). he walks, so not now; the flight motor neurons (DLMn,
DVMn) are in his nerve cord, and that loop is the first thing to wire when he flies.

**the room, take two (18:21 PDT).** nate, from the render: the posts were fly-sized
spheres, so a post and the female were the same object to him, and he orbited the post;
the flies passed through each other. fixed: posts are pillars (floor-to-sky cylinders,
r 0.35, bark-dark 0.08; `omma.Scene(pillars=...)`, and the viewer's own raytracer draws
them too), the flies are solid (pushed apart on contact), her body is the larger sex's
(r 0.12 to his 0.05 collision body) and fly-toned (0.5) against a 0.4 ground and 0.8 sky.
her W_syn is 0.45 on the fixed build (6.0% KC sparsity). with pillars he stops bumping
things and his P1 stays at 0-1 spikes per 5 s the whole run (it was touch after all);
they came within 0.47 m and touched for 36 frames; pIP10 1 spike; her pC1 2. **no
courtship behaviour yet:** his P1 needs contact-pheromone input (the ppk23 leg neurons
are not typed by name in either build), his song neuron does not follow P1 in this LIF,
and her receptivity neuron vpoEN is silent to everything tried.

**her conditioning, redone on the fixed build (W 0.45):** weights depress as before
(reward A: 1,388 synapses < 90%; unpaired: 164) but the output barely moves: A rewarded,
MBON-to-A 654 -> 652; B rewarded, MBON-to-B 776 -> 725 (-7%), MBON-to-A +10%. the
16-26% drops reported above were measured with 27,547 of her neurons silenced by the
co-transmitter bug and are withdrawn as numbers; the direction survives weakly. memory
forms at the synapse; on the honest build it is not yet expressed at the output.

## the song (18:40 PDT)

**the hop works:** drive his P1 (156 pC1-type cells) at 50 Hz and pIP10, the song
descending neuron, fires 142 spikes/s (71 per cell); at 150 Hz, 276. P1 -> pIP10 is 93
edges, 1,796 synapses. so silence in the room is upstream of P1.

**P1's sensory drive is net inhibitory under contact.** P1's largest inputs are mAL_m8
(-3,241), mAL_m1 (-3,182), SMP702m, oviIN, SIP116m - the mAL gate. bristles + fly odour
give P1 ~60 spikes/s over 156 cells; the contact-pheromone leg neurons exist
(`receptorType` putative_ppk23, 269 cells; putative_ppk25, 257) and driving all of them
gives P1 0 and mAL 104 - the brake. biology: ppk23 has F-cells (female pheromone -> P1)
and M-cells (male pheromone -> mAL -> P1 off; Thistle et al. 2012); the annotation does
not split them. vAB3 does not exist by that name here (the path runs through AN05B102).
**an arousal hold on P1** (tonic drive, as the engine's mbon_hold) at 0.85 of threshold
makes him sing alone (13 pIP10 spikes, no female) and contact then REDUCES P1 (1168 ->
552). wrong twice; discarded. next: split ppk23 by wiring (two-hop reach to P1 vs to
mAL) into F-like and M-like, and drive only the F-like on contact with her.

**F/M split by wiring (18:45 PDT, `world/ppk23_split.npz`).** two-hop signed reach from
each putative ppk23 cell to P1 and to mAL. the bottom 40% by (P1 - mAL) reach drive
mAL hard (658) and P1 not at all: M-like. the top 40% leave mAL alone (10) and, with
bristles and fly odour, give P1 147 spikes/s - twice what all 269 together give (66),
because the M-like brake is out of the sum. **still two orders of magnitude short of
the ~7,000 P1 spikes/s that make pIP10 sing.** the song is not reachable from his
senses in this model; the gate is real and the drive is small. left there.

**pace, from the wiring:** leg motor neurons (699 in his cord) fire ~4,000 spikes/s
standing, ~6,400 with an odour, ~25,000 when touched; DNp09 (forward walking, 2 cells)
and MDN (backward, 4) are both present and each raises leg output ~70% when driven.
in `pair.py`: his speed = 0.45 m/s x clip((legMN - standing) / (4 x standing), 0, 1) +
0.05; reversed at half speed when MDN outfires DNp09. she has no cord: her descending
total stands in, labelled. his contact with HER (not with a pillar) now also drives
the F-like ppk23 neurons.

**pace, measured in the room (18:54 PDT).** his leg motor output ran 402-1,126 spikes
per 100 ms (median 687) against a standing 398, so speed = 0.05 + 0.45 x clip((legMN -
398) / 1592) puts him at 0.05-0.25 m/s, varying with what he senses. MDN, the
backward-walking driver, fires tonically (~10 spikes per chunk, 4 cells) under visual
drive in this LIF while DNp09 (forward) is silent (0.09); a reverse rule keyed on MDN
walked him backward for a whole run. no reverse rule; MDN's tonic activity is noted as
a model property (in life it is silent unless triggered). she has no cord: constant
0.15 m/s, labelled.

## the room, take three: walls that are walls (20:08 PDT)

**a correction first.** the 5-minute room (`world/pair_long.npz`) was reported as four
encounters with his P1 at ~9 spikes/s "near her". nate, from the map: the touch rings
were pillar touches and the flies never visibly met. both true. the sim's contact rule
fired at 20 cm centre-to-centre while his drawn body was 16 cm and hers 24 cm, so
"contact" was a 3 cm gap between the drawn bodies - a near miss on the map. of 139
touch frames, 56 were that rule and 26 were pillars; the rings did not say which. his
P1 by chunk: 6.2 spikes in those "contact" chunks, 0.6 within 40 cm without contact,
0.02 far. so the P1 response was touch-driven as claimed (F-like ppk23 + bristles on
the contact rule), and the contact was one the viewer could not show. **fixed:** contact
is when the drawn bodies meet (his r 0.08, hers 0.12), the viewer draws both collision
bodies and rings touches in two colours (grey: wall or pillar; rose: her), and the
touch readout says which. `touch_kind` is saved (1 wall/pillar, 2 her).

**walls.** they were mirrors: crossing x = 2 flipped his heading and clipped his
position, with no touch and nothing to see - the raytracer had sky, ground, pillars,
spheres, and no room. nate: "can we have this activate touch instead of just a bouncy
trampoline surface?" now: (1) the walls hold him at the surface and fire his bristles
on the wall's side, exactly as pillars do; (2) they are rendered, in both raytracers,
as a 1 m band of albedo 0.6 (lighter than the 0.4 floor, darker than the 0.8 sky);
(3) while any bristles are pressed, his leg-MN asymmetry steers alone and vision is
dropped for the chunk. (3) was forced by measurement: with the wall on his left, his
DNa02 wheel said "turn left" (R-L = -1.15 per frame vs +0.95 free) and cancelled the
reflex to -0.7 deg/chunk; he sat on the south wall for 52 of 60 s.

**the reflex, calibrated.** the touch term was 30 x (leg asymmetry - rest), which is
under a degree per chunk for the asymmetry a bristle actually evokes. it is now
calibrated in the standing phase: left bristles driven give (R-L)/(R+L) = -0.090,
right +0.050, and the gain (86 deg per unit) makes that worth 6 deg/chunk. pillars
"worked" before only because sliding around a small cylinder is what a pinned fly does.

**result, 60 s, seed 2:** frames at a wall 87% -> 22%; longest pinned stretch 52 s ->
5.7 s; yaw with wall on the right +8.9 deg/chunk, on the left -3.1 (his leg output
leans left at rest, -0.038; the male map, again), head-on +3.9. **his pace dropped**
from a saturated 0.50 m/s to 0.12-0.22: the leg-MN drive is scene-dependent and a
room of mid-grey wall is a calmer scene than open sky. that is a property of the
readout, recorded, not tuned away. the 5-minute room is being re-run under these rules
(`world/pair_long2.npz`). viewer: `world/viewer_walls.html` (local).

**the room is not repeatable, and why (20:25 PDT).** two runs of the same seed diverge in
the first chunk, in his leg-MN count, before he has moved. rendering is identical for
those frames and the LIF step is deterministic (the compiled step matches the numpy
step spike-for-spike from the same seed, 1,000/1,000 on both brains), so it is flyvis:
the same 10 frames through `net.simulate` three times give three answers differing at
1.4e-6 (GPU scatter order), which is enough to flip a Poisson draw in the T4/T5 drive,
and the two brains then take their own paths. so every "N seeds" in this record was N
seeds plus GPU chaos - fine for behaviour claims, which are statistical, and no good for
exact regression checks. `torch.use_deterministic_algorithms(True)` fixes it (three
calls identical) at 72 ms vs 8 ms per eye per chunk; `pair.py --deterministic` turns it
on, off by default.

**head-on (20:42 PDT).** the first 5-minute re-run (seed 3) sat pushing into a wall for
273 of 300 s: head-on contact ("B", |bearing| < 8 deg) drove both bristle sides, the
leg asymmetry was ~0, and yaw was +1.6 deg/chunk against a wall he could not pass. no
wall is exactly head-on: the class is gone for walls and pillars, whichever side the
bearing leans to owns the reflex. 60 s, seed 3: wall time 22%, longest pinned 11.2 s
(was 92% / 273 s). 5-minute run relaunched under this rule.

**the 5-minute room, walls that are walls (20:59 PDT, seed 3, `world/pair_long2.npz`).**
wall time 30%, 12 wall visits, longest pinned 19 s; he covered 55 m at a mean 0.23
m/s. **no contact with her in 5 minutes:** closest 0.25 m, two passes within 0.5 m
(142 s for 2.2 s, 209 s for 1.7 s). his P1 by what he was touching: 9.9 spikes per
chunk against a wall or pillar, 1.4 near her without contact, 0.1 free and far - the
touch-driven P1 again, now with the touch source known. pIP10 630 spikes in 5 minutes,
no song bouts. viewer: `world/viewer_room_5min_walls.html` (local, stride 4; ring
colours say what he touched).

**she becomes visible (21:10 PDT).** nate, from the 5-minute viewer: the one moment he
tracked her was when she passed in front of a dark pillar, and then she walked into
the pillar (no collision) and vanished. her body was 0.5 against a 0.4 floor and 0.6
walls: invisible by construction. nate proposed white for contrast; done the other way
round, on his measured behaviour: flies are dark and every approach he has shown is
toward dark things in a light world (posts, bar). so she is 0.1 and the pillars are
pale (0.85), making her the only dark object in the room; and she now collides with
pillars (held at the surface, her bristles on that side, her turn-away rule acts).
60 s, seed 3: they met at 10 s (85 contact frames, his first real contact with her in
this arena), wall time 5%; range rate when she is ahead of him -0.11 m/s. no approach
claim from one minute: his yaw when she is ahead-left is -0.19 and ahead-right -0.48
(his rightward lean, not her). three 2-minute seeds running to ask it properly.

**does he turn toward her? (22:20 PDT; seeds 4-6, 120 s, and the invisible-her 5-minute
run as control).** statistic: his yaw per chunk (+ = left) when she is ahead-left
(bearing 10-90) vs ahead-right (-10 to -90), free of walls, against each run's own
free-walking mean (his rightward lean, -0.3 to -0.8).

| run | yaw, she ahead-left | n | yaw, ahead-right | n | free mean |
|---|---|---|---|---|---|
| her invisible (0.5), 5 min | -0.58 | 793 | -1.71 | 192 | -0.57 |
| her dark, seed 3, 60 s | -0.19 | 192 | -0.48 | 185 | -0.44 |
| her dark, seed 4 | +0.05 | 142 | -0.39 | 526 | -0.47 |
| her dark, seed 5 | +1.47 | 247 | -0.71 | 261 | -0.30 |
| her dark, seed 6 | +0.77 | 283 | -0.99 | 155 | -0.84 |

with her dark, she-ahead-left shifts his yaw leftward of his own baseline in 4 of 4
runs (by 0.25 to 1.8 deg/chunk), against his lean; with her invisible it does not
(-0.58 vs -0.57). she-ahead-right is more rightward than baseline in 2 of 4. contact
in 3 of 4 dark runs (85, 57, 90, 0 frames) vs 0 in the 5-minute invisible run.
**reading: a weak, left-side-consistent turn toward a dark her, on the same one-neuron
wheel whose rightward lean has been the story all day.** suggestive; not a claim. the
clean test is her at 0.1 vs 0.5 across 10 seeds each, which is a `run_many.py` job.

**the clean test (23:50 PDT; seeds 10-19, 120 s, her 0.1 vs 0.5, `world/approach/`).**
yaw shift = his mean yaw when she is ahead-left (or ahead-right), free of walls, minus his
free-walking mean in that run.

| her | ahead-left shift | seeds > 0 | ahead-right shift | seeds < 0 | runs with contact | contact frames | time < 0.5 m |
|---|---|---|---|---|---|---|---|
| dark 0.1 | +0.49 | 10/10 | **-0.34** | **8/10** | 7/10 | 113 | 10.9% |
| invisible 0.5 | +0.52 | 10/10 | -0.05 | 4/10 | 7/10 | 49 | 6.1% |

**the ahead-left shift is an artefact:** it is the same with her invisible (Mann-Whitney
p = 0.49). the "left-side-consistent turn toward her" read from four runs above is
withdrawn; it was the geometry of where he is when she happens to be ahead-left. **what
survives:** with her dark he shifts right when she is ahead-right (8/10 seeds, one-sided
Mann-Whitney p = 0.019 against invisible) and spends ~1.8x the time within 0.5 m of her
(contact frames 2.3x). a weak right-side turn toward a dark her on a right-leaning wheel,
plus more time near her. suggestive; not yet a claim (n = 10, one-sided test, one
statistic chosen after looking at four runs). the running-baseline steering fix and the
corrected constants come first, then this test again as a pre-registered one.

## proprioception (21:25 PDT, `pair.py --proprio`)

nate: will hooking senses up one by one normalise him or make chaos? "only one way to
find out." starting with the one sense that is a loop: his leg proprioceptors
(mechanosensory_proprioceptive, 1,383 cells: SApp/SNpp leg chordotonal and campaniform
types, 699 L / 683 R, all vnc_sensory or ascending) have been silent in every run, so
his brain has been walking without feeling its legs. **open loop, standing, 2 s:**

| proprio drive | leg MN /s | DN /s | whole brain /s | cells > 1 Hz |
|---|---|---|---|---|
| 0 Hz | 3,470 | 901 | 14,444 | 1,512 |
| 20 Hz | 7,170 | 6,308 | 95,462 | 6,237 |
| 50 Hz | 9,839 | 606 | 136,112 | 4,493 |
| 100 Hz | 16,027 | 1,626 | 245,641 | 5,205 |

the loop is strongly positive (proprio -> leg MN doubles at 20 Hz) and the brain as a
whole is very sensitive to these cells (6.6x at 20 Hz); DN output is not monotonic.
that is the chaos warning in numbers: this brain rests at 0 Hz and every input pushes
up. closed-loop rule (labelled): rate = peak x clip(pace / 0.45) x (0.5 + 0.5 sin 2pi
10 Hz t), phasic with a 10 Hz step cycle, since real leg proprioceptors fire with the
step, not tonically.

**closed loop, tonic rule, 60 s seed 3 (21:35 PDT):** pace 0.13 vs 0.11 without, leg MN
704 vs 624 per chunk, DN output 581 vs 238. not runaway: at his actual pace the drive
is ~3 Hz per cell and the loop gain sits below one. but DN output doubled, so the
brain felt it.

**legs, from the wiring (22:00 PDT; nate: "does driving his proprioception mean you
need physics-accurate legs?").** no legs, but a gait: the MaleCNS table carries
`entryNerve` and `rootSide` per sensory cell, which splits his proprioceptors into six
legs (ProLN / MesoLN / MetaLN x L / R): L1 35, R1 17, L2 127, R2 133, L3 130, R3 138
(the front-leg counts are a tracing asymmetry of the table, noted), and says the tonic
rule had been driving 396 haltere (DMetaN) and 237 wing-nerve (ADMN) cells with a
walking rhythm, which a walking fly's halteres would not do. `world/legs.npz`. new
rule: leg-nerve cells only; tripod gait at 10 Hz (L1 R2 L3 vs R1 L2 R3, half a cycle
apart), each leg's sensors fire in its stance half-cycle at peak x pace, plus a 15%
tonic load term. no joint angles, no forces: what the wiring can address is which
leg and when, so that is what he gets. physics legs become worth building when a
readout distinguishes joints, and nothing here does yet.

**gait rule, 20 Hz peak, 60 s seed 3 (22:13 PDT):** pace 0.11, leg MN 632 (L 331 / R
301), DN 248, wall 6%: indistinguishable from no proprioception. at his pace the
per-cell mean is ~4 Hz on 580 cells and the brain does not notice. neither
normalised nor chaos: below threshold. 50 and 100 Hz peak running.

**gait gain sweep, 60 s seed 3 (22:23 PDT):**

| proprio peak | pace (sd) | at max | leg MN /chunk | DN | wall | her-contact | his pC1 total |
|---|---|---|---|---|---|---|---|
| 0 | 0.11 (0.12) | 8% | 624 | 238 | 5% | 85 | 4,870 |
| 20 | 0.11 (0.12) | 7% | 632 | 248 | 6% | 39 | 6,090 |
| 50 | 0.12 (0.12) | 7% | 651 | 263 | 6% | 68 | 4,900 |
| 100 | 0.09 (0.04) | 0% | 524 | 199 | 0% | 41 | 220 |

20 and 50 are nothing. at 100 Hz peak the loop turns over: pace variance drops to a
third, he never touches a wall, leg MN and DN output fall, and his P1 (touch-driven)
falls 20x because he stops bumping. the open-loop tonic table went the other way
(leg MN up 4.6x at 100 Hz), so this is the phasic, leg-only drive acting as negative
feedback at his walking pace. **first answer to "normalise or chaos": at the one gain
that does anything, normalise.** one seed, one minute; a sweep across seeds is next.

## physiology briefs (22:40 PDT, `docs/physiology/`)

nate: send agents to collect how the receptors are really driven. three opus agents,
one per system, each writing rates, time constants and a one-line-per-class drive
rule with citations. first back: `chemo_thermo_hygro.md` (3,900 words). what it
corrects in this record:

- **the contact-pheromone tap.** our 150 Hz tonic hold on the F-responsive ppk23 cells
  has no measurement behind it (all the ppk23 work is calcium imaging); the grounded
  ceiling for a contact GRN is ~60 spikes/s (Weiss 2011) and a single tap is a complete
  trigger (Kohatsu 2011), so it is a burst, not a hold; and both F- and M-responsive
  cells fire on contact in life with P1 weighing them (Kallman 2015), so silencing the
  M channel was wrong. **changed:** tap = 60 Hz decaying with tau 300 ms on both
  channels at contact onset with her.
- **VP1m / VP1l labels.** Marin 2020 infer VP1m = humid and VP1l = cool, the opposite
  of the annotation prefixes (TRN_VP1m, HRN_VP1l). we have not driven either; audit
  before we do.
- **cooling cells rest at ~95 Hz** regardless of temperature and fire to -dT/dt only
  (Budelli 2019); hot cells are tonic and exponential in T (37 Hz at 25 C, Q10 4.4).
  so the posterior antennal lobe is missing a ~95 Hz tonic input in every run so far.
  the warm corner, when built, reads these rules.
- **plumes are intermittent** (power-law whiffs, Gorur-Shandilya 2017) and ORNs divide
  by a running mean (Weber-Fechner); our smooth exp(-d/0.8) odour is the wrong shape.
- Or67d rests at 0.12 Hz, not our generic ~8.

**briefs 2 and 3 (22:50 PDT): `mechanosensation.md`, `vision_motor_courtship.md`.**
what they correct, in order of consequence:

- **the male's heat has a number.** Plaza 2025 (bioRxiv 2025.10.16.682869) compares
  synapse detection across fly EM volumes: FIB-SEM finds ~1.49x more synapses than
  ssTEM for the same tissue (male CNS vs FAFB pair: 1.49, missed synapses ~random).
  MaleCNS is FIB-SEM, FlyWire is ssTEM, and Shiu's 0.275 mV per synapse was fit on
  FlyWire. so every male edge is ~1.5x too strong. **tested (22:55, odour A at 1.0,
  2 s):** KCs active 28% at 0.275 -> 7.9% at 0.185 (KC 6.4 -> 0.9 Hz, MBON 39 -> 12.5);
  the female at 0.275: 4.7%, KC 0.6 Hz. target ~5%. so the corrected constant puts both
  brains in the same sparse regime, and her 0.45 (calibrated on a different odour
  protocol) is over. **decision: male 0.185, female 0.275, from the next room run
  (`--wsyn-m`, `--wsyn-f`); every baseline re-measured.** the rest-state test says
  nothing (both silent), the tonic MDN activity noted on 09-16 goes away at 0.185.

**first minute at the corrected constants (2026-09-17 00:00 PDT, seed 3, `world/
pair_w185.npz`).** standing baselines are all zero now: his DNa02 rest offset 0.00, his
standing leg MN 0 (was 398 per chunk), her standing DN 0. walking, his leg MN halves
(624 -> 306 per chunk), DN 238 -> 176, DNa02 4.3/3.9 -> 1.6/1.4 per chunk, her pC1 1,580
-> 0, her DN 220 -> 72. he met her (101 contact frames) and his P1 fired 1,950 to touch.
**the pace readout is degenerate at these constants:** speed = 0.05 + 0.45 x clip((leg MN
- standing) / (4 x standing)) with standing = 0 saturates on any output, so he ran at
0.50 m/s the whole minute (sd 0.02) and covered 27 m, wall time 25%. that rule assumed a
tonic standing rate the corrected brain does not have (the physiology says slow leg MNs
fire ~30 Hz standing; this LIF gives 0). the pace readout needs an absolute reference and,
per the vision brief, weighting by MN class: an effectors-refactor item, not a midnight
tune. the touch reflex recalibrated itself (gain 53). the corrected brain is quieter
everywhere and still walks, feels, and finds her; the readouts on top of it are what have
to be rebuilt, which is the plan. oracle runs (refactor step 1) launched 00:05:
`world/oracle/room_{old,new}_s{3,4}.npz`, deterministic, 30 s.

## the refactor begins (2026-09-17 00:35 PDT, `docs/ARCHITECTURE.md`)

**step 1, the oracle:** four deterministic 30 s rooms (seeds 3 and 4, old and corrected
constants) from the pre-refactor script, frozen as `world/oracle/pair_oracle.py` (a copy
of `world/pair.py` at df26aa7). a lesson on the way: the first attempt edited `pair.py`
while its oracle runs were queued, and two "oracles" ran on half-ported code. an oracle
you can edit is not one; hence the frozen copy. `scripts/oracle_check.sh` reruns the
comparison.

**step 2, the receptor registry** (`src/fly_afterlife/receptors.py`): annotation-table
selectors (class / type / side / entryNerve / rootSide / receptorType / bodyId) that
reproduce every hand-built cell set in the room (bristles L 1,224, ppk F 108, leg R3 138,
the 580 leg-nerve proprioceptors, 394 haltere cells they exclude); transducers with their
sources on them (Hold, Scaled, TapBurst, GaitLeg, Gate); a registry applied in order. the
room's drive block ported: five lines where there were fourteen, every float and one
quirk (the gait evaluated at chunk-end time) kept. **verified: 69 arrays x 4 configs,
bit-identical to the oracle.** next: body + world (step 3).

**step 3, body + world (00:58 PDT):** `src/fly_afterlife/body.py` (pose, speed, radius,
albedo, this frame's contact) and `world.py` (`Room`: walls, pillars, the pair, the scene
for the eye; `step_frame` in the script's exact order). the room script's physics block is
three lines. two pillar-hold formulas (his by offset ratio, hers by polar angle) are kept
distinct because they are not bit-equal; unifying them is its own change. **verified: 4
configs x 69 arrays, bit-identical.** a hole in the check found on the way: a failed port
run inherited the previous pass's output file and "passed"; the check now deletes port
outputs first. (the regex that renamed variables also renamed a log key inside single
quotes; caught by the same failure.)

**step 4, effectors (01:10 PDT):** `src/fly_afterlife/effectors.py`: `Steering` (his DNa02
wheel + touch reflex), `Pace`, `HerSteering` (consumes the episode rng in the same order),
`SongDetector`, and the three calibration procedures (DNa02 rest offset, standing
baselines, reflex gain) as functions over the brain. each carries its assumptions and the
physiology it contradicts. the room script's per-chunk block is four lines. **verified: 4
configs x 69 arrays, bit-identical.**

**step 5, the episode (01:21 PDT):** `src/fly_afterlife/episode.py`: one chunk loop (render
and move, front end, smells, drive and step, effectors, log) and the save. `world/pair.py`
is 134 lines, all of it setup: brains, registries, room, bodies, calibrations, effectors,
then three lines to run. **verified: 4 configs x 69 arrays, bit-identical.** the refactor's
verified core is done in one night: five layers, five oracle passes, the record unchanged.
`world/loop.py` is not ported: it is a research script of one-off calibration variants, most
of them withdrawn; its modes (drum first) are re-implemented on the stack and validated
against the recorded numbers instead.

**the drum on the new stack (01:28 PDT, `experiments/drum.py`).** a `Drum` world (striped
cylinder at infinity, the same programme), a single-fly `Episode` (her = None), the flyvis
front end as its own module (`frontend.py`, the room script's block verbatim), `Steering`
with the touch term off, no pace. heading rate per phase, deg/s (+ = left), model 000,
0.275 mV:

| seed | still | drum +30 | still | drum -30 | still | follows both ways |
|---|---|---|---|---|---|---|
| 0 | +2.1 | **+21.9** | +0.4 | **-8.8** | +25.0 | yes |
| 1 | -8.6 | **+5.0** | -21.9 | **-21.7** | +1.9 | yes |
| 2 | +2.5 | -1.9 | -6.6 | **-6.2** | +4.5 | no |

2 of 3 follow both ways (the record's `loop.py --rest-sub` result on model 000 was 3 of 3,
and 2-3 of 10 across the ensemble); the still-phase drift (-21.9 in seed 1) is the same
resting bias the wheel has always had. the new stack reproduces the recorded behaviour
within the fragility already on record; it is not a bit-identical port and does not
claim to be. this is the drum the running-baseline steering fix (TODO 2) gets tested on.

## the first physiology change: running-baseline steering (01:49 PDT, `RunningBaselineSteering`)

the vision brief: rotational velocity is linear in DNa02 right-minus-left through its whole
range with zero at zero (Rayshubskiy 2020), so the resting lean is not physiology; reference
each side to its own running mean (~2 s) before differencing. every fixed correction tried on
09-16 (still offset, plateau offset, still- and motion-normalised ratios, equalisation) failed;
this is the first running one. rule: base_side += (count - base_side) / 20 per chunk, updated
after use; net = (R - base_R) - (L - base_L); the rest as before. drum, model 000, three seeds,
heading rate deg/s (+ = left) in the two moving phases:

| seed | fixed offset: drum +30 / -30 | both | running baseline: +30 / -30 | both |
|---|---|---|---|---|
| 0 | +21.9 / -8.8 | yes | +11.6 / -10.4 | yes |
| 1 | +5.0 / -21.7 | yes | +4.5 / -9.8 | yes |
| 2 | -1.9 / -6.2 | no | +5.1 / -8.8 | yes |

3 of 3 with the running baseline (2 of 3 fixed), with smaller, more symmetric magnitudes.
the price shows in the still phases after a moving one (-24.9, -8.2, -13.8 deg/s): the
baseline adapts to the moving-phase rate, so when the drum stops the difference flips, an
after-effect of the estimator (waterfall illusions are real biology; this one is 2 s of
arithmetic and should be called what it is). the test that matters is the ensemble, where
fixed was 2-3 of 10; running now.

**the ensemble (01:55 PDT; 10 flyvis models, seed 0, heading rate deg/s in the +30 / -30
phases):**

| model | fixed offset | both | running baseline | both |
|---|---|---|---|---|
| 000 | +11.9 / -26.8 | yes | +8.7 / -14.0 | yes |
| 001 | -40.6 / -30.9 | no | -18.4 / +0.4 | no |
| 002 | +33.3 / +15.0 | no | +7.1 / +3.9 | no |
| 003 | -4.9 / -16.2 | no | +7.2 / -11.6 | yes |
| 004 | -91.6 / -29.5 | no | -16.4 / +13.8 | no (anti) |
| 005 | -103.2 / -107.6 | no | -20.8 / +18.5 | no (anti) |
| 006 | -13.4 / -13.5 | no | -2.3 / -1.3 | no |
| 007 | -8.2 / -28.7 | no | -4.8 / -19.8 | no |
| 008 | +2.8 / -10.9 | yes | +11.6 / -12.1 | yes |
| 009 | -0.2 / -8.8 | no | +4.0 / +0.9 | no |

**fixed 2/10, running 3/10.** what the running baseline does: it removes the lean (biases
of -100 deg/s become +-20) and so makes the wheel's sign readable per model; what it
reveals is that two models (004, 005) follow the drum *backwards* in both phases, which
the fixed offset had buried under the bias, and four are near zero. so the running baseline
is the right estimator and not a fix: the one-neuron DNa02 readout's sign is not consistent
across flyvis models on this seam, as the 09-16 ensemble section already said from the
other direction (HS robust 8/10, DNa02 not). the steering rule stays running-baseline from
here (it is what the physiology says and it does not hide anything); the wheel's
model-dependence goes back on the list as a seam question (direction selectivity per
model), not a steering one.

## morning, 2026-09-17: the pace readout, then the corrected brain (08:58 PDT)

**`RunningPace`:** v = 0.05 + 0.45 x clip(legMN / (2 x running mean legMN), 0, 1), mean
updated after use (tau 20 chunks). the same estimator the steering now uses: his own recent
history is the reference, so it works at any synapse constant. labelled; the physiology item
(MN class weights, Azevedo 2020) stays open. `pair.py --steer running --pace running`.

**male-only minute, seed 3, old vs corrected:**

| | 0.275 mV, fixed rules | 0.185 mV, running rules |
|---|---|---|
| pace mean (sd) | 0.08 (0.03), at minimum 6% of the time... | 0.20 (0.13) |
| leg MN / chunk | 492 | 193 |
| DNa02 L / R per chunk | 3.92 / 4.03 | 2.14 / 0.63 |
| wall time | 0% | 35% |
| distance | 4.7 m | 9.0 m |
| his P1 (touch-driven) | 0 | 660 |

the corrected brain walks (the old one, at 0.275 with the fixed rule, barely moved in this
seed: standing 398 vs walking 492 per chunk is a small drive), runs at 40% of the old leg-MN
output, and spends a third of the minute on walls at a pace that varies instead of sitting
at a bound. this is the new baseline; three seeds x 2 min male-only next, then her.

**male-only baseline, 0.185 mV, running steering and pace, 150 Hz bristle hold (09:12 PDT;
seeds 10-12, 120 s):**

| seed | pace (sd) | leg MN / chunk | DNa02 L / R | wall time | longest pinned | wall visits | touch frames | distance | his P1 |
|---|---|---|---|---|---|---|---|---|---|
| 10 | 0.20 (0.13) | 324 | 1.78 / 1.01 | 45% | 21.8 s | 6 | 3,567 | 14.7 m | 2,640 |
| 11 | 0.19 (0.13) | 113 | 1.54 / 1.30 | 15% | 6.8 s | 8 | 1,031 | 20.0 m | 1,450 |
| 12 | 0.19 (0.14) | 224 | 1.76 / 1.02 | 44% | 11.4 s | 7 | 2,441 | 16.4 m | 1,870 |

the corrected brain walks 15-20 m in two minutes at a pace that varies; wall time is high
(15-45%) with long pinned stretches (7-22 s): with the running pace he arrives at walls
faster and the touch reflex, calibrated at the 150 Hz hold, is what it is. this is the
baseline the bristle kernel is scored against: same seeds, same everything, `--bristle
adapting`.

## the bristle kernel (09:14 PDT, `Adapting`, `pair.py --bristle adapting`)

the mechanosensation brief: bristle afferents are slowly adapting (Corfas & Dudai 1990):
~200 Hz at onset, tau ~30 ms, 10-25 Hz plateau, and only about half a contact patch fires
(direction gating). `Adapting(onset 200, tau 30 ms, plateau 20, fraction 0.5)` replaces the
150 Hz hold; the reflex gain is calibrated by driving the bristles at the plateau (10 Hz
effective) instead of 150. same seeds, same everything else:

| bristle | seed | pace (sd) | wall time | longest pinned | visits | touch frames | distance | his P1 |
|---|---|---|---|---|---|---|---|---|
| hold 150 Hz | 10 | 0.20 (0.13) | 45% | 21.8 s | 7 | 3,567 | 14.7 m | 2,640 |
| | 11 | 0.19 (0.13) | 15% | 6.8 s | 8 | 1,031 | 20.0 m | 1,450 |
| | 12 | 0.19 (0.14) | 44% | 11.4 s | 8 | 2,441 | 16.4 m | 1,870 |
| adapting | 10 | 0.27 (0.11) | **86%** | **103 s** | 1 | 10,303 | 7.4 m | 2,190 |
| | 11 | 0.27 (0.11) | 86% | 104 s | 1 | 10,365 | 7.9 m | 2,200 |
| | 12 | 0.28 (0.11) | 87% | 105 s | 1 | 10,479 | 7.3 m | 2,100 |

**pinned, all three.** the calibration says why: at the plateau the bristle-evoked leg-MN
asymmetry is -0.058 with left bristles driven and -0.166 with right, no sign change with
side, so the reflex (gain 111) steers on noise and he pushes into the first wall for the
rest of the run. the 150 Hz hold had been carrying a reflex that, in life, is carried by
the onset burst: a fly sliding along a wall does not hold one deflection, every step
re-deflects its bristles (~10 Hz). **next, one change:** the burst re-triggers at the step
rate while in contact, and the reflex is calibrated against the kernel's own time course
rather than a constant. the brief's warning applies in reverse here: a large effect from
one afferent change was a calibration artefact, not biology.

**v2: step-locked re-deflection + kernel calibration (09:23 PDT).** `Adapting(retrigger_hz=10)`:
while contact holds, a new onset burst every 100 ms (each step re-deflects the bristles;
a labelled choice, the step rate from the gait literature); and `reflex_gain(kernel=...)`
drives the bristles with the kernel's own time course during calibration, so the gain is
measured on what the loop delivers.

| bristle | seed | pace (sd) | wall time | longest pinned | visits | touch frames | distance | his P1 |
|---|---|---|---|---|---|---|---|---|
| hold 150 Hz | 10 / 11 / 12 | 0.20 / 0.19 / 0.19 | 45 / 15 / 44% | 22 / 7 / 11 s | 7 / 8 / 8 | 3,567 / 1,031 / 2,441 | 14.7 / 20.0 / 16.4 m | 2,640 / 1,450 / 1,870 |
| adapting, single burst | 10 / 11 / 12 | 0.27 / 0.27 / 0.28 | 86 / 86 / 87% | 103 / 104 / 105 s | 1 / 1 / 1 | ~10,400 | 7.4 / 7.9 / 7.3 m | ~2,150 |
| adapting + step re-deflection | 10 / 11 / 12 | 0.23 / 0.25 / 0.23 | **18 / 49 / 17%** | 5.8 / 38.8 / 7.3 s | 7 / 4 / 5 | 2,159 / 5,733 / 1,659 | **22.8 / 15.3 / 23.5 m** | 2,800 / 7,350 / 2,040 |

mean wall time 28% (hold 35%), distance up in two of three seeds, one seed (11) worse. the
physiological kernel with step-locked bursts does at least what the 150 Hz hold did, without
the hold. **adopted** (`--bristle adapting` is the room's default from here). the caveat,
recorded: the calibration asymmetries are small and do not flip sign with the side driven
(-0.049 left, -0.023 right; gain 462), so the lateralised leg reflex in this LIF is weak at
bristle rates the physiology allows, and part of what frees him is the onset burst kicking
both legs. the bristle-to-leg-MN gain of the corrected brain is a property to measure on
its own (TODO: audits).

## the warm corner (09:49 PDT, `Room.temperature`, `HotCells`, `CoolingCells`, `--thermo`)

the room is 25 C (his preferred temperature, Sayeed & Benzer 1996) with a warm spot at
(+1.5, +1.5): T = 25 + 8 exp(-d^2 / 2 x 0.8^2), so 33 C at the centre and a gradient of the
order life's avoidance assays use (5 C/cm at fly scale = ~5 C per 0.64 m here, Ni 2013).
his arista thermosensors are driven from the temperature at each antenna tip: hot cells
(TRN_VP2, 4 L / 3 R) tonic and exponential, 37 Hz at 25 C with Q10 4.4 (17 / 37 / 74 at
20 / 25 / 30; Budelli 2019); cooling cells (TRN_VP3a/b, 3 L / 4 R) resting at 95 Hz and
firing to -dT/dt with a 0.3 s rise and 2 s adaptation, suppressed by warming. VP1m / VP1l
left out (labels under audit). the control is not "no cells": it is the same cells at their
25 C rates with no field, so the 95 Hz tonic input the posterior antennal lobe had been
missing is present in both arms and the field is the only difference. male-only, 120 s:

| seed | arm | mean T felt | time T > 28 | time T > 30 | closest to the spot | mean distance | wall | walked |
|---|---|---|---|---|---|---|---|---|
| 10 | rest | 25.71 | 9.6% | 4.3% | 0.55 m | 2.56 | 33% | 25.3 m |
| 10 | field | 26.34 | 17.6% | 11.9% | 0.18 m | 2.34 | 18% | 29.7 m |
| 11 | rest | 27.25 | 35.2% | 19.9% | 0.25 m | 1.83 | 17% | 29.7 m |
| 11 | field | 26.45 | 19.0% | 12.9% | 0.01 m | 2.34 | 23% | 28.3 m |
| 12 | rest | 26.50 | 23.5% | 13.2% | 0.24 m | 2.36 | 15% | 30.5 m |
| 12 | field | 26.44 | 19.9% | 12.8% | 0.25 m | 2.40 | 24% | 28.4 m |

**no thermotaxis.** time above 28 C with the field: 17.6 / 19.0 / 19.9% against 9.6 / 35.2 /
23.5% at rest; the field arm is more consistent seed to seed (his own walk is the variance)
and shows no avoidance, one seed walked through the centre. the expected reason, tested
next in open loop: the only steering readout is DNa02, and a thermal asymmetry that lands
in other descending neurons cannot turn him. (the tonic 95 Hz cooling input did not change
his walking: rest-arm numbers are the bristle-v2 baseline's.)

**open loop (09:55 PDT; standing, 0.185 mV, cooling cells at 95 Hz both sides, hot cells at
the rate for each antenna's temperature, 3 s each):**

| antennae | hot drive L / R | DNa02 L / R | DNa L / R | all DN L / R | leg MN L / R |
|---|---|---|---|---|---|
| 25 / 25 (rest) | 37 / 37 Hz | 0 / 0 | 29 / 14 | 704 / 549 | 377 / 341 |
| 33 L / 25 R | 121 / 37 | 0 / 0 | 30 / 15 | 781 / 575 | 392 / 375 |
| 25 L / 33 R | 37 / 121 | 0 / 0 | 32 / 18 | 869 / 856 | 661 / 630 |
| 33 / 33 | 121 / 121 | 0 / 0 | 33 / 18 | 906 / 841 | 621 / 603 |

**DNa02 is silent to temperature**, so the wheel cannot turn him from it; that is the null.
but the descending population responds, lateralised ipsilaterally: warm on the right lifts
right DN output by +307 spikes/s against +165 on the left; warm on the left, +76 L against
+27 R. and warmth on either side raises leg-MN output (341-377 -> 600-660 with the right
antenna warm), so the running pace would carry him faster through warm air, which is
half of thermotaxis with no direction. **next:** a wheel reading all descending neurons
left minus right through the running baseline, checked on the drum first (it must still
follow), then the warm room.

**the DN-population wheel on the drum (10:10 PDT; 0.185 mV, running baseline, 3 seeds):**

| wheel | seed 0: +30 / -30 | seed 1 | seed 2 | follows |
|---|---|---|---|---|
| DNa02 (gain 3) | +9.4 / -23.3 | +6.6 / -22.9 | +8.6 / -20.5 | **3/3** |
| all DN (gain 6) | -27.6 / -1.0 | -8.0 / +3.7 | +2.5 / +7.4 | 0/3 |

the corrected brain follows the drum 3 of 3 on the DNa02 wheel (a first: at 0.275 it was
2-3 of 3). the DN-population wheel does not, and the calibration line says why: under
vision alone at 0.185 the descending population fires 0.1-0.5 spikes per side per chunk,
near silence, where the thermo cells had driven it to ~700/s. so the population carries
warmth and barely carries sight; DNa02 carries sight and not warmth. **the readout that
matches the wiring is two channels summed**, each through its own running baseline:
DNa02 for vision (gain 3), the DN population for warmth (gain to be set by the size of
the thermal asymmetry: ~14 spikes per chunk net for an 8 C difference across the antennae,
so gain 0.5 = 7 deg per chunk). labelled as what it is: a two-channel readout built from
what the population test showed, not a circuit we found. tested on the drum (vision must
still follow) and in the warm room.

**two-channel wheel, drum and warm room (10:11 PDT; DNa02 gain 3 + DN population gain 0.5):**
drum 3 of 3 both ways (vision intact). warm room, male-only, 120 s:

| seed | arm | mean T felt | time T > 28 | time T > 30 | closest | mean distance | walked |
|---|---|---|---|---|---|---|---|
| 10 | rest | 26.22 | 18.8% | 8.5% | 0.00 | 2.53 | 31.1 m |
| 10 | field | **27.39** | **34.1%** | 23.7% | 0.23 | **1.72** | 30.1 m |
| 11 | rest | 26.70 | 26.9% | 10.9% | 0.34 | 2.21 | 31.0 m |
| 11 | field | 26.45 | 18.8% | 13.1% | 0.25 | 2.13 | 30.0 m |
| 12 | rest | 26.89 | 28.4% | 14.9% | 0.26 | 2.13 | 30.7 m |
| 12 | field | 27.10 | 27.1% | 12.4% | 0.11 | 1.66 | 24.0 m |

**no avoidance; if anything, approach** (seed 10 warmer and closer with the field; the
others flat). the sign was never checked: the population's warmth response is ipsilateral
(open loop above), and the wheel reads "right side up = turn right", DNa02's convention
(Rayshubskiy 2020), so a warm right antenna turns him right, toward the heat. that
convention is known for DNa02 and unknown for the population. flipping the thermal gain's
sign would make him avoid heat by construction, so it is not done. **next:** a screen of
descending types for a lateralised thermal response, and whether any of them is a turning
neuron with a known sign; the thermal channel gets built from those or not at all.

**the DN thermal screen (10:20 PDT; standing, 0.185 mV, 33 C on one antenna vs 25, two
seeds, 3 s each; lateralised = the (L-R) change flips sign with the warm side in both
seeds, |change| >= 2 spikes/s):** 10 descending types qualify, **all ipsilateral**: DNp06
(warm-right change -33/s), DNp35 (-19), DNge054, DNg56, DNpe002, DNp31, DNge037, DNge041,
DNbe001, DNge125. none is a neuron with a published turning sign (DNa02 and DNa01 are
absent; DNp09 and MDN are absent). so a thermal steering channel cannot be built from the
literature's signs, and the two-channel wheel's approach-or-nothing was reading ten
unsigned neurons with DNa02's sign. **the model has its own answer to "which way does
this neuron turn him":** the leg-MN asymmetry it evokes through the cord, the signal the
touch reflex already steers by. if the leg-MN asymmetry carries the visual turn on the
drum, it is the effector for everything, and the descending code's sign is decided by the
wiring rather than by me. tested next: `--wheel legMN` on the drum.

**the leg-MN wheel on the drum (10:17 PDT; 0.185 mV, running baseline on leg-MN L/R counts,
3 seeds):**

| gain (sign) | seed 0: +30 / -30 | seed 1 | seed 2 | follows |
|---|---|---|---|---|
| -0.3 (more right-leg spikes = left turn; the touch reflex's convention) | -2.0 / +2.6 | -2.1 / +2.6 | -1.8 / +2.8 | 0/3, anti in all |
| +0.3 (more right-leg spikes = right turn) | +1.8 / -3.4 | +2.2 / -3.0 | +1.9 / -3.4 | **3/3** |

the visual turn is carried by the leg-MN asymmetry, weakly (2-3 deg/s at this gain
against DNa02's 9-23) and with a definite sign: **more right-leg spikes = right turn**,
consistent in six of six phases. that is the opposite of the convention the touch reflex
has used since 09-16 (chosen from the inside-leg / outside-leg intuition, which a spike
count over a mixed flexor-extensor population does not owe anything). so the sign of the
model's leg code is now an empirical fact from one behaviour, and the reflex's success at
freeing him from walls is suspect (the onset burst kicking, as suspected at 09:23). **the
leg wheel is the effector that lets the wiring decide the sign of every input**, at the
price of a weak visual gain; tested next in the warm room at both signs and both arms,
and the touch reflex's sign re-tested on its own.

## thermotaxis (10:45 PDT): the warm corner with the leg-MN wheel

male-only, 120 s, `--wheel legMN`, the sign set by the drum (gain +0.3: more right-leg spikes
= right turn), rest (cells at 25 C rates, no field) vs field, three seeds; and the opposite
sign as the control that the sign matters:

| sign | seed | arm | mean T felt | time T > 28 | time T > 30 | closest | mean distance | wall |
|---|---|---|---|---|---|---|---|---|
| drum's (+0.3) | 10 | rest | 27.25 | 33.8% | 21.0% | 0.00 | 1.83 | 16% |
| | 10 | field | **25.09** | **0.0%** | **0.0%** | **1.76** | **3.04** | 16% |
| | 11 | rest | 26.94 | 30.2% | 18.3% | 0.20 | 1.96 | 19% |
| | 11 | field | **25.78** | **9.7%** | 3.9% | 0.18 | 2.48 | 25% |
| | 12 | rest | 26.48 | 20.4% | 15.1% | 0.08 | 2.32 | 11% |
| | 12 | field | 26.33 | 18.1% | 10.9% | 0.12 | 2.19 | 9% |
| opposite (-0.3) | 10 | rest / field | 27.51 / 26.92 | 38.2 / 26.6% | | | 1.95 / 2.13 | 36 / 55% |
| | 11 | rest / field | 25.89 / **27.29** | 12.3 / **31.3%** | | | 2.99 / 1.95 | 32 / 58% |
| | 12 | rest / field | 27.30 / 26.97 | 34.9 / 27.5% | | | 1.99 / 2.14 | 31 / 42% |

**he avoids the heat: 3 of 3 seeds cooler with the field than without**, one of them (seed
10) never entering the warm zone at all. the opposite sign is mixed (one seed warmer with
the field) and spends half its time on walls. what makes this a result and not a fit: the
sign of the leg wheel was fixed by the drum, a different behaviour, before this test ran;
the thermal cells' rates are Budelli 2019's; the control arm has the same cells firing at
the same rest rates; and no thermal steering channel exists: the same effector that turns
him to a moving drum turns him away from a warm antenna, because the descending code
for both lands on the leg motor neurons with one sign. n = 3, so a pre-registered ten-seed
replication follows in the same chain as the touch reflex's sign test. this is the first
behaviour in the record that arrived from a sense the physiology briefs added.

**the touch reflex's sign (11:48 PDT; leg wheel +0.3, rest arm, 120 s):** with the 09-16
convention (more right-leg spikes = left turn) wall time 15 / 16 / 15%, 10-11 visits, 31 m
walked; with the drum's sign, 91 / 91 / 91%, one visit of 109 s, 6.6 m. **the reflex's
direction is real** (not the burst), and it is the opposite of the visual turn's. so a
right-heavy leg-MN count means "turn toward the right" when vision or warmth caused it and
"turn away from the right" when a bristle caused it: **the scalar leg-MN asymmetry is not
one motor code.** different inputs recruit different motor neurons (withdrawal flexors vs
stance drive, presumably), and counting every leg MN alike, which the vision brief already
flagged (Azevedo 2020: three MN classes, force per spike 0.1 / 1 / 10 uN), hides that. the
MN audit (which types each input drives) is now the priority, not an item.

**the pre-registered replication (11:48 PDT; seeds 20-29, rest vs field, leg wheel +0.3,
reflex sign +1):** time above 28 C, rest 23.4% vs field 16.4%; mean temperature felt 26.56
vs 26.23 C; **7 of 10 seeds cooler with the field; paired one-sided Wilcoxon p = 0.14.**
two seeds went the other way hard (20: the rest run never entered the warm zone, the
field run did; 28: 42% of its time warm with the field). with the pilot, 10 of 13 seeds
cooler. **a trend of about seven percentage points of time in the warm zone, not a
claim of thermotaxis.** the thermal leg asymmetry is small (open loop: 661 L vs 630 R with
the right antenna warm, 5%), and at walls the wheel and the reflex now pull with opposite
conventions, which the MN audit may resolve. the seed-10 avoidance run stands as what it
is: one run.

## the motor neuron audit (12:05 PDT)

open loop, standing, 0.185 mV, 2 s each: every leg-MN type's left-minus-right response to a
bristle on one side (150 Hz), warmth on one side (33 vs 25 C at the antennae, cooling cells
at 95 Hz), and the world turning (the yaw renders through the seam). 142 MN types, 699
cells; totals per side, spikes/s:

| input | leg MN L | leg MN R |
|---|---|---|
| rest | 0 | 0 |
| bristle L | 7,539 | 5,614 |
| bristle R | 4,626 | 5,333 |
| warm L | 396 | 363 |
| warm R | 662 | 610 |
| world turning left | 10 | 28 |
| world turning right | 45 | 27 |

**three inputs, three different motor pictures.** a bristle drives the legs enormously and
in a muscle-specific pattern with names: sternotrochanter MN (R-L change -579 with the
left bristle, +208 with the right), trochanter flexor (+341 / -209), sternal posterior
rotator (+324 / -318), tibia extensor (-251 / +159), sternal anterior rotator, pleural
remotor/abductor, tibia flexor: each muscle with its own left-right sign. that is a
withdrawal program, and it is why the touch reflex's direction is real and why a count over
all MNs had a sign that only worked for touch. the world turning reaches the legs as a
whisper, 20-45 spikes/s in total and no type above 3/s: the leg wheel's drum following rode
that. **warmth raises leg output on both sides alike** (per type, the warm-left and
warm-right changes are equal), no lateralisation at all. **so the thermal avoidance had no
lateralised motor substrate: at most it is thermokinesis** (he walks faster when warm, the
running pace carries him out of warm air sooner) plus noise, which is what 7 of 10 and
p = 0.14 look like. the morning's "he avoids the heat" is downgraded to that, in place.

what the audit gives instead: a turning readout with a wiring-derived sign. the bristle
program defines an axis in leg-MN space (the left-bristle pattern minus the right-bristle
pattern, per cell); any input's motor pattern projected onto it has a sign the wiring set,
not me. tested next, open loop first: do the thermal and visual patterns project onto the
withdrawal axis at all?

**projection onto the withdrawal axis (12:15 PDT; axis = per-cell leg-MN rates under a left
bristle minus under a right bristle, seed 0; test patterns from seed 1, spikes/s along the
axis, + = the left-bristle direction):** bristle L +717, bristle R -161 (the axis works for
what built it, with a left-heavy magnitude); bristles at 30 Hz +65 / +3; **warm L +9.8, warm
R +24.3** (both positive: warmth projects on the same side whichever antenna is warm; with
the bilateral part removed, +6.2 / +18.8, still no sign flip); **world turning left 0.0,
right -0.2**; rest 0.0. so the legs carry a directional program for touch only. the visual
turn lives in DNa02 and does not appear in the leg code at these constants (the cord does
not translate a DNa02 asymmetry into a leg asymmetry here, which is its own finding), and
warmth has no directional motor expression at all. **the leg wheel is dropped as a
steering readout;** DNa02 for vision and the touch reflex stand. thermotaxis needs the
thermal descending types (the screen's ten) to produce a lateralised leg pattern when
driven; tested next, directly.

**the thermal descending types, driven directly (12:30 PDT; each type on one side at 100 Hz,
2 s, leg-MN totals per side and the projection on the withdrawal axis):** six of the ten do
nothing at the legs (DNge054, DNg56, DNpe002, DNge041, DNbe001 ~0; DNp35 bilateral 280 /
280). **DNge125 is a clean contralateral driver:** left cell -> right legs 278/s, left legs
0; right cell -> left legs 288/s, right legs 0. DNge037 the same, weakly (24 / 17). DNp06
drives the left legs from either side. all ten together: side L -> R-L +262, side R -> -478,
contralateral. and **DNa02 at 100 Hz moves the legs by 8-12 spikes/s**: the visual turn
command does not reach the cord in this model at these constants, which is the finding
behind the leg wheel's whisper.

so a warm antenna recruits a contralateral leg drive through DNge125. by the one turning
sign the wiring has provided (the withdrawal program: louder legs on a side = turn away
from that side), contralateral drive from the warm side is a turn *toward* the warmth. but
DNge125's pattern projects at 0.0 on the withdrawal axis: it is a different motor chord,
and no behaviour in the record says which way that chord turns him. **thermotaxis is
under-determined in this model**, and the reason is precise: the turning sign of an
arbitrary leg-MN pattern needs a leg with muscles (which muscle, which joint, stance or
swing), not a spike count. nate's question of 09-16 ("does this need physics-accurate
legs?") now has its answer: for the sign of a motor pattern, yes. the warm corner stays in
the world with its cells firing; the readout waits for legs.

## the leg motor brief (~12:28 PDT, `docs/physiology/leg_motor.md`; the clock was not read for this header or the two below, times corrected at 12:37)

an opus agent, briefed on the audit. what it changes:

- **the leg-MN set was contaminated.** MANC names motor neurons `MN` + a two-letter muscle
  code (Marin 2024, eLife): fl / ml / hl = front / middle / hind leg, **ad = abdominal**,
  wm / hm / nm = wing / haltere / neck. of the 699 `vnc_motor` cells, the annotation
  `subclass` says: fl 133, ml 116, hl 124 (**373 leg MNs**), ad 214, wm 66, nm 24, hm 16,
  xm 6. the `tpn`, `ps1`, `b1/b2/i1/i2/iii1`, `hi2` names are wing or haltere MNs and
  `TTMn/STTMm` the escape-jump pair. every leg-count readout in this record (pace, the touch
  reflex asymmetry, the leg wheel, the 12:05 audit) summed abdominal, wing and haltere motor
  neurons with the legs. `world/legmn.npz` is the leg set by segment and side; `pair.py`
  and the drum read it (`--legmn leg`, default; the oracle pins `all`).
- **the turning rule, measured:** the fly turns toward the side with *less* stance
  excursion (Yang 2024, Cell): DNa02 shortens ipsilateral strides, ipsiversive; DNg13
  crosses the midline, lengthens contralateral strides, also ipsiversive. so a crossed DN
  exciting contralateral power-stroke MNs turns the fly toward its own side, away from the
  legs it drives. DNg13 is the template for DNge125 (nothing is published on DNge125 itself).
- **front legs brake, middle and hind propel** (Full 1991; Dallmann 2016; Isakov 2016: a
  fly turns *away* from an amputated foreleg), so the segments need different signs
  (recommended mu_T1 -0.5, mu_T2 = mu_T3 +1.0); never measured in the fly directly.
- the model (brief s.6): filter to leg MNs, baseline-subtract, per-MN force from size
  (Lesser 2024, 0.45 synapses per um^2, r 0.94) calibrated to Azevedo 2020's 10 / 1 / 0.1
  uN fast / intermediate / slow, a saturating transfer, signed muscle weights (remotor,
  sternotrochanter, trochanter extensor positive; promotor, trochanter flexor negative),
  segment-weighted P_R - P_L. under it the bristle pattern (levator/flexor-dominated,
  ipsilateral withdrawal; Medeiros 2024) and the DNge125 pattern (remotor/extensor-
  dominated, contralateral) predict opposite turn signs, which is exactly why the unsigned
  count flipped. the sign-fixing experiment in life is unilateral MN-pool optogenetics on a
  ball with leg tracking; nothing else measures the weights directly.

**withdrawn (~12:33 PDT): "DNge125 is a clean contralateral leg driver."** re-run with the
motor neurons split by subclass (each thermal DN type driven on one side at 100 Hz, 2 s):

| driven | abdominal L / R | front leg L / R | middle L / R | hind L / R | wing L / R |
|---|---|---|---|---|---|
| DNge125 L, R | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| DNge037 L | 0 / 0 | 0 / 14 | 0 / 9 | 0 / 0 | 0 / 0 |
| DNge037 R | 0 / 0 | 7 / 0 | 2 / 0 | 6 / 0 | 0 / 0 |
| DNp06 L, R | 5-8 / 0 | 0 | 0 | 2 / 0 | 56-80 / 32-34 |
| DNp35 L, R | 55-60 / 48-54 | 0 | 0 | 0 | 220 / 219 |

DNge125 moves nothing (the 12:30 numbers were the contaminated set, and are withdrawn);
DNge037 is a weak contralateral leg driver (7-14 spikes/s), the only one among the thermal
types; **DNp35 and DNp06 drive wing motor neurons**, bilaterally, and abdominal ones. so the
thermal descending signal in this model reaches the wings before the legs. thermotaxis by
walking has, at these constants, almost no motor substrate; what a warm antenna recruits
looks more like a take-off than a turn. recorded; the leg model is tested on what does
reach the legs.

## the leg model (~12:36 PDT, `src/fly_afterlife/legs.py`)

the brief's model, as an effector: leg MNs only (373), a running per-cell baseline, force
per spike from input-synapse count as the size proxy ((S / median)^2.5, the ratio clipped
to 0.2-5 because the raw counts span 0-19,000, a tracing confound), a saturating transfer
(k = 5 spikes per bin), signed muscle weights by type name (remotor and posterior rotator
+1.0, sternotrochanter and trochanter extensor +0.8, tibia flexors +0.5, grip +0.4, tibia
extensor +0.2, anterior rotator / promotor and trochanter flexors -0.6), segment weights
(front 0.3, middle and hind 1.0) and segment yaw signs (front -0.5: braking), and the
measured rule: turn toward the side with less stance drive. 290 of the 373 leg MNs have a
named muscle. **open loop, two seeds, yaw_left (+ = left turn), c_y = 1:**

| pattern | seed 1 | seed 3 | reading |
|---|---|---|---|
| DNa02 L / R at 100 Hz | +7.5 / -10.2 | +13.3 / -16.5 | **ipsiversive: Rayshubskiy 2020's sign, reproduced** |
| DNge037 L / R at 100 Hz | +5.4 / -8.0 | +8.9 / -12.0 | crossed DN, contralateral legs, turns toward its own side (the DNg13 template) |
| bristle L / R at 150 Hz | +43 / -26 | +51 / -21 | toward the touched leg (the brief's prediction: withdrawal = levation = less stance drive) |
| bristle L / R at 30 Hz | +71 / -101 | +86 / -110 | toward the touched leg |
| warm L / R | +8.6 / +10.4 | +8.7 / +9.1 | same sign both sides: no turn |

the model is validated on the one published sign we have (DNa02), consistent with the
brief on DNge037, and says touch turns him toward the touched leg in walking terms, which
is the withdrawal reflex's opposite: the reflex (which does free him from walls, 15% vs
91%) stays a separate labelled reflex, as the brief argues (withdrawal is not walking;
Medeiros 2024). warmth has no lateral component in the legs, so thermotaxis by walking is
not in this model at these constants, full stop. **adopted as the effector** (`--effector
legs`: DNa02 wheel + the leg model's yaw, the touch reflex overriding on contact), to be
scored in the room against the leg-set baseline.

**the room on the true leg set (12:40 PDT; male-only, 120 s, seeds 10-12, DNa02 wheel, running
pace read from the 373 leg MNs):**

| MN set | seed | pace (sd) | leg MN / chunk | wall | longest | visits | touch frames | walked | P1 |
|---|---|---|---|---|---|---|---|---|---|
| all 699 | 10 / 11 / 12 | 0.23 / 0.25 / 0.23 | 61 / 151 / 50 | 18 / 49 / 17% | 6 / 39 / 7 s | 7 / 4 / 5 | 2,159 / 5,733 / 1,659 | 22.8 / 15.3 / 23.5 m | 2,800 / 7,350 / 2,040 |
| leg 373 | 10 / 11 / 12 | **0.10 / 0.09 / 0.08** | **14 / 10 / 6** | 18 / 12 / 7% | 20 / 14 / 9 s | 2 / 1 / 1 | 2,043 / 1,481 / 931 | **6.5 / 6.8 / 7.3 m** | 2,540 / 1,890 / 1,090 |

**his brain does not drive his legs from sight.** under visual drive at 0.185 mV the 373 leg
motor neurons fire 6-14 spikes per 100 ms in total, a quarter of a hertz per cell; the
walking the record has been reading since 09-16 came mostly from abdominal, wing and
haltere motor neurons standing in for legs. what does drive the legs: touch (7,500/s),
warmth (400-660/s, both sides), and the proprioceptive gait when we drive it ourselves,
which is a loop. **there has never been a walking command in the room.** in life walking
is commanded (DNp09 and its relatives, Bidaye 2020; the "walk" and "brake" DNs of Sapkal
2024); the fly's spontaneous locomotion is a state we have not given him. tested next, open
loop: DNp09 driven tonically, what the legs do; and whether DNa02 steers once the cord is
walking (its own effect on the legs was 8-12 spikes/s in a standing cord).

**walking-command descending neurons, driven (12:43 PDT; both sides tonic, 2 s, leg MN per
chunk on the true set, and the leg model's forward / yaw_left at c = 1):**

| DN (pair) | 30 Hz: leg L / R, forward, yaw_left | 100 Hz: leg L / R, forward, yaw_left | hind-leg drive L / R at 100 |
|---|---|---|---|
| DNp09 | 0.1 / 0.6, +5, +5 | **19 / 34, +143, +120** | +10 / **+130** |
| DNa03 | 0.2 / 1.7, +15, +15 | 3 / 15, +106, +97 | +5 / +85 |
| MDN | 0.8 / 0, +5, -5 | 22 / 9, +164, -27 | +73 / +53 |
| DNp42 | 0 | 6 / 2, +15, +4 | |
| DNg13 | 0.6 / 0 | 9 / 1, -20, +9 | (front legs, negative: swing) |
| DNa02, DNa01, DNb01, DNb02 | 0 | 0-2 | nothing |
| DNp09 100 + DNa02 L 100 / R 100 | | yaw_left +135 / +112 | DNa02 nudges ipsiversively, ~20 units |
| DNp09 100 + DNa02 L 30 / R 30 | | +122 / +129 | nothing at 30 Hz |

**there is a walking command:** DNp09 at ~100 Hz makes the cord produce five times the leg
output of the visual baseline (the threshold lies between 30 and 100). in this male it is
lopsided: the right hind legs get 130 units and the left 10, DNa03 the same way, the
rightward tracing bias the record has met at every readout (the female's descending
output is symmetric). DNa02 on a walking cord adds a ~20-unit ipsiversive nudge at 100 Hz
and nothing at 30, so the visual turn is still essentially brain-side. MDN (backward
walking in life) drives the legs bilaterally and the model, which has no direction of
travel, reads it as forward; a stance/swing phase model is what would tell them apart.
**next:** the room with the command on (`--walk 100`, DNp09 both sides tonic, labelled: in
life the command is state-dependent), the leg model as effector with its running baseline
absorbing the constant asymmetry, sight and touch on top.

**the leg model as effector, no walking command (12:50 PDT; male-only, 120 s, seeds 10-12):**
pace 0.09 / 0.07 / 0.06, leg MN 8 / 4 / 1 per chunk, 7.4 / 6.7 / 7.0 m, wall 15 / 9 / 2%:
indistinguishable from the wheel on the same set (0.10 / 0.09 / 0.08; 6.5-7.3 m). expected:
a readout cannot matter until the cord produces something to read. the walking command
runs next.

## he walks (12:56 PDT): the walking command in the room

**[09:14 PDT, 09-18: silent-brain result: with the tonic floor on (18:18) the command adds nothing to the cord (09-18 motor review, confirmed by probe below).]**

`--walk 100` (DNp09, both sides, tonic) with the leg model as effector, the true leg set, running
steering and pace, adapting bristles; male-only, 120 s, seeds 10-12:

| config | seed | pace (sd) | leg MN / chunk | wall | longest | visits | touch frames | walked | mean yaw |
|---|---|---|---|---|---|---|---|---|---|
| no command, wheel | 10 / 11 / 12 | 0.10 / 0.09 / 0.08 | 14 / 10 / 6 | 18 / 12 / 7% | 20 / 14 / 9 s | 2 / 1 / 1 | 2,043 / 1,481 / 931 | 6.5 / 6.8 / 7.3 m | -0.1 |
| no command, legs | 10 / 11 / 12 | 0.09 / 0.07 / 0.06 | 8 / 4 / 1 | 15 / 9 / 2% | 14 / 10 / 3 s | 2 / 2 / 1 | 1,322 / 665 / 221 | 7.4 / 6.7 / 7.0 m | +0.1 |
| **command, legs** | 10 / 11 / 12 | **0.28 / 0.28 / 0.27** | **58 / 56 / 53** | 41 / 41 / 18% | 8 / 8 / 7 s | 17 / 21 / 10 | 2,489 / 2,459 / 1,328 | **30.7 / 31.1 / 31.3 m** | +0.9 / +1.2 / +2.9 |

**the first run in which a descending command walks his legs and a muscle-weighted model
reads them.** five times the leg output, four times the distance, many short wall visits
instead of long pinned ones (the reflex frees a walking cord faster than a standing one),
and a leftward drift of 1-3 deg per chunk: the lopsided right-hind drive of this male's
DNp09 read by the measured rule (more stance on the right, turn toward the left), which
the running baseline damps but does not remove. labelled: the command is a constant here
where in life it is a state. what it unlocks, run next: the drum on a walking cord (does
DNa02's nudge now show in the legs?), the warm corner on a walking cord, and the room with
her.

**on a walking cord (13:28 PDT):**

*drum, 3 seeds, `--walk 100`:* DNa02 wheel +3.1 / -18.6, +15.7 / -10.0, +1.0 / -19.4: **3 of 3**
(the command does not break vision). leg model as steering: +59.5 / +52.8, +32.8 / +59.6,
+22.5 / +40.7: **0 of 3**, a leftward 20-60 deg/s whatever the drum does. the lopsided DNp09
drive dominates, and the model's per-cell baseline rectifies fluctuations (delta = max(c -
base, 0)), so the stronger side always wins. as a wheel the leg model fails on this cord; as
the source of his pace it is what walks him. **steering stays DNa02.** one specific fix to
test: a signed delta.

*warm corner, 3 seeds, walking, rest vs field:* time above 28 C 16.7 -> 14.8%, 4.8 -> 27.7%,
5.2 -> 43.5%; mean temperature 26.28 -> 26.19, 25.63 -> 26.91, 25.83 -> 27.82; with the field
he is on walls 40% of the time (rest 0-13%). **no avoidance; two of three warmer.** warmth on
a walking cord drives the legs harder on both sides, and harder is not away.

*the room with her, walking, 5 min, seed 3:* 77.8 m, wall 34%, three encounters, **269
frames of contact with her**, his P1 4,560, hers 0. viewer next in the honest configuration
(command on, DNa02 steering, legs for pace).

**signed baseline for the leg model (13:44 PDT; drum, walking cord, 3 seeds):** +9.3 / +2.0,
+25.3 / +15.5, +26.3 / -1.7: the drift halves and 1 of 3 follows. not a wheel; it stays the
source of his pace and a diagnostic of what the cord is doing. **the configuration from
here:** `--walk 100 --steer running --pace running --bristle adapting` (DNa02 steers, the
true leg set paces, DNp09 walks, adapting bristles feel).

**the room with her in that configuration (13:44 PDT; seed 3, 300 s):** 78.8 m, wall time
8% (was 31-34% with the standing cord and the drifting leg wheel), five encounters, 264
frames of contact with her, mean yaw -0.98 deg per chunk (the DNa02 wheel's known lean),
his P1 2,340, hers 0. the room artifact, v6.

## the brake (13:55 PDT): halting is in the wiring

**[09:14 PDT, 09-18: silent-brain result: with the tonic floor on the brake does not brake (09-18 motor review, confirmed by probe below).]**

Sapkal 2024 (Nature): halting is active, a brain-side inhibition of the walking neurons
(Foxglove, Bluebell) and a cord-side brake (BRK) that co-contracts the legs. the
annotation synonyms find them: **BRK = AN19A018 (12 cells, 6 per side; ascending)**,
**Bluebell = DNg60 (2)**; Foxglove is not annotated. open loop, a walking cord (DNp09 100
Hz), 2 s, leg MN per chunk on the true set:

| drive | leg MN L / R | stance-muscle MN | swing MN | forward | yaw_left |
|---|---|---|---|---|---|
| DNp09 100 | 23.6 / 38.2 | 33.6 | 15.9 | +150 | +105 |
| DNp09 100 + BRK 30 | **0.0 / 0.7** | 0.6 | 0.0 | +6 | +6 |
| DNp09 100 + BRK 100 | 0.0 / 0.0 | 0 | 0 | 0 | 0 |
| DNp09 100 + Bluebell 100 | 0.2 / 1.4 | 1.1 | 0.2 | +12 | +14 |
| DNp09 100 + DNa02 L 100 | 26.6 / 47.8 | 43.7 | 13.9 | +212 | +124 |
| DNp09 100 + DNa02 L 100 + Bluebell 100 | 2.5 / 12.7 | 10.6 | 1.4 | +86 | +86 |

**the brake halts a walking cord completely at 30 Hz.** in the LIF it reads as silence
rather than co-contraction (no stiff-joint activity to see; the model has no joints), which
is what a spike count can show of it. Bluebell nearly halts walking too (the brief has it
inhibiting the turning DNs specifically; here DNp09-driven walking drops 95%). so he has an
on (DNp09) and an off (AN19A018), both from the wiring. **the first use:** a male that stops
when he reaches her (`--stop-at-her`: BRK driven at 50 Hz while in contact with her,
labelled; in life the stop is part of the courtship sequence, not a reflex), scored by
contact time against the 264 frames of v6.

**stop-at-her (13:59 PDT; seed 3, 300 s, brake at 50 Hz while in contact with her):** contact
frames 132 in 3 bouts (longest 0.8 s) against 264 in 3 bouts (1.3 s) without; five
encounters both; 78.7 m both; his P1 3,090 vs 2,340. **nothing.** the reason is mechanical
and instructive: contact lasts a few frames because the bodies are pushed apart on
overlap, the brake is on only while `kind == 2`, so it fires for tens of milliseconds and
he walks on; and she keeps walking at her constant 0.15 m/s regardless. a stop keyed to a
contact frame is not a state. the male that stops at her needs (a) a persistent state
(the vision brief: persistence lives in pCd, minutes long, not in P1) that holds the brake
and (b) something for her to do besides leave: her own stop, or his following. that is the
courtship sequence proper, a build of its own, not an afternoon flag. recorded as the
first thing the brake was tried on.

## the pillars went through the floor (17:15 PDT; nate's report)

nate, from the viewer: the pillars render full height "through / in front of the floor", an
optical illusion from his point of view. a raytracer bug, in both raytracers: pillars were
infinite cylinders and the floor is not a plane but a gradient by ray direction, so a pillar
continued below the floor to infinity and hid the ground under it. fixed: pillars have a
height (1.5 m, standing on z = 0; `Scene(pillar_height=)`, `Room.pillar_height`, the viewer's
own tracer, `pillar_height` saved in the npz). check from his eye at 0.5 m, a pillar 1.25 m
away: it spans -21 to +38 degrees of elevation, floor to top, as geometry says. this changes
what he sees, so the oracle is re-frozen (same frozen script, corrected raytracer); every
run before this section saw the old pillars.

## thermokinesis, the physiology's own answer (17:20 PDT; nate's question)

nate: the apparatus (two aristae half a millimetre apart) can hardly support a spatial
gradient; "move fast, erratically" would be the simplest solution. the physiology agrees:
the cooling cells are differentiators (rate of change, threefold for 0.2 C, adapting), a
temporal sensor for a moving animal, and the algorithm that falls out is a biased random
walk: turn more and go faster when warming, straight when cooling. so the question for the
model is not "does he turn away from the spot" but "does warming change his turning rate
and his pace." from the walking-cord runs of 13:28 (`world/thermo5`, per 100 ms chunk, off
the walls, |dT/dt| > 0.05 C/s):

| arm | seed | n | Spearman dT/dt vs pace | vs turning rate | turning rate warming / cooling | pace warming / cooling |
|---|---|---|---|---|---|---|
| rest (cells at rest, no field) | 10 / 11 / 12 | 672 / 806 / 831 | -0.07 / -0.00 / -0.03 | +0.01 / -0.01 / -0.02 | 8.0 / 8.2, 8.0 / 7.9, 8.3 / 8.1 | 0.27 / 0.28, 0.28 / 0.27, 0.27 / 0.27 |
| field | 10 / 11 / 12 | 603 / 526 / 597 | **-0.19 / -0.24 / -0.20** (p < 0.01) | +0.08 (p 0.06) / -0.01 / **+0.09 (p 0.03)** | **9.4 / 8.6, 9.0 / 8.8, 8.5 / 7.7** | 0.26 / 0.27, 0.25 / 0.28, 0.25 / 0.27 |

**when he is warming he turns more, in all three seeds** (two significant), and the rest
arm shows nothing: the turning half of the klinokinesis is in the wiring. the speed half
has the wrong sign: he slows when warming, in all three, where the algorithm and the
open-loop leg output (warmth raises it) both say faster. that is a readout question: the
running pace normalises by his own recent mean, and a warming fly that turns more covers
less ground per chunk; the pace rule and the turning interact. the thermal story, restated
honestly: no taxis, a weak klinokinesis with the turning sign right and the speed sign to
be understood.

**nate's other point, adopted as the next build: the tonic floor.** this brain rests at
0 Hz on nearly every sensory channel and the real one does not (ORNs a few Hz, hot cells 37,
cooling 95, slow leg MNs 30 standing, proprioceptors under load, JO in still air); every
circuit downstream was tuned against that floor, and we have been handing it silence and
calling the result the wiring. the proprioception result and the thermal "rest" arm were
this principle by accident. next: every typed sense at its resting rate from the briefs by
default, the world modulating, as its own step against the current baseline.

## the cold corner and the extremes (18:07 PDT; nate's 10 C)

walking cord, three seeds, 120 s, pillars now on the floor (this section and everything
after it sees the corrected pillars; the "rest" arm is the same room with the cells at
their 25 C rates and no field). `field2` = warm corner 33 C + cold corner 10 C at the
opposite corner; `field2x` = 40 C + 10 C.

| arm | seed | mean T | time > 28 | time < 20 | time < 15 | wall | walked |
|---|---|---|---|---|---|---|---|
| rest | 10 / 11 / 12 | (22.4 / 20.5 / 22.7 if the field were on) | 9 / 0 / 12% | 18 / 25 / 19% | 6 / 15 / 10% | **40 / 49 / 42%** | 20.7 / 19.8 / 21.5 m |
| field2 (33 / 10) | 10 / 11 / 12 | 22.3 / 27.1 / 22.0 | 12 / 36 / 4% | 33 / 0 / 27% | 16 / 0 / 20% | **15 / 14 / 10%** | 29.3 / 31.4 / 31.3 m |
| field2x (40 / 10) | 10 / 11 / 12 | 21.6 / 26.1 / 21.0 | 12 / 31 / 9% | 34 / 13 / 38% | 24 / 9 / 24% | 17 / 13 / 17% | 29.8 / 31.4 / 31.2 m |

**no taxis, warm or cold, at 33 or at 40:** two of three seeds spend *more* time in the cold
corner with the field than without, one seed (11) leaves the cold entirely and sits in the
warm. **the robust effect is the kinesis:** with any field on, wall time drops from 40-49%
to 10-17% and he walks 30 m instead of 20, in every seed, both fields. thermal transients
as he moves (the cooling cells are differentiators) keep his cord active and free him
from walls; the warmth of the world moves him, it does not aim him. nate's prediction
("move fast, erratically") is what the model does with heat and cold alike.

**a confound found on the way, recorded:** the rest arm's wall time here (40-49%) is far
above the walking baseline of 13:28 (0-13%, `world/thermo5`, same configuration). the
difference between the runs is the pillar fix: the infinite pillars filled his lower
visual field with vertical contrast everywhere, the standing pillars do not, and the
DNa02 wheel gets less to steer by near walls. the render bug had been part of his
behaviour. tested directly next: pillars at 1.5 m vs infinite, same seeds, rest arm.

**the control (18:15 PDT): the pillars were not it.** same seeds, rest arm, walking cord:
infinite pillars wall 40 / 38 / 40%, 23.6 / 24.0 / 22.4 m; pillars at 1.5 m wall 40 / 49 / 42%,
20.7 / 19.8 / 21.5 m. the same. **the confound sentence above is withdrawn:** the render fix did
not change his wall time. what differs between the 13:28 runs (0-13%) and these is the
*effector*: those used the leg model as steering, whose constant leftward drift (20-60 deg/s)
keeps a walking fly circling off the walls; these use the DNa02 wheel, which barely drifts,
so he walks straight into walls and the reflex has to free him each time (9-13 visits).
and the wheel's input on a walking cord is one-sided: DNa02 L 2.5-2.7 spikes per chunk,
**DNa02 R 0.01-0.03**, where a standing cord gave 1.6 / 1.4. the walking command (DNp09,
lopsided right) silences the right DNa02 through the brain, and the running baseline can
only read fluctuations of one side. that is the kind of interaction nate warned about at
17:20: a command we added changed a readout we trusted. on the list.

**traced (18:17 PDT):** DNa02's strongest input on each side is an *ascending* neuron from
the cord (AN03A008, 741 synapses on the left cell, 654 on the right), so the wheel reads
the cord as much as the brain. driving DNp09 alone, no vision: left DNp09 at 100 Hz gives
DNa02 L 12.7/s and R 0; right DNp09 gives R 2.7 and L 0; both give 14.0 / 0.7. **the walking
command excites its own side's DNa02 through the cord's feedback, and this male's right
loop is five times weaker than his left.** so on a walking cord the DNa02 wheel is mostly
the command's asymmetric echo, with vision riding on the left side; it followed the drum
3 of 3 through that. the running baseline removes the constant part; the one-sidedness
stays. the wheel on a walking cord needs re-thinking (a per-side normalisation, or a
readout that is not DNa02), and the asymmetry itself joins the list of things the female
does not have.

## the tonic floor (18:18 PDT; nate's point of 17:20, built)

`receptors.FLOOR`: twelve rows, applied before every other row so the world overrides them
on the cells it drives. every typed sense at its physiological resting rate from the
briefs, estimates marked: olfactory receptor neurons 8 Hz (2,635 cells; Or67d 0.12, Or47b
and Or88a 3, Or65a 0.5), gustatory 2 Hz (1,416), hot cells 37, cooling cells 95, VP1m 10
(label under audit), hygrosensory 20 (66), Johnston's organ 5 Hz in still air (672, E),
the 580 leg-nerve proprioceptors 15 Hz under standing load (E). bristles stay silent
until touched; his own photoreceptors stay silent (flyvis sees for him). `pair.py --floor`.

**the standing operating point (no vision, 3 s):**

| | whole brain | central (non-KC) | KC | KC active | DN L / R per s | leg MN per s | cells > 10 Hz |
|---|---|---|---|---|---|---|---|
| floor off (the record) | 0.002 Hz | 0.013 Hz | 0 | 0% | 0 / 4 | 0 | 2 |
| **floor on** | **0.387 Hz** | **0.533 Hz** | 0.013 Hz | 0.2% | **1,061 / 1,002** | **593** | 1,415 |

**his central brain now rests at 0.53 Hz, inside the 0.5-5 Hz band the vision brief gives
for a living fly brain** (Turner 2008: PNs 4.6 Hz, KCs 0.1); it was two orders of magnitude
below it, on silence. his descending output is a thousand spikes a second per side and
symmetric, where the record's asymmetries were measured on a near-silent population; his
legs carry a standing tonus (1.6 Hz per leg MN; the physiology's slow-MN 30 Hz is still
above that). and the odour code is untouched: odour A wakes 7.8% of Kenyon cells without
the floor, 8.0% with it, MBONs 12.6 / 12.5 Hz. the floor woke the brain without blurring
what it hears. every result in this record before this section was measured on the silent
brain; the room is being re-run on the woken one.

**the walking room on the woken brain (18:27 PDT; male-only, 120 s, seeds 10-12, same
configuration as the 18:07 rest arm, `--floor` the only change):**

| | seed | pace | leg MN / chunk | DNa02 L / R | wall | longest pinned | visits | touch frames | walked | his P1 |
|---|---|---|---|---|---|---|---|---|---|---|
| no floor | 10 / 11 / 12 | 0.28 | 54 / 55 / 53 | 2.7 / 0.02 | 40 / 49 / 42% | 31 / 50 / 27 s | 4 / 9 / 13 | 5,193 / 5,514 / 4,691 | 20.7 / 19.8 / 21.5 m | 7,230 / 8,050 / 6,340 |
| **floor** | 10 / 11 / 12 | 0.28 | 56 / 56 / 57 | 2.5 / 0.01 | **26 / 22 / 47%** | **10 / 8 / 23 s** | 14 / 11 / 10 | 2,559 / 2,016 / 4,932 | **28.4 / 30.6 / 22.7 m** | 2,420 / 1,550 / 5,190 |

the woken brain pins less (two seeds clearly, one marginal), walks further, and touches
walls half as much; his pace and leg output are unchanged (the walking command sets
those); the walking-cord wheel is still one-sided (DNa02 R 0.01), which the floor was
never going to fix. modest, in the direction every added sense has pushed: a brain with
its floor is calmer at walls than a brain on silence. **the floor is the configuration of
record from here** (`--floor` on by default, `--no-floor` for the record before it; the
oracle pins `--no-floor`).

## the left-right question, re-measured on the woken brain (22:14 PDT; nate: "still a fly with a brain lesion?")

synapse counts by side, from the build (input synapses summed over cells):

| population | cells L / R | input synapses L / R | R / L |
|---|---|---|---|
| every neuron | 80,171 / 81,558 | 40.96 M / 40.99 M | **1.00** |
| descending neurons | 653 / 647 | 1.87 M / 1.74 M | 0.93 |
| leg motor neurons (373) | 189 / 184 | 518 k / 444 k | 0.86 |
| DNp09 (the walking command) | 1 / 1 | 7,123 / 5,258 | 0.74 |
| DNa02 (the wheel) | 1 / 1 | 22,601 / 20,781 | 0.92 |
| AN03A008 (the cord's feedback onto DNa02) | 1 / 1 | 1,186 / 575 | **0.48** |

**not a lesion.** the brain as a whole is balanced to one percent, and with the corrected
constants and the floor its standing descending output is symmetric (1,061 / 1,002 per s).
what the record has been calling "the male map's asymmetry" is a handful of specific
pathways, 10-50% off in synapse count, which the LIF's threshold turns into 2-5x in spikes:
the walking command's cell has a quarter fewer inputs on the right, its feedback neuron
onto the wheel half as many, and the right leg motor neurons get 14% fewer synapses. so the
DNa02 wheel on a walking cord reads a lopsided loop, and DNp09 drives the right hind legs
harder (the leg model's leftward drift). the running baseline removes the constant part of
these; the one that still matters is the walking-cord echo (DNa02 L 2.6 / R 0.02), which is
one crooked wire, AN03A008, not a hemisphere. the fixed "rightward lean" of 09-16 was
measured on the silent brain at 0.275 mV and is not present on the woken one at rest.
whether these are tracing or the animal, the female cannot say (she has no cord); the
honest label from here is "a few asymmetric connections, named", and the wheel should be
read with a per-side normalisation on a walking cord.

## the garden (22:36 PDT; `src/fly_afterlife/garden.py`, `docs/GARDEN.md`)

built tonight from nate's "a more exciting playground": a 6 x 6 m patch at fly scale with a
real floor plane carrying a two-scale soil-and-litter texture (value noise, ~1.2 cm per
texel; moss patches), thirty grass stalks of 0.5-2 m, three leaves overhead with shade
beneath (darker floor, 3 C cooler), a pale stone, a dark red fruit (a plume downwind with
intermittent whiffs; sugar on its skin, on his 719 leg gustatory neurons at contact), a
puddle (humidity 0.9 above it, cooler), a sunlit patch (+6 C; the sky brightens toward the
sun), and a 0.3 m rim. the world carries RGB; his eye reduces it with a fly weighting (0.2
R, 0.7 G, 0.1 B: green-heavy, red-blind), so the red fruit is dark on the litter to him.
the raytracer grew a floor plane with a texture lookup, horizontal discs and a sun, in the
numpy path and the kernel alike (agree to 1e-8; the room path bit-identical, oracle
re-run). the fruit's plume drives the five fruit-odour receptor types (Or42b, Or92a, Or59b,
Or22a, Or85a; 118 L / 142 R cells) through a Weber-Fechner transducer with a 1 s running
mean; humidity drives the 28 dry and 12 moist cells; temperature the hot and cooling
cells as before. `pair.py --world garden`. `docs/figures/garden_first_look.png` is the
view through his own tracer; `garden_map.png` the world from above.

**his first minute (seed 3, walking command, floor, DNa02 steering):** 16.6 m; rim time
7%, 299 touch frames (grass, the stone); closest approach to the fruit 0.89 m, to the
puddle 1.08 m, to the sun patch 1.26 m; never inside any of them. the path
(`garden_first_walk.png`): out from under the leaf he started under, around it, then the
long way round the patch along the rim, past the fruit without turning. the fruit's
odour neurons ran at 4.5 spikes per chunk mean on a plume he mostly crossed at its
fringe. a rim-walker still, in a bigger loop; the scores that ask whether any sense
steers him here (plume on / off, fruit dark / litter-toned) run next, three seeds each.

**the viewer question (nate):** the browser's raytracer was a second implementation of the
same primitives, checked by eye. from tonight the human view is rendered by his own
kernel: `world/replay.py` serves an episode on localhost and renders each pinhole frame on
demand (0.5 ms, same function as his retina); the JavaScript tracer retires for anything
beyond the plain room.

**the first garden scores (2026-09-18 00:25 PDT; male alone, 120 s, walking, floor, three seeds
per arm; a first attempt crossed the arm and tag lists in the runner's grid and overwrote
its own outputs: discarded, rerun one batch per arm):**

| arm | seed | walked | rim | touch frames | closest to fruit | time < 0.6 m | sugar contacts | closest to puddle | in sun | in shade |
|---|---|---|---|---|---|---|---|---|---|---|
| full garden | 10 / 11 / 12 | 32-33 m | 6-10% | 1,081 / 613 / 561 | **0.38** / 0.59 / 1.17 | 2.4 / 0.6 / 0% | **88** / 0 / 0 | 1.07 / 0.85 / 1.02 | 3.4 / 3.7 / 1.3% | 4 / 9 / 7% |
| fruit without its plume | 10 / 11 / 12 | 32-33 m | 7-12% | 1,165 / 613 / 745 | **0.38** / 0.59 / **0.38** | 2.5 / 0.8 / 3.3% | **89** / 0 / **99** | 0.39 / 0.88 / 1.03 | 0 / 0 / 6.8% | 8 / 6 / 21% |
| fruit toned like the litter (invisible) | 10 / 11 / 12 | 33 m | 7-9% | 587 / 842 / 829 | 0.63 / 1.33 / 1.14 | 0 / 0 / 0% | **0 / 0 / 0** | 0.37 / 0.48 / 1.08 | 3.2 / 0 / 0% | 11 / 10 / 13% |

**the fruit is found by sight, not by smell.** with the fruit dark he reaches it and tastes
it in one seed (full) or two (no plume); with the fruit invisible, never, closest 0.63 m.
and the plume changes nothing: seeds 10 and 11 give the same closest approach with and
without it (0.38, 0.59), because his path was the same, because the fruit's odour
neurons, driven through Weber-Fechner at up to ~200 Hz, do not reach the steering
readout (the record's smell-steering null of 09-16, in the garden). the dark fruit
attracting him is the walk's "approach to dark posts" of 09-16 with a reason to exist.
the puddle, the sun patch and the shade see him 0-7%, 0-7% and 4-21% of the time: passed
through, not sought. so, in the garden as built: **vision steers him, touch turns him,
walking carries him; smell, taste, warmth and humidity are felt and change nothing yet.**
the senses that do not steer are the same three the record already knew could not reach
DNa02; the garden makes the gap visible in one table.

## which sense reaches which readout (00:44 PDT; the woken brain, cord walking)

open loop, floor on, DNp09 at 100 Hz, 0.185 mV, no vision; each sense driven on one side for
2 s; readouts: DNa02 L / R (spikes per chunk), the descending population and the leg MNs
as deltas from baseline, and the leg model's yaw (+ = left; its sign validated on DNa02);
two seeds:

| input | DNa02 L / R | DN L / R (delta) | leg MN L / R (delta) | legs yaw_left (s1, s3) |
|---|---|---|---|---|
| baseline | 0.0 / 0.0 | +110 / +105 | +34 / +19 | 0 |
| fruit odour L / R (150 Hz) | 0 / 0 | -9 / -3, -0 / -12 | -4 / -2, -0 / -2 | -0.2, +1.1 / +6.0, -0.5 |
| fly odour L / R | 0 / 0 | -0 / +1, -12 / -20 | ~0 | +2.2, +0.2 / +4.9, +3.1 |
| sugar on left / right legs (26 Hz) | 0 / 0 | +9 / +4, +9 / +8 | +5 / +1, 0 / 0 | **+8.7, +1.3** / -0.9, +0.2 |
| warm L / R antenna (33 C) | 0 / 0 | +3 / +1, +6 / +19 | +2 / 0, 0 / +1 | **+10.5, +4.2** / +4.9, -3.2 |
| bristles L / R (40 Hz) | 0 / 0 | +58 / +54, +52 / +53 | -2 / -7, -13 / +1 | -3.6, -6.3 / -5.4, -6.9 |
| DNa02 L / R at 100 (control) | 7.5 / 0, 0 / 8.4 | +19 / +1, -0 / +3 | -8 / -1, +1 / -1 | **+9.6, +12.4 / -8.2, -2.1** |

**no sense but vision reaches DNa02** (every row 0.0 but the control). **smell lateralises
nothing**: fruit and fly odour on one antenna move the descending population and the legs
by a handful of spikes with no consistent side, and fly odour suppresses the DN population
a little, bilaterally. **taste and warmth show left-only leg effects**: sugar on the left
legs turns the leg model toward that leg in both seeds, sugar on the right does nothing;
warmth on the left antenna turns him toward it, on the right inconsistently: this male's
left-heavy leg wiring, not a channel. touch drives the DN population bilaterally (+55 each
side) and the leg model reads a rightward bias whichever side is touched.

so closed-loop smell and taste runs would only re-measure this. what the biology does
instead of "turn toward the odour" is turn *upwind when the odour arrives* (odour-gated
anemotaxis: Budick & Dickinson 2006; Alvarez-Salvado 2018), and the wind sense is
Johnston's organ, which we hold at rest. that is the smell experiment worth running:
wind on the ear, odour gating it. built and tested open loop next.

**wind on Johnston's organ (00:46 PDT; open loop, woken walking brain).** his JO is typed in
groups (A 50, B 88, C 68, D 8, E 267, F 78, plus untyped): C and E are the wind and gravity
groups (Yorozu 2009). driven as typed, the left wind cells (203) lift his descending
population fivefold and turn the leg model hard right, the right ones (132) do almost
nothing, and both together look like the left alone: **a typing and tracing asymmetry**
(the left cells carry 99,376 output synapses, median 462 per cell; the right 33,204, median
177). with the populations equalised (132 per side, 20 Hz):

| wind from | DN L / R (delta) | leg MN L / R | legs yaw_left (s1, s3) |
|---|---|---|---|
| left | +17 / +5, +25 / +6 | -2 / 0, -1 / +2 | **+5.0, +5.4** (left: into the wind) |
| right | +12 / +29, +2 / +21 | +3 / +3, +1 / +2 | **-5.5, -3.8** (right: into the wind) |
| left + fruit odour | +14 / -6, +13 / -8 | | +7.0, +0.9 |
| right + fruit odour | +7 / +18, -3 / +9 | | -2.8, -2.5 |
| both sides | +29 / +32, +24 / +25 | | -6.0, -8.5 (the residual asymmetry) |

**an upwind-turning channel exists in the wiring:** wind on one antenna drives that side's
descending population and turns the leg model toward the wind, in both seeds, both
sides, with the sign the DNa02 validation fixed. the two-channel wheel (DNa02 + the DN
population through a running baseline) reads it with the right sign by DNa02's own
convention (left up, turn left), which is the convention that read warmth wrongly
because warmth is bilateral. the odour does not gate the wind response in open loop (in
life the gate is central and state-dependent), so the gate is a labelled stand-in, tested
both ways. sound on one ear (JO-A/B) lateralises nothing.

**hunger (00:54 PDT; nate: "might smell only steer if he's hungry?").** in life, yes, twice:
starvation raises the food-odour receptors' gain (Or42b presynaptic facilitation through
sNPF, Root 2011) and hunger sharpens sugar taste (Inagaki 2012); fed flies do not track
plumes. his connectome carries the machinery by name: 16 insulin-producing cells (satiety;
silent when starved), 2 NPF (hunger), 2 allatostatin-A and 4 DSK (satiety), 12 leucokinin,
4 hugin; sNPF and SIFamide untyped. **at baseline he has no hunger state:** the insulin
cells sit at zero (starved) and the NPF cells at zero (fed); nothing reads either. open
loop, three states x fruit odour on one antenna x the Or42b gain raised 2.5x, two seeds:

| state | odour side | DN L / R (delta) | legs yaw_left |
|---|---|---|---|
| none | L / R | -7 / -1, 0 / -12 | +0.5, +1.1 / +4.4, +0.9 |
| none, Or42b x2.5 | L / R | -5 / -3, +1 / -9 | -0.1, -0.2 / +1.4, -0.5 |
| hungry (NPF 30, LK 30) | L / R | -9 / -5, -1 / -14 | +0.2, -1.0 / -2.3, +0.1 |
| hungry, Or42b x2.5 | L / R | -8 / -6, -5 / -10 | -1.1, +3.5 / -0.6, +6.0 |
| fed (IPC 30, AstA, DSK, hugin 20) | L / R | -9 / -4, -1 / -11 | +1.0, -2.4 / +3.1, -3.5 |

**nothing, under any state.** the lesson is about the engine: neuropeptide neurons act in
life through slow receptors that change other cells' excitability over minutes; this LIF
has fast synapses only, so driving the hunger cells drives a few dozen weakly connected
neurons and changes no gain anywhere. hunger as a state has to be modelled as *what it
does* (a gain on the food receptors, a threshold on the food outputs, a drive on the
walking command) and labelled as such; and even then, the table of 00:44 says there is no
lateralised path downstream of the odour for it to unmask. smell in this brain is state,
not direction; the wind is the direction, and the wind runs are on the cores.

**wind in the garden (01:12 PDT; closed loop, `--wind on`, `--wind-gate none|odour`, `--dn-gain 0.5`,
three seeds, 120 s, male alone, the config of record).** the wind on JO-C/E (equalised 132 per side,
up to 20 Hz on the windward side) read by the two-channel wheel. scored on where he heads relative to
upwind, the fruit (dark, with its plume), and, reconstructed from his path, how much of the run he
spent inside the plume envelope (C > 0.02, whiffs ignored):

| arm | upwind cos | rim | in plume | d fruit min | visits < 0.6 m | sugar frames |
|---|---|---|---|---|---|---|
| off (control) | -0.11, +0.06, -0.08 | 0.06, 0.12, 0.06 | 2%, 2%, 31% | 0.38 x3 | 1, 1, 1 | 78, 46, 119 |
| wind, ungated | +0.14, +0.12, -0.02 | 0.28, 0.20, 0.13 | 0%, 0%, 2% | 1.77, 1.11, 0.38 | 0, 0, 1 | 0, 0, 113 |
| wind, odour-gated | -0.01, -0.04, -0.06 | 0.08, 0.05, 0.02 | 4%, 26%, 43% | 0.38 x3 | 1, 3, 5 | 59, 278, 411 |

**the design has a flaw, stated first:** he starts at (-0.5, -0.5), upwind of the fruit, with no
odour on him. so the ungated wind measures pure anemotaxis, and pure anemotaxis walks him to the
upwind rim (rim time doubled or tripled, two seeds never in the plume, the fruit lost in both);
the heading tilt is small (+0.12 to +0.14 mean cos in those two seeds against about zero) because
the rim reflex dominates once he is there. **the gated wind is the mechanism working in two seeds
of three:** the gate only opens inside the plume, which is downwind of the fruit, and there the wind
turns him upwind, which is toward the fruit; seeds 11 and 12 spend 26% and 43% of the run inside
the plume and return to the fruit three and five times (every control visits once and leaves), with
three to five times the sugar contact. seed 10 is indistinguishable from its control. the control
with 31% plume time (seed 12) visited once: being in the plume without the gate did not bring him
back. not yet a claim: the effect is "he stays and returns", in 2/3, from a start that makes the
plume hard to reach. the proper test, pre-registered and on the cores: `--start 2.26,-0.94,90`, one
metre downwind of the fruit inside its plume, facing crosswind; all three arms; prediction: gated
and ungated both turn him upwind onto the fruit within the first seconds and the control does not.

**the downwind start (09:15 PDT; `--start 2.26,-0.94,90`: one metre downwind of the fruit inside its
plume, facing crosswind; the laptop slept through the gated arm, hence the morning stamp).** the
prediction was that gated and ungated wind both turn him upwind onto the fruit within seconds and
the control does not. **it failed, and the way it failed is the finding:**

| arm | first 10 s: upwind cos | d fruit at 10 s | in plume, whole run | d fruit min | sugar frames | rim |
|---|---|---|---|---|---|---|
| off (control) | +0.18, +0.07, -0.19 | 1.32, 1.29, 1.70 | 40%, 24%, 32% | 0.38, 0.63, 0.38 | 135, 0, 72 | 0.04, 0.05, 0.01 |
| wind, ungated | **+0.42, +0.50, +0.19** | 2.48, 2.06, 2.05 | 8%, 4%, 5% | 0.90 x3 (= the start) | 0, 0, 0 | 0.18, 0.11, 0.23 |
| wind, gated | +0.59, -0.01, -0.05 | 1.17, 1.92, 1.33 | 11%, 6%, 23% | 0.38, 0.40, 0.52 | 44, 0, 0 | 0.05, 0.08, 0.02 |

**the wind turns him upwind, replicated:** ungated, three of three seeds swing toward the wind in
the first ten seconds, well above the control, and the whole-run tilt (+0.10 to +0.16) matches
the upwind-start runs (+0.12, +0.14), five of six ungated seeds positive against a control
scattered around zero. **and it never brings him to the fruit:** at a pace pinned at 0.275 m/s
(motor review, below) the turn is an arc, not a saccade; by ten seconds the arc has carried him
two metres north and out of the plume, the heading only two-thirds of the way round, and he
rim-walks the east edge. the control, drifting, spends more of the run in the plume than he does.
the gate turns him once (seed 10, +0.59, one visit) and does nothing in the other two. so the
upwind-start result ("he stays and returns", 2/3) is **not confirmed** from the start that was
meant to confirm it; what survives is the heading channel: right sign, modest size, in six
seeds. anemotaxis in this fly waits on the one thing the review says he cannot do: slow down
while he turns. the two results are the same finding.

**the motor review (09:14 PDT; `docs/MOTOR_REVIEW.md`, an opus agent that read the code first, at nate's
three questions: steering, speed, walking vs wings).** its central finding, which i then reproduced
with my own probe (open loop, no vision, 4 s after a 1.5 s settle, the 373 leg MNs, seeds 1 / 3):

| floor | DNp09 0 | 100 | 200 | 100 + brake 30 | other VNC motor (wing, neck, abdominal, haltere) at DNp09 100 |
|---|---|---|---|---|---|
| on | 559 / 586 | 526 / 551 | 504 / 516 | 543 / 553 | 1,131 / 1,160 |
| off | 0 / 0 | 388 / 404 | 618 / 655 | 1 / 8 | 618 / 978 |

**the walking command and the brake are silent-brain results.** on the silent brain DNp09 at
100 Hz is everything (0 to 388) and AN19A018 at 30 Hz halts the cord (388 to 1), which is what
12:56 and 13:55 say. with the tonic floor on, the cord fires 560-590 leg-MN spikes a second of
its own, the command adds nothing (slightly negative at 200 Hz), and the brake does nothing.
the floor's tonus is not one row: the review ablated them and found the fourteen thermal cells
alone carry half of it (526 to 288 without them), JO a fifth, the leg proprioceptors a tenth.
and the motor neurons we do not read, the 326 other VNC motor cells, fire at twice the legs'
rate, led by the flight power muscles (DVMn, DLMn at 25-53 Hz per cell), driven mostly by the
ORN resting rate (the review: 867 to 195 spikes/s without the five ORN rows).

**what this does to the record since 18:27.** `--walk 100` in the config of record has been
inert; "he walks" has been `RunningPace`'s fixed point (the running mean makes v = 0.275 the
attractor: median 0.277-0.279 in every garden run, 0 of 12,000 frames at the floor speed).
the distance walked, the rim time, the fruit visits and the wind result all stand as measured,
but their pace was the estimator's, not the cord's. the wheel, too, is one cell: DNa02 R sits at
0.02-0.07 spikes per chunk in every garden run, so the difference reduces to the left cell
against its own mean; the review also notes AN03A008 fires 0.0 on the woken brain, so my 18:17
explanation for the pinned right cell belongs to the silent brain as well. **and the three
calibrations run on the silent brain:** `dna02_rest_offset`, `standing_baselines` and
`reflex_gain` drive vision and the bristles only; the floor rows are applied in the episode loop
alone (`episode.py`), so the rest offset (+0.00), the standing baselines (0) and the touch-reflex
gain were measured in a regime the loop never visits. that one is a bug of mine and is fixed
next, one change, with the oracle (which pins `--no-floor`) unaffected.

the review's other findings, untested by me yet and queued: DNa01 (2 cells, the published
partner of DNa02, read by nothing), DNg13, DNb06 (alive and lateralised), PFL3 (24, the compass's
output onto DNa02); the seven types the old wheel screen picked are mostly neck neurons (gaze,
on a body with no head); the `--dn-gain` channel is eight tonic types, one of them our own DNp09,
and it steers *toward* warmth while DNa02 steers away; DNg100 (BDN2) with 1,870 direct leg
synapses against DNp09's 10 as the other walking command. the closed-loop dose-response
(`--walk 0 | 100` under the floor, and `--no-floor --walk 100`, three seeds) is on the cores
behind the downwind batch.

**the dose-response in the loop (09:44 PDT; garden, config of record, three seeds, 120 s):**

| arm | walked | leg MN per chunk | DNp09 per chunk | rim | sugar frames |
|---|---|---|---|---|---|
| floor, `--walk 0` | 32.4, 32.7, 32.6 m | 55, 66, 58 | 0.0 | 0.06, 0.06, 0.11 | 0, 0, 150 |
| floor, `--walk 100` | 32.7, 32.5, 32.6 m | 57, 60, 60 | 15.3 | 0.07, 0.10, 0.05 | 0, 0, 131 |
| no floor, `--walk 100` | 32.0, 32.4, 32.1 m | 44, 46, 45 | 15.4 | 0.07, 0.06, 0.08 | 0, 0, 81 |

thirty-two metres in every arm. the leg-MN rate moves (44 to 66 per chunk across the arms) and
the distance does not, because `RunningPace` divides the rate by its own running mean and lands
at v = 0.275 whatever the cord does. so the walking command is inert in the loop under the
floor, as in the open loop, and the distance walked has been the estimator's since the readout
was adopted (08:58 yesterday): the 20 to 30 m differences in the record were rim and wall time,
not pace. the calibration fix (`apply_tonic` in `effectors.py`: the floor, the command and the
thermal cells at 25 C applied during the three calibrations) is in and being checked against the
oracle and against these runs; the pace reference is next.

**the other walking command (09:53 PDT; open loop, floor on, no vision, seeds 1 / 3, leg-MN spikes/s, L / R):**

| drive | seed 1 | seed 3 |
|---|---|---|
| floor only | 559 (348 / 211) | 586 (362 / 224) |
| DNg100 30 Hz | 627 (390 / 238) | 670 (416 / 254) |
| DNg100 100 Hz | **821** (479 / 342) | **808** (464 / 344) |
| DNg100 200 Hz | **1,121** (590 / 531) | **1,130** (602 / 528) |
| DNp09 100 + DNg100 100 | 762 | 790 |
| DNg100 100 + brake 30 | 786 | 791 |
| DNg74_a 100 | 457 | 470 |
| DNg105 100 | 299 | 306 |

**DNg100 (annotated BDN2; 2 cells; 1,870 direct synapses onto leg MNs against DNp09's 10) walks
the woken cord, as a dose:** half again at 100 Hz, double at 200, in both seeds; and it evens the
split the floor leaves left-heavy (62 / 38 at rest, 53 / 47 at 200 Hz), which bears on the
one-sided readouts of 22:14. DNp09 added to it subtracts a little, as it did alone. the brake at
30 Hz does not touch it. DNg74_a and DNg105, both heavy onto leg MNs by synapse count, turn the
legs *down* (to 0.8x and 0.5x the floor): the count says nothing about the sign. so the fly has
a walking command that works on the brain we run; it is not the one the record wired at 12:56.
next, one change each: `--walk-dn DNg100` in the loop, then the pace read against the standing
tonus measured in the floor (the fixed rule, its reference finally non-zero), so that standing
and walking are two readings of the cord and not two ends of an estimator.

**the calibrations in the standing brain (10:06 PDT; `apply_tonic`; oracle PASS, bit for bit, since it pins
`--no-floor`).** what the three calibrations measure now, against what they measured on the silent brain
(seed 10, config of record):

| calibration | silent brain (the record) | standing brain (now) |
|---|---|---|
| DNa02 rest offset (R - L per chunk) | +0.00 | -0.45 |
| standing leg-MN tonus per chunk | 0 | 51 |
| touch reflex asymmetry, left / right bristles | -0.099 / +0.041 -> gain 86 | -0.393 / +0.118 -> gain 24 |

the reflex is four times more lateralised on the woken cord than the silent one showed, so the
gain the loop needs is a third of what it had; the standing tonus is finally a number the fixed
pace rule can reference. three garden seeds, same config, before and after: walked 32.7 / 32.5 /
32.6 m -> 28.7 / 32.0 / 32.6; rim 0.07 / 0.10 / 0.05 -> 0.28 / 0.04 / 0.04; sugar frames
0 / 0 / 131 -> 387 / 279 / 0. two seeds within scatter, seed 10 pinned longer and on the fruit
longer. no behavioural claim; the claim is that the numbers the effectors run on are now measured
where they are used. adopted (it is a bug fix, not a tune).

**DNg100 in the loop, first attempt (10:31 PDT; `--walk-dn DNg100`, `--pace fixed --pace-k 1`, three seeds):**
walked 15-18 m with no command, 17-20 m at 100 Hz, **10-13 m at 200 Hz**, while the cord went 62-68 ->
90-95 -> 121-124 spikes per chunk. the higher dose walked slower. the reason is in the calibration i had
just fixed: `apply_tonic` applies the walking command too, so the standing tonus the pace rule
references was measured *with* the command on (76 per chunk at 100 Hz, more at 200), and the rule
read only the excess over the command's own output. the rest offset and the reflex gain should see
the command, because the loop runs with it; the standing reference must not. fixed (`TONIC_STAND`
skips the walk row); the three arms are re-running. and the arm with no command did not stand:
41 / 28 / 30 % of frames at the floor speed, mean 0.13-0.15 m/s, because the loop's leg output
(62-68) sits above the calibration's standing tonus (51): vision, contact and the fields drive the
legs above standing even with no command. that residual is real and stays in view.

**second attempt (10:55 PDT):** the three arms walked 14-19 m alike again (v 0.12-0.16), and the standing
baselines printed for one seed were 82, 106 and 58 per chunk across the arms, against 51 in the calibration
run an hour earlier. two causes, both mine: skipping the walk row left its cells at the drive the previous
calibration had set (the row was skipped, the cells were not zeroed); and the calibrations count from the
moment the brain is built, so the one-second standing measurement lands inside the floor's settling
transient (the open-loop probe settled 1.5 s before counting; that is why its 559 was stable). fixed:
a two-second warm-up under the tonic rows before any calibration, and the walk cells zeroed for the
standing measurement. third attempt on the cores; the oracle re-run alongside (the warm-up only runs
when tonic rows exist, so the silent brain is untouched).

**he walks, from the cord (11:41 PDT; third attempt: warm-up, standing tonus without the command; garden,
three seeds, 120 s; `--walk-dn DNg100`, `--pace fixed --pace-k 1`):** the standing tonus now calibrates at
57 / 58 / 59 per chunk across the arms (one seed), the same number whichever command the run will use.

| arm | walked | v mean | frames at floor speed | frames above 0.4 | leg MN per chunk | rim | sugar frames |
|---|---|---|---|---|---|---|---|
| no command | 16.5, 16.4, 19.5 m | 0.14, 0.14, 0.16 | 35, 34, 29 % | 1, 1, 2 % | 64, 64, 64 | 0.04, 0.09, 0.05 | 0, 0, 0 |
| DNg100 100 Hz | **33.7, 35.9, 36.5 m** | 0.28, 0.30, 0.31 | 15, 17, 10 % | 29, 36, 34 % | 89, 89, 91 | 0.11, 0.09, 0.13 | 406, 0, 0 |
| DNg100 200 Hz | **49.8, 48.7, 50.4 m** | 0.42, 0.41, 0.42 | 1, 2, 2 % | 68, 67, 70 % | 117, 121, 119 | 0.12, 0.18, 0.16 | 59, 0, 48 |

**a dose, three of three, for the first time in the loop:** no command 16-20 m, 100 Hz 34-37 m, 200 Hz
49-50 m, with the cord at 64 -> 90 -> 119 per chunk and the pace reading it against a standing
tonus that is finally a measured number. his speed is the brain's now, and the walking command
does what the record said it did, on the brain we actually run. **config of record from here:**
`--walk-dn DNg100 --walk 100 --pace fixed --pace-k 1` (DNg100 and k = 1 are the defaults now;
`--walk 100` still explicit) with the floor, adapting bristles, running steering and the two-channel
wheel as before; 100 Hz because its 0.29 m/s matches the estimator's 0.275 that every result since
yesterday morning was measured at, so those results stay comparable. every oracle pin unchanged.

**the residual, stated:** with no command he does not stand. the loop's leg output (64) sits a tenth
above the calibrated standing tonus (58), and the fixed rule half-wave rectifies the fluctuation, so
a cord that is merely noisy around standing reads as a slow walk (0.14 m/s, a third of frames at the
floor). two candidates, in order: the readout (an EMA over three chunks before the rule, as the
steering has, so noise does not rectify into speed), then the physiology (which floor row lifts the
loop's tonus above standing: the review's ablation, closed loop; nate's "flee response" question
lives here, since the thermal floor carries half the tonus and the ORN floor runs the wing motor).
one change per run, the readout first.

**the pace as a state (12:22 PDT; `StatePace`, `--pace state`; nate: "flies swap between no-walk and fast-walk").**
the cord's count smoothed over three chunks; walking switches on above 1.25x the standing tonus and off
below 1.10x; standing is v = 0; walking speed 0.15 + 0.35 x clip((c - 1.25 s) / s). labelled as the
assumption it is: forward velocity is bimodal, modes at zero and ~17 mm/s (DeAngelis 2019), and the
switch in life is the descending walk / halt state on a premotor network this LIF holds no state in,
so the threshold stands in for it at the readout. garden, three seeds, 120 s:

| command | standing | bouts | mean bout | v walking | walked | leg MN per chunk |
|---|---|---|---|---|---|---|
| none | 52, 60, 89 % | 56, 66, 15 | 1.0, 0.7, 0.9 s | 0.19, 0.17, 0.18 | 10.9, 8.1, 2.4 m | 65, 64, 59 |
| DNg100 100 Hz | 19, 14, 6 % | 20, 23, 8 | 4.9, 4.5, 14.1 s | 0.30, 0.30, 0.32 | 28.9, 31.5, 35.7 m | 86, 91, 94 |
| DNg100 200 Hz | 1, 0, 4 % | 3, 2, 9 | 40, 60, 13 s | 0.40, 0.42, 0.36 | 48.0, 50.4, 42.0 m | 117, 119, 118 |

**he stands, and he walks in bouts.** no command: standing most of the run, one-second fidgets; the
command at 100 Hz: bouts of five to fourteen seconds with stops between; at 200 Hz: nearly
continuous. the first velocity histogram of his with two modes. **adopted as the config of record**
(`--pace state` the default; the oracle pins `--pace fixed`), with `--walk 100`. **the residual, now
smaller and sharper:** two seeds of three fidget half the run with no command, because the resting
cord in the loop crosses 1.25x standing often (65 against 58); one seed stands 89%. which floor row
lifts the resting cord above its own calibration is the ablation, next, closed loop, no command:
the full floor against the floor without the thermal cells, without the ORNs, without JO, without
the leg proprioceptors. nate's question of the morning ("a flee response justifying a constant
walking rate?") is what that run answers.

**the floor-row ablation, closed loop (13:11 PDT; no command, state pace, garden, three seeds; nate's
question: is a missing or wrong signal producing a flee response that would justify a constant walk?):**

| floor | standing | bouts | walked | standing tonus (calibrated) | leg MN per chunk (loop) | DN per chunk |
|---|---|---|---|---|---|---|
| full | **92, 88, 91 %** | 10, 21, 16 | 1.7, 2.5, 2.0 m | 58 | 58, 61, 57 | 375, 341, 359 |
| without hot + cooling cells | 61, 69, 80 % | 34, 22, 26 | 7.7, 6.8, 4.4 m | 61 | 66, 62, 61 | 288, 335, 348 |
| without the ORNs | 73, 50, 85 % | 54, 44, 35 | 5.7, 11.1, 2.9 m | 61 | 60, 63, 58 | 243, 258, 227 |
| without JO | 53, 52, 66 % | 42, 44, 50 | 11.1, 9.5, 7.0 m | 49 | 53, 58, 55 | 224, 234, 242 |
| without the leg proprioceptors | 51, 71, 58 % | 37, 26, 51 | 10.8, 5.2, 9.1 m | 52 | 58, 62, 57 | 277, 286, 273 |

**no row pushes him to walk; every row taken out makes him fidget more.** the full floor stands
best, and the floor's tonus behaves as ballast: with less of it, vision and contact are a larger
fraction of the resting cord, more fluctuations cross the walking threshold, and the one-second
bouts multiply. so at the legs the flee hypothesis gets a no: a resting fly under the whole floor
is the stillest fly we have had. two things stay open. the descending population drops by a
third without the ORNs or JO (360 -> 230-250 per chunk), which is where the review's wing-motor
finding lives (the ORN resting rate runs the flight power muscles, open loop; not measured in
the loop yet). and the scatter: this same configuration stood 52, 60 and 89 % an hour ago
(12:20) and 92, 88, 91 % now, so run-to-run variance on the standing fraction is large (flyvis
on the GPU is not deterministic by default, and one-second bouts are triggered by fluctuations),
and three seeds per arm is thin for differences under about twenty points. the ordering (full
above every ablation, in every seed) is the claim; the sizes are not.

**the brake against the walking command (13:15 PDT; open loop, floor on, seeds 1 / 3, leg-MN spikes/s):**

| drive | seed 1 | seed 3 |
|---|---|---|
| DNg100 100 | 821 | 808 |
| + AN19A018 30 / 100 / 300 | 786 / 747 / 760 | 791 / 774 / 770 |
| AN19A018 100 alone | 547 | 556 |
| **+ DNg105 100** | **469** | **485** |
| + DNg74_a 100 | 614 | 636 |

**AN19A018 cannot halt the woken cord** at any rate, and alone it leaves the floor's tonus where
it is (13:55 yesterday was the silent brain). **DNg105 halts it:** against the walking command it
takes the legs to 0.57x, below the floor's own standing tonus, in both seeds; under the state pace
that is a stop. DNg74_a halts halfway. which of Sapkal 2024's halting types these are by name is
an audit item (the record called AN19A018 "BRK" from the silent-brain result; the type identities
against the paper's IDs are unverified). `--brake-dn DNg105` from here for the halting rows, and
the first piece of a feeding state, one change: `--stop-at-fruit 100`, the brake driven while
sugar is on his tarsi. nothing releases it yet, so the prediction is that he stops on the fruit
and stays; the satiety scalar that lets him go is the next change.

**the brake at the fruit, per frame (13:24 PDT; `--brake-dn DNg105 --stop-at-fruit 100`, three seeds):** he did
not stop. sugar on his tarsi for 0.6-0.8 s at most (control 0.5 s), the cord on the fruit at 94-100 per
chunk, walking pace. two reasons, both visible: the halt has a latency the contact never outlasts, and
the fruit is a solid he collides with, so the touch reflex steers him off it in the same frames he tastes
it. a fly on fruit does not withdraw from it. so the feeding state is built as a state (`FeedingState`,
`--feeding 3`): sugar latches it for three seconds (refreshed while he tastes), it holds the halt on
DNg105 and silences the withdrawal reflex while it lasts; satiety (`--satiety T`) fills at 1/T per second
of feeding and ends it, decaying over three minutes, and while full the taste no longer latches. the
first thing in him that outlasts its stimulus, modelled as what it does, labelled (the hunger lesson of
00:54). one change: the latch without satiety first; prediction: he stops on the fruit and stays.

**[13:38 PDT] the latch did not halt him either** (3.0 s on the fruit in one seed, the cord *rising* to 132 per
chunk on contact, no halt), and the open-loop time course says the halt is fast (two chunks on, one chunk
off). the cause is neither: `pair.py` only marked the brake cells as driven for `--stop-at-her`, so the
fruit brake and the feeding latch set a rate on two cells the engine never drew. both brake runs today
drove nothing; the "two reasons" above were plausible and beside the point. fixed; the state is logged
per chunk now (`feeding`, `sat100`); the latch re-run.

**he stops for the fruit (14:01 PDT; `--feeding 3 --brake-dn DNg105`, start 0.7 m east of the fruit facing it,
60 s, three seeds; the brake cells driven this time):**

| arm | reached the fruit | longest stay | feeding | leg MN feeding / walking | v feeding / other |
|---|---|---|---|---|---|
| control (walk 100) | 2 of 3 (2.1, 2.2 s) | 1.2, 1.2 s | | / 86-91 | / 0.20-0.24 |
| latch | 2 of 3 (55, 31 s) | **5.0, 9.2 s** | 8 %, 34 % of the run | **52, 59** / 86-90 | **0.02, 0.05** / 0.21 |

**the halt works in the loop:** while feeding, DNg105 takes the cord from ~88 to 52-59 per chunk (the
open-loop 0.57x), the state pace reads standing, and he stays on the fruit five and nine seconds
against the control's 1.2. the first time he has stopped for something he wants. (the start "facing
the fruit" did not deliver it: two seeds per arm reached it, at 2 s or at 31-55 s; the wheel drifts
him off a 0.7 m line.) **why he leaves:** the collision leaves him standing exactly at the fruit's
surface and the taste fired only while he pushed *into* it; a halted fly does not push, so the
taste stopped, the three-second latch ran out, the reflex returned. a fly standing on fruit is
tasting it: one centimetre of tolerance on the tarsal contact (`garden.py`). rerun; prediction:
he stays until the run ends, since nothing releases him; satiety next.

**he eats, and he leaves (14:13 PDT; the latch with the tarsal tolerance, and the latch with satiety filling in
8 s of feeding; start 0.7 m east of the fruit facing it, 60 s, three seeds each):**

| arm | seed | reached the fruit at | stayed | feeding | cord feeding / walking | v feeding | satiety |
|---|---|---|---|---|---|---|---|
| latch | 11 | 1.9 s | **58.1 s (to the end)** | 97 % | 48 / 87 | 0.00 | |
| latch | 12 | 56.7 s | 3.3 s (to the end) | 5 % | 66 / 92 | 0.02 | |
| latch | 10 | never | | | | | |
| latch + satiety | 12 | 15.4 s | **10.3 s, then left** | 20 % | 59 / 81 | 0.06 | reached 100 |
| latch + satiety | 10, 11 | never | | | | | |

**the state does what it says in every seed that reaches the fruit:** with the tolerance, a halted fly
keeps tasting and the latch holds him for the rest of the run (seed 11: 0.4 m walked in a minute, the
cord at 48 per chunk, speed zero); with satiety, he eats for ten seconds, fills, and walks away (seed
12: 9 m after leaving). the first thing in him that outlasts its stimulus, and the first thing he has
done on purpose: scenarios 5 and 7 of `docs/SCENARIOS.md`, in the loop. **what is weak is reaching
it:** from 0.7 m facing the fruit, one or two seeds in three get there, because the wheel is one cell
(DNa02 L against its own mean; the review, 09:14) and the arc is wide. the steering item is next.
adopted: `--brake-dn DNg105` the default; `--feeding 3 --satiety 8` explicit, a labelled state, in
the garden config of record from here. a 180 s run of the satiety fly (seed 12) is the one to watch:
satiety decays with tau 180 s, so he may come back.

**DNa01 on the drum (14:34 PDT; the review's first steering test; silent-brain drum as the record runs it, DNp09
100, 0.185 mV, running baseline, three seeds):** DNa02 follows both ways 3/3 (heading rate up to 15 deg/s
in the drum's direction); DNa01 follows 2/3 by sign, at 0.3-1.8 deg/s, barely above the drift. the rates say
why: DNa02 fires 2.0 left / 0.3 right per chunk on the drum, DNa01 0.2 / 0.2. **DNa01 is balanced and
nearly silent;** DNa02 is loud and one-sided. so DNa01 is not a wheel at these rates, but it is the first
candidate with a live right cell, and its rates under the floor (where everything is louder) are being
logged now, with DNb06 and DNg13. `pair.py` logs all three from here.

**the right side, at the level of single types (14:40 PDT; open loop, floor + DNg100 100, no vision, seeds 1 + 3
pooled, every descending type's left and right cell):** under the floor in the garden run, DNa01 is silent
on both sides, DNg13 silent, DNb06 6.0 left / 0.0 right, DNa02 1.6 / 0.05: every named steering type has
a dead right cell. but the descending population is balanced (159 L / 148 R per chunk in that run), and
across the 43 bilateral DN types that fire open loop the median right share is 0.45, with nine types
right-silent and nine left-silent: **the one-sidedness is per type and goes both ways**, not a lesion
of a hemisphere (the 22:14 conclusion holds at the population and fails type by type). the big tonic
types are symmetric (DNb05 191 / 198, DNg33 174 / 174, DNg100 74 / 80); the thermal pair fires right
only (DNp06 0 / 61, DNp35 0 / 55); DNb06, DNb09, DNp18, DNp20 left-heavy. is it the wiring? partly:
across 471 bilateral DN types the median right / left excitatory input weight is 0.93, 44 types have
the right below 0.7x and 28 the left; the correlation between a type's right rate share and its right
input-weight share is 0.48. DNb06 is a tracing hole (32 vs 710 excitatory input weight). **DNa02 is
not:** its right cell has 0.9x the left's input (2,540 vs 2,819 excitatory, 1,305 vs 1,362 inhibitory)
and fires nothing, so its silence comes from upstream, from whichever presynaptic partners are
themselves one-sided (22:14 named DNp09 R at 0.74x and AN03A008 R at 0.48x; under DNg100 the pattern
is the same). next: log DNa02's strongest presynaptic partners per cell in the loop and find the
one-sided ones; the fix, if it is a tracing asymmetry in a mirror pair, is a labelled per-type mirror
normalisation of the wiring, opt-in, oracle-checked.

**DNa02's partners (14:46 PDT; `--log-pre DNa02`, the 40 strongest inputs to each cell logged per chunk, garden,
60 s):** the wiring into the two cells is a mirror: AN03A008 137 (L) / 121 (R), PS049 -91 / -89, DNa03 47 / 50,
LAL018 45 / 54, CB0431 43 / 52, DNae005 54 / 43, and so on down the list. **and every one of the eighty is
silent in the loop** (0.00-0.07 spikes per chunk; the weighted drive from them is small and net inhibitory
on both sides: L -5.3, R -2.7). DNa02 L's 1.44 per chunk does not come from its strong inputs; it comes
from the long tail of weak ones, hundreds of cells, and that is where the left-right difference is. so
the question is a pathway, not a partner: the same run with every presynaptic cell logged (3,000), summed
by type, is on the cores.

**the pathway (14:53 PDT; all 3,451 presynaptic cells of DNa02 logged, garden, 60 s, seed 12):** the
excitation into the two cells is nearly equal and it is the horizontal system: HSS 130 (L) / 64 (R), HSE
55 / 64, HSN 0 / 41, the lobula plate's wide-field motion cells, the pathway the physiology names
(Rayshubskiy 2020). **the difference is inhibition: 88 into the left, 205 into the right.** one type carries
most of it: IN12B014, a crossing inhibitory pair in the cord whose left cell projects to DNa02 R at -18.9
and whose right cell projects to DNa02 L at -20.7 (a mirror), and whose left cell fires ten times more
(2.95 / 0.31 per chunk). the rest: MBON31 (-12 / -34), PS321 (0 / -14), IN19A003 (-9 / -21), PS100 (-4 / -15).
so DNa02 R is not dead; it is held under by a cord interneuron that is louder on the left, which puts
the asymmetry one level up, in the cord's own left-heaviness (348 / 211 leg-MN spikes at rest this
morning). the floor rows themselves are balanced per side (leg proprioceptors 292 / 288, JO 348 / 324,
GRN 706 / 710; only the ORNs lean right, 883 / 1,343), so the floor is not the lopsided input. next:
IN12B014's own inputs (logged), and the cord's per-side wiring.

**the amplifier, and the hole (15:00 PDT).** IN12B014's own inputs, all 3,123 logged: its loudest is DNb05, the
balanced tonic pair (190 / 198 spikes/s), and the *weights* differ: DNb05 L -> IN12B014 L 11.5, DNb05 R ->
IN12B014 R 7.1; DNbe007 12.8 / 6.1; total excitatory drive 262 into the left, 168 into the right. and the
pair inhibits each other (L -> R -25, R -> L -14), a winner-take-all, so a 1.6x weight difference becomes a
100x rate difference (34 / 0 open loop), and the winner sits on DNa02 R. structurally the whole right
ventral cord is under-traced: right / left total input weight 0.85 for the leg MNs, 0.82 for all cord
interneurons, 0.69 for IN12B014; the brain's descending neurons 0.93. **so the lesion is real, it is in
the reconstruction, it is the right cord, and a bistable pair carries it to the wheel.** the correction:
`wiring.mirror_normalise` (`--mirror all|vnc`, off by default, the oracle untouched): for every bilateral
type, each cell's excitatory and inhibitory input scaled to the pair's mean, factors clipped at 2x.
labelled as what it is: bilateral pairs taken as mirrors, count differences taken as tracing. open loop,
walking (seed 1): mirror off, leg MN 479 L / 342 R, IN12B014 34 / 0, DNb06 29 / 0; mirror all, 379 / 424,
27 / 12, DNb06 0.8 / 0 (that pair is a hole at one end, 32 vs 710, and the clip cannot mend it); with the
cord scope (the measured bias) the numbers are below. the loop test next: DNa02 R, the drum, the fruit.

**the cord mirror in the loop (15:09 PDT; `--mirror vnc`: 3,389 bilateral cord types, 474 factors at the clip):**
open loop, walking: leg MN 392 L / 451 R (from 479 / 342: it overshoots, so the cord's output asymmetry is
not only its input weight), IN12B014 28 / 10 (from 34 / 0). drum, DNa02 wheel: follows 3/3 (unchanged;
the drum runs the silent brain). garden beside the fruit, three seeds: he walks onto it in two (1.2 and
1.4 s), eats 9 and 10 s, fills, leaves; leg MN 41 / 48 per chunk (from 50 / 40); IN12B014 2.1-3.0 / 0.9-1.1
(from 2.95 / 0.31). **and DNa02 did not get its right cell back:** R 0.03-0.16 (from 0.05), and L fell to
0.04-0.59 (from 1.56), because the woken right IN12B014 now inhibits DNa02 L as its mirror did DNa02 R.
the correction evens the cord and quiets the wheel on both sides. **not adopted** (a change that silences
the one live steering cell is not an improvement; it stays opt-in, labelled, for the cord questions).
what the pathway said stands: the excitation into both DNa02 cells is the horizontal system, alive on
both sides at 10-20 per chunk. HS left minus right is the flow-balance signal (Srinivasan 1991; Kern
2012; `docs/GARDEN.md`), and it is what drives DNa02 in life; reading the wheel one synapse upstream, at
HS, is the next test, on the drum first, both signs.

**HS as the wheel (15:13 PDT; drum, `--wheel HS --wheel-gain +0.5 | -0.5`, running baseline, DNp09 100, 0.185, three
seeds):** at +0.5 he follows both ways 3/3, heading rate 12-16 deg/s with the drum at +30 and 28-35 deg/s
at -30 (DNa02's wheel: up to 15), with HS at 20-24 per chunk on *both* sides; at -0.5 he anti-follows and
spins at the clip (120 deg/s) in every seed. the sign is decisive. HSN / HSE / HSS are the cells that
drive DNa02 in life and in this brain (the pathway, 14:53), they are alive under the floor on both sides,
and their left-right difference is the flow-balance signal insects steer by (Srinivasan 1991; Kern 2012).
so the wheel reads one synapse upstream of the descending neuron, which is where the lesion cannot reach
it. `--wheel HS` in the garden next, from the usual start and from beside the fruit; DNa02 stays logged.

**HS in the garden (15:40 PDT; `--wheel HS`, the config of record otherwise, three seeds from the usual start and
three from beside the fruit):** equal to DNa02, not better: from the usual start he finds the fruit in one
seed (at 6.6 s, eats 12.9 s) as DNa02 did in one; from beside it two of three, as before; rim time the
same (0.04-0.14). HS at 41-54 per chunk on both sides. **adopted as the default wheel** on principle (both
cells alive, sign validated on the drum, upstream of the cord's hole; behaviour no worse); the oracle pins
`--wheel DNa02`. so reaching the fruit was never the wheel's dead cell. **it is noise:** his heading
change per chunk while walking has an sd of 4.2-5.6 degrees on every file, either wheel, which is 42-56
deg/s rms, and Katsov 2017 calls anything over 45 deg/s a saccade. he is saccading continuously, in
random directions, because the wheel reads the difference of two Poisson counts of ~50 through a gain
with three chunks of smoothing. no fly walks like that, and no fly reaches a fruit 0.7 m away through
it. one change: the wheel's smoothing, three chunks to ten (`--steer-ema 10`; a graded HS cell
integrates over that anyway), on the drum and in the garden, heading noise measured.

**the smoothing, and where the noise is (16:09 PDT; `--steer-ema 10`):** drum, HS wheel, three seeds: follows
3/3 (+16 / -31 deg/s), and the still phases are flat where at three chunks they drifted at 10-25 deg/s.
garden: touch frames 366-718 (from 1,070-2,452), rim the same, heading noise 37-41 deg/s rms (from
42-50): less than the smoothing alone predicts, so the HS counts are not the noise. reconstructing each
channel's yaw from the logged counts (walk, seed 10): **the HS channel contributes 1.3 degrees per chunk,
the descending-population channel 3.6** (its raw L-R has an sd of 17.5 spikes per chunk across 1,310
cells), and their sum matches his actual heading change at r = 0.87. the population channel, added for
warmth (10:15 yesterday) and kept for the wind, is the noise on the wheel; the review said retire it
(09:14). **adopted:** ten chunks the default (the oracle pins three); the population channel out of the
garden's config of record (`--dn-gain 0.5` stays a flag for the wind question, whose result stands as
recorded with it on). **and a bug in satiety, found because he finally stayed put:** beside the fruit,
seed 10 walked onto it at 2.5 s and fed for 117 s, 98% of the run, because at full the state ended,
satiety began to decay, and a hair under one the taste latched again, every frame. hysteresis: full at
one, hungry again below half (`rearm`). the noisy wheel used to carry him off before it mattered.

**the settled fly (16:30 PDT; HS wheel, ten chunks of smoothing, no population channel, DNg100 walking at 100 Hz,
the state pace, DNg105 halting, feeding with satiety and hysteresis; beside the fruit, 120 s, three seeds):**

| seed | onto the fruit at | fed for | feeding, whole run | heading noise (deg/s rms) | chunks over 45 deg/s | walked |
|---|---|---|---|---|---|---|
| 10 | 2.1 s | 9.9 s | 7 % | 25 | 8 % | 24.0 m |
| 11 | 1.9 s | 8.7 s | 7 % | 25 | 8 % | 22.3 m |
| 12 | 2.0 s | 10.8 s | 7 % | 27 | 9 % | 23.1 m |

**three of three:** he walks onto the fruit in two seconds, eats until full, leaves, and wanders for the
rest of the run. heading noise 25-27 deg/s rms (from 50-53 with the population channel and three chunks;
Katsov 2017's saccade threshold is 45, and he crosses it in 8 % of chunks now against 29-36 %). this is the config of record from here, and the fly nate gets to watch.

**[16:48 PDT] the walk from the usual start, same config, three seeds** (the first attempt was killed
mid-batch by another agent's process kill; relaunched): walked 25-28 m, standing 15-24 %, rim 0.07-0.14,
heading noise 20-29 deg/s rms (from 37-41 with the population channel out and 42-56 this morning), chunks
over 45 deg/s 4-9 %. **no seed found the fruit from the far corner** (0/3; the earlier "found by sight" runs
were 1-2 of 3 with a wheel whose noise walked him into things). so the settled fly walks straight, eats
when he reaches food and leaves when full; he does not seek it by sight from four metres. seeking from
afar is the plume and the wind gate, and the anemotaxis result of 09:12 was measured on a fly that could
not hold a heading: that is the experiment to re-run first on this one.

**where the time goes (17:10 PDT; `docs/PERFORMANCE.md`, an opus agent that profiled it):** the LIF step is 81-88 %
of the loop, the eye render 4-12 %, flyvis 5-7 % (the record's "largest single cost" of 09-17 is stale).
inside the step: the membrane pass over every cell ~84 %, the Poisson draw for the 25,973 driven receptor
cells ~22 % (the floor made it large), propagation 3 % (six million synapses, but ~100 cells fire per ms).
the step scales 1.86x from one thread to six and nothing from two to six under contention, so the unit of
parallelism is the job, and three jobs at four threads on eight cores, which is how every batch today
ran, was oversubscribed. the one measured, bit-identical win: the Poisson draw folded into one nogil
kernel, 1.216x on the step, 500 / 500 steps identical, prototyped, not yet adopted. two plausible ideas
died on measurement (batching the ten frames of a chunk into one raytrace is slower than hoisting the
ray rotation; slicing T4/T5 on the GPU before the transfer buys 3 %), and flyvis is non-deterministic call
to call at 3e-7, which is what `--deterministic` suppresses. **and an incident:** the agent ran
`pkill -f world/pair.py` to clean up its own runs; `run_many.py`'s command line carries that string, so it
killed the settled walk batch and the oracle's fourth arm mid-run (16:28). both were re-run; the rule
(no pattern kills, own PIDs only, scratchpad only) is in every brief from here. nate caught it.

**the benchmark scorer, calibrated on real flies first (17:27 PDT; `experiments/benchmark.py`; `docs/BENCHMARKS.md`;
the Roman lab's trajectories via `scripts/fetch_opynfield.sh`, ten flies per arena):** tracked centroids at 33 Hz
jitter, so the tracks are smoothed over 0.15 s, heading is taken from displacement only while moving and
held through stops, and the walking mode is the peak above the valley at 4 mm/s (the stop mode sits below it).
with that, the 8.4 cm flies read where the papers put them, and the 5.0 cm flies read as a different animal,
which is the spread a pass bar gets calibrated against:

| metric (published) | 8.4 cm, 10 flies | 5.0 cm, 10 flies |
|---|---|---|
| fraction below 1 mm/s | 0.21 | 0.72 |
| walking mode, mm/s (11-15) | 10.3 | 5.6 |
| within 6 mm of the wall (0.88-0.90) | 0.92 | 0.96 |
| outer third of the radius (0.90) | 0.97 | 0.96 |
| inter-turn interval, ms (250 +/- 110) | 258 | 1,224 |
| turn angle at 1 s, mode, deg (12.6 edge) | 15.5 | 20.2 |
| circling bias (population 0) | -0.06 | +0.04 |

two rows are the scorer's, not the flies': walking bouts and pauses fragment at the 1 mm/s threshold
(0.35 s against Valente's 1.4-2.1) and the angular-velocity tail is displacement noise (2,500 deg/s); both
marked in the code, both fixed by a hysteresis and a heading filter when our runs exist to compare. the
round arena (5.6 sim m, a 0.47 m rim) is the next build; his runs go through the same scorer, decimated
to 33 Hz, with the time-rescaling control for his slow gait.

**the dish (18:25 PDT; `--world arena`: a 5.6 m circle, a 0.47 m rim, a uniform floor, the wall the only object;
600 s, three seeds, the config of record without the feeding flags; `experiments/benchmark.py` against ten of the
Roman lab's Canton-S males in the 8.4 cm dish, both decimated to 33 Hz):**

| metric (published, source in `docs/BENCHMARKS.md`) | real flies, 10 | him, seeds 10 / 11 / 12 |
|---|---|---|
| within 6 mm of the wall (0.88-0.90) | 0.92 | 0.98, 0.98, 0.98 |
| outer third of the radius (0.90) | 0.97 | 0.99, 0.98, 0.99 |
| walking speed mode, mm/s (11-15) | 10.3 | 4.5 x3 |
| fraction below 1 mm/s | 0.21 | **0.00 x3** |
| turns under 30 / 45 / 60 deg per 40 ms (0.60 / 0.72 / 0.80) | ~0.9 / 0.95 / 0.96 | **1.00 / 1.00 / 1.00** |
| inter-turn interval, ms (250 +/- 110) | 258 | **1,102, 1,351, 1,014** |
| 99th percentile angular velocity, deg/s (< 450) | 2,500 (tracking noise) | 241, 234, 251 |
| circling bias, signed (population 0) | -0.06 | **+1.00, +1.00, -1.00** |

**he wall-follows like a fly, slightly more; his gait is the known third; and three misses are one
thing:** in ten minutes he never stops (0 % below 1 mm/s against 21 %), never makes a sharp turn (every
40 ms heading change under 30 degrees against 60 % in life; an inter-turn interval four to five times
theirs), and never reverses along the wall (a circling bias of exactly one: he picks a direction at
the rim and keeps it for the whole run). the flow wheel is smooth by construction, and the cord stops
only when something makes it. what a fly has and he lacks is *structured* spontaneity: saccades, which
are discrete events preceded by DNa02 bursts in walking flies (Rayshubskiy 2020), and bouts that end on
their own through halting neurons firing without a cue. this morning's fly had noise and no structure;
tonight's has neither. the next physiology is the saccade and the spontaneous stop, looked for first in
the wiring (do the steering and halting pairs burst on the woken brain, and can a burst be read as an
event rather than a rate) before any stand-in. two scorer notes stand: the real flies' bout and pause
durations fragment at the 1 mm/s threshold and their angular-velocity tail is tracking noise; his
tracks are exact, so on those rows only his side is trustworthy until the scorer gets its hysteresis
and heading filter. the viewers do not yet draw the ring (they draw a square wall for the dish).

**is the compass alive? (21:14 PDT; nate: "what triggers the spontaneous bursts in real flies?"; `--log-types`,
`experiments/compass.py`; garden, 180 s, seed 12, the config of record):** **no.** EPG (46), EPGt, PEN (42), Delta7
(42), PEG, PFL1 / 2 / 3 (50): every cell at 0.00 Hz for three minutes with vision on. no bump, so no heading, so
nothing for a goal to be compared against, so no PFL3 drive onto DNa02, so no saccade: the saccade generator
is not asleep, its instrument is unplugged. **where it is unplugged:** structurally the ring neurons (282 ER)
are fed by the tubercle cells (156 TuBu), those by 1,009 MeTu cells in the medulla, and those by Mi15 and Dm2
(15,816 and 10,612 synapses), the targets of R7 and R8: the anterior visual pathway, the colour / UV / polarisation
channel, which is how a fly's compass sees the sun. the seam carries T4 and T5 only. **and the ring does not
hold a bump when kicked:** two wedges (L3, L4) driven at 60 Hz for a second fire only while driven (64 Hz summed),
PEN answers at 1.3, Delta7 at 25, and within a tenth of a second of release everything is 0.0, both seeds; the
EPG-PEN recurrence (4,200 synapses) does not sustain itself at these constants. two problems, in order of
tractability: (1) the input: flyvis computes Mi15 (not Dm2), so the seam can carry Mi15 onto his own Mi15 cells
by column as T4 / T5 go today, a luminance stand-in for a UV pathway, labelled, with a sun disc in the sky to
give the ring something to hold; a sensory-driven bump is still a compass while the sun is up. (2) the
persistence in darkness: the attractor's own physiology, its own item. nate's other question, ocelli and
colour: colour is exactly this pathway; the ocelli, as far as this record knows, serve flight and gaze
stabilisation rather than the ring, said with less confidence. the anterior visual pathway is the next build.

**the UV eye (21:26 PDT; nate: "does our 3d world need to properly model UV sources?"; `--uv`, `garden.scene_uv`, a sun
disc in `omma`, a second flyvis handing Mi15 to his Mi15 cells by column, `seam/columns_uv.py`).** in UV the sky is
the source (Rayleigh), the ground dark (soil and leaves absorb it), water a mirror, the sun a clipped disc; the
eye's five-degree acceptance angle is the bloom. built as a second retina from the same eye: on his UV retina
the ground reads 0.05, the horizon band 0.43, the sky 0.70, the disc 1.0. flyvis computes Mi15 (not Dm2), so
Mi15 crosses the seam as T4 / T5 do (1,043 cells placed by column): **Mi15 fires at 15 Hz mean, up to 106; MeTu3c
answers at 7 Hz; nothing beyond.** each tubercle type wants a different MeTu and the ones it wants are fed by
what the seam did not carry: TuBu01 / 06 want MeTu2a, whose inputs are Dm-DRA1 and R7d, the dorsal rim area,
the *polarisation* compass; MeTu1 wants Dm2 (41 synapses per cell), which flyvis does not model; MeTu3c's own
targets are TuBu09 / 10 (not logged in that run). **and the photoreceptors are in the build:** R7p 332, R7y 481,
R7d 82 (the dorsal rim), R7_unclear 404, R8 the same, all silent. so the honest seam for this pathway is not
flyvis: drive his own R7 cells by column from the UV retina and his R8 from the green one, as receptors, and let
his medulla do Dm2, MeTu and the rest. `seam/columns_uv.py` places 570 R7, 1,273 R8 and 1,441 Dm2 cells by
column from their wiring (photoreceptors by where they project). R7d stays at rest: we have no polarisation to
give it, and that is the sky compass we cannot build with this eye. the receptor rows are next, behind the
oracle. nate's other asks tonight: the UV in the human view as false colour (the viewer agent, in flight); an
ocelli panel waits for ocelli.

**the anterior visual pathway does not propagate as spikes (21:44 PDT).** three attempts, each one honest:
(1) **his own photoreceptors driven by column** (`--uv-photo`: R7 from the UV retina, R8 from the green, Poisson
stand-ins; R7 at 25 Hz mean, sky-facing cells at 100; R8 at 60): Dm2 silent, MeTu3c *quieter* (6.6 -> 3.9 Hz).
the reason is the sign: every photoreceptor in him is histaminergic, so light makes them inhibit their targets
(R7 -> Dm8 -6.4, -> MeTu3c -3.1 per cell), and the next cells signal in life by release from that inhibition, which
a silent spiking cell cannot do. the receptor-level seam is wrong in principle here, as it was for the motion eye.
(2) **the graded ON cells across the seam** (`--uv`: flyvis's Mi15, L5 and Mi1 onto his own, 1,043 + 1,551 + 1,543
cells by column; Dm2's traced excitation is L5 +2.1 and Mi1 +1.7 per cell): L5 fires at 2 Hz, Mi1 at 8, Mi15 at
15; **Dm2 stays silent** (two synapses' worth against a seven-millivolt threshold); MeTu3c 6 Hz; TuBu09 / 10 at 2
and 0.7; every ring neuron and every compass cell 0.00. (3) **a gain on the pathway** (`--uv-gain 400 | 1000`):

| gain (Hz per unit) | Mi15 | MeTu3c | TuBu09 | TuBu10 | Dm2 | MeTu1 | ER2_c | ER4d | EPG |
|---|---|---|---|---|---|---|---|---|---|
| 150 | 14.7 | 6.4 | 2.1 | 0.7 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 400 | 30.3 | 20.9 | 16.4 | 9.8 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 1,000 | 49.1 | 36.4 | 28.1 | 23.4 | 0.03 | 0.00 | 0.01 | 0.00 | 0.02 |

at an absurd drive the chain reaches two tubercle types at 25 Hz and the ring neurons behind them do not
answer; Dm2, MeTu1 and the other tubercle types never wake. **so the pathway is four graded stages deep (R7,
Dm2, MeTu, TuBu) and does not carry spikes at these constants, which is monday's optic-lobe finding one neuropil
over. and the ring itself needs more than input:** its bump is tonic recurrent excitation (EPG-PEN, ExR1)
shaped by *inhibition* from the ring neurons (ER -> EPG is GABAergic), and a silent cell cannot be shaped by
inhibition; the kick test (21:14) said the recurrence does not hold at 0.185 mV either. the compass in this
fly is a graded-physiology build, like flyvis was for the motion eye: a graded model of the anterior pathway
and of the ring, or a labelled stand-in at the ring neurons with the ring given a tonic floor. neither is
tonight. what stands: the UV retina, the sun, the columns for R7 / R8 / Dm2, the per-type logging, and the
measurement that says where the wall is. the viewer draws all of it (a UV false-colour layer as a second
raytrace, the eye in green / UV / both, the dish as a ring).

**the compass points (22:50 PDT; `--ring`: the stand-in, labelled; nate: "the stand-in will tell us if the work's worth it").**
the stand-in, built on his cells and his wiring: ExR1 (4 cells, 1,107 synapses onto EPG) held tonic so the ring sits
near threshold; the 215 ring neurons with real output onto EPG given field azimuths tiling the circle and fired by the
sun at that azimuth relative to his heading (von Mises, kappa 2); their synapses onto the wedge that should hold the bump
notched to a tenth (`wiring.ring_map`: the plastic map of Kim 2019 and Fisher 2019, which life learns and we impose);
PEN, Delta7, PFL as wired. the ring is a *ring*: every ring neuron inhibits every wedge within a concentration of 0.1,
so without the notch the sun lowers inhibition everywhere at once and nothing forms. at ExR1 100 Hz and a ring peak of
60, over-inhibited, EPG 0.00. the sweep (40 s, seed 12, garden, the sun at 27 deg):

| ExR1 Hz | ring peak Hz | EPG Hz | Delta7 | bump strength (shuffle) | phase vs heading | offset held | bump follows turns |
|---|---|---|---|---|---|---|---|
| 200 | 20 | 3.2 | 0.3 | **0.76** (0.25) | **+0.987** | **0.95** | **+0.70** |
| 200 | 60 | 0.15 | 0.0 | 0.98 (0.30) on 0.7 spikes per chunk | +0.81 | 0.98 | +0.10 |
| 400 | 20 | 8.3 | 2.4 | 0.67 (0.19) | +0.22 | 0.92 | +0.78 |
| 400 | 60 | 1.2 | 0.0 | 0.88 (0.52) | +0.90 | 0.97 | |

**at ExR1 200 and a ring peak of 20, a bump:** three times the shuffled vector length, a constant offset from his
heading (concentration 0.95), a circular correlation of 0.987 with where he faces, and it moves with him when he turns
(`docs/figures/compass_bump.png`). his heading, in world coordinates, in his own ring cells, from the sky. **the
honest caveats:** it is sensory-driven; PEN are silent, so the bump is the sun through the ring neurons, not the
attractor integrating his turns, and it will vanish when the sun does (the kick test said the recurrence does not
hold). and PFL3 is silent, because the comparator's other input, the goal in the fan-shaped body (hDelta, FC2, PFN:
its largest inputs), has no source. so: the ring can hold a bump when given tonic excitation and a map, which is what
nate asked the stand-in to find out; the eye work (a graded anterior pathway) would replace the imposed fields with
seen ones; and the goal is the next stand-in, the one that makes PFL3 fire and a saccade happen. defaults set
(`--ring-exr 200 --ring-er 20`).

**the comparator fires (23:37 PDT; `--goal`: the goal in the fan-shaped body as a bump over the 92 FC2 cells by column,
the column-to-wedge offset read from PFL3's own glomerulus / column labels: -1 degree, from 24 cells).** PFL3's inputs
are the textbook (Delta7 -40 per cell: the heading, inverted; hDelta and FC2 +18 to +28: the goal) and its outputs go to
the LAL (LAL121 +20) and AOTU019. with the quiet ring (ExR1 200, ring peak 20; EPG 3 Hz, Delta7 0.4) and the goal at
40 Hz, PFL3 fires at 0.2 Hz and follows nothing: the heading side never arrives. with a louder, sharper ring (ExR1 400,
ring peak 30: bump 0.81 against a shuffle of 0.25, phase correlation 0.98) and the goal at 100 Hz (FC2 26 Hz):

| goal 200 deg, he starts at 35 | PFL3 Hz | PFL3 L-R, goal to his left / right / ahead | corr(L-R, sin error) | LAL121 | DNa02 |
|---|---|---|---|---|---|
| goal 40 Hz | 0.18 | +0.23 / +0.12 / -0.09 | -0.31 | flat | 29 L / 5 R, flat |
| goal 100 Hz | **3.56** | **+0.50 / -0.39** / -0.93 | **-0.68** | follows (+0.54) | 29 L / 5 R, flat (+0.10) |

**PFL3 left minus right flips with the side the goal is on, with the ipsiversive sign** (goal to his left -> PFL3 L
up -> DNa02 L in the wiring -> a left turn), reaches LAL121, and dies at DNa02, which the cord's hole (14:53) holds
one-sided at 29 / 5 whatever PFL3 says. so the goal loop is closed one cell upstream, as the wheel was this
afternoon: `--goal-wheel` reads PFL3 L-R as a third channel through the running baseline, labelled as the readout it
is. prediction, running: with the goal at 200 he turns to it and holds; with the goal at 35, where he starts, he
stays. both stand-ins are tuned (ExR1 400, ring 30, goal 100) and say so.

**menotaxis, not yet (23:55 PDT; `--goal-wheel`: PFL3 L-R as a wheel channel; three readings, seed 12, the garden).**
(1) through the running baseline, gain 10: no holding (the running baseline subtracts a sustained error away: the
wrong estimator for a goal). (2) a fixed baseline, gain 10: he turns toward the goal once (error 165 -> 30 in ten
seconds) and the rest of the loop takes him away; |error| < 30 in 21 % of the run; with the goal where he starts,
32 %, drifting off. (3) a fixed baseline, gain 20, five seconds of smoothing on the channel, 120 s: 16 % and 42 %,
the error wandering through the whole circle in both; moments of closing, nothing held. the arithmetic: PFL3 fires
3.7-5 spikes per chunk per side, so the Poisson noise on left minus right is ~2.7 spikes against a goal signal of
0.5; at any smoothing short of the run itself the noise wins, and the flow wheel and the rim reflex are louder
besides. **so the comparator computes the sign of the error and its spiking output is too sparse to steer with.** in
life PFL3 is graded and has no shot noise. the goal loop, like the anterior pathway and the ring's persistence, is a
graded build. what stands from the night: a ring that holds a heading from the sky, a goal that PFL3 reads with the
right sign, and the exact place where spikes stop being enough. the stand-ins stay opt-in (`--ring`, `--goal`,
`--goal-wheel`), tuned as labelled (ExR1 400, ring 30, goal 100).

**the profile, corrected (10:30 PDT; nate's question about flyproject.io's "one fly brain per CPU core").** the
performance table of 17:00 yesterday was measured while my batches held every core; on a quiet machine, in the loop's
own process, the LIF step is 1.25 ms at two threads (the bare membrane pass 0.83 ms there, 0.42 ms standalone, 0.12 at
four threads: ten flops over eight arrays per cell, memory-bound), and the brain plus flyvis interleaved as the loop
does it runs at 0.95 s per simulated second. a clean 20 s garden run: 56 s wall at two threads, 39 s at four, 2-3 s
per simulated second including the eye. so a whole-fly LIF at 1 kHz on about one core is plausible, for them and
nearly for us; what a tight Java loop would cut is our Python around the kernel and the Poisson draw over 26,000
receptor cells. their claim is not the dubious part; what they cut from the wiring (3.1 M synapses of BANC's) and
what they hand-tuned ("time constants, thresholds and a few gains are ours") is, and two agents are reading the
decompiled jar and the two open-source siblings for exactly that.

**three flies in Minecraft, and what they said about ours (10:39 PDT; nate: "how did they get one core, and how accurate";
`docs/MINECRAFT_FLYPROJECT.md`, `docs/MINECRAFT_OPEN.md`, two opus agents, claims spot-checked in the decompiled and
compiled sources).** flyproject.io (closed, CC-BY-SA, BANC v888): one core is real, measured at 0.5-1.0 ms per step on
one pinned core through their own loader, dense float32 loops, no tricks; **and the network is inert**: at the awake
operating point the game injects ~295 suprathreshold kicks per ms and the brain emits 272 spikes, the network's own
contribution near zero (all synaptic input together depolarises a cell by 0.65 % of threshold). the turn signal is the
L-R imbalance of all 1,316 descending neurons, half of whose spikes are a uniform random kick (`SplittableRandom`,
z-scored against its own mean; a permanent rightward bias from the 651 / 665 split); the male is forty scripted lines
under a HUD label reading "MaleCNS courtship"; 9 % of BANC's synapses retained; no delay; an uncited adaptation term;
gains of x2, x20, x25. blendi-remade/fly-brain-minecraft (open, MaleCNS): the best open Shiu implementation the agent
had read: exact linear integration, the right constants, real cell types both ends, 1,769 measured columns, a
validation doc that publishes its failures; its loom-escape claim does not reproduce and its odour readout is
anticorrelated with the stimulus. AshtonLong/fruitfly-brain-mod (open, FlyWire): faithful graph, 25 ms of neural
time per 500 ms of wall clock, neither readout works (odour left or right both turn left; looming escape 0 of 12);
behaviour scripted with a neural jitter. **the two findings about our own engine:** (1) the membrane kernel divides
by tau per cell; a multiply is 1.63x on the pass that is most of the step (not bit-identical, 1.9e-6). (2) **Shiu's
model integrates the linear system exactly** (`method='linear'` in his `model.py`, checked) **and freezes g during the
refractory period; the reference engine we matched spike for spike, and therefore we, use forward Euler at 1 ms,
which puts the synaptic potential's peak 16 % low** (analytic 0.1575 per unit jump; Euler at dt 1.0: 0.1323; the
total charge preserved, the peak not, and spiking is a threshold on the peak). so this fly is ~16 % less synaptically
efficacious than the paper's at the same constant, which bears on the 0.275 / 0.185 argument of 09-17. staged as
`--integrate exact` (opt-in), to be checked against the analytic PSP, then the sparsity, the drum and a garden run,
then the oracle re-frozen with a label if it holds. also learned from them: decayed conductances go subnormal in a
quiet brain and slow the step 1.8x (ours: 0.29 -> 0.52 ms after 20 s); a flush at 1e-20 is in the kernel, under the
oracle now. the landscape doc gets these three as rows.

**the exact integrator (10:45 PDT; `--integrate exact`; Shiu 2024's `method='linear'`, checked in his `model.py`).** the
kernel steps the linear system exactly: v <- v e_m + ext (1 - e_m) + g A (e_s - e_m), g <- g e_s, A = tau_syn /
(tau_syn - tau_m); three multiplies, no divides. on one cell with a unit synaptic jump the peak is 0.15744 against the
analytic 0.15750; our Euler kernel at dt 1 ms gives 0.13228, 16 % low (the total charge is conserved, the peak is not,
and spiking is a threshold on the peak). and it is faster: 0.51 ms a step against 0.75. under it the brain is a
different operating point:

| open loop, floor on, seed 1 | Euler (the record) | exact |
|---|---|---|
| leg MN spikes/s: no command / DNg100 100 / 200 | 559 / 821 / 1,121 | 927 / 1,269 / 1,510 |
| DNg100 100 + DNg105 100 (the halt) | 469 | 848 (below standing: still a halt) |
| other VNC motor (wing, neck, abdomen) | 1,160-1,360 | 3,300-3,500 |
| undriven cells: mean Hz / cells firing | 0.23 / 2,120 | 0.42 / 4,004 |

**Kenyon-cell sparsity** (five food-ORN types at 150 Hz for 1 s, the fraction of KCs that fire; life ~5-10 %,
Turner 2008, Honegger 2011):

| | 0.185 mV | 0.275 mV |
|---|---|---|
| Euler | 1.8 % (0.19 Hz) | 7.4 % (1.3 Hz) |
| exact | **3.9 %** (0.59 Hz) | 12.6 % (3.0 Hz) |

so with the paper's integration, 0.185 lands closest to the physiological band from below and 0.275 overshoots it,
which is the same ordering the 09-17 argument gave and a slightly different place on the line. the dose and the halt
survive with their ordering; the wing motor triples, which stays in view. the drum and a fruit run under the exact
engine are scored below; if they hold, the exact engine becomes the record's, with the oracle re-frozen on it and
labelled, and the Euler engine kept behind `--integrate euler` with the old oracle for the port's history.

**the exact engine adopted (10:47 PDT).** the drum under it follows both ways 3/3 (HS wheel, +13 to +15 / -31 to -35
deg/s); beside the fruit he walks onto it at 1.8 s, eats 9.3 s, leaves; the standing tonus recalibrates to 99 per chunk
and the state pace reads it; the cord's crossing inhibitor's right cell wakes to 2.4 against the left's 5.7 (Euler:
0.3 / 3.0), and DNa02 R to 0.17. **`--integrate exact` is the default from here**, for the reason that it is what the
paper's model does and the Euler engine was not; every number in the record before this line was measured on the
Euler engine, and the sections that matter most (the constants, 09-17 08:58; the floor; the walking command; the state
pace; the feeding state) keep their ordering under exact but not their values. **the oracle now has two versions:**
v1 pins `--integrate euler` and keeps reproducing the pre-refactor script bit for bit (the port's history); v2 freezes
today's `pair.py` (`world/oracle/pair_oracle_v2.py`) on the exact engine with the defaults of record and `--walk 100`,
four deterministic configs, and every change from here must reproduce it bit for bit or say why. the README's caveats
gain a line: the Euler results are the record's past, not its present.

**the comparator, read graded (11:11 PDT; `vread`: a population's mean membrane per chunk; `--goal-wheel-v`; the exact
engine).** PFL3's membrane, left minus right, averaged over each 100 ms chunk, against the heading error: correlation
-0.72 (goal 200) and -0.65 (goal 35), a spread of 0.26-0.28 mV per chunk, and no shot noise, because there are no
spikes in it. the comparator's output is in the cell's voltage the way it is in life. on the wheel at 5 deg per mV with
two seconds of smoothing: he turns to the goal (165 deg off to 11 in the first ten seconds) and overshoots to 121, and
the error oscillates through the run (27 % within 30 deg overall, 68 % in the last quarter); the goal at his starting
heading: 32 %, wandering. lag and gain, not noise: a smoothed signal smoothed again, against a flow wheel that turns
him five degrees a chunk. the gain and the smoothing are being set (two runs), labelled as the readout's, since the
signal itself is now the cell's.

**menotaxis, in stretches (11:26 PDT; the null point measured with the bump present: +0.28 / +0.22 mV, the bias the
fits had found; 20 deg per mV, half a second of smoothing; 120 s; `docs/figures/menotaxis.png`).** the goal at 200 with
him facing 35: within 30 deg of it 41 % of the run (6-27 % on every earlier attempt); he turns from 165 deg off to
-10 in twenty seconds, holds for thirty, is knocked off, and holds again from 80 to 100 s. the goal at 35, where he
starts: 64 % of the first quarter and 72 % of the third within 30 deg, and 0-2 % of the quarters between. what takes
it from him is the rim, where the touch reflex outranks every channel, and what makes him slow to return is the
saddle at 180 deg, where the comparator's torque is zero. **so the loop from sky to body is closed, the way a fly does
it, on stand-ins where the physiology is graded:** the ring holds his heading from the sun; a goal sits in the
fan-shaped body; PFL3 compares them in its membrane; the difference turns him. every stand-in is labelled and tuned
(ExR1 400, ring 30, goal 100, 20 deg per mV, a null point), and the honest measure of it is 41 % and 34 %, not a
lock. the wrong null point (the bump absent during calibration, +0.52 mV) made it worse than none, which is worth
a line: a calibration is only as good as the state it is taken in. the residual bias (+0.16 to +0.23 mV over the
runs) says the null drifts with the walk; a slow adaptation of the baseline is the next readout item, and in the
dish, without a rim to hit, the number should be cleaner.

**the same loop in the dish (11:31 PDT; `--world arena`, the same stand-ins and gains):** 9 % and 18 % within 30 deg, at
the wall 51 % and 75 % of the run. in a dish the rim is the whole perimeter, he is a wall-follower by sight and by
touch, and the wall reflex outranks the comparator whenever he is on it, which in a dish is most of the time. this is
not a contradiction of the garden result but its condition: menotaxis in life is measured on a ball or in an arena
too large to reach the wall, and a fly that does reach one pauses rather than abandons its heading. so the goal loop
holds where he is free and loses where the wall owns him, in both worlds; the picture in `docs/figures/menotaxis.png`
is the honest statement of it. the next physiology for this is PFL2, the forward drive that in life gates walking on
alignment (Westeinde 2024), which would let the goal survive a wall by stopping him at it instead of dragging him
along it. the readout stand-ins stay as they are, tuned and labelled; the goal loop closes end to end.

**PFL2 as the walking gain (12:22 PDT; `--pfl2-walk`: PFL2's mean membrane, its two ends measured in calibration with
the goal ahead and behind, mapped to a gain on the walking command, 0.15 when fully off-goal, 1 when aligned;
Westeinde 2024: PFL2 drives forward walking when heading matches the goal).** first, a sign the wiring gave and the
paper did not [withdrawn 13:55: the paper says the same; see the bridge offsets]: PFL2's membrane is -3.00 mV with the goal ahead and -2.29 behind, more depolarised when he points
*away*; the stand-in maps the measured ends regardless, but the anatomy says PFL2's bridge inputs sit differently
from PFL3's than my imposed goal map assumes (PFL2's PB and FB offsets differ by half a turn in life), which is a
thing to read off its glomerulus labels next. the runs, 120 s, against the controls without it:

| goal | with PFL2 gain: within 30 deg | standing | at the rim | control: within 30 deg | standing |
|---|---|---|---|---|---|
| 35 (where he starts) | **64 %** (quarters 48 / 62 / 94 / 54; error never past 56 deg) | 63 % | 69 % | 34 % (64 / 0 / 72 / 2) | 4 % |
| 200 (165 deg off) | 38 % (51 / 3 / 59 / 41) | 14 % | 62 % | 41 % (53 / 32 / 34 / 47) | 4 % |

**holding improves, acquiring does not.** with the goal already held, the gain turns the wall from a drag into a
pause: he stands at it instead of following it, keeps his heading through the stop, and the goal survives the whole
run (the control lost it for two quarters of four). with the goal far off he is no better, because off-goal he is
*meant* to slow, and the flow wheel and the rim still own the turn. that is the shape Westeinde's flies have too:
PFL2 is the gas, PFL3 the wheel. the next thing is not a gain but the geometry: PFL2's own bridge offset from its
labels, so the stand-in stops assuming PFL3's.

**what nate saw (13:07 PDT; the goal-35 run with the PFL2 gain, in the viewer):** "he slowly walks along, some pauses
to look around and continue, hits the wall... and doesn't turn away from it like usual. he presses against it and gets
caught in the corner of the garden, facing outward the whole time." that is the stand-in doing what it was told. the
goal is a fixed compass heading, 35 degrees, and the garden has a rim: walk at 35 long enough and you reach the
north-east corner, where the comparator says keep pointing at 35, which is into the wall; PFL2 says you are pointed
right, so the walk gain is high and he keeps pushing; and the touch reflex, which owns the wheel only on contact
frames, turns him sideways for a frame and the goal channel, at 20 deg per mV, turns him back. the pauses are PFL2
idling him when the reflex has knocked him off the goal. so: not a broken navigator, an obedient one with a goal that
knows nothing about walls. in life a fly holds a menotaxis heading for minutes and then switches (Green 2019), and a
wall is a reason to switch; the next stand-in item is the goal as a state that yields (a new heading after N seconds
of contact), labelled, which is also what turns "hold one heading" into "explore by headings". the viewer gets a
compass panel first, so this is visible rather than inferred (`compass_wedges`, `compass_pfl`, the goal and the sun
are saved into garden episodes from this commit).

**the goal that yields (13:45 PDT; `--goal-switch 3`: after three seconds of continuous contact, a new heading drawn
uniformly; the compass, the goal and the comparator are saved into the file and the viewer draws them).** first attempt:
zero switches in 107 s at the rim, because "contact" was a collision event and a fly standing still against a wall,
which is what PFL2 makes him do there, is never pushed by it; contact is now his body within 2 cm of the boundary.
then, 180 s, seed 12, against the fixed goal nate watched:

| | fixed goal (120 s) | the goal yields (180 s) |
|---|---|---|
| in a corner | 54 % | **4 %** |
| standing | 66 % | 13 % |
| at the rim | 66 % | 59 % |
| walked | 5.9 m | 32.2 m |
| goal switches | 0 | 31 |

the corner is gone and he walks again; the rim is not gone, because a heading drawn uniformly points back into the
wall half the time and the wall-following holds him until the next switch, and 31 switches in three minutes is a
fly changing its mind every six seconds where life holds a heading for minutes. so the next refinement is the one
a fly makes: the new heading drawn from the half-circle facing away from the wall he is on, with five seconds of
patience. labelled, as the goal state is.

**the inward draw (13:50 PDT; `--goal-switch 5`, the new heading from the half-circle facing away from the wall):** 16
switches (11 s per heading), corner 11 %, standing 18 %, walked 29 m, **at the rim 57 %**, within 30 deg of the current
goal 21 %. no better than the uniform draw on the rim (59 %), worse on holding. so an inward goal does not get him
off a wall: with the goal pointing into the garden he still spends 15-28 s runs on the rim, which means at the wall
the goal channel loses to the flow wheel and the touch reflex, and possibly to PFL2 idling him (its sign in this map
is the paper's inverted, 13:07, and an idle fly at a wall with an inward goal is what an inverted gas would produce).
the corner is solved and the rim is not, and the next thing to look at is not another gain but PFL2's own bridge
offset from its labels, because if its map is half a turn from PFL3's, the gas has been off when it should be on.
`world/compass/yield3_g35.npz` is the run to watch with the compass panel.

**the bridge offsets, from the labels (13:50 PDT; column minus wedge, per cell, from the instance names):** PFL3, 24
cells: +66 deg on the left, -65 on the right (mean 359, concentration 0.40 because the sides cancel). PFL2, 12 cells:
**182 deg**, concentration 0.84. PFL1: 2 deg, 0.77. **two corrections to this morning's record follow.** (1) PFL3's
comparator is the +/-65: the same goal read from two vantage points a quarter-turn apart, so the difference between
the sides is the sign of the error; my single goal-map offset of -1 deg was the average of the two, and the
comparison worked because the anatomy carried the shift, not the map. (2) PFL2's bridge input is half a turn from
its goal column, so PFL2 peaks when he faces *away* from the goal, which is what the calibration measured (-2.29 mV
behind, -3.00 ahead), and which is what Westeinde 2024 report: PFL2 signals the size of the heading error and the fly
slows and turns when it is large. i had the paper backwards at 13:07 ("inverted from the paper"): the cell was right,
the stand-in's mapping of the measured ends was right, and the note was wrong. withdrawn. and the rim (57 % with a
yielding goal) is not the gas either: it is the flow wheel winning at a wall, thigmotaxis, which real flies do in a
dish 90 % of the time (`docs/BENCHMARKS.md`), and which is why menotaxis is measured in open arenas. the corner was
the bug; the rim is the fly.

**anemotaxis through the compass, first attempt (14:40 PDT; `--goal-wind 4`: while a fruit whiff is on either antenna
the goal heading is upwind, held four seconds after the last whiff; the downwind start of 09:12; three seeds each;
nate: "do behaviours hold up or evolve with more complete sensory inputs?").** neither arm reaches the fruit. the
control (wind ignored): closest 0.68-0.90 m, in the plume 22-66 % of the run. the wind arm: the goal is upwind 62 % of
the run in 8-11 surges, closest 0.56-0.63 m, in the plume 16-24 %, and **during every surge his heading error grows**
(95 deg off at a surge's start, 120-176 at its end): he turns away from upwind. the comparator's raw left-minus-right
during surges is +0.16 mV where the geometry (d = c - a sin err, 11:20) predicts -0.03: the bias c is ~0.2 mV larger
in this run than the null point measured at its start, and the goal's signal amplitude is 0.3 mV. a comparator whose
offset drifts by most of its own signal steers by the drift; the residual bias noted at 11:26 is now the result. so
the answer to nate's question so far is: the compass, the goal and the gas hold up; the readout's bias does not.
the knob with physiology behind it is the goal drive (doubled, so the signal outgrows the bias) before any adaptive
baseline, because an adapting null would also subtract a real sustained error. running.

**the goal drive doubled (14:46 PDT; `--goal-hz 200`, the wind arm, three seeds):** a circle. the goal stays upwind
the whole run (one surge), he never leaves the plume envelope (100 %), never comes closer than 0.71 m, and rotates at
117 deg/s, every seed, with PFL3's left cells 0.43 mV above the right. doubling the goal doubled the bias, because the
bias *is* asymmetric goal input onto a mirror pair, and a comparator with a constant offset commands a constant turn.
the wiring: PFL3 R carries 166 excitatory synapse-units per cell to PFL3 L's 191, 0.87x; PFL2 186 to 216. the cord's
lesion in miniature (14:53 yesterday), on the two cells the whole loop turns on. so the fix is the one that category
gets, scoped: `--mirror PFL3,PFL2` (the pair's inputs normalised to their mean, `wiring.mirror_normalise` with a
named-type scope), with the null point still calibrated after it. running, at the ordinary goal drive.

**the comparator pair mirrored (14:51 PDT; `--mirror PFL3,PFL2`: each cell's inputs scaled to the pair's mean, factors
0.94 / 1.07, none clipped; the wind arm, three seeds):** the bias is gone from the run, PFL3's raw left-minus-right
averaging -0.001, +0.005 and +0.003 mV. and he still turns away in surges (closing in 3 of 11, 3 of 13, 2 of 12) and
rotates at 45-55 deg/s, because the null point, measured at the start on a standing fly with the goal ahead, reported
-0.26 mV, and the channel subtracted a bias that no longer existed. the calibration that was the crutch for the hole
became a bias once the hole was mended. so with the pair normalised the null goes (`--goal-null off`); one fix per
problem. running.

**anemotaxis through the compass (14:58 PDT; the comparator pair mirrored, no null point, the goal set by the wind while a
whiff is on his antennae and for four seconds after; the downwind start; three seeds; `docs/figures/anemotaxis.png`):**

| seed | first surge: heading error | on the fruit at | fed | closest | net rotation |
|---|---|---|---|---|---|
| 10 | 98 deg -> (on the fruit before the surge ends) | **6.4 s** | 8.0 s | 0.38 m | +6 deg/s |
| 11 | 98 -> 28 deg | **5.9 s** | 8.0 s | 0.38 m | +0.6 deg/s |
| 12 | 105 -> 53 deg | never | | 0.48 m | +6 deg/s |

the control, the wind ignored, the same start: 0 of 3, closest 0.68-0.90 m. this morning's wind on Johnston's organ
through the noisy channel (09:12): 0 of 3, and he arced out of the plume. **two of three walk up the plume onto the
fruit in six seconds and eat**, with every piece of the last two days used in one behaviour: the ring holding his
heading from the sun, the goal set by a sense instead of a dice, PFL3 comparing them in its membrane, PFL2 gating
the walk, the halt and the feeding state at the fruit. the path there went through three wrong readouts, each one
recorded: a null point that drifted, a doubled drive that doubled the bias into a metronome, and a null that became
a bias once the pair was mended; the fix that held was the physiological one, the comparator pair's traced input
asymmetry (0.87x) normalised as the cord's was. so nate's question of 14:20, whether behaviours hold up or evolve with
more complete input: they evolved. a fly who could not hold a heading arced out of the plume; a fly who can walks up
it. the compass configuration of record for the garden, all opt-in and labelled: `--ring --goal <deg> --goal-switch
5 --goal-wind 4 --goal-wheel-v 20 --goal-ema 5 --pfl2-walk --mirror PFL3,PFL2 --goal-null off`.

**the room with her at the corrected constants (12:14 PDT; seed 3, 300 s, 0.185 / 0.275,
running steering and pace, adapting bristles, DNa02 wheel, thermo off):** pace 0.23 (sd 0.13),
48.9 m walked; wall time 31% (13 visits, longest 21.5 s); five encounters within 0.5 m (at 5,
60, 98, 156 and 221 s, the fourth lasting 11 s), 71 frames of contact with her; his P1
11,130 spikes (touch: 8,863 wall and pillar contact frames); her P1 0 and her DN output 46
per chunk at 0.275 (she is quiet at Shiu's constant on her own tissue, as the 22:55 odour
test predicted). the viewer: `world/viewer_room185.html` (local, stride 4) and the room
artifact (v5, stride 6).
- **Shiu's constants, from the code not the paper:** rest/reset -52, threshold -45,
  tau_m 20 ms, tau_syn 5, refractory 2.2, delay 1.8, w_syn 0.275 (a free parameter),
  Poisson 150 Hz. our 150 Hz optic-lobe cap is Shiu's default, not a measurement.
- **the rightward lean is not physiology** (yaw is linear in R-L through the whole
  range, zero at zero; Rayshubskiy 2020). recommended: running per-side baseline
  (~2 s) before differencing. our still/plateau offsets were fixed, not running.
- **DNa02 dynamic range ~150 spikes/s** (Yang 2024: stride modulation 15 Hz = 10%);
  yaw 3-10 deg/s per Hz; ours is the conservative end.
- **leg MNs: slow MNs fire ~30 Hz standing** (Azevedo 2020), force per spike spans
  0.1 / 1 / 10 uN by class; counting spikes equally misreads speed.
- **P1 is not the persistent one** (Jung 2020): persistence is pCd, minutes long; P1
  output is threshold-graded (aggression low, song high; Hoopfer 2015). and LC10a's
  gain is P1-dependent (Hindmarsh Sten 2021): with fixed gain he will not track her.
- **population-rate target:** PNs 4.6 Hz, KCs 0.1 Hz spontaneous (Turner 2008);
  central mean 0.5-5 Hz; above 10 Hz mean is a calibration failure.
- **bristles are slowly adapting** (Corfas & Dudai 1990): ~200 Hz onset, tau ~30 ms
  to a 10-25 Hz plateau, direction-gated (half a contact patch fires), plus seconds-
  scale fatigue. our 150 Hz hold is wrong in shape and size.
- **campaniform sensilla encode dF/dt** (Zill 2024; Harris 2022): burst on loading,
  adapt out mid-stance, a subpopulation on unloading. the 15% tonic load term is the
  wrong shape.
- **hook FeCO axons are presynaptically inhibited during walking** by a 9A
  interneuron under descending walk command (Dallmann 2025); claw, club, hair plates
  are not. our proprioceptors are Poisson sources that ignore their membrane, so this
  gate cannot act on them in this engine: it has to be applied at the drive.
- **halteres do not oscillate while walking** (Hall 2015): silent is right.
- **gait:** speed is step frequency (Wosnitza 2013), stance ~ v^-1, swing 20-45 ms,
  step period floors at ~60 ms (16 Hz max, not 10); tetrapod below 5 BL/s, tripod
  above 10. sensory delay 5-15 ms, motor 20-40 ms: the loop is ~one swing.
- **an efference copy lands directly on JO-A/B** (Cheong 2024), and a warning: single
  afferent-loop silencings in life give small-or-null effects, so a big effect from
  closing one loop in the sim is probably a bug.
- **song constants check out:** IPI 35 ms (29 Hz), sine 140-170 Hz, her JO 100-300 Hz.

## performance (20:40 PDT, `world/fastlif.py`)

nate asked what bounds the sim (CPU: the LIF step) and whether a spike on it was worth
it ("drastically improves our guess-and-check solutioning"). done tonight, not tomorrow:

- **the LIF step, compiled (numba).** the edge walk for propagation (was a ragged
  gather + `np.add.at`) and the membrane update (decay, integrate, refractory, floor,
  threshold) fused into one pass; delay line, APL, Poisson receptors, STD, plasticity
  stay numpy. same arithmetic order and float32 constants: **spike-for-spike identical
  to flysim.step, 1,000/1,000 steps on both brains** (17,225 and 130,179 spikes). 0.31
  ms/step vs ~2 ms on an idle box (8 threads beat 16; the kernels are memory-bound).
  `FastFlyBrain` is a drop-in subclass; `pair.py --numpy-engine` keeps the original.
- **the ommatidium shader, compiled.** one ray per iteration, same primitives (sky,
  ground, drum, walls, pillars, spheres): 0.26 ms vs 5 ms per 42k-ray render, max
  difference 2e-8.
- **readout counting** once per chunk from accumulated spike indices instead of 25
  fancy-index sums per brain per step (exact by construction).
- **room, 10 s, seed 2, idle box:** numpy engine 53 s -> compiled 21 s; a 60 s episode
  191 s (bristle-driven stretches spike more). the flyvis chunk is now the largest
  single piece (8 ms per eye per chunk, GPU) after the two brains' steps.

## the transplant learns from flyvis (19:24 PDT, `seam/distill.py`)

student-teacher: the transplant (flyvis dynamics on the MaleCNS per-cell optic lobe,
left eye: 40,180 cells incl. virtual R1-R8 and CT1 compartments, 933k edges) is trained
to reproduce flyvis model 000's responses, cell type by cell type, column by column,
on synthetic clips (moving bars, gratings, expanding discs, drifting dots; 40 frames at
100 fps) rendered on the flyvis lattice and mapped to our columns by the derived map.
learnable: 604 pair strengths, 65 time constants, 65 biases, 65 per-type input scales
(all log-parametrised where positive). loss: MSE of rest-subtracted activity over 49
shared types. adaptation (300 ms) on. gradients flow through an edge-list gather-
scatter (the sparse product's backward wanted 6 GB). 3 s per clip on the 1650, 0.8 GB.
**400 steps: loss 0.12 -> 0.009.** the physiology moved moderately: strengths median
0.80x flyvis (IQR 0.59-1.01), time constants 0.84x, input scales 0.82x. nothing about
looms is in the objective; the loom is the exam.

**distilled model 1, examined (19:26 PDT).** a loading bug first (dividing by flyvis
strengths that are exactly zero gave NaN weights; fixed: zero pairs stay zero). then:
finite, stable, ON pathway alive (Mi1 mod 0.36, Mi4 0.80, T4a 0.49, T4b 0.34), **OFF
pathway collapsed** (T5a/T5b mod 0.01, 70-90% of cells silent), and no direction
preference in the T4 means (|shift| < 0.04). the ball reads polarity-shaped as before.
the MSE on rest-subtracted activity is dominated by the large-response types; T5's
small responses barely register, and without a rest anchor a type can go dead for
free. retrains: (2) 60 grey frames before each clip + a rest anchor to flyvis's rest +
a small activity penalty; (3) as (2) with each type's loss divided by the teacher's
response variance for that type, so T4/T5 count as much as Mi4.

**distilled models 2 and 3, examined (20:10 PDT).** both bring the OFF pathway back:
T5a/T5b cells with rest > 0 are 74-99% (model 1: 10-30%), T5 modulation 0.06-0.13
(model 1: 0.01). neither sharpens direction selectivity. DS in the mean shift is nil
(|DS| <= 0.03 for every T4/T5 subtype, both eyes) and DS in the temporal modulation is
the ratio the untrained transplant already had (T4a L: +az 0.467 vs -az 0.349; R the
mirror, 0.449 vs 0.594; ~1.3:1 where flyvis is ~3:1). model 2's loss settled at 0.019
(rest-anchored MSE), model 3's at 0.48 (per-type-normalised; not comparable). **verdict:**
imitation by MSE on this wiring keeps every type alive and reproduces the magnitudes
but does not make T4/T5 more direction-selective than the per-cell wiring is with
flyvis's per-type strengths. the remaining levers are (a) ensemble-averaged flyvis
T4/T5 as the seam input and (b) training the transplant on the optic-flow task itself
(flyvis's objective) rather than on flyvis's outputs. neither started.

## choices, labelled

1. **orientation** of our hex grid onto theirs. not in the data. calibrated by biology:
   LPLC2 is loom-selective (klapoetke 2017); the map where loom >> recede is the map.
   the left eye may need the mirror of the right's.
2. **gain / A_REF.** flyvis activity is unitless. T4/T5 are graded in life; a rate is
   a stand-in. swept in calib.py.
3. **both eyes see the same render.** fine for a midline loom. lateral stimuli need a
   per-eye render.
4. **the LIF's own optic lobe stays at 0 Hz.** only flyvis-driven cells fire. driven
   cells with zero rate are held silent (engine behaviour).
5. **one flyvis model (000).** the ensemble of 50 exists; average later.
6. **right hemisphere is more completely traced** (known bias). R-eye readouts run
   higher. compare within eye.

## next

- calib.py result -> fix map + gain. then five stimuli x 5 seeds on the fixed map
  = the loom result, with a shuffle control (flyvis columns permuted) after.
- seam v1 depth: T4/T5 for the lobula plate is right; for the lobula (LC4 path), test a
  high-pass / transient transform on Tm drive vs STD with a smaller U vs leaving LC4 out.
- flash control stays in every table from now on.
- per-eye mirrored render for lateral stimuli; then left vs right loom -> DNa steering.
- ensemble average over the 50 flyvis models.
- write it up.

## the ocelli are not in the table (16:30 PDT; nate asked how we would find the ocellar photoreceptors, and whether a label could go upstream)

the method was going to be the sensory fingerprint: a cell that receives almost nothing, enters by the ocellar nerve, is predicted
histaminergic, and synapses onto the typed ocellar interneurons (OCG / OCC, 46 cells). the table has an `entryNerve` column, and
39 cells enter by `ON`: 8 typed vertex bristles (BM_Vt_PoOc), 25 untyped cells with the same targets (DNge132, ANXXX027,
DNg48, AN09B023: bristle afferents by connectivity), 2 `cb_sensory_tbc`, and 4 DNx02 (sensory_descending, unknown_sensory:
120-175 input synapses in the volume, 7,000-10,000 outputs, onto AN06B025 and GNG288 above all). **none of the 39 makes a
single synapse onto an ocellar interneuron.** the 23,320 synapses onto OCG / OCC come from typed brain cells (PS053, aMe_TBD1,
GNG311, other OCG). so the retinal input to the ocellar pathway, which in life is made in the ocellar plexus under the cuticle
of the vertex, was never in the imaged volume, and there is no photoreceptor to find or label. (transmitters, consensus_nt:
OCG01a/c/f glutamate, the other OCG acetylcholine, OCC02a/b unclear.)

what that leaves: a labelled stand-in on the interneurons. in life the ocellar L-neurons sit depolarised in the dark and
hyperpolarise to light, because the photoreceptors are histaminergic (the same wall the compound-eye R7/R8 hit on 09-18), so
the stand-in is OCG rate proportional to one minus the sky light over him, labelled, an afternoon. moved from "research" to
"an afternoon" in `docs/TODO.md` §S. the four DNx02 in the ocellar nerve are the one open question worth an upstream ask:
what they are is not in the table either. and on nate's upstream question in general: a simulation response is not evidence
of identity (it is the table read back); a connectivity fingerprint is, and that is the kind of proposal FlyWire took in the
open. how the MaleCNS annotators take proposals is not yet known here.

## his antennae were two body lengths apart (16:44 PDT; nate asked whether a millimetre between a fly's antennae is enough to read a plume gradient, and whether ours factors the geometry)

**in life.** the antennae sit ~0.35 mm apart on a ~0.7 mm head. that is enough to lateralise: Gaudry 2013 (odour on one
antenna turns the walking fly toward it; asymmetric PN release), Taisz 2023 (lateral-horn cells that subtract left from right
ORNs), Kadakia 2022 (odour *motion* sensed from the delay of a packet between the two antennae). but a concentration gradient
across 0.35 mm of turbulent plume is mostly noise, and the walking fly's strategy is whiff timing plus wind (Alvarez-Salvado
2018, Demir 2020): the antennae answer "odour now?", the wind answers "which way".

**ours.** `Body.antennae()` put the tips 0.1 m ahead and 0.15 m to each side: 0.30 sim m = 4.5 mm apart at 15 mm per m,
twelve times a fly's, nearly two body lengths (2.4 mm), straddling a plume that is 3.75 mm wide at the source. so every
bilateral smell number in this record was measured on a head that does not exist, and the 09-18 finding that smell
lateralises nothing at the steering readouts was a finding about the wiring, not the geometry (the input asymmetry was
huge and still steered nothing). the whiff state is one coin per source shared by both antennae, so the between-antenna
delay is zero by construction: odour-motion sensing is impossible here at any spacing until sensory time is finer than the
10 ms frame. the error hid in the units: 0.15 looks like nothing until it is multiplied by fifteen.

**the change** (one): `--antennae real` (0.08 m ahead = the front of the head, 0.012 m to each side = 0.35 mm; `wide` is the
old geometry, the default until the flip). the anemotaxis batch of 14:57 re-run on it, UV layer on for the viewer, three seeds,
with its control (no wind goal):

| run | walked | in plume | first on the fruit | feeding | bilateral asymmetry \|L-R\|/(L+R), mean |
|---|---|---|---|---|---|
| windn (wide) s10 / 11 / 12 | 17.2 / 22.2 / 13.7 m | 19 / 23 / 11 % | 6.4 / 5.9 / never | 7 / 7 / 0 % | 0.21 / 0.37 / 0.43 |
| windr (real) s10 / 11 / 12 | 2.5 / 6.4 / 19.7 m | 98 / 22 / 40 % | 11.2 / 10.7 / 8.0 s | 7 / 7 / 7 % | 0.035 / 0.019 / 0.046 |
| ctl (wide) | 13.6 / 15.4 / 12.0 m | 34 / 66 / 22 % | never | 0 | |
| ctlr (real) | 12.2 / 12.7 / 14.4 m | 100 / 29 / 25 % | never | 0 | |

the bilateral asymmetry falls ten-fold to a few percent, which is what a real head sees. **anemotaxis holds: 3/3 on the
fruit (8-11 s; wide 2/3 at 6 s), each eats for 8 s, control 0/3.** the result did not lean on the fake gradient; if anything
the honest head is better, because with both antennae in the plume the whiff is on him more of the time.

**what the honest head exposed.** after eating, windr s10 walked 0.0 m in the remaining 90 s and s11 3.4 m (wide s10 walked
13.5 m away). at the source the whiff never ends, so the wind goal never releases: s10 stands pressed against a grass stalk a metre downwind of the
fruit for the last 90 s (speed 0.0, touch on every frame, the goal held at 197 deg = upwind by the whiff), the goal-switch
firing every 5 s of contact (18 switches) and the wind goal overriding it on the next whiff. the wide
head sat with one antenna half out of the plume and got released by chance. in life the sated fly ignores the food odour
(satiety lowers ORN sensitivity through sNPF, Root 2011; the fed fly leaves). the FeedingState already has the `full` flag; the
wind goal should read it. next change, its own run against this one.

## the ocellar stand-in, built (16:51 PDT; nate: "let's do it soon, before we forget this small discovery")

the photoreceptors are not in the volume (above), so the channel starts at the interneurons. built, all opt-in and labelled:

- `Garden.sky_light(x, y, h)`: the sky brightness each of the three ocelli sees, 0..1. the median ocellus looks along his
  heading, the laterals 60 deg to each side, all upward: the leaf shade sampled 0.3 m out along each line of sight (the leaves
  are 0.8-1.4 m up), times the sky, plus the sun's disc when it is in that ocellus's field (27 deg azimuth, 48 deg up, boost
  0.3 as the raytracer has it), normalised so 1 = open sky facing the sun, ~0.7 = open sky facing away, ~0.4 = under a leaf.
  a geometric stand-in for three lenses that in life each see ~90 deg of sky with no resolution (Krapp 2009).
- `receptors.OcellarL`: rate = dark_hz x (1 - light). the sign is life's: the ocellar L-neurons are depolarised in the dark
  and hyperpolarised by light because the receptors are histaminergic (Hardie 1989; Wilson 1978 on the locust; Krapp 2009
  review). they are GRADED in life; a rate here stands in for a membrane level, the R7/R8 wall dressed better. dark_hz 40 is a
  chosen number, not a measured one, and the label says so.
- `pair.py --ocelli on [--ocelli-hz 40]`: the 46 OCG / OCC cells by side (23 L, 23 R), the left cells from the mean of the
  left and median ocelli, the right from the right and median; cells added to the driven set. the floor holds them at 0
  otherwise.
- the episode logs the three values per frame (`ocelli`, n x 3) and the viewer draws them as three discs on the vertex above
  his eye, lit by what each sees (the placeholder comment in `replay_app.py` said "nothing identifies or drives the three
  ocelli yet"; now something does).

smoke test (4 s, his start beside the fruit, real antennae): sky light median 0.47, left 0.51, right 0.88 (the sun is off
his right); OCG / OCC at 16-23 Hz, more on the left (darker side), as built. the run against its own rest (`--ocelli off`,
three seeds, the config of record of the hour) is queued behind the wind and thermal arms: the GPU holds seven flyvis
processes and no more (two seeds of the satiety-gate arm died of CUDA out-of-memory under nine; rerun queued).

what to measure: does a light-level channel change what he does at all (time under the leaves, pace in the sun patch, the
stops in the shade nate noticed). where OCG / OCC project (looked up while the arms ran): 124,799 output synapses, 65 % onto
bodies with no annotation row (fragments and untyped cells), 16 % onto descending neurons, above all DNp20, DNpe017, DNp22,
DNge107, DNp18 (the DNp set that serves flight and the neck in life), 2 % onto cervical-nerve neck motor neurons (CvN6 / CvN7),
11 % central-brain intrinsic. so in life's terms this is a flight and head-stabilisation channel; a walking fly may show
nothing, and that would be the result.

## two senses switched on, one per arm (17:04 PDT; nate's rule of the day: every implemented sense on unless the run says why not)

writing the README's "what senses are on" table caught that the wind rows on his Johnston's organ (`--wind on`) were OFF in
every anemotaxis run: the compass goal read the wind direction from the world, a stand-in for the JO channel, not the channel.
and the thermal field was at rest by a reason that had expired (warmth does not steer him at these constants; it does drive
his legs, and that is a thing flies do). each on as its own arm against windr (real antennae, 16:42), three seeds, 120 s:

| arm | on the fruit | first on it | walked | feeding | switches |
|---|---|---|---|---|---|
| windr (baseline) | 3/3 | 11.2 / 10.7 / 8.0 s | 2.5 / 6.4 / 19.7 m | 7 % each | 18 / 13 / 1 |
| windj: `--wind on` (JO-C/E rows fed by the world's wind, plus the compass goal) | 2/3 | 8.7 / never / 12.1 s | 17.5 / 13.2 / 16.4 m | 7 / 0 / 7 % | 0 / 4 / 0 |
| therm: `--thermo field` (the sun patch, the shade, the water) | 3/3 | 8.6 / 6.9 / 8.2 s | 18.4 / 19.9 / 19.8 m | 7 % each | 1 / 2 / 3 |

anemotaxis holds under both: the JO rows on his antennae do not disturb the compass goal (2/3 is within three seeds of 3/3;
s11 came within 0.55 m and missed), and the thermal field sends him up the plume as reliably as its absence and faster. both
arms also leave the fruit after eating, where two of the three baseline seeds stood pinned against it; neither arm is the
fix for that (the satiety gate is, its own arm, below), but both change the brain's input enough that the pin's chance
dependence shows. **both go into the default flip.** what `--wind on` still lacks is the wind of his own walking on his
aristae, and what the thermal field lacks is a measurement of what it does to him beyond the fruit (the shade and sun-patch
table follows).

the shade and sun-patch table (all runs, position every 100 ms, the garden's own fields):

| run | mean speed | moving | in shade | in the sun patch | T at him, mean / max |
|---|---|---|---|---|---|
| windr s10 / 11 / 12 | 0.02 / 0.05 / 0.16 m/s | 12 / 28 / 83 % | 9 / 11 / 17 % | 0 % | 24.8 / 25.2 C |
| windj | 0.15 / 0.11 / 0.14 | 79 / 60 / 72 % | 7 / 7 / 8 % | 0 % | 24.9 / 25.1 |
| therm | 0.15 / 0.17 / 0.17 | 79 / 84 / 83 % | 7 / 6 / 11 % | 0 % | 24.9 / 25.2 |

so the thermal-field arm is honest but nearly empty: starting beside the fruit and walking up its plume, he never enters the
sun patch and the temperature at his antennae stays within 0.4 C of 25 for the whole run. the field was on; the fly was not
in it. the arm says "the thermal rows at their field values do not break anemotaxis," not "warmth does something." what
warmth does to him needs a run that starts him in the patch, or a patch on his way (the record's warm-corner runs of 09-17
are the last word on that: kinesis, no taxis). the baseline's two pinned seeds show as 12 % and 28 % moving.

**correction (17:12), in place:** the thermal arm was not a change at all. `--thermo field` sets `room.thermal`, the ROOM's
warm corner, which the garden's own `temperature()` (sun patch +6 C, shade -3, water -2) never reads. under `rest` and `field`
alike the hot and cooling rows read the garden's field at his antennae. so the garden's thermal field has been on in every
garden run since 09-17 under the name `rest`, the "parked" reason of 16:12 was a misreading of my own flag, and the therm arm is
three more seeds of the baseline configuration (the runs are not deterministic: flyvis differs call to call). read that way:
six baseline runs, two pinned; the satiety gate three, none. the README's senses table is corrected with it. the thermo row
in the flip is `rest` (rows on; the room uniform at 25 C, the garden its own field), and `field` keeps its meaning for the room.

## the sated fly leaves (17:10 PDT; `--wind-sated`, one change against windr; two seeds re-run after CUDA out-of-memory under nine jobs)

the pin (16:42): with real antennae both are in the plume near the fruit, the whiff never ends, the wind goal keeps him
pushing upwind after he is full (into a grass stalk, in s10, for the last 90 s of the run), and the goal-switch's inward
heading is overridden on the next whiff. the physiology: the sated fly ignores food odour (sNPF lowers ORN sensitivity with feeding, Root 2011; the fed fly
leaves). the FeedingState already carries `full` (satiety at 1, re-armed below 0.5); `--wind-sated` makes the wind goal
ignore the whiff while it is set.

| run | on the fruit | first on it | feeding | walked after 30 s | distance from the fruit at 120 s | switches |
|---|---|---|---|---|---|---|
| windr s10 / 11 / 12 | 3/3 | 11.2 / 10.7 / 8.0 s | 7 % each | 0.0 / 3.4 / 15.9 m | 1.02 / 1.49 / 1.90 m | 18 / 13 / 1 |
| winds s10 / 11 / 12 | 3/3 | 9.8 / 9.9 / 11.6 s | 7 % each | 11.6 / 11.8 / 9.6 m | 4.44 / 3.45 / 4.15 m | 6 / 5 / 4 |

**he walks up the plume, eats for eight seconds, and leaves, three of three** (the baseline stood pinned in two of three).
the gate is one line and a flag, labelled with its source, and it is the second state-dependent gain in him after the
feeding latch itself: satiety now changes what an odour means, which is what it does in a fly. adopted; in the flip.
(figure: `docs/figures/sated_leaves.png`.) the fuller version, the ORN gain itself lowered by satiety so the whole olfactory
side sees less rather than one goal ignoring it, is the next step on the smell row; it needs the plume to reach a readout
first, which it still does not.

## the default flip (17:26 PDT; nate, 16:50: "default implemented senses on rather than remember to give them to him for each run")

the argument, from the day: a sense that has to be remembered is off half the time. thermo was "parked" by a reason that
turned out to be my misreading of my own flag; the wind rows were off in every anemotaxis run and nobody noticed until a
README table was written from the flag list. so from this commit the config of record is the fly, and a command line only
says what is missing. flipped in `world/pair.py`, each measured as its own arm today before it moved:

| flag | was | now | measured |
|---|---|---|---|
| `--antennae` | wide (4.5 mm apart) | real (0.35 mm) | 16:42, anemotaxis 3/3 |
| `--wind` | off | on (JO-C/E rows fed by the world's wind; garden only) | 17:03, 2/3 |
| `--thermo` | off | rest (hot / cooling rows on; the room uniform at 25 C, the garden its own field) | on since 09-17 under this name |
| `--wind-sated` | (absent) | on (satiety gates the wind goal) | 17:09, eats and leaves 3/3 |
| `--ocelli` | | stays off until its run lands (below) | |

stays opt-in on purpose: the compass stand-ins (`--ring`, `--goal*`) because they are labelled models, not senses; her
(`--no-female`) because a male-only question is a question; `--uv`, a viewer layer that reaches nothing in him.

and nate's question of 16:55, what the oracle is for if his senses move every few hours: it tests the engine, not the fly.
its four frozen runs say whether an edit to the loop, the integrator or a kernel changed anything not meant to change; the
fly they are pinned to only has to be stable, not current. v1 always pinned its own fly (old floor, old integrator, old pace)
and never minded a default. v2 read the defaults, which was a mistake of this morning; both lines now state every sense flag
explicitly (`--antennae wide --wind off --thermo off --ocelli off --wind-sated off`), so the flip changes neither reference
and no refreeze is needed. the oracle run after the flip is the test of that claim.

## the ocelli, run (17:35 PDT; `--ocelli on` against windr, three seeds; the oracle passed on the build first)

| run | on the fruit | first on it | walked | moving | in shade | mean sky light at him |
|---|---|---|---|---|---|---|
| windr (baseline) s10 / 11 / 12 | 3/3 | 11.2 / 10.7 / 8.0 s | 2.5 / 6.4 / 19.7 m | 12 / 28 / 83 % | 9 / 11 / 17 % | 0.80-0.83 |
| therm (= baseline, three more seeds) | 3/3 | 8.6 / 6.9 / 8.2 s | 18.4 / 19.9 / 19.8 m | 79 / 84 / 83 % | 7 / 6 / 11 % | 0.79-0.81 |
| ocel: `--ocelli on` | 3/3 | 6.5 / 6.3 / 7.2 s | 18.8 / 23.6 / 23.3 m | 79 / 85 / 84 % | 14 / 5 / 20 % | 0.79-0.81 |

the light-level channel breaks nothing. he reaches the fruit a second or two sooner and walks a little further than the six
baseline runs, and at three seeds that is a hint, not a result: the mean sky light he saw is the same in every run (0.8; the
plume runs along open ground), so the channel was near-constant at ~8 Hz on the interneurons, and what could have changed
him is a tonic input to DNp20 / DNp22 / DNpe017 (their main descending targets), which in life serve flight and the neck. a
walking fly on open ground is the wrong test for the ocelli, and the record said so before the run. what would be a test:
a run that crosses shade (the light on him drops to ~0.4 under a leaf, the interneurons to ~24 Hz), and the ocellar cells
logged (the run of record of 17:35, `world/record/garden_0919_s10.npz`, logs OCG01a/b/d, OCG02c, OCC02b, DNp20, DNp22).

**adopted as a default** (`--ocelli on`; the garden only, the room's stimulus is 1.0 = 0 Hz), by the rule of the day: a
labelled sense that is implemented is on unless a run says why not. no oracle rerun is needed for this flip: both oracle
lines pin `--ocelli off`. what stays written on it: the photoreceptors are outside the imaged volume; the L-neuron sign is
life's; the 40 Hz is chosen; the cells are graded in life.

oracle after the flip (17:46 PDT): v1 and v2, old and new constants, seeds 3 and 4: differing arrays none, eight of eight. the
defaults moved and the engine's references did not, which is the claim of the flip section. (the ocelli default was set after
this run; both lines pin it off, so it cannot change them either.)

**where the ocellar channel goes, measured (17:50 PDT; 15 s garden runs, seed 10, defaults, the descending targets logged):**

| | DNp20 | DNp22 | DNpe017 | OCG01a |
|---|---|---|---|---|
| ocelli off, wind rows off | 150 Hz | 4.4 | 21 | 0 |
| ocelli off | 156 | 9.3 | 12.5 | 0 |
| ocelli on (sky light ~0.8: the interneurons at ~8 Hz) | 160 | 24 | 58 | 17 |

so the stand-in reaches its descending targets: DNpe017 x4.6 and DNp22 x2.6 from 46 cells at 8 Hz, which is the wiring
(124,799 output synapses) doing what the table says. DNp20 is at 150 Hz with everything off: that is not the ocelli, it is
the walking fly's floor or the command (DNg100 -> ?), and it is a number to look at another day (a descending neuron at
150 Hz is a hot cell by any physiology). in the 180 s run of record the ocellar cells sat at 8.7 Hz and followed the sky
light he saw with r = -0.9 (OCC02b) to -0.5 (the OCG01s), as built: he crossed shade (light 0.41 at the darkest).

## a bug in the per-chunk hook (17:50 PDT; found because the run of record wandered)

the 180 s run of record (everything on, the ocellar cells logged) never surged, never yielded, never reached the fruit, and
the viewer said "no compass arrays". the cause: `pair.py` gave the episode ONE per-chunk hook, chosen by precedence,
`--log-pre` over `--log-types` over the compass, so any run that logged cells had no compass hook at all: no EPG wedge log,
no goal yield at walls, no wind goal, no PFL2 walk gain. fixed: all hooks that apply run, in that order.

what it touches in the record: every run made with `--log-types` AND `--goal-switch` or `--goal-wind`. the anemotaxis
batches (anemo4-8) logged no cells, so their numbers stand. the morning's goal and compass analyses (`experiments/goal.py`,
`experiments/compass.py`) ran on logged cells with a fixed goal and no switch, so the goal drive (registry rows) and the
graded readout (`vread`, in the episode) were live and the hook's only lost job was the wedge log, which those scripts do
not use. the 17:52 run of record is moved out of the way (`garden_0919_s10_nohook`), and the run of record is being made
again on the fixed script. the oracle runs after it (its runs have no hooks; the edit is still an edit).

**oracle FAIL (17:59 PDT), and why:** the hook fix of 18:05 named the three hook functions in one list, and each is defined only
under its own flag, so every `pair.py` run without `--log-pre` died on a NameError at setup: the oracle's four port arms
included, hence FAIL, and the remade run of record with them. fixed (the list looks the names up and keeps what exists),
smoke-tested both ways, the run of record launched a third time, the oracle again behind it. an oracle FAIL from a crash is
still a FAIL and it goes in the record as one.

## the run of record, evening of 09-19 (18:14 PDT; `world/record/garden_0919_s10.npz`, 180 s, seed 10)

everything on, by default now: real antennae, the JO wind rows, the thermal rows on the garden's field, the satiety gate,
the ocellar stand-in; plus the compass configuration (`--ring --ring-exr 400 --ring-er 30 --goal 90 --goal-hz 100 --mirror
PFL3,PFL2 --goal-null off --goal-wheel-v 20 --goal-ema 5 --pfl2-walk --goal-switch 5 --goal-wind 4`), feeding and satiety,
the UV layer for the viewer, and the ocellar cells and their descending targets logged. from the anemotaxis start, downwind of
the fruit:

- on the fruit at 8.1 s, eats for 8 s, leaves; ends 4.1 m from it. 1 surge, 7 goal switches, 16.7 m walked, moving 51 % of
  the three minutes; the darkest sky he saw 0.41 (under a leaf).
- the ocellar cells at 8.3-8.5 Hz, following the sky light with r = -0.80 (OCC02b, 16 cells) and -0.4 to -0.5 (the OCG
  pairs), as built. their targets: DNpe017 at 48 Hz, DNp22 at 11, both correlated with the light at -0.3 to -0.4 through
  the interneurons; DNp20 at 131 Hz regardless (the hot descending neuron noted at 17:58, not the ocelli's doing).

the viewer: `uv run python world/replay_app.py world/record/garden_0919_s10.npz --scale 2` (the three ocelli sit over his
eye; `c` cycles the eye's channel through the UV retina; the compass panel is live; the map has its 10 mm bar).


oracle after the hook fix (18:22 PDT): PASS, eight of eight.

## is the feeding latch a puppet? (18:56 PDT; nate asked whether we ever found a true signal that he has started feeding, and whether he has a proboscis)

he has a proboscis: 107 head motor neurons in the table (`cb_motor`), 67 of them proboscis motor (`pm`: MN1-MN13 and the
MNx set, Schwarz 2017's muscles; MN9 is the rostrum protractor, the extension itself), 20 neck, 13 antennal, 7 rostrum.
and the path from his tarsi is drawn: the 719 leg gustatory cells make no direct synapse on a proboscis motor neuron or on
DNg105, but two synapses out, 143 of their targets reach the proboscis motor neurons (8,355 synapses, through gnathal relays
GNG014, GNG125, GNG271, GNG391) and 40 reach DNg105 (394 synapses, through the ascending neurons AN04A001 and AN08B032).

**what the latch is.** `FeedingState` (09-18): sugar on the tarsi -> a scalar of ours latches "feeding", which DRIVES DNg105
(the halt) at 45 Hz and silences the withdrawal reflex; satiety fills and releases. the record labelled it "modelled as
what it does". nobody had asked whether his own wiring, given the sugar, would halt him or extend the proboscis by itself.

**the measurement** (12 s runs, seed 10, walking command on, proboscis motor neurons and DNg105 logged; rates after 2 s):

| | DNg105 | MN9 | MN1 / MN7 / MN10 / MN11D / MN12D / MN3L / MN4a | DNa02 | pace | moving |
|---|---|---|---|---|---|---|
| beside the fruit (no sugar) | 0.0 Hz | 0.0 | all 0.0 | 9.7 | 0.30 m/s | 100 % |
| standing on the fruit, sugar on the tarsi (719 leg GRNs at 26 Hz), NO latch | 0.0 | 0.0 | all 0.0 | 9.1 | 0.30 | 100 % |
| on the fruit, the latch (`--feeding 3`) | 45.7 (ours) | 0.1 | all 0.0 | 5.6 | 0.11 | 37 % |

so, plainly: **at these constants his own wiring does nothing with sugar on his tarsi.** the proboscis motor neurons stay at
zero, the halting neuron stays at zero, he walks off the fruit at full pace. the halt during feeding is ours, and the
proboscis never extends at all, latch or no latch. the latch is in the puppet class, and the label was right to say so; the
difference from the jar is that this record says it, and that the path he would need is in his table and can be asked
where it dies (the relays, logged next).

**correction (18:57), in place, before the ink dried:** the relays run showed the leg taste cells at 0 Hz after 2 s in the
"standing on the fruit" arm: with the walking command on and no latch, he was pushed out of the fruit and walked off it
within the first second, so the sugar was on his tarsi for a moment, not for the run. the table above measured a fly who
left, not a fly who stood on sugar. the sentence "at these constants his own wiring does nothing with sugar on his tarsi" is
not yet earned. re-measured with the walking command off (`--walk 0`), standing on the fruit vs beside it, the taste cells
themselves logged so the stimulus is verified, not assumed; the result follows. (the relays in the walked run: AN04A001 14 ->
19 Hz, AN08B032 0.8 -> 1.4, the gnathal relays and DNg77 at 0 in both.)

**the standing run (19:00) measured nothing either, and the reason is nate's point.** with the walking command off he is
pushed out of the fruit to its edge (0.38 m from the centre: the fruit's radius plus his), sugar on his tarsi, touched on
the left; and the bristle withdrawal reflex, the one the latch silences, turns him and walks him off the skin within a
second (pace 0.1 m/s with no command; the taste cells at 0 Hz after 2 s). a fly lands ON its food and stays; ours meets a
collider and flinches from it like a wall. so "sugar on the tarsi for twelve seconds" cannot be produced by the world as it
stands, only by pressing him into the fruit with the walking command, which the latch was built to allow. this is a physics
limit before it is a wiring one (`docs/TODO.md` §P: walkable tops), and the two are confounded in every feeding result so far.

to ask the wiring question anyway: `--taste-hold sugar`, a TEST stimulus (never a default; labelled in the flag), holds the
taste on his tarsi every frame after the world's contacts, standing beside the fruit, against the same run with nothing held.

**the held-taste pair (19:02 PDT; 12 s, standing beside the fruit, seed 10; rates after 2 s):**

| | leg GRNs (719) | AN04A001 (6) | AN08B032 (2) | GNG014 / 125 / 271 / 391 (11) | MN9 (2) | MN11D / MN12D (7) | DNg105 (2) |
|---|---|---|---|---|---|---|---|
| nothing held | 0.0 Hz | 17.4 | 1.6 | 0.0 | 0.0 | 0.0 | 0.4 |
| sugar held | 24.0 | 32.6 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 |

the stimulus is verified this time (the taste cells at 24 Hz). **the first synapse carries: the ascending neuron AN04A001
doubles, 17 -> 33 Hz** (AN08B032 falls to 0: inhibited on the way). **the second does not:** the four gnathal relays that
feed the proboscis motor neurons stay at 0, MN9 and the pump at 0, the halting neuron at 0. so sugar on his tarsi reaches
his brain and stops one synapse short of every motor consequence, which is the 0.185 mV wall at the second synapse, the
same wall the plume hit (ORN -> PN carries, PN -> LHN does not, 09-16) and the anterior visual pathway hit (09-18).

the honest statement, now earned: at these constants his own wiring does nothing with sugar on his tarsi beyond one
ascending neuron. the feeding latch is a puppet in exactly the sense of the piece, labelled, and this is where the string
attaches. what retires it is written in §P: the relays carrying (a question of the second-synapse gain, which is a
question about the whole brain, not about feeding), MN9 read as "feeding", and a fruit he can stand on.


oracle on the `--taste-hold` flag (19:20 PDT): PASS, eight of eight.

## the taste brief reframes the wall (19:37 PDT; `docs/physiology/taste_per.md`, an opus agent; its three claims verified against the tables here)

1. **i was driving the wrong cells.** the "sugar on the tarsi" row (`pair.py`, since 09-17) drives `LgLG*` + `claw_tpGRN`,
   719 cells. verified: the 669 `LgLG*` are `vnc_sensory`, local to the leg neuropils, and the 50 `claw_tpGRN` are labellar
   taste pegs (`cb_sensory`, entering by the maxillary-labial nerve), not leg cells at all. the tarsal cells that reach the
   brain are `LgAG1..9`, 76 cells, `sensory_ascending` (MANC SAch01/02), and they were never in the drive set. the 212 direct
   synapses from the 719 onto the gnathal relays all come from the 50 pegs; the 669 leg cells make **zero** onto GNG014 /
   125 / 271 / 391, MN9, the pump or DNg105.
2. **the sugar label exists, in our own `type` column.** Tastekin et al. 2026 (Cell, the pan-CNS gustatory connectome on
   this dataset): `LgLG4` (43 cells) = Gr64f + Ir56b, the tarsal sugar GRN; `LgAG2` (11) = Gr61a ascending appetitive;
   `LgAG1` (25) = Gr33a ascending bitter; labellar `LB3c` (23) = Gr64f sugar, `LB3a` (17) = ppk28 water, `LB3b` (11) = Ir56b
   low salt. `LgLG3` (162, the largest class in our row) has no molecular identity anywhere. (the `receptorType` column is
   pheromone-only.)
3. **MN9's silence was anatomy before it was the constant.** two hops onto MN9: from the labelled tarsal sugar set 5
   synapses via 2 relays; from labellar `LB3c` 313 via 26 relays; Tastekin reports the tarsal sugar path to the feeding
   motor neurons is ~7 hops. and Shiu 2024's extension result used 21 **labellar** GRNs; MN9 first fires at 30 Hz of GRN
   drive in his model, ~80 % of max at 100 Hz; w = 0.275 was set with that in view. our held taste was 24 Hz: below his
   threshold with the right cells, on the wrong cells.

the arithmetic, from the brief (v_th 7 mV above rest, tau_m 20, tau_syn 5, 0.185 mV): one volley needs ~240 coincident
synapses, and AN04A001's best cell receives 336 leg synapses, so at 24 Hz it sits at ~107 % of threshold: exactly the one
cell that doubled. everything else on the path sits at 0-30 %.

also from the brief, to check against the record: **DNg105 is not one of Sapkal 2024's halting neurons** (those are
Foxglove, Bluebell, BRK); it has no published function, is GABAergic here, with a courtship-side input profile and zero
taste input. our measurement that driving it halts the cord (09-18, 821 -> 469 /s) stands as a measurement; the source
attached to it does not. the brake row in `docs/SENSES.md` and TODO §2 gets a "source under audit" mark.

so the puppet verdict of 19:02 stands, and the wall moves: not "the second synapse cannot carry at 0.185 mV" but "we
pressed every key but the sugar key, below the rate the model needs". the arms the brief asks for run tonight: labellar
`LB3c` (23) vs tarsal `LgLG4 + LgAG2` (54) vs the legacy 719, each held at 100 Hz standing beside the fruit, MN9 and the pump
logged; then a 10-200 Hz dose-response on MN9 with the right cells (the Shiu replication); then 0.275 mV as the single
variable; then "feeding" read from MN9.

**the right key, pressed (19:39 PDT; `--sugar-cells labellar|tarsal|legacy --sugar-hz 100 --taste-hold sugar`, 12 s standing beside the fruit, seed 10, rates after 2 s):**

| arm | the driven cells (measured) | AN04A001 (6) | AN08B032 | GNG014/125/271/391 | MN9 (2) | MN11D / MN12D | DNg105 |
|---|---|---|---|---|---|---|---|
| legacy 719 at 100 Hz | LgLG4 75 Hz (inside the set) | 57.8 | 0.0 | 0.0 | 0.4 | 0.0 | 0.0 |
| tarsal: LgLG4 + LgAG2 (54) | 75 / 77 Hz | 20.0 | 1.8 | 0.0 | 0.0 | 0.0 | 0.2 |
| labellar: LB3c (23) | 77 Hz | 19.2 | 3.4 | 0.0 | 0.1 | 0.0 | 0.2 |

**MN9 does not fire for the labelled sugar cells at 100 Hz either**, labellar or tarsal, and the pump stays at zero. (the
four gnathal relays logged here are the ones the taste pegs reach; LB3c's own 26 relays onto MN9 are other cells, being
looked up now.) so the input is right and the rate is Shiu's, and the extension still does not happen: the remaining
variables are the constant (0.185 here, Shiu's 0.275), the dataset (MaleCNS vs FlyWire), and the dose. queue items 3 and 3b
run next as single variables: 0.275 mV on the labellar arm; 200 Hz on the labellar arm at 0.185. the legacy arm's AN04A001
at 58 Hz is the 669 local leg cells' 336-synapse convergence, as the brief computed; it goes nowhere.

the labellar path, looked up: LB3c's 23 cells make 29,780 synapses onto 11,522 cells; first hop by type: LB3c itself
(1,737), GNG038 (1,149), GNG042 (890), GNG215 (766), GNG232 (519). the cells that drive MN9 and the pump hardest are four
GNG467 (430-480 synapses each onto MN9 / the pump; together with a few untyped bodies they are 72 % of MN9's 6,991 input
synapses), and each of them receives only 7-20 synapses from LB3c directly. so sugar-to-extension here is three hops or more
(LB3c -> GNG038 / 042 / 215 -> ... -> GNG467 -> MN9), and what Shiu's model did at 0.275 mV was carry a chain, not a synapse.
the 0.275 arm and the 200 Hz arm are the test of whether this dataset carries the same chain at either constant.

## HIS OWN WIRING EXTENDS THE PROBOSCIS (19:41 PDT; the single-variable arms on the labellar sugar cells, 12 s standing beside the fruit, seed 10, rates after 2 s)

| arm | LB3c (23, measured) | AN04A001 | MN9 (extension, 2) | MN11D (pharyngeal pump, 3) | MN12D (4) | DNg105 |
|---|---|---|---|---|---|---|
| 100 Hz at 0.185 mV (19:39) | 77 Hz | 19.2 | 0.1 | 0.0 | 0.0 | 0.2 |
| **200 Hz at 0.185 mV** | 125 | 15.5 | **19.1** | 0.0 | 0.0 | 0.1 |
| **100 Hz at 0.275 mV (Shiu's constant)** | 76 | 48.2 | **5.1** | **185.9** | 0.0 | 0.0 |

**MN9 fires.** at our constant it needs a 200 Hz drive on the labellar sugar cells (the Poisson gate gives 125 Hz measured);
at Shiu's it fires at 100 Hz and the pharyngeal pump motor neurons run at 186 Hz, which is a fly swallowing. so the chain
(LB3c -> GNG038 / 042 / 215 -> ... -> GNG467 -> MN9 / the pump) carries in the male dataset, through his own wiring, with the
key pressed hard enough. three hours ago the record said "the proboscis never extends"; it never had the right input.

what this is and is not: it is the first motor consequence of a taste that came from him and not from a scalar of ours.
it is not yet feeding in the garden: the garden's sugar row still drives the legacy cells at 26 Hz; the tarsal set at 100 Hz
did not fire MN9 (its path is ~7 hops, Tastekin 2026), and in life it is the labellum that touches the food, which he has
no geometry for. and DNg105 stays at zero in every arm: the halt during feeding is still ours, and the brief says its
source is wrong anyway. the constant question is now live and sharp: 0.185 was set from KC sparsity; the pump at 0.275
and its silence at 0.185 is a physiological fact to weigh it against (a fed fly pumps). in flight: the dose-response at
0.185 (30, 50, 150 Hz) and the tarsal set at 200 Hz.

**the dose-response (19:43 PDT; LB3c held, 0.185 mV, 12 s, seed 10; the drive is nominal, the rate measured):**

| nominal drive | LB3c measured | MN9 | the pump (MN11D / MN12D) | DNg105 |
|---|---|---|---|---|
| 30 Hz | 28 Hz | 0.1 | 0 | 0.1 |
| 50 | 43 | 0.1 | 0 | 0.2 |
| 100 | 77 | 0.1 | 0 | 0.2 |
| 150 | 103 | **5.8** | 0 | 0.0 |
| 200 | 125 | **19.1** | 0 | 0.1 |
| tarsal LgLG4 + LgAG2 at 200 | 122 (LgLG4) | 0.1 | 0 | 0.1 |

so at 0.185 mV the extension motor neuron has a threshold near 90-100 Hz of labellar sugar firing and rises steeply above
it; Shiu's model at 0.275 has its threshold at 30 Hz of GRN drive. the shape is his, the threshold three times higher, and
the pump never runs at our constant. the tarsal set does nothing at 200 Hz: its path is the long one. what this says about
0.185: it was set from the mushroom body's sparsity, one measurement; the taste chain is a second, independent measurement
of the same constant, and it says the wiring under-carries by about a factor of three relative to the model whose
constants we cite. the decision is nate's (docs/ASK.md); the honest options are (a) keep 0.185 and let the fly be quiet, (b)
0.275 with the KC sparsity re-measured, (c) the KC calibration re-examined, since it may have been the outlier.


oracle on the sugar-cells and sugar-rate flags (19:55 PDT): PASS, eight of eight (read from the log before it was written here).

## the constant, measured twice (22:05 PDT; nate's answer in docs/ASK.md: (c) first, then (b) with 0.275 authorised)

**(c) the Kenyon-cell calibration, re-made as a script** (`experiments/kc_sparsity.py`: the standing brain with the floor, 2 s
warm-up, then ORN_DM1-DM5 (258 cells) at 150 Hz for 1 s; the fraction of the 4,064 KCs that fire at least once, and their
mean rate; exact engine, seed 0):

| w (mV) | KCs firing | mean KC Hz | | the taste chain at the same w (LB3c at 100 Hz): AN04A001 | MN9 | pump MN11D |
|---|---|---|---|---|---|---|
| 0.185 | 6.8 % | 1.10 | | 19.2 Hz | 0.1 | 0 |
| 0.220 | 10.8 % | 2.21 | | 31.0 | 1.4 | 0 |
| 0.250 | 15.4 % | 3.72 | | 37.8 | 0.9 | 0 |
| 0.275 | 18.4 % | 5.22 | | 48.2 | 5.1 | 186 |

life: 5-10 % of KCs per odour (Turner 2008, Honegger 2011). two things to say before any decision:

1. **the sparsity number is protocol-soft.** this morning's inline measurement gave 3.9 % at 0.185 and 12.6 % at 0.275;
   tonight's script gives 6.8 % and 18.4 % with a floor-first warm-up and a fixed odour set. same engine, same constant,
   a factor of ~1.6 from the protocol. it is a weak calibration, and it was the only one we had.
2. **the two calibrations disagree, and neither is a clean instrument.** by sparsity, 0.185 sits in the band and 0.275
   is far out of it; by the taste chain, MN9's threshold at 0.185 is ~100 Hz of sugar firing against Shiu's 30, and the
   pump runs only at 0.275. the mushroom body has its own gain control in the wiring (APL feedback) and is expected to
   resist w; the taste chain is a few feedforward relays and is expected to be sensitive to it. so they measure different
   things, and the honest reading is that no single w satisfies both on this dataset with this engine.

so (b) is not taken tonight. the pump's 186 Hz at 0.275 is looked at below before it is called a swallow.

**the pump at 0.275, looked at (22:06):** MN11D per second: 0, 0, 157, 190, 190, 189, 189, 188, 189, 190, 189, 188. it snaps from
nothing to a flat 190 Hz in the third second and never moves again, while MN9 fires in bursts (19, 16, 0, 3, 0, 4, 0, 8 ...)
and the sugar cells and AN04A001 are steady. MN11D's 21,103 input synapses come from gnathal cells (GNG334 4,441, GNG019
2,127, GNG001 2,082, MNx01 1,523, GNG467 1,499 ...), a recurrent neighbourhood; a plateau that saturates and never adapts is
a loop that tipped over, not a fly swallowing (pumping is rhythmic, bursts at a few Hz). so at 0.275 on this dataset the
gnathal circuit has an attractor that the exact engine at 0.185 does not enter, and the sparsity is out of its band as
well. **recommendation to nate (docs/ASK.md): keep 0.185.** the taste chain's threshold at 0.185 is ~100 Hz of sugar-cell
firing, which is a physiological rate for sugar cells on food (Gr5a ~100-150 Hz at 100-500 mM sucrose; the chemo brief's
65 Hz is the 100 mM value); so the honest reading of tonight is not "the constant is too low" but "he needs to be on the
food, with the labellum, at a real sugar concentration", which is the physics item and the labellar geometry (§P). 0.22 is
noted as a labelled test constant, sparsity 10.8 %, MN9 at 1.4 Hz from 100 Hz, in case the feeding readout needs it;
it is not adopted.

## the DNg105 audit (23:10 PDT; queue item 3d, from the taste brief's note)

where the record picked it: the motor review (09-18) listed the descending neurons heaviest onto leg motor neurons by synapse
count (DNg105 8,736 leg / 304 wing); the 09-18 dose runs found DNg74_a and DNg105 turn the legs *down* against the walking
command (0.8x and 0.57x the floor), and DNg105 became the brake because it was measured to halt the woken cord, in both
seeds, below the standing tonus. the record wrote at the time: "which of Sapkal 2024's halting types these are by name is
an audit item." the brief answers it: DNg105 is not one of Sapkal 2024's named halting neurons (Foxglove, Bluebell, BRK),
has no published function, is GABAergic in the table, with a courtship-side input profile and zero taste input. so the
brake is a **measured** halting neuron of this model, not a **named** one, and the attribution "Sapkal 2024" attaches to
the idea (halting is active, brain-side) and to AN19A018, not to DNg105. labels corrected in `docs/SENSES.md` and TODO.
the measurement stands; the citation moves.

## the ocelli, crossing shade (23:14 PDT; `world/ocelli/`, 60 s, three seeds each, start (2.0, -1.1) heading north under open sky toward the leaf at (2.0, 0.2); the compass config of record, feeding on; ocellar cells and their descending targets logged)

| arm | walked in 60 s | in shade | sky light min / mean | OCC02b (16) | DNpe017 (2) | DNp22 (2) | corr(OCC02b, light) |
|---|---|---|---|---|---|---|---|
| ocelli off, s10 / 11 / 12 | 3.6 / 3.6 / 5.6 m | 11 / 0 / 39 % | 0.47-0.70 / 0.65-0.84 | 0 | 28 / 30 / 28 Hz | 2.0 / 0.6 / 3.1 | |
| ocelli on, s10 / 11 / 12 | 8.6 / 7.7 / 7.7 m | 27 / 10 / 10 % | 0.41-0.48 / 0.68-0.78 | 11.9 / 8.6 / 9.7 | 57 / 50 / 54 | 15.1 / 10.5 / 12.2 | -0.91 / -0.89 / -0.84 |

the light at him changed this time (0.41 under the leaf, 0.8 in the open), and the ocellar cells followed it, r -0.84 to
-0.91, as built. their targets moved: DNpe017 doubles, DNp22 five-fold. and **he walks about twice as far with the channel
on, three of three** (7.7-8.6 m against 3.6-5.6 m). speed in the sun 0.12-0.14 vs 0.06-0.12 m/s; in shade mixed (s10 0.20
vs 0.06, the others equal). so a light-level channel does something to a walking fly here, and the something is more
walking. what it is not yet: a *light* effect as opposed to a *tonic* one. 46 cells at 8-12 Hz onto DNpe017 could be a
constant push that has nothing to do with what the ocelli see. the control that separates them: the same channel held at
a constant sky light (0.8, the open-ground value) so the cells fire at their open-sky rate whatever is over him. in flight.

**the constant-light control (23:18 PDT; `--ocelli-light 0.8`, the channel pinned at its open-sky rate whatever is over him):**

| arm | walked in 60 s | OCC02b | DNpe017 | DNp22 |
|---|---|---|---|---|
| off | 3.6 / 3.6 / 5.6 m | 0 | 28-30 Hz | 0.6-3.1 |
| on, the garden's light | 8.6 / 7.7 / 7.7 m | 8.6-11.9 (following the light) | 50-57 | 10.5-15.1 |
| on, light held at 0.8 | 7.2 / 6.8 / 5.7 m | 7.8 flat | 47-52 | 9.7-11.5 |

**mostly tonic.** the channel held constant gives most of the extra walking (5.7-7.2 m against 3.6-5.6 off), and the real
light adds 7.7-8.6, which at three seeds overlaps the constant arm (7.2). so what the ocellar stand-in does to him today is
a tonic push on DNpe017 and DNp22 from 46 cells at 8-12 Hz, and the light-specific part, if there is one, is inside the
noise of three seeds. the record says that and nothing more: a light-level channel that changes his walking amount, not
yet a light effect. the honest next step is not more seeds; it is a run in which the light changes a lot (dusk, or a
long stretch under the canopy) and the cells' rate doubles rather than moves by 30 %. `--ocelli-light` stays as the control
flag. the ocelli remain on by default: they break nothing and the push is small.


oracle on the `--ocelli-light` control flag (23:32 PDT): PASS, eight of eight, read from the log first.

## the constant sweep (2026-09-21 08:55 PDT; TODO §Q 3f, criteria stated before the run: KC sparsity in 5-10 %, the sugar-to-MN9 threshold, no gnathal runaway; `experiments/kc_sparsity.py` and `world/wsweep/`, LB3c held at 100 and 150 Hz nominal, 12 s, seed 10)

| w (mV) | KCs firing | MN9 at 100 Hz (LB3c 77 measured) | MN9 at 150 Hz (LB3c 103) | MN11D pump |
|---|---|---|---|---|
| 0.185 (09-19) | 6.8 % | 0.1 | 5.8 | 0 |
| 0.200 | 8.4 % | 0.2 | 8.4 | 0 |
| 0.220 | 10.8 % | 1.0 | 12.5 | 0 |
| 0.240 | 13.7 % | 2.2 | 13.5 | **plateau 186 Hz at 150 Hz drive** |
| 0.260 | 16.4 % | 10.8 | 60.2 | **plateau 188 Hz at both** |
| 0.275 (09-19) | 18.4 % | 5.1 | | plateau 186 |

what the sweep says, plainly:

1. **the runaway is the ceiling, and it is 0.24.** the gnathal loop that feeds the pharyngeal pump tips into a flat ~188 Hz
   plateau at 0.26 for any drive and at 0.24 for a strong one. above that the constant is not available to us at all.
2. **below the ceiling the constant is not the lever for the taste chain.** MN9's threshold sits near 100 Hz of measured
   labellar sugar firing at every w from 0.185 to 0.22; what w changes is how hard MN9 fires above it (5.8 -> 12.5 Hz at
   150 Hz nominal), not whether. the lever is the input: a fly standing on food, with the labellum, at a real sugar
   concentration, drives those cells at 100-150 Hz in life. that is the physics item, not the constant.
3. **sparsity crosses the band's edge at 0.22.** 0.185 and 0.20 sit inside it; 0.22 is at the top; above that, out.

so by the three stated criteria, every constant from 0.185 to 0.20 passes and 0.22 is marginal, and none of them changes
what he can do. **the constant of this build stays 0.185:** it is inside every criterion, it is what the whole record was
measured on, and moving it to 0.20 would buy MN9 three hertz at the cost of a refreeze day. this is Shiu's method on our
network with the floor on, and it lands where we already were. the question is settled by the sweep, not by preference,
and it goes into the settled list. if the physics puts him on food and the chain still needs more, the sweep says where
the room is: up to 0.22, and no further.

## the climb, built (2026-09-21 08:58 PDT; nate: "flies land on their food and spend quite some time there"; TODO §P physics, §Q 4)

first, the collider jumps nate remembered: not in any current run. the largest frame-to-frame move in the run of record,
the anemotaxis batches, the HS runs and the oracle's room runs is his own step (0.003-0.005 m); the zooming was older
code. so the contact fix is a guard, not the change. the change is height:

- `Body.z`, the height of his feet. `Garden.surface(x, y)`: the fruit and the stone are spheres resting on the floor,
  walkable domes with z = zc + sqrt(r^2 - d^2); a fly walks up any slope, so there is no slope limit.
- `--climb on` (opt-in until measured): inside a dome's footprint his feet follow the surface, there is no push-out and
  no touch (a surface underfoot is not a wall to his bristles), and on the fruit his tarsi are on the skin, so taste is
  sugar wherever he stands on it, not only while pressing into its side. `off` keeps the record's colliders.
- his eye rises with him: the raytracer's viewpoint is 0.5 + z (the top of the fruit is 0.52 m up, so from there he sees
  over the grass). pitch along the slope is not done (the eye's rotation is yaw only; a pitch would be a seam change).
- `pose_z` saved per frame; the viewer raises his viewpoint from it.

smoke (4 s, starting at the fruit's edge facing it, feeding on): he walks up to the top (z 0.52), stands at its centre, and
the latch holds for every frame. in flight: the anemotaxis config of record with `--climb on`, three seeds, against the
09-19 winds arm; and the oracle (the default path adds 0.0 to the eye height, which is bit-exact).

**the climb, measured (09:14 PDT; the anemotaxis config of record, three seeds, 120 s, `--climb on` vs the 09-19 winds arm):**

| arm | first on the fruit | height reached | feeding | walked / after 30 s | ends from the fruit | goal switches | frames touching |
|---|---|---|---|---|---|---|---|
| winds (colliders) s10 / 11 / 12 | 9.8 / 9.9 / 11.6 s | 0 | 8 s each | 15.0 / 14.7 / 12.6 m; 11.6 / 11.8 / 9.6 | 4.4 / 3.5 / 4.2 m | 6 / 5 / 4 | 12 / 21 / 9 % |
| climb (domes) s10 / 11 / 12 | 21.5 / 6.4 / 7.1 s | 0.44 / 0.51 / 0.52 m | 8 / 10 / 8 s | 20.6 / 21.6 / 19.2 m; 15.4 / 16.1 / 14.2 | 4.6 / 1.3 / 3.7 m | 4 / 0 / 2 | 11 / 7 / 3 % |

**he walks up the plume, climbs onto the fruit, eats standing on it, and leaves, three of three.** the top of the fruit is
0.52 m up and two seeds reached it; the goal-switch fires less because food is no longer a wall; he touches less and
walks further afterwards. one seed took 21 s to arrive (a detour), within what three seeds do. anemotaxis holds through
the physics change, and "on the fruit" is now a state of the world rather than a collision. **`--climb on` becomes the
default** (garden only; the oracle's room runs cannot see it). oracle on the edits: PASS, eight of eight.

what this unblocks, in order: the labellum as geometry (standing on food and stopped, the labellum is on the skin, the
labellar sugar cells fire at the food's concentration), feeding *read* from MN9 and the pump rather than imposed (the
latch's exit, §P), and the withdrawal reflex no longer needing to be silenced on food because food no longer touches him.

## feeding, read from him (2026-09-21 09:23 PDT; TODO §Q 3c, the latch's exit in §P; built on the climb)

the pieces, each labelled:
- **the labellum, as geometry.** on the fruit his labellum is on the skin (a fly walking over fruit dabs it), so the labellar
  sugar cells (`LB3c`, 23, Gr64f) fire at the food's rate: `--labellum-hz`, 200 Hz nominal, which the Poisson gate makes
  ~125 Hz measured, the top of what sugar cells do on strong sucrose in life. this is a stand-in for the extension itself,
  which his tarsal taste path does not drive (the long path, 09-19); it is in §P with that exit.
- **feeding, read.** `FeedingState(read="mn9")`: feeding is true while MN9, his proboscis extension motor neuron, fires above
  `--mn9-thr` (2 Hz per cell, smoothed over a second: single stray spikes latched it at first, six in 120 chunks, and one
  spike in 100 ms is not a meal). the halt while feeding is still the DNg105 drive (ours, §P) and satiety still fills and
  releases. so the causal order is now his: sugar cells -> three gnathal hops -> MN9 -> "feeding" -> the halt.

smoke (20 s, starting at the fruit's edge, the walking command on): at 150 Hz nominal (104 measured) MN9 fires 0-1 Hz on
the fruit with the cord walking, the read never latches, and he walks off in two seconds; at 200 nominal (125 measured)
MN9 runs at 8-26 Hz, feeding latches from it, he stands on the fruit at its top, satiety fills over eight seconds, and he
leaves when full. the pump (MN11D) stays at 0 at this constant, as the sweep said it would. the walking command matters:
in the standing sweep MN9 fired at 104 measured; on a walking cord it needs 125. the batch at the anemotaxis config
against the climb arm (latch) runs now, with the oracle.

**feeding read from him, measured (09:40 PDT; the anemotaxis config of record with the climb, three seeds, 120 s; `--feed-read mn9` vs the climb arm's latch):**

| arm | first on the fruit | MN9 on the fruit / off it | feeding | walked / after 30 s | ends from the fruit |
|---|---|---|---|---|---|
| climb, the latch (09-21 09:05) | 21.5 / 6.4 / 7.1 s | | 8 / 10 / 8 s | 20.6 / 21.6 / 19.2 m; 15.4 / 16.1 / 14.2 | 4.6 / 1.3 / 3.7 m |
| climb, feeding READ from MN9 | 9.6 / 7.6 / 14.4 s | 16.0 / 14.7 / 13.4 Hz on; 0.0 / 0.1 / 0.1 off | 8 / 9 / 8 s | 11.3 / 21.8 / 16.6 m; 7.8 / 17.6 / 13.4 | 1.3 / 1.5 / 3.8 m |

**three of three: he walks up the plume, climbs the fruit, his extension motor neuron fires at 13-16 Hz while he is on it
and not at all off it, the record reads that as feeding, satiety fills, he leaves.** the same behaviour as the latch, with
the first sentence of it his. oracle on the edits: PASS, eight of eight. **`--feed-read mn9` becomes the default.** what is
still ours, in §P: the halt while feeding (DNg105 driven by the state), and the labellum-on-food condition. what would take
the first: a halting path from taste that carries, which the tarsal path does not; or a stop read from the cord itself when
MN9 fires (the pause is a state in life, Bidaye 2020). what would take the second: the extension driven by the tarsal path,
which needs the long path to carry, which the sweep says the constant cannot give. both stay written.


**a slipped default (09:47 PDT):** the first remade run of record reached the fruit at 7.5 s, climbed it, and never fed: MN9 at 0 Hz on the fruit. the read was the default but the labellar rate was still 150 Hz nominal, at which MN9 does not fire on a walking cord (the smoke of 09:20 said so). `--labellum-hz` default is now 200, the value the batch was measured at; the run of record is being remade again. caught by the rule that the run of record is made on the defaults, not on the batch flags.

**seed 10 on the defaults, remade (09:55 PDT): a miss, recorded.** he reached the fruit at 7.7 s, spent 1.8 s within 10 cm of its edge and 0.5 s on the dome (z 0.28 at most), and walked on; the labellar cells fired for that half second and MN9 did not reach the read's threshold. no feeding in 180 s; ends 4.3 m away. the batch of 09:30 (three of three, seeds 10-12) stands as the evidence; this is one more seed on the same configuration and it grazed instead of climbing. the run of record is remade on seed 11 (the batch's 7.6 s feeder), and this file is kept beside it as the miss it was.

## the run of record, 09-21 (10:02 PDT; `world/record/garden_0921_s11.npz`, 180 s, seed 11, the defaults: real antennae, the wind rows, the thermal rows, the satiety gate, the ocelli, the climb, feeding read from MN9; plus the compass configuration, feeding and satiety, the UV layer, and the taste and ocellar cells logged)

- on the fruit at 7.0 s, 11.7 s on it in all, up to the top; MN9 at 13.5 Hz while on it and 0.0 off it; feeding read from
  that for 8 s; satiety fills; he leaves and ends 3.9 m away. 1 surge, 5 goal switches, 22.9 m walked, moving 67 %.
- he also climbed the stone at some point (height 0.83 m, the stone's dome), which the climb allows and nobody asked for.
- viewer: `uv run python world/replay_app.py world/record/garden_0921_s11.npz --scale 2`.

the day's ledger for him, the 21st: the constant settled by a sweep (0.185, with the runaway ceiling at 0.24 and the lever
shown to be the input), the climb (he stands on food), and feeding read from his own motor neuron. two stand-ins retired
from the feeding row of §P, two remain written there.

## the motor census (13:21 PDT; nate: "what other motor neurons do we have access to and is he firing them?"; 20 s, seed 11, the defaults, from the fruit's edge so he walks and feeds; all 191 motor types logged, grouped by the annotation table's subclass)

| muscle group | cells | Hz per cell, walking | Hz per cell, feeding | cells silent |
|---|---|---|---|---|
| front legs | 180 | 3.0 | 1.5 | 146 |
| middle legs | 60 | 3.3 | 1.1 | 33 |
| hind legs | 133 | 5.5 | 4.6 | 98 |
| abdominal | 201 | 4.2 | 3.2 | 75 |
| **wing** | 56 | **31.1** | **32.3** | 11 |
| neck (cord) | 20 | 15.4 | 13.5 | 2 |
| haltere | 16 | 7.1 | 5.0 | 8 |
| proboscis (head) | 67 | 0.13 | 0.65 | 55 |
| neck (head) | 20 | 13.5 | 11.0 | 1 |
| antennal | 12 | 6.9 | 7.8 | 4 |
| rostrum | 7 | 10.0 | 16.6 | 1 |

so: he has 708 motor neurons in the cord and 107 in the head, and the loudest of them are the wrong ones. **his wing motor
neurons fire at 31 Hz per cell while he walks and while he eats**, ten times his leg motor neurons, and his halteres' at 7;
a walking fly's wing and haltere motor neurons are silent. the record had this in view since the exact engine (09-19,
"the wing motor triples") and now it has the number. the legs carry the pace on a minority of cells (146 of 180 front-leg
cells silent). the neck runs at 13-15 Hz in cord and head, which a head-stabilising fly does. the proboscis set is quiet
except MN9 and the rostrum group, which rises from 10 to 17 Hz while he feeds: the extension muscles, as they should.

the wing artefact is the next diagnostic (queue 8b): which floor row or command drives the wing motor neurons. in flight.

## the wing artefact, traced (13:32 PDT; queue 8b; twelve 12 s arms, seed 11, the 56 wing and 16 haltere motor neurons logged, rates after 2 s)

| arm | wing MNs, Hz per cell | haltere |
|---|---|---|
| the defaults (walking, feeding) | 31.3 | 7.8 |
| no smell floor / no wind floor / no leg floor / no walking command | 31.7 / 31.5 / 33.2 / 32.7 | 6.9 / 7.4 / 7.8 / 6.3 |
| ocelli off / no taste floor / no thermal-humidity floor | 30.9 / 31.3 / 30.3 | 6.3 / 8.0 / 7.3 |
| the silent brain (no floor) | 36.1 | 7.7 |
| the wind rows off | 31.5 | 7.1 |
| vision only (no floor, no wind, no ocelli, no command) | 33.4 | 3.3 |
| **nothing driven at all** (the above and the seam's gain 0) | **31.7** | 0.8 |
| nothing driven, **membrane noise 0** | **30.9** | 0.5 |
| nothing driven, w 0.17 / 0.16 / 0.15 | 20.2 / 12.6 / 1.5 | 0 |

so no sense, no floor row, no command, no vision and no noise is the source: **with nothing driven and no noise the wing motor
neurons still fire at 31 Hz per cell.** the table says who: 80 % of their input is cord interneurons, and of the fourteen
strongest, two are hot: IN06B013 (4 cells, 62 Hz in the defaults, **39 Hz with nothing driven and no noise**) and dMS2
(20 cells, 23 Hz, 3 with nothing). IN06B013's targets are the flight motor: MNwm36, ps1, tp1, the DLMn power-muscle motor
neurons, the b1 / b2 basalar steering motor neurons. and in the defaults the whole song premotor network is up with it
(vMS12_a 65 Hz, IN11B004 63, vMS12_c 43, dPR1 31): the circuit that in life turns the pIP10 command into wing song, with
pIP10 itself at 0.

so the wings are driven by a **bistable loop in the flight / song premotor network of the cord**: once lit it stays lit
with no input and no noise, and its rate scales with the constant (31 Hz at 0.185, 20 at 0.17, 13 at 0.16, out at 0.15).
what lights it is the next question (the setup's calibrations drive bristles and command cells before the run; a wall
touch would do it too), and what would put it out in life is the thing the model does not have: the flight motor is gated
by a state, and a walking fly's is held silent. it is not a fly wanting to fly (nate's fair question); it is the flight
motor pattern running at a fixed rate in a fly standing on a fruit, because nothing in him can stop it.

**found (13:43 PDT).** three more arms, and one correction to the paragraph above: the loop is not self-sustaining. it is fed.

| arm | wing MNs | IN06B013 | dMS2 | cooling cells (VP3) | hot cells (VP2) |
|---|---|---|---|---|---|
| nothing driven, the brain reset, the setup's leftover drive (314 cells) and the engine's tonic current (97 MBONs) zeroed | 32.5 | 39 | | | |
| the same, **and the thermal rows off** | **0.9** | 2.2 | 0.0 | 0.0 | 0.0 |
| the defaults with `--thermo off` (the floor's thermal rows still on) | 31.0 | 68 | 22 | 74 | 32 |

the bare engine with a zero state, zero drive and zero noise fires nothing, and one kick of the four cells gives four spikes
and silence. what was never off in any "nothing driven" arm was the thermal rows: `--thermo rest` (the default since 09-19)
adds the hot and cooling transducers at their resting rates whether or not the floor is on, and the floor holds the same
cells at the same rates when it is. **the cooling cells' resting rate is 95 Hz** (Budelli 2019; ~75 measured through the
gate), on 14 cells, all the time, because that is what cooling cells do in life. and the record of 09-17 wrote, in the
warm-corner runs, "thermal DNs reach wing MNs mostly." so: fourteen cooling cells at their true resting rate, through the
thermal descending neurons, light the flight and song premotor network (IN06B013 at 40-70 Hz, vMS12_a at 62, dMS2 at 22)
and the wing motor neurons follow at 31 Hz. remove them and the wings are silent; nothing else in him touches it.

so the wing artefact is the plume's failure inverted: a real tonic input that the wiring at this constant carries too well,
into a motor output a resting fly never shows. it is not a bistable loop and it is not the fly wanting to fly. what to do
about it is a physiology question, not an engine one: whether the cooling cells' central synapses should carry a 95 Hz
tonic rate at a uniform 0.185 mV (in life their downstream is graded and gain-controlled), or whether the flight motor's
gate is the missing state. first, the dose: the wing rate against the cooling cells' resting rate (0, 25, 50, 75, 95).

two housekeeping facts from the trail, for the record: (1) the setup's calibrations leave `drive_hz` nonzero on 314 cells that
no row of the run overwrites (a leak; measured, not yet fixed; it did not change the wing result); (2) the reference engine holds
the 97 MBONs at 85 % of threshold by a tonic current of its own (`mbon_hold_frac`, a flybrain design decision, not Shiu's);
it did not change the wing result either, but it has been in every run and the record did not know it. both go to the queue.


**the cooling dose (13:46 PDT):** cooling rest at 0 / 25 / 50 / 75 / 95 Hz nominal (0 / 28 / 52 / 52 / 74 measured): the wing MNs at 30.4 / 29.1 / 30.4 / 30.0 / 31.0 Hz, IN06B013 51-68, flat. **the cooling cells are innocent**; the paragraph above named the wrong half of the thermal rows. what `--thermo off` also removes is the hot cells (VP2, 14 cells at 37 Hz nominal at 25 C, 27-32 measured), and they are the remaining suspect: arms with the hot cells at 0, at 18, and both classes at 0 are running.

**the hot cells, dosed (13:48 PDT):** hot at 18 / 0 nominal, and hot and cooling both at 0, on the defaults: the wing MNs at 32.8 / 31.7 / 31.5, IN06B013 58 / 60 / 48. **neither thermal class is the driver either.** what the arms actually say, laid side by side: everything off but the thermal rows -> 31.7; everything on but the thermal rows at 0 Hz -> 31.5; everything off including the thermal rows -> 0.9. so the loop is lit by any sufficient tonic input, whichever it is, and runs at the same 31 Hz once lit. a bare-engine test follows: the thermal cells driven for 3 s, then silence, to see whether it keeps going on its own.

**the bare-engine test (13:49 PDT; the engine alone, zero state, no noise; the 28 thermal cells driven at 60 Hz for 3 s, then
silence for 5 s, then driven again):** driven, IN06B013 runs at 49 Hz and the whole network at 26,000 spikes/s; drive off, it
falls to 0.2 Hz and the network to 112 spikes/s within the window; drive on again, 49 Hz again. **not bistable. driven.**
(the wing motor neurons themselves stayed at 0 in this test: with only the thermal cells driven the hub lights but the
wing motor needs the rest of the premotor network, dMS2 and vMS12, which the full input set supplies.)

**so, the wing artefact, settled as far as today goes:** IN06B013 is a four-cell hub in the cord's flight / song premotor
network that any broad tonic input lights, the thermal cells, the floor, vision, each on its own; and with the full input
set of a standing fly the hub sits near 50-70 Hz, the song premotor cells with it, and the 56 wing motor neurons at 31 Hz.
it is not a loop, not one sense's fault, and not a fly wanting to fly: it is the cord's premotor network at 0.185 mV
being too excitable to tonic input as a whole, the mirror image of the plume not carrying. in life the flight motor is
gated: a walking fly's wing motor neurons are silent whatever its senses are doing. the options, for the queue and for
nate: (a) the gate as a state (S2): "not flying" holds the flight premotor network below threshold, labelled, like the
walking command in reverse; (b) a labelled wiring correction on the hub's input gain, with the reason written (it is the
same class as the mirror normalisation, and the same risk); (c) leave it, since the wing motor neurons drive nothing in
the world here and the record now knows the number. (c) is where it sits tonight; (a) is my lean, because the flight
state is a real thing he will need for take-off anyway.

**the tarsal reflex, looked for (14:14 PDT; nate: are there signals in life that damp the flight motor while walking, that we should be driving rather than gating?)**
in life, yes: feet on the ground suppress flight (Fraenkel 1932 and after); lift the fly and the wings start. so the question was whether that path is
visible in his table. the hub's sensory inputs, first: 1,964 synapses from mechanosensory-proprioceptive cells, and they are all WING campaniform
sensilla (SNpp16 / 07 / 37 / 28, SApp10; ADMN, the wing nerve; cholinergic), the wing's own feedback, silent here because his wings do not move, correctly;
no leg afferent reaches the hub directly. the hub's inhibition, second: a third of its input is GABA (34,375 of 104,320 synapses; IN06B047 with 17 cells
the largest, IN11B004, IN11B024, IN06B036) and 9 % glutamate, so the brake exists in the wiring; but those inhibitory cells receive essentially no leg
sensory input either (0-1 % from leg-nerve afferents). so the tarsal reflex is not a two-hop motif here; if it lives in this table it is deeper, through
whatever drives IN06B047 in a standing fly, which is the question to ask when the flight gate is built. the leg-load floor (`floor_leg_proprio`, 15 Hz
on the leg-nerve proprioceptors) is on in every run and does not reach the hub. left there; tilt next, which needs the same leg-load thinking.

## tilt, built (2026-09-21 14:19 PDT; nate: "should we actually tilt him properly as he traverses the angled surfaces, taking heading into account to map gravity across his senses?"; TODO §Q 4b)

- `Garden.slope(x, y)`: the gradient of the walkable surface (for a sphere on the floor, -(x - ox) / sqrt(r^2 - d^2)); with `--tilt on`
  (needs the climb) his body takes **pitch** = atan(slope along his heading), nose up positive, and **roll** = atan(slope across it),
  left side up positive. a fly stands parallel to the surface, so this is the geometry, not a model.
- the eye: `Eye.render` gains `pitch_deg` and `roll_deg`; body-frame rays are rolled about x, pitched about y, then yawed. both
  zero is the old arithmetic exactly (the oracle's path). **the pitch sign was wrong on the first build**: nose-up showed him the
  ground; a numerical check (forward ommatidia at +60 deg should see the sky: 0.89 against 0.50 level and 0.37 nose-down) caught
  it before any result was taken, and the batch that had started on the wrong sign was stopped and remade.
- gravity on his Johnston's organ: the wind rows (JO-C/E) gain a term from the tilt: roll deflects the downhill antenna as a side wind
  would, pitch both as a head or tail wind (`--tilt-jo`, 1.0 = the weight of a full wind; Kamikouchi 2009 for the cells, the rate an
  estimate). this is the "gravity" row of the senses table, on for the first time.
- the leg load: the floor's 15 Hz on the leg-nerve proprioceptors becomes six rows by leg segment and side, shifting toward the
  downhill legs (`--tilt-load` 0.5: 15 Hz on the flat, 0-30 on a slope; nose up loads the hind legs, left side up loads the right). an
  estimate, labelled; the hair plates and campaniforms under load are the next physiology on that row.
- `pose_tilt` saved per frame; the viewer rotates the human view with his head.
- not done: the ocelli's sky sampling along the tilted head (small; noted).

smoke (6 s walking east over the fruit): pitch +47 deg climbing on, 0 at the top, -55 coming off; roll swinging -18 to +7 as he
veers. in flight: the config of record with `--tilt on`, three seeds, against the feeding-read batch (tilt off); the oracle.

**tilt, measured (14:29 PDT; the config of record with `--tilt on`, three seeds, 120 s, against the feeding-read batch of 09:30):**

| arm | first on the fruit | time on it | feeding (read from MN9) | MN9 on the fruit | mean / max pitch on the fruit | walked / after 30 s | ends from the fruit |
|---|---|---|---|---|---|---|---|
| tilt off (09:30) | 9.6 / 7.6 / 14.4 s | 10.1 / 1.6 / 9.5 s | 8 / 9 / 8 s | 16.0 / 14.7 / 13.4 Hz | 0 | 11.3 / 21.8 / 16.6 m; 7.8 / 17.6 / 13.4 | 1.3 / 1.5 / 3.8 m |
| tilt on | 8.1 / 5.9 / 9.1 s | 6.1 / 7.0 / 9.5 s | 8 / 9 / 8 s | 18.6 / 11.9 / 15.0 Hz | 28 / 31 / 20 deg mean; 85-87 max | 19.3 / 23.1 / 13.9 m; 13.6 / 17.7 / 9.5 | 4.4 / 2.8 / 4.3 m |

three of three, as before: he walks up the plume with his head pitching to the slope, gravity on his aristae and his weight on
his downhill legs, climbs the fruit (pitching to nearly vertical at its edge, 20-30 deg on average while on it), feeds by his own
motor neuron, and leaves. nothing broke; nothing obviously changed at three seeds (arrival a little sooner, a little further
walked, inside the spread). the point of tilt is not this batch: it is that the eye now sees a horizon that moves, the JO
gravity cells have a stimulus for the first time, and the leg-load rows have a slope to read. **`--tilt on` becomes the
default** (garden only, with the climb). what it opens: a run scored on the head's pitch against his steering (does a tilted
horizon change the HS wheel? the optic-flow cells were trained level), the JO gravity rows against the wind rows (they share
cells; a fly on a slope in a wind feels both), and the terrain item of §2a, now a heightfield away.


oracle on the tilt edits (14:36 PDT; the eye gained pitch and roll, zero = the old path): PASS, eight of eight, read from the log first.

**the standing signal, dosed (14:55 PDT; nate: "how deeply did we dig into whether we're failing to send a proper standing signal which might be leaving the wing reflex enabled?"; `--leg-load-hz`, the floor's 15 Hz on the 645 leg-nerve proprioceptors set to 0 / 30 / 60 / 120, the defaults otherwise, 12 s, seed 11)**

first the table: the leg proprioceptors DO reach the hub in two hops, 8,811 synapses through 230 relay cells, 44 % of them GABAergic
(IN06B036, IN13B008, IN06B043) and the rest cholinergic (the ascending neurons AN04A001, AN19B001); and 4,856 synapses reach the
hub's own inhibitors in two hops. so a standing signal can touch the flight hub here. then the dose:

| standing load on the leg proprioceptors | wing MNs | haltere | IN06B013 (the hub) | dMS2 | vMS12_a | IN06B047 (the hub's GABA input) | leg MNs, Hz per cell |
|---|---|---|---|---|---|---|---|
| 0 | 35.2 | 9.0 | 57.5 | 22.5 | 64.0 | 0.4 | 36.8 |
| 15 (the floor, the record) | ~31 | ~7.8 | ~58 | ~23 | ~65 | ~1 | |
| 30 | 30.5 | 7.4 | 63.9 | 23.1 | 67.8 | 1.0 | 46.4 |
| 60 | 28.0 | 5.7 | 60.1 | 22.7 | 67.3 | 1.0 | 49.9 |
| 120 | 28.3 | 6.1 | 67.2 | 24.6 | 72.4 | 1.0 | 63.0 |

so a proper standing signal damps the wings by about a fifth (35 -> 28 Hz) and saturates by 60 Hz; the hub itself does not
move (57-67 Hz), and the GABA class that could hold it down is not recruited (1 Hz). the damping arrives below the hub, on the
motor neurons or their other drivers. and the leg load feeds the leg motor neurons hard (37 -> 63 Hz per cell): the standing tonus
scales with it, which the pace readout is calibrated against, so the floor's 15 is not a free knob. answer to nate: the
standing signal is real, it is in the wiring, and it is worth a fifth; the other four fifths are the gate, which in life is a
state. not worth more arms now; the gate decision stays with nate (docs/ASK.md).


oracle on the leg-load flag (15:12 PDT): PASS, eight of eight, read from the log first.

## the wings, systematically (2026-09-21 16:49 PDT; nate: "you feel confident on our wings answer? ... what would it take to be systematic about this?"; TODO 8d)

the honest answer to the first question was no: the arms of the afternoon were one seed, 12 s, one dose per knob, the hub picked by eye,
and "the cord is too excitable to tonic input" was a description. the protocol is in TODO 8d; its parts land here as they finish.

**(1) is it song? no. (2) which muscles? the power muscles.** the standing brain in the bare engine (the floor's tonic rows, 20 s, spike
times at 1 ms, the 66 wing motor neurons by muscle type):

| motor neurons | cells | Hz per cell |
|---|---|---|
| DLMn a, b (dorsal longitudinal, the power muscles) | 2 | 119 |
| DVMn 1a-c (dorsoventral, power) | 6 | 116 |
| DLMn c-f | 8 | 93 |
| DVMn 3a, b / DVMn 2a, b | 4 / 4 | 86 / 85 |
| i2, hg1, i1 (steering) | 2 / 2 / 2 | 66 / 51 / 46 |

the busiest cells fire every 8 ms with a coefficient of variation of 0.11-0.13: a clock, not a song. the population's autocorrelation
is flat at every lag from 5 to 100 ms and the spectrum has no power at 28 Hz (pulse song's rate in life) and its peaks at 100-125 Hz
are the cells' own firing. so what runs in a standing fly here is the **flight power motor**, the DLM and DVM motor neurons at
~100 Hz, regular, with the steering motor neurons behind them, and the song premotor cells up beside it because they share the
network. in life the power muscles are silent on the ground and fire at a few tens of Hz in flight; 119 Hz standing is neither
state. the picture is a flight motor with nothing gating it, which is what the afternoon guessed, now with the muscles named
and the rhythm ruled out.

**the power motor neurons' own inputs (16:50 PDT):** the 24 DLMn / DVMn cells receive 148,421 synapses, 63 % cholinergic, 30 % GABA,
80 % from cord interneurons. the excitation is concentrated: IN19B043 (14,719 synapses onto them) and IN19B067 (12,086), cholinergic,
which the presynaptic arm of 13:3x found firing at 8.5 and 4.7 Hz, a few hertz on a cell with fourteen thousand synapses onto the
motor neurons, which at a uniform 0.185 mV is a lot. and the inhibition is concentrated too: IN03B089 (7,417), IN06B066 (6,645),
IN11B013 (5,980), GABAergic, which the same arm found at **0.0, 0.1 and 0.0 Hz**. so the brake on the flight power motor exists in
the wiring, a third of the motor neurons' input, and in ours it is silent. what would drive those three classes in a standing fly
is the next lookup; the sensitivity map will say whether any input we have moves them.

**what drives the silent brakes (16:51 PDT):** IN03B089 (18 cells; 51 % excitatory input, 12 % descending: DNae009 410 syn; 9 % sensory), IN06B066
(25; 63 % excitatory; 12 % sensory, of which SNpp16 the wing campaniforms 1,135; 9 % descending: DNp31 720), IN11B013 (10; 67 % excitatory; 9 %
descending: DNg27 502; 4 % sensory). so the three classes that could hold the power motor down are driven mostly by cord interneurons and by a few
descending neurons we do not drive (DNae009, DNp31, DNg27), and the largest sensory input to one of them is the wing's own feedback, silent
because the wings do not move. two readings, to be separated by the map and the paths: (a) the brakes are the flight pattern generator's own
antagonist-phase inhibition (DLM and DVM alternate in flight; here both fire tonically at ~100 Hz, a pattern generator saturated rather than
oscillating), or (b) the brakes are the "not flying" gate, driven from the brain through those descending neurons in a standing fly. the
sensitivity map says which inputs move any of this; the linear paths say what the wiring predicts each should do.

**(5) the constant with the full input set (17:13 PDT; the defaults, three seeds x 30 s, mean ± sd over seeds; the trace's first and last 10 s):**

| w (mV) | wing MNs, Hz per cell | first / last 10 s | power MNs (DLMn + DVMn) | the hub | leg MNs |
|---|---|---|---|---|---|
| 0.15 | 14.3 ± 0.8 | 11.8 / 16.2 | 24 | 29 | 25 |
| 0.16 | 20.4 ± 0.9 | 18.2 / 22.4 | 44 | 32 | 30 |
| 0.17 | 26.2 ± 0.5 | 23.2 / 28.3 | 63 | 35 | 34 |
| 0.185 (the record) | 31.6 ± 0.8 | 30.7 / 31.9 | 78 | 36 | 39 |
| 0.20 | 38.6 ± 0.9 | 37.3 / 39.2 | 100 | 39 | 44 |
| 0.22 | 46.4 ± 0.3 | 45.7 / 46.6 | 126 | 42 | 49 |

**graded, monotonic, stable in time, no threshold.** the wing rate is a smooth function of the constant from 0.15 up, and the
power motor neurons go from 24 to 126 Hz across the sweep; the seeds agree to a hertz; the first and last ten seconds agree.
so with the full input set there is no constant below the runaway ceiling at which the wings are silent (at 0.15, where the
sparsity would already be below its band, they still run at 14), and the "nothing driven" sweep of the afternoon, which
found them out at 0.15, was measuring the thermal rows' drive alone. the wings are a graded, driven output of the whole
input set at every constant: the constant scales them and does not gate them. what gates them in life is a state, or the
silent brakes; the map (running) says which inputs, if any, reach those brakes.

**(4) the path on paper (17:41 PDT; `wing_paths.py`: each input class propagated one, two and three hops through the wiring, edge weight = the
target's signed input fraction from that source (GABA and glutamate negative), summed at the wing motor neurons, the hub and the leg
motor neurons, per source cell):** every sensory class gives +0.000 at the wings and the hub at every hop; the only concentrated path in
the table is the walking command's, DNg100 -> leg motor neurons, +0.324 direct. so the wiring, read linearly, predicts NO input class has
a concentrated route to the wing motor within three hops. and the engine, measured, lights the wings at 31 Hz from any of them. the gap
between those two is the mechanism: **the wing drive is a network amplification, not a path.** the bare-engine test of 13:5x is the number
for it: 28 thermal cells at 60 Hz, 1,700 input spikes per second, and the whole network answers with 26,000 spikes per second, a gain of
about fifteen through cord interneurons whose 80 % share of the power motor neurons' input is the amplifier's last stage. a linear
estimate cannot see that; it needs the recurrence and the thresholds, which is the LIF. so (4) was worth doing for what it rules out: there
is no single wire to cut. the amplifier is the cord's own recurrent excitation at this constant, its brakes silent, and the honest lever is
whatever holds the brakes in a standing fly, which the map (running) is asking of every input we have.

**the excitatory premotor, looked up (17:48 PDT; nate: "are we interpreting the wrong neurons as flight reflex? is there really no dampening potential?")**
the identities are the atlas's: DLMn / DVMn are the flight power muscle motor neurons, b1 / b2 / i1 / hg the steering ones; nothing is
misread there, only the word "reflex", which nothing here deserves. the two classes that push the power motor neurons, IN19B043 (9 cells)
and IN19B067 (14), cholinergic, 16,094 and 15,173 input synapses, are themselves a third GABA-braked, and by the same two silent classes:
IN06B066 is the largest single input to BOTH (940 and 1,037 synapses) and IN03B089 the second and fifth. their excitation is a quarter and a
seventh descending (DNa08, DNg02, DNg27, DNp31) and the rest cord interneurons; their sensory input is 5-6 %. and IN19B067 and IN06B066
are reciprocal (IN19B067 -> IN06B066 353 synapses; IN06B066 -> IN19B067 1,037): the shape of a half-centre. so reading (a) of 15:0x
strengthens: **IN06B066 / IN03B089 look like the flight pattern generator's own antagonist-phase inhibition**, and in ours the excitatory
half runs tonically from the cord's amplified input while the inhibitory half never engages (0.1 Hz on 18,547 input synapses, of which
the premotor's 1,037 are 6 %). the dampening potential is real and it is these cells; what would engage them in a standing fly is
either the pattern generator running properly (the CPG alternates DLM and DVM in flight; ours saturates both) or a state that holds
the excitatory half down. the descending neurons that excite both halves at once, DNp31 and DNg27, are the flight command's shape,
and they are not driven here. nothing is misidentified; the missing thing is the gate, and now its cells have names.

**(3) the input sensitivity map (18:00 PDT; `world/wingmap/`, 36 arms x 3 seeds x 30 s: every driving row alone with everything else off, and
removed with everything else on; wing MNs Hz per cell, mean ± sd over seeds; the power MNs; IN06B013 / dMS2 / vMS12_a; the leg MNs):**

| arm | wing | power MNs | IN06B013 etc. | leg MNs |
|---|---|---|---|---|
| everything on (the defaults) | 31.6 ± 0.8 | 78 | 36 | 39 |
| nothing | 1.2 ± 0.4 | 0.1 | 0.3 | 3 |
| **alone:** the food-ORN floor (2,635 cells at 8 Hz) | **24.1** | 93 | 1.5 | 5 |
| the cooling cells alone / the hot cells alone / the thermo rows alone | **34.8 / 26.1 / 34.0** | 109 / 92 / 107 | 8 / 9 / 8 | 16 / 7 / 15 |
| vision alone (T4/T5) | **27.0 ± 5.4** | 89 | 0.3 | 7 |
| the walking command alone (DNg100) | **26.5** | 75 | **33.5** | 24 |
| the ocelli alone | 9.8 ± 11.7 (lit in some seeds) | 34 | 0.2 | 4 |
| the GRN floor / JO floor / the four small ORN floors / VP1m / hygro / leg proprio / wind, each alone | 0.5-1.9 | 0 | 0-1 | 3-4 |
| **minus** any one of the sixteen rows, everything else on | 29.8-34.8 (all within 3 Hz of 31.6) | 75-87 | 35-37 (minus the walk command: 7) | 29-41 |

three things the map says that the arms could not:

1. **redundancy, then saturation.** six different inputs each light the wings alone, to 24-35 Hz: the food-ORN floor, either
   thermal class, the thermal rows, vision, the walking command. remove any one of them with the rest on and nothing changes,
   within 3 Hz. so the flight motor here is a saturating amplifier: any tonic input above a small threshold (the small ORN
   classes, the GRN floor, the JO floor, hygro, the leg load and the wind rows alone do not reach it) drives it to the same
   plateau, and the plateau is set by the constant (the sweep above: 14 -> 46 Hz for 0.15 -> 0.22). that is the mechanism the
   afternoon was groping for, and it is not a fault of any one sense.
2. **the hub was the walking command's, not the wings'.** IN06B013 / dMS2 / vMS12_a sit at 33.5 Hz with DNg100 alone and at 7
   with everything but DNg100; the wings light to 24 Hz from the ORN floor with the hub at 1.5. so the four-cell "hub" of the
   afternoon rides on the walking command and is not the wings' driver; the wings' driver is the power motor neurons' own
   premotor (IN19B043 / IN19B067), which any of the six inputs reaches. the record's afternoon story is corrected here.
3. **more input, slightly less power.** the power motor neurons run at 92-109 Hz on any single input and 78 with everything on:
   the inhibitory half engages a little when more of the network is up. small, but the right sign for reading (a).

what the map did not log, by my omission: the brake classes themselves (IN06B066, IN03B089, IN11B013) and the premotor pair.
a second, smaller batch runs now: the six lighting inputs alone, those cells logged.

**the brakes under each lighting input (18:10 PDT; `world/wingbrake/`, six arms x 3 seeds x 30 s, Hz per cell after 2 s):**

| input alone | power MNs | IN19B043 / IN19B067 (the premotor push) | IN06B066 / IN03B089 / IN11B013 (the brakes) | IN06B013 |
|---|---|---|---|---|
| nothing | 0.1 | 0 / 0 | 0 / 0 / 0 | 2 |
| the food-ORN floor | 93 | 9.0 / 6.5 | 0.0 / 0.0 / 0.0 | 12 |
| the thermal rows | 107 | 16.4 / 6.5 | 0.9 / 0.0 / 0.0 | 53 |
| vision | 100 | 9.9 / 6.3 | 0.0 / 0.0 / 0.1 | 3 |
| the walking command | 75 | 6.2 / 5.0 | 0.0 / 0.0 / 0.1 | 32 |
| everything on | 76 | 9.5 / 4.6 | 0.4 / 0.0 / 0.0 | 66 |

**no input in the model engages the brakes.** the three GABA classes that hold the flight power motor and its premotor in the wiring sit
below one hertz under every input alone and with everything on, while the premotor push runs at 5-16 Hz and the power motor neurons at
75-107 under any of them. so the systematic pass ends where the afternoon's guess pointed, but on evidence now, and with the cells named:

**the wings, concluded (09-21).** (1) not song; (2) the flight power muscles, tonic, clock-regular, plus the steering set behind; (3) any tonic
input above a small threshold lights them to the same plateau, six do, ten do not, removing any one changes nothing: a saturating
amplifier in the cord; (4) read linearly the wiring has no concentrated path to them, so the drive is recurrent amplification, gain ~15,
with the power motor neurons' premotor pair as the last stage; (5) the plateau scales with the constant and no available constant gates
it; (6) the traces are stable over 30 s; and the pattern generator's inhibitory half, IN06B066 / IN03B089 / IN11B013, a third of the
motor neurons' input and a third of the premotor's, reciprocal with it, is unreachable by anything he senses or is commanded. in life
the half-centre alternates in flight and both halves are quiet on the ground; here one half is on and the other cannot be turned on.
the flight gate is therefore a state, and the state has an address: whatever drives those three classes in a standing fly (their
inputs are cord interneurons and the descending neurons DNae009 / DNp31 / DNg27, none driven here). options unchanged from ASK.md, now
with the cells named: (a) the gate as a state that drives the brake classes, labelled "not flying", with its exit the flight command
(DNp31 / DNg27 excite both halves); (b) a labelled gain correction on the premotor pair; (c) leave it. (a) is the lean and it is a
better-founded (a) than this morning's.

## what holds the inhibitory half back (18:20 PDT; nate: "have we examined all of the inputs that drive these, in isolation or not?"; `brake_balance.py`: the standing brain in the bare engine, floor + thermal rows, 10 s; every presynaptic cell of each class weighted by its measured rate x synapses x sign)

| class | cells | rate | mean membrane, % of threshold | excitatory input (synapse-spikes/s per cell) | inhibitory | synapses from silent cells |
|---|---|---|---|---|---|---|
| IN06B066 (brake) | 25 | 3.2 Hz | +24 % | 3,541 | 760 | 88 % |
| IN03B089 (brake) | 18 | 0.0 | +1 % | 529 | 88 | 95 % |
| IN11B013 (brake) | 10 | 0.0 | -2 % | 1,104 | 798 | 96 % |
| IN19B043 (premotor push) | 9 | 16.9 | +39 % | 10,040 | 3,142 | 87 % |
| IN19B067 (premotor push) | 14 | 5.7 | +25 % | 5,323 | 2,047 | 88 % |
| DLMn c-f (power MNs) | 8 | ~100 | | 59,867 | 27,358 | 80 % |

**nothing holds the brakes back. they are under-driven.** their membranes sit at a quarter, one and minus two percent of threshold: not
hyperpolarised by anyone firing, just not pushed, because 88-96 % of their input synapses come from cells that are silent in the
standing brain. the premotor push, by contrast, receives 5,000-10,000 synapse-spikes per second per cell, and its two largest sources
are the same for both cells and for the power motor neurons: **IN19B040**, a cord interneuron (5,608 and 3,724 onto the pair; 18,124
onto the DLMns) and **DNp31, a descending neuron, firing in the standing brain** (3,122 and 886 onto the pair; 11,540 onto the DLMns;
2,361 onto IN06B066, its largest excitatory input too). so the drive chain has a name at every stage: DNp31 and IN19B040 push the
premotor pair, the pair pushes the power motor neurons, and the largest inhibitors of the motor neurons (IN12B015, 16,820) and of the
pair (**IN06B013**, 1,756 and 1,301: the afternoon's "hub", GABAergic, the walking command's) fire but do not win. that last fact is
a motif worth its own line: **the walking command's interneuron inhibits the flight premotor**, a walking-versus-flight switch in the
wiring, which is why the power motor neurons ran at 75 Hz with the command and 93-109 without it in the map.

so the question moves one stage up the chain and out of the cord: **what drives DNp31 in a standing fly?** a descending neuron carrying a
flight-command-shaped drive (it excites both halves of the generator) into the cord while he stands is the anomaly, and its inputs are
in the brain. the driver balance for DNp31, IN19B040 and IN12B015 runs now; the sweep of candidate inputs to the brakes runs beside it.

**the two drivers, in the table (18:21 PDT):** DNp31 (2 cells, cholinergic; hemibrain and FlyWire agree on the name) receives 36,126 synapses,
60 % from central-brain intrinsics and **26 % from visual projection neurons: LLPC2 (2,591), LPLC4 (2,022), LPC2 (776), LC36 (663)**, the
lobula-plate and lobula columnar cells that carry wide-field motion and looming out of the optic lobe; its only sensory input is a
whisper of JO. so the descending neuron that pushes the flight generator from above is a visual-motion descending neuron, and "vision
alone lights the wings" in the map is that wire: flyvis -> his T4 / T5 -> the lobula plate -> DNp31 -> the cord. IN19B040 (4 cells,
cholinergic, 5,972 input synapses) is 53 % cord-intrinsic with its largest single input **itself** (901 synapses, self-excitation), then
an ascending glutamatergic class, the ascending sensory SAxx01 (580), and descending DNpe036; a recurrent node, which is what a gain of
fifteen needs somewhere. what DNp31 does in life is the next thing to read (Namiki 2018's DNp set is the place to look); a visual-motion
descending neuron into the flight premotor is the shape of an optomotor or landing command, and a standing fly in a lit garden gives it
optic flow whenever he turns. the rate-weighted balance for DNp31 / IN19B040 / IN12B015 / IN06B013 / DNbe001 runs now.

**the drivers, balanced (18:22 PDT; the same method, the standing brain):** IN19B040 fires at 116 Hz (membrane +29 % of threshold) and its
input is 26,028 synapse-spikes/s per cell from ITSELF and 9,300 from the descending neuron DNg33, with 36 inhibitory against 36,182
excitatory: a self-exciting node with a descending input and no brake, the amplifier's core. IN12B015 (155 Hz), the largest inhibitor of
the DLMns, is driven by **DNb05** (57,727). IN06B013 (71 Hz) is driven by **DNb05** (10,585) and DNp31 (6,325). DNp31 itself is driven by
**DNb05** (15,977, its largest input by far), then DNbe007, LHPV2i1, LoVP50. so one descending neuron, DNb05, firing in the standing brain,
feeds the flight-command DN (DNp31), the motor neurons' largest inhibitor (IN12B015) and the premotor's largest inhibitor (IN06B013) at
once; and a second, DNg33, feeds the self-exciting node. the chain, top to bottom, now reads: **DNb05 and DNg33 (descending, firing while
he stands) -> DNp31 and IN19B040 -> IN19B043 / IN19B067 -> the power motor neurons**, with the brakes on that chain (IN12B015, IN06B013)
also fed by DNb05 and firing, and the generator's own inhibitory half (IN06B066 / IN03B089 / IN11B013) fed by cells that are silent. the
question moves up again: what drives DNb05 and DNg33 in the brain of a standing fly, and what are they in life. running.

**who can turn the brakes on (18:23 PDT; `brake_drivers.py`: the standing brain, each of 21 candidate input classes of the brakes driven alone at 50 Hz for 6 s;
rates over the last 4 s):** none. IN03B089 stays at 0.0 under every candidate; IN11B013 reaches 3.0 Hz under AN19B001 and 1.4 under INXXX095; IN06B066 reaches
9.7 under IN08B068 (from 3.2) and 5.1 under DNa08. the power motor neurons fall below their 99 Hz baseline only under inputs that also blow the whole
network up (SNpp16, the wing campaniforms, 69 Hz with the network at 164,000 spikes/s; INXXX095 likewise) or modestly under IN08B068 (76) and DNp31 (78,
which was already firing at 82 Hz before the extra drive); DNa08 and IN19B075 push them up to 128. so no single presynaptic class, driven hard, engages the
generator's inhibitory half: its input is many small sources, and it wants a broad or a state-shaped drive that none of the 21 supplies alone.

**the two upstream descending neurons, in the table:** DNb05 (2 cells, cholinergic; hemibrain and FlyWire agree) receives 36,551 synapses, 26 % from visual
projection neurons, above all **LPLC4 (4,712) and LLPC2 (1,805)**, the lobula-plate columnar loom / expansion cells, with a little cooling-cell and hygro input;
its outputs go 20 % into the cord (IN12B018, IN12B015, IN23B001, IN12A001). DNg33 (2 cells, cholinergic; FlyWire only) is self-excitatory (1,496), fed by the
LAL (LAL195: the steering output of the central complex), DNp35, DNd03 and ascending neurons, and it projects to ascending neurons and to IN19B040. so the
two descending neurons that feed the flight machinery while he stands are a visual-loom / expansion DN (DNb05, the same inputs as DNp31 one stage down) and
a LAL-driven, self-exciting DN (DNg33). a walking fly in a lit garden gives the loom / expansion cells self-motion optic flow at every turn, and the LAL is
where his steering lives: both are inputs a standing fly has, and both reach the flight generator's excitatory half through nothing we can remove without
removing sight and steering. the literature brief (running) is asked what DNb05 / DNp31 / DNg33 do in life and whether a flight state gates the visual
drive into them, which is where the honest fix would sit if it does.

**what fires into the two upstream descending neurons while he stands (18:25 PDT; the standing brain, no vision):** DNb05 fires at **217 Hz** (membrane +11 %
of threshold: not near threshold, driven straight through it) and its rate-weighted input is **the cooling pathway: VP3+_l2PN 60,840 synapse-spikes/s per
cell, VP5+VP3_l2PN 19,865, TRN_VP3a (the cooling cells themselves) 15,712**, then a multiglomerular olfactory PN (M_l2PNm16, 12,892) and the lateral horn
(LHPV2i1, 9,567): 206,000 excitatory against 18,000 inhibitory. so the cooling cells at their 95 Hz resting rate, through the VP3 projection neurons, drive a
descending neuron at 217 Hz, and that descending neuron drives the flight command (DNp31), the motor neurons' inhibitor (IN12B015) and the premotor's
(IN06B013). the map's "cooling cells alone light the wings hardest" is this wire; the cooling dose being flat when everything else is on is the other
inputs (the ORN floor through the multiglomerular PNs, the hygro floor through VP5) feeding the same DN. DNg33 fires at **200 Hz** and its input is
**itself: 149,600 of 181,313 synapse-spikes/s**, a two-cell pair locked in its own excitation (1,496 recurrent synapses; net inhibition 896), fed at the start
by DNp35 / IN09A005 / AN09A005. that is the gnathal runaway's shape again, in the brain: a self-exciting pair with no adaptation and almost no
inhibition, which a LIF without spike-frequency adaptation or frozen refractory conductance holds at its maximum forever once lit.

so the two facts under the whole wing story are now: (1) **a thermosensory descending neuron, DNb05, driven at 217 Hz by the cooling pathway at rest**, and
(2) **a self-locked descending pair, DNg33, at 200 Hz**. neither is a fly wanting to fly; one is a resting rate carried too far and the other a loop the
engine cannot damp. the lesion arms run now (`--silence`, an in-silico lesion flag, never a default): DNb05 out, DNg33 out, both, DNp31 out, on the
defaults, 30 s, the whole chain logged.

## the lesions (18:29 PDT; `--silence`, an in-silico lesion: the named cells' threshold put out of reach; the defaults, 30 s, seed 11; rates after 2 s)

| silenced | power MNs | premotor | brakes | DNb05 | DNg33 | DNp31 | IN19B040 | IN12B015 | IN06B013 | walked |
|---|---|---|---|---|---|---|---|---|---|---|
| nothing | 79.6 | 6.9 | 0.2 | 188 | 209 | 40 | 112 | 145 | 67 | 6.8 m |
| DNb05 (2 cells) | **106.5** | 7.9 | 0.0 | 0 | 210 | 7 | 112 | 16 | 22 | **0.0 m** |
| **DNg33 (2 cells)** | **2.4** | **0.0** | 0.2 | 190 | 0 | 38 | **0.0** | 145 | 66 | 6.9 m |
| both | 1.3 | 0.0 | 0.0 | 0 | 0 | 7 | 0 | 17 | 22 | 0.0 m |
| DNp31 (2 cells) | 48.7 | 3.5 | 0.0 | 202 | 201 | 0 | 111 | 151 | 61 | 7.6 m |

**the wings are two cells.** silence DNg33, the self-locked descending pair, and the power motor neurons fall from 80 Hz to 2, the premotor to 0, the
self-exciting cord node IN19B040 to 0, and he walks exactly as before (6.9 m). the whole flight motor of a standing fly here hangs on one descending
pair locked in its own excitation at 200 Hz, through one cord node locked in its own at 112. DNp31, the visual flight-command DN, contributes: cut it
and the power motor neurons halve (49). and DNb05, the thermosensory DN at 188 Hz, turns out to be on the OTHER side: cut it and the power motor
neurons rise to 106, because it drives the motor neurons' largest inhibitor (IN12B015, 145 -> 16) and the premotor's (IN06B013, 67 -> 22); and **he
stops walking**, 0.0 m, because its descending drive is part of the leg tonus the pace reads: the "kinesis" of 09-17, warmth driving the legs, has
a cell now, and the cooling pathway at rest is the thing walking him as much as the walking command is. two puppets' worth of physiology in one
lesion.

so the afternoon's "state with an address" collapses to something smaller and stranger: **a two-cell descending pair, DNg33, self-locked at 200 Hz,
is the flight motor's drive, and nothing in the model can unlock it** because the engine has no spike-frequency adaptation and does not freeze the
synaptic conductance during the refractory period (Shiu's second difference, TODO 5b), so a pair with 1,496 mutual synapses runs at the refractory
ceiling forever once lit. what lights it is DNp35 / IN09A005 / AN09A005, which any tonic input reaches. the honest fixes are now engine-side and
citable, not a stand-in: the refractory conductance freeze (Shiu 2024's own model), spike-frequency adaptation (in the flybrain engine as an option;
its source to be checked), or DNg33's identity in life if it is known to be self-limiting. the refractory test runs now in the bare engine: the
pair's lock against the refractory period.

**the pair, alone (18:31 PDT; `dng33_kick.py` and `dng33_lock.py`, the bare engine):**

| test | DNg33 | IN19B040 | power MNs | the network |
|---|---|---|---|---|
| zero state, zero drive, zero noise, ONE kick of the two DNg33 cells, then 5 s | **250 Hz, every second** | 120 | 93-97 | 8,200 spikes/s |
| the standing brain, refractory 2.2 ms (the record) / 5 / 10 | 200 / 167 / 68 | 116 / 78 / **0** | 98 / 50 / **0.0** | 87,800 / 63,200 / 45,100 |

**DNg33 is a bistable pair.** with nothing else in the engine, one kick locks the two cells at 250 Hz, the refractory ceiling, forever, and
through IN19B040 they run the flight power motor at 95 Hz on an otherwise silent network of 8,000 spikes a second. this is the same
object as the gnathal runaway of the constant sweep, one stage smaller: two cells with 1,496 synapses between them and 900 of inhibition
against 181,000 of self-excitation, in an engine with no spike-frequency adaptation, no synaptic depression on that path, and no freeze of
the synaptic conductance during the refractory period. a real pair like that does not lock, because real synapses depress and real cells
adapt; the LIF of the record does neither. the refractory period alone shows the lock's dependence on rate: at 10 ms the pair drops to 68 Hz
and the cord node and the wings go to exactly zero, so the wings need the pair above roughly 100 Hz, which only the lock provides. and
DNb05, the thermosensory DN, is NOT bistable: its rate tracks its input (217 -> 139 -> 74 across the refractory sweep, following the network),
which is what a driven cell does.

so the wing artefact, all the way down, is one bistable two-cell loop in the brain that anything lights and nothing in the engine can
put out. the honest fixes are engine-side and citable, in this order: (1) Shiu 2024's refractory conductance freeze (TODO 5b), the one
difference between his LIF and ours that touches exactly this, to be tested on the kick first; (2) if that does not break the lock,
spike-frequency adaptation or synaptic depression as an opt-in with a source, oracle v3; (3) a labelled correction on DNg33's recurrent
synapses only if the physiology brief says the pair is self-limiting in life for a reason the engine cannot hold. not a state, not a
stand-in: a loop the engine lacks the biology to damp. the kick is the test bench: two cells, five seconds, pass or fail.

## the two fixes on the bench (18:34 PDT; the kick bench: zero state, zero drive, zero noise, one kick of the DNg33 pair, five seconds)

| engine | DNg33 | IN19B040 | power MNs | the network |
|---|---|---|---|---|
| the record's | 250 Hz forever | 120 | 95 | 8,200 spikes/s |
| **Shiu's refractory conductance freeze** (`--refrac-freeze`, opt-in, bit-exact off) | 250 | **225** | **232** | 14,300 |
| **short-term synaptic depression on the pair's own synapses** (`--std pair`; u 0.08 per spike, recovery 480 ms) | 19.5 in the first second, **then 0** | 0 | 0 | 0 |
| the same depression on every cell (`--std all`) | 19.5, then 0 | 0 | 0 | 0 |

**the freeze makes it worse, as it should:** a conductance that does not decay while the cell is refractory arrives intact when the cell is free
again, so the loop gains. it is Shiu's equation and it stays as an opt-in for the fidelity question (TODO 5b), but it is not this fix.
**depression breaks the lock in under a second.** with the engine's own Tsodyks-Markram-style rule on the pair's output synapses, each spike
spends 8 % of the pair's resource and the resource takes half a second to come back; at 250 Hz the pair depletes itself to nothing within the
first second and stays quiet, the resource recovers to 1.0, and the cord node and the flight motor never light. the same rule on every cell gives
the same bench result (the bench has nothing else firing). the engine's constants (u 0.08, tau 480 ms) are the flybrain engine's, chosen for its
sensory populations; their sources are the literature brief's to check (Tsodyks & Markram 1997 for the rule; fly synapses depress strongly at
first order, Kazama & Wilson 2008 for ORN -> PN; the DN pair itself is unknown).

so the wing artefact's honest fix is a synaptic mechanism the engine has and the record never turned on: depression. two ways to apply it, both
running now on the configuration of record, three seeds each: `--std pair`, the minimal labelled correction (two cells, the reason written), and
`--std all`, the physiology (every synapse depresses, which also re-scales every tonic sensory row: the cooling cells at 95 Hz would sit at a
fifth of their drive at steady state), which is a refreeze and every baseline re-measured. the batch says what each does to him.


**oracle FAIL (18:38 PDT), mine:** the `--std` block was inserted after the engine line by string replacement, which carried the rest of that line (`mty = ...`, the type array every later line uses) into the new `if` block, so every run without `--std` died on a NameError at the readouts, the oracle's four port arms included. restored at top level; the oracle reruns. the depression batch, which passes `--std`, was not affected. an oracle FAIL from my own edit is recorded as a FAIL.

## the flight-gate brief (18:43 PDT; `docs/physiology/flight_gate.md`, an opus agent, 517 lines; the claims that change the plan, checked where the table could check them)

- **the cooling cells are phasic and their 95 Hz basal rate is the zero of the code** (Budelli 2019): a cooling cell at rest is saying "nothing is
  changing." feeding that rate through non-depressing synapses into a LIF is a sensory-encoding artefact before it is anything about flight, and it is
  DNb05's largest input. the brief's first recommendation is to fix that whether or not the wings quiet.
- **the DNg33 pair's 1,496 recurrent synapses are mutual, not autapses**: 773 one way, 723 the other (verified here). a pair like that with no
  adaptation is a latch by construction; "a fix to the engine, not to the fly." (the bench agrees: depression unlocks it in a second.)
- **the flight gate in life is a gain, not a brake** (Ache et al. 2019: the landing descending neurons' visual responses are "severely attenuated
  during non-flight periods", by octopamine in one case and by flight-motor feedback in the other; Maimon 2010, Suver 2012 for the whole visual
  pathway). so the honest representation of "not flying", if one is needed, is a multiplicative gain on the LPLC4 / LLPC2 / LPC2 / LC36 synapses
  onto DNp31 and DNb05, labelled `flight_state = 0`, a modulatory mechanism as a modulatory parameter.
- **do not silence DNb05 or DNp31 as a default**: DNb05 is established to be active in walking flies and steering-correlated (Yang et al. 2024,
  Cell; Namiki 2018 flagged it as the odd descending neuron reading both optic and olfactory glomeruli, which is our input table exactly). the
  lesion of 18:xx agrees from the other side: silence it and he stops walking.
- **the three GABA classes are not a "not flying" switch**: Cheong et al. 2024 name IN06B066 as the target of DNa08 and DNp31 that may form an
  inhibition-stabilised network with the tectular interneurons "to limit runaway excitation": inhibition that follows excitation. and a new
  table fact: IN06B066 and IN03B089 are DLM-biased (5,763 and 6,312 synapses onto DLMns against 882 and 1,105 onto DVMns), IN11B013 is DVM-biased
  46:1; the excitation is common to both. phase and gain machinery for DLM versus DVM.
- **the target number**: real DLM / DVM motor neurons fire 5-20 Hz in flight (Harcombe & Wyman 1977), sequenced by electrical coupling between the
  motor neurons (Hürkey et al. 2023, Nature) that turns unpatterned premotor input into splayed firing. our 119 Hz is six to twenty times a
  flying fly, and our engine has no gap junctions, so it cannot make the real pattern in any state. "not flying" is 0 Hz; anything that lands them
  at 40 has not fixed it. the giant-fibre path is present in name only for the same reason (DNp01 -> TTMn 90 chemical synapses; the pathway is
  electrical in life), and the octopaminergic axis is outside the model (101 cells; mesVUM-MJ makes one synapse onto the power motor neurons).

the brief's experiments, in its order, against what is already done: (1) a control with DLM and DVM logged apart [the std batch logs them apart];
(2) the cooling row at its true zero [done at 15:1x: the wings did not move, because DNb05 has other inputs and, per the lesion, DNb05 is not
the wings' driver but their inhibitors'; the brief was written without the lesion]; (3) depression on the thermosensory pathway [the `--std all`
arm]; (4) DNg33 de-latched [the `--std pair` arm]; (5) the flight-state visual gain, Ache 2019, labelled [to build, in `wiring.py`, as a
correction class with a source]; (6) the labelled brake state, only if 1-5 leave the wings up [unlikely to be needed]. the batch decides
between 3 and 4 tonight; 5 is queued as the gate's honest form for when he has a flight state to switch it.

## depression on the run of record (18:52 PDT; `world/std/`, the configuration of record (climb, tilt, feeding read from MN9), three seeds x 120 s; the tilt batch of 14:28 as the baseline; rates after 2 s)

| arm | first on the fruit | feeding | walked | DLMn | DVMn | DNg33 | IN19B040 | DNb05 | MN9 on the fruit | KCg-m | leg MNs |
|---|---|---|---|---|---|---|---|---|---|---|---|
| the defaults (tilt batch) | 8.1 / 5.9 / 9.1 s | 8 / 9 / 8 s | 19.3 / 23.1 / 13.9 m | ~100 | ~100 | ~200 | ~112 | ~190 | 13.5 / 6.2 / 12.0 Hz | | 32.8 / 34.1 / 32.6 |
| **`--std pair`** (depression on the DNg33 pair's synapses only) | 13.8 / 5.8 / 8.1 s | 8 / 8 / 8 s | 10.8 / 16.8 / 13.3 m | **0.0 / 0.0 / 0.1** | **9.5 / 9.3 / 7.8** | 62-70 | **0.0** | 206-213 | 10.9 / 10.0 / 9.1 | 0.03 | 31.8 / 32.6 / 32.2 |
| `--std all` (every cell) | never / never / 78.5 s | 0 / 0 / 0 s | 44.8 / 47.3 / 38.2 m | 0.1 | 0.1 | 0 | 0 | 48-50 | 0 | 0.00 | **1.7 / 2.3 / 1.6** |

**depression on the pair alone quiets the wings and leaves him alone.** the DLM motor neurons go from ~100 Hz to 0.0, the DVMs to 8-9, the
self-exciting cord node to 0, the pair itself from a locked 200 to a driven 62-70; and he walks up the plume, climbs the fruit at 6-14 s, feeds
by MN9 for 8 s, and leaves, three of three, with the leg tonus (32 Hz per cell) and the feeding readout unchanged. the DVMs' remaining 9 Hz is
below the flying fly's 5-20 (Harcombe & Wyman 1977) and not the brief's "not flying = 0"; it is driven by what still reaches the premotor
through DNp31 and the descending set, and it is the residue the flight-state gain (TODO 8e) is for.

**depression on every cell breaks the calibration**, as predicted: the leg motor neurons fall from 32 Hz per cell to 2, so the standing
tonus the pace is read against is gone and he runs 38-47 m in two minutes without ever reaching the fruit; the mushroom body goes to zero;
DNb05 drops to 49. every tonic sensory row depresses to a fifth of its drive at steady state and every calibration of the record was made
without that. it is the physiology, and it is a refreeze day with every baseline re-measured, which is nate's call (docs/ASK.md). the
middle option, depression on the sensory populations plus the pair (`--std sensory`: the encoding fix the brief asks for, Budelli 2019),
runs now. tonight's honest default is the pair: two cells, the reason written (a mutual 773 / 723 loop in an engine with no adaptation),
the mechanism cited (Tsodyks & Markram 1997), the exit the engine-wide physiology when the refreeze is done.


oracle after the NameError fix (18:59 PDT; the refractory-freeze flag off, the depression flag off): PASS, eight of eight, read from the log first. the exact kernel's new argument changes nothing when it is false.

**the sensory arm (19:05 PDT; `--std sensory`: depression on the engine's sensory populations, 19,839 cells, plus the pair):** the wings quieter still
(DLMn 2.5-2.7, DVMn 3.0-3.5) and the fly broken in two new places: he reaches the fruit at 27-29 s and never feeds, because the labellar sugar cells
depress to a fifth of their drive and MN9 never crosses the read's threshold (0.0 Hz on the fruit); the Kenyon cells go to zero; he walks 50-57 m
because the plume's ORNs depress and the compass goal loses its whiff. so depression on the sensory synapses at the engine's constants (u 0.08,
480 ms) is the encoding fix the brief asked for and it invalidates the feeding read, the KC calibration and the anemotaxis threshold at once: every
one of those was set against non-depressing sensory drive. it is right and it is a refreeze, the same day as `--std all`, with the sugar rate,
the sparsity and the plume re-measured against depressing synapses.

**decision (tonight): `--std pair` is the default.** two cells, the reason and the source written, the fly intact, the DLMs at zero and the DVMs at
9. the engine-wide depression (sensory, then all) is the refreeze item, bundled with the two leaks and, from nate's question of 19:xx, the
synapse-strength policy below. the oracle lines pin `--std off`, so the flip changes no reference.

## the policy for fitting what the connectome cannot say (19:05 PDT; nate: "where synapse strength isn't known, is it intellectually honest to manipulate those constants by receptor type or location, so long as we produce a fly-like fly with minimal boolean intervention?")

yes, on one line drawn hard: **constants are fit to physiology, never to the behaviour we want.** the rules, standing from here:

1. few parameters, structured by biology: by transmitter, by neuropil, by receptor class, by short-term dynamics. never per cell, never per
   behaviour. a gain with a behaviour's name on it is the flyproject's file of twos and twenties.
2. the targets are measured rates and response curves, with sources: Kenyon-cell sparsity (Turner 2008, Honegger 2011), the sugar dose-response
   on MN9 (Shiu 2024), the flight power motor at 5-20 Hz in flight and 0 on the ground (Harcombe & Wyman 1977), the ORN -> PN gain and its
   depression (Kazama & Wilson 2008), the cooling cells' phasic code (Budelli 2019). each fitted value is written with what it was fit to.
3. behaviour is the held-out test. he is never tuned until he forages; he is tuned until his cells match their papers, and then we watch.
4. fewer free numbers than measured constraints, and both counts stated side by side.
5. every fitted parameter set runs against the uniform fly on the record's behaviours, and is its own oracle freeze, so drift stays visible.

the first two axes, because the literature exists: transmitter class (acetylcholine, GABA and glutamate synapses differ in unitary size and
kinetics in the fly; we give them one number) and short-term dynamics per sensory class (what the pair and the cooling cells taught this week).
a handful of numbers, fit to about six targets, tested on the whole record. the refreeze day, with a design behind it: `docs/TODO.md` 5c.

## the run of record, 09-21 evening (19:19 PDT; `world/record/garden_0921b_s11.npz`, 180 s, seed 11, every default of the day: real antennae, the wind rows, the thermal rows, the satiety gate, the ocelli, the climb, tilt, feeding read from MN9, depression on the DNg33 pair; the compass configuration, feeding and satiety, the UV layer, the taste, wing and ocellar cells logged)

- on the fruit at 10.2 s, 14.6 s on it in all, up to the top; MN9 at 11 Hz while there; feeding read from it for 8 s; he leaves, 13 m walked, moving 40 %,
  ends 3.7 m from the fruit.
- **his wings are down**: the DLM motor neurons at 0.0 Hz, the DVMs at 7.4, the pair at a driven 43 instead of a locked 200, the cord node at 0. the
  first run of record in which a standing fly's flight motor is not running.
- viewer: `uv run python world/replay_app.py world/record/garden_0921b_s11.npz --scale 2`.


oracle after the depression default (19:26 PDT; `--std pair` the default, `--std off` pinned on both oracle lines): PASS, eight of eight, read from the log first.

## the stall at 1:50 (20:23 PDT; nate: "around 1:45 he seems to get trapped on a blade of grass, and though he's facing away from it for over a minute never seems to escape")

from 110 s to the end of the run of record he stood at (-2.175, -2.179), speed exactly 0, touching a stalk on every frame, facing away from it, while the
goal switched four times. the cause, once checked against the run's own stalk layout (the garden's grass is drawn per seed; a first check against the
default layout said he was 3 cm inside a stalk, which was my error and is kept here): he rests at exactly the stalk's radius plus his own after a
push-out, and the contact test `dd < gr + r` passes by a rounding hair every frame, so a fly standing still against a stalk is "touching" it a
hundred times a second. the bristle rows then hold the cord in its withdrawal pattern (leg motor neurons 12,100 -> 9,200 spikes/s), the state pace
reads that as standing, and standing he never leaves: a deadlock made of one floating-point ulp. fixed: a touch is a penetration of at least 0.1 mm,
i.e. motion into the stalk; and the stalk contacts now resolve iteratively against every stalk, which the record had assumed and the code did not do.
the run of record is being made again on it. (the pace reading the summed cord, which the withdrawal pattern pulls down, is the deeper thing here:
TODO §2's motor-pattern readout.) and nate's other note: the viewpoint snapped to the sky in a frame at the fruit's edge; pitch and roll are now the
surface under his feet front to back over the body length (the edge crossed over a body length, 54 deg at the first foot on the dome, then 71, then
down), and the viewer smooths them with the same box filter as the heading.

**the run of record, remade on the stall fix (20:37 PDT; `world/record/garden_0921b_s11.npz`, the same seed and flags):** on the fruit at 6.5 s, 9.9 s on it,
feeding read from MN9 for 8 s (12 Hz on the fruit), the wings down (DLMn 0.0, DVMn 7.9); then 28 m walked, moving 80 % of the three minutes, touching
something on 12 % of frames and never still for ten seconds, the stone climbed (0.90 m), ending 5.4 m from the fruit. the stalled file of the
first make is kept beside it in the scratchpad as what it was. the viewer line is unchanged.

## the neck (20:41 PDT; nate: "do we have any way to interpret what his neck neurons are doing? has our guy been trying to look around? what degrees of freedom does a fly neck have, and are they active lookers?")

**in life:** about twenty-one pairs of neck muscles (Strausfeld et al. 1987, the blowfly atlas; the set is conserved), yaw, pitch and roll of some
tens of degrees each, roll the largest. no eye movement; the head is the eye's only mount. flies are not scanners: nobody has described a fly looking
around a scene. what the head does is two things: in flight, saccades of ~20 deg in milliseconds that lead the body's turn (Schilstra & van Hateren
1999), and counter-roll against the body's roll for gaze stabilisation (Hengstenberg 1993), haltere-, ocelli- and visually driven; walking flies move
the head less, with the same corrections on top.

**in the table:** his neck motor neurons are MNnm01-14 in the cord (24 cells, left and right) and 20 in the head; their 292,990 input synapses are
36 % descending neurons (DNge002, DNge033, DNg93), 24 % ascending, 18 % central-brain, and among the largest single inputs the wing and haltere
campaniform afferents (SApp09 / SApp22, 4,452): commanded from above, corrected from below, the haltere-to-neck reflex in the wiring.

**in the run** (60 s of the configuration of record, 14 of the neck types logged; per-chunk rates against his turning rate and his body's tilt):
28 Hz per cell, left 39 and right 17 (a side bias to audit against the tracing, like the cord's), and **no relation to anything he does**:
correlation of the left-right difference with his turning +0.06, with his roll -0.22; of the total with his pitch -0.01; with the size of his
turns -0.27. the steering cells for scale, HS and DNa02 left-right against turning, -0.11 and -0.05 in the same run. so his neck is a tonic
hum with a side bias, not a gaze: he has not been looking around, and nothing in him is trying to. the descending neck commands the wiring
expects come from cells we do not drive, and the haltere afferents that would correct the head are silent because his halteres do not beat,
which is right for a walking fly. the gaze reflex of TODO 4d is therefore a build, not a readout: the neck motor neurons carry nothing yet to
read.


## the legs, per muscle (21:38 PDT; nate: "where would you like to continue from? filling out some of his inputs? or starting to monitor and interpret his muscle outputs?" — outputs first, because every sense is judged through the summed cord, and proprioception (the largest missing sense) needs legs to exist; nate agreed the body will be actuated from motor neurons through a sourced muscle model, never a trained controller: "I'd rather have our guy flailing and spasming in place")

**the table:** the male cord carries 373 leg motor neurons in the brain file (133 front, 116 mid, 124 hind; sides within three cells), most named
by the muscle they pull (Lesser 2024 / Azevedo 2024 names: tibia flexor and accessory flexor, tibia extensor, trochanter flexor / extensor,
sternotrochanter, femur reductor, sternal anterior / posterior rotator, pleural remotor, tergopleural promotor, the long tendon muscles ltm /
ltm1 / ltm2, tarsal depressor / levator, tergotrochanter); 45 mid- and hind-leg cells carry MANC numbers without a muscle (MNml29, 76-83; MNhl01,
02, 29, 59-65, 87, 88). so a muscle map is a readout off the table, nothing inferred. `--log-frames` (new; with `--log-types`) saves the logged
cells' counts per 10 ms frame, since a step cycle in life is ~100 ms; oracle on the changed loop PASS (v1 + v2, 8 configurations, none differing,
read from the log). `experiments/gait.py` asks the neck's question of the legs.

**the probe** (90 s, seed 11, the configuration of record, all 38 leg motor types per frame; walking 62 % of frames at 0.19 m/s, standing 30 %):

| Hz per cell, walking / standing | L1 | R1 | L2 | R2 | L3 | R3 |
|---|---|---|---|---|---|---|
| coxa retract (remotor, post. rotator) | 2.6 / 1.0 | 2.4 / 1.2 | 2.3 / 0.6 | 1.1 / 0.6 | 7.5 / 5.8 | 8.3 / 4.7 |
| coxa protract (ant. rotator, promotor) | 5.7 / 5.5 | 6.5 / 6.0 | **43.9 / 54.7** | **51.1 / 60.3** | 12.6 / 10.9 | 4.8 / 4.4 |
| trochanter depress (sternotrochanter, tr extensor) | 16.8 / 12.6 | 15.6 / 11.8 | 0.4 / 0.1 | 0.3 / 0.1 | 2.4 / 0.2 | 2.5 / 0.5 |
| trochanter levate (tr flexor, acc.) | 0 / 0 | 0 / 0 | 5.3 / 5.4 | 12.8 / 6.4 | 0 / 0 | 2.0 / 0.8 |
| **tibia flex (ti flexor, acc.; 84 cells)** | **0 / 0** | **0 / 0** | **0 / 0** | **0 / 0** | **0 / 0** | **0 / 0** |
| tibia extend | 3.3 / 3.1 | 2.7 / 3.3 | **93.8 / 85.8** | **44.9 / 37.4** | 3.7 / 1.7 | 5.2 / 2.5 |
| tarsus (depressor, levator; front only) | 0 / 0 | 0 / 0 | | | | |
| ltm (grip) | 0 / 0 | 0 / 0 | 0.1 / 0.1 | 0 / 0 | 0 / 0 | 0 / 0 |
| tergotrochanter (jump) | **18.4 / 16.7** | 0.2 / 0 | 0 / 0 | 0 / 0 | 0.1 / 0.1 | 0.1 / 0 |

- **the flexors are silent.** every tibia flexor on every leg, the largest motor group in the cord, at 0.0 Hz walking and standing; the grip and
  tarsal muscles too. the mid-leg tibia extensors carry the cord: two cells at 103 and 78 Hz on the left, 75 and 10 on the right; the mid-leg
  anterior rotators at 29-65 Hz. and those are *higher standing than walking*. the front-left jump muscle at 13-30 Hz on three of four cells,
  its right twin at 0.
- **no rhythm.** the spectral peak of each leg's total rate scatters (21, 14, 1.2, 1.7, 1.2, 11 Hz walking) and is no sharper walking than
  standing (x8-11 the band median in both).
- **no phase.** every leg correlates with every other at lag 0, all positive (+0.19 to +0.44): one common dose moving the whole cord together.
  tripod would put L1-R1, L1-L2 in anti-phase; nothing is.
- **antagonists** at the coxa alternate weakly in the mid and hind legs (-0.25 to -0.36 at 30 ms); every other joint is flat, because one side
  of it is silent.
- **left minus right per leg against his turning:** -0.05 (T1), -0.10 (T2), -0.22 (T3); the summed cord against his speed +0.41, by construction.

so the cord under a tonic walking command is a posture, mid tibiae extended and mid coxae protracted, that rises and falls with the dose. no
stepping in it. the neck was a hum; the legs are a stance.

**why (the table, signed):** leg motor neurons get balanced input (tibia extensor 3,313 excitatory / 2,354 inhibitory synapses per cell;
anterior rotator 4,465 / 3,527; tibia flexor 786 / 599; the accessory flexors, ltm and tarsal cells under 300 each: the distal muscles are
thinly connected in this file, worth checking against Azevedo 2024). DNg100's own 1,870 synapses land on the coxa (retract 621, protract 420),
the mid-leg tibia extensors (218) and the trochanter depressors (151), and barely on a flexor (tibia flex 43, trochanter levate 65): the command
excites the stance muscles directly and the swing muscles not at all. and the third-largest input to the tibia flexors is DNg105, the brake,
which is purely inhibitory onto every leg muscle (-8,700 synapses) and largest on exactly the flexors (-1,890). two hypotheses for the silence:
nothing excites the flexors under this command, or the brake holds them down tonically. two 30 s arms running: the flexors' seven largest inputs
logged under the defaults, and the same with `--silence DNg105`.

(a query error, kept: my first input census read the weight's sign and found "0 inhibitory synapses on every motor neuron"; the brain file keeps
weights unsigned and the sign per presynaptic cell. redone with the sign array before anything was concluded from it.)

**the arms (21:46 PDT; 30 s, seed 11, the defaults; the tibia flexors' seven largest inputs and the extensors' three logged):**

| Hz per cell, L / R | defaults | `--silence DNg105` |
|---|---|---|
| tibia flexor (37) / acc. flexor (47) | 0.0 / 0.0 | 0.0 / 0.0 |
| tibia extensor (12) | 30.7 / 16.8 (one cell 97) | 32.3 / 16.5 |
| DNg100 (the walking command, driven) | 60.3 / 58.7 | 59.8 / 61.2 |
| DNg105 (the brake, driven) | 22.2 / 22.1 | 22.4 / 21.8 |
| the flexors' excitatory inputs: IN21A004, IN03A004, IN20A.22A009, IN03A031 | 0.0, 0.0, 0.0, 0.0 (one spike in 30 s among 40 cells) | the same |
| the flexors' inhibitory inputs: IN16B016, IN09A002, IN21A003, IN21A002 | 48.5 / 51.1, 49.7 / 59.3, 11.8 / 17.3, 5.0 / 9.8 | the same |
| the extensors' inhibitory inputs: IN19A005, IN08A007, IN13A006 | 9.2 / 10.7, 9.0 / 10.5, 16.6 / 9.7 | the same |

- **arm B is void, and says something anyway.** DNg105 fired identically with its threshold "out of reach", because it is a *driven* cell:
  the feeding state marks the brake population driven (pair.py line 225), and a driven cell spikes from its rate and never from its membrane.
  aligned with the feeding array: 77 Hz per cell in the 80 chunks he fed (100 nominal), 0.0 in the other 220. so the brake is a pure input
  (its own wiring never fires it: the "measured brake" of 09-18 is a puppet string, which §P should say), the lesion flag cannot touch a driven
  cell (noted on `--silence`), and outside feeding the brake was already silent while the flexors stayed at zero. **the brake is not why.**
- **the flexors are silent because nothing excites them.** their four largest excitatory premotor types are dead in the run (one spike in
  thirty seconds), while their inhibitory premotor types run at 50-60 Hz (IN16B016, IN09A002) and 5-17 Hz (21A). the tibia extensors' inhibitors
  are at 9-17 Hz and the extensors fire anyway, one cell at 97 Hz. the posture is the sign structure of the cord under a tonic dose: the
  command excites the extensors and the coxa directly; the flexors' excitation is two synapses further in and never lights.
- the save crashed on both first arms (an empty per-frame array reshaped to zero rows: my new save path; the oracle logs no cells so it could
  not see it); fixed, both rerun, the oracle rerun on the fix.

next (the question the neck's answer set): what should drive IN21A004 / IN03A004 / IN20A.22A009 / IN03A031 in life, and what does in the
table. if it is the proprioceptors (the swing-phase afferents: the femoral chordotonal's flexion-sensitive cells, the tarsal load release), the
cord's rhythm is closed through the legs, not held in the cord, which is Bidaye 2018's reading of the fly and the build order of §Q 4e: legs first.

**what should drive the flexors' premotor cells (21:49 PDT; the table, signed):** IN21A004 (6 cells, cholinergic; 2,421 excitatory /
1,806 inhibitory synapses per cell) is excited by IN17A016 (+917), IN03A059, IN04B032 and, directly, the femoral chordotonal's claw cells
SNpp51 (+576) and the proprioceptive class as a whole (+129 per cell); inhibited by IN21A002, IN13A002, IN13A005, IN13B011. IN03A004 (6,
cholinergic; 3,585 / 3,564) likewise: IN17A016 (+1,712), IN01A005, IN19B003 against IN12B003, IN08A008, IN13A002. and the walking command
itself excites the flexors' inhibitor: DNg100 -> IN09A002 (GABA, +1,026), which runs at 50-60 Hz in the run. so on paper the tonic command
holds the flexors down and their excitation waits on premotor cells two synapses in, with a direct proprioceptive line (the claw) among
their inputs. that is the swing-phase circuit of Bidaye 2018 / Agrawal 2020 as far as the table can say it: closed through the leg.

**a diagnostic before any body** (21:49): `--proprio 100`, the old tripod rule (the leg-nerve proprioceptive class per leg, class-filtered,
17-138 cells per leg, a 10 Hz sine per leg in two tripods), 60 s, seed 11, the defaults otherwise, all leg motor types per frame; the 90 s
probe above is its control. the question: does phasic proprioceptive input wake the flexors and put a phase between the legs. a stand-in
gait driving the afferents, labelled, not a default: it says whether the cord's rhythm is closable through the legs, which is what §Q 4e builds.
two errors on the way, kept: (1) the rule evaluated its sine at the chunk's end time, and chunk ends fall on the 10 Hz period, so every leg
got a constant (the code's own note said "to be fixed as its own change"; fixed: the frame's time); (2) my fix dropped a closing paren, the
first rerun died at import, the oracle was restarted on the compiled file.

**the diagnostic's answer (21:57 PDT; `--proprio 100`, 60 s, seed 11; walking 70 % of frames at 0.20 m/s; against the 90 s probe):** nothing
moves. the tibia flexors 0.0 / 0.0 on all six legs; the posture the same to within noise (mid tibia extensors 99 / 79 and 48 / 38 walking /
standing, mid coxa protractors 40-55, front trochanter depressors 16, the left jump muscle 19); the coxal antagonists -0.14 to -0.32 as
before; spectral peaks scattered and no sharper walking than standing; every inter-leg pair positive at lag 0 except L3-R3 at -0.22 with a
30 ms lag, one pair on one seed, not called. the afferents were driven (the floor's 15 Hz plus a tripod sine of up to ~37 Hz at his pace,
100 nominal x 0.85 x pace 0.44), and the claw's line onto IN21A004 is 129 of its 2,421 excitatory synapses per cell: a small handle, and it
did not lift. so at this dose the cord's rhythm is not closable through the afferents alone.

**what this says, and what it does not.** in life a headless fly's cord steps when a walking DN is driven (Bidaye 2020: BDN2 activation
walks decapitated flies), so a cord that will not pattern under a tonic DNg100 dose is a failure of the *model*, not a hole in the wiring:
the premotor network that should turn a tonic command into alternation is present (its sign structure is right there: the command excites
the extensors and the flexors' inhibitors; the flexors' excitation waits two synapses in), but nothing in a memoryless LIF at one uniform
constant makes it swing. half-centre oscillators need a fatigue term: adaptation or depression. that is 5c's refreeze day (`--std all`, the
Tsodyks-Markram rule on every synapse with the calibrations redone), which was queued for the wings and turns out to be the legs' question
too. queued as the next single variable on this row: the 90 s probe under `--std all` (the raw calibrations, no refreeze), the same analysis,
before any body. the body is built regardless (nate: the posture is the honest output, flailing included), and with the flexors silent the
first body will lie on the floor, which is the finding stage 2 of §Q 4e is for.

**depression on every synapse (22:13 PDT; `--std all`, 90 s, seed 11, the raw calibrations, all leg motor types per frame; against the 90 s probe):**

- **the cord goes quiet.** every muscle group on every leg at 0-3 Hz per cell; the posture is gone (mid tibia extensors 0.9 / 1.5 from 94 / 45;
  mid coxa protractors 2.1 / 0.3 from 44 / 51); the flexors still 0.0. the antagonists are flat or weakly positive. left minus right per leg
  now tracks his turning at -0.25 / -0.54 / -0.50 (front / mid / hind), which is new and worth a look once the readout is honest.
- **his "walking 84 % of frames at 0.40 m/s" is the pace readout, not the cord.** the standing tonus it divides by was calibrated on a
  depressed cord near zero, so the sum reads as full speed while the legs are silent: the calibration break 5c was queued for, measured on the
  legs. no behavioural number from this run counts.
- **a 10.0 Hz beat in the left mid and hind legs, thirty and sixty times the band median, is an artefact.** the rate by frame-within-chunk
  (spikes per frame summed over the leg, the whole run): L3 0.19 0.14 0.09 0.16 0.17 0.18 0.17 0.26 0.37 0.30, a dip after every chunk
  boundary and a climb to the eighth frame, 4.2x peak to trough, the same shape in all four mid and hind legs (2.3-4.2x). the chunk is 100 ms.
  a cord that stepped would drift against the chunk; this one is nailed to it. **and the control carries the same shape at a tenth of the size**
  (1.1-1.2x, the same dip at frames 5-8 in L2): the world updates once a chunk (the eye's still chunk, the wheel and the pace, the goal) and the
  cord feels the step. small under the tonic posture, dominant once depression takes the posture away. this is a seam artefact in every run,
  now measured; the fix is per-frame updates or interpolation within the chunk, queued.

so fatigue on every synapse, as the engine has it (u 0.08, tau 480 ms, uncalibrated), does not make the cord step; it makes it quiet, and
uncovers the chunk seam. the half-centre question is not closed by this: the rule's constants are the wings' (5c), the calibrations are broken
under it, and the headless preparation (§Q 4f) is where the dose and the constants can be swept cheaply. the answer tonight is "not like this."

**oracle (22:18 PDT), on the loop with `--log-frames`, the empty-array fix and the tripod rule on frame time: PASS, v1 + v2, eight configurations, none differing (read from the log).** committed.

## the headless preparation (22:21 PDT; §Q 4f; nate: "if walking is a reflex that works without the head, we may be able to work on that in isolation")

`scripts/build_cord.py` cuts the cord out of `brain_whole.npz`: 23,074 cells (the vnc superclasses, the ascending cells, and the 1,310
descending neurons kept as the inputs they are in a decapitated fly), 1,117,963 edges (22.6 % of the synapses); 130,465 brain-side inputs
to the descending neurons cut. `world/cord.py` runs it with no eye, no body and no world: the tonic floor's cord rows (the leg proprioceptors
at 15 Hz), the walking command on DNg100 at a dose after a 2 s warm-up, every leg motor neuron per frame, `--std off|pair|all` with `--std-u`
and `--std-tau`, `--silence`, the same engine and constants. **30 s of cord runs in 5 s of wall clock** (the whole fly: ~8 s per second):
forty times cheaper per arm. `experiments/gait.py` reads it (legs mapped by bodyId now, so either brain file works; no pose: frames after
2 s count as walking).

**the first three arms (30 s, seed 11):**

| Hz per cell | the cord at the record's dose (DNg100 100 Hz) | the same, `--std all` | the cord at rest (no command) |
|---|---|---|---|
| whole cord / leg MNs | 1.13 / 1.96 | 0.53 / 0.08 | 0.64 / 0.27 |
| leg MNs above 1 Hz | 52 of 373 | 9 | 21 |
| tibia flexors, all legs | **0.0** | 0.0 | 0.0 |
| mid tibia extensors L / R | 36.3 / 7.9 | 0 / 0 | 1.1 / 0.1 |
| hind trochanter depressors | 12.6 / 13.2 | 0.2 / 1.0 | 0.5 / 1.5 |
| hind coxa retract L / femur reductor L | 14.0 / 11.5 | 0 / 0 | 0.5 / 0.4 |
| inter-leg correlation | all positive at lag 0 (+0.2 to +0.5) | sparse | sparse |
| frame-within-chunk profile | x1.2-1.4, no shape | | |

- **the cord alone gives the whole fly's answer: a posture.** the same muscles (mid tibia extensors, the coxa, the hind trochanter depressors),
  the same silent flexors, the same everything-together at lag zero, at a third the rate (36 Hz where the whole fly's L2 extensor sat at 94),
  because the other descending neurons the brain drives (DNb05 and the rest) are silent here. so the preparation is faithful enough to
  the whole fly's result to sweep on, and cheap enough to sweep.
- **no chunk seam in the cord** (x1.2-1.4 with no consistent shape, against x4 under depression in the whole fly): the seam is the world's
  per-chunk update, as §Q 4g says, not the engine.
- **depression at the engine's constants (u 0.08, tau 480 ms) silences the cord**, as it did the whole fly.
- the spectral "peaks" at 17-20 Hz (x10-22 the median) in the cord are single cells firing regularly at their own rate, a line at the rate,
  not a population beat; the analysis needs a rhythm measure that a tonic cell cannot produce (next: the spectrum of the leg's rate with each
  cell's own line removed, or the pairwise phase between cells of one leg).

**the sweep (22:25 PDT; the cord, 30 s, seed 11, one variable per arm against the cord at the record's dose; `experiments/gait_score.py`:
MN Hz = mean per leg motor neuron, active = above 1 Hz, flex = tibia flexors Hz per cell, antag = the most negative antagonist correlation,
legs = the most negative inter-leg correlation at lag 0, beat = a cross-spectral rhythm measure (E; noise ~1-4)):**

| arm | MN Hz | active | flex Hz | ext Hz | antag | legs | beat |
|---|---|---|---|---|---|---|---|
| rest (no command) | 0.27 | 21 | 0.00 | 0.5 | -0.04 | +0.00 | 3.7 |
| DNg100 50 Hz | 0.99 | 53 | 0.00 | 4.4 | -0.12 | +0.00 | 2.9 |
| **100 Hz (the record's dose)** | 1.96 | 52 | 0.00 | 9.3 | -0.16 | +0.00 | 4.3 |
| 200 Hz | 3.83 | 58 | 0.01 | 17.5 | -0.36 | +0.00 | 6.1 |
| 400 Hz | 6.35 | 65 | 0.04 | 29.0 | -0.28 | +0.00 | 15.1 (R2, 22 Hz) |
| w 0.22 mV | 2.81 | 70 | 0.01 | 14.1 | -0.26 | +0.00 | 6.1 |
| w 0.275 mV | 9.02 | 87 | 0.03 | 47.8 | -0.40 | +0.00 | 4.8 |
| std all, u 0.08 tau 480 (the engine's) | 0.08 | 9 | 0.00 | 0.1 | -0.00 | -0.00 | 2.9 |
| std all, u 0.02 tau 480 | 0.71 | 41 | 0.00 | 2.4 | -0.10 | +0.00 | 3.8 |
| std all, u 0.08 tau 100 | 0.65 | 38 | 0.00 | 2.1 | -0.05 | +0.00 | 4.5 |
| std all, u 0.08 tau 2000 | 0.00 | 0 | 0.00 | 0.0 | | | |
| std all, u 0.20 tau 480 | 0.00 | 0 | 0.00 | 0.0 | | | |
| std all, u 0.02 tau 100 | 1.48 | 54 | 0.00 | 6.5 | -0.14 | +0.00 | 4.0 |
| std all (engine's) at 400 Hz | 0.09 | 9 | 0.00 | 0.1 | -0.02 | +0.00 | 3.0 |
| std all u 0.02 tau 100 at 400 Hz | 4.00 | 55 | 0.00 | 18.1 | -0.41 | +0.00 | 18.1 (R2, 23 Hz) |

- **the flexors never wake.** 0.00-0.04 Hz per cell across the dose (50-400 Hz), the constant (0.185-0.275) and the depression's box
  (u 0.02-0.2, tau 100-2000 ms). the extensors and the coxa scale with the dose and the constant (the posture gets louder); depression
  at the engine's constants or stronger silences the cord, weaker depression (u 0.02, tau 100) leaves the posture as it was.
- **no leg ever anti-phases another** (the most negative inter-leg correlation is 0.00 in every arm). the coxal antagonists alternate
  weakly and more at higher dose (-0.16 to -0.41), which is the only gait-shaped number in the box, and it is at the hip alone.
- the "beat" at 22-23 Hz in R2 at 400 Hz is being checked against two tonic cells at one rate (the measure's known blind spot).

so fatigue, as a uniform rule on every synapse, does not make this cord step at any constant in the box; nor does the dose; nor the
synaptic constant. the half-centre is not one missing ingredient away. what the sweep leaves standing: the flexors' excitatory premotor
cells wait on input the tonic command does not provide, and in life that input is the legs' own unloading (the campaniform swing trigger,
Zill 2024 / Dallmann 2025): a leg that has pushed and been unloaded is a leg allowed to lift. the floor holds every leg's load at 15 Hz for
ever: a fly standing on six loaded legs, told to walk. next arms: the load signal off, high, and the floor off entirely.

**the load arms (22:26 PDT; the cord, 30 s, seed 11; the floor's rate on the leg proprioceptors, 15 Hz = standing load):**

| arm | MN Hz | active | flex Hz | ext Hz | antag | legs |
|---|---|---|---|---|---|---|
| load 15 Hz (the floor), DNg100 100 Hz | 1.96 | 52 | 0.00 | 9.3 | -0.16 | +0.00 |
| **load 0**, 100 Hz | 2.25 | 65 | **0.20** | 4.8 | -0.22 | +0.00 |
| load 60, 100 Hz | 3.77 | 64 | 0.05 | **31.7** | -0.16 | +0.00 |
| no floor at all, 100 Hz | 2.29 | 66 | 0.21 | 4.9 | -0.18 | +0.00 |
| load 15, 400 Hz | 6.35 | 65 | 0.04 | 29.0 | -0.28 | +0.00 |
| **load 0**, 400 Hz | 6.16 | 73 | **0.43** | 24.5 | -0.37 | +0.00 |
| load 60, 400 Hz | 6.90 | 61 | 0.14 | 43.0 | -0.38 | +0.00 |

- **the load signal is the lever, with the right sign.** more load drives the extensors (9 -> 32 Hz per cell at 60 Hz of load) and holds
  the flexors down; *no* load lets the tibia flexors fire for the first time in this whole investigation: 0.20 Hz per cell at the record's
  dose, 0.43 at four times it. small, but the first non-zero, and in the direction life has it (load -> stance muscles; unloading -> swing;
  Zill 2024, Dallmann 2025). the floor's 15 Hz on every leg for ever is a fly standing on six loaded legs and told to walk, and the cord
  answers correctly: it stands harder.
- (the R2 "beat" at 22 Hz under 400 Hz is two trochanter flexor cells at 109 and 118 Hz with a shared modulation (ISI CV 0.5): two cells of
  one type, not a leg; left as unresolved.)

so the closed loop through the legs is the thing: stance loads the leg, the load holds stance, the push unloads it, the unloading releases
swing. the cord cannot do this against a constant load and there is no honest way to give it a phasic load except from a body, or from a
labelled treadmill (a tripod-timed load on the campaniform cells alone, the position cells at their floor) as the headless diagnostic that
says whether unloading alone is enough. the treadmill first, because it is ten seconds; the body regardless.

**the treadmill and the constant (22:29 PDT; the cord, 30 s, seed 11):**

| arm | MN Hz | active | flex Hz | ext Hz | antag | legs | beat |
|---|---|---|---|---|---|---|---|
| treadmill 2 / 5 / 10 Hz steps, load 15 in stance, 0 in swing, DNg100 100 Hz | 2.0 | 63-65 | 0.02-0.03 | 5.7-6.7 | -0.17 to -0.22 | +0.00 | 4-5 |
| treadmill 5 Hz, 400 Hz | 6.3 | 74 | 0.11 | 27.6 | -0.35 | **-0.27** | 30 (at 5.1 Hz: the input's) |
| treadmill 5 Hz, load 60 in stance, 100 Hz | 2.5 | 63 | 0.01 | 16.1 | -0.13 | -0.11 | 16 (5.1 Hz) |
| treadmill 5 Hz, no command | 0.2 | 20 | 0.00 | 0.2 | | -0.09 | |
| w 0.35 mV, 100 Hz | 17.5 | 93 | 0.43 | 72.1 | -0.51 | +0.00 | 9 |
| w 0.50 mV, 100 Hz | 24.0 | 94 | 2.68 | 65.6 | -0.35 | +0.00 | 8 |
| w 0.50, load 0 | 24.0 | 94 | 2.63 | 70.3 | -0.65 | -0.00 | 4 |
| w 0.35, **no command** | 15.2 | 93 | 0.29 | 72.0 | -0.47 | +0.00 | 8 |

- **the treadmill makes the legs alternate, and it is the treadmill.** the inter-leg correlation goes negative for the first time (-0.27 at
  the high dose) and the beat sits exactly at the step frequency: the extensors follow the load (the load reflex, phasic now), so
  tripod-timed load gives tripod-timed extensors. the flexors stay at 0.02-0.11 Hz: unloading half the cycle releases less swing than
  constant unloading did (0.20). **unloading alone is not the trigger.**
- **the constant is not it either** (nate: "could our low mV constant be a factor?"): at 0.35 and 0.50 mV the cord runs away, 93-94 of the
  373 leg motor neurons active *with or without the command* (15 Hz per cell at 0.35 with DNg100 silent), the extensors at 65-72 Hz per cell
  and the flexors at 0.3-2.7: the posture, twenty-five times louder, self-sustaining, command-blind. the constant makes the cord run away
  before it makes a flexor matter. the whole fly cannot even go there (the pharyngeal runaway at 0.275).

**where the headless night leaves the leg row.** under a tonic dose on the walking descending neuron, this cord holds a stance and cannot
be pushed into swing by the dose (50-400 Hz), the constant (0.185-0.5), depression (u 0.02-0.2, tau 0.1-2 s), the load (0-60 Hz, constant
or tripod-timed) or any pair of them tried. the only things that moved the flexors at all were unloading (0.2-0.4 Hz) and a runaway
constant (2.7). what remains, in the order i would test them, each in the cord first:
1. **the command is a population, not a cell.** walking in life recruits many descending neurons together (Braun / Sapkal 2024: the
   walking DN population; DNa01 / DNa02, DNp09, oDN1, DNg13, the DNge cells that drive IN17A016 and IN16B016 above). one DN at 100 Hz is
   Bidaye's optogenetic experiment, and the paper's fly walked; ours does not. a census of which DNs excite the flexors' premotor cells
   (IN17A016, IN01A005, IN19B003, IN03A059) and a dose on that set is a table query and ten seconds of cord.
2. **what the model lacks that a cord has:** electrical synapses (gap junctions are not in any chemical connectome and central pattern
   generators lean on them), intrinsic currents (plateau potentials, post-inhibitory rebound: the half-centre's other classic ingredient,
   absent from a LIF), neuromodulation. each is a labelled engine change with a source, and each is 5c's kind of day.
3. **the body.** the honest closure regardless: a load that is the leg's own, from muscles the cord actually drives, on a floor. the first
   body lies down, and that is the record's starting frame for the row.

**the command as a population (22:32 PDT; the cord; census then arms):** two-synapse excitatory reach DN -> interneuron -> tibia flexor MN
against the same onto the extensors: DNg100 is extension-biased (0.09 / 0.20); DNge035 (0.40 / 0.24; the largest exciter of IN21A004,
IN20A.22A009, IN03A031 and IN19B003), DNge049 (0.27 / 0.15), DNg95 (0.21 / 0.00), DNge038 (0.20 / 0.00), MDN (0.19 / 0.09; the moonwalker,
backward walking, which a headless fly obeys: Bidaye 2014), DNp02 / DNp06 / DNp11 (escape-side, flexor-only) are flexion-biased.

| arm (30 s, seed 11, 100 Hz on the named cells) | MN Hz | active | flex Hz | ext Hz | antag | legs |
|---|---|---|---|---|---|---|
| DNg100 (the record's command) | 1.96 | 52 | 0.00 | 9.3 | -0.16 | +0.00 |
| DNge035 | 1.40 | 47 | 0.00 | 9.2 | -0.12 | +0.00 |
| DNg95 | 0.48 | 23 | 0.02 | 0.3 | -0.07 | -0.02 |
| DNge038 | 0.37 | 24 | 0.11 | 0.2 | -0.05 | -0.05 |
| MDN (4 cells) | 2.58 | 58 | 0.08 | 3.4 | -0.36 | -0.09 |
| **the flexor set** DNge035 + DNge049 + DNg95 + DNge038 (8 cells) | 1.68 | 54 | **0.93** | 2.9 | -0.21 | -0.01 |
| the flexor set, load 0 | 1.81 | 48 | **2.72** | 0.7 | -0.16 | -0.02 |
| DNg100 + the flexor set + DNge048 (12 cells) | 2.54 | 70 | 0.57 | 8.6 | -0.26 | +0.00 |

- **the population changes the posture, not the pattern.** the flexor-biased set puts the tibia flexors at 0.93 Hz per cell and the
  extensors down to 3; with the load off, flexors 2.7 and extensors 0.7: the first swing posture the cord has held. DNg100 added back gives
  both at once (0.57 / 8.6), co-contraction, not alternation. no leg anti-phases another in any arm.
- so the cord routes a command to the right muscles (extension DN -> stance, flexion DNs -> swing, with the load reflex on top) and never
  switches between them under tonic input. **the switch is the missing thing**, and nothing on the command side supplies it.
- the table's candidate for the switch runs through the leg: the extension-tuned claw cells of the femoral chordotonal organ (SNpp50) sit
  on IN21A004, the flexors' premotor cell, with 576 synapses: the resistance reflex (extension sensed, flexors answered). if that link is
  live, then stance extends the knee, the claw fires, the flexors lift, the load drops, the command re-extends: an oscillator through the
  body, which is what the body is for. next arm: the claw driven in the cord (`--drive TYPE:HZ`), does it wake the flexors.

**the claw (22:34 PDT; the cord, `--drive TYPE:HZ`; the femoral chordotonal's claw cells held at a rate on top of the floor):**

| arm (30 s, seed 11) | MN Hz | active | flex Hz | ext Hz | antag | legs |
|---|---|---|---|---|---|---|
| DNg100 100 Hz (the record) | 1.96 | 52 | 0.00 | 9.3 | -0.16 | +0.00 |
| extension-tuned claw SNpp50 (62 cells) 50 Hz, no command | 1.05 | 35 | 0.00 | 8.0 | -0.17 | -0.01 |
| SNpp50 50 Hz + DNg100 | 2.28 | 50 | 0.00 | **18.0** | -0.20 | +0.00 |
| SNpp50 150 Hz + DNg100 | 3.25 | 53 | 0.00 | **31.7** | -0.47 | +0.00 |
| SNpp50 150 Hz + DNg100, load 0 | 3.07 | 45 | 0.00 | 26.2 | -0.53 | +0.00 |
| flexion-tuned claw SNpp51 (32) 50 Hz + DNg100 | 2.08 | 57 | 0.00 | 7.9 | -0.17 | +0.00 |
| hook SNpp39 + SNpp41 (61) 50 Hz + DNg100 | 2.02 | 54 | 0.00 | 10.6 | -0.15 | +0.00 |

- **the claw drives extension, never flexion.** the extension-tuned cells at 50 and 150 Hz double and triple the extensors (9 -> 18 -> 32 Hz
  per cell) and leave every flexor at 0.00, with or without the load. the 576 synapses onto IN21A004 do not carry against whatever else
  the claw excites. in a resting animal this is the wrong sign (the resistance reflex: extension sensed, flexors answered); in a walking
  animal the reflex reverses to assistance (Bässler's reflex reversal; extension sensed, extension helped) and the cord under a walking
  command answering this way is not obviously wrong. either way it is not a switch.
- so, tonight's last null: the femoral position signal does not release swing in this cord, at rest or under the command. the flexors
  have fired under exactly one condition all night: a flexion-biased descending population, and then as a posture.

**where the row stands at the end of the headless night.** the cord routes commands to the right muscles and holds whichever posture it
is told: extension DN -> stance, flexion DNs -> swing, load -> stance, and nothing switches. the candidates for the switch, in order:
(1) engine physics a cord has and a LIF lacks: post-inhibitory rebound and plateau currents (the half-centre's classic ingredients besides
fatigue), electrical synapses (absent from the chemical connectome); each a labelled engine change with a source, tested in the cord in
seconds; (2) the walking command as it is in life: a population with a *time course* (the DN population of Braun / Sapkal 2024, and the
brain's own modulation of it, which the headless fly lacks and Bidaye's optogenetic fly also lacked, and walked); (3) the body, which
closes the load loop honestly and is built regardless (§Q 4e). the headless preparation is the place for (1) and (2): forty times cheaper,
and it reproduced the whole fly's answer.

## the switch (22:37 PDT; nate: "you have some targets to hunt. go for it")

two intrinsic currents a real neuron has and this LIF does not, added to the engine as labelled terms on the external-current path
(`world/fastlif.py`; the compiled membrane kernels untouched; off by default, so the oracle's runs are bit for bit what they were: running):

- **spike-frequency adaptation** (`--adapt B:TAU`): a per-cell variable a (mV) that jumps by B on each spike and decays with TAU, subtracted
  from the drive. the AdEx model's w in voltage units (Brette & Gerstner 2005); ubiquitous in insect neurons; the constants for fly cells
  are not tabulated per type (van der Veen 2025 use tau_w 50 ms, b 264 pA for insect afferents), so B and TAU are swept and marked (E).
- **post-inhibitory rebound** (`--rebound G:TAU`): a per-cell variable r that follows G x (the hyperpolarisation below rest) with TAU and is
  added to the drive: a sag while inhibited and a push that outlasts the inhibition, the shape of an I_h. present in Drosophila motor
  neurons (larval: Ih documented; adult leg MNs: not measured, (E)).

both are the classic half-centre ingredients besides synaptic fatigue (Brown 1911; Marder & Bucher 2001: reciprocal inhibition needs a
release, from adaptation, depression or rebound, to alternate). the cord's wiring has the reciprocal inhibition (the 13A / 13B hemilineages
between flexor and extensor premotor circuits, Cheong 2024); tonight's sweep says depression alone does not release it. arms: each term over
a box, under the single command (DNg100) and under the population that co-contracts (DNg100 + the flexor set), which is the arm that can
turn co-contraction into alternation if anything can.

**the arms (22:43 PDT; the cord, 30 s, seed 11; `experiments/gait_score.py`):**

| arm | MN Hz | active | flex Hz | ext Hz | antag | legs |
|---|---|---|---|---|---|---|
| DNg100 alone (the record) | 1.96 | 52 | 0.00 | 9.3 | -0.16 | +0.00 |
| + adaptation b 0.5 / 2 mV, tau 100 / 300 ms (four arms) | 0.97-1.78 | 63-69 | 0.00-0.04 | 2.3-6.6 | -0.04 to -0.14 | +0.00 |
| + rebound g 0.5 / 2, tau 50 / 150 ms (four arms) | 2.2-3.4 | 66-100 | 0.00-0.10 | 9.0-10.0 | -0.18 to -0.33 | +0.00 |
| + both (b 1 tau 200; g 1 tau 100) | 2.06 | 89 | 0.11 | 4.6 | -0.16 | +0.00 |
| the population DNg100 + the flexor set (co-contraction) | 2.54 | 70 | 0.57 | 8.6 | -0.26 | +0.00 |
| + adaptation (four arms) | 1.9-2.7 | 76-91 | 0.48-0.61 | 5.0-9.4 | -0.12 to -0.26 | +0.00 |
| + rebound (four arms) | 2.9-4.1 | 80-110 | 0.62-0.78 | 10.2-11.6 | -0.25 to -0.33 | +0.00 |
| + both | 3.28 | 104 | 0.75 | 8.4 | -0.30 | +0.00 |

- **neither current switches anything.** adaptation quietens the stance (the extensors 9 -> 2-7 Hz) without waking the flexors; rebound
  recruits cells (52 -> 100-110 active) into the same posture; under the co-contracting population both terms leave flexors and extensors
  on together at every constant, and no leg anti-phases another anywhere (the inter-leg column is +0.00 in all eighteen arms).
- with synaptic depression (the sweep above), that is all three classic release mechanisms of a half-centre failing on this wiring at
  these constants. the question underneath them is structural: **is there a half-centre in the table at all**, as reciprocal inhibition
  between the flexor-side and extensor-side premotor pools? a query, next.

**the half-centre is in the table (22:43 PDT; the cord file, signed synapses between the ten largest premotor types on each side of the knee):**

| from -> to | excitatory | inhibitory |
|---|---|---|
| flexor-exciters -> extensor-**inhibitors** | **+13,543** | |
| extensor-exciters -> flexor-**inhibitors** | **+9,968** | |
| flexor-inhibitors -> extensor-inhibitors | | **-13,006** |
| extensor-inhibitors -> flexor-inhibitors | | **-15,368** |
| flexor-inhibitors -> extensor-exciters | | -1,660 |
| extensor-inhibitors -> flexor-exciters | | -666 |
| flexor-exciters -> flexor-exciters (self) | +8,715 | |
| extensor-exciters -> extensor-exciters (self) | +2,459 | |
| between the exciter pools | +572 / +2,354 | |

(flexor-exciters: IN21A004, IN03A004, IN20A.22A009, IN03A031, IN21A022, IN20A.22A010, IN03A039, IN19B012, IN21A020, IN17A016, all
cholinergic; flexor-inhibitors: IN21A002, IN19A015, IN14A004, IN13A005, IN21A006, IN12B018, IN13A001, IN13A002 + DNg105, DNge079, GABA
and glutamate; extensor-exciters: IN20A.22A007, IN04B031, IN12A001, IN04B027, IN20A.22A036 / 005 / 004, IN04B037, IN19B003, IN01A038;
extensor-inhibitors: IN19A005, IN08A007, IN13A006 / 014 / 015 / 045 / 042, IN08A005, IN16B077 + DNg105.)

each side's exciters drive the *other* side's inhibitors, and the two inhibitor pools inhibit each other: reciprocal inhibition through
interneurons, Brown 1911's circuit as Cheong 2024 drew it for the 13A / 13B hemilineages. what it does under a tonic command is
winner-take-all: the side the command favours drives the other side's inhibitors, which also silence their own opponents, and the loser's
exciters never light (the run of record exactly: extensors on, IN09A002 / IN16B016 at 50-60 Hz, IN21A004 / IN03A004 dead). a half-centre
alternates only when the winning side tires; fatigue on *every* synapse silenced the cord instead. the mechanism-shaped test (nate, 09-21:
depression on targeted cells over gates): **depression on the two inhibitor pools alone**, so the winning inhibition fades and the other side
can take over; the exciter pools as the control. `--std` takes a type list now.

**depression on the inhibitor pools alone (22:49 PDT; the cord; 115 cells of the two inhibitor pools, or 164 of the two exciter pools as the control):**

| arm | flex Hz | ext Hz | antag | legs |
|---|---|---|---|---|
| DNg100 (the record) | 0.00 | 9.3 | -0.16 | +0.00 |
| + std on the inhibitor pools, u 0.08 / 0.2 / 0.5, tau 0.5-2 s (four arms) | 0.03-0.18 | 11.5-18.5 | -0.14 to -0.18 | +0.00 |
| + std on the exciter pools (control, two arms) | 0.00 | 3.5 | -0.12 | +0.00 |
| the population (co-contraction) | 0.57 | 8.6 | -0.26 | +0.00 |
| + std on the inhibitor pools (four arms) | 1.19-2.20 | 10.0-15.8 | -0.21 to -0.23 | +0.00 |
| + std on the exciter pools (control) | 0.38 | 6.1-6.6 | -0.12 | +0.00 |

- **tiring the inhibitors disinhibits both sides.** flexors and extensors both rise (to 2.2 and 15.8 under the population), together, and
  no leg anti-phases another. the control (tiring the exciters) lowers both. no switch.
- **why, from the table above:** the inhibitor pools barely touch the opposing *exciters* (-666 and -1,660) against what they put onto each
  other (-13,000 / -15,000) and onto the motor neurons directly. so the reciprocal inhibition in this cord acts at the motor neuron and the
  inhibitor level, while the exciter pools are driven from above (the descending neurons) and from the leg (the claw onto IN21A004), not
  by each other's silence. a circuit like that does not oscillate on its own under a steady command; it holds whichever side is fed, and
  it alternates when its *inputs* alternate: the descending population with a time course, and the leg's own sensors through a body.
  which is what deafferented insects do: they walk badly (Bässler & Büschges 1998; in the fly, Mendes 2013 on proprioceptive loss).

**the switch, at the end of the hunt.** four release mechanisms tried on a half-centre that is present in the wiring (synaptic
depression everywhere, on the inhibitors alone, spike-frequency adaptation, post-inhibitory rebound; 40 arms in the cord, 5-25 s each), none
switches it, and the table says why: the two sides do not silence each other's exciters. the honest reading is that this cord is a router
with a load reflex, and the rhythm in life is closed through the leg and shaped from above. **the body moves to the front of the queue.**

## the first body (22:57 PDT; §Q 4e stage 1-2 on one leg; nate: "if you start to get what you'd at least describe as twitching motion, I would like to begin watching")

`flygym` 2.1.0 installed (NeuroMechFly v2's package; it now ships the DeepMind body and FlyMimic's musculoskeletal leg, Özdil 2026, as
`MusculoskeletalFly`: a tethered thorax with the left front leg on fifteen Hill-type muscles, MuJoCo at 0.1 ms, 0.7x real time on this
laptop). its fifteen muscle names are the table's muscle names, so the map from his motor neurons is by name: promotors, remotor, the
rotators, the adductor, trochanter flexors / extensors, tibia flexor / extensor; unmapped (no muscle or joint in FlyMimic): the long tendon
muscles, the tarsal muscles, the femur reductor, the jump muscle. `experiments/leg_replay.py`: the cord's per-frame spikes of the 68 left
front-leg motor neurons -> a twitch kernel (difference of exponentials, rise 7 ms, decay 20 ms, peak 21 ms; Azevedo 2020) x a force weight
by input-synapse size within the muscle ((S / S_max)^1.2, the brief's exponent) / a saturation of 10 spike-equivalents -> the muscle's
activation in [0, 1] -> the body, 1 ms control, joint angles recorded, a video rendered. **a replay, nothing fed back.** spikes sit at the
log's 10 ms frames (coarse; the twitch is longer than a frame; noted).

| the cord's arm, 5 s replayed | tibia pitch range (sd) | trochanter pitch range (sd) | coxa yaw sd |
|---|---|---|---|
| at rest (no command) | 89-107 (0.9) | -143 to -137 (0.4) | 1.2 |
| DNg100 100 Hz (the record's dose) | 72-107 (4.9) | -153 to -99 (7.5) | 3.8 |
| DNg100 400 Hz | 36-107 (17.5) | -146 to -86 (14.0) | 4.3 |
| 400 Hz + the 5 Hz treadmill | 36-107 (16.9) | -154 to -94 (13.1) | 4.0 |
| the flexor set, load 0 (the swing posture) | 70-107 (3.6) | -173 to -108 (10.0) | 2.3 |

- **it twitches.** at rest the leg holds still to within a degree; under the command the tibia and trochanter swing tens of degrees, more
  with the dose (a 70 deg tibia range at 400 Hz). the activations are small (the promotors peak at 0.4 of full, most muscles under 0.2)
  because the cord's front leg is quiet, and the movement is the leg answering what little there is.
- `docs/figures/leg_replay_joints.png` (the joint traces across the arms); videos in `world/cord/video/*.mp4` (untracked; 5 s each, the
  scene camera). this is the point nate asked to start watching: `world/cord/video/walk400.mp4` is the loudest.
- what it is not: a leg on the ground (the thorax is anchored: a tethered fly), a loop (the joint angles go nowhere yet), or six legs.
  stage 2 is the NeuroMechFly body on the floor with the same map on all six legs through joint torques; stage 3 feeds its joints and
  loads back as his proprioceptors. and the map's honest gap: FlyMimic's muscle dynamics (tau_act 0.1 ms) are 85x faster than the measured
  8.5 ms half-rise, which is why the twitch kernel is ours and the body's own activation dynamics are left near-instant.

**oracle (23:00 PDT) on the engine with `--adapt` / `--rebound` present and off: PASS, v1 + v2, eight configurations, none differing (read from the log). the engine terms committed.**

## the first loop (23:36 PDT; `experiments/leg_loop.py`: the cord and FlyMimic's left front leg in one process at 1 ms, 0.47x real time)

the leg's tibia angle drives this leg's claw cells (extension-tuned SNpp50 as it extends, flexion-tuned SNpp51 as it flexes, 0-100 Hz over
60 deg either side of 90, (E)), its angular velocity drives the hook cells (SNpp39 flexion / SNpp41 extension, 100 Hz at 300 deg/s, (E)),
and the treadmill can load this leg's other 27 proprioceptors on a clock; the cord's spikes drive the fifteen muscles through the twitch
kernel. **the sensory side of this leg is thin:** 35 proprioceptive cells in the cord for the left front leg, of which 1 extension claw, 3
flexion claw, 3 + 1 hook (the worst-traced leg in the volume; the mid legs carry 127-133 each).

| arm (20 s, seed 11) | LF MN Hz | tibia flexors | tibia extensors | tibia range (sd) | claw drove (ext / flex Hz) | hook drove |
|---|---|---|---|---|---|---|
| DNg100 100 Hz, loop off (a live replay) | 0.57 | 0.01 | 1.25 | 54-97 (7.5) | 3 / 5 | 12 / 14 |
| + position | 0.63 | 0.01 | 1.81 | 50-97 (9.4) | 3 / 8 | 17 / 19 |
| + position + treadmill 5 Hz | 0.58 | 0.00 | 1.78 | 46-97 (9.3) | 3 / 7 | 16 / 18 |
| + treadmill only | 0.56 | 0.00 | 1.25 | 51-97 (8.0) | 3 / 5 | 13 / 14 |
| DNg100 400 Hz, loop off | 3.18 | 0.20 | 12.9 | 36-100 (17.6) | 1 / 49 | 38 / 37 |
| + position | 3.22 | 0.20 | 11.5 | 35-100 (17.3) | 1 / 46 | 38 / 37 |
| + position + treadmill | 3.29 | 0.21 | 11.8 | 34-101 (16.9) | 1 / 48 | 38 / 38 |
| + treadmill only | 3.30 | 0.18 | 14.3 | 35-99 (17.1) | 0 / 52 | 38 / 38 |

- **closing the loop on this leg changes nothing measurable.** the sensory cells fired (the flexion-tuned claw at ~49 Hz with the tibia
  flexed at the high dose, the hooks at 38), the cord's leg output did not move (0.57 vs 0.63 Hz per cell; flexors 0.01 in every arm; the
  joint ranges within noise of the open-loop replay). the leg's own load clock on its 27 load cells did nothing either.
- the reading, with the earlier claw arms: this leg's sensory return is one extension cell and three flexion cells into a cord whose
  flexor premotor cells need thousands of synapses to move, and the treadmill's effect in the whole cord (the inter-leg alternation) came
  from 645 cells on six legs, not 27 on one. **the loop's honest test needs the mid legs**, which are traced (127-133 sensory cells each),
  and a body that has them: the six-legged NeuroMechFly on a floor, its own stance as the load. that was the next build already; this
  makes it the only one.
- the tibia-angle spectral "peak x800-1500" printed by the script is the red spectrum of a smooth angle signal, not a beat; ignore it.
  videos: `world/cord/loop/*.mp4`.

**the lifts (00:03 PDT; nate, watching: "garden_LF ... the leg raises, moves forward or backward, and falls"; "ctl ... strong, decisive extensions, a forward-back component"):**
a lift = the smoothed trochanter pitch more than 15 deg above its resting level (levation). the question: do lifts come at a walking
interval, and does the coxa swing *during* them (a swing phase) rather than at random?

| arm | lifts | lift duration | interval (cv) | coxa yaw change during lifts: sign agreement |
|---|---|---|---|---|
| **him** (`garden_LF`: the run of record's left front leg, 8 s) | 16 | 213 ms | 492 ms (0.93) | 0.12 |
| the cord, DNg100 100 Hz (`ctl`) | 5 | 82 ms | 774 ms (0.59) | 0.20 |
| the cord, 400 Hz | 18 | 113 ms | 256 ms (0.62) | 0.11 |
| the cord, 400 Hz + the 5 Hz treadmill | 16 | 126 ms | 305 ms (0.53) | 0.25 |
| the flexor set, load 0 | 2 | 156 ms | | |
| at rest | 0 | | | |

- **the lifts are real.** discrete trochanter levations, 100-200 ms long, two a second in him, four a second at the high dose, none at
  rest: the leg lifts and drops, and that is more than twitching. it is a burst on the trochanter flexors, and what makes a burst in a
  cord that holds a posture is the next thing to look at.
- **they are not steps.** the interval's coefficient of variation is 0.93 in him (a walking fly's step interval sits near 0.1-0.2), and the
  coxa's swing during a lift has no consistent direction (sign agreement 0.12-0.25; a swing phase protracts every time). the coxa moves as
  much on the ground as in the air. so the eye assembles "raise, move, fall" from a lift and an unrelated coxa wobble. the treadmill arm is
  the most regular (cv 0.53) and the most directional (0.25), which is the clock showing through, and still far from a step.

**what makes a lift (00:13 PDT; 60 s of him, seed 11, the trochanter flexors, their premotor inputs and the walking-side descending
neurons per frame; burst-triggered averages around trochanter-flexor bursts):** the front-left leg's flexors burst 10 times in 60 s
(interval cv 1.8: random), and in the 300 ms before a burst the walking command rises (DNg100 43 -> 51 -> 65 Hz: the command is dosed
through the PFL2 walk gain, so it surges) and the brake with it (DNg105 10 -> 38 -> 45 Hz: he is feeding at those moments); their
premotor exciter IN21A010 goes 11 -> 26. the mid-left leg's flexors "burst" 135 times, but the summed rate's autocorrelation is flat at every
lag from 100 to 500 ms, the loudest cell's spike intervals have cv 0.94, and a burst is 3-4 of 7 tonic cells coinciding: a threshold on
noise, not a rhythm. the right legs' flexors: 0 bursts (the right cord's under-tracing again). **so the lifts nate saw are coincidences on a
few tonic trochanter flexors, plus, on the front-left leg, the command surging with the brake.** no oscillator hides in them.

## the six legs (00:16 PDT; §Q 4e stage 1-2 on the whole body; `experiments/body_signs.py`, `experiments/body_six.py`)

**the body:** NeuroMechFly v2 (flygym 2.1) on flat ground, the legs' 42 active joints on torque actuators (+-30), the claws as adhesion,
MuJoCo at 0.1 ms; 0.43x real time with the replay. **the map, measured not assumed:** each joint of each leg was pushed both ways in
zero gravity and the foot's displacement read (the springs' passive drift cancels in the difference): lifting the foot is the trochanter's
pitch on every leg, shortening the leg is the knee's pitch, swinging the foot forward is the coxa's pitch on the front and mid legs and its
yaw on the hind legs, each with its sign; the adductor's joint is the coxa's roll (front, mid) and yaw (hind; shared with protraction,
noted). `results/body_dof_signs.json`. **the muscles onto the joints:** promotors + anterior rotator vs remotor + posterior rotator on the
swing joint; trochanter flexors vs sternotrochanter + trochanter extensor on the lift joint; tibia flexors vs extensor on the knee; tarsal
levators (Ta levator, and MNml81 / MNhl65 by the serial set) vs depressor on the tarsus; the adductor alone; the long tendon muscles onto
the claw's adhesion (on while they fire). 301 of the 373 leg motor neurons mapped to a joint, 42 to the grip; unmapped: the femur reductor
(the trochanter-femur joint is fused in this body), the jump muscle, and the mid / hind numbered types the brief has not yet assigned
beyond the tarsal levators (19 types; §A's remaining assignments are the next map revision). torque = 10 x (agonist - antagonist) in the
twitch kernel's activation units, (E). the run: the cord's or his motor neurons per frame, replayed.

| arm (thorax height, mm; 0.7 = standing) | joint springs | height at the end | travelled |
|---|---|---|---|
| the cord, DNg100 100 Hz | flygym's (stiffness 10) | 0.69 | 0.8 mm |
| the cord, 400 Hz | flygym's | 0.71 | 0.8 |
| **him** (the run of record's motor neurons, 8 s) | flygym's | 0.72 | 2.3 |
| the cord, DNg100 100 Hz | **the measured passive stiffness** (Wang 2025: ~70x weaker; 0.14) | **0.40** | 0.7 |
| the cord at rest | the measured | 0.44 | 0.7 |

- **on flygym's springs he stands** (`docs/figures/body_six_stands_springs.png`): the springs hold the neutral pose, the cord's torques
  twitch the legs on top, he drifts a millimetre or two. **on the measured springs he lies down** (`body_six_collapses_measured.png`):
  the thorax sinks from 0.7 to 0.4 mm, the legs splay, the belly is on the floor, with the cord's actual output (extensors at 9 Hz per cell,
  flexors silent) and with it at rest alike. that is the honest first frame this row was promised: the brief said a body that stands with
  silent muscles is wrong, and it is; standing in life is tonic slow-motor-neuron drive, and his cord does not supply enough of it at
  0.185 mV under this command to hold a fly up. the stance posture the cord holds is a posture of *rates*, not of force.
- so the first six-legged fly is a fly on the floor, and the number to move next is the one that lifts him: the tonic drive on the slow
  motor units (the standing tonus of the leg row), measured against the body's weight. that is a calibration with a target (a fly that
  stands is a fly whose slow MNs carry its weight; Azevedo 2020: standing is slow-unit drive) and a control (the measured springs), and
  it is the first place the body tells the cord something back.
- videos: `world/body/*.mp4` (the tracking camera). nate wanted to watch when there was twitching; this is a whole fly, twitching, and
  then a whole fly lying down.

**the torque from the measurement (00:19 PDT):** the model's units resolve to the micronewton and the nanonewton-metre (mass 1.02 mg, g
9,810 mm/s^2, weight 10.05 uN), so the brief's measured 4.2 nN m of knee torque per fast spike (Azevedo 2020) drops in as the gain: 42 nN m
per unit of the kernel's activation (ten spike-equivalents), the actuators' clip raised to +-60. holding a fly up needs under 1 nN m per
knee: a fraction of one fast spike. a derivation, not a fit; the arms on the measured springs (stiffness 0.14):

| arm | thorax height after 1 s (0.7 = standing) | planar speed | what the film shows |
|---|---|---|---|
| the cord at rest | 0.42 | 0.1 mm/s | lies on his belly |
| DNg100 100 Hz (the record's dose) | 0.44 | 0.2 | lies on his belly, legs splayed |
| him (the run of record, 8 s) | 0.41 | 0.3 | the same |
| DNg100 400 Hz | 0.71 (min 0.36, max 2.1) | **20.9 (max 111)** | thrashes four body lengths, rolls onto his side, then his back, legs kicking (`docs/figures/body_six_tumbles_400hz.png`) |
| the load signal at 60 Hz, 100 Hz | 0.57 | 10.0 | pushes off backwards, rolls onto his side |
| the load at 60, 400 Hz | 0.60 | 18.5 | the same, faster |

- **the first body lies down, and when driven it tumbles.** with the measured torque per spike the cord's rest output and the record's
  dose do not hold him up; at the high dose or with the load reflex driving the extensors he pushes, unevenly, and rolls. a fly walks at
  10-20 mm/s; he covers ground at that speed on his side. nate's "flailing and spasming in place", on film, with the numbers from the paper.
- **why he rolls:** the cord's stance is lopsided. the left mid tibia extensor at 36 Hz against the right at 8, the front-left jump muscle
  on and the front-right silent, the right cord under-traced throughout (SEAM 09-19: 15 % less input on the right): a posture of unequal
  rates, which on springs that hold the pose is a twitch and on real-stiffness legs is a fall to one side. the body has told the cord its
  first thing: its left and right are not the same fly.
- what would stand him up, in order of honesty: (1) the standing tonus as physiology: the slow motor units' tonic drive under load
  (Azevedo 2020: standing is slow-unit drive; our slow MNs are the small-input cells the size rule weights at 0.1), which the load reflex
  supplies only unevenly here; (2) the mirror normalisation of the cord's left-right input asymmetry (`--mirror`, the labelled tracing
  correction already used on the compass pair), applied to the leg motor pools, tested on the body: if a mirrored cord stands and the raw
  one falls, the fall was the tracing; (3) the loop, so that a leg that takes weight loads its own sensors and the load reflex holds it.
  the mirror test is one flag and one replay: first thing tomorrow.

**the mirror test (00:33 PDT; nate: "mirror correction, real brain surgery eh? let's give it a shot"; `world/cord.py --mirror vnc`: 3,389
bilateral types' input weights scaled toward the pair mean, clip 2, 462 cells at the clip; the labelled tracing correction of 09-19 on the
whole cord):**

| the cord | mid tibia extensor L / R (Hz per cell) | segment totals L / R |
|---|---|---|
| raw, DNg100 100 Hz | 36.3 / 7.9 | fl 0.58 / 0.54, ml 2.31 / 2.30, hl 3.08 / 3.21 |
| mirrored | 24.8 / 13.1 | 0.42 / 0.57, 1.87 / 2.73, 2.95 / 3.42 |
| raw, 400 Hz | 95.7 / 38.9 | |
| mirrored | 81.2 / 48.5 | |

| the body, measured springs, derived torque (mean thorax height after 1 s; 0.7 = standing; planar speed) | raw | mirrored |
|---|---|---|
| at rest | 0.45, 1.1 mm/s | 0.45, 1.0 |
| DNg100 100 Hz | 0.58, 6.3 | 0.58, 5.0 |
| 400 Hz | 0.71 (tumbling), 20.9 | 0.57, 16.2 |
| the load at 60 Hz | 0.57, 10.0 | 0.58, 11.4 |

- **the mirror narrows the asymmetry and changes nothing on the body.** the mid knee's 36 / 8 becomes 25 / 13; the segment totals were
  even already (the lopsidedness is in *which* cells fire, not in how many spikes a side gets); and on the floor the mirrored cord lies
  down and scoots exactly as the raw one does (`world/body/mir_*_weak42.mp4`; frame: on his side, legs up). so the fall is not the tracing,
  or not mainly. (the earlier table's heights were end-of-run values; these are means after the first second, which is why the record's
  dose reads 0.58 here and 0.44 there; the film is the same film.)
- what is left is the physiology: a stance that holds a fly up is tonic, symmetric, and on the slow units of every leg at once, and this
  cord under this command gives a few loud fast cells on a few legs. the standing tonus (SEAM above, (1)) is the next single variable:
  the load reflex, per leg, from the leg's own load, which is the loop. the mirror stays available as the labelled correction it is.

**things thrown at the wall (00:44 PDT; nate: "is there any kind of frankenstein effect ... some kind of electric shock to kick everything into
some initial state?"; the cord, 30 s, seed 11):**

| arm | leg MN Hz | active | flex Hz | ext Hz | antag | legs | note |
|---|---|---|---|---|---|---|---|
| DNg100 100 Hz (the control) | 1.96 | 52 | 0.00 | 9.3 | -0.16 | +0.00 | |
| **the jolt**: every descending neuron (1,310) at 100 Hz for 1 s after the warm-up, then the command alone | 2.06 | 68 | 0.00 | 8.4 | -0.15 | +0.00 | during the jolt the leg MNs go to 9.5 Hz per cell; from 4 s on the per-cell rates correlate 0.986 with the control, 18 cells differ by more than 2 Hz |
| the jolt at 200 Hz for 0.2 s | 1.89 | 58 | 0.00 | 7.4 | -0.14 | +0.00 | the same |
| the jolt, then 400 Hz | 5.50 | 82 | 0.02 | 24.2 | -0.51 | +0.00 | |
| **the command with a time course**: 100 Hz gated at 3 Hz, half duty | 1.12 | 53 | 0.00 | 4.8 | -0.14 | +0.00 | the cord follows the gating (a "beat" at 3.1 Hz: the input's) |
| gated at 8 Hz | 1.08 | 54 | 0.00 | 5.0 | -0.11 | +0.00 | the same at 7.8 |
| 400 Hz gated at 3 Hz | 3.15 | 62 | 0.01 | 14.4 | -0.20 | +0.00 | |
| **membrane noise** 0.5 mV (the default is 0.15) | 3.49 | 74 | 0.02 | 19.8 | -0.41 | +0.00 | |
| noise 1.0 mV | 5.93 | **283** | **1.54** | 23.4 | -0.45 | +0.00 | the noise fires three quarters of the cord's motor neurons, flexors included; the whole cord at 4.6 Hz per cell |
| noise 1.0 at 400 Hz | 8.90 | 241 | 1.50 | 34.4 | -0.46 | -0.03 | |

- **no frankenstein effect.** the cord has no state for a jolt to set: a second of every descending neuron at 100 Hz sends the legs to six
  times their rate and, once it stops, the cord is back where the gentle start put it within a hair. the membrane forgets in twenty
  milliseconds and nothing slower exists in it but the two-cell pair we damped. (the first two jolt arms drove nothing: the jolt's cells
  were not marked driven, and the runs came out identical to the control to the spike; kept, fixed, rerun.)
- **a command with a time course is followed, not transformed:** gate it at 3 or 8 Hz and the extensors pulse at 3 or 8 Hz; the flexors
  stay at zero; no leg takes a turn.
- **noise unsticks cells, not the circuit:** at 1.0 mV (seven times the default, past physiology) the noise fires most motor neurons
  including the flexors, and the legs still move together. the coxal antagonists alternate more (-0.45), which is noise decorrelating
  two pools, not a rhythm.
- on the body (measured springs): the 3 Hz-gated 400 Hz command scoots him backwards 12 mm on his side; the 1.0 mV noise cord lies
  down and drifts; and on flygym's springs the gated 400 Hz command knocks him over too (`world/body/pulse3_400_springs.mp4`: on his
  back). the pushes are big enough to topple a standing body and not coordinated enough to carry it.

**seeds (00:45 PDT):** the lopsided stance is the wiring, not the dice: the mid tibia extensors at 36 / 8 Hz (L / R) on seeds 10, 11, 12 and 13 alike (36.3 / 7.1, 36.3 / 7.9, 34.8 / 7.5, 35.6 / 8.0), the hind trochanter depressors even (12-13 both sides), the flexors 0.00 on all four. one left mid extensor cell receives far more drive than its right twin, and the mirror (above) narrows that to 25 / 13 without changing what the body does. (the front-left jump muscle that fired in the whole fly is silent in the cord alone: it was brain-driven.)

## the night's wall, continued (01:07 PDT; nate asleep, the laptop mine)

**steering and the moonwalker, in the cord:** a one-sided command makes one-sided legs, crossed for DNa02 and straight for DNa01: DNa02's
left cell at 100 Hz drives the right legs (0.81 Hz per cell) four to one over the left (0.20) and its right cell the reverse (0.29 / 0.56);
DNa01's left cell drives the left (0.58 / 0.18). MDN (the moonwalker, 4 cells) drives the hind legs hardest and the right side more
(L 1.90 / R 3.28; hind 2.13 / 7.13). `--walk-side`.

**on the body, inconclusive, and the reason is a finding:** the body under the plain command on flygym's springs spins (+157 deg of
heading in 6 s) before any steering is added, because the stance is lopsided; the one-sided arms turn -145 / +75 (steer left, springs /
measured), MDN +71 / -119, DNa01-left -2: signs that flip with the springs and cannot be read against a control that spins by itself. a
turning test needs a body that stands straight first.

**the slow units are not in the file.** the 373 leg motor neurons' input synapses run from 0 to 19,137 per cell (quartiles 178 / 872 /
4,268). the smallest quarter (93 cells, under 178 synapses: 26 accessory tibia flexors, 16 accessory trochanter flexors, 12 tibia flexors,
11 ltm, 7 trochanter flexors, 6 tarsal depressors, 5 femur reductors) receives **26 excitatory synapses per cell**, against 4,671 for the
largest quarter, and the leg proprioceptors reach them with **zero** synapses, directly or through one interneuron (117 direct per cell
onto the large ones). if these are the slow units (the size rule says so; Azevedo 2020's slow tibia flexor MNs are the small ones), then
the standing tonus, which in life is tonic slow-unit drive under load, has no wiring to run on in this volume: not a constant to fit, a
hole in the map. the honest options are a labelled stand-in (slow units held at a load-scaled tonic rate, the way the floor holds the
proprioceptors) or a body that stands on its fast units, which is not a fly. this goes to `docs/ASK.md`.

**the 36 and the 8:** the two left mid tibia extensors receive 5,100 and 5,209 excitatory synapses; the right pair 4,966 and **1,856**. one
right cell is traced at a third of its twin, and it fires 10 Hz where the left twin fires 78. the mirror scales by the pair mean and cannot
give one cell what the other three have; a named-homologue correction (its inputs copied from its mirror twin, labelled) could. queued.

**the hinges (01:13 PDT):** the body ships its leg joints unlimited, and under the cord's torques the mid and hind knees wound through 1,000-2,000 deg in the first loop smoke; ranges about the neutral pose (knee +-70, trochanter pitch +-50, coxa +-45, tarsus +-40; (E), the brief's measured ranges next) were not enough, because the limit constraint's default softness (20 ms, impedance 0.95) lets a full torque on a tibia of a hundredth of a milligram blow through it (a +60 push: 104 -> 1,660 deg in 300 ms); stiffened to 2 ms and 0.99 / 0.999 it holds within 8 deg. a solver setting, labelled. **every body result above this line was made with unlimited hinges** and is being remade; the standing / lying-down heights should stand, the tumbling may not.

**the body remade with limited hinges (01:15 PDT; measured springs, derived torque; the same arms as above):**

| arm | height after 1 s | travelled in 6 s | net turn |
|---|---|---|---|
| at rest | 0.44 | 0.8 mm | 0 |
| DNg100 100 Hz | 0.46 | 1.0 | +9 |
| DNg100 400 Hz | 0.40 | 1.8 | +90 |
| him (8 s) | 0.40 | 1.7 | +3 |
| DNg100 100 Hz on flygym's springs | 0.75 (standing) | 3.2 | +172 |
| 400 Hz on flygym's springs | 0.56 | 3.8 | +132 |

- **the tumbling was the hinges.** with joints that hold their ranges, the measured-stiffness body lies down at every dose and barely
  moves: no scooting, no rolling, no four body lengths. "flailing and spasming" is withdrawn; what stands is "lying down, twitching". on
  flygym's springs, standing, he still turns on the spot from the lopsided pushes (+172 / +132 deg; the seeds gave -178 / +105 / +133
  before the fix, and that spread was partly wind-up too).
- so the steering and moonwalker body arms above are void twice over (unlimited hinges, and a spinning control), and are not re-run
  until a body stands straight. the heights stand: on real legs he lies down.

## the loop on six legs (01:22 PDT; `experiments/body_loop.py`: the cord and the NeuroMechFly body in one process at 1 ms, 0.3-0.45x real
time; measured springs, derived torque, limited hinges; 20 s, seed 11; the mid and hind legs' sensory cells: 12-18 extension claws, 4-9
flexion claws, 7-9 hooks, 93-101 load cells each; the front legs 1-3 / 27 and 0-1 / 9)

| arm | leg MN Hz | flexors | extensors | thorax height (0.7 = standing) | leg forces (uN; F_stand 1.67) |
|---|---|---|---|---|---|
| DNg100 100 Hz, **loop off** | 1.99 | 0.00 | 9.35 | 0.40 | 0 (on his belly) |
| + **position** (claw + hook from the knees) | 2.26 | **0.49** | **3.27** | 0.41 | 0 |
| + load only | 2.04 | 0.00 | 5.84 | 0.41 | 0.0-0.2 |
| + position + load | 2.45 | **0.61** | 4.03 | 0.41 | 0-1.1 |
| 400 Hz, loop off | 6.34 | 0.04 | 29.1 | 0.41 | 0 |
| 400 Hz, position + load | 6.32 | 0.68 | 21.3 | 0.41 | 0-0.2 |
| the stand-in: the 93 smallest MNs at 30 x load, position + load | 3.45 | 1.98 | 4.19 | 0.49 | one mid leg 1.6 |
| at 60 x load | 6.08 | 6.55 | 3.62 | 0.57 | one mid leg 6.0 |
| at 60, no command | 2.43 | 4.77 | 0.00 | 0.43 | |
| set down standing (load clamped to standing for 5 s), 30 / 60 / 120 x load | 4.4 / 6.2 / 13.8 | 4.2 / 7.4 / 20.2 | 3.6 / 3.8 / 3.7 | 0.53 / 0.53 / 0.55 | ~0 after the clamp |

- **the loop moves the cord.** with the knees' angles and speeds fed back through his own claw and hook cells, the tibia flexors wake
  (0.00 -> 0.49-0.68 Hz per cell) and the extensors fall by two thirds (9.4 -> 3.3-4.0), at both doses; the cord and the body are talking
  for the first time. lying with the knees flexed, the flexion-tuned claws fire and the cord answers with flexion: the resistance reflex,
  with the sign life has it, which the one-leg loop could not show because that leg has one extension claw cell and three flexion. the
  mid and hind legs' sensory sets are enough.
- **he does not get up.** on his belly the feet bear no load, so the load rows and the stand-in see nothing, and set down standing he sinks
  back within the clamp. the stand-in as designed drives the wrong muscles: the 93 smallest motor neurons are the accessory *flexors*, ltm
  and the tarsal cells (the table above), so "slow units by size" is a flexion tonus, not a standing one; at 60 x load he curls (flexors
  6.5, extensors 3.6) and one mid leg pushes to 6 uN under him. the standing tonus in life is on the slow units of the extensors too, and
  those are not the smallest cells in this file. docs/ASK.md's option (a) needs the slow units picked by muscle, not by size.
- so the row stands here: a body that lies down, a loop that works, and a stance that this cord cannot yet hold. the standing tonus is the
  one remaining stand-in question, and it is now precisely posed: which extensor motor neurons carry the tonic load reflex, and at what
  rate under a body weight.

**the extensor stand-in (01:28 PDT; `--slow-set extensor`: the stance muscles' motor neurons below the median input size, held at a
load-scaled rate, set down standing; 20 s, seed 11):** only **7** of the stance muscles' motor neurons (posterior rotators and trochanter
extensors) fall below the median input size in this file: the sternotrochanter, trochanter extensor and tibia extensor pools are all
large-input cells. so the "slow extensor units" do not exist by the size rule either, and seven cells at 60-200 Hz x load do not stand
him up: thorax 0.43-0.56 (0.7 = standing), one mid leg pushing to 5-6 uN under him again, the loop's flexor wake-up (0.5-0.6) intact, the
rest unchanged. **the standing tonus has no cells to run on by size in either direction:** the small cells are flexors, the extensor
cells are large. what remains is a tonus on the extensor motor neurons regardless of size, which is a stand-in for a *function* (the
slow-unit standing reflex) on cells the size rule calls fast: labelled puppetry of §P's kind, with the exit being a dataset that resolves
the slow units, or (b) no stand-in and a fly on the floor. this is docs/ASK.md's question, now exactly posed, and it is nate's.

**the first negative inter-leg correlation (09:00 PDT), read before it is believed:** the two load-scaled stand-in arms score the inter-leg column at -0.17 / -0.18 (`experiments/gait_score.py`), the first negatives in any arm on this row. the matrix says which legs: the left mid leg against its neighbours (lf -0.17, lh -0.15, rf -0.11). that leg carries 6 uN (a third of his weight) with its knee pinned at the range limit (173 deg) while the other five bear 0.1-0.9, and its load-scaled drive rises and falls against theirs; the load traces anti-correlate the same way (-0.12 to -0.20). a one-legged push alternating with five unloaded legs, not a tripod. the number is real and it is not a gait.

## he stands (09:08 PDT; the laptop slept through the small hours and the batch finished at 09:06; nate: "any diagnostics are valid if they produce data")

**the arms (`experiments/body_loop.py`, the loop closed (position + load), measured springs, derived torque, limited hinges, 20 s, seed 11):**

| arm | leg MN Hz | flexors | extensors | thorax height (0.7 = standing) | leg forces, six legs (uN) | legs (inter-leg min) |
|---|---|---|---|---|---|---|
| **tethered** (propped: thorax fixed, no floor), DNg100 100 Hz, loop off | 1.99 | 0.00 | 9.35 | held | none | +0.00 |
| tethered, position loop | 2.26 | 0.58 | 3.50 | held | none | +0.00 |
| tethered, 400 Hz, position loop | 6.19 | 0.43 | 22.1 | held | none | +0.00 |
| gravity x0.1, loop | 2.55 | 0.66 | 3.78 | 0.57 | 0 | +0.00 |
| gravity x0.3, loop | 2.46 | 0.65 | 3.94 | 0.48 | 0-0.3 | +0.00 |
| **the stance tonus** (73 stance-muscle MNs at 60 Hz x load, set down standing), 100 Hz | 5.97 | 0.44 | 24.9 | **0.71** | 0.8 0.2 0.5 0.8 0.4 0.9 | -0.02 |
| the same at 120 Hz x load | 9.05 | 0.30 | 41.9 | **0.71** | 0.8 0.2 0.6 0.7 0.3 0.7 | -0.03 |
| the same, no command | 5.52 | 1.47 | 25.9 | **0.71** | 0.7 0.3 0.6 0.8 0.2 0.9 | -0.04 |
| the same at gravity x0.3 | 7.25 | 0.31 | 32.6 | 0.84 | 0.7 0.1 0.2 0.7 0.2 0.2 | -0.29 |
| the same, 400 Hz | 7.62 | 0.51 | 25.9 | **0.72** | 1.2 0.5 0.7 0.9 0.4 0.8 | -0.28 |

- **he stands, on all six feet, at full gravity.** the tonus on the stance muscles' motor neurons regardless of size (docs/ASK.md's (a),
  run as a diagnostic), load-scaled and set down standing, holds the thorax at the standing height for the whole run at rest, at the
  record's dose and at the high one, with the weight spread over six feet (0.2-1.2 uN each) instead of one leg's 6. the loop's flexor
  wake-up survives standing (0.3-0.5). the extensors run at 25-42 Hz per cell under it, which is the stand-in's own doing.
- **propped up, the cord does what it does on the floor.** tethered with the legs free, the position loop wakes the flexors exactly as
  it did lying down (0.58) and nothing else changes; so the thrashing-by-crushing hypothesis is out: the legs were never being crushed
  into a different pattern, the cord's pattern is the same with no weight at all. and reduced gravity does not stand him up (0.48-0.57 at
  a tenth and a third of his weight): without tonus the legs hold nothing, at any weight.
- **standing, he does not step.** the negative inter-leg correlations (-0.28 / -0.29) are the front legs against the mid legs (lf-lm -0.24
  / -0.27, rf-rm -0.29) with the two front legs moving *together* (+0.37 to +0.51, in rate and in load): a front-leg push-up against the
  mid legs, not a tripod. the knees' autocorrelations decay without a negative lobe (slow drifts, no oscillation); the mid and hind knees
  wander tens of degrees (sd 20-60) while the front knees sit at their limits (sd 1). frames: `docs/figures/body_stands_tonus.png`.
- so the row now has a standing fly with the loop closed, and the question it was built to ask is finally askable: does his own stance
  time his own swing. tonight's answer is no, with one honest caveat: the tonus that stands him is a stand-in at a rate i chose
  (60-120 Hz x load), and the swing trigger in life is the *unloading* of a leg, which a body held up by a tonic push never produces
  unless something lifts a leg first. the next arms: the tonus with a leg-load *derivative* term (the campaniform brief's dF/dt, so a
  loaded leg's push fades and its unloading registers), and the flexion-biased descending set on top of the standing body.

**the standing body, more arms (09:14 PDT; the stance tonus at 60 Hz x load, the loop closed, 20 s):**

| arm | flexors | extensors | height | travelled | lf-lm | lm-rf | lf-rf |
|---|---|---|---|---|---|---|---|
| DNg100 100 Hz, seed 11 / 10 / 12 | 0.44 / 0.40 / 0.50 | 24.8 / 24.8 / 24.9 | 0.71 all | ~1 mm | +0.07 / +0.01 | +0.22 / +0.20 | +0.51 / +0.40 |
| no command | 1.47 | 25.9 | 0.71 | | +0.01 | +0.22 | +0.15 |
| DNg100 + the flexor set | 3.15 | 27.0 | 0.71 | | | | |
| the flexor set alone | 6.25 | 25.1 | 0.71 | 2.6 mm | -0.08 | +0.03 | +0.36 |
| MDN (the moonwalker) | 2.98 | 27.6 | 0.71 | 4.7 mm | **-0.39** | **+0.35** | -0.00 |
| DNg100 400 Hz (mislabelled `stand_pulse3`) | 0.51 | 25.9 | 0.72 | | -0.27 | | +0.46 |

- **standing is robust:** three seeds, three commands, no command, all at 0.71.
- **how he stands, read from the feet:** the front feet carry the weight (median force 0.4-0.6 uN, on the ground 60-75 % of the time,
  knees pinned at their limit) and the mid and hind feet tap: median force 0, off the floor 66-92 % of the time, 12-82 "lifts" of over
  50 ms in 18 s, knees wandering 40-66 deg, **in the controls as much as in any arm**. so the feet do come off the ground by themselves,
  and it is the stand-in's posture doing it: the tonus pushes the front legs into the floor and the mid and hind legs wave. a push-up with
  the back four feet tapping, in every arm; not a step.
- **the moonwalker's matrix has a tripod-shaped corner** (left-front against left-mid -0.39; left-mid with right-front +0.35; the control
  +0.07 / +0.22) and moved him 4.7 mm, the most of any arm. one seed, one command, and the control's mid-front pair already sits at +0.2:
  weak evidence, kept, to be tried on three seeds against DNg100 before it is called anything.

**the moonwalker on four seeds (09:18 PDT; the standing body, the loop closed, MDN's 4 cells at 100 Hz):**

| | lf-lm | lm-rf | travelled | along his own heading | turn |
|---|---|---|---|---|---|
| DNg100, seeds 11 / 10 / 12 (controls) | +0.07 / +0.01 / +0.09 | +0.22 / +0.20 / +0.18 | 1.8-2.6 mm | +1.8 to +2.5 (forward) | +9 / -18 / +24 |
| **MDN, seeds 11 / 10 / 12 / 13** | **-0.39 / -0.36 / -0.34 / -0.30** | **+0.35 / +0.37 / +0.36 / +0.35** | 4.7-6.4 | **+4.8 to +5.4 (forward)** | **-30 / -63 / -46 / -70** |

- **it replicates, and it is not walking backwards.** under MDN the left mid leg takes load (1.3-1.5 uN against 0.2 under DNg100), its
  drive anti-correlates with the left front leg and co-varies with the right front, the same on four seeds; he covers twice the control's
  distance, forward along his own heading, turning right every time. MDN's job in life is backward walking (Bidaye 2014, in headless
  flies). here it re-distributes the stance (which legs carry him) and the push-up carries him forward and round. so: a command-specific,
  seed-robust change in inter-leg coordination, the first on this row, and the wrong direction, which is the finding's own control.
- the mechanism is the load loop: MDN loads one mid leg, the load rows and the tonus answer on that leg, and the anti-phase is that leg's
  reflex against the front legs' push, not a swing. the knees under it do not oscillate (no negative lobe).

**the unloading term (09:20 PDT; `--load-deriv G`: the load rows and the stance tonus get F/F_stand + G x dF/dt x 50 ms / F_stand, so a leg
being unloaded loses its stance drive before its load is gone; the standing body, the loop closed, 20 s, seed 11):**

| arm | flexors | extensors | height | legs (inter-leg min) | feet on the ground (%, lf lm lh rf rm rh) | lifts > 50 ms |
|---|---|---|---|---|---|---|
| G = 0 (the standing control) | 0.44 | 24.8 | 0.71 | -0.02 | 59 24 18 64 10 19 | 1 69 44 0 82 82 |
| G = 1 | 0.36 | 31.4 | 0.71 | -0.15 | | |
| G = 3 | 0.21 | 34.6 | 0.71 | -0.14 | 68 24 19 68 9 20 | 0 38 35 1 79 44 |
| G = 10 | 0.33 | 35.1 | 0.71 | -0.19 | 70 25 19 71 7 18 | 1 58 43 1 72 67 |
| G = 3, 400 Hz | 0.42 | 27.1 | 0.64 | -0.23 | | |
| G = 3, DNg100 + the flexor set | 3.12 | 28.8 | 0.72 | -0.09 | 43 14 19 42 10 18 | 15 58 36 17 104 73 |
| G = 3, MDN | 2.91 | 33.7 | 0.71 | -0.38 | | |

- **rate sensitivity on the load makes the legs a little more independent and no more rhythmic.** the inter-leg minimum moves from -0.02 to
  -0.14 / -0.19 as G rises (each leg's drive now follows its own load's changes), the extensors rise (loading adds), the flexors do not
  wake further, the feet keep the same on-ground fractions (the front pair 60-70 %, the back four 10-25 %), the back feet tap as before
  (35-80 lifts), and no knee oscillates. the swing trigger, as a derivative on load feeding the load rows, is not enough by itself: an
  unloaded leg loses its stance drive and then nothing lifts it, because the flexors' excitation (IN21A004 and company) still waits on
  input that neither the claws (which drive extension here) nor the load's fall provides.

**where the body row stands, the morning after.** he stands (a labelled stand-in holds him; the file has no slow units); the loop is closed
and it works (position wakes the flexors; load re-distributes the stance; MDN reorganises the legs the same way on four seeds); nothing
steps. every reflex term and command tried on the standing body leaves the front pair pushing and the back four tapping. the flexors'
premotor cells, which have to fire for a swing, have fired for one reason all week: a flexion-biased descending population. so the next
honest arm is the walking command as the population it is in life (Braun 2024; DNa01 / DNa02 / DNp09 / DNg13 / oDN1 / DNge035 and the rest
together, at rates from the whole fly's own run rather than a flat 100 Hz), on the standing body, with the loop; and past that the whole
fly, brain and all, in the body: the descending population as the brain actually produces it. that is the build the row was always
heading for, and it is now a matter of running him at an eighth of real time with a body attached.

## the struts and the ice (17:12 PDT; nate, watching the standing clips: "his front legs slowly splay out until his abdomen is back on the
ground ... they're stuck straight out"; "did we fail to give him friction with the ground, or adhesion?")

**the struts.** the front knees sit at their range limit for the whole run (sd 1 deg): the stand-in drives the extensors only, so every
front joint goes to the end of its range and what holds him up is the joint limit, not a muscle; a strut on a hinge splays (the front
coxa's yaw drifts 10 -> 22 deg over the run). gravity is right (1.02 mg, 9.81 m/s^2, 10.05 uN: a fruit fly). standing in life is
co-contraction, both antagonists on and the joint stiff mid-range. `--cocon F`: the swing muscles' motor neurons at F x the stance tonus x
load (a stand-in, labelled, within nate's licence: "any manipulation of the motor neurons that doesn't involve us scripting his walking
sequence"):

| cocon | height | lf knee (mean, sd) | lf coxa yaw drift | feet on the ground (%) |
|---|---|---|---|---|
| 0 (extensors only) | 0.71 | 7 (1): at the limit | 10 -> 22 | 59 24 18 64 10 19 |
| **0.2** | **0.70** | **29 (27): off the limit, moving** | 22 -> 25 | 54 23 21 45 18 25 |
| 0.4 | 0.53 | 114 (26) | -58 -> -16 | 2 5 10 0 3 8 (crouched, feet off) |
| 0.6 | 0.55 | 112 (28) | | 0-5 |
| 0.4, no command / MDN | 0.53 / 0.55 | 130 / 145 | | |

- **a fifth of co-contraction takes the front legs off their limits and keeps him standing;** two fifths and up the flexors win and he
  crouches with his feet off the floor. 0.2 is the arm to carry forward. (the file's own flexors fire at 5 Hz under it: the stand-in on
  the swing muscles wakes the swing side too, which is the point of co-contraction.)

**the ice.** the ground's friction coefficient is 1.0 (the package's; a plain surface), and his adhesion, wired to the long tendon
muscles' motor neurons as the honest hookup, has never switched on, because those cells are among the unwired (100-250 synapses each,
0 Hz in every arm). a fly walks up glass on its pulvilli: pads of tenent hairs with a secreted fluid film, capillary and van der Waals
adhesion, several body weights, pressed to stick and peeled to release. `--adhesion contact --adhesion-gain 20`: a loaded foot sticks
(20 uN, two body weights) and an unloaded one releases; a labelled stand-in for the pads' passive adhesion (the Ramdya lab's convention:
adhesion during stance). arms running: the record's dose and MDN with the pads, with and without co-contraction.

**nate's clip** (`stand_mdn.mp4`, from 8 s: "his middle legs start doing a rhythmic walking motion that does indeed propel him forward"):
the right mid knee in that window oscillates at 1.5 Hz with a clean autocorrelation lobe at 352 ms, the first knee on this row with one;
the thorax moves at 1.1 mm/s (a fly walks 10-20), sliding. the other three moonwalker seeds do not repeat it (slow wander, no lobe, like
the controls). one leg on one seed: real, kept, not called a gait.

**the tick (17:17 PDT; nate: "is it possible different behavior would emerge from a finer tick rate?"; the cord, DNg100 100 Hz, 20 s, seed 11, `--dt`, the membrane noise scaled by sqrt(dt)):** dt 1.0 / 0.5 / 0.25 / 0.1 ms: cord 1.13 / 1.23 / 1.32 / 1.35 Hz per cell, leg MNs 1.99 / 2.12 / 2.29 / 2.36, active 54 / 53 / 61 / 62, extensors 9.4 / 10.2 / 11.6 / 11.5, flexors 0.00 at all four, no inter-leg phase at any. a millisecond tick delays every threshold crossing by up to a step and rounds the 1.8 ms delay and the 2.2 ms refractory to whole steps, and that costs about 18 % of the rate against a tenth-of-a-millisecond tick (Shiu 2024 ran Brian2 at 0.1 ms); the shape of the output does not move. the membrane is exact at any tick (the analytic integrator since 09-19); the events are what the tick quantises. so: a rate correction worth knowing, no behaviour hiding under it. the whole fly at 0.1 ms would run ten times slower, which is the reason it is 1.0.

**the pads (17:24 PDT; `--adhesion contact --adhesion-gain 20`: a loaded foot sticks with 20 uN, an unloaded one releases; the standing
body, the loop closed, 20 s):**

| arm | height | along his heading | turn | flexors | extensors | feet on the ground (%) | lf-lm / lm-rf |
|---|---|---|---|---|---|---|---|
| DNg100, no pads (the control) | 0.71 | 2.5 mm | +9 | 0.44 | 24.8 | 59 24 18 64 10 19 | +0.07 / +0.22 |
| DNg100, pads | 0.70 | 0.3 | +76 | 0.16 | 40.6 | 58 52 33 59 8 38 | +0.03 / +0.01 |
| DNg100, pads + co-contraction 0.2 | 0.65 | 0.2 | -7 | 11.7 | 49.1 | 59 11 32 83 95 32 | -0.02 / -0.07 |
| no command, pads + 0.2 | 0.66 | 0.8 | -56 | 12.0 | 50.1 | 61 11 25 80 93 37 | |
| 400 Hz, pads + 0.2 | 0.65 | 1.1 | -40 | 10.3 | 44.4 | 42 11 16 85 96 32 | |
| MDN, no pads | 0.71 | 4.8 | -30 | 2.98 | 27.6 | 54 23 9 66 19 25 | **-0.39 / +0.35** |
| MDN, pads | 0.71 | 5.0 | **-175** | 2.72 | 35.2 | 55 21 24 59 12 32 | -0.13 / +0.19 |
| MDN, pads + 0.2, seeds 11 / 10 | 0.65 / 0.68 | 1.0 / -0.5 | -59 / +87 | 10.1 / 9.4 | 43.9 / 39.3 | | -0.01 / -0.18 |
| the flexion population, pads + 0.2 | 0.65 | 2.9 | -76 | 10.7 | 45.1 | 38 10 19 82 93 38 | +0.12 / -0.16 |

- **the pads make him stick, and the sliding goes:** 0.2-1 mm of travel where there was 2.5-5. the feet that are down stay down (the
  right mid 93-96 % of the time with co-contraction) and the loop pushes harder against feet that cannot move: the flexors run at 10-12 Hz
  and the extensors at 40-50 under the pads and the fifth of co-contraction, a body straining against its own grip. no knee oscillates
  in any arm (no autocorrelation lobe under a second anywhere).
- **the moonwalker's structure was a sliding pattern.** with the pads its left-front / left-mid anti-phase falls from -0.39 to -0.13 and
  with co-contraction to zero; on sticky feet MDN spins him half a turn on the spot (-175 deg) instead of drifting. the coordination that
  replicated on four seeds was a reflex pattern of a body sliding on its front legs.
- so, with feet that grip, legs that co-contract, a tonus that stands him and a loop that answers: he stands, he grips, he strains,
  and nothing steps. every lever on the body's side has now been pulled once. what has not been tried is the command as the brain
  makes it: the descending population at its own rates. a whole-fly run with every descending type logged is in flight, to play the
  brain's descending output into the headless cord and body as a recording (the same headless preparation, the real channels).

**the descending census (17:30 PDT; 60 s of the whole fly, the configuration of record, every descending-neuron type logged per chunk; `world/record/dn_census_0922.cells.npz`):** 1,306 descending cells, 481 types; mean 3.9 Hz per cell; 256 cells above 1 Hz, 65 above 20. the loudest: DNb05 194 Hz per cell (the thermosensory / steering DN the floor drives), DNp20 144, DNg56 124, DNp12 108, DNp18 92, DNbe001 85, DNge129 73, DNg99 72, DNg33 67 (the damped pair), DNb06 60, DNp26 51, DNpe017 54, DNg100 48 (the walking command as the PFL2 gain doses it), DNp15 47, DNp31 42, DNge033 35. he walked 70 % of the recording at 0.14 m/s. **the playback** (`--dn-playback`): each of these cells in the headless cord held at its own recorded rate, chunk by chunk, on the standing body with the loop: the brain's descending output as a recording, the same headless preparation with the real channels. running.

**the brain's own descending output, played into the headless cord and body (17:37 PDT; `--dn-playback`, all 1,306 descending cells at
their recorded rates chunk by chunk; the standing body, the loop closed, 20 s; 0.22-0.29x real time):**

| arm | leg MN Hz | flexors | extensors | height | along his heading | turn | feet on the ground (%) | knee lobes |
|---|---|---|---|---|---|---|---|---|
| playback, tonus + co-contraction + pads, seeds 11 / 10 | 14.5 / 12.4 | 10.7 / 9.2 | 45.6 / 38.4 | 0.65 / 0.69 | +2.0 / -0.6 mm | -27 / +157 | 45 11 16 83 95 39 | none |
| playback, tonus + co-contraction | 7.80 | 5.27 | 23.1 | 0.70 | +0.8 | +70 | 56 24 19 41 15 27 | none |
| playback, tonus alone | 6.92 | 0.17 | 26.3 | 0.71 | +5.2 | +112 | 62 16 19 53 19 20 | none |
| playback, lying (no tonus) | 2.98 | 0.32 | 2.42 | 0.41 | 0.0 | -40 | on his belly | none |
| DNg100 100 Hz, tonus + co-contraction + pads (the control) | 15.2 | 11.7 | 49.1 | 0.65 | +0.2 | -7 | 59 11 32 83 95 32 | none |

- **the brain's descending population does not make the cord step either.** with all 1,306 descending cells held at the rates the brain
  gave them in the garden (DNb05 at 194, DNp20 at 144, the walking command at 48 as his compass doses it, 65 cells above 20 Hz), the
  standing body does what it did under one cell at a flat 100 Hz: the front pair pushes, the back four tap, no knee oscillates, no leg
  anti-phases another (the inter-leg minimum -0.11 to -0.20, the same as the controls), and he covers 0.6-5 mm turning on the spot.
  the plain-tonus playback arm travels the most (5.2 mm) and spins 112 deg, which is the lopsided push-up again.
- (with the pads on, the contact-force readings include the adhesion's pull, so "19 uN on the right mid leg" is the pad holding, not
  the body's weight; the load rows saturate at twice standing and read it the same. noted, not fixed: the loop's load signal should be
  the ground reaction net of adhesion, a later correction.)

**where this leaves the leg row, at the end of the day (17:37).** every input the headless preparation can be given has now been given:
one walking neuron at a flat rate, a flexion-biased set, the moonwalker, a gated command, a jolt, noise, the brain's own descending
population as a recording; and every body-side term: a tonus that stands him, co-contraction, pads that grip, an unloading term, a
loop that feeds his knees and his loads back into his own sensory cells. he stands, grips, strains, taps, turns, and does not step. the
cord's premotor network routes every command to the right muscles and never alternates between them, and the table said why two
nights ago: the half-centre's inhibitors do not reach the opposing exciters. **the gap is in the cord model**, and it is one of three
things, each a labelled engine change with a source: (1) the premotor interneurons that are graded in life (non-spiking local
interneurons are the substrate of insect leg pattern generation, Büschges 1995 / Bässler & Büschges 1998; in a LIF a graded cell is
either silent or a spiker, and the 13A / 13B / 21A pools may be the cells whose analogue release the switch needs, the way flyvis's
graded optic lobe was the seam's fix for vision); (2) electrical synapses (absent from a chemical connectome; central pattern generators
lean on them); (3) the slow units and the front legs' sensory tracing, which this file lacks and no model change supplies. (1) is the one
the record's own history points at, and it is the next single variable: a graded-unit engine for named premotor hemilineages, in the
cord, on the standing body.

## graded premotor interneurons (17:48 PDT; §Q 4h; nate: "if this is the biology, it's a fair move")

**the engine change** (`world/fastlif.py`, off by default; `--graded PREFIXES:GAIN[:V1]` in `world/cord.py` and `experiments/body_loop.py`):
a graded unit never spikes (its threshold is put out of reach and it is never reset) and each millisecond delivers to its targets a
fraction of a spike, GAIN x clip(v / V1, 0, 1), through the delay line's per-emission scale (the depression rule's machinery). the
source: non-spiking local interneurons are the substrate of insect leg pattern generation (Büschges 1995, stick insect; Bässler &
Büschges 1998); which fly hemilineages are graded is not established, (E), so the pools are swept (13A + 13B, the GABAergic premotor
inhibitors; 21A, the glutamatergic flexor-side pool; all three) against a random set of the same size, and the gain (0.05-0.2 of a spike
per ms: a graded cell at threshold delivers what a spiker at 50-200 Hz would).

**the cord, DNg100 100 Hz, 30 s, seed 11:**

| graded | cells | gain | leg MN Hz | active | flexors | extensors | antag | legs | beat |
|---|---|---|---|---|---|---|---|---|---|
| none (the record) | | | 1.96 | 52 | 0.00 | 9.3 | -0.16 | +0.00 | 4.3 |
| 13A + 13B | 871 | 0.05 / 0.1 / 0.2 | 1.41 / 1.29 / 1.22 | 47 / 41 / 34 | 0.00 | 6.9 / 9.3 / 9.7 | -0.12 / -0.08 / -0.13 | +0.00 | 4-5 |
| 21A | 409 | 0.1 / 0.2 | 3.99 / 4.83 | 58 / 67 | 0.00 / 0.04 | 9.9 / 10.8 | -0.19 / -0.15 | +0.00 | 17 / **44 (L3, 1.6 Hz)** |
| all three | 1,280 | 0.1 / 0.2 | 2.40 / 2.43 | 49 / 52 | 0.00 | 8.6 / 8.7 | -0.21 | +0.00 | 12 / 17 (L3, 2-3.5 Hz) |
| random 1,280 (control) | 1,280 | 0.1 / 0.2 | 3.34 / **13.7** | 56 / 78 | 0.00 / **10.7** | 10.2 / 8.1 | -0.31 / -0.42 | -0.06 | 3.7 / 15.5 |

- **graded inhibitors quieten the cord, graded 21A doubles its leg output, and a random graded set at the higher gain wakes the flexors
  to 10.7 Hz** (a tonic-excitation effect: graded cholinergic cells drive continuously); no leg anti-phases another in any arm. the hind
  legs' "beat" at 1.6-3.5 Hz under graded 21A and all-three is being read before it is believed (the next block); the same arms are
  running on the standing body with the loop.

- **the hind legs' "beat" under graded 21A, read (17:49 PDT):** no autocorrelation lobe of the leg's summed rate at any lag under 750 ms; the loudest cells are two sternal posterior rotators and a femur reductor at 120-155 Hz each, tonic. the beat measure's blind spot (two cells at one rate) once more; a tonic drive on the hind coxa's retractors, not a rhythm. graded 21A makes the flexor-side pool a continuous source, and what it feeds most, through the cord, is the hind legs' stance muscles.

**the graded pools on the standing body (17:55 PDT; the tonus, co-contraction 0.2, the pads, the loop; DNg100 100 Hz; 20 s, seed 11):**

| graded | flexors | extensors | height | along | turn | feet on the ground (%) | inter-leg min | knee lobes |
|---|---|---|---|---|---|---|---|---|
| none (the control) | 11.7 | 49.1 | 0.65 | 0.2 mm | -7 | 59 11 32 83 95 32 | -0.07 | none |
| 13A + 13B, 0.1 | 11.9 | 49.7 | 0.65 | 2.3 | -63 | 64 10 19 82 95 44 | -0.16 | none |
| 21A, 0.1 / 0.2 | 11.8 / 12.9 | 49.3 / 51.9 | 0.65 | 1.6 / 1.1 | -26 / -96 | 73 12 21 82 94 32 | -0.14 / -0.12 | none |
| all three, 0.2 | 12.0 | 50.6 | 0.65 | 1.2 | -47 | 79 11 17 81 97 36 | -0.14 | none |
| random 1,280, 0.2 (control) | 9.9 | 43.1 | 0.65 | 1.4 | -88 | 39 22 4 84 95 11 | -0.19 | none |

- **graded premotor pools do not make him step,** at these gains, on this body, with this loop: the same push-up, the same feet, no knee
  oscillates, and the inter-leg structure of the biological pools (-0.12 to -0.16) sits inside the random control's (-0.19). the graded
  units change what the cord does (13A / 13B graded quietens it, 21A graded doubles the leg output and drives the hind coxae) and not
  whether it alternates.

**the switch, at the end of 09-22.** in two days the leg row has tried, each once and labelled: fatigue (everywhere, on the inhibitors,
on the exciters), adaptation, rebound, the constant, the dose, noise, a jolt, a gated command, the load (constant, tripod-timed, with
a derivative), the claw, a flexion-biased population, the moonwalker, the brain's own descending output as a recording, a body that
stands, grips and co-contracts, the loop closed through the mid and hind legs, and now graded premotor units. every one changed what
the cord does; none made it alternate. the half-centre is in the wiring and its inhibitors do not reach the opposing exciters, and no
engine-level property tried so far substitutes for whatever closes that loop in life. what is left, honestly: (1) electrical synapses,
which no chemical connectome maps and which insect pattern generators use (a stand-in would be a guess about where they are); (2) the
tracing: the front legs' sensory set, the thin right mid extensor, the slow units, none of which a model change supplies; (3) the
premotor cells' own dynamics beyond a LIF or a graded unit (plateau potentials, which stick-insect non-spiking interneurons have, and
which nothing here has: a bistable graded unit is a different engine term, and the last one on the list I can source). the honest next
move is not another arm tonight. it is to write the row up as it stands, with the negative results as the result, and let the body row's
stand-ins (the tonus, co-contraction, the pads) go to nate for the default decision while the switch waits on (3) or on a better map.

## the review (18:27 PDT; nate: "should we set off a pair of opus agents to have a look at our hookups, physics, etc and see if our baseline
was indeed sound?"; `docs/REVIEW_BODY_LOOP.md`, an independent code-and-physics read of the whole body pipeline)

**three hookup errors in the body loop, each on its own enough to void "the loop is closed and nothing steps":**

- **F0. the standing stand-in replaced the cord instead of adding to it.** `experiments/body_loop.py` marked the stance (and, with `--cocon`,
  the swing) motor neurons as *driven* cells, and a driven cell fires from its assigned rate only: every synapse the cord sends it is
  ignored. so from 09:08 on, in every standing-body arm (the seeds, the flexion set, MDN, the unloading term, the pads, the descending
  playback, the graded pools on the body), 234 of the 259 joint-mapped motor neurons were Poisson sources scaled by load and the cord
  drove only the tarsi and the adductors. the tables above show it: the flexor and extensor rates did not move across no command, 100 Hz,
  400 Hz and the brain's own output, and I read that as robustness. **every standing-body result above, from "he stands" onward, is
  withdrawn as a result about the cord.** (the arms before the stand-in, lying down and tumbling, had no driven motor neurons and stand.)
- **F1. the knee-to-claw mapping lost its centre** in the move from `leg_loop.py` (which had the 90 deg centre) to `body_loop.py`: the knee
  angle is always positive in the body's coordinates, so the extension claw never fired in any loop arm and the flexion claw fired at 50-60
  Hz on straight knees. with SNpp51 driving flexion, the knee loop was positive feedback, and so were the hooks; positive feedback pins a
  joint at its limit, which is where the knees sat. and the SNpp50 / SNpp51 extension / flexion labels (`E_table_male.md`) have no source:
  both assignments have to be run.
- **F2. "standing" at 0.70 mm was the fly resting on his thorax:** per-segment ground force in the co-contraction arm: thorax 5.7 uN,
  abdomen 1.0, all six feet 3.3, of 10.05. the load rows never saw a loaded leg to unload. standing must be defined by weight on the feet.
- **F3.** under `--adhesion contact` the foot force includes the pad's pull (~20 uN), so the load term sits at its clip up to 94 % of the time
  on a stuck foot and the switch latches. **F7.** the "load" row also drives hair plates and vibration cells, and the floor holds claws of
  both tunings and hooks of both directions at 15 Hz together.
- **two engine-level facts for the refreeze day:** a driven cell loses ~3 ms after each spike (the refractory gate), so a nominal 100 / 400
  Hz is 81 / 182 measured (the playback under-delivers the loud descending cells); and the synaptic delay is 3 ms at the 1 ms tick, not
  1.8 (measured on a two-cell network). both were true of every run in this record.
- (a credit corrected: the 576 claw synapses onto IN21A004 are SNpp51's, not SNpp50's; the SNpp51 arm was run and was null.)

**clean:** the muscle-to-joint map and its signs (a synthetic push per role moves every antagonist pair oppositely on all six legs);
actuator, joint-angle and leg orders; the cord cut (every excitatory synapse onto the flexors' premotor cells kept; 1-6 % of their
excitation from driven sensory cells); the graded emission's timing and scale (no double counting); the sensory-class marking (no
interneurons silenced); the units (uN, nN m); the gait measures (a synthetic tripod scores antag -0.73, legs -0.81). **so the headless
cord's negative results stand; the body loop's are remade.** fixes, in the reviewer's order: F0 (the stand-in as an added current), F1
(the centre restored, both claw labellings run), F2 (standing = weight on the feet), F3, F7.

## the literature review (18:28 PDT; `docs/physiology/walking_review.md`, an independent read of the walking baseline against the field)

- **the rhythm is generated in the cord, not closed through the legs.** Sapkal et al. 2026 (bioRxiv 10.64898/2026.04.29.721658) drove DNg100
  in headless flies with the legs held in the air: the legs stepped at ~11 Hz, in a stronger tripod than on a ball, left-right antiphase
  on every pair; stumps with the femoral chordotonal organ removed still oscillated. **this row's reading since 09-21, that the rhythm comes
  back through the legs, is contradicted by the experiment that decides it.** (a citation corrected in place: the headless DNg100 walking
  result is Sapkal 2024, Nature 634:191, not Bidaye 2020, which is the P9 / BPN paper; Braun 2024: headless DNp09 does not walk forward,
  MDN does walk backward.)
- **a rhythm has been produced from this wiring.** Pugliese et al. 2026 (Tuthill / Brunton; `docs/research/sources/pugliese_2026_connectome_cpg.md`)
  ran the MaleCNS cord as a rate model and got a 7-15 Hz within-leg rhythm on the coxa's promotor and remotor from a three-cell loop,
  IN17A001 -> INXXX466 -> IN16B036 -| IN17A001. their decisive ingredient: **each cell's gain and threshold scaled by its size** (volume /
  surface area), stated necessary: "without adjusting a and theta for size, the network does not produce robust oscillations in response
  to DNg100 input." a uniform-threshold network, which ours is, is the configuration they say fails. in their model too the tibia flexors
  were silent or arrhythmic and the legs did not coordinate. the reviewer checked the male file today: all of Pugliese's and Sapkal's
  candidate rhythm cells exist, 6 per type; DNg100 -> IN17A001 818 synapses, IN17A001 -> INXXX466 2,733, INXXX466 -> IN16B036 445 (the weak
  link), IN16B036 -> IN17A001 3,705. IN09A002, the flexor inhibitor at 50-60 Hz in every arm, is in Sapkal's published motif, and DNg100
  excites it (1,026) harder than the rhythm cell (818).
- **the motor neurons' resting potentials are measured and graded by size** (Azevedo 2020): -68 / -60 / -48 mV for fast / intermediate / slow,
  input resistance 150 / 300 / 700 MOhm; the slow units fire ~30 Hz with no drive. a uniform-threshold LIF gives every cell the same 7 mV
  to threshold, so **"the slow units are not in the file" (09-22 01:07) was the engine, not the map**: in life the small cells are the ones
  that need almost no input. withdrawn in place as a statement about the map.
- **the claw labels are probably inverted:** SNpp50 excites the tibia extensor directly (470 synapses) and SNpp51 the flexors (360) and
  IN21A004 (577); by the measured rule (Lee 2025) that makes SNpp51 the extension-sensing claw; one indicator (SNpp50 -> 13B, 2,280 vs 511)
  disagrees. and "claw extension answered with more extension is the assistance reflex" does not hold: no reflex reversal is shown in
  Drosophila, and the stick-insect reversal answers movement during active flexion, not a steady position.
- **only one fly leg interneuron is known to be graded (13B-alpha), and it relays posture, not rhythm;** nothing is known of 13A, 21A, 19A,
  03A or 12B. the graded sweep of 17:48 had no fly source. gap junctions: no location, strength or count published for fly leg circuits.
  neuromodulation: the headless fly walks without the brain's modulatory neurons and Pugliese's model steps with none; both rank last.
- **the next moves, in the reviewer's order:** log the eight published rhythm cells in the cord under DNg100; rescore the coxa at 50-150 ms
  lags with fine bins (the coxal antagonist anti-correlation at 30 ms is half a 14 Hz cycle); run Pugliese's rate model on our table as
  the positive control; **size-scaled excitability in the LIF**; settle the claw labels. a fair negative has a narrow scope: "a LIF at Shiu
  2024's uniform constants fails where a rate model on the same table oscillates", and needs the positive control and a rhythm measure
  checked against a planted 10-15 Hz oscillation. **the burden is on the engine, not the wiring.**

**oracle (18:34 PDT), the engine with graded units present and off: PASS, v1 + v2, eight configurations, none differing (read from the log). committed.**

## the loop rings (18:40 PDT; the review's item 5: "the loop cells at Pugliese's LIF weight alone")

**the published rhythm cells under DNg100 in our cord, as they are:** IN17A001 17.8 Hz per cell, INXXX466 20.3, IN16B036 5.2, IN19A007 21.7,
IN03A006 15.6, INXXX464 10.8, IN12B003 37.8, IN09A002 40.5 (the reviewer's prediction: IN09A002, the motif's sink, loudest). their pooled
autocorrelations have the refractory trough at 20-30 ms and nothing after it: active, not ringing. the coxa rescored at rhythm lags
(`experiments/coxa_rhythm.py`: promotor vs remotor pools per leg, cross-correlation over +-150 ms, autocorrelation lobes, spectra against a
phase-shuffled null): no lobe, no antiphase, the spectral peaks at the null's level. **the cord at 0.185 mV does not ring.**

**size-scaled excitability** (`--size-gain A`: synapses onto cell i x (S_med / S_i)^A; `--size-thr B`: v_th = 7 x (S_i / S_med)^B; S = input
synapses, the size proxy this file has): at the record's constant it starves the large cells that carry the cord's activity (leg MNs
1.65 / 0.45 / 0.40 Hz at A 0.25 / 0.5 / 1.0; the threshold form the same) and no rhythm; with the constant raised to 0.275-0.37 the cord
comes back tonic (leg MNs 2-12 Hz), no lobe anywhere. Pugliese's necessary ingredient, in this LIF at these exponents, is not sufficient.

**the loop's own synapses** (`--edge-scale DNg100,IN17A001,INXXX466,IN16B036:F`: the 44 synapses among the four types scaled by F; 1.49 = the
published LIF weight 0.275 on the loop with the rest at 0.185):

| loop weight x | DNg100 | IN17A001 / INXXX466 / IN16B036 Hz | their autocorrelation at 70 / 140 / 210 ms | spectral peak |
|---|---|---|---|---|
| 1 (the record) | 100 Hz | 18 / 20 / 5 | -0.30 / -0.12 / -0.02 (the refractory trough only) | none |
| 1.49 | 100 | 23 / 28 / 10 | -0.21 / +0.05 / - | none |
| **3** | 100 | 35 / 52 / 28 | **-0.29 / +0.10 / -0.04** | 22 Hz x44 |
| 5 / 8 / 12 | 100 | 41-47 / 67-71 / 52-91 | -0.25 / +0.05-0.09 / 0 | 22-23 Hz x50-86 |
| 3 | 200 | 48 / 69 / 34 | -0.30 / -0.07 / +0.19 | 24 Hz x133 |
| **3** | **400** | **63 / 87 / 40** | **-0.15 / -0.45 / +0.18** | **25.0 Hz x270** |
| 5 | 400 | 67 / 97 / 70 | +0.14 / -0.28 / -0.28 | 26 Hz x363 |

- **at three times the constant on its own 44 synapses, under the high dose, the published loop rings.** logged at 1 ms (`--log-ms`): a
  25.0 Hz oscillation in IN17A001 (x480 the band median), INXXX466 (x702), IN16B036 (x288), with IN19A007 (x232) and **IN09A002, the flexor
  inhibitor, ringing with them (x368)**; the autocorrelation -0.18 at 20 ms, +0.19 at 40 ms, -0.15 at 60, +0.16 at 80: a clean 40 ms period.
  **seeds 10 and 12: 24.9 Hz, x393 and x386.** the first oscillation-shaped autocorrelation in this cord in two days, on the cells the field
  named, by the change the review ranked.
- the period is the loop's: three synapses at the engine's 3 ms effective delay plus the membrane's rise, ~40 ms round the ring, hence
  25 Hz, above Pugliese's 7-15 (a rate model with tau 20 ms; their linearised minimal circuit gave 14).
- **what reaches the muscles:** the left front leg's promotor pool carries the 25 Hz (x104 the median at 1 ms; the right front x23, the mid
  legs nothing) at 28 Hz per cell, but its promotor and remotor pools do not alternate (cross-correlation within +-0.03 at every lag): the
  rhythm arrives on both sides of the coxa in phase. the flexors stay at 0.04. on the body (`body_six`, a replay on flygym's springs) the
  coxa torque's spectrum peaks at 5 Hz: the twitch kernel (decay 20 ms) low-passes a 25 Hz drive to a flutter, and he turns 92 deg on the
  spot as before.
- so: the rhythm generator the field found is in this file and rings in this engine once its own synapses are strong enough; at the
  uniform constant it does not, which is the narrow negative the review asked for. what it does not yet do is alternate the coxa or reach
  the knee, and at 25 Hz it is faster than a leg can follow. next, in the cord: the ring's frequency against the delay and the membrane
  constant (a 1.8 ms delay at a finer tick will make it faster still; a slower loop needs what Pugliese's tau gives), and the second ring
  (INXXX464 <-> IN19A007) at the same scaling; and the body loop's three fixes so a ringing cord has legs to reach.

**the body loop repaired (18:53 PDT; the review's fixes F0-F3 in `experiments/body_loop.py`: the stand-ins as an ADDED CURRENT on the engine's
ext path (`--slow-mv`, 13.6 mV ~ 60 Hz alone; the driven form `--slow-hz` kept as the withdrawn one), the knee centred on its neutral angle,
`--claw-labels 50ext|50flex`, the pad's pull removed from the load, and standing judged by the ground reaction on the non-leg segments):**

| arm (20 s, seed 11, measured springs, pads, co-contraction 0.2) | thorax height | flexors | extensors | feet on the ground (%) | lf coxa peak |
|---|---|---|---|---|---|
| no command, tonus 13.6 mV | 0.85 | 0.00 | 36.3 | 60 1 17 62 2 2 | none |
| DNg100 100 Hz, tonus 13.6 | 0.86 | 0.04 | 42.6 | 49 1 14 54 2 17 | none |
| DNg100 100 Hz, tonus 8 | 0.41 (on the floor) | 0.00 | 29.0 | 47 9 23 28 5 3 | none |
| DNg100 100 Hz, tonus 13.6, claw labels swapped | 0.72 | **0.62** | 17.3 | 36 12 14 36 7 10 | 18 Hz x18 |
| **the ringing cord** (400 Hz, loop x3), tonus 13.6 | 0.40 (on the floor) | 0.12 | 53.4 | 19 2 3 8 3 7 | **25 Hz x34** |
| the ringing cord, tonus 8 | 0.40 | 0.09 | 47.7 | | 25 Hz x26 |
| the ringing cord, tonus 13.6, claw labels swapped | 0.62 | 0.49 | 36.2 | 15 42 3 20 3 8 | **25 Hz x118** |

- **with the tonus as a current the cord drives the muscles and the current sits under it:** the extensors run at 36-43 Hz (the cord's own
  9 plus the current), the flexors move with the claw labels (0.04 -> 0.62 when SNpp51 is taken as extension-tuned, the review's reading),
  and he holds 0.72-0.86 of height at 13.6 mV, the floor at 8. the first "standing" judged by the feet is the next batch (the statistic
  was wrong in this one: the body's own ground reaction is the number, fixed).
- **the ringing cord reaches the body's coxa** (the left front promotor pool at 25 Hz, x34-118 the median) and at the high dose the
  extensors run at 47-53 Hz and he sinks to the floor: the ring's command is the 400 Hz that lights it, and that dose pushes the whole cord
  hard. no knee oscillates below 25 Hz; nothing steps. the twitch kernel low-passes a 25 Hz coxa to a flutter.
- so the rhythm is in the cord and reaches a muscle, and it is too fast for a leg by a factor of two or three, in phase across the coxa's
  antagonists, and absent at the knee. running: the ringing cord on flygym's springs with film (nate: "i wanna see some leg motion"), and
  the standing checks with the repaired statistic.

**the positive control (18:54 PDT; `experiments/rate_model.py`, `docs/physiology/rate_model_control.md`: Pugliese 2026's rate model on our
cord table; their Methods: gain divided by size and threshold multiplied by size, median-normalised volume, DNg100 input 400 for MaleCNS;
our file has no volumes, so input-synapse count stands in, stated):**

- **the loop alone oscillates on our file at 10-18 Hz under their equation** (their ~14), and with the coxa motor neurons added drives the
  left front promotor pool at 17 Hz. the loop's wiring and signs are cleared. the rhythm survives the loop's 80 strongest partners and is
  gone by 160.
- **embedded in our front-leg network (3,109 cells; MANC's was 4,604) their model runs away:** about half the cells pinned near r_max, the
  rest silent, with size scaling on, total or off, at any input from 0.01 to 400, any b, one-sided DNg100, the DNs' own inputs cut; the
  loop cells pinned or switching at 1-3 Hz, IN16B036 and IN19A007 at 0 in every seed (inhibited by pinned cells), **IN09A002 pinned near
  200 Hz**. the whole cord the same with the inhibitors pinned instead of silent.
- so the control does not give the clean "wiring or engine" answer: under their model too, on our file, the network around the loop
  smothers it, and the sink is the same cell our LIF finds at 50-60 Hz. what it cannot separate: volume-based size scaling (theirs) from
  our synapse-count proxy, or the smaller network; their code or the MaleCNS volumes would settle it (a query to make: neuprint carries
  a size per body that the flat files do not). **in this engine the loop rings when its own synapses dominate the surround (x3); in
  theirs the loop rings alone and the surround smothers it. the two engines agree on where the problem is: not the loop, the balance
  around it.**

**the ringing cord on film (19:00 PDT; flygym's springs, the pads, the loop closed, 20 s; standing now judged by the ground reaction on
the non-leg segments, 0 = on his feet):**

| arm | body on the floor (% of his weight) | thorax height | flexors | extensors | lf coxa pitch (sd) / knee (sd) | joint spectra |
|---|---|---|---|---|---|---|
| DNg100 400 Hz (control) | 64 | 0.58 | 0.08 | 39.7 | 12 / - | |
| **the ringing cord** (400 Hz, loop x3) | 54 | 0.55 | 0.07 | 42.4 | 13.2 / 13.7 deg | peaks at 1.1-1.6 Hz, nothing at 25 |
| the ringing cord, claw labels swapped | **20** | 0.64 | 0.22 | 22.3 | 9 / 14 | |
| the ringing cord, measured springs, tonus 13.6 mV | 94 (on the floor) | 0.40 | 0.12 | 53.4 | | |
| DNg100 100 Hz, measured springs, tonus 13.6 mV | 33 | 0.86 | 0.04 | 42.6 | | |

- **the legs move, and the ring is not in them.** under the ringing cord the left front coxa swings 13 deg and the knee 14 (sd), the mid
  coxa 17, but the joint-angle spectra peak at 1.1-1.6 Hz with smooth autocorrelations: the 25 Hz that the promotor pool carries is
  filtered out by the twitch kernel (20 ms decay) and the leg's own inertia, and what remains is slow wander at the size of the
  control's. `world/body/loop/ring_springs.mp4` is the film nate asked for: a fly held by springs whose front legs stir at the ring's
  dose; nothing you would call a step.
- **standing, judged honestly, is not yet achieved in any arm:** the best is the swapped-claw arm on springs at 20 % of his weight on the
  body; the current tonus at 13.6 mV under the record's dose leaves a third of him on the floor (the earlier "0.86 of height" was the
  abdomen up and the thorax down); under the 400 Hz dose the extensors at 47-53 Hz drive him flat regardless.
- so the ring is real in the cord and lost at the body, for two reasons the record can name: its period (40 ms, the loop's three
  delays) is two to three times too short for a leg, and it reaches the coxa's antagonists in phase. the two engines' controls agree
  the loop's surround is the problem and name the same sink (IN09A002). next, in the cord: a conduction delay on the loop's cells (a
  per-cell output delay in the engine; axonal delays in the cord are real and unmeasured, (E)) to see whether the ring slows to the
  band, and depression on the sink itself.

**the sink (19:01 PDT; IN09A002 + IN16B016, the flexor inhibitors both engines find pinned, depressed (u 0.2, tau 1 s) or silenced, in the cord):** without the ring (DNg100 100 Hz): leg MNs 5.1 / 4.1 Hz per cell (from 2.0), flexors 0.01 / 0.00, no rhythm. **with the ring** (400 Hz, loop x3): leg MNs 15.0 / 12.4, flexors 0.16 / 0.07, and with IN09A002 silenced the front legs' promotor and remotor pools anti-correlate at the ring's half-period (lf -0.26 at +10 ms, rf -0.22; the promotor spectrum 24-25 Hz at x40 / x22 against a shuffled null of x5.6): **the first antiphase between a coxa's antagonists on this row**, at 25 Hz, and only when the sink is out. the sink is where the ring's alternation dies in this cord as in Pugliese's model; in life IN09A002 is part of Sapkal's motif, so silencing it is a diagnostic, not a correction.

## the ring slowed, and the coxa alternates (19:07 PDT; `--cell-delay`: a per-cell conduction delay in the engine (the delay line is
Dmax long and a cell's emission is inserted at its own delay; off by default; oracle running); on the loop's three cells IN17A001, INXXX466,
IN16B036, with the loop at x3 and DNg100 at 400 Hz; the cord, 30 s, seed 11, logged at 1 ms)

| delay on the loop cells | the ring (IN17A001 / IN16B036) | lf promotor pool | lf promotor vs remotor cross-correlation |
|---|---|---|---|
| the engine's (3 ms effective) | 25.0 / 25.0 Hz, x480 / x288 | 25.0 Hz x104 | -0.03: in phase |
| 4 ms | 20.3 / 20.3, x464 / x346 | 15.1 x46 | -0.03 |
| 6 ms | 16.2 / 16.9, x235 / x118 | 13.6 x91 | -0.03 |
| 8 ms | 13.8 / 13.8, x77 / x76 | 11.8 x276 | **-0.38 at +10 ms, +0.31 at +50** |
| **12 ms** | **10.4 / 10.4**, x47 / x90 | **8.8 Hz x771** | **-0.37 at 0 ms, +0.31 at +60 ms** |

- **the delay sets the period, as the arithmetic said,** and as the ring slows into the band a fly steps at, the left front coxa's
  promotor pool carries it harder (x46 -> x771 the median) and **its promotor and remotor pools alternate:** anti-correlated at zero lag and
  back in phase half a period later, at 8.8 Hz (12 ms) and 11.8 Hz (8 ms); the right front coxa the same, weaker (-0.24 / +0.16). the
  promotor autocorrelation at 70 ms is -0.49 at 12 ms. **the first alternation between a joint's antagonists on this row, at the walking
  frequency, from the published loop at the published weight with a conduction delay.** (Pugliese 2026's result, coxa promotor vs remotor
  at 7-15 Hz, reproduced in the spiking engine; Sapkal 2026's headless flies step at ~11 Hz.)
- **who carries it, at 12 ms (1 ms bins):** left front promotors 24 Hz per cell at 8.8 Hz (x654), remotors 15 Hz (x39), the tibia extensors
  22 Hz (x169), the trochanter depressors 7 Hz (x14); left mid remotors 11 Hz (x101), tibia extensors 76 Hz (x78); right front trochanter
  depressors (x58). **the tibia flexors and the trochanter levators: 0.0 Hz in every leg.** the rhythm is on the stance side of every joint
  and alternates only at the front coxa. the mid and hind legs carry the beat without alternation.
- the delay is a stand-in with a source and no measurement: axonal conduction in the cord is real, intersegmental premotor cells are
  long, and no per-cell delay is published (E); the loop's 12 ms is chosen for the band, which is a fit to physiology (the step frequency of
  a headless fly), not to the gait. the ring's own weight (x3 on 44 synapses) is the other stand-in, labelled since 18:40.

- **seeds (19:09 PDT):** the alternation replicates: left front promotor vs remotor -0.38 / -0.39 / -0.37 at zero lag and +0.34 / +0.34 / +0.31 at half a period, 8.8 Hz on seeds 10, 12 and 11; the right front -0.29 / -0.29 / -0.24. the promotor autocorrelation at 70 ms -0.51 / -0.50 / -0.49. three of three.

## a leg steps (19:20 PDT; the slowed ring on the body: flygym's springs, the pads, the loop closed, 20 s, seed 11)

| arm | body on the floor (% of his weight) | lf coxa pitch (sd, peak, autocorr 60 / 110 ms) | lf tibia pitch | rf coxa pitch | foot lifts > 50 ms (lf lm lh rf rm rh) |
|---|---|---|---|---|---|
| the ring at 12 ms (10 Hz), claw labels as the table has them | 57 | 16.9 deg, 2.1 Hz x230, -0.10 / +0.29 | 2.5 Hz | 2.8 Hz | 4 69 29 46 6 68 |
| the ring at 8 ms (14 Hz) | 53 | 16.2, 11.1 Hz x101 | 2.6 Hz | 2.9 Hz | 3 50 27 44 10 58 |
| **the ring at 12 ms, the claw labels swapped** (SNpp51 extension-tuned: the review's reading) | 94 | **18.6, 8.8 Hz x558, -0.36 / +0.49** | **8.8 Hz x1246** | 8.8 Hz x174 | **102** 67 3 1 78 4 |
| the ring at 12 ms, measured springs, the tonus current | 96 | 38.6, 2.6 Hz | | | 89 107 119 67 53 87 |

- **with the claw labels swapped, the left front leg steps.** its coxa pitch swings 18.6 deg (sd) at 8.8 Hz with an autocorrelation trough
  at 60 ms and peak at 110 (a clean cycle), its tibia at the same 8.8 Hz (x1246 the median), and its foot leaves the ground 102 times in
  18 s. the right front coxa carries the same 8.8 Hz weaker. the rest of him lies on his belly (94 % of his weight on the floor; the
  400 Hz dose that lights the ring also drives the extensors to 21-40 Hz and folds him), and the mid legs tap as before. so: **one leg
  stepping at the frequency a headless fly steps, on a fly who is lying down.** `world/body/loop/dly12_springs_flex.mp4`.
- the swap matters, and it is the review's F1 in action: with SNpp51 taken as the extension-tuned claw, an extended knee feeds the
  flexors' premotor cell (IN21A004, the 577 synapses) and the position loop is negative feedback at the knee; with the table's labels
  it is positive and the ring is filtered out (2.1 Hz wander). the labels are unsourced either way; the swapped assignment is the one
  under which the wiring's own reflex sign comes out as life has it, which is a reason but not a measurement.
- the tibia flexors themselves still fire at 0.28 Hz; the knee's rhythm at 8.8 Hz is the extensors modulated by the ring against the
  springs. the stance-side rhythm with a swing-side reflex, not yet a swing muscle.

- **the step test (19:21 PDT), the one that failed on every lift before:** the left front foot's 102 lifts last 145 ms and come every 176 ms (cv 0.62, against 0.93 for his lifts in the garden); the coxa swings +7.8 deg forward during a lift and -8.3 deg back on the ground, with sign agreement 0.55 / 0.44 (0.12 before): protraction in the air, retraction on the floor, a swing and a stance. the coxa pitch autocorrelation -0.36 / +0.49 / -0.33 / +0.36 at 60 / 110 / 170 / 230 ms: a sustained 9 Hz cycle. the foot is on the ground 12 % of the time: a leg stepping mostly in the air, on a fly lying down. seeds running.

- **seeds (19:25 PDT):** the stepping leg replicates on seeds 10 and 12: left front coxa at 8.8 Hz (x202 / x477), autocorrelation -0.39 / +0.49 and -0.40 / +0.47 at 60 / 110 ms, 128 and 106 lifts, interval cv 0.51 and 0.57, sign agreement of the coxa's swing during lifts 0.70 and 0.66 (0.55 on seed 11). **one honest wrinkle:** on seed 10 the coxa swings *backward* during lifts (-17 deg) where seeds 11 and 12 swing forward (+8, +9): the rhythm and the lift are the same on all three, the direction of the swing is not, so the step's direction is not yet the cord's to claim. three of three on the rhythm; two of three on the direction.

**oracle (19:32 PDT), the engine with per-cell conduction delays present and off: PASS, v1 + v2, eight configurations, none differing (read from the log). committed.**

**the ring at a lower dose (19:34 PDT; the loop stronger so it rings under less command; 12 ms delay, claw labels swapped, the pads, the
loop closed, 20 s, seed 11):**

| arm | body on the floor (% of his weight) | thorax height | lf coxa pitch: peak, autocorr 60 / 110 ms | foot lifts (lf lm lh rf rm rh) | flexors / extensors |
|---|---|---|---|---|---|
| DNg100 400 Hz, loop x3, springs (the stepping arm above) | 94 | 0.57 | 8.8 Hz x558, -0.36 / +0.49 | 102 67 3 1 78 4 | 0.28 / 21.3 |
| 200 Hz, loop x5, springs | **10** | 0.70 | 9.3 Hz x246, -0.39 / +0.49 | **126** 2 28 43 18 11 | 0.26 / 14.4 |
| **100 Hz (the record's dose), loop x8, springs** | **2** | 0.68 | **8.9 Hz x220, -0.20 / +0.42** | **126** 1 8 64 75 2 | 0.31 / 9.8 |
| 200 Hz, loop x5, measured springs + the tonus current | 63 | 0.64 | 2.8 Hz (wander) | 53 35 73 60 33 78 | 0.60 / 26.4 |
| 100 Hz, loop x8, measured springs + the tonus current | 77 | 0.59 | 9.4 Hz x94 under +0.77 / +0.85 (drift) | 47 14 64 51 31 86 | 0.76 / 20.4 |

- **at the record's dose, with the loop at eight times the constant, on flygym's springs, he stands on his feet (2 % of his weight on
  the body) and his left front leg steps at 8.9 Hz, 126 lifts in 18 s;** the right front lifts 64 times and the right mid 75, without the
  9 Hz cycle (their coxae wander). the extensors are at the record's 9.8 Hz per cell, the cord is the record's cord with one loop's
  synapses strong. `world/body/loop/ld_100_x8_springs.mp4`.
- on real-stiffness legs with the tonus current he does not stand (63-77 % on the floor) and the wander swamps the cycle: the standing
  problem is still the standing problem; the stepping leg needs a body held up by something, and the springs are that something for now.

- **seeds (19:39 PDT), the standing-and-stepping arm (DNg100 100 Hz, loop x8, delay 12 ms, claw labels swapped, springs, pads, the loop closed):** three of three. body on the floor 2 / 2 / 1 % of his weight; the left front coxa at 8.9 / 9.6 / 9.1 Hz (x220 / x222 / x173), autocorrelation -0.20 / -0.27 / -0.22 at 60 ms and +0.42 / +0.42 / +0.46 at 110; 125 / 123 / 116 lifts, interval cv 0.50 / 0.51 / 0.50; the coxa pitch changes -14 / -15 / -13 deg during a lift with sign agreement 0.81 / 0.80 / 0.83. by the measured joint roles (`results/body_dof_signs.json`: the left front leg protracts on coxa pitch with sign -1) a negative pitch change is the foot swinging FORWARD: **protraction in the air, three seeds of three, at 0.8 agreement.** (the 400 Hz arm above swung the other way on one seed; at the record's dose the direction is the cord's.) so, on springs: he stands on his feet and his left front leg takes steps, forward in the air and back on the ground, nine a second, at the frequency of a headless fly's.

**the fling at two seconds (19:42 PDT; nate: "he holds a standing posture, abdomen up, for two seconds ... and then flings himself at that 2 s mark"):** the two seconds are the warm-up: the cord under its floor with no command, and the body in NeuroMechFly's micro-CT neutral pose held by the springs at 0.97 of height (the package's posture, not his). at 2.000 s the walking neuron steps from 0 to 100 Hz in one millisecond, the ring lights, and the transient is the fling: thorax speed 0.2 mm/s in the second before, 4.7 in the second after. `--walk-ramp`: the command rising over 1 s cuts the onset to 1.9 mm/s, over 3 s to 1.3, and the steady state is the same either way: he sags from 0.97 to 0.67 of height under the command, shuffles and turns at 4 mm/s on his feet (1-2 % of his weight on the body), and the left front leg steps at 9-9.5 Hz (82-96 lifts in the last 14 s). so the fling is the step in drive, gone with a ramp; the crouch is the command's steady state, and a fly walking is lower than a fly standing, which is also true of the animal.

## the second pass (19:56 PDT; nate: "bring back those two agents ... see if they think you did them some justice"; `docs/REVIEW_BODY_LOOP.md`
"## second pass": the same reviewer, the repairs and the result; the record arm re-run and three controls, 20 s each)

- **the repairs are right and nothing in the new code fakes the result.** the tonus as an added current, the knee centred, the standing
  check (the right column and sign), the pad's pull subtracted (right on average, flickering ~1,300 times in 18 s; immaterial here), the
  delay line's bookkeeping including scales and graded cells. two traps noted: `--slow-mv` defaults to `--slow-set size` (the flexors;
  every saved run passed `stance_all`); `--edge-scale x8` also scales DNg100's own synapses onto the ring cells.
- **the 9 Hz is the cord's, not a resonance.** without the ring (its synapses back to x1): 2.6 Hz wander, 19 lifts; without the command:
  the coxa barely moves; the frequency tracks the delay; the promotor pool's spike counts are coherent with the coxa angle at 0.95-0.98.
- **the standing is the springs.** withdrawn in place as his: with the command off he carries 3.8 % on the body at 0.92 of height, better
  than the record's arm; the command lowers him to 0.68; without the ring half his weight is on the floor. "the springs hold him up while
  a leg moves" is what is true.
- **the sensory loop has no part in this arm.** with `--loop off` (no claw, hook or load; the pads never engage) he steps at 9.5 Hz, 107
  lifts, the right front coxa joining. **"the swap is the review's F1 in action" (19:20) is withdrawn for this arm:** the labels did not
  make the difference here. (they did change the 400 Hz arm from wander to rhythm; that arm is not the record arm.)
- **it is not yet a step:** the promotor pool carries the rhythm and the remotors only faintly (-0.14 at +20 ms); the trochanter levators
  are silent; in this body pulling the front coxa forward also lifts the foot, and "back on the ground" is the spring returning the coxa,
  not a muscle; the foot is in the air 67 % of the time (foot heights rebuilt from the saved joint angles); no other leg is coordinated
  with it. **"forward" has the right sign** (+x is the front; a negative coxa pitch moves the foot forward), with the coxa moving forward
  during 65-74 % of lifts by the reviewer's lift criterion (the record's 0.8 was a different criterion). so: one muscle pool's twitches,
  at the cord's rhythm, ridden by a spring. the reviewer's next: the same arm on the measured springs with the added-current tonus (77 %
  on the floor there now), and a stance phase that muscles drive.
- **a bug older than tonight, in both engines:** short-term depression cuts every spike's delivery by (1 - u) even on a fresh synapse
  (the scale pushed onto the delay line is read after the decrement that the same spike caused): in a two-cell test with u 0.5 a fresh
  synapse delivered 7.57 instead of 15.15. **every `--std` arm in this record ran that way**, including the run of record's `--std pair`
  (u 0.08: the pair's synapses at 0.92 of nominal). tonight's stepping arm has depression off and stands. fixed below with its oracle; the
  run of record's pair to be re-measured.

## the literature reviewer's second pass (19:58 PDT; `docs/physiology/walking_review.md` "## second pass"; the reviewer ran Pugliese's own
code, github.com/smpuglie/Pugliese_cpg_2025)

- **their spiking loop rings at ~13.5 Hz with no added delay:** five isolated cells at their weight 0.275 mV (x1.49 ours) and the usual
  1.8 ms delay; the period is set by I1's single large inhibitory kick onto E1 and E1's recovery, not by conduction time. **at x3 their own
  model rings at 26 Hz**, the row's 25.0. so the fast ring is what this circuit does at triple gain, and **the 12 ms delay made up for the
  gain, not for something missing from the loop.**
- **neither stand-in is a physiology fit, and the record called them that (18:40, 19:07): corrected in place.** nothing published supports
  x3 or x8 (x8 is five times their spiking weight); no conduction delay is published for any fly premotor cell (the giant fibre conducts at
  1.15-2.07 m/s, Kadas 2019; scaled to thin premotor axons, 0.2-2 ms (E)). **the 12 ms delay is a frequency fit with no source; the loop
  weight is a gain fit beyond the published value.** both stay in the record as the labelled fits they are.
- **their full network is quiet, ours is busy:** 0-7 motor neurons active per replicate in their DNg100 runs (most often 3); ours 52 and
  up, and the rate model runs away on our file. **why ours is dense is the question**, not how to push the loop past its surround.
- **the claw labels:** nothing new settles them; the direct wiring supports the swap, the two-synapse effects are mixed; every body result
  is to be reported under both labellings (the second-pass code review found the labels immaterial to the record arm, which helps).
- **"9 Hz, the frequency a headless fly steps" is circular:** the delay was chosen to land there, and Sapkal's ~11 Hz is air-stepping. the
  independent test: does the ring speed up with the DNg100 dose, as the fly's stepping does and Pugliese's rate model does. (in this record,
  the x3 loop at 100 / 200 / 400 Hz rang at 22 / 24 / 25 Hz: barely.)
- **the other legs:** Sapkal names 19B commissural -> 19A for left-right alternation and 19A intersegmental -> 19A for neighbouring legs on
  one side; no model has coupled the legs yet. the next target: all six loops (one per hemineuromere) logged together, their phases.
- **claims in this record that overreach their sources, corrected here** (the reviewer's softer wording adopted): "at the published weight"
  -> at three to eight times it; "Pugliese's result reproduced in the spiking engine" -> a ring of the same cells in this engine at a gain
  their model also rings at; "the frequency a headless fly steps" -> a chosen frequency; "the field found" the generator -> two preprints
  calling the circuit putative; "the slow units were the engine, not the map" -> at least partly, and size scaling then failed; **"a leg
  steps" -> a front coxa alternating on stiff springs with the swing muscles silent**; "the review's reading" for the label swap -> the
  labels are uncertain.
- **the revised order:** log all six loops; run their rate code on their table and on ours to find why ours is dense; hold the loop at
  x1.49 and remove named surround cells one at a time (IN19A002 / 005 / 008, IN26X001, IN09A002) to see which lets it ring; measure the
  ring against the dose; both claw labellings beside every body result.

**the surround, one cell at a time (20:02 PDT; the loop at the published x1.49, DNg100 100 Hz, `--silence` on IN19A002 / IN19A005 / IN19A008 / IN26X001 / IN09A002 singly and all five together; 1 ms logs):** no ring in any arm. IN17A001 at 22-23 Hz per cell and IN16B036 at 9-14 with spectral peaks at 19-22 Hz of x38-66 the median and autocorrelations within +-0.05 at 40 and 70 ms (the ring proper had -0.18 / +0.19); silencing all five raises IN16B036 to 13.6 Hz and nothing else. so the five cells the reviewer named are not what holds the loop below threshold at its own weight in this engine; the density of the surround is (their runs: 0-7 motor neurons active; ours: 100+), and that is the next question, with their code on their table beside ours.

**Pugliese's code and data (20:04 PDT; nate: "is this pugliese paper or code something we can/should look at?"):** cloned to `ref/pugliese_cpg` (untracked; github smpuglie/Pugliese_cpg_2025; JAX, tutorials, configs). inside it, the thing this file lacks: `data/imac t1 connectome data/wTable_20260210_vncRoisOnly.csv`, their processed table of the male cord's front-leg network, 4,310 cells with a `size` per cell (voxel volume, median ~1e9) keyed by bodyId, and `W_*.csv`, their weight matrix for the same cells; `src/utils/sim_utils.py: set_sizes` is the scaling exactly (size / median; gain / size; threshold x size); `configs/neuron_params/default.yaml` the parameters (tau 20 ms, gain 1, threshold 7.5, cap 200 Hz, 0.03 per synapse both signs). so the positive control can be run with their sizes on our table and with their table on the same model: the "why is ours dense" question has its instrument. (what they achieved, for the record: a rate model of four cord connectomes driven by DNg100 gives 7-15 Hz rhythmic leg motor output; pruning finds a three-cell loop necessary and sufficient across the four; headless flies confirm DNg100 drives stepping; within-leg only, no interleg coordination, the tibia flexors silent in theirs too; a preprint, "putative" throughout.)

**their sizes in our engine (20:09 PDT; `--size-from` their wTable: 4,242 of the cord's cells matched by bodyId, the rest at the median;
their scaling exactly, gain / size and threshold x size (`--size-gain 1 --size-thr 1`, clip 10); the cord, DNg100 100 Hz, 30 s, seed 11):**

| arm | leg MN Hz | active | **flexors** | extensors | antag | the loop cells (autocorr 40 / 70 ms) |
|---|---|---|---|---|---|---|
| the record (uniform) | 1.96 | 52 | 0.00 | 9.3 | -0.16 | refractory trough only |
| gain / size | 3.03 | 74 | 0.00 | 5.5 | -0.16 | |
| threshold x size | 3.01 | 74 | 0.01 | 5.3 | -0.17 | |
| both (their scaling) | 5.58 | 67 | 0.01 | 20.9 | -0.36 | flat (+0.00 / -0.01) |
| **both, at their weight 0.275 mV** | 16.4 | 104 | **12.4** | 9.9 | **-0.50** | flat |
| both, the loop at x1.49 | 5.84 | 67 | 0.00 | 22.1 | -0.40 | flat |
| both, DNg100 400 Hz | 8.58 | 70 | 0.00 | 28.6 | -0.46 | flat |

- **no ring** (the loop cells' autocorrelations within +-0.04 at 40 and 70 ms in every arm), so true sizes alone do not do in the LIF what
  they did in their rate model.
- **but with their scaling at their weight the tibia flexors fire, 12.4 Hz per cell, from 0.00 in every arm for two days,** the extensors
  at 9.9, the antagonist correlation the most negative on the row (-0.50): the size principle with real volumes (small cells excitable,
  large cells hard to drive: Azevedo 2020's rest and input resistance by class, Lesser 2024's weights by size) wakes the swing side of the
  knee, which no dose, population, reflex or engine term managed. the sizes are measured (their table), the scaling is their published
  form, and 0.275 is Shiu's constant. **the first swing muscles on, from physiology, in the cord.** no rhythm in them yet.

**withdrawn (20:15 PDT), the flexors under true sizes:** the "12.4 Hz per cell" is two left hind tibia flexor cells at 248.7 Hz with an
inter-spike interval of exactly 4 ms (cv 0.000, the refractory ceiling), firing in lock-step (coincidence 1.0), one at 83 and one at 71,
and the other thirteen at 0; the "10 Hz rhythm" in them (autocorrelation 0.84 at 100 / 200 / 300 ms) is my sampling landing on the comb
of a 4 ms period. the size rule at exponent 1 puts the smallest cells' thresholds at 2.3 mV and pins them. **not swing muscles recruited
from physiology; two cells pinned by the scaling.** the antagonist column's -0.50 is those pinned cells against the extensors.

## the cut (20:15 PDT; the positive control's second pass, `docs/physiology/rate_model_control.md` "with their sizes and their table")

- **the equation printed in the preprint is not what their code runs** (`vnc_sim.py`: the gain inside the tanh is a / r_max and DNg100's
  input is I, not r_max x I); the printed form saturates their own table as it did ours. with the code's form, **their table oscillates in
  our port** (11-15 Hz, 74-197 cells active, none saturated, 3-9 front motor neurons on one DNg100, promotor-remotor antiphase -0.73 to
  -0.87, the tibia flexors silent), and **our cord table restricted to their 4,242 cells with their sizes oscillates too** (the loop at
  12-14.4 Hz, 4-8 motor neurons, the same offset). the wiring is cleared: 117,347 shared edges with the same weights (median ratio 1.00),
  not one sign disagreeing, the inputs onto IN17A001 / INXXX466 / IN16B036 / IN19A007 / IN09A002 identical.
- **why ours is dense: the headless cut kept the brain.** `scripts/build_cord.py` keeps every edge between kept cells, and 25,157 of them
  are synapses ONTO descending neurons from other descending and ascending neurons, ~623 k synapses, which sit in the brain (their matrix
  counts only synapses inside the cord's ROIs: DNg100's inputs +0 / -84 in theirs, +2,300 / -3,900 in ours). a decapitated fly does not
  have them. with both DNg100s driven our table runs away (2,063 cells active, 610 saturated) and theirs stays sparse; **with those edges
  dropped ours runs sparse and rhythmic too** (177-202 cells, none saturated, 10 motor neurons, both loops at 12-14.4 Hz).
- **every cord arm since 09-21 22:20 ran with the brain's synapses onto its descending neurons.** the cut is fixed below (v2: no synapses
  onto descending neurons; v1 kept for the record), and the baseline arms are re-run on it before anything else is claimed. the
  synapse-count size proxy is also out (it overstates the big cells 2-3x and leaves the loop silent); their volumes stand in for the
  4,242 cells they cover.

**the depression fix, oracle (20:19 PDT):** `scripts/oracle_check.sh` v1 + v2, all eight configs bit for bit (`--std off` in every oracle config; the fix touches only the depressed path). the scale a spike delivers is now the resource before its own decrement; a fresh synapse delivers 1, not 1 - u. the `--std pair` run of record is re-measured under it before the 09-21 depression numbers are cited again (TODO 4i).

## the cord on the corrected cut (20:24 PDT; `scripts/build_cord.py` v2: no edges onto a descending neuron from a descending or ascending cell, 1.01 M synapses across the 1,310 DNs; v1 kept beside it as `brain_cord_v1.npz`; 30 s, seed 11, DNg100 100 Hz, 0.185, the 423 leg motor neurons and Pugliese's cited cells logged at 1 ms)

- **the baseline moves.** the control's leg motor neurons 1.99 -> 4.33 Hz per cell, 54 -> 95 active, the cord itself unchanged (1.13 -> 1.10 Hz per
  cell); the DNs had been held down by their own brain-side inhibition. the flexors stay silent (0.00 Hz) and the extensors hold (9.3 -> 8.0 Hz);
  no inter-leg phase (legs +0.00), no promotor-remotor antiphase (xcorr min -0.05 to -0.15, no lobe), same as v1.
- **a line at 20 Hz, at the published weight, in the loop cells.** IN17A001 / INXXX466 / IN16B036 / IN09A002 at 17 / 19 / 5 / 38 Hz per cell,
  each pool with a spectral line at 19.7 Hz, 45 / 51 / 21 / 46 times the 2-60 Hz band median; the autocorrelation alternates sign at 25 / 50 / 75 /
  100 ms (-0.07 / +0.05 / -0.03 / +0.02: a damped 20 Hz). **checks:** the chunk is 10 ms (a seam would sit at 100 Hz); the DNg100 drive is
  flat (top peaks x10 at 90-110 Hz); the cells are irregular (ISI cv 0.68-1.13, no cell regular at 20 Hz), the pooled line beats a rolled null
  (each cell's train rolled by a random offset) 45 vs 14, 51 vs 13, 46 vs 8, and pairs of cells correlate +0.12 to +0.17 at 5 ms: **shared,
  not one regular cell.** three seeds: 19.7 / 16.4 / 17.8 Hz (x45 / x29 / x38). dose: the loop's edges x0.5 -> 18.1 Hz x20, x1.49 -> 21.6 x43,
  x2 -> 20.8 x61-71; DNg100 at 50 Hz -> 17.6 x36; at rest (no command) the same cells carry a weak 10-12 Hz (x12-21).
- **it is not the three-cell loop.** silence IN16B036 (the inhibitory arm): the line stays, 19.1 Hz x30-38 in the other three. silence
  INXXX466: 21.6 Hz x31 in IN17A001. silence IN17A001: the line drops to 13.6 Hz (x18-28) in INXXX466 / IN16B036 / IN19A007 / the trochanter
  flexors, x20 at 18.1 in IN09A002. a rhythm that survives the loss of any one arm of a loop is not that loop's. **where it lives:** across
  the 423 logged cells the strongest lines at 19.7-20.0 Hz are IN19A007 (x53), INXXX466 (x39), the Tr flexor MNs (x38, 35 cells at 3 Hz),
  IN09A002 (x37), IN17A001 (x36), INXXX464 (x30), the Sternotrochanter MNs (x28), IN16B036 (x21): **Pugliese's wider subnet and the
  trochanter motor neurons, with their frequency set in part by IN17A001** (13.6 Hz without it). the front promotor pool carries it weakly
  (left front 20.0 Hz x18, r +0.09 with IN17A001 at +10 ms), the tibia extensors of the left front and right hind at 19.7 (x10-12).
  **and v1 had it:** the same logged cells on the old cut at 10 ms, 20.1 Hz x23 (the "beat" column at R2 / 18 Hz in the 09-21 gait tables
  was this). so the corrected cut did not create the 20 Hz; it lifted the DNs, the loop cells fire more (v1: IN17A001 under 5 Hz), and the
  line got loud enough to read. the whole cord's population count keeps its 9.5 Hz line on both cuts (x165 v1, x222 v2; x328 with
  IN17A001 silenced), the one the second pass already put on record as the cord's own.
- **standing claims, unchanged:** no step, no flexor, no inter-leg phase. what changed is the count of active motor neurons and a rhythm
  at twice Pugliese's frequency in his cells that his loop does not own. the subnet silencings (each cited cell alone, all eight together,
  the three-loop cells together) and the v1 cut read at 1 ms are running.

**the body on the corrected cut, the published wiring alone (20:26 PDT; `experiments/body_loop.py`, DNg100 100 Hz ramped over 1 s, the loop
closed (position + load), springs, pads, NO edge scale, NO cell delay, 20 s, seed 11; both claw labellings):**
- **claw labels swapped (50flex):** he stands. the body rests 2 % of his weight on the floor, the feet carry 10.3 uN; leg motor neurons 2.16 Hz
  per cell, flexors 0.13 (v1's 0.00), extensors 5.31; thorax height 0.69 mm (min 0.50); speed 2.8 mm/s. the left front foot leaves the ground
  14 times in 18 s (lifts over 50 ms, by height; 24 by zero net force; the two masks agree 90 %), the coxa pitch changing -8.5 deg during a
  lift, forward on 0.86 of them. **no rhythm in any coxa:** every coxa's spectrum peaks at 1.1-2.0 Hz (drift), the front coxa's autocorrelation
  at half and one period of that +0.08 / +0.04. so on the published wiring: standing, an occasional forward lift, no stepping.
- **claw labels as printed (50ext):** he collapses, 64 % of his weight on the floor, extensors 16 Hz, one lift in 18 s.
- **against the record's arm** (`ld_100_x8_ramp1`: loop x8, 12 ms delay, the v1 cut): 116 lifts, the front coxa at 10.1 Hz (x621). **the nine
  steps a second were the fit's** (x8 on the loop's edges, an unsourced 12 ms delay); the corrected cut at x1 does not step. the 20 Hz of the
  cord is in the body arm's own cells (the trochanter flexor motor neurons 22.4 Hz x38 at 10 ms with the labels as printed, 18.0 x14 swapped)
  and does not appear in the joints (every coxa's 12-30 Hz band is the 1/f tail at 12 Hz, on the record's arm too): the body low-passes it.
- **what stands on the corrected cut, then:** posture from the cord's tonic output on springs and pads; a front foot that lifts forward about
  once a second; the cord's 9.5 Hz population line and a 16-22 Hz line across Pugliese's subnet, neither of which reaches a joint. the
  same arm with x8 and the delay on the corrected cut is running for the comparison; it is a fit either way and is reported as one.

- **the fit on the corrected cut (20:28 PDT; loop x8, 12 ms delay, labels swapped, otherwise as above):** the same as on v1. 3 % of his weight
  on the floor, 124 lifts in 18 s (both masks, 88 % agreement), the left front coxa at 9.5 Hz (x708; autocorrelation -0.16 / +0.39 at half and
  one period), the coxa forward on 0.77 of the lifts; flexors 0.22 Hz. the stepping leg is robust to the cut and belongs to the fit.
- **subnet silencings (each of Pugliese's cited cells alone; the 20 Hz line read as before):** IN19A007 out -> 21.9 Hz x40; IN09A002 out
  -> 19.3 x35; INXXX464 out -> 21.2 x23; IN03A006 out -> 16.0 x41; IN12B003 out -> 20.0 x54. **no single cited cell owns it.** the three loop
  cells out together: 13.6 Hz x24 across the logged cells (INXXX464 / IN19A007 / the Tr flexors at 20.5, x15-19), the same 13.6 the loss of
  IN17A001 alone gave. **all eight cited cells out together: the 20 Hz is gone** (the logged cells' strongest line is the cord's 9.6 Hz at x18;
  the leg motor neurons fall to 1.84 Hz per cell, 44 active). so the rhythm needs the subnet as a whole and none of its cells singly; IN17A001
  sets its frequency (20 -> 13.6 without it). a distributed oscillation among Pugliese's eight, not his three-cell loop.

**withdrawn in place (20:30 PDT): "the baseline moves."** the 1.99 -> 4.33 Hz and 54 -> 95 active above compared the 373 leg motor neurons of
09-21 with tonight's logged set of 423, which adds Pugliese's fifty cited interneurons and the driven DNg100 pair at 100 Hz; averaged
together they read 4.5. the old cut re-run tonight is bit for bit the 09-21 control on the 373 common cells (max difference 0.000 Hz), and
the four-way cross of the 09-21 cord script and engine against tonight's gives 1.96 / 52 in every combination: **no dynamics changed since
09-21.** on the matched 373: v1 1.96 Hz per cell, 52 active, tibia extensors 9.25; v2 1.84, 52, 7.96; the loop cells 17.8 / 20.3 / 5.2 ->
16.9 / 19.3 / 4.6 Hz. **the corrected cut changes almost nothing in the LIF,** and the reason is the engine's drive gate: a driven cell's
membrane does not integrate its synapses (`_drive_gate`), so the 1.01 M synapses onto the DNs never reached the one DN that fires (DNg100 is
driven); they reached the 1,308 undriven DNs, which are nearly silent without a brain. the same synapses run the RATE model away because
there DNg100 integrates its inputs. the cut was wrong in the file and right in effect for the LIF; the v2 file is kept because it is the
decapitated fly's wiring and the rate model needs it. **"v1 had it at x23" corrects to: v1 has it at the same strength,** 19.2 Hz x29 at
1 ms with IN17A001 at 17.8 Hz per cell (not "under 5"). so the 20 Hz was always there; **the 18:40 read ("no ring at x1") was a 10 ms lobe
read** (autocorrelation at 30 / 70 / 140 ms, coxa lags) that cannot see a 20 Hz line, and tonight's 1 ms spectral read can. a new read, not a
new cut. and the twelve percent: with all eight cited cells silent the leg motor neurons fall 1.84 -> 1.67 Hz per cell (52 -> 42 active), so
the subnet carries about a tenth of the motor output at this dose and the tonic posture is not its.

## the campaign opens (22:38 PDT; `docs/CAMPAIGN.md`: the line moved on purpose, the action list, the ledger)

**why the flexors are silent, one layer up (the cord, v2, DNg100 100 Hz, seed 11; the tibia flexors' 24 largest presynaptic types logged at
1 ms):** the tibia flexor motor neurons (37 cells) receive 1,386 synapses per cell against the extensors' 5,674, and under the walking
command what they receive is **fourteen parts inhibition to one part excitation** (synapses x rate over the 24: I 100,650, E 7,058). the
inhibition is the 13A premotor cells: IN13A002 at 52 Hz per cell (875 synapses onto the flexors), IN13A005 at 29 (1,008), IN13A001 at 16
(831), with INXXX471 at 15 and IN19A015 at 4. the excitation that exists in the file does not fire: IN21A004 (3,442 synapses onto the
flexors, six cells) 0.0 Hz, IN03A004 (1,679) 0.1, IN20A.22A009 (1,468, eighteen cells) 0.0, IN03A031 (1,428) 0.0, IN20A.22A010, IN03A039,
IN17A016, IN21A020 all 0.0; the only excitors awake are IN19B012 at 4.7 Hz and DNg100's own 32 synapses. **so the silence is not the
flexors' threshold alone: the command wakes the cells that hold them down and none of the cells that would lift them.** the file has a
flexor-excitor layer and the walking neuron does not reach it, or reaches it through cells that our uniform physiology leaves under
threshold. the layer above the excitors is logged next.

**the layer above (22:38 PDT; the six flexor-excitor types' 30 largest inputs logged):** the excitors are held down the same way, eight to one
(I 364,285 vs E 43,033 in synapses x rate), by the same cells: IN13A002 (2,145 synapses onto the six, 52 Hz), IN12B003 (1,968, 38 Hz),
IN13A005 (1,976, 29 Hz), IN19A004 (993, 47 Hz), IN19A002 (2,004, 12 Hz), IN13A001, IN21A003. their own excitors are silent too (IN17A016,
2,864 synapses, 0.0 Hz; IN17A028 0.0) except IN19B003 (1,191, 21 Hz) and the sensory SNpp51 (1,026, 14 Hz). **the walking command, delivered
as one tonic DN at 100 Hz, is an extension command in this file:** it wakes the 13A / 12B / 19A premotor inhibitors and they fire tonically at
30-50 Hz, holding the flexor motor neurons and their excitors under threshold together. in the fly the 13A cells are phasic (Sapkal 2026;
the 13A-13B reciprocal inhibition already on record, 09-21: "the half-centre is in the table and four release mechanisms do not switch
it"). so the flexor problem is the switch problem seen from the flexors' side: nothing in our physiology lets 13B win a half-cycle from 13A.
this is where campaign items 2-4 aim (slower inhibition, per-type excitability, rebound/plateau on the 13A-13B pair), and the read is fixed:
IN13A002's rate and the flexor motor neurons' rate, beside the 20 Hz line.

**the layer above that (22:40 PDT; the four tonic inhibitors' 30 largest inputs logged):** the inhibitors are driven eleven to one (E 286,831
vs I 24,896). the largest input is **SNpp50, the leg-load sensory cells: 5,517 synapses onto the four, at 14.2 Hz, which is the cord's own
tonic load stand-in (`--leg-load-hz 15`)**; then DNg100 directly (780 synapses at 78 Hz); IN07B001 (1,886, 22 Hz); SNpp48 (2,281, 15 Hz,
the same stand-in); IN19A009; and IN17A001, the loop cell, exciting the inhibitors with 1,031 synapses at 17 Hz. the cells that would
inhibit the inhibitors are silent: IN13A006 (1,893 synapses, 0.1 Hz), AN06B002 (1,826, 0.3), IN13A015 (1,637, 0.2), IN13B019 (1,496, 0.0),
IN14A008, IN14A018, IN14B005 all 0. so, top to bottom: **a load signal that never lifts and a command that never pauses drive the 13A / 12B /
19A inhibitors tonically; they hold the flexor motor neurons and the flexor excitors down together; the 13B side, which would release
them, has nothing waking it.** in the cord alone the load is a constant by construction; on the body it is the loop we closed, and the foot
never lifts because the flexors never fire because the load never lifts. the load sweep (0 / 5 / 15 / 30 Hz) is beside this.

**the load sweep (22:41 PDT; `--leg-load-hz` 0 / 5 / 15 / 30, DNg100 100 Hz, seed 11):** IN13A002 0.0 / 14.2 / 52.0 / 86.3 Hz and IN13A005
4.0 / 10.5 / 29.0 / 53.4: **the 13A pair's tonic rate is the load stand-in's, almost entirely.** IN12B003 (40 / 40 / 38 / 37) and IN19A004
(40 / 44 / 47 / 47) do not move: theirs is the command's. with the load off the tibia flexors reach 0.42 Hz per cell (from 0.00) and the
flexor excitor IN03A004 4.4 Hz (from 0.1); the 13B side stays silent at every load (IN13B019 / IN13A006 / IN13A015 all under 0.2 Hz). the
extensors 4.3 / 4.5 / 8.0 / 16.7. so the standing load is half of what holds the flexors, the command is the other half, and removing the
load alone does not release them (the treadmill's finding of 09-21, seen from inside). the 20 Hz line is at every load (17.8 / 18.5 / 19.7 /
23.0 Hz, x38-48), rising with it.

**campaign item 1, the weak edges (agent A; `docs/physiology/weak_edges.md`):** the five-synapse floor was ours (`ref/flybrain/scripts/
build_creature.py --min-weight 5`), not the release's: `connectome-weights-male-cns-v1.0-minconf-0.5.feather` carries every edge down to one
synapse (151.9 M edges, 311.8 M synapses; the 0.5 is a detection confidence). rebuilt without it as `brain_whole_all.npz` (25.1 M edges,
122.2 M synapses between typed cells) and `brain_cord_all.npz` (3.78 M edges against 1.07 M; 23.7 M synapses against 18.9 M: 3.5x the
edges, 25 % more synapses, at each cell's existing E/I ratio; the tibia flexors 1,386 -> 1,578 per cell, the extensors 5,674 -> 6,078).
**the cord does not move on it:** leg MNs (373) 1.80 / 1.72 Hz per cell on seeds 11 / 12 (v2: 1.84 / 1.78), 52 / 53 active, flexors 0.00,
IN17A001 16.9 Hz with its line at 19.8 / 20.0 Hz (x37 / x42). inside the seed spread. the floor is a removed compromise, not a fix; the
files stay beside the originals (untracked, like them) for anything that wants the full graph. a second filter remains: only traced, typed
cells (211,577 -> 162,517), and the synapses onto untyped fragments are not counted.

**the 13B side (22:42 PDT; the seven silent releasers' 30 largest inputs logged):** the cells that would inhibit the inhibitors are themselves
inhibited 3.5 to 1 (I 215,605 vs E 61,096), and **the largest input onto them is IN13A002, 2,279 synapses at 52 Hz: the winner inhibits its
own releasers.** with it IN13A003 (1,040, 28 Hz), IN26X001 (511, 47 Hz), IN13B001 (529, 33 Hz), IN19A005. their excitors are the same
sensory stand-in (SNpp51, 2,084 synapses at 14 Hz), DNg100 (168), IN21A018 (6 Hz), and a row of silent ones (IN12A001 1,207 synapses,
IN20A.22A007, IN01A012 / 025 / 042, IN03A071, IN17A019 / 017, all 0.0). so the half-centre is on record from inside: 13A002 is woken by the
load and the command, inhibits the flexors, the flexor excitors and the 13B cells that would inhibit it, and holds, because nothing in
our physiology tires it and nothing on the other side is woken by anything but the same two tonic signals. the fly switches this at
7-15 Hz. the targeted test is on the winning cell: depression on 13A002's output (the engine's depression fixed tonight), adaptation on
13A002, rebound on the 13B side, each alone, at physiological values, with IN13A002 / IN13B019 / the tibia flexors / the loop line read.

**fatigue, global, read on the half-centre (22:47 PDT; `--std all` u 0.08 / u 0.3 tau 300, `--adapt` 1:200 / 3:500, `--rebound` 1:100, the load
off, the load off + adapt 3:500; seed 11):** IN13A002 52 -> 34 / 21 / 30 / 9 / 52 / 0 / 0 Hz across the arms, and **IN13B019 never rises above
0.2 Hz in any of them**, not even with IN13A002 at 0.0 (the load off). the tibia flexors' best is 0.42 (the load off, no fatigue); every
global mechanism dims the whole cord (leg MNs 9.6 -> 2.3 / 1.3 / 6.7 / 2.5 / 10.7 / 7.6 / 1.9) and the 13B side with it. so the 13B side is not
only held down by 13A002: **with 13A002 silent it still has nothing waking it.** its excitors in the file (IN12A001 1,207 synapses, IN20A.22A007,
IN01A012 / 025 / 042, IN03A071, IN17A019 / 017) are at 0.0 under the command, and its only live excitation is the same sensory stand-in
(SNpp51) that wakes its opponent. tiring the winner is necessary and not sufficient; the loser needs a source. the layer above the 13B
side's excitors is next, and the sensory classes onto both sides (what the floor stand-in drives, and what it does not).

**the sense we never gave him (22:48 PDT):** the file's leg sensory classes: SNpp 928 cells (mechanosensory_proprioceptive: chordotonal and
campaniform), **SNta 2,573 cells (mechanosensory_tactile: the leg's bristles)**, SNxx 903 unknown, SNch 124 chemosensory. the floor stand-in
(`floor_leg_proprio`, 580 cells) and the body loop drive proprioceptors only. **the 13B side's silent excitors (IN12A001, IN20A.22A007,
IN01A012 / 025 / 042, IN17A019 / 017) take 27 % of their excitatory synapses from tactile afferents** (SNta29 276, SNta20 221, SNta37 179,
SNta28 109, SNta38 101, SNta26 61), against 16 % sensory onto the 13A winners (SNpp50 / 39 / 45 / 52, the proprioceptors we DO drive) and 4 %
onto the flexor excitors. so the two sides of the half-centre listen to two different senses, we drive the winner's and not the loser's,
and the loser's has a plain biological story: a standing fly's tarsi are on the ground and its bristles fire on contact (Tuthill &
Wilson 2016: leg bristle afferents; a touch to the leg evokes flexion). the six tactile types are driven at 15 and 40 Hz beside the floor,
with the load off, and at rest; IN13B019 and the tibia flexors are the read. a labelled sensory stand-in, ledger row 4 if it does anything.

**the bristles driven (22:51 PDT; the six tactile types onto the 13B side's excitors at 15 / 40 Hz beside the floor, at 40 with the load off, at
40 at rest):** IN13B019 0.1 / 0.6 / 2.5 / 0.1 Hz (control 0.0; the load off alone 0.1), the tibia flexors 0.06 / 0.02 / 0.61 / 0.00 (the load off
alone 0.42); IN13A002 untouched by it (54 / 58 / 0 / 57). the tactile drive wakes the winner's side as much as the loser's (the extensors 11.1
at 15 Hz, the cord 1.1 -> 2.2-3.2 Hz per cell). **a sense we had left at zero, now on, and not the switch either:** the releaser reaches 2.5 Hz
only with the load off, and the flexors 0.6. ledger row 4 (tactile stand-in) is a diagnostic, not a default. what the four layers say
together: the loser's side of the half-centre has no live excitation in this file under a tonic command and tonic senses; its excitors
(IN12A001, IN20A.22A007, IN01A012) stay silent under tactile drive too (read below). the switch needs either a phasic input we do not have
or an intrinsic property that lets the loser escape (rebound on the 13B side specifically, plateau on the flexor excitors), which is
campaign item 4 with a named target now: IN13B019 / IN13A006 / AN06B002 and the flexor excitors IN21A004 / IN03A004.

**parameter provenance (agent D; `docs/physiology/parameter_provenance.md`; nate: "how did Shiu et al produce their numbers?"):** none of
Shiu 2024's biophysical constants was measured for the cells simulated; all inherited, most through Kakaria & de Bivort 2017 ("generic
neuronal properties consistent with various Drosophila measurements"): rest -52 and threshold -45 mV from larval central neurons and
adult clock neurons (Rohrbough & Broadie 2002; Sheeba 2008); membrane R and C from compartmental fits to adult antennal-lobe DM1
projection neurons (Gouwens & Wilson 2009), the 20 ms tau being R x C, never written as 20 by either paper; the 1.8 ms delay measured at a
larval glutamatergic NMJ at 18 C (Paul 2015); the 5 ms synaptic decay from a neuromorphic larval mushroom-body model with no measurement
behind it (Jurgensen 2021; that model used 10 ms for inhibition); the 2.2 ms refractory's trail breaks (Lazar 2021 cites Kakaria, which has
only a 2 ms template); reset-to-rest is Shiu's own. **the weight, 0.275 mV, is their one declared free parameter, set by simulation so that
100 Hz of sugar input gives ~80 % of the model's own maximum MN9 rate** (an internal target, not a measured rate); varied +-30 %, the I/E
ratio +-50 %, glutamate flipped, a shuffled connectome. their validation is not fitting: 164 held-out predictions, 91 % correct, a 106-type
optogenetic screen run after the predictions, a grooming circuit that played no part in setting any value. Pugliese 2026: tau 20 ms and
the 200 Hz cap "reasonable ranges"; gain and threshold "have no direct biological analogs", chosen by grid search on a test network; size
scaling by argument (input resistance falls with area) and necessary; the DNg100 drive the one value tuned toward the result. the field:
tuned-until-it-worked (Kakaria, Pisokas), fitted to measured activity (Churgin, Zarin), fitted to a task then checked against 26 recorded
studies (Lappalainen 2024), and Huang 2018, a whole-brain LIF that ran away as ours does and needed short-term depression. **two facts for
our files:** Shiu's connectivity has no synapse floor (82 % of its edges under 5); and with Shiu's kinetics one synapse gives a 0.157 mV
bump, not 0.275, so ~45 coincident synapses reach threshold, not the 26 in `docs/physiology/vision_motor_courtship.md` (to correct there).

**the knobs, sourced (agent B; `docs/physiology/knobs.md`, 22:52 PDT):** what the literature actually licenses, and it corrects one of my bets.
- **inhibition is not slower than excitation in the fly.** nicotinic ACh decays in 4.5-6.7 ms in adult Kenyon cells in the intact brain
  (1.4-2.1 in culture); GABA-A (Rdl) 3.7-6 ms, culture only. the only slow inhibitory number is a larval GluCl current onto motor neurons,
  ~300 ms after a train, an upper bound from one trace; GABA-B exists in the adult antennal lobe with no numbers. so **campaign item 2's
  bet ("GABA and glutamate are slower, the 20 Hz drops to 7-15") rests on glutamate alone,** and glutamate is a fifth of the cord's inhibition
  at most. the term stays worth having (labelled), the prediction is withdrawn before it is tested. both inhibitory channels reverse near
  rest in larval motor neurons: real inhibition is shunting, the engine's is unbounded hyperpolarisation. and the engine's decay is a
  strength: charge = weight x tau, so a kinetics term must say whether it holds peak or charge.
- **the tibia flexors have a measured resting state and ours is wrong.** Azevedo 2020: slow / intermediate / fast tibia flexor motor
  neurons rest at -48 / -60 / -68 mV with input resistances 700 / 300 / 150 MOhm, and **the slow cells fire ~30 Hz at rest,** partly from
  cholinergic input (blocking nicotinic receptors lowers it). ours: one rest (-52), one threshold (-45), one resistance, and the flexors
  at 0.00 Hz. thresholds and membrane time constants were never measured for any leg motor neuron; the extensors have never been
  recorded. **this is campaign item 3 with a measured target:** per-type rest and input resistance for the flexor pool from Azevedo, the
  slow cells' 30 Hz at rest as the physiological check, never the step.
- per-synapse size: measured adult central connections give 0.1-0.27 mV at the soma; response size tracks synapses per unit membrane
  area (Liu 2022), which is Pugliese's real source for size scaling.
- plateaus and rebound: no fly leg cell has either measured; cockroach calcium plateaus, locust plateaus only under octopamine (50-75 ms
  bursts at 4-16 Hz), a <= 5 mV tonic depolarisation in walking stick-insect motor neurons. borrowed if used.
- **octopamine has cells in the file:** 50 octopaminergic cells in the cord, all efferent; the leg ones EN00B008, one per segment, and
  **DNp68 and DNg100 synapse onto them** (the walking command reaches the modulators); they make no chemical synapses onto leg motor or
  premotor cells, so a state computed from their firing comes from real cells; what it does is stick-insect sign only (suppresses the
  resistance reflex, supports the active state), no fly magnitude.
- gap junctions: the only adult VNC coupling measured is between flight motor neurons (Hurkey 2023, coefficient 0.01-0.02, ShakB), weak
  and desynchronising. senses: no adult leg proprioceptor has a recorded spike rate (all imaging); the front leg's femoral chordotonal
  organ keeps 16 of ~152 cells in the file, the middle and hind legs near complete.

**campaign item 3, the flexors at Azevedo's rest (23:00 PDT; the tibia flexor motor neurons' threshold set through the size path from a CSV
of explicit factors, every other cell at 1.0; seed 11, 30 s):** Azevedo 2020 rests the slow / intermediate / fast tibia flexors at -48 / -60 /
-68 mV; the model rests every cell at -52 with threshold -45, so the slow cells' 7 mV becomes 3 mV (factor 3/7). **every tibia flexor at 3
mV:** 0.00 Hz at rest, 0.01 under the command. with their synapses scaled by their input resistance too (700 vs ~300 MOhm, factor 2.3,
`--size-gain 1`): 0.14. the load off as well: 2.69 (the load off alone gave 0.42). a graded labelling by size rank (smallest third at 3 mV,
largest at 23; the normalisation put the slow third at 1.4 mV, more extreme than intended): 0.16 at rest, 0.32 under the command.
**a cell that will not cross a 1.4 mV threshold is being held far below rest.** Azevedo's slow flexors fire ~30 Hz at rest; ours cannot be
brought to fire at any threshold, because the inhibition onto them (fourteen to one) hyperpolarises without bound in this engine, where
in the cell GABA-A and GluCl reverse near rest (`knobs.md`: shunting, not driving). so item 3's measured target cannot be reached by the
threshold, and the gap it exposes is the form of inhibition: **campaign item 2b, reversal potentials per transmitter class (inhibition
as a conductance to a reversal near rest), an engine term, off by default, oracle.** the membrane of the flexors is to be logged directly
(`--log-v`) once the engine's current edit lands. ledger row 5.

**campaign item 2, the engine side landed (23:01 PDT; commit 6d4c5b4, agent C; `--syn-tau ACH:GABA:GLU` in `world/cord.py` and
`experiments/body_loop.py`, off by default; oracle PASS, v1 + v2, eight configs; `experiments/syn_tau_test.py`: the six-cell PSPs match the
closed form to 1e-6 mV, IPSP / EPSP area 4.00 at 5:20:20):** one conductance row per presynaptic transmitter class (ACh 13,491 cord cells,
GABA 5,915, glutamate 2,648, other 1,020 = the six histamine cells and the edgeless modulators). **a slower tau is a stronger synapse in this
term** (charge = weight x tau; the IPSP peak -1.01 mV against the EPSP's +0.43 at 5:20), so a kinetics arm is also a strength arm and is
read as both. the help's 5:20:20 is an illustration, not a sourced value: the sourced ranges (`knobs.md`) are ACh 4.5-6.7 ms, GABA-A
3.7-6 ms, glutamate (GluCl) one larval trace at ~300 ms as an upper bound. the arms below use those.

**the time constants swept (23:03 PDT; `--syn-tau` ACh:GABA:Glu = 5:5:5 (bit for bit the control), 5:5:20, 5:5:100, 5:5:300, 2:4:5, 7:6:300;
seed 11, DNg100 100 Hz):** slowing glutamate (a fifth of the cord's inhibition, and a stronger synapse at every longer tau) dims the cord
(leg MNs 9.6 -> 5.4 / 3.3 / 2.3 Hz per cell; the extensors 8.0 -> 2.6 / 0.5 / 1.1), leaves IN13A002 nearly where it was (52 -> 51 / 48 / 43: its
drive is cholinergic and sensory), **wakes no flexor (0.00 in every arm) and no releaser (IN13B019 <= 0.5)**, and pulls the 20 Hz line down
and thin: 19.7 x45 -> 16.3 x45 / 16.0 x16 / 13.6 x10, and 7.8 Hz x10 at 7:6:300. faster synapses all round (2:4:5) halve the cord (0.52 Hz per
cell) and take the line to 23 Hz x21. so the sourced kinetics move the subnet's frequency in the direction of Pugliese's, at the cost of the
rhythm's strength and of the cord's activity, and touch the half-centre not at all. item 2 is a labelled knob, not the switch; item 2b
(the form of inhibition) is the one aimed at the flexors, and its engine term is being built.

**the senses mapped (agent F; `scripts/build_leg_senses.py` -> `world/leg_senses.npz` / `.csv`, `docs/physiology/leg_senses_map.md`; 23:14 PDT):**
3,567 of the cord file's 6,146 sensory cells belong to a leg, 3,566 placed by the release's own annotation (entry nerve ProLN / MesoLN /
MetaLN and root side; the wiring agrees for 97 % of tactile and 88 % of proprioceptive cells). per leg (lf / lm / lh / rf / rm / rh): tactile
169 / 372 / 388 / 156 / 426 / 413 (1,924 on the legs; the rest of the 2,573 SNta are wing, notum, haltere), proprioceptors 48 / 129 / 132 / 31 /
133 / 139, of which claw (SNpp50 / 51), hook (SNpp39 / 41), club, hair plates (SNpp45 / 52), campaniform (2-3 per leg named), unclassified
chordotonal and untyped. **the front legs are thin in the file** (48 and 31 proprioceptors, one and zero extension-tuned claw cells).
**and the standing-load stand-in is the wrong cells:** the floor's 580 are club 207 (the femoral chordotonal organ's vibration cells, silent
standing still), untyped 88, claw_50 62, unclassified chordotonal 41, hair plates 78, hook 61 (movement cells, silent at rest), claw_51 31,
**campaniform 12.** the body loop's "load" row (426 cells) is 49 % club, 21 % untyped, 18 % hair plate, 3 % campaniform (the review's F7 with
numbers). so IN13A002's 52 Hz is the floor driving the vibration- and movement-sensing cells of a motionless leg at 15 Hz. ledger row 6. the
floor is trimmed from the command line (`--drive TYPE:0` overrides it on named types) to the cells that fire standing still: campaniform,
hair plates, the claw; the club, hook and unclassified chordotonal cells at 0. arms below.

**the floor trimmed (23:14 PDT; `--drive TYPE:0` over the floor's cells; DNg100 100 Hz unless "rest"; seed 11):** club + hook + unclassified
chordotonal at 0 (the cells silent in a motionless leg): IN13A002 52 -> 39 Hz, flexors 0.00. those and the extension-tuned claw (SNpp50) at
0: **IN13A002 0.0 Hz**, IN13A006 1.4, the flexor excitor IN03A004 3.3, tibia flexors 0.20. campaniform + hair plates only (both claw classes
off too): IN13A002 0.0, flexors 0.18. campaniform + untyped only: IN13A002 0.0, IN13B019 0.2, IN03A004 4.9, **flexors 0.50**, extensors 4.3.
at rest on campaniform + hair plates: the cord at 0.26 Hz per cell, the leg motor neurons 0.15 (eleven active), IN13A002 0. **so the
winner's 52 Hz was the stand-in's choice of cells:** the floor at 15 Hz on 207 club, 61 hook and 62 extension-claw cells is what drove
IN13A002, and with the floor on the cells that fire standing still it is silent. **which corrects tonight's "the winner locks":** under
an honest standing floor the half-centre is not locked, it is quiet on both sides, and the flexors sit at 0.2-0.5 Hz because nothing
excites them enough, not because IN13A002 holds them. the flexor excitors wake a little (IN03A004 3-5 Hz), the releasers barely
(IN13B019 0.2). the switch question stands, reframed: with the winner quiet, what lifts the flexor side to Azevedo's 30 Hz at rest; item
2b is still the mechanism aimed at it (the inhibition they do get, from 13A003 at 17 Hz and 12B003 / 19A004 at 40, still hyperpolarises
without bound). the floor's default is changed in the ledger, not yet in the code (`world/cord.py` is under an engine agent's edit).

**item 5, octopamine, designed and parked (agent E; `docs/physiology/octopamine_state.md`, `experiments/oa_census.py`):** 50 octopaminergic
cells in the cord, all unpaired midline efferents, three on the leg nerves (EN00B008, one per segment); the engine gives them sign 0 and
their 208 outputs go to other octopamine cells. **DNg100 sends them 62 synapses (0.3 % of its output; mostly T3 / T2), DNp68 716,** and
under DNg100 at 100 Hz EN00B008 sits at +1.45 mV and fires 0 Hz (0.33 at 400 Hz; 59 Hz with DNp68 driven too). so a state computed from
the real cells is zero in the headless walking arm as we run it, and item 5 is a DNp68 question (arousal / aggression input in the
female brain). the fly biology: no adult leg measurement; larval RP2 motor neurons show no effect at 1-10 uM (Schutzler 2019); flies
without octopamine walk; clearance half-life 1.4 s in the larval cord. borrowed effects cut both ways (locust: extension-tuned sensors
up strengthens our 13A side). the design (a low-passed EN00B008 rate, saturating, applied as gains on named targets, no 13A target, three
controls including the cells silenced) is on file; not built. two count errors in `knobs.md` section 4a are flagged there (T1 / T3 swapped).

**which sense feeds which side (23:15 PDT; the excitatory synapses onto each layer of the flexor chain by sensory subtype, from
`world/leg_senses.csv`):** the 13A winners (IN13A002 / 005 / 003, IN12B003, IN19A004) take 15 % of their excitation from the senses and of
that **claw_50 (SNpp50, the extension-tuned class as labelled) 5,517**, tactile 3,353, unclassified chordotonal 3,196, hook 439. the 13B
releasers, 14 %: **tactile 2,328, claw_51 (flexion-tuned as labelled) 2,084**, hair plates 400. the 13B side's excitors, 27 %: tactile 11,661,
claw_51 397. the flexor excitors, 4 %: claw_51 1,026, tactile 913, hair plate 247. the tibia flexor motor neurons themselves, 2 %: claw_51
293, hook 156, campaniform 106; the extensors, 2 %: claw_50 408. **the two sides of the half-centre listen to the two claw classes and
the bristles: extension-tuned claw to the extension side, flexion-tuned claw and touch to the flexion side.** the file's resistance-reflex
wiring, readable. two consequences: (1) the floor at 15 Hz on BOTH claw classes was feeding both sides and the extension side more (62 vs
31 cells); a standing fly's tibia is flexed, so the honest standing claw signal is claw_51, not claw_50, under the labels as printed, and
the reverse if the labels are swapped (ledger row 1 is now the question of which side the standing leg feeds); (2) sensory is 2-5 % of the
excitation onto the flexor motor neurons and their excitors: **95 % is central and silent.** the flexor side is not waiting on a sense; it
is waiting on interneurons that nothing wakes under a tonic command. the claw arms are beside this.

**the standing leg's own senses (23:18 PDT; the floor on campaniform + hair plates, the club / hook cells at 0, and the claw class of a FLEXED
tibia (SNpp51 as labelled) at 15 or 40 Hz with the extension class at 0; seed 11):** claw_51 at 15 under the command: IN13A002 0, IN13A006 1.4,
flexors 0.20. at 40: IN13A006 9.1, IN03A004 4.8, flexors 0.33. the other class instead (claw_50 at 15, claw_51 at 0): IN13A002 39 Hz, flexors
0.00, IN13A006 0.1: **the two claw classes pick the side, as the wiring said.** claw_51 at 40 plus the six tactile types at 20 Hz (a foot on
the ground): **IN13A006 21.4 Hz, IN03A004 12.7, the tibia flexors 2.30 Hz per cell against the extensors' 2.8: the first arm in which the
flexors fire from a sensory story alone, and nearly match the extensors.** the same at rest (no command): IN13A006 15.8, IN21A004 2.5,
flexors 1.01, extensors 0.0. seeds and the swapped labelling are running. what this is: the standing leg's afferents as the file has them
(flexed tibia -> claw_51; feet on the ground -> bristles) driven at rates nobody has recorded in an adult leg (ledger row 7), instead of a
floor that drove the vibration cells. what it is not: Azevedo's 30 Hz, or a step. and the reading of "which claw class is extension-tuned"
(ledger row 1) now has a physiological handle: under the labels as printed, the flexed standing leg wakes the flexion side.

**replicated (23:20 PDT):** the flexion claw at 40 + the six tactile types at 20 under the command, seeds 11 / 12 / 13: tibia flexors 2.30 /
2.26 / 2.37 Hz per cell, extensors 2.8 / 2.8 / 2.8, IN13A006 21.4 / 21.1 / 20.8, IN03A004 12.7 / 12.8 / 13.0, IN13A002 0 on all three. **three
of three.** the same senses at rest (no command): flexors 4.59 Hz, extensors 0.0, IN13A006 25.1, IN03A004 17.8, IN21A004 2.1: **the flexion
side is livelier without the walking neuron than with it,** because DNg100 drives IN12B003 / IN19A004 (the command's own inhibitors of the
flexion side, unchanged by the floor). the claw classes swapped (claw_50 at 40 + tactile): IN13A002 85.5 Hz, extensors 13.8, flexors 0.00,
IN13A006 0.0. the labelling picks the side, wholesale. the antagonist column reads -0.27 on this arm (0.00 to -0.19 on every earlier arm);
the flexor-extensor lag structure is read above. Azevedo's 30 Hz at rest for the slow flexors is still six times away, and the 95 % of the
flexors' central excitation is still silent; what has changed is that the flexion side of the file is now awake enough to be studied.
  (the lag read: flexor-extensor cross-correlation min -0.15 at +10 ms, max +0.08 at -60, no lobe in the flexors' autocorrelation (-0.04 / 0.00 / -0.04 at 30 / 70 / 140 ms); the flexors carry the subnet's line at 19.9 Hz x11. no alternation: the -0.27 is the flexors and extensors sharing the line out of phase at one lag, not a rhythm of their own.)

**campaign item 2b landed (23:25 PDT; commit 44a16b8, agent; `--syn-rev ACH:GABA:GLU` in mV re rest and `--log-v TYPES` in `world/cord.py` and
`experiments/body_loop.py`, off by default; oracle PASS, v1 + v2, eight configs; `experiments/syn_rev_test.py`: far reversals reproduce the
current-based PSPs to 5e-7 mV, the IPSP at rest is 5/70 of today's and doubles at +5 mV, twenty thousand GABA synapses stop at E_GABA where
the current-based cell sits on the engine's -7 mV floor).** as built the scale holds the ACh EPSP (kappa = sign / E_ach for every class), so an
inhibitory synapse at rest is fourteen times weaker than today and the cord runs away: 1.10 -> 42.0 Hz per cell, the flexors 93 Hz, the
extensors 209, IN17A001 246. that is inhibition lost everywhere, not the flexors released; a `--syn-rev-hold each` option (kappa = sign /
|E_c| per class: every synapse keeps today's PSP at rest, inhibition still shunting) is being added with its own oracle before any arm of
record.

**withdrawn in place (23:25 PDT): "held far below rest."** the membrane logged (`--log-v`, 20 s, seed 11, after the warm-up): under the
control the tibia flexors sit at **-1.53 mV re rest with a standard deviation over time of 0.24 mV**, the accessory flexors at -1.11, the
extensors at -1.09 (sd 1.04, firing 8 Hz), IN13A002 at +2.07 (52 Hz), IN13A006 at -5.09, IN03A004 at -6.56, IN21A004 at -4.08. the engine
cannot sit a cell below -7. so the flexors are not parked deep; they are held a little under rest **and almost nothing moves them** (a
quarter-millivolt of fluctuation against a 7 mV threshold): the item 3 arms failed at 3 mV and at 1.4 mV because the input is too small
and too steady, not because the cell is too deep. the 13B side and the flexor excitors ARE deep (-4 to -6.6 mV, on the floor's side of
things). with the standing senses (flexion claw 40 + bristles 20): the flexors at -0.05 mV (sd 0.44, 2.3 Hz), the extensors -3.38, IN13A002
-1.14 (silent), IN13A006 +1.23 (21.6 Hz), IN13B019 +1.91, IN21A004 -0.25, IN03A004 -2.75; at rest with the same senses the flexors at +0.57
(4.5 Hz), IN21A004 +1.69, IN03A004 +2.21. the flexion side moved from six millivolts under to around rest by the senses alone, and what
it lacks now is drive, which shunting inhibition cannot supply. so 2b matters for the cells the winner holds down (the 13B side at -5, the
excitors at -6.5, where a shunt would leave them near rest instead), and item 3's threshold matters once they are near rest; neither is
the drive. the drive is the 95 % of central excitation onto the flexion side that a tonic command does not wake.

**the body's senses, read before editing (23:26 PDT; `experiments/body_loop.py` lines 91-107, 206-217):** on the body the whole 580-cell floor
runs at `--leg-load-hz` (15 Hz) as a tonic set (line 93) AND each leg's "load" row (everything in `legs.npz` that is not claw or hook: club,
hair plates, untyped, campaniform) is driven at 15 x load on top. so the body loop has been driving a standing leg's vibration cells at
15 Hz throughout, the same fault as the cord's floor (ledger 6). the claw rows (SNpp50 / 51) are driven by the knee angle FROM THE MODEL'S
NEUTRAL POSE (78 deg front, 103 middle, 101 hind, as the model measures the femur-tibia joint) at `--claw-hz` x |angle| / 60 deg, which
zeroes the claw at the standing posture. Mamiya's claw cells are tonic in angle and **silent near 90 deg**, not near the model's neutral:
at the standing pose the front knees sit 12 deg to the flexion side of the claw's null and the middle and hind 11-13 deg to the extension
side, so a standing fly's claw is not silent, it is a small flexion signal in front and a small extension signal behind (a fifth of the
60-deg range), and which class carries which is ledger row 1. the hooks are velocity cells (right as built, silent standing), the
bristles are not driven at all, the hair plates are inside the load row. **the edit, once the engine agent's hands are off the file:**
`--senses v2`: the floor and the load row on campaniform + untyped only (`world/leg_senses.npz`), club / hook / unclassified at 0, the
claw from |angle - 90 deg| by class, hair plates from coxa angle near its limits (a stand-in, rate unsourced), the leg's tactile cells at
a rate while its foot's contact force is above the pads' threshold (onset burst, then tonic; rates unsourced, ledger 7). every row
labelled; the default stays as it was so every run of record reproduces.

## the three sourced changes together (23:45 PDT; the cord, seed 11, 30 s; the standing senses = the floor on campaniform + hair plates, club /
hook / unclassified chordotonal at 0, the flexion claw class (SNpp51 as labelled) at 40 Hz, the six tactile types at 20; Azevedo = every tibia
flexor's threshold at 3 mV (slow rest) with its synapses x2.3 (700 vs ~300 MOhm); rev = reversal potentials 70:-5:-5 held each; membranes
logged)

| arm | Ti flexors Hz (membrane) | Ti extensors | IN13A002 | IN13A006 | IN03A004 |
|---|---|---|---|---|---|
| control (floor as built) | 0.00 (-1.53 mV) | 8.0 | 52 | 0.1 | 0.1 |
| rev alone | 0.00 (-0.61) | 3.7 | 49 | 0.2 | 0.0 |
| rev + Azevedo | 0.33 (-0.80) | 3.7 | 49 | 0.2 | 0.0 |
| senses alone | 2.30 (-0.05) | 2.8 | 0 | 21.4 | 12.7 |
| senses + rev | 0.51 (+0.17) | 1.8 | 0 | 10.3 | 7.2 |
| senses + rev + Azevedo | 3.25 (+0.02) | 1.6 | 0 | 10.1 | 7.3 |
| senses + rev + Azevedo + gain | 8.66 (-0.03) | 1.6 | 0 | 10.3 | 6.9 |
| **senses + Azevedo + gain (no rev)** | **14.22** (-0.69) | 2.7 | 0 | 21.4 | 12.6 |
| senses + rev + Azevedo + gain, at rest | 11.85 (+0.20) | 0.0 | 0 | 15.9 | 9.2 |

- **the order matters and it is the senses first.** with the floor as built nothing moves the flexors (rev + Azevedo: 0.33 Hz); with the
  standing leg's own senses they reach 2.3, and Azevedo's rest and resistance on top take them to 14.2 Hz per cell under the command,
  five times the extensors, and 11.9 at rest with shunting on. **Azevedo's slow flexors at ~30 Hz at rest is within a factor of two to
  three, from three changes each with a source, none of them aimed at a step.**
- **shunting inhibition halves the flexors here** (14.2 -> 8.7) rather than freeing them: with the senses on, the flexion side's inhibition
  is already small and the shunt also weakens the excitation's reach (a conductance to +70 from near rest is today's EPSP, and the
  reversal term's inhibition grows as the cell depolarises). it does what it should for the cells the winner held deep (IN13A006 from
  -5.1 to -2.1 mV under the control; the excitors from -6.6 / -4.1 to -3.1), which is the argument for keeping it; it is not the flexors' lever.
- **caveats, all of them:** every tibia flexor is labelled slow here (the pool is a third slow by size rank; the graded labelling is running);
  the claw class is as printed and the whole result flips with the labels (ledger 1); the sensory rates are chosen (ledger 7); the
  accessory flexors stay at 0.00 in every arm; the extensors fall to 1.6-2.7 Hz, which is a standing fly's extensors going quiet, not a
  gait; no alternation anywhere (antagonist -0.3 is the shared 20 Hz line, lag read earlier). seeds 12 / 13 and the graded labelling
  are beside this. the same senses go onto the body next (`--senses v2`).

**withdrawn in place (23:46 PDT): "within a factor of two to three of Azevedo's 30."** the 14.2 Hz (13.8 / 14.0 on seeds 12 / 13) is the LARGEST third
of the tibia flexor pool at 38.7 Hz per cell with the small third at 0.0 and the middle at 1.9. Azevedo's slow cells are the small ones, and
the large ones are the fast cells that rest at -68 mV; the arm gave every flexor the slow rest and the fast cells took it. **the graded
labelling (small third at 3 mV and x2.3, middle at 15, large at 23): 0.00 Hz under the command, 0.01 at rest, every third at 0.** so the
sourced arm does not reach the target, and the all-slow arm reached the wrong cells. what stands from the table above: the senses wake
the flexion side (that was measured on the pooled rate and holds: 2.3 Hz is the large cells too, to be re-read by third), Azevedo's
rest and resistance on the right cells do nothing, and the reason is in the wiring: **the small tibia flexors carry 13 to 111 input
synapses each in this file** (the pool's inputs by cell, ascending: 13, 35, 47, 51, 69, 75, 93, 111, 151, ... 8,167), against 1,569-8,167 for
the large third. a cell with fifty synapses cannot be brought to 30 Hz by its inputs at any threshold. Azevedo's slow flexors fire ~30 Hz
at rest partly on cholinergic input and partly on their own (blocking nicotinic receptors lowers, does not abolish, the rate): so the
gap is either the tracing (small cells' inputs missing: item 7 with a reason) or the cell's own excitability (a depolarised rest with
its own noise: item 3 done properly, the membrane noise scaled with input resistance the way the synapses were, which the engine cannot
do per cell yet). both are on the table; the noise term is the cheaper and the more honest first. the rates by size third are added to
the read from here on.

**the flexors by size third, every arm re-read (23:47 PDT; small / middle / large third of the 37 tibia flexors by input synapses):** the senses
alone under the command 0.00 / 0.00 / 6.5 Hz (pool 2.3); at rest 0.00 / 0.01 / 13.1 (pool 4.6); senses + rev + Azevedo-all-slow at rest 0.01 /
0.54 / 33.2 (pool 11.9); Pugliese's true volumes at 0.275 (the pinned arm, withdrawn) 0.27 / 18.8 / 61.1. **the small third has never fired in
any arm of the night.** every flexion result so far is the large cells. the standing senses wake the big flexors, which in Azevedo are the
fast ones and should be silent at rest; the small ones, which should carry the tone, have 13-111 input synapses and nothing to fire on.
the engine gets a per-cell membrane-noise scale (`world/fastlif.py`, off unless set, oracle running): the same current noise on a 700
MOhm cell is a larger voltage noise than on a 300 MOhm one, so the noise follows the synaptic scale; with the small cells' rest 3 mV
under threshold that is the cell's own excitability, sourced the same way the synapses were, and it is the honest test of whether
Azevedo's tone can come from the cell rather than from wiring the file does not have.

**corrected in place (23:53 PDT): the claw's side at the standing pose.** the model's knee angle is 0 with the leg straight and grows with
flexion, so the femur-tibia angle is 180 minus it (checked on the geometry by the agent: model 0 -> 179.6 deg, 30 -> 150.4, 90 -> 90.4). at the
neutral pose the femur-tibia angle is 102 / 77 / 79 deg (front / middle / hind): **the front legs stand 12 deg on the EXTENSION side of
Mamiya's 90-deg null and the middle and hind 13 / 11 deg on the flexion side**, the reverse of the 23:26 entry. the magnitude stands; the
class flips per leg. the code (`--senses v2`) uses the geometry.

**the senses on the body, the option landed (23:53 PDT; commit cefd3b2, agent; `--senses v1|v2` in `experiments/body_loop.py`, `--floor
all|standing` in `world/cord.py`, `src/fly_afterlife/leg_senses.py`; the defaults reproduce the runs of record bit for bit, body (thorax,
quaternion, forces, knees, joints, frames, counts: max difference 0) and cord):** v2 puts the floor and each leg's load row on the 111
campaniform + untyped cells (was 580), holds club 208 / hook 61 / unclassified 41 at 0, drives the claw from |femur-tibia - 90 deg| by
class, the hair plates (97) from coxa pitch toward its +-45 deg limit at `--hp-hz` 30 (unsourced), and a seeded quarter of each leg's
tactile cells (42-106 per leg) at `--tactile-hz` 20 with a 30 ms onset burst while the foot's contact force is above the pads' threshold
(unsourced). the 8 s smoke (50flex, no reversal): 63 % of his weight on the floor against v1's 1 %, flexors 0.08 / 0.18 (Ti), extensors 6.0:
**the honest senses take away the standing** the 580-cell floor was giving him (its 15 Hz on the vibration cells was tone). the 20 s
arms on both labellings follow. ledger rows 3 and 6 are answered by this option; the rates in it are row 7's.

**the slow flexors from the cell (23:56 PDT; the graded labelling (small third slow: rest 3 mV under threshold, synapses x2.3), the standing
senses, and the engine's new per-cell noise scale following the synaptic scale; seed 11, 30 s; flexors read by size third small / middle /
large):**

| arm | small | middle | large | extensors | IN13A006 |
|---|---|---|---|---|---|
| senses + graded thresholds + gain, at rest (no noise scale) | 0.02 | 0.00 | 0.0 | 0.0 | 25.0 |
| + noise scale k = 1 (x2.33 on the small cells: 700 / 300 MOhm), at rest | **1.15** | 0.09 | 0.0 | 0.0 | 25.0 |
| the same under the command | 1.58 | 0.01 | 0.0 | 3.0 | 21.3 |
| + noise scale k = 2 (x5.4, a fit), at rest | 14.05 | 1.24 | 0.0 | 0.0 | 25.0 |
| k = 1 with the floor as built, at rest | 0.80 | 0.09 | 0.0 | 0.6 | 0.2 |
| k = 1 with `--floor standing` (no claw, no touch), at rest | 0.80 | 0.09 | 0.0 | 0.0 | 2.2 |

**the right cells, for the first time.** with their measured rest, their measured resistance on both the synapses and the membrane noise,
and the standing leg's senses, the small tibia flexors fire at rest and the large ones do not, which is Azevedo's ordering; the rate is
1.2 Hz against his ~30, a factor of twenty-five. the noise scale is the one term here without a direct measurement behind it: it follows
from the resistance ratio if the cell's current noise is the same across sizes (an assumption, stated), and the engine's noise is white
per millisecond where a cell's is synaptic and coloured. k = 2 is a fit and is reported as one. what the row says: Azevedo's tone is
mostly not in this file's wiring for these cells (13-111 synapses) and mostly not reachable from a white noise at the sourced scale; the
remainder is the cell's own excitability (a persistent inward current, a lower threshold than the population's, or synaptic noise the
file cannot carry), which is campaign item 4 with the small flexors as the named target and Azevedo's 30 Hz as the measured check. one
seed; the k = 1 row is replicated before it is cited. the oracle for the noise term is running; nothing here is a default.

**replicated (23:58 PDT):** the small third at rest, k = 1: 1.15 / 1.18 / 1.30 Hz on seeds 11 / 12 / 13, the large third 0.0 / 0.0 / 0.0, the
extensors 0.0 on all three, IN13A006 25 Hz on all three; every one of the twelve small cells fires (0.4-3.1 Hz). **three of three.** with the
claw classes swapped (claw_50 at 40 instead of claw_51, touch the same): the small third 0.67, the extensors 6.6, IN13A002 86 Hz, IN13A006
0.0; so about 0.7 Hz of the small cells' rate is their own noise at the measured resistance regardless of the senses, and about 0.5 is the
flexion side's senses under the labels as printed. the caveat stands in both directions: the noise term is an assumption made explicit,
and the labelling of which claw class is which decides whether the standing leg adds to it or not.

**the body on the standing senses (00:00 PDT, 09-23; `--senses v2`, 20 s, seed 11, springs, pads, the loop closed, ramp 1 s):** under the command
(DNg100 100 Hz) he lies down in both labellings: 88 % of his weight on the floor with the labels swapped (extensors 6.7 Hz, flexors 0.06),
94 % as printed (extensors 13.4, flexors 0.24). **at rest, no command: 0 % on the floor, the feet carrying all of him** (extensors 0.74, leg
MNs 0.65 Hz per cell): the springs' standing, as recorded on 09-22 ("the standing is the springs'"), now on senses that a standing leg
makes. under the command with shunting inhibition on (`--syn-rev 70:-5:-5 --syn-rev-hold each`): 8 % on the floor, extensors 2.2, leg MNs
1.13. so with the honest senses the command as we give it knocks him down (the tonic extension drive splays the legs), less command-driven
output leaves the springs holding him, and the 580-cell floor's 1 % of 09-22 was the vibration cells' 15 Hz supplying a tone that kept the
legs under him. the honest body: stands on its springs at rest, falls under a tonic walking neuron, stands again when inhibition shunts.
no step, no rhythm, no flexor tone on the body yet (the small flexors' rest of the cord arms needs the graded thresholds and the noise
scale on the body, which `body_loop.py` does not take yet).

**the noise term, oracle (00:05 PDT, 09-23):** `scripts/oracle_check.sh` v1 + v2, all eight configs bit for bit with the per-cell membrane-noise scale unset (`M._noise_scale`, `world/fastlif.py`; `--size-noise K` in the size path). committed.

**the small flexors' rest on the body (00:06 PDT, 09-23; the size path as one helper, `src/fly_afterlife/size.py`, shared by `world/cord.py` and
`experiments/body_loop.py`, defaults bit for bit (body: every saved array, max difference 0; cord: with the flags off and on); the standing
senses, the graded flexor labelling, synapses and noise scaled by the resistance ratio; 20 s, seed 11):**

| arm | on the floor | leg MN Hz | extensors | Ti flexors small / middle / large |
|---|---|---|---|---|
| labels swapped, at rest | 0 % (the feet carry 10.7 uN) | 0.67 | 0.74 | **0.68** / 0.00 / 0.00 |
| labels swapped, command | 86 % | 2.41 | 6.90 | **1.61** / 0.00 / 0.00 |
| labels as printed, at rest | 2 % | 1.16 | 0.04 | **0.75** / 0.00 / 0.00 |
| labels as printed, command | 91 % | 2.62 | 14.27 | **1.28** / 0.00 / 0.00 |

Azevedo's ordering holds on the body under both labellings: all thirteen small cells fire at rest (0.17-1.22 Hz), the middle and large
thirds at 0. the two labellings differ little on the body at rest (0.68 / 0.75) where the cord gave 1.15 / 0.67: on the body the claw
signal at the standing pose is a fifth of the range (the knees 11-13 deg from Mamiya's null) where the cord arm drove it at 40 Hz, so
on the body the rest is nearly all the cell's own noise at its measured resistance. he stands at rest and lies down under the command
in both; the flexor tone at this rate changes neither. the small cells sit at -0.5 to -0.7 mV re rest on the body (sd 0.2-0.3). **where
the campaign's first night ends:** the slow flexors fire at rest, on the body, in the right order, from three sourced changes and one
stated assumption, at a fortieth of Azevedo's rate; the rest of the tone is the cell's own and is item 4's; the standing is the springs';
the command as one tonic neuron knocks him down; no step, no rhythm, no claim about walking.

## day two (10:22 PDT, 09-23): the recorded population on the honest body

**the arm:** `--senses v2`, the graded flexor labelling with synapses and noise at the resistance ratio, shunting inhibition (70:-5:-5 each),
springs, pads, the loop closed, 20 s, seed 11; the command = the whole fly's own descending output recorded on 09-22 (`world/record/
dn_census_0922`: 1,306 DN cells, 60 s, 3.9 Hz per cell mean) replayed onto the cord's DNs, beside DNg100 tonic at 100 Hz and rest.

| arm | on the floor | leg MN Hz | extensors | lifts (lf, 18 s) | coxa fwd frac | lf coxa rhythm | flexors small / mid / large |
|---|---|---|---|---|---|---|---|
| playback, labels swapped | 2 % | 1.06 | 3.4 | 17 | 0.71 | 1.2 Hz (drift) | 0.89 / 0.00 / 0.0 |
| playback, as printed | 31 % | 1.66 | 12.1 | 11 | 0.18 | 1.5 (drift) | 1.00 / 0.00 / 0.0 |
| DNg100 tonic, swapped | 7 % | 1.23 | 2.1 | 10 | 0.60 | 2.0 (drift) | 1.19 / 0.03 / 0.0 |
| rest, swapped | 0 % | 0.12 | 0.1 | 0 | - | 1.1 (sd 1 deg) | 0.68 / 0.10 / 0.0 |

**he stands under the recorded population** (2 % of his weight on the floor with the labels swapped; 31 % as printed, the extensors at 12 Hz
splaying him) with the small flexors' tone on and the middle and large thirds silent, and the left front foot lifts 17 times in 18 s, the
coxa swinging forward on 0.71 of them. no rhythm in any coxa (every spectrum peaks at 1-2 Hz, drift). the tonic DNg100 with the shunt on
also stands (7 %) where without the shunt it lay him down (86-94 % last night): **the shunt is what keeps him up under a command,** in both
forms of it. the recorded population does not walk him; it stands him with occasional forward lifts, the same as one tonic neuron with
the shunt. what it changes: the extensors 2.1 -> 3.4 Hz and the lifts 10 -> 17 in the swapped labelling. the standing is still the
springs' (rest: 0 %, leg MNs 0.12 Hz). one seed; the sourced population (agent) will say which DNs in the recording carry walking and at
what rate, and whether the playback's 3.9 Hz mean is a standing fly's or a walking one's (the recording was the whole fly in its garden,
mostly standing).

**the walking command, sourced (agent; `docs/physiology/walking_command.md`, 10:33 PDT):** no spike rate exists for any forward-walking DN
during walking (DNa02's stride-locked ripple of ~15 spikes/s is the only number, and its lock comes from ascending input the cut removes;
DNg13 >100 Hz under current injection); the population imaging (Aymanns 2022) has ~60 % of imaged DNs encoding walking and never saw the
gnathal DNs (DNg100, DNg97). **the command is tonic at the step timescale; a headless fly steps in a tripod under steady light, so a
step-locked envelope on the DNs is a puppet.** DNg100 favours the extension side at two synapses (IN09A002 1,026, IN17A001 818, IN12B003
771), and so do DNg97, DNg75, DNa13, DNb08, DNg13; the flexion-side DNs in the file are DNg95 (strongly), DNge038 / 035, DNg16, DNa01 (mildly),
none with a walking record but DNa01. DNp09 hardly reaches the cord (it drives DNa11, DNg100, DNg75, DNg97). Pugliese's combinatorial
screen found the rhythm LESS likely when the drive is spread over many DNs. every absolute rate in any population arm is chosen.

**the population arms on the cord (10:33 PDT; the standing senses, the graded tone, the shunt; seed 11, 30 s; DN rates matched to DNg100's
synaptic drive at 100 Hz as the doc sets them):**

| arm | leg MN Hz | extensors | IN13A006 | IN03A004 | promotors | IN17A001 (line) | flexors small / mid / large |
|---|---|---|---|---|---|---|---|
| A0 DNg100 alone, 100 Hz | 4.77 | 1.8 | 10.1 | 7.4 | 2.7 | 15.8 (22.7 Hz x31) | 1.53 / 0.03 / 0.0 |
| A1 DNg100 + DNg97 + DNg75 + DNa01 + DNa02 at 38.2 | 3.37 | 0.4 | 12.5 | 8.9 | 1.2 | 9.8 (x19) | 1.14 / 0.05 / 0.0 |
| A2 the same without DNg100 / DNg97, 79.3 | 1.89 | 0.1 | 14.8 | 11.2 | 0.0 | 3.4 (x15) | 0.97 / 0.09 / 0.0 |
| A3 A1 + the flexion set, 22.9 | 3.05 | 0.4 | 13.0 | 9.7 | 1.9 | 8.5 (x36) | 1.24 / 0.02 / 0.0 |
| the flexion set alone, 100 | 3.21 | 0.6 | 15.5 | 10.0 | 6.4 | 8.2 (x24) | 1.44 / 0.01 / 0.0 |
| rest | 1.28 | 0.0 | 16.2 | 9.3 | 0.0 | 2.0 (x17) | 1.06 / 0.09 / 0.0 |

spreading the command quiets the extension side (extensors 1.8 -> 0.4 -> 0.1, the subnet's line x31 -> x19 -> x15) and leaves the flexion
side where rest has it (IN13A006 10-16 Hz, the small flexors 1-1.5 Hz in every arm); the flexion-side DNs wake the promotors (6.4 Hz) and
nothing else. **no arm switches anything.** the command decides how hard the extension side is pushed and that is all it decides; the
rhythm is not in the command, which is what the sourced doc and Pugliese's screen both say, and the subnet's 20 Hz is loudest under the
one neuron. the doc's prediction for the body (the population still lies him down) is being tested with the shunt on, which stood him
under DNg100 this morning.

**campaign item 4 landed (10:43 PDT; commit 2aa78b7, agent; `--pic TYPES:G:VHALF:K:TAU` in `world/cord.py` and `experiments/body_loop.py`, a
persistent inward current on named cells, off by default; oracle PASS, v1 + v2, eight configs; `experiments/pic_test.py`: a single cell is
quiet below v_half, fires 13 / 25 / 41 / 63 Hz at g 0.25 / 0.5 / 1 / 2 once held near it, off vs g = 0 bit for bit):** I = g m (E - v), E +70 mV re
rest, m first-order with m_inf a sigmoid at v_half, on the ext path. **the parameters are borrowed and say so in the help:** the cockroach
Df L-type calcium plateau (its -51 / -37 mV numbers unverified), the locust plateaus under octopamine (50-75 ms bursts); v_half +3 mV re
rest (the small cells' threshold; -45 mV absolute against Azevedo's -48 rest), k 3 mV (chosen so the onset lands on the cockroach's
plateau threshold), tau 50 ms (the locust's low end), and g set so a fully open cell sits 5 / 10 / 15 mV up (10-15 mV is the plateau
envelope in `knobs.md`; 5 is deliberately below it). no fly leg cell has this measured.

**the arm (the standing senses, the graded tone, the shunt; seed 11, 30 s; `--pic smallflex:G:3:3:50`):**

| g (plateau) | small third | middle | large | extensors | IN13A002 | IN13A006 |
|---|---|---|---|---|---|---|
| 0 (control) | 1.24 (0.4-2.6) | 0.00 | 0.01 | 0.00 | 0.0 | 28.8 |
| 0.27 (5 mV) | 12.1 (8.9-15.8) | 0.00 | 0.01 | 0.00 | 0.0 | 28.8 |
| 0.58 (10 mV) | **36.4** (28.9-39.7) | 0.00 | 0.01 | 0.00 | 0.0 | 28.8 |
| 0.95 (15 mV) | 62.3 (52.5-65.0) | 0.00 | 0.01 | 0.00 | 0.0 | 28.8 |

**Azevedo's ~30 Hz at rest for the slow tibia flexors falls between the small and the medium borrowed value (about g 0.5 by interpolation;
not tuned to it), with the middle and large thirds and the extensors at zero in every arm.** so a persistent inward current of the size
other insects' motor neurons carry supplies the tone the file's wiring cannot; it does not pin how big the fly's is. the caveat the agent
wrote and i keep: with these parameters the current is a quarter open at rest (m_inf(0) = 0.27), so the small cells fire on their own
current, a tonic depolarisation rather than a plateau switched on by input, which follows from mixing absolute voltages across species.
nothing downstream moves (IN13A002 0, IN13A006 28.8 in every arm). ledger row 9. one seed, cord only.

**the population on the body (10:43 PDT; the standing senses, the graded tone, the shunt, ramp 1 s, 20 s, seed 11):** A1 (DNg100 + DNg97 +
DNg75 + DNa01 + DNa02 at 38.2 Hz): **0 % of his weight on the floor in both labellings** (leg MNs 0.84 / 0.85 Hz per cell, extensors 0.84 / 0.56),
10 lifts (swapped) / 2 (as printed); A3 (+ the flexion set at 22.9): 0 %, 5 lifts, the coxa forward on all of them, -10 deg. the sourced
doc's prediction ("the body still lies down") was written for a body without the shunt; with it he stands under the population as he
stood under the single neuron, and quieter (the extensors 0.6-1.1 against 2.1). the standing is the springs' in every case. no rhythm.

## the switch, aimed (10:46 PDT, 09-23; the cord under DNg100 100 Hz on the full stack: the standing senses, the graded flexor tone, the shunt;
release mechanisms on the half-centre's own cells: the winners IN13A002 / 003, IN13B001, IN26X001, IN12B003, IN19A004 and the releasers
IN13A006 / 015, IN13B019, AN06B002; seed 11, 30 s)

- **fatigue (depression u 0.3, tau 300 ms) on the winners' outputs:** IN13A003 7.1 -> 11.9 Hz (the depressed cell fires more, its output
  weaker), IN13A006 10.1 -> 12.8, IN03A004 7.4 -> 10.4, the extensors 1.8 -> 1.1, the tibia flexors 12.7 -> 12.7 (the small third's tone,
  unchanged); r(IN13A002, IN13B019) 0.00. **on the releasers' outputs:** nothing moves (IN13A006 10.0, extensors 2.3). no alternation, no
  lobe in the promotors (autocorrelation -0.04 / -0.01 / 0.00 at 30 / 70 / 140 ms; lf promotor 3.5 Hz, remotor 1.4).
- the `--pic` parser takes one group (TYPES:G:VHALF:K:TAU) and `smallflex` does not combine with named types, so the plateau arms on the
  pair run without the small flexors' current (their tone is the graded rest + noise, 1.2 Hz); the switch question does not need it.
  plateau on the releasers, on the winners, on both, both + fatigue on both (u 0.3 / 300 and u 0.5 / 500), fatigue on both alone: running.

**plateaus on the pair (10:49 PDT; `--pic` at the medium borrowed size (g 0.58, v_half +3, k 3, tau 50) on the releasers, the winners, both;
both + fatigue on both (u 0.3 / 300 ms; u 0.5 / 500); fatigue on both alone; with the shunt; seed 11):**

| arm | IN13A002 | IN13A003 | IN13B019 | IN13A006 | IN03A004 | extensors | r(13A002, 13B019) |
|---|---|---|---|---|---|---|---|
| control | 0.0 | 7.1 | 0.1 | 10.1 | 7.4 | 1.8 | - |
| plateau on the releasers | 0.0 | 7.4 | **23.3** | 27.9 | 9.5 | 0.4 | - |
| plateau on the winners | **12.3** | 20.1 | 0.0 | 6.9 | 5.7 | 2.2 | -0.01 |
| plateau on both | 5.9 | 20.0 | 21.7 | 21.1 | 8.0 | 0.5 | -0.06 |
| fatigue on both alone | 0.0 | 11.9 | 0.2 | 12.7 | 9.5 | 1.6 | - |
| plateau + fatigue on both (u 0.3 / 300) | 8.2 | 32.1 | 23.7 | 32.5 | 10.3 | 1.0 | -0.10 |
| plateau + fatigue on both (u 0.5 / 500) | 10.3 | 35.0 | 23.8 | 35.8 | 10.4 | 1.5 | -0.05 |

a plateau on one side wakes that side and quiets the other (the releasers up: IN13A002 stays 0, the extensors 1.8 -> 0.4; the winners up:
IN13B019 0, IN13A006 halves); **a plateau on both sides wakes both, and they fire together** (IN13A002 6-10 Hz beside IN13B019 22-24), with
fatigue on both making them fire more, not alternate: r -0.05 to -0.10 at zero lag, no lobe in the promotors (autocorrelation -0.05 / 0 / 0
and -0.09 / 0 / 0.02 at 30 / 70 / 140 ms; lf promotor and remotor 3.9 / 3.6 and 4.6 / 4.6 Hz, xcorr min -0.04 / -0.09). the mutual inhibition
is reciprocal in the file (2,279 onto IN13B019 from IN13A002; 1,500-1,900 back onto the winners from each releaser type), but under the
shunt a cell held up by its own current is shunted, not silenced, so both sides sit near their plateaus and neither wins. **the classic
recipe (plateaus + fatigue on a reciprocally inhibiting pair) does not alternate here under shunting inhibition.** the same arms with
current-based inhibition, and with slow fatigue (tau 2 s), and the lag structure out to +-2 s, are running: if there is a slow
alternation the 10 ms zero-lag read would miss it.

**the pair under current-based inhibition and slow fatigue (10:51 PDT; the same stack without the shunt; plateaus on both; fatigue u 0.5 at
500 ms and at 2 s; the plateau at the large borrowed size; the lag structure of the winners' pool against the releasers' pool out to +-2 s):**

| arm | IN13A002 | IN13A003 | IN13B019 | IN13A006 | extensors | xcorr at 0 (min, lag) | winners' autocorr 0.1 / 0.5 / 1 / 2 s |
|---|---|---|---|---|---|---|---|
| plateaus, shunt (S7) | 5.9 | 20.0 | 21.7 | 21.1 | 0.5 | +0.18 (-0.05 at +1.1 s) | +0.01 / +0.01 / +0.02 / 0.00 |
| plateaus, no shunt | 6.6 | 33.2 | 23.9 | 35.1 | 0.7 | +0.26 (-0.03 at -0.9 s) | +0.01 / -0.01 / 0.00 / 0.00 |
| + fatigue u 0.5 / 500 ms, no shunt | 12.4 | 44.1 | 24.6 | 45.4 | 3.7 | +0.33 (-0.08 at -100 ms) | -0.04 / -0.04 / 0.00 / -0.02 |
| + fatigue u 0.5 / 2 s, no shunt | 13.0 | 45.8 | 24.8 | 47.2 | 4.6 | +0.36 (-0.12 at -100 ms) | -0.07 / +0.03 / 0.00 / -0.01 |
| + fatigue u 0.5 / 2 s, shunt | 11.8 | 35.9 | 24.2 | 38.7 | 1.8 | +0.31 (-0.04 at -1.5 s) | +0.05 / -0.02 / +0.01 / -0.02 |
| the large plateau (g 0.95), fatigue 2 s, no shunt | 32.2 | 61.1 | 44.6 | 62.5 | 4.6 | +0.19 (-0.06 at +200 ms) | -0.03 / -0.02 / -0.01 / +0.02 |

**the two sides of the half-centre are positively correlated at zero lag in every arm (+0.18 to +0.36) and nowhere anti-correlated at any
lag out to two seconds; both pools carry the subnet's line (the winners' spectrum peaks at 16-19 Hz, x17-29).** with or without the
shunt, with fatigue fast or slow, with the plateau at the medium or the large borrowed size, they fire together. so the file's 13A / 13B
pair, reciprocally wired as it is, is not a half-centre at these weights: its common drive (the 20 Hz subnet, the senses, the command)
outweighs its mutual inhibition, and every release mechanism the engine has makes both sides louder together. the wiring's reciprocity
is real (the one-sided plateau arms show it); the switching is not a property of these cells with these synapses. **item 4 on the pair:
closed, negative, on one seed.** what would make it a switch: stronger mutual inhibition than the file's (item 7, a claim about
missing synapses, with no source yet), or a phasic input that neither side shares, which in a headless fly is the leg's own movement
senses (hook / club / campaniform in swing), silent in every cord arm because nothing moves, and driven on the body only by a leg that
already moves. the campaign's line for today: the switch is not in the premotor pair's intrinsic properties. next: the body with the
full stack, both labellings, clips; and the movement senses read on the body's own lifts.

**the small flexors' current on the body (10:54 PDT; the full stack: the standing senses, the graded tone, the shunt, `--pic smallflex:0.58:3:3:50`,
DNg100 100 Hz ramped, 20 s, seed 11, both labellings):** the small third fires **35.3 / 36.3 Hz per cell on the body** (the middle 2.2, the
large 0.0): Azevedo's slow-flexor rate, on him, in his ordering, in both labellings. and it costs him the stance: 55 % of his weight on the
floor (swapped) / 30 % (as printed), the left front foot in the air 87 % of the time (swapped; its height's tenth percentile 0.25 mm
against 0.03 standing), the left middle knee pulled to 43 deg (as printed) from 87-93 in the other arms. **the tone is right and the force
is wrong:** every motor neuron spike moves the joint by the same 42 nN.m in `body_loop.py` (the gain from Azevedo's FAST tibia extensor
spike), so thirteen slow cells at 35 Hz pull like thirteen fast ones. in the fly the slow motor neurons' force per spike is a small fraction
of the fast ones' (Azevedo 2020 measured the tibia's force per spike by type; the size principle is a force principle), and thirty hertz of
slow tone holds a posture, it does not fold the leg. so the next body change is sourced and on the muscle side: force per spike by motor
neuron class, from Azevedo's measurements, in the muscle map. until then the small flexors' current stays a cord result. (the pair's
current on the body is running for completeness; `body_loop.py` takes `--std TYPES` without u / tau overrides.)

**the pair's current on the body (10:55 PDT; plateaus + depression on the winners and the releasers, the full stack, DNg100 100 Hz, labels swapped):** he stands (0 % on the floor, the feet carrying 10.7 uN), leg MNs 1.13 Hz, extensors 1.41, flexors 0.36 (no small-flexor current in this arm); 8 lifts of the left front foot in 18 s, the coxa forward on all of them (-10 deg). the pair's cells are not in the body's default log; on the cord they co-fire (above). for completeness: a standing fly with a few forward lifts, as before.

**withdrawn in place (11:02 PDT): "the tone is right and the force is wrong."** `experiments/body_loop.py` already weights each motor
neuron's force by its size (`f_w`, from its input synapses): the small tibia flexors pulled at 0.003-0.06 of a fast cell before any change,
0.13-0.37 nN.m of flexion torque per leg at 35 Hz; the 42 nN.m is the gain, not what a slow spike delivers. **and no knee sits flexed in
any arm:** the left front foot's time in the air comes from another joint, the left middle knee's 43 deg was EXTENSION by its extensor (a
-60 deg swing in the as-printed arm), and by the pooled thirds the left front and left middle legs have no slow flexor at all. the 55 %
on the floor is one seed. the explanation was mine and it was wrong; the agent checked the torque and the knees before building.

**force per spike, sourced (agent; `docs/physiology/force_per_spike.md`; `--mn-force uniform|azevedo` in `experiments/body_loop.py`,
default bit for bit; commit bb5ce64):** Azevedo et al. 2020 is **eLife** 9:e56754 (not Nature, as `knobs.md` and the 09-22 entries have it;
corrected here) and measured the **tibia flexor only**, female front leg, force on a probe at the tibia tip: fast (1 cell) ~10 uN and ~50 um
per spike; intermediate (2-5 cells) ~1 uN, ~5 um; slow (8-9 cells) under 0.1 uN (fitted slope 0.013 uN), ~1 um, no twitch at all, force still
rising at 500 ms, and blocking their input drops the resting force by ~1.5 uN. ratios 1 : 0.1 : 0.0013. two spikes give 1.6x one; force
stops growing at ~10 spikes; no fusion series, no tetanic force, no extensor ever measured, no other pool, nothing in NeuroMechFly or
FlyMimic at the spike-to-force step. with `azevedo` the measured factor replaces the size weight on the 37 tibia flexors by third (the
thirds label 12 cells fast where the pool has one per leg, a known mismatch), the other 222 mapped cells keep their size weight.
**the arms (the full stack with the small flexors' current, 20 s, seed 11):** the small third at 34-36 Hz in all four; walk, swapped: 8 %
on the floor (uniform 55 %), the foot in the air 66 % (uniform 87 %), 11 lifts; walk, as printed: 26 % (30 %); rest: 0 % in both, no lifts,
the knees at 1-3 deg sd. one seed each; the 55 -> 8 could be chaos on a 0.2 nN.m change. the slow factor may be ten times too low (the
1.5 uN resting-force drop implies ~10x the fitted slope; bracketed in the doc). so the slow flexors' tone on the body, at either force
scale, neither holds him nor folds him: the standing is the springs' and the tone is a few hundredths of a nanonewton-metre.
  (correction to the correction: `knobs.md` already cites eLife 9:e56754; the 'Nature' was in my brief to the agent, not in the doc.)

## the movement senses on his own lifts (11:27 PDT, 09-23; `--log-x` in `experiments/body_loop.py` (named types at 1 ms, off by default),
`experiments/lift_read.py`; the full stack (the standing senses, the graded tone with the small flexors' current, the shunt, Azevedo's force
per spike) under the recorded whole-fly DN population, 30 s, seeds 11 / 12 (labels swapped) and 11 (as printed); a lift = the foot's
smoothed contact force at or under 0.05 for 50 ms or more)

- **lifts come in bouts.** left front: 30 / 47 / 22 lifts in 28 s; inter-lift intervals cv 1.45 / 1.62 / 1.63 (a Poisson process gives 1) with
  serial correlation +0.35 / +0.39 / +0.68; after a lift ends the next begins within 300 ms 0.59 / 0.72 of the time where Poisson at the
  same rate gives 0.27 / 0.40. **inside a bout the gap is 160-200 ms with a cv of 0.25-0.46: five hertz, regular.** the middle legs more so:
  lm 72 / 63 lifts and rm 69 / 76, ten bouts of three or more per leg, in-bout gaps 190-200 ms at cv 0.24-0.32; the hind legs never lift.
- **who leads a lift (the 100 ms before onset against the run's baseline, 20 ms bins):** the hooks (SNpp39 / 41, the velocity cells) rise
  first, 40-100 ms before the foot unloads, because the leg is already moving; the flexion claw (SNpp51) with them; the trochanter
  extensor motor neurons (the levators) up from 0.8 to 1.2-1.7 Hz over the preceding 200 ms; **the 20 Hz subnet bursts in the 20 ms at
  onset** (INXXX466 20 vs 10 Hz base, IN09A002 51 vs 33, IN17A001 15 vs 9), coincident with it (cross-correlation with the onset train
  peaks at +20 ms), not before; IN13A002 falls (0.85-0.88 of base) under the labels swapped and RISES (1.23) with them as printed, where
  SNpp50 leads instead; the releaser IN13B019 never fires; the clubs never fire (v2 holds them at 0: they have no motion drive). so a lift
  in this body is: the leg moves, the movement senses say so, the subnet fires with the unloading, and the next lift follows more often
  than chance. sensory-motor, per leg.
- **the legs do not talk to each other.** onset-train cross-correlations between the middle legs, and front to middle, are 0.02-0.12 at
  their best lags; the right middle's lifts fall uniformly across the left middle's in-bout cycle (histograms 5 / 8 / 1 / 1, 6 / 4 / 3 / 2,
  3 / 3 / 3 / 2 in quarters); both middle feet are off the ground together exactly as often as independence predicts (29.6 vs 32.2 %,
  40.1 vs 39.1, 23.7 vs 27.0). **six oscillators, uncoupled.** no tripod, no antiphase, no gait.
- **and the five hertz is not the command's and not new:** the same 150-240 ms in-bout gap at cv 0.2-0.4 appears in every arm with an
  unloaded leg: at rest (rm 19 lifts, 228 ms), under the tonic neuron (rm 200, lh 238), under the shunt (lf 179), and in the 09-22 fit
  (`ld_100_x8_ramp1`: lf 154, rf 184, rm 199). what the command changes is how much of the time a leg is off the ground (the middle legs 50-75 %
  under the population, 2-9 % at rest). so the per-leg five hertz is a property of the leg-ground-spring-pad system with the cord in the
  loop; whether the cord is in it at all (a reflex bounce) or the leg would bounce with its motor output frozen (a mechanical bounce) is
  the control this read needs and the body script cannot yet run (`--freeze-mn S`: hold every muscle activation at its value at S seconds).
  until that control is run, the bouts are a per-leg oscillation of unknown origin at the frequency of a slow step, uncoupled across legs,
  and the record claims no more.

**the control (11:29 PDT; `--freeze-mn 15` in `experiments/body_loop.py`: every muscle activation and grip held at its value at 15 s and no
spike fed into it afterwards; the same arm and seed as `lift_s11`):** before the freeze the two runs are the same run (lf 8 lifts, lm 37
with 184 ms gaps at cv 0.34, rm 20 at 222 ms / 0.22, in both). **after it, nothing: 0 lifts on every leg, 0 % of the time off the ground,
thorax speed 0.00 mm/s for fifteen seconds,** where the unfrozen run goes on at lf 22 / lm 35 / rm 49 lifts with the same 170-200 ms
gaps. a frozen muscle set on springs and pads holds a still posture; the bouts need the cord. **so the per-leg five hertz is neural: a
reflex oscillation through the leg's own senses and the cord, on a body, with no term fitted to it.** what it is not: coupled across
legs (above), a gait, or a rhythm the cord makes alone (no cord arm has ever shown it; it needs the leg to move). what it is: the first
rhythm in this project that the connectome makes with its body and nothing else. one seed; the second and the subnet's part are running.

**replicated and opened (11:33 PDT):** the freeze on seed 12: before it the same run as `lift_s12` (lf 14 lifts at 174 ms, lm 34 at 207, rm 31 at
183); after it 0 lifts on every leg (the left middle frozen in the air, the others on the ground) where the unfrozen seed goes on at 33 /
29 / 45. **two of two.** and the loop opened (`--loop off`: no claw, hook, hair-plate, load or touch rows; the floor and the command as
before): he holds every foot off the ground for the whole run (100 % off on all three legs read, 18 % of his weight on the floor) and
makes no lift at all. so the bouts need the senses in the loop AND the cord in the loop: a leg that cannot feel itself does not step, a
cord that cannot move the leg does not step, and a leg that can do both steps at five hertz on its own. the reflex has its two halves.

**what the reflex is made of, first pass (11:37 PDT; the bouts arm, seed 11, cells silenced by threshold; `--silence` added to `body_loop.py`):**
the eight cited subnet cells silenced (48 cells): lf 35 lifts at 192 ms, lm 62 at 195, rm 53 at 213: **the bouts do not need the 20 Hz
subnet** (it bursts with each lift; it does not make them). the 13A inhibitors IN13A002 / 003 / 005 silenced (18 cells): lf 51 / lm 73 / rm 77
at 192-209 ms, the extensors 4.1 -> 2.9: **not needed either,** more lifts without them. the hook cells (SNpp39 / 41) "silenced": the run
is bit for bit the control, because the hooks are driven rows and the threshold cannot touch a driven cell (the flag says so); the
senses are removed by their own rates instead (`--hook-hz 0`, `--claw-hz 0`, `--leg-load-hz 0`, `--tactile-hz 0`), running next. what
stands: the reflex runs through the leg's senses and the cord's motor side without the rhythm subnet and without the premotor
inhibitors the campaign spent two days on.

## the legs on the ground (11:42 PDT, 09-23; the tonic DNg100 dosed 30 / 60 / 100 / 150 Hz on the full stack, ramp 1 s, 30 s, seed 11; the
question: do the bouts survive with weight on the legs, and do the legs then avoid each other)

| DNg100 Hz | on the floor | lf off / lifts / gap | lm off / lifts / gap | rm off / lifts / gap | both middle feet off: seen vs independent |
|---|---|---|---|---|---|
| 30 | 0 % | 8 % / 11 | 1 % / 2 | 4 % / 6 | 0.2 vs 0.1 % |
| 60 | 1 % | 25 % / 36 / 207 ms | 22 % / 38 / 194 | 11 % / 17 / 170 | **0.8 vs 2.5 %** |
| 100 | 10 % | 77 % / 11 | 74 % / 13 / 153 | 10 % / 13 / 178 | **1.3 vs 7.1 %** |
| 150 | 87 % | 98 % / 2 | 96 % / 3 | 85 % / 4 | 83.5 vs 81.9 % (down) |
| the recorded population | 7 % | 22 % / 30 / 163 | 69 % / 72 / 191 | 46 % / 69 / 182 | 29.6 vs 32.2 % |

at 60 Hz the bouts run with every leg on the ground three quarters of the time or more (lf 36 lifts, lm 38, at the same 170-207 ms gaps),
and **the two middle feet are off the ground together a third as often as independence predicts (0.8 vs 2.5 %); at 100 Hz a fifth as
often (1.3 vs 7.1 %).** under the recorded population, where the middle legs hang in the air half the time, the same statistic is at
independence (29.6 vs 32.2). so when the legs carry him, one middle leg up means the other stays down: the first sign of coupling
between legs in this project, and it appears exactly where mechanics would put it (a loaded body) and disappears where a leg is not
loading the other. the onset cross-correlations stay small (0.03-0.07 at their best lag), so it is exclusion, not a phase lock. small
counts (13-38 lifts); seeds 12 / 13 at 60 and 100 Hz and 80 Hz are running before the word "coupling" is used without a hedge.

**the senses removed one at a time (11:50 PDT; the bouts arm, seed 11; each sense's rate set to 0 with the others on):**

| removed | lf off / lifts / gap | lm off / lifts / gap | rm off / lifts / gap |
|---|---|---|---|
| nothing (the arm) | 22 % / 30 / 163 ms | 69 % / 72 / 191 | 46 % / 69 / 182 |
| the hooks (velocity) | 26 % / 40 / 222 | 78 % / 66 / 201 | 48 % / 75 / 188 |
| the claw (position) | 35 % / 37 / 229 | 78 % / 45 / 194 | 40 % / 50 / 192 |
| the load (campaniform + untyped) | 16 % / 23 / 200 | 54 % / 66 / 191 | 57 % / 66 / 193 |
| touch (the bristles) | 38 % / 55 / 202 | 79 % / 46 / 181 | 28 % / 62 / 163 |
| the hair plates | 37 % / 60 / 202 | 79 % / 51 / 183 | 44 % / 69 / 190 |
| everything (`--loop off`) | 100 % / 0 | 100 % / 0 | 100 % / 0 |

**no single sense is necessary and the sum of them is:** the bouts run at 160-230 ms with any one sense gone and stop only when all are.
the reflex is redundant across the leg's afferents, which is what a leg's reflexes are in the stick insect (any of load, position and
movement can time the transition). the load is the one whose removal lowers the front leg's lifts (30 -> 23) and raises the middle's
time in the air least; touch and the hair plates, removed, raise the front leg's lifts (55, 60): they hold the foot down. which single
sense is SUFFICIENT is the next arm (`--loop position` = claw, hook, hair plates only; `--loop load` = load and touch only).

**withdrawn before it was claimed (11:51 PDT): "the first sign of coupling."** the seeds: at 60 Hz the right middle leg lifts 17 times on seed
11 and 1 / 0 times on seeds 12 / 13; at 100 Hz, 13 / 0 / 0. with one middle leg still there is nothing to exclude, and the both-off statistic
sits at independence (0.9 vs 1.5 %, 1.1 vs 1.2, 2.4 vs 2.4, 2.3 vs 2.4). seed 11 was the one run in which both middle legs stepped, and its
deficit (0.8 vs 2.5, 1.3 vs 7.1) is one seed. **not claimed.** what does replicate is the other way round: the left front and left middle
feet are off the ground together MORE than independence on every seed where both lift (12.6 vs 5.5 %; 78 vs 73; 87 vs 83; 61 vs 49; 73 vs
57; 95 vs 93; 97 vs 95): the ipsilateral neighbours co-lift, where a fly's are antiphase. and the asymmetry underneath it: the left legs
are off the ground 20-97 % of the time and the right legs 0-13 % in every dose arm. he leans right, the left side hangs, and the left
legs lift together because they are the unloaded side. that is a posture, not a coordination. the record's line on coupling stands as
it was before noon: six oscillators, uncoupled, and the fly's coupling is central (Mendes 2013: proprioceptive silencing leaves the
tripod intact; Sapkal 2026: the commissural 19B cells onto the 19A locals), which is the read that comes next.

**which sense is sufficient (11:56 PDT; the bouts arm, seed 11, one class of sense at a time):**

| senses in the loop | lf | lm | lh | rm |
|---|---|---|---|---|
| all (the arm) | 22 % off, 30 lifts, 163 ms | 69 %, 72, 191 | 5 %, 7 | 46 %, 69, 182 |
| position only (claw + hook + hair plates; `--loop position`) | 100 % off, 0 | 100 %, 0 | 100 %, 0 | 100 %, 0 |
| hooks only | 100 %, 0 | 100 %, 0 | 100 %, 0 | 100 %, 0 |
| load + touch (`--loop load`) | 57 %, 41, 222 | 88 %, 25, 209 | 32 %, 44, 170 | 19 %, 27, 184 |
| **load only (campaniform + untyped, no touch)** | 62 %, 42, 210 | 89 %, 26, 194 | 36 %, 35, 188 | 12 %, 13 |
| none | 100 %, 0 | 100 %, 0 | 100 %, 0 | 100 %, 0 |

**the load reflex is the oscillator.** with only the campaniform (load) rows in the loop, four legs step in bouts at 170-210 ms; with every
position and movement sense in the loop and no load, he holds all six feet in the air and never steps, exactly as with no senses at all.
so: load on a foot -> the cord extends the leg into stance; the foot's unloading (or the extension itself) -> the leg lifts; the lift
unloads it further; ~200 ms later it comes back down. the stick insect's load-dependent stance-swing transition (campaniform sensilla
timing the step: Zill, Büschges; `walking_review.md`), running on the fly's wiring and the fly's body, with the load signal as the file
and the map give it (111 cells; rate chosen, ledger row 3 / 6). the position senses shape it (touch and the hair plates hold the foot
down; the claw and hooks change the gaps by 20-60 ms) and cannot make it. **campaign: the reflex is named.** next: the fly's central
coupling (the commissural 19B cells onto the 19A locals, Sapkal 2026; Mendes 2013 says the tripod survives without proprioception), logged
and silenced on this arm.

**the fly's coupling circuit, on this arm (12:02 PDT; Sapkal 2026's commissural 19B cells AN19B009 (4 cells) and IN19B005 (2), both
excitatory in the file, their largest targets IN19A011 (813 synapses), IN19A012 (561), IN19B010, IN09A006, IN19B003, IN17A025, IN19A001;
logged at 1 ms in the bouts arm and silenced on seeds 11 / 12, their four 19A targets silenced on seed 11):** **the commissurals are silent
in this arm** (AN19B009 0.4 Hz per cell, IN19B005 near 0) while their 19A targets fire 9-17 Hz from other sources; silencing the
commissurals changes nothing (lm 72 / rm 77 lifts on seed 11, 55 / 65 on 12; the both-off statistic at independence before and after:
29.6 vs 32.2 -> 33.7 vs 35.2; 40.1 vs 39.1 -> 27.7 vs 29.3), and silencing their 19A targets changes nothing (65 / 54; 20.6 vs 22.7). so
the circuit the field names for left-right alternation is present, wired as described, and not driven in a headless fly under his own
recorded standing command; Pugliese found the same cells "insufficient to couple the phase" in their model with the command at its
walking rate. what drives them in the fly is the next census (their inputs, below), and the arm that follows is the tonic command at
60-100 Hz with the commissurals logged: if they wake under a walking-rate command, the coupling test is theirs to fail or pass.

**the commissurals under a walking-rate command (12:07 PDT; logged on the full stack, seed 11):** AN19B009 / IN19B005 at 0.4 / 3.5 Hz under
the recorded standing command, 2.0 / 7.3 under DNg100 at 60 Hz, 3.1 / 12.3 at 100, 2.1 / 8.1 under the five-DN population; their 19A
targets 15-20 / 7-10 Hz throughout. so the command wakes them a little (their inputs: IN17A001 622 synapses, INXXX468 605, DNg100 366,
IN03A006 364; inhibited by their own targets IN19A011 477, IN19A020 346, IN19A001 293; E and I one to one, 2,936 synapses per cell), and
at 3 and 12 Hz they are not the strong commissural drive Sapkal describes; and at those doses only one middle leg steps on two of three
seeds, so there is no second leg to couple. the sourced coupling circuit is present, wired as described, weakly driven by the command
and the subnet, and balanced by its own targets. **where day two ends on coupling:** the fly's circuit needs, in this file at these
weights, either more drive than the command gives it or more weight on its synapses than the file carries, and the second is item 7
with, for the first time, a named circuit and a paper that names it. not built today.

## withdrawn in place (12:39 PDT, 09-23; the code review of day two, `docs/REVIEW_DAY_TWO.md`, R1-R5)

**R1, the highest: "the loop opened: no senses, no lifts" and "the load reflex is the oscillator" are withdrawn.** `experiments/body_loop.py`
read the feet's contact force only when load was in the loop (`F = leg_forces() if (use_load or ...) else np.zeros(6)`), and the lift
counter reads a lift as force <= 0.05, so in the `--loop off`, `--loop position` and hooks-only arms every foot was "off the ground 100 % of
the time, 0 lifts" by construction (the saved `leg_force` of those arms is identically zero), and the pads never engaged in them either.
the reviewer rebuilt foot heights from the saved joint angles and body pose (82-97 % agreement with the force count where the force was
read): **all three arms step in the same ~200 ms bouts, the no-senses arm included.** so the sufficiency table's position / hooks / none rows
are artifacts, the bouts do not need the senses, "the reflex has its two halves" is withdrawn, and the campaign's "named" reflex is unnamed.
what stands: the freeze control (force read; the bouts need the cord's motor output), the ablation rows (force read; no single sense
necessary), the load-only row (force read; bouts with load alone), and every clip. the force is now read unconditionally (the
`position+load` path is unchanged); the three arms are re-run below with the force read.
**R2:** the bout statistics do not show an oscillator: gaps drawn from a memoryless process give the same ~190 ms and cv ~0.3; the
Poisson rate taken over time on the ground puts the middle legs' clustering at chance (0.93 vs 0.92); the motor neurons carry no 5 Hz
peak. what the lifts track is the trochanter levator burst 20 ms ahead. "five hertz, regular" is withdrawn; "lifts in bouts" stays as a
description. **R3:** the slow / intermediate / fast thirds were ranked across all six legs, so the left front and left middle legs got no
slow tibia flexor, no rest tone and no plateau current: the two legs that hang in "he leans right". untested as a cause. **R4: the
small flexors' rest is built in.** an isolated LIF with no synapses, a 3 mV threshold and the engine's noise x2.33 fires 0.80 Hz (the
record: 1.15); with x5.4, 13.6 Hz (the record: 14.05). so "the small third fires at rest" is the thresholds and the noise scale i set,
and "Azevedo's ordering" is the ordering i put in; the entries of 23:47-23:58 and 00:06 stand as measurements with this beside them: they
are constructions, not physiology, and the one size CSV also gave the middle and large thirds x0.47 and x0.30 where the stated
resistances give x1.0 and x0.5. **R5:** the touch rows chatter (the net force crosses the contact threshold 20-74 times a second per leg,
restarting the onset burst), so touch ran at ~100 Hz for 31-93 % of stance instead of 20. **sound:** the three engine terms and their
tests, the defaults (max difference 0), the claw's 90-deg reference and the knee sign, the tactile seeding, the load-only arm's rows.

**the claims review (12:42 PDT; `docs/REVIEW_CAMPAIGN_DAY_TWO.md`):** verdict: the first night holds because it was withdrawn in place each time;
"the load reflex is the oscillator" does not hold (R1); the freeze shows only that the lifts need the cord's changing motor output; **the
likeliest reading is timing set by the body (springs, pads, the 120 ms twitch kernel) under a noisy cord output, and nothing yet rules
that out.** the test: feed the muscle map Poisson spike trains at each motor neuron's own mean rate and change only the body; if the
lifts survive, the body sets the rhythm. built (`--mn-poisson RUN` in `body_loop.py`) and running on three seeds. also from the review, in
place: **the load pathway's sign is opposite to the stick-insect reflex** (new cord arms, three seeds: loading the cord pushes the middle
legs toward swing, promotors 0.1-0.8 -> 5.6-7.2 Hz, remotors down), so the stick-insect analogy in the withdrawn entries goes with them;
**"the first rhythm the connectome makes with its body" is withdrawn** wherever it stands; **"Tr extensor MN (the levators)" is wrong:
the trochanter extensors are depressors** (the levators are the trochanter flexors), so the cell that rises before a lift in the
lift-triggered read is the depressor, which is consistent with a push-off, not a lift; **"six oscillators" is "at most four legs"**
(the right front and right hind never lift); the lean has a second candidate cause, a command-side asymmetry the cord shows alone
(the left middle driven toward remotion, the right toward levation) that persists without the size terms, the current or the shunt;
"Azevedo's ordering" is put in, not found, and the plateau strength "nearest 30 Hz" is calibration; fourteen ledger rows were missing
and are added to `CAMPAIGN.md` now; silencing the commissurals at 0.4 Hz tested nothing.

**the three arms re-run with the force read (12:45 PDT; seed 11; the default path checked bit for bit against `lift_s11` first):**

| senses in the loop | lf off / lifts / gap | lm | lh | rm |
|---|---|---|---|---|
| all (`lift_s11`, and the re-run `fx_full`, identical) | 22 % / 30 / 163 ms | 69 % / 72 / 191 | 5 % / 7 | 46 % / 69 / 182 |
| none (`--loop off`) | 62 % / 33 / 226 | 88 % / 24 / 172 | 36 % / 32 / 186 | 16 % / 27 / 193 |
| position only | 29 % / 47 / 191 | 76 % / 60 / 178 | 3 % / 5 | 39 % / 60 / 207 |
| hooks only | 65 % / 23 / 173 | 88 % / 30 / 179 | 37 % / 35 / 190 | 14 % / 22 / 205 |
| load only | 62 % / 42 / 210 | 89 % / 26 / 194 | 36 % / 35 / 188 | 12 % / 13 |

**with no sense in the loop at all the legs lift in the same 170-230 ms bouts, on four legs.** the senses change which legs and how long
they hang (with none or with load only the left legs hang more and the left hind joins in; with the position senses the pattern is the
full arm's), not whether the bouts happen. so the bouts are the cord's motor output on the body with no sensory loop required, which
leaves two candidates for their timing: the cord's own output dynamics under the command, or the body (springs, pads, the twitch kernel)
under a noisy drive. the Poisson-motor control (running) separates them.

## the physics review (12:52 PDT, 09-23; `docs/REVIEW_PHYSICS.md`; nate: "he does look heavy")

**sound:** gravity 9810 mm/s^2 (9.81 m/s^2, flygym's `mujoco_globals.yaml`; our only override is `--gravity`, 1.0 in every clip); units mm / g / s
so forces are uN and torques nN.m; his weight 10.05 uN computed from the body masses (`body_loop.py:248`), the vertical ground reactions
summing to it at rest (10.02-10.20); the model 1.024 mg (head 0.150, thorax 0.307, abdomen 0.450, legs 0.109) against Vaxenburg 2025's
weighed females (0.983 mg), so 15-25 % heavy for a male, worth 0.05 mm of height; the spike-to-torque conversion consistent (gain 42 / 10 =
4.2 nN.m at the peak of a full spike, Azevedo's fast tibia spike; the actuator cap +-60 nN.m); ten physics steps per neural millisecond;
friction and the contact solver; no joint limit carrying weight at rest.

**withdrawn in place: "he stands."** the clips ran on flygym's default springs (stiffness 10, not the 0.14 the record calls "measured": the
0.14 was flygym's 10 divided by 70, a derivation), and those springs cannot hold the model's neutral pose: with no muscle he sinks from
1.39 mm to 0.78, and **the hind coxae rest on the floor carrying 45 % of his weight.** the standing statistic ("the body (thorax / abdomen /
head) rests on the floor with x % of his weight") counts only those three segments, and each leg's contact force is summed from the coxa
down, so a coxa on the ground was counted as a foot: in the clips a coxa is down in 45-78 % of frames. so every "he stands on his feet, n %
on the floor" since 09-22 is "he sits on his hind coxae with his feet under him"; the pads (1 uN each, a tenth of his weight, unsourced)
are not holding him up (on a flat floor their pull only adds to the floor's push: 16.07 = 10.05 + 6). the body needs a stiffness of ~20 to
stand on its feet with no muscle and >= 50 to stand near its neutral height; the repo's own sourced passive stiffness (2e-8 N.m/rad = 20
in model units) would stand this body alone, which the earlier headline ("the standing is the springs'") had backwards in scale.
the joint damping 0.5 has no source.

**why the hind legs never lift:** lifting a hind foot on these springs takes 4-8 nN.m (measured directly); the cord's hind levators deliver
0.00-0.20 on average (1.5 at the 95th percentile) where the middle legs' deliver 3.7-5.2 (12-18); the left hind leg has ONE trochanter
flexor in the map (the middle legs seven) firing at 0 Hz, the accessory trochanter flexors at 0, the depressors at ~9; the body keeps
loading the hind legs (38-68 % of the load, part of it the coxa on the floor; a lifted hind foot's coxa takes 6 uN and the leg still reads
5.5, so the load rows keep it in stance); **the hind coxa pitch, the joint he sinks through (+10 deg under his weight), has no motor
neuron mapped to it** (hind protraction and adduction both map to coxa yaw in `results/body_dof_signs.json`); and the hind leg's busiest
motor neurons (MNhl62 at 8-33 Hz, a promotor; MNhl59) are not in the joint table. the senses are not the difference (same counts as the
middle legs).

**the fix order (the reviewer's, agreed):** (1) the standing check and the foot load from the tarsal segments only, the coxa share reported;
(2) a muscle on the hind coxa pitch; (3) a start pose with all six feet down (at the neutral pose the front feet are 0.3 mm up and the hind
legs load first); (4) 0.14 relabelled as derived, the springs set from the sourced 2e-8 N.m/rad with the derivation shown; (5) then the
hind levators re-read with honest hind-leg load. none of this changes a neuron; all of it changes what the clips mean.

## the rhythm is the body's (12:56 PDT, 09-23; `--mn-poisson RUN` in `experiments/body_loop.py`: the muscle map fed Poisson spike trains at
each of the 373 leg motor neurons' own mean rate from `lift_s11` (2.12 Hz per cell), the cord running and logged but never reaching the
body; the full stack otherwise; seeds 11 / 12 / 13; the default path re-checked bit for bit after the restructure)

| arm | lf off / lifts / gap (cv) | lm | rm | lh, rf, rh | floor (old statistic) |
|---|---|---|---|---|---|
| the cord's spikes (`lift_s11`) | 22 % / 30 / 163 ms (0.46) | 69 % / 72 / 191 (0.32) | 46 % / 69 / 182 (0.29) | 7, 1, 0 lifts | 7 % |
| Poisson at the same rates, seed 11 | 28 % / 52 / 200 (0.26) | 79 % / 49 / 212 (0.29) | 62 % / 72 / 191 (0.31) | 1, 0, 0 | 4 % |
| seed 12 | 38 % / 68 / 189 (0.31) | 86 % / 40 / 224 (0.19) | 47 % / 67 / 192 (0.31) | 1, 1, 0 | 5 % |
| seed 13 | 40 % / 66 / 190 (0.30) | 85 % / 38 / 184 (0.30) | 50 % / 71 / 191 (0.32) | 2, 1, 0 | 5 % |

**random spike trains at the cord's mean rates make the same bouts on the same legs with the same 180-220 ms gaps at the same cv, three of
three.** the cord's timing plays no part; what the cord supplies is each motor neuron's mean rate, which is the posture (which legs
hang), and the body (springs at flygym's default, pads, the 120 ms twitch kernel, the floor) does the rest under a noisy drive. so, in
place: **the bouts are not a reflex, not the cord's rhythm, and not a rhythm of the connectome's at all; they are the body's, with the
connectome setting the tone.** the freeze control stands and reads correctly now: a frozen drive has no noise, so no bouts. "lifts in
bouts that need the cord's motor output" becomes "lifts in bouts that need a noisy motor drive at the cord's rates". the claims
reviewer's likeliest reading was right. what this leaves for the connectome: the posture (real: which legs he holds up under which
command, the lean, the tone), and nothing rhythmic yet. the campaign's coupling question dissolves with it (there was nothing to couple);
the rhythm question returns to the cord, where every arm since 09-21 has found the 20 Hz subnet line and no step. the record's honest
sentence for a stranger, today: a headless fly on a physics floor, driven by his own recorded brain, sits on his hind coxae with his
legs under him, and the legs twitch in bouts that any noisy drive at the same rates would make.

## his feet under him (13:02 PDT, 09-23; commit f1fb78e: the physics fix order as options, every default bit for bit: `--load-from leg|tarsi`,
`--hind-map v1|v2`, `--start-pose neutral|feet`, `--stiffness sourced` (= 20 nN.m/rad: 1 model unit = g.mm^2/s^2 = 1e-9 N.m, so 2e-8
N.m/rad = 20); the standing line now reads feet / other leg segments / body, saved per ms as `tarsal_force`, `other_leg_force`,
`body_force`; the full stack under the recorded command, seed 11, 30 s)

| | (a) as the clips were | (b) tarsal load, hind map v2, feet down | (c) + the sourced springs (20) | (d) as (c), DNg100 60 Hz |
|---|---|---|---|---|
| feet / other leg segments / body, uN of 10.05 | 4.39 / 4.84 / 0.69 | 6.34 / 2.89 / 0.43 | **9.65 / 0.29 / 0.03** | 10.04 / 0.02 / 0.00 |
| thorax height, mm (min) | 0.75 (0.50) | 0.70 (0.52) | 0.81 (0.57) | 0.84 (0.64) |
| tarsal load per leg (lf lm lh rf rm rh) | .55 .09 1.01 1.25 .18 1.30 | .87 .19 1.66 1.53 .26 1.84 | 1.40 .32 2.83 2.30 .55 2.24 | 1.32 1.25 2.34 2.06 1.04 2.03 |
| coxa-and-femur share over the run | 37-57 % | 18-42 % | 1-6 % | 0 % |
| lifts lm / rm (in-bout gap, cv) | 69 / 81 (188 / 194 ms, 0.30 / 0.25) | 52 / 58 (208 / 195) | 83 / 74 (176 / 174, 0.32 / 0.34) | 4 / 27 (194, 0.31) |
| lifts lh / rh | 8 / 1 | 5 / 8 | 0 / 0 | 1 / 1 |
| hind Tr flexor (levator) Hz per cell, lh / rh | 0.00 / 0.38 | 0.00 / 0.28 | 0.00 / 0.39 | 0.00 / 0.01 |

- **(a) is the honest reading of every clip nate has:** about half his weight on coxae, femora and tibiae (the left hind mostly), 4.4 uN
  on his feet, where the old line said "7 % on the floor". **(c) is him standing:** on the sourced springs, six tarsi loaded (1.3-2.8 uN
  each), the coxae and femora carrying 0.3 uN, 0.03 on his body, thorax at 0.81 mm; under the tonic neuron at 60 Hz (d) the coxa share
  is zero throughout. the settle before the warm-up (0.5 s of physics, no torque, pads off) is what puts the feet down; at stiffness 10
  the hind coxae still end on the floor (review P2), at 20 nothing but tarsi touches.
- **the bouts go on** on the middle legs at 175-210 ms in every arm (the body's, as the Poisson control says), and **the hind legs still
  do not lift with their coxa pitch driven and their load read honestly (0 / 0 in (c)): the hind levators (the trochanter flexors) are
  silent in every arm, 0.00 Hz on the left hind,** with MNhl62 (a promotor by A2, now on coxa pitch) at 25-31 Hz there. by the review's own
  test, that silence is the cord's, not the body's.
- the caveats the agent kept: moving the hind protract role to coxa pitch makes the protractors push the body up (MNhl62 at 30 Hz is part of
  why (c) sits higher than the passive settle); joining cells rescale their size-proxy groups; MNhl59, the largest and busiest hind motor
  neuron, stays unmapped (A2's low confidence); "sourced" is the printed number and on it he stands with no muscle at all, which the
  paper's headline (a fly cannot stand on passive stiffness) contradicts, so the spring's value is bracketed, not settled (ledger 21).
- clip: `world/body/loop/feet_c.mp4`.

**where the day ends.** he stands on his feet on the sourced springs with the connectome setting his posture; his middle legs twitch in
bouts the body makes; his hind legs never lift because the cord never drives their levators; nothing rhythmic is the connectome's yet.
the rhythm goes back to the cord with the body honest for the first time: the next arms are the cord's own, on this body.

## the levators, by leg (13:06 PDT, 09-23; nate: "bouncing... back and front legs fairly firmly planted, bit of a palsy"; the file's input
synapses per motor neuron by pool and leg, `brain_cord.npz` with `world/legmn.npz`)

| pool | front (cells / synapses per cell) | middle | hind |
|---|---|---|---|
| **Tr flexor MN (the levators)** | **15 / 486** | **14 / 4,938** | **6 / 1,494** |
| Acc. tr flexor MN | 6 / 151 | 4 / 589 | 12 / 163 |
| Tr extensor MN (depressors) | 4 / 2,491 | 4 / 1,920 | 3 / 1,471 |
| Sternotrochanter MN | 4 / 5,287 | 4 / 9,032 | 6 / 10,560 |
| Ti flexor MN | 10 / 773 | 10 / 2,327 | 17 / 1,192 |
| Ti extensor MN | 4 / 4,766 | 4 / 6,982 | 4 / 5,276 |
| all leg motor neurons | 133 / 1,916 | 116 / 3,219 | 124 / 3,056 |

the hind legs as a whole are wired like the middle legs (3,056 vs 3,219 synapses per motor neuron; 379 k vs 373 k synapses onto them),
so "the hind legs are underwired" is not it. **the levators are:** the middle legs' trochanter flexors carry 4,938 synapses per cell where
the front's carry 486 and the hind's 1,494 (from the same input types: IN21A010 +, IN19A008 -, IN21A015 -, IN19B012 +, IN13A010 -), and the
accessory levators 589 against 151 / 163. ten times the levator wiring in T2. **that is why the middle legs are the ones that lift and the
front and hind stay planted, in every arm since 09-21:** the file gives the middle leg's levators the drive and the others a tenth of it.
whether that asymmetry is the fly's (Harris 2015: activating the 19A hemilineage in headless flies made the T2 legs wave, and only T2)
or the tracing's (T1 and T3 leg neuropils less complete for these small cells) is not decidable from the file; it is the file's, and it is
what he does. the front and hind legs' levators have 6-15 cells each with a few hundred synapses: the depressors out-wire them three
to five to one, which is a planted leg. **the palsy is the middle legs' levators under a noisy drive on springs; the planted legs are
the file's wiring.** the honest-body arms (both labellings, the recorded population, DNg100 60 / 100, the five-DN population, rest, and
the Poisson drive at stiffness 20 and 50 as the bounce's characterisation) are running.

## the cord's commands on the honest body (13:24 PDT, 09-23; the new stack: `--load-from tarsi --hind-map v2 --start-pose feet --stiffness
sourced` on the full stack of record; 30 s, seed 11; the subnet, the pair and the levators logged at 1 ms; a lift from the tarsal force)

| command | feet / other / body, uN | thorax z (sd) | lf lifts | lm | rm | lh, rf, rh | subnet line | Tr flexor Hz |
|---|---|---|---|---|---|---|---|---|
| the recorded population, labels swapped | 9.69 / 0.32 / 0.02 | 0.81 (0.108) | 5 | 83 (176 ms) | 74 (174) | 0, 0, 0 | 7.0 Hz x16 | 1.5 |
| the recorded population, as printed | 9.70 / 0.29 / 0.02 | 0.84 | 4 | 50 (210) | 57 (187) | 0, 5, 0 | 3.2 x17 | 2.1 |
| DNg100 60 Hz | 10.09 / 0.02 / 0.00 | 0.84 | 4 | 4 | 27 (194) | 1, 0, 1 | 18.8 x32 | 0.8 |
| DNg100 100 Hz, swapped | 10.01 / 0.02 / 0.00 | 0.85 (0.089) | 0 | 7 | 71 (185) | 13, 1, 1 | 22.9 x47 | 1.3 |
| DNg100 100 Hz, as printed | 10.02 / 0.01 / 0.00 | 0.87 | 5 | 7 | 47 (194) | 4, 0, 3 | 19.1 x48 | 0.8 |
| the five-DN population | 10.02 / 0.02 / 0.00 | 0.85 | 0 | 16 (209) | 49 (205) | 3, 1, 0 | 21.6 x30 | 0.9 |
| rest | 10.05 / 0 / 0 | 0.83 (0.028) | 0 | 0 | 0 | 0, 0, 0 | - | - |
| Poisson at the cord's rates, springs 20 | 9.89 / 0.11 / 0 | 0.82 (0.083) | 2 | 77 (186, cv 0.31) | 68 (184, 0.35) | 0, 0, 0 | - | - |
| Poisson, springs 50 | 10.09 / 0 / 0 | 1.08 (0.034) | 2 | 64 (181, 0.33) | 80 (185, 0.32) | 0, 0, 0 | - | - |

- **he stands under every command** on the honest body (feet 9.7-10.1 of 10.05 uN, body 0.00-0.03), at rest without a twitch (thorax sd
  0.028 mm, no lifts), and the lifts are the middle legs' only (the front and hind 0-13 in 28 s, the levators at 0.8-2.1 Hz); the middle
  legs bounce under the recorded population (83 / 74 lifts at 175 ms) and under the tonic neuron the right middle mostly (27-71), which is
  the lean.
- **the bounce, characterised:** the Poisson drive makes the same middle-leg bouts at the same gap on springs of 20 and 50 (186 / 184 ->
  181 / 185 ms, cv 0.31-0.35): **the gap is not the springs',** so it is the twitch kernel's (120 ms, K = e^-t/20 - e^-t/7) under a noisy
  drive; the springs set only the bounce's amplitude (thorax sd 0.083 -> 0.034 mm, the height 0.82 -> 1.08) and the thorax's slow rock
  is 1.1-1.7 Hz in every arm. the palsy is the muscle model's time course seen through the springs. nate's word for it stands.
- **the cord on this body:** the 20 Hz subnet line under the tonic neuron and the population (19-23 Hz, x30-48), weak and low under the
  recorded standing command (3-7 Hz, x16); no alternation between the middle legs at any lag (xcorr <= 0.09); nothing rhythmic that the
  body did not make. the levators of the front and hind legs at ~1 Hz: the wiring (above) at work.
