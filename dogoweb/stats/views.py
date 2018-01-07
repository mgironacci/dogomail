from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from seg.models import Menu, Pantalla

@login_required()
def index(request):
    return render(request, 'stats/index.html')

@login_required()
def pizarron(request):
    vernu = '1.0'
    menu_list = Menu.objects.filter(activo = True)
    return render(request, 'stats/pizarron.html', locals())
