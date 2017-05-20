from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.contrib.postgres.search import (
    SearchQuery,
    SearchVector,
)
from django.shortcuts import render
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from braces.views import LoginRequiredMixin

from .models import (
    JobPost,
    Skill,
)
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


class DashboardView(LoginRequiredMixin, View):
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

dashboard = DashboardView.as_view()


class SearchView(LoginRequiredMixin, TemplateView):
    template_name = 'recruit/search.html'

    def get_context_data(self, *args, **kwargs):
        context = super(SearchView, self).get_context_data(*args, **kwargs)
        search = self.request.GET.get('search', None)
        filters = self.request.GET.get('filters', None)
        results = []

        if search or filters:
            search_query = None

            # generate SearchQuery item from search
            for index, item in enumerate(filters.split(',')):
                if index == 0:
                    search_query = SearchQuery(item)
                search_query |= SearchQuery(item)

            # generate additioanl SearchQuery item from filters
            for index, item in enumerate(search.split()):
                if not search_query:
                    search_query = SearchQuery(item)
                search_query |= SearchQuery(item)

            # job posts seatch
            if self.request.user.registered_as == User.ACCOUNT_CANDIDATE:
                results = JobPost.objects\
                    .annotate(search=SearchVector('title', 'skills__name', 'city', 'country'))\
                    .filter(search=search_query)\
                    .distinct('id')
            # candidate search
            else:
                results = Candidate.objects.filter(
                    Q(skills__iexact=search) | Q(title__iexact=search)
                )

        context['skills'] = Skill.objects.all()
        context['results'] = results
        context['filters'] = filters.split(',') if filters else []
        context['search'] = search
        return context

search = SearchView.as_view()


class JobPostListView(LoginRequiredMixin, ListView):
    """
    View for displaying the list of all the company's job posts.
    """
    model = JobPost
    context_object_name = 'job_posts'
    template_name = 'recruit/job_posts/list.html'

    def get_queryset(self):
        return JobPost.objects.filter(posted_by=self.request.user.agent).order_by('-updated_at')

job_post_list = JobPostListView.as_view()


class JobPostCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating a new job post.
    """
    model = JobPost
    form_class = JobPostForm
    template_name = 'recruit/job_posts/create_update.html'
    success_url = reverse_lazy('recruit:job_post_list')

    def get_initial(self):
        return {'posted_by': self.request.user.agent}

job_post_create = JobPostCreateView.as_view()


class JobPostUpdateView(LoginRequiredMixin, UpdateView):
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


class JobPostDeleteView(LoginRequiredMixin, DeleteView):
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
