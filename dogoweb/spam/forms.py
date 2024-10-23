from django import forms
from django.utils.translation import gettext as _
from .models import Modulo, Politica, Listas, Regla, TIPO_LISTAS_SRCH, ACCION_REGLA_SRCH


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


class ListaSearchForm(forms.Form):
    tipo = forms.ChoiceField(label='Type', choices=TIPO_LISTAS_SRCH, required=False, initial=0)
    ip_orig = forms.GenericIPAddressField(label='IP', protocol='IPv4', required=False)
    sender = forms.CharField(label='Sender', required=False)
    recipient = forms.CharField(label='Recipient', required=False)
    esactivo = forms.NullBooleanField(label='Active', required=False)

    class Meta:
        localize = '__all__'


class ReglaForm(forms.ModelForm):
    form_header = {
        'create': {'title': _('Add rule'),    'icon': 'icmn-plus-circle',  'url': 'spam_rule_create'},
        'update': {'title': _('Change rule'), 'icon': 'icmn-pencil7',      'url': 'spam_rule_update'},
        'delete': {'title': _('Delete rule'), 'icon': 'icmn-minus-circle', 'url': 'spam_rule_delete'},
        'templt': 'spam/form_regla.html',
    }

    class Meta:
        model = Regla
        fields = ('orden', 'nombre', 'accion', 'ip', 'remitente', 'destino', 'activo', 'dominios', 'asunto', 'cuerpo')

    # Sobrecargamos el __init__ para aceptar el request.user
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Capturamos el usuario
        super(ReglaForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        obj = super(ReglaForm, self).save(commit=False)
        if self.user:
            if not hasattr(obj, 'creado_por'):
                obj.creado_por = self.user
            if not hasattr(obj, 'cliente') or obj.cliente is None:
                for d in self.user.dominio_set.all():
                    obj.cliente = d.cliente
                    break
        if commit:
            obj.save()
        return obj


class ReglasSearchForm(forms.Form):
    sch_nombre = forms.CharField(label='Name', required=False)
    sch_accion = forms.ChoiceField(label='Action', choices=ACCION_REGLA_SRCH, required=False, initial=0)
    sch_activo = forms.NullBooleanField(label='Active', required=False)
    sch_ip = forms.CharField(label='IP', required=False)
    sch_remitente = forms.CharField(label='Sender', required=False)
    sch_destino = forms.CharField(label='Recipient', required=False)
    sch_asunto = forms.CharField(label='Subject', required=False)
    sch_cuerpo = forms.CharField(label='Body', required=False)

    class Meta:
        localize = '__all__'
