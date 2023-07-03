#!/bin/bash

BaseRoot="./workload_scripts"
echo "Running workload ... $1"
ls "."
cd $BaseRoot && source venv/bin/activate && python attack_script_mixed_version.py "$1"
echo "Done Work load"
