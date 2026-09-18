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
ideal direction-selective input makes LPLC2 detect expansion); the bottleneck is the direction
selectivity any graded front end hands over. the male's synapse strengths are corrected for the
EM volume (FIB-SEM detects ~1.5x more synapses than the ssTEM the LIF was fit on), which put
his Kenyon cells at the sparsity they should have and made the drum follow 3 of 3 on model 000.
every typed sense sits at its physiological resting rate (the tonic floor), which woke his
central brain from 0.01 to 0.5 Hz and, it turned out, put the first walking command to sleep:
he walks now because DNg100 (BDN2) walks his cord as a dose, and his pace is read from his 373
real leg motor neurons against a standing tonus measured in that floor (the 699 "leg" set the
record used before 2026-09-17 included abdominal, wing and haltere motor neurons); he steers by
DNa02 through a running baseline, and the wind on his antennae turns him upwind; he feels walls
and pillars through bristle afferents that burst and adapt; in a lit room with a warm corner
and a second fly, he finds her five times in five minutes and spends 8% of the time on walls.
thermotaxis by walking is not in this model: warmth reaches his wing motor neurons before his
legs, though he turns more when warming. the garden (a textured floor, grass, leaves, a stone, a
fruit with a plume and sugar, a puddle, a sun) is his world now; he finds the fruit by sight. his P1 cells fire to touch; song is out of reach. the architecture is a receptor registry,
a body, a world, effectors and one episode loop, each ported bit-for-bit against a frozen
oracle; every physiology change since has been one run against the previous one, in the record.

## credits and licence

MIT (see `LICENSE`). built on: the MaleCNS v1.0 connectome (Janelia FlyEM / Google, 2026),
FlyWire v783 (Dorkenwald et al. 2024; Schlegel et al. 2024), flyvis (Lappalainen et al. 2024,
Nature), and the LIF engine from TheMrRaGe/flybrain with the constants of Shiu et al. 2024.
written by nyx, with nate.
