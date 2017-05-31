from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from core.models import AbstractTimeStampedModel


class Message(AbstractTimeStampedModel):
    text = models.CharField(_('Message text'), max_length=1024)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               verbose_name=_('Message author'),)
    conversation = models.ForeignKey('Conversation', on_delete=models.CASCADE,
                                     verbose_name=_('Conversation'))


class Conversation(AbstractTimeStampedModel):
    users = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                   verbose_name=_('Conversation participants'),
                                   through='Participant',
                                   related_name='+')


class Participant(AbstractTimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             verbose_name=_('Conversation participant'))
    conversation = models.ForeignKey('Conversation',
                                     on_delete=models.CASCADE,
                                     verbose_name=_('Conversation'))
