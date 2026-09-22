# walking: what a fly's cord does, and what his does instead

a one-page version of the leg work, without the synapse counts. the numbers and sources are in `docs/SEAM.md` ("the legs, per muscle")
and `docs/physiology/leg_biomech.md`. this page is the thing to argue with.

## in life

**walking is made in the cord, not the brain.** the brain says *go* and *how fast* and *which way*, as a steady rate on a few descending
neurons. the ventral nerve cord (the fly's spinal cord) turns that steady signal into stepping. the proof is old and simple: cut the head
off a fly and drive one of its walking neurons, and the body walks (Bidaye 2020, on the same neuron we drive, DNg100). the rhythm lives
below the neck.

**a step has two halves.** stance: the foot is down and the leg pushes the body forward. swing: the foot lifts and the leg comes forward
for the next stance. each half uses its own muscles, and each joint has a pair that pull against each other: one for stance, one for
swing. a walking leg alternates them, joint by joint, about ten times a second at a fly's normal pace.

**the joints, from the body outward:** the coxa (the hip; it rotates the whole leg back in stance and forward in swing), the trochanter
(the leg lifts and lowers here), the femur-tibia joint (the knee: it flexes and extends), and the tarsus (the foot: it grips and lets go).
one honest complication: the knee's job differs by leg. front legs flex the knee in stance and pull; hind legs extend it and push.

**the legs take turns.** at speed, three feet are down while three are up: left-front, right-middle, left-hind together, then the other
three. this is the tripod. at slower speeds more feet stay down at once, but neighbours still alternate: a leg never swings while the leg
beside it swings.

**the cord listens to the legs.** every joint carries sensors: position and movement at the knee (the femoral chordotonal organ), load in
the cuticle (campaniform sensilla), and hair plates at the hip. their signals go back into the cord and time the switch from stance to
swing: a leg that has pushed far enough and been unloaded is a leg allowed to lift. the rhythm is generated in the cord and shaped by the
legs. the two are hard to separate, and in a fly nobody has fully separated them.

**what the muscles need.** a motor neuron's spike makes a muscle twitch that peaks about twenty milliseconds later and fades over about
twenty more; spikes close together add up, then saturate. a leg's own springiness is far too weak to hold the fly up, so a fly whose leg
muscles are silent is a fly lying down.

## what his cord does

we drive DNg100 at a steady rate, exactly the headless experiment, and read every leg motor neuron ten times a millisecond, grouped by
the muscle it pulls.

- **he holds a posture.** the same few muscles fire the whole time: the mid legs' knee extensors and hip protractors, the front legs'
  trochanter depressors, and, oddly, the left front leg's jump muscle. they fire slightly *harder* when he stands than when he walks.
- **the swing muscles are silent.** every knee flexor on every leg, the grip muscles, the foot muscles: zero, walking or standing.
- **there is no rhythm and no turn-taking.** no leg's output has a beat, and every leg rises and falls together with every other, in
  step, because they are all riding the same steady dose from the command.
- **his speed is read from the sum of all of this,** so "walking" in the viewer is the posture getting louder. that readout is a labelled
  stand-in, and this is why.

**why.** the walking command's own connections land on the stance muscles and on the cells that *inhibit* the flexors. the flexors' own
excitation sits two connections further in and never lights. the brake is not the reason (it only fires while he eats). feeding his leg
sensors a fake tripod rhythm is not the fix either (tried: nothing changed). the wiring for turn-taking is there; what the model lacks is
any way for a cell to tire. a rhythm made of two sides pushing against each other needs one side to fatigue so the other can win, and this
neuron model has no fatigue: no adaptation, no synaptic depression except on one pair of cells we added for the wings.

## what we do next, in order

1. **depression on every synapse** (running now): the one ingredient a half-centre needs. if the flexors wake and the legs start taking
   turns, the leg question and the wing question were the same question, and the refreeze day (5c) is next.
2. **the headless preparation:** run the cord alone, without the brain, with the descending neurons as driven inputs. it is a seventh of
   him, so seven times faster to iterate, and it is literally the experiment the field does. everything in this list gets tested there
   first and then confirmed in the whole fly.
3. **the muscle map:** every motor neuron to its muscle and joint, with the twitch shape and the per-leg signs from the brief, so the cord's
   output becomes joint torques instead of a sum.
4. **a body:** the MuJoCo fly (NeuroMechFly v2), driven by those torques, first as a display beside the garden, then on the ground with
   gravity, then closed: its joint angles and loads become his leg sensors, its displacement becomes his speed and heading, and the summed
   readout retires. with the flexors silent the first body will lie down. that is the honest starting frame.
5. **the sensors from the legs:** position, movement and load computed from the body's joints, into the sensory cells by name (he has
   them, labelled, on all three leg pairs), so the cord can listen to the legs the way it does in life.

## how to read a result on this row

five questions, in order, for any run: does the muscle fire at all? do its antagonist and it alternate, or fire together? is there a
beat in the leg's output, and is it there only when he walks? do neighbouring legs take turns? and the one that decides everything: if we
turn the thing off, does anything change? a yes on the last with a no on the rest is a puppet. a no on the last is a number that means
nothing yet.
