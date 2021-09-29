#!/usr/bin/env python
# $Id$
#
# Copyright (c) 2021 Lalokalabs Inc

__author__ = "Surya Banerjee <surya@xoxzo.com>"

from getotp.client import GetOTPClient

from django.conf import settings

def user_verification(user, user_detail=None):
    try:
        key = settings.GETOTP_API_KEY,
        token = settings.GETOTP_AUTH_TOKEN,
        success_link = settings.GETOTP_SUCCESS_REDIRECT,
        fail_link = settings.GETOTP_FAIL_REDIRECT,
        channels = settings.GETOTP_CHANNELS
    except AttributeError:
        raise ValueError("Required variables missing from settings.py")

    client = GetOTPClient(
        key, token, success_link, fail_link,
    )

    resp = client.send_otp(channels)

    if resp.errors is not None:

    else:
        raise ConnectionError(f"API returned these errors - {resp.errors}")
