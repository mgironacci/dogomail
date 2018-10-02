from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required, permission_required
from seg.views import ajax_permission_required
from .models import Modulo, Politica, Listas
from .forms import ModuloForm, PoliticaForm, ListaForm
import json


@login_required()
def index(request):
    return render(request, 'spam/index.html')


@login_required()
def avirus(request):
    return render(request, 'spam/avirus.html')


@login_required()
def lists(request):
    return render(request, 'spam/lists.html')


@login_required()
@ajax_permission_required('spam.manage_listas')
def lista(request):
    if request.is_ajax() and request.method == 'POST':
        jbody = json.loads(request.body.decode(request._encoding))
    else:
        return JsonResponse({'error': "Bad request"})
    ret = Listas.objects.dt_filter(jbody)
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('spam.add_lists')
def lista_create(request):
    ret = Listas.objects.dt_create(request, ListaForm)
    ret['panel'] = 'lista'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('spam.change_lists')
def lista_update(request, pks):
    ret = Listas.objects.dt_update(pks, request, ListaForm)
    ret['panel'] = 'lista'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('spam.delete_lists')
def lista_delete(request, pks):
    ret = Listas.objects.dt_delete(pks, request, ListaForm)
    ret['panel'] = 'lista'
    return JsonResponse(ret)


@login_required()
@permission_required('spam.manage_modules')
def modules(request):
    return render(request, 'spam/modules.html')


@login_required()
@ajax_permission_required('spam.manage_modules')
def module(request):
    if request.is_ajax() and request.method == 'POST':
        jbody = json.loads(request.body.decode(request._encoding))
    else:
        return JsonResponse({'error': "Bad request"})
    ret = Modulo.objects.dt_filter(jbody)
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('spam.add_modulo')
def module_create(request):
    ret = Modulo.objects.dt_create(request, ModuloForm)
    ret['panel'] = 'modulo'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('spam.change_modulo')
def module_update(request, pks):
    ret = Modulo.objects.dt_update(pks, request, ModuloForm)
    ret['panel'] = 'modulo'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('spam.delete_modulo')
def module_delete(request, pks):
    ret = Modulo.objects.dt_delete(pks, request, ModuloForm)
    ret['panel'] = 'modulo'
    return JsonResponse(ret)


@login_required()
def policies(request):
    return render(request, 'spam/policies.html')


@login_required()
@ajax_permission_required('spam.manage_politicas')
def policy(request):
    if request.is_ajax() and request.method == 'POST':
        jbody = json.loads(request.body.decode(request._encoding))
    else:
        return JsonResponse({'error': "Bad request"})
    ret = Politica.objects.dt_filter(jbody)
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('spam.add_politica')
def policy_create(request):
    ret = Politica.objects.dt_create(request, PoliticaForm)
    ret['panel'] = 'politica'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('spam.change_politica')
def policy_update(request, pks):
    ret = Politica.objects.dt_update(pks, request, PoliticaForm)
    ret['panel'] = 'politica'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('spam.delete_politica')
def policy_delete(request, pks):
    ret = Politica.objects.dt_delete(pks, request, PoliticaForm)
    ret['panel'] = 'politica'
    return JsonResponse(ret)


@login_required()
def rules(request):
    return render(request, 'spam/rules.html')


@login_required()
def config(request):
    return render(request, 'spam/config.html')
