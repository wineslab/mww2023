#!/bin/bash
ip="155.98.37.201"

#today=$(date +"%m_%d_%Y")
#now=$(date +"%T")

#out="/var/emulab/save/$today"
#mkdir "$out"
#out="/var/emulab/save/$today/$now"
#mkdir "$out"

cd /local/repository/shout
#python3 meascli.py -p 2000 -s $ip -l "$out/log" 
python3 meascli.py -p 2000 -s $ip 