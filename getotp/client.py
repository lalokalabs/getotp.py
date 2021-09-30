#!/usr/bin/env python
# $Id$
#
# Copyright (c) 2021 Lalokalabs Inc

__author__ = "Surya Banerjee <surya@xoxzo.com>"

import requests

VERIFY_API_URL = "http://localhost:9000/api/verify/"
VERIFY_API_PARAMS = [
    "success_redirect_url",
    "fail_redirect_url",
    "channel",
    "callback_url",
    "phone_sms",
    "phone_voice",
    "email",
    "hide",
    "metadata",
]
VERIFY_API_RESP = ["otp_id", "link", "otp_secret"]
VERIFY_API_DETAIL = ["otp_id", "status", "channels", "creation_time"]


class GetOTPClient:
    def __init__(
        self, sid, token, success_redirect_url=None, fail_redirect_url=None, **kwargs
    ):
        self.verify_api_url = VERIFY_API_URL
        self.success_redirect_url = success_redirect_url
        self.fail_redirect_url = (
            fail_redirect_url if fail_redirect_url is not None else success_redirect_url
        )
        self.sid = sid
        self.token = token

    def send_otp(self, channel, **kwargs):
        _available_params = [
            value
            for value in VERIFY_API_PARAMS
            if value not in ["success_redirect_url", "fail_redirect_url", "channel"]
        ]

        if kwargs.get("success_redirect_url") is not None:
            success_redirect_url = kwargs.get("success_redirect_url")
        elif self.success_redirect_url is not None:
            success_redirect_url = self.success_redirect_url

        if kwargs.get("fail_redirect_url") is not None:
            fail_redirect_url = kwargs.get("fail_redirect_url")
        elif self.fail_redirect_url is not None:
            fail_redirect_url = self.success_redirect_url

        if success_redirect_url is None:
            raise ValueError("Should atleast have the success_redirect_url")
        else:
            data = {
                "channel": channel,
                "success_redirect_url": success_redirect_url,
                "fail_redirect_url": fail_redirect_url,
            }

        for key, value in kwargs.items():
            if key in _available_params:
                data.update({key: value})
            else:
                raise ValueError(f"Invalid parameter - {key}")

        try:
            resp = requests.post(
                self.verify_api_url, data=data, auth=(self.sid, self.token)
            )
        except requests.exceptions.RequestException as e:
            raise e
        else:
            if resp.status_code == 201:
                return GetOTPResponse(**resp.json())
            else:
                return GetOTPResponse(errors=resp.json())

    def getotp_status(self, otp_id):
        try:
            resp = requests.get(
                f"{self.verify_api_url}{otp_id}/", auth=(self.sid, self.token)
            )
        except requests.exceptions.RequestException as e:
            raise e

        if resp.status_code == 200:
            return GetOTPResponse(**resp.json())
        elif resp.status_code == 404:
            return GetOTPResponse(errors={"otp_id": "Not found"})
        else:
            return GetOTPResponse(errors=resp.json())


class GetOTPResponse:
    def __init__(self, errors=None, **kwargs):
        self.errors = errors
        self.__dict__.update(
            {
                k: v
                for (k, v) in kwargs.items()
                if k in VERIFY_API_PARAMS + VERIFY_API_RESP + VERIFY_API_DETAIL
            }
        )

    def __str__(self):
        if self.errors:
            return "Invalid parameters. Check errors."
        else:
            return self.otp_id
