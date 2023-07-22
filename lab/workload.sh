#!/bin/bash

BaseRoot="./workload_scripts"
echo "Running workload ... $1 - $2 - $3 - $4 - $5 - $6 - $7 - $8"
cd $BaseRoot && python3 -m venv venv && source venv/bin/activate
pip3 install -r requirements.txt
sleep "60"
python attack_script.py $1 $2 $3 $4 $5 $6 $7 $8
echo "Done Work load"
