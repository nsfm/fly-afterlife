# Goldsmith, Szczecinski & Quinn 2020 — fCO afferents in a neuromechanical joint model

**Citation.** Goldsmith CA, Szczecinski NS, Quinn RD (2020). "Response of a Neuromechanical
Insect Joint Model to Inhibition of fCO Sensory Afferents." *Living Machines 2020*
(9th Int. Conf. on Biomimetic and Biohybrid Systems, Freiburg), LNCS **12413**:141–152.
Springer. DOI 10.1007/978-3-030-64313-3_15. PDF: https://par.nsf.gov/servlets/purl/10202932
Read in full from the NSF-PAR PDF.

Subject: stick insect femur-tibia (FTi) joint control network and reflex reversal
(resistance reflex ↔ active reaction), targeted at **Drosophibot**, a robot modelled on
adult *Drosophila melanogaster*.

## The key negative result for encoder work (verbatim)

> "As the exact conversion between **fCO stretch and injected current has not been
> characterized**, we arbitrarily chose a stimulus strength of **5 nA** applied to the
> sensory neurons over 3.25 seconds. The stimulus ramps up to and down from the hold current
> over a period of 0.25 seconds."

Also: "Because Drosophibot is about 5 times larger than the stick insect, the length of the
stimulus was made about 5 times longer."

So as of 2020 there was **no calibrated joint-angle → fCO-afferent-activity function** in the
literature. Nothing I found since fills that gap for *Drosophila*.

## Structure they do commit to

- fCO sensory neurons split into **four groups**: flexion-position, flexion-velocity,
  extension-position, extension-velocity. Half the afferents respond to fCO **elongation**
  (= tibia flexion), half to **relaxation** (= extension).
- Each sensory neuron carries "an arbitrary tonic noise of **0.01 mV**" to give slight
  variance across the group.
- Six spiking interneurons mediate **delayed inhibitory** input from the velocity neurons
  onto the non-spiking interneurons (NSIs), which also get direct excitation from position
  and velocity sensory neurons.
- Only the **slow muscle fibres** are modelled, each driven by one slow motor neuron.

## Equations

Non-spiking leaky integrator NSIs:
```
C_m dV/dt = I_leak + I_syn + I_app          (eq 1)
I_leak    = G_m·(E_r − V)                    (eq 2)
```
Sensory neurons and motor neurons: same, integrate-and-fire, with
```
if V = θ, then V(t) ← E_r                    (eq 5)
```
Synapse: on a presynaptic spike G_s ← G_max, then
```
τ_s dG_s/dt = −G_s                           (eq 6)
```
Muscle-fibre analog: an extra non-spiking neuron after the slow MNs with time constant
**2000 ms** ("so the neuron acts as a leaky integrator of synaptic inputs similar to a
muscle").

Limb mechanics:
```
J·θ̈ = τ_ext + τ_flex − k_spring·θ            (eq 7)
```
J = moment of inertia, k_spring = stiffness of the limb's parallel elastic elements.

Synaptic conductances set from "the relative values given in Figure 11 of ref. [13]"
(Sauer et al. 1996), tuned to match the recorded NSI responses.
Flexor half-network built by **mirroring** the extensor connectivity, justified by Bässler's
finding that extensor and flexor tibiae forces vary in nearly equal and opposite ways under
sinusoidal fCO stimulation.
