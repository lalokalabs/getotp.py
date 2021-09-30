#!/usr/bin/env python
# $Id$
#
# Copyright (c) 2021 XoxzoEU Inc

__author__ = "Surya Banerjee <surya@xoxzo.com>"

import json
import logging

from django.conf import settings
from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login

from getotp.auth import confirm_user_verification
from getotp.models import GetOTP, UserDetails

logger = logging.getLogger(__name__)


def signup_success(request):
    otp_id = request.GET.get("otp_id", False)
    if otp_id:
        user = confirm_user_verification(otp_id)
        if user:
            login(request, user)
            return redirect(settings.GETOTP_SUCCESS_REDIRECT)

    return HttpResponse(status=404)


def login_success(request):
    pass


@csrf_exempt
def signup_callback(request):
    payload = json.loads(request.body)
    otp_id = payload["otp_id"]

    try:
        getotp = GetOTP.objects.get(otp_id=otp_id)
    except Exception as e:
        logger.error(f"Exception occured when trying to fetch otp_id: {otp_id} - {e}")

    if payload["otp_secret"] == getotp.otp_secret:
        if payload["auth_status"] == "verified":
            if not getattr(settings, "GETOTP_CUSTOM_USER", False):
                try:
                    user_details = UserDetails.objects.get(otp_id=otp_id)
                except Exception as e:
                    logger.error(
                        f"Exception occured when trying to fetch otp_id: {otp_id} - {e}"
                    )
                else:
                    if user_details.phone_number == payload["phone_number"]:
                        save_getotp(getotp, user_details)
            else:
                save_getotp(getotp, user_details)

        getotp.callback_time = timezone.now()
        getotp.save()

    return HttpResponse(status=200)


def save_getotp(getotp, user_details):
    user = user_details.user
    getotp.user = user
    getotp.status = "verified"
    getotp.save()
    user.is_active = True
    user.save()


def login_callback(request):
    pass
