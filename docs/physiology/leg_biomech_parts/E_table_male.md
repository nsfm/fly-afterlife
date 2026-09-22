# §E "in the table": the leg proprioceptors the male actually carries

All **(D)** — derived 2026-09-21 from `data/body-annotations-male-cns-v1.0-minconf-0.5.feather`
(superclasses `vnc_sensory` / `sensory_ascending`, filtered to the six leg nerves). These are the
cells step 3 would deliver proprioception *to*, and the good news is that they are named,
published types, not an undifferentiated pool.

**Read the MANC two-letter codes correctly** (Marin et al. 2024, *eLife* 13:RP97766): `pp` =
**proprioceptive**, `ta` = **tactile**, `ch` = **chemosensory** — *not* chordotonal. Chordotonal
afferents, hair plates and campaniform sensilla are all `SNpp##`; the sensillum identity lives in
`subclass`, not in the type name. There is no `SNhp` and no `SNcs` code.

**Totals by entry nerve**, all sensory superclasses:

| Nerve | Segment | n |
|---|---|---|
| ProLN | T1 | 992 |
| MesoLN | T2 | 1,402 |
| MetaLN | T3 | 1,521 |
| DProN / VProN / ProAN | T1 | 32 / 19 / 10 |

3,976 leg sensory neurons both sides. The front-leg deficit (992 vs 1,402 and 1,521) is the same
tracing gap that shows in the front-leg MNs (§A3) and it is worst exactly where we most want it:
the front leg's proprioceptors.

**By class:**

| Stem | ProLN | MesoLN | MetaLN | Reading |
|---|---|---|---|---|
| `SNta` (+`SNtaxx`, `SNta,SNta`) | 292 | 800 | 801 | **tactile** — bristles. The largest class by far. |
| `LgLG` | 257 | 202 | 210 | **leg gustatory** — the only leg types carrying `receptorType`: 173 `putative_ppk23`, 161 `putative_ppk25`, 130 `putative_IR52b` (`WG` is the wing equivalent). Taste, not proprioception. |
| `SNpp` (+`SNppxx`) | 45 | 250 | 251 | **proprioceptive** — the target set for step 3. 570 cells total across leg nerves. |
| `SNch` | 21 | 2 | 66 | **chemosensory**, 3 types; `SNch10` is T1+T3 only, `SNch08` is T1-only, male-specific and *fru*+ (pheromone). Not proprioceptors. |
| `LgAG` | 29 | 22 | 25 | |
| `SApp` | 7 | 8 | 8 | ascending proprioceptive |
| `SNxx`/`SNxxxx`/`SAxx` | 90 | 50 | 67 | unresolved |

**The named proprioceptor types he carries**, per entry nerve **(D)**; functional identities from
Marin et al. 2024:

| Type | Organ / class | ProLN | MesoLN | MetaLN | VProN | DProN |
|---|---|---|---|---|---|---|
| `SNpp50` | FeCO **claw** (extension-tuned) | 1 | 26 | 35 | 0 | 0 |
| `SNpp51` | FeCO **claw** (flexion-tuned) | 4 | 15 | 13 | 0 | 0 |
| `SNpp39` | FeCO **hook** | 8 | 17 | 14 | 0 | 0 |
| `SNpp41` | FeCO **hook** | 3 | 11 | 8 | 0 | 0 |
| `SNpp45` | **hair plate** | 1 | 23 | 17 | 12 | 0 |
| `SNpp52` | **hair plate** (authors caveat: may be campaniform) | 0 | 21 | 16 | 0 | 6 |
| `SNpp53` | **trochanter campaniform sensilla** (TrCS, bilateral) | 4 | 4 | 4 | 0 | 0 |

Plus 15 further `SNpp` types with n ≥ 4 (`SNpp40, 42, 43, 44, 47, 48, 49, 55, 56, 57, 58, 59, 60`)
and 80 `SNppxx` untyped. `SNpp42` (20 cells) and `SNpp55` (7) are **hind-leg only**; `SNpp49` (4)
is **middle-leg only**.

**What this means for step 3.** Proprioception does not need a stand-in population. The claw,
hook and hair-plate afferents are individually addressable in this male by type name, with
published tuning (claw = tonic femur–tibia angle, two oppositely tuned subsets; hook =
directional movement; hair plate = joint-limit detection) and published downstream reflexes
(Agrawal et al. 2020; the limit-detector paper). The transducer can be written straight onto the
FTi joint angle and its derivative from §D's body, with no invented labels.

**Two caveats.** (1) `SNpp` includes no **club** type in the list above — club afferents (vibration
/ bidirectional movement) are not separately named here, so vibration encoding would be a
stand-in. (2) The front leg carries 1 `SNpp50`, 4 `SNpp51`, 1 `SNpp45` against the middle leg's
26 / 15 / 23 — the front-leg FeCO is essentially absent from this volume, so a front-leg
proprioceptive loop cannot be built on real afferent counts.
