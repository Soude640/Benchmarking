import math
import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.core.validators import FileExtensionValidator
from django.db import models
from app.models import Application

from utils.base_errors import SPARK_WORKERS_COUNTS_FIELD, WORK_LOAD_USER_COUNTS_FIELD, WORK_LOAD_USER_DURATION, \
    WORK_LOAD_DATA_SIZES_FIELD, WORK_LOAD_USER_THINK_TIME, TOTAL_TIME_OF_EXPERIMENT_FIELD, \
    WORKER_CPU_COUNTS, WORKER_MEMORY_AMOUNT, SERVER_COUNT_FIELD

convert_map = {
    "b": 1,
    "kb": 1024,
    "mb": 1024 * 1024,
    "gi": 1024 * 1024 * 1024,
}


def convert_size_to_bytes(desired_size: str) -> float:
    split = re.split("(kb|Kb|KB|mb|Mb|MB|gi|Gi|GI|b|B)", desired_size)
    number, unit = float(split[0]), str(split[1]).lower()

    if unit not in convert_map:
        raise Exception(f"bad format desired size. {unit} not known")

    return number * convert_map[unit]


def convert_bytes_to_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("b", "kb", "mb", "gi")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


private_storage = FileSystemStorage(location=settings.DATA_STORAGE_ROOT)


def get_data_file_path(instance, filename):
    return filename


class Lab(models.Model):
    name = models.CharField(
        max_length=1024
    )

    is_active = models.BooleanField(
        default=False
    )
    server_count = models.IntegerField(
        verbose_name="Servers count",
        help_text=f"<h4>{SERVER_COUNT_FIELD}</h4>",
        choices=((1, 1), (2, 2))
    )
    app_spark_workers_count = models.CharField(
        verbose_name="Application spark workers count",
        max_length=1024,
        help_text=f"<h4>{SPARK_WORKERS_COUNTS_FIELD}</h4>",
    )
    work_load_users_count = models.CharField(
        verbose_name="Work load users count",
        max_length=1024,
        help_text=f"<h4>{WORK_LOAD_USER_COUNTS_FIELD}</h4>"
    )
    work_load_data_sizes = models.CharField(
        verbose_name="Work load data sizes",
        max_length=1024,
        help_text=f"<h4>{WORK_LOAD_DATA_SIZES_FIELD}</h4>",
        blank=True,
        null=True
    )
    work_load_user_duration = models.CharField(
        verbose_name="Work load users duration",
        max_length=1024,
        help_text=f"<h4>{WORK_LOAD_USER_DURATION}</h4>",
    )
    work_load_user_think_time = models.CharField(
        verbose_name="Work load users think time",
        max_length=1024,
        help_text=f"<h4>{WORK_LOAD_USER_THINK_TIME}</h4>",
    )
    total_time_of_experiment = models.IntegerField(
        verbose_name="Total time of experiment",
        help_text=f"<h4>{TOTAL_TIME_OF_EXPERIMENT_FIELD}</h4>",
    )
    worker_cpu_counts = models.IntegerField(
        verbose_name="Worker cpu counts",
        help_text=f"<h4>{WORKER_CPU_COUNTS}</h4>",
    )
    worker_memory_amount = models.CharField(
        verbose_name="Worker memory amount",
        help_text=f"<h4>{WORKER_MEMORY_AMOUNT}</h4>",
        max_length=10
    )
    app = models.ForeignKey(
        to=Application,
        verbose_name="Application",
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


def validate_data_size(value):
    values = value.split(" ")
    if len(values) != 2 and not str(values[0]).isnumeric() and not values[1] in ["kb", "mb", "gi"]:
        raise ValidationError(
            "%(value) is not in this format: <number> <symbol> like 100 mb or 1 gi or 50 mb",
            params={"value": value},
        )


class Data(models.Model):
    RAW = "Raw"
    GENERATED = "Generated"
    PENDING = "Pending"

    STATUS_CHOICES = (
        (RAW, RAW),
        (GENERATED, GENERATED),
        (PENDING, PENDING),
    )
    sample_data = models.FileField(
        verbose_name="Sample data file",
        help_text="Your sample data must be a csv file",
        upload_to=get_data_file_path,
        validators=[FileExtensionValidator(['csv'])],
        storage=private_storage
    )
    desired_size = models.CharField(
        verbose_name="Desired Size",
        help_text="Your desired size with postfix: [kb, mb, gi] for example `100 mb`",
        max_length=7,
        validators=[validate_data_size]
    )
    current_size = models.CharField(
        verbose_name="Current Size",
        max_length=7,
        blank=True
    )
    status = models.CharField(
        verbose_name="Status",
        choices=STATUS_CHOICES,
        max_length=20,
        default=RAW
    )

    def __str__(self):
        return self.sample_data.name

    def save(self, *args, **kwargs):
        self.current_size = convert_bytes_to_size(self.sample_data.size)
        super(Data, self).save(*args, **kwargs)
