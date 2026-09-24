"""kin_lock_rank.py <hearing_run> <deaf_run>: which logged types lock to the imposed step (kin-drive), ranked. per type from x_ms (1 ms) and
kin_swing (per ms, per leg; a cell is read against its own leg's cycle when its leg is known, else against the left front's): rate, the
swing/stance rate ratio, the vector strength of its spikes' phase in the imposed cycle (0 = swing onset) against a rolled-train null (20
draws, the 95th percentile), and the same type's vector strength in the deaf run (the cord under the same command, the senses off), which
is the noise floor for that type. locked = above its own null AND above the deaf run's value by the null's width. (09-23, the listening rig)"""
import sys, numpy as np
lm = np.load("world/legmn.npz"); wb = np.load("brain_whole.npz", allow_pickle=True)["bodyId"].astype(np.int64); legof = {}
LEGS = ["lf", "lm", "lh", "rf", "rm", "rh"]; KEY = {"fl_L": 0, "ml_L": 1, "hl_L": 2, "fl_R": 3, "ml_R": 4, "hl_R": 5}
for k, li in KEY.items():
    for i in lm[k]: legof[int(wb[i])] = li
# interneurons: the leg from world/interleg.csv (the census's per-cell 'to_legs', the legs its output reaches, first listed; soma side breaks ties)
try:
    import csv
    for row in csv.DictReader(open("world/interleg.csv")):
        tl = row.get("to_legs", "") or row.get("from_legs", "")
        if tl:
            first = tl.split(";")[0].split(",")[0].strip()
            if first in LEGS: legof.setdefault(int(row["bodyId"]), LEGS.index(first))
except Exception as e: print("interleg.csv not used:", e)
rng = np.random.default_rng(0)
def cycles(sw):
    on = np.flatnonzero(np.diff(sw.astype(int)) == 1) + 1; return on
def phases(spk_ms, on):
    if len(on) < 3: return np.zeros(0)
    idx = np.searchsorted(on, spk_ms, side="right") - 1; ok = (idx >= 0) & (idx < len(on) - 1)
    a = on[idx[ok]]; b = on[idx[ok] + 1]; return (spk_ms[ok] - a) / (b - a)
def vs(ph): return np.abs(np.exp(2j * np.pi * ph).mean()) if len(ph) else 0.0
def read(path):
    D = np.load(path + ".npz", allow_pickle=True); C = np.load(path + ".cells.npz", allow_pickle=True); X = C["x_ms"].astype(np.int16); xt = C["x_type"].astype(str); xb = C["x_bodyId"].astype(np.int64); SW = D["kin_swing"].astype(bool); n = min(len(X), len(SW)); X = X[:n]; SW = SW[:n]
    t0 = 3000; out = {}
    for t in sorted(set(xt)):
        m = np.flatnonzero(xt == t); legs = [legof.get(int(xb[i]), 0) for i in m]; leg = max(set(legs), key=legs.count)
        sw = SW[:, leg]; on = cycles(sw); on = on[on >= t0]; col = X[:, m].sum(1); spk = np.flatnonzero(col[t0:] > 0) + t0
        # weight repeated spikes in a ms by count
        spk = np.repeat(spk, col[spk].astype(int))
        if len(spk) < 30: out[t] = None; continue
        rate = len(spk) / ((n - t0) / 1000) / len(m); insw = sw[spk].mean(); frac = sw[t0:].mean(); ratio = (insw / max(frac, 1e-9)) / max((1 - insw) / max(1 - frac, 1e-9), 1e-9)
        ph = phases(spk, on); v = vs(ph); null = np.array([vs(phases((spk + rng.integers(0, n - t0)) % (n - t0) + t0, on)) for _ in range(20)])
        out[t] = dict(rate=rate, ratio=ratio, vs=v, null=float(np.quantile(null, 0.95)), phase=float(np.angle(np.exp(2j * np.pi * ph).mean()) / (2 * np.pi) % 1), n=len(spk), leg=LEGS[leg])
    return out
H = read(sys.argv[1]); Dd = read(sys.argv[2]) if len(sys.argv) > 2 else {}
rows = []
for t, r in H.items():
    if r is None: continue
    d = Dd.get(t); dv = d["vs"] if d else 0.0; locked = r["vs"] > r["null"] and r["vs"] > dv + (r["null"] * 0.5)
    rows.append((r["vs"] - r["null"], t, r, dv, locked))
rows.sort(reverse=True)
print(f"{'type':22s} {'leg':3s} {'Hz':>6s} {'sw/st':>6s} {'VS':>5s} {'null':>5s} {'deaf':>5s} {'phase':>5s} {'n':>6s}  locked")
for margin, t, r, dv, locked in rows[:60]: print(f"{t:22s} {r['leg']:3s} {r['rate']:6.1f} {r['ratio']:6.2f} {r['vs']:5.2f} {r['null']:5.2f} {dv:5.2f} {r['phase']:5.2f} {r['n']:6d}  {'LOCKED' if locked else ''}")
print(f"\n{sum(1 for x in rows if x[4])} of {len(rows)} types locked; {sum(1 for x in rows if x[4] and x[2]['ratio'] > 1)} of them fire more in the imposed swing")
