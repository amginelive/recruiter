from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.models import AbstractTimeStampedModel


class Message(AbstractTimeStampedModel):
    text = models.TextField(_('Message text'))
    author = models.ForeignKey('users.User',
                               verbose_name=_('Message author'),)
    conversation = models.ForeignKey('Conversation', on_delete=models.CASCADE,
                                     verbose_name=_('Conversation'))


class Conversation(AbstractTimeStampedModel):
    users = models.ManyToManyField('users.User',
                                   verbose_name=_('Conversation participants'),
                                   related_name='+')
