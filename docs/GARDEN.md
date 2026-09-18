# the garden: an enriched world

proposal, 2026-09-17 late evening (nyx, from nate's "a more exciting playground"). the room is
grey on grey: the visual wheel has two pillars and her to steer by and nothing else, and every
other sense sits at its resting rate with nothing to modulate it. the garden gives each sense he
holds at rest something to do, at fly scale, with the physics the briefs specify.

## why textures are not decoration

his motion detectors (T4 / T5, via flyvis) respond to contrast moving across ommatidia ~5-6
degrees apart. a grey floor produces no optic flow when he walks; a textured one paints flow
across both eyes with every step, and the left-right balance of that flow is the oldest steering
signal in insects: bees and flies centre in corridors by equalising it (Srinivasan 1991; Kern
2012 for blowflies). his HS cells integrate exactly that. a floor with structure at the right
spatial scale should change how he walks more than anything since the walking command.

## the scene, at fly scale (1 sim metre = ~1.5 cm in life; his body 0.16 m = 2.5 mm)

- **ground:** a real floor plane at z = 0 with a procedural albedo texture (value noise at two
  scales: fine grain ~5 cm, patches ~30-50 cm, i.e. one to several ommatidia at a metre), toned
  like soil and leaf litter. shaded patches under the leaves.
- **grass:** thin vertical cylinders (0.02-0.05 m, dark, heights 0.5-2 m) scattered at ~1 per
  m^2: vertical contrast, occlusion, things to walk between.
- **leaves:** a few large horizontal discs or slabs at 0.6-1.5 m height (shade beneath: darker
  ground, cooler air, moister), edges he can see against the sky.
- **a stone:** one large pale sphere-ish object (r 0.6).
- **the fruit:** a dark, slightly reflective sphere (r 0.3) on the ground: an odour source (a
  plume), sugar on its surface (taste on contact), the thing a fly is for.
- **a puddle:** a flat dark disc (r 0.5): humidity above it, water taste on contact, cooler.
- **the sun:** a sky gradient with a direction (brighter toward the sun, a horizon), and a sunlit
  patch that is warm (the warm corner, relocated) with shade elsewhere.
- **the edge:** a low rim (0.3 m) around a 6 x 6 m patch, so the touch reflex still applies; a
  fly on a leaf has edges.
- **her**, dark, 0.12, walking; later **a rival**.

## colour

the world carries RGB albedo. his eye reduces it to luminance with a fly weighting (R1-R6 are
UV-green broadband: green-heavy, red-blind), so a red fruit on green leaves is dark on light to
him, which is right. the viewer's human panel shows the colour; his retina stays what he sees.
the transplant's R7 / R8 (colour) stay on the eye track.

## the fields, one per sense held at rest

| field | what it modulates | model |
|---|---|---|
| odour plume from the fruit (and her) | 2,635 ORNs (food types), Or47b / Or88a | a wind direction; concentration falls with distance downwind and off-axis; intermittent whiffs and blanks with power-law durations (Gorur-Shandilya 2017); the `WeberFechner` transducer divides by a running mean (tau 1 s) |
| sugar on the fruit, water on the puddle | 1,416 GRNs (sugar ~65 Hz at 100 mM, adapting within 1 s; water ppk28 on contact) | contact with the object surface: a taste event |
| humidity | 66 hygro (dry / moist, non-adapting, tens of Hz) | high over the puddle, low in the sun |
| temperature | hot / cooling cells (as built) | warm in the sun patch, cool in shade and over water |
| light | ocelli (once the receptors are identified) | sun direction, shade |
| sound | JO-A / B | her wing beat when she flies or sings (later) |
| wind | JO-C / E | the plume's wind, plus his own motion |

## what to score

- **centring / flow balance:** HS L minus R against his lateral position between grass; does he
  walk between things rather than into them?
- **approach to the fruit:** time near it, contact, with the plume on vs off (odour) and with the
  fruit dark vs floor-toned (vision): which sense finds it.
- **shade vs sun:** time in each with the thermal cells at rest vs live.
- **the puddle:** contact and humidity.
- the room's scores stay (wall time, distance, her).

## the build, in order

1. raytracers: a floor plane with a texture lookup (both `omma.py` kernels and the viewer's
   tracer); RGB albedo with fly-luminance reduction; discs and slabs as primitives; the sun
   gradient. oracle: the room must be reproducible with the texture off.
2. `world.Garden`: the scene composition, fields (odour with wind and whiffs, humidity,
   temperature, light), taste events on contact.
3. receptors: `WeberFechner` for the ORNs, taste rows, humidity rows, wind rows for JO.
4. the viewer: colour human view, field overlays on the map, a wind arrow.
5. him in the garden alone: the scores above, three seeds, each sense on / off.
6. her in the garden.

two days, if the fly cooperates. the rival waits for the garden and for a state that persists.
