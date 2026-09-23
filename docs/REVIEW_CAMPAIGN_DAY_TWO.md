# review: the campaign's first two days, as a referee (SEAM "the campaign opens" to the end; CAMPAIGN.md; the physiology notes)

written 2026-09-23, an independent read. scope: `docs/CAMPAIGN.md`, `docs/physiology/{walking_review,knobs,parameter_provenance,
walking_command,force_per_spike}.md`, and `docs/SEAM.md` from "the campaign opens" to "the commissurals under a walking-rate command".
code read: `experiments/body_loop.py` (as it stood before commit 78cf104), `world/cord.py`, `src/fly_afterlife/receptors.py`,
`src/fly_afterlife/leg_senses.py`, `experiments/lift_read.py`. the saved body runs in `world/body/loop/` were re-read. new evidence is
fifteen short cord arms (20 s each). they and the scripts are in the session scratchpad (`.../scratchpad/rev2/`, `.../scratchpad/offfrac.py`).
no body arm was run. no project file other than this one was changed.

**overlap with `docs/REVIEW_DAY_TWO.md` (R1-R9), which landed while this was being written.** that code review found the unread force
(R1), the memoryless bout null (R2), the pooled thirds (R3), the built-in rest (R4), the touch chatter (R5), the 12 % campaniform (R6)
and the freeze's limits (R7). R1 is already withdrawn in place (SEAM "withdrawn in place", commit 78cf104). this review reached R1, R3, R4,
R6 and R7 independently (§ "what I ran", 1-2) and concurs with each. it does not repeat their arguments. **what is new here:** the sign
of the file's load pathway on the cord (§3), a second left-right asymmetry that is not R3's (§4), the claims table as a referee's,
the ledger rows, the one-seed hedges, and the withdrawals that R1 did not reach.

## verdict

the first night holds up, because it was withdrawn in place each time it was wrong: the floor on the wrong cells, "held far below
rest", the fast cells passed off as slow, the fold that was not the flexors' force, the coupling seen on one seed. the cord results
on the flexor chain are fair as written, with the caveats they already carry, and a few one-seed conclusions need the hedge written
into them. the afternoon's headline did not hold, and R1 has withdrawn it. what is left after R1 and R2 is a narrower result than
even the withdrawal says. the freeze shows the leg's movements need a time-varying motor output. no arm shows that output needs the
senses. no arm shows the cord makes a rhythm. every cord-side manipulation left the lift spacing at 150-240 ms, and the motor pools'
spectra are broadband. so the most economical reading is a cadence set by the body (springs, pads, gravity, the 20 ms twitch) under a
noisy drive. that is excluded by nothing yet, and it is cheap to test. two findings here bear on what comes next. (1) on the cord,
the file's load pathway as driven pushes the middle legs toward swing (protraction and levation up, remotion down, three seeds),
which is the opposite sign of the insect load reflex that "the stick insect's stance-swing transition" invoked. (2) the lean has at
least two candidate causes, not one. R3's right-sided flexor tone is one. The other is a pool-level left-right asymmetry that the
cord makes under a bilateral command with no size terms, no current and no shunt, and that mirror normalisation does not remove. on
the side questions: the small flexors' rest and the current are constructions with sources (R4 agrees), "Azevedo's ordering" is
assigned, and the body's 35 Hz is calibration, not agreement. the ledger is missing about a dozen of the day's compromises.

## what I ran, and what it shows

**1. the no-load arms never read the force (= R1).** `leg_force` max is 0.0 in `loop_position`, `loop_hookonly` and `lift_s11_nosense`,
against 50.8 in `loop_loadonly` and 40.4 in `lift_s11`. without the load row, the load cells also sit at the floor's tonic 15 Hz (R6),
and the pads, which follow F under `--adhesion contact`, never grip.

