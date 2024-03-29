from datetime import datetime

from django.contrib.auth import get_user_model
from django.db.models import Q, ObjectDoesNotExist
from django.core.exceptions import ValidationError

from channels.generic.websockets import JsonWebsocketConsumer

from chat.models import Conversation, GroupInvite, Message, Participant
from chat.utils import update_user_idle, update_user_presence
from recruit.models import Connection

User = get_user_model()


class ChatServer(JsonWebsocketConsumer):
    http_user = True

    message_list_limit = 15

    def connection_groups(self, **kwargs):
        return [str(self.message.user.id)]

    def _create_group_chat_data_dict(self, group_chat, participant=None):
        if not participant:
            participant = group_chat.participants.get(user=self.message.user)
        last_read_message = participant.last_read_message
        if last_read_message:
            unread = group_chat.messages \
                .filter(created_at__gt=last_read_message.created_at) \
                .count()
        else:
            unread = group_chat.messages.all().count()
        # TODO: refactor code duplication.
        last_message = group_chat.messages \
            .all() \
            .order_by('created_at') \
            .last()
        if last_message:
            if participant.user == last_message.author:
                last_message_text = 'You: '
            else:
                last_message_text = f'{last_message.author.get_full_name()}: '
            last_message_text += last_message.text
            last_message_time = last_message.created_at.isoformat()
        else:
            last_message_text = ''
            last_message_time = datetime.fromtimestamp(0).isoformat()
        return {
            'users': {
                participant.user.id: {'status': participant.status}
                for participant
                in group_chat.participants.all()
            },
            'name': group_chat.name,
            'owner': group_chat.owner.id,
            'unread': unread,
            'last_message_time': last_message_time,
            'last_message_text': last_message_text
        }

    def _create_user_chat_data_dict(self, user):
        conversation = self._get_or_create_conversation(user)
        last_read_message = self.message.user.participations \
            .get(conversation=conversation) \
            .last_read_message
        if last_read_message:
            unread = conversation.messages \
                .exclude(Q(group_invite__isnull=False) &
                         Q(author=self.message.user)) \
                .filter(created_at__gt=last_read_message.created_at) \
                .count()
        else:
            unread = conversation.messages \
                .exclude(Q(group_invite__isnull=False) &
                         Q(author=self.message.user)) \
                .count()
        last_message = conversation.messages \
            .exclude(Q(group_invite__isnull=False) &
                     Q(author=self.message.user)) \
            .order_by('created_at') \
            .last()
        if last_message:
            if self.message.user == last_message.author:
                last_message_text = 'You: '
            else:
                last_message_text = f'{user.get_full_name()}: '
            last_message_text += last_message.text
            last_message_time = last_message.created_at.isoformat()
        else:
            last_message_text = ''
            last_message_time = datetime.fromtimestamp(0).isoformat()
        return (
            conversation.id,
            {
                'user': user.id,
                'name': user.get_full_name(),
                'unread': unread,
                'last_message_time': last_message_time,
                'last_message_text': last_message_text
            }
        )

    @staticmethod
    def _create_user_data_dict(user, include_email=True):
        response = {
            'name': user.get_full_name(),
            'photo': user.get_photo_url(),
            'online': user.online()
        }
        if include_email:
            response['email'] = user.email
        return response

    def connect(self, message, **kwargs):
        if message.user.is_authenticated():
            self.message.reply_channel.send({'accept': True})
        else:
            self.message.reply_channel.send({'close': True})
            return

        connections = Connection.objects.filter(Q(connecter=message.user) | Q(connectee=message.user))
        user_list = [
            next(filter(lambda user: user != self.message.user,
                        connection.users))
            for connection in connections
        ]
        self.message.channel_session['user_list'] = user_list
        group_participants = Participant.objects \
            .filter(conversation__conversation_type=Conversation.CONVERSATION_GROUP) \
            .filter(conversation__users=self.message.user) \
            .exclude(user=self.message.user)
        self.message.channel_session['extra'] = {
            participant.user
            for participant
            in group_participants
            if participant.user not in user_list
        }

        response = {
            'users': {
                'self': self.message.user.id,
                str(self.message.user.id): self._create_user_data_dict(self.message.user),
                'extra': {
                    user.id: self._create_user_data_dict(user)
                    for user
                    in self.message.channel_session.get('extra')
                }
            },
            'chats': {
                'activeChat': 0,
                'agents': {},
                'candidates': {},
                'groups': {}
            }
        }
        for user in user_list:
            account_type = f'{user.get_account_type_display().lower()}s'
            conversation_id, user_dict = self._create_user_chat_data_dict(user)
            response['chats'][account_type][str(conversation_id)] = user_dict
            response['users'][str(user.id)] = self._create_user_data_dict(user)
        group_chats = Conversation.objects \
            .filter(conversation_type=Conversation.CONVERSATION_GROUP) \
            .filter(participants__user=self.message.user,
                    participants__status=Participant.PARTICIPANT_ACCEPTED)
        for group_chat in group_chats:
            response['chats']['groups'][str(group_chat.id)] = self._create_group_chat_data_dict(group_chat)
        self.send({'type': 'init', 'payload': response})

        users_count = len(response.get('chats').get('agents')) \
            + len(response.get('chats').get('candidates'))
        if kwargs.get('mode') != 'bg' and users_count > 0:
            if kwargs.get('cid'):
                try:
                    init_conversation = self.message.user.participations \
                        .filter(status=Participant.PARTICIPANT_ACCEPTED) \
                        .get(conversation_id=int(kwargs.get('cid'))) \
                        .conversation
                    self.cmd_init(init_conversation.id)
                    return
                except ObjectDoesNotExist:
                    pass

            last_conversation = self.message.user.participations \
                .filter(status=Participant.PARTICIPANT_ACCEPTED) \
                .order_by('updated_at') \
                .last() \
                .conversation
            self.cmd_init(last_conversation.id)

    def _get_or_create_conversation(self, user):
        conversation = Conversation.objects \
            .filter(conversation_type=Conversation.CONVERSATION_USER) \
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

    def _create_message_data_dict(self, message):
        if message.group_invite:
            group_invite = {
                'type': 'group_invite',
                'status': message.group_invite.status,
                'conversation_id': message.group_invite.participant.conversation.id,
                'invite_id': message.group_invite.id
            }
        else:
            group_invite = None
        return {
            'user': {
                'id': message.author.id,
                'name': message.author.get_full_name()
            },
            'group_invite': group_invite,
            'conversation_id': message.conversation.id,
            'text': message.text,
            'id': message.id,
            'time': message.created_at.isoformat()
        }

    def receive(self, content, **kwargs):
        if content.get('type') not in ['userIdle', 'userPresence'] \
                or (content.get('type') == 'userIdle'
                    and not content.get('payload')):
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
            self.cmd_idle(content.get('payload'))
        elif content.get('type') == 'readMessage':
            self.cmd_read_message(content.get('payload'))
        elif content.get('type') == 'createGroup':
            self.cmd_create_group(content.get('payload'))
        elif content.get('type') == 'answerInvite':
            self.cmd_answer_invite(content.get('payload'))
        elif content.get('type') == 'leaveGroup':
            self.cmd_leave_group()
        elif content.get('type') == 'kickUser':
            self.cmd_kick_user(content.get('payload'))
        elif content.get('type') == 'inviteUsers':
            self.cmd_invite_users(content.get('payload'))

    def cmd_init(self, payload):
        if payload:
            conversation = self.message.user.participations.get(
                conversation_id=payload).conversation
        else:
            conversation = self.message.user.participations \
                .filter(status=Participant.PARTICIPANT_ACCEPTED) \
                .order_by('updated_at') \
                .last() \
                .conversation
        if not conversation:
            return
        self.message.channel_session['conversation'] = conversation
        query = Message.objects.filter(conversation=conversation) \
            .exclude(Q(group_invite__isnull=False) &
                     Q(author=self.message.user))
        messages = []
        more = query.count() > self.message_list_limit
        last_messages = query.order_by('-created_at')[:self.message_list_limit]
        for message in reversed(last_messages):
            messages.append(self._create_message_data_dict(message))
        self.send({'type': 'initChat',
                   'payload': {'conversation_id': conversation.id,
                               'more': more,
                               'messages': messages}})
        if len(messages) > 0:
            self.cmd_read_message(messages[-1]['id'])

    def cmd_message(self, payload, for_user=None, group_invite=None):
        if not for_user:
            conversation = self.message.channel_session.get('conversation')
        else:
            conversation = self._get_or_create_conversation(for_user)

        message = Message.objects.create(text=payload,
                                         author=self.message.user,
                                         conversation=conversation,
                                         group_invite=group_invite)
        response = {
            'type': 'newMessage',
            'payload': self._create_message_data_dict(message)
        }
        if not for_user:
            for participant in conversation.participants \
                    .filter(status=Participant.PARTICIPANT_ACCEPTED):
                self.group_send(str(participant.user.id), response)
        else:
            self.group_send(str(for_user.id), response)

    def cmd_typing(self):
        conversation = self.message.channel_session.get('conversation')

        response = {'type': 'userTyping',
                    'payload': {'name': self.message.user.get_full_name(),
                                'id': self.message.user.id,
                                'conversation_id': conversation.id}}
        for user in conversation.users.exclude(id=self.message.user.id):
            self.group_send(str(user.id), response)

    def cmd_presence(self):
        user_list = self.message.channel_session.get('user_list')
        extra = self.message.channel_session.get('extra')
        payload = {
            str(user.id): {'online': user.online()}
            for user in user_list
        }
        payload['extra'] = {
            user.id: self._create_user_data_dict(user)
            for user
            in extra
        }
        response = {
            'type': 'userPresence',
            'payload': payload
        }
        return self.send(response)

    def cmd_more_messages(self, payload):
        conversation = self.message.channel_session.get('conversation')

        from_time = conversation.messages \
            .get(id=payload.get('message_id')) \
            .created_at
        query = conversation.messages \
            .exclude(Q(group_invite__isnull=False) &
                     Q(author=self.message.user)) \
            .filter(created_at__lt=from_time) \
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
        # TODO: need some more checks here.
        participant.last_read_message = Message.objects.get(id=payload)
        participant.save()
        self.send({
            'type': 'readMessage',
            'payload': conversation.id
        })

    def _emit_group_chat_update(self, conversation):
        active_participants = conversation.participants.filter(
            status=Participant.PARTICIPANT_ACCEPTED)
        for participant in active_participants:
            chat_data = self._create_group_chat_data_dict(conversation,
                                                          participant)
            self.group_send(str(participant.user.id), {
                'type': 'chatsUpdate',
                'payload': {
                    'id': conversation.id,
                    'data': chat_data
                }
            })

    def _check_user_ids_in_network(self, user_ids):
        network_users_ids = [
            user.id
            for user
            in self.message.channel_session.get('user_list')
        ]
        return all([user_id in network_users_ids
                    for user_id
                    in user_ids])

    def cmd_create_group(self, payload):
        if not self._check_user_ids_in_network(payload.get('user_ids')):
            return

        chat_group = Conversation.objects.create(
            conversation_type=Conversation.CONVERSATION_GROUP,
            name=payload.get('name'),
            owner=self.message.user
        )
        Participant.objects.create(
            user=self.message.user,
            conversation=chat_group
        )
        for user_id in payload.get('user_ids'):
            participant = Participant.objects.create(
                user=User.objects.get(id=user_id),
                conversation=chat_group,
                status=Participant.PARTICIPANT_PENDING
            )
            GroupInvite.objects.create(
                participant=participant,
                text=payload.get('message')
            )

        try:
            chat_group.full_clean()
        except ValidationError:
            chat_group.delete()
            return

        chat_group.save()

        for user_id in payload.get('user_ids'):
            self.cmd_invite_to_group(user_id, group=chat_group)

        response = self._create_group_chat_data_dict(chat_group)
        response['id'] = chat_group.id
        response['extra'] = dict()
        self.send({
            'type': 'createGroup',
            'payload': response
        })
        self.cmd_init(chat_group.id)

    def cmd_invite_to_group(self, user_id, text=None, group=None):
        if not group:
            conversation = self.message.channel_session.get('conversation')
        else:
            conversation = group
        if (conversation.conversation_type != Conversation.CONVERSATION_GROUP
                or conversation.owner != self.message.user):
            return

        user = User.objects.get(id=user_id)
        participant = conversation.participants.get(user=user)
        if (user not in conversation.users.all() or
                participant.status != Participant.PARTICIPANT_PENDING):
            return

        if not text:  # Initial invitation on group creation
            invite = participant.invites.last()
        else:
            invite = GroupInvite.objects.create(
                participant=participant,
                text=text
            )

        self.cmd_message(invite.text, user, invite)

    def cmd_answer_invite(self, payload):
        participant = Participant.objects \
            .filter(conversation_id=payload.get('conversation_id')) \
            .get(user=self.message.user)

        if participant.status == Participant.PARTICIPANT_ACCEPTED:
            return

        current_conversation = self.message.channel_session.get('conversation')
        if payload.get('accept'):
            participant.status = Participant.PARTICIPANT_ACCEPTED
            for invite in participant.invites.filter(status=GroupInvite.INVITE_PENDING):
                invite.status = GroupInvite.INVITE_ACCEPTED
                invite.save()
            participant.save()
            response = self._create_group_chat_data_dict(participant.conversation)
            response['id'] = participant.conversation.id
            user_list = self.message.channel_session.get('user_list')
            extra_users = {
                participant.user
                for participant
                in participant.conversation.participants.exclude(
                    user=self.message.user)
                if participant.user not in user_list
            }
            response['extra'] = {
                user.id: self._create_user_data_dict(user, include_email=False)
                for user
                in extra_users
            }
            self.message.channel_session.get('extra').update(extra_users)
            self.group_send(
                str(self.message.user.id),
                {'type': 'createGroup', 'payload': response}
            )
            self.group_send(
                str(self.message.user.id),
                {
                    'type': 'answerInvite',
                    'payload': {
                        'accept': True,
                        'group_id': participant.conversation.id,
                        'conversation_id': current_conversation.id
                    }
                }
            )
            self.cmd_init(participant.conversation.id)
        else:
            invite = participant.invites.get(id=payload.get('invite_id'))
            invite.status = GroupInvite.INVITE_DECLINED
            invite.save()
            participant.status = Participant.PARTICIPANT_DECLINED
            participant.save()
            current_conversation.participants.get(user=self.message.user).save()
            self.group_send(
                str(self.message.user.id),
                {
                    'type': 'answerInvite',
                    'payload': {
                        'accept': False,
                        'group_id': participant.conversation.id,
                        'invite_id': invite.id,
                        'conversation_id': current_conversation.id
                    }
                }
            )
        self._emit_group_chat_update(participant.conversation)

    def cmd_leave_group(self):
        conversation = self.message.channel_session.get('conversation')
        participant = conversation.participants.get(user=self.message.user)
        if conversation.conversation_type != Conversation.CONVERSATION_GROUP \
                or participant.status != Participant.PARTICIPANT_ACCEPTED:
            return

        active_participants = conversation.participants.filter(
            status=Participant.PARTICIPANT_ACCEPTED)
        if conversation.owner == self.message.user \
                and active_participants.count() > 1:
            any_other_user = active_participants \
                .exclude(user=self.message.user) \
                .first() \
                .user
            conversation.owner = any_other_user
            try:
                conversation.full_clean()
            except ValidationError:
                return
            conversation.save()

        self.group_send(str(self.message.user.id), {
            'type': 'leaveGroup',
            'payload': conversation.id
        })

        if active_participants.count() == 1:
            pending_participants = conversation.participants.filter(
                status=Participant.PARTICIPANT_PENDING)
            for participant in pending_participants:
                self.group_send(str(participant.user.id), {
                    'type': 'kickUser',
                    'payload': conversation.id
                })
            conversation.delete()
        else:
            participant.delete()
            self._emit_group_chat_update(conversation)

    def cmd_kick_user(self, user_id):
        conversation = self.message.channel_session.get('conversation')
        participant = conversation.participants.get(user=self.message.user)
        if conversation.conversation_type != Conversation.CONVERSATION_GROUP \
                or conversation.owner != participant.user \
                or user_id == self.message.user.id:
            return

        target = conversation.participants.get(user_id=user_id)

        if target.status == Participant.PARTICIPANT_ACCEPTED:
            self.group_send(str(user_id), {
                'type': 'leaveGroup',
                'payload': conversation.id
            })
        elif target.status == Participant.PARTICIPANT_PENDING:
            self.group_send(str(user_id), {
                'type': 'kickUser',
                'payload': conversation.id
            })

        target.delete()
        self._emit_group_chat_update(conversation)

    def cmd_invite_users(self, payload):
        conversation = self.message.channel_session.get('conversation')
        if conversation.conversation_type != Conversation.CONVERSATION_GROUP \
                or conversation.owner != self.message.user \
                or not self._check_user_ids_in_network(payload.get('user_ids')):
            return

        for user_id in payload.get('user_ids'):
            try:
                participant = conversation.participants.get(user_id=user_id)
                if participant.status != participant.PARTICIPANT_DECLINED:
                    continue
            except ObjectDoesNotExist:
                Participant.objects.create(
                    user=User.objects.get(id=user_id),
                    conversation=conversation,
                    status=Participant.PARTICIPANT_PENDING
                )
            else:
                participant.status = Participant.PARTICIPANT_PENDING
                participant.save()
            self.cmd_invite_to_group(
                user_id,
                group=conversation,
                text=payload.get('message')
            )
        self._emit_group_chat_update(conversation)

    def disconnect(self, message, **kwargs):
        self.cmd_idle(False)
