

from django.urls import path, include, re_path

urlpatterns = [
    path("", include("getotp.urls", namespace="test")),
]
