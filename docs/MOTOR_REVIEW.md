# motor review: steering, speed, and the wings

an outside read, 2026-09-18, of the configuration of record (`--walk 100 --steer running
--pace running --bristle adapting --wheel DNa02 --dn-gain 0.5`, floor on, 0.185 mV). i read the
effectors, legs, episode, receptor and `pair.py` code before the docs, queried `brain_whole.npz`
for every count below, and ran four open-loop probes on the woken walking brain (seeds 1/3/5/7,
4 s per condition after a 1.5 s settle). flyvis was **not** attached to the probes, so "silent"
below means silent to the senses i could drive, not silent under the eye; closed-loop numbers
come from `world/garden3/*.npz`.

the three questions share an answer underneath. **the tonic floor (09-17 18:27) moved the
operating point and the motor results were never re-measured on it.** the walking command, the
brake and all three per-run calibrations date from the silent brain, and two of those three no
longer do what the record says.

---

## 1. steering: what we forgot to consider

`RunningBaselineSteering` reads DNa02 (1 cell per side) against each side's own running mean
(tau 20 chunks), EMA 3, 3 deg per net spike per chunk, clipped at 12 deg/chunk. `MultiWheelSteering`
adds a second channel over all 1,310 descending cells at gain 0.5. the touch reflex overrides on
contact; `--effector legs` exists but is not the config of record.

**the wheel is not a difference; it is one cell.** DNa02 per chunk in the three garden runs:
2.79 / 0.06, 3.05 / 0.03, 2.74 / 0.07. the left cell sits at 27-30 Hz, inside the 10-40 Hz the
vision brief derives from Yang 2024; the right has no variance for a baseline to subtract, so
`(R - base_R) - (L - base_L)` reduces to `-(L - base_L)`. the rule in force is "turn left when the
left DNa02 rises above its own 2 s average". the sign is right (ipsiversive, Rayshubskiy 2020) but
a bilateral visual transient also turns him left, because nothing cancels it. the record blames
the ascending echo under the walking command; on the woken brain **AN03A008 fires 0.0 spikes/s**
and DNa02 R is still zero, so that explanation belongs to the silent brain too. what remains true
is that AN03A008 is DNa02's largest input (741 L / 717 R synapses, symmetric, against 1,197 / 636
of its own) and driving it at 100 Hz gives DNa02 89-95 L / 66-70 R, nearly as much as driving
DNa02 itself. the biggest lever on the wheel is not firing.

**the populations nothing reads.** counts are cells in this build; synapse counts are direct onto
leg MNs, with the two-hop weight through VNC interneurons in brackets.

| candidate | cells | onto leg MNs | why |
|---|---|---|---|
| **DNa01** | 2 | 360 (2.87 M) | the other half of the published steering pair — ipsiversive, low-gain and sustained where DNa02 is high-gain and transient (Rayshubskiy 2020). its top inputs are VES007, LT51, LAL124, VES074; AN03A008 is not among them, so whatever pins DNa02 R has no obvious route to it. |
| **DNg13** | 2 | 280 (1.94 M) | the crossed ipsiversive turner, the only crossed steering DN with a measured sign (Yang 2024) and the template the leg brief leans on. silent at base. |
| **DNb06** | 2 | 316 (0.70 M) | contraversive (Yang 2024) and, unlike DNg13, alive: 30-36 spikes/s left, 0 right, swinging +15 with wind and +17 with touch. |
| **PFL3** | 24 | — | the second-largest input to DNa02 after AN03A008 (380 R / 356 L). the compass is in the build (EPG 46, EPGt 4, PEN 42); TODO §2c wants the bump measured before menotaxis is built. |

**the seven types the wheel screen picked are mostly neck neurons.** DNg49 puts 3,142 synapses
onto neck MNs and 13 onto legs; DNa06 935 neck / 24 leg; DNp20 206 neck and nothing onto legs or
wings; DNge125, from the thermal set, 3,692 neck. consistent lateralisation across vision, smell
and touch — what the screen selected for — is what gaze stabilisation looks like, and in a fly
those move the head. this sim has no head: `eye.render` takes the body's heading. the screened
wheel turned the body with a head command, which is why it spun him at +40 to +110 deg/s.

