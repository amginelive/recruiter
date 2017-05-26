from django.contrib import admin

from .models import (
    Connection,
    ConnectionRequest,
    JobPost,
    Skill,
)


admin.site.register(Connection)
admin.site.register(ConnectionRequest)
admin.site.register(JobPost)
admin.site.register(Skill)
