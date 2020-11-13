#!/bin/bash

EMUBOOT=/var/emulab/boot
REPODIR=/local/repository
SHOUTSRC=/local/repository/shout

cd $REPODIR
git submodule update --init --remote || \
    { echo "Failed to update git submodules!" && exit 1; }

$SHOUTSRC/orchestrator.py -d

exit 0
