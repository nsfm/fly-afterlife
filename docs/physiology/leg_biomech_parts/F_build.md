# F. What this changes in the build

Three builds were named. Here is what §§A–E say about each, and what should *not* be done.

## F.1 The probe (read 373 MNs per 10 ms frame and ask "is this walking?")

**The frame is the wrong length for an instantaneous readout, and right for a kernel.** A single
fast or intermediate tibia-flexor twitch peaks at **~21 ms** and decays with **tau ≈ 20 ms**,
back to baseline at 70–80 ms (Azevedo et al. 2020, digitised). At 10 ms frames a spike's force is
spread over the next **5–8 frames**. So the probe must convolve, not threshold: force in frame *t*
is a kernel over spikes in frames *t−8…t*, and the existing `1 − exp(−Δ/k)` per-frame saturation
is not that. It is also the wrong shape — measured summation is **2 spikes = 1.6 × 1 spike** and
saturation at **~10 spikes**, which an exponential-saturation curve fits only by accident.

**The slow units are a separate regime, not the bottom of the same one.** The slow tibia flexor
has no resolvable twitch: force is still rising at 500 ms and release takes ~100 ms. It fires
**~30 Hz at rest** (10–52 Hz) while fast and intermediate are silent, i.e. **3 spikes per 10 ms
frame from a single cell, standing still**. Baseline subtraction stays non-optional, and the slow
pool wants a tau of order 200–500 ms **(E)**, not a twitch kernel.

**Group by (leg × joint × antagonist pair), not by cell.** §A gives the map for all six legs.
The six grouped drives per leg are: ThC promotion vs remotion, CTr levation vs depression, TrF
reduction, FTi flexion vs extension, TiTa levation vs depression. That is the readout the probe
should print, per leg, per frame, against §C's phase expectations.

**Fix the 45 dead cells first.** §A2 assigns 37 of them. Until then, the mid and hind legs have
**no tarsal grip channel and no promotor channel in the readout at all**, and the probe would be
asking whether a pattern is walking-shaped while blind to the muscle that puts the foot down.

## F.2 The muscle-up effector

Replace `a_i = f_i * (1 - exp(-delta/k))` with, per MN *i*:

```
f_i      = f0 * (S_i / S_ref,segment) ** alpha      # alpha ~= 1.2 (E), NO clipping,
                                                    # S normalised WITHIN segment (A3, A4)
force(t) = f_i * sum_s K(t - t_s)                   # K: tau_rise ~ 7 ms, tau_decay ~ 20 ms,
                                                    # peak ~21 ms  (Azevedo 2020, digitised)
                                                    # slow class: K -> single exp, tau 200-500 ms (E)
```

with, where class labels exist, **10 / 1 / 0.1 µN per spike** for fast / intermediate / slow
directly, skipping the proxy. Three things that must not be done:

- **Do not clip the size span.** The current `clip(S/S_ref, 0.2, 5.0)` removes the very spread
  that carries the force class: within the tibia flexor pool the measured span in this volume is
  **37–92×**, and the measured force ratio across it is **100:1**.
- **Do not normalise size across segments.** The front leg is under-traced by 1.5–4× for the same
  muscle (§A3); a global `S_ref` makes every front-leg muscle weak for a tracing reason.
- **Do not fit anything to the behaviour.** The exponent falls out of two measured numbers
  (span ≈ 50×, ratio ≈ 100×); if it stops giving good walking, that is a result, not a knob.

Joint torque, not a body scalar: `torque_joint = sum over muscles of (sign × force × moment arm)`.
Moment arms exist for the front leg in FlyMimic (§D.5) and nowhere else; for T2/T3 they are **(E)**.

## F.3 Proprioception

§E's table says this can be built on real labelled cells: the male carries FeCO **claw**
(`SNpp50`, `SNpp51`), **hook** (`SNpp39`, `SNpp41`), **hair plate** (`SNpp45`, `SNpp52`) and
**trochanter campaniform** (`SNpp53`) afferents on all three leg pairs, with published tuning and
published downstream reflexes. Two constraints:

