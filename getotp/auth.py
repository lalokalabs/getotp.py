#!/usr/bin/env python
# $Id$
#
# Copyright (c) 2021 Lalokalabs Inc

__author__ = "Surya Banerjee <surya@xoxzo.com>"

import logging
from urllib.parse import urlparse, urlunparse

from django.urls import reverse
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth import login

from getotp.client import GetOTPClient
from getotp.models import GetOTP

logger = logging.getLogger(__name__)


def user_verification(user, user_details=None):
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
    resp = client.send_otp(
        channels,
        callback_url=callback_link,
        phone_sms=user_details.phone_number,
        phone_voice=user_details.phone_number,
        email=user.email
    )

    # Set user inactive till they verify OTP
    user.is_active = False
    user.save()

    user_details.user = user
    user_details.otp_id = resp.otp_id
    user_details.save()

    if resp.errors is None:
        try:
            GetOTP.objects.create(
                otp_id=resp.otp_id, link=resp.link, otp_secret=resp.otp_secret,
            )
        except Exception as e:
            logger.error(f"Exception occurred creating GetOTP object - {e}")
            return HttpResponse(status=500)
        else:
            logger.info(f"Sign up initiated with otp_id: {resp.otp_id}")
            return redirect(resp.link)
    else:
        raise ConnectionError(f"API returned these errors - {resp.errors}")


def confirm_user_verification(otp_id):
    try:
        getotp = GetOTP.objects.get(otp_id=otp_id)
    except Exception as e:
        logger.error(f"Exception occured when trying to fetch otp_id: {otp_id} - {e}")
    else:
        if getotp.status == "verified":
            return getotp.user

    return False
