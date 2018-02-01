from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group, Permission
from django.contrib.sessions.models import Session
from django.contrib.admin.models import LogEntry
from .models import LoginLogout, DTFilter, Menu, Pantalla
from .forms import MenuForm, PantallaForm
from ipwhois.utils import get_countries
import json


@login_required()
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
    ret, objs = LoginLogout.objects.dt_filter(jbody, user=request.user)

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
    ret, objs = DTFilter(LogEntry.objects, jbody, user=request.user)
    for a in objs:
        ret['data'].append([timezone.localtime(a.action_time).strftime('%Y-%m-%d %X'), acc[a.action_flag], a.object_repr])
    return JsonResponse(ret)


@login_required()
def users(request):
    if request.is_ajax() and request.method == 'POST':
        jbody = json.loads(request.body.decode(request._encoding))
    else:
        return JsonResponse({'error': "Bad request"})
    ret, objs = DTFilter(User.objects, jbody)
    for a in objs:
        uact = '<i class="icmn-checkbox-checked"></i>'
        if not a.is_active:
            uact = '<i class="icmn-checkbox-unchecked"></i>'
        ret['data'].append([a.username, a.last_name + " " + a.first_name, uact])
    return JsonResponse(ret)


@login_required()
def groups(request):
    if request.is_ajax() and request.method == 'POST':
        jbody = json.loads(request.body.decode(request._encoding))
    else:
        return JsonResponse({'error': "Bad request"})
    ret, objs = DTFilter(Group.objects, jbody)
    for a in objs:
        ret['data'].append([a.name, a.user_set.all().count(), a.permissions.all().count()])
    return JsonResponse(ret)


@login_required()
def perms(request):
    if request.is_ajax() and request.method == 'POST':
        jbody = json.loads(request.body.decode(request._encoding))
    else:
        return JsonResponse({'error': "Bad request"})
    ret, objs = DTFilter(Permission.objects, jbody)
    for a in objs:
        ret['data'].append([a.name, str(a.content_type), a.group_set.all().count()])
    return JsonResponse(ret)


@login_required()
@permission_required('seg.manage_menus')
def menus(request):
    if request.is_ajax() and request.method == 'POST':
        jbody = json.loads(request.body.decode(request._encoding))
    else:
        return JsonResponse({'error': "Bad request"})
    ret, objs = Menu.objects.dt_filter(jbody)
    for a in objs:
        mico = '<i class="%s"></i>' % a.icono
        mact = '<i class="icmn-checkbox-checked"></i>'
        if not a.activo:
            mact = '<i class="icmn-checkbox-unchecked"></i>'
        ret['data'].append([a.id, mico, a.nombre, a.orden, mact])
    return JsonResponse(ret)


@login_required()
@permission_required('seg.add_menu')
def menu_create(request):
    return JsonResponse(Menu.objects.dt_create(request, MenuForm, 'seg/form_menu_new.html'))


@login_required()
@permission_required('seg.change_menu')
def menu_update(request, pks):
    return JsonResponse(Menu.objects.dt_update(pks, request, MenuForm, 'seg/form_menu_edit.html'))


@login_required()
@permission_required('seg.delete_menu')
def menu_delete(request, pks):
    return JsonResponse(Menu.objects.dt_delete(pks, request, MenuForm, 'seg/form_menu_delete.html'))


@login_required()
@permission_required('seg.manage_menus')
def pants(request):
    if request.is_ajax() and request.method == 'POST':
        jbody = json.loads(request.body.decode(request._encoding))
    else:
        return JsonResponse({'error': "Bad request"})
    ret, objs = Pantalla.objects.dt_filter(jbody)
    for a in objs:
        mico = '<i class="%s"></i>' % a.icono
        mact = '<i class="icmn-checkbox-checked"></i>'
        if not a.activo:
            mact = '<i class="icmn-checkbox-unchecked"></i>'
        ret['data'].append([a.id, mico, a.nombre, str(a.menu), a.orden, a.permiso.name, mact])
    return JsonResponse(ret)


@login_required()
@permission_required('seg.add_pantalla')
def pant_create(request):
    return JsonResponse(Pantalla.objects.dt_create(request, PantallaForm, 'seg/form_pant_new.html'))


@login_required()
@permission_required('seg.change_pantalla')
def pant_update(request, pks):
    return JsonResponse(Pantalla.objects.dt_update(pks, request, PantallaForm, 'seg/form_pant_edit.html'))


@login_required()
@permission_required('seg.delete_pantalla')
def pant_delete(request, pks):
    return JsonResponse(Pantalla.objects.dt_delete(pks, request, PantallaForm, 'seg/form_pant_delete.html'))

