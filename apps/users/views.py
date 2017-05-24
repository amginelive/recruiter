from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import (
    DetailView,
    View,
)

from braces.views import LoginRequiredMixin

from .forms import (
    AgentPhotoUploadForm,
    AgentUpdateForm,
    CandidateCVUploadForm,
    CandidatePhotoUploadForm,
    CandidateUpdateForm,
)
from .mixins import CandidateRequiredMixin
from .models import (
    Agent,
    Candidate,
)
from .utils import get_profile_completeness
from companies.models import CompanyRequestInvitation


User = get_user_model()


class ProfileUpdateView(LoginRequiredMixin, View):
    """
    View for updating the profile of the user.
    """
    template_name = 'users/candidate_update.html'

    def get(self, request, **kwargs):
        completeness = []
        profile = []
        # show profile form according to user role
        # start with candidate profile
        form = []
        if request.user.account_type == User.ACCOUNT_CANDIDATE:
            self.template_name = 'users/candidate_update.html'
            form = CandidateUpdateForm(instance=request.user.candidate)
            completeness = get_profile_completeness(request.user.candidate)
        # show agent dashboard
        elif request.user.account_type == User.ACCOUNT_AGENT:
            self.template_name = 'users/agent_update.html'
            profile = request.user.agent
            form = AgentUpdateForm(instance=profile)
        return render(request, self.template_name, {
            'form': form,
            'completeness': completeness,
            'profile': profile,
        })

    def post(self, request, **kwards):
        form = []
        completeness = {}
        form_values = request.POST.copy()
        form_values['user'] = request.user.id

        if request.user.account_type == User.ACCOUNT_CANDIDATE:
            self.template_name = 'users/candidate_update.html'
            form = CandidateUpdateForm(form_values, request.FILES, instance=request.user.candidate)
            completeness = get_profile_completeness(request.user.candidate)

            if form.is_valid():
                form.save(commit=True)

        # show agent dashboard
        elif request.user.account_type == User.ACCOUNT_AGENT:
            self.template_name = 'users/agent_update.html'
            form = AgentUpdateForm(form_values, request.FILES, instance=request.user.agent)

            if form.is_valid():
                form.save(commit=True)

        return render(request, self.template_name, {
            'form': form,
            'completeness': completeness
        })

profile_update = ProfileUpdateView.as_view()


class ProfilePhotoUploadView(LoginRequiredMixin, View):
    """
    View for uploading a user's profile picture.
    """
    def post(self, request, **kwargs):
        # show profile dashboard according to user role
        # start with candidate profile
        form_values = request.POST.copy()
        form_values['user'] = request.user.id
        if request.user.account_type == User.ACCOUNT_CANDIDATE:
            candidate = request.user.candidate
            form = CandidatePhotoUploadForm(form_values, request.FILES, instance=candidate)
            if form.is_valid():
                candidate = form.save()
                return JsonResponse({'success': True, 'image': candidate.photo.url})

        # show agent dashboard
        elif request.user.account_type == User.ACCOUNT_AGENT:
            agent = request.user.agent
            form = AgentPhotoUploadForm(form_values, request.FILES, instance=agent)

            if form.is_valid():
                agent = form.save()
                return JsonResponse({'success': True, 'image': agent.photo.url})

profile_photo_upload = ProfilePhotoUploadView.as_view()


class ProfileCVUploadView(CandidateRequiredMixin, View):
    """
    View for uploading a candidate's CV.
    """
    def post(self, request, **kwargs):
        # show profile dashboard according to user role
        # start with candidate profile
        form_values = request.POST.copy()
        form_values['user'] = request.user.id
        candidate = request.user.candidate
        form = CandidateCVUploadForm(form_values, request.FILES, instance=candidate)

        if form.is_valid():
            candidate = form.save(commit=True)
            return JsonResponse({'success': True, 'cv': candidate.cv.url})

profile_cv_upload = ProfileCVUploadView.as_view()


class ProfileDetailView(LoginRequiredMixin, DetailView):
    """
    View for viewing a user's profile.
    """

    context_object_name = 'profile'

    def get_object(self):
        user = User.objects.get(slug=self.kwargs.get('slug'))

        if user.account_type == User.ACCOUNT_CANDIDATE:
            return user.candidate
        elif user.account_type == User.ACCOUNT_AGENT:
            return user.agent

    def get_template_names(self):
        profile = self.get_object()

        if profile.user.account_type == User.ACCOUNT_CANDIDATE:
            return ['users/candidate_profile.html']
        elif profile.user.account_type == User.ACCOUNT_AGENT:
            return ['users/agent_profile.html']

    def get_context_data(self, *args, **kwargs):
        context = super(ProfileDetailView, self).get_context_data(*args, **kwargs)
        profile = self.get_object()

        if profile.user.account_type == User.ACCOUNT_CANDIDATE:
            context['photo_form'] = CandidatePhotoUploadForm
            context['completeness'] = get_profile_completeness(profile)
            context['candidate_form'] = CandidateUpdateForm(instance=profile)

        elif profile.user.account_type == User.ACCOUNT_AGENT:
            company = profile.company
            context['company'] = company
            context['invitation_requests'] = CompanyRequestInvitation.objects.filter(company=company)
            context['photo_form'] = AgentPhotoUploadForm

        return context

profile_detail = ProfileDetailView.as_view()
