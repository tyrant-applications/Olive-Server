#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User

from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout

from django.forms.models import model_to_dict

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.mail import send_mail

from django.core.files.base import ContentFile
from django.core.files import File


from controller.models import *
from controller.utils import *
from controller.forms import *

import datetime,json

from django.utils.encoding import smart_unicode, smart_str
from django.db.models import Q


from django.conf import settings

from emailusernames.utils import *

import os,json
from django.conf import settings
from io import BufferedWriter,FileIO
from django import forms


import re

from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@post_required
@token_required
def check(request):
    result = dict()
    if not request.POST.get('device_type'):
        return print_json_error(None,"Device Type required",'#0.2')
    if not request.POST.get('device_id'):
        return print_json_error(None,"Device ID required",'#0.2')

    device_type = request.POST['device_type']
    device_id = request.POST['device_id']

    try:
        user = get_user_from_token(request)
        if user is None:
            return print_json_error(None,"No such User",'#0.1')
		
        if not user.is_active:
            return print_json_error(None,"No such User",'#0.2')
        
        try:
            user_profile = UserProfile.objects.get(user=user)
            if user_profile.device_type == 0:
                return print_json(process_user_profile(user))
            else:
                if (device_type == str(user_profile.device_type)) & (device_id == user_profile.device_id):
                    return print_json(process_user_profile(user))
                return print_json_error(None,"Old Device, Do Logout",'#1')
        except Exception as e:
            return print_json_error(None,"Error Loading Profile",'#2')
		
    except Exception as e:
        print str(e)
        return print_json_error(None,"Invalid user",'#5')
    