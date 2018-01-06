from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required()
def index(request):
    return render(request, 'stats/index.html')

@login_required()
def pizarron(request):
    vernu = '1.0'
    return render(request, 'stats/pizarron.html', locals())
