#!/bin/bash

ip="155.98.37.212"
#cmd="cbrs_tx_sine"
#cmd="cbrs_tx_sine_rx"
#cmd="cbrs_tx_sine_rx_rev"
#cmd="cbrs_meas"
#cmd="cell_rx_recv"
cmd="cell_power_var_meas"
#cmd="cell_power_var_meas_test"
#cmd="cell_power_var_meas_sine"


now=$(date +"%m_%d_%Y_%I_%M_%S")
out="/var/emulab/save/run_$now"
mkdir "$out"
mkdir "$out/data"
cd shout/
#cd /local/repository/shout
cp "/local/$cmd.json" "$out/data/$cmd.json"
python3 measiface.py -p 2000 -l "$out/log" -s $ip -o "$out/data" -c "/local/$cmd.json"