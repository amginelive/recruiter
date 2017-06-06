from django.contrib import admin

from .models import (
    Connection,
    ConnectionInvite,
    ConnectionRequest,
    JobPost,
    JobReferral,
    UserReferral,
    Skill,
)


admin.site.register(Connection)
admin.site.register(ConnectionInvite)
admin.site.register(ConnectionRequest)
admin.site.register(JobPost)
admin.site.register(JobReferral)
admin.site.register(UserReferral)
admin.site.register(Skill)
