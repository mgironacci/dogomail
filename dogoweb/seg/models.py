# -*- coding: UTF-8 -*-
from django.db import models
from django.db.models import Q, Count
from django.dispatch import receiver
from django.contrib.auth.models import User, Permission
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.template.loader import render_to_string
from django.utils import timezone, formats
from django.utils.translation import gettext as _
from dogoweb.settings import VERSION, ICO_OK, ICO_WARN, ICO_INFO, ICO_CRIT
import hashlib
import datetime
import urllib.request
import json
from ipwhois import IPWhois


# Utilidad para DataTables ---------------------------------------------

def html_icon(icon):
    return '<i class="%s"></i>' % icon


def html_check(check):
    ret = '<i class="icmn-checkbox-checked"></i>'
    if not check:
        ret = '<i class="icmn-checkbox-unchecked"></i>'
    return ret


def html_estado(stat, disp):
    ESTADOS = {
        # base
        'success': 'success',
        'primary': 'primary',
        'secundary': 'secundary',
        'info': 'info',
        'warning': 'warning',
        'critical': 'critical',
        'default': 'default',
        # propios
        'normal': 'success',
        'down': 'secondary',
        'ok': 'success',
        'disabled': 'default',
    }
    ret = '<span class="label label-%s">%s</span>' % (ESTADOS[stat], disp)
    return ret


def html_link(link):
    if link[0:4] == 'http':
        href = link
    else:
        href = 'http://' + link
    return '<a href="%s" target="_blank">%s</a>' % (href, link)


