# fly-afterlife

a fruit fly's whole nervous system, run as a spiking network and given a body, senses and a world.

the wiring is the male fly's connectome (MaleCNS v1.0, 2026: brain and ventral nerve cord, 162,517
neurons, six million synapses), run as a leaky integrate-and-fire model with the constants of Shiu et
al. 2024. in front of it sits a real eye: a compound eye raytraced on the measured geometry of the
same fly, seen through flyvis (Lappalainen et al. 2024), a graded, connectome-constrained optic lobe,
whose motion cells drive the spiking brain's own T4 and T5. behind it sits a body: his leg motor
neurons set his pace, his descending neurons and his horizontal-system cells steer him, his bristles
feel walls, his antennae smell, sense warmth, humidity and wind, his feet taste sugar. the world is a
room, a striped drum, a round dish, or a garden with a fruit in it. a second fly (FlyWire, female)
can share the room.

the point is to give the spiking fly senses it can act on, one at a time, and write down what the
wiring does with them: what works, what does not, and what had to be assumed to make it work at all.

## what he can do today (2026-09-18)

- stand, and walk in bouts of several seconds, on a walking command (DNg100) that moves his cord
  as a dose; his speed is read from his 373 leg motor neurons against the standing tonus of a
  brain in which every sense sits at its resting rate.
- steer by optic flow: the left-right difference of his horizontal-system cells turns him, with the
  sign that follows a rotating drum three seeds of three; he follows a wall by sight without touching
  it, and turns into the wind when it blows on his antennae.
- feel: bristle afferents that burst and adapt on contact with walls, a rim, pillars, another fly.
- halt: a descending halting neuron (DNg105) stops the cord against the walking command.
- eat: sugar on his tarsi latches a feeding state that holds the halt and silences the withdrawal
  reflex; satiety fills over seconds of feeding, releases him, and decays over minutes. beside a
  fruit he walks onto it in two seconds, eats until full, and leaves, three seeds of three. it is
  the first thing in him that outlasts its stimulus, and it is modelled as what it does, labelled.
- in a lit room with a second fly he finds her five times in five minutes; his P1 cells fire to
  touch; song is out of reach.

what he cannot do yet is written down too: `docs/TODO.md` is the list, and `docs/SCENARIOS.md`
is his own version of it, a day in the life of the fly as twenty test cases, written from his side.

## watch him

```
uv sync
uv run python world/pair.py --world garden --seconds 120 --no-female --wsyn-m 0.185 --wsyn-f 0.275 \
    --steer running --walk 100 --thermo rest --start 2.1,-1.2,180 --feeding 3 --satiety 8 --out world/meal.npz
uv run python world/replay_app.py world/meal.npz --scale 2
```

the first command runs him for two minutes in the garden, starting a body length from the fruit;
the second opens the viewer: his own raytraced view, his retina (dots per ommatidium, or a
panorama), a map with his trail, and the neurons that matter, scrubbing at any speed. press `?`
inside it. the same viewer plays the room, the drum and the dish. a run takes about four times its
own length on a laptop; `docs/PERFORMANCE.md` says where the time goes and how to shorten it.

## how it is built

`src/fly_afterlife/` is the stack, one layer per file: `receptors.py` (a registry of receptor
classes, each a set of cells, a transducer with its own time course, and a stimulus read from the
world; and the tonic floor that holds every typed sense at its resting rate), `body.py`,
`world.py` / `garden.py` / `arena.py` (the worlds: contacts, fields, what the eye sees),
`effectors.py` (how populations of neurons become turning, pace, halting, a feeding state),
`legs.py` (a leg model with muscle weights, used as a diagnostic), `frontend.py` (flyvis),
`wiring.py` (labelled corrections to the wiring, opt-in), `episode.py` (the loop). `seam/` is
the eye and the seam into the optic lobe. `world/pair.py` is the setup script with every flag
labelled; `world/fastlif.py` is the LIF step compiled with numba, spike-for-spike identical to
the reference; `world/run_many.py` fans runs across cores; `experiments/` holds the drum and the
benchmark scorer. `docs/ARCHITECTURE.md` explains the layering.

