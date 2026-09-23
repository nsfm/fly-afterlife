# the leg senses, per leg (campaign item 6: finish the senses)

built 2026-09-22 by `scripts/build_leg_senses.py` (no engine run). outputs:

- `world/leg_senses.npz`: per leg (`lf lm lh rf rm rh`) x key, arrays of MaleCNS bodyIds (map to cord indices through
  `brain_cord.npz["bodyId"]`). keys: `tactile`, `proprio_all`, `claw_50`, `claw_51`, `hook_39`, `hook_41`, `club`,
  `co_unclassified`, `hair_plate` (= `hair_plate_45` + `hair_plate_52` + `hair_plate_xx`), `campaniform`, `untyped`,
  `gustatory`, `chemo`, `unknown`. e.g. `z["lm_tactile"]`. 102 arrays + `legs` + `README`.
- `world/leg_senses.csv`: one row per sensory cell of `brain_cord.npz` (6,146: 5,605 vnc_sensory, 528 sensory_ascending, 12
  sensory_descending, 1 sensory_ascending_tbc) with `bodyId, type, cls, sc, fam, entryNerve, rootSide, subclass, synonyms, leg,
  modality, modality_by, subtype, assigned_by, confidence, wiring_leg, wiring_share, wiring_seg_share, out_syn`.

## method

**the leg, from the annotation.** the MaleCNS v1.0 table (`data/body-annotations-male-cns-v1.0-minconf-0.5.feather`) carries
`entryNerve` and `rootSide` for every sensory cell but one. leg nerves: `ProLN`, `MesoLN`, `MetaLN` (the main leg nerves, one per
segment) and the three T1 accessory nerves `ProAN`, `VProN`, `DProN`, which MANC's annotation assigns to the front leg (hair
plates SNpp45 / SNpp52, the bilateral tactile type SNta42, the intersegmental tactile type SNta33; `leg_biomech_parts/
manc_leg_sensory_annotation.md` §9). leg = rootSide x segment. `assigned_by = annotated`; confidence `high` on a main nerve,
`medium` on an accessory nerve, one step lower where the wiring below confidently points to another leg. every other nerve
(ADMN wing, PDMN notum, DMetaN haltere, AbN* abdomen, PrN prosternal organ, ProCN prothoracic chordotonal, and the brain nerves
of the 12 sensory_descending cells) is `not_leg:<nerve>`.

**the leg, from the wiring (the check, and the fallback).** every cord cell gets a six-leg affinity: leg motor neurons one-hot
from `world/legmn.npz`; every interneuron its synapse-weighted share of output onto each leg's MNs; cells with no MN output one
hop further (weight 0.5). a sensory cell's score per leg is its output synapses times its targets' affinities; `wiring_leg` is
the argmax, `wiring_share` its fraction. the one leg-type cell with no nerve (SNpp53 bodyId 1050206135, rootSide unknown, the
bilateral trochanter campaniform type) is placed by this: `lh`, share 0.59, `assigned_by = inferred`, `medium`.

**the modality.** from `cls` where it names one; where `cls` is `unknown_sensory` or blank, from the MANC family in the type
name (`SNta` tactile, `SNpp` / `SApp` proprio, `SNch` chemo, `LgLG` / `LgAG` gustatory); `modality_by` says which. this moves
76 SNta cells (cls unknown, subclass "mechanosensory bristle", mostly ProLN) into tactile, 68 SNch10 taste-bristle cells (cls
blank) into chemo, 2 LgLG taste-bristle cells (cls blank) into gustatory, and 4 SNpp / SNppxx cells into proprio. two SNta21 cells labelled proprioceptive by `cls` stay proprio
(`untyped`), against their type's other 113 tactile cells: probably a label slip, left as the file has it.

**the proprioceptor subtypes,** by MANC type (Marin 2024; MANC v1.2.3 `synonyms`), then the per-cell MaleCNS `subclass`:

