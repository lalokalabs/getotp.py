#!/usr/bin/env python
# $Id$
#
# Copyright (c) 2021 Lalokalabs Inc

__author__ = "Surya Banerjee <surya@xoxzo.com>"

import logging
from urllib.parse import urlparse, urlunparse

from django.urls import reverse
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

from getotp.models import OTP

User = get_user_model()

logger = logging.getLogger(__name__)

class OTPBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        otp_id = username
        try:
            otp = OTP.objects.get(otp_id=otp_id)
        except Exception as e:
            logger.error(f"Exception occured when trying to fetch otp_id: {otp_id} - {e}")
            return None

        if otp.status != "verified":
            logger.warning(f"Attempt to complete non-verified otp {getotp}")
            return None

        try:
            user = User.objects.get(email=otp.email)
        except User.DoesNotExist:
            logger.error(f"Login attempt for non-existsing user {getotp.email}")
            return None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
