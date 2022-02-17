#!/bin/bash

CMDDIR="/local/repository/etc/cmdfiles"
#OUT="/var/emulab/save/"
OUT="/SpectSet/"


cd /local/repository/
#git submodule update --init --remote || { echo "Failed to update git submodules!" && exit 1; }

for i in 1 2 3 4 5 6 7 8 9 10
do
	#for CMD in "save_iq_w_simult_tx_1" "save_iq_w_simult_tx_2" "save_iq_w_simult_tx_3"
	for CMD in "save_iq_w_simult_tx_2" "save_iq_w_simult_tx_3"
	do
	
		today=$(date +"%m-%d-%Y")
		now=$(date +"%H-%M-%S")
		out="$OUT"/Shout_meas_"$today"_"$now"
		mkdir "$out"

		cmd_file="$CMDDIR/$CMD.json"
		cp  $cmd_file "$out/$CMD.json"

		cd /local/repository/shout
		python3 measiface.py -l "$out/log" -o "$out/" -c $cmd_file

	done

done