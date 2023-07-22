from django.conf import settings
from django.contrib import admin

from lab.forms import LabForm
from lab.models import Lab, Data
import subprocess
from django.utils.safestring import mark_safe

from utils.data_generator import fix_size


class LabAdmin(admin.ModelAdmin):
    form = LabForm
    list_display = [f.name for f in Lab._meta.fields]
    actions = ['activate']
    search_fields = ['name']

    @admin.action(description='Activate lab')
    def activate(self, request, queryset):
        try:
            if len(queryset) != 1:
                self.message_user(request, "please select a lab")
                return
            lab: Lab = queryset.first()
            subprocess.Popen(
                [
                    "./lab/workload.sh",
                    lab.work_load_users_count,
                    lab.app_spark_workers_count,
                    lab.work_load_data_sizes,
                    lab.work_load_user_duration,
                    str(lab.server_count),
                    lab.app.application.name.replace("apps/", ""),
                    lab.work_load_user_think_time,
                    str(lab.total_time_of_experiment)
                ], stdin=subprocess.PIPE
            )
            subprocess.Popen(
                [
                    "./lab/server.sh",
                    str(lab.worker_cpu_counts),
                    lab.worker_memory_amount,
                    settings.SPARK_ROOT,
                    settings.MEDIA_ROOT,
                    settings.MODE
                ], stdin=subprocess.PIPE
            )
            lab.is_active = True
            lab.save(update_fields=['is_active'])
            spark_link = "http://206.12.91.107:3000/dashboards"
            self.message_user(
                request,
                mark_safe(
                    f'To see results of experiment see <a href="{spark_link}">dashboard spark and containers</a>'
                )
            )
        except Exception as e:
            self.message_user(request, f"An error occur: {e}")


class DataAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Data._meta.fields]
    actions = ['convert']
    search_fields = ['name']

    @admin.action(description='Convert data')
    def convert(self, request, queryset):
        try:
            for item in queryset:
                # data_generator.delay(file=item.sample_data.path, desired_size=item.desired_size)
                fix_size(item.sample_data.path, item.sample_data.path, item.desired_size)
        except Exception as e:
            self.message_user(request, f"An error occur: {e}")


admin.site.register(Lab, LabAdmin)
admin.site.register(Data, DataAdmin)