def DTFilter(mmodel, jbody, autodata=True, filter=None, exclude=None):
    ret = {
        'draw': jbody['draw'],
        'recordsTotal': 0,
        'recordsFiltered': 0,
        'error': "",
        'data': [],
    }
    # Busqueda base con filtros de entrada
    try:
        if filter and exclude:
            bobjs = mmodel.exclude(**exclude).filter(**filter)
        elif filter:
            bobjs = mmodel.filter(**filter)
        elif exclude:
            bobjs = mmodel.exclude(**exclude)
        else:
            bobjs = mmodel.all()
        ret['recordsTotal'] = bobjs.count()
        ret['recordsFiltered'] = ret['recordsTotal']
    except Exception as e:
        ret['error'] = str(e)
        if autodata:
            return ret
        return ret, []
    # Reviso si hay una busqueda general y la refino
    if jbody['search']['value'] and len(jbody['search']['value']) >= 2:
        # Busco columnas buscables
        cbuscar = []
        for cc in jbody['columns']:
            if cc['searchable']:
                if cc['name'].count('+') == 0:
                    cbuscar.append(cc['name'] + "__icontains")
                elif cc['name'].count('+') == 1:
                    fkn = False
                    tipo, campo = cc['name'].split('+')
                elif cc['name'].count('+') == 2:
                    tipo, campo, fkn = cc['name'].split('+')
                else:
                    continue
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
    # Busco si es por columna
    elif 'colsearch' in jbody and jbody['colsearch']:
        # Busco columnas buscables
        cbuscar = []
        crelate = []
        cpfetch = []
        for cc in jbody['columns']:
            if cc['searchable']:
                if cc['search']['value'] == '':
                    continue
                if cc['name'].count('+') == 0:
                    cbuscar.append((cc['name'] + "__icontains", cc['search']['value']))
                    continue
                elif cc['name'].count('+') == 1:
                    fkn = False
                    tipo, campo = cc['name'].split('+')
                elif cc['name'].count('+') == 2:
                    tipo, campo, fkn = cc['name'].split('+')
                else:
                    continue
                if tipo == 'fks':
                    cbuscar.append((campo.replace("_set", "") + "__" + fkn + "__icontains", cc['search']['value']))
                    cpfetch.append(campo)
                elif tipo == 'cho' or tipo == 'choh':
                    cbuscar.append((campo, cc['search']['value']))
                elif tipo == 'hb': # Tratamiento de entero
                    imin, imax = str(cc['search']['value']).split("|")
                    if imin != '' and imax != '':
                        cbuscar.append((campo + "__range", (imin,imax)))
                    elif imin != '':
                        cbuscar.append((campo + "__gte", imin))
                    elif imax != '':
                        cbuscar.append((campo + "__lte", imax))
                elif str(cc['search']['value']).find("|") >= 0: # Tratamiento de entero/fecha
                    imin, imax = str(cc['search']['value']).split("|")
                    if imin != '' and imax != '':
                        cbuscar.append((campo + "__range", (imin,imax)))
                    elif imin != '':
                        cbuscar.append((campo + "__gte", imin))
                    elif imax != '':
                        cbuscar.append((campo + "__lte", imax))
        if 'colhidden' in jbody:
            for ch in jbody['colhidden']:
                if str(ch[1]).find("|") >= 0:
                    imin, imax = str(ch[1]).split("|")
                    if imin != '' and imax != '':
                        cbuscar.append((ch[0] + "__range", (imin, imax)))
                    elif imin != '':
                        cbuscar.append((ch[0] + "__gte", imin))
                    elif imax != '':
                        cbuscar.append((ch[0] + "__lte", imax))
                else:
                    cbuscar.append((ch[0], ch[1]))
        cfiltro = None
        for cr in crelate:
            bobjs = bobjs.select_related(cr)
        for cr in cpfetch:
            bobjs = bobjs.prefetch_related(cr)
        for cf in cbuscar:
            fkw = {cf[0]: cf[1]}
            if cfiltro:
                cfiltro &= Q(**fkw)
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
            if jbody['columns'][jbody['order'][0]['column']]['orderable']:
                if jbody['order'][0]['dir'] == 'asc':
                    direc = ""
                else:
                    direc = "-"
                if campo.find('+') > 0:
                    if campo.count('+') == 1:
                        fko = False
                        tipo, subcampo = campo.split('+')
                    elif campo.count('+') == 2:
                        tipo, subcampo, fko = campo.split('+')
                    if tipo == 'count':
                        sobjs = sobjs.annotate(ord_count=Count(subcampo.replace('_set','')))
                        campo = 'ord_count'
                    elif tipo == 'fk':
                        if fko:
                            campo = "%s__%s" % (subcampo,fko)
                        else:
                            campo = subcampo
                    elif tipo == 'perm':
                        campo = "%s__name" % subcampo
                    else:
                        campo = subcampo
                    oobjs = sobjs.order_by(direc+campo)
                else:
                    oobjs = sobjs.order_by(direc+campo)
            else:
                oobjs = sobjs
        except Exception as e:
            ret['error'] = str(e)
            if autodata:
                return ret
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

    # Transformo en arreglo los objetos si autodata es true
    if autodata:
        for o in fobjs:
            ao = [o.id, ]
            for cc in jbody['columns']:
                ccn = cc['name']
                if cc['name'] == 'id': continue
                # Si no tiene _ es nombre directo
                if ccn.find("+") == -1:
                    ao.append(getattr(o, ccn))
                    continue
                if ccn.count('+') == 1:
                    fko = False
                    tipo, ccn = ccn.split('+')
                elif ccn.count('+') == 2:
                    tipo, ccn, fko = ccn.split('+')
                else:
                    ao.append("invalid")
                    continue
                # En base al prefijo, armo conversion
                if tipo == 'ico':
                    ao.append(html_icon(getattr(o, ccn)))
                elif tipo == 'int':
                    ao.append(getattr(o, ccn))
                elif tipo == 'check':
                    ao.append(html_check(getattr(o, ccn)))
                elif tipo == 'est':
                    ao.append(html_estado(getattr(o, ccn), getattr(o, 'get_%s_display' % ccn)()))
                elif tipo == 'cho':
                    ao.append(getattr(o, 'get_%s_display' % ccn)())
                elif tipo == 'choh':
                    ao.append(getattr(o, 'get_%s_html' % ccn)())
                elif tipo == 'link':
                    ao.append(html_link(getattr(o, ccn)))
                elif tipo == 'fk':
                    if fko:
                        ao.append(getattr(getattr(o, ccn),fko))
                    else:
                        ao.append(str(getattr(o, ccn)))
                elif tipo == 'perm':
                    ao.append(getattr(o, ccn).name)
                elif tipo == 'count':
                    ao.append(str(getattr(o, ccn).count()))
                elif tipo == 'fks':
                    if fko:
                        svals = [getattr(svo, fko) for svo in getattr(o, ccn).all()]
                    else:
                        svals = [str(svo) for svo in getattr(o, ccn).all()]
                    ao.append(" ".join(svals))
                elif tipo == 'hb':
                    val = int(getattr(o, ccn))
                    suf = ''
                    if val >= 10485760:
                        val /= (1048576)
                        suf = ' M'
                    elif val >= 10240:
                        val /= 1024
                        suf = ' K'
                    ao.append(str(int(val)) + suf)
                elif tipo=='date':
                    ao.append(formats.date_format(getattr(o, ccn), format='SHORT_DATE_FORMAT'))
                elif tipo=='datetime':
                    ao.append(formats.date_format(getattr(o, ccn), format='SHORT_DATETIMESEC_FORMAT'))

            ret['data'].append(ao)
        return ret

    return ret, fobjs


