from macrosurl import url

from . import views


urlpatterns = (
    url(r'^$', views.ChatView.as_view(), name='chat'),
)
