from django.views.generic import TemplateView
from braces.views import LoginRequiredMixin


class ChatView(LoginRequiredMixin, TemplateView):
    template_name = 'chat/index.html'
