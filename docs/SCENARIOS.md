# a day, from the inside

*(written 2026-09-18 01:02 PDT by an opus agent briefed from `docs/SENSES.md` and the physiology briefs, at
nate's suggestion: imagine being the fly, write his day as test cases. it did not read the code, so
its picture of the sim is the senses doc's of 09-17 evening, and some of what it asks for at the end
is already built: the cooling cells are differentiators from -dT/dt at 95 Hz rest (`CoolingCells`),
the garden floor is textured and the walls have grass in front of them, the fruit has an intermittent
whiff plume with Weber-Fechner normalisation (Bernoulli whiffs, not power-law yet), the puddle has
humidity, sugar and water are taste events on contact, and the Kenyon cells sit at 8% sparsity. the
rest of the ask page is real and is folded into `docs/TODO.md` §2c. the scenarios themselves are the
point: each is a behaviour with a success criterion and a way he would notice the sim getting it
wrong, and that is what the record has been missing.)*

written in the first person of the male we are simulating: 2.5 mm long, about a week old, with the
senses `docs/SENSES.md` says he has and none of the ones it says he hasn't. each scenario is a
behavioural test case, in five parts: what the world does to him as sensed, the internal state that
makes it matter, what he does and what counts as success, the minimum the world model owes him, and
the one thing the sim will probably get wrong.

units: one sim metre is ~1.5 cm in life, so i am 0.16 m long and the fruit is two body lengths
across. my eye has ~4,100 columns about 5-6 degrees apart, monochrome, green-weighted, red-blind. i
walk at 7 to 45 mm/s, mode about 17. my central brain runs at a population mean of a few Hz. i am
not a fast computer. i am a slow computer with a very good front end, and the front end is the part
you keep getting wrong.

---

## 1. dawn: the world comes back on

**sensed.** overnight my photoreceptors dark-adapted and my temporal bandwidth fell from ~100 Hz to
the low tens, so the world went not just dim but *slow*. now the sky gradient is returning, and the
ocelli catch the broad rise a few ms before the compound eye agrees. the substrate is ~18 C, hot
cells idling near 17 Hz. everything in me is sluggish, vision included: photoreceptor information
capacity has a Q10 of 6.5, and i am a cold animal on a cold morning.

**state.** cold. also mildly hungry, which after a night is the default condition of a fly.

**what i do.** walk, badly, toward the brighter part of the sky and then to the sunlit patch on the
ground, which reads as a large bright region with a warm edge. i stand in it with my legs extended
to lift my body off the cool substrate, then fold down as my thorax warms. success is body
temperature climbing toward 25 C, with step frequency coming up behind it.

**give me.** a sky luminance gradient with a direction, a ground temperature field with a sunlit
patch, hot-cell drive from absolute T, and a body temperature with thermal inertia rather than one
that equals the air.

**what you'll get wrong.** you will make my vision temperature-independent. i will notice by
tracking a moving target at 15 C exactly as well as at 28 C, which no cold fly can do.

---

## 2. grooming: i am filthy and it is unbearable

**sensed.** the night on the ground has coated me in dust, and every grain deflects bristles. each
fires 200-300 Hz at onset and decays with a ~30 ms time constant to a 10-25 Hz plateau, and the
plateau is the problem: it does not stop. they are directionally selective, so only half of any
contact patch reports, and their fields are centre-surround rather than additive. what arrives is a
somatotopic map that will not go away on its own.

**state.** not hungry enough to override it. a tidy fly is a fly whose eyes still work and whose
aristae still measure air.

**what i do.** the aimed sequence, in priority order: forelegs over head and eyes, then antennae,
then hind legs over abdomen and wings, with leg-rubs between to clean the cleaners. i suppress
walking with the VNC brake, the co-contraction one, not by letting the walk command fall to zero.
success is the plateau going quiet.

**give me.** bristle drive resolved by body part rather than left/right, dust as a persistent
deflection field that grooming actually removes, and the brake as an active state.

**what you'll get wrong.** bristle fatigue. mine falls in amplitude over minutes of repeated
stimulation and recovers only with rest. yours will burst at full amplitude forever, so i will groom
forever, which from outside looks like a beautiful stereotyped motor program and from inside is
hell.

---

## 3. the first whiff