## how it keeps itself honest

- **the record.** `docs/SEAM.md` is every experiment, result, withdrawal and decision, timestamped,
  in the order they happened. wrong turns stay where they were made, marked; nothing is rewritten
  to look cleaner than it was. read its STATUS block first.
- **controls, always.** an invisible female for the approach test, the fruit toned like the floor
  for the vision test, the plume off for the smell test, the same run with a sense at rest for
  every sense that is live.
- **one change per run.** every physiology change is one run against the previous one, and a
  large effect from closing one small loop is treated as a bug until shown otherwise.
- **the oracle.** the loop is ported and changed against a frozen script; `scripts/oracle_check.sh`
  must reproduce four reference runs bit for bit after any change to the engine, the drive path
  or the defaults, and the record says when it did.
- **stand-ins are labelled.** where the physiology is a slow state this engine cannot hold (hunger,
  satiety, the walking state), it is modelled as what it does, with a flag, a source, and a
  sentence saying so. the same for corrections to the wiring.
- **outside reads.** `docs/physiology/` are literature briefs per sense, with the numbers used.
  `docs/MOTOR_REVIEW.md` is an independent review of the motor side that found the walking
  command asleep; `docs/BENCHMARKS.md` is the published locomotion statistics and datasets he
  is scored against (`experiments/benchmark.py`, calibrated on real flies first);
  `docs/LANDSCAPE.md` is who else runs a 2026 connectome in a body, and what they do better.

## getting the data

- MaleCNS v1.0 tables (Janelia FlyEM / Google, 2026): `data/body-annotations-*.feather`,
  `data/body-neurotransmitters-*.feather`, `data/connectome-weights-*.feather`.
- FlyWire v783: `data/flywire/neuron_annotations.tsv`, `proofread_connections_783.feather`.
- flyvis (Lappalainen et al. 2024): `flyvis_data/` via the flyvis package's download; the code
  sets `FLYVIS_ROOT_DIR` to it.
- the brains: `ref/flybrain/scripts/build_creature.py --whole` -> `brain_whole.npz`;
  `seam/build_flywire.py` -> `brain_female2.npz`. `ref/flybrain/` is TheMrRaGe/flybrain, the LIF
  engine, not tracked.
- eye geometry: `seam/eye_geom.py` -> `seam/eye_geom.npz`; columns: `seam/columns_all.py`.
- real flies for the benchmark: `scripts/fetch_opynfield.sh` (the Roman lab's open-field
  trajectories; their data, their licence, not tracked).

run outputs (`.npz` episodes) are not tracked; `results/` keeps the json and logs worth keeping,
`docs/figures/` the pictures, `attic/` the superseded scripts the record still cites.

## the honest caveats

the engine integrates the linear membrane exactly, as Shiu's Brian2 model does, since 2026-09-19; before that it used
forward Euler at 1 ms, which put every synaptic potential's peak 16% low, and the record's earlier numbers were
measured on that engine (their orderings hold, their values do not). he walks at about a third of a fly's speed by a scale choice made early; the benchmark carries a
time-rescaling control for it. the right side of his ventral cord is under-traced in the
reconstruction (about 15% less input than the left), which a bistable pair of interneurons
amplifies onto one steering neuron; the wheel now reads one synapse upstream of it. the optic
lobe's direction selectivity is the seam's bottleneck, and he cannot yet see a loom. nothing in
him persists but feeding. and every number in the record was measured on one laptop, with three
seeds where it says three.

## credits and licence

MIT (see `LICENSE`). built on: the MaleCNS v1.0 connectome (Janelia FlyEM / Google, 2026),
FlyWire v783 (Dorkenwald et al. 2024; Schlegel et al. 2024), flyvis (Lappalainen et al. 2024,
Nature), the LIF engine from TheMrRaGe/flybrain with the constants of Shiu et al. 2024, and the
physiology of a few hundred papers cited where they are used. written by nyx, with nate.
