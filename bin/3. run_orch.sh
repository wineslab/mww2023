#!/bin/bash

ip="155.98.37.214"

cmd="bus_tx_rx"

today=$(date +"%m_%d_%Y)
now=$(date +"%T")
out="/var/emulab/save/$today"
out="/var/emulab/save/$today/$now"
mkdir "$out"

cmd_file="/local/repository/etc/cmd_files/$cmd.json"
cp  $cmd_file "$out/$cmd.json"

cd /local/repository/shout
python3 measiface.py -p 2000 -l "$out/" -s $ip -o "$out/" -c $cmd_file