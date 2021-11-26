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
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

from getotp.client import GetOTPClient
from getotp.models import GetOTP

User = get_user_model()

logger = logging.getLogger(__name__)

def send_otp(channels, success_redirect_url, fail_redirect_url,
             callback_url=None, email="", phone_sms="", phone_voice=""):
    key = settings.GETOTP_API_KEY
    token = settings.GETOTP_AUTH_TOKEN

    kwargs = {}
    client = GetOTPClient(
        key,
        token,
        success_redirect_url=success_redirect_url,
        fail_redirect_url=fail_redirect_url
    )

    resp = client.send_otp(
        channels,
        callback_url=callback_url,
        phone_sms=phone_sms,
        phone_voice=phone_voice,
        email=email,
    )

    if resp.errors is not None:
        return resp

    kwargs.update(
        {"otp_id": resp.otp_id, "link": resp.link, "otp_secret": resp.otp_secret,}
    )
    kwargs["email"] = email
    kwargs["phone_voice"] = phone_voice
    kwargs["phone_sms"] = phone_sms
    try:
        getotp = GetOTP.objects.create(**kwargs)
    except Exception as e:
        logger.error(f"Exception occurred creating GetOTP object - {e}")
        return HttpResponse(status=500)

    logger.info(f"Initiated OTP with otp_id: {resp.otp_id}")
    return resp

    raise ConnectionError(f"API returned these errors - {resp.errors}")

class GetOTPBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        otp_id = username
        try:
            getotp = GetOTP.objects.get(otp_id=otp_id)
        except Exception as e:
            logger.error(f"Exception occured when trying to fetch otp_id: {otp_id} - {e}")
            return None

        if getotp.status != "verified":
            logger.warning(f"Attempt to complete non-verified otp {getotp}")
            return None

        try:
            user = User.objects.get(email=getotp.email)
        except User.DoesNotExist:
            logger.error(f"Login attempt for non-existsing user {getotp.email}")
            return None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
