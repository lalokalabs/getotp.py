from django.urls import path
from getotp.views import (
    login_start,
    login_complete,
    otp_callback,
    index,
)

app_name = "getotp"
urlpatterns = [
    path("", index, name="index"),
    path("login/start/", login_start, name="login-start"),
    path("login/complete/", login_complete, name="login-complete"),
    path('callback/', otp_callback, name="callback"),
]
