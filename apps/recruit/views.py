from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import (
    ListView,
    TemplateView,
    View,
)

from braces.views import LoginRequiredMixin

from .models import JobPost
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
        job_posts = JobPost.objects.filter(company=self.request.user.agent.company).order_by('-updated_at')
        return job_posts

job_post_list = JobPostListView.as_view()
