from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='statindex'),
    url(r'^pizarron$', views.index, name='pizarron'),
]