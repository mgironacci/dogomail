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
    url(r'^auditoria$', views.auditoria, name='segauditoria'),
    url(r'^users$', views.users, name='segusers'),
    url(r'^users/create/$', views.user_create, name='seg_user_create'),
    url(r'^users/update/(?P<pks>[\,\d]+)*$', views.user_update, name='seg_user_update'),
    url(r'^users/delete/(?P<pks>[\,\d]+)*$', views.user_delete, name='seg_user_delete'),
    url(r'^groups$', views.groups, name='seggroups'),
    url(r'^groups/create/$', views.group_create, name='seg_group_create'),
    url(r'^groups/update/(?P<pks>[\,\d]+)*$', views.group_update, name='seg_group_update'),
    url(r'^groups/delete/(?P<pks>[\,\d]+)*$', views.group_delete, name='seg_group_delete'),
    url(r'^perms$', views.perms, name='segperms'),
    url(r'^perms/update/(?P<pks>[\,\d]+)*$', views.perm_update, name='seg_perm_update'),
    url(r'^menus$', views.menus, name='segmenus'),
    url(r'^menus/create/$', views.menu_create, name='seg_menu_create'),
    url(r'^menus/update/(?P<pks>[\,\d]+)*$', views.menu_update, name='seg_menu_update'),
    url(r'^menus/delete/(?P<pks>[\,\d]+)*$', views.menu_delete, name='seg_menu_delete'),
    url(r'^pants$', views.pants, name='segpants'),
    url(r'^pants/create/$', views.pant_create, name='seg_pant_create'),
    url(r'^pants/update/(?P<pks>[\,\d]+)*$', views.pant_update, name='seg_pant_update'),
    url(r'^pants/delete/(?P<pks>[\,\d]+)*$', views.pant_delete, name='seg_pant_delete'),
]