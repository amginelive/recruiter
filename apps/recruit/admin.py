from django.contrib import admin
from recruit.models import Company, CompanyInvitation, CompanyRequestInvitation

# Register your models here.
admin.site.register(Company)
admin.site.register(CompanyInvitation)
admin.site.register(CompanyRequestInvitation)
