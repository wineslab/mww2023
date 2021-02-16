#!/bin/bash
ip="155.98.37.210"
txrx=false

now=$(date +"%m_%d_%Y_%I_%M_%S")
out="/var/emulab/save/run_$now"
#out="/var/emulab/save/band7_dl_nuc1_test"
mkdir "$out"
cd /local/repository/shout


if [ "$txrx" != true ] ; then 
	echo "Not tx/rx"
	python3 meascli.py -p 2000 -l "$out/log" -s $ip
else
	python3 meascli.py -t -p 2000 -l "$out/log" -s $ip
fi