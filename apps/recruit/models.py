import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _


from core.models import AbstractTimeStampedModel, optional
from django_countries.fields import CountryField


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
    applications = models.ManyToManyField(
        'users.Candidate',
        related_name='applications',
        through='JobApplication',
        verbose_name=_('Application')
    )

    class Meta:
        verbose_name = _('Job Post')
        verbose_name_plural = _('Job Posts')

    def __str__(self):
        return self.title

    @property
    def applicants(self):
        return [job_application.candidate for job_application in self.candidate_applications.all()]

    @property
    def new_applications(self):
        return self.candidate_applications.filter(is_viewed=False)


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
    CONNECTION_CANDIDATE_TO_CANDIDATE_NETWORK = 1
    CONNECTION_CANDIDATE_TO_CANDIDATE_TEAM_MEMBER = 2
    CONNECTION_CANDIDATE_TO_AGENT_NETWORK = 3
    CONNECTION_AGENT_TO_AGENT_NETWORK = 4
    CONNECTION_TYPE_CHOICES = (
        (CONNECTION_CANDIDATE_TO_CANDIDATE_NETWORK, _('Candidate to Candidate Network')),
        (CONNECTION_CANDIDATE_TO_CANDIDATE_TEAM_MEMBER, _('Candidate to Candidate Team Member')),
        (CONNECTION_CANDIDATE_TO_AGENT_NETWORK, _('Candidate to Agent Network')),
        (CONNECTION_AGENT_TO_AGENT_NETWORK, _('Agent to Agent Network')),
    )

    connecter = models.ForeignKey('users.User', related_name='+', verbose_name=_('Connecter'))
    connectee = models.ForeignKey('users.User', related_name='+', verbose_name=_('Connectee'))
    connection_type = models.IntegerField(_('Connection Type'), choices=CONNECTION_TYPE_CHOICES)

    class Meta:
        verbose_name = _('Connection')
        verbose_name_plural = _('Connections')

    def __str__(self):
        return self.connectee.get_full_name()

    @property
    def users(self):
        return [self.connecter, self.connectee]


class ConnectionRequest(AbstractTimeStampedModel):
    """
    Model for requesting to be added to network or team.
    """
    CONNECTION_CANDIDATE_TO_CANDIDATE_NETWORK = 1
    CONNECTION_CANDIDATE_TO_CANDIDATE_TEAM_MEMBER = 2
    CONNECTION_CANDIDATE_TO_AGENT_NETWORK = 3
    CONNECTION_AGENT_TO_AGENT_NETWORK = 4
    CONNECTION_TYPE_CHOICES = (
        (CONNECTION_CANDIDATE_TO_CANDIDATE_NETWORK, _('Candidate to Candidate Network')),
        (CONNECTION_CANDIDATE_TO_CANDIDATE_TEAM_MEMBER, _('Candidate to Candidate Team Member')),
        (CONNECTION_CANDIDATE_TO_AGENT_NETWORK, _('Candidate to Agent Network')),
        (CONNECTION_AGENT_TO_AGENT_NETWORK, _('Agent to Agent Network')),
    )

    connecter = models.ForeignKey('users.User', related_name='connecter_requests', verbose_name=_('Connecter'))
    connectee = models.ForeignKey('users.User', related_name='connectee_requests', verbose_name=_('Connectee'))
    connection_type = models.IntegerField(_('Connection Type'), choices=CONNECTION_TYPE_CHOICES)
    uuid = models.SlugField(_('UUID'), default=uuid.uuid4, editable=False)

    class Meta:
        verbose_name = _('Connection Request')
        verbose_name_plural = _('Connection Requests')

    def __str__(self):
        return str(self.uuid)


class ConnectionInvite(AbstractTimeStampedModel):
    """
    Model for inviting to join the site and be in their network or team.
    """
    CONNECTION_CANDIDATE_TO_CANDIDATE_NETWORK = 1
    CONNECTION_CANDIDATE_TO_CANDIDATE_TEAM_MEMBER = 2
    CONNECTION_CANDIDATE_TO_AGENT_NETWORK = 3
    CONNECTION_AGENT_TO_AGENT_NETWORK = 4
    CONNECTION_TYPE_CHOICES = (
        (CONNECTION_CANDIDATE_TO_CANDIDATE_NETWORK, _('Candidate to Candidate Network')),
        (CONNECTION_CANDIDATE_TO_CANDIDATE_TEAM_MEMBER, _('Candidate to Candidate Team Member')),
        (CONNECTION_CANDIDATE_TO_AGENT_NETWORK, _('Candidate to Agent Network')),
        (CONNECTION_AGENT_TO_AGENT_NETWORK, _('Agent to Agent Network')),
    )

    connecter = models.ForeignKey('users.User', related_name='+', verbose_name=_('Connecter'))
    connectee_email = models.EmailField(_('Connectee'), max_length=255)
    connection_type = models.IntegerField(_('Connection Type'), choices=CONNECTION_TYPE_CHOICES)
    uuid = models.SlugField(_('UUID'), default=uuid.uuid4, editable=False)

    class Meta:
        verbose_name = _('Connection Invitation')
        verbose_name_plural = _('Connection Invitations')

    def __str__(self):
        return str(self.uuid)


class JobReferral(AbstractTimeStampedModel):
    """
    Model for referring a job post.
    """
    job_post = models.ForeignKey('recruit.JobPost', related_name='+', verbose_name=_('Job Post'))
    referred_by = models.ForeignKey('users.Candidate', related_name='+', verbose_name=_('Referred By'))
    referred_to = models.ForeignKey('users.Candidate', related_name='+', verbose_name=_('Referred To'))

    class Meta:
        verbose_name = _('Job Referral')
        verbose_name_plural = _('Job Referrals')

    def __str__(self):
        return self.job_post.title


class UserReferral(AbstractTimeStampedModel):
    """
    Model for referring a user to another user.
    """
    referred_by = models.ForeignKey('users.User', related_name='+', verbose_name=_('Referred By'))
    referred_to = models.ForeignKey('users.User', related_name='+', verbose_name=_('Referred To'))
    referred_user = models.ForeignKey('users.User', related_name='+', verbose_name=_('Referred User'))

    class Meta:
        verbose_name = _('User Referral')
        verbose_name_plural = _('User Referrals')

    def __str__(self):
        return self.referred_to.get_full_name()


class JobApplication(AbstractTimeStampedModel):
    """
    Model for Job Application.
    """
    job_post = models.ForeignKey('recruit.JobPost', related_name='candidate_applications', verbose_name=_('Job Post'))
    candidate = models.ForeignKey('users.Candidate', related_name='job_applications', verbose_name=_('Candidate'))
    is_viewed = models.BooleanField(_('Is Viewed?'), default=False)

    class Meta:
        verbose_name = _('Job Application')
        verbose_name_plural = _('Job Applications')

    def __str__(self):
        return self.candidate.user.get_full_name()
