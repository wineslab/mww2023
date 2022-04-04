#!/bin/bash

CMDDIR="/local/repository/etc/cmdfiles"
#CMD="save_iq"
OUT="/var/emulab/save/"
#OUT="/local/repository/"


cd /local/repository/
#git submodule update --init --remote || { echo "Failed to update git submodules!" && exit 1; }

#for CMD in  "save_iq_2490" "save_iq_2530" "save_iq_2560" "save_iq_2590" "save_iq_2630" "save_iq_2660" "save_iq_2690"
for CMD in "save_iq_2690" "save_iq_2660" "save_iq_2630" "save_iq_2590" "save_iq_2560" "save_iq_2530" "save_iq_2490" "save_iq_2460" "save_iq_2430"
do
	echo "$CMDDIR/$CMD.json"
	today=$(date +"%m-%d-%Y")
	now=$(date +"%H-%M-%S")
	out="$OUT"/Shout_meas_"$today"_"$now"
	mkdir "$out"

	cmd_file="$CMDDIR/$CMD.json"
	cp  $cmd_file "$out/$CMD.json"

	#cd "$out"
	#wget https://gitlab.flux.utah.edu/powderrenewpublic/powder-deployment/-/blob/master/powder-deployment.csv
	#wget https://gitlab.flux.utah.edu/powderrenewpublic/powder-deployment/-/blob/master/configuration.csv

	cd /local/repository/shout
	python3 measiface.py -l "$out/log" -o "$out/" -c $cmd_file
done