from django.contrib.auth import get_user_model
from django.contrib.postgres.search import (
    SearchQuery,
    SearchVector,
)

from django.shortcuts import render
from django.views.generic import (
    DetailView,
    TemplateView,
    View,
)

from braces.views import LoginRequiredMixin

from .forms import (
    AgentPhotoUploadForm,
    AgentUpdateForm,
    CandidatePhotoUploadForm,
    CandidateUpdateForm,
)
from .mixins import CandidateRequiredMixin
from .models import (
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


class CandidateSearchView(CandidateRequiredMixin, TemplateView):
    """
    View for candidates to search for another candidate to add to their network.
    """
    template_name = 'users/candidate_search.html'

    def get_context_data(self, *args, **kwargs):
        context = super(CandidateSearchView, self).get_context_data(*args, **kwargs)
        search = self.request.GET.get('search', None)
        candidates = []

        if search:
            search_list = search.split()

            for index, item in enumerate(search_list):
                if index == 0:
                    search_query = SearchQuery(item)
                search_query |= SearchQuery(item)

            candidates = Candidate.objects\
                .annotate(search=SearchVector('user__first_name', 'user__last_name'))\
                .filter(search=search_query)\
                .exclude(user=self.request.user)\
                .distinct('id')

        context['candidates'] = candidates

        return context

candidate_search = CandidateSearchView.as_view()
