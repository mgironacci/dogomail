from django import forms
from django.utils.translation import gettext as _
from .models import Server, Dominio, Dogomail, Mensaje, Destinatario, TIPO_SRVS, ESTADO_SRCH
from seg.models import html_check


DATEFMT = ['%Y-%m-%d %H:%M:%S',
 '%Y-%m-%d %H:%M',
 '%Y-%m-%d',
 '%d/%m/%Y %H:%M:%S',
 '%d/%m/%Y %H:%M',
 '%d/%m/%Y',
 '%d/%m/%y %H:%M:%S',
 '%d/%m/%y %H:%M',
 '%d/%m/%y']


class ServerNameForm(forms.Form):
    form_header = {
        'templt': 'mail/form_server_name.html',
        'url': 'mail_server_create',
    }

    nombre = forms.CharField(label='Name', max_length=50, required=True)
    dirdns = forms.CharField(label='DNS Address', max_length=70, required=True)


class ServerInfoForm(forms.ModelForm):
    form_header = {
        'templt': 'mail/form_server_info.html',
        'url': 'mail_server_create',
    }

    class Meta:
        model = Server
        fields = [ 'nombre', 'dirip4', 'dirip6', 'dirdns', 'tipo_s', 'sslcrt',
                   'cliente', 'servicios', 'adminusr', 'adminpas', ]
        localize = '__all__'


SERVER_STEPS = {
    'title': _('Add server'),
    'icon': 'icmn-plus-circle',
    'count': 2,
    'steps': [
        {
            'title': _('Name'),
            'icon': 'icmn-server',
            'form': ServerNameForm,
        },
        {
            'title': _('Info'),
            'icon': 'icmn-inf',
            'form': ServerInfoForm,
        },
    ]
}


class DominioW1Form(forms.ModelForm):
    form_header = {
        'templt': 'mail/form_domain_w1.html',
        'url': 'mail_domain_create',
    }

    step = forms.HiddenInput()

    class Meta:
        model = Dominio
        fields = [ 'nombre', 'server', 'autentica', 'cliente', 'politica', 'admins' ]
        localize = '__all__'


class DominioW2Form(forms.Form):
    form_header = {
        'templt': 'mail/form_domain_w2.html',
        'url': 'mail_domain_sendmail',
    }

    step = forms.HiddenInput()
    mprueba = forms.CharField(label='Test mail', max_length=100, required=False)


class DominioW3Form(forms.Form):
    form_header = {
        'templt': 'mail/form_domain_w3.html',
        'url': 'mail_domain_create',
    }

    step = forms.HiddenInput()
    dato = forms.CharField(label='Sent mail', max_length=100, required=False)


DOM_STEPS = {
    'title': _('Add domain'),
    'icon': 'icmn-plus-circle',
    'count': 3,
    'steps': [
        {
            'title': _('Info'),
            'icon': 'icmn-at-sign',
            'form': DominioW1Form,
        },
        {
            'title': _('Test'),
            'icon': 'icmn-database-check',
            'form': DominioW2Form,
        },
        {
            'title': _('Test'),
            'icon': 'icmn-checkmark',
            'form': DominioW3Form,
        },
    ]
}


class ServerForm(forms.ModelForm):
    form_header = {
        'create': {'title': _('Add server'),    'icon': 'icmn-plus-circle',  'url': 'mail_server_create'},
        'update': {'title': _('Change server'), 'icon': 'icmn-pencil7',      'url': 'mail_server_update'},
        'delete': {'title': _('Delete server'), 'icon': 'icmn-minus-circle', 'url': 'mail_server_delete'},
        'templt': 'mail/form_server.html',
    }

    class Meta:
        model = Server
        #fields = '__all__'
        fields = ['nombre', 'dirdns', 'tipo_s', 'activo', ]
        localize = '__all__'


class DominioForm(forms.ModelForm):
    form_header = {
        'create': {'title': _('Add domain'),    'icon': 'icmn-plus-circle',  'url': 'mail_domain_create'},
        'update': {'title': _('Change domain'), 'icon': 'icmn-pencil7',      'url': 'mail_domain_update'},
        'delete': {'title': _('Delete domain'), 'icon': 'icmn-minus-circle', 'url': 'mail_domain_delete'},
        'templt': 'mail/form_domain.html',
    }

    class Meta:
        model = Dominio
        fields = '__all__'
        localize = '__all__'


class DogomailForm(forms.ModelForm):
    form_header = {
        'create': {'title': _('Add dogo'),    'icon': 'icmn-plus-circle',  'url': 'mail_dogo_create'},
        'update': {'title': _('Change dogo'), 'icon': 'icmn-pencil7',      'url': 'mail_dogo_update'},
        'delete': {'title': _('Delete dogo'), 'icon': 'icmn-minus-circle', 'url': 'mail_dogo_delete'},
        'templt': 'mail/form_dogo.html',
    }

    class Meta:
        model = Dogomail
        fields = ['nombre', 'dirdns', 'dirip4', 'dirip6', 'activo', 'tipodm' ]
        localize = '__all__'


class SearchMailForm(forms.Form):
    form_header = {
        'templt': 'mail/form_search_mail.html',
        'url': 'mailsearch',
    }

    msgids = forms.CharField(label='MessageID', required=False)
    ip_orig = forms.GenericIPAddressField(label='Origin IP', protocol='IPv4', required=False)
    sender = forms.CharField(label='Sender', required=False)
    recipient = forms.CharField(label='Recipient', required=False)
    subject = forms.CharField(label='Subject', required=False)
    msgids = forms.CharField(label='Message IDs', required=False)
    minsize = forms.CharField(label='Min Size', required=False)
    maxsize = forms.CharField(label='Max Size', required=False)
    estado = forms.ChoiceField(label='Status', choices=ESTADO_SRCH, required=False, initial=0)
    es_local = forms.NullBooleanField(label='Local', required=False)
    es_cliente = forms.NullBooleanField(label='Client', required=False)

    class Meta:
        localize = '__all__'


class MailForm(forms.ModelForm):
    form_header = {
        'show': {'title': _('View message'), 'icon': 'icmn-envelop4', 'url': 'mailshow'},
        'templt': 'mail/form_mail.html',
    }

    class Meta:
        model = Mensaje
        exclude = []
        localize = '__all__'

    def get_etapa(self):
        return self.instance.get_etapa_display()

    def get_estado(self):
        return self.instance.get_estado_html()

    def get_dogo(self):
        return self.instance.dogo.nombre

    def get_es_cliente(self):
        return html_check(self.instance.es_cliente)

    def get_es_local(self):
        return html_check(self.instance.es_local)

    def get_recipients(self):
        ret = ""
        for r in self.instance.destinatario_set.all():
            ret += "<small>" + r.get_estado_html() + "</small>&nbsp;" + r.receptor + "<br/>"
        return ret

    def get_recipient_count(self):
        return self.instance.destinatario_set.count()

    def get_validaciones(self):
        ret = []
        for t in self.instance.testspam_set.all():
            tt = {
                'modulo': t.modulo.nombre,
                'resultado': t.result,
                'descripcion': t.desc_resul,
                'puntaje': t.puntaje,
            }
            if t.modulo.nombre == "SPAMASSASSIN":
                tt['descripcion'] = "<pre>" + t.desc_resul + "</pre>"
            ret.append(tt)
        return ret

    def mheaders(self):
        try:
            return self.instance.mensajeheader.headers
        except:
            return None