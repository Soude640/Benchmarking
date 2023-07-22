#!/bin/bash
mediaRoot=$4
SparkRoot=$3

echo "Running spark with Mode: $MODE"
docker stack rm test
sleep "30"

docker volume rm test_grafana_data
docker volume rm test_prometheus_data

echo "Remove apps from $SparkRoot/src/apps"
rm -rf "$SparkRoot/src/apps/*"
echo "Copy apps files to $SparkRoot/src/apps"
cp -r "$mediaRoot/apps" "$SparkRoot/src/"
echo "Starting lab with cpu $1, memory $2"
export WORKER_CPU_COUNTS=$1
export WORKER_MEMORY_AMOUNTS=$2
cd $mediaRoot && export export MEDIA_ROOT=$(pwd)
echo "mount directory is: $MEDIA_ROOT"
docker swarm init
if [ $MODE == "dev" ]; then
  cd $SparkRoot && docker stack deploy --compose-file docker-compose-dev.yml test
else
  cd $SparkRoot && docker stack deploy --compose-file docker-compose.yml test
fi
sleep "60"
echo "Sleep ended"
