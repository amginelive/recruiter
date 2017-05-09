import datetime
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from django.core.files.storage import default_storage
from libs.tools import resize_image
from libs.general import COUNTRIES
from recruit.models import Company

# user profile types / roles
CANDIDATE = 'c'
AGENT = 'a'

ACC_CHOICES = (
    (CANDIDATE, _('Candidate')),
    (AGENT, _('Agent')),
)

# user profile
class ProfileBase(models.Model):
    
    # Status choices
    ACTIVE = 'a'
    INACTIVE = 'i'
    MODERATION = 'm'

    STATUS_CHOICES = (
        (ACTIVE, _('active')),
        (INACTIVE, _('inactive')),
        (MODERATION, _('moderation'))
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = PhoneNumberField(blank=True, null=True)
    photo = models.FileField(upload_to='images/photo/%Y/',
                              max_length=120,
                              editable=True,
                              blank=True,
                              null=True,
                              verbose_name='Photo',
                              help_text="200x200px")
    date_updated = models.DateTimeField(auto_now=True, editable=False, null=False)
    status = models.CharField(max_length=3,
                              choices=STATUS_CHOICES,
                              default=ACTIVE)

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
            content_name = "{}_{}".format('profileme', self.__class__.__name__.lower())
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

    # job type
    CONTRACTING = 'c'
    PERMANENT = 'p'

    JOB_TYPE_CHOICES = (
        (CONTRACTING, _('contract')),
        (PERMANENT, _('permanent')),
    )

    title = models.CharField(blank=True, null=True, max_length=200, verbose_name=_('Job title'))
    skills = models.TextField(blank=True, null=True, max_length=250, verbose_name=('Skills'), help_text="Comma separated skills")
    location = models.CharField(blank=True, null=True, max_length=200, verbose_name=_('Current location'))
    job_location = models.CharField(blank=True, null=True, max_length=200, verbose_name=_('Desired job location'))
    job_type = models.CharField(_('Job type'),
                                max_length=1,
                                choices=JOB_TYPE_CHOICES,
                                blank=True,
                                null=True)
    residence_country = models.CharField(_('Country of residence'),
                                         max_length=2,
                                         choices=COUNTRIES,
                                         blank=False,
                                         null=False)
    experience = models.SmallIntegerField(blank=True, null=True, verbose_name=_("Experience (full years)"))
    cv = models.FileField(upload_to=get_cv_path,
                          max_length=150,
                          editable=True,
                          blank=True,
                          null=True,
                          verbose_name=_("CV"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        
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


# Agent / Employer profile
class Agent(ProfileBase):

    company = models.ForeignKey(Company, blank=True, null=True, on_delete=models.SET_NULL, verbose_name=_('Company'))
    company_name = models.CharField(blank=True, null=True, max_length=200, verbose_name=_('Company name'), help_text="Company name entered during registration")
    is_charity = models.BooleanField(_("Charity / NPO?"), null=False, default=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
