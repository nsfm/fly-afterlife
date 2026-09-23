"""THE SOLVER's driver (docs/SOLVER.md; campaign ledger row 31). NOTHING it produces is a result: a fitted cord is a puppet by construction.

CMA-ES (pycma) over the nine-number vector of experiments/solver/params.py, in the unit cube. per candidate: the size CSV (the base CSV
extended), a cord-only prefilter (world/cord.py, --cord-seconds, rejected if the leg motor neurons' pooled mean rate leaves 0.5-60 Hz or
the cord runs away), then the honest body (experiments/body_loop.py, --seconds) on each seed, scored by objective.py and averaged.
at most --concurrent subprocesses at once, each with NUMBA_NUM_THREADS=--threads. checkpoint every generation to
experiments/solver/runs/<name>/; the same command line resumes; --hours is a hard budget for this invocation (a generation that cannot
finish in time is not started; one that overruns is killed at the deadline and left pending, and resumes from its finished evaluations).

    uv run python experiments/solver/run.py --name s1 --hours 12                              # the solve (popsize 8, 4 concurrent)
    uv run python experiments/solver/run.py --name s1 --hours 12                              # ... resumed, the same line
    uv run python experiments/solver/run.py --name smoke --popsize 4 --generations 1 --hours 0.3 --concurrent 2
    uv run python experiments/solver/run.py --name t1 --time-one --concurrent 2               # one evaluation at the file's vector, timed
"""
from __future__ import annotations
import os, sys, json, time, pickle, shutil, argparse, threading, subprocess, datetime, numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "experiments")); sys.path.insert(0, os.path.join(ROOT, "src"))
from solver import params as PR, objective as OB
from solver import TAG

ap = argparse.ArgumentParser(description="THE SOLVER (not a result): CMA-ES over labelled gains, scored on the honest body")
ap.add_argument("--name", required=True, help="the run's name; its directory is experiments/solver/runs/<name>/")
ap.add_argument("--hours", type=float, default=1.0, help="hard wall-clock budget for THIS invocation")
ap.add_argument("--popsize", type=int, default=8); ap.add_argument("--sigma0", type=float, default=0.2, help="CMA's initial step in the unit cube (0.2 = 1.2 octaves of gain)")
ap.add_argument("--generations", type=int, default=0, help="stop after this many generations in total (0 = until --hours or CMA stops)")
ap.add_argument("--concurrent", type=int, default=4, help="subprocesses at once (cord prefilters and body runs share the slots)")
ap.add_argument("--threads", type=int, default=4, help="NUMBA_NUM_THREADS per subprocess")
ap.add_argument("--seconds", type=float, default=20.0, help="body run length"); ap.add_argument("--seeds", default="11,12")
ap.add_argument("--cord-seconds", type=float, default=10.0); ap.add_argument("--cord-seed", type=int, default=11)
ap.add_argument("--cord-runaway-hz", type=float, default=10.0, help="the prefilter's runaway line: the whole cord's mean rate, Hz per cell, after the warm-up")
ap.add_argument("--no-prefilter", action="store_true")
ap.add_argument("--lift-rule", default="standard", choices=["standard", "fine"], help="the lift rule the stepping and coordination terms read (objective.LIFT_RULES): standard = leg_pairs.py's 21 ms / 50 ms (the default); fine = the replay reader's 5 ms / 10 ms, which sees an 11 Hz swing")
ap.add_argument("--keep-arrays", type=int, default=10, help="after each generation keep the .npz arrays and CSVs of the best K evaluations only (reads and logs are always kept)")
ap.add_argument("--run-timeout", type=float, default=2400.0, help="seconds before one subprocess is killed and scored as failed")
ap.add_argument("--cma-seed", type=int, default=1)
ap.add_argument("--time-one", action="store_true", help="evaluate the file's own vector once, report the timings, and exit (no CMA)")
args = ap.parse_args()