**2. the legs keep the cadence with the loop open (concurs with R1's foot heights by another route).** trochanter levation angle
from the saved joints (the body's own role map). peaks of >= 5 deg prominence at 10 ms, after the warm-up:

| arm | lf peaks / in-bout gap | lm | rm |
|---|---|---|---|
| `lift_s11` (all senses) | 76 / 185 ms | 81 / 200 | 160 / 140 |
| `lift_s12` | 84 / 220 | 89 / 170 | 158 / 140 |
| `loop_loadonly` | 79 / 175 | 84 / 185 | 152 / 150 |
| `abl_load` (load at 0, the rest on) | 68 / 220 | 88 / 190 | 160 / 150 |
| `loop_position` (load clamped at 15 Hz) | 88 / 200 | 83 / 190 | 153 / 150 |
| `loop_hookonly` | 87 / 195 | 94 / 190 | 154 / 150 |
| `lift_s11_nosense` (`--loop off`) | 93 / 200 | 86 / 200 | 151 / 150 |
| `lift_s11_freeze15`, after the freeze | angle sd 0.00 on every leg | | |

the leg MN pools' spectra (10 ms frames; the 3-8 Hz share of 0.5-50 Hz, flat = 0.10) are 0.07-0.21 with the loop closed and 0.07-0.17
open. the motor output is broadband either way, as R2 found.

**3. the cord alone, under a constant load, does not oscillate, and the load pushes the middle legs toward swing.** the full stack on
the cord: `--floor standing --hp-hz 0`, `--syn-rev 70:-5:-5 --syn-rev-hold each`, `--pic smallflex:0.58:3:3:50`, the graded size CSV
with gain / thr / noise 1, DNg100 60 Hz. the campaniform + untyped rows stepped from 0 to 30 Hz, seeds 11 / 12 / 13:

| pool, Hz per cell (by the file's type names) | load 0 | load 30 |
|---|---|---|
| lm promotor / remotor | 0.1-0.2 / 5.6-6.3 | 5.6-6.3 / 1.9-2.0 |
| rm promotor / remotor | 0.6-0.8 / 0.9-1.2 | 5.8-7.2 / 0.3-0.4 |
| rm trochanter levator | 0.8-0.9 | 2.8-3.0 |
| lh promotor / remotor | 5.2-5.9 / 1.6-1.7 | 4.8-5.1 / 3.0-3.2 |

no pool has excess 3-8 Hz power at any load (0.06-0.14). at rest (no command) the load raises the middle promotors too (lm 0 -> 3.2
Hz). **on the middle legs, the file's load pathway as driven excites protraction and levation and suppresses remotion.** that is
negative feedback onto stance, the opposite sign of the insect load reflex (campaniform load reinforcing stance and delaying swing).
the hind leg goes the insect's way. caveats: the load is tonic and on all six legs at once, 98 of the 111 cells are `untyped` (R6),
and it is one dose.

**4. two left-right asymmetries, not one.** the cord at load 15, DNg100 60 Hz, no body:

| pool, L / R Hz per cell | full stack s11 / s12 | no size terms, no current, s11 / s12 | and no shunt, s11 | full stack + `--mirror vnc`, s11 / s12 |
|---|---|---|---|---|
| middle remotor | 4.3 / 0.5, 4.2 / 0.8 | 4.3 / 0.5, 4.1 / 0.8 | 5.3 / 1.3 | 4.3 / 0.9, 4.2 / 1.0 |
| middle levator | 0.0 / 1.6, 0.1 / 1.8 | 0.0 / 1.6, 0.1 / 1.7 | 0.4 / 3.1 | 0.0 / 1.9, 0.0 / 2.0 |
| hind tibia extensor | 0.3 / 3.7, 0.4 / 3.8 | 0.3 / 3.7, 0.3 / 3.8 | 0.2 / 6.8 | 0.3 / 4.1, 0.4 / 4.7 |
| hind promotor | 6.0 / 1.8, 6.5 / 1.9 | 6.0 / 1.8, 6.1 / 1.7 | 4.9 / 1.7 | 6.1 / 2.8, 6.1 / 2.6 |
| all leg MNs | 1.71 / 2.42, 1.72 / 2.46 | 0.81 / 0.82, 0.80 / 0.85 | 1.40 / 1.38 | 1.71 / 2.46, 1.72 / 2.53 |

the whole-population difference is R3's: remove the size terms and the current and it goes (0.81 / 0.82). the pool-level differences
are not R3's. they are identical to the digit without the size terms, they persist without the shunt, and mirror normalisation of the
cord's input weights leaves them in place. so under a bilateral command, the cord drives the left middle leg toward remotion and the
right middle leg toward levation, and the right hind toward tibia extension, with no body in the loop. which of the two makes the
body lean is untested.

**a correction to the brief's premise (c).** in the load-only arm the floor did not act. the per-leg load rows are registered after the
floor on the same 111 cells, and `Registry.apply` lets a later row overwrite an earlier one, so under `load` the cells run at 15 x
clip(F / F_stand, 0, 2) and at nothing else. it is the arms WITHOUT the load row where the floor's 15 Hz stands, as a clamp (R6).

## the claims

| # | claim (as the record puts it) | evidence | controls | verdict | the experiment that settles it |
|---|---|---|---|---|---|
| 1 | the small tibia flexors fire at rest "in Azevedo's ordering" (noise scale k = 1: 1.15 / 1.18 / 1.30 Hz; body 0.68-0.75) | cord 3 seeds; body 1 seed per labelling | swapped claw classes; floor as built; k = 2 marked a fit | **supported-with-caveat** as a rate, and a construction (R4). **overclaimed** as an ordering: the rest, gain, noise and current were given to the small third only, so the ordering is assigned. the only arm with identical cells (every flexor at the slow rest) recruited the LARGE third first (38.7 vs 0.0 Hz), the reverse of the size principle | every tibia flexor given the same membrane: does small-first recruitment emerge from the file's inputs? thirds ranked within each leg (R3) |
| 2 | a borrowed persistent inward current gives 12 / 36 / 62 Hz, "not tuned to it"; on the body "Azevedo's slow-flexor rate, on him" | cord and body, one seed each | g = 0; the middle and large thirds and the extensors stay at 0 | **supported-with-caveat** on the cord (a statement about g, R9). on the body it is **calibration, not validation**: g 0.58 was carried forward because it sat nearest the target, so 35 Hz cannot then be cited as agreement. ledger row 9's "fire ~30 Hz at rest partly on their own" goes past the source: MLA lowers the rate and does not abolish it, and the remainder is unassigned (muscarinic, electrical and intrinsic are all open) | say "calibrated to Azevedo" and hold out a different target (his slow cells' EPSPs or rate under passive extension) |
| 3 | reversal potentials: "the shunt is what keeps him up under a command" | body 7-8 % vs 86-94 % on the floor | both labellings | **supported-with-caveat**: one seed per arm; -5 mV and hold `each` are choices | seeds 12 / 13; reversal at -10 / -2 mV |
| 4 | force per spike: the fold was not the small flexors' force | code (f_w already 0.003-0.06); four arms | uniform vs azevedo | **supported**; 55 -> 8 % is one seed and marked | none |
| 5 | the command as a population "switches nothing" | cord, six arms | rest; matched drive | **supported** for the reads made; one seed, unhedged | seeds 12 / 13 |
| 6 | the 13A / 13B pair is not a half-centre at the file's weights; "the switch is not in the premotor pair" | plateaus x fatigue x shunt, xcorr to +-2 s | one-sided plateaus show the reciprocity is real | **supported-with-caveat**: SEAM says one seed, CAMPAIGN's closing line drops it; tested only the pair's intrinsic properties at borrowed sizes | seeds; the pair at 1.5x mutual inhibition as a labelled diagnostic |
| 7 | lifts come in bouts, "five hertz, regular" | three runs | a Poisson null | "in bouts" **supported** as description. "regular" **withdrawn by R2** (a memoryless touchdown gives the same) | R2's nulls beside every bout claim |
| 8 | the freeze: "the per-leg five hertz is neural: a reflex oscillation through the leg's own senses and the cord" | `--freeze-mn 15`, seeds 11, 12 | the pre-freeze run is identical | **half supported** (R7): the body has no self-sustained oscillation under a constant torque, so the movement needs the motor output. it says nothing about the senses or about the cord's circuitry being specific. the MN spikes were not logged after the freeze | log spikes through the freeze; the Poisson surrogate (next steps, 1) |
| 9-11 | `--loop off`: "a leg that cannot feel itself does not step"; "the sum of them is [necessary]"; "the load reflex is the oscillator ... the load is sufficient" | the no-load arms | none valid | **unsupported (artifact)**; withdrawn in SEAM by R1. "no single sense is necessary" stands, one seed. load is not necessary either (`abl_load` bouts) | the re-runs R1 promised, seeds 11-13 |
| 12 | "the stick insect's stance-swing transition on the fly's wiring"; "load on a foot -> the cord extends the leg into stance" | analogy | none | **unsupported, and the cord points the other way** (§3): load drives the middle legs toward swing, 3 of 3 seeds | trace the load -> promotor path per leg; one leg's row stepped alone |
| 13 | "six oscillators, uncoupled" | lift statistics at independence (3 runs) | the independence product | **overclaimed**: rf and rh never lift in any day-two arm (0-2 % off) and lh only sometimes, so at most four legs bout. "uncoupled" is true and uninformative if each leg is its own mechanical response to independent noise | after R1's re-runs: count only the legs that move; the surrogate test |
| 14 | "the first sign of coupling" withdrawn; "he leans right ... that is a posture, not a coordination" | seeds 11-13 at 60 / 100 Hz | independence | the withdrawal is **correct**. the lean's **presence is supported**, its **cause not identified**: two candidates (R3's thirds; §4's pool asymmetry in the cord alone) | the body with thirds within legs; then the body with the cord's left and right leg outputs swapped |
| 15 | the commissurals are "present, wired as described, nearly silent"; "silencing them or their targets changes nothing" | logged 0.4 / 3.5 Hz; silenced on seeds 11, 12 (targets on 11) | the independence statistic | logging **supported** (the dose arms: one seed, unhedged). silencing a cell that fires 0.4 Hz tests nothing, so "changes nothing" is **uninformative, not negative**. "Pugliese found the same cells 'insufficient'" is **unverified**: their sentence says "several VNC neurons", unnamed (`interleg.md`) | silence them under DNg100 100 Hz, where they fire 3 / 12 Hz, seeds 11-13, after the legs move symmetrically |
| 16 | "item 7 now has a named circuit and a source: ... underdriven at the file's weights" | the dose logging | none | fine as a plan, **overclaimed** as a finding. "not the strong commissural drive Sapkal describes": Sapkal's is a connectome motif with no rates, so there is no measured drive to fall short of | a rate, when one exists; until then a hypothesis |
| 17 | the hooks lead each lift; "the trochanter extensor motor neurons (the levators) up" | lift-triggered averages | baseline | **supported**, mislabelled: in `body_loop.py`'s `ROLE` and `results/body_dof_signs.json`, Tr extensor is `levate -1`, a **depressor** | re-label; re-read with R2's levator result beside it |
| 18 | CAMPAIGN: "the first rhythm the connectome makes with its body and no fitted term" | 8 | 8 | **unsupported as stated**: no term was fitted to the rhythm, but the rhythm is not shown to be the connectome's, and the stack carries calibrated terms (PIC g, alpha 1.2) | next steps, 1 |

## the withdrawals: were they complete?

in SEAM, R1's entry covers claims 9-11 and the named reflex. what still stands elsewhere without its withdrawal:

- `CAMPAIGN.md`, "the lift read": "**neural** (...). a per-leg reflex oscillation at five hertz through the leg's senses, the first rhythm
  the connectome makes with its body and no fitted term." R1's "WITHDRAWN" marker sits on the next paragraph ("named") and not on this one.
- `CAMPAIGN.md` item 2b, "original note": "which is why fourteen-to-one inhibition parks the flexors where no threshold reaches them."
  withdrawn in SEAM ("held far below rest": -1.53 mV, sd 0.24). it needs the pointer.
- `CAMPAIGN.md`, "the target, named 09-22 night": "the tibia flexors are silent because the 13A / 12B / 19A premotor inhibitors, woken
  by the standing load and the command, hold the flexors ...". corrected in SEAM "the floor trimmed" ("under an honest standing floor
  the half-centre is not locked, it is quiet on both sides"). it needs the pointer.
- `CAMPAIGN.md` item 3: "Azevedo's ordering; his 30 Hz is 25x away and is the cell's own (item 4)". per R4 and claim 1, the ordering is
  assigned, and "the cell's own" is not established.
- SEAM "the load sweep" ("the standing load is half of what holds the flexors") and the three "layer above" entries were superseded by
  "the floor trimmed" and carry no forward pointer.
- SEAM "the small flexors' current on the body": "(the gain from Azevedo's FAST tibia extensor spike)". Azevedo measured the flexor; the
  withdrawn paragraph still has the wrong word.
- SEAM "the body's senses, read before editing" is corrected by "corrected in place: the claw's side at the standing pose". that is
  fine, but the original sentence carries no marker.
- `docs/physiology/interleg.md` line 3: "the lift read left six five-hertz reflex oscillators, one per leg, each closed through its own
  senses and the cord". written before R1, and now wrong on all three counts (six, reflex, closed through its senses).

## ledger rows to add

| # | what | why | to remove it |
|---|---|---|---|
| 10 | the body's load row: 15 x clip(F / F_stand, 0, 2) Hz on each leg's campaniform + untyped (13 + 98 cells); F raw each ms; no dF/dt; F_stand = weight / 6 | no adult fly CS rate exists; the gain and the clip set the loop gain of any load feedback | a CS encoder (Zill 2025, Custodio 2026: force and rate terms); the untyped split by modality |
| 11 | the claw on the body: 100 Hz x \|femur-tibia - 90\| / 60 deg by class, with the 90-deg null on every leg | Mamiya 2018 gives the tuning in one leg; the rate and the linear 60-deg range are ours | Mamiya's curves per leg; a rate |
| 12 | the hooks: 100 Hz at 300 deg/s, with no presynaptic suppression during walking | no rate measured; Dallmann 2025 suppress hook input during walking via 9A, which the loop omits | a suppression term from the 9A cells in the file |
| 13 | the hair plates: 30 Hz x the coxa pitch's fraction of the way to its +-45 deg limit, either direction, both types alike (R9) | Pratt 2026: limit detectors, threshold unpublished; the limit is the model's coarse range | per-plate thresholds |
| 14 | touch: a seeded quarter of each leg's tactile cells at 20 Hz on contact (F > 0.05), x5 for 30 ms at touch-down (and ~100 Hz in practice, R5) | a foot on the ground touches; no adult rate | a debounced contact; a sourced rate |
| 15 | the pads: `--adhesion contact`, gripping while the foot's force is over 0.05 | the ltm MNs are unwired in the file; on every day-two body arm | the ltm wiring, or a sourced pad model |
| 16 | the membrane-noise scale k = 1 (x2.33 on the small third) | equal current noise across sizes is an assumption; the engine noise is white | a measured noise spectrum in a leg MN |
| 17 | the graded labelling: input-synapse thirds pooled over six legs; the small third given the slow rest, gain x2.3, noise x2.33, the current; the CSV's x0.47 / x0.30 on the other thirds (R4) | Azevedo's classes are genetic and anatomical, ~1 : 2-5 : 8-9 per leg; the pooled thirds give none on lf / lm (R3) | within-leg ranking; a FANC / MaleCNS match of Azevedo's drivers |
| 18 | reversal potentials +70 / -5 / -5 mV re rest with `--syn-rev-hold each` | knobs.md says "near rest" (larval MNs); -5 and the hold are choices | a fly central E_Cl |
| 19 | `--mn-force azevedo` by pooled third; the slow class on a 20 ms twitch it does not have; f_w x 1.0 on every other pool | force_per_spike.md; the slow factor may be 10x low | the slow kernel (tau 0.2-0.5 s); FETi + SETi |
| 20 | the lift read's command: the whole fly's recorded DN output (a model's rates, (D)), in 100 ms chunks | walking_command.md §1b; a 100 ms chunk carries nothing above 5 Hz | a sourced population; state the chunking beside every playback result |
| 21 | the body's passive mechanics: default joint springs, the +-70 / 50 / 45 / 40 deg limits "coarse first cut" (E), stiff-limit solver settings, the 7 / 20 ms twitch cut at 120 ms, gain 42, sat 10, alpha 1.2 | the prime candidates for the ~200 ms cadence; the line says physics is sourced, and several of these are not | Karashchuk 2021 ranges; a measured passive stiffness; the twitch per class |
| 22 | every day-two arm of record reads `--size-from` from a CSV in a session scratchpad under /tmp | the runs cannot be reproduced from the repo | commit the CSV or its generator; point the runs at it |

also: the ledger's numbering skips 8, and rows 3 / 6 name the body's load row as the fix without recording its own chosen numbers
(row 10 above). the commissural arms' seeds belong in their entry rather than the ledger: silencing on 11 and 12, the targets on 11,
the dose logging on 11.

## sentences to soften or withdraw, quoted

already withdrawn by R1 in SEAM, and to be carried to CAMPAIGN (see above): "the load reflex is the oscillator", "he holds every foot
off the ground", "the reflex has its two halves", the position / hooks / none rows, "campaign: the reflex is named".

still standing in `docs/SEAM.md`:

- "what it is: the first rhythm in this project that the connectome makes with its body and nothing else." -> withdraw.
- "**no single sense is necessary and the sum of them is:**" -> "no single sense is necessary (one seed)".
- "the stick insect's load-dependent stance-swing transition (campaniform sensilla timing the step: Zill, Büschges; `walking_review.md`),
  running on the fly's wiring and the fly's body" -> withdraw. on the cord the sign is reversed on the middle legs (§3).
- "**six oscillators, uncoupled.**" and "the record's line on coupling stands as it was before noon: six oscillators, uncoupled" -> "up to
  four legs lift independently; rf and rh never lift".
- "the trochanter extensor motor neurons (the levators) up from 0.8 to 1.2-1.7 Hz" -> "(the depressors, by the body's role map)".
- "(the gain from Azevedo's FAST tibia extensor spike)" -> "flexor".
- "silencing the commissurals changes nothing" and "silencing their 19A targets changes nothing" -> "silencing cells at 0.4 Hz is not a
  test; not yet silenced where they fire".
- "Pugliese found the same cells "insufficient to couple the phase"" -> "Pugliese found unnamed left-right cells insufficient".
- "at 3 and 12 Hz they are not the strong commissural drive Sapkal describes" -> Sapkal gives no rate; drop the comparison.
- "which is Azevedo's ordering" and "Azevedo's ordering holds on the body under both labellings" -> "the ordering we assigned by size third
  is expressed; with identical cells the file recruits the large third first".
- "Azevedo's slow-flexor rate, on him, in his ordering, in both labellings" -> "at the g chosen as nearest Azevedo's rate".
- "**the shunt is what keeps him up under a command,**" -> add "one seed".
- the bold conclusions of "what the reflex is made of, first pass", "the senses removed one at a time", "the commissurals under a
  walking-rate command", "the population arms on the cord", "the population on the body", "the body on the standing senses" and "the
  small flexors' rest on the body" -> add "one seed".

in `docs/CAMPAIGN.md`:

- "a per-leg reflex oscillation at five hertz through the leg's senses, the first rhythm the connectome makes with its body and no fitted
  term." -> withdraw. put in its place what the freeze showed: the movement needs the motor output.
- "silencing them or their targets changes nothing" and "underdriven at the file's weights" -> as above.
- item 2b: "which is why fourteen-to-one inhibition parks the flexors where no threshold reaches them" -> add the pointer to the withdrawal.
- "**the switch is not in the premotor pair:**" -> add "one seed, at borrowed plateau sizes".
- item 3, "Azevedo's ordering; ... is the cell's own" and ledger row 9, "Azevedo's slow cells fire ~30 Hz at rest partly on their own" ->
  "partly on nicotinic input (MLA lowers the rate and does not abolish it); the remainder is unassigned".

in `docs/physiology/interleg.md`: line 3, as claim 13.

## the three things I would do next, in order

R1's re-runs (the no-load arms with the force read, seeds 11-13) are assumed done first. they are already promised in SEAM.

1. **the surrogate test: is the cadence the body's?** drive the body open-loop with the cord's leg MNs replaced by Poisson trains at each
   cell's mean rate from `lift_s11`, and with a phase-randomised surrogate of the recorded trains. if the ~200 ms lifts survive, the body
   sets them. then vary only the body: twitch tau 10 / 20 / 40 ms, the measured springs (`--stiffness 0.14`) against the default, gravity
   x0.5. a period that tracks these and ignores every cord manipulation (the record already has the second half) is mechanical. only if
   the lifts die under the surrogate does the connectome's part begin. then the question is "the connectome's reflex" against "any
   negative-feedback loop through a spiking network", and §3 gives the sign to test: flip the load onto the remotors (a diagnostic) and
   see whether the timing survives.
2. **the lean, both candidates, one at a time.** first the thirds ranked within each leg (R3's fix). if he still leans, swap the cord's
   left and right leg outputs onto the body. if the lean flips, it is §4's pool asymmetry, and its carriers can be found on the cord
   alone (the command's reach per side and segment onto the middle remotors, the middle levators and the hind tibia extensors). no
   coupling statistic means anything while two legs never lift and one side hangs.
3. **the load path by name.** on the cord, step one leg's load row at a time and trace which interneurons carry campaniform + untyped
   input to the middle legs' promotors and remotors. then run the same step with the 13 named campaniform cells alone, apart from the 98
   untyped ones. this says whether the swing-ward sign is the file's campaniform wiring or an artefact of driving untyped cells as load.
   it turns "the load reflex" from a name into a circuit, or retires it. alongside all three: the ledger rows and the withdrawals above,
   about an hour's work.
