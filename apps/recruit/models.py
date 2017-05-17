import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _


from core.models import AbstractTimeStampedModel
from libs.general import COUNTRIES


class JobPost(AbstractTimeStampedModel):

    company = models.ForeignKey('companies.Company', related_name='job_posts')
    title = models.CharField(_('Title'), max_length=255)
    description = models.TextField(_('Description'))
    contract = models.TextField(_('Contract'))
    city = models.CharField(_('City'), max_length=80)
    country = models.CharField(_('Country'), max_length=2, choices=COUNTRIES)
    skills = models.ManyToManyField('recruit.Skill', related_name='job_posts', verbose_name=_('Skills'))
    uuid = models.SlugField(_('UUID'), default=uuid.uuid4, editable=False)

    class Meta:
        verbose_name = _('Job Post')
        verbose_name_plural = _('Job Posts')

    def __str__(self):
        return self.title


class Skill(AbstractTimeStampedModel):

    name = models.CharField(_('Name'), max_length=100)

    class Meta:
        verbose_name = _('Skill')
        verbose_name_plural = _('Skills')

    def __str__(self):
        return self.name
