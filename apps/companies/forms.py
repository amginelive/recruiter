from django import forms

from .models import Company


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
        company.owner = self.user.agent
        company.save()

        self.user.agent.company = company
        self.user.agent.save()
