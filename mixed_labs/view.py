import json

from rest_framework.views import APIView
from rest_framework.response import Response

from app.models import Application
from lab.models import Data
from .models import ServerConfig, WorkloadConfig, AppConfig, MixedLab
from .serializers import ConfigurationSerializer
from django.db import transaction


class MixedLabCreateAPIView(APIView):

    @transaction.atomic
    def post(self, request):
        with transaction.atomic():
            data = request.data
            config = json.dumps(request.data)
            modified_data = dict(data)
            workload_config = modified_data.get("workload_config", None)
            if workload_config is None or not isinstance(workload_config, dict):
                return Response({"error": "input must have workload_config"}, status=400)
            apps = workload_config.get("apps", [])

            if not isinstance(apps, list) or len(apps) == 0:
                return Response({"error": "workload_config has not any target app"}, status=400)
            total_percentage = 0
            for app in apps:
                if not isinstance(app, dict):
                    return Response({"error": "each workload app must be a json object that has app_name"}, status=400)
                app_name = app.get("app_name", "")
                try:
                    application = Application.objects.get(application__exact=f"apps/{app_name}")
                    app.pop("app_name")
                    app["app"] = application.id
                except Exception:
                    return Response({"error": f"app_name {app_name} does not exists"}, status=400)
                data_files = app.get("data_files", [])
                if not isinstance(data_files, list) or len(data_files) == 0:
                    return Response({"error": "data files must be a list of data file name."}, status=400)
                tmp_data_files = []
                for data_file in data_files:
                    try:
                        d = Data.objects.get(sample_data__exact=data_file)
                        tmp_data_files.append({"sample_data": d.id})
                    except Exception:
                        return Response({"error": f"data file {data_file} does not exists"}, status=400)
                app["data_files"] = tmp_data_files
                if len(app["data_files"]) != len(app.get("data_file_percentage", [])):
                    return Response({"error": "data files and percent of each data file must be sets."}, status=400)
                user_percent_of_app = app.get("user_percentage", None)
                if user_percent_of_app is None or not str(user_percent_of_app).isnumeric():
                    return Response({"error": "user_percentage is required and must be an integer."}, status=400)
                total_percentage += int(user_percent_of_app)
            if total_percentage != 100:
                return Response(
                    {"error": "summation of user_percentage must be 100. Note: all user_percentage must be integer"},
                    status=400
                )
            serializer = ConfigurationSerializer(data=modified_data)
            if serializer.is_valid():
                lab = self.save_configuration(modified_data)
                lab.config = config
                lab.save()
                return Response(data=request.data, status=200)
            else:
                return Response(serializer.errors, status=400)

    def save_configuration(self, validated_data):
        server_config_data = validated_data.pop('server_config')
        workload_config_data = validated_data.pop('workload_config')

        server_config = ServerConfig.objects.create(**server_config_data)
        workload_config = WorkloadConfig.objects.create(
            users_count=workload_config_data.get("users_count"),
            time_in_second=workload_config_data.get("time_in_second"),
        )

        apps_data = workload_config_data.pop('apps')
        for app_data in apps_data:
            data_files_data = app_data.pop('data_files')
            app = AppConfig.objects.create(
                app_id=app_data.get("app"),
                user_percentage=app_data.get("user_percentage"),
                think_time_in_second=app_data.get("think_time_in_second"),
            )
            for file_data in data_files_data:
                data_file = Data.objects.get(id=file_data.get("sample_data"))
                app.data_files.add(data_file)
            workload_config.apps.add(app)

        configuration = MixedLab.objects.create(
            server_config=server_config, workload_config=workload_config
        )
        return configuration
