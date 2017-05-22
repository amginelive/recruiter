from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from django.http import (
    HttpResponseRedirect,
    JsonResponse,
)

from braces.views import LoginRequiredMixin


User = get_user_model()


class CandidateRequiredMixin(LoginRequiredMixin):
    """
    Only allow candidates to access this page. Otherwise, redirect them back to their dashboard page.
    """
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.account_type != User.ACCOUNT_CANDIDATE:
            if request.is_ajax():
                return JsonResponse({
                    'success': False,
                    'message': 'Not Authorized',
                })
            return HttpResponseRedirect(reverse_lazy('recruit:dashboard'))
        return super(CandidateRequiredMixin, self).dispatch(request, *args, **kwargs)



class AgentRequiredMixin(LoginRequiredMixin):
    """
    Only allow agents to access this page. Otherwise, redirect them back to their dashboard page.
    """
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.account_type != User.ACCOUNT_AGENT:
            if request.is_ajax():
                return JsonResponse({
                    'success': False,
                    'message': 'Not Authorized',
                })
            return HttpResponseRedirect(reverse_lazy('recruit:dashboard'))
        return super(AgentRequiredMixin, self).dispatch(request, *args, **kwargs)
