# the weak edges put back (campaign item 1; 2026-09-22, written 22:39 PDT by agent A)

## where the floor was: ours, not the release's

- **the release is not thresholded.** `data/connectome-weights-male-cns-v1.0-minconf-0.5.feather` (male-cns.janelia.org download,
  columns body_pre / body_post / weight) has 151,856,684 edges, 311,833,243 synapses, **min weight 1**. edges by weight: 1 syn 94,185,919;
  2: 34,656,359; 3: 11,222,655; 4: 4,168,887; >=5: 7,622,864. 144.2 M of the 151.9 M edges (213.8 M of the synapses) are under 5.
  (the `minconf-0.5` in the name is the release's per-synapse detection-confidence cut, not a synapse-count floor.)
- **the floor is our build step:** `ref/flybrain/scripts/build_creature.py` line 76, `--min-weight`, default 5 ("drop connections below
  N synapses (default 5)"), applied at line 128 (`k = w >= a.min_weight`). `brain_whole.npz` was built with `--whole` and the default
  (README.md line 125). it is an inherited convention from the older creature build (the flysim.py docstring's "weight>=5 connectome
  threshold"), not a release property.
- **checked:** rebuilt with `--whole --min-weight 1`, the node table (bodyId, type, cls, sc, side, nt, sign) is identical to
  `brain_whole.npz`, and the new file's w >= 5 edges are `brain_whole.npz`'s pre / post / w exactly, in order. `scripts/build_cord.py`
  (v2) re-run on `brain_whole.npz` reproduces `brain_cord.npz` exactly.

## the files (new, untracked; the originals untouched)

- `brain_whole_all.npz`: `uv run python ref/flybrain/scripts/build_creature.py --data data --weights data/connectome-weights-male-cns-v1.0-minconf-0.5.feather --whole --min-weight 1`
- `brain_cord_all.npz`: `scripts/build_cord.py` v2 logic unchanged, pointed at `brain_whole_all.npz` (a scratch copy with only the in / out
  paths as arguments; the tracked script is not edited).

| file | cells | edges | synapses | min w |
|---|---|---|---|---|
| brain_whole.npz | 162,517 | 6,138,378 | 88,488,128 | 5 |
| **brain_whole_all.npz** | 162,517 | **25,120,209** | **122,181,879** | 1 |
| brain_cord.npz | 23,074 | 1,074,031 | 18,943,840 | 5 |
| **brain_cord_all.npz** | 23,074 | **3,778,510** | **23,701,822** | 1 |

the cord: edges x3.5, synapses +25 %. the v2 cut drops 1,189,432 synapses onto DNs from DN / ascending cells (1,012,026 on the >=5 file).
the engine loads 3,627,528 nonzero edges (1,051,471 before; modulatory presynaptic cells carry no current); the hemisphere balance factor
moves 1.086 -> 1.076.

**input synapses per cell** (mean over the type; excitatory / inhibitory by presynaptic sign; edges = distinct input edges per cell):

| type | n | cord (>=5): syn | +exc | -inh | edges | cord_all: syn | +exc | -inh | edges | ratio |
|---|---|---|---|---|---|---|---|---|---|---|
| Ti flexor MN | 37 | 1,386 | 786 | 599 | 59 | 1,578 | 912 | 663 | 162 | x1.14 |
| Ti extensor MN | 12 | 5,674 | 3,313 | 2,354 | 194 | 6,078 | 3,579 | 2,485 | 406 | x1.07 |
| Acc. ti flexor MN | 47 | 476 | 222 | 254 | 35 | 643 | 315 | 326 | 126 | x1.35 |
| IN17A001 | 6 | 8,884 | 4,900 | 3,972 | 216 | 9,411 | 5,191 | 4,190 | 510 | x1.06 |
| INXXX466 | 6 | 3,245 | 1,709 | 1,533 | 76 | 3,482 | 1,840 | 1,630 | 219 | x1.07 |
| IN16B036 | 6 | 1,303 | 892 | 406 | 70 | 1,668 | 1,122 | 531 | 277 | x1.28 |
| IN19A007 | 6 | 6,702 | 3,311 | 3,357 | 232 | 7,248 | 3,599 | 3,600 | 521 | x1.08 |
| IN09A002 | 6 | 7,393 | 5,137 | 2,254 | 218 | 7,934 | 5,475 | 2,443 | 507 | x1.07 |
| INXXX464 | 6 | 9,706 | 4,491 | 5,191 | 251 | 10,335 | 4,815 | 5,475 | 600 | x1.06 |
| IN03A006 | 6 | 3,925 | 1,416 | 2,463 | 146 | 4,436 | 1,667 | 2,705 | 446 | x1.13 |
| IN12B003 | 6 | 5,566 | 3,284 | 2,254 | 207 | 6,114 | 3,623 | 2,449 | 512 | x1.10 |

the weak edges roughly triple each cell's partner count but add 6-35 % of its synapses, at about the cell's existing E:I ratio. the tibia
flexors gain 192 synapses per cell (126 excitatory); they stay at about a quarter of the extensors' input.

## the runs (`world/cord.py --seconds 30 --walk 100 --brain brain_cord_all.npz --log-ms`, the v2_arms.sh log-types, seeds 11 / 12;
`world/cord/sweep/all_ctl{,_s12}.npz`; 14 s each)

**the 20 Hz read** (`v2_read.py`; per-cell rate, 2-60 Hz spectral peak, x band median, autocorrelation 40 / 70 ms):

| run | IN17A001 | INXXX466 | IN16B036 | IN09A002 |
|---|---|---|---|---|
| v2_ctl | 16.9 Hz, 19.7 x45 | 19.3, 19.7 x51 | 4.6, 20.0 x21 | 38.3, 19.7 x46 |
| v2_ctl_s12 | 16.7, 16.4 x29 | 19.0, 16.4 x32 | 4.4, 20.9 x11 | 37.3, 16.4 x32 |
| **all_ctl** | 16.9, 19.8 x37 | 18.9, 18.8 x37 | 4.3, 17.4 x14 | 38.0, 22.3 x38 |
| **all_ctl_s12** | 16.8, 20.0 x42 | 18.8, 20.0 x44 | 4.0, 21.1 x17 | 37.6, 20.0 x39 |

autocorrelations at 40 / 70 ms within +-0.04 in every run (no ring). the line stays at 17-22 Hz, x37-44 in IN17A001 (x45 / x29 on v2).

**gait score** (`experiments/gait_score.py`, the 423 logged cells):

| run | MN Hz | active | flex Hz | ext Hz | antag | legs | beat | beat leg/Hz |
|---|---|---|---|---|---|---|---|---|
| v2_ctl | 4.33 | 95 | 0.00 | 8.0 | -0.19 | +0.00 | 3.9 | L1/19.5 |
| all_ctl | 4.26 | 95 | 0.00 | 8.1 | -0.16 | +0.00 | 4.5 | R2/19.5 |
| all_ctl_s12 | 4.15 | 96 | 0.00 | 7.6 | -0.18 | +0.00 | 3.2 | L2/17.2 |

**the 373 leg motor neurons** (`world/legmn.npz` "leg", matched by bodyId through `brain_whole.npz`; frames after the 2 s warm-up;
the method reproduces v2_ctl's 1.84 / 52 exactly):

| run | Hz / cell | active (>1 Hz) | Ti flexor | Ti extensor | Acc. ti flexor |
|---|---|---|---|---|---|
| v2_ctl | 1.84 | 52 | 0.00 | 7.96 | 0.00 |
| v2_ctl_s12 | 1.78 | 53 | 0.00 | 7.80 | 0.00 |
| **all_ctl** | 1.80 | 52 | 0.00 | 8.10 | 0.00 |
| **all_ctl_s12** | 1.72 | 53 | 0.00 | 7.61 | 0.00 |

## what it says

putting back the 18.9 M weak edges in the whole file (2.7 M in the cord, +25 % of the cord's synapses) **changes nothing measurable in the
cord baseline**: leg motor neurons 1.84 -> 1.80 Hz per cell (seed 12: 1.78 -> 1.72), 52 active either way, the tibia flexors still 0.00, the
extensors 8, the loop cells' rates within 0.5 Hz, the 20 Hz line still there (19.8-20.0 Hz in IN17A001, x37-42 against x45 / x29). the
differences are the size of the seed-to-seed spread. the weak edges add input at each cell's existing E:I balance, which is why. **the floor
was not what keeps the flexors silent or sets the 20 Hz.** it is removed as a compromise either way: the `_all` files are the release's
wiring without our cut.

## what I could not determine

- whether the release's `minconf-0.5` synapse-confidence cut matters (a lower-confidence table was not in `data/`; not checked online).
- the node filter is a second, separate cut: `build_creature.py` line 89 keeps `status == "Traced"` and typed bodies (211,577 segments
  -> 162,517). the raw table's 311.8 M synapses fall to 122.2 M between kept bodies even at weight >= 1; the rest go to untraced or untyped
  fragments. how many of those would land on cord cells as real partners was not measured.
- the body loop (`experiments/body_loop.py`) and the rate model were not run on the new files.

**control on the code as run:** `world/cord.py` and `world/fastlif.py` carry uncommitted edits from another agent (the new engine term,
off by default) during these runs. v2_ctl re-run on the same working tree against `brain_cord.npz` gives frames bit for bit identical to the
stored `v2_ctl`, so the comparison above is the wiring alone.
