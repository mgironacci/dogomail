from django import forms
from django.utils.translation import gettext as _
from .models import Menu, Pantalla


class MenuForm(forms.ModelForm):
    form_header = {
        'create': {'title': _('Add menu'),    'icon': 'icmn-plus-circle',  'url': 'seg_menu_create'},
        'update': {'title': _('Change menu'), 'icon': 'icmn-pencil7',      'url': 'seg_menu_update'},
        'delete': {'title': _('Delete menu'), 'icon': 'icmn-minus-circle', 'url': 'seg_menu_delete'},
        'templt': 'seg/form_menu.html',
    }

    class Meta:
        model = Menu
        fields = ('idm', 'nombre', 'icono', 'orden', 'activo', )


class PantallaForm(forms.ModelForm):
    form_header = {
        'create': {'title': _('Add screen'),    'icon': 'icmn-plus-circle',  'url': 'seg_pant_create'},
        'update': {'title': _('Change screen'), 'icon': 'icmn-pencil7',      'url': 'seg_pant_update'},
        'delete': {'title': _('Delete screen'), 'icon': 'icmn-minus-circle', 'url': 'seg_pant_delete'},
        'templt': 'seg/form_pant.html',
    }

    class Meta:
        model = Pantalla
        fields = ('idm', 'nombre', 'url', 'orden', 'icono', 'activo', 'menu', 'permiso', )