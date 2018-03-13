from django import forms
from django.utils.translation import gettext as _
from .models import Modulo


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

