GetOTP Python Library

## Quickstart

Add `getotp` to `INSTALLED_APPS` settings:-

```
NSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "getotp",
    ...
```

Add to `AUTHENTICATION_BACKENDS`:

```
AUTHENTICATION_BACKENDS = [
  "django.contrib.auth.backends.ModelBackend",
  "some.other.auth.OtherBackend",
  ...,
  "getotp.auth.GETOTPBackend",
]
```

Add to `urls.py`:-

```
urlpatterns = [
    path("", views.index),
    path("accounts/", include(("django.contrib.auth.urls", "auth"), namespace="auth")),
    ...
    path("getotp/", include("getotp.urls")),
    ...
]
```

Run `migrate`.

The login button should be available under https://yoursite.com/getotp/login/start/.

Design Document:
https://docs.google.com/document/d/1hjvc07wU_8oo5Y6_G0in-txrvQ__SobwMuyFjHAVxiI/edit#
