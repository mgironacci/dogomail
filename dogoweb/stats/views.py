from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from seg.models import Menu, Pantalla, json4stats
from seg.views import ajax_permission_required
from stats.models import DogoStat


@login_required()
def index(request):
    return render(request, 'stats/index.html')


@login_required()
def pizarron(request):
    vernu = '1.0'
    menu_list = Menu.objects.filter(activo = True)
    return render(request, 'stats/pizarron.html', locals())


@login_required()
def dogo_grafs(request):
    if request.is_ajax() and request.method == 'POST':
        jbody = json4stats(request)
    else:
        return JsonResponse({'error': "Bad request"})
    jbody = DogoStat.filtro_usuario(request.user, jbody)
    ret = DogoStat.get_stats(jbody)
    return JsonResponse(ret)


@login_required()
def dogo_tops(request):
    if request.is_ajax() and request.method == 'POST':
        jbody = json4stats(request)
    else:
        return JsonResponse({'error': "Bad request"})
    jbody = DogoStat.filtro_usuario(request.user, jbody)
    ret = DogoStat.get_tops(jbody)
    return JsonResponse(ret)


@login_required()
def dogo_topr(request):
    if request.is_ajax() and request.method == 'POST':
        jbody = json4stats(request)
    else:
        return JsonResponse({'error': "Bad request"})
    jbody = DogoStat.filtro_usuario(request.user, jbody)
    ret = DogoStat.get_topr(jbody)
    return JsonResponse(ret)

