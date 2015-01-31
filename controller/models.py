from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    nickname = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    picture = models.ImageField(upload_to="profile", default='default.png')
    reg_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    activation_key = models.CharField(max_length=40)
    key_expires = models.DateTimeField()



class Friendship(models.Model):
    reg_date = models.DateTimeField(auto_now_add=True, editable=False)
    user = models.ForeignKey(User, related_name="user")
    friend = models.ForeignKey(User, related_name="friend")


class Rooms(models.Model):
    reg_date = models.DateTimeField(auto_now_add=True, editable=False)
    creator = models.ForeignKey(User)
    attendants_list = models.TextField()
    
class RoomAttendants(models.Model):
    room = models.ForeignKey(Rooms)
    user = models.ForeignKey(User)


class Messages(models.Model):
    room = models.ForeignKey(Rooms)
    author = models.ForeignKey(User)
    reg_date = models.DateTimeField(auto_now_add=True, editable=False)
    msg_type = models.IntegerField(default=0)
    contents = models.TextField(null=False)

class RoomNotifications(models.Model):
    user = models.ForeignKey(User)
    message = models.ForeignKey(Messages)
    processed = models.BooleanField(default=False)
