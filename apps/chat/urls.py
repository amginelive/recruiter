from macrosurl import url

from . import views
from . import api


urlpatterns = (
    url(r'^$', views.ChatView.as_view(), name='chat'),
    url(r'^users/$', api.UsersListAPIView.as_view(), name='users'),
)
