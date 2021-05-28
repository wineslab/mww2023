#!/bin/bash

cmd="rx"


today=$(date +"%m_%d_%Y")
now=$(date +"%T")
folder="/var/emulab/save/"
mkdir "$out"
out="$folder/$today/$now"
mkdir "$out"

cmd_file="/local/repository/etc/cmd_files/$cmd.json"
cp  $cmd_file "$out/$cmd.json"

cd /local/repository/shout
python3 measiface.py -l "$out/log" -o "$out/" -c $cmd_file




#ip="155.98.37.211"

#cmd="cell_power_var_meas"
#cmd="rx"


#folder="/local/"
#out="$folder/$today"
#mkdir "$out"
#out="$folder/$today/$now"
#mkdir "$out"

#cmd_file="/local/repository/etc/cmd_files/$cmd.json"
#cp  $cmd_file "$out/$cmd.json"

#cd /local/repository/shout
#python3 measiface.py -p 2000 -l "$out/log" -s $ip -o "$out/" -c $cmd_file