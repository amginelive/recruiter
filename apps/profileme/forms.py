from django import forms

from profileme.models import Candidate, Agent
from recruit.models import Company, CompanyInvitation, CompanyRequestInvitation


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

class CompanyUpdateForm(forms.ModelForm):

    class Meta:
        model = Company
        exclude = ['owner', 'date_updated', 'status', 'slug']

class CompanyInvitationForm(forms.Form):

    email = forms.EmailField()


class CompanyForm(forms.ModelForm):

    class Meta:
        model = Company
        fields = ['name', 'domain', 'city', 'country']

    def __init__(self, *args, **kwargs):
        super(CompanyForm, self).__init__(*args, **kwargs)
        initial = kwargs.get('initial')
        self.user = initial.get('user')

    def save(self, *args, **kwargs):
        company = super(CompanyForm, self).save(commit=False)
        company.owner = self.user
        company.save()

        self.user.agent.company = company
        self.user.agent.save()

