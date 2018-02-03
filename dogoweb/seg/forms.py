from django import forms
from django.utils.translation import gettext as _
from django.contrib.auth.models import User, Group, Permission
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

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        if 'instance' in kw and kw['instance'] is not None and kw['instance'].groups.count() > 0:
            self.fields['grupo'].initial = kw['instance'].groups.first()

    def save(self, commit=True):
        self.instance.groups.clear()
        self.instance.groups.add(self.cleaned_data['grupo'])
        return super().save(commit=commit)


class GroupForm(forms.ModelForm):
    form_header = {
        'create': {'title': _('Add group'),    'icon': 'icmn-plus-circle',  'url': 'seg_group_create'},
        'update': {'title': _('Change group'), 'icon': 'icmn-pencil7',      'url': 'seg_group_update'},
        'delete': {'title': _('Delete group'), 'icon': 'icmn-minus-circle', 'url': 'seg_group_delete'},
        'templt': 'seg/form_group.html',
    }
    users = forms.ModelMultipleChoiceField(User.objects.all(), required=False)

    class Meta:
        model = Group
        fields = ('name', 'permissions', )

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        if 'instance' in kw and kw['instance'] is not None:
            self.fields['users'].initial = kw['instance'].user_set.all()

    def save(self, commit=True):
        self.instance.user_set.set(self.cleaned_data['users'])
        return super().save(commit=commit)


class PermissionForm(forms.ModelForm):
    form_header = {
        'update': {'title': _('Change permission'), 'icon': 'icmn-pencil7', 'url': 'seg_perm_update'},
        'templt': 'seg/form_perm.html',
    }
    groups = forms.ModelMultipleChoiceField(Group.objects.all(), required=False)

    class Meta:
        model = Permission
        fields = ('name', 'groups', )

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.fields['name'].disabled = True
        if 'instance' in kw and kw['instance'] is not None:
            self.fields['groups'].initial = kw['instance'].group_set.all()

    def save(self, commit=True):
        self.instance.group_set.set(self.cleaned_data['groups'])
        return super().save(commit=commit)


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