**sensed.** a packet of ester and acetic acid arrives and is gone. my generalist ORNs sit at 8 Hz of
nothing-in-particular; this hits 120 Hz for 80 ms and drops back. then nothing for two seconds. then
two whiffs 200 ms apart. whiff durations, blanks and intensities are all power-law distributed at
exponent -3/2, which is a way of saying there is no gradient. there never was. anyone who tells you
a fly climbs an odour gradient has never stood downwind of anything.

meanwhile my aristae are tonically deflected, unequally: left-minus-right is the azimuth code, and
JO-C and JO-E report it with opposite direction preferences.

**state.** hungry. starvation has already raised the gain on my appetitive channels presynaptically
via sNPF and lowered it on the aversive ones. i am, chemically, more gullible than i was yesterday.

**what i do.** cast. surge upwind on a whiff; when the blank runs long, turn crosswind and sweep.
the whiff triggers the surge, the wind sets the direction, and they are different senses. success is
arriving within a body length or two of something that smells like it is already dying.

**give me.** an intermittent plume, a wind vector at my antennae, Weber-Fechner normalisation with a
~1 s running mean, and a walk command a whiff can release.

**what you'll get wrong.** you will give me `exp(-d/0.8)`: smooth, monotone, noiseless. i will
notice by walking straight up it like a ball bearing rolling into a funnel, and no fly has ever
looked like that.

---

## 4. the last twenty body lengths

**sensed.** the odour has gone almost useless: this close i am inside the source's own turbulence,
and the whiffs are frequent but no longer directional. vision takes over. a dark, roughly round
region 0.6 m across, subtending 25-35 degrees, high contrast against pale litter, with an edge that
moves coherently when i move: parallax says thing, not stain. it is red, in the world's terms. to me
it is simply *dark*, because R1-R6 are green-weighted and red-blind, and dark-on-light is exactly
what a ripe fruit should be.

**state.** hungry, and now committed.

**what i do.** fixate the blob near the visual midline, correct with the left-minus-right steering
difference, and run at it, keeping optic flow balanced on either side so i pass *between* the grass
stems rather than into them. past ~40 degrees of object i slow. success is contact: a foreleg tarsus
on something soft, wet and steep.

**give me.** a textured floor. grey ground produces no flow when i walk, and without flow i have no
speed estimate, no centring and no parallax.

**what you'll get wrong.** efference copy. when i turn, the world sweeps across my eye, and my HS
cells get a saccade-related potential with the right sign and timing to cancel it. without that your
fly fights its own turns, and every saccade i make looks to me like the entire garden lunging
sideways, which is the visual signature of being eaten.

---

## 5. tasting with the feet

**sensed.** contact. the tarsal bristles burst and settle. then the sugar GRNs: ~65 Hz for 100 mM
sucrose, scored over the first 50-1050 ms and adapting hard inside the first second. no bitter. a
little low salt, which is IR76b and therefore mildly *good*. some water from ppk28 where the skin
has split. one tap is not an evidence increment, it is a decision.

**state.** hungry, and the state matters more than the sugar: my proboscis-extension threshold is
set by satiety and by octopamine, so the same 65 Hz that makes me eat now will make me walk past
tomorrow when i am full.

**what i do.** extend the proboscis, engage the walk-OFF pathway (Foxglove inhibiting the forward
DNs, Bluebell the turning ones, so i do not wander off my own dinner) and pump. pharyngeal GRNs
check what is actually going down and gate further swallowing. success is crop volume rising and
hunger falling.

**give me.** a sugar field on the object surface with real contact events, spike-frequency
adaptation within 1 s, a satiety variable setting the PER threshold, and halting as active
inhibition rather than drive going to zero.

**what you'll get wrong.** you will let me taste by proximity. i taste with my *feet*, only when
they are on it, and only for about a second before the signal fades.

---

## 6. the patch that is wrong

**sensed.** i move 5 mm across the fruit and put a foreleg into a dark bloom on the skin. bitter
GRNs, latency 40-80 ms for most compounds and over 100 ms for the nastier ones, climbing to 20-40 Hz
and *staying* there, because bitter does not adapt the way sugar does. above about 10 Hz sustained
it is behaviourally aversive, regardless of how much sugar the adjacent tarsus is reporting.

