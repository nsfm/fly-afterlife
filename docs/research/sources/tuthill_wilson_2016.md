# Tuthill & Wilson 2016 — the two 2016 papers

## (A) Tuthill JC, Wilson RI (2016). *Parallel transformation of tactile signals in central circuits of Drosophila.* **Cell 164:1046–1059.** doi:10.1016/j.cell.2016.01.014
**Status: VERIFIED — full PDF incl. supplemental methods read.**
(Note: the brief called this "Cell 164:759–774" / "Neuron"; the correct pages are **1046–1059**,
Feb 25 2016. Cell 184:759–774 is Phelps et al. 2021 = FANC.)

### Bristle neuron facts
- **One sensory neuron per bristle.** "A single neuron resides at the base of each bristle."
- "Mechanical stimulation of the bristle can evoke **intense spiking activity** within the bristle
  neuron" — *qualitative only; the paper gives no number for peak bristle-neuron firing rate.*
- Bristle neurons are **directionally selective** — respond most strongly to deflection in one
  direction set by the asymmetric orientation of the hair socket (cites Burrows 1996; Corfas &
  Dudai 1990). All recordings here used the preferred direction = the one that reduces the acute
  angle between bristle and cuticle.
- Bristle axons terminate in **the most ventral layer of the VNC neuropil** and form a topographic
  map there. Hair plate, campaniform and chordotonal (proprioceptive) axons terminate **more
  dorsally / in intermediate layers** — a clean laminar separation of exteroceptive from
  proprioceptive input.

### ⭐ CONDUCTION DELAY AND VELOCITY (the one hard timing number I found for Drosophila leg
### mechanosensation) — Fig. S6A, VERIFIED
> "we measured a consistent delay of about **3 ms** from the time of a femur bristle neuron spike
> in the periphery to the onset of an EPSP in the VNC… The distance from the femur bristle to the
> VNC is approximately **850 µm**, suggesting that the conduction velocity is **0.28 m/s**, assuming
> a negligible delay for synaptic transmission."
> "This delay is presumably even longer for mechanosensory signals arising from the distal leg,
> since the axons of **tarsus bristle neurons can be over twice as long** as the axons of femur
> bristle neurons." ⇒ implies ≳6–7 ms for tarsal bristles.
(The PDF's text layer renders µm as "mm"; the stated 0.28 m/s is unambiguous.)

### Latency budget for insect mechanosensory reflexes (intro, cited to other insects)
- Whole reflex, stimulus → behavioural response: **20–30 ms** (Jindrich & Full 2002, cockroach;
  Schaefer et al. 1994).
- Mechanosensory transduction + axonal conduction: **6–8 ms** (Höltje & Hustert 2003;
  Ridgel et al. 2001). ⚠ NOT Drosophila.
- Muscle force-production kinetics: **10 ms** (Ahn et al. 2006). ⚠ NOT Drosophila.

### Other verified numbers
- **69 of 699** identifiable neuronal somata in the anterior VNC showed calcium bursts significantly
  correlated with optogenetic bristle stimulation (authors call this a lower bound).
- Optogenetic light spot on the leg ≈ **200 µm** diameter, encompassing **20–80 bristles** depending
  on location (bristle density from Hannah-Alava 1958).
- Recording: extracellular, clipped bristle + glass pipette with high-K⁺ mechanoreceptor-lymph-mimic
  saline (NaCl 9 mM / KCl 121 mM); band-pass 100–400 Hz; digitized 10 kHz.
  Mechanical stimulus: closed-loop piezo (PI P-841.60, **90 µm travel range**).
  Bristle used: second-most-distal bristle on the posterior femur, clipped to ~25% length.
- Central (2nd-order) neuron spike rates, from figure axes: y-axis maxima of **5, 8, 10 and 15
  spikes/s** across panels (Figs. 4B/E, 5B/E, 6). So **downstream VNC neurons fire at single-digit
  to ~15 spikes/s** in response to bristle stimulation. Figure-read, not quoted in text.
- Three classes of 2nd-order VNC neurons downstream of one femur bristle: (1) intersegmental
  ascending, (2) midline local, (3) a third class; one compares touch within a limb, one across
  limbs, one compares touch vs proprioception. GABA-B antagonist CGP54626 used to test inhibition.
- **Proprioceptive inhibition**: chordotonal (FeCO) activation *inhibits* the spike rate of central
  touch neurons (Figs. 4D-E) — i.e. touch gain is modulated by leg position.

---

## (B) Tuthill JC, Wilson RI (2016). *Mechanosensation and adaptive motor control in insects.* **Curr. Biol. 26:R1022–R1038.** doi:10.1016/j.cub.2016.06.070
**Status: VERIFIED — full PDF read.**

### Hair plates
> "In Drosophila, hair plates can be found at **most leg joints** but **have not been identified on
> the antenna**." (cites Murphey, Possidente, Pollack & Merritt 1989; Merritt & Murphey 1992)
> "Like a tactile hair, **each individual sensillum within a hair plate is innervated by a single
> sensory neuron**. Hair plate sensilla occur as **two physiological types: rapidly adapting neurons
> that respond phasically to hair movements and slowly adapting neurons that respond tonically to
> maintained deflections**." ⚠ the rapid/slow dichotomy is cited to **locust** work
> (Newland, Watkins, Emptage & Nagayama 1995 J. Exp. Biol. 198:2397–2404, and French & Sanders),
> **not** Drosophila. Pratt et al. 2026 later found **no phasic component** in Drosophila CxHP8.
- Hair plates sit at folds in the cuticle so they are deflected during joint movement; they can also
  be **exteroceptive** (cockroach antennal hair plates do object localisation — Okada & Toh 2000).
- ⚠ **Cockroach**: "a hair plate at the most proximal leg joint provides **direct excitatory input
  to extensor motor neurons of the trochanter and indirect inhibitory input to the motor neurons
  that control flexion**. **Ablation of this hair plate causes the leg to overstep and collide with
  the more anterior leg**, indicating that proprioceptive signals from the hair plate limit the
  forward movement of the leg during the swing phase." (Pearson, Wong & Fourtner 1976;
  Wong & Pearson 1976, J. Exp. Biol.)