**the `dn_gain` channel is eight cell types.** on the woken walking brain **86 of 1,310 descending
neurons fire at all** (seed 1). shares of the 2,228 spikes/s: DNb05 17.2%, DNg33 15.0%, DNp12
8.5%, DNg56 8.3%, **DNp09 6.7%** (the drive we supply), DNp31 5.5%, DNg99 4.5%, DNbe001 4.4% —
sixteen cells, 70% of the channel, none of them a steering signal (DNb05 alone runs at 190-200
spikes/s *per cell*, symmetric and unmoved by anything). the types that do carry laterality are
small: wind swings DNp20 by +53.8 spikes/s of L-R, DNp73 +41.5, DNge016 +30.8,
DNp18 +29.8, DNpe017 +22.2, DNb06 +15.2; warmth swings DNp06 +105.8 and DNp35 +46.5, and those
two are wing DNs. summing 1,310 cells to find a twelve-cell signal is the problem.

**the two channels disagree about warmth, and the big one has the wrong sign.** 33 C on one
antenna, floor on, walking, four seeds: the descending population goes ipsilateral — L-R is +77 at
base, +216 with the left antenna warm, -91 with the right — a swing of ~300 spikes/s, which at
`--dn-gain 0.5` is 15 deg/chunk, i.e. clipped, **toward** the warm side. DNa02 does the opposite
and far more weakly: 3.4 spikes/s at base, 7.9 with the right antenna warm, 2.0 with the left,
about 1.4 deg/chunk away from it. the DN channel's sign was fixed by the wind result (windward
side up, turn upwind), and the same scalar is wrong for temperature — the 11:48 lesson again.

**tests, ranked.**

1. **DNa01 as a wheel.** add `DNa01` to `RM`, run `experiments/drum.py --steer running --walk 100
   --wheel DNa01`, 3 seeds, against the DNa02 arm. positive: DNa01 R above 0.5 spikes/chunk on a
   walking cord (DNa02 R is 0.03-0.07) *and* following the drum's sign in both phases in 2 of 3.
2. **retire the 1,310-cell channel for a named six.** `--dn-gain` over {DNp20, DNp73, DNge016,
   DNp18, DNpe017, DNb06}. positive: garden wind arm holds upwind cos at or above the current
   +0.12-0.14 with rim time back near the control's 0.06-0.12.
3. **confirm the screen found gaze.** drive DNg49, DNa06 and DNp20 unilaterally at 100 Hz with the
   floor on and read MN counts split by `subclass` (the 12:33 protocol). positive: neck ≫ leg for
   all three, which retires them from the wheel and promotes them to a head channel.
4. **gain and clip.** the brief wants 5 deg/s per Hz and a ±800 deg/s cap; we run 3 and clip at
   120 deg/s. drum, 3 seeds, 3/12 against 5/80. positive: following both ways in more seeds.
5. **is the compass alive?** add PFL3, EPG and PEN to `RM`, 120 s of garden. positive: any nonzero
   PFL3 rate — that gates the menotaxis item.

---

## 2. speed: why he is always walking

`RunningPace` is `v = 0.05 + 0.45 · clip(c / (2·mean), 0, 1)` with the mean over 20 chunks,
updated after use. its fixed point is `c = mean → v = 0.275`, and that is where the runs sit:

| run | v mean | median | sd | frames at the 0.05 floor | at the 0.5 ceiling |
|---|---|---|---|---|---|
| gated_s11 | 0.278 | 0.277 | 0.085 | 0 of 12,000 | 3.0% |
| off_s10 | 0.277 | 0.279 | 0.065 | 0 | 1.1% |
| wind_s12 | 0.276 | 0.277 | 0.060 | 0 | 0.7% |

a fly's forward velocity is bimodal with a mode at **zero** and another near 17.5 mm/s (DeAngelis
2019). ours is unimodal, never stops, and returns to 0.275 within 2 s of any change in leg output,
by construction. so part of the answer is arithmetic.

**the larger part is that the walking command stopped working.** open loop, leg-MN spikes per
second on the 373-cell set, seeds 1/3/5:

| floor | DNp09 0 | 30 | 100 | 200 | 100 + brake 30 |
|---|---|---|---|---|---|
| **on** | 559 / 586 / 579 | 575 / 588 / 582 | 540 / 522 / 538 | 477 / 515 / 501 | 546 / 557 / 552 |
| off | 0 / 0 / 0 | 5 / 46 / 26 | 387 / 344 / 449 | 671 / 689 / — | 4 / 4 / — |

on the silent brain DNp09 at 100 Hz is everything and the brake halts the cord completely, which
is what the record says at 12:43 and 13:55. **with the floor on, neither is true.** the command
adds nothing (slightly negative at 200 Hz) and the brake does not brake. the 520-590 spikes/s is
the floor's own tonus: ablating rows one at a time, dropping the hot and cooling rows (fourteen
cells at 37 and 95 Hz) takes leg output from 526 to 288, dropping the JO row (672 cells at 5 Hz)
to 446, dropping the 580 leg proprioceptors to 484. no single row owns it, and all of it is bigger
than the command.

