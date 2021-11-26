from django.urls import path
from getotp.views import (
    login_start,
    login_callback,
    login_complete,
)

urlpatterns = [
    path("login/start/", login_start, name="login-start"),
    path('login/callback/', login_callback, name="login-callback"),
    path("login/complete/", login_complete, name="login-complete"),
]
