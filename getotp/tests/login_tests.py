
import json

from django.urls import reverse
from httmock import urlmatch, HTTMock

def test_login_ok(request_client, settings):
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
        "GETOTP_LOGIN_SUCCESS_REDIRECT": "",
        "GETOTP_CALLBACK": "",
    }

    with HTTMock(mock_otp):
        with(settings(**test_settings)):
            resp = client.post(url)
            print(resp)
            assert resp.status_code == 302
            assert resp.url == otp_api_response["link"]
