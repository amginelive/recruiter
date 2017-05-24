import datetime
import logging

from django.db import models
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

from core.models import AbstractTimeStampedModel
from libs.tools import random_string_gen, resize_image


logger = logging.getLogger('console_log')
optional = {
    'blank': True,
    'null': True,
}


class UserManager(BaseUserManager):
    """
    Model for a Custom user Manager
    """

    def _create_user(self, email, first_name, last_name, password, is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('Email must be set')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, first_name, last_name, password, **extra_fields):
        return self._create_user(email, first_name, last_name, password, True, True, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    A fully featured User model with admin-compliant permissions that uses
    a full-length email field as the username.

    Email and password are required. Other fields are optional.
    """
    ACCOUNT_CANDIDATE = 1
    ACCOUNT_AGENT = 2

    ACCOUNT_TYPE_CHOICES = (
        (ACCOUNT_CANDIDATE, _('Candidate')),
        (ACCOUNT_AGENT, _('Agent')),
    )

    email = models.EmailField(_('Email Address'), max_length=254, unique=True)
    first_name = models.CharField(_('First Name'), max_length=30)
    last_name = models.CharField(_('Last Name'), max_length=30)
    slug = models.SlugField(_('Alias/Slug'), **optional)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.')
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=('Designates whether this user should be treated as '
                   'active. Unselect this instead of deleting accounts.')
    )
    get_ads = models.BooleanField(_('Receive ads by email?'), default=True)
    date_joined = models.DateTimeField(_('Date Joined'), default=timezone.now)
    account_type = models.IntegerField(
        _('Account Type'),
        choices=ACCOUNT_TYPE_CHOICES,
        default=ACCOUNT_CANDIDATE,
        help_text='User role selected during registration'
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    index_together = [
        ['slug', 'is_active'],
    ]

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def get_absolute_url(self):
        return "/user/{}/".format(self.slug)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return "{} {}".format(self.first_name, self.last_name[0].upper())

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    @property
    def domain(self):
        """
        Retrieves the domain name from the email address.
        """
        return self.email[self.email.find('@') + 1:]

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = random_string_gen(12, 16)
            while User.objects.filter(slug=self.slug).exists():
                self.slug = random_string_gen(12, 16)

        super(User, self).save(*args, **kwargs)


class ProfileBase(AbstractTimeStampedModel):
    """
    Abstract model for Profile.
    """
    # Status choices
    STATUS_ACTIVE = 0
    STATUS_INACTIVE = 1
    STATUS_MODERATION = 2

    STATUS_CHOICES = (
        (STATUS_ACTIVE, _('Active')),
        (STATUS_INACTIVE, _('Inactive')),
        (STATUS_MODERATION, _('Moderation'))
    )

    phone = PhoneNumberField(_('Phone'), **optional)
    photo = models.ImageField(_('Photo'), upload_to='images/photo/%Y/', help_text="200x200px", **optional)
    status = models.IntegerField(_('Status'), choices=STATUS_CHOICES, default=STATUS_ACTIVE)

    class Meta:
        abstract = True

    index_together = [
        ["user", "status"],
    ]

    def __str__(self):
        return '%s' % (self.user)

def get_cv_path(self, filename):
    return "files/cv/{}/{}/{}".format(datetime.date.today().year, self.user.pk, filename)


class Candidate(ProfileBase):
    """
    Model for Candidate.
    """
    JOB_TYPE_CONTRACTING = 0
    JOB_TYPE_PERMANENT = 1

    JOB_TYPE_CHOICES = (
        (JOB_TYPE_CONTRACTING, _('Contract')),
        (JOB_TYPE_PERMANENT, _('Permanent')),
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='candidate')
    title = models.CharField(_('Job title'), max_length=200, **optional)
    skills = models.ManyToManyField(
        'recruit.Skill',
        related_name='candidates',
        verbose_name=_('Skills')
    )
    job_location = models.CharField(_('Desired job location'),  max_length=200, **optional)
    job_type = models.IntegerField(_('Job type'), choices=JOB_TYPE_CHOICES, **optional)
    city = models.CharField(_('City'),  max_length=200)
    country = CountryField(_('Country'))
    experience = models.SmallIntegerField(_('Experience (full years)'), **optional)
    cv = models.FileField(_("CV"), upload_to=get_cv_path, max_length=150, editable=True, **optional)

    # delete old cv file if new is there
    def cv_has_changed(self):
        if getattr(self, 'cv') and getattr(self, '_ProfileBase__initial_cv_file_path') !=  getattr(self, 'cv').path:
            try:
                default_storage.delete(getattr(self, '_ProfileBase__initial_cv_file_path'))
            except:
                pass
            return True
        return False

    def save(self, *args, **kwargs):
        if self.pk:
            self.cv_has_changed()
        super(Candidate, self).save()

    def delete(self, *args, **kwargs):
        if self.cv:
            try:
                self.cv.delete()
            except:
                pass

        super(Candidate, self).delete(*args, **kwargs)


class Agent(ProfileBase):
    """
    Model for Agent.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='agent')
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.SET_NULL,
        verbose_name=_('Company'),
        related_name='agents',
        **optional
    )

    class Meta:
        verbose_name = _('Agent')
        verbose_name_plural = _('Agents')

    def __str__(self):
        return self.user.get_full_name()
