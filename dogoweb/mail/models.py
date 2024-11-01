from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _
from django.template.loader import render_to_string
from django.contrib.auth.models import User
import codecs
from seg.models import DTManager, html_check
from erp.models import Cliente
from spam.models import Politica, Modulo, AutoReglas
from dogoweb.settings import VERSION, ICO_OK, ICO_WARN, ICO_INFO, ICO_CRIT
import subprocess as sp
from zimsoap.client import ZimbraAdminClient


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
    ultacc = models.DateTimeField('Last actions', default=timezone.now)
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
    numdoms = models.PositiveIntegerField('Domains', blank=True, null=True, default=None)

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

    def html_show(self, request):
        ret = {}
        context = {
            'pk': self.id,
            'name': self.nombre,
            'dirdns': self.dirdns,
            'doms': self.lista_dominios(),
        }
        ret['html_form'] = render_to_string('mail/form_show_server.html', context, request=request)
        return ret

    def check_estado(self):
        # Si no estoy activo directo down
        if not self.activo:
            self.estado = 'down'
            self.save()
            return
        # Probamos ping
        if self.dirip4:
            status, result = sp.getstatusoutput("ping -c3 -W2 " + str(self.dirip4))
        else:
            status, result = sp.getstatusoutput("ping -c3 -W2 " + str(self.dirdns))
        if status != 0:
            self.estado = 'down'
            self.save()
            return
        # Probamos autenticar si es zimbra
        if self.tipo_s in ('zimbra5', 'zimbra6', 'zimbra7', 'zimbra8', ):
            try:
                z = ZimbraAdminClient(self.dirdns)
                # z.login(self.adminusr, self.adminpas)
            except:
                self.estado = 'critical'
                self.save()
                return
        # Esta bien, pongo normal
        self.estado = 'normal'
        self.save()

    def update_numdoms(self):
        if self.activo and self.estado == 'normal' and self.tipo_s in ('zimbra5', 'zimbra6', 'zimbra7', 'zimbra8', ):
            try:
                z = ZimbraAdminClient(self.dirdns)
                # z.login(self.adminusr, self.adminpas)
                # doms = z.get_all_domains()
                doms = 0
                self.numdoms = len(doms)
            except:
                self.estado = 'critical'
            self.save()

    def lista_dominios(self):
        ret = []
        if self.activo and self.estado == 'normal' and self.tipo_s in ('zimbra5', 'zimbra6', 'zimbra7', 'zimbra8', ):
            try:
                z = ZimbraAdminClient(self.dirdns)
                z.login(self.adminusr, self.adminpas)
                doms = z.get_all_domains()
                self.numdoms = len(doms)
                self.save()
            except:
                self.estado = 'critical'
                self.save()

            for d in doms:
                dd = {
                    'id': d.id,
                    'nombre': d.name,
                    'cliente': '',
                    'manejado': html_check(False),
                    'numcas': '-',
                }
                try:
                    od = Dominio.objects.get(nombre=d.name)
                    dd['cliente'] = str(od.cliente)
                    dd['manejado'] = html_check(True)
                    dd['numcas'] = od.numcas
                except Exception as e:
                    pass
                ret.append(dd)

        return ret

    def lista_casillas(self, dominio):
        if self.activo and self.estado == 'normal' and self.tipo_s in ('zimbra5', 'zimbra6', 'zimbra7', 'zimbra8', ):
            try:
                z = ZimbraAdminClient(self.dirdns)
                z.login(self.adminusr, self.adminpas)
                doms = z.get_all_domains()
                for d in doms:
                    if dominio == d.name:
                        return z.get_all_accounts(domain=d)
            except Exception as e:
                self.estado = 'critical'
                self.save()
        return []

    @classmethod
    def sincronizar(cls):
        # Reviso el estado de todos los servidores
        for s in cls.objects.all():
            s.check_estado()
        for s in cls.objects.filter(estado='normal'):
            s.update_numdoms()

    @classmethod
    def filtro_usuario(self, user, jbody):
        if user.groups.count() > 0:
            clients = False
            operator = False
            for g in user.groups.all():
                if g.name == 'clients':
                    clients = True
                if g.name == 'operator':
                    operator = True
            if clients or operator:
                # Busco los clientes que tiene asignado el usuario por dominio
                clis = set()
                for d in user.dominio_set.all():
                    clis.add(d.cliente.id)
                if len(clis) > 0:
                    if 'colhidden' in jbody:
                        jbody['colhidden'].append(['cliente', str(clis.pop())])
                        jbody['colsearch'] = True
                    else:
                        jbody['colhidden'] = [['cliente', str(clis.pop())],]
                        jbody['colsearch'] = True
        return jbody