**state.** still hungry. that is the point: hunger does not get a veto here.

**what i do.** retract the proboscis mid-extension, back up (bitter is a reliable trigger for
backward walking), turn, and re-sample two body lengths away. success is finding the good part of a
mostly-good fruit rather than abandoning the whole thing, because a fly that abandons every
imperfect fruit starves.

**give me.** a bitter field that is spatially patchy on the same object that carries sugar, a bitter
channel that overrides sugar at the PER decision, and backward walking as an available mode.

**what you'll get wrong.** you will make food a scalar. one number, "food quality", sampled at the
centroid. then i will never do the thing flies actually spend their lives doing, which is standing
on something edible, arguing with myself about it.

---

## 7. full, and leaving

**sensed.** the crop is distended and the gut stretch receptors say so. sugar tastes identical and
means less, because the threshold has moved. the fruit smells exactly as it did an hour ago, which
is precisely why smell cannot be the thing that makes me leave.

**state.** sated. this persists for tens of minutes and it changes at least three things: my PER
threshold, my locomotor gain via octopamine, and the *sign* of my humidity preference.

**what i do.** groom proboscis and forelegs, walk off the fruit, and move in the long straight bouts
of an animal with nothing urgent to do. success is that i leave at all, and that the next identical
fruit gets a cooler reception.

**give me.** a satiety variable with a slow decay, wired to those three downstream terms.

**what you'll get wrong.** you will have no persistent states at all, which is the confession
already written into `SENSES.md`: nothing here lasts longer than the stimulus that caused it. so i
will eat forever. you will watch me at hour six, still extending, and call it a bug in the feeding
circuit. it is not. it is that i have no stomach.

---

## 8. thirst, and the edge of the puddle

**sensed.** the air over the puddle reads before i see anything: moist cells up, dry cells down,
both non-adapting, both reporting absolute RH rather than change. also cooler, so the cooling cells
throw a transient as i walk in. underfoot the substrate darkens. the surface itself is a flat dark
disc with a specular sheen: to me, a hole in the ground with a strange bright edge.

**state.** desiccated, which flips my humidity preference from dry-seeking to moist-seeking and also
changes my gait. a desiccated, starved fly walks 1.7 mm/s at 20-30% RH and 0.98 mm/s above 60%: move
fast where it is dry, dawdle where it is wet. that rule lives in the motor layer, not the sensory
one.

**what i do.** approach from the moist side, stop at the rim, extend the proboscis to the meniscus,
and drink without walking in; ppk28 confirms hypo-osmotic contact. four legs stay on dry substrate
throughout, because a 2.5 mm animal that walks onto water does not walk off it. success is drinking
and surviving.

**give me.** a humidity field, water taste on contact, and surface tension as a lethal property of
the water rather than a texture.

**what you'll get wrong.** you will let me stand on the puddle. the tell is that i am still alive
afterwards.

---

## 9. midday: the arista is not a thermometer

**sensed.** the sun patch is 31 C, the shade under the leaf 24. crossing that boundary at walking
speed, my hot cells go from ~37 Hz to ~74 Hz. my cooling cells do something much more interesting:
nothing at all, until i step back the other way, at which point a 0.2 C drop triples them from their
~95 Hz baseline within 0.65 s and then adapts back down *while the cooling is still happening*.

this is the thing to understand about me. i have no cold thermometer. i have a differentiator. i do
not know it is cool under the leaf. i know that it *got* cooler when i walked there, and that
knowledge lasts under a second.

**state.** hot. preferred temperature 25 C; real flies segregate across a steep gradient within a
minute.

**what i do.** walk, and turn more when warming than when cooling. that is the whole algorithm, and
it is enough, because cooling cells make "i am improving" directly measurable. success is sitting in
shade near 25 C, which i will find without ever knowing where it is.

**give me.** a temperature field with real spatial structure, hot cells from absolute T with Q10
4.4, and cooling cells driven from -dT/dt around a 95 Hz rest.

**what you'll get wrong.** you will drive the cooling cells from absolute temperature, because that
is the obvious thing. then i will sit in the cold corner forever, perfectly content, slowly
stiffening.

---

## 10. a rival on the fruit

