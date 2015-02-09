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
def post(request):
    if not request.POST.get('room_id'):
        return print_json_error(None,"Room ID required",'#0.1')

    if not request.POST.get('msg_type'):
        return print_json_error(None,"Message Type required",'#0.2')

    room_id = request.POST['room_id']
    msg_type = request.POST['msg_type']
    
    if msg_type == '0': #text message
        return post_text(request, room_id, msg_type)
    elif msg_type == '1': #image
        return post_file(request, room_id, msg_type)
    elif msg_type == '2': #video
        return post_file(request, room_id, msg_type)
    elif msg_type == '3': #audio
        return post_file(request, room_id, msg_type)
    elif msg_type == '4': #location
        return post_text(request, room_id, msg_type)
    elif msg_type == '5': #emoticon
        return post_text(request, room_id, msg_type)
    return print_json_error(None,"Unsupported MSG Type",'#5.0')


def post_file(request, room_id, msg_type):
    #upload_files(request)
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
            message = Messages.objects.create(room=room, author=user, msg_type=msg_type,contents=msg_type)
            
            success, attached_file = upload_files(request)
            if success == False:
                message.delete()
                print attached_file
                if attached_file == 0:
                    return print_json_error(None,"No File", '#3.1')                
                elif attached_file == -2:
                    return print_json_error(None,"No Such User", '#3.2')
                return print_json_error(None,"File Upload Error", '#3')
            
            message.attached_file = attached_file
            
            message_saved = False
            for attendant in attendants:
                if user.username.lower() == attendant.user.username.lower():
                    message_saved = True
                    message.save()
            
            if not message_saved:
                message.delete()
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
            if message is not None:
                if isinstance(message, Messages):
                    message.delete()
            return print_json_error(None,"Something wrong", '#3')

    except Exception as e:
        print str(e)
        return print_json_error(None,"Invalid user",'#5')
    


def post_text(request, room_id, msg_type):
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
                message.delete()
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
            if message is not None:
                if isinstance(message, Messages):
                    message.delete()
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
        if request.POST.get('last_msg_id'):
           last_msg_id = request.POST['last_msg_id']
           query = Q(message__id__lte=last_msg_id)
        
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
@token_required
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





import uuid
def save_upload(request, uploaded, filename, raw_data ):
    """
    raw_data: if True, upfile is a HttpRequest object with raw post data
    as the file, rather than a Django UploadedFile from request.FILES
    """
    try:
        user = get_user_from_token(request)
        if user is None:
            return False, -2
        input_file_name = filename
        (fileBaseName, fileExtension)=os.path.splitext(filename)
        real_file_name = str(user.id) + "_" + str(uuid.uuid1()) + fileExtension
        filename = os.path.normpath(os.path.join(settings.MEDIA_ROOT+'/files/', real_file_name))
        
        with BufferedWriter( FileIO( filename, "w" ) ) as dest:
            # if the "advanced" upload, read directly from the HTTP request
            # with the Django 1.3 functionality
            if raw_data:
                (dirName, fileName) = os.path.split(filename)
                (fileBaseName, fileExtension)=os.path.splitext(fileName)
                fileExtension=fileExtension[1:]
#                 print fileName+"['"+fileBaseName+ "','"+fileExtension+"']"
                
                new_file = AttachedFile(file_type=fileExtension,file_name=input_file_name, uploader=user)
                new_file.file_contents.save(fileName,ContentFile(uploaded.read()))
            # if not raw, it was a form upload so read in the normal Django chunks fashion
            else:
                (dirName, fileName) = os.path.split(filename)
                (fileBaseName, fileExtension)=os.path.splitext(fileName)
                fileExtension=fileExtension[1:]
#                 print "2 " + fileName+"['"+fileBaseName+ "','"+fileExtension+"']"
                
                # TODO: figure out when this gets called, make it work to save into a Photo like above
                for c in uploaded.chunks():
                    dest.write( c )
                
                dest.close()
#                fileName2 = str(user.id) + "_" + str(uuid.uuid1()) +'.'+ fileExtension
#                 new_file = AttachedFile(file_type=fileExtension,file_name=fileName2, uploader=user)
#                 new_file.file_contents.save(fileName2,ContentFile(uploaded.read()))
#                 new_file.save()
                new_file = AttachedFile(file_type=fileExtension,file_name=fileName, uploader=user)
                #fileName2 = user.username + "_" + str(uuid.uuid1()) +'.'+ fileExtension
                new_file.file_contents.save(fileName,File(open(filename)))
                new_file.save()

    except Exception as e:
        print str(e)
        # could not open the file most likely
        return False, -1
    return True, new_file


@csrf_exempt
def upload_files(request):
    is_raw = False
    if len( request.FILES ) == 1:
        upload = request.FILES.values()[ 0 ]
    else:
        return False, 0
    filename = upload.name
    filename=smart_unicode(filename, encoding='utf-8', strings_only=False, errors='strict')
    # save the file
    
    return save_upload(request, upload, filename, is_raw)
