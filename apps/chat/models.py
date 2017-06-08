from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.models import AbstractTimeStampedModel


class Message(AbstractTimeStampedModel):
    """
    Model for message.
    """
    text = models.TextField(_('Message text'))
    author = models.ForeignKey(
        'users.User',
        related_name='messages',
        verbose_name=_('Message author')
    )
    conversation = models.ForeignKey(
        'chat.Conversation',
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('Conversation')
    )

    class Meta:
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')

    def __str__(self):
        return self.author.get_full_name()


class Conversation(AbstractTimeStampedModel):
    """
    Model for conversation.
    """
    users = models.ManyToManyField(
        'users.User',
        related_name='conversations',
        verbose_name=_('Conversation participants')
    )

    users_new = models.ManyToManyField(
        'users.User',
        through='chat.Participant',
        related_name='conversations_new',
        verbose_name=_('Conversation participants')
    )

    class Meta:
        verbose_name = _('Conversation')
        verbose_name_plural = _('Conversations')

    def __str__(self):
        return ', '.join([user.get_full_name() for user in self.users.all()])


class Participant(AbstractTimeStampedModel):
    last_read_message = models.ForeignKey(
        'chat.Message',
        null=True,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Last read message'
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='participations',
        verbose_name='User'
    )
    conversation = models.ForeignKey(
        'chat.Conversation',
        on_delete=models.CASCADE,
        related_name='participants',
        verbose_name='Conversation'
    )

    class Meta:
        verbose_name = _('Participant')
        verbose_name_plural = _('Participants')
        unique_together = [
            ['user', 'conversation']
        ]

    def __str__(self):
        return self.user.get_full_name()
