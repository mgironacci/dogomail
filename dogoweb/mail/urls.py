from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='mailindex'),
    url(r'^blocked/$', views.blocked, name='mailblocked'),
    url(r'^queues/$', views.queues, name='mailqueues'),
    url(r'^doms/$', views.doms, name='maildoms'),
    url(r'^mboxes/$', views.mboxes, name='mailmboxes'),
    url(r'^domadm/$', views.domadm, name='maildomadm'),
    url(r'^srvdash/$', views.srvdash, name='mailsrvdash'),
    url(r'^srvadm/$', views.srvadm, name='mailsrvadm'),
]
