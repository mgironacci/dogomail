# -*- coding: UTF-8 -*-
from django.db import models
from django.db.models import Q
from django.dispatch import receiver
from django.contrib.auth.models import User, Permission
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.template.loader import render_to_string
from dogoweb.settings import VERSION
from django.utils import timezone
import hashlib
import datetime
import urllib.request
import json
from ipwhois import IPWhois


# Utilidad para DataTables ---------------------------------------------

def DTFilter(mmodel, jbody, *args, **kw):
    ret = {
        'draw': jbody['draw'],
        'recordsTotal': 0,
        'recordsFiltered': 0,
        'error': "",
        'data': [],
    }
    # Busqueda base con filtros de entrada
    try:
        bobjs = mmodel.filter(*args, **kw)
        ret['recordsTotal'] = bobjs.count()
        ret['recordsFiltered'] = ret['recordsTotal']
    except Exception as e:
        ret['error'] = str(e)
        return ret, []
    # Reviso si hay una busqueda general y la refino
    if jbody['search']['value'] and len(jbody['search']['value']) >= 2:
        # Busco columnas buscables
        cbuscar = []
        for cc in jbody['columns']:
            if cc['searchable']:
                cbuscar.append(cc['name'] + "__icontains")
        cfiltro = None
        for cf in cbuscar:
            fkw = {cf: jbody['search']['value']}
            if cfiltro:
                cfiltro |= Q(**fkw)
            else:
                cfiltro = Q(**fkw)
        # Armo filtro
        if cfiltro:
            sobjs = bobjs.filter(cfiltro)
            ret['recordsFiltered'] = sobjs.count()
        else:
            sobjs = bobjs
    else:
        sobjs = bobjs

    # Ordeno
    if 'order' in jbody:
        try:
            campo = jbody['columns'][jbody['order'][0]['column']]['name']
            direc = jbody['order'][0]['dir']
            if direc == 'asc':
                oobjs = sobjs.order_by(campo)
            else:
                oobjs = sobjs.order_by("-" + campo)
        except Exception as e:
            ret['error'] = str(e)
            return ret, sobjs
    else:
        oobjs = sobjs

    # Filtro por inicio y largo
    try:
        st = jbody['start']
        lt = jbody['length']
        fobjs = oobjs[st:st+lt]
    except Exception as e:
        ret['error'] = str(e)
        fobjs = oobjs

    return ret, fobjs


def DTCreate(request, oform, otemplate, *args, **kw):
    data = dict()
    if request.method == 'POST':
        data['snext'] = request.POST.get('snext', '')
        form = oform(request.POST)
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            if data['snext'] == 'new':
                form = oform()
        else:
            data['form_is_valid'] = False
    else:
        form = oform()
    context = {'form': form}
    data['html_form'] = render_to_string(otemplate, context, request=request)
    return data


def DTUpdate(mmodel, pks, request, oform, otemplate, *args, **kw):
    data = dict()
    if request.method == 'POST':
        data['snext'] = request.POST.get('snext', '')
        idpks = request.POST.get('pks', '').split(',')
        obj = mmodel.get(pk=idpks[0])
        form = oform(request.POST, instance=obj)
        context = {'idpks': pks, 'form': form}
        if len(idpks) > 1:
            otros = {}
            for n,v in enumerate(idpks):
                otros[idpks[n]] = idpks[n:] + idpks[0:n]
            context['inext'] = ','.join(otros[idpks[1]])
            context['iprev'] = ','.join(otros[idpks[-1]])
            context['sobjs'] = []
            for i in idpks:
                o = mmodel.get(pk=i)
                context['sobjs'].append({'ids': ','.join(otros[str(o.id)]), 'obj': str(o)})
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    else:
        idpks = pks.split(',')
        obj = mmodel.get(pk=idpks[0])
        form = oform(instance=obj)
        context = {'idpks': pks, 'form': form}
        if len(idpks) > 1:
            otros = {}
            for n,v in enumerate(idpks):
                otros[idpks[n]] = idpks[n:] + idpks[0:n]
            context['inext'] = ','.join(otros[idpks[1]])
            context['iprev'] = ','.join(otros[idpks[-1]])
            context['sobjs'] = []
            for i in idpks:
                o = mmodel.get(pk=i)
                context['sobjs'].append({'ids': ','.join(otros[str(o.id)]), 'obj': str(o)})
    data['html_form'] = render_to_string(otemplate, context, request=request)
    return data


