#!/bin/bash

REPODIR=/local/repository
MEASSRC=/local/repository/thesis/src

cd $REPODIR
git submodule update --init --remote || \
    { echo "Failed to update git submodules!" && exit 1; }

