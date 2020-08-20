from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    user_profile = models.FileField(upload_to='user-profile/', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    REQUIRED_FIELDS = ['user_profile', 'updated_at']


class ChatGroup(models.Model):
    group_name = models.CharField(max_length=250)
    group_users = models.CharField(max_length=250, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)


class Room(models.Model):
    room_name = models.CharField(max_length=250)
    allowed_users = models.CharField(max_length=250, blank=True, null=True)
    allowed_group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)


class Messages(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, blank=True, null=True)
    sender = models.ForeignKey('User', on_delete=models.CASCADE, related_name='sender_user')
    receiver = models.ForeignKey('User', on_delete=models.CASCADE, related_name='receiver_user', blank=True, null=True)
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, blank=True, null=True)
    message = models.TextField(max_length=65500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

