from django.urls import path
from getotp.views import (
    signup_callback,
    login_callback,
    verification_success,
)

urlpatterns = [
    path('signup_callback/', signup_callback, name="signup-callback"),
    path('login_callback/', login_callback, name="login-callback"),
    path("verification_success/", verification_success, name="verification-success"),
]
