from django.urls import path
from mixed_lab.views import MixedLabCreateAPIView

app_name = "mixed_lab"
urlpatterns = [
    path('create/', MixedLabCreateAPIView.as_view()),
]
