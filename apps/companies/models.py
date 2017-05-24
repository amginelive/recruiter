import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_save
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from django_countries.fields import CountryField

from core.models import AbstractTimeStampedModel
from core.utils import get_upload_path
from libs.tools import random_string_gen


optional = {
    'blank': True,
    'null': True,
}


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

    owner = models.ForeignKey('users.User', on_delete=models.SET_NULL, verbose_name=_('Major company representative'), **optional)
    name = models.CharField(max_length=200, verbose_name=_('Company name'))
    domain = models.CharField(
        _('Domain name'),
        max_length=200,
        unique=True,
        help_text='If your email is john@squareballoon.com, your domain name will be squareballon.com.'
    )
    overview = models.CharField(_('Overview'), max_length=255, **optional)
    alias = models.SlugField(_('Alias/Slug'), max_length=120)
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

    index_together = [
        ['alias', 'status'],
        ['name', 'status'],
    ]

    class Meta:
        verbose_name = _('Company')
        verbose_name_plural = _('Companies')

    def get_absolute_url(self):
        return '/company/%s' % self.id

    def __str__(self):
        return '%s' % (self.name)

    def clean(self):
        if not self.pk:
            # user is allowed to have only 1 company
            if Company.objects.filter(owner=self.owner).exists():
                raise ValidationError({'user': ['User is allowed to have only one company.']})
            super(Company, self).clean()


class CompanyInvitation(AbstractTimeStampedModel):
    """
    Model for Company Invitation.
    """
    sent_by = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='+', verbose_name=_('Sent By'), **optional)
    sent_to = models.EmailField(_('Email of recipient'))
    sent_to_user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='+', verbose_name=_('Sent To'), **optional)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='+', verbose_name=_('Company'))
    invite_key = models.CharField(_('Invitation key'), max_length=30, unique=True)

    class Meta:
        verbose_name = _('Company Invitation')
        verbose_name_plural = _('Company Invitations')

    def __str__(self):
        return '%s %s' % (self.sent_by, self.sent_to)

    def save(self, *args, **kwargs):

        if not self.pk:
            # create unique key
            self.invite_key = random_string_gen(12, 18)
            while CompanyInvitation.objects.filter(invite_key=self.invite_key).exists():
                self.invite_key = random_string_gen(12, 18)

        super(CompanyInvitation, self).save(*args, **kwargs)


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


def post_save_invitation(sender, instance, created, **kwargs):
    """
    Signal for sending an email invitation.
    """
    if created and instance.sent_to:
        msg_plain = render_to_string(
            'companies/email/company_invitation.txt',
            {
                'sender_name': instance.sent_by.get_full_name,
                'invite_key': instance.invite_key,
                'company': instance.sent_by.agent.company.name
            }
        )
        msg_html = render_to_string(
            'companies/email/company_invitation.html',
            {
                'sender_name': instance.sent_by.get_full_name,
                'invite_key': instance.invite_key,
                'company': instance.sent_by.agent.company.name
            }
        )
        send_mail(
            _('Recruiter Invitation, SquareBalloon'),
            msg_plain,
            settings.NOREPLY_EMAIL,
            [instance.sent_to,],
            html_message=msg_html,
            fail_silently=False
        )
        del msg_plain
        del msg_html

post_save.connect(post_save_invitation, sender=CompanyInvitation)
