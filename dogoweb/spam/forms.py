from django import forms
from django.utils.translation import gettext as _
from .models import Modulo, Politica, Listas


class ModuloForm(forms.ModelForm):
    form_header = {
        'create': {'title': _('Add module'),    'icon': 'icmn-plus-circle',  'url': 'spam_module_create'},
        'update': {'title': _('Change module'), 'icon': 'icmn-pencil7',      'url': 'spam_module_update'},
        'delete': {'title': _('Delete module'), 'icon': 'icmn-minus-circle', 'url': 'spam_module_delete'},
        'templt': 'spam/form_module.html',
    }

    class Meta:
        model = Modulo
        fields = ('nombre', 'activo', 'config')


class PoliticaForm(forms.ModelForm):
    form_header = {
        'create': {'title': _('Add policy'),    'icon': 'icmn-plus-circle',  'url': 'spam_policy_create'},
        'update': {'title': _('Change policy'), 'icon': 'icmn-pencil7',      'url': 'spam_policy_update'},
        'delete': {'title': _('Delete policy'), 'icon': 'icmn-minus-circle', 'url': 'spam_policy_delete'},
        'templt': 'spam/form_policy.html',
    }

    class Meta:
        model = Politica
        fields = ('nombre', 'activo')


class ListaForm(forms.ModelForm):
    form_header = {
        'create': {'title': _('Add list'),    'icon': 'icmn-plus-circle',  'url': 'spam_list_create'},
        'update': {'title': _('Change list'), 'icon': 'icmn-pencil7',      'url': 'spam_list_update'},
        'delete': {'title': _('Delete list'), 'icon': 'icmn-minus-circle', 'url': 'spam_list_delete'},
        'templt': 'spam/form_lista.html',
    }

    class Meta:
        model = Listas
        fields = ('tipo', 'ip', 'remitente', 'destino', 'activo')


class AutoReglasSearchForm(forms.Form):
    valor = forms.CharField(label='Value', required=False)
    activo = forms.NullBooleanField(label='Active', required=False)
    mincant = forms.CharField(label='Min Quantity', required=False)
    maxcant = forms.CharField(label='Max Quantity', required=False)
    descripcion = forms.CharField(label='Description', required=False)
    confirmada = forms.NullBooleanField(label='Confirmed', required=False)

    class Meta:
        localize = '__all__'
