from django.conf.urls import url
from . import views

app_name = 'classifier'

urlpatterns = [
    url('^$', views.index, name='index'),
]
