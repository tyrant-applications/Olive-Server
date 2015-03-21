from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    nickname = models.CharField(max_length=50, null=True)
    phone = models.CharField(max_length=50, null=True)
    picture = models.ImageField(upload_to="profile", default='default.png')
    reg_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    activation_key = models.CharField(max_length=40, null=True)
    key_expires = models.DateTimeField(null=True)
    device_type = models.IntegerField(default=0)
    device_id = models.CharField(max_length=256, null=True)


class Friendship(models.Model):
    reg_date = models.DateTimeField(auto_now_add=True, editable=False)
    user = models.ForeignKey(User, related_name="user")
    friend = models.ForeignKey(User, related_name="friend")


class Rooms(models.Model):
    reg_date = models.DateTimeField(auto_now_add=True, editable=False)
    creator = models.ForeignKey(User)
    attendants_list = models.TextField(null=True)
    
class RoomAttendants(models.Model):
    room = models.ForeignKey(Rooms)
    user = models.ForeignKey(User)


class AttachedFile(models.Model):
    file_type = models.CharField(max_length=10)
    file_contents = models.FileField(upload_to='files',null=False)
    upload_date = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    uploader = models.ForeignKey(User)
    file_name = models.CharField(max_length=256)
    is_attached = models.BooleanField(default=False)


class Messages(models.Model):
    room = models.ForeignKey(Rooms)
    author = models.ForeignKey(User)
    reg_date = models.DateTimeField(auto_now_add=True, editable=False)
    msg_type = models.IntegerField(default=0)
    contents = models.TextField(null=False)
    attached_file = models.ForeignKey(AttachedFile, blank=True, null=True)


class RoomNotifications(models.Model):
    user = models.ForeignKey(User)
    message = models.ForeignKey(Messages)
    processed = models.BooleanField(default=False)


class PushNotifications(models.Model):
    from_user = models.ForeignKey(User,related_name="from_user")
    to_user = models.ForeignKey(User,related_name="to_user")
    push_type = models.IntegerField(default=0)
    device_type = models.IntegerField(default=0)
    device_id = models.CharField(max_length=256)
    contents = models.TextField()
    processed = models.BooleanField(default=False)
