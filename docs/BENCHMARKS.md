# benchmarking his wandering against real flies

2026-09-18 (nyx), from nate's question: yes, there is something to score him against. an
open-field trajectory literature, one paper with a generative model we can run head to head
against ours, and several downloadable corpora that survive inspection. nothing here is invented;
where a value exists only inside a figure i could not read, it says so.

## our units, first

1 sim metre = 1.5 cm = 15 mm; his body is 0.16 sim m = 2.4 mm, the standard length of a
*melanogaster* adult. everything below is in mm and body lengths so it can be compared.

| quantity | sim units | mm | body lengths |
|---|---|---|---|
| his body | 0.16 m | 2.4 | 1 |
| the garden patch | 6 x 6 m | 90 x 90 | 37.5 across |
| the room | 4 x 4 m | 60 x 60 | 25 across |
| his walking speeds | 0.15-0.5 m/s | 2.3-7.5 | 0.9-3.1 /s |
| the literature's 6 mm edge zone | 0.4 m | 6 | 2.4 |

the speed row is the known scale choice and the benchmark flags it first: real flies walk at
4.5-6.2 body lengths per second at room temperature, ours tops out at 3.1. the arena rows are
better news: at 25 and 37.5 body lengths across, both our boxes sit inside the band the literature
uses.

## speed: bimodal, and everyone agrees

every paper that plots a speed histogram finds two modes, one at zero and one in the low tens of
mm/s. the walking mode moves with temperature, which matters for picking a target.

| source | arena, light, flies | stop threshold | walking mode, and spread |
|---|---|---|---|
| Valente, Golani & Mitra 2007, *PLoS ONE* 2(10):e1083 | 15 cm circle, 25 Hz, one wild-type fly, 2 h | 0.1 cm/s | 1.48 cm/s centre, 1.14 rim; mode transition 0.75 / 0.4 cm/s (fig. 4a-b) |
| DeAngelis, Zavatone-Veth & Clark 2019, *eLife* 8:e46409 | 5 cm circle, 34 C, 150 fps, 114 females 1-2 d | 0.5 mm/s | peaks at 0 and ~17.5 mm/s (fig. 1C); 2.5-97.5 pct = -1.3 to 30.4 |
| Katsov, Freifeld, Horowitz, Kuehn & Clandinin 2017, *eLife* 6:e26410 | 25 x 150 mm tubes and a 300 mm arena, 30 fps, 7364 female Oregon-R | - | translation binned -0.6 to 3.2 cm/s, sideslip under 0.94, rotation under 450 deg/s |

Gattuso et al. 2025, *PNAS* 122:e2407626122 (4 x 14 cm arena, females 3-8 d) agree in shape: "a
peak near zero, and ground speeds from 5-20 mm/s" (fig. 2C), with no means in the text. the 34 C
in DeAngelis is why their walking mode is the fastest of the set; Valente's 11-15 mm/s at room
temperature is our target.

## bouts: short walks, shorter stops, a fat tail on the stops

Valente 2007 is the only paper i found that fits durations directly, split by zone (fig. 8):
walking segments decay with a time constant of 2.1 s in the centre and 1.37 s at the rim, "rarely
more than 10 s"; near-zero-speed segments decay on 0.14 s (centre) and 0.17 s (rim); 76% of rim
stops are under 0.3 s, while centre stops carry finite probability past 5 s.

Katsov 2017 reaches the same structure from the other end, cutting behaviour into 15 submodes in 5
modes (stops and dithers, sharp and shallow turns, side-slips, slow runs, fast straight walking).
a first-order Markov chain suffices: the previous submode explains rho = 0.271 of the uncertainty
about the next, the one before adds 0.015, the chain stays predictive for 4.3 +/- 0.55 s, and
dwell times are near-exponential (fig. 5G).

Martin 2004, *Behav. Processes* 67:207-219, is the paper nate remembered: inactivity episode
durations follow a power law and activity episodes do not, in "a small square arena". the
exponent, arena size, speed and meander are paywalled - shape confirmed, numbers not read. Martin,
Faure & Ernst 2001, *J. Neurogenetics* 15:1-15, show that blocking ellipsoid-body synapses
destroys that power law: a good later target, given we have a central complex.

