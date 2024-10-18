from django.contrib import admin
from .models import Dogomail, Server, Dominio, Mensaje, Destinatario, Cliente

admin.site.register(Dogomail)
admin.site.register(Server)
admin.site.register(Dominio)
admin.site.register(Mensaje)
admin.site.register(Destinatario)
admin.site.register(Cliente)
