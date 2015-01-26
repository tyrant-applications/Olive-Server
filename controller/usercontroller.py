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
from controller.emailer import *
import datetime,json

from django.utils.encoding import smart_unicode

from django.conf import settings

from emailusernames.utils import *

import os,json
from django.conf import settings
from io import BufferedWriter,FileIO
from django import forms

from django.views.decorators.csrf import csrf_exempt


import re

@csrf_exempt
@post_required
def leave(request):

    if not request.POST.get('username'):
        return print_json_error(None,"Please Input Username",'#1.1')

    if not request.POST.get('password'):
        return print_json_error(None,"Please Input Password",'#1.2')

    username = request.POST['username']
    password = request.POST['password']
    

    try: 
        user = authenticate(username=username,password=password)
        if user is not None:
            user.is_active = False
            user.save()
        else:
            try:
                user = get_user(username)
                return print_json_error('Invalid Password','#5')
            except:
                return print_json_error(None,"No such User "+username,'#2')
   
        result = list()
        #result['username'] = process_user(user) 
        return print_json(username)

    except Exception as e:
        print str(e)
        return print_json_error(None,"Something wrong",'#4')

@csrf_exempt
def signup(request):
    if request.user.is_authenticated():
        return print_json_error(None,'You are already logined.','#1')
    if not request.POST:
        return print_json_error(None,'POST method is required.','#2')

    username=request.POST.get('username','')
    username=smart_unicode(username, encoding='utf-8', strings_only=False, errors='strict')
    password=request.POST.get('password','')

    try:
#         username_valid= re.match('[\w0-9]*',username) and len(username) >= 3 and len(username) < 16
        username_valid=re.match('[\w.]*@\w*\.[\w.]*',username)
        password_valid=len(password) >= 6 

        if not (username_valid and password_valid):
            return print_json_error(None,'username or password invalid','#3')
            
        impossible_username = ['apple','facebook','twitter']    
        if username in impossible_username:
            return print_json_error(username+' is already taken','#7')
        try:
            user = get_user(username)
            return print_json_error(username+' is already taken','#4')
        except:
            new_user = create_user(username, password)
            #new_user = User.objects.create_user(username,password)
            new_user.is_active = True
            new_user.email = username
            new_profile = UserProfile(user=new_user)
            try:
                new_user.save()
                new_profile.save()
            except Exception as e:
                print "2: " + str(e)
                return print_json_error(None,"Something wrong:2",'#5')
            return print_json(username)
    except Exception as e:
        print str(e)
        return print_json_error(None,"Something wrong:3",'#')
    return print_json_error(None,"Something wrong:4",'#6')

@csrf_exempt
def signin(request):
    if not request.POST:
        return print_json_error(None,"Please Use POST Method",'#1')

    username = request.POST['username']
    password = request.POST['password']

    try: 
        user = authenticate(username=username,password=password)
        if user is not None:
            login(request, user)
        else:
            return print_json_error(None,"No such User",'#2')
   
        result = list()
        #result['username'] = process_user(user) 
        return print_json(username)

    except Exception as e:
        print str(e)
        return print_json_error(None,"Something wrong",'#4')


def signout(request):
    try:
        user = get_user('ujlikes@naver.com')
        print user.username
        print user.email
        profile = UserProfile.objects.get(user=user)
        print profile
        send_activation_mail(user, profile)
    except Exception as e:
        print str(e)
        return print_json('')
    if request.user.is_authenticated():
    	username = request.user.username
    	logout(request)	
        return print_json(username)
    else:
        return print_json('')
        
        

@csrf_exempt        
@post_required
@token_required
def update(request):   

    try: 
        user = get_user_from_token(request)
        if user is None:
            return print_json_error(None,"No such User",'#2')
        else:
            print user
            user_profile = UserProfile.objects.get(user=user)
            if not request.POST.get("password"):
                if not access_from_local(request):
                    return print_json_error(None, "Please Input User PW", '#2.1')
            else:
                password = request.POST['password']
                if not user.check_password(password):
                    return print_json_error(None, "Invalid User PW", '#2.2')
            
            #set new password
            if request.POST.get("new_password"):
                new_password = request.POST['new_password']
                if new_password is not None and new_password is not '' and len(new_password) > 0:
                    new_password = new_password.strip()
                    
                    if len(new_password) >=6:
                        user.set_password(new_password)
                    else:
                        return print_json_error(None, "Password Length should be >=6", '#4')
            
            if request.POST.get("new_phone"):
                new_phone = request.POST['new_phone']    
                if new_phone is not None and new_phone != '':
                    new_phone = new_phone.strip()
                    user_profile.phone = new_phone
                        
            form = ImageUploadForm(request.POST, request.FILES)
            if form.is_valid():
                user_profile.picture = form.cleaned_data['new_picture']
            
            user.save()            
            user_profile.save()
            
            if form.is_valid():
                make_thumbnail(user, user_profile)
            #upload new profile picture
            return print_json(user.username)
                
    except Exception as e:
        print str(e)
        return print_json_error(None,"Something wrong",'#4')

from PIL import Image, ImageOps

size = 128, 128

def make_thumbnail(user, user_profile):
    try:
        if user_profile.picture.name:
            filename = os.path.join(settings.MEDIA_ROOT, user_profile.picture.name)
            (dirName, fileName) = os.path.split(filename)
            image = Image.open(filename)
            #thumb = ImageOps.fit(image, size, Image.ANTIALIAS)
            #thumb = image.resize((150,150), Image.ANTIALIAS)
            #thumb.save(filename+".thumb.png", 'PNG', quality=75)
            image.thumbnail(size, Image.ANTIALIAS)
            image.save(filename+".thumb.png", 'PNG', quality=75)
    except IOError as e:
    	print e
    	return False
    return True



def confirm(request):
    activation_key=request.GET['key']
        
    user_profile = UserProfile.objects.get(activation_key=activation_key)
    #if user_profile.key_expires < datetime.datetime.today():
    #    return HttpResponse('Expired Key. ')
    
    user_account = user_profile.user
    user_account.is_active = True
    user_account.save()
    return HttpResponse(user_account.username + ' is Activated. ')



