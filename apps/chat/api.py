from django.views.generic import View
from django.contrib.auth import get_user_model
from braces.views import JSONResponseMixin, LoginRequiredMixin

User = get_user_model()


class UsersListAPIView(LoginRequiredMixin, View, JSONResponseMixin):
    """
    API view for requesting list of users by chat application.
    """
    def get(self, request):
        user_list = User.objects.exclude(id=request.user.id)
        response = [{'id': user.id, 'name': user.email} for user in user_list]
        return self.render_json_response(response)
