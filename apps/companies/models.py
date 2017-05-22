import os
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_save
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from django_countries.fields import CountryField
from slugify import slugify_url

from core.models import AbstractTimeStampedModel
from libs.tools import resize_image, random_string_gen


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
        upload_to='images/company/logo/%Y',
        help_text=_('Logo size 600x200px, .jpg, .png, .gif formats'),
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

    # process company images
    def delete(self, *args, **kwargs):
        try:
            self.logo.delete()
        except ValueError:
            pass
        super(Company, self).delete(*args, **kwargs)

    # save existing values for later comparison (logo change)
    def __init__(self, *args, **kwargs):
        super(Company, self).__init__(*args, **kwargs)
        try:
            self.__initial_logo_file_path = self.logo.path
        except ValueError:
            self.__initial_logo_file_path = ''

    def logo_has_changed(self):
        if getattr(self, '_Company__initial_logo_file_path') !=  getattr(self, 'logo').path:
            return True
        return False

    def save(self, *args, **kwargs):
        # resize uploaded logo
        def generate_images(self):
            # content type name will be used as a reference for alias,
            # please make sure you don't have duplicates or overlaps.
            # format for config "{app_label}_{model}"
            content_name = "{}_{}".format('companies', self.__class__.__name__.lower())
            # TODO: make alias the same as content_type.model
            filename, file = resize_image(self.logo, settings.THUMBNAIL_ALIASES[content_name]['logo'])
            self.logo.save(filename, file, save=False)

        # remember original photo path to delete it later
        to_delete = []

        if not self.pk:
            # slugify company name
            # later add scope check to avoid duplicate aliases
            if self.name:
                self.alias = slugify_url(self.name)

            # new object, save first and then generate logo
            # only if logo has been supplied
            if self.logo.name:
                super(Company, self).save()
                # save later
                # mark new photo original for deletion
                try:
                    to_delete.append(self.logo.path)
                except:
                    pass
                generate_images(self)

        else:
            # try to delete old image if new passed
            try:
                c = Company.objects.get(pk=self.pk)
                if self.logo != c.logo:
                    os.remove(c.logo.path)
            except:
                pass

            # check if a new photo submitted, if yes delete the old one
            try:
                old_image_path = getattr(self, '_Company__initial_logo_file_path')
            except AttributeError:
                old_image_path = ''

            # check if filefield clear checkbox was checked
            # in this case e.g. self.logo.name == '' and self.logo._file == None
            # so, maybe not the best solution, but when everything is empty
            # we will try to delete both files. Ok, it works.
            if self.logo.name == '' and self.logo._file is None:
                try:
                    to_delete.append(old_image_path)
                    self.logo.delete()
                except:
                    pass

            if self.logo.name != '' and self.logo_has_changed() is True:
                # got new image, delete old
                try:
                    to_delete.append(old_image_path)
                except ValueError:
                    pass
                # mark for deletion existing picture
                try:
                    to_delete.append(self.logo.path)
                except ValueError:
                    pass
                # save object and new photo original
                super(Company, self).save(*args, **kwargs)
                # mark new original image for deletion as we are going
                # to generate resized later using generate_images
                try:
                    to_delete.append(self.logo.path)
                except ValueError:
                    pass
                # generate new images
                generate_images(self)
            else:
                # no images changed
                pass

        # delete previous versions of logo if there are any
        for file in to_delete:
            try:
                default_storage.delete(file)
            except:
                pass

        super(Company, self).save(*args, **kwargs)


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
