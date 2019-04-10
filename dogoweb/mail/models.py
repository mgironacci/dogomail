from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
import codecs
from seg.models import DTManager
from erp.models import Cliente
from spam.models import Politica, Modulo, AutoReglas
from dogoweb.settings import VERSION, ICO_OK, ICO_WARN, ICO_INFO, ICO_CRIT


# Campos seleccionables
TIPO_SRVS = (
    ('sendmail', 'Sendmail'),
    ('postfix', 'Postfix'),
    ('zimbra5', 'Zimbra 5'),
    ('zimbra6', 'Zimbra 6'),
    ('zimbra7', 'Zimbra 7'),
    ('zimbra8', 'Zimbra 8'),
    ('exchange', 'Exchange'),
)

TIPO_DOGO = (
    ('dogo0', 'Dogomail 1'),
    ('dogo1', 'Dogomail 1.5'),
    ('dogo2', 'Dogomail 2'),
)

ESTADO_SRVS = (
    ('normal', _('Normal')),
    ('down', _('Down')),
    ('warning', _('Warning')),
    ('critical', _('Critical')),
)

MAIL_SERVICES = (
    ('smtp', 'SMTP'),
    ('smtps', 'SMTPS'),
    ('subm', 'Submission'),
    ('pop', 'POP'),
    ('imap', 'IMAP'),
    ('pops', 'POPS'),
    ('imaps', 'IMAPS'),
)

ESTADO_MSG = (
    (1, _('Queued')),
    (2, _('Delivered')),
    (3, _('Rejected')),
    (4, _('Blocked')),
    (5, _('Erased')),
)

ESTADO_ICO = {
    0: "icmn-question",
    1: "icmn-clock",
    2: "icmn-checkmark4",
    3: "icmn-cross2",
    4: "icmn-construction",
    5: "icmn-bin",
}

ESTADO_COL = {
    0: "secondary",
    1: "info",
    2: "success",
    3: "danger",
    4: "warning",
    5: "default",
}

ESTADO_SRCH = (
    (0, '-'),
    (1, _('Queued')),
    (2, _('Delivered')),
    (3, _('Rejected')),
    (4, _('Blocked')),
    (5, _('Erased')),
)
#ESTADO_SRCH = {
#    (0, '-'),
#    (1, '<i class="%s"></i> %s' % (ESTADO_ICO[1], _('Queued'))),
#    (2, '<i class="%s"></i> %s' % (ESTADO_ICO[2], _('Delivered'))),
#    (3, '<i class="%s"></i> %s' % (ESTADO_ICO[3], _('Rejected'))),
#    (4, '<i class="%s"></i> %s' % (ESTADO_ICO[4], _('Blocked'))),
#    (5, '<i class="%s"></i> %s' % (ESTADO_ICO[5], _('Erased'))),
#}

RUN_DISPOSICION_MSG = (
    (1,'Mensaje Entregado'),
    (2,'Mensaje Retenido'),
    (3,'Mensaje Rechazado'),
    (4,'Mensaje Eliminado'),
    (5,'Mensaje en Transito'),
    (6,'Mensaje Liberado para enviar'),
    (7,'Mensaje Liberado en Tránsito'),
    (8,'Mensaje saliente entregado'),
    (20,'Liberado pero no se encontro cuerpo')
)

RUN_ETAPA_MSG = (
    (1,'Etapa indefinida'),
    (2,'Validacion de remitente'),
    (3,'Validacion de destinatarios'),
    (4,'Examen del cuerpo del mensaje'),
)

TIPO_AUTH = (
    ('smtp', 'SMTP'),
    ('pop3', 'POP'),
    ('ldap', 'LDAP'),
)


def html_estado_mail(e):
    if 0 < e < 6:
        return '<span class="label label-pill label-%s"><i class="%s"></i></span>' % (ESTADO_COL[e], ESTADO_ICO[e])
    return '<span class="label label-pill label-%s"><i class="%s"></i></span>' % (ESTADO_COL[0], ESTADO_ICO[0])


