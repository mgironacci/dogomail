# -*- coding: UTF-8 -*-
from django.db import models
from django.contrib.auth.models import Permission

# Modelo de visualizacion ----------------------------------------------

class Control(models.Model):
    idm = models.CharField(max_length=50)
    nombre = models.CharField(max_length=50)
    permiso = models.ForeignKey(Permission)
    activo = models.BooleanField(default=True)


    def __repr__(self):
        return '<Control: nombre="%s">' % self.nombre

    def __unicode__(self):
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
    #objects=MenuManager()

    idm = models.CharField(max_length=50)
    nombre = models.CharField(max_length=50, unique=True)
    url = models.CharField(max_length=200)
    url_base = models.CharField(max_length=200)
    orden = models.PositiveIntegerField()
    icono = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)

    def __repr__(self):
        return '<Menu: nombre="%s">' % self.nombre

    def __unicode__(self):
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
    #objects = PantallaManager()

    idm = models.CharField(max_length=50)
    nombre = models.CharField(max_length=50)
    url = models.CharField(max_length=200)
    orden = models.PositiveIntegerField()
    icono = models.CharField(max_length=100)
    permiso = models.ForeignKey(Permission)
    menu = models.ForeignKey(Menu)
    activo = models.BooleanField(default=True)

    def __repr__(self):
        return '<Pantalla: nombre="%s">' % self.nombre

    def __unicode__(self):
        return self.nombre
