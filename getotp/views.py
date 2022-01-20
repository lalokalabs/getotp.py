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
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from getotp.models import GetOTP
from getotp.client import send_otp

logger = logging.getLogger(__name__)

User = get_user_model()

@login_required
def index(request):
    return HttpResponse(f"Logged in as {request.user.email}")

def login_start(request):
    if request.method == "POST":
        otp = send_otp("email",
                success_redirect_url=settings.GETOTP_LOGIN_SUCCESS_REDIRECT,
                fail_redirect_url=settings.GETOTP_LOGIN_FAIL_REDIRECT,
                callback_url=settings.GETOTP_CALLBACK,
            )
        if otp.ok:
            return redirect(otp.link)
        print(otp.errors)
    return render(request, "getotp/login/start.html")

def login_complete(request):
    otp_id = request.GET.get("otp_id", None)
    if otp_id is None:
        return redirect("/")

    user = authenticate(request, username=otp_id)
    if user is None:
        return redirect("/")

    login(request, user)
    return redirect("/")


@csrf_exempt
def otp_callback(request):
    payload = json.loads(request.body)
    otp_id = payload["otp_id"]
    otp_secret = payload["otp_secret"]

    if payload["auth_status"] == "verified":
        try:
            getotp = GetOTP.objects.get(otp_id=otp_id, otp_secret=otp_secret)
        except Exception as e:
            logger.error(
                f"Exception occured when trying to fetch user_details with otp_id: {otp_id} - {e}"
            )
        else:
            getotp.email = payload.get("email", "")
            getotp.phone_sms = payload.get("phone_sms", "")
            getotp.phone_voice = payload.get("phone_voice", "")
            getotp.metadata = payload["metadata"]
            getotp.status = "verified"
            getotp.callback_time = timezone.now()
            getotp.save()
            logger.info(f"Saved verified OTP otp_id: {otp_id} email: {getotp.email} phone_sms: {getotp.phone_sms} phone_voice: {getotp.phone_voice}")

    return HttpResponse(status=200)
