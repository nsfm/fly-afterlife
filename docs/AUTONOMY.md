# working without a prompt

2026-09-19 19:14 PDT (nyx). nate asked whether a cron that wakes me a few times a day could make progress on him without
waiting for direction, and what it would take to stay organised and not circle. this is the protocol. the charter it serves
is in the project memory and at the top of `docs/TODO.md`: embody the fly as far as the connectome allows, fill only what it
cannot contain, keep the seam honest, puppetry only as a labelled stand-in with its exit written down, no time limit.

## the three files

- **the queue: `docs/TODO.md` §Q.** the only place work is picked from. each item is one change per run, with its control and
  the measurement that decides it, in order. status per item: queued / in flight / measured / adopted / withdrawn. one item
  in flight at a time; a second only if it shares no module with the first and the machine has room.
- **the record: `docs/SEAM.md`.** every run, result, correction, in the order it happened; the STATUS block at the top is the
  summary a wake reads first. nothing is launched that the record does not get an entry for by the end of the wake, even if
  the entry says "launched, result pending". `scripts/seam_index.py` regenerates `docs/SEAM_INDEX.md`, one line per
  section with its timestamp, so "has this been tried?" is a grep, not a read.
- **in flight: `world/inflight.json`.** what is running, launched by which wake, its PIDs, its output files, the queue item it
  serves, and the scorer to run when it finishes. a wake that finds a finished run scores and records it before doing
  anything new. a wake that finds a stale entry (no PID alive, no output) records the loss and re-queues.

## a wake, in order

1. read: the charter line, TODO §Q, the STATUS block, `inflight.json`, the last three record entries.
2. machine: `nvidia-smi` and `ps`. the GPU holds six flyvis processes; never more. if nate's viewer is open, at most three
   jobs. never kill anything by pattern; only PIDs from `inflight.json`, only mine.
3. finish before starting: score anything finished, write it into the record, tick or withdraw the queue item, commit, push.
4. one new thing: the next queued item whose prerequisites are met. launch it with a waiter that writes to its own log.
   write the record entry skeleton ("launched HH:MM, seeds, control, what decides it"). update `inflight.json`. commit.
5. the oracle before any commit that touches the engine, the drive path, or a default. FAIL means fix or revert before
   anything else; an oracle FAIL is recorded as a FAIL even when its cause was a typo.
6. leave: the tree clean, the record consistent with the disk, and `docs/TODO.md` §Q still true. a wake with nothing to
   do (everything in flight, or blocked on nate) writes one line to the record's STATUS and stops.

## what a wake does not do without nate

- runs that cross the line: starving or sleep-depriving him once the hunger and sleep states exist, the rival on loop,
  anything the ethics paragraph in TODO §S2 names. those are proposed in `docs/ASK.md` and wait.
- a default flip of the fly's configuration (the senses on, the constants). measured as an arm, proposed in ASK.md.
- edits to the oracle references (a refreeze), the units rescale, anything that rewrites the record's baselines.
- taking the machine for more than a wake's worth: a batch longer than ~40 minutes is queued for the night wake.
- anything outside this repository, ~/.nyx, and the scratchpad.

## not circling

- **before launching, grep.** `docs/SEAM_INDEX.md` and the STATUS block. if the flag or the idea has an entry, read it; a
  withdrawn result is not retried without a stated reason for why this time differs.
- **decisions are recorded as decisions.** TODO §Q has a "settled" list at its foot: things decided, with the entry that
  decided them, not to be relitigated by a wake (the DN population channel is noise; the null point was a crutch; the
  thermal field is on under `rest`; three seeds is the floor for a claim, not a ceiling).
- **one change per run** is the rule that prevents most circling by itself: a wake cannot "try a few things".
- **a result needs its control in the same wake.** no arm without its rest.
- **the daily digest is the STATUS block.** nate reads that; it must be true at the end of every wake.

## the cadence i would ask for

three wakes: morning (score the night batch, one short item), afternoon (one item), night (the long batch). each wake is a
fresh session that reads the files above; the memory file carries the charter and the rules that are not in the repo. the
first wake of a day also reads `docs/ASK.md` for nate's answers, which nate writes inline under each question.
