# Hopkins, Barmina & Kopp 2023 — single-cell atlas of the Drosophila foreleg + sensory organs

**Citation:** Hopkins BR, Barmina O, Kopp A (2023). *A single-cell atlas of the sexually dimorphic
Drosophila foreleg and its sensory organs during development.* **PLOS Biology 21(6):e3002148.**
doi:10.1371/journal.pbio.3002148
**Status: VERIFIED — full manuscript XML pulled and read.**

Scope caveat: this is a scRNA-seq paper on the **first tarsal segment (ta1, "basitarsus") of the
MALE foreleg** during pupal development. Its anatomical statements are in the intro/Fig 1 legend and
are themselves cited to older morphology papers, so treat the counts as their citation of those.

## Chordotonal organs in the Drosophila leg — ANSWERS "is there a tibial CO?"
> "Two chordotonal organs (COs) are present outside of the tarsal segments… One is situated in the
> **proximal femur (FeCO)** and the other in the **distal tibia (tCO)**" — cites Mamiya, Gurung &
> Tuthill 2018 (Neuron 100:636–650.e6) and McKelvey et al. 2021 (Curr. Biol. 31:3894–3904.e5).

**⇒ YES: Drosophila has a tibial chordotonal organ (tCO) in the distal tibia, distinct from the
FeCO.** No neuron/scolopidia count for tCO is given here.

> "chordotonal organs are not present in the upper tarsal segments"
> "we recovered 3 putative chordotonal organ neuron clusters that were absent from our first tarsal
> segment dataset because these organs fall outside the dissected area."

**⇒ NO tarsal chordotonal organ.** (Confirmed by their own negative result in the ta1 scRNA-seq.)

## Tarsal campaniform sensilla
> "**Three campaniform sensilla are present in ta1**, two on the dorsal distal end of ta1 and one on
> the proximal ventral side [**Ta1GF** and **Ta1SF**, respectively, using the nomenclature of
> Dinges et al. 2021]; **no campaniform sensilla are present in the distal tibia, ta2, or proximal
> ta3**."
- eyg-GAL4 marks the tarsal CS; nuclear reporter detected **4 cells per tarsal campaniform
  sensillum** = neuron, sheath (thecogen), socket (tormogen), dome (trichogen). CS are
  **singly innervated** (1 neuron each).

## Tarsal bristles
- ta1 "has the **highest concentration of mechanosensory bristles of any part of the leg**."
- Arrangement: **transverse rows on the ventral side** (thought to aid grooming) and
  **longitudinal rows on the anterior, dorsal, and posterior sides** (cites Hannah-Alava 1958).
- Male-specific: the most distal transverse ventral row of ta1 is transformed into the **sex comb** —
  bristles become "teeth", thicker/longer/blunter/more melanized, and the whole row **rotated 90°**.
- **Chemosensory taste bristles in ta1: ~11 in males vs ~7 in females** (cites Nayak & Singh 1983).
- Chemo/mechano split at the bristle level: a **mechanosensory bristle is mono-innervated (1
  neuron)**; a **chemosensory taste bristle is poly-innervated — multiple gustatory receptor
  neurons PLUS a single mechanosensory neuron.** So taste bristles also report deflection.
- All three organ classes (mechanosensory bristle, taste bristle, campaniform sensillum) share the
  same 4-cell blueprint from one sensory organ precursor: trichogen (shaft/dome), tormogen (socket),
  thecogen (sheath), neuron(s).

## Onward references worth pulling (from Hopkins' reference list, verified as listed)
- **Hannah-Alava A (1958). Morphology and chaetotaxy of the legs of Drosophila melanogaster.
  J. Morphol. 103:281–310. doi:10.1002/JMOR.1051030205** ← the canonical per-segment bristle count.
- **Nayak SV, Singh RN (1983). Sensilla on the tarsal segments and mouthparts of adult Drosophila
  melanogaster. Int. J. Insect Morphol. Embryol. 12:273–291. doi:10.1016/0020-7322(83)90023-5**
  ← the canonical tarsal sensilla survey.
- Dinges GF, Chockley AS, Bockemühl T, Ito K, Blanke A, Büschges A (2021). Location and arrangement
  of campaniform sensilla in Drosophila melanogaster. J. Comp. Neurol. 529:905–925.
  doi:10.1002/cne.24987 (covered by the other agent).
- McKelvey EGZ et al. (2021). Drosophila females receive male substrate-borne signals through
  specific leg neurons during courtship. Curr. Biol. 31:3894–3904.e5. doi:10.1016/j.cub.2021.06.002
- Walker RG, Willingham AT, Zuker CS (2000). A Drosophila mechanosensory transduction channel.
  Science 287:2229–2234. doi:10.1126/science.287.5461.2229 (NompC; bristle deflection sensitivity).