| subtype | types | organ | tuning (`mechanosensation.md`) |
|---|---|---|---|
| `claw_50` / `claw_51` | SNpp50 / SNpp51 | FeCO claw | tonic femur-tibia angle; which one is extension-tuned is ledger row 1 |
| `hook_39` / `hook_41` | SNpp39 / SNpp41 | FeCO hook | directional tibia velocity (body_loop: 39 flexion, 41 extension) |
| `club` | SNpp40 43 47 56 57 58 59 60, SApp23 (and SApp23,SNpp56) | FeCO club | movement transients and vibration; no motor connectivity |
| `co_unclassified` | SNpp42 44 46 48 49 | leg chordotonal, no FeCO subtype in MANC | unknown |
| `hair_plate_45` / `_52` / `_xx` | SNpp45 / SNpp52 / SNppxx with subclass or synonym "hair plate" | hair plate (SNpp52: MANC's caveat, may be campaniform) | joint-limit, tonic |
| `campaniform` | SNpp53 (TrCS), SNpp63, subclass "campaniform sensilla" | campaniform sensilla | force, dF/dt |
| `untyped` | SNppxx, SNxxxx, SNpp55, SNta21 (proprio by cls) | unknown; MANC: SNppxx holds most leg CS and extra hair plates | unknown |

**what could not be separated:** the leg's campaniform fields beyond the trochanter (MANC types only SNpp53; the femoral /
tibial / tarsal CS are inside `untyped`, not individually labelled); hair plates by joint (SNpp45 and SNpp52 are pooled over
the coxa and trochanter plates; the joint is inferred from their MN targets only); the claw's tuning direction (row 1); the
hook's direction (from the MANC reflex sign, not a recording); the FeCO club's per-cell frequency; tactile bristles by leg
segment (SNta19-45 are connectivity clusters with no segment label here, so a tarsal bristle cannot be told from a femoral
one); SNta33 / SNta42 are named intersegmental / bilateral but carry no position.

## the counts

per leg x modality (all sensory superclasses; the sensory_ascending cells are 16-22 per leg: SApp23 club, LgAG taste, SAxx):

| | lf | lm | lh | rf | rm | rh | total |
|---|---|---|---|---|---|---|---|
| tactile | 169 | 372 | 388 | 156 | 426 | 413 | 1,924 |
| proprio_all | 48 | 129 | 132 | 31 | 133 | 139 | 612 |
| gustatory | 147 | 109 | 121 | 147 | 117 | 119 | 760 |
| chemo | 11 | 0 | 24 | 9 | 0 | 37 | 81 |
| unknown | 39 | 32 | 31 | 41 | 16 | 31 | 190 |
| **all** | 414 | 642 | 696 | 384 | 692 | 739 | 3,567 |

proprioceptor subtypes:

| | lf | lm | lh | rf | rm | rh |
|---|---|---|---|---|---|---|
| claw_50 | 1 | 14 | 18 | 0 | 12 | 17 |
| claw_51 | 3 | 9 | 5 | 1 | 6 | 8 |
| hook_39 | 3 | 8 | 7 | 5 | 9 | 7 |
| hook_41 | 1 | 3 | 3 | 2 | 8 | 5 |
| club | 17 | 45 | 47 | 8 | 44 | 47 |
| co_unclassified | 0 | 4 | 15 | 0 | 5 | 17 |
| hair_plate (45 / 52 / xx) | 11 (8 / 3 / 0) | 22 (12 / 10 / 0) | 14 (8 / 6 / 0) | 8 (5 / 3 / 0) | 22 (11 / 11 / 0) | 20 (9 / 10 / 1) |
| campaniform | 2 | 2 | 3 | 2 | 2 | 2 |
| untyped | 10 | 22 | 20 | 5 | 25 | 16 |

