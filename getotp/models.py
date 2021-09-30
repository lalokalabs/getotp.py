#!/usr/bin/env python
# $Id$
#
# Copyright (c) 2021 Lalokalabs Inc

__author__ = "Surya Banerjee <surya@xoxzo.com>"


from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model


class SignUp(models.Model):
    otp_id = models.CharField(max_length=100, unique=True)
    link = models.URLField()
    otp_secret = models.CharField(max_length=100)
    status = models.CharField(max_length=200, default="initiated")
    callback_time = models.DateTimeField(null=True, blank=True)
    creation_time = models.DateTimeField(default=timezone.now, blank=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="signup", blank=True, null=True)

class UserDetails(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="signup_details")
    phone_number = models.CharField(max_length=15, blank=False, null=True)

