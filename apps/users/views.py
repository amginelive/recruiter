from django.contrib.auth import get_user_model
from django.contrib.postgres.search import (
    SearchQuery,
    SearchVector,
)
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import (
    CreateView,
    DetailView,
    TemplateView,
    UpdateView,
    View,
)

from braces.views import LoginRequiredMixin

from .forms import (
    AgentUpdateForm,
    CandidatePhotoUploadForm,
    CandidateUpdateForm,
    CandidateProfileDetailUpdateForm,
    CandidateSettingsForm,
)
from .mixins import CandidateRequiredMixin
from .models import (
    Agent,
    Candidate,
    CandidateSettings,
    UserNote,
)
from .utils import get_profile_completeness
from chat.models import (
    Conversation,
    Message,
)
from recruit.models import (
    Connection,
    ConnectionRequest,
    Skill,
)


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


class CandidateProfileView(LoginRequiredMixin, DetailView):
    """
    View for viewing a user's profile.
    """
    model = Candidate
    context_object_name = 'profile'
    template_name = 'users/candidate_profile.html'

    def get_object(self):
        return Candidate.objects.get(user__slug=self.kwargs.get('slug'))

    def get_context_data(self, *args, **kwargs):
        context = super(CandidateProfileView, self).get_context_data(*args, **kwargs)
        profile = self.get_object()

        if self.request.user == profile.user:
            context['profile_candidate_form'] = CandidateProfileDetailUpdateForm(instance=profile)

        context['user_note'] = UserNote
        context['user_notes'] = UserNote.objects\
            .filter(note_by=self.request.user, note_to=profile.user)\
            .order_by('-created_at')

        is_connected = True
        if self.request.user != profile.user:
            is_connected = Connection.objects.filter(
                (Q(connecter=self.request.user) & Q(connectee=profile.user)) |
                (Q(connecter=profile.user) & Q(connectee=self.request.user))
            ).exists()
        context['is_connected'] = is_connected

        if not is_connected:
            connection_request = ConnectionRequest.objects.filter(
                (Q(connecter=self.request.user) & Q(connectee=profile.user)) |
                (Q(connecter=profile.user) & Q(connectee=self.request.user))
            )
            context['candidate_to_candidate_team_member_request'] = connection_request\
                .filter(connection_type=ConnectionRequest.CONNECTION_CANDIDATE_TO_CANDIDATE_TEAM_MEMBER)\
                .exists()
            context['candidate_to_candidate_network_request'] = connection_request\
                .filter(connection_type=ConnectionRequest.CONNECTION_CANDIDATE_TO_CANDIDATE_NETWORK)\
                .exists()
            context['candidate_to_agent_team_member_request'] = connection_request\
                .filter(connection_type=ConnectionRequest.CONNECTION_CANDIDATE_TO_AGENT_NETWORK)\
                .exists()

        context['skills'] = [skill.name for skill in Skill.objects.all()]
        context['photo_form'] = CandidatePhotoUploadForm
        context['completeness'] = get_profile_completeness(profile)
        context['candidate_form'] = CandidateUpdateForm(instance=profile)
        context['connection_request'] = ConnectionRequest

        if self.request.user.account_type == User.ACCOUNT_AGENT:
            messages = Message.objects\
            .filter(conversation__users=profile.user)\
            .filter(conversation__conversation_type=Conversation.CONVERSATION_USER)\
            .order_by('created_at')

            sent = messages.filter(author=self.request.user)
            context['first_contact_sent'] = sent.first()

            received = messages.exclude(author=self.request.user)
            context['last_message_sent'] = sent.last()
            context['last_message_received'] = received.last()

        return context

candidate_profile = CandidateProfileView.as_view()


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


class SettingsView(LoginRequiredMixin, TemplateView):
    """
    View for the Settings page.
    """
    template_name = 'users/settings.html'

    def get_context_data(self, **kwargs):
        context = super(SettingsView, self).get_context_data(**kwargs)

        if self.request.user.account_type == User.ACCOUNT_CANDIDATE:
            context['form'] = CandidateSettingsForm(instance=self.request.user.candidate.settings)

        return context
settings = SettingsView.as_view()


class SettingsUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for the Settings page.
    """
    model = CandidateSettings
    form_class = CandidateSettingsForm
    success_url = reverse_lazy('users:settings')

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(self.success_url)

    def get_object(self):
        return self.request.user.candidate.settings

settings_update = SettingsUpdateView.as_view()
