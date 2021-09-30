from django.urls import path
from getotp.views import (
    signup_callback,
    login_callback,
    signup_success,
    login_success,
)

urlpatterns = [
    path('signup_callback/', signup_callback, name="signup-callback"),
    path('login_callback/', login_callback, name="login_callback"),
    path("signup_success/", signup_success, name="signup-success"),
    path("login_success/", login_success, name="login-success"),
]
