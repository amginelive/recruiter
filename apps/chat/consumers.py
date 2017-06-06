from django.contrib.auth import get_user_model
from django.db.models import ObjectDoesNotExist, Q

from channels.generic.websockets import JsonWebsocketConsumer

from recruit.models import Connection
from .models import Conversation, Message
from .utils import update_user_presence

User = get_user_model()


class ChatServer(JsonWebsocketConsumer):
    http_user = True

    message_list_limit = 10

    def connection_groups(self, **kwargs):
        return [str(self.message.user.id)]

    def connect(self, message, **kwargs):
        self.send({'accept': True})

        connections = Connection.objects\
            .filter(Q(connecter_id=message.user.id) |
                    Q(connectee_id=message.user.id))\
            .filter(connection_type__in=(
                Connection.CONNECTION_CANDIDATE_TO_AGENT_NETWORK,
                Connection.CONNECTION_AGENT_TO_AGENT_NETWORK if
                    self.message.user.account_type == User.ACCOUNT_AGENT else
                    Connection.CONNECTION_CANDIDATE_TO_CANDIDATE_TEAM_MEMBER))
        user_list = [
            next(filter(lambda user: user != self.message.user,
                        connection.users))
            for connection in connections
        ]
        self.message.channel_session['user_list'] = user_list

        response = {
            'agents': [{'id': user.id,
                        'name': user.email,
                        'photo': user.get_photo_url(),
                        'online': user.online()}
                       for user in user_list if
                       user.account_type == User.ACCOUNT_AGENT],
            'candidates': [{'id': user.id,
                            'name': user.email,
                            'photo': user.get_photo_url(),
                            'online': user.online()}
                           for user in user_list if
                           user.account_type == User.ACCOUNT_CANDIDATE]
        }
        self.send({'type': 'initUsers', 'payload': response})
        #if len(response) > 0:
        #    self.cmd_init({'user_id': response[0].get('id')})

    def receive(self, content, **kwargs):
        update_user_presence(self.message.user)
        if content.get('type') == 'initChat':
            self.cmd_init(content.get('payload'))
        elif content.get('type') == 'newMessage':
            self.cmd_message(content.get('payload'))
        elif content.get('type') == 'userTyping':
            self.cmd_typing()
        elif content.get('type') == 'userPresence':
            self.cmd_presence()
        elif content.get('type') == 'moreMessages':
            self.cmd_more_messages(content.get('payload'))

    def cmd_init(self, payload):
        conversation = Conversation.objects\
            .filter(users__id=payload.get('user_id'))\
            .filter(users=self.message.user)\
            .first()
        if not conversation:
            conversation = Conversation.objects.create()
            conversation.users.add(User.objects.get(id=payload.get('user_id')),
                             self.message.user)
            conversation.save()
        self.message.channel_session['conversation'] = conversation

        query = Message.objects.filter(conversation=conversation)\
            .order_by('-created_at')[:self.message_list_limit]
        messages = []
        more = conversation.message_set.count() > self.message_list_limit
        for message in reversed(query):
            messages.append(  # TODO: Refactor message creation
                {'user': {'name': message.author.email,
                          'photo': message.author.get_photo_url(),
                          'id': message.author.id},
                 'conversation_id': message.conversation.id,
                 'text': message.text,
                 'id': message.id,
                 'time': message.created_at.isoformat()}
            )
        self.send({'type': 'initChat',
                   'payload': {'conversation_id': conversation.id,
                               'more': more,
                               'messages': messages}})

    def cmd_message(self, payload):
        conversation = self.message.channel_session.get('conversation')

        message = Message.objects.create(text=payload,
                                         author=self.message.user,
                                         conversation=conversation)
        response = {'type': 'newMessage',
                    'payload': {'user': {'name': message.author.email,
                                         'photo': message.author.get_photo_url(),
                                         'id': message.author.id},
                                'conversation_id': message.conversation.id,
                                'text': message.text,
                                'id': message.id,
                                'time': message.created_at.isoformat()}}
        for user in conversation.users.all():
            self.group_send(str(user.id), response)

    def cmd_typing(self):
        conversation = self.message.channel_session.get('conversation')

        response = {'type': 'userTyping',
                    'payload': {'name': self.message.user.email,
                                'id': self.message.user.id,
                                'conversation_id': conversation.id}}
        for user in conversation.users.exclude(id=self.message.user.id):
            self.group_send(str(user.id), response)

    def cmd_presence(self):
        # It is tied to the order of users sent in connect
        user_list = self.message.channel_session['user_list']
        response = {
            'type': 'userPresence',
            'payload': {
                'agents': [{'online': user.online()} for user in user_list
                           if user.account_type == User.ACCOUNT_AGENT],
                'candidates': [{'online': user.online()} for user in user_list
                               if user.account_type == User.ACCOUNT_CANDIDATE]
            }
        }
        return self.send(response)

    def cmd_more_messages(self, payload):
        conversation = self.message.channel_session.get('conversation')

        from_time = conversation.message_set\
            .get(id=payload.get('message_id'))\
            .created_at
        query = conversation.message_set\
            .filter(created_at__lt=from_time)\
            .order_by('-created_at')

        message_list = [
            {
                'user': {'name': message.author.email,
                         'photo': message.author.get_photo_url(),
                         'id': message.author.id},
                'conversation_id': message.conversation.id,
                'text': message.text,
                'id': message.id,
                'time': message.created_at.isoformat()
            }
            for message in reversed(query[:self.message_list_limit])
        ]
        more = query.count() > self.message_list_limit
        response = {
            'type': 'moreMessages',
            'payload': {
                'more': more,
                'conversation_id': conversation.id,
                'messages': message_list
            }
        }
        self.send(response)

    def disconnect(self, message, **kwargs):
        pass
