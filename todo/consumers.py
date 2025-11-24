import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Todo


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        if self.user.is_authenticated:
            self.group_name = f"notifications_{self.user.id}"
            
            # Join notification group
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        # Leave notification group
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']
        
        if message_type == 'notification.read':
            notification_id = text_data_json['notification_id']
            # Mark notification as read in database
            # await self.mark_notification_as_read(notification_id)

    # Receive message from room group
    async def notification_message(self, event):
        message = event['message']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': message,
        }))


class TodoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        if self.user.is_authenticated:
            self.group_name = f"todos_{self.user.id}"
            
            # Join todo updates group
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        # Leave todo updates group
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']
        
        if message_type == 'todo.create':
            todo_data = text_data_json['todo']
            await self.create_todo(todo_data)
        elif message_type == 'todo.update':
            todo_id = text_data_json['todo_id']
            todo_data = text_data_json['todo']
            await self.update_todo(todo_id, todo_data)
        elif message_type == 'todo.delete':
            todo_id = text_data_json['todo_id']
            await self.delete_todo(todo_id)

    # Receive message from room group
    async def todo_message(self, event):
        todo_data = event['todo_data']
        action = event['action']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'todo',
            'action': action,
            'todo': todo_data,
        }))

    @database_sync_to_async
    def create_todo(self, todo_data):
        user = User.objects.get(id=self.user.id)
        todo = Todo.objects.create(
            title=todo_data.get('title', ''),
            description=todo_data.get('description', ''),
            priority=todo_data.get('priority', 'medium'),
            user=user
        )
        return todo

    @database_sync_to_async
    def update_todo(self, todo_id, todo_data):
        try:
            todo = Todo.objects.get(id=todo_id, user=self.user)
            for attr, value in todo_data.items():
                setattr(todo, attr, value)
            todo.save()
            return todo
        except Todo.DoesNotExist:
            return None

    @database_sync_to_async
    def delete_todo(self, todo_id):
        try:
            todo = Todo.objects.get(id=todo_id, user=self.user)
            todo.delete()
            return True
        except Todo.DoesNotExist:
            return False