from rest_framework import serializers
from .models import *


class DataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Data
        fields = ('id',)


class AppConfigSerializer(serializers.ModelSerializer):
    data_files = DataSerializer(many=True)

    class Meta:
        model = AppConfig
        fields = ('app', 'user_percentage', 'data_files', 'think_time_in_second')


class ServerConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServerConfig
        fields = ('server_counts', 'spark_worker_counts', 'cpu_of_every_worker', 'memory_of_every_worker')


class WorkloadConfigSerializer(serializers.ModelSerializer):
    apps = AppConfigSerializer(many=True)

    class Meta:
        model = WorkloadConfig
        fields = ('users_count', 'time_in_second', 'apps')


class ConfigurationSerializer(serializers.ModelSerializer):
    server_config = ServerConfigSerializer()
    workload_config = WorkloadConfigSerializer()

    class Meta:
        model = MixedLab
        fields = ('server_config', 'workload_config')se
