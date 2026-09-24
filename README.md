# fly-afterlife

**we took the complete wiring diagram of a fruit fly's nervous system, every neuron and every
connection, and switched it on inside a simulated fly, to find out how much of a fly is in the
wiring.**

he has an eye that sees the way a fly's eye does, a body that feels the ground, antennae that smell
and feel wind, feet that taste. we give him a room, a garden, sometimes a second fly, and we watch
what his own neurons do with it, one sense at a time. when the wiring alone is not enough to make him
do something a real fly does, we fill the gap with what biology says should be there, and we write
down every such choice, why we made it, and what would let us take it back. the record keeps its
wrong turns.

the wiring is the male fly's connectome (MaleCNS v1.0, 2026: brain and ventral nerve cord, 162,517
neurons, six million synapses), run as a leaky integrate-and-fire spiking model with the constants of
Shiu et al. 2024. two tracks of work run on it.

**the brain track** gives the spiking fly senses he can act on, one at a time, and writes down what
the wiring does with them. in front of it sits a real eye: a compound eye raytraced on the measured
geometry of the same fly, seen through flyvis (Lappalainen et al. 2024), a graded, connectome-
constrained optic lobe, whose motion cells drive the spiking brain's own T4 and T5. his bristles feel
walls, his antennae smell, sense warmth, humidity and wind, his feet taste sugar. the world is a room,
a striped drum, a round dish, or a garden with a fruit in it. a second fly (FlyWire, female) can share
the room. on this track his locomotion is a *readout*: his leg motor neurons set a pace and his
descending and horizontal-system cells steer a point on a floor. that readout is a labelled stand-in
for a body, and it is what every result in `docs/SEAM.md` before 2026-09-21 rides on.

**the body track** replaces the readout with a body. the ventral nerve cord alone (the headless
preparation, `world/cord.py`) or the whole fly drives a NeuroMechFly v2 physics body (flygym 2.1,
MuJoCo) through its 373 leg motor neurons, on sourced springs, with the leg's own senses (claw, hooks,
hair plates, load, touch) computed from the moving body and fed back to the cord. the question is
whether the connectome's own cord makes a step. the honest answer as of 2026-09-23 is: he stands on his
feet, his legs lift, and the file at its weights does not make stance and swing. `docs/CAMPAIGN.md` is
that track's plan, its line (physics sourced; biology filled in where the connectome has gaps; every
compromise in a ledger with its source and its removal), and its ledger of thirty-one rows.

the point of both is the same: what works, what does not, and what had to be assumed to make it work
at all.

## what he can do today (2026-09-23)

on the brain track (unchanged since 09-18; all on the pace readout):

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

on the body track (`docs/CAMPAIGN.md`; the record from "the headless preparation" onward in `docs/SEAM.md`):

- **stand.** on sourced springs, with the load read from his tarsi and a feet-down start, six feet
  carry 9.7-10.1 of his 10.05 uN under every command we give the cord (his own recorded descending
  output, one tonic walking neuron, a five-neuron population). before 09-23 he sat on his hind
  coxae and the standing statistic could not see it (the physics review, `docs/REVIEW_PHYSICS.md`).
- **hear his legs.** with a living fly's recorded kinematics moving his legs by position control and
  the cord only listening (`--kin-drive`), the 13A premotor inhibitors phase-lock to the imposed
  stance and flip with the claw's sign; the flexor excitors and the hold side's own releasers lock to
  the swing at a hertz. both halves of a step's timing are in the file; the lift side fires at a
  hundredth of a step's rate.
- **lift, not step.** his middle legs twitch in bouts that random spike trains at the same rates
  reproduce (the body's, not the cord's); at a labelled gain on four swing-locked excitors five legs
  lift and he sinks; through Hill muscles at ten times FlyMimic's forces a scripted tripod steps at
  11 Hz with no lag and he hops. no arm of the connectome's own makes stance and swing, alternates
  two legs, or moves him forward past a millimetre a second. a real fly's legs walk the same body at
  10 mm/s, so the body is a fly's body and the gap is the cord's.
- **the solver** (`experiments/solver/`, `docs/SOLVER.md`) searches nine labelled gains on the named
  cell sets against the real fly's numbers. everything it writes is marked SOLVER; what it finds is
  the fly's own circuitry with nine gains set, a result under a ledger row, reported with its vector.

what he cannot do yet is written down too: `docs/TODO.md` is the list, `docs/WALKING.md` is the
plain-language page on the walking question, and `docs/SCENARIOS.md` is his own version of the brain
track, a day in the life of the fly as twenty test cases, written from his side.

## what senses are on, and how to turn them on

