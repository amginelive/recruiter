from django.contrib.auth import get_user_model
from django.db.models import ObjectDoesNotExist

from channels.generic.websockets import JsonWebsocketConsumer

from .models import Conversation, Message

User = get_user_model()


class ChatServer(JsonWebsocketConsumer):
    http_user = True

    def connection_groups(self, **kwargs):
        return [str(self.message.user.id)]

    def connect(self, message, **kwargs):
        self.send({'accept': True})
        user_list = User.objects.exclude(id=self.message.user.id)
        self.message.channel_session['user_list'] = user_list
        response = [{'id': user.id,
                     'name': user.email,
                     'online': user.online()}
                    for user in user_list]
        self.send({'type': 'initUsers', 'payload': response})
        if len(response) > 0:
            self.cmd_init({'user_id': response[0].get('id')})

    def receive(self, content, **kwargs):
        if content.get('type') == 'initChat':
            self.cmd_init(content.get('payload'))
        elif content.get('type') == 'newMessage':
            self.cmd_message(content.get('payload'))
        elif content.get('type') == 'userTyping':
            self.cmd_typing()
        elif content.get('type') == 'userPresence':
            self.cmd_presence()

    def cmd_init(self, payload):
        conversation = Conversation.objects\
            .distinct()\
            .filter(users__id=payload.get('user_id'))\
            .filter(users=self.message.user)\
            .first()
        if not conversation:
            conversation = Conversation.objects.create()
            conversation.users.add(User.objects.get(id=payload.get('user_id')),
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
        self.send({'type': 'initChat',
                   'payload': {'conversation_id': conversation.id,
                               'messages': messages}})

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

    def cmd_typing(self):
        try:
            conversation = Conversation.objects.get(id=self.message.channel_session.get('conversation_id'))
        except ObjectDoesNotExist:
            return

        response = {'type': 'userTyping',
                    'payload': {'name': self.message.user.email,
                                'id': self.message.user.id,
                                'conversation_id': conversation.id}}
        for user in conversation.users.exclude(id=self.message.user.id):
            self.group_send(str(user.id), response)

    def cmd_presence(self):
        # It is tied to the order of users sent in connect
        user_list = self.message.channel_session['user_list']
        response = {'type': 'userPresence',
                    'payload': [{'online': user.online()} for user in user_list]}
        return self.send(response)

    def disconnect(self, message, **kwargs):
        pass
