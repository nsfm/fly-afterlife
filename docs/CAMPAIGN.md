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
   command, 2.7 with the load off (WITHDRAWN: those were the large, fast cells). DONE RIGHT 09-22 late: the graded labelling (small third
   slow), synapses AND membrane noise scaled by the resistance ratio (a new engine term), the standing senses: the small third fires at rest
   (1.2 Hz, three of three), the large third and the extensors do not. Azevedo's ordering; his 30 Hz is 25x away and is the cell's own (item 4).
2b. **reversal potentials.** LANDED 09-22 (44a16b8, dcfbf9f; `--syn-rev 70:-5:-5 --syn-rev-hold each`). the as-built `ach` hold loses inhibition
   fourteen-fold and runs the cord away; `each` holds every PSP at rest and shunts. it lifts the cells the winner held deep by 2-3 mV and halves
   the flexors when the senses are on; not the flexors' lever. **original note:** GABA-A and GluCl reverse near rest in the fly (`knobs.md`): inhibition is a shunt, not a current. the engine
   subtracts inhibitory current without limit, which is why fourteen-to-one inhibition parks the flexors where no threshold reaches them.
   an engine term: inhibitory (and excitatory) conductances to reversal potentials, off by default, oracle. NEXT, after item 2 lands.
4. **plateau potentials and rebound on named cells.** LANDED 09-23 (2aa78b7, `--pic`): a borrowed persistent inward current on the small tibia flexors
   gives 12 / 36 / 62 Hz at rest at three borrowed sizes with everything else at zero; Azevedo's 30 falls between the first two. ledger 9.
   the pair (09-23): plateaus + fatigue on both sides, with and without the shunt: the two sides fire TOGETHER (+0.2 to +0.4 at zero lag),
   no alternation at any lag to 2 s. the file's 13A / 13B pair is not a half-centre at its weights; the switch is not in its intrinsic properties.
5. **neuromodulation as a state.** DESIGNED AND PARKED 09-22 (`octopamine_state.md`): the leg octopamine cells EN00B008 get 62 synapses from
   DNg100 and 716 from DNp68; under DNg100 alone they are silent (0 Hz), so the state is zero in our arm. a DNp68 question; no fly magnitude.
6. **finish the senses.** MAPPED 09-22 (`world/leg_senses.npz`, `leg_senses_map.md`): every leg sensory cell by leg and modality. the floor and the
   body's load row were driving club / hook cells that are silent at rest (ledger 6). next: the floor by subtype; tactile on contact, hair plates
   from coxa angle, campaniform from rising load, clubs and hooks from motion, in the body loop.
7. **add connections.** OPENED 09-23 on the 19B -> 19A pathway (ledger 26): weight and drive sweeps on the cord and the honest body.
   also queued (nate): a puppet gait as a baseline, so the connectome's attempt has a "working" body to be measured against.
   nate (09-23): no full-brain runs until the cord steps on its own; "we know the body should have a walking reflex without the brain; we
   haven't provided it yet." the gap is the cord's. original: gap junctions; the flexor motor neurons' inputs where tracing is thin. a reason each time.
8. **the fitter,** bounded by 2-5's ranges, aimed at measured targets.

**the target, named 09-22 night (`docs/SEAM.md` "the campaign opens"):** the tibia flexors are silent because the 13A / 12B / 19A premotor
inhibitors, woken by the standing load and the command, hold the flexors and their excitors down and inhibit their own releasers (IN13A002
-> IN13B019, 2,279 synapses). the loser's side has no live excitation under tonic senses. so every item above is aimed at one thing: what
lets IN13B019 / IN13A006 / AN06B002 and the flexor excitors IN21A004 / IN03A004 win a half-cycle. read those cells, not the gait.

order: 1 tonight, 2 and 3 this week, then look. if the flexors wake and the 20 Hz drops toward 10 on sourced changes, the rest is earned.
if not, 4-7 are a claim about what the file is missing, and we say so.

## day two (09-23, opened 10:16 PDT)

nate, on the reversal clip: "still a bit twitchy but less chaotic, and he doesn't totally flip himself over. seems like progress." and on the
methods dig: "the field is less shy than we are." agreed, with the edit that the wrong answer still exists (fit until he walks). two threads:

- **4 (running).** the small flexors' own tone: a persistent inward current on the small third, borrowed parameters named, Azevedo's 30 Hz at
  rest as the check, three values of g reported and none tuned to hit it. engine term, oracle, one arm.
- **the command (running).** one tonic DN drives the extension side and knocks the honest body over. the walking command as a population,
  sourced (which DNs, what rates, tonic or phasic, which premotor side each favours); meanwhile the recorded whole-fly DN population
  (`--dn-playback world/record/dn_census_0922`) replayed on the honest body beside the tonic command and rest, both labellings.
- then both together on the body, both labellings, with clips.