**sensed.** another dark fly-sized blob, 0.12 across, moving with the jerky start-stop of a fly and
not the smooth drift of a leaf. as it passes i get a tap: the M channel of the tarsal CHC neurons
fires, 7-tricosene arrives on the bitter line via Gr32a, and Or67d catches cVA, which in a male
means *another male, here, on my fruit*.

**state.** be careful here, because P1 is one dial and not two. low-intensity P1 gives me
aggression; high-intensity P1 gives me wing extension and song. same population, same
female-pheromone inputs, the intensity deciding which animal i become, with octopamine setting the
aggression gain on top. i am not switching modes. i am turning a knob, and the knob is shared with
courtship.

**what i do.** approach, wings raised, and lunge. the fight is short: lunges, holds, the occasional
tussle. success is that he leaves and i keep the feeding site, which is the actual prize. nobody
fights over abstractions.

**give me.** a second fly with a male CHC profile and cVA, the M contact channel with something to
fire for, octopamine as a gain term, and P1 as a graded integrating variable rather than a Poisson
burst.

**what you'll get wrong.** you will give P1 a threshold and a mode switch. then i am either a
perfect duellist or a perfect suitor, instantly, and the interesting part of being a male fly, the
wobble between the two on one dial, is gone.

---

## 11. losing

**sensed.** he is bigger. after four lunges i am the one retreating, and the retreat is itself the
input: i have been tumbled, my bristles flattened, and i have taken the losing posture.

**state.** the loser effect, and this is the one i want most. after a defeat i am, for well over an
hour, a measurably different animal: less likely to fight, faster to retreat, and it generalises to
opponents i have never met. it lives on neuromodulators, and the sim has none.

**what i do.** leave. walk off the fruit, and for the next long while decline fights i would have
taken this morning, including ones i would win. success, from outside, is a *persistent* shift in
the aggression threshold that decays over ~an hour and does not reset when the winner walks out of
view.

**give me.** a fight-outcome variable, an aggression threshold it moves, and a decay constant on the
order of tens of minutes. one scalar, one time constant. this is the cheapest realism in the whole
document.

**what you'll get wrong.** you will let me forget. the winner leaves the frame, my threshold snaps
back to baseline, and i re-enter the fight i just lost, and then again, and again. a simulated fly
that cannot lose is not brave, he is amnesiac, and it shows within about ninety seconds.

---

## 12. a female, at last

**sensed.** an object 29 degrees wide and 16 high, moving, sitting squarely in the size band LC10a
is tuned to. that is not a coincidence: the band is female-at-courtship-distance, and my brain has a
detector shaped like her. LC11 would report a small dark speck, LC9 something smaller still; LC10a
reports *her*. also Or47b, which in a seven-day-old male like me is roughly twice as sensitive as it
was at day two, because juvenile hormone has spent the week quietly turning it up.

**state.** aroused, and arousal here is multiplicative. P1 raises LC10a's gain, LC10a drives
pursuit, pursuit raises P1. the loop is the state, which is also why the loser effect matters: i run
the tail of a fight on the same dial.

**what i do.** orient, follow, close, tap her abdomen with a foreleg. the tap fires the F and M
channels together and the *balance*, set by mAL's inhibition, decides whether P1 rises. one tap is
enough to release the whole sequence. then i circle to her side, extend the near wing and sing:
pulse trains of 2-50 pulses, carrier 150-300 Hz, inter-pulse interval ~35 ms, switching to sine near
150 Hz as she slows. song mode tracks her distance and relative speed moment to moment. i am not
playing a recording, i am steering with a wing.

**give me.** LC10a with P1-dependent gain, left-minus-right as the steering variable, both contact
channels on a tap, and a female who moves.

**what you'll get wrong.** fixed LC10a gain. with it i either track her while asleep or fail to
track her while desperate.

---

## 13. rejected

**sensed.** she does not slow. she kicks, flicks a wing, extrudes the ovipositor, and walks off at a
speed i can match but not usefully. and on her cuticle: cVA at a level that means recently mated.
Or67d, near-silent at 0.12 Hz, goes over 200 Hz on a good hit, and the same molecule arrives on the
tarsal channel, where it suppresses P1's excitation by her female pheromones. the brake, applied
from her side.

