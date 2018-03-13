from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _
from seg.models import DTManager


# Modelo de modulos
class Modulo(models.Model):
    objects=DTManager()

    nombre = models.CharField('Name', max_length=50, unique=True)
    activo = models.BooleanField('Active', default=True)
    config = models.TextField('Configuration', default='')

    def __repr__(self):
        return '<Modulo: nombre="%s">' % self.nombre

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ["nombre"]
        permissions = (
            ("view_modules", "View menu modules"),
            ("manage_modules", "Manage modules"),
        )

    def probar(self, datos):
        return False


# Modelo de politicas
class Politica(models.Model):
    objects=DTManager()

    nombre = models.CharField('Name', max_length=50, unique=True)
    activo = models.BooleanField('Active', default=True)

    def __repr__(self):
        return '<Politica: nombre="%s">' % self.nombre

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ["nombre"]
        permissions = (
            ("view_politicas", "View menu policies"),
            ("manage_politicas", "Manage policies"),
        )

    def probar(self, datos):
        return False