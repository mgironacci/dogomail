from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url('^ingreso/', auth_views.login),
    url('^salir/', auth_views.logout_then_login),
]