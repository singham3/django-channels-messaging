import json
from channels.generic.websocket import AsyncWebsocketConsumer
from UserApp.models import *
from django.db.models import Q
from channels.db import database_sync_to_async
from django.core.paginator import Paginator
from django.forms.models import model_to_dict


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_authenticated:
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.method = self.scope['url_route']['kwargs']['method']
            self.page = self.scope['url_route']['kwargs']['page'] if self.scope['url_route']['kwargs']['page'] else 1
            self.room_obj = await database_sync_to_async(self.is_room)()
            self.room_group_name = 'chat_%s' % self.room_name
            print(self.room_name, self.method, self.page, self.room_obj)

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            if self.method == "GET":
                self.messages_json = await database_sync_to_async(self.get_messages)()
                await self.send(text_data=json.dumps({'messages': self.messages_json}))

    def get_messages(self):
        if Messages.objects.filter(room=self.room_obj).exists():
            msg_obj = Messages.objects.filter(room=self.room_obj)
            if msg_obj.exists():
                paginator = Paginator(msg_obj, 10)
                messages_data = paginator.page(self.page)
                msg_list = []
                for k in messages_data:
                    json = model_to_dict(k)
                    json['created_at'] = k.created_at.strftime("%Y-%m-%d %H:%M:%S.%f")
                    json['sender'] = k.sender.username
                    json['sender_profile'] = k.sender.user_profile.url
                    json['receiver'] = k.receiver.username
                    json['receiver_profile'] = k.receiver.user_profile.url
                    msg_list.append(json)
                return msg_list
        return []

    def is_room(self):
        users = []
        if '_' in self.room_name:
            for i in self.room_name.split('_'):
                users.append(User.objects.get(username=i).id)
            if any(users):
                if Room.objects.filter(Q(allowed_users__contains=users[0]) & Q(allowed_users__contains=users[1])).exists():
                    return Room.objects.get(Q(allowed_users__contains=users[0]) & Q(allowed_users__contains=users[1]))
                else:
                    Room(room_name=self.room_name, allowed_users=str(users)).save()
                    return Room.objects.last()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        self.text_data_json = json.loads(text_data)
        self.text_data_json['type'] = 'chat_message'
        self.rec_msg_json = await database_sync_to_async(self.receive_msg)()
        self.text_data_json['message'] = self.rec_msg_json
        await self.channel_layer.group_send(
            self.room_group_name, self.text_data_json
        )

    def receive_msg(self):

        Messages(room=self.room_obj, sender=User.objects.get(id=self.text_data_json['sender']),
                 receiver=User.objects.get(id=self.text_data_json['receiver']),
                 message=self.text_data_json['message']).save()
        k = Messages.objects.last()
        json = model_to_dict(k)
        json['created_at'] = k.created_at.strftime("%Y-%m-%d %H:%M:%S.%f")
        json['sender'] = k.sender.username
        json['sender_profile'] = k.sender.user_profile.url
        json['receiver'] = k.receiver.username
        json['receiver_profile'] = k.receiver.user_profile.url
        return json

    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
