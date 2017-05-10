from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import (
    CreateView,
    DeleteView,
    TemplateView,
    View,
)

from braces.views import JSONResponseMixin

from profileme.models import Candidate, Agent
from profileme.forms import (
    AgentPhotoUploadForm,
    AgentUpdateForm,
    CandidateCVUploadForm,
    CandidatePhotoUploadForm,
    CandidateUpdateForm,
    CompanyForm,
    CompanyInvitationForm,
    CompanyUpdateForm,
)
from recruit.models import (
    Company,
    CompanyInvitation,
    CompanyRequestInvitation
)


User = get_user_model()


def get_profile_completeness(profile):
    ''' Calculates candidate profile completeness and
        returns data to display progress bar, etc.
    '''

    is_complete = False # profile completeness flag for candidate
    progress = 0.3  # profile progress, 0.3 is default after registration
    if (profile.title and profile.location and profile.skills and
        profile.phone and profile.experience and profile.residence_country):
        is_complete = True

    # calculate profile progress in %
    progress += 0.2 if is_complete else 0
    progress += 0.3 if profile.cv else 0
    progress += 0.2 if profile.photo else 0
    progress *= 100

    return {'is_complete': is_complete,
            'progress': progress,
            'photo': True if profile.photo else False,
            'cv': True if profile.cv else False}

class DashboardView(View):
    template_name = 'profileme/dashboard.html'

    def get(self, request, **kwargs):
        if request.user.agent and not request.user.agent.company:
            company = Company.objects.filter(domain=request.user.domain)

            if company.exists():
                company = company.first()
                # add user to company if auto invite is activated
                if company.allow_auto_invite:
                    request.user.agent.company = company
                    request.user.agent.save()
                # create company request invitation and redirect to pending page
                # if auto invite is not activated
                else:
                    if not CompanyRequestInvitation.objects.filter(user=request.user).exists():
                        CompanyRequestInvitation.objects.create(
                            user=request.user,
                            company=company,
                        )
                    return HttpResponseRedirect(reverse_lazy('dashboard_company_pending'))
            return HttpResponseRedirect(reverse_lazy('dashboard_company_create'))

        company = []
        f = []
        # show profile dashboard according to user role
        # start with candidate profile
        is_complete = False  # profile completeness flag for candidate
        completeness = 0.3  # profile completeness, 0.3 is default after registration
        if request.user.registered_as == 'c':
            self.template_name = 'profileme/candidate_dashboard.html'
            profile = request.user.candidate
            if (profile.title and profile.location and profile.skills and
                profile.phone and profile.experience and profile.residence_country):
                is_complete = True
            # calculate profile completeness in %
            completeness += 0.2 if is_complete else 0
            completeness += 0.3 if profile.cv else 0
            completeness += 0.2 if profile.photo else 0
            completeness *= 100

            # form will be used to generate user profile data
            f = CandidateUpdateForm(instance=profile)

        # show agent dashboard
        elif request.user.registered_as == 'a':
            self.template_name = 'profileme/agent_dashboard.html'
            profile = request.user.agent
            company = profile.company

        return render(request, self.template_name, {
            'profile': profile,
            'is_complete': is_complete,
            'profile_completeness': completeness,
            'company': company,
            'f': f, # form, for candidate
            'invitation_requests': CompanyRequestInvitation.objects.filter(company=company),
        })

    @method_decorator(login_required(login_url='/accounts/login/'))
    def dispatch(self, *args, **kwargs):
        return super(DashboardView, self).dispatch(*args, **kwargs)

# profile update for candidate and agent
class ProfileUpdateView(View):
    template_name = 'profileme/candidate_update.html'

    def get(self, request, **kwargs):
        completeness = []
        profile = []
        # show profile form according to user role
        # start with candidate profile
        form = []
        if request.user.registered_as == 'c':
            self.template_name = 'profileme/candidate_update.html'
            form = CandidateUpdateForm(instance=request.user.candidate)
            completeness = get_profile_completeness(request.user.candidate)
        # show agent dashboard
        elif request.user.registered_as == 'a':
            self.template_name = 'profileme/agent_update.html'
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

        if request.user.registered_as == 'c':
            self.template_name = 'profileme/candidate_update.html'
            form = CandidateUpdateForm(form_values, request.FILES, instance=request.user.candidate)
            completeness = get_profile_completeness(request.user.candidate)

            if form.is_valid():
                candidate = form.save(commit=True)

        # show agent dashboard
        elif request.user.registered_as == 'a':
            self.template_name = 'profileme/agent_update.html'
            form = AgentUpdateForm(form_values, request.FILES, instance=request.user.agent)

            if form.is_valid():
                agent = form.save(commit=True)

        return render(request, self.template_name, {
            'form': form,
            'completeness': completeness
        })


    @method_decorator(login_required(login_url='/accounts/login/'))
    def dispatch(self, *args, **kwargs):
        return super(ProfileUpdateView, self).dispatch(*args, **kwargs)


