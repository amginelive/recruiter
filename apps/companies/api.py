from django.views.generic import (
    DeleteView,
)

from braces.views import JSONResponseMixin

from .models import (
    CompanyRequestInvitation,
)
from users.mixins import AgentRequiredMixin


class CompanyInvitationRequestAPIView(AgentRequiredMixin, DeleteView, JSONResponseMixin):
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

        return self.render_json_response({'success': True})

company_invitation_request = CompanyInvitationRequestAPIView.as_view()
