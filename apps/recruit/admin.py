from django.contrib import admin

from .models import (
    JobPost,
    Skill,
)


admin.site.register(JobPost)
admin.site.register(Skill)
