from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from phonenumber_field.formfields import PhoneNumberField
from slugify import slugify_url

from .models import Candidate, Agent


User = get_user_model()


class UserCreationForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given email and password.
    """
    def __init__(self, *args, **kargs):
        super(UserCreationForm, self).__init__(*args, **kargs)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'first_name', 'last_name', 'account_type')


class UserChangeForm(UserChangeForm):
    """
    A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """

    def __init__(self, *args, **kargs):
        super(UserChangeForm, self).__init__(*args, **kargs)

    class Meta(UserChangeForm.Meta):
        model = User


class CustomSignupForm(forms.Form):
    """
    Custom signup form to replace allauth.
    """
    ACCOUNT_CANDIDATE = 1
    ACCOUNT_AGENT = 2

    ACCOUNT_TYPE_CHOICES = (
        (ACCOUNT_CANDIDATE, _('Candidate')),
        (ACCOUNT_AGENT, _('Agent')),
    )

    first_name = forms.CharField(max_length=30, label=_('First name'))
    last_name = forms.CharField(max_length=30, label=_('Last name'))
    phone = PhoneNumberField(required=False, label=_('Phone'))
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE_CHOICES)

    def signup(self, request, user):
        if type(user).__name__ == 'SocialLogin':
            user = user.user
        user = User.objects.get(pk=user.id)

        user.first_name = self.cleaned_data['first_name'].strip()
        user.last_name = self.cleaned_data['last_name'].strip()
        user.email = self.cleaned_data['email'].strip()
        user.account_type = self.cleaned_data['account_type']

        if user.first_name and user.last_name:
            user.slug = slugify_url('{} {}'.format(user.first_name, user.last_name))

        user.save()

        data = {
            'user': user,
            'phone': self.cleaned_data['phone']
        }

        # create profile for new user
        if user.account_type == User.ACCOUNT_CANDIDATE:
            Candidate.objects.create(**data)
        elif user.account_type == User.ACCOUNT_AGENT:
            Agent.objects.create(**data)


class CandidateUpdateForm(forms.ModelForm):

    class Meta:
        model = Candidate
        exclude = ['user', 'date_updated', 'status', 'photo', 'cv']


class AgentUpdateForm(forms.ModelForm):

    class Meta:
        model = Agent
        exclude = ['user', 'date_updated', 'status', 'photo', 'company']


class CandidatePhotoUploadForm(forms.ModelForm):

    class Meta:
        model = Candidate
        fields = ['photo',]


class CandidateCVUploadForm(forms.ModelForm):

    class Meta:
        model = Candidate
        fields = ['cv',]


class AgentPhotoUploadForm(forms.ModelForm):

    class Meta:
        model = Agent
        fields = ['photo',]
