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

    def _create_user(self, email, firstname, lastname, password, is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('Email must be set')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            firstname=firstname,
            lastname=lastname,
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
    ACCOUNT_CANDIDATE = 1
    ACCOUNT_AGENT = 2

    ACCOUNT_TYPE_CHOICES = (
        (ACCOUNT_CANDIDATE, _('Candidate')),
        (ACCOUNT_AGENT, _('Agent')),
    )

    email = models.EmailField(_('email address'), max_length=254, unique=True)
    firstname = models.CharField(_('First name'), max_length=30)
    lastname = models.CharField(_('Last name'), max_length=30)
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
    REQUIRED_FIELDS = ['firstname', 'lastname']

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

    # show image thumbnail in admin
    def admin_thumbnail(self):
        if self.photo:
            thumbnail = self.photo.url
        else:
            thumbnail = ''
        return u'<img src="%s" / width="60">' % thumbnail

    admin_thumbnail.short_description = _('Photo')
    admin_thumbnail.allow_tags = True

    # process profile images
    def delete(self, *args, **kwargs):
        if self.photo:
            try:
                default_storage.delete(self.photo.path)
                self.photo.delete()
            except:
                pass

        super(ProfileBase, self).delete(*args, **kwargs)

    # save existing values for later comparison (photo change)
    def __init__(self, *args, **kwargs):
        super(ProfileBase, self).__init__(*args, **kwargs)
        try:
            self.__initial_photo_file_path = self.photo.path
        except ValueError:
            self.__initial_photo_file_path = ''
        # TODO: think of a better solution later for cv
        try:
            self.__initial_cv_file_path = self.cv.path
        except:
            self.__initial_cv_file_path = ''

    def photo_has_changed(self):

        if getattr(self, '_ProfileBase__initial_photo_file_path') !=  getattr(self, 'photo').path:
            return True
        return False

    def save(self, *args, **kwargs):
        # resize uploaded photo
        def generate_images(self):
            # content type name will be used as a reference for alias,
            # please make sure you don't have duplicates or overlaps.
            # format for config "{app_label}_{model}"
            content_name = "{}_{}".format('users', self.__class__.__name__.lower())
            # TODO: make alias the same as content_type.model
            filename, file = resize_image(self.photo, settings.THUMBNAIL_ALIASES[content_name]['photo'])
            self.photo.save(filename, file, save=False)

        # remember original photo path to delete it later
        to_delete = []
        if self.pk:
            # check if a new photo submitted, if yes delete the old one
            try:
                old_image_path = getattr(self, '_ProfileBase__initial_photo_file_path')
            except AttributeError:
                old_image_path = ''

            # check if filefield clear checkbox was checked
            # in this case self.img_med.name == '' and self.img_med._file == None
            # so, maybe not the best solution, but when everything is empty
            # we will try to delete both files. Ok, it works.
            if self.photo.name == '' and self.photo._file is None:
                try:
                    to_delete.append(old_image_path)
                    self.photo.delete()
                except:
                    pass

            if self.photo.name != '' and self.photo_has_changed() is True:
                # got new image, delete old
                try:
                    to_delete.append(old_image_path)
                except ValueError:
                    pass
                # mark for deletion existing picture
                try:
                    to_delete.append(self.photo.path)
                except ValueError:
                    pass
                # save object and new photo original
                super(ProfileBase, self).save(*args, **kwargs)
                # mark new original image for deletion as we are going
                # to generate resized later using generate_images
                try:
                    to_delete.append(self.photo.path)
                except ValueError:
                    pass
                # generate new images
                generate_images(self)
            else:
                # no images changed
                pass
        # new object, save first and then generate photos
        else:
            # if we don't have profiles yet generate images
            # only if photo has been supplied
            if self.photo.name:
                super(ProfileBase, self).save()
                # save later
                # mark new photo original for deletion
                try:
                    to_delete.append(self.photo.path)
                except:
                    pass
                generate_images(self)

        # delete previous versions of profile photo if there are any
        for file in to_delete:
            try:
                default_storage.delete(file)
            except:
                pass

        # finally save object with new images
        super(ProfileBase, self).save()


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
