from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    TemplateView,
    View,
)

from braces.views import (
    JSONResponseMixin,
    LoginRequiredMixin,
)

from .forms import (
    CompanyForm,
    CompanyInvitationForm,
    CompanyUpdateForm,
)
from .models import (
    Company,
    CompanyInvitation,
    CompanyRequestInvitation
)


class CompanyUpdateView(LoginRequiredMixin, View):
    """
    View for updating the company.
    """
    template_name = 'companies/company_update.html'

    def get(self, request, **kwargs):
        form = []
        try:
            company = Company.objects.get(owner=request.user)
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
            company = Company.objects.get(owner=request.user)
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


class CompanyInviteView(LoginRequiredMixin, View):
    """
    View for inviting user to the company.
    """
    template_name = 'companies/company_invite.html'

    def get(self, request, **kwargs):
        completeness = []

        form = []
        if (request.user.registered_as == 'a' and
            request.user.agent.company.owner == request.user):

            return render(request, self.template_name, {})
        else:
            raise Http404('You are not allowed to access this page')

    def post(self, request, **kwards):
        form = []
        success = False

        if request.user.registered_as == 'a':
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


class CompanyCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating a company for a new user.
    """
    model = Company
    form_class = CompanyForm
    template_name = 'companies/company_create.html'

    def get_success_url(self):
        return reverse_lazy('recruit:dashboard')

    def dispatch(self, request, *args, **kwargs):
        if request.user.agent and request.user.agent.company:
            return HttpResponseRedirect(reverse_lazy('recruit:dashboard'))
        return super(CompanyCreateView, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        return {'user': self.request.user}

company_create = CompanyCreateView.as_view()


class CompanyPendingView(LoginRequiredMixin, TemplateView):
    """
    View for requesting an invitation to a company.
    """
    template_name = 'companies/company_pending.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.agent and request.user.agent.company:
            return HttpResponseRedirect(reverse_lazy('recruit:dashboard'))
        return super(CompanyPendingView, self).dispatch(request, *args, **kwargs)

company_pending = CompanyPendingView.as_view()


class CompanyInvitationRequestAPIView(LoginRequiredMixin, DeleteView, JSONResponseMixin):
    """
    View for accepting or rejecting a company invitation request.
    """
    model = CompanyRequestInvitation

    def get_object(self):
        return CompanyRequestInvitation.objects.get(uuid=self.kwargs.get('uuid'))

    def post(self, request, *args, **kwargs):
        request_invitation = self.get_object()
        request_invitation.delete()

        if request.POST.get('action') == 'accept':
            request_invitation.user.agent.company = request_invitation.company
            request_invitation.user.agent.save()

        return self.render_json_response({})

api_company_invitation_request = CompanyInvitationRequestAPIView.as_view()


class CompanyInviteSuccessView(LoginRequiredMixin, DetailView):
    """
    View for the success page when successfully invited to a company.
    """
    model = Company
    template_name = 'companies/company_invite_success.html'

    def get_object(self):
        return self.request.user.agent.company

company_invite_success = CompanyInviteSuccessView.as_view()
