from django.db import models
from lab.models import Data
from app.models import Application


class AppConfig(models.Model):
    app = models.ForeignKey(Application, on_delete=models.CASCADE)
    data_files = models.ManyToManyField(Data)
    user_percentage = models.FloatField()
    think_time_in_second = models.IntegerField()

    def __str__(self):
        data_files = ""
        for data_file in self.data_files.all():
            data_files += str(data_file) + "\n"
        return f"app: {str(self.app)}, data_files: {data_files}," \
               f" user_percentage: {str(self.user_percentage)}," \
               f"think_time_in_second: {str(self.think_time_in_second)}"


class ServerConfig(models.Model):
    server_counts = models.IntegerField()
    spark_worker_counts = models.IntegerField()
    cpu_of_every_worker = models.IntegerField()
    memory_of_every_worker = models.IntegerField()

    def __str__(self):
        return f"server_counts: {str(self.server_counts)}, spark_worker_counts: {str(self.spark_worker_counts)}, " \
               f"cpu_of_every_worker: {str(self.cpu_of_every_worker)}, memory_of_every_worker: {str(self.memory_of_every_worker)}"


class WorkloadConfig(models.Model):
    users_count = models.IntegerField()
    time_in_second = models.IntegerField()
    apps = models.ManyToManyField(AppConfig)

    def __str__(self):
        apps = ""
        for i in self.apps.all():
            apps += f"[{str(i)}]\t"
        return f"users_count: {str(self.users_count)}, apps: {apps}"


class MixedLab(models.Model):
    server_config = models.OneToOneField(ServerConfig, on_delete=models.CASCADE)
    workload_config = models.OneToOneField(WorkloadConfig, on_delete=models.CASCADE)
    config = models.TextField()

    def __str__(self):
        return f"server_config: {str(self.server_config)}, workload_config: {str(self.workload_config)}"
