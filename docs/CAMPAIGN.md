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
2. **synaptic kinetics per transmitter.** one decay for every synapse now; ACh is fast, GABA and glutamate (inhibitory here) are slower and
   measured. one engine term, off by default, oracle. the bet for why the subnet runs at 20 Hz and not 7-15. *(agent C builds; agent B sources)*
3. **intrinsic properties per type.** thresholds and membrane time constants for slow / intermediate / fast motor neurons from Azevedo 2020,
   with a floor so no cell pins; the tibia flexors (37 small cells, 1,386 synapses each against the extensors' 5,674, silent at every dose under
   one uniform threshold) are the test. *(agent B sources; then one arm)*
4. **plateau potentials and rebound on named cells.** rebound is in the engine (off); plateaus are not. stick-insect walking runs on them.
5. **neuromodulation as a state.** octopamine on the walking circuits, from the VNC's own modulatory cells, as a gain on targeted synapses.
6. **finish the senses.** hair plates and campaniform fields as populations where the file's afferents are thin; FANC where MaleCNS is incomplete.
7. **add connections.** gap junctions; the flexor motor neurons' inputs where tracing is thin. a reason each time.
8. **the fitter,** bounded by 2-5's ranges, aimed at measured targets.

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
| 3 | 09-21 | the standing load as a tonic 15 Hz on the leg proprioceptors (`--leg-load-hz`) | the cord alone has no body to unload | the body loop (position + load) replaces it; on the body the load never lifts because the flexors never fire |
