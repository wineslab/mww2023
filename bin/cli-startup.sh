#!/bin/bash

ORCHNAME=$1

EMUBOOT=/var/emulab/boot
REPODIR=/local/repository
SHOUTSRC=/local/repository/shout

HNAME=`hostname`
HARR=(${HNAME//./ })
DOMELTS=${HARR[@]:1}
DOMAIN=${DOMELTS// /.}
ORCHHOST="$ORCHNAME.$DOMAIN"

cd $REPODIR
git submodule update --init --remote || \
    { echo "Failed to update git submodules!" && exit 1; }

sudo ntpdate -u ops.emulab.net && \
    sudo ntpdate -u ops.emulab.net || \
	echo "Failed to update clock via NTP!"

$SHOUTSRC/meascli.py -d -s $ORCHHOST

exit 0
