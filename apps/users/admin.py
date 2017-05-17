from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth import get_user_model
User = get_user_model()
from users.forms import UserChangeForm, UserCreationForm


class UserAdmin(UserAdmin):
    # The forms to add and change user instances

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference the removed 'username' field
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('firstname', 'lastname', 'slug', 'registered_as')}),
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
    list_display = ('email', 'firstname', 'lastname', 'is_staff', 'registered_as')
    search_fields = ('email', 'firstname', 'lastname')
    ordering = ('email', 'last_login', 'date_joined')

admin.site.register(User, UserAdmin)
