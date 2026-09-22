# Szczecinski, Zill, Dallmann & Quinn 2020 — conference version of the CS model

**Citation.** Szczecinski NS, Zill SN, Dallmann CJ, Quinn RD (2020). "Modeling the Dynamic
Sensory Discharges of Insect Campaniform Sensilla." In: *Biomimetic and Biohybrid Systems,
Living Machines 2020*, LNCS vol. **12413**, pp. **342–353**. Springer, Cham.
DOI 10.1007/978-3-030-64313-3_33. PDF: https://par.nsf.gov/servlets/purl/10202934
(Citation form confirmed against the reference list of Harris et al. 2022, PMC9529259.)

⚠ **The letters mean different things here than in the 2021 journal paper.** Use the 2021
values (see `szczecinski_2021.md`) for implementation; this file exists so the two are not
confused.

```
y  = max(0, a·(u − x) + b·u + c)          (their eq 11)
τ·ẋ = sign(u − x)·|u − x|^d                (their eq 12)
```
"y is the instantaneous firing frequency (Hz) of afferent nerves from a population of CS;
u is the instantaneous loading (mN) of the limb segment in the CS population's [field]".

## Table 1 (verbatim) — cockroach *Periplaneta americana* tibial CS

| Parameter | Description | Value |
|---|---|---|
| a | Adaptation term scale | 1088 |
| b | Proportional term scale | 40.45 |
| c | Constant offset | −52.84 |
| d | Exponent in low-pass filter function, f(z) = z^d | 2.369 |
| τ | Time constant for ẋ | 2.668 × 10³ |

⚠ τ is printed **without a unit**. The 2021 refit gives τ in ms of order 1.7–9.7 ms, so
2.668 × 10³ is presumably 2.668 × 10⁻³ s. Reported here exactly as printed.

## Stimulus protocol used for tuning

Hold amplitude **1.66 mN** for all stimuli. Ramp durations **0.125, 0.224, 0.456, 0.915 s**.
Each applied to the tibia **11 times**. Ramp phase split into **20 bins**; spikes per bin →
mean afferent firing frequency. Each "dataset" = 20 time points × 20 frequency samples
averaged over 11 repetitions. Naturalistic force waveforms from freely walking insects also
applied (Dallmann et al. 2016).

## Derivation stated compactly

`Δt = (T/A)·f⁻¹(τ·A/T)`; `x(t) = u(t − Δt)`; `y = a·f⁻¹(τ·u̇)`.
Special case f(z) = z ⇒ f⁻¹(z) = z ⇒ Δt = τ, a fixed lag independent of ramp rate.
The nonlinearity d > 1 is exactly what makes Δt rate-dependent and produces the power law.
