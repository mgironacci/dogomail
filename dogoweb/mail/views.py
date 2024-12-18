from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required, permission_required
from seg.views import ajax_permission_required
from .models import Server, Dominio, Dogomail, Mensaje, Destinatario
from .forms import ServerForm, DominioForm, DogomailForm, SERVER_STEPS, DOM_STEPS, SearchMailForm, MailForm
from dogoweb.settings import VERSION, ICO_OK, ICO_WARN, ICO_INFO, ICO_CRIT
import json


@login_required()
def index(request):
    form = SearchMailForm()
    return render(request, 'mail/index.html', locals())


@login_required()
def search(request):
    if request.is_ajax() and request.method == 'POST':
        jbody = json.loads(request.body.decode(request._encoding))
    else:
        return JsonResponse({'error': "Bad request"})
    jbody = Mensaje.filtro_usuario(request.user, jbody)
    ret = Mensaje.objects.dt_filter(jbody)
    return JsonResponse(ret)


@login_required()
def show(request, ids):
    ret = Mensaje.objects.dt_show(ids, request, MailForm)
    ret['panel'] = 'mail'
    return JsonResponse(ret)


@login_required()
def sendemail(request, ids):
    ret = Mensaje.cambiar_estado(ids, 'send')
    ret['panel'] = 'mail'
    return JsonResponse(ret)


@login_required()
def trashemail(request, ids):
    ret = Mensaje.cambiar_estado(ids, 'trash')
    ret['panel'] = 'mail'
    return JsonResponse(ret)


@login_required()
def blocked(request):
    form = SearchMailForm()
    return render(request, 'mail/blocked.html', locals())


@login_required()
def blocked_search(request):
    if request.is_ajax() and request.method == 'POST':
        jbody = json.loads(request.body.decode(request._encoding))
    else:
        return JsonResponse({'error': "Bad request"})
    jbody = Mensaje.filtro_usuario(request.user, jbody)
    ret = Mensaje.objects.dt_filter(jbody)
    return JsonResponse(ret)


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
    Server.sincronizar()
    return render(request, 'mail/srvadm.html')


@login_required()
@ajax_permission_required('mail.manage_servers')
def servers(request):
    if request.is_ajax() and request.method == 'POST':
        jbody = json.loads(request.body.decode(request._encoding))
    else:
        return JsonResponse({'error': "Bad request"})
    jbody = Server.filtro_usuario(request.user, jbody)
    ret = Server.objects.dt_filter(jbody)
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('mail.view_servers')
def server_show(request, pk):
    ret = {}
    try:
        obj = Server.objects.get(id=pk)
        ret.update(obj.html_show(request))
    except Exception as e:
        ret['mensaje'] = {
            'icon': ICO_CRIT,
            'msg': _('The item had a problem, please review'),
            'tipo': 'danger',
        }
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
    jbody = Dominio.filtro_usuario(request.user, jbody)
    ret = Dominio.objects.dt_filter(jbody)
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('mail.view_domains')
def domain_show(request, pk):
    ret = {}
    try:
        obj = Dominio.objects.get(id=pk)
        ret.update(obj.html_show(request))
    except Exception as e:
        ret['mensaje'] = {
            'icon': ICO_CRIT,
            'msg': _('The item had a problem, please review'),
            'tipo': 'danger',
        }
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
    # enviar correo de prueba
    mprueba = request.POST.get('mprueba', '')
    if mprueba != '':
        try:
            domnam = mprueba.split('@')[-1]
            dominio = Dominio.objects.filter(nombre=domnam)[0]
            dominio.enviarPrueba(mprueba)
        except:
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
