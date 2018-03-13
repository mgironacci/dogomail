from django import forms
from django.utils.translation import gettext as _
from .models import Server, Dominio, Dogomail, Mensaje, Destinatario, TIPO_SRVS


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


DOM_STEPS = {
    'title': _('Add domain'),
    'icon': 'icmn-plus-circle',
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
        fields = '__all__'
        localize = '__all__'
