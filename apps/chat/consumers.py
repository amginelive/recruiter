from django.db.models import ObjectDoesNotExist, Q
from channels.generic.websockets import JsonWebsocketConsumer
from django.contrib.auth import get_user_model

from .models import Conversation, Message

User = get_user_model()


class ChatServer(JsonWebsocketConsumer):
    http_user = True

    def connection_groups(self, **kwargs):
        return [str(self.message.user.id)]

    def connect(self, message, **kwargs):
        self.send({'accept': True})

    def receive(self, content, **kwargs):
        if content['type'] == 'initChat':
            self.cmd_init(content['payload'])
        elif content['type'] == 'newMessage':
            self.cmd_message(content['payload'])

    def cmd_init(self, payload):
        conversation = Conversation.objects.distinct().filter(
            users=User.objects.get(id=payload['user_id'])).filter(
            users=self.message.user).first()
        if not conversation:
            conversation = Conversation.objects.create()
            conversation.users.add(User.objects.get(id=payload['user_id']),
                             self.message.user)
            conversation.save()
        self.message.channel_session['conversation_id'] = conversation.id

        query = Message.objects.filter(conversation=conversation)\
            .order_by('created_at')
        messages = []
        for message in query:
            messages.append(  # TODO: Refactor message creation
                {'user': {'name': message.author.email,
                          'id': message.author.id},
                 'conversation_id': message.conversation.id,
                 'text': message.text,
                 'time': message.created_at.isoformat()}
            )
        self.send({'type': 'initChat', 'payload': messages})

    def cmd_message(self, payload):
        try:
            conversation = Conversation.objects.get(id=self.message.channel_session.get('conversation_id'))
        except ObjectDoesNotExist:
            return

        message = Message.objects.create(text=payload,
                                         author=self.message.user,
                                         conversation=conversation)
        response = {'type': 'newMessage',
                    'payload': {'user': {'name': message.author.email,
                                         'id': message.author.id},
                                'conversation_id': message.conversation.id,
                                'text': message.text,
                                'time': message.created_at.isoformat()}}
        for user in conversation.users.all():
            self.group_send(str(user.id), response)

    def disconnect(self, message, **kwargs):
        pass
