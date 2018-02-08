from django import forms
from django.utils.translation import gettext as _
from .models import Server, Dominio, Dogomail, Mensaje, Destinatario


class ServerForm(forms.ModelForm):
    form_header = {
        'create': {'title': _('Add server'),    'icon': 'icmn-plus-circle',  'url': 'mail_server_create'},
        'update': {'title': _('Change server'), 'icon': 'icmn-pencil7',      'url': 'mail_server_update'},
        'delete': {'title': _('Delete server'), 'icon': 'icmn-minus-circle', 'url': 'mail_server_delete'},
        'templt': 'mail/form_server.html',
    }

    class Meta:
        model = Server
        fields = '__all__'
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
