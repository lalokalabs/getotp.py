#!/usr/bin/env python
# $Id$
#
# Copyright (c) 2021 XoxzoEU Inc

__author__ = "Surya Banerjee <surya@xoxzo.com>"

import json
import logging

from django.utils import timezone
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from getotp.auth import confirm_verification
from getotp.models import SignUp

logger = logging.getLogger(__name__)


def signup_success(request):
    otp_id = request.GET.get("otp_id", False)
    if otp_id:
        if confirm_verification(otp_id):
            import pdb

            pdb.set_trace()  ################

    return HttpResponse(status=404)


def login_success(request):
    pass

@csrf_exempt
def signup_callback(request):
    payload = json.loads(request.body)
    if payload["auth_status"] == "verified":
        otp_id = payload["otp_id"]
        try:
            signup = SignUp.objects.get(otp_id=otp_id)
        except Exception as e:
            logger.error(f"Exception occured when trying to fetch otp_id: {otp_id} - {e}")
        else:
            if payload["otp_secret"] == signup.otp_secret:
                signup.status = "verified"
                signup.callback_time = timezone.now()
    
    return HttpResponse(status=200)


def login_callback(request):
    pass

