from django.contrib import admin

from .models import (
    ConnectionRequest,
    JobPost,
    Skill,
)


admin.site.register(ConnectionRequest)
admin.site.register(JobPost)
admin.site.register(Skill)
