from django import forms

from profileme.models import Candidate, Agent
from recruit.models import Company, CompanyInvitation


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
        
