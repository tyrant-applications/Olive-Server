#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout


from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.mail import send_mail

from controller.models import *
from controller.utils import *
from controller.emailer import *

import datetime,json

from django.utils.encoding import smart_unicode

from django.conf import settings

def main(request):
    t = loader.get_template('console.html')
    context = RequestContext(request)

    return HttpResponse(t.render(context))

def signin(request):
    t = loader.get_template('signin.html')
    context = RequestContext(request)

    return HttpResponse(t.render(context))

def update(request):
    t = loader.get_template('update.html')
    context = RequestContext(request)

    return HttpResponse(t.render(context))


def leave(request):
    t = loader.get_template('leave.html')
    context = RequestContext(request)

    return HttpResponse(t.render(context))


def add_friends(request):
    t = loader.get_template('add_friends.html')
    context = RequestContext(request)

    return HttpResponse(t.render(context))

def delete_friends(request):
    t = loader.get_template('delete_friends.html')
    context = RequestContext(request)

    return HttpResponse(t.render(context))

def find_friends(request):
    t = loader.get_template('find_friends.html')
    context = RequestContext(request)

    return HttpResponse(t.render(context))

def message_new(request):
    t = loader.get_template('message_new.html')
    context = RequestContext(request)

    return HttpResponse(t.render(context))


@token_required
def check_token(request):
	return HttpResponse("123")