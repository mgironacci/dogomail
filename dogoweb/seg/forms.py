from django import forms
from .models import Menu, Pantalla


class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ('idm', 'nombre', 'icono', 'orden', 'activo', )


class PantallaForm(forms.ModelForm):
    class Meta:
        model = Pantalla
        fields = ('idm', 'nombre', 'url', 'orden', 'icono', 'activo', 'menu', 'permiso', )