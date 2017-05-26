import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _


from core.models import AbstractTimeStampedModel
from django_countries.fields import CountryField


optional = {
    'blank': True,
    'null': True,
}


class JobPost(AbstractTimeStampedModel):
    """
    Model for Job Post.
    """
    posted_by = models.ForeignKey(
        'users.Agent',
        on_delete=models.SET_NULL,
        related_name='job_posts',
        verbose_name=('Posted By'),
        **optional
    )
    title = models.CharField(_('Title'), max_length=255)
    description = models.TextField(_('Description'))
    contract = models.TextField(_('Contract'))
    city = models.CharField(_('City'), max_length=80)
    country = CountryField(_('Country'))
    skills = models.ManyToManyField(
        'recruit.Skill',
        related_name='job_posts',
        verbose_name=_('Skills')
    )
    uuid = models.SlugField(_('UUID'), default=uuid.uuid4, editable=False)

    class Meta:
        verbose_name = _('Job Post')
        verbose_name_plural = _('Job Posts')

    def __str__(self):
        return self.title


class Skill(AbstractTimeStampedModel):
    """
    Model for Skill.
    """
    name = models.CharField(_('Name'), max_length=100)

    class Meta:
        verbose_name = _('Skill')
        verbose_name_plural = _('Skills')

    def __str__(self):
        return self.name


class Connection(AbstractTimeStampedModel):
    """
    Model for requesting to be added to network or team.
    """
    CONNECTION_NETWORK = 1
    CONNECTION_TEAM_MEMBER = 2
    CONNECTION_TYPE_CHOICES = (
        (CONNECTION_NETWORK, _('Network')),
        (CONNECTION_TEAM_MEMBER, _('Team Member')),
    )
    connecter = models.ForeignKey('users.Candidate', related_name='+', verbose_name=_('Connecter'))
    connectee = models.ForeignKey('users.Candidate', related_name='+', verbose_name=_('Connectee'))
    connection_type = models.IntegerField(_('Connection Type'), choices=CONNECTION_TYPE_CHOICES)

    class Meta:
        verbose_name = _('Connection')
        verbose_name_plural = _('Connections')

    def __str__(self):
        return self.connecter.user.get_full_name()



class ConnectionRequest(AbstractTimeStampedModel):
    """
    Model for requesting to be added to network or team.
    """
    CONNECTION_NETWORK = 1
    CONNECTION_TEAM_MEMBER = 2
    CONNECTION_TYPE_CHOICES = (
        (CONNECTION_NETWORK, _('Network')),
        (CONNECTION_TEAM_MEMBER, _('Team Member')),
    )
    connecter = models.ForeignKey('users.Candidate', related_name='connecter_requests', verbose_name=_('Requested By'))
    connectee = models.ForeignKey('users.Candidate', related_name='connectee_requests', verbose_name=_('Request Recipient'))
    connection_type = models.IntegerField(_('Connection Type'), choices=CONNECTION_TYPE_CHOICES)
    uuid = models.SlugField(_('UUID'), default=uuid.uuid4, editable=False)

    class Meta:
        verbose_name = _('Connection Request')
        verbose_name_plural = _('Connection Requests')

    def __str__(self):
        return self.uuid
