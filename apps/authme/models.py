# authme, C user model with e-mail authentication

import re
from django.db import models
from django.core import validators
from django.utils import timezone
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.db.models.signals import post_save, post_delete
from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from libs.tools import random_string_gen

import logging
lgr = logging.getLogger('console_log')


# user profile types / roles
CANDIDATE = 'c'
AGENT = 'a'

ACC_CHOICES = (
    (CANDIDATE, _('Candidate')),
    (AGENT, _('Agent')),
)

# Custom User Manager
class UserManager(BaseUserManager):

    def _create_user(self, email, firstname, lastname, password,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('Email must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, firstname=firstname, lastname=lastname,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, firstname, lastname, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, firstname, lastname, password, **extra_fields):
        return self._create_user(email, firstname, lastname, password, True, True, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    A fully featured User model with admin-compliant permissions that uses
    a full-length email field as the username.

    Email and password are required. Other fields are optional.
    """

    email = models.EmailField(_('email address'), max_length=254, unique=True)
    firstname = models.CharField(_('First name'), max_length=30, blank=False, null=False)
    lastname = models.CharField(_('Last name'), max_length=30, blank=False, null=False)
    slug = models.SlugField(_('Alias / slug'), blank=True, null=False, unique=False)
    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=('Designates whether this user should be treated as '
                                               'active. Unselect this instead of deleting accounts.'))
    get_ads = models.BooleanField(_('Receive ads by email?'), default=True) 
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    registered_as = models.CharField(max_length=1,
                                     choices=ACC_CHOICES,
                                     default=CANDIDATE,
                                     editable=True,
                                     help_text='User role selected during registration')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'lastname']

    index_together = [
        ["slug", "is_active"],
    ]

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_absolute_url(self):
        return "/user/{}/".format(self.slug)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.firstname, self.lastname)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return "{} {}".format(self.firstname, self.lastname[0].upper())

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = random_string_gen(12, 16)
            while User.objects.filter(slug=self.slug).exists():
                self.slug = random_string_gen(12, 16)

        super(User, self).save(*args, **kwargs)


# 
# def post_save_user(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)
# 
# post_save.connect(post_save_user, sender=User)