## turning

**turn angle.** Soibam et al. 2012, *PLoS ONE* 7(10):e46570, at dt = 0.04 s, find 60%, 72% and 80%
of movements restricted to turn angles under 30, 45 and 60 degrees. their companion (Soibam et al.
2012, *Brain and Behavior* 2(2):97-108) resamples at 1 s and finds the modal turn angle is 12.6
degrees at the edge and 3.6 in the centre (chi-square 43,412, p < 0.0001). neither number means
anything without its sampling interval; our 100 Hz log must be decimated to match.

**angular velocity.** Katsov 2017 bin rotation over 450 deg/s and find peaks separated by 250 +/-
110 ms, roughly four turning events a second in active walking. Gattuso 2025 define a turn as an
upward crossing of 45 deg/s in absolute angular velocity - copy that exactly. DeAngelis 2019 call
the lateral and angular velocity distributions "roughly symmetric"; widths in fig. 1C only.

**handedness.** Buchanan, Kain & de Bivort 2015, *PNAS* 112:6700-6705, ran 25,000 flies through
Y-mazes, 2 h each, for 16 million turn choices. mean right-turn probability is ~0.5, but 23.5% of
Canton-S individuals turn right over 70% or under 30% of the time, far beyond the binomial null (p
< 1e-16), and sequential turns are independent. the same flies in 2-inch arenas show a persistent
circling bias correlated with their maze score (112 flies, fig. S2e-g), stable across days (r =
0.81 at 1 day, 0.57 at 28). Ayroles et al. 2015, *PNAS* 112:6706-6711, adds that the *magnitude*
of that variability is heritable, mapping to *Ten-a* and the central complex. so a run of ours
should show *some* bias; the test is that our per-seed biases sit inside the spread.

## spatial statistics: the wall is the strongest effect in the literature

| source | arena | flies | time near the boundary |
|---|---|---|---|
| Soibam et al. 2012, *Brain Behav* 2(2):97-108 | 8.4 cm circle, 0.7 cm wall, lit, 22-24 C, 30 fps, 10 min | Canton-S males, 2-5 d | 89.9% in the outer third of the radius (fig. 2) |
| Soibam et al. 2012, *PLoS ONE* 7(10):e46570 | 4.2 cm radius circle | Canton-S | 88% within 0.6 cm of the wall, "over 90% within 6 mm"; mutants 72-79% |
| Valente, Golani & Mitra 2007 | 15 cm circle, 2 h | one wild-type fly | 42% within 1 cm of the wall (fig. 3) |
| Besson & Martin 2005, *J. Neurobiol.* 62:386-396 | open field, video tracked | MB-ablated vs wild type | centre avoidance greatly reduced by MB ablation and by blocking the gamma lobes; percentages not read |

the spread from 42% to 90% is arena size and duration, not disagreement. Valente's arena is 60
body lengths across over two hours; Soibam's is 34 over ten minutes. ours are 25 and 37.5, so
Soibam is the target and Valente the sanity floor.

Soibam argues the preference is neither thigmotaxis nor centrophobism, and not a by-product of
walking straight: in an hourglass arena whose convex walls force a straight-versus-wall choice, a
straight-trajectory simulation crosses the central gap while real flies follow the wall. blind
*norpA* and *w1118* flies fail to attenuate their initial activity, and raising the edge contrast
rescues it - the boundary is a *visual* object of exploration. our fly has both vision and a touch
reflex; if he wall-follows only on contact, he is doing it by the wrong mechanism even when the
percentage comes out right. the hourglass is the discriminating experiment, and cheap.

**the square case.** ours are square, the literature mostly circular. Soibam's *PLoS ONE* paper
ran a 7.2 cm square split into 16 sectors as 4 corner, 8 wall, 4 centre, and reports corner
occupancy (time fraction over area fraction) of 4.692 +/- 0.268, walls preferred over centre,
their model matching all three (p = 0.141, 0.123, 0.145). near 4.7 is the square-arena target; in
60/120-degree parallelograms flies prefer the acute corners (p = 0.011).

