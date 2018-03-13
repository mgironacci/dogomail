from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required, permission_required
from seg.views import ajax_permission_required
from .models import Cliente
from .forms import ClienteForm
import json


@login_required()
def index(request):
    return render(request, 'erp/index.html')


@login_required()
@ajax_permission_required('spam.manage_modules')
def clientes(request):
    if request.is_ajax() and request.method == 'POST':
        jbody = json.loads(request.body.decode(request._encoding))
    else:
        return JsonResponse({'error': "Bad request"})
    ret = Cliente.objects.dt_filter(jbody)
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('seg.add_cliente')
def cliente_create(request):
    ret = Cliente.objects.dt_create(request, ClienteForm)
    ret['panel'] = 'cliente'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('seg.change_cliente')
def cliente_update(request, pks):
    ret = Cliente.objects.dt_update(pks, request, ClienteForm)
    ret['panel'] = 'cliente'
    return JsonResponse(ret)


@login_required()
@ajax_permission_required('seg.delete_cliente')
def cliente_delete(request, pks):
    ret = Cliente.objects.dt_delete(pks, request, ClienteForm)
    ret['panel'] = 'cliente'
    return JsonResponse(ret)