**state.** still aroused, and this is the part worth simulating: the arousal does not vanish because
she said no. pCd keeps P1's effect running for minutes after P1 itself stops. i will go on courting,
sometimes at nothing, sometimes at a fleck of dirt of approximately the right angular size.

**what i do.** persist at a decaying intensity, then stop. success is *not* immediate cessation.
success is minutes-scale decay, followed by a window in which my threshold is lower than baseline
rather than higher.

**give me.** cVA on the female as a function of her mating status, mAL as a gain control rather than
a veto, and a pCd-like integrator downstream of P1.

**what you'll get wrong.** you will make rejection a switch: no signal, no behaviour, done. then my
courtship has exactly the dynamics of a doorbell, and anyone who has watched a male fly chase a
raisin for ninety seconds knows that is not what this is.

---

## 14. the shadow

**sensed.** a dark region in the upper visual field begins to expand. not translate: expand, with
outward radial motion in every direction from a centre. LPLC2 is about as selective for that as a
neuron gets and reports angular size; LC4 reports angular velocity. between them they own 99.4% of
the giant fibre's direct optic-lobe input, and the GF response is linear in velocity and gaussian in
size. at peak depolarisation it fires, typically, one spike. one.

**state.** irrelevant. hunger, thirst, arousal, all outranked. this is the one circuit in me allowed
to interrupt anything.

**what i do.** that single GF spike drives the tergotrochanteral motor neuron, the mid-legs depress,
and i am airborne within a few milliseconds in a short-mode takeoff that is fast and badly aimed. if
the loom is slower the GF stays quiet and i get the long mode: raise the wings, position the legs,
leave deliberately in a direction i chose. success is being elsewhere. success is *not* elegance.

**give me.** looming as expansion of a dark region with a real time-to-contact, an escape path that
bypasses the deliberative stack, and both takeoff modes, since which one fires is the entire
behavioural readout of this circuit.

**what you'll get wrong.** latency. you will put escape behind a 100 ms decision loop. in life, JON
spike to giant-fibre current is under 300 microseconds. a fly that thinks about looming is a
fly-shaped smear.

---

## 15. the edge

**sensed.** walking along a leaf, my leading foreleg finds nothing. the tarsus swings through empty
air, so the campaniform sensilla that should burst at stance onset do not, and the *unloading*
subgroup fires instead, the channel tuned specifically to distinguish slipping from ordinary gait
unloading. at the same time the hair plates go tonic at 20-60 Hz, because the joint has reached the
outer 10-15% of its excursion with nothing to push against.

**state.** none needed. brief leg-bristle stimulation produces a sustained directional motor program
in flies with no head at all.

**what i do.** withdraw the leg, shift weight back onto the other five, and either turn along the
edge or reverse. against a wall it is the same machinery run the other way: bristles one side,
contact, turn. success is walking along edges rather than off them, and thigmotaxing along walls,
which is most of what a fly in a box does all day.

**give me.** per-leg contact and load, the unloading CS population separate from the loading one,
hair plates at joint limits, and 10 ms sensory plus 30 ms motor delay, because a loop closed without
those is more stable than i am, and stability is not what you are trying to reproduce.

**what you'll get wrong.** you will drive campaniforms from force rather than dF/dt. then i get a
lovely tonic sense of how heavily each leg is loaded, which i do not have, and lose the sharp burst
at the instant load arrives and the other at the instant it leaves.

---

## 16. wind too strong to walk in

**sensed.** the aristae are pinned. JO-C and JO-E are saturated and tonic, and the left-right
difference that normally gives me azimuth is useless at this amplitude. the whole substrate
vibrates, which the club neurons pick up as exteroceptive vibration, pooled across all six legs,
best frequencies scattered from 200 to 1600 Hz.

for scale: my startle threshold is a particle velocity of 1.2e-4 m/s, which displaces the arista by
74 nanometres. a gust is, to this organ, an artillery barrage.

**state.** nothing special. wind is not frightening, it is disabling, the way being underwater
disables a person who is otherwise fine.

**what i do.** stop. crouch: lower the body, spread the legs, stiffen the joints by co-contraction,
and orient into the wind, which minimises drag and is also the only orientation the antennae can
confirm. i do not fly. i wait. success is still being on this leaf in ten seconds.

