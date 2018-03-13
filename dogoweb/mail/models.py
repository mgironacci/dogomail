from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from seg.models import DTManager
from erp.models import Cliente
from spam.models import Politica



# Campos seleccionables
TIPO_SRVS = {
    ('sendmail', 'Sendmail'),
    ('postfix', 'Postfix'),
    ('zimbra5', 'Zimbra 5'),
    ('zimbra6', 'Zimbra 6'),
    ('zimbra7', 'Zimbra 7'),
    ('zimbra8', 'Zimbra 8'),
}

ESTADO_SRVS = {
    ('normal', _('Normal')),
    ('down', _('Down')),
    ('warning', _('Warning')),
    ('critical', _('Critical')),
}

MAIL_SERVICES = {
    ('smtp', 'SMTP'),
    ('smtps', 'SMTPS'),
    ('subm', 'Submission'),
    ('pop', 'POP'),
    ('imap', 'IMAP'),
    ('pops', 'POPS'),
    ('imaps', 'IMAPS'),
}

ESTADO_MSG = {
    (1, _('Queued')),
    (2, _('Delivered')),
    (3, _('Rejected')),
    (4, _('Blocked')),
    (5, _('Erased')),
}


TIPO_AUTH = {
    ('smtp', 'SMTP'),
    ('pop3', 'POP'),
    ('ldap', 'LDAP'),
}


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ShaField(models.CharField):

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 20
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
    msgids = CommaSepField('MessageIDs', max_length=200)
    ip_orig = models.GenericIPAddressField('Origin IP', default='::1')
    rcv_time = models.DateTimeField('Received Time', default=timezone.now)
    sender = models.CharField('Sender', max_length=150, default='')
    subject = models.CharField('Subject', max_length=200, default='')
    sizemsg = models.PositiveIntegerField('Size')
    headers = CompressedField('Headers', default='')
    bodysha = ShaField('Body SHA')
    estado = models.SmallIntegerField('State', choices=ESTADO_MSG)
    dogo = models.ForeignKey(Dogomail, on_delete=models.PROTECT)

    def __repr__(self):
        return '<Mensaje: remitente="%s", asunto="%s">' % (self.sender,self.subject)

    def __str__(self):
        return self.subject

    class Meta:
        ordering = ["rcv_time"]


class Destinatario(models.Model):
    objects=DTManager()

    id = models.BigAutoField('ID', primary_key=True)
    mensaje = models.ForeignKey(Mensaje, on_delete=models.CASCADE)
    receptor = models.CharField('Receptor', max_length=150, default='')
    estado = models.SmallIntegerField('State', choices=ESTADO_MSG)
    dominio = models.ForeignKey(Dominio, on_delete=models.SET_NULL, null=True)

    def __repr__(self):
        return '<Destinatario: remitente="%s", destino="%s", asunto="%s">' % (self.mensaje.sender,self.receptor,self.mensaje.subject)

    def __str__(self):
        return self.receptor

    class Meta:
        ordering = ["id", "receptor"]