# Campos personalizados
class CommaSepField(models.CharField):

    def __init__(self, separator=",", *args, **kwargs):
        self.separator = separator
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        # Only include kwarg if it's not the default
        if self.separator != ",":
            kwargs['separator'] = self.separator
        return name, path, args, kwargs


class CompressedField(models.TextField):

    def to_python(self, value):
        if not value:
            return value
        try:
            return value.decode('base64').decode('gzip').decode('utf-8')
        except Exception:
            return value

    def from_db_value(self, value, expression, connection):
        if not value:
            return value
        try:
            return codecs.decode(codecs.decode(value.encode('utf8'), 'base64'), 'zlib').decode('utf-8')
        except Exception as e:
            return value


class ShaField(models.CharField):

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 50
        kwargs['default'] = ''
        super().__init__(*args, **kwargs)


# Modelos de mail
class Dogomail(models.Model):
    objects=DTManager()

    nombre = models.CharField('Name', max_length=50, unique=True)
    activo = models.BooleanField('Active', default=True)
    dirip4 = models.GenericIPAddressField('IPv4 Address', protocol='IPv4', unique=True, blank=True, null=True)
    dirip6 = models.GenericIPAddressField('IPv6 Address', protocol='IPv6', unique=True, blank=True, null=True)
    dirdns = models.CharField('DNS Address', unique=True, max_length=70)
    estado = models.CharField('Status', choices=ESTADO_SRVS, max_length=10, default='down')
    tipodm = models.CharField('Type', choices=TIPO_DOGO, max_length=10, default='dogo2')
    ultvis = models.DateTimeField('Last seen', default=timezone.now)
    sqlusr = models.CharField('SQL User', blank=True, null=True, max_length=20)
    sqlpas = models.CharField('SQL Password', blank=True, null=True, max_length=20)

    def __repr__(self):
        return '<Dogomail: nombre="%s">' % self.nombre

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ["nombre"]
        permissions = (
            ("view_dogomail", "View menu dogomail"),
            ("manage_dogomail", "Manage dogomail"),
        )


class Server(models.Model):
    objects=DTManager()

    nombre = models.CharField('Name', max_length=50, unique=True)
    activo = models.BooleanField('Active', default=True)
    dirip4 = models.GenericIPAddressField('IPv4 Address', protocol='IPv4', unique=True, blank=True, null=True)
    dirip6 = models.GenericIPAddressField('IPv6 Address', protocol='IPv6', unique=True, blank=True, null=True)
    dirdns = models.CharField('DNS Address', unique=True, max_length=70)
    tipo_s = models.CharField('Type', choices=TIPO_SRVS, max_length=10)
    estado = models.CharField('Status', choices=ESTADO_SRVS, max_length=10, default='down')
    sslcrt = models.TextField('Private SSL Cert', blank=True, default='', help_text='Not commercial certificate or CA')
    cliente = models.ForeignKey(Cliente, blank=True, on_delete=models.PROTECT, null=True, default=None)
    servicios = models.CharField('Services', choices=MAIL_SERVICES, default='smtp', max_length=35)
    adminusr = models.CharField('Admin User', blank=True, max_length=100)
    adminpas = models.CharField('Admin Password', blank=True, max_length=100)

    def __repr__(self):
        return '<Server: nombre="%s", tipo="%s">' % (self.nombre, self.tipo_s)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ["nombre"]
        permissions = (
            ("view_servers", "View menu servers"),
            ("manage_servers", "Manage servers"),
        )


