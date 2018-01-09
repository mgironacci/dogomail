from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required()
def index(request):
    return render(request, 'mail/index.html')

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
def srvdash(request):
    return render(request, 'mail/srvdash.html')

@login_required()
def srvadm(request):
    return render(request, 'mail/srvadm.html')
