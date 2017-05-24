from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from phonenumber_field.formfields import PhoneNumberField
from slugify import slugify_url
from PIL import Image

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

        first_name = self.cleaned_data.get('first_name').strip()
        last_name = self.cleaned_data.get('last_name').strip()
        email = self.cleaned_data.get('email').strip()
        account_type = int(self.cleaned_data.get('account_type'))

        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.account_type = account_type

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
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())

    class Meta:
        model = Candidate
        fields = ['photo', 'x', 'y', 'width', 'height', ]
        widgets = {
            'photo': forms.FileInput(attrs={'id': 'photo_upload'})
        }

    def save(self):
        candidate = super(CandidatePhotoUploadForm, self).save(commit=False)
        x = int(self.cleaned_data.get('x'))
        y = int(self.cleaned_data.get('y'))
        w = int(self.cleaned_data.get('width'))
        h = int(self.cleaned_data.get('height'))

        img = Image.open(candidate.photo)
        cropped_image = img.crop((x, y, w + x, h + y))
        resized_image = cropped_image.resize((200,200), Image.ANTIALIAS)
        resized_image.save(candidate.photo.path)

        candidate.save()

        return candidate


class CandidateCVUploadForm(forms.ModelForm):

    class Meta:
        model = Candidate
        fields = ['cv',]


class AgentPhotoUploadForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())

    class Meta:
        model = Agent
        fields = ['photo', 'x', 'y', 'width', 'height', ]
        widgets = {
            'photo': forms.FileInput(attrs={'id': 'photo_upload'})
        }

    def save(self):
        agent = super(AgentPhotoUploadForm, self).save(commit=False)
        x = int(self.cleaned_data.get('x'))
        y = int(self.cleaned_data.get('y'))
        w = int(self.cleaned_data.get('width'))
        h = int(self.cleaned_data.get('height'))

        img = Image.open(agent.photo)
        cropped_image = img.crop((x, y, w + x, h + y))
        resized_image = cropped_image.resize((200,200), Image.ANTIALIAS)
        resized_image.save(agent.photo.path)

        agent.save()

        return agent
