#!/bin/sh
# the refactor's regression check (docs/ARCHITECTURE.md step 1): the ported room must reproduce the
# frozen pre-refactor script bit for bit on four deterministic configs (seeds 3, 4 x old / corrected
# synapse constants, 30 s). oracle npz files are made once from world/oracle/pair_oracle.py (a copy of
# world/pair.py at commit df26aa7) and kept locally (npz is gitignored); rerun them with --make-oracle.
#   sh scripts/oracle_check.sh [--make-oracle]
cd "$(dirname "$0")/.." || exit 1
rm -f world/oracle/port_*.npz   # a failed run must not inherit a stale output from the last pass
for w in old new; do
  if [ "$w" = old ]; then WM=0.275; WF=0.45; else WM=0.185; WF=0.275; fi
  for s in 3 4; do
    if [ "$1" = "--make-oracle" ] || [ ! -f "world/oracle/room_${w}_s$s.npz" ]; then
      uv run python world/oracle/pair_oracle.py --seconds 30 --seed $s --deterministic --wsyn-m $WM --wsyn-f $WF --out "world/oracle/room_${w}_s$s.npz" > "world/oracle/room_${w}_s$s.log" 2>&1 || echo "oracle $w s$s FAILED"
    fi
    uv run python world/pair.py --seconds 30 --seed $s --deterministic --wsyn-m $WM --wsyn-f $WF --bristle hold --legmn all --no-floor --out "world/oracle/port_${w}_s$s.npz" > "world/oracle/port_${w}_s$s.log" 2>&1 || echo "port $w s$s FAILED"
  done
done
uv run python - <<'PY'
import numpy as np, os
ok = True
for w in ('old', 'new'):
    for s in (3, 4):
        fa, fb = f'world/oracle/room_{w}_s{s}.npz', f'world/oracle/port_{w}_s{s}.npz'
        if not (os.path.exists(fa) and os.path.exists(fb)): print(f'{w} s{s}: missing'); ok = False; continue
        a = np.load(fa, allow_pickle=True); b = np.load(fb, allow_pickle=True)
        bad = [k for k in a.files if k not in b.files or not np.array_equal(a[k], b[k])]
        print(f'{w} s{s}: {len(a.files)} arrays, differing: {bad or "none"}'); ok &= not bad
print('ORACLE CHECK', 'PASS' if ok else 'FAIL')
PY
