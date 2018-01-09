from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

@login_required()
def index(request):
    return render(request, 'seg/index.html')

@login_required()
def audit(request):
    return render(request, 'seg/audit.html')