## an algorithm we can run against ours

the best answer to nate's question. Soibam et al. 2012 (*PLoS ONE* 7(10):e46570) publish a
complete two-component generative model of open-field position: **directional persistence** in the
interior, step size r and turn angle theta drawn jointly from the empirical P(r, theta) over 272
real trajectories (binned 0.18 cm in r, 0.1 rad in theta, dt = 0.04 s); plus **wall attraction**,
F = F0 (1 - d/Rc), F0 = 0.0268 cm^-1 and Rc = 0.6 cm for Canton-S (fig. 6E; mutants
0.0217-0.0326). a two-parameter null that reproduces occupancy in square, hourglass,
internal-corner and Texas-shaped arenas - and *fails* on spirals, underestimating outer-zone
preference, which the authors read as a global mapping strategy it lacks. that failure is the
target: if our connectome fly beats a two-parameter random walk on the spiral, that is a real
result.

the analysis side has a maintained Python implementation: **opynfield** (McMullen et al. 2025,
*Neuroinformatics*, doi 10.1007/s12021-025-09753-2), GPL-3.0, PyPI 1.0.0,
github.com/EllenMcMullen/opynfield, Zenodo doi 10.5281/zenodo.15794680. it takes plain CSV of
time, x, y and computes activity, **coverage** (visits to boundary sectors, a novelty-habituation
measure) and **directional persistence P++** (probability the angle between consecutive steps is
<= 90 degrees). Canton-S references: activity 0.072 cm/step at steady state, coverage asymptote ~7
visits/sector, habituation rate ~0.008/s (figs. 3B, 4B, table 3). the catch: **circular arenas
only**.

## run lengths: not Levy, and the Levy claim is about flight

Reynolds & Frye 2007, *PLoS ONE* 2(4):e354, is the scale-free search paper and it is about **free
flight**: inverse-square inter-saccade intervals, ~90 degree saccades. it does not transfer.
Valente 2007 checked and found neither Gaussian processes nor Levy laws "particularly appropriate
here"; the walking model is Soibam's correlated random walk plus Katsov's Markov chain.

## the Berman behavioural space: not usable by us; Katsov's is

Berman, Choi, Bialek & Shaevitz 2014, *J. R. Soc. Interface* 11:20140672: a 100 mm dome, 100 Hz,
Oregon-R, 59 males and 51 females aged 1-14 d, one hour each, ~4e7 frames. 50 PCA postural
eigenmodes and a Morlet transform over 25 frequencies from 1-50 Hz, embedded by t-SNE and cut by
watershed, give **122 behavioural states**; flies sit in low-velocity stereotyped peaks roughly
45% of the time, and the fast running gait peaks at 12.9 Hz
(github.com/gordonberman/MotionMapper).

but it eats **postural** input - aligned images of the limbs. we log a centroid and a heading and
render no legs, so MotionMapper has nothing to work on. Katsov 2017 is the version that *does* fit
us, its feature space being (vT, vR, vS), exactly what we differentiate out of (x, y, heading).

## downloadable data

verified by opening the files, not by trusting landing pages. start with the first two.

