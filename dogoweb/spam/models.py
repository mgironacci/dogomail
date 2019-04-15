from django.db import models
from django.apps import apps
from django.utils import timezone
from django.utils.translation import gettext as _
from seg.models import DTManager, html_check
from dogoweb.settings import VERSION, ICO_OK, ICO_WARN, ICO_INFO, ICO_CRIT


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


# Modelo de politicas
TIPO_LISTAS = (
    ('blanca', 'Blanca'),
    ('negra', 'Negra'),
    ('rapida', 'Rápida'),
    ('nosa', 'No SA'),
    ('cliente', 'Cliente'),
)

TIPO_LISTAS_SRCH = (
    ('', '-'),
    ('blanca', 'Blanca'),
    ('negra', 'Negra'),
    ('rapida', 'Rápida'),
    ('nosa', 'No SA'),
    ('cliente', 'Cliente'),
)


class Listas(models.Model):
    objects=DTManager()

    tipo = models.CharField('Type', max_length=10, choices=TIPO_LISTAS, default='blanca', db_index=True)
    ip = models.CharField('IP', max_length=15, db_index=True)
    remitente = models.CharField('Sender', max_length=180, db_index=True)
    destino = models.CharField('Recipient', max_length=100, default='%', db_index=True)
    activo = models.BooleanField('Active', default=True)
    creado_el = models.DateTimeField('Created', auto_now_add=True)
    cambiado_el = models.DateTimeField('Updated', auto_now=True)

    def __repr__(self):
        return '<Listas: tipo="%s", ip="%s", rem="%s", dest="%s">' % (self.tipo, self.ip, self.remitente, self.destino)

    def __str__(self):
        return self.tipo + ": " + self.ip

    class Meta:
        ordering = ["ip", "remitente", "destino"]
        permissions = (
            ("view_listas", "View menu listas"),
            ("manage_listas", "Manage listas"),
        )
        unique_together = ("tipo", "ip", "remitente", "destino")


TEST_REGLA = (
    (2, 'por IP'),
    (3, 'por Remitente'),
    (4, 'por Asunto'),
    (5, 'por Cuerpo'),
)


class AutoReglas(models.Model):
    objects=DTManager()

    rdogoid = models.IntegerField('dogo ID', db_index=True)
    dogo = models.ForeignKey('mail.Dogomail', on_delete=models.PROTECT)
    testid = models.IntegerField('Test', choices=TEST_REGLA, db_index=True)
    valor = models.CharField('Value', max_length=255)
    activo = models.BooleanField('Active', default=True)
    hora = models.DateTimeField('Time')
    cantidad = models.IntegerField('Count')
    descripcion = models.CharField('Description', max_length=255)
    confirmada = models.BooleanField('Confirmed', default=False)
    cambiado_el = models.DateTimeField('Updated', auto_now=True)

    def __repr__(self):
        return '<AutoReglas: id="%d", rdogoid="%d", dogo="%s", valor="%s">' % \
               (self.id, self.rdogoid, self.dogo.nombre, self.valor)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ["hora"]
        permissions = (
            ("manage_autorules", "Manage AutoRules"),
        )
        unique_together = ['dogo', 'rdogoid']

    def get_confirmada_display(self):
        return html_check(bool(self.confirmada))

    def get_activo_display(self):
        return html_check(bool(self.activo))

    @classmethod
    def set_ignored(cls, pks):
        data = dict()
        fallo = False
        Mensaje = apps.get_model('mail', 'Mensaje')
        AccionDogo = apps.get_model('mail', 'AccionDogo')
        idpks = [int(idp) for idp in pks.split(',')]
        rules = cls.objects.filter(id__in=idpks)
        for r in rules:
            r.activo = False
            mpks = [idm.id for idm in r.mensaje_set.all()]
            mret = Mensaje.cambiar_estado(mpks, 'send')
            if mret['mensaje']['tipo'] == 'critical':
                fallo = True
            r.save()
            try:
                nact = {
                    'dogo': r.dogo,
                    'rdogotp': 'reglas',
                    'rdogoid': r.rdogoid,
                    'rcampo': 'activo',
                    'rvalor': '0',
                }
                oact = AccionDogo(**nact)
                oact.save()
            except:
                fallo = True
        if fallo:
            data['mensaje'] = {
                'icon': ICO_CRIT,
                'msg': _('The rules were not marked to be ignored'),
                'tipo': 'critical',
            }
        else:
            data['mensaje'] = {
                'icon': ICO_OK,
                'msg': _('The rules were marked to be ignored'),
                'tipo': 'success',
            }
        return data

    @classmethod
    def set_confirmed(cls, pks):
        data = dict()
        fallo = False
        Mensaje = apps.get_model('mail', 'Mensaje')
        AccionDogo = apps.get_model('mail', 'AccionDogo')
        idpks = [int(idp) for idp in pks.split(',')]
        rules = cls.objects.filter(id__in=idpks)
        for r in rules:
            r.confirmada = True
            mpks = [idm.id for idm in r.mensaje_set.all()]
            mret = Mensaje.cambiar_estado(mpks, 'trash')
            if mret['mensaje']['tipo'] == 'critical':
                fallo = True
            r.save()
        try:
            nact = {
                'dogo': r.dogo,
                'rdogotp': 'reglas',
                'rdogoid': r.rdogoid,
                'rcampo': 'confirmada',
                'rvalor': '1',
            }
            oact = AccionDogo(**nact)
            oact.save()
        except:
            fallo = True
        if fallo:
            data['mensaje'] = {
                'icon': ICO_CRIT,
                'msg': _('The rules were not marked to be confirmed'),
                'tipo': 'critical',
            }
        else:
            data['mensaje'] = {
                'icon': ICO_OK,
                'msg': _('The rules were marked to be confirmed'),
                'tipo': 'success',
            }
        return data