every typed sense in him sits at its resting rate by default (the tonic floor, `--floor`; `--floor-drop` takes rows out).
a sense is *active* when the world also modulates it. the flags are `world/pair.py`'s; the status table with cell counts,
resting rates and sources is `docs/SENSES.md`, and the per-sense to-do is `docs/TODO.md` §S. rule of the house: every
implemented sense on unless the run says why not, and every active sense has a control run with it at rest.

| sense | active by default? | turn it on | its control |
|---|---|---|---|
| vision, motion (T4/T5 through flyvis) | yes, every world | always on | her painted invisible, the fruit toned like the floor |
| touch, bristles | yes | `--bristle adapting` (default; `hold` is the old kernel) | `--bristle hold`, or a run with nothing to touch |
| taste, sugar and water on the tarsi | yes, in the garden | the fruit and the stone are domes he climbs (`--climb on`, default since 09-21): standing on the fruit is tasting it, and since 09-21 feeding is read from his own proboscis motor neuron firing (`--feed-read mn9`, default) rather than latched by a timer; the puddle is water; `--feeding 3 --satiety 8` lets taste latch the feeding state | a run without the feeding state |
| smell, the fruit's plume | yes, in the garden | on with the garden; `--antennae real` puts his antennae at a fly's spacing (default `wide`, the old geometry) | `--no-plume` |
| smell, her odour and his cVA | when she is present | drop `--no-female` | `--no-female` |
| wind on the antennae (Johnston's organ) | no | `--wind on` (`--wind-gate odour` gates it on a whiff) | `--wind off` |
| temperature (hot and cooling cells) | no (yes after the flip) | `--thermo rest`: the rows are on and read the world's temperature at his antennae, which in the garden is its own field (the sun patch, the shade, the water) and in the room a uniform 25 C; `--thermo field` adds the room's warm corner | `--thermo off` (rows silent) |
| humidity | not yet | the puddle is a field; the cells wait on a label audit | |
| contact pheromone (ppk23) | when she is present | a tap on her fires it | `--no-female` |
| leg proprioception | no | `--proprio <Hz>` (a tripod rule, diagnostic) | off |
| ultraviolet and colour (R7/R8) | no | `--uv` renders the UV retina for the viewer; `--uv-photo` drives his R7 (a negative result: photoreceptors are histaminergic, so spiking them inhibits) | `--uv` without `--uv-photo` |
| the compass | no; a labelled stand-in, not a sense | `--ring` (a heading bump from the sun's azimuth on his own ring cells) with `--goal <deg>`, `--goal-switch`, `--goal-wind` (the goal set upwind while a whiff is on him) and the graded readout `--goal-wheel-v 20 --goal-ema 5 --pfl2-walk --mirror PFL3,PFL2 --goal-null off` | the same run without `--ring`, or `--goal-wind 0` |
| gravity and slope (Johnston's organ, the leg load, the eye's horizon) | yes, in the garden | `--tilt on` (default since 09-21): on the fruit or the stone his body pitches and rolls with the surface, his eye sees the horizon move, gravity deflects his antennae onto the wind rows, and his weight shifts to the downhill legs | `--tilt off` |
| ocelli (a labelled stand-in on the interneurons: the photoreceptors are outside the imaged volume) | yes, in the garden | `--ocelli on` (default): the ocellar cells fire in the dark and go quiet under the sky, the L-neuron sign from life; three discs on his vertex in the viewer | `--ocelli off` |
| hearing, gravity, loom | not yet | see `docs/TODO.md` §S: nobody sings yet, the world is flat, the eye cannot yet see a loom | |

the garden run of record today: `--world garden --walk 100 --feeding 3 --satiety 8 --thermo rest` plus the compass line
above with `--goal-wind 4`; from the evening of 09-19 the real antennae, the wind rows and the satiety gate are the defaults,
so a run that lacks one says so (`--antennae wide`, `--wind off`, `--wind-sated off`). `--uv` is a viewer layer, opt-in.

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

## the body track: run him on a body

```
uv sync
# the cord alone, thirty seconds, DNg100 at 100 Hz, the standing floor on the cells that fire standing still:
uv run python world/cord.py --seconds 30 --seed 11 --walk 100 --floor standing --log-ms --out world/cord/run.npz
# the honest body stack (every flag a ledger row; the defaults reproduce the runs of record bit for bit):
uv run python experiments/body_loop.py --seconds 30 --seed 11 --walk 0 --dn-playback world/record/dn_census_0922 \
    --loop position+load --adhesion contact --senses v2 --size-from world/flex_graded.csv --size-thr 1 --size-gain 1 \
    --size-noise 1 --size-clip 10 --syn-rev 70:-5:-5 --syn-rev-hold each --pic smallflex:0.58:3:3:50 --mn-force azevedo \
    --load-from tarsi --hind-map v2 --start-pose feet --stiffness sourced --claw-labels 50flex --fps 30 --out world/body/loop/run
# the yardsticks: a real fly's kinematics on this body, and a scripted tripod through the same muscles (both labelled):
uv run python experiments/kin_replay.py --out world/body/loop/replay
uv run python experiments/body_loop.py ... --puppet tripod:5:0.6 --puppet-swing-hz 50 --puppet-stance-hz 25 --out world/body/loop/puppet
```

the body script writes a clip (`--fps`, `--playback-speed 0.2` for native slow motion) and the arrays
the readers use: `experiments/leg_pairs.py` (per-leg lifts, gaps, pair coupling), `experiments/lift_read.py`
(lift-triggered cell rates), `experiments/kin_drive_read.py` and `kin_lock_rank.py` (phase-locking to an
imposed step). the engine terms the track added, all off by default and each with its oracle pass:
per-transmitter synaptic decay (`--syn-tau`), reversal potentials (`--syn-rev`), a persistent inward
current on named cells (`--pic`), a per-cell noise scale, per-type thresholds and gains through a size
file. the reviews of the track are `docs/REVIEW_BODY_LOOP.md`, `docs/REVIEW_DAY_TWO.md`,
`docs/REVIEW_CAMPAIGN_DAY_TWO.md` and `docs/REVIEW_PHYSICS.md`; the sourced numbers are in
`docs/physiology/` (`knobs.md`, `force_per_spike.md`, `parameter_provenance.md`, `walking_command.md`,
`interleg.md`, `claw_and_13A.md`, `leg_senses_map.md`).

## how it is built

`src/fly_afterlife/` is the stack, one layer per file: `receptors.py` (a registry of receptor
classes, each a set of cells, a transducer with its own time course, and a stimulus read from the
world; and the tonic floor that holds every typed sense at its resting rate), `body.py`,
`world.py` / `garden.py` / `arena.py` (the worlds: contacts, fields, what the eye sees),
`effectors.py` (how populations of neurons become turning, pace, halting, a feeding state),
`legs.py` (a leg model with muscle weights, used as a diagnostic), `frontend.py` (flyvis),
`wiring.py` (labelled corrections to the wiring, opt-in), `episode.py` (the loop). `seam/` is
the eye and the seam into the optic lobe. `world/pair.py` is the setup script with every flag
labelled; `world/fastlif.py` is the LIF step compiled with numba (exact integration of the linear
membrane by default; the Euler engine that matched the reference spike for spike is kept behind a flag); `world/run_many.py` fans runs across cores; `experiments/` holds the drum and the
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
- **the ledger.** on the body track every compromise is a numbered row in `docs/CAMPAIGN.md` with what it
  was, why, and what would remove it; the readme's flags above are its rows.
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
him persists but feeding. the engine has no synaptic depression or adaptation, so a mutually excitatory pair of
descending neurons (DNg33) locked itself at 250 Hz and ran his flight motor while he stood; since 09-21 depression is on that
pair's synapses alone (`--std pair`, the engine's Tsodyks-Markram rule, a labelled two-cell correction in `docs/TODO.md` §P),
and depression on every synapse is the next refreeze. and every number in the record was measured on one laptop, with three
seeds where it says three. on the body track: the pace readout of the brain track is a stand-in for
the body and the two do not yet meet (the whole fly does not drive the physics body in the garden);
the standing is the sourced springs' as much as the cord's; the muscle model is a sourced twitch summed
linearly, and FlyMimic's Hill muscles disagree with Azevedo's force measurement by a factor of 4-40;
the claw's two classes are pinned by wiring at 85-90 %, not by a recording; the solver's output is a fit on
nine named gains, reported with its vector.

## credits and licence

MIT (see `LICENSE`). built on: the MaleCNS v1.0 connectome (Janelia FlyEM / Google, 2026),
FlyWire v783 (Dorkenwald et al. 2024; Schlegel et al. 2024), flyvis (Lappalainen et al. 2024,
Nature), the LIF engine from TheMrRaGe/flybrain with the constants of Shiu et al. 2024, and the
physiology of a few hundred papers cited where they are used; on the body track, NeuroMechFly v2 /
flygym 2.1 (Wang-Chen et al.) with FlyMimic's muscles (Ozdil et al. 2026) and its recorded fly kinematics
(Wang-Chen, Stimpfling, Azcorra & Ramdya 2026). written by nyx, with nate.
