#!/bin/bash

EMUBOOT=/var/emulab/boot
REPODIR=/local/repository
SHOUTSRC=/local/repository/shout

cd $REPODIR
git submodule update --init --remote || \
    { echo "Failed to update git submodules!" && exit 1; }

sudo ip route add 155.98.47.0/24 via 155.98.36.204

$SHOUTSRC/orchestrator.py -d

exit 0