# company update
class CompanyUpdateView(View):
    template_name = 'profileme/company_update.html'

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


    @method_decorator(login_required(login_url='/accounts/login/'))
    def dispatch(self, *args, **kwargs):
        return super(CompanyUpdateView, self).dispatch(*args, **kwargs)

# invitations to company
class InviteCompanyUserView(View):
    template_name = 'profileme/invite_users.html'

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
                    sent_to = form.cleaned_data['email'],
                    sent_by = request.user,
                    company = request.user.agent.company)
                if invitation.pk > 0:
                    success = True

        return render(request, self.template_name, {
            'form': form,
            'success': success
        })

    @method_decorator(login_required(login_url='/accounts/login/'))
    def dispatch(self, *args, **kwargs):
        return super(InviteCompanyUserView, self).dispatch(*args, **kwargs)

# accept invitation
# invitations to company
class AcceptInvitationView(View):
    template_name = 'profileme/invite_users.html'

    def get(self, request, **kwargs):
        completeness = []

        form = []
        if (request.user.registered_as == 'a' and
            request.user.agent.company.owner == request.user):

            return render(request, self.template_name, {})
        else:
            raise Http404('You are not allowed to access this page')


        return render(request, self.template_name, {
            'form': form,
            'success': success
        })

    @method_decorator(login_required(login_url='/accounts/login/'))
    def dispatch(self, *args, **kwargs):
        return super(AcceptInvitationView, self).dispatch(*args, **kwargs)


class ProfilePhotoUploadView(View):

    def post(self, request, **kwargs):
        if request.user.is_authenticated:
            # show profile dashboard according to user role
            # start with candidate profile
            form_values = request.POST.copy()
            form_values['user'] = request.user.id
            if request.user.registered_as == 'c':
                candidate = request.user.candidate
                form = CandidatePhotoUploadForm(form_values, request.FILES, instance=candidate)

                if form.is_valid():
                    candidate = form.save(commit=True)
                    return JsonResponse({'success': True, 'image': candidate.photo.url})

            # show agent dashboard
            elif request.user.registered_as == 'a':
                agent = request.user.agent
                form = AgentPhotoUploadForm(form_values, request.FILES, instance=agent)

                if form.is_valid():
                    agent = form.save(commit=True)
                    return JsonResponse({'success': True, 'image': agent.photo.url})
        else:
            return JsonResponse({'success': False, 'message': 'Not authorized'})

# update candidates' CV
class ProfileCVUploadView(View):

    def post(self, request, **kwargs):
        if request.user.is_authenticated:
            # show profile dashboard according to user role
            # start with candidate profile
            form_values = request.POST.copy()
            if request.user.registered_as == 'c':
                form_values['user'] = request.user.id
                candidate = request.user.candidate
                form = CandidateCVUploadForm(form_values, request.FILES, instance=candidate)

                if form.is_valid():
                    candidate = form.save(commit=True)
                    return JsonResponse({'success': True, 'cv': candidate.cv.url})

            # restricted for agents
            else:
                return JsonResponse({'success': False, 'message': 'Not authorized'})
        else:
            return JsonResponse({'success': False, 'message': 'Not authorized'})


class CompanyCreateView(CreateView):
    """
    View for creating a company for a new user.
    """
    model = Company
    form_class = CompanyForm
    template_name = 'profileme/company_create.html'

    def get_success_url(self):
        return reverse_lazy('dashboard')

    def dispatch(self, request, *args, **kwargs):
        if request.user.agent and request.user.agent.company:
            return HttpResponseRedirect(reverse_lazy('dashboard'))
        return super(CompanyCreateView, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        return {'user': self.request.user}

company_create = CompanyCreateView.as_view()


class CompanyPendingView(TemplateView):
    """
    View for requesting an invitation to a company.
    """
    template_name = 'profileme/company_pending.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.agent and request.user.agent.company:
            return HttpResponseRedirect(reverse_lazy('dashboard'))
        return super(CompanyPendingView, self).dispatch(request, *args, **kwargs)

company_pending = CompanyPendingView.as_view()


class CompanyInvitationRequestAPIView(DeleteView, JSONResponseMixin):
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
