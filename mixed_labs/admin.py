from django.contrib import admin

from mixed_lab.models import MixedLab, AppConfig, ServerConfig, WorkloadConfig

import subprocess
from django.utils.safestring import mark_safe


class MixedLabAdmin(admin.ModelAdmin):
    list_display = [f.name for f in MixedLab._meta.fields]
    actions = ['activate']

    @admin.action(description='Activate lab')
    def activate(self, request, queryset):
        try:
            if len(queryset) != 1:
                self.message_user(request, "please select a lab")
                return
            lab: MixedLab = queryset.first()
            subprocess.Popen(
                [
                    "./mixed_lab/workload.sh",
                    lab.config
                ], stdin=subprocess.PIPE
            )
            subprocess.Popen(
                [
                    "./mixed_lab/server.sh",
                    str(lab.server_config.cpu_of_every_worker),  # cpu
                    str(lab.server_config.memory_of_every_worker)+"g"  # memory
                ], stdin=subprocess.PIPE
            )
            spark_link = "http://206.12.91.107:3000/dashboards"
            self.message_user(
                request,
                mark_safe(
                    f'To see results of experiment see <a href="{spark_link}">dashboard spark and containers</a>'
                )
            )
        except Exception as e:
            self.message_user(request, f"An error occur: {e}")


admin.site.register(MixedLab, MixedLabAdmin)


class AppConfigAdmin(admin.ModelAdmin):
    list_display = [f.name for f in AppConfig._meta.fields]


admin.site.register(AppConfig, AppConfigAdmin)


class ServerConfigAdmin(admin.ModelAdmin):
    list_display = [f.name for f in ServerConfig._meta.fields]


admin.site.register(ServerConfig, ServerConfigAdmin)


class WorkloadConfigAdmin(admin.ModelAdmin):
    list_display = [f.name for f in WorkloadConfig._meta.fields]


admin.site.register(WorkloadConfig, WorkloadConfigAdmin)
