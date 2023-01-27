#!/bin/bash

ORCHNODE=$1
RUNSCRIPT="/local/repository/bin/3.run_cmd.sh"

ed $RUNSCRIPT << SNIP
/^ORCHNODE/c
ORCHNODE=$ORCHNODE
.
w
SNIP

# Install/update some packages
sudo apt-get -q update
sudo apt-get -q -y install python3-pandas
sudo pip3 -q install --upgrade scipy
