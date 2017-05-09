from django.views.generic import View
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template import RequestContext, loader
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import re
import os

from django.conf import settings

from recruit.models import Company
from profileme.models import Candidate, Agent

#from recruit.forms import CandidateForm, AgentForm, CompanyForm
from django.contrib.auth.decorators import login_required

from django.contrib.auth import get_user_model
User = get_user_model()

class HomeView(View):
    template_name = 'recruit/landing.html'

    def get(self, request, **kwargs):

        return render(request, self.template_name, {

        }) 

class SearchView(View):
    template_name = 'recruit/search.html'

    def get(self, request, **kwargs):
        search_string = request.GET.get('search', None)
        candidates = []
        print(search_string)
        if search_string is not None:
            candidates = Candidate.objects.filter(Q(skills__iexact=search_string) |
                                              Q(title__iexact=search_string))

        return render(request, self.template_name, {
            'candidates': candidates
        })
        
    @method_decorator(login_required(login_url='/accounts/login/'))
    def dispatch(self, *args, **kwargs):
        return super(SearchView, self).dispatch(*args, **kwargs)
        