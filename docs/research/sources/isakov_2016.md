# Isakov, Buchanan, Sullivan, Ramachandran, Chapman, Lu, Mahadevan & de Bivort 2016

**Citation.** Isakov A, Buchanan SM, Sullivan B, Ramachandran A, Chapman JKS, Lu ES, Mahadevan L, de Bivort B (2016). "Recovery of locomotion after injury in *Drosophila melanogaster* depends on proprioception." *Journal of Experimental Biology* 219(11):1760–1771. DOI 10.1242/jeb.133652.
PDF read in full: https://softmath.seas.harvard.edu/wp-content/uploads/2019/10/2016-10.pdf

**Method.** Right foreleg amputated between mid-femur and the femur-tibia joint. Strains: Canton-S (WT), *nan³⁶ᵃ* (BDSC 24902), *iav³⁶²¹* (BDSC 24768). Flies 4–8 d post-eclosion. Open arenas 5.08 cm diameter; gait video of straight walking bouts at **60 Hz**. n: 50≤N≤56 WT, 16≤N≤17 *inactive*, 13≤N≤15 *nanchung* bouts per time point.

## Turn bias (µ score) — verbatim from Results
> "For wild-type animals, we find that on average they start unbiased before amputation (μ = −0.006), develop a very strong bias immediately post-amputation (μ = −0.410), and steadily recover towards an unbiased state over the next 3 days (μ = −0.031)."
> *inactive*: μ = −0.026 pre, −0.247 day 0, **−0.129 at day 3** (still P<0.001 vs pre).
> *nanchung*: **μ = −0.250 at day 3**, no recovery (day 3 ≈ day 1).
> WT day 3 vs pre: **P = 0.372** (not significant) — full recovery.

## Speed
Immediately post-amputation speed fell by **34% (WT), 14% (inactive), 56% (nanchung)**. Never returns to baseline in 3 days. WT slope over days significantly positive (P = 0.001); inactive P = 0.741, nanchung P = 0.116.

## Gait (hidden-Markov 1-leg / 2-leg / 3-leg states)
3-leg (tripod) frequency drops to near 0 immediately post-amputation in all genotypes and does not recover (P > 0.060). WT alone shows plasticity: significant increase in 2-leg gait (P = 0.003). Mutants: no change (P > 0.647).

## Gait parameters fitted from WT pre-amputation video (Table 1) — **directly usable Drosophila numbers**
- Excitation pulse (stride) frequency **ω = 11.4 ± 1.8 strides/s**
- Duty factor per leg δ = **[0.62, 0.70, 0.66, 0.65, 0.70, 0.68] ± [0.07, 0.06, 0.06, 0.07, 0.06, 0.06]**
  (legs 1–3 = left front/mid/hind; 4–6 = right front/mid/hind)
- Swing-onset phase relative to leg 1, in cycles: φ = **[0, 0.58, 0.17, 0.48, 0.13, 0.60] ± [0, 0.07, 0.07, 0.06, 0.07, 0.09]**
- Model units: **body length unit = 2.5 mm; body mass unit = 0.25 mg**
- Leg-body attachment y positions: **+0.20 (front), 0 (mid), −0.11 (hind)** b.l.u.; x = ±0.05 b.l.u.
- Relaxed leg lengths ℓ*: **0.59 (front), 0.66 (mid), 0.42 (hind)** b.l.u. = 1.48 / 1.65 / 1.05 mm
- Relaxed leg angles θ*: 1.19 / 0.33 / 0.69 rad (front/mid/hind; sign extraction ambiguous from PDF)
- Relaxed endpoints (×ℓ): x* 0.27 / 0.67 / 0.37; y* 0.75 / 0.21 / 0.37 (signs ambiguous)
- Body width **0.34 b.l.u.**; inertia **0.01 b.m.u.·b.l.u.²**; translational and rotational damping **1.5** each (over-damped)
- Leg and neuron relaxation time constants **τ_L = τ_N = 10 ms**; neuron threshold n̂ = 0.9 a.u.; max stretch ratio 2
- Integration step h = 0.001; converges after 2–3 strides to **~0.65 body lengths per stride** (≈7.4 BL/s ≈ 18.5 mm/s at ω = 11.4 Hz)

## Torque model
Torque of leg i about the body: **m_i = (x_i − X)·f_iy − f_ix·(y_i − Y)**, with leg force applied only while the neuron is below threshold, rotated into world frame by R_Θ.

## The force-redistribution result
- With per-leg forces **held constant**, no genotype recovers turn bias — "if anything, all three lines exhibited increased bias with time."
- With force tuned by simulated annealing (1.5×10³ steps), the recovery trajectory is reproduced to **mean discrepancy <1%**.
- Sweeping force one leg at a time (Fig. 6B): **the middle leg requires the least force change to hit a given turn-bias target, then the hind leg, then the front leg** — i.e. per unit force, midlegs have the greatest yaw leverage. Required right/left force ratio spans roughly **0.7–1.0** during recovery.
- Recovery significant for all legs in WT (P < 0.038 / P < 0.03, F-test); in mutants, only the *inactive* front leg has a significantly positive slope (P < 0.001).
- Leg placement alone is insufficient: WT front-leg centroid distance changed **<1%** between day 0 and day 3.
- Explicitly contrasts with the cockroach division of labour (Mu & Ritzmann 2005: front legs steer, hind legs propel) — not sufficient to explain fly recovery.

## Verified
Everything above read directly from the PDF (pdftotext). Signs of θ* and the relaxed-endpoint coordinates are the only items degraded by PDF extraction.
