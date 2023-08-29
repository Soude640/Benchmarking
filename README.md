##local development

First, you need to pull these images:

docker pull bde2020/spark-master:3.3.0-hadoop3.3   
docker pull Soude640/spark-worker:v3.3.0
docker pull Soude640/backend:v5
docker pull prom/prometheus:v2.17.1
docker pull prom/node-exporter:v0.18.1
docker pull gcr.io/google-containers/cadvisor:v0.34.0
docker pull grafana/grafana:6.7.2
docker pull prom/pushgateway:v1.2.0
docker pull jupyter/pyspark-notebook:notebook-6.5.4


To run this project on your local machine, you only have to do the three steps below.

1 - Clone the project with the below command

git clone https://github.com/Soude640/benchmarking.git

2 - After cloning this repo you need to change the environment variable based on your system

SPARK_ROOT : is your spark project directory like (/home/ubuntu/projects/spark)

3 - Run the project with the below command

chmod +x setup.sh && ./setup.sh
