from django.contrib.auth import get_user_model
from django.db.models import ObjectDoesNotExist, Q

from channels.generic.websockets import JsonWebsocketConsumer

from recruit.models import Connection
from .models import Conversation, Message, Participant
from .utils import update_user_idle, update_user_presence

User = get_user_model()


class ChatServer(JsonWebsocketConsumer):
    http_user = True

    message_list_limit = 10

    def connection_groups(self, **kwargs):
        return [str(self.message.user.id)]

    def connect(self, message, **kwargs):
        if message.user.is_authenticated():
            self.send({'accept': True})
        else:
            self.send({'accept': False})
            return

        connections = Connection.objects\
            .filter(Q(connecter=message.user) |
                    Q(connectee=message.user))\
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

        def create_user_data_dict(user):
            conversation = self._get_or_create_conversation(user)
            last_read_message = self.message.user.participations.get(
                conversation=conversation).last_read_message
            unread = conversation.messages\
                .filter(created_at__gt=last_read_message.created_at)\
                .count() if last_read_message\
                else conversation.messages.all().count()
            return {
                'name': user.email,
                'photo': user.get_photo_url(),
                'online': user.online(),
                'unread': unread
            }

        response = {
            'agents': {},
            'candidates': {}
        }
        for user in user_list:
            if user.account_type == User.ACCOUNT_AGENT:
                response['agents'][str(user.id)] = create_user_data_dict(user)
            if user.account_type == User.ACCOUNT_CANDIDATE:
                response['candidates'][str(user.id)] = create_user_data_dict(user)
        self.send({'type': 'initUsers', 'payload': response})
        #if len(response) > 0:
        #    self.cmd_init({'user_id': response[0].get('id')})

    def _get_or_create_conversation(self, user):
        conversation = Conversation.objects \
            .filter(users=user) \
            .filter(users=self.message.user) \
            .first()
        if not conversation:
            conversation = Conversation.objects.create()
            participant_connecter = Participant.objects.create(
                user=self.message.user,
                conversation=conversation
            )
            participant_connectee = Participant.objects.create(
                user=user,
                conversation=conversation
            )
            conversation.save()
        return conversation

    @staticmethod
    def _create_message_data_dict(message):
        return {
            'user': {
                'name': message.author.email,
                'photo': message.author.get_photo_url(),
                'id': message.author.id
            },
            'conversation_id': message.conversation.id,
            'text': message.text,
            'id': message.id,
            'time': message.created_at.isoformat()
        }

    def receive(self, content, **kwargs):
        if content.get('type') not in ['userIdle', 'userPresence']:
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
        elif content.get('type') == 'userIdle':
            self.cmd_idle(True)
        elif content.get('type') == 'userActive':
            self.cmd_idle(False)
        elif content.get('type') == 'readMessage':
            self.cmd_read_message(content.get('payload'))

    def cmd_init(self, payload):
        conversation = self._get_or_create_conversation(payload.get('user_id'))
        self.message.channel_session['conversation'] = conversation

        query = Message.objects.filter(conversation=conversation)\
            .order_by('-created_at')[:self.message_list_limit]
        messages = []
        more = conversation.messages.count() > self.message_list_limit
        for message in reversed(query):
            messages.append(self._create_message_data_dict(message))
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
                    'payload': self._create_message_data_dict(message)}
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
        user_list = self.message.channel_session['user_list']
        response = {
            'type': 'userPresence',
            'payload': {
                'agents': {
                    str(user.id): {'online': user.online()}
                    for user in user_list
                    if user.account_type == User.ACCOUNT_AGENT
                },
                'candidates': {
                    str(user.id): {'online': user.online()}
                    for user in user_list
                    if user.account_type == User.ACCOUNT_CANDIDATE
                }
            }
        }
        return self.send(response)

    def cmd_more_messages(self, payload):
        conversation = self.message.channel_session.get('conversation')

        from_time = conversation.messages\
            .get(id=payload.get('message_id'))\
            .created_at
        query = conversation.messages\
            .filter(created_at__lt=from_time)\
            .order_by('-created_at')

        message_list = [
            self._create_message_data_dict(message)
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

    def cmd_idle(self, idle):
        update_user_idle(self.message.user, idle)

    def cmd_read_message(self, payload):
        conversation = self.message.channel_session.get('conversation')

        participant = conversation.participants.get(user=self.message.user)
        participant.last_read_message = Message.objects.get(id=payload)
        participant.save()

    def disconnect(self, message, **kwargs):
        if not message.user.is_authenticated():
            return
        self.cmd_idle(False)
