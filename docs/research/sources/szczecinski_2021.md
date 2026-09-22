# Szczecinski, Dallmann, Quinn & Zill 2021 — the campaniform sensilla encoding model

**Citation.** Szczecinski NS, Dallmann CJ, Quinn RD, Zill SN (2021). "A computational model
of insect campaniform sensilla predicts encoding of forces during walking."
*Bioinspiration & Biomimetics* **16**(6):065001. DOI 10.1088/1748-3190/ac1ced.
Received 31 Mar 2021, accepted 12 Aug 2021, published 7 Sep 2021.
Code: https://github.com/nss36/campaniformSensillaModeling
Read in full from the IOP PDF (session scratchpad, `szcz2021.pdf`).

Species: cockroach *Periplaneta americana* (proximal tibial CS group) and stick insect
*Carausius morosus* (tibial groups 6A and 6B). **Not Drosophila.**

## The model (verbatim)

```
y  = max(0, a·(u − x) + c·u + d)          (eq 1)
τ·ẋ = f(u − x)                            (eq 2)
f(z) = sign(z)·|z|^b                       (eq 8)
```
`u` = stimulus force on the tibia (mN). `y` = discharge (AP/s). `x` = adaptive variable.
f must be monotone increasing with f(0)=0 ⇒ the only equilibrium is x = u, at which
y relaxes to the tonic level c·u + d.

Abbreviation table (Table 1, verbatim): A = amplitude of bending force stimulus (mN);
T = duration of ramp phase (s); u = stimulus force applied to the tibia (mN);
x = model's dynamic variable; y = model discharge (AP/s).

## Why rate-sensitivity and power-law adaptation are emergent

For a ramp u = (A/T)·t:
- `x_ss = u(t − Δt) = (A/T)·(t − Δt)` (eq 3)
- `y_ss = a·(u(t) − u(t − Δt))` (eq 4) — a finite difference approximating u̇ when a = 1/Δt
- `Δt = (T/A)·f⁻¹(τ·A/T)` (eq 5) ⇒ `y_ss = a·f⁻¹(τ·A/T)` (eq 6) = `a·f⁻¹(τ·u̇)` (eq 7)
- with f(z) = sign(z)|z|^b, b = 1/k, this gives the empirical y ∝ u̇^k.

Step response is an exact power law in time:
`x(t) = B·((t + Δt)/τ)^s` (eq 11), `s = 1/(1 − b)` (eq 16),
`B = (b − 1)^(1/(1−b))` (eq 17), `Δt = τ·x₀^(1−b)/(b − 1)` (eq 18).
Requires s < 0, Δt > 0, sign(B) = sign(x₀).
⇒ **power-law adaptation from a first-order, integer-order ODE; no fractional derivatives.**

## Table 2 — fitted parameters (verbatim)

| Parameter | Cockroach prox. tibia | Stick insect 6A | Stick insect 6B |
|---|---|---|---|
| a — amplitude of adaptive term (Hz mN⁻¹) | 707.6 | 265.0 | 605.0 |
| b — exponent of adaptive term (unitless) | 2.262 | 1.675 | 3.325 |
| c — amplitude of proportional term (Hz mN⁻¹) | 54.29 | 17.75 | 5.750 |
| d — amplitude of bias term (Hz) | −41.16 | −22.50 | 10.50 |
| τ — amplitude of adaptive time constant (ms) | 3.859 | 9.678 | 1.659 |
| model tuned using single trial from | fig 3(a) | fig 7(a) | fig 7(b) |

Cockroach fitted by gradient MSE minimisation (MATLAB `fmincon`); stick insect 6A/6B by
genetic algorithm then gradient refinement. Dynamics simulated with `ode15s`.
Firing rate from spikes in a moving window, "typically 20 ms".

## Fractional-derivative comparison model

`y = max(0, a·D^b u(t))` (eq 19). Fitted to the cockroach ramp-and-hold of fig 3(a):
**a = 40.6, b = 0.631**.

MAE (AP/s), selected rows of Table 3:
| trial | nonlinear | fractional | improvement |
|---|---|---|---|
| fig 3(a) (tuning trial) | 4.85 | 5.56 | 0.71 |
| fig 3(b) (naturalistic joint torque, held out) | 9.87 | 16.22 | 6.35 |
| fig 7(a) 6A | 6.49 | 6.11 | −0.38 |
| fig 7(a) 6B | 47.3 | 69.8 | 22.5 |
| fig 7(b) 6A | 5.58 | 5.59 | 0.01 |
| fig 7(b) 6B | 65.0 | 60.3 | −4.70 |
Nonlinear wins 12 of 18 listed trials.

## Power-law rate exponent k (peak discharge vs ramp rate, log-log slope)

- varying stimulus amplitude: animal **0.28–0.57**, model **0.27–0.46**
- varying tonic offset: animal **0.34–0.43**, model **0.25–0.38**
(animal values from Ridgel et al. 2000)

## Notes for reuse

- CS come in **antagonistic pairs**; the paper's two-group inversion feeds the second group
  the sign-flipped stimulus (−u). ⇒ two units per site: y⁺ = model(u), y⁻ = model(−u).
- a and c have units Hz·mN⁻¹ ⇒ u must be in mN.
- τ is 1.7–9.7 ms and |·|^b with b > 1 is stiff near x ≈ u; integrate with small dt.
- Downstream re-users describe x as "a **dynamic threshold**" (Harris et al 2022) and note
  the model is "**descriptive, not mechanistic** — none of the model parameters (a, b, c,
  and d) relate to specific mechanical or electrochemical processes".
