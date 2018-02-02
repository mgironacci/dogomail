from django import forms
from django.utils.translation import gettext as _
from django.contrib.auth.models import User, Group
from .models import Menu, Pantalla
from .icons import ICON_SET


class UserForm(forms.ModelForm):
    form_header = {
        'create': {'title': _('Add user'),    'icon': 'icmn-plus-circle',  'url': 'seg_user_create'},
        'update': {'title': _('Change user'), 'icon': 'icmn-pencil7',      'url': 'seg_user_update'},
        'delete': {'title': _('Delete user'), 'icon': 'icmn-minus-circle', 'url': 'seg_user_delete'},
        'templt': 'seg/form_user.html',
    }
    grupo = forms.ModelChoiceField(Group.objects.all(), label=_("Group"))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'is_staff', 'is_active', )
        field_classes = {
            'username': forms.EmailField,
        }
        label_suffix = ''

class GroupForm(forms.ModelForm):
    form_header = {
        'create': {'title': _('Add group'),    'icon': 'icmn-plus-circle',  'url': 'seg_group_create'},
        'update': {'title': _('Change group'), 'icon': 'icmn-pencil7',      'url': 'seg_group_update'},
        'delete': {'title': _('Delete group'), 'icon': 'icmn-minus-circle', 'url': 'seg_group_delete'},
        'templt': 'seg/form_group.html',
    }

    class Meta:
        model = Group
        fields = ('name', )


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
        widgets = {
            'icono': forms.Select(choices=ICON_SET),
        }


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
        widgets = {
            'icono': forms.Select(choices=ICON_SET),
        }
