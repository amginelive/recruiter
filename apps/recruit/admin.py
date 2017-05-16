from django.contrib import admin
from recruit.models import (
    Company,
    CompanyInvitation,
    CompanyRequestInvitation,
    JobPost,
    Skill,
)


admin.site.register(Company)
admin.site.register(CompanyInvitation)
admin.site.register(CompanyRequestInvitation)
admin.site.register(JobPost)
admin.site.register(Skill)