| dataset | what is in it | arena, rate, flies | format, size, licence |
|---|---|---|---|
| **opynfield test data**, `test_data/` at github.com/EllenMcMullen/opynfield | the Roman lab's own corpus: 243 BuriTrack `.dat` + 272 Ethovision `.txt` runs, including a 5.0 vs 8.4 cm arena comparison | 8.4 cm circle, ~31 Hz, 600 s, Canton-S **males 2-5 d, alone, lit** | tab-separated `frame, time(ms), x, y, burst`; 334 MB; GPL-3.0 |
| **Corrales-Carvajal, Faisal & Ribeiro 2016**, *eLife*, Dryad 10.5061/dryad.s58qh, Zenodo 4950387 | one fly per arena, 2 h; head and body centroids, so heading is `atan2(head - body)` | 33 mm radius (27.5 body lengths), 50 fps, 146 Canton-S | plain CSV; 836 MB; CC0 |
| **Kim & Dickinson 2017**, Mendeley 10.17632/3rfdw7p6x6.1 | explicit `heading(radians)` and angular-velocity columns, mm units | 170 mm circle, 60 Hz, females, food at centre | CSV after a 3-section header; 2.56 GB; CC BY 4.0 |
| **York et al. 2022**, *Curr. Biol.* 32, Dryad 10.5061/dryad.z8w9ghxfc, Zenodo 7306160 | position and heading per frame, 1030 flies, 13 species | **1 m x 1 m**, 100 Hz, up to 20 min/fly, virgin females | `.RDS`; 2.01 GB; CC0; needs `pyreadr` or an R re-export |

the JAABA sample data (sourceforge.net/projects/jaaba/files/Sample Data/, 646 MB) adds one Fly
Bowl experiment as `registered_trx.mat` with x, y, theta per fly per frame - the canonical Janelia
format, but a demo, not a corpus. then four negatives, these being the ones everyone assumes have
trajectories. **the Janelia Fly Bowl / Robie 2017 screen is summary statistics only**: the
per-trial `data.csv` at research.janelia.org/bransonlab/FlyBowl/ is `field, value, zscore,
nflyframes` aggregates, and the 400,000-fly corpus is not public. **Katsov's Dryad deposit**
(10.5061/dryad.854j2, Zenodo 4941715, CC0) **has no positions**: `dataset_A.mat` under h5py holds
ten vectors, `UI T V1 VE VR VT VS VRTH VU VM`, over 1,022,954 samples - useless for spatial
metrics, exactly right for metric 13. **Berman's raw data was never deposited.** **the de Bivort
turn-bias file** (lab.debivort.org, 52,338 flies) is L/R choice sequences, not trajectories.
DeAngelis 2019 (Dryad 10.5061/dryad.3p9h20r, Zenodo 4956217, 8.33 GB) is named as step and limb
tables; whether centroid and heading survive is **not verified**. and Dryad now sits behind an
anti-bot wall that defeats scripted downloads - the Zenodo mirrors above carry the same DOIs and
work.

## the proposed benchmark

all computable from (x, y, heading) at 100 Hz with no new instrumentation. decimate to the
source's sampling interval before comparing.

| # | metric | published target | source |
|---|---|---|---|
| 1 | speed histogram bimodal, one mode at zero | two modes in every paper that plots one | Valente fig. 4; DeAngelis fig. 1C |
| 2 | walking-mode speed | 11-15 mm/s at room temperature; 17.5 at 34 C | Valente; DeAngelis |
| 3 | fraction below 1 mm/s | 1 mm/s is a stationary fly's noise floor | Valente 2007 |
| 4 | walking-bout duration, exponential fit | decay 1.37 s (rim) to 2.1 (centre); few over 10 s | Valente fig. 8 |
| 5 | pause duration | decay 0.14-0.17 s; 76% of rim stops under 0.3 s | Valente fig. 8; Martin 2004 |
| 6 | turn angle at dt = 0.04 s | 60 / 72 / 80% within 30 / 45 / 60 deg | Soibam *PLoS ONE* |
| 7 | turn angle at dt = 1 s | mode 12.6 deg at edge, 3.6 in centre | Soibam *Brain Behav* |
| 8 | turn rate, upward crossings of 45 deg/s | inter-turn interval 250 +/- 110 ms | Gattuso; Katsov |
| 9 | 99th percentile of \|omega\| | under ~450 deg/s | Katsov 2017 |
| 10 | time within 0.4 sim m (6 mm) of a wall | 88-90% at 34 body lengths; 42% at 60 | Soibam (both); Valente |
| 11 | corner occupancy, square arena | 4.69 +/- 0.27 | Soibam *PLoS ONE* fig. 2B |
| 12 | per-seed circling bias | population mean 0, individuals biased; spread not read | Buchanan fig. S2e |
| 13 | Markov order over (vT, vR, vS) submodes | first order explains rho = 0.271, second adds 0.015 | Katsov + its Dryad velocities |