- **The front legs are not usable for this.** 1 `SNpp50` cell versus the middle leg's 26. Build
  the loop on T2/T3 and say so.
- **`SNch` is chemosensory, not chordotonal** (Marin et al. 2024). Anything that filtered on
  "ch = chordotonal" has been reading the taste neurons.

## F.4 Body

§D: **NeuroMechFly v2 / flygym** for the walking body and the proprioceptive physics;
**FlyMimic** (Özdil et al., ICLR 2026; arXiv:2509.06426; Apache-2.0, vendored inside flygym 2.1.0)
for the left front leg driven by the *unreduced* per-muscle vector, as the measurement of what the
per-muscle → per-joint collapse costs. Both Apache-2.0, both MuJoCo, one dependency.

Label the collapse as what it is. `docs/LANDSCAPE.md` takes flyverse-core's instrument-labelling
discipline as the first thing worth stealing: a stand-in declares in code whether it supplies a
missing **input** or replaces a missing **computation**. The antagonist-pair → position-setpoint
map in §D.7.2 replaces a *computation* (the muscle mechanics), and the T2/T3 moment arms supply a
missing *input*. Both should carry the flag.

### F.4a The front-leg map onto FlyMimic's 15 actuators **(D)**

Our front-leg MN types against FlyMimic's actuator names (§D.5). This is the whole reason the
per-muscle drive is worth building: for the front leg it is not a mapping, it is an identity.

| Our MN type (n cells) | FlyMimic actuator(s) |
|---|---|
| `Tergopleural/Pleural promotor MN` (8) | `LFC_tergopleural_promotor_a`, `_b`, `LFC_pleural_promotor` |
| `Pleural remotor/abductor MN` (4) | `LFC_pleural_remotor_and_abductor` |
| `Sternal anterior rotator MN` (4) | `LFC_sternal_anterior_rotator` |
| `Sternal posterior rotator MN` (6) | `LFC_sternal_posterior_rotator` |
| `Sternal adductor MN` (2) | `LFC_sternal_adductor` |
| `Tr flexor MN` (15) | `LFF_trochanter_flexor_a`, `_b` |
| `Acc. tr flexor MN` (6) | `LFF_accesory_trochanter_flexor` |
| `Tr extensor MN` (4) | `LFF_trochanter_extensor` |
| `Sternotrochanter MN` (4) + `Tergotr. MN` (8) | `LFF_sterno-tergo-trochanter_extensor_a`, `_b` |
| `Ti flexor MN` (10) + `Acc. ti flexor MN` (19) | `LFTibia_flex_93434` |
| `Ti extensor MN` (4) | `LFTibia_extensor_93932` |
| **`Fe reductor MN` (10), `Ta depressor MN` (9), `Ta levator MN` (5), `ltm MN` (8), `ltm1-tibia MN` (3), `ltm2-femur MN` (4)** | **none** |

**94 of the male's 133 front-leg MNs (71 %) map onto a Hill-type actuator by name. The remaining
39 (29 %) are the TrF and TiTa muscles FlyMimic does not model** — the femur reductor, the whole
tarsal apparatus and the long tendon muscle. So the cross-check in §D.8 is strong for ThC, CTr and
FTi, and absent for the two joints that decide grip. Say that wherever the comparison is quoted.

## F.5 One correction to `leg_motor.md` §6's segment weights

`leg_motor.md` §6 sets `μ_T1 = −0.5, μ_T2 = +1.0, μ_T3 = +1.0` on the argument that front legs
brake. Isakov et al. 2016's neuromechanical model, fitted to the amputation-recovery trajectory to
within 1 % mean discrepancy, gives a per-leg sensitivity that the brief did not use: sweeping the
force in one leg at a time, **the middle legs need the smallest force change to produce a given
turn-bias change, then the hind legs, then the front legs, which need the largest.** Per unit
force the yaw leverage is **T2 > T3 > T1**, and the required right/left force ratio over recovery
sits in **0.7–1.0**.