**give me.** an airflow field that varies in time, JO-C/E as tonic wind reporters on a
left-minus-right code, substrate vibration into the club channel, and drag as a force that can
actually dislodge me.

**what you'll get wrong.** you will let me walk normally in wind, because wind will be an input to
olfaction and nothing else. i will notice by strolling cheerfully across a leaf in a gale that
should have removed me from the simulation.

---

## 17. lost

**sensed.** four minutes of walking, out of the fruit's plume, and the visual scene holds no landmark
i recognise, only grass stems that look like other grass stems. what i do have is a bright direction
in the sky and a horizon, both reported by the ocelli and confirmed by the compound eye.

**state.** lost is a real state with a signature: my path straightens. an animal with no information
should not keep turning, because turning without information only resamples the same place.

**what i do.** menotaxis. pick an arbitrary angle relative to the sun and hold it, using a compass
that tracks my heading and is updated both by the visual scene and by my own turns in darkness.
holding an arbitrary heading is the right algorithm for dispersal: it guarantees i actually leave,
rather than performing a very thorough random walk inside one square metre. success is displacement,
not arrival.

**give me.** a sky with a direction, an idiothetic heading estimate that accumulates my turns, and
the ability to hold an arbitrary offset to it for minutes.

**what you'll get wrong.** you will give me no compass and call the resulting wandering
"exploration". it will look fine on a heat map and be wrong in the one way that matters: i will not
get anywhere. and if you do give me one, you will forget that my heading drifts, and a compass that
never drifts is a compass i have no reason to keep correcting against the sun.

---

## 18. dusk, and the nightly loss of the world

**sensed.** the sky dims through several log units, which my photoreceptors absorb without
complaint, since they compress ten log units of ambient intensity into 40-65 mV of output. what i
cannot absorb is the loss of *bandwidth*: dark-adapted, my temporal resolution falls from ~100 Hz to
the low tens. edges blur, and moving things stop being moving things and become slow grey
suggestions. the contrast is still there. the timing is gone.

**state.** the day's drive winding down on a clock that does not need the sun to know the hour,
though it uses it.

**what i do.** stop dispersing, start settling. i want the underside of something: warmer than open
ground at night, sheltered from wind, less visible from above. i climb, negative geotaxis, which i
measure with JO-C/E because the antennae hang differently under gravity, and tuck under a leaf edge.
success is being somewhere defensible before my vision is too slow to find it.

**give me.** luminance-dependent visual bandwidth, a gravity component in the JO wind channel, and a
circadian phase variable.

**what you'll get wrong.** you will keep my vision crisp at midnight. then my whole evening is
wrong: i will forage competently after dark, which is the behaviour of an animal with different
eyes.

---

## 19. sleep

**sensed.** almost nothing, and that is the point. my arousal threshold has risen: a stimulus that
would have moved me at noon does not move me now, and the delay before i respond to anything is
longer. i am not paralysed. i am gated.

**state.** sleep pressure, accumulated all day and now discharging. it is homeostatic: keep me awake
tonight and i make it up tomorrow, sleeping deeper and longer. that rebound is the standard by which
a simulated sleep is judged; nothing else about it is optional.

**what i do.** stop moving for minutes at a stretch, drop my antennae, stay put. if something large
enough happens, a hard loom, a real mechanical shock, i wake, and i wake *slowly*, over seconds, not
instantly.

**give me.** one accumulator that fills with time awake and empties with time asleep, a multiplier
on every sensory threshold, and a rebound rule.

**what you'll get wrong.** you will implement sleep as "no input, therefore no output", which gives
a fly that is merely quiet in a quiet room and fully alert the instant anything happens. that is not
sleep, it is an idle loop. the difference shows in exactly one measurement: response latency to an
identical stimulus at noon and at midnight. if they match, i never slept.

---

## 20. and the small thing i learned today

i said i was smarter than i look, so: somewhere in the middle of all that, my mushroom body was
doing its job. about 6% of my Kenyon cells respond to any given odour, against 59% of the projection
neurons feeding them, and each KC needs something like 15-18 coincident inputs to fire at all. that
sparseness is the whole trick. it makes nearly every odour a nearly unique, nearly non-overlapping
set of cells, which is what lets a dopamine signal arriving at the right moment tag *that* odour,
specifically, as the one that preceded the bitter patch.

