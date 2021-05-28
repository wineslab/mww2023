#!/bin/bash


EMUBOOT=/var/emulab/boot
REPODIR=/local/repository
SHOUTSRC=/local/repository/shout

# Install gpsd-clients

#REQUIRED_PKG="gpsd-clients"
#PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG|grep "install ok installed")
#echo Checking for $REQUIRED_PKG: $PKG_OK
#if [ "" = "$PKG_OK" ]; then
#  echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG."
#  sudo apt-get update
#  sudo apt-get --yes install $REQUIRED_PKG 
#fi

sudo apt-get update
sudo apt -y install gpsd-clients

cd $REPODIR
git submodule update --init --remote || \
    { echo "Failed to update git submodules!" && exit 1; }

#sudo ip route add 155.98.47.0/24 via 155.98.36.204
sudo ip route add 155.98.46.0/23 via 155.98.36.204


$SHOUTSRC/orchestrator.py

exit 0

#ip -4 -brief address show
#cd /local/repository/shout
#python3 orchestrator.py -p 2000