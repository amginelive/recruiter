from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from braces.views import LoginRequiredMixin

from .models import JobPost
from .forms import JobPostForm
from companies.models import (
    Company,
    CompanyRequestInvitation,
)
from users.models import Candidate
from users.forms import (
    CandidateUpdateForm,
)


User = get_user_model()


class HomeView(TemplateView):
    template_name = 'recruit/landing.html'


class DashboardView(View):
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
            self.template_name = 'recruit/candidate_dashboard.html'
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
            self.template_name = 'recruit/agent_dashboard.html'
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


class SearchView(View):
    template_name = 'recruit/search.html'

    def get(self, request, **kwargs):
        search_string = request.GET.get('search', None)
        candidates = []

        if search_string is not None:
            candidates = Candidate.objects.filter(Q(skills__iexact=search_string) |
                                              Q(title__iexact=search_string))

        return render(request, self.template_name, {
            'candidates': candidates
        })

    @method_decorator(login_required(login_url='/accounts/login/'))
    def dispatch(self, *args, **kwargs):
        return super(SearchView, self).dispatch(*args, **kwargs)


class JobPostListView(ListView, LoginRequiredMixin):
    """
    View for displaying the list of all the company's job posts.
    """
    model = JobPost
    context_object_name = 'job_posts'
    template_name = 'recruit/job_posts/list.html'

    def get_queryset(self):
        return JobPost.objects.filter(company=self.request.user.agent.company).order_by('-updated_at')

job_post_list = JobPostListView.as_view()


class JobPostCreateView(CreateView, LoginRequiredMixin):
    """
    View for creating a new job post.
    """
    model = JobPost
    form_class = JobPostForm
    template_name = 'recruit/job_posts/create_update.html'
    success_url = reverse_lazy('recruit:job_post_list')

    def get_initial(self):
        return {'company': self.request.user.agent.company}

job_post_create = JobPostCreateView.as_view()


class JobPostUpdateView(UpdateView, LoginRequiredMixin):
    """
    View for updating a job post.
    """
    model = JobPost
    context_object_name = 'job_post'
    form_class = JobPostForm
    template_name = 'recruit/job_posts/create_update.html'
    success_url = reverse_lazy('recruit:job_post_list')

    def get_object(self):
        return JobPost.objects.get(uuid=self.kwargs.get('uuid'))

job_post_update = JobPostUpdateView.as_view()


class JobPostDeleteView(DeleteView, LoginRequiredMixin):
    """
    View for deleting a job post.
    """
    model = JobPost
    context_object_name = 'job_post'
    template_name = 'recruit/job_posts/delete.html'
    success_url = reverse_lazy('recruit:job_post_list')

    def get_object(self):
        return JobPost.objects.get(uuid=self.kwargs.get('uuid'))

job_post_delete = JobPostDeleteView.as_view()
