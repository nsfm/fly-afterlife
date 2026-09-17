"""
run_many.py - fan simulation configs across cores.

    uv run python world/run_many.py --jobs 8 --script world/loop.py --common "--mode drum --wheel dna02 --rest-sub --seconds 12" \\
        --vary "--model flow/0000/{m} --out world/ens/par_m{m}.npz" --values m=000,001,002,003,004,005,006,007,008,009

each job is one process: {script} {common} {vary with substitutions}. flyvis models share the GPU (each
process ~0.8 GB; the 1650 holds four comfortably, so --jobs 4 when the config uses flyvis). CPU-only
configs (--no-vision) can use all cores. logs to <out>.log next to each --out. prints a summary table
of drum-following if the outputs are drum runs.
"""
import argparse, itertools, os, subprocess, sys, time, re
from concurrent.futures import ThreadPoolExecutor
ap = argparse.ArgumentParser(); ap.add_argument("--jobs", type=int, default=4); ap.add_argument("--script", required=True); ap.add_argument("--common", default=""); ap.add_argument("--vary", required=True); ap.add_argument("--values", required=True); a = ap.parse_args()
grid = {k: v.split(",") for k, v in (kv.split("=") for kv in a.values.split(";"))}
combos = [dict(zip(grid, vals)) for vals in itertools.product(*grid.values())]
env = dict(os.environ, FLYVIS_ROOT_DIR="/home/nate/code/fly-afterlife/flyvis_data", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1")
def run(c):
    vary = a.vary.format(**c); out = re.search(r"--out (\S+)", vary); log = (out.group(1) if out else "run_" + "_".join(c.values())) + ".log"
    cmd = f"uv run python {a.script} {a.common} {vary}"; t0 = time.time()
    with open(log, "w") as fh: rc = subprocess.call(cmd, shell=True, stdout=fh, stderr=subprocess.STDOUT, env=env, cwd="/home/nate/code/fly-afterlife")
    return c, rc, time.time() - t0
t0 = time.time()
with ThreadPoolExecutor(max_workers=a.jobs) as ex:
    for c, rc, dt in ex.map(run, combos): print(f"{c}  exit {rc}  {dt:.0f}s", flush=True)
print(f"{len(combos)} jobs in {time.time()-t0:.0f}s wall with {a.jobs} workers")
