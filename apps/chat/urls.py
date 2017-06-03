from macrosurl import url

from . import api
from . import views


urlpatterns = (
    url(r'^$', views.chat_view, name='chat'),
    url(r'^users/$', api.user_list_api, name='users'),
)