**scoring, two tiers.** *tier A is a checklist*: rows 1, 3, 6, 7, 8, 9, 10 and 11 each give a
yes/no - is our value inside the published range, or inside the spread between studies where two
disagree. eight boxes, and the headline is how many we tick; most rows are one study's point
estimate and pretending we can do a likelihood would be theatre. *tier B is distribution
distance*: for speed, turn rate, wall distance and bout duration we have whole distributions on
both sides once the data is down - earth-mover's distance for the first three, which carry units,
Kolmogorov-Smirnov for the durations. calibrate "close" by computing the same distance *between
two published conditions*, opynfield's 5.0 cm set against its 8.4 cm, so the pass bar is real
spread and not a number we made up.

**the time-rescaling control.** our fly walks at a third of life speed, so every duration metric
(4, 5, 8, 13) is expected to be wrong in the same direction for a reason we already know. compute
each twice: raw, and with time rescaled by the ratio of our walking mode to the published one. if
the rescaled versions land and the raw ones do not, the decision timing is right and only the gait
speed is wrong - a completely different bug from the alternative.

**which protocol to reproduce.** Soibam et al. 2012, *Brain and Behavior*: an 8.4 cm circular
arena with a 0.7 cm wall, lit from above, Canton-S males 2-5 days old, alone, 10 minutes at 30
fps. it matches us on every axis that matters - male, alone, light on - and at 34 body lengths
across it sits between our room (25) and garden (37.5). its companion supplies the model and the
square-arena numbers, `opynfield` the analysis code, and the bundled `.dat` files that protocol's
raw trajectories. Corrales-Carvajal is the second, independent set, at almost exactly our room's
size.

two changes make the comparison fair. **add a circular arena**, 5.6 sim m across with a 0.47 m
rim: the quantitative literature is circular, `opynfield` supports circles only, and corners are a
separate effect we would otherwise confound with wall-following. keep the square garden and room
and add the circle as the benchmark fixture. and **run 600 s, not 120** - exploration is
non-stationary, activity decays through the trial, and 120 s samples only the initial
high-activity phase where wall-following is least comparable. if 600 s is too expensive, score
against the first two minutes of a published trial, not its whole-trial average, and say so every
time.

## corrections, and what i could not verify

three references in the brief needed fixing. **"Liu, Davis & Roman 2007, exploratory activity in
Drosophila requires the kurtosis of turning" does not exist** - the real paper is Liu, Davis &
Roman 2007, *Genetics* 175:1197-1212, "Exploratory activity in *Drosophila* requires the *kurtz*
nonvisual arrestin": a gene, not a moment of a distribution, and not a turning-statistics paper.
**Katsov et al. 2017 is Katsov, Freifeld, Horowitz, Kuehn & Clandinin**, not Golani/Mitra/Maimon;
those two are on Valente 2007 and on Gomez-Marin et al. 2016, *Sci. Rep.* 6:27555, which reuses
that 15 cm arena with nine Canton-S males but is about cocaine. and **Reynolds & Frye 2007 is
flight**.

not read, and never quoted as a number above: Martin 2004's arena size, speed, episode counts,
turning angle, meander and power-law exponent (paywalled; the abstract confirms only the shape of
the result and the square arena); Besson & Martin 2005's centre-versus-periphery percentages
(abstract only); the widths of DeAngelis 2019's velocity distributions (fig. 1C); `opynfield`'s
and Berman's per-timepoint P++ and stereotypy values (figures only); Buchanan's circling-score
distribution (fig. S2e); and Gattuso's baseline means, which exist only as ranges and figures.

two dataset caveats: the `.xml` headers bundled with opynfield's `.dat` files carry a stale
default BuriTrack template (`ARENA_DIAMETER_MM 115`, stripe fields) contradicting the paper's 8.4
cm, so take arena scale from the paper and not the XML; and those trajectories are centroid-only,
so heading must be derived from velocity direction and is undefined while stopped.
