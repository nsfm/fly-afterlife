# the seam: a graded optic lobe driving a spiking whole-fly connectome

> **STATUS (2026-09-16 03:10 PDT) - read this before the sections below, several of
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
> - **the bottleneck, named (partly):** the direction selectivity of the T4/T5 activity handed
>   to the LIF - from any single flyvis model, and from the transplant - is not clean
>   enough per position for LPLC2's layout to read expansion; edge polarity and edge
>   energy dominate. next: (1) ensemble-averaged flyvis T4/T5 as the input; (2)
>   subtracting the non-directional component was tried and does NOT rescue it (see
>   03:20); (3) train the transplant's pair strengths on the real
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

**choices:** IOA 5 deg uniform (no acute zone); azimuthal-equidistant wrap about an
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

## ENSEMBLE CHECK (2026-09-16 02:30 PDT) - the loom result does not generalize

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

**polarity control result (02:50 PDT), models 000 / 001 / 005, ipsilateral LPLC2:**

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

**LPLC2's receptive field is in the wiring (03:00 PDT).** synapse-weighted offset of
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

**ideal-input test (03:05 PDT), `seam/ideal_t4t5.py`.** left eye's own T4/T5 cells
driven with a perfectly direction-selective pattern (expanding ring: T4a/T5a fire behind
the centre, b ahead, c above, d below, rate 150 * |cos|; contracting: mirrored; flash:
all subtypes on a fixed ring for 200 ms; static: nothing). LPLC2_L over the second:
**expand 99, contract 13, flash 17, static 0**; expand holds 8-13 per 100 ms for the
whole second, contract and flash die within 200 ms. LPi_L fires equally for expand and
contract (2238 / 2240), so the discrimination is the dendritic layout, not inhibition.
the LIF's expansion circuit works on this wiring. every failure tonight was input-side.

**DS-only drive does not rescue it (03:20 PDT, `seam_v2.py --dsonly`).** subtracting
each subtype's sibling mean before driving (models 000 and 001, dark and bright, one
seed): 000 dark loom 7 / recede 1, bright 0 / 0; 001 dark 0 / 35, bright 10 / 18, right
4 / 30 and 27 / 54. the residual directional pattern from a single flyvis model is
too weak or too noisy at this eye's resolution for LPLC2's layout to read, and the
non-directional component was not the whole story. candidates for the morning:
edge speed (the ideal test fired at 150 Hz regardless; flyvis's T4/T5 have a speed
optimum and the ball's edge speed runs 0-100 deg/s over the second), ensemble-averaged
input, and per-position DS measured directly on the flyvis output for the ball
(does T4a fire behind the ball and T4b ahead, in flyvis's own numbers?).

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