**day two, closed (11:02 PDT).** item 4 landed (`--pic`): the small tibia flexors reach Azevedo's rate at a borrowed size, on the cord and on
the body, in his ordering, in both labellings; force per spike sourced (Azevedo 2020, eLife; tibia flexor only) and built (`--mn-force`); the
walking command sourced (tonic; no measured rates; DNg100 is the extension neuron) and its population arms switch nothing; the recorded
population and the five-DN population both stand the shunted body. **the switch is not in the premotor pair:** plateaus + fatigue on both
sides of the file's 13A / 13B pair, with and without the shunt, co-fire at every lag to 2 s. two withdrawals in place (the folded leg was
not the flexors' force; the fast-spike claim was wrong). **where the sourced moves end:** the two candidates left for a rhythm are (a) the
leg's movement senses closing on the body's own lifts, which is a read, not a term, and (b) stronger mutual inhibition than the file
has, which is item 7 and needs a source. nothing else on the list has a paper behind it.

**the lift read (09-23 afternoon):** done. lifts come in five-hertz bouts per leg, uncoupled across legs, present in every arm with an
unloaded leg including rest and the old fit; the hooks lead each lift because the leg is already moving, the subnet fires with the
unloading. **neural** (09-23, `--freeze-mn 15`: muscles frozen, every leg stops; the cord in the loop, the bouts continue). a per-leg reflex
oscillation at five hertz through the leg's senses, the first rhythm the connectome makes with its body and no fitted term. uncoupled
across legs (at most four legs lift; the right front and right hind never do); no gait yet.
**WITHDRAWN (09-23, review R1: the force was not read in the no-load arms; the no-senses arm steps too). the bouts need a NOISY MOTOR DRIVE at the cord's rates and nothing else: Poisson trains at each motor neuron's mean rate make the same bouts, three of three (`--mn-poisson`). the rhythm is the body's; the connectome sets the posture. was:** the load reflex. campaniform rows alone make the bouts; position and movement senses alone make none
(he holds all six feet up); no single sense is necessary, the load is sufficient. the stick insect's stance-swing transition on the fly's wiring.
the hinted middle-leg exclusion did not replicate (one seed); he leans right and the left legs co-lift. coupling: central in the fly
(Mendes 2013, Sapkal 2026's 19B commissurals onto 19A locals). LOGGED AND SILENCED: present, wired as described, nearly silent under
the recorded command (0.4 / 3.5 Hz), 3 / 12 Hz under DNg100 at 100; silencing them or their targets changes nothing. **item 7 now has a
named circuit and a source:** the 19B commissural -> 19A local pathway, underdriven at the file's weights. nate's call.

**the yardstick and the listening cord (14:45 PDT, 09-23).** nate on the kinematic replay: "a natural fly, walking at varied paces,
turning, pausing... the back legs genuinely do not lift much if at all, but do provide a push. the front legs... contribute a lot of the
pulling. the central legs are also pushing back and sweep a broad range... the fly is standing much more upright." on the refined puppet:
"no legs are providing enough backwards push, and he's hanging lower to the ground than the true fly." and his move: use the imposed
walking to drive the cord's senses and watch the motor neurons. built as `--kin-drive`: the living fly's kinematics move the body by
position control, every sense is computed from that moving body, the cord runs under its command, and its motor output is logged and
not applied. the read is phase-locking of each motor pool and each cited premotor cell to the imposed step, against a deaf control.
RESULT: the 13A inhibitors phase-lock to the imposed stance (and to the swing when the claw labels flip), vanish when the cord is
deaf; the levators, the tibia flexors and IN21A010 do not lock. the cord shapes a step's inhibition and not its excitation.

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
| 10 | 09-22 | the load row's rate: 15 Hz x (foot force / standing force), `--leg-load-hz` | no adult campaniform rate exists | a recorded rate |
| 11 | 09-22 | the claw's rate: `--claw-hz` 100 x |angle - 90| / 60 deg, and which class is which (row 1) | Mamiya's tuning is imaging; the scale is chosen | a recorded rate |
| 12 | 09-22 | the hooks' rate: `--hook-hz` 100 x velocity / 300 deg/s | chosen | a recorded rate |
| 13 | 09-23 | the hair plates: 30 Hz toward the coxa's limit (`--hp-hz`) | threshold angle unpublished | a recorded rate |
| 14 | 09-23 | touch: a quarter of each leg's bristles at 20 Hz on contact with a 5x onset burst; the burst restarts on every chatter of the force (review R5) | no adult bristle recording during contact | a recorded rate; a debounced contact |
| 15 | 09-22 | the pads: adhesion switched by contact force (`--adhesion contact`, gain 1 uN) | a fly's pads hold several body weights; the switching rule is ours | a pad model |
| 16 | 09-22 | the per-cell membrane-noise scale following the synaptic scale (`--size-noise`) | an assumption: equal current noise across sizes | a measurement of a slow MN's noise |
| 17 | 09-22 | the slow / intermediate / fast labelling by input-synapse third, pooled across all six legs (review R3: the left front and left middle get no slow cell) | no per-cell identity in the file | per-leg thirds at least; an identity |
| 18 | 09-22 | reversal potentials 70 / -5 / -5 mV re rest, held each (`--syn-rev`) | the reversals are larval numbers; the hold is a choice | adult central measurements |
| 19 | 09-23 | force per spike by class, the thirds as the classes (12 cells "fast" where the pool has one per leg) | Azevedo's numbers are the flexor's only | per-leg classes |
| 20 | 09-22 | the recorded DN population replayed in 100 ms chunks (`--dn-playback`) from a whole-fly run that was mostly standing | the only recording of his own command | a walking recording |
| 21 | 09-21 | the body's springs: the clips ran on flygym's default stiffness 10; the record's 0.14 "measured" was 10 / 70, a derivation (physics review); the joint limits +-45-70 deg with a stiff solref; joint damping 0.5 unsourced | no fly leg spring was measured here | the sourced 2e-8 N.m/rad (= 20) with the derivation shown; a damping source |
| 24 | 09-23 (resolved as an option: `--load-from tarsi`, the standing line from the tarsi; on the sourced springs 9.65 of 10.05 uN on the feet) | "he stands": the standing statistic counted thorax / abdomen / head only; the hind coxae sit on the floor carrying 45 % of him | a blind spot in the read | the check from the tarsi only, the coxa share reported (to do first) |
| 25 | 09-23 (an option: `--hind-map v2`; the hind levators stay silent, the cord's) | the hind coxa pitch has no motor neuron; MNhl62 / MNhl59 unmapped | the joint-role table was built from the front leg's map | a muscle on the hind coxa pitch from the hind leg's own motor neurons |
| 22 | 09-22 | the size CSV lives in the session scratchpad (`flex_graded_abs.csv`) | built ad hoc | `world/flex_graded.csv` in the repo (to do) |
| 23 | 09-23 | the noise scale, the plateau current and the thresholds together make the small flexors fire; an isolated cell at that threshold and noise fires 0.8 Hz alone (review R4) | the rest is a construction | a fly measurement of the slow MN's intrinsic rate |
| 26 | 09-23 | **item 7, approved by nate (13:35):** the synapses among Sapkal 2026's left-right coupling pathway (AN19B009, IN19B005 -> IN19A011 / 012 / 001 / 016, IN19B003) scaled x3-x30 by `--edge-scale`, and/or the commissurals driven at 20-50 Hz by `--drive`; on the cord and on the honest body | the pathway is named by a paper and present in the file, wired as described, and nearly silent under any command we give (0.4-12 Hz); Pugliese found it "insufficient to couple" at the file's weights; no fly measurement of its synaptic weight or its drive exists | a measurement of either; every number produced under this row is a fit and is reported as one |
| 27 | 09-23 | the muscle model: Azevedo's twitch kernel summed linearly per spike, clipped at +-60 nN.m, no fusion, no length-tension | the fly's twitch is sourced; its summation at 50-100 Hz is not, and a real fly's legs on this body walk at 11 Hz by position control where the muscle path cannot carry more than ~8 | a measured force-frequency curve for a fly leg muscle, or FlyMimic's Hill muscles on all six legs |
| 9 | 09-23 | a persistent inward current on the small tibia flexors (`--pic smallflex:G:3:3:50`), parameters from cockroach / locust motor neurons | Azevedo's slow cells fire ~30 Hz at rest partly on their own; no fly leg cell has the current measured; the file gives them 13-111 synapses | a fly measurement of the current; g is bracketed, not pinned |
| 7 | 09-22 | in the cord alone, the standing leg's afferents driven at chosen rates: the flexion-tuned claw class (as labelled) at 40 Hz, the six tactile types feeding the flexion side at 20 Hz | a standing fly's tibia is flexed and its feet touch the ground; no adult recording gives the rates | the body loop driving claw by angle (exists) and tactile by contact (to build) |
| 6a | 09-22 | the floor trimmed to campaniform + hair plates (+ claw) by `--drive TYPE:0` in the arms; the default in the code still drives all 580 | the engine agent holds `world/cord.py` | change the default once the edit lands; re-baseline |
| 6 | 09-16 | the standing floor (`floor_leg_proprio`, 580 cells at 15 Hz) drives every leg proprioceptor alike: 207 club and 61 hook cells that are silent in a motionless leg, and only 12 campaniform | there was no per-subtype map | `world/leg_senses.npz` (09-22): the floor on campaniform + hair plates + claw only; the body loop's load row on campaniform + untyped |
| 3 | 09-21 | the standing load as a tonic 15 Hz on the leg proprioceptors (`--leg-load-hz`) | the cord alone has no body to unload | the body loop (position + load) replaces it; on the body the load never lifts because the flexors never fire |
