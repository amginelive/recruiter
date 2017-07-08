from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.db import transaction
from django.forms import BaseFormSet, formset_factory
from django.utils.translation import ugettext_lazy as _

from phonenumber_field.formfields import PhoneNumberField
from PIL import Image

from .models import (
    Agent,
    Candidate,
    CandidateSettings,
    CandidateSkill,
    CVRequest,
    UserNote,
)
from companies.models import CompanyInvitation
from recruit.models import (
    Connection,
    ConnectionInvite,
    Skill,
)


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
        with transaction.atomic():
            if type(user).__name__ == 'SocialLogin':
                user = user.user

            user.account_type = int(self.cleaned_data.get('account_type'))
            user.save()

            # create profile for new user
            data = {
                'user': user,
                'phone': self.cleaned_data['phone']
            }
            if user.account_type == User.ACCOUNT_CANDIDATE:
                Candidate.objects.create(**data)
            elif user.account_type == User.ACCOUNT_AGENT:
                agent = Agent.objects.create(**data)

            invite_type = request.GET.get('invite_type')
            uuid = request.GET.get('uuid')
            if invite_type == 'connection':
                connection_invitation = ConnectionInvite.objects.filter(uuid=uuid)
                if connection_invitation.exists():
                    connection_invitation = connection_invitation.first()
                    Connection.objects.create(
                        connecter=connection_invitation.connecter,
                        connectee=user,
                        connection_type=connection_invitation.connection_type
                    )
                    connection_invitation.delete()
            elif invite_type == 'company':
                company_invitation = CompanyInvitation.objects.filter(uuid=uuid)
                if company_invitation.exists():
                    agent.company = company_invitation.first().inviter.company
                    agent.save()
                    company_invitation.delete()


class CandidateUpdateForm(forms.ModelForm):

    class Meta:
        model = Candidate
        exclude = ('user', 'date_updated', 'photo', 'cv', 'connections')


class CandidateProfileDetailUpdateForm(forms.ModelForm):

    class Meta:
        model = Candidate
        fields = ('experience', 'city', 'country',
                  'desired_city', 'desired_country', 'willing_to_relocate',
                  'status', 'in_contract_status', 'out_contract_status',)

    def __init__(self, *args, **kwargs):
        super(CandidateProfileDetailUpdateForm, self).__init__(*args, **kwargs)

        initial = [
            {
                'skill': candidate_skill.skill.name,
                'experience': candidate_skill.experience,
            }
            for candidate_skill in self.instance.candidate_skills
        ]
        self.candidate_skill_formset = CandidateSkillFormSet(initial=initial)

    def clean(self):
        super(CandidateProfileDetailUpdateForm, self).clean()
        self.candidate_skill_formset = CandidateSkillFormSet(self.data)

        if not self.candidate_skill_formset.is_valid() or self.candidate_skill_formset.non_form_errors():
            raise forms.ValidationError(_('Please check the core skill errors.'))

        return self.cleaned_data

    def save(self, *args, **kwargs):
        candidate = super(CandidateProfileDetailUpdateForm, self).save()

        CandidateSkill.objects.filter(candidate=candidate).delete()
        for form in self.candidate_skill_formset.forms:
            if form.is_valid() and form.cleaned_data:
                form.initial['candidate'] = candidate
                form.save()

        return candidate


class CandidateSkillForm(forms.ModelForm):
    """
    Form for Candidate Skill.
    """
    skill = forms.CharField(max_length=100, label=_('Skill'))

    class Meta:
        model = CandidateSkill
        fields = ('experience',)

    def save(self, *args, **kwargs):
        candidate_skill = super(CandidateSkillForm, self).save(commit=False)

        candidate_skill.candidate = self.initial.get('candidate')

        skill = Skill.objects.filter(name__iexact=self.cleaned_data.get('skill'))
        if skill.exists():
            skill = skill.first()
        else:
            skill = Skill.objects.create(name=self.cleaned_data.get('skill'))
        candidate_skill.skill = skill

        candidate_skill.save()

        return candidate_skill


class BaseCandidateSkillFormSet(BaseFormSet):
    """
    Base formset for Candidate Skill.
    """
    def clean(self):
        if any(self.errors):
            return

        skills = []
        for form in self.forms:
            if form.is_valid() and form.cleaned_data:
                skill = form.cleaned_data['skill'].lower()
                if skill in skills:
                    raise forms.ValidationError(_('You cannot add duplicate skills.'))
                skills.append(skill)


CandidateSkillFormSet = formset_factory(CandidateSkillForm, formset=BaseCandidateSkillFormSet)


class AgentUpdateForm(forms.ModelForm):

    class Meta:
        model = Agent
        exclude = ('user', 'date_updated', 'status', 'photo', 'company')


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
        candidate = super(CandidatePhotoUploadForm, self).save()
        x = int(self.cleaned_data.get('x'))
        y = int(self.cleaned_data.get('y'))
        width = int(self.cleaned_data.get('width'))
        height = int(self.cleaned_data.get('height'))

        img = Image.open(candidate.photo)
        cropped_image = img.crop((x, y, width + x, height + y))
        resized_image = cropped_image.resize((200, 200), Image.ANTIALIAS)
        resized_image.save(candidate.photo.path)

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
        agent = super(AgentPhotoUploadForm, self).save()
        x = int(self.cleaned_data.get('x'))
        y = int(self.cleaned_data.get('y'))
        width = int(self.cleaned_data.get('width'))
        height = int(self.cleaned_data.get('height'))

        img = Image.open(agent.photo)
        cropped_image = img.crop((x, y, width + x, height + y))
        resized_image = cropped_image.resize((200, 200), Image.ANTIALIAS)
        resized_image.save(agent.photo.path)

        return agent


class UserNoteForm(forms.ModelForm):
    """
    Form for UserNote.
    """

    class Meta:
        model = UserNote
        fields = ('note_to', 'text', 'type',)

    def __init__(self, *args, **kargs):
        super(UserNoteForm, self).__init__(*args, **kargs)
        if not self.instance.pk:
            initial = self.initial
            self.user = initial.get('user')

    def save(self, *args, **kargs):
        user_note = super(UserNoteForm, self).save(commit=False)

        if not self.instance.pk:
            user_note.note_by = self.user
        user_note.save()

        return user_note


class CandidateSettingsForm(forms.ModelForm):
    """
    Form for CandidateSettings.
    """

    class Meta:
        model = CandidateSettings
        fields = ('auto_cv_download',)


class CVRequestForm(forms.ModelForm):
    """
    Form for CandidateSettings.
    """

    class Meta:
        model = CVRequest
        fields = ('status',)

    def __init__(self, *args, **kargs):
        super(CVRequestForm, self).__init__(*args, **kargs)
        if not self.instance.pk:
            initial = self.initial
            self.candidate = initial.get('candidate')
            self.requested_by = initial.get('requested_by')

    def save(self, *args, **kargs):
        cv_request = super(CVRequestForm, self).save(commit=False)

        if not self.instance.pk:
            cv_request.candidate = self.candidate
            cv_request.requested_by = self.requested_by
        cv_request.save()

        return cv_request