DNp09 was also weak on the wiring: **10** direct synapses onto leg MNs. DNg100 (annotated BDN2,
the walk-OFF target in Sapkal 2024) has 1,870 and the largest two-hop weight of any named DN
(5.15 M); DNg74_a 2,635; DNg105 8,736. MDN (4 cells) logs 0.00-0.01 spikes/chunk in every run, so
backward walking is absent as well as unreadable.

**so: misreading, and there is no state to read.** the pace is pinned by its own estimator, the
command adds nothing to the floor, the brake is inert, 86 of 1,310 DNs and 111 of 1,841 ANs fire
at all, and nothing persists (00:54). the one state-like modulation in the record is the 17:20
klinokinesis — he turns more when warming, 3 of 3 seeds, rest arm flat — and that is what to
build speed on.

**tests, ranked.**

1. **dose-response in the loop.** `--walk 0|100|200` × `--floor|--no-floor`, 3 seeds, 120 s, score
   distance walked and mean leg MN. positive: distance rises with `--walk` when the floor is on.
   the open-loop numbers predict it will not.
2. **an absolute pace reference.** replace the running mean with a reference measured once per
   brain configuration at `--walk 0` with the floor on (~550 spikes/s), plus Azevedo 2020's class
   weights. positive: the pace histogram gains mass at `v_min` — today it is 0 of 12,000 frames.
3. **the brake, latched.** `--stop-at-her 100` held 2 s after a contact frame instead of per
   frame, floor on. positive: any drop in leg MN; my probe says 30 and 100 Hz both do nothing.
4. **the other walking command.** drive DNg100 at 30 / 100 / 200 Hz, floor on, open loop. positive:
   above ~1,100 spikes/s, twice the floor's tonus, which DNp09 never reaches.

---

## 3. walking and the wings

`--legmn leg` correctly restricts the readouts to the 373 leg MNs (`fl` 133, `ml` 116, `hl` 124).
the other 326 `vnc_motor` cells — abdominal 214, **wing 66**, neck 24, haltere 16, unknown 6 — are
driven by the same premotor network, read by nothing and suppressed by nothing. they are not idle:

| set | cells | spikes/s, woken walking brain | per cell |
|---|---|---|---|
| leg MNs | 373 | 526-588 | 1.4 Hz |
| **wing MNs** | 66 | 867-925 | **13.4 Hz** |
| neck MNs | 24 | 155 | 6.5 Hz |
| abdominal MNs | 214 | 108 | 0.5 Hz |

and the wing MNs that fire are the wrong ones: DVMn 1a-c at 52.8 Hz/cell, hg1 37.5, DLMn a,b 31.8,
DVMn 2a,b 31.2, DVMn 3a,b 25.9, i2 25.1 — while every steering-muscle MN that would carry a
courtship or corrective wing movement (b1, b2, b3, tp1, tp2, tpn, ps1, ps2, iii1, iii3, hg2-4)
sits at **0**. DVM and DLM are the indirect **flight power** muscles. our grounded fly is running
his flight motor at 25-53 Hz per cell and the body model cannot see it.

**what flies him is the smell floor.** removing the five ORN rows (2,635 cells at 8 Hz) takes wing
MN output from 867 to 195 spikes/s and abdominal from 108 to 6, while leg output is unchanged at
540. the largest descending input to the power MNs is DNp31 (2,361 synapses), at 124 spikes/s and
5.5% of the DN channel. an 8 Hz resting rate on the olfactory receptors — the right call for the
brain — is running the wing motor system.

**the overlap is structural.** 84 DN types put more than 100 synapses onto leg MNs, 79 onto wing
MNs, and 15 onto both: DNg105 (8,736 leg / 304 wing), DNge079, DNg93, DNg74_b (3,333 / 511 / 1,813
abdominal), DNp18 (444 / 357), DNb05 (423 / 318). DNa02 itself has 74 wing, 33 haltere and 42 neck
synapses, which is what Rayshubskiy 2020 reports. the withdrawn thermal result is this fact from
the other side: DNp35 and DNp06 reach wing MNs and nothing else, and they are the most lateralised
warm channel in the descending population. courtship shares the motor too — pIP10 (2 cells) →
DNg74_b, 177 / 123 synapses — and pIP10 logs 0.00 in every run, so wing extension never competes.
the power muscles have it uncontested.

