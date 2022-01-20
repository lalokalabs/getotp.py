
import json

import requests

from django.test import Client
from django.urls import reverse
from httmock import urlmatch, HTTMock

from getotp.models import GetOTP

def test_login_ok(user, request_client, settings):
    url = reverse("test:login-start")
    print(url)
    client = request_client()

    otp_api_response = {
        "otp_id": "kpb9c0a357pdf4jaz05c",
        "link": "https://otp.dev/api/ui/verify/kpb9c0a357pdf4jaz05c/email/",
        "otp_secret": "dxn07vdzqy7wfblk89r9",
    }

    @urlmatch(netloc="otp.dev", path="/api/verify/")
    def mock_otp(url, request):
        return {
            "status_code": 201,
            "content": json.dumps(otp_api_response),
        }

    test_settings = {
        "GETOTP_LOGIN_FAIL_REDIRECT": "",
        "GETOTP_LOGIN_SUCCESS_REDIRECT": "/",
        "GETOTP_CALLBACK": "",
    }

    with HTTMock(mock_otp):
        with(settings(**test_settings)):
            resp = client.post(url)
            print(resp)
            assert resp.status_code == 302
            assert resp.url == otp_api_response["link"]

    otp_callback_payload = {
        "otp_id": otp_api_response["otp_id"],
        "auth_status": "verified",
        "channel": "email",
        "otp_secret": otp_api_response["otp_secret"],
        "email": "ali@getotp.test",
        "ip_address": "10.9.8.7",
        "metadata": "",
    }

    url = reverse("test:callback")
    resp = client.post(url, json.dumps(otp_callback_payload), content_type="application/json")
    assert resp.status_code == 200

    otp = GetOTP.objects.get(otp_id=otp_callback_payload["otp_id"])
    assert otp.status == "verified"
    assert otp.email == otp_callback_payload["email"]
    user.email = otp.email
    user.save()

    client = Client()
    url = reverse("test:login-complete")
    resp = client.get(url, {"otp_id": otp_callback_payload["otp_id"]}, follow=True)
    assert f"Logged in as {otp.email}" in resp.content.decode("utf8")