class Dominio(models.Model):
    objects=DTManager()

    nombre = models.CharField('Name', max_length=50, unique=True)
    activo = models.BooleanField('Active', default=True)
    server = models.ForeignKey(Server, on_delete=models.PROTECT)
    cliente = models.ForeignKey(Cliente, blank=True, on_delete=models.PROTECT, null=True)
    politica = models.ForeignKey(Politica, on_delete=models.PROTECT)
    autentica = models.CharField('Authentication', choices=TIPO_AUTH, default='smtp', max_length=6)
    admins = models.ManyToManyField(User, blank=True)

    def __repr__(self):
        return '<Dominio: nombre="%s">' % self.nombre

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ["nombre"]
        permissions = (
            ("view_domains", "View menu domains"),
            ("manage_domains", "Manage domains"),
        )

    def validar_casilla(self):
        return False

    def enviarPrueba(self, destino):
        return True


class Mensaje(models.Model):
    objects=DTManager()

    id = models.BigAutoField('ID', primary_key=True)
    rdogoid = models.BigIntegerField('dogo ID', db_index=True, blank=True, null=True, default=None)
    msgids = CommaSepField('MessageIDs', max_length=200)
    ip_orig = models.GenericIPAddressField('Origin IP', default='::1', db_index=True)
    rcv_time = models.DateTimeField('Received Time', default=timezone.now)
    sender = models.CharField('Sender', max_length=150, default='', db_index=True)
    subject = models.CharField('Subject', max_length=200, blank=True, null=True, default=None)
    sizemsg = models.PositiveIntegerField('Size')
    headers = CompressedField('Headers', blank=True, null=True, default=None)
    bodysha = ShaField('Body SHA', blank=True, null=True, db_index=True)
    estado = models.SmallIntegerField('State', choices=ESTADO_MSG, db_index=True)
    dogo = models.ForeignKey(Dogomail, on_delete=models.PROTECT)
    es_local = models.BooleanField('Is Local', default=False, db_index=True)
    es_cliente = models.BooleanField('Is Client', default=False, db_index=True)
    etapa = models.SmallIntegerField('Stage', choices=RUN_ETAPA_MSG, default=1, db_index=True)
    autoregla = models.ForeignKey(AutoReglas, on_delete=models.PROTECT, blank=True, null=True, db_index=True)
    #con_cuerpo = models.BooleanField('Has body', default=True)

    def __repr__(self):
        return '<Mensaje: remitente="%s", asunto="%s">' % (self.sender,self.subject)

    def __str__(self):
        if self.subject is None:
            return _("Empty")
        return self.subject

    class Meta:
        ordering = ["rcv_time"]
        unique_together = ['dogo', 'rdogoid']

    def get_estado_display(self):
        ahora = self.estado
        cuenta = 0
        diverge = False
        estados = {}
        for d in self.destinatario_set.all():
            if cuenta == 0:
                ahora = d.estado
                estados[ahora] = None
            elif ahora != d.estado:
                diverge = True
                estados[ahora] = None
            cuenta += 1
        if self.destinatario_set.count() == 0:
            ahora = 3
        if diverge:
            if 1 in estados:
                self.estado = 1
            elif 4 in estados:
                self.estado = 4
            elif 2 in estados:
                self.estado = 2
            elif 3 in estados:
                self.estado = 3
            elif 5 in estados:
                self.estado = 5
            self.save()
        elif self.estado != ahora:
            self.estado = ahora
            self.save()
        return html_estado_mail(self.estado)

    @classmethod
    def cambiar_estado(cls, pks, request, nuevoestado):
        data = dict()
        idpks = [int(idp) for idp in pks.split(',')]
        hayerror = False
        if nuevoestado == 'send':
            # Busco mensajes con etapa 4 y estado no enviado
            msgs = cls.objects.filter(id__in=idpks).filter(etapa=4).filter(estado__in=[1, 3, 4])
            for m in msgs:
                try:
                    nact = {
                        'dogo': m.dogo,
                        'rdogotp': 'run_mensaje',
                        'rdogoid': m.rdogoid,
                        'rcampo': 'disposicion',
                        'rvalor': '6',
                    }
                    oact = AccionDogo(**nact)
                    oact.save()
                except:
                    hayerror = True
            if hayerror:
                data['mensaje'] = {
                    'icon': ICO_CRIT,
                    'msg': _('The emails were not marked to be sent'),
                    'tipo': 'critical',
                }
            else:
                data['mensaje'] = {
                    'icon': ICO_OK,
                    'msg': _('The emails were marked to be sent'),
                    'tipo': 'success',
                }
        elif nuevoestado == 'trash':
            # Busco mensajes con etapa 4 y estado esperando o bloqueado
            msgs = cls.objects.filter(id__in=idpks).filter(etapa__in=[3, 4]).filter(estado__in=[1, 4])
            for m in msgs:
                try:
                    nact = {
                        'dogo': m.dogo,
                        'rdogotp': 'run_mensaje',
                        'rdogoid': m.rdogoid,
                        'rcampo': 'disposicion',
                        'rvalor': '3',
                    }
                    oact = AccionDogo(**nact)
                    oact.save()
                except:
                    hayerror = True
            if hayerror:
                data['mensaje'] = {
                    'icon': ICO_CRIT,
                    'msg': _('The emails were not marked to be rejected'),
                    'tipo': 'critical',
                }
            else:
                data['mensaje'] = {
                    'icon': ICO_OK,
                    'msg': _('The emails were marked to be rejected'),
                    'tipo': 'success',
                }
        else:
            data['mensaje'] = {
                'icon': ICO_CRIT,
                'msg': _('Unknown new state'),
                'tipo': 'critical',
            }
        return data


