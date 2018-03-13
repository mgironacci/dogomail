from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required, permission_required
from seg.views import ajax_permission_required
from .models import Modulo
from .forms import ModuloForm
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
@ajax_permission_required('seg.add_modulo')
def module_create(request):
    ret = Modulo.objects.dt_create(request, ModuloForm)
    ret['panel'] = 'modulo'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('seg.change_modulo')
def module_update(request, pks):
    ret = Modulo.objects.dt_update(pks, request, ModuloForm)
    ret['panel'] = 'modulo'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('seg.delete_modulo')
def module_delete(request, pks):
    ret = Modulo.objects.dt_delete(pks, request, ModuloForm)
    ret['panel'] = 'modulo'
    return JsonResponse(ret)


@login_required()
def policies(request):
    return render(request, 'spam/policies.html')


@login_required()
def rules(request):
    return render(request, 'spam/rules.html')


@login_required()
def config(request):
    return render(request, 'spam/config.html')