def DTCreate(request, oform, otemplate='seg/modal_form_create.html', *args, **kw):
    data = dict()
    if request.method == 'POST':
        data['snext'] = request.POST.get('snext', '')
        form = oform(request.POST)
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            if data['snext'] == 'new':
                form = oform()
            data['mensaje'] = {
                'icon': ICO_OK,
                'msg': _('The item was successfully created'),
                'tipo': 'success',
            }
        else:
            data['form_is_valid'] = False
            data['mensaje'] = {
                'icon': ICO_CRIT,
                'msg': _('The item had a problem, please review'),
                'tipo': 'danger',
            }
    else:
        form = oform()
    context = {'form': form, 'form_header': oform.form_header}
    data['html_form'] = render_to_string(otemplate, context, request=request)
    return data


def DTShow(mmodel, pks, request, oform, otemplate='seg/modal_form_show.html', *args, **kw):
    data = dict()
    if request.method == 'POST':
        data['snext'] = request.POST.get('snext', '')
        idpks = request.POST.get('pks', '').split(',')
        obj = mmodel.get(pk=idpks[0])
        form = oform(request.POST, instance=obj)
        context = {'idpks': pks, 'form': form, 'form_header': oform.form_header}
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
    else:
        idpks = pks.split(',')
        obj = mmodel.get(pk=idpks[0])
        form = oform(instance=obj)
        context = {'idpks': pks, 'form': form, 'form_header': oform.form_header}
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


def DTUpdate(mmodel, pks, request, oform, otemplate='seg/modal_form_update.html', *args, **kw):
    data = dict()
    if request.method == 'POST':
        data['snext'] = request.POST.get('snext', '')
        idpks = request.POST.get('pks', '').split(',')
        obj = mmodel.get(pk=idpks[0])
        form = oform(request.POST, instance=obj)
        context = {'idpks': pks, 'form': form, 'form_header': oform.form_header}
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
            data['mensaje'] = {
                'icon': ICO_OK,
                'msg': _('The item was successfully saved'),
                'tipo': 'success',
            }
        else:
            data['form_is_valid'] = False
            data['mensaje'] = {
                'icon': ICO_CRIT,
                'msg': _('The item had a problem, please review'),
                'tipo': 'danger',
            }
    else:
        idpks = pks.split(',')
        obj = mmodel.get(pk=idpks[0])
        form = oform(instance=obj)
        context = {'idpks': pks, 'form': form, 'form_header': oform.form_header}
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


def DTDelete(mmodel, pks, request, oform, otemplate='seg/modal_form_delete.html', *args, **kw):
    data = dict()
    if request.method == 'POST':
        idpks = request.POST.get('pks','').split(',')
        try:
            objs = mmodel.filter(id__in=idpks)
            for o in objs:
                o.delete()
            data['form_is_valid'] = True
            data['mensaje'] = {
                'icon': ICO_OK,
                'msg': _('The items where successfully deleted'),
                'tipo': 'success',
            }
        except:
            data['form_is_valid'] = False
            data['mensaje'] = {
                'icon': ICO_CRIT,
                'msg': _('There was a problem deleting the items'),
                'tipo': 'danger',
            }
            context = {'idpks': request.POST.get('pks',''), 'form_header': oform.form_header}
            data['html_form'] = render_to_string(otemplate, context, request=request)
    else:
        context = {'idpks': pks, 'form_header': oform.form_header}
        data['html_form'] = render_to_string(otemplate, context, request=request)
    return data


