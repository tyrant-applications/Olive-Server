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

import dateutil.parser



def get_unread_count(user):
    try:          
        notifications = RoomNotifications.objects.filter(user=user, processed=False)
        return len(notifications)
    except Exception as e:
        return 0


'''
push_type
1: new message
2: room create
3: leave room
4: 
'''
def add_notification(from_user,to_user, data, push_type):
    if not to_user.is_active:
        return False
    try:
        user_profile = UserProfile.objects.get(user=to_user)
        if not user_profile.device_id:
            return False
        if user_profile.device_type == 2: #ios
            data['unread_cnt'] = get_unread_count(to_user)
        data['push_type'] = push_type
        contents = json.dumps(data)
        noti = PushNotifications.objects.create(from_user=from_user,to_user=to_user,device_id=user_profile.device_id, device_type = user_profile.device_type, contents=contents, push_type=push_type)        
        return True
    except Exception as e:
        print str(e)
        return False


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
        result['update_date'] = str(user_profile.update_date)
        return result
    except Exception as e:
        return None
        
def process_room_info(room):
    result = dict()
    result['id'] = room.id
    result['create_date'] = str(room.reg_date)
    result['creator'] = process_user_profile(room.creator)
    result['room_attendants'] = room.attendants_list
    try:
        last_msg = Messages.objects.filter(room=room).order_by('-reg_date')[0]
        result['last_msg'] = process_message(last_msg)
    except:
        result['last_msg'] = ''
    
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
        if message.attached_file is not None:
            result['contents'] = message.attached_file.file_contents.url
        return result
    except Exception as e:
        print str(e)
        return None
    

def check_user_in_room(user, room):
    attendant = RoomAttendants.objects.filter(room=room, user=user)
    if len(attendant) <= 0:
        return False
    return True

def get_user_from_token(request):
    try:
        key = request.META.get('HTTP_AUTHORIZATION')
        if access_from_local(request):
            token = AccessToken.objects.get(token='development')
        else:
            token = AccessToken.objects.get(token=key)
        if not token:
            return None
        if not token.user.is_active:
            return None
        return token.user
    except:
        return None


def get_datetime_from_str(str):
    return dateutil.parser.parse(str)



# decorators
def token_required(func):
    def decorator(request, *args, **kwargs):
        if access_from_local(request):
            return func(request, *args, **kwargs)

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
                    return func(request, *args, **kwargs)
                except AccessToken.DoesNotExist, e:
                    return print_json_error('', "invalid token", "#4") 
        except Exception as e:
            return print_json_error('',"something wrong","#5")
        return func(request, *args, **kwargs)

    return decorator


def post_required(func):
    def decorated(request, *args, **kwargs):
        if access_from_local(request):
            return func(request, *args, **kwargs)
        if request.method != 'POST':        
            return print_json_error(None,"Please Use POST Method",'#1')
        return func(request, *args, **kwargs)
    return decorated



# For Development
def access_from_local(request):
    #if get_client_ip(request) == '127.0.0.1':
    #    return True
    return False

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
