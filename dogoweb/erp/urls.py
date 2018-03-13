from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='erpindex'),
    url(r'^clientes$', views.clientes, name='erp_clientes'),
    url(r'^cliente/create/$', views.cliente_create, name='erp_cliente_create'),
    url(r'^cliente/update/(?P<pks>[\,\d]+)*$', views.cliente_update, name='erp_cliente_update'),
    url(r'^cliente/delete/(?P<pks>[\,\d]+)*$', views.cliente_delete, name='erp_cliente_delete'),
]
