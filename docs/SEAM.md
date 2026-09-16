# the seam: a graded optic lobe driving a spiking whole-fly connectome

status: working draft, 2026-09-16 00:10 PDT. everything below is either measured
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
- seam v1: drive all 55 types from `columns_all.npz`. LC4/LC6 come alive?
- per-eye mirrored render for lateral stimuli; then left vs right loom -> DNa steering.
- ensemble average over the 50 flyvis models.
- write it up.
