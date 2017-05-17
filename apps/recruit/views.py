from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
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
from profileme.models import Candidate


User = get_user_model()


class HomeView(TemplateView):
    template_name = 'recruit/landing.html'


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
