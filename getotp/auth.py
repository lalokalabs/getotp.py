#!/usr/bin/env python
# $Id$
#
# Copyright (c) 2021 Lalokalabs Inc

__author__ = "Surya Banerjee <surya@xoxzo.com>"

import logging
from urllib. parse import urlparse, urlunparse

from django.urls import reverse
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect

from getotp.client import GetOTPClient
from getotp.models import SignUp

logger = logging.getLogger(__name__)


def user_verification(user, user_detail=None):
    try:
        key = settings.GETOTP_API_KEY
        token = settings.GETOTP_AUTH_TOKEN
        end_success_redirect = settings.GETOTP_SUCCESS_REDIRECT
        fail_redirect = settings.GETOTP_FAIL_REDIRECT
        channels = settings.GETOTP_CHANNELS
    except AttributeError:
        raise ValueError("Required variables missing from settings.py")

    parsed_success = urlparse(end_success_redirect)
    parsed_success = parsed_success._replace(path=reverse("signup-success"))
    success_link = urlunparse(parsed_success)
    parsed_callback = parsed_success._replace(path=reverse("signup-callback"))
    callback_link = urlunparse(parsed_callback)

    client = GetOTPClient(key, token, success_link, fail_redirect)
    resp = client.send_otp(channels, callback_url=callback_link)

    import pdb; pdb.set_trace()

    if resp.errors is None:
        try:
            SignUp.objects.create(
                otp_id=resp.otp_id, link=resp.link, otp_secret=resp.otp_secret,
            )
        except Exception as e:
            logger.error(f"Exception occurred creating signup object - {e}")
            return HttpResponse(status=500)
        else:
            logger.info(f"SignUp initiated with otp_id: {resp.otp_id}")
            return redirect(resp.link)
    else:
        raise ConnectionError(f"API returned these errors - {resp.errors}")

def confirm_verification(otp_id):
    import pdb; pdb.set_trace()