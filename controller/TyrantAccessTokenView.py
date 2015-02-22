#!/usr/bin/python
# -*- coding: utf-8 -*-


from provider.oauth2.views import *
from controller.models import *


class TAccessTokenView(AccessTokenView):
    def create_access_token(self, request, user, scope, client):
        device_type = 0
        if request.POST.get('device_type'):
            device_type = int(request.POST['device_type'])        
        device_id = ''
        if request.POST.get('device_id'):
            device_id = request.POST['device_id']        
        
        try:
            user_profile = UserProfile.objects.get(user=user)
            user_profile.device_type = device_type
            user_profile.device_id = device_id
            user_profile.save()
        except Exception as e:
            print str(e)
            pass
        
        return AccessToken.objects.create(
            user=user,
            client=client,
            scope=scope
        )