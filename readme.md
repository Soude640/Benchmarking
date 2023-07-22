
## Local development

docker pull bde2020/spark-master:3.3.0-hadoop3.3   
docker pull mortezarastegarrad/spark-worker:v3.3.0
docker pull mortezarastegarrad/backend:v5
docker pull prom/prometheus:v2.17.1
docker pull prom/node-exporter:v0.18.1
docker pull gcr.io/google-containers/cadvisor:v0.34.0
docker pull grafana/grafana:6.7.2
docker pull prom/pushgateway:v1.2.0
docker pull jupyter/pyspark-notebook:notebook-6.5.4

export WORKER_CPU_COUNTS=4
export WORKER_MEMORY_AMOUNTS=7g
export MEDIA_ROOT=<your-data-file-path-that-you-want-volumes-to-docker>


docker stack deploy --compose-file docker-compose-dev.yml test 
