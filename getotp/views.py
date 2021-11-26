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
from django.views.decorators.csrf import csrf_exempt

from getotp.models import GetOTP
from getotp.auth import send_otp

logger = logging.getLogger(__name__)

User = get_user_model()

def login_start(request):
    if request.method == "POST":
        otp = send_otp("email", "https://boring.xoxzo.site", "https://boring.xoxzo.site")
        if otp.ok:
            return redirect(otp.link)
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
def login_callback(request,):
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

        getotp.status = "verified"

    getotp.callback_time = timezone.now()
    getotp.save()
    return HttpResponse(status=200)