**the assignment:** 3,567 of 6,146 sensory cells are leg cells: 3,566 annotated (99.97 %: 3,509 by a main leg nerve, 57 by
the T1 accessory nerves), 1 inferred (0.03 %). confidence: 3,369 high; 186 medium (45 accessory-nerve cells, the
inferred one, and 140 main-nerve cells whose wiring confidently points to another leg); 12 low (accessory-nerve cells whose
wiring points elsewhere, 10 of them SNta33 on DProN). the other 2,579 enter by non-leg nerves and are
not leg cells; **no sensory cell is left unassigned.** of the 5,605 vnc_sensory cells, 3,454 are leg cells (3,453 annotated, 1
inferred). "SNta 2,573" (the SEAM count) is the family across nerves: 1,918 of them are leg cells (the rest: wing ADMN 352,
notum PDMN 264, haltere DMetaN 39); 1,916 of those are tactile (2 SNta21 are proprio by cls), and with 8 tactile SNxxxx
the leg's tactile is 1,924.

**the wiring check.** of the 3,473 annotated leg cells that have output onto scored cells, the wiring's leg agrees with the
annotation for 87.9 % (segment 89.8 %, side 96.0 %). by modality: tactile 97.1 % (99.6 % where the wiring is confident),
proprio 87.8 % (97.1 %), unknown 94.7 %, chemo 89.7 %, gustatory 62.8 % (taste afferents barely reach motor circuits, so the
check is weak there). by nerve: MesoLN 96.7 %, MetaLN 91.9 %, ProLN 64.4 % (its gustatory cells, and its FeCO clubs and SApp23,
which project intersegmentally, as Lee 2025 found: club and SApp23 score to the hind or middle leg on the same side),
DProN 21.9 % (SNta33, the intersegmental tactile type: 22 of 24 score to the middle leg on the same side; kept on the front
leg by the nerve, confidence lowered). 93 leg cells have no output in the floored cord (39 unknown, 30 tactile). 109 non-leg
cells score into leg neuropil with share >= 0.6 (78 haltere DMetaN, 15 AbN4, 10 ADMN): not moved, they enter elsewhere.

**the front-leg deficit is in the file, not the method:** lf / rf carry 48 / 31 proprioceptors and 169 / 156 tactile cells
against ~130 and ~400 on the middle and hind legs; the front leg's claw_50 is 1 / 0 cells. FANC is the source if the front leg
matters (campaign item 6's "FANC where MaleCNS is incomplete").

## against the existing sets

- **`world/legs.npz` (580 cells, brain_whole indices; cls proprioceptive x the three main nerves; the same 580 as
  `receptors.py`'s `floor_leg_proprio`):** every one of its cells is in my `proprio_all` on the same leg (0 disagreements, 0
  missing). mine adds 32: the front leg's accessory-nerve proprioceptors (lf 13: VProN SNpp45 x7, DProN SNpp52 x3, ProAN SNxxxx
  x3; rf 14: VProN SNpp45 x5 + SNppxx x2, DProN SNpp52 x3, ProAN SNppxx x3 + SNpp40 x1), four cells proprio by type with cls
  unknown (lm SNppxx x2, lh SNpp51, rh SNpp45), and the nerve-less SNpp53 (lh).
- **body_loop's claw / hook sets** (typed out of legs.npz): claw_e = my claw_50, claw_f = claw_51, hook_f = hook_39, hook_e =
  hook_41 exactly on every leg, except lh claw_51: 4 in body_loop, 5 here (the cls-unknown SNpp51).
- **body_loop's `load` set** (legs.npz minus the four claw / hook types: lf 27, lm 93, lh 98, rf 9, rm 98, rh 101) is by my
  subtypes: club 207 (lf 17, lm 45, lh 47, rf 7, rm 44, rh 47), untyped 88, hair plates 78, co_unclassified 41, campaniform 12
  (426 cells). so **the load row is 49 % FeCO club, 18 % hair plate, 10 % unclassified chordotonal, 21 % untyped and 3 % named
  campaniform;** only the
  campaniforms and some of `untyped` are load sensors. this is the review's F7 (`docs/REVIEW_BODY_LOOP.md`) with numbers.
