from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import (
    View,
)

from .forms import (
    AgentPhotoUploadForm,
    AgentUpdateForm,
    CandidateCVUploadForm,
    CandidatePhotoUploadForm,
    CandidateUpdateForm,
)
from companies.models import (
    Company,
    CompanyRequestInvitation,
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
        if request.user.registered_as == 'a' and not request.user.agent.company:
            company = Company.objects.filter(domain=request.user.domain)

            if company.exists():
                company = company.first()
                # add user to company if auto invite is activated
                if company.allow_auto_invite:
                    request.user.agent.company = company
                    request.user.agent.save()
                    return HttpResponseRedirect(reverse_lazy('companies:company_invite_success'))

                # create company request invitation and redirect to pending page
                # if auto invite is not activated
                else:
                    if not CompanyRequestInvitation.objects.filter(user=request.user).exists():
                        CompanyRequestInvitation.objects.create(
                            user=request.user,
                            company=company,
                        )
                    return HttpResponseRedirect(reverse_lazy('companies:company_pending'))
            return HttpResponseRedirect(reverse_lazy('companies:company_create'))

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
            'invitation_requests': CompanyRequestInvitation.objects.filter(company=company) if request.user.registered_as == 'a' else None,
        })

    @method_decorator(login_required(login_url='/accounts/login/'))
    def dispatch(self, *args, **kwargs):
        return super(DashboardView, self).dispatch(*args, **kwargs)

dashboard = DashboardView.as_view()


class ProfileUpdateView(View):
    """
    View for updating the profile of the user.
    """
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

profile_update = ProfileUpdateView.as_view()


class ProfilePhotoUploadView(View):
    """
    View for uploading a user's profile picture.
    """
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

profile_photo_upload = ProfilePhotoUploadView.as_view()


class ProfileCVUploadView(View):
    """
    View for uploading a candidate's CV.
    """
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

profile_cv_upload = ProfileCVUploadView.as_view()