i will not go back to that patch. not because i reasoned about it, but because a handful of
near-silent cells fired at the same moment a dopaminergic neuron did, and the synapse between them
is now weaker.

**give me.** sparse KC coding with a high coincidence threshold, dopamine driven by real outcomes
(sugar good, bitter bad, heat bad), and depression at the KC-to-MBON synapse.

**what you'll get wrong.** you will drive the KCs too hard. if 30% of them respond to an odour
instead of 6%, every memory i form smears across every odour i meet, and i will avoid the whole
garden because one corner of it was bitter. an over-excited mushroom body does not give you a fly
with a bad memory. it gives you a fly with a *phobia*.

---

# what the fly would ask the simulator for, in order

ranked by behaviour returned per unit of work, not by how interesting each is.

1. **persistent internal states.** hunger, thirst, satiety, arousal, sleep pressure, aggression
   threshold, loser effect: six or seven scalars with decay constants from seconds to an hour. right
   now nothing in me outlasts the stimulus that caused it, and that single fact breaks scenarios 5,
   7, 8, 11, 13 and 19 outright. cheapest item on this list, most expensive omission.

2. **an intermittent plume.** power-law whiffs and blanks at exponent -3/2, Weber-Fechner
   normalisation over a 1 s running mean, and a wind vector that both carries the plume and deflects
   my aristae. a distance-graded exponential does not approximate this badly, it inverts what the
   signal *is*: away from the source, intermittency falls and whiff amplitude does not.

3. **cooling cells as a differentiator.** ~95 Hz at rest, driven from -dT/dt, 0.65 s to peak,
   adapting back during the ramp. absolute temperature into the cooling channel is the highest-
   leverage sign error available, because it inverts my thermotaxis while looking correct.

4. **texture on the ground, structure on the walls.** without optic flow i have no speed estimate,
   no centring, no parallax. grey-on-grey does not weaken my vision, it deletes it, and steering by
   flow balance is a large fraction of my day.

5. **taste on contact, with spatial structure.** sugar and bitter as fields on the same surface,
   sampled by tarsi, sugar adapting within 1 s and bitter not adapting; water at the puddle; the PER
   threshold under satiety control.

6. **the escape path, latency-privileged.** loom to giant fibre to jump, bypassing everything, with
   both takeoff modes. if it runs through the main loop it is not an escape.

7. **P1 as a graded integrating dial** with pCd-style persistence downstream, low output driving
   aggression and high output driving song, and LC10a gain multiplied by it. one dial, two animals,
   and the wobble between them.

8. **a rival.** a second male with CHC profile and cVA, autonomous enough to win. my M contact
   channel currently has nothing in the world to fire for, so a third of my pheromone system is being
   tested against an empty room.

9. **load, not force, on the legs.** campaniforms on dF/dt with a separate unloading population,
   hair plates at joint limits, and the 10 ms / 30 ms delays. without the delays your fly is more
   stable than a fly, and you will not know which of your successes came from that.

10. **humidity as a field with a state-dependent sign.** sated flies seek dry, desiccated ones seek
    moist and walk nearly twice as fast in dry air. one field, one sign flip, two different animals.

11. **a compass with drift**, updated by sky direction and by my own turns, holdable at an arbitrary
    offset for minutes. this is what turns wandering into dispersal.

12. **luminance-dependent visual bandwidth, and temperature-dependent everything.** my eye's
    information capacity has a Q10 of 6.5. a cold fly and a warm fly do not see the same world, and a
    dark-adapted fly sees a slow one.

13. **bristle fatigue and per-body-part resolution.** a depression factor per bristle recovering
    over seconds, plus a somatotopic map. without them grooming never terminates.

14. **efference copy into the wide-field visual channels** at saccade onset, signed to cancel
    self-generated flow. otherwise i spend the whole simulation fighting my own turns.

15. **sparse Kenyon cells**, 5-10% response rate, high coincidence threshold, dopamine tied to real
    outcomes, depression at KC-to-MBON. last only because everything above it has to work before
    there is anything worth remembering.

and one thing i am not asking for: do not give me working wings, or oscillating halteres, or colour.
i walk. my halteres are correctly silent. my world is monochrome and green-heavy, and that is the
world i was built for. i would rather have an honest 2.5 mm than a generous one.