def DTDelete(mmodel, pks, request, oform, otemplate, *args, **kw):
    data = dict()
    if request.method == 'POST':
        idpks = request.POST.get('pks','').split(',')
        try:
            objs = mmodel.filter(id__in=idpks)
            for o in objs:
                o.delete()
            data['form_is_valid'] = True
        except:
            data['form_is_valid'] = False
    else:
        context = {'idpks': pks}
        data['html_form'] = render_to_string(otemplate, context, request=request)
    return data

class DTManager(models.Manager):

    def dt_filter(self, jbody, *args, **kw):
        return DTFilter(self, jbody, *args, **kw)

    def dt_create(self, request, oform, otemplate):
        return DTCreate(request, oform, otemplate)

    def dt_update(self, pks, request, oform, otemplate):
        return DTUpdate(self, pks, request, oform, otemplate)

    def dt_delete(self, pks, request, oform, otemplate):
        return DTDelete(self, pks, request, oform, otemplate)


# Modelo de visualizacion ----------------------------------------------


# class MenuManager(models.Manager):
# 	def select_list(self):
# 		tl=[(yo.id, yo.nombre) for yo in self.select(orderBy=self.q.nombre)]
# 		return tl
#
# 	def select_list_nil(self):
# 		tl=self.select_list()
# 		tl.insert(0, (0, _('Not specified')))
# 		return tl
#
# 	def mi_select(self, yo):
# 		mi_perms=yo.get_all_permissions()
# 		pants=[]
# 		for pp in Pantalla.objects.all():
# 			if pp.permiso is None:
# 				pants.append(pp)
# 				continue
# 			mp=pp.permiso.content_type.app_label+'.'+pp.permiso.codename
# 			if mp in mi_perms:
# 				pants.append(pp)
# 		if len(pants)==0:
# 			return []
# 		return [m for m in Menu.objects.filter(id__in=[p.menu.id for p in pants]).filter(activo=True).order_by('orden')]


class Menu(models.Model):
    objects=DTManager()

    idm = models.CharField('ID', max_length=50, unique=True)
    nombre = models.CharField('Name', max_length=50, unique=True)
    orden = models.PositiveIntegerField('Order')
    icono = models.CharField('Icon', max_length=100, blank=True)
    activo = models.BooleanField('Active', default=True)

    class Meta:
        ordering = ["orden"]

    def __repr__(self):
        return '<Menu: nombre="%s">' % self.nombre

    def __str__(self):
        return self.nombre

    class Meta:
        permissions = (
            ("manage_menus", "Manage menus"),
        )


# class PantallaManager(models.Manager):
# 	def mi_select(self, yo, selmenu=None):
# 		if selmenu is None:
# 			return []
# 		mi_perms=yo.get_all_permissions()
# 		pants=[]
# 		m=Menu.objects.get(idm=selmenu)
# 		for pp in Pantalla.objects.filter(menu=m).filter(activo=True).order_by('orden'):
# 			if pp.permiso is None:
# 				pants.append(pp)
# 				continue
# 			mp=pp.permiso.content_type.app_label+'.'+pp.permiso.codename
# 			if mp in mi_perms:
# 				pants.append(pp)
# 		return pants


class Pantalla(models.Model):
    objects=DTManager()

    idm = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=50)
    url = models.CharField(max_length=200)
    orden = models.PositiveIntegerField()
    icono = models.CharField(max_length=100)
    permiso = models.ForeignKey(Permission, on_delete=models.PROTECT)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["orden"]

    def __repr__(self):
        return '<Pantalla: nombre="%s">' % self.nombre

    def __str__(self):
        return self.nombre


