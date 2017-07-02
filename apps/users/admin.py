from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from .forms import (
    UserChangeForm,
    UserCreationForm
)
from .models import (
    Agent,
    Candidate,
    CandidateSettings,
    CandidateSkill,
    CVRequest,
    UserNote,
)

User = get_user_model()


class UserAdmin(UserAdmin):
    # The forms to add and change user instances

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference the removed 'username' field
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'slug', 'account_type')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}),
    )
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'account_type')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email', 'last_login', 'date_joined')


admin.site.register(Agent)
admin.site.register(Candidate)
admin.site.register(CandidateSettings)
admin.site.register(CandidateSkill)
admin.site.register(CVRequest)
admin.site.register(User, UserAdmin)
admin.site.register(UserNote)
