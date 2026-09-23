"""the solver's parameter vector (docs/SOLVER.md, "the parameter set"): nine numbers, each one scalar on a named set or a named knob.

CMA-ES works in a unit cube u in [0, 1]^9; decode() maps u to the physical values:
  gains     log-uniform on [0.25, 16]: g = 2 ** (-2 + 6 u), so u = 1/3 is the file's own weight (g = 1)
  pic_g     the small tibia flexors' plateau strength G (--pic smallflex:G:3:3:50), uniform on [0, 1]; the arms of record ran 0.58
  dng100_hz DNg100's rate (--walk), uniform on [30, 150] Hz; the arms of record ran 100

a gain reaches its cells through the size path, as ledger rows 28-30 did: the candidate CSV extends the base CSV (the graded tibia flexor
thresholds, ledger 5 / 17) with size = base size / g on every cell of the set, and the stack's --size-gain 1 --size-thr 1 --size-noise 1
--size-clip 20 turn that into inputs x g, threshold / g and membrane noise x g (each clipped to [1/20, 20]). so a "gain" here is the
size path's excitability, not a pure synaptic weight; the doc says so.
"""
from __future__ import annotations
import csv, os, numpy as np

BASE_CSV = "world/flex_graded.csv"

# name, cell types, ledger row(s), what it is
GAIN_SETS = [
    ("lift",     ["IN03A004", "IN17A028", "IN21A022", "IN21A010"], "28", "the lift side's swing-locked excitors"),
    ("release",  ["IN14A008", "IN13B013", "IN13B006", "IN13B004"], "30", "the hold side's swing-locked releasers (13B / 14A)"),
    ("hold13A",  ["IN13A002", "IN13A005", "IN13A003"], "31", "the hold side's 13A premotor inhibitors"),
    ("cmdinh",   ["IN12B003", "IN19A004"], "31", "the command's own inhibitors (IN19A004 onto the levators)"),
    ("levinh",   ["IN16B016", "IN19A008"], "31", "the levators' other tonic inhibitors"),
    ("subnet",   ["IN17A001", "INXXX466", "IN16B036", "IN19A007", "IN09A002", "INXXX464"], "31", "Pugliese's rhythm subnet"),
    ("levMN",    ["Tr flexor MN", "Acc. tr flexor MN"], "31", "the levator motor neurons themselves"),
]
GAIN_LO, GAIN_HI = 0.25, 16.0
NAMES = [s[0] for s in GAIN_SETS] + ["pic_g", "dng100_hz"]
DIM = len(NAMES)
LOGGED_TYPES = [t for s in GAIN_SETS for t in s[1] if not t.endswith(" MN")]   # --log-x on the body, --log-types on the cord

# the honest stack (experiments/body_loop.py) plus --walk-ramp 1, which every row 28-30 body arm ran; the per-candidate flags are added by body_flags()
BODY_STACK = ("--adhesion contact --senses v2 --size-thr 1 --size-gain 1 --size-noise 1 --size-clip 20 --syn-rev 70:-5:-5 --syn-rev-hold each "
              "--mn-force azevedo --load-from tarsi --hind-map v2 --start-pose feet --stiffness sourced --claw-labels 50flex --no-video --walk-ramp 1").split()
# the cord alone as rows 28-30 ran it (world/cord.py): the standing floor, the pinned flexion claw of a flexed standing tibia, the same size path and shunt
CORD_STACK = ("--floor standing --drive SNpp50:40 --size-thr 1 --size-gain 1 --size-noise 1 --size-clip 20 --syn-rev 70:-5:-5 --syn-rev-hold each").split()


def u_file() -> np.ndarray:
    """the file's own vector (every gain 1, G 0.58, DNg100 100 Hz) in the unit cube: the solve's start."""
    u = np.full(DIM, 1.0 / 3.0); u[NAMES.index("pic_g")] = 0.58; u[NAMES.index("dng100_hz")] = (100.0 - 30.0) / 120.0; return u


def decode(u) -> dict:
    u = np.clip(np.asarray(u, float), 0.0, 1.0); out = {}
    for i, (n, *_r) in enumerate(GAIN_SETS): out[n] = float(2.0 ** (-2.0 + 6.0 * u[i]))
    out["pic_g"] = float(u[NAMES.index("pic_g")]); out["dng100_hz"] = float(30.0 + 120.0 * u[NAMES.index("dng100_hz")])
    return out


def write_csv(p: dict, path: str, tag: str, brain_types=None, brain_ids=None) -> dict:
    """the base CSV with size = base / g on each set's cells. the header carries an extra, empty column named for the solver and the run
    (size.py reads bodyId and size only). returns {set: n cells touched}."""
    if brain_types is None:
        b = np.load("brain_cord.npz", allow_pickle=True); brain_types = b["type"].astype(str); brain_ids = b["bodyId"].astype(np.int64)
    scale = {}; n = {}
    for name, types, *_r in GAIN_SETS:
        ids = brain_ids[np.isin(brain_types, types)]; n[name] = int(len(ids))
        for b_ in ids: scale[int(b_)] = scale.get(int(b_), 1.0) / p[name]
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(BASE_CSV) as f, open(path, "w") as g:
        r = csv.DictReader(f); g.write(f"bodyId,size,{tag}_not_a_result\n")
        for row in r:
            b_ = int(row["bodyId"]); s = float(row["size"]) * scale.get(b_, 1.0); g.write(f"{b_},{s:.6g}\n")
    return n


def pic_flag(p: dict) -> str:
    return f"smallflex:{p['pic_g']:.4f}:3:3:50"


def body_flags(p: dict, csv_path: str, seed: int, seconds: float, out: str) -> list:
    return BODY_STACK + ["--size-from", csv_path, "--pic", pic_flag(p), "--walk", f"{p['dng100_hz']:.3f}", "--seed", str(seed), "--seconds", f"{seconds:g}",
                         "--log-x", ",".join(LOGGED_TYPES), "--out", out]


def cord_flags(p: dict, csv_path: str, seed: int, seconds: float, out: str, log_types: list) -> list:
    return CORD_STACK + ["--size-from", csv_path, "--pic", pic_flag(p), "--walk", f"{p['dng100_hz']:.3f}", "--seed", str(seed), "--seconds", f"{seconds:g}",
                         "--log-types", ",".join(log_types), "--out", out]


def describe(p: dict) -> str:
    return " ".join(f"{n} x{p[n]:.2f}" for n, *_r in GAIN_SETS) + f" | pic G {p['pic_g']:.2f} | DNg100 {p['dng100_hz']:.0f} Hz"
