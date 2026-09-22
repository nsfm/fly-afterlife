# Dinges et al. 2021 — Location and arrangement of campaniform sensilla in Drosophila

**Citation.** Dinges GF, Chockley AS, Bockemühl T, Ito K, Blanke A, Büschges A (2021).
"Location and arrangement of campaniform sensilla in *Drosophila melanogaster*."
*J Comp Neurol* **529(4):905–925**. DOI **10.1002/cne.24987**. PMID 32678470.
Received 2020-04-24, accepted 2020-07-01. Institute of Zoology, University of Cologne.
**VERIFIED** by reading the full OA PDF from the Cologne repository
(https://kups.ub.uni-koeln.de/25156/1/Blanke%20in%20Dinges%202020.pdf). Wiley served 403 to every
direct route; use the KUPS mirror. Supporting data: https://uni-koeln.sciebo.de/s/zxPiRV0CjRd6GKq

Method: scanning electron microscopy (FEI Quanta 250 FEG) of **female** flies, plus µCT for 3D
reference. **All counts are external cap counts from SEM, not neuron counts.** One CS = one
sensillum = one bipolar sensory neuron is the standard assumption in this literature but is **not
measured in this paper.**

## Whole-body total (VERIFIED, direct quote)

> "In total, we found over **680 sensilla** arranged in **26 fields, 54 groups, and 34 single CS**."

Female flies. "Based on previous work … it is likely that CS in males are at the same locations as in
females" — i.e. male counts are **inferred, not measured.**

## Naming scheme (VERIFIED)

The paper introduces the extended scheme this project should use. Structure is
`<segment><arrangement><position><leg>`:

- segment: `Tr` trochanter, `Fe` femur, `Ti` tibia, `Ta1`/`Ta3`/`Ta5` tarsomere 1/3/5, `Cx` coxa
- arrangement: `F` = **field**, `G` = **group**, `S` = **single** CS
  (their own distinction: roughly ≥5 = field, <5 = group; they note in the haltere discussion that
  this boundary is "arbitrar[y]")
- position qualifier: `p` posterior, `a` anterior, `d` dorsal, `v` ventral
- leg suffix: **`F` = prothoracic (front), `M` = mesothoracic (middle), `R` = metathoracic (rear)**

So `TiGvF` = tibia, group, ventral, front leg. `TrFpM` = trochanter, field, posterior subfield,
middle leg. Careful: the letter `F` is overloaded — it means both "field" (2nd position) and
"front leg" (suffix).

## Leg CS inventory (VERIFIED, all three leg pairs)

Counts as reported; `x/y flies` = that count seen in x of y flies examined at that location.

| Location | Segment / side | Front (T1) | Middle (T2) | Rear (T3) |
|---|---|---|---|---|
| **TrFp** trochanteral field, posterior subfield | dorsal trochanter | **8** (7 in 1/8) | **8** (8/9); 7 (1/9) | **8** (5/9); **7** (4/9) |
| **TrFa** trochanteral field, anterior subfield | dorsal trochanter | **5** (7 flies, always) | **5** (9/10); 4 (1/10) | **5** (11 flies, always) |
| **FeF** femoral field | proximal ventral femur, 3 columns | **10** (3/5); **11** (2/5) | **11** (8/9); 12 (1/9) | **11** (4/5); 12 (1/5) |
| **TrG** trochanteral group | posterior trochanter | **3** (10 flies) | **3** (6 flies) | **3** (7 flies) |
| **TiGd** dorsal tibia group | dorsal, posterior end of tibia | **2** (10 flies) | **2** (11 flies) | **2** (10 flies) |
| **TiGv** ventral tibia group | ventral, posterior end of tibia | **3** (9 flies) | **3** (11/12); 2 (1/12) | **3** (9 flies) |
| **Ta1G** | dorsal distal 1st tarsomere | **2** (7 flies) | **2** (6 flies) | **2** (6 flies) |
| **Ta3G** | dorsal distal 3rd tarsomere | **2** (6 flies) | **2** (8 flies) | **2** (8 flies) |
| **Ta5G** | ventral distal 5th tarsomere | **4** (4/5); 3 (1/5) | **4** (6 flies) | **4** (3 flies) |
| **FeS** single femoral CS | dorsal femur (posterior in T1; more anterior in T2, T3; more distal in T3) | **1** | **1** | **1** |
| **Ta1S** single tarsal CS | ventral 1st tarsomere (more anterior on hind leg) | **1** | **1** | **1** |
| **Cx** coxa | — | **0** | 0 | 0 |

**The coxa has no campaniform sensilla at all** — direct quote: *"In spite of its large volume no CS
was observed on the Coxa (Cx)."* Worth flagging: coxal load sensing in this fly is **not** done by CS.

### Totals per leg (VERIFIED)

> "From the 14 flies, three legs (one front, one middle, and one rear leg) did not have any occlusions
> so they could be imaged at all CS locations. These three legs had **42 (front, middle) and 41 CS
> (rear)**."

So **~42 CS per leg, ~250 CS across all six legs**. n = 1 leg per pair for those exact totals.
Summing the modal counts in my table gives 42 for front and middle, and 42 for rear — the rear leg
that was fully imaged presumably had TrFpR = 7 rather than 8, which is the commonest variant there.

The prothoracic leg is described as **"two fields, six groups, and two single CS"**
(fields = TrFF split into TrFpF+TrFaF, and FeFF; groups = TrGF, TiGdF, TiGvF, Ta1GF, Ta3GF, Ta5GF;
singles = FeSF, Ta1SF).

## Variability (VERIFIED) — this matters for a sim

- *"the number and relative arrangement of CS varied between individuals, and single CS of
  corresponding segments showed characteristic differences between legs."*
- *"as a general rule, numerical variability was higher when there were larger numbers of sensilla,
  and little numerical variability if any was seen for groups with fewer than four sensilla."*
- **Invariant across all samples:** the two single CS (FeS, Ta1S), the three 2-CS groups
  (TiGd, Ta1G, Ta3G), and TrG (3 CS).
- **Most variable:** TrFp (7 sensilla in **6 of 28** samples) and FeF (10 or 12 in **5 of 20** samples).
- *"only four locations showed variability in the number (±1 CS)"* across the whole study.
- Arrangement is also variable where number is not: the 3 CS of TiGv form either a **triangular** or a
  **linear** arrangement; the smallest and least eccentric of the three is **consistently in the
  middle position**.

## Morphology (VERIFIED)

- CS caps are ellipses; eccentricity is reported qualitatively throughout (0 = circle, →1 = elongated).
  Trochanteral field CS all have eccentricity "closer to 1". In FeF, **3 of the ~11 CS are less
  eccentric than the other 8**. FeS is less eccentric than Ta1S on every leg.
  Cap **orientation/eccentricity is the directional-tuning substrate** in the CS literature — an
  elongated cap is compressed selectively by strain perpendicular to its long axis.
- Cap surfaces are mostly smooth; rare depressions/elevations **3–5 nm** in diameter seen on Ta5S,
  TiGvM and outside the collar of FeS.
- SEM scale bars on leg CS images are **15 µm**, so individual CS caps are of order a few µm.
  **Exact cap diameters are not tabulated in the text — could not verify a cap size number.**

## Non-leg CS (VERIFIED, for completeness)

- Haltere dorsal scabellum field **d.Scab = 44 CS** (Chevalier 1969 reported ~45; Cole & Palka 1982
  reported 42). Dorsal pedicellus **d.Ped = 43 CS**. Two single CS (d.Scab.s, d.Ped.s) which they
  argue should be split out from the fields.
- Haltere ventral pedicellus **v.Ped ≈ 39 CS** (counting difficult; Cole & Palka 1982 reported 46);
  ventral scabellum **v.Scab = 4 CS** (Cole & Palka reported 5).
- Wing: d.Rad.C had **17 CS in one fly and 18 in another**; another field had 4 vs 5 across two flies.

## Prior descriptions this paper reconciles (VERIFIED)

Merritt & Murphey (1992) and Yasuyama & Salvaterra (1999) described the prothoracic leg: 3 CS on
posterior trochanter (= TrGF), fields of 5 and 8 on dorsal trochanter (= TrFaF, TrFpF), **11 CS on
proximal ventral femur (= FeFF)**, a single dorsal femoral CS (= FeSF), 3 on ventral tibia (= TiGvF),
2 on dorsal tibia (= TiGdF), and a single ventral CS on tarsomere 1 (= Ta1SF). Good agreement.

## What this paper does NOT contain

- **No physiology at all.** No firing rates, no adaptation, no force thresholds, no encoding model.
  It is pure SEM morphology.
- No neuron counts (cap counts only).
- No male data (female flies; male equivalence is inferred from prior work).
- No cap diameters in numeric form in the text.
