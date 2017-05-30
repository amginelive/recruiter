from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .models import (
    Connection,
    ConnectionInvite,
    ConnectionRequest,
    JobPost,
    JobReferral,
)
from core.utils import send_email
from users.models import Candidate


User = get_user_model()


class JobPostForm(forms.ModelForm):
    """
    Form for Job Posts.
    """
    class Meta:
        model = JobPost
        exclude = ('posted_by',)

    def __init__(self, *args, **kwargs):
        super(JobPostForm, self).__init__(*args, **kwargs)
        if not self.instance.pk:
            initial = self.initial
            self.agent = initial.get('agent')

    def save(self, *args, **kwargs):
        job_post = super(JobPostForm, self).save(commit=False)
        skills = self.cleaned_data.get('skills')

        if not self.instance.pk:
            job_post.posted_by = self.agent
        job_post.save()

        job_post.skills.clear()
        job_post.skills.set(skills)

        return job_post


class ConnectionRequestForm(forms.ModelForm):
    """
    Form for Connection Requests.
    """
    class Meta:
        model = ConnectionRequest
        fields = ('connectee', 'connection_type',)

    def __init__(self, *args, **kwargs):
        super(ConnectionRequestForm, self).__init__(*args, **kwargs)
        if not self.instance.pk:
            initial = self.initial
            self.candidate = initial.get('candidate')

    def clean(self):
        connectee = self.cleaned_data.get('connectee')

        connections = Connection.objects.filter(
            (Q(connecter=self.candidate) & Q(connectee=connectee)) |
            (Q(connecter=connectee) & Q(connectee=self.candidate))
        )

        if connections.exists():
            raise forms.ValidationError(_('You are already connected to this candidate.'))

        return self.cleaned_data

    def save(self, *args, **kwargs):
        connection_request = super(ConnectionRequestForm, self).save(commit=False)

        if not self.instance.pk:
            connection_request.connecter = self.candidate
        connection_request.save()

        return connection_request


class ConnectionInviteForm(forms.ModelForm):
    """
    Form for Connection Invite.
    """
    class Meta:
        model = ConnectionInvite
        fields = ('connectee_email', 'connection_type',)

    def __init__(self, *args, **kwargs):
        super(ConnectionInviteForm, self).__init__(*args, **kwargs)
        if not self.instance.pk:
            initial = self.initial
            self.candidate = initial.get('candidate')

    def clean_connectee_email(self):
        connectee_email = self.cleaned_data.get('connectee_email')

        if User.objects.filter(email=connectee_email).exists():
            raise forms.ValidationError(_('A user with this email already exists.'))

        return connectee_email

    def save(self, *args, **kwargs):
        connection_invite = super(ConnectionInviteForm, self).save(commit=False)

        with transaction.atomic():
            if not self.instance.pk:
                connection_invite.connecter = self.candidate
                connection_invites = ConnectionInvite.objects.filter(connectee_email=connection_invite.connectee_email)
                if connection_invites.exists():
                    connection_invite.pk = connection_invites.first().pk
            connection_invite.save()

            send_email(
                _('Candidate Invitation, SquareBalloon'),
                [connection_invite.connectee_email,],
                'recruit/email/connection_invitation',
                {
                    'connection_invite': connection_invite,
                    'user': User,
                },
            )

        return connection_invite


class JobReferralForm(forms.Form):
    """
    Form for referring a job post.
    """
    job_post = forms.IntegerField()
    refer_to = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        super(JobReferralForm, self).__init__(*args, **kwargs)
        initial = self.initial
        self.candidate = initial.get('candidate')
        connections = Connection.objects\
            .filter(Q(connecter=self.candidate) | Q(connectee=self.candidate))\
            .filter(connection_type=Connection.CONNECTION_TEAM_MEMBER)

        choices = []
        for connection in connections:
            if connection.connecter == self.candidate:
                choices.append((connection.connectee.pk, connection.connectee.user.get_full_name()))
            elif connection.connectee == self.candidate:
                choices.append((connection.connecter.pk, connection.connecter.user.get_full_name()))
        self.fields['refer_to'].choices = choices

    def clean_job_post(self):
        job_post = self.cleaned_data.get('job_post')
        return JobPost.objects.get(pk=job_post)

    def clean_refer_to(self):
        refer_to = self.cleaned_data.get('refer_to')
        return Candidate.objects.filter(pk__in=refer_to)

    def save(self, *args, **kwargs):
        refer_to = self.cleaned_data.get('refer_to')
        job_post = self.cleaned_data.get('job_post')

        referrals = []
        for candidate in refer_to:
            referrals.append(
                JobReferral(
                    job_post=job_post,
                    referred_by=self.candidate,
                    referred_to=candidate,
                    created_at=timezone.now(),
                    updated_at=timezone.now(),
                )
            )
        JobReferral.objects.bulk_create(referrals)
