from macrosurl import url

from . import views


urlpatterns = (
    url(r'^$', views.chat_view, name='chat'),
)
