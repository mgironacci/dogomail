from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from seg.models import LoginLogout
from ipwhois.utils import get_countries
import json

@login_required()
def index(request):
    return render(request, 'seg/index.html')


@login_required()
def audit(request):
    return render(request, 'seg/audit.html')


@login_required()
def profile(request):
    return render(request, 'seg/profile.html')

@login_required()
def accesos(request):
    if request.is_ajax() and request.method == 'POST':
        jbody = json.loads(request.body.decode('UTF8'))
    else:
        return JsonResponse({'error': "Bad request"})
    ret = {
        'draw': jbody['draw'],
        'recordsTotal': 0,
        'recordsFiltered': 0,
        'error': "",
        'data': [],
    }
    paises = get_countries()
    ret['recordsTotal'] = LoginLogout.objects.filter(user=request.user).count()
    ret['recordsFiltered'] = ret['recordsTotal']
    st = jbody['start'] - 1
    if st < 0:
        st = 0
    llog = LoginLogout.objects.filter(user=request.user)[st:jbody['length']]
    for a in llog:
        pais = ""
        flag = ""
        if a.country == 'yo':
            pais = "Local"
        elif a.country in paises:
            pais = paises[a.country]
            flag = "&nbsp;&nbsp;<img src='/static/cleanui/flags/png100px/%s.png' height='16px'/>" % a.country.lower()
        li = ""
        if a.login_time:
            li = timezone.localtime(a.login_time).strftime('%Y-%m-%d %X')
        if a.logout_time:
            lo= timezone.localtime(a.logout_time).strftime('%Y-%m-%d %X')
        else:
            sesiones = Session.objects.filter(session_key=a.session_key)
            if len(sesiones) > 0:
                lo = _("Still logged in")
            else:
                lo = _("Expired")
        ret['data'].append([li, lo, a.host, a.provider, pais + flag])
    return JsonResponse(ret)
