from django.conf.urls import url

from .views import ServiceNowTokenView

app_name = 'service_now_cmdb'

urlpatterns = [
    url(r'^$', ServiceNowTokenView.as_view(), name='service_now_token'),
]
