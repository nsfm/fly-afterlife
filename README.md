# fly-afterlife

a whole-fly connectome (MaleCNS v1.0, male, brain + nerve cord, 162,517 neurons) run as a
spiking model, with a real optic lobe in front of it: a graded, connectome-constrained
visual system (flyvis) driving the spiking brain's own T4/T5 cells, on the compound eye's
actual geometry. a second fly (FlyWire, female) shares the room. the point is to give the
spiking fly senses it can act on, one at a time, and record what the wiring does with them.

the record is `docs/SEAM.md`. read its STATUS block first; several sections are superseded
by later ones and it says which. everything in it is measured on this machine or labelled
as a choice.

## layout

- `docs/SEAM.md` - the record: every experiment, result, withdrawal and decision, timestamped.
- `docs/ARCHITECTURE.md` - the refactor plan (body / world / receptors / effectors / brain / episode).
- `docs/physiology/` - literature briefs per sensory system: rates, time constants, drive rules, citations.
- `docs/figures/` - eye geometry and what the fly sees.
- `seam/` - the eye and the seam: `eye_geom.py` (geometry from the wiring), `omma.py` (ommatidium
  raytracer, compiled), `world_flyvis.py` (scene -> both eyes -> flyvis), `seam_v2.py` (flyvis ->
  LIF), `transplant.py` (flyvis physiology on the real per-cell optic lobe), `distill.py`
  (training the transplant against flyvis), `build_flywire.py` (the female brain). input tables
  (`flyvis_*.json`, `calib.json`, `pair_counts.csv`) live here; outputs do not.
- `world/` - the arena and the closed loops: `pair.py` (two brains in a walled room), `loop.py`
  (one brain: drum, bar, walk, blind, spin, forage), `fastlif.py` (the LIF step compiled with
  numba, spike-for-spike identical to `flysim.py`), `export_viewer.py` + `viewer_template.html`
  (the single-file viewer: human view, top-down map, both retinas, traces), `run_many.py`
  (fan configs across cores), the DN gain tables.
- `results/` - run outputs that are worth keeping (json, logs). npz episodes are not tracked.
- `scripts/ens/` - ensemble drivers.
- `attic/` - superseded scripts, kept because the record cites them.
- `ref/flybrain/` - the LIF engine (TheMrRaGe/flybrain, Shiu et al. 2024 constants), not tracked.
- `data/`, `flyvis_data/`, `brain_*.npz` - the connectome tables, the flyvis models, the built
  brains. not tracked; see "getting the data".

## running the room

```
uv sync
uv run python world/pair.py --seconds 60 --seed 3 --out world/room.npz
uv run python world/export_viewer.py world/room.npz - world/viewer_room.html "the room" 1
```

useful flags: `--proprio 100` (leg proprioceptors, tripod gait), `--her-albedo 0.5` (her
invisible: the control), `--wsyn-m 0.185 --wsyn-f 0.275` (synapse strengths corrected for
the EM volume, see the record), `--deterministic` (bit-identical reruns; flyvis on the GPU is
otherwise nondeterministic at 1e-6, which is enough to diverge a run), `--numpy-engine`
(the original step). the GPU needs `prime-run` on this laptop.

## getting the data

- MaleCNS v1.0 tables (Janelia, 2026): `data/body-annotations-*.feather`,
  `data/body-neurotransmitters-*.feather`, `data/connectome-weights-*.feather`.
- FlyWire v783: `data/flywire/neuron_annotations.tsv`, `proofread_connections_783.feather`.
- flyvis (Lappalainen et al. 2024): `flyvis_data/` via the flyvis package's download; the
  code sets `FLYVIS_ROOT_DIR` to it.
- the brains: `ref/flybrain/scripts/build_creature.py --whole` -> `brain_whole.npz`;
  `seam/build_flywire.py` -> `brain_female2.npz`.
- eye geometry: `seam/eye_geom.py` -> `seam/eye_geom.npz`; columns: `seam/columns_all.py`.

## status, in one paragraph

the eye's orientation is decided by anatomy alone. the spiking side of the seam is sound (an
ideal direction-selective input makes LPLC2 detect expansion); the bottleneck is the
direction selectivity any graded front end hands over. on flyvis model 000 he follows a
drum both ways, approaches dark posts, feels walls and pillars through his bristles, walks
at a pace read from his leg motor neurons, and, when she is the one dark object in a light
room, turns toward her weakly and meets her in most runs. his P1 cells fire to touch; song
is out of reach in this model. the male brain's synapse strengths are ~1.5x too strong for
the constants they were fit on (FIB-SEM vs ssTEM synapse detection) and are being
corrected; the architecture is being rebuilt around a receptor registry so the physiology
briefs can be applied one row at a time.
