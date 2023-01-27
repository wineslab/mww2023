#!/bin/bash

EMUBOOT=/var/emulab/boot
REPODIR=/local/repository
SHOUTSRC=/local/repository/shout

# Install gpsd-clients
REQUIRED_PKG="gpsd-clients"
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG|grep "install ok installed")
echo "Checking for $REQUIRED_PKG: $PKG_OK"
if [ "" = "$PKG_OK" ]; then
  echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG."
  sudo apt-get -qq update
  sudo apt-get -q -y install $REQUIRED_PKG
fi

cd $REPODIR

# Static return route to ME/FE aggregates.
sudo ip route add 155.98.46.0/23 via 155.98.36.204

$SHOUTSRC/orchestrator.py

exit 0
