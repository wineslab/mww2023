#!/bin/bash
ip="155.98.37.212"
txrx=true

now=$(date +"%m_%d_%Y_%I_%M_%S")
out="/var/emulab/save/run_$now"
mkdir "$out"
cd shout/
#cd /local/repository/shout


if [ "$txrx" != true ] ; then 
	python3 meascli.py -p 2000 -l "$out/log" -s $ip
fi

if [ "$txrx" == true ] ; then 
	python3 meascli.py -t -p 2000 -l "$out/log" -s $ip
fi
