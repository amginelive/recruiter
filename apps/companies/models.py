import itertools
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from django_countries.fields import CountryField

from core.models import AbstractTimeStampedModel, optional
from core.utils import get_upload_path


class Company(AbstractTimeStampedModel):
    """
    Model for Company.
    """
    STATUS_ACTIVE = 0
    STATUS_INACTIVE = 1

    STATUS_CHOICES = (
        (STATUS_ACTIVE, 'Active'),
        (STATUS_INACTIVE, 'Inactive'),
    )

    owner = models.ForeignKey('users.Agent', on_delete=models.SET_NULL, related_name='companies_owned',verbose_name=_('Major company representative'), **optional)
    name = models.CharField(max_length=200, verbose_name=_('Company name'))
    domain = models.CharField(
        _('Domain name'),
        max_length=200,
        unique=True,
        help_text='If your email is john@squareballoon.com, your domain name will be squareballon.com.'
    )
    overview = models.CharField(_('Overview'), max_length=255, **optional)
    slug = models.SlugField(_('Slug'), max_length=120)
    description = models.TextField(_('Description'), **optional)
    logo = models.ImageField(
        _('Logo'),
        upload_to=get_upload_path,
        **optional
    )
    address_1 = models.CharField(_('Address line 1'), max_length=80, **optional)
    address_2 = models.CharField(_('Address line 2'), max_length=80, **optional)
    zip = models.CharField(_('Postal code / ZIP'), max_length=10, **optional)
    city = models.CharField(_('City'), max_length=80)
    country = CountryField(_('Country'))
    website = models.URLField(_('Website'), **optional)
    is_charity = models.BooleanField(_('Is it a charity organization?'), default=False)
    allow_auto_invite = models.BooleanField(_('Allow auto invite?'), default=False)
    status = models.IntegerField(_('Status'), choices=STATUS_CHOICES, default=STATUS_ACTIVE)

    class Meta:
        verbose_name = _('Company')
        verbose_name_plural = _('Companies')

    def get_absolute_url(self):
        return '/company/%s' % self.id

    @property
    def location(self):
        if self.city and self.country:
            return '{}, {}'.format(self.city, self.country.name)
        return None

    def __str__(self):
        return self.name

    def clean(self):
        if not self.pk:
            # user is allowed to have only 1 company
            if Company.objects.filter(owner=self.owner).exists():
                raise ValidationError({'user': ['User is allowed to have only one company.']})
            super(Company, self).clean()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = slug_copy = slugify(self.name)
            for i in itertools.count(1):
                if not Company.objects.filter(slug=self.slug).exists():
                    break
                self.slug = '{}-{}'.format(slug_copy, i)

        return super(Company, self).save(*args, **kwargs)


class CompanyInvitation(AbstractTimeStampedModel):
    """
    Model for Company Invitation.
    """
    inviter = models.ForeignKey('users.Agent', related_name='+', verbose_name=_('Inviter'))
    invitee_email = models.EmailField(_('Invitee Email'))
    uuid = models.UUIDField(_('Request Invitation key'), default=uuid.uuid4, editable=False)

    class Meta:
        verbose_name = _('Company Invitation')
        verbose_name_plural = _('Company Invitations')

    def __str__(self):
        return str(self.uuid)


class CompanyRequestInvitation(AbstractTimeStampedModel):
    """
    Model for Company Request Invitations.
    """
    user = models.ForeignKey('users.User', related_name='invitation_request', verbose_name=('User'))
    company = models.ForeignKey('companies.Company', related_name='invitation_request', verbose_name=('Company'))
    uuid = models.UUIDField(_('Request Invitation key'), default=uuid.uuid4, editable=False)

    class Meta:
        verbose_name = _('Company Request Invitation')
        verbose_name_plural = _('Company Request Invitations')

    def __str__(self):
        return self.user.get_full_name()