RUN = os.path.join(HERE, "runs", args.name); os.makedirs(os.path.join(RUN, "evals"), exist_ok=True)
LABEL = f"{TAG} {args.name}"; T_START = time.time(); DEADLINE = T_START + args.hours * 3600.0
LOCK = threading.Lock(); SLOTS = threading.Semaphore(args.concurrent); PROCS = set(); ABORT = threading.Event()
SEEDS = [int(s) for s in args.seeds.split(",") if s]


def now(): return datetime.datetime.now().isoformat(timespec="seconds")


def log(msg: str):
    line = f"{LABEL} | {now()} | {msg}"
    with LOCK:
        print(line, flush=True)
        with open(os.path.join(RUN, "log.txt"), "a") as f: f.write(line + "\n")


def dump(path: str, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f: json.dump(obj, f, indent=1, default=float)
    os.replace(tmp, path)


def legmn_types():
    from fly_afterlife.receptors import annotations
    a = annotations(); return sorted(set(a.loc[(a["superclass"] == "vnc_motor") & a["subclass"].isin(["fl", "ml", "hl"]), "type"].dropna().astype(str)))


def run_proc(cmd: list, logpath: str) -> tuple[int, float]:
    """one subprocess in a slot; killed on ABORT (the deadline) or --run-timeout. returns (returncode, seconds); -9 = killed."""
    with SLOTS:
        if ABORT.is_set() or time.time() > DEADLINE: return -9, 0.0
        env = dict(os.environ, NUMBA_NUM_THREADS=str(args.threads), PYTHONUNBUFFERED="1"); t0 = time.time()
        with open(logpath, "w") as lf:
            lf.write(f"# {LABEL}: NOT A RESULT\n# {' '.join(cmd)}\n"); lf.flush()
            p = subprocess.Popen(cmd, cwd=ROOT, env=env, stdout=lf, stderr=subprocess.STDOUT)
            with LOCK: PROCS.add(p)
            try:
                while True:
                    try: rc = p.wait(timeout=5.0); break
                    except subprocess.TimeoutExpired:
                        if ABORT.is_set() or time.time() > DEADLINE or time.time() - t0 > args.run_timeout:
                            p.kill(); p.wait(); rc = -9; break
            finally:
                with LOCK: PROCS.discard(p)
        return rc, time.time() - t0


MN_TYPES = None


def evaluate(gen: int, k: int, u, tag: str) -> dict:
    """one candidate, end to end. returns the evaluation record (also appended to evals.jsonl)."""
    p = PR.decode(u); d = os.path.join(RUN, "evals", tag); os.makedirs(d, exist_ok=True); stem = f"{TAG}_{args.name}_{tag}"
    csv_path = os.path.join(d, stem + ".csv"); t0 = time.time()
    ncells = PR.write_csv(p, csv_path, f"{TAG}_{args.name}")
    rec = dict(SOLVER=args.name, NOT_A_RESULT=True, gen=gen, k=k, tag=tag, u=[float(x) for x in u], params=p, cells=ncells, csv=csv_path, when=now())
    py = sys.executable
    if not args.no_prefilter:
        co = os.path.join(d, stem + "_cord")
        rc, tc = run_proc([py, "world/cord.py"] + PR.cord_flags(p, csv_path, args.cord_seed, args.cord_seconds, co + ".npz", MN_TYPES + PR.LOGGED_TYPES), co + ".log")
        rec["t_cord"] = tc
        if rc != 0:
            rec.update(total=-0.5, reason=f"cord run failed (rc {rc})", aborted=(rc == -9 and (ABORT.is_set() or time.time() > DEADLINE))); return finish(rec, t0)
        CR = OB.read_cord(co, legmn_types=MN_TYPES); rec["cord"] = CR
        why = OB.cord_verdict(CR, args.cord_runaway_hz)
        if why:
            # rejected before the body: below any body score, ordered by how far out the leg MNs' rate is (a slope for CMA)
            mn = max(CR["mn_mean_hz"], 1e-3); dist = max(np.log10(OB.MN_RANGE[0] / mn), np.log10(mn / OB.MN_RANGE[1]), 0.0)
            rec.update(total=float(-0.25 - 0.05 * min(dist, 5.0) - (0.1 if "runaway" in why else 0.0)), reason="prefilter: " + why); return finish(rec, t0)
    res = {}
    def one(seed):
        bo = os.path.join(d, f"{stem}_body_s{seed}")
        rc, tb = run_proc([py, "experiments/body_loop.py"] + PR.body_flags(p, csv_path, seed, args.seconds, bo), bo + ".log")
        if rc != 0: res[seed] = dict(rc=rc, t=tb); return
        try: R = OB.read_body(bo, args.lift_rule); res[seed] = dict(rc=0, t=tb, reads=R, score=OB.score(R))
        except Exception as e: res[seed] = dict(rc=-1, t=tb, err=repr(e))
    th = [threading.Thread(target=one, args=(s,)) for s in SEEDS]
    for t in th: t.start()
    for t in th: t.join()
    rec["body"] = {str(s): r for s, r in res.items()}; rec["t_body"] = {str(s): r["t"] for s, r in res.items()}
    if any(r["rc"] == -9 for r in res.values()): rec.update(total=-0.5, reason="killed at the deadline or the run timeout", aborted=ABORT.is_set() or time.time() > DEADLINE); return finish(rec, t0)
    sc = [r["score"]["total"] if r["rc"] == 0 else -0.25 for r in res.values()]
    rec["total"] = float(np.mean(sc)); rec["reason"] = "" if all(r["rc"] == 0 for r in res.values()) else "a body run failed: " + ", ".join(f"s{s} rc {r['rc']}" for s, r in res.items() if r["rc"] != 0)
    comps = [r["score"] for r in res.values() if r["rc"] == 0]
    if comps: rec["components"] = {c: float(np.mean([x[c] for x in comps])) for c in comps[0]}
    return finish(rec, t0)


def finish(rec: dict, t0: float) -> dict:
    rec["t_eval"] = time.time() - t0
    if rec.get("aborted"): log(f"{rec['tag']} ABORTED ({rec['reason']}); left pending"); return rec
    with LOCK:
        with open(os.path.join(RUN, "evals.jsonl"), "a") as f: f.write(json.dumps(rec, default=float) + "\n")
    log(eval_line(rec)); return rec


def eval_line(r: dict) -> str:
    s = f"{r['tag']} score {r['total']:+.4f} | {PR.describe(r['params'])} | {r['t_eval']:.0f} s"
    if "cord" in r: c = r["cord"]; s += f" | cord: leg MN {c['mn_mean_hz']:.2f} Hz, cord {c['cord_hz']:.2f} Hz/cell ({r.get('t_cord', 0):.0f} s)"
    if r.get("reason"): s += f" | {r['reason']}"
    for seed, b in r.get("body", {}).items():
        if b["rc"] != 0: s += f" | s{seed}: rc {b['rc']}"; continue
        R, S = b["reads"], b["score"]
        s += (f" | s{seed} ({b['t']:.0f} s): {S['total']:+.3f} [stand {S['stand']:.2f} step {S['step']:.2f} coord {S['coord']:.2f} prog {S['prog']:.2f} "
              f"-body {S['pen_body']:.2f} -mn {S['pen_mn']:.2f} -type {S['pen_type']:.2f}{' FELL' if S['fell'] else ''}] "
              f"feet/other/body {R['feet']:.2f}/{R['other']:.2f}/{R['body']:.2f} uN; lifts/s " + " ".join(f"{l} {R['lift_hz'][l]:.1f}" for l in OB.LEG6)
              + "; " + "; ".join(f"{nm} both-off x{R[nm]['ratio']:.2f} anti {R[nm]['anti']:.2f} (n {R[nm]['n']})" for nm, *_ab in OB.PAIRS)
              + f"; fwd {R['speed_fwd']:+.2f} mm/s; leg MN {R['mn_mean_hz']:.2f} Hz ({R['mn_below']} < 0.5, {R['mn_above']} > 60 of {R['mn_n']})"
              + (f"; over 200 Hz: {','.join(R['types_over'])}" if R["types_over"] else ""))
    return s


def evaluate_many(gen: int, U, done: dict) -> list:
    out = [None] * len(U); th = []
    for k, u in enumerate(U):
        tag = f"g{gen:03d}_c{k:02d}"
        if tag in done and np.allclose(done[tag]["u"], u): out[k] = done[tag]; continue
        def w(k=k, u=u, tag=tag): out[k] = evaluate(gen, k, u, tag)
        th.append(threading.Thread(target=w)); th[-1].start()
    for t in th: t.join()
    return out


def prune(keep: int):
    recs = load_done()
    ranked = sorted(recs.values(), key=lambda r: -r["total"]); top = {r["tag"] for r in ranked[:keep]}
    for r in ranked[keep:]:
        d = os.path.join(RUN, "evals", r["tag"])
        if not os.path.isdir(d): continue
        for f in os.listdir(d):
            if f.endswith(".npz") or f.endswith(".csv"): os.remove(os.path.join(d, f))


def load_done() -> dict:
    out = {}; fp = os.path.join(RUN, "evals.jsonl")
    if os.path.exists(fp):
        for ln in open(fp):
            if ln.strip(): r = json.loads(ln); out[r["tag"]] = r
    return out


def update_best():
    recs = load_done()
    if not recs: return None
    b = max(recs.values(), key=lambda r: r["total"]); p = b["params"]
    dump(os.path.join(RUN, "best.json"), dict(b, SOLVER=args.name, NOT_A_RESULT="a fitted cord is a puppet by construction; read the vector, not the walk"))
    if os.path.exists(b["csv"]): shutil.copyfile(b["csv"], os.path.join(RUN, f"{TAG}_{args.name}_best.csv"))
    else: PR.write_csv(p, os.path.join(RUN, f"{TAG}_{args.name}_best.csv"), f"{TAG}_{args.name}")
    with open(os.path.join(RUN, f"{TAG}_{args.name}_best_flags.txt"), "w") as f:
        f.write(f"# {LABEL}: the best vector's body command line; NOT A RESULT\n# {PR.describe(p)}; score {b['total']:+.4f} ({b['tag']})\n")
        f.write("uv run python experiments/body_loop.py " + " ".join(f"'{x}'" if " " in x else x for x in PR.body_flags(p, os.path.join(RUN, f"{TAG}_{args.name}_best.csv"), SEEDS[0], args.seconds, f"world/body/loop/{TAG}_{args.name}_best_s{SEEDS[0]}")) + "\n")
    return b


def main():
    global MN_TYPES
    MN_TYPES = legmn_types()
    cfg_path = os.path.join(RUN, "config.json")
    fixed = dict(popsize=args.popsize, sigma0=args.sigma0, seconds=args.seconds, seeds=args.seeds, cord_seconds=args.cord_seconds, cord_seed=args.cord_seed,
                 cord_runaway_hz=args.cord_runaway_hz, no_prefilter=args.no_prefilter, lift_rule=args.lift_rule, cma_seed=args.cma_seed)
    if os.path.exists(cfg_path):
        cfg = json.load(open(cfg_path)); diff = {k: (cfg["fixed"].get(k), v) for k, v in fixed.items() if cfg["fixed"].get(k) != v}
        if diff and not args.time_one: sys.exit(f"{LABEL}: resume with different fixed settings {diff}; use the original values or a new --name")
    else:
        dump(cfg_path, dict(SOLVER=args.name, NOT_A_RESULT=True, created=now(), fixed=fixed, names=PR.NAMES, sets=PR.GAIN_SETS, base_csv=PR.BASE_CSV,
                            body_stack=" ".join(PR.BODY_STACK), cord_stack=" ".join(PR.CORD_STACK), weights=weights()))
    log(f"start (NOT A RESULT): hours {args.hours}, popsize {args.popsize}, concurrent {args.concurrent} x {args.threads} threads, seeds {SEEDS}, body {args.seconds:g} s, cord {args.cord_seconds:g} s")
    if args.time_one:
        t0 = time.time(); r = evaluate(-1, 0, PR.u_file(), "time_one")
        log(f"time-one: one evaluation {time.time() - t0:.0f} s wall (cord {r.get('t_cord', 0):.0f} s; body " + ", ".join(f"s{s} {t:.0f} s" for s, t in r.get("t_body", {}).items()) + f"; {args.concurrent} slots)")
        return
    import cma
    es_path = os.path.join(RUN, "es.pkl"); pend_path = os.path.join(RUN, "pending.json")
    if os.path.exists(es_path):
        es = pickle.load(open(es_path, "rb")); log(f"resumed at generation {es.countiter}{' (a pending generation)' if os.path.exists(pend_path) else ''}")
    else:
        es = cma.CMAEvolutionStrategy(PR.u_file(), args.sigma0, dict(bounds=[0.0, 1.0], popsize=args.popsize, seed=args.cma_seed, verbose=-9))
    gen_times = []
    while not es.stop():
        gen = es.countiter if not os.path.exists(pend_path) else json.load(open(pend_path))["gen"]
        if args.generations and gen >= args.generations: log(f"stop: {gen} generations done (--generations)"); break
        left = DEADLINE - time.time(); est = float(np.mean(gen_times)) if gen_times else 0.0
        if left <= 0 or (gen_times and left < est): log(f"stop: {left / 60:.0f} min left in the budget, a generation takes ~{est / 60:.0f}"); break
        if os.path.exists(pend_path):
            P = json.load(open(pend_path)); U = [np.array(x) for x in P["U"]]
        else:
            U = es.ask(); dump(pend_path, dict(SOLVER=args.name, gen=gen, U=[list(map(float, x)) for x in U]))
            with open(es_path + ".tmp", "wb") as f: pickle.dump(es, f)
            os.replace(es_path + ".tmp", es_path)   # the post-ask state: a resume tells these same solutions
        tg = time.time(); log(f"generation {gen}: {len(U)} candidates")
        recs = evaluate_many(gen, U, load_done())
        if any(r is None or r.get("aborted") for r in recs) or time.time() > DEADLINE:
            ABORT.set(); log(f"generation {gen} did not finish inside the budget; pending, resumable"); break
        es.tell(U, [-r["total"] for r in recs])
        with open(es_path + ".tmp", "wb") as f: pickle.dump(es, f)
        os.replace(es_path + ".tmp", es_path); os.remove(pend_path)
        dump(os.path.join(RUN, f"gen_{gen:03d}.json"), dict(SOLVER=args.name, NOT_A_RESULT=True, gen=gen, sigma=float(es.sigma), mean_u=list(map(float, es.mean)), mean_params=PR.decode(es.mean),
                                                           population=[dict(tag=r["tag"], u=r["u"], params=r["params"], total=r["total"], reason=r.get("reason", ""), components=r.get("components")) for r in recs]))
        gen_times.append(time.time() - tg); b = update_best(); prune(args.keep_arrays)
        log(f"generation {gen} done in {gen_times[-1]:.0f} s: best of generation {max(r['total'] for r in recs):+.4f}, best so far {b['total']:+.4f} ({b['tag']}: {PR.describe(b['params'])}); "
            f"CMA mean {PR.describe(PR.decode(es.mean))}, sigma {es.sigma:.3f}")
    update_best(); log(f"end: {time.time() - T_START:.0f} s in this invocation")


def weights():
    return {k: getattr(OB, k) for k in ("W_STAND", "W_STEP", "W_COORD", "W_PROG", "STAND_FULL", "BODY_TOUCH", "P_BODY", "BODY_FALL", "FALL_FACTOR", "LIFT_BAND", "LIFT_SOFT", "LIFT_ZERO",
                                         "BOTH_OFF_GOOD", "BOTH_OFF_ZERO", "ANTI_GOOD", "ANTI_ZERO", "ANTI_N", "PAIR_LIFTS", "SPEED_CAP", "MN_RANGE", "P_MN", "TYPE_MAX", "P_TYPE", "P_TYPE_CAP")}


if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt:
        ABORT.set(); log("interrupted; the pending generation resumes from its finished evaluations")
    finally:
        with LOCK:
            for p in list(PROCS):
                try: p.kill()
                except Exception: pass
