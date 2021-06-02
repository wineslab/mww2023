#!/bin/bash

cmd="rx_iq_w_tx_file"

folder="/local/" #"/var/emulab/save/"

cd /local/repository/
git submodule update --init --remote || { echo "Failed to update git submodules!" && exit 1; }

today=$(date +"%m_%d_%Y")
now=$(date +"%T")
out="$folder/$today"
mkdir "$out"
out="$folder/$today/$now"
mkdir "$out"

cmd_file="/local/repository/shout/cmdfiles/$cmd.json"
cp  $cmd_file "$out/$cmd.json"

cd "$out"
wget https://gitlab.flux.utah.edu/powderrenewpublic/powder-deployment/-/blob/master/powder-deployment.csv
wget https://gitlab.flux.utah.edu/powderrenewpublic/powder-deployment/-/blob/master/configuration.csv

cd /local/repository/shout
python3 measiface.py -l "$out/log" -o "$out/" -c $cmd_file