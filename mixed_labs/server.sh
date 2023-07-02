#!/bin/bash
appsRoot="/mnt/data/apps"
BaseRoot="/home/ubuntu/proj/spark"

docker stack rm test
sleep "30"

docker volume rm test_grafana_data
docker volume rm test_prometheus_data

echo "Copy apps files to $BaseRoot/src/apps"
cp -r $appsRoot "$BaseRoot/src/"
echo "Starting lab"
export WORKER_CPU_COUNTS=$1
export WORKER_MEMORY_AMOUNTS=$2
cd $BaseRoot && docker stack deploy --compose-file docker-compose.yml test
sleep "60"
echo "Sleep ended"
