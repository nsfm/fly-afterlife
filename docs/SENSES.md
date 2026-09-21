# his senses: what he has, what we drive, what we could

status as of 2026-09-17 evening (nyx); the antenna row and the units note added 09-19 16:15. cell counts are from the MaleCNS build (`brain_whole.npz`);
"in life" is from the physiology briefs in `docs/physiology/`. "driven" means a registry row exists
and fires in the room today. the floor (`receptors.FLOOR`) holds every typed sense at its resting
rate by default; a sense is "active" when the world also modulates it.

## the sample points, and the units

1 sim m = 15 mm (`docs/BENCHMARKS.md`; his body 0.16 m = 2.4 mm). the antennae are the sample points for odour, warmth
and humidity (`Body.antennae_at`). the original geometry put them 0.1 m ahead and 0.15 m to each side: 4.5 mm apart,
twelve times a fly's ~0.35 mm (head ~0.7 mm wide), straddling the plume, which is 3.75 mm wide at the source. so his
bilateral smell difference was far larger than any fly's, and the fruit plume's whiff state is one coin per source
shared by both antennae, so the between-antenna delay that odour-motion sensing lives on (Kadakia 2022) is zero by
construction. `pair.py --antennae real` puts them at the front of the head, 0.35 mm apart (09-19 16:15; a fly can
lateralise at that spacing: Gaudry 2013, Taisz 2023; in a turbulent plume it mostly reads whiff timing and the wind:
Alvarez-Salvado 2018, Demir 2020). the result of the re-run is in the record.

## driven by the world today

