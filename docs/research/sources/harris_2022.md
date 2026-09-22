# Harris, Szczecinski, Büschges & Zill 2022 — CS model applied to unloading

**Citation.** Harris CM, Szczecinski NS, Büschges A, Zill SN (2022). "Sensory signals of
unloading in insects are tuned to distinguish leg slipping from load variations in gait:
experimental and modeling studies." *Journal of Neurophysiology* **128**(4):790–807.
DOI 10.1152/jn.00285.2022. PMC9529259. CC BY. Read from the Europe PMC full-text XML.

## Why it's here

It reuses the Szczecinski et al. 2021 CS model **verbatim** and shows it reproduces
responses to force *decreases* (unloading) and cuticular viscoelastic creep. It adds no new
parameter table, but it gives the most useful plain-language framing of the model.

Model restated in the paper (verbatim):
> "the discharge frequency, y, is a function of the instantaneous force applied to the
> tibia, u, and the low-pass filtered force, x: **y = max[0, a·(u − x) + c·u + d]**, where a
> scales the adaptive term (u − x), c scales the tonic term u, and d is a constant offset.
> The low-pass filtered force variable x functions like a **dynamic threshold** and is
> calculated via the following differential equation: **τ·dx/dt = sign(u − x)·|u − x|^b**.
> In short, x is driven to the value of u over time, with x changing more slowly as it
> approaches u."

And the honest caveat (verbatim):
> "Because none of the model parameters (e.g., a, b, c, and d) relate to specific mechanical
> or electrochemical processes, this model is **descriptive, not mechanistic**."

## Substantive additions

- The model's adaptive variable x exhibits "**creep** like that measured in the animal's
  cuticle": as each force stimulus lengthens, x progresses further from its resting value of
  0, and the discharge at unloading grows with hold duration — matching the animal.
  "the model incidentally mimics the material properties of the animal."
- Simulated 6A CS fires **bursts of action potentials when the force stimulus ends**
  (unloading response), as observed in stick insect group 6A; 6B and cockroach proximal
  receptors instead cease immediately on force decrease.
- They note the parameter values for the creep simulations are not calibrated because
  "the value of the cuticle stiffness (elastic modulus) ... has not been determined for
  these data."
- Experimental design detail: stick insect groups 6A/6B are **spatially separated** on the
  proximal tibia, whereas in cockroaches the homologous distal/proximal subgroups are
  adjacent.

## Related, same series

- Zill SN, Dallmann CJ, Szczecinski NS, Büschges A, Schmitz J (2021). "Evaluation of force
  feedback in walking using joint torques as 'naturalistic' stimuli." *J Neurophysiol*
  **126**:227–248. DOI 10.1152/jn.00120.2021. PMC8424542.
- Zill SN, Dallmann CJ, Zyhowski WP, Chaudhry H, Gebehart C, Szczecinski NS (2024).
  "Mechanosensory encoding of forces in walking uphill and downhill: force feedback can
  stabilize leg movements in stick insects." *J Neurophysiol* **131**:198–215.
  DOI 10.1152/jn.00414.2023. PMC11286306.
