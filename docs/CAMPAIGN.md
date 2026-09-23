# the campaign: a body that stands up (opened 2026-09-22 22:35 PDT)

nate, tonight: *"we're not running a research lab. we're doing a task as honestly as we can for the love of curiosity. i'd like to see an
entity that i could reasonably call a fly; i wouldn't begrudge a fly an unusual motor neuron synapse. let's learn what we can, and more
importantly, let's play, and log our compromises as we do."*

so the line moves, on purpose, and this file is where it is written down. `docs/SEAM.md` stays the record of what was measured;
this is the plan and the ledger of what we changed on the fly to get there.

## the line, as of tonight

- **physics stays as accurate as we can make it.** gravity, springs, muscles, contacts: sourced, never tuned to the outcome.
- **biology is ours to fill in.** the connectome has wiring and nothing else: no time constants, no thresholds, no transmitter kinetics,
  no plateaus, no modulators, no gap junctions, no synapse under five. every one of those is a gap, and filling a gap is fair.
- **a signal is natural if there is a biological story for it,** unnatural if it is an algorithm wrapped around puppet neurons. a neuromodulator
  state driven by cells that exist is natural. a sine on the motor neurons is not.
- **per-type tuning to measured ranges is fair. per-neuron tuning is fair where somebody measured that neuron, and logged where nobody did.**
  a new connection needs a reason (a source, or a gap we can name), not a proof.
- **the objective is the line, not the knob.** a fitter may search inside the ranges above; its targets are measured things (Pugliese's
  7-15 Hz, Azevedo's rates, Sapkal's phases), never "did he walk."
- **every compromise gets a row in the ledger below,** with what it was, why, and what it would take to remove it. we revisit at the next
  connectome or the next paper that does this better.

## the action list, least to most drastic

1. **put the weak edges back.** DONE 09-22: the floor was ours (`--min-weight 5` in the build), the release has every edge; rebuilt as
   `brain_cord_all.npz` (3.5x the edges, 25 % more synapses); the cord baseline does not move on it. `docs/physiology/weak_edges.md`.
2. **synaptic kinetics per transmitter.** one decay for every synapse now. SOURCED 09-22 (`knobs.md`): ACh 4.5-6.7 ms and GABA-A 3.7-6 ms are the
   SAME speed in the fly; only glutamate (GluCl) has a slow number, ~300 ms, one larval trace, an upper bound. the term is built (agent C, oracle)
   and kept labelled; the "20 Hz drops to 7-15" bet is withdrawn before the test. a kinetics term must hold peak or charge and say which.
3. **intrinsic properties per type.** SOURCED 09-22: Azevedo 2020 gives the tibia flexor pool rest -48 / -60 / -68 mV and input resistance
   700 / 300 / 150 MOhm for slow / intermediate / fast, and **the slow cells fire ~30 Hz at rest** (ours 0.00). thresholds and taus unmeasured
   for any leg MN; extensors never recorded. RUN 09-22: every flexor at the slow rest (3 mV to threshold, x2.3 input): 0.14 Hz under the
   command, 2.7 with the load off; the cells sit far under rest because inhibition here hyperpolarises without bound. the target needs 2b.
2b. **reversal potentials.** GABA-A and GluCl reverse near rest in the fly (`knobs.md`): inhibition is a shunt, not a current. the engine
   subtracts inhibitory current without limit, which is why fourteen-to-one inhibition parks the flexors where no threshold reaches them.
   an engine term: inhibitory (and excitatory) conductances to reversal potentials, off by default, oracle. NEXT, after item 2 lands.
4. **plateau potentials and rebound on named cells.** rebound is in the engine (off); plateaus are not. stick-insect walking runs on them.
5. **neuromodulation as a state.** DESIGNED AND PARKED 09-22 (`octopamine_state.md`): the leg octopamine cells EN00B008 get 62 synapses from
   DNg100 and 716 from DNp68; under DNg100 alone they are silent (0 Hz), so the state is zero in our arm. a DNp68 question; no fly magnitude.
