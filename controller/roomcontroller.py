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

from django.utils.encoding import smart_unicode

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
def create_room(request):
             
#     username = 'ujlikes@naver.com'
#     friends_id = '3ujlikes2@naver.com, ujlikes2@naver.com'
    if not request.POST.get('friends_id'):
        return print_json_error(None, "Please input Friends IDs", '#1')    
    
    results = dict()
    results['room_attentdants'] = list()
    
    try:
        user = get_user_from_token(request)
        if user is None:
            return print_json_error(None,"No such User",'#0')
        new_room = Rooms.objects.create(creator=user)
        results['room'] = process_room_info(new_room)

        friends_id = request.POST['friends_id']
        friends_id_list = friends_id.split(",")
        active_users = list()
        for friend_id in friends_id_list:
            f_id = friend_id.strip()
            f_user = get_user(f_id)
            if not f_user.is_active:
                continue
            active_users.append(f_user)

        active_users.remove(user) # Case: my email is in friend_id, (Chat with myself? nono)
        
        if len(active_users) <= 0:
            return print_json_error(None,"No Friends",'#2')

        active_users.append(user)
        for active_user in active_users:
            try:
                attendant, created = RoomAttendants.objects.get_or_create(user=active_user, room=new_room)
                friend_info = process_user_profile(active_user)
                if friend_info is not None:
                    results['room_attentdants'].append(friend_info)
            except Exception as e:
                print str(e)
                return print_json_error(None,"No such User "+f_id,'#4')
    except Exception as e:
        print str(e)
        return print_json_error(None,"Invalid user",'#5')
    return print_json(results)
       

@csrf_exempt
@post_required
@token_required
def leave_room(request):
                
    if not request.POST.get('room_id'):
        return print_json_error(None, "Please input Room ID", '#1')    

    room_id = request.POST['room_id']
    
    result = dict()
    try:
        user = get_user_from_token(request)
        if user is None:
            return print_json_error(None,"No such User",'#0')
        room = Rooms.objects.filter(id=room_id)
        if len(room) != 1:
            return print_json_error(None,"Invalid Room", '#2')
        try:
            ## TODO 1: Add room out message
            ## TODO 2: delete room if there is no attendants?
            
            attendant = RoomAttendants.objects.get(user=user, room=room)
            attendant.delete()
            
        except:
            return print_json_error(None,"You are not participant of this room", '#3')

    except Exception as e:
        print str(e)
        return print_json_error(None,"Invalid user",'#5')

    return print_json(result)
       


@csrf_exempt
@post_required
@token_required
def info(request): 
    if not request.POST.get('room_id'):
        return print_json_error(None, "Please input Room ID", '#1')    

    room_id = request.POST['room_id']

    results = dict()
    results['room_attentdants'] = list()

    try:
        user = get_user_from_token(request)
        if user is None:
            return print_json_error(None,"No such User",'#0')
        room = Rooms.objects.filter(id=room_id)
        if len(room) != 1:
            return print_json_error(None,"Invalid Room", '#2')
        room = room[0]
        try:                    
            if not check_user_in_room(user, room):
                return print_json_error(None,"You are not participant of this room", '#3')
            
            results['room'] = process_room_info(room)

            attendants = RoomAttendants.objects.filter(room=room)
            for attendant in attendants:
                friend_info = process_user_profile(attendant.user)
                if friend_info is not None:
                    results['room_attentdants'].append(friend_info)

            return print_json(results)

        except Exception as e:
            print str(e)
            return print_json_error(None,"Something wrong", '#6')

    except Exception as e:
        print str(e)
        return print_json_error(None,"Invalid user",'#5')

    return print_json(results)
