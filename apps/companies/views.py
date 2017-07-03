from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.views.generic import (
    CreateView,
    DetailView,
    TemplateView,
    View,
)

from braces.views import LoginRequiredMixin

from .forms import (
    CompanyForm,
    CompanyInvitationForm,
    CompanyUpdateForm,
)
from .models import (
    Company,
    CompanyInvitation,
    CompanyRequestInvitation,
)
from chat.models import (
    Conversation,
    Message,
)
from recruit.models import (
    Connection,
    ConnectionRequest,
)
from users.forms import AgentPhotoUploadForm
from users.mixins import AgentRequiredMixin
from users.models import (
    Agent,
    UserNote,
)


User = get_user_model()


class CompanyUpdateView(AgentRequiredMixin, View):
    """
    View for updating the company.
    """
    template_name = 'companies/company_update.html'

    def get(self, request, **kwargs):
        form = []
        try:
            company = Company.objects.get(owner=request.user.agent)
        except Company.DoesNotExist:
            raise Http404('You have no rights to edit company details.')

        form = CompanyUpdateForm(instance=company)

        return render(request, self.template_name, {
            'form': form,
            'company': company
        })

    def post(self, request, **kwards):
        form = []
        company = []
        form_values = request.POST.copy()

        try:
            company = Company.objects.get(owner=request.user.agent)
            form_values['owner'] = company.owner
        except Company.DoesNotExist:
            raise Http404('You have no rights to edit company details.')

        form = CompanyUpdateForm(form_values, request.FILES, instance=company)

        if form.is_valid():
            company = form.save(commit=True)

        return render(request, self.template_name, {
            'form': form,
            'company': company
        })

company_update = CompanyUpdateView.as_view()


class CompanyInviteView(AgentRequiredMixin, View):
    """
    View for inviting user to the company.
    """
    template_name = 'companies/company_invite.html'

    def get(self, request, **kwargs):
        if (request.user.account_type == User.ACCOUNT_AGENT and
            request.user.agent.company.owner == request.user.agent):

            return render(request, self.template_name, {})
        else:
            raise Http404('You are not allowed to access this page')

    def post(self, request, **kwards):
        form = []
        success = False

        if request.user.account_type == User.ACCOUNT_AGENT:
            form = CompanyInvitationForm(request.POST)
            # create invitation
            if form.is_valid():
                invitation = CompanyInvitation.objects.create(
                    sent_to=form.cleaned_data['email'],
                    sent_by=request.user,
                    company=request.user.agent.company
                )
                if invitation.pk > 0:
                    success = True

        return render(request, self.template_name, {
            'form': form,
            'success': success
        })

company_invite = CompanyInviteView.as_view()


class CompanyCreateView(AgentRequiredMixin, CreateView):
    """
    View for creating a company for a new user.
    """
    model = Company
    form_class = CompanyForm
    template_name = 'companies/company_create.html'

    def get_success_url(self):
        return reverse_lazy('recruit:dashboard')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.agent and request.user.agent.company:
            return HttpResponseRedirect(reverse_lazy('recruit:dashboard'))
        return super(CompanyCreateView, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        return {'user': self.request.user}

company_create = CompanyCreateView.as_view()


class CompanyPendingView(AgentRequiredMixin, TemplateView):
    """
    View for requesting an invitation to a company.
    """
    template_name = 'companies/company_pending.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.agent and request.user.agent.company:
            return HttpResponseRedirect(reverse_lazy('recruit:dashboard'))
        return super(CompanyPendingView, self).dispatch(request, *args, **kwargs)

company_pending = CompanyPendingView.as_view()


class CompanyInviteSuccessView(AgentRequiredMixin, DetailView):
    """
    View for the success page when successfully invited to a company.
    """
    model = Company
    template_name = 'companies/company_invite_success.html'

    def get_object(self):
        return self.request.user.agent.company

company_invite_success = CompanyInviteSuccessView.as_view()


class CompanyDetailView(LoginRequiredMixin, DetailView):
    """
    View for the Company's profile.
    """
    model = Company
    template_name = 'companies/company_detail.html'

    def get_object(self):
        return Company.objects.get(slug=self.kwargs.get('slug'))

    def get_context_data(self, *args, **kwargs):
        context = super(CompanyDetailView, self).get_context_data(*args, **kwargs)

        company = self.get_object()
        agent = Agent.objects.filter(pk=self.request.GET.get('agent'))
        current_agent = agent.first() if agent else company.owner

        context['photo_form'] = AgentPhotoUploadForm
        context['invitation_requests'] = CompanyRequestInvitation.objects.filter(company=company)
        context['current_agent'] = current_agent
        context['user_note'] = UserNote
        context['user_notes'] = UserNote.objects\
            .filter(note_by=self.request.user, note_to=current_agent.user)\
            .order_by('-created_at')
        context['current_agent_connection'] = Connection.objects.filter(
            (Q(connectee=self.request.user) & Q(connecter=current_agent.user)) |
            (Q(connectee=current_agent.user) & Q(connecter=self.request.user))
        ).first()
        context['connection_request'] = ConnectionRequest
        context['current_agent_connection_request'] = ConnectionRequest.objects.filter(
            (Q(connectee=self.request.user) & Q(connecter=current_agent.user)) |
            (Q(connectee=current_agent.user) & Q(connecter=self.request.user))
        ).first()

        messages = Message.objects\
            .filter(conversation__users=current_agent.user)\
            .filter(conversation__conversation_type=Conversation.CONVERSATION_USER)\
            .order_by('created_at')

        sent = messages.filter(author=self.request.user)
        context['first_contact_sent'] = sent.first()

        received = messages.exclude(author=self.request.user)
        context['last_message_sent'] = sent.last()
        context['last_message_received'] = received.last()

        company_agent_users = [company_agent.user for company_agent in company.agents.all()]
        if self.request.user not in company_agent_users:
            last_message = Message.objects\
                .filter(conversation__users__in=company_agent_users)\
                .filter(conversation__users=self.request.user)\
                .filter(conversation__conversation_type=Conversation.CONVERSATION_USER)\
                .order_by('created_at')\
                .last()
            context['last_person_in_contact'] = last_message.conversation.participants.exclude(user=self.request.user).first() if last_message else None

            last_user_note = UserNote.objects\
                .filter(note_by=self.request.user)\
                .filter(note_to__in=company_agent_users)\
                .last()
            context['last_person_added_manual_track'] = last_user_note.note_to if last_user_note else None

        return context

company_detail = CompanyDetailView.as_view()
