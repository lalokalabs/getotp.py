#!/usr/bin/env python
# $Id$
#
# Copyright (c) 2021 XoxzoEU Inc

__author__ = "Surya Banerjee <surya@xoxzo.com>"

import json
import logging

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.http import HttpResponse
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt

from getotp.auth import confirm_user_verification
from getotp.models import GetOTP, UserDetails

logger = logging.getLogger(__name__)


def verification_success(request):
    otp_id = request.GET.get("otp_id", False)
    if otp_id:
        user = confirm_user_verification(otp_id)
        if user:
            login(request, user)
            return redirect(settings.GETOTP_SUCCESS_REDIRECT)

    return HttpResponse(status=404)


@csrf_exempt
def signup_callback(
    request,
):  # Works currently with phone_number. Code needs to be adapted to use email too.
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

@transaction.atomic
def save_getotp(getotp, user_details):
    user = user_details.user
    getotp.user = user
    getotp.status = "verified"
    getotp.save()
    user.is_active = True
    user.save()


@csrf_exempt
def login_callback(
    request,
):  # Works currently with phone_number. Code needs to be adapted to use email too.
    payload = json.loads(request.body)
    otp_id = payload["otp_id"]
    User = get_user_model()

    if payload["auth_status"] == "verified":
        if getattr(settings, "GETOTP_CUSTOM_USER", False):
            try:
                user = User.objects.get(
                    **{get_fields(field="phone_number"): payload["phone_number"]},
                    is_active=True,
                )
            except User.DoesNotExist:
                pass
            except Exception as e:
                logger.error(
                    f"Exception occured when trying to fetch user with otp_id: {otp_id} - {e}"
                )

            if user.getotp.get(otp_id=otp_id).exists():
                getotp = user.getotp.get(otp_id=otp_id)
                getotp.status = "verified"
                getotp.user = user

        else:
            try:
                getotp = GetOTP.objects.get(otp_id=otp_id)
            except Exception as e:
                logger.error(
                    f"Exception occured when trying to fetch user_details with otp_id: {otp_id} - {e}"
                )

            getotp.status = "verified"
            if UserDetails.objects.filter(phone_number=payload["phone_number"], user__is_active=True
            ).exists():
                getotp.user = UserDetails.objects.get(
                    phone_number=payload["phone_number"],
                    user__is_active=True
                ).user

    getotp.callback_time = timezone.now()
    getotp.save()
    return HttpResponse(status=200)
