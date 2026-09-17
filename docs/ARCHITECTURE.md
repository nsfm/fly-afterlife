# architecture plan: from a room script to a fly

status: proposal, 2026-09-16 23:15 PDT (nyx). nate asked whether the current architecture
holds up for a long-term effort at "relatively complete" sensory and behavioural support.
it does not. this is what to build instead, and how to get there without losing what works.

## what we have

`world/pair.py` (the room) and `world/loop.py` (single fly, six modes) are research scripts
that grew by accretion. each contains, inline: scene construction, body physics (walls,
pillars, contact), every sensory drive rule (`drive_hz[idx] = constant`), the flyvis chunking,
readout population definitions, steering and pace rules, calibration phases, logging, and the
npz schema. they share code by copy. constants live in expressions. the physiology docs
(`docs/physiology/`) now specify ~20 receptor classes with rest rates, evoked ranges,
adaptation kernels, direction gating, running-mean normalisation and state-dependent gates.
none of that fits the current shape.

tonight's bugs were architecture bugs: a tap-onset flag kept in the wrong loop; per-frame vs
per-chunk arrays confused twice; a "proprioceptive" index set that included halteres and wing
sensors; a head-on touch class that silently zeroed a reflex. none were about the fly.

what works and must survive: the compiled LIF step (`world/fastlif.py`, spike-identical to
flysim), the compiled ommatidium raytracer (`seam/omma.py`), the flyvis seam and its
calibrations, the eye geometry, the viewer, the deterministic mode, the doc discipline.

## the shape

six layers, each a module with one job and a small interface. dependencies point downward.

```
experiments/        scripts that compose the layers; ensembles; the record (docs/SEAM.md)
  episode.py        the chunk loop, logging schema, npz + viewer export, deterministic mode
    body.py         a physical fly: pose, speed, gait phase, six legs, body-part contacts
    world.py        scene primitives, walls, other flies, FIELDS (odour plume, temperature,
                    humidity, light), and queries: render(eye), field(pos), contacts(body)
    receptors.py    registry: receptor class -> connectome cells + transducer model
    effectors.py    registry: readout population -> body command (steer, pace, song, groom)
      brain.py      the LIF (fastlif) + optic-lobe front end (flyvis/transplant) + readouts
```

### body
one object per fly (male or female, same class). holds pose (x, y, heading), speed, a gait
generator (step frequency from speed, Wosnitza 2013; tetrapod below 5 BL/s, tripod above 10;
swing 20-45 ms; period floors at 60 ms), six leg phases, and a contact map keyed by body part
(head, antenna, each leg, wing, abdomen) rather than L/R. the body knows nothing about
neurons. the female uses the same body with a different brain.

### world
the scene as now (sky, ground, walls, pillars, spheres, drum) plus scalar fields sampled at a
point: odour (an intermittent plume, power-law whiffs, Gorur-Shandilya 2017), temperature,
humidity, airflow, light level. queries: `render(eye, pose)`, `sample(field, pos, t)`,
`resolve_contacts(body)` (holds bodies at surfaces and reports which body part touched what).

### receptors
the registry is the heart of the change. a receptor class is:

```
ReceptorClass(
  name="bristle",                 # one row of the physiology table
  cells=select(cls="mechanosensory_tactile", part=...),   # from the annotation table, by
                                                           # class / type / entryNerve /
                                                           # rootSide / receptorType
  transducer=Adapting(onset_hz=200, tau_ms=30, plateau_hz=(10, 25), gate="direction",
                      fatigue_tau_s=...),                  # the model, with its citation
  stimulus=lambda body, world: body.contacts[part],        # what world variable it reads
)
```

transducers are small stateful objects: `Tonic(rest, gain)`, `Adapting(onset, tau, plateau)`,
`Differentiator(rest, gain_dT, tau_peak)` (cooling cells), `WeberFechner(tau_mean)` (ORNs),
`Gait(phase, stance_burst)` (campaniforms encode dF/dt: burst at stance onset), plus explicit
gates for state-dependent suppression (hook FeCO during walking, Dallmann 2025) applied at the
drive, since Poisson receptors ignore their membrane in this engine. every constant carries
its source. adding a receptor is adding a row, not editing a loop.