6. **finish the senses.** MAPPED 09-22 (`world/leg_senses.npz`, `leg_senses_map.md`): every leg sensory cell by leg and modality. the floor and the
   body's load row were driving club / hook cells that are silent at rest (ledger 6). next: the floor by subtype; tactile on contact, hair plates
   from coxa angle, campaniform from rising load, clubs and hooks from motion, in the body loop.
7. **add connections.** gap junctions; the flexor motor neurons' inputs where tracing is thin. a reason each time.
8. **the fitter,** bounded by 2-5's ranges, aimed at measured targets.

**the target, named 09-22 night (`docs/SEAM.md` "the campaign opens"):** the tibia flexors are silent because the 13A / 12B / 19A premotor
inhibitors, woken by the standing load and the command, hold the flexors and their excitors down and inhibit their own releasers (IN13A002
-> IN13B019, 2,279 synapses). the loser's side has no live excitation under tonic senses. so every item above is aimed at one thing: what
lets IN13B019 / IN13A006 / AN06B002 and the flexor excitors IN21A004 / IN03A004 win a half-cycle. read those cells, not the gait.

order: 1 tonight, 2 and 3 this week, then look. if the flexors wake and the 20 Hz drops toward 10 on sourced changes, the rest is earned.
if not, 4-7 are a claim about what the file is missing, and we say so.

## working habits

one change per run, controls beside every arm, both claw labellings beside every body result, the oracle before any engine commit, agents
on their own PIDs, no clock time typed by hand. opus agents carry the labour (literature, builds, sweeps) and leave durable documents;
the reads and the record stay mine.

## the ledger of compromises

| # | date | what | why | to remove it |
|---|------|------|-----|--------------|
| 0 | 09-21 | the headless cut keeps the descending neurons as driven inputs | a decapitated fly's DNs can be driven (Bidaye 2020) | a brain |
| 1 | 09-22 | claw labels reported both ways (as printed / swapped) | the file's label may be inverted for the tibia joint | a measured sign |
| 2 | 09-22 | edges under 5 synapses dropped at the build (brain_whole.npz / brain_cord.npz) | a build default of ours; the release has them | removed: `brain_*_all.npz` beside the originals; every run of record is on the floored file, and the cord baseline is the same on both |
| 4 | 09-22 | the leg's tactile afferents (SNta, 2,573 cells) driven at a rate as a stand-in for ground contact | the file's 13B-side excitors take 27 % of their excitation from them and nothing drives them; a standing fly's tarsi are on the ground | a contact model on the body; as a cord diagnostic it wakes the releaser to 2.5 Hz, not the switch |
| 5 | 09-22 | tibia flexor thresholds set per type from Azevedo 2020's resting potentials (slow 3 mV, intermediate 15, fast 23 to threshold), the slow / intermediate / fast labelling by size rank within the pool | measured rest per class; the labelling of which cell is which is inferred | a per-cell identity; and it did not wake them (see 2b) |
| 6a | 09-22 | the floor trimmed to campaniform + hair plates (+ claw) by `--drive TYPE:0` in the arms; the default in the code still drives all 580 | the engine agent holds `world/cord.py` | change the default once the edit lands; re-baseline |
| 6 | 09-16 | the standing floor (`floor_leg_proprio`, 580 cells at 15 Hz) drives every leg proprioceptor alike: 207 club and 61 hook cells that are silent in a motionless leg, and only 12 campaniform | there was no per-subtype map | `world/leg_senses.npz` (09-22): the floor on campaniform + hair plates + claw only; the body loop's load row on campaniform + untyped |
| 3 | 09-21 | the standing load as a tonic 15 Hz on the leg proprioceptors (`--leg-load-hz`) | the cord alone has no body to unload | the body loop (position + load) replaces it; on the body the load never lifts because the flexors never fire |
