#!/bin/bash

ip="155.98.37.215"
#cmd="cbrs_tx_sine"
#cmd="cbrs_tx_sine_rx"
#cmd="cbrs_tx_sine_rx_rev"
#cmd="cbrs_meas"
#cmd="cell_rx_recv"
#cmd="cell_power_var_meas"
#cmd="cell_power_var_meas_test"
#cmd="cell_power_var_meas_sine"
#cmd="find_lte"
cmd="band7_dl_nuc1_nuc2_test"



now=$(date +"%m_%d_%Y_%I_%M_%S")
out="/var/emulab/save/run_$now"
#out="/var/emulab/save/band7_dl_nuc1_test"

mkdir "$out"
mkdir "$out/data"

cmd_file="/local/repository/etc/cmd_files/$cmd.json"
cp  $cmd_file "$out/data/$cmd.json"

cd /local/repository/shout
python3 measiface.py -p 2000 -l "$out/log" -s $ip -o "$out/data" -c $cmd_file