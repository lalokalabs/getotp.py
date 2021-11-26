from django.urls import path
from getotp.views import (
    signup_callback,
    login_callback,
    verification_success,
    login_start,
    login_complete,
)

urlpatterns = [
    path("login/start/", login_start, name="login-start"),
    path("login/complete/", login_complete, name="login-complete"),
    path('signup_callback/', signup_callback, name="signup-callback"),
    path('login/callback/', login_callback, name="login-callback"),
    path("verification_success/", verification_success, name="verification-success"),
]