class Destinatario(models.Model):
    objects=DTManager()

    id = models.BigAutoField('ID', primary_key=True)
    dogo = models.ForeignKey(Dogomail, on_delete=models.PROTECT)
    rdogoid = models.BigIntegerField('dogo ID', db_index=True, blank=True, null=True, default=None)
    mensaje = models.ForeignKey(Mensaje, on_delete=models.CASCADE)
    receptor = models.CharField('Receptor', max_length=150, default='', db_index=True)
    estado = models.SmallIntegerField('State', choices=ESTADO_MSG, db_index=True)
    dominio = models.ForeignKey(Dominio, on_delete=models.SET_NULL, null=True)
    es_local = models.BooleanField('Is Local', default=False, db_index=True)
    existe = models.BooleanField('Exists', default=False, db_index=True)

    def __repr__(self):
        return '<Destinatario: remitente="%s", destino="%s", asunto="%s">' % (self.mensaje.sender,self.receptor,self.mensaje.subject)

    def __str__(self):
        return self.receptor

    class Meta:
        ordering = ["id", "receptor"]
        unique_together = ['dogo', 'rdogoid']

    def get_estado_display(self):
        return html_estado_mail(self.estado)


class TestSpam(models.Model):
    id = models.BigAutoField('ID', primary_key=True)
    dogo = models.ForeignKey(Dogomail, on_delete=models.PROTECT)
    rdogoid = models.BigIntegerField('dogo ID', db_index=True, blank=True, null=True, default=None)
    mensaje = models.ForeignKey(Mensaje, on_delete=models.CASCADE)
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE)
    estado = models.PositiveIntegerField(blank=True, null=True, default=None)
    result = models.CharField(max_length=255)
    puntaje = models.FloatField(blank=True, null=True, default=None)
    desc_resul = models.TextField()

    class Meta:
        ordering = ["id"]
        unique_together = ['dogo', 'rdogoid']


class AccionDogo(models.Model):
    id = models.BigAutoField('ID', primary_key=True)
    dogo = models.ForeignKey(Dogomail, on_delete=models.PROTECT)
    rdogotp = models.CharField(max_length=30, db_index=True)
    rdogoid = models.BigIntegerField('dogo ID', db_index=True)
    rcampo = models.CharField(max_length=40)
    rvalor = models.CharField(max_length=200, blank=True, null=True, default=None)
    creado_el = models.DateTimeField('Created', auto_now_add=True)
    ejecel = models.DateTimeField('Executed', blank=True, null=True, default=None)

    class Meta:
        ordering = ["id"]
