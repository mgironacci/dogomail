from django.db import models
from seg.models import DTManager


class Cliente(models.Model):
    objects=DTManager()

    nombre = models.CharField('Name', max_length=100, unique=True)
    activo = models.BooleanField('Active', default=True)
    oerpid = models.PositiveIntegerField('OpenERP ID', blank=True)

    def __repr__(self):
        return '<Cliente: nombre="%s">' % self.nombre

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ["nombre"]
        permissions = (
            ("view_clients", "View clients"),
            ("manage_clients", "Manage clients"),
        )
