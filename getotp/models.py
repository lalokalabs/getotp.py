#!/usr/bin/env python
# $Id$
#
# Copyright (c) 2021 Lalokalabs Inc

__author__ = "Surya Banerjee <surya@xoxzo.com>"


from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model


class Registration(models.Model):
    otp_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=200, default="initiated")
    phone_number = models.CharField(max_length=15, blank=False)
    email = models.EmailField(max_length=200, blank=False)
    fullname = models.CharField(max_length=255, blank=False)
    callback_time = models.DateTimeField(null=True, blank=True)
    creation_time = models.DateTimeField(default=timezone.now, blank=True)

class UserDetails(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="details")
    phone_number = models.CharField(max_length=15, blank=False)
    verified = models.BooleanField(default=False)
