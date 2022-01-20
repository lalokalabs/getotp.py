
from pytest_djangoapp import configure_djangoapp_plugin

pytest_plugins = configure_djangoapp_plugin({
        "ROOT_URLCONF": "getotp.tests.urls_tests",
        "GETOTP_API_KEY": "",
        "GETOTP_AUTH_TOKEN": "",
    },
    extend_AUTHENTICATION_BACKENDS = [
        "getotp.auth.OTPBackend",
    ],
    extend_INSTALLED_APPS=[
        'django.contrib.sessions',
    ],
    extend_MIDDLEWARE=[
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
    ],
)
