#!/bin/zsh
cd /home/nate/code/fly-afterlife
export FLYVIS_ROOT_DIR=/home/nate/code/fly-afterlife/flyvis_data
uv run python world/pair.py --seconds 300 --seed 1 --out world/pair_long.npz > world/pair_long.log 2>&1
uv run python world/export_viewer.py world/pair_long.npz - world/viewer_room_5min.html "the room, five minutes" 4 >> world/pair_long.log 2>&1
echo "long room done $(date +%H:%M)" >> world/pair_long.log
