#!/bin/bash

ORCHNAME="orch"

REPODIR=/local/repository
SHOUTSRC=/local/repository/shout
CLILOG=/var/tmp/controller.log

sudo ntpdate -u ops.emulab.net && \
    sudo ntpdate -u ops.emulab.net || \
	echo "Failed to update clock via NTP!"

sudo rm $CLILOG

cd $REPODIR

ORCHDOM=`$REPODIR/bin/getexpdom.py`
ORCHHOST="$ORCHNAME.$ORCHDOM"
echo "Using Shout orchestrator host: $ORCHHOST"
$SHOUTSRC/meascli.py -t -x -s $ORCHHOST

exit 0