class Dominio(models.Model):
    objects=DTManager()

    nombre = models.CharField('Name', max_length=50, unique=True)
    activo = models.BooleanField('Active', default=True)
    server = models.ForeignKey(Server, on_delete=models.PROTECT)
    cliente = models.ForeignKey(Cliente, blank=True, on_delete=models.PROTECT, null=True)
    politica = models.ForeignKey(Politica, on_delete=models.PROTECT)
    autentica = models.CharField('Authentication', choices=TIPO_AUTH, default='smtp', max_length=6)
    admins = models.ManyToManyField(User, blank=True)
    zid = models.CharField('ZimbraID', max_length=40, unique=True, blank=True, null=True, default=None)
    numcas = models.PositiveIntegerField('Mailboxs', blank=True, null=True, default=None)

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

    def html_show(self, request):
        ret = {}
        context = {
            'pk': self.id,
            'name': self.nombre,
            'cliente': self.cliente,
            'servidor': self.server,
            'numcas': self.numcas,
            'cas': self.lista_casillas(),
        }
        ret['html_form'] = render_to_string('mail/form_show_domain.html', context, request=request)
        return ret

    def validar_casilla(self):
        return False

    def enviarPrueba(self, destino):
        return True

    def update_numcas(self):
        if self.activo and self.server:
            self.server.check_estado()
            cas = self.server.lista_casillas(self.nombre)
            self.numcas = len(cas)
            self.save()

    def lista_casillas(self):
        ret = []
        # if self.activo:
        #     self.server.check_estado()
        #     cas = self.server.lista_casillas(self.nombre)
        #     self.numcas = len(cas)
        #     self.save()
        #
        #     for c in cas:
        #         cc = {
        #             'id': c.id,
        #             'nombre': c.name,
        #         }
        #         ret.append(cc)

        return ret

    @classmethod
    def filtro_usuario(self, user, jbody):
        if user.groups.count() > 0:
            clients = False
            operator = False
            for g in user.groups.all():
                if g.name == 'clients':
                    clients = True
                if g.name == 'operator':
                    operator = True
            if clients or operator:
                # Busco los clientes que tiene asignado el usuario por dominio
                clis = set()
                for d in user.dominio_set.all():
                    clis.add(d.cliente.id)
                if len(clis) > 0:
                    if 'colhidden' in jbody:
                        jbody['colhidden'].append(['cliente', str(clis.pop())])
                        jbody['colsearch'] = True
                    else:
                        jbody['colhidden'] = [['cliente', str(clis.pop())],]
                        jbody['colsearch'] = True
        return jbody


