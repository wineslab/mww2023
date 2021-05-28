#!/bin/bash

ORCHNAME="orch"

EMUBOOT=/var/emulab/boot
REPODIR=/local/repository
SHOUTSRC=/local/repository/shout
CLILOG=/var/tmp/ccontroller.log

# Install GRC
sudo apt-get update
sudo apt -y install python3-gi gobject-introspection gir1.2-gtk-3.0

cd $REPODIR
git submodule update --init --remote || \
    { echo "Failed to update git submodules!" && exit 1; }

sudo ntpdate -u ops.emulab.net && \
    sudo ntpdate -u ops.emulab.net || \
	echo "Failed to update clock via NTP!"

sudo rm $CLILOG

ORCHDOM=`$REPODIR/bin/getexpdom.py`
ORCHHOST="$ORCHNAME.$ORCHDOM"

$SHOUTSRC/meascli.py -s $ORCHHOST

exit 0
