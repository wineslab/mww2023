#!/bin/bash
ip="155.98.37.214"

today=$(date +"%m_%d_%Y)
now=$(date +"%T")

out="/var/emulab/save/$today"
out="/var/emulab/save/$today/$now"
mkdir "$out"

cd /local/repository/shout
python3 meascli.py -p 2000 -l "$out/log" -s $ip