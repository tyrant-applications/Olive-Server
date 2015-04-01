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
def add_friends(request):
    if not request.POST.get('friends_id'):
        return print_json_error(None, "Please input Friends IDs", '#1')    
    
    friends_id = request.POST['friends_id']
    friends = friends_id.split(",")
    if len(friends) <= 0:
        return print_json_error(None,"No Friends",'#2')
    
    results = list()
    try:
        user = get_user_from_token(request)
        if user is None:
            return print_json_error(None,"No such User",'#0')

        for friend_id in friends:
            f_id = friend_id.strip()
            try:
                print f_id
                f_user = get_user(f_id)
                if not f_user.is_active:
                    continue
                if user.username.lower() == f_user.username.lower():
                    return print_json_error(None, "You cannot add yourself",'#6')
                friendship, created = Friendship.objects.get_or_create(user=user, friend=f_user)
                friend_info = process_user_profile(f_user)
                if friend_info is not None:
                    results.append(friend_info)
            except Exception as e:
                print str(e)
    except:
        return print_json_error(None,"Invalid user",'#5')
    
    return print_json(results)


@csrf_exempt
@post_required
@token_required
def delete_friends(request):

    if not request.POST.get('friends_id'):
        return print_json_error(None, "Please input Friends IDs", '#1')    
    
    friends_id = request.POST['friends_id']
    friends = friends_id.split(",")
    if len(friends) <= 0:
        return print_json_error(None,"No Friends",'#2')
    
    results = list()
    try:
        user = get_user_from_token(request)
        if user is None:
            return print_json_error(None,"No such User",'#0')

        for friend_id in friends:
            f_id = friend_id.strip()
            try:
                f_user = get_user(f_id)
                if user.username.lower() == f_user.username.lower():
                    return print_json_error(None, "You cannot delete yourself",'#6')
                
                friendship = Friendship.objects.get(user=user, friend=f_user)
                friendship.delete()
                friend_info = process_user_profile(f_user)
                if friend_info is not None:
                    results.append(friend_info)
            except Exception as e:
                return print_json_error(None,"No such Friendship "+f_id,'#4')
        
            return print_json(results)
    except:
        return print_json_error(None,"Invalid user",'#5')
    

@csrf_exempt
@post_required
def find_friends(request):
    results = dict()
    results["emails"] = list()
    results["contacts"] = list()
    if request.POST.get("emails"):
        emails_info = request.POST['emails']
        emails = emails_info.split(",")
        if len(emails) <= 0:
            return print_json_error(None,"No Emails",'#2')
        
        for email in emails:
            try:
                f_user = get_user(email)
                if not f_user.is_active:
                    continue
                friend_info = process_user_profile(f_user)
                print friend_info
                if friend_info is not None:
                    results["emails"].append(friend_info)
            except Exception as e:
                print str(e)
                continue
    
    if request.POST.get("contacts"):
        contacts_info = request.POST['contacts']
        contacts = contacts_info.split(",")
        if len(contacts) <= 0:
            return print_json_error(None,"No Contacts",'#2')
        
        for contact in contacts:
            try:
                f_user_profile = UserProfile.objects.get(phone=contact)
                if not f_user_profile.user.is_active:
                    continue
                print f_user_profile
                friend_info = process_user_profile(f_user_profile.user)
                if friend_info is not None:
                    results["contacts"].append(friend_info)
            except:
                continue
    
    return print_json(results)
    

@csrf_exempt
@post_required
def profile_friends(request):
    if not request.POST.get('friends_id'):
        return print_json_error(None, "Please input Friends IDs", '#1')    
    
    friends_id = request.POST['friends_id']
    friends = friends_id.split(",")
    if len(friends) <= 0:
        return print_json_error(None,"No Friends",'#2')
    
    results = list()
    try:
        user = get_user_from_token(request)
        if user is None:
            return print_json_error(None,"No such User",'#0')

        for friend_id in friends:
            f_id = friend_id.strip()
            try:
                f_user = get_user(f_id)
                if not f_user.is_active:
                    continue
                friend_info = process_user_profile(f_user)
                if friend_info is not None:
                    results.append(friend_info)
            except Exception as e:
                print str(e)
    except:
        return print_json_error(None,"Invalid user",'#5')
    
    return print_json(results)

@csrf_exempt
@token_required
def list_friends(request):
    try:
        user = get_user_from_token(request)
        if user is None:
            return print_json_error(None,"No such User",'#0')

        friendships = Friendship.objects.filter(user=user)
        results = list()
        for friendship in friendships:
            friend_info = process_user_profile(friendship.friend)
            if friend_info is not None:
                results.append(friend_info)
        
        return print_json(results)
    except Exception as e:
        print str(e)
        return print_json_error(None,"Invalid user",'#5')
