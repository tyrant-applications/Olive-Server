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
def create_room(request):
        
    username = request.POST['username']
    friends_id = request.POST['friends_id']
     
#     username = 'ujlikes@naver.com'
#     friends_id = '3ujlikes2@naver.com, ujlikes2@naver.com'
    
    friends = friends_id.split(",")
    if len(friends) <= 0:
        return print_json_error(None,"No Friends",'#2')
    
    results = dict()
    results['room_attentdants'] = list()
    
    try:
        user = get_user(username)
        new_room = Rooms.objects.create(creator=user)
        results['room'] = process_room_info(new_room)

        friends.append(username)
        for friend_id in friends:
            f_id = friend_id.strip()
            try:
                f_user = get_user(f_id)
                if not f_user.is_active:
                    continue
                attendant, created = RoomAttendants.objects.get_or_create(user=f_user, room=new_room)
                friend_info = process_user_profile(f_user)
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
def leave_room(request):
            
    username = request.POST['username']
    room_id = request.POST['room_id']
    # 
#     username = 'ujlikes@naver.com'
#     room_id = '7'
#     
    result = dict()
    try:
        user = get_user(username)
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
def info(request): 
    username = request.POST['username']
    room_id = request.POST['room_id']
#     
#     username = "ujlikes@naver.com"
#     room_id = '10'
    
    results = dict()
    results['room_attentdants'] = list()

    try:
        user = get_user(username)
        room = Rooms.objects.filter(id=room_id)
        if len(room) != 1:
            return print_json_error(None,"Invalid Room", '#2')
        room = room[0]
        try:
            attendants = RoomAttendants.objects.filter(room=room)
            
            user_in_room = False
            for attendant in attendants:
                if user.username.lower() == attendant.user.username.lower():
                    #user is attendant
                    user_in_room = True
                    
            if not user_in_room:
                return print_json_error(None,"You are not participant of this room", '#3')
            
            
            results['room'] = process_room_info(room)

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
