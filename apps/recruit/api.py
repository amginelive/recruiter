from django.views.generic import (
    CreateView,
)

from braces.views import JSONResponseMixin

from .forms import ConnectionRequestForm
from .models import ConnectionRequest
from users.mixins import CandidateRequiredMixin


class ConnectionRequestCreateAPIView(CandidateRequiredMixin, CreateView, JSONResponseMixin):
    """
    API view for requesting a connection to another candnidate.
    """
    model = ConnectionRequest
    form_class = ConnectionRequestForm

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

connection_request_create = ConnectionRequestCreateAPIView.as_view()
