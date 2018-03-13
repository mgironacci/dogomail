from django import forms
from django.utils.translation import gettext as _
from .models import Cliente


class ClienteForm(forms.ModelForm):
    form_header = {
        'create': {'title': _('Add client'),    'icon': 'icmn-plus-circle',  'url': 'erp_cliente_create'},
        'update': {'title': _('Change client'), 'icon': 'icmn-pencil7',      'url': 'erp_cliente_update'},
        'delete': {'title': _('Delete client'), 'icon': 'icmn-minus-circle', 'url': 'erp_cliente_delete'},
        'templt': 'erp/form_cliente.html',
    }

    class Meta:
        model = Cliente
        fields = ('nombre', 'activo', 'oerpid')