the annotation table (`data/body-annotations-*.feather`) becomes the source of cell sets:
`entryNerve`, `rootSide`, `receptorType`, `somaLocation`. the six-leg map is the first
instance of this; it should be general.

### effectors
readout populations by name (DNa02_L/R, legMN by class if typeable, pC1, pIP10, ...), and the
labelled rules that turn spike counts into body commands: steering from DNa02 with a RUNNING
per-side baseline (Rayshubskiy: zero difference = zero turn), pace from leg-MN output with
the slow-MN 30 Hz standing rate accounted for, the touch reflex as a self-calibrated term,
song from pIP10. calibration phases (standing baselines, reflex gain) live here and run once
per brain configuration, cached by (brain file, w_syn, seed).

### brain
`FastFlyBrain` plus: the optic-lobe front end as a pluggable module (flyvis model N, the
transplant, or none), the receptor drive interface (`set_rates(cells, hz)` per 1 ms step,
not per 10 ms frame, so adaptation kernels at 30 ms are resolved), and a readout interface
(`counts(population)` from accumulated spike indices, per chunk). the synapse-strength
constant is a parameter of the brain configuration with its provenance (0.275 ssTEM; 0.185
FIB-SEM, Plaza 2025).

### episode
one chunk loop for every experiment: sensory step for each fly (world -> receptors -> brain),
brain steps, effector step (brain -> body), world step (bodies -> contacts), logging. the log
schema is explicit: `per_frame[...]` and `per_chunk[...]` are separate namespaces in the npz,
never mixed. deterministic mode is a switch. two brains step in threads (numba kernels can
release the GIL) once the loop is single.

## how to get there

not a rewrite. carve, port, verify, in this order:

1. **regression anchor.** run the current room with `--deterministic` for 30 s, seeds 3 and 4,
   at both the old and the corrected synapse constants. these four npz files are the oracle:
   the ported room must reproduce them bit for bit before any behaviour changes.
2. **receptors.py + the annotation selector.** port the existing drives as they are (150 Hz
   bristles, the tap burst, the gait rule, T4/T5 from flyvis) into registry rows. verify
   against the oracle.
3. **body.py + world.py.** move walls, pillars, contacts, her body, the scene builder. verify.
4. **effectors.py.** move steering, pace, reflex, song, calibration phases. verify.
5. **episode.py.** the loop and the log schema; `pair.py` and `loop.py` become thin
   experiments. verify. delete the duplicated code.
6. **then, one at a time, behaviour changes from the physiology docs**, each its own run
   against the previous: corrected synapse constants (and re-baseline); running-baseline
   steering; adapting bristles; campaniform stance bursts; cooling/hot cells and a warm
   corner; plume intermittency; P1-dependent LC10a gain; pCd persistence readout. the rule
   from the mechanosensation brief applies: a large effect from closing one afferent loop is
   probably a bug.

steps 1-5 are a day of work with the compiled engine (a 30 s deterministic room is ~2 min).
each verification is one command. nothing in the record changes until step 6.

## what this buys

- a receptor is a table row with a citation; the physiology docs map onto it directly.
- body parts, not L/R: head-on contact stops being a special case.
- fields in the world: temperature, humidity, plumes, light are the same kind of thing.
- one loop, one log schema, one calibration cache: the per-frame/per-chunk class of bug ends.
- both flies are the same body and the same episode with different brains and constants.
- the pi and the fpga ideas become "a different world" (webcam render) and "a different
  brain" (hardware step), not different scripts.

## what it does not fix

- the engine's receptors are Poisson sources that ignore their membrane, so presynaptic
  inhibition of afferents and efference copies onto sensory neurons (JO, Cheong 2024) can only
  be applied as gates at the drive. an engine change (driven cells with real membranes and an
  input current) is a separate, later decision.
- the optic lobe's fidelity (direction selectivity at the seam) is a modelling problem, not an
  architecture one. it stays on its own track.
- GPU nondeterminism in flyvis: `--deterministic` is a switch, not a fix.
