from macrosurl import url

from . import views
from . import api


urlpatterns = (
    url(r'^$', views.chat_view, name='chat'),
    url(r'^users/$', api.user_list_api, name='users'),
)