| sense | cells | what it encodes in life | how we drive it | fidelity | source |
|---|---|---|---|---|---|
| vision, motion | his T4/T5 (~10,000 of 4,107 photoreceptor columns' worth) | direction-selective motion, both eyes | flyvis (graded, trained) sees through a raytraced compound eye on his real geometry; its T4/T5 become Poisson rates on his T4/T5 cells | good for motion; DS ~1/3 of flyvis at the transplant; loom detection not carried | SEAM.md, the seam sections |
| touch, bristles | 2,503 tactile | contact and deflection by body part | adapting kernel: 200 Hz onset, tau 30 ms, 20 Hz plateau, half the patch, re-triggered each step; left / right by the side of the wall, pillar or her | shape right; by body part not yet; fatigue not yet | mechanosensation brief; Corfas & Dudai 1990 |
| contact pheromone | ppk23 F 108 + M 108 | her cuticle (F) / a male's (M) on a tap | 60 Hz burst, tau 300 ms, both channels, on contact onset with her | shape right; M channel has no rival to fire for | chemo brief; Kallman 2015; Kohatsu 2011 |
| fly odour | Or47b / Or88a (262) | fly cuticular volatiles | exp(-d / 0.8) from her position at each antenna | smooth, not a plume; no running-mean normalisation | chemo brief s.1 |
| cVA (hers) | her Or67d | male pheromone | exp(-d / 0.8) from him at her antennae | as above | |
| temperature | hot 7, cooling 7 | absolute T (hot, exponential, Q10 4.4); rate of cooling (cooling, phasic, 95 Hz rest) | `HotCells`, `CoolingCells` from the temperature at each antenna tip; warm / cold corners | rates and time course from Budelli 2019 | chemo brief s.4 |
| the walking command | DNp09 (2) | forward walking (state-dependent) | tonic 100 Hz (`--walk`) | a constant standing in for a state | leg motor brief; Bidaye 2020 |
| the brake | AN19A018 (12); since 09-18 DNg105 (2), a MEASURED halting DN of this model (heaviest onto leg MNs by synapse count, halts the woken cord), not a named one (not in Sapkal 2024's set; no published function; audit 23:10) | halting by co-contraction | opt-in on contact (`--stop-at-her`): did nothing, contact too brief | needs a persistent state to hold it | Sapkal 2024 |
| leg proprioception | 580 leg-nerve cells | joint angle, load, stance / swing per leg | opt-in tripod gait rule (`--proprio`), phasic per leg by segment and side; floor 15 Hz standing | tonic load term is the wrong shape (campaniforms encode dF/dt); hook FeCO gating not applied | mechanosensation brief; Dallmann 2025 |

## held at rest by the floor, not yet modulated by the world

| sense | cells | resting rate used | what would modulate it | how hard |
|---|---|---|---|---|
| olfaction, all other ORNs | 2,635 in 53 types | 8 Hz (Or67d 0.12, Or65a 0.5) | odour sources with intermittent plumes (power-law whiffs), Weber-Fechner normalisation; food, her, a rival | a plume model in `world.py` + the `WeberFechner` transducer: a day |
| taste | 1,416 gustatory (sugar, bitter, water, salt, pharyngeal) | 2 Hz | a food spot (sugar ~65 Hz at 100 mM, adapting within 1 s), water, salt | a field + rows: half a day (forage mode in `loop.py` did sugar patches already) |
| humidity | 66 (dry VP4, moist VP5; VP1d, VP1l) | 20 Hz | a humidity field; dry / moist non-adapting | easy; VP1 labels under audit |
| Johnston's organ | 672 (JO-A/B sound, C/E gravity and wind) | 5 Hz (estimate) | wind: ON (`--wind on`, default); gravity: ON since 09-21 (`--tilt on`: roll and pitch deflect the aristae onto the same JO-C/E rows, `--tilt-jo`); song never yet | song rows exist; gravity and wind share cells, as in life |
| ocelli | OCG / OCC 46 interneurons; **the photoreceptors are not in the volume** (09-19 16:30: the 39 cells entering by the ocellar nerve are vertex bristles, 25 untyped bristle-like cells and the four DNx02, and none of them touches an ocellar interneuron; the 23,320 synapses onto OCG / OCC all come from typed brain cells, so the retinal input, made in the plexus under the cuticle in life, was never imaged) | 40 Hz in the dark x (1 - sky light), DEFAULT ON since 17:35 (`--ocelli off` to silence) | ambient light level, horizon | a labelled stand-in on the interneurons, BUILT 16:51 (`receptors.OcellarL`, `Garden.sky_light`): in life the L-neurons are tonic in the dark and hyperpolarised by light (histaminergic receptors), so OCG rate ~ (1 - sky light); OCG01a/c/f glutamate, the rest acetylcholine, OCC unclear (consensus_nt). an afternoon, as a stand-in; there is nothing upstream to label |
| colour | R7 / R8 (in the 4,107) | 0 (flyvis is monochrome) | a coloured world | needs the transplant with R7/R8: the eye track |

## silent, correctly

| sense | cells | why silent |
|---|---|---|
| haltere proprioceptors | 396 (DMetaN) | halteres do not oscillate while walking (Hall 2015) |
| wing sensors | 237 (ADMN) | he does not fly |
| his own photoreceptors R1-R6 | most of 4,107 | flyvis sees for him; driving them in the LIF computes nothing at 0 Hz rest |

## silent, unknown

| class | cells | note |
|---|---|---|
| unknown_sensory | 986 | untyped |
| chemosensory (other) | 48 | untyped further |
| bristle subtypes by body part | within the 2,503 (BM_Hau, BM_Vib, BM_InOm, BM_MaPa, BM_Taste ...) | typed; we drive them as left / right only |

## internal states he does not have

hunger, thirst, sleep, arousal, the loser effect, courtship persistence (pCd): all states on
neuromodulators (octopamine 37, serotonin 8, the PAM / PPL1 dopamine sets) that this model holds
only as instantaneous drive. nothing persists longer than a stimulus. this is the next build
after the world.

## the world he is in, and the one he should be in

today: a 4 x 4 m room, floor 0.4, walls 0.6 one metre high, sky 0.8, two pale pillars, her at
0.1, an optional warm or cold corner, fly odour from her. grey on grey: the visual wheel has
almost nothing to steer by except the pillars and her.

an enriched world (proposed 09-17 evening, nate): a floor with texture (a real floor plane in
both raytracers with an albedo pattern), walls with structure, objects of several sizes and
tones, a sky with a light direction, a food spot with sugar and an odour plume, a water spot
with humidity, the warm corner, her, and later a rival. every one of those is a sense he has
and we hold at rest. the enriched world is the next build; the rival after it.
