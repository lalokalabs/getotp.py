#!/usr/bin/env python
# $Id$
#
# Copyright (c) 2021 XoxzoEU Inc

__author__ = "Surya Banerjee <surya@lalokalabs.com>"


import phonenumbers

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.module_loading import import_string

from getotp.models import UserDetails


def parse_phone_number(data):
    try:
        phone_number = phonenumbers.parse(data)
        if not phonenumbers.is_valid_number(phone_number):
            raise ValueError("Invalid Phonenumber")
    except phonenumbers.phonenumberutil.NumberParseException:
        raise ValueError("Invalid Phonenumber")
    except AttributeError:
        raise ValueError("Invalid Phonenumber")

    return f"+{phone_number.country_code}", f"{phone_number.national_number}"

# parse fields for custom user
def get_fields(field=""):
    """
    Custom fieldnames should be defined as a dict in settings
    Example:
    #For a custom user model containing "phone" and "mail_id" fieldnames
    GETOTP_CUSTOM_USER_FIELDS = {
        "phone_number": "phone",
        "email": "mail_id",
    }
    """
    field_conf = getattr(settings, "GETOTP_CUSTOM_USER_FIELDS", None)
    if field_conf is not None:
        if "email" in field_conf:
            try:
                email = field_conf["email"]
            except KeyError:
                raise ValueError("Invalid email field config")
        elif "phone_number" in field_conf:
            try:
                phone_number = field_conf["phone_number"]
            except KeyError:
                raise ValueError("Invalid phone_number field config")
        else:
            # Default to fieldname 'email' and 'phone_number' if not specified
            email = "email"
            phone_number = "phone_number"
    else:
        return ["phone_number"]

    if field:
        return field_conf.get(field, None)
    else:
        return (phone_number, email)


class UserDetailForm(forms.ModelForm):
    """
    When using custom user model, specify boolean in settings
    Example:
    #For custom user model
    GETOTP_CUSTOM_USER = True
    """
    invalid_phonenumber_err = "Please enter a valid phone number."

    class Meta:
        if getattr(settings, "GETOTP_CUSTOM_USER", False):
            model = get_user_model()
            fields = get_fields()
        else:
            model = UserDetails
            fields = ["phone_number"]

    def clean_email(self):
        email = self.cleaned_data["email"]
        User = get_user_model()
        if getattr(settings, "GETOTP_CUSTOM_USER", False):
            qs = User.objects.filter(**{get_fields(field="email"): email}, is_active=True)
        else:
            qs = User.objects.filter(email=email, is_active=True)

        if qs.count() > 0:
            raise forms.ValidationError("email invalid or already in use")

        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data["phone_number"]

        try:
            locale, national_number = parse_phone_number(phone_number)
        except ValueError:
            raise forms.ValidationError(self.invalid_phonenumber_err)

        phone_number = locale + national_number

        # Validate phone number already in use
        User = get_user_model()
        if getattr(settings, "GETOTP_CUSTOM_USER", False):
            qs = User.objects.filter(**{get_fields(field="phone_number"): phone_number}, is_active=True)
        else:
            qs = UserDetails.objects.filter(phone_number=phone_number)

        if qs.count() > 0:
            raise forms.ValidationError("phone_number invalid or already in use")

        return phone_number
