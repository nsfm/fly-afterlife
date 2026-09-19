#!/bin/sh
# the Roman lab's open-field trajectories bundled with opynfield (McMullen et al. 2025; github.com/EllenMcMullen/opynfield, GPL-3.0):
# Canton-S males, alone, lit, 600 s at ~33 Hz, in 8.4 cm and 5.0 cm circular arenas. tab-separated time (s), x, y (cm).
# fetches the first N runs of each arena size into data/opynfield/ (not committed: their data, their licence).
N=${1:-20}
for d in 8.4cm 5.0cm; do mkdir -p data/opynfield/$d; i=1; while [ $i -le $N ]; do
  [ -f data/opynfield/$d/run$i.txt ] || curl -sL -o data/opynfield/$d/run$i.txt "https://raw.githubusercontent.com/EllenMcMullen/opynfield/main/test_data/Analysis2_ArenaSizeComparison/Data/$d/run$i.txt"; i=$((i+1)); done; done
ls data/opynfield/*/ | head -3
