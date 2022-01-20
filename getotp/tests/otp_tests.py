import json

from httmock import urlmatch, HTTMock
from getotp.client import send_otp

def test_send_multi_channels():
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
        resp = send_otp("email, sms",
                        success_redirect_url="https://localhost/success/",
                        fail_redirect_url="https://localhost/fail/")
        assert resp.ok is True
        assert resp.otp.otp_id == otp_api_response["otp_id"]
