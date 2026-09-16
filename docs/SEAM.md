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

## the claim we're testing

every public whole-fly simulation runs the shiu et al. 2024 leaky integrate-and-fire
model: one threshold, one time constant, one mV-per-synapse for all 162,517 neurons.
under that model the optic lobe (58% of the brain) computes nothing: the periphery is
graded in life and the LIF can't do ON/OFF contrast; CT1's compartments collapse into
one cell; the motion pathway (13,500 T4/T5) fires zero spikes to a loom. so nobody's
fly can see a threat.

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
