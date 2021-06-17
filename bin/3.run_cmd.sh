#!/bin/bash

CMDDIR="/local/repository/etc/cmdfiles"
CMD="save_iq"
OUT="/var/emulab/save"


cd /local/repository/
git submodule update --init --remote || { echo "Failed to update git submodules!" && exit 1; }

today=$(date +"%m-%d-%Y")
now=$(date +"%H-%M-%S")
out="$OUT"/Shout_meas_"$today"_"$now"
mkdir "$out"

cmd_file="$CMDDIR/$CMD.json"
cp  $cmd_file "$out/$CMD.json"

cd "$out"
wget https://gitlab.flux.utah.edu/powderrenewpublic/powder-deployment/-/blob/master/powder-deployment.csv
wget https://gitlab.flux.utah.edu/powderrenewpublic/powder-deployment/-/blob/master/configuration.csv

cd /local/repository/shout
python3 measiface.py -l "$out/log" -o "$out/" -c $cmd_file