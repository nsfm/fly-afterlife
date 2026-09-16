#!/bin/zsh
cd /home/nate/code/fly-afterlife
export FLYVIS_ROOT_DIR=/home/nate/code/fly-afterlife/flyvis_data
mkdir -p world/ens
for i in 000 001 002 003 004 005 006 007 008 009; do
  uv run python world/loop.py --mode drum --model flow/0000/$i --seed 0 --seconds 12 --out world/ens/drum_m$i.npz > world/ens/drum_m$i.log 2>&1
  uv run python world/loop.py --mode walk --model flow/0000/$i --seed 0 --seconds 20 --out world/ens/walk_m$i.npz > world/ens/walk_m$i.log 2>&1
  echo "model $i done $(date +%H:%M)"
done
echo "ensemble behaviour done $(date +%H:%M)"
