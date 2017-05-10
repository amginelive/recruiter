from django.db import models
from django.conf import settings
from authme.models import User

import os
import random
import string
from datetime import datetime

from slugify import slugify, slugify_url
from django.utils.translation import get_language, ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.db.models.signals import post_save, post_delete

# email, messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError

from phonenumber_field.modelfields import PhoneNumberField
from libs.general import COUNTRIES
from libs.tools import resize_image, random_string_gen


ACTIVE = 'act'
INACTIVE = 'ina'
MODERATION = 'mod'

YES = 'y'
NO = 'n'


# Company model
class Company(models.Model):

    STATUS_CHOICES = (
        (ACTIVE, 'active'),
        (INACTIVE, 'inactive'),
    )

    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, verbose_name=_('Major company representative'))
    name = models.CharField(blank=False, null=False, max_length=200, verbose_name=_('Company name'))
    domain = models.CharField(blank=False, null=False, max_length=200, unique=True, verbose_name=_('Domain name'))
    overview = models.CharField(blank=True, null=True, max_length=255, verbose_name=_("Company's short title or short 'about' text"))
    alias = models.SlugField(blank=False, null=False, max_length=120, verbose_name='Alias / slug')
    description = models.TextField(blank=True, null=True, max_length=4000)
    logo = models.FileField(upload_to='images/company/logo/%Y', max_length=100, editable=True, blank=True, null=True, help_text=_('Logo size 600x200px, .jpg, .png, .gif formats'))
    address_1 = models.CharField(blank=True, null=True, max_length=80, verbose_name=_('Address line') + ' 1')
    address_2 = models.CharField(blank=True, null=True, max_length=80, verbose_name=_('Address line') + ' 2')
    zip = models.CharField(blank=True, null=True, max_length=10, verbose_name=_('Postal code / ZIP'))
    city = models.CharField(blank=False, null=False, max_length=80)
    country = models.CharField('Country',
                               max_length=2,
                               choices=COUNTRIES,
                               blank=False,
                               null=False)
    website = models.URLField(blank=True, null=True)
    is_charity = models.BooleanField(_("Is it a charity organization?"), null=False, default=False)
    reg_date = models.DateTimeField(auto_now_add=True, editable=False)
    update_date = models.DateTimeField(auto_now=True, editable=False)
    allow_auto_invite = models.BooleanField(_("Allow auto invite?"), default=False)
    status = models.CharField(max_length=3,
                              choices=STATUS_CHOICES,
                              default=ACTIVE)

    index_together = [
        ["alias", "status"],
        ["name", "status"],
    ]

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
            content_name = "{}_{}".format('recruit', self.__class__.__name__.lower())
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


# Invitations company to its agents
class CompanyInvitation(models.Model):

    id = models.AutoField(primary_key=True)
    sent_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name='+')
    sent_to = models.EmailField(_('Email of recipient'), blank=False, null=False)
    sent_to_user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name='+')
    company = models.ForeignKey(Company, blank=False, null=False, on_delete=models.CASCADE, related_name='+')
    invite_key = models.CharField(_('Invitation key'), max_length=30, null=False, unique=True)
    sent_date = models.DateTimeField(auto_now_add=True, editable=False)
    accepted_date = models.DateTimeField(editable=False, null=True, blank=True)
    is_accepted = models.BooleanField(_('Accepted by receiver?'), default=False)

    index_together = [
        ["sent_by", "is_accepted"],
    ]

    def __str__(self):
        return '%s %s' % (self.sent_by, self.sent_to)


    def save(self, *args, **kwargs):

        if not self.pk:
            # create unique key
            self.invite_key = random_string_gen(12, 18)
            while CompanyInvitation.objects.filter(invite_key=self.invite_key).exists():
                self.invite_key = random_string_gen(12, 18)

        super(CompanyInvitation, self).save(*args, **kwargs)


class CompanyRequestInvitation(models.Model):

    user = models.ForeignKey(User, blank=True, null=True, related_name='invitation_request')
    company = models.ForeignKey(Company, blank=False, null=False, related_name='invitation_request')
    key = models.CharField(_('Request Invitation key'), max_length=30, null=False, unique=True)

    def __str__(self):
        return self.user.get_full_name()

    def save(self, *args, **kwargs):
        if not self.pk:
            # create unique key
            self.key = random_string_gen(12, 18)
            while CompanyRequestInvitation.objects.filter(key=self.key).exists():
                self.key = random_string_gen(12, 18)

        super(CompanyRequestInvitation, self).save(*args, **kwargs)


# send email to recipient
def post_save_invitation(sender, instance, created, **kwargs):

    if created and instance.sent_to:
        msg_plain = render_to_string('recruit/email/company_user_invitation.txt',
                                     {'sender_name': instance.sent_by.get_full_name,
                                      'invite_key': instance.invite_key,
                                      'company': instance.sent_by.agent.company.name})
        msg_html = render_to_string('recruit/email/company_user_invitation.html',
                                    {'sender_name': instance.sent_by.get_full_name,
                                     'invite_key': instance.invite_key,
                                     'company': instance.sent_by.agent.company.name})
        send_mail(
            _('Recruiter invitation, SquareBalloon'),
            msg_plain,
            settings.NOREPLY_EMAIL,
            [instance.sent_to,],
            html_message=msg_html,
            fail_silently=False
        )
        del msg_plain
        del msg_html

post_save.connect(post_save_invitation, sender=CompanyInvitation)