- **the floor's 580** at 15 Hz, by subtype: club 207, untyped 88, claw_50 62, co_unclassified 41, hair_plate_45 40, hook_39 39,
  hair_plate_52 37, claw_51 31, hook_41 22, campaniform 12, hair_plate_xx 1. hooks and clubs, silent at rest in life, are 268
  of them. **no tactile cell is in any existing set.**

## a proposal for body_loop.py (for the owner; nothing here is implemented)

load the map once: `LS = np.load("world/leg_senses.npz")`, cells per leg and key as
`np.array([pos[b] for b in LS[f"{leg}_{key}"] if b in pos])`, one `ReceptorClass` row per leg and key, as the claw rows are
built now. rows that are not driven stay at 0 (they are sensory, so the engine already holds them as driven-at-zero).

1. **tactile (new; the 13B side's missing input).** a leg's `tactile` cells fire while its tarsus touches the floor:
   contact = `F[i] > 0.05` (the threshold `pad_on` uses now, model uN). **rate source:** fly bristles are silent at rest
   (Corfas & Dudai 1990); onset burst ~100-300 Hz decaying with tau ~20-50 ms to a plateau (both (E), from the same paper's
   traces); the 10-25 Hz plateau in `mechanosensation.md` §7 is our estimate, **no adult leg bristle has a recorded rate under
   walking contact.** so: per leg, `rate = 200 x exp(-t_contact / 30 ms) + 15` Hz while in contact, 0 in swing, all (E). **the
   caveat that matters:** the map cannot tell tarsal bristles from femoral or tibial ones, and a standing tarsus touches the
   floor with a few dozen of a leg's ~400 bristles. drive a fixed random fraction per leg (e.g. 0.1, seeded, labelled) or the
   whole set at a proportionally lower rate, and say which; driving all 1,924 at the plateau is the SEAM's 15 / 40 Hz arm again
   and wakes both sides of the half-centre. optional, sourced: scale the rate down while the leg's hooks fire (proprioceptors
   gate touch, Tuthill & Wilson 2016) only if the cord does not do it itself.
2. **hair plates, from joint angle.** `hair_plate_45` (MANC: onto the remotor / abductor and sternal rotator MNs, the
   posterior movers) and `hair_plate_52` (onto the promotors). life: 0 inside the working range, tonic 20-60 Hz in the outer
   10-15 % of the excursion, no walking suppression (Pratt 2026). proposal: SNpp45 = 40 x clip((theta_protraction - (limit -
   0.15 x span)) / (0.15 x span), 0, 1) on the coxa protraction axis (CxHP8's anterior limit excites the posterior movers),
   SNpp52 the same on the opposite limit; `hair_plate_xx` with 45. the pairing of type to limit is inferred from the MN targets
   (E); the span is `limit_joints`' coarse range, not a measured one.
3. **campaniform, from load.** `campaniform` (the TrCS, 2 per leg) and `untyped` (MANC: most leg CS live in SNppxx) on dF/dt,
   not F: `rate = clip(100-300 Hz x dF/dt_+ / scale, ...)`, burst on the rising force at touchdown, adapting within 20-40 ms,
   silent in swing (Zill 2024, stick insect; the cockroach axes, (C)); `--load-deriv` already computes dF. the unloading
   subgroup (fires on force decrease; Harris 2022) cannot be identified in the file; a labelled split of `untyped` would be a
   guess. if the tonic F term stays, it belongs on these rows only.
4. **clubs, co_unclassified, hooks at rest.** clubs to 0 (or a vibration channel, which the rigid body does not produce);
   `co_unclassified` to 0 until someone types it; take clubs, hooks and claws out of the floor's 15 Hz and give the floor
   per-subtype rests (claw nonzero at rest, hook 0, club 0, hair plate 0 inside range, CS ~0 unloaded). that makes the `load`
   row about 100 cells over six legs instead of 580.
5. **gustatory / chemo / unknown:** 0 on a clean floor. `unknown` includes the SNxx29 heat nociceptors.
