from django.db import models
from django.db.models import Count
from django.apps import apps
from django.utils import timezone
import time
import datetime


ESTADO_MSG = {
    1: 'queued',
    2: 'delivered',
    3: 'rejected',
    4: 'blocked',
    5: 'erased',
}


class DogoStat(models.Model):
    tiempo = models.DateTimeField(db_index=True)
    dogo = models.ForeignKey("mail.Dogomail", on_delete=models.CASCADE)
    tipo = models.CharField(max_length=30, db_index=True)
    clave = models.CharField(max_length=50, db_index=True)
    valor = models.IntegerField()

    class Meta:
        ordering = ['tiempo', 'dogo']
        unique_together = (('tiempo', 'dogo', 'tipo', 'clave'),)

    @classmethod
    def actualizar(cls, hora=None):
        Mensaje = apps.get_model('mail', 'Mensaje')
        Dogomail = apps.get_model('mail', 'Dogomail')
        TestSpam = apps.get_model('mail', 'TestSpam')
        Modulo = apps.get_model('spam', 'Modulo')
        # Modulos
        mods = {}
        for mm in Modulo.objects.all():
            mods[mm.id] = mm.nombre
        # Hora redondeada al minuto
        if hora:
            ahora = hora
        else:
            time.sleep(2)
            ahora = timezone.now().replace(second=0, microsecond=0)
        antes = ahora - datetime.timedelta(minutes=5)
        # Buscamos mensajes creados de los ultimos 5 minutos
        for d in Dogomail.objects.filter(activo=True):
            mss = Mensaje.objects.filter(rcv_time__gte=antes, rcv_time__lt=ahora, dogo=d)
            # Cantidad de mensajes
            # Entrantes
            nis = {
                'tiempo': ahora,
                'dogo': d,
                'tipo': 'total',
                'clave': 'entrante',
                'valor': mss.filter(es_local=False).count(),
            }
            onis, creado = DogoStat.objects.update_or_create(**nis)
            onis.save()
            # Salientes
            nis = {
                'tiempo': ahora,
                'dogo': d,
                'tipo': 'total',
                'clave': 'saliente',
                'valor': mss.filter(es_local=True).count(),
            }
            onis, creado = DogoStat.objects.update_or_create(**nis)
            onis.save()
            # Por estado
            for e in [1, 2, 3, 4, 5]:
                nis = {
                    'tiempo': ahora,
                    'dogo': d,
                    'tipo': 'status',
                    'clave': ESTADO_MSG[e],
                    'valor': mss.filter(es_local=False, estado=e).count()
                }
                onis, creado = DogoStat.objects.update_or_create(**nis)
                onis.save()
            # Por tipo de rechazo
            tss = TestSpam.objects.filter(mensaje__in=mss.filter(estado=3))
            for ts in tss.values('modulo').annotate(total=Count('modulo')).order_by('total'):
                nis = {
                    'tiempo': ahora,
                    'dogo': d,
                    'tipo': 'rejects',
                    'clave': mods[ts['modulo']],
                    'valor': ts['total'],
                }
                onis, creado = DogoStat.objects.update_or_create(**nis)
                onis.save()


    @classmethod
    def get_stats(cls, jdata):
        tif, tgraf, rutid = jdata['grafico'].split('-')

    @classmethod
    def get_top10(cls, jdata):
        return
