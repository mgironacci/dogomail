from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='spamindex'),
    url(r'^lists$', views.lists, name='spamlists'),
    url(r'^avirus$', views.avirus, name='spamavirus'),
    url(r'^modules$', views.modules, name='spammodules'),
    url(r'^module$', views.module, name='spam_module'),
    url(r'^module/create/$', views.module_create, name='spam_module_create'),
    url(r'^module/update/(?P<pks>[\,\d]+)*$', views.module_update, name='spam_module_update'),
    url(r'^module/delete/(?P<pks>[\,\d]+)*$', views.module_delete, name='spam_module_delete'),
    url(r'^policies$', views.policies, name='spampolicies'),
    url(r'^rules$', views.rules, name='spamrules'),
]