So the magnitudes should not be `μ_T2 = μ_T3`. A sourced ordering is `|μ_T2| > |μ_T3| > |μ_T1|`
**(M, via a fitted model)**. The paper also explicitly declines the cockroach assignment
(Mu & Ritzmann 2005: front legs steer, hind legs propel) as insufficient in the fly — which is a
caution against the sign of `μ_T1`, not a confirmation of it. Keep `μ_T1` negative if you like,
but mark it **(E)** as before and note that the one fitted fly model does not require it.

## F.6 The muscle sign vector cannot be global — it flips between T1 and T3

`legs.py`'s `MUSCLE_W` is one signed weight per muscle, applied to all six legs. Haustein, Blanke,
Bockemühl & Büschges 2024 (*Front Bioeng Biotechnol* 12:1357598, DOI 10.3389/fbioe.2024.1357598;
12 flies, 400 Hz motion capture, 2,250 steps at 14.7 ± 4.0 mm/s) measured the step-phase signs
directly, and they are not the same in the three leg pairs **(M)**:

- promotion in **swing**, remotion in **stance**, in all three pairs — the ThC weights are safe;
- **front legs extend during swing and flex during stance**;
- **hind legs do the opposite — flex during swing, extend during stance**;
- middle legs are idiosyncratic: the trochanter flexes in swing and extends in stance, but tibia
  flexion runs through nearly the whole swing *and* the first half of stance, with extension only
  in the second half.

So `Ti flexor` is a **stance** muscle in T1 and a **swing** muscle in T3, and `Ti extensor` the
reverse. A single `w = +0.5` for the tibia flexor across all six legs has the sign **wrong for the
hind legs**, which are also the pair with the most tibia flexor motor neurons in this male (17,
against 10 front and 10 mid — §A3). `MUSCLE_W` has to become `MUSCLE_W[segment]`, at minimum for
the FTi and CTr pairs.

Two more numbers worth carrying into the effector from the same paper **(M)**. Range of motion
during forward walking, front / middle / hind:

- coxa promotion–remotion **40.9° / 26.5° / 18.6°**
- trochanter flexion–extension (CxTr-yaw) **91.2° / 22.5° / 56.3°**
- tibia flexion–extension (FeTi-yaw) **96.6° / 21.5° / 84.1°**

**The middle leg barely moves its distal joints** — 22° of trochanter and 21° of tibia against the
front leg's 91° and 97°. It walks almost entirely from the thorax–coxa joint. Any per-joint
effector that gives all three legs the same gain will over-drive the middle leg's knee by a factor
of four.

## F.7 Two traps in the body model

**Do not inherit FlyMimic's activation dynamics.** Its MJCF sets `dynprm` to τ_act ≈ 0.1 ms and
τ_deact ≈ 0.4 ms. The measured half-rise of a *Drosophila* leg-muscle twitch is **8.5 ms**
(Azevedo et al. 2020), with peak at ~21 ms — the shipped value is **~85× too fast**. It is a
fitting convenience, not a measurement, and it exists because their input is a continuous
activation, not a spike train. Our spike→force stage (§F.2) *is* the missing physiology; put the
20 ms kernel in front of the actuator and leave the actuator's own filter effectively transparent.

**Passive stiffness exists and it is small.** Wang, Babski, Perdomo, McMahan, Ramakrishnan,
Biswas & Bhandawat 2025 (bioRxiv 2025.04.29.651225; PMC12324252; **a preprint**) silenced the whole
motor pool and measured a **linear angular spring over ±40°** about the rest angle, for four DoFs ×
three leg pairs. Their own conclusion is the one to hold onto: **passive muscle force is large but
not enough to hold the fly up** — of order 70× short. So a body run with the muscles silent must
collapse, and if it stands up instead, the body's joint stiffness is doing work the fly's isn't.
Note the units in that paper are self-contradictory (`mN/°` in the table caption, `Nm/°` in the
discussion); §B derives ~2 × 10⁻⁸ N·m/rad for the T1 femur–tibia joint by cross-check against
Azevedo's probe stiffness, and marks it uncertain to a factor of ~50. **No damping has been
measured in any fly leg joint.**
