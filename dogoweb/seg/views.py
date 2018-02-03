from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group, Permission
from django.contrib.sessions.models import Session
from django.contrib.admin.models import LogEntry
from .models import LoginLogout, Menu, Pantalla, DTFilter, DTCreate, DTUpdate, DTDelete, html_icon, html_check
from .forms import MenuForm, PantallaForm, GroupForm, UserForm, PermissionForm
from dogoweb.settings import VERSION, ICO_OK, ICO_WARN, ICO_INFO, ICO_CRIT
from ipwhois.utils import get_countries
import json


# Utilidades ----------------
# Decorador para ajax para validar permisos
def ajax_permission_required(perm):
    return permission_required(perm, login_url='/seg/modal_denied/')


# Mensaje ajax para cuando falla el acceso de permiso, usado por el decorador
@login_required()
def modal_denied(request):
    data = dict()
    data['form_is_valid'] = True
    data['mensaje'] = {
        'icon': ICO_CRIT,
        'msg': _('Permission denied!'),
        'tipo': 'danger',
    }
    return JsonResponse(data)


# Indice del modulo ---------
@login_required()
@permission_required('seg.view_security')
def index(request):
    return render(request, 'seg/index.html')


@login_required()
def audit(request):
    return render(request, 'seg/audit.html')


@login_required()
def profile(request):
    return render(request, 'seg/profile.html')


@login_required()
def accesos(request):
    if request.is_ajax() and request.method == 'POST':
        jbody = json.loads(request.body.decode(request._encoding))
    else:
        return JsonResponse({'error': "Bad request"})
    paises = get_countries()
    ret, objs = LoginLogout.objects.dt_filter(jbody, user=request.user, autodata=False)

    for a in objs:
        pais = ""
        flag = ""
        if a.country == 'yo':
            pais = "Local"
        elif a.country in paises:
            pais = paises[a.country]
            flag = "&nbsp;&nbsp;<img src='/static/cleanui/flags/png100px/%s.png' height='16px'/>" % a.country.lower()
        li = ""
        if a.login_time:
            li = timezone.localtime(a.login_time).strftime('%Y-%m-%d %X')
        if a.logout_time:
            lo= timezone.localtime(a.logout_time).strftime('%Y-%m-%d %X')
        else:
            sesiones = Session.objects.filter(session_key=a.session_key)
            if len(sesiones) > 0:
                lo = _("Still logged in")
            else:
                lo = _("Expired")
        ret['data'].append([li, lo, a.host, a.provider, pais + flag])
    return JsonResponse(ret)


@login_required()
def auditoria(request):
    acc = {
        1: _("Add"),
        2:_("Change"),
        3:_("Delete"),
    }
    if request.is_ajax() and request.method == 'POST':
        jbody = json.loads(request.body.decode(request._encoding))
    else:
        return JsonResponse({'error': "Bad request"})
    ret, objs = DTFilter(LogEntry.objects, jbody, user=request.user, autodata=False)
    for a in objs:
        ret['data'].append([timezone.localtime(a.action_time).strftime('%Y-%m-%d %X'), acc[a.action_flag], a.object_repr])
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('seg.view_security')
def users(request):
    if request.is_ajax() and request.method == 'POST':
        jbody = json.loads(request.body.decode(request._encoding))
    else:
        return JsonResponse({'error': "Bad request"})
    ret, objs = DTFilter(User.objects, jbody, autodata=False)
    for a in objs:
        ret['data'].append([a.id, a.username, a.last_name + " " + a.first_name, html_check(a.is_active)])
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('auth.add_user')
def user_create(request):
    ret = DTCreate(request, UserForm)
    ret['panel'] = 'user'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('auth.change_user')
def user_update(request, pks):
    ret = DTUpdate(User.objects, pks, request, UserForm)
    ret['panel'] = 'user'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('auth.delete_user')
def user_delete(request, pks):
    ret = DTDelete(User.objects, pks, request, UserForm)
    ret['panel'] = 'user'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('seg.view_security')
def groups(request):
    if request.is_ajax() and request.method == 'POST':
        jbody = json.loads(request.body.decode(request._encoding))
    else:
        return JsonResponse({'error': "Bad request"})
    ret = DTFilter(Group.objects, jbody)
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('auth.add_group')
def group_create(request):
    ret = DTCreate(request, GroupForm)
    ret['panel'] = 'user'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('auth.change_group')
def group_update(request, pks):
    ret = DTUpdate(Group.objects, pks, request, GroupForm)
    ret['panel'] = 'user'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('auth.delete_group')
def group_delete(request, pks):
    ret = DTDelete(Group.objects, pks, request, GroupForm)
    ret['panel'] = 'user'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('seg.manage_groupperms')
def perms(request):
    if request.is_ajax() and request.method == 'POST':
        jbody = json.loads(request.body.decode(request._encoding))
    else:
        return JsonResponse({'error': "Bad request"})
    ret = DTFilter(Permission.objects, jbody)
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('seg.manage_groupperms')
def perm_update(request, pks):
    ret = DTUpdate(Permission.objects, pks, request, PermissionForm)
    ret['panel'] = 'user'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('seg.manage_menus')
def menus(request):
    if request.is_ajax() and request.method == 'POST':
        jbody = json.loads(request.body.decode(request._encoding))
    else:
        return JsonResponse({'error': "Bad request"})
    ret = Menu.objects.dt_filter(jbody)
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('seg.add_menu')
def menu_create(request):
    ret = Menu.objects.dt_create(request, MenuForm)
    ret['panel'] = 'menu'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('seg.change_menu')
def menu_update(request, pks):
    ret = Menu.objects.dt_update(pks, request, MenuForm)
    ret['panel'] = 'menu'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('seg.delete_menu')
def menu_delete(request, pks):
    ret = Menu.objects.dt_delete(pks, request, MenuForm)
    ret['panel'] = 'menu'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('seg.manage_menus')
def pants(request):
    if request.is_ajax() and request.method == 'POST':
        jbody = json.loads(request.body.decode(request._encoding))
    else:
        return JsonResponse({'error': "Bad request"})
    ret = Pantalla.objects.dt_filter(jbody)
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('seg.add_pantalla')
def pant_create(request):
    ret = Pantalla.objects.dt_create(request, PantallaForm)
    ret['panel'] = 'menu'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('seg.change_pantalla')
def pant_update(request, pks):
    ret = Pantalla.objects.dt_update(pks, request, PantallaForm)
    ret['panel'] = 'menu'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('seg.delete_pantalla')
def pant_delete(request, pks):
    ret = Pantalla.objects.dt_delete(pks, request, PantallaForm)
    ret['panel'] = 'menu'
    return JsonResponse(ret)

