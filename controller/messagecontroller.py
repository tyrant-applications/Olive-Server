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
@token_required
def post(request):

    if not request.POST.get('room_id'):
        return print_json_error(None,"Room ID required",'#0.1')

    if not request.POST.get('msg_type'):
        return print_json_error(None,"Message Type required",'#0.2')

    room_id = request.POST['room_id']
    msg_type = request.POST['msg_type']
        
    if request.POST.get('contents'):
        contents = smart_unicode(request.POST['contents'], encoding='utf-8', strings_only=False, errors='strict')
    else:
        return print_json_error(None,"Contents required",'#0.3')
    
    result = dict()
    try:
        user = get_user_from_token(request)
        if user is None:
            return print_json_error(None,"No such User",'#0')
        room = Rooms.objects.filter(id=room_id)
        if len(room) != 1:
            return print_json_error(None,"Invalid Room", '#2')
        room = room[0]
        
        if not check_user_in_room(user, room):
            return print_json_error(None,"You are not participant of this room", '#3')

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
@token_required
def read(request):
    
    if not request.POST.get('room_id'):
        return print_json_error(None,"Room ID required",'#0.1')

    room_id = request.POST['room_id']
    
#     room_id = '9'
#     last_timestamp = "2015-01-26 14:00:00+00:00"
    result = list()
    try:
        user = get_user_from_token(request)
        if user is None:
            return print_json_error(None,"No such User",'#0')
        room = Rooms.objects.filter(id=room_id)
        if len(room) != 1:
            return print_json_error(None,"Invalid Room", '#2')
            
        query = Q()
        if request.POST.get('last_timestamp'):
           last_timestamp = request.POST['last_timestamp']
           query = Q(message__reg_date__lte=get_datetime_from_str(last_timestamp))
        
        try:
            attendant = RoomAttendants.objects.get(user=user, room=room)
            
            notifications = RoomNotifications.objects.filter(query, user=user, processed=False, message__room__id=room_id).order_by('message__reg_date')
            
            for noti in notifications:
                noti.processed = True
                result.append(process_message(noti.message))
                noti.save()
            
            return print_json(result)
        except Exception as e:
            print str(e)
            return print_json_error(None,"You are not participant of this room", '#3')

    except Exception as e:
        print str(e)
        return print_json_error(None,"Invalid user",'#5')

    return print_json(result)


@csrf_exempt
@post_required
def new(request):
    
    result = list()
    try:
        user = get_user_from_token(request)
        if user is None:
            return print_json_error(None,"No such User",'#0')
        query = Q()
        if request.POST.get('room_id'):
            room_id = request.POST['room_id']
            room = Rooms.objects.filter(id=room_id)
            if len(room) != 1:
                return print_json_error(None,"Invalid Room", '#2')
            query = Q(message__room__id=room_id)

        try:            
            if request.POST.get('room_id'):
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


