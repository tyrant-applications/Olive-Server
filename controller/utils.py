#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User

from controller.models import *
from django.shortcuts import get_object_or_404
from django.utils.encoding import smart_unicode
from django.http import HttpResponse

import json
import parser
import re



from django.conf import settings


from django.core import serializers

import datetime
from provider.oauth2.models import AccessToken
from functools import wraps
from django.utils.decorators import available_attrs
from django.utils import timezone

def print_json(data):
    result=dict()
    result['success']=True
    result['message']='Success'
    result['data']=data
    return HttpResponse(json.dumps(result, indent=4), content_type='application/json')

def print_json_error(data,msg,code):
    result=dict()
    result['success']=False
    result['message']=msg
    result['data']=data
    result['error_code']=code
    return HttpResponse(json.dumps(result, indent=4), content_type='application/json')

def process_user_profile(user):
    if not user.is_active:
        return None
    try:
        user_profile = UserProfile.objects.get(user=user)
        
        result = dict()
        result['username'] = user.username
        result['phone'] = user_profile.phone
        result['picture'] = user_profile.picture.url
        return result
    except Exception as e:
        return None
        
def process_room_info(room):
    result = dict()
    result['id'] = room.id
    result['create_date'] = str(room.reg_date)
    result['creator'] = process_user_profile(room.creator)
    return result    

def process_message(message):
    try:
        result = dict()
        result['message_id'] = message.id        
        result['room_id'] = message.room.id
        result['author'] = message.author.username
        result['reg_date'] = str(message.reg_date)
        result['msg_type'] = str(message.msg_type)
        result['contents'] = message.contents
        return result
    except Exception as e:
        return None
    


def token_required(function):
    @wraps(function)
    def decorator(*args, **kwargs):
        request = args[0]
        key = request.META.get('HTTP_AUTHORIZATION')
        #print request
        try:
            if not key:
                return print_json_error('', "No token", "#1")
            else:
                try:
                    token = AccessToken.objects.get(token=key)
                    if not token:
                        return print_json_error('', "invalid token", "#2")
#                    if token.expires < datetime.datetime.now():
                    if token.expires < timezone.now():
                        return print_json_error('', "expired token", "#3")
                    if not token.user.is_active:
                        return print_json_error('', "inactive user", "#6")
                    #return print_json(process_user_profile(token.user))
                    return function
                except AccessToken.DoesNotExist, e:
                    return print_json_error('', "invalid token", "#4") 
        except Exception as e:
            return print_json_error('',"something wrong","#5")
        return function

    return decorator


# decorators
def post_required(func):
    def decorated(request, *args, **kwargs):
        if request.method != 'POST':
            return print_json_error(None,"Please Use POST Method",'#1')
        return func(request, *args, **kwargs)
    return decorated
