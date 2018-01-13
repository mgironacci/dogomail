# -*- coding: UTF-8 -*-
from django.db import models
from django.contrib.auth.models import User, Permission
from dogoweb.settings import VERSION
from django.utils import timezone
import hashlib
import datetime
import urllib.request
import json

# Modelo de visualizacion ----------------------------------------------

class Control(models.Model):
    idm = models.CharField(max_length=50)
    nombre = models.CharField(max_length=50)
    permiso = models.ForeignKey(Permission, on_delete=models.PROTECT)
    activo = models.BooleanField(default=True)

    def __repr__(self):
        return '<Control: nombre="%s">' % self.nombre

    def __str__(self):
        return self.nombre


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
    # objects=MenuManager()

    idm = models.CharField(max_length=50)
    nombre = models.CharField(max_length=50, unique=True)
    orden = models.PositiveIntegerField()
    icono = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["orden"]

    def __repr__(self):
        return '<Menu: nombre="%s">' % self.nombre

    def __str__(self):
        return self.nombre

        # class Meta:
        #		permissions = (
        #			("can_login", "Can login"),
        #		)

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
    # objects = PantallaManager()

    idm = models.CharField(max_length=50)
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
    gravatar = models.CharField(max_length=32, default=None)
    fgravatar = models.CharField(max_length=100, default=None)
    cgravatar = models.CharField(max_length=7, default=None)
    last_gravatar = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    def version(self):
        return VERSION

    def mis_menus(self):
        ret = []
        if self.user.is_superuser:
            menus = Menu.objects.filter(activo=True)
        else:
            # TODO: usar permisos de usuarios para obtener pantallas
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
        return True

    def spam_rejected(self):
        return str(0)

    def good_received(self):
        return str(0)