from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required, permission_required
from seg.views import ajax_permission_required
from .models import Modulo, Politica, Listas, AutoReglas, Regla
from .forms import ModuloForm, PoliticaForm, ListaForm, AutoReglasSearchForm, ListaSearchForm, ReglasSearchForm, ReglaForm
import json


@login_required()
def index(request):
    return render(request, 'spam/index.html')


@login_required()
def avirus(request):
    return render(request, 'spam/avirus.html')


@login_required()
def lists(request):
    form = ListaSearchForm()
    return render(request, 'spam/lists.html', locals())


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
@ajax_permission_required('spam.add_listas')
def lista_create(request):
    ret = Listas.objects.dt_create(request, ListaForm)
    ret['panel'] = 'lista'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('spam.change_listas')
def lista_update(request, pks):
    ret = Listas.objects.dt_update(pks, request, ListaForm)
    ret['panel'] = 'lista'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('spam.delete_listas')
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
    form = ReglasSearchForm()
    return render(request, 'spam/rules.html', locals())


@login_required()
def rules_search(request):
    if request.is_ajax() and request.method == 'POST':
        jbody = json.loads(request.body.decode(request._encoding))
    else:
        return JsonResponse({'error': "Bad request"})
    jbody = Regla.filtro_usuario(request.user, jbody)
    ret = Regla.objects.dt_filter(jbody)
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('spam.add_regla')
def rules_create(request):
    ret = Regla.objects.dt_create(request, ReglaForm)
    ret['panel'] = 'regla'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('spam.change_regla')
def rules_update(request, pks):
    ret = Regla.objects.dt_update(pks, request, ReglaForm)
    ret['panel'] = 'regla'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('spam.delete_regla')
def rules_delete(request, pks):
    ret = Regla.objects.dt_delete(pks, request, ReglaForm)
    ret['panel'] = 'regla'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('spam.change_regla')
def rules_up(request, ids):
    ret = Regla.ordenar('up', ids)
    ret['panel'] = 'regla'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('spam.change_regla')
def rules_down(request, ids):
    ret = Regla.ordenar('down', ids)
    ret['panel'] = 'regla'
    return JsonResponse(ret)


@login_required()
def autorules(request):
    form = AutoReglasSearchForm()
    return render(request, 'spam/autorules.html', locals())


@login_required()
def autorulesp(request):
    form = AutoReglasSearchForm()
    return render(request, 'spam/autorulesp.html', locals())


@login_required()
def autorules_search(request):
    if request.is_ajax() and request.method == 'POST':
        jbody = json.loads(request.body.decode(request._encoding))
    else:
        return JsonResponse({'error': "Bad request"})
    ret = AutoReglas.objects.dt_filter(jbody)
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('spam.manage_autorules')
def autorules_confirm(request, ids):
    ret = AutoReglas.set_confirmed(ids)
    ret['panel'] = 'autorule'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('spam.manage_autorules')
def autorules_ignore(request, ids):
    ret = AutoReglas.set_ignored(ids)
    ret['panel'] = 'autorule'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('spam.manage_autorules')
def autorules_show(request, ids):
    ret = AutoReglas.html_show(ids, request)
    ret['panel'] = 'autorule'
    return JsonResponse(ret)


@login_required()
def config(request):
    return render(request, 'spam/config.html')
