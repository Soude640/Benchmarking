import re

from django import forms
from django.core.exceptions import ValidationError

from utils.base_errors import SPARK_WORKERS_COUNTS_FIELD, WORK_LOAD_USER_COUNTS_FIELD, WORK_LOAD_USER_DURATION, \
    WORK_LOAD_DATA_SIZES_FIELD, WORK_LOAD_USER_THINK_TIME, SAME_STEP_ERROR, TOTAL_TIME_OF_EXPERIMENT_FIELD, \
    WORKER_CPU_COUNTS, WORKER_MEMORY_AMOUNT, SERVER_COUNT_FIELD


class LabForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()

        server_count = cleaned_data.get('server_count', "")
        if server_count is None or server_count not in [1, 2]:
            raise ValidationError(SERVER_COUNT_FIELD)

        app_spark_workers_count = cleaned_data.get('app_spark_workers_count', "")
        if app_spark_workers_count is None or not re.match(r'^(\d+,)*\d+$', app_spark_workers_count):
            raise ValidationError(SPARK_WORKERS_COUNTS_FIELD)

        work_load_users_count = cleaned_data.get('work_load_users_count', "")
        if work_load_users_count is None or not re.match(r'^(\d+,)*\d+$', work_load_users_count):
            raise ValidationError(WORK_LOAD_USER_COUNTS_FIELD)

        work_load_user_duration = cleaned_data.get('work_load_user_duration', "")
        if work_load_user_duration is None or not re.match(r'^(\d+,)*\d+$', work_load_user_duration):
            raise ValidationError(WORK_LOAD_USER_DURATION)

        work_load_data_sizes = cleaned_data.get('work_load_data_sizes', "")
        if work_load_data_sizes is None:
            work_load_data_sizes = ""
            cleaned_data['work_load_data_sizes'] = work_load_data_sizes
        elif work_load_data_sizes is None or not re.match(r'^([\w\s]+\.csv,)*[\w\s]+\.csv$', work_load_data_sizes):
            raise ValidationError(WORK_LOAD_DATA_SIZES_FIELD)

        work_load_user_think_time = cleaned_data.get('work_load_user_think_time', "")
        if work_load_user_think_time is None or not re.match(r'^(\d+,)*\d+$', work_load_user_think_time):
            raise ValidationError(WORK_LOAD_USER_THINK_TIME)

        if len(work_load_users_count.split(",")) != len(work_load_user_duration.split(",")) or \
                len(app_spark_workers_count.split(",")) != len(work_load_users_count.split(",")) or \
                len(app_spark_workers_count.split(",")) != len(work_load_user_think_time.split(",")):
            raise ValidationError(SAME_STEP_ERROR)

        total_time_of_experiment = cleaned_data.get('total_time_of_experiment', "")
        if total_time_of_experiment is None or not re.match(r'^\d+$', str(total_time_of_experiment)):
            raise ValidationError(TOTAL_TIME_OF_EXPERIMENT_FIELD)

        worker_cpu_counts = cleaned_data.get('worker_cpu_counts', "")
        if worker_cpu_counts is None or not str(worker_cpu_counts).isnumeric():
            raise ValidationError(WORKER_CPU_COUNTS)

        worker_memory_amount = cleaned_data.get('worker_memory_amount', "")
        if worker_memory_amount is None or not re.match(r'^\d+g$', worker_memory_amount):
            raise ValidationError(WORKER_MEMORY_AMOUNT)

        return cleaned_data
