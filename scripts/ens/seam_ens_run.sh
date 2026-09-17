#!/bin/zsh
cd /home/nate/code/fly-afterlife
export FLYVIS_ROOT_DIR=/home/nate/code/fly-afterlife/flyvis_data
for i in 000 001 002 003 004 005 006 007 008 009; do
  uv run python seam/world_flyvis.py --geom seam/eye_geom.npz --model flow/0000/$i --stim empty loom_left recede_left static_left loom_right recede_right static_right yaw_left yaw_right --out seam/ens/m$i > seam/ens/m$i.render.log 2>&1
  uv run python seam/seam_v2.py --geom seam/eye_geom.npz --prefix seam/ens/m$i --rest empty --stims loom_left recede_left static_left loom_right recede_right static_right yaw_left yaw_right --seeds 0 --out seam/ens/m$i.json > seam/ens/m$i.seam.log 2>&1
  echo "model $i done $(date +%H:%M)"
done
uv run python seam/ensemble_summary.py > seam/ens/SUMMARY.txt 2>&1
echo "ensemble done $(date +%H:%M)"