- ⚠ **Fly neck (not leg)**: two hair plates on the ventral neck form the **prosternal organ**, which
  encodes head rotations about all three axes; shaving the hairs on one side makes the fly roll its
  head toward the operated side.

### Campaniform sensilla (context only — other agent owns this)
> "**Approximately 1200 campaniform sensilla** are distributed over the legs, wings, halteres, and
> antennae of the fly" (their ref 59). Two physiological categories: rapidly and slowly adapting.
- Wing and haltere CS each fire **a single action potential at a unique phase within a wing stroke
  cycle**, which in Drosophila lasts about **4–5 ms**.
- Directional selectivity from the elliptical dome, first recognised by J.W.S. Pringle (1938).
  ⚠ **Cockroach tibia**: proximal-cluster CS respond maximally to **dorsal** tibial movement,
  distal-cluster CS to **ventral** movement.

### Bristles
- Bristles are the primary external mechanoreceptors; **stimulation of just one or two bristles is
  sufficient to trigger complex grooming sequences**, and grooming is precisely targeted to the
  stimulated site (locust: Vandervorst & Ghysen 1980; Seeds/Simpson work).
- ⚠ **Locust**: mechanosensory neurons within taste hairs are **directionally selective and rapidly
  adapting**, with a **lower mechanical threshold than purely tactile hairs**. "Their response
  properties in Drosophila are not known."

### Central projections
> Bristle neurons arborize in the **ventral** region of the VNC; proprioceptive organs (hair plates,
> campaniform sensilla, fCO) project to **intermediate layers**; "hair plate axons terminate in a
> more dorsal region."
