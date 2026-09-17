#!/bin/zsh
cd /home/nate/code/fly-afterlife
export FLYVIS_ROOT_DIR=/home/nate/code/fly-afterlife/flyvis_data
for i in 000 001 002 003 004 005 006 007 008 009; do
  uv run python seam/world_flyvis.py --geom seam/eye_geom.npz --model flow/0000/$i --stim empty yaw_left yaw_right --out seam/worldN_m$i > /dev/null 2>&1
  uv run python world/loop.py --mode drum --wheel dna02 --rest-sub --efference --model flow/0000/$i --seed 0 --seconds 12 --out world/ens/eff_m$i.npz --yawprefix seam/worldN_m$i > world/ens/eff_m$i.log 2>&1
  echo "model $i done $(date +%H:%M)"
done
echo "eff done $(date +%H:%M)"