**grounded flies differ in four ways, and we model one.** visual gain is not constant: walking
raises HS amplitude and shifts its temporal-frequency optimum (Chiappe 2010), and in flight the
same boost is octopaminergic (Suver 2012; Maimon 2010). `--drive-gain` is a fixed 150 for every
state; the substrate is in the build (101 octopamine cells, OA-AL2i2 alone with 28,944 synapses
into the optic lobe) but the engine has no slow receptors, so like hunger it has to be a gain, not
a drive. second, gaze: 24 neck MNs at 6.5 Hz and several neck-dominant DNs, against an eye bolted
rigidly to the thorax. third, escape, which is most of what a grounded fly does with vision —
DNp01 (2 cells, 70 synapses onto TTMn), LC4 126, LPLC2 185, LC6 124, LC16 182, all present, none
in the loop, loom detector withdrawn in TODO §3. fourth, halteres, correctly silent (Hall 2015),
and the only one we get right.

**tests, ranked.**

1. **log the other 326.** add `wingMN`, `neckMN`, `abdMN` by `subclass` to `RM`. positive: free,
   and every run from here says what the rest of the motor system did.
2. **is the smell floor flying him in the loop?** garden, 120 s, 3 seeds, three arms — full floor,
   floor minus the ORN rows, no floor — with the readout from test 1. positive: closed-loop wing
   MN tracks the open-loop 867 → 195, which makes the ORN resting rate a calibration item.
3. **a walking-state visual gain.** drum, 10 flyvis models, `--walk 100`, `--drive-gain 150`
   against 225 (the brief's ×1.3-2). positive: following both ways in more than the 3 of 10 the
   running baseline gets. blunt — it scales all of T4/T5, not the HS-projecting channels — and
   should be labelled so.
4. **the leg model on the full set as a diagnostic.** `--effector legs` with `P` printed per side
   and segment next to the wing totals. positive: if wing output moves with the same inputs and
   signs as leg output, "warmth reaches the wings" is shared premotor drive, not a wing channel.

---

## what i would change first, and why

1. **run the three calibrations inside the floor.** `dna02_rest_offset`, `standing_baselines` and
   `reflex_gain` never call `REG.apply`, so they execute on a silent brain. the logs say it aloud:
   `DNa02 rest offset +0.00/chunk`, `his leg MN 0`, and a touch-reflex gain of 104 deg per unit
   asymmetry measured against a zero background — then the loop runs at 520-590 spikes/s of it.
   the touch reflex is the one effector with a large replicated behavioural effect (wall time 15%
   against 91%) and its gain is calibrated in a regime the loop never visits. one call, moved.
2. **re-measure the walking command and the brake on the woken brain, and mark the record.** "he
   walks (12:56)" and "the brake (13:55)" are silent-brain results. today `--walk 100` changes leg
   output by less than the run-to-run scatter and `--stop-at-her` cannot work in principle. they
   are the two load-bearing motor claims in SEAM and they need the strikethrough DNge125 got.
3. **fix the pace reference.** the running mean guarantees a fly that never stops and never
   sprints, which forecloses the exploration question before the brain gets a vote. already the
   open item in TODO §2; now the difference between measuring a behaviour and measuring an
   estimator.
4. **give DNa01 a readout and stop summing 1,310 DNs.** the wheel is one cell with a dead partner,
   the second channel is eight tonic types (one of them our own drive), and it steers into warmth
   while DNa02 steers out of it. adding DNa01 costs a line.
5. **log the wing, neck and abdominal motor neurons.** we are running a fly whose flight power
   muscles fire ten times harder per cell than his legs, driven by the olfactory resting rate, and
   no readout would have told us. it needs to be visible before it needs a fix.

## what i could not verify

flyvis was not attached to my probes, so every "silent" in section 1 is silent to warmth, wind,
touch and direct drive only. LC10a is the one genuine exception — 275 cells logging 0.00
spikes/chunk across three 120 s garden runs *with* the eye on — but HS (8 cells), VS (18), LC4,
LPLC2 and PFL3 were never measured under vision, and i re-ran no closed-loop scoring. whether
DNa01 is visually driven is therefore open; test 1 answers it. the warmth-to-DNa02 result is
one-sided by construction — DNa02 R is pinned at zero — and bilateral warmth gives the same 7.9
spikes/s as the right antenna alone, so the wheel would turn him a fixed direction in warm air
rather than away from a gradient. repeats of one condition on a reused brain object scatter by
about 15% on leg-MN totals, so single-row differences under ~20% in my tables are noise; the
claims i draw from
them (0 against 387 for the command, 546 against 4 for the brake) are an order of magnitude larger. and i did not audit the leg
model's muscle weights beyond confirming that `muscle_weight` matches 290 of the 373 leg MNs by
type-name substring.