class Mensaje(models.Model):
    objects=DTManager()

    id = models.BigAutoField('ID', primary_key=True)
    rdogoid = models.BigIntegerField('dogo ID', db_index=True, blank=True, null=True, default=None)
    msgids = CommaSepField('MessageIDs', max_length=200, db_index=True)
    ip_orig = models.GenericIPAddressField('Origin IP', default='::1', db_index=True)
    rcv_time = models.DateTimeField('Received Time', default=timezone.now, db_index=True)
    sender = models.CharField('Sender', max_length=150, default='', db_index=True)
    subject = models.CharField('Subject', max_length=200, blank=True, null=True, default=None, db_index=True)
    sizemsg = models.PositiveIntegerField('Size')
    headers = CompressedField('Headers', blank=True, null=True, default=None)
    bodysha = ShaField('Body SHA', blank=True, null=True, db_index=True)
    estado = models.SmallIntegerField('State', choices=ESTADO_MSG, db_index=True)
    dogo = models.ForeignKey(Dogomail, on_delete=models.PROTECT)
    es_local = models.BooleanField('Is Local', default=False, db_index=True)
    es_cliente = models.BooleanField('Is Client', default=False, db_index=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, default=None)
    etapa = models.SmallIntegerField('Stage', choices=RUN_ETAPA_MSG, default=1, db_index=True)
    autoregla = models.ForeignKey(AutoReglas, on_delete=models.PROTECT, blank=True, null=True, db_index=True)
    #con_cuerpo = models.BooleanField('Has body', default=True)
    creado_el = models.DateTimeField('Created', auto_now_add=True)
    modifi_el = models.DateTimeField('Modified', auto_now=True)

    def __repr__(self):
        return '<Mensaje: remitente="%s", asunto="%s">' % (self.sender,self.subject)

    def __str__(self):
        if self.subject is None:
            return _("Empty")
        return self.subject

    class Meta:
        ordering = ["rcv_time"]
        unique_together = ['dogo', 'rdogoid']

    def get_estado_html(self):
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
    def cambiar_estado(cls, pks, nuevoestado):
        data = dict()
        if type(pks) == list or type(pks) == tuple:
            idpks = pks
        else:
            idpks = [int(idp) for idp in pks.split(',')]
        hayerror = False
        if nuevoestado == 'send':
            # Busco mensajes con etapa 4 y estado no enviado
            msgs = cls.objects.filter(id__in=idpks).filter(etapa=4).filter(estado__in=[0, 1, 3, 4])
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
            msgs = cls.objects.filter(id__in=idpks).filter(etapa__in=[3, 4]).filter(estado__in=[0, 1, 4])
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

    @classmethod
    def filtro_usuario(self, user, jbody):
        if user.groups.count() > 0:
            clients = False
            operator = False
            for g in user.groups.all():
                if g.name == 'clients':
                    clients = True
                if g.name == 'operator':
                    operator = True
            if clients or operator:
                # Busco los clientes que tiene asignado el usuario por dominio
                clis = set()
                for d in user.dominio_set.all():
                    clis.add(d.cliente.id)
                if len(clis) > 0:
                    if 'colhidden' in jbody:
                        jbody['colhidden'].append(['cliente', str(clis.pop())])
                        jbody['colsearch'] = True
                    else:
                        jbody['colhidden'] = [['cliente', str(clis.pop())],]
                        jbody['colsearch'] = True
        return jbody


class MensajeHeader(models.Model):
    mensaje = models.OneToOneField(Mensaje, on_delete=models.CASCADE, primary_key=True)
    headers = CompressedField('Headers', blank=True, null=True, default=None)
    creado_el = models.DateTimeField('Created', auto_now_add=True)

    def __repr__(self):
        return '<MensajeHeader: remitente="%s", asunto="%s">' % (self.mensaje.sender,self.mensaje.subject)

    def __str__(self):
        if self.mensaje.subject is None:
            return _("Empty")
        return self.mensaje.subject


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
    creado_el = models.DateTimeField('Created', auto_now_add=True)
    modifi_el = models.DateTimeField('Modified', auto_now=True)

    def __repr__(self):
        return '<Destinatario: remitente="%s", destino="%s", asunto="%s">' % (self.mensaje.sender,self.receptor,self.mensaje.subject)

    def __str__(self):
        return self.receptor

    class Meta:
        ordering = ["id", "receptor"]
        unique_together = ['dogo', 'rdogoid']

    def get_estado_html(self):
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
    creado_el = models.DateTimeField('Created', auto_now_add=True)

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
