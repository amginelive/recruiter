from django.contrib.auth import get_user_model
from django.contrib.postgres.search import (
    SearchQuery,
    SearchVector,
)
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
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
    CandidateProfileDetailUpdateForm,
)
from .mixins import CandidateRequiredMixin
from .models import (
    Agent,
    Candidate,
    UserNote,
)
from .utils import get_profile_completeness
from chat.models import Message
from companies.models import CompanyRequestInvitation
from recruit.models import ConnectionRequest


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
        valid = False

        if request.user.account_type == User.ACCOUNT_CANDIDATE:
            self.template_name = 'users/candidate_update.html'
            form = CandidateUpdateForm(form_values, request.FILES, instance=request.user.candidate)
            completeness = get_profile_completeness(request.user.candidate)
            if form.is_valid():
                form.save(commit=True)
                valid = True

        # show agent dashboard
        elif request.user.account_type == User.ACCOUNT_AGENT:
            self.template_name = 'users/agent_update.html'
            form = AgentUpdateForm(form_values, request.FILES, instance=request.user.agent)

            if form.is_valid():
                form.save(commit=True)
                valid = True

        if valid:
            return HttpResponseRedirect(reverse_lazy('users:profile_update'))
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
            context['user_note'] = UserNote
            context['user_notes'] = UserNote.objects.filter(note_by=self.request.user, note_to=profile.user)
            if self.request.user.account_type == User.ACCOUNT_AGENT:
                messages_sent = Message.objects.filter(author=self.request.user).order_by('created_at')
                context['first_contact_sent'] = messages_sent.first()
                context['last_message_sent'] = messages_sent.last()
                context['last_message_received'] = Message.objects\
                    .filter(conversation__users=self.request.user)\
                    .exclude(author=self.request.user)\
                    .order_by('created_at')\
                    .last()
            if self.request.user == profile.user:
                context['profile_candidate_form'] = CandidateProfileDetailUpdateForm(instance=profile)

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

        context['search'] = search
        context['candidates'] = candidates
        context['connection_request'] = ConnectionRequest

        connection_requests = ConnectionRequest.objects.filter(
            connectee__candidate__in=candidates,
            connecter=self.request.user
        )
        context['candidate_to_candidate_team_member_requests'] = connection_requests\
            .filter(connection_type=ConnectionRequest.CONNECTION_CANDIDATE_TO_CANDIDATE_TEAM_MEMBER)\
            .values_list('connectee__pk', flat=True)
        context['candidate_to_candidate_network_requests'] = connection_requests\
            .filter(connection_type=ConnectionRequest.CONNECTION_CANDIDATE_TO_CANDIDATE_NETWORK)\
            .values_list('connectee__pk', flat=True)

        return context

candidate_search = CandidateSearchView.as_view()


class AgentSearchView(LoginRequiredMixin, TemplateView):
    """
    View for candidates to search for agents to add to their network.
    """
    template_name = "users/agent_search.html"

    def get_context_data(self, *args, **kwargs):
        context = super(AgentSearchView, self).get_context_data(*args, **kwargs)
        search = self.request.GET.get('search', None)
        agents = []

        if search:
            search_list = search.split()

            for index, item in enumerate(search_list):
                if index == 0:
                    search_query = SearchQuery(item)
                search_query |= SearchQuery(item)

            agents = Agent.objects\
                .annotate(search=SearchVector('user__first_name', 'user__last_name'))\
                .filter(search=search_query)\
                .exclude(user=self.request.user)\
                .distinct('id')

        context['search'] = search
        context['agents'] = agents
        context['connection_request'] = ConnectionRequest

        connection_requests = ConnectionRequest.objects.filter(
            connectee__agent__in=agents,
            connecter=self.request.user
        )
        if self.request.user.account_type == User.ACCOUNT_CANDIDATE:
            context['candidate_to_agent_network_requests'] = connection_requests\
                .filter(connection_type=ConnectionRequest.CONNECTION_CANDIDATE_TO_AGENT_NETWORK)\
                .values_list('connectee__pk', flat=True)
        elif self.request.user.account_type == User.ACCOUNT_AGENT:
            context['agent_to_agent_network_requests'] = connection_requests\
                .filter(connection_type=ConnectionRequest.CONNECTION_AGENT_TO_AGENT_NETWORK)\
                .values_list('connectee__pk', flat=True)

        return context

agent_search = AgentSearchView.as_view()
