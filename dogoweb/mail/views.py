from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required, permission_required
from seg.views import ajax_permission_required
from .models import Server, Dominio, Dogomail, Mensaje, Destinatario
from .forms import ServerForm, DominioForm, DogomailForm, SERVER_STEPS, DOM_STEPS
from dogoweb.settings import VERSION, ICO_OK, ICO_WARN, ICO_INFO, ICO_CRIT
import json


@login_required()
def index(request):
    return render(request, 'mail/index.html')


@login_required()
def search(request):
    if request.is_ajax() and request.method == 'POST':
        jbody = json.loads(request.body.decode(request._encoding))
    else:
        return JsonResponse({'error': "Bad request"})
    ret = Mensaje.objects.dt_filter(jbody)
    return JsonResponse(ret)


@login_required()
def blocked(request):
    return render(request, 'mail/blocked.html')


@login_required()
def queues(request):
    return render(request, 'mail/queues.html')


@login_required()
def doms(request):
    return render(request, 'mail/doms.html')


@login_required()
def mboxes(request):
    return render(request, 'mail/mboxes.html')


@login_required()
def domadm(request):
    return render(request, 'mail/domadm.html')


@login_required()
@permission_required('mail.view_servers')
def srvdash(request):
    return render(request, 'mail/srvdash.html')


@login_required()
@permission_required('mail.manage_servers')
def srvadm(request):
    return render(request, 'mail/srvadm.html')


@login_required()
@ajax_permission_required('mail.manage_servers')
def servers(request):
    if request.is_ajax() and request.method == 'POST':
        jbody = json.loads(request.body.decode(request._encoding))
    else:
        return JsonResponse({'error': "Bad request"})
    ret = Server.objects.dt_filter(jbody)
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('mail.add_server')
def server_create(request):
    ret = Server.objects.dt_create(request, ServerForm)
    ret['panel'] = 'server'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('mail.change_server')
def server_update(request, pks):
    ret = Server.objects.dt_update(pks, request, ServerForm)
    ret['panel'] = 'server'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('mail.delete_server')
def server_delete(request, pks):
    ret = Server.objects.dt_delete(pks, request, ServerForm)
    ret['panel'] = 'server'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('mail.manage_domains')
def domains(request):
    if request.is_ajax() and request.method == 'POST':
        jbody = json.loads(request.body.decode(request._encoding))
    else:
        return JsonResponse({'error': "Bad request"})
    ret = Dominio.objects.dt_filter(jbody)
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('mail.add_domain')
def domain_create(request):
    ret = Dominio.objects.dt_wizard(request, DOM_STEPS)
    ret['panel'] = 'dominio'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('mail.add_domain')
def domain_smail(request):
    ret = Dominio.objects.dt_wizard(request, DOM_STEPS)
    # enviar correo
    if request.POST.get('mprueba', '') != '':
        pass
    ret['panel'] = 'dominio'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('mail.change_domain')
def domain_update(request, pks):
    ret = Dominio.objects.dt_update(pks, request, DominioForm)
    ret['panel'] = 'dominio'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('mail.delete_domain')
def domain_delete(request, pks):
    ret = Dominio.objects.dt_delete(pks, request, DominioForm)
    ret['panel'] = 'dominio'
    return JsonResponse(ret)


@login_required()
@permission_required('mail.view_dogomail')
def dogoadm(request):
    return render(request, 'mail/dogoadm.html')


@login_required()
@ajax_permission_required('mail.view_dogomail')
def dogos(request):
    if request.is_ajax() and request.method == 'POST':
        jbody = json.loads(request.body.decode(request._encoding))
    else:
        return JsonResponse({'error': "Bad request"})
    ret = Dogomail.objects.dt_filter(jbody)
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('mail.add_server')
def dogo_create(request):
    ret = Dogomail.objects.dt_create(request, DogomailForm)
    ret['panel'] = 'dogo'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('mail.change_server')
def dogo_update(request, pks):
    ret = Dogomail.objects.dt_update(pks, request, DogomailForm)
    ret['panel'] = 'dogo'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('mail.delete_server')
def dogo_delete(request, pks):
    ret = Dogomail.objects.dt_delete(pks, request, DogomailForm)
    ret['panel'] = 'dogo'
    return JsonResponse(ret)