class DTManager(models.Manager):

    def dt_filter(self, jbody, *args, **kw):
        return DTFilter(self, jbody, *args, **kw)

    def dt_create(self, request, oform, otemplate='seg/modal_form_create.html'):
        return DTCreate(request, oform, otemplate)

    def dt_update(self, pks, request, oform, otemplate='seg/modal_form_update.html'):
        return DTUpdate(self, pks, request, oform, otemplate)

    def dt_show(self, pks, request, oform, otemplate='seg/modal_form_show.html'):
        return DTShow(self, pks, request, oform, otemplate)

    def dt_delete(self, pks, request, oform, otemplate='seg/modal_form_delete.html'):
        return DTDelete(self, pks, request, oform, otemplate)

    def dt_wizard(self, request, steps, otemplate='seg/modal_form_wizard.html'):
        data = dict()
        cstep = 0
        if request.method == 'POST':
            data['snext'] = request.POST.get('snext', '')
            cstep = int(request.POST.get('step', '0'))
            data['step'] = cstep
            oform = steps['steps'][data['step']]['form']
            form = oform(request.POST)
            if form.is_valid():
                if hasattr(form, 'save'):
                    form.save()
                cstep += 1
                data['form_is_valid'] = True
                if cstep < steps['count']:
                    data['snext'] = 'yes'
                    oform = steps['steps'][cstep]['form']
                    form = oform()
                else:
                    data['mensaje'] = {
                        'icon': ICO_OK,
                        'msg': _('The item was successfully created'),
                        'tipo': 'success',
                    }
            else:
                data['form_is_valid'] = False
                data['mensaje'] = {
                    'icon': ICO_CRIT,
                    'msg': _('The item had a problem, please review'),
                    'tipo': 'danger',
                }
        else:
            oform = steps['steps'][cstep]['form']
            form = oform()
        context = {'form': form, 'form_header': oform.form_header, 'form_steps': steps }
        if cstep < steps['count']:
            context.update({
                'cur_step': cstep,
                'cur_step_icon': steps['steps'][cstep]['icon'],
                'cur_step_title': steps['steps'][cstep]['title'],
            })
        data['html_form'] = render_to_string(otemplate, context, request=request)
        return data


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

    def __repr__(self):
        return '<Menu: nombre="%s">' % self.nombre

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ["orden"]
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

    idm = models.CharField('ID',max_length=50, unique=True)
    nombre = models.CharField('Name',max_length=50)
    url = models.CharField('URL',max_length=200)
    orden = models.PositiveIntegerField('Order')
    icono = models.CharField('Icon',max_length=100, blank=True)
    permiso = models.ForeignKey(Permission, on_delete=models.PROTECT)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    activo = models.BooleanField('Active',default=True)

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

    class Meta:
        permissions = (
            ("view_security", "View menu security"),
            ("manage_users", "Manage users and groups membership"),
            ("manage_groupperms", "Manage groups and permissions"),
            ("view_audit", "View menu audit"),
            ("manage_audit", "View global audit"),
        )

    def __str__(self):
        return self.user.username

    def version(self):
        return VERSION

    def mis_menus(self):
        ret = []
        menus = Menu.objects.filter(activo=True)
        if self.user.is_superuser:
            perms = Permission.objects.all()
        else:
            perms = self.user.user_permissions.all() | Permission.objects.filter(group__user=self.user)
        for m in menus:
            mm = {
                'nombre': m.nombre,
                'icono': m.icono,
                'pantallas': m.pantalla_set.filter(activo=True).filter(permiso__in=perms),
            }
            if mm['pantallas'].count() > 0:
                ret.append(mm)
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
            login_logout_log = LoginLogout(login_time=timezone.now(),session_key=request.session.session_key, user=user, host=request.META['REMOTE_ADDR'], provider=prov, country=pais)
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
        prov = ipr['asn_description']
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
        login_logout_logs.filter(logout_time__isnull=True).update(logout_time=timezone.now())
        if not login_logout_logs:
            login_logout_log = LoginLogout(logout_time=timezone.now(), session_key=request.session.session_key, user=user, host=request.META['REMOTE_ADDR'], provider=prov, country=pais)
            login_logout_log.save()
    except Exception as e:
        # log the error
        #error_log.error("log_user_logged_in request: %s, error: %s" % (request, e))
        pass
