from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='mailindex'),
    url(r'^blocked/$', views.blocked, name='mailblocked'),
    url(r'^queues/$', views.queues, name='mailqueues'),
    url(r'^doms/$', views.doms, name='maildoms'),
    url(r'^mboxes/$', views.mboxes, name='mailmboxes'),
    url(r'^domadm/$', views.domadm, name='maildomadm'),
    url(r'^domains$', views.domains, name='mail_domains'),
    url(r'^domains/create/$', views.domain_create, name='mail_domain_create'),
    url(r'^domains/smail/$', views.domain_smail, name='mail_domain_sendmail'),
    url(r'^domains/update/(?P<pks>[\,\d]+)*$', views.domain_update, name='mail_domain_update'),
    url(r'^domains/delete/(?P<pks>[\,\d]+)*$', views.domain_delete, name='mail_domain_delete'),
    url(r'^srvdash/$', views.srvdash, name='mailsrvdash'),
    url(r'^srvadm/$', views.srvadm, name='mailsrvadm'),
    url(r'^servers$', views.servers, name='mail_servers'),
    url(r'^servers/create/$', views.server_create, name='mail_server_create'),
    url(r'^servers/update/(?P<pks>[\,\d]+)*$', views.server_update, name='mail_server_update'),
    url(r'^servers/delete/(?P<pks>[\,\d]+)*$', views.server_delete, name='mail_server_delete'),
]
