#!/bin/zsh
cd /home/nate/code/fly-afterlife
export FLYVIS_ROOT_DIR=/home/nate/code/fly-afterlife/flyvis_data
for i in 000 001 002 003 004 005 006 007 008 009; do
  uv run python world/loop.py --mode drum --rest-sub --rest-chunks 100 --smooth 10 --model flow/0000/$i --seed 0 --seconds 12 --out world/ens/drum3_m$i.npz > world/ens/drum3_m$i.log 2>&1
  echo "model $i done $(date +%H:%M)"
done
echo "drum3 done $(date +%H:%M)"
