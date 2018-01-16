from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    url(r'^$', views.index, name='segindex'),
    url('^login/', auth_views.LoginView.as_view(), name='login'),
    url('^logout/', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^audit$', views.audit, name='segaudit'),
    url(r'^profile$', views.profile, name='segprofile'),
    url(r'^accesos$', views.accesos, name='segaccesos'),
]