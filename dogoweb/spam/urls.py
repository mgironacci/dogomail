from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='spamindex'),
    url(r'^lists$', views.lists, name='spamlists'),
    url(r'^avirus$', views.avirus, name='spamavirus'),
    url(r'^modules$', views.modules, name='spammodules'),
    url(r'^policies$', views.policies, name='spampolicies'),
    url(r'^rules$', views.rules, name='spamrules'),
]
