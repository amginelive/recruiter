from django.views.generic import (
    CreateView,
    DeleteView,
    FormView,
)

from braces.views import LoginRequiredMixin, JSONResponseMixin

from .forms import (
    ConnectionRequestForm,
    JobReferralForm,
    UserReferralForm,
)
from .models import (
    Connection,
    ConnectionRequest,
    JobReferral,
    UserReferral,
)
from users.mixins import CandidateRequiredMixin


class ConnectionRequestCreateAPIView(LoginRequiredMixin, CreateView, JSONResponseMixin):
    """
    API view for requesting a connection to another candnidate.
    """
    model = ConnectionRequest
    form_class = ConnectionRequestForm

    def get_initial(self):
        return {'user': self.request.user}

    def form_valid(self, form):
        form.save()
        return self.render_json_response({
            'success': True,
        })

    def form_invalid(self, form):
        return self.render_json_response({
            'success': False,
            'errors': form.errors,
        })

connection_request_create = ConnectionRequestCreateAPIView.as_view()


class ConnectionRequestDeleteAPIView(LoginRequiredMixin, DeleteView, JSONResponseMixin):
    """
    API View for accepting or declining a connection request.
    """
    model = ConnectionRequest

    def get_object(self):
        return ConnectionRequest.objects.get(uuid=self.kwargs.get('uuid'))

    def post(self, request, *args, **kwargs):
        connection_request = self.get_object()
        connection_request.delete()

        if request.POST.get('action') == 'accept':
            Connection.objects.create(
                connecter=connection_request.connecter,
                connectee=connection_request.connectee,
                connection_type=connection_request.connection_type,
            )

        return self.render_json_response({'success': True})

connection_request_delete = ConnectionRequestDeleteAPIView.as_view()


class JobReferralCreateView(CandidateRequiredMixin, FormView, JSONResponseMixin):
    """
    View for referring a job post to a team member.
    """
    model = JobReferral
    form_class = JobReferralForm

    def get_initial(self):
        return {'candidate': self.request.user.candidate}

    def form_valid(self, form):
        form.save()
        return self.render_json_response({
            'success': True,
        })

    def form_invalid(self, form):
        return self.render_json_response({
            'success': False,
            'errors': form.errors,
        })

job_referral_create = JobReferralCreateView.as_view()


class UserReferralCreateView(CandidateRequiredMixin, FormView, JSONResponseMixin):
    """
    View for referring a user to another user.
    """
    model = UserReferral
    form_class = UserReferralForm

    def get_initial(self):
        return {'user': self.request.user}

    def form_valid(self, form):
        form.save()
        return self.render_json_response({
            'success': True,
        })

    def form_invalid(self, form):
        return self.render_json_response({
            'success': False,
            'errors': form.errors,
        })

user_referral_create = UserReferralCreateView.as_view()
