from django.shortcuts import render
from django.contrib.auth.decorators import login_required


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
def modules(request):
    return render(request, 'spam/modules.html')


@login_required()
def policies(request):
    return render(request, 'spam/policies.html')


@login_required()
def rules(request):
    return render(request, 'spam/rules.html')


@login_required()
def config(request):
    return render(request, 'spam/config.html')