# Perfil de usuario ----------------------------------------------------

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gravatar = models.CharField(max_length=32, default='')
    fgravatar = models.CharField(max_length=100, default='')
    cgravatar = models.CharField(max_length=7, default='')
    last_gravatar = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username

    def version(self):
        return VERSION

    def mis_menus(self):
        ret = []
        if self.user.is_superuser:
            menus = Menu.objects.filter(activo=True)
        else:
            # TODO: filtro en base a permisos del usuario
            menus = Menu.objects.filter(activo=True)
        for m in menus:
            ret.append({
                'nombre': m.nombre,
                'icono': m.icono,
                'pantallas': m.pantalla_set.filter(activo=True),
            })
        return ret

    def mi_avatar(self):
        if self.user.is_superuser:
            return "/static/dogoweb/img/dogoadmin.png"
        elif self.user.is_staff:
            ret = "/static/dogoweb/img/dogostaff.png"
        else:
            ret = "/static/dogoweb/img/dogouser.png"
        # Reviso si hay gravatar
        if self.gravatar:
            ret = "https://www.gravatar.com/avatar/" + self.gravatar
        elif (self.last_gravatar < timezone.now() - datetime.timedelta(minutes=10)
              and self.gravatar == ''):
            try:
                grahash = hashlib.md5(self.user.username.lower().encode("utf8")).hexdigest()
                graurl = "https://www.gravatar.com/avatar/" + grahash
                urllib.request.urlopen(graurl + "?d=404")
                ret = graurl
                self.gravatar = grahash
            except:
                pass
            self.last_gravatar = timezone.now()
            self.save()
        return ret

    def mi_fondo(self):
        ret = ""
        # Reviso si hay gravatar
        if self.fgravatar:
            ret = self.fgravatar
        elif self.gravatar:
            try:
                gprof = urllib.request.urlopen("https://www.gravatar.com/" + self.gravatar + ".json")
                pback = json.loads(gprof.read().decode(gprof.info().get_content_charset('utf-8')))["entry"][0]["profileBackground"]
                ret = pback["url"]
                self.fgravatar = ret
                self.cgravatar = pback["color"]
                self.save()
            except:
                pass
        return ret

    def mi_color(self):
        ret = "#aaaaaa"
        # Reviso si hay gravatar
        if self.cgravatar:
            ret = self.cgravatar
        return ret

    def esta_online(self):
        accesos = LoginLogout.objects.filter(user=self.user).filter(logout_time=None)
        if len(accesos) > 0:
            return True
        return False

    def spam_rejected(self):
        return str(0)

    def good_received(self):
        return str(0)


# Registro de actividades ----------------------------------------------

class LoginLogout(models.Model):
    objects = DTManager()

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=100, blank=False, null=False)
    login_time = models.DateTimeField(blank=True, null=True)
    logout_time = models.DateTimeField(blank=True, null=True)
    host = models.CharField(max_length=100, blank=False, null=False)
    provider = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        ordering = ["-login_time"]

    def __str__(self):
        return "Login " + self.user.username + ": " + str(self.login_time)


@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    pais = 'yo'
    prov = ''
    # Busco en el whois
    try:
        ipw = IPWhois(request.META['REMOTE_ADDR'])
        ipr = ipw.lookup_rdap(depth=1)
        pais = ipr['asn_country_code']
        prov = ipr['asn_description']
    except Exception as e:
        pass
    # Veo si puedo mejorar el proveedor
    try:
        if len(ipr['entities']) > 0:
            for e in ipr['entities']:
                if ipr['objects'][e]['contact']:
                    prov = ipr['objects'][e]['contact']['name']
                    break
    except:
        pass
    # Registro el ingreso
    try:
        login_logout_logs = LoginLogout.objects.filter(session_key=request.session.session_key, user=user.id)[:1]
        if not login_logout_logs:
            login_logout_log = LoginLogout(login_time=datetime.datetime.now(),session_key=request.session.session_key, user=user, host=request.META['REMOTE_ADDR'], provider=prov, country=pais)
            login_logout_log.save()
    except Exception as e:
        # log the error
        #error_log.error("log_user_logged_in request: %s, error: %s" % (request, e))
        pass


@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):
    pais = 'yo'
    prov = ''
    # Busco en el whois
    try:
        ipw = IPWhois(request.META['REMOTE_ADDR'])
        ipr = ipw.lookup_rdap(depth=1)
        pais = ipr['asn_country_code']
        prov = ips['asn_description']
    except Exception as e:
        pass
    # Veo si puedo mejorar el proveedor
    try:
        if len(ipr['entities']) > 0:
            for e in ipr['entities']:
                if e['contact']:
                    prov = e['contact']['name']
                    break
    except:
        pass
    # Registro el ingreso
    try:
        login_logout_logs = LoginLogout.objects.filter(session_key=request.session.session_key, user=user.id, host=request.META['REMOTE_ADDR'])
        login_logout_logs.filter(logout_time__isnull=True).update(logout_time=datetime.datetime.now())
        if not login_logout_logs:
            login_logout_log = LoginLogout(logout_time=datetime.datetime.now(), session_key=request.session.session_key, user=user, host=request.META['REMOTE_ADDR'], provider=prov, country=pais)
            login_logout_log.save()
    except Exception as e:
        # log the error
        #error_log.error("log_user_logged_in request: %s, error: %s" % (request, e))
        pass
