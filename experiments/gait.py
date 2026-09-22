"""gait.py - is his leg motor pattern walking-shaped? reads a <run>.cells.npz made with --log-types <every leg MN type>
--log-frames, groups the 373 leg motor neurons by leg (T1/T2/T3 x L/R, world/legmn.npz) and by muscle (the type name), and asks
the neck's question of the legs, at 10 ms:

  1. rates per muscle per leg, walking vs standing (Hz per cell);
  2. within a leg, do antagonists alternate (flexor vs extensor at each joint: negative correlation), co-contract (positive),
     or ignore each other (zero)?
  3. is there a rhythm: the power spectrum of each leg's total rate while walking, against standing;
  4. between legs, the phase: cross-correlation peak lag between legs (tripod: L1/R2/L3 together, against R1/L2/R3);
  5. per leg, left minus right against his turning.

    uv run python experiments/gait.py <run>.npz
"""
import sys, numpy as np

f = sys.argv[1].replace(".npz", "") + ".cells.npz"; C = np.load(f, allow_pickle=True)
ty = C["type"].astype(str); side = C["side"].astype(str); cells = C["cells"]; X = C["frames"].astype(np.float64); pose = C["pose_frame"]
n, k = X.shape; FPS = 100.0
lm = np.load("world/legmn.npz"); _bid = np.load("brain_whole.npz", allow_pickle=True)["bodyId"]; segof = {}   # legmn.npz indexes brain_whole; match by bodyId so the cord's own file (brain_cord.npz) reads too
for g in ("fl", "ml", "hl"):
    for s in "LR":
        for i in lm[f"{g}_{s}"]: segof[int(_bid[i])] = g
seg = np.array([segof.get(int(b), "?") for b in C["bodyId"]]); print(f"{n} frames ({n / FPS:.0f} s), {k} cells; by leg:", {g: int((seg == g).sum()) for g in ("fl", "ml", "hl", "?")})

# his speed and turning per frame, from the pose
dx = np.diff(pose[:, 0], prepend=pose[0, 0]); dy = np.diff(pose[:, 1], prepend=pose[0, 1]); v = np.hypot(dx, dy) * FPS
dh = (np.diff(pose[:, 2], prepend=pose[0, 2]) + 180) % 360 - 180; turn = dh * FPS   # deg/s, + = left
sm = lambda x, w: np.convolve(x, np.ones(w) / w, mode="same")
walking = sm(v, 25) > 0.08; standing = sm(v, 25) < 0.02
if pose[:, :2].std() == 0: walking = np.arange(n) >= 200; standing = np.zeros(n, bool); print('no pose (the headless cord): frames after 2 s count as walking, none as standing')
print(f"walking {walking.mean() * 100:.0f}% of frames, standing {standing.mean() * 100:.0f}%; speed while walking {v[walking].mean() if walking.any() else 0:.2f} m/s")

# muscle groups by type-name substring (legs.MUSCLE_W's vocabulary), antagonist pairs by joint
GROUPS = {
    "ThC retract": ("Pleural remotor", "Sternal posterior rotator"), "ThC protract": ("Sternal anterior rotator", "promotor"),
    "CTr depress": ("Sternotrochanter", "Tr extensor"), "CTr levate": ("Tr flexor", "Acc. tr flexor"),
    "FTi flex": ("Ti flexor", "Acc. ti flexor"), "FTi extend": ("Ti extensor",),
    "TiTa depress": ("Ta depressor",), "TiTa levate": ("Ta levator",),
    "ltm (grip)": ("ltm",), "Fe reductor": ("Fe reductor",), "Tergotr (jump)": ("Tergotr",), "Sternal adductor": ("Sternal adductor",),
}
PAIRS = [("ThC retract", "ThC protract"), ("CTr depress", "CTr levate"), ("FTi flex", "FTi extend"), ("TiTa depress", "TiTa levate")]
def grp(t):
    for g, keys in GROUPS.items():
        if any(kk in t for kk in keys): return g
    return "unnamed"
group = np.array([grp(t) for t in ty])
LEGS = [(g, s) for g in ("fl", "ml", "hl") for s in "LR"]; LEGNAME = {("fl", "L"): "L1", ("fl", "R"): "R1", ("ml", "L"): "L2", ("ml", "R"): "R2", ("hl", "L"): "L3", ("hl", "R"): "R3"}

# 1. rates per muscle group per leg, walking vs standing
print("\n1. Hz per cell by muscle group and leg: walking / standing")
gs = [g for g in list(GROUPS) + ["unnamed"] if (group == g).any()]
print(f"{'group':18s}" + "".join(f"{LEGNAME[l]:>13s}" for l in LEGS))
for g in gs:
    row = f"{g:18s}"
    for (sg, sd) in LEGS:
        m = (group == g) & (seg == sg) & (side == sd)
        if not m.any(): row += f"{'-':>13s}"; continue
        w_ = X[walking][:, m].mean() * FPS if walking.any() else 0; s_ = X[standing][:, m].mean() * FPS if standing.any() else 0
        row += f"{w_:6.1f}/{s_:<5.1f} "
    print(row)

