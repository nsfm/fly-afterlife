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
paper did not: PFL2's membrane is -3.00 mV with the goal ahead and -2.29 behind, more depolarised when he points
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
