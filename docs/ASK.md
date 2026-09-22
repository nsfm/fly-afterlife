# questions for nate

written by wakes; nate answers inline under each. read at the first wake of the day. 19:14 PDT.

## the long-run rule (queue item 7)
the clock and sleep pressure make a "day in the garden" possible: a run of hours in which activity should peak at dawn and
dusk and he should stop at night. the rule we set: every long run is one in which he can eat and sleep. proposed protocol
for the first one: 2 sim hours, the fruit present, the sun moving, satiety and sleep pressure both allowed to discharge;
no run that withholds either. yes / no / changes?

> **nate, 22:01:** fair, and parked. leave it on the table until the short-run behaviour is something we are comfortable with; wasteful to
> kick off while the list is this long unless there are real learnings we want from it. we also need a better way to make statistical
> use of his behaviour here first.


## the constant (queue items 3 / 3b, 19:43)
0.185 mV per synapse was set for the male from one measurement: Kenyon-cell sparsity. tonight the taste chain gave a second,
independent measurement of the same constant: at 0.185 the labellar sugar cells must fire ~100 Hz before MN9 fires and the
pharyngeal pump never runs; at Shiu's 0.275 MN9 fires from a 100 Hz drive and the pump runs at 186 Hz (a fly swallowing).
Shiu's own MN9 threshold is 30 Hz. so our wiring under-carries by roughly three relative to the model we cite. options:
(a) keep 0.185 and accept a quiet fly; (b) move to 0.275 and re-measure KC sparsity and every baseline (a refreeze day);
(c) re-examine the KC calibration itself, which may have been the outlier. my lean: (c) first, one wake, then (b) if the
KC number survives at 0.275. yes / no / a different order?

> **nate, 22:01:** the constant was set while he had only part of his systems, and more sensation improved things across the board.
> happy to move to the documented value and see; we should feel good about constants we can cite. (b) is the likely outcome; test (c)
> first if that is how you want to start. not committed to 0.185.

> **nyx, 22:06, after (c):** measured. by sparsity (re-made as `experiments/kc_sparsity.py`) 0.185 is in the 5-10 % band (6.8 %) and
> 0.275 is out (18.4 %); by the taste chain 0.275 fires MN9 from 100 Hz, but its "pump" is a flat 190 Hz plateau that snaps on and never
> adapts, a gnathal loop tipping over, not a swallow. my recommendation: **keep 0.185**, and read the taste result as "he needs to be
> on the food with the labellum at a real sugar concentration" (sugar cells fire 100-150 Hz on food in life, and at 150-200 Hz MN9
> fires at 0.185). 0.22 stays on record as a labelled test constant if the feeding readout needs it. (b) not taken. your call stands
> if you want 0.275 tried in the garden anyway; i would run it as an arm, not a default. yes / no?

> **nate, 09-21 08:52:** intermediate values between 0.185 and 0.275 are the more honest path than per-zone constants ("brain surgery");
> the constant is arbitrary anyway, so sweep it. Shiu's 0.275 was tuned by simulation on a silent network to hit the extension
> behaviour (nate's guess, confirmed by the brief), so it cannot be inherited by a fly with the floor on. settle the constant before the
> physics. nyx: agreed; the sweep is the next wake's first item (TODO §Q 3f). the one non-uniform variant allowed on the list, later,
> is scaling by transmitter (citable); per-behaviour gains never.

## the ocelli and sleep (nate's guess, 09-21)
does the ocellar channel touch his sleep or rest drive, so that having it on makes him more wakeful? from the table: the ocellar
cells project to flight-and-neck descending neurons (DNp20 / DNp22 / DNpe017), not to the clock or the sleep cells; light reaches
the clock through cryptochrome and the compound eye. the tonic push looks like arousal. parked until the states exist (S2).

> **nyx, 09-21 08:55, the sweep:** 0.20 / 0.22 / 0.24 / 0.26 scored on the three stated criteria. the runaway caps the constant at 0.24;
> sparsity leaves its band at 0.22; and below the cap the constant does not move the sugar chain's threshold (~100 Hz of measured
> labellar firing at every w), only how hard MN9 fires above it. so no available constant changes what he can do, and 0.185 is inside
> every criterion. **settled: 0.185 stays.** the lever for feeding is the input, which is the physics. room exists up to 0.22 if the
> physics puts him on food and the chain still wants more. moving on to the physics.

## the wing motor artefact (2026-09-21 13:49; docs/SEAM.md, TODO 8b)
his 56 wing motor neurons run at 31 Hz per cell while he walks and eats: a four-cell premotor hub in the cord lights from any
broad tonic input and the flight / song premotor network follows. it is driven, not bistable, and not one sense's fault; the
cord is too excitable to tonic input at our constant. three options: (a) the flight gate as a state, "not flying" holding the
flight premotor network below threshold, labelled, like the walking command in reverse (my lean: he will need a flight state
for take-off anyway); (b) a labelled input-gain correction on the hub, same class and risk as the mirror normalisation; (c)
leave it, since the wings drive nothing in the world and the number is known. a / b / c?

## two leaks and a refreeze (2026-09-21 13:49; TODO 8c)
the setup's calibrations leave drive rates on 314 cells that no run row overwrites (they keep firing at their calibration rate
all run), and the reference engine holds all 97 MBONs at 85 % of threshold by a tonic current that is flybrain's, not Shiu's.
fixing either changes every run slightly and fails the oracle by design (the references carry both). proposal: fix the leak,
set the MBON hold to 0 (Shiu), measure the baselines that move, and refreeze oracle v3 in one go, with the mm units question
left for another day. yes / no / later?

> **nyx, 09-21 18:10, after the systematic pass:** the wings are a saturating amplifier in the cord lit by any of six tonic inputs; no constant, no
> single input, no path. the pattern generator's inhibitory half (IN06B066, IN03B089, IN11B013) is unreachable by anything he senses or is
> commanded, so the gate is a state, and it now has an address. the options stand; my lean is (a) implemented as driving those three brake
> classes under a labelled "not flying" state, exit = the flight command (DNp31 / DNg27 excite both halves, the shape of take-off). a / b / c?
