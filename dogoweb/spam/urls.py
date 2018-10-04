from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='spamindex'),
    url(r'^lists$', views.lists, name='spamlists'),
    url(r'^list$', views.lista, name='spam_list'),
    url(r'^list/create/$', views.lista_create, name='spam_list_create'),
    url(r'^list/update/(?P<pks>[\,\d]+)*$', views.lista_update, name='spam_list_update'),
    url(r'^list/delete/(?P<pks>[\,\d]+)*$', views.lista_delete, name='spam_list_delete'),
    url(r'^avirus$', views.avirus, name='spamavirus'),
    url(r'^modules$', views.modules, name='spammodules'),
    url(r'^module$', views.module, name='spam_module'),
    url(r'^module/create/$', views.module_create, name='spam_module_create'),
    url(r'^module/update/(?P<pks>[\,\d]+)*$', views.module_update, name='spam_module_update'),
    url(r'^module/delete/(?P<pks>[\,\d]+)*$', views.module_delete, name='spam_module_delete'),
    url(r'^policies$', views.policies, name='spampolicies'),
    url(r'^policy$', views.policy, name='spam_policy'),
    url(r'^policy/create/$', views.policy_create, name='spam_policy_create'),
    url(r'^policy/update/(?P<pks>[\,\d]+)*$', views.policy_update, name='spam_policy_update'),
    url(r'^policy/delete/(?P<pks>[\,\d]+)*$', views.policy_delete, name='spam_policy_delete'),
    url(r'^rules$', views.rules, name='spamrules'),
    url(r'^autorules$', views.autorules, name='spamautorules'),
]
