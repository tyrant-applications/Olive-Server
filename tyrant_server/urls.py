from django.conf.urls import patterns, include, url
from django.conf import settings

from django.conf.urls.static import static

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'tyrant_server.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^oauth2/', include('provider.oauth2.urls', namespace = 'oauth2')),

    url(r'^confirm/$','controller.usercontroller.confirm'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^user/signup',  'controller.usercontroller.signup'),
    url(r'^user/signout',  'controller.usercontroller.signout'),
    url(r'^user/leave',  'controller.usercontroller.leave'),
    url(r'^user/update',  'controller.usercontroller.update'),

    url(r'^accounts/login',  'controller.usercontroller.signin'),


    url(r'^friends/add',  'controller.friendscontroller.add_friends'),
    url(r'^friends/find',  'controller.friendscontroller.find_friends'),
    url(r'^friends/delete',  'controller.friendscontroller.delete_friends'),
    url(r'^friends/profile',  'controller.friendscontroller.profile_friends'),
    url(r'^friends/list',  'controller.friendscontroller.list_friends'),

    url(r'^rooms/create',  'controller.roomcontroller.create_room'),
    url(r'^rooms/leave',  'controller.roomcontroller.leave_room'),
    url(r'^rooms/info',  'controller.roomcontroller.info'),

    url(r'^message/post',  'controller.messagecontroller.post'),
    url(r'^message/read',  'controller.messagecontroller.read'),
    url(r'^message/new',  'controller.messagecontroller.new'),


    url(r'^api/console/message_new', 'api_console.views.message_new'),
    url(r'^api/console/signin', 'api_console.views.signin'),
    url(r'^api/console/update', 'api_console.views.update'),
    url(r'^api/console/leave', 'api_console.views.leave'),
    url(r'^api/console/add_friends', 'api_console.views.add_friends'),
    url(r'^api/console/delete_friends', 'api_console.views.delete_friends'),
    url(r'^api/console/find_friends', 'api_console.views.find_friends'),
    url(r'^api/console', 'api_console.views.main'),
    url(r'^api/check_token', 'api_console.views.check_token'),
    #add_friends

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
