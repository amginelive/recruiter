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
        fields = ("email", "firstname", "lastname", "registered_as")


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
    CANDIDATE = 'c'
    AGENT = 'a'

    ACC_CHOICES = (
        (CANDIDATE, _('Candidate')),
        (AGENT, _('Agent')),
    )

    firstname = forms.CharField(max_length=30, label=_('First name'))
    lastname = forms.CharField(max_length=30, label=_('Last name'))
    phone = PhoneNumberField(required=False, label=_('Phone'))
    registered_as = forms.ChoiceField(choices=ACC_CHOICES)

    def signup(self, request, user):
        if type(user).__name__ == 'SocialLogin':
            user = user.user
        user = User.objects.get(pk=user.id)

        user.firstname = self.cleaned_data['firstname'].strip()
        user.lastname = self.cleaned_data['lastname'].strip()
        user.email = self.cleaned_data['email'].strip()
        user.registered_as = self.cleaned_data['registered_as']

        if user.firstname and user.lastname:
            user.slug = slugify_url("{} {}".format(user.firstname, user.lastname))

        user.save()

        data = {
            'user': user,
            'phone': self.cleaned_data['phone']
        }

        # create profile for new user
        if user.registered_as == 'c':
            Candidate.objects.create(**data)
        elif user.registered_as == 'a':
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