# 2. antagonists within a leg: correlation of the two groups' summed rates, smoothed 30 ms, walking frames
print("\n2. antagonist correlation within each leg (30 ms smoothing, walking frames; negative = alternation)")
print(f"{'joint':26s}" + "".join(f"{LEGNAME[l]:>7s}" for l in LEGS))
for a, b in PAIRS:
    row = f"{a + ' vs ' + b:26s}"
    for (sg, sd) in LEGS:
        ma = (group == a) & (seg == sg) & (side == sd); mb = (group == b) & (seg == sg) & (side == sd)
        if not (ma.any() and mb.any()) or not walking.any(): row += f"{'-':>7s}"; continue
        A = sm(X[:, ma].sum(1), 3)[walking]; B = sm(X[:, mb].sum(1), 3)[walking]
        row += f"{np.corrcoef(A, B)[0, 1]:+7.2f}" if A.std() > 0 and B.std() > 0 else f"{'flat':>7s}"
    print(row)

# 3. rhythm: power spectrum of each leg's total rate, walking vs standing, 0.5-25 Hz
print("\n3. the rhythm: peak of the power spectrum of each leg's total rate (1-25 Hz), walking vs standing; ratio of peak power to the band's median")
def spec(x):
    x = x - x.mean(); F = np.abs(np.fft.rfft(x * np.hanning(len(x)))) ** 2; fr = np.fft.rfftfreq(len(x), 1 / FPS); m = (fr >= 1) & (fr <= 25)
    return fr[m], F[m]
for (sg, sd) in LEGS:
    m = (seg == sg) & (side == sd); out = f"{LEGNAME[(sg, sd)]}: "
    for nm, sel in (("walking", walking), ("standing", standing)):
        if sel.sum() < 200: out += f"{nm}: too few frames; "; continue
        # longest contiguous stretch
        idx = np.flatnonzero(sel); brk = np.flatnonzero(np.diff(idx) > 1); starts = np.r_[0, brk + 1]; ends = np.r_[brk, len(idx) - 1]; j = np.argmax(ends - starts); run = idx[starts[j]:ends[j] + 1]
        if len(run) < 200: out += f"{nm}: longest bout {len(run) / FPS:.1f} s, too short; "; continue
        fr, F = spec(X[run][:, m].sum(1)); pk = np.argmax(F); out += f"{nm} ({len(run) / FPS:.1f} s bout): peak {fr[pk]:.1f} Hz, x{F[pk] / max(np.median(F), 1e-12):.1f} the median; "
    print(out)

# 4. between legs: cross-correlation peak lag of band-passed (1-15 Hz) total rates, walking frames
print("\n4. inter-leg phase (walking; cross-correlation of each leg's rate, 30 ms smoothing, peak lag within +-150 ms; tripod: L1-R2, R2-L3, L1-L3 in phase; L1-R1, L1-L2 anti-phase)")
if walking.sum() > 300:
    sig = {l: sm(X[:, (seg == l[0]) & (side == l[1])].sum(1), 3) for l in LEGS}
    for l in LEGS: sig[l] = sig[l] - sm(sig[l], 50)   # remove the slow envelope (the bouts)
    W = walking; lags = np.arange(-15, 16)
    print(f"{'':6s}" + "".join(f"{LEGNAME[l]:>16s}" for l in LEGS))
    for a in LEGS:
        row = f"{LEGNAME[a]:6s}"
        for b in LEGS:
            xa, xb = sig[a][W], sig[b][W]
            if xa.std() == 0 or xb.std() == 0: row += f"{'flat':>16s}"; continue
            cc = [np.corrcoef(xa[max(0, -L):len(xa) - max(0, L)], xb[max(0, L):len(xb) - max(0, -L)])[0, 1] for L in lags]
            j = int(np.argmax(np.abs(cc))); row += f"{cc[j]:+6.2f}@{lags[j] * 10:+4d}ms  "
        print(row)
else: print("too few walking frames")

# 5. per leg L-R against turning
print("\n5. left minus right per leg against his turning (100 ms smoothing; + would mean more left-leg drive when he turns left)")
for g in ("fl", "ml", "hl"):
    L = sm(X[:, (seg == g) & (side == "L")].sum(1), 10); R = sm(X[:, (seg == g) & (side == "R")].sum(1), 10); d = L - R; t_ = sm(turn, 10)
    print(f"  T{['fl', 'ml', 'hl'].index(g) + 1}: corr(L-R, turn) {np.corrcoef(d, t_)[0, 1]:+.3f}; L {L.mean() * FPS:.0f} Hz, R {R.mean() * FPS:.0f} Hz summed")
tot = sm(X.sum(1), 10); print(f"  all legs summed vs speed: corr {np.corrcoef(tot, sm(v, 10))[0, 1]:+.3f}")

# 6. the chunk seam: rate by frame-within-chunk (the world updates once a chunk; a beat at the chunk rate is the seam, not the cord)
print("\n6. the chunk seam: spikes per frame summed over the leg by frame-within-chunk (0..9), whole run; peak / trough (1.0 = no seam)")
CHK = 10; nn = (n // CHK) * CHK
for (sg, sd) in LEGS:
    x = X[:nn, (seg == sg) & (side == sd)].sum(1).reshape(nn // CHK, CHK).mean(0)
    print(f"  {LEGNAME[(sg, sd)]}: {np.round(x, 2)}  x{x.max() / max(x.min(), 1e-9):.1f}")
