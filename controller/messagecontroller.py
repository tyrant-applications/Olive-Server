#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User

from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout

from django.forms.models import model_to_dict

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.mail import send_mail

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
def post(request):

    username = request.POST['username']
    room_id = request.POST['room_id']
    msg_type = request.POST['msg_type']
    if request.POST['contents']:
        contents = smart_unicode(request.POST['contents'], encoding='utf-8', strings_only=False, errors='strict')

#     username = 'ujlikes@naver.com'
#     room_id = '9'
#     msg_type = '0'
#     contents = u'안녕친구야'
#     if contents:
#         contents = smart_unicode(contents, encoding='utf-8', strings_only=False, errors='strict')

    result = dict()
    try:
        user = get_user(username)
        room = Rooms.objects.filter(id=room_id)
        if len(room) != 1:
            return print_json_error(None,"Invalid Room", '#2')
        room = room[0]
        try:            
            attendants = RoomAttendants.objects.filter(room=room)
            message = Messages.objects.create(room=room, author=user, msg_type=msg_type,contents=contents)
            
            message_saved = False
            for attendant in attendants:
                if user.username.lower() == attendant.user.username.lower():
                    message_saved = True
                    message.save()
            
            if not message_saved:
                return print_json_error(None,"You are not in this room", '#4')
            
            #TODO : Notification
            for attendant in attendants:
                if user.username.lower() != attendant.user.username.lower():
                    noti = RoomNotifications.objects.create(user=attendant.user, message=message)
                    noti.save()
            
            result = process_message(message)
            return print_json(result)

        except Exception as e:
            print str(e)
            return print_json_error(None,"Something wrong", '#3')

    except Exception as e:
        print str(e)
        return print_json_error(None,"Invalid user",'#5')



@csrf_exempt
@post_required
def read(request):
    username = request.POST['username']
    room_id = request.POST['room_id']

#     username = '3ujlikes2@naver.com'
#     room_id = '9'

    result = list()
    try:
        user = get_user(username)
        room = Rooms.objects.filter(id=room_id)
        if len(room) != 1:
            return print_json_error(None,"Invalid Room", '#2')
        try:            
            attendant = RoomAttendants.objects.get(user=user, room=room)
            
            notifications = RoomNotifications.objects.filter(user=user, processed=False, message__room__id=room_id).order_by('message__reg_date')
            
            for noti in notifications:
                noti.processed = True
                result.append(process_message(noti.message))
                noti.save()
            
            return print_json(result)
        except:
            return print_json_error(None,"You are not participant of this room", '#3')

    except Exception as e:
        print str(e)
        return print_json_error(None,"Invalid user",'#5')

    return print_json(result)


@csrf_exempt
@post_required
def new(request):
    username = request.POST['username']
    room_id = request.POST['room_id']

    #username = '3ujlikes2@naver.com'
    
    result = list()
    try:
        user = get_user(username)
        query = Q()
        if request.POST['room_id']:
            room_id = request.POST['room_id']
            room = Rooms.objects.filter(id=room_id)
            if len(room) != 1:
                return print_json_error(None,"Invalid Room", '#2')
            query = Q(message__room__id=room_id)

        try:            
            if request.POST['room_id']:
                attendant = RoomAttendants.objects.get(user=user, room=room)
            
            notifications = RoomNotifications.objects.filter(query, user=user, processed=False,).order_by('message__reg_date')
            
            for noti in notifications:
                result.append(process_message(noti.message))
            
            return print_json(result)
        except Exception as e:
            print str(e)
            return print_json_error(None,"You are not participant of this room", '#3')

    except Exception as e:
        print str(e)
        return print_json_error(None,"Invalid user",'#5')

    return print_json(result)


