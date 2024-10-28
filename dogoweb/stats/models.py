from django.db import models
from django.db.models import Count
from django.apps import apps
from django.utils.translation import gettext as _
from django.utils import timezone
from dogoweb.settings import DATABASES
import time
import datetime


ESTADO_MSG = {
    1: 'queued',
    2: 'delivered',
    3: 'rejected',
    4: 'blocked',
    5: 'erased',
}

ESTADO_COLOR = {
    'queued': 'blue',
    'delivered': 'green',
    'rejected': 'red',
    'blocked': 'yellow',
    'erased': 'gray',
}

ESTADO_LABEL = {
    'queued': _('Queued'),
    'delivered': _('Delivered'),
    'rejected': _('Rejected'),
    'blocked': _('Blocked'),
    'erased': _('Erased'),
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
        Dogomail = apps.get_model('mail', 'Dogomail')
        tif, tgraf, dogoid = jdata['grafico'].split('-')
        ret = {}

        if tif == 'graf':
            ret = {
                'chart': {
                    'zoomType': 'x',
                    'type': 'area',
                    #'spacing': [0, 0, 0, 0],
                    #'margin': [0, 0, 0, 0],
                    #'spacingBottom': 0,
                    #'marginBottom': 40,
                },
                'title': {
                    'text': _('Unknown'),
                    'align': 'left',
                    'style': { "color": "#444444", "fontSize": "14px" }
                    #'verticalAlign': 'middle',
                    #'y': 40,
                },
                'legend': {
                    'align': 'center',
                    'verticalAlign': 'top',
                    'floating': True,
                },
                'subtitle': {
                    'text': _('Traffic'),
                    'align': 'right',
                    'floating': True,
                    'verticalAlign': 'top',
                    #'x': -40,
                },
                'xAxis': {
                    'type': 'datetime',
                    #'tickPixelInterval': 150,
                    'maxZoom': 1800 * 1000,
                },
                'yAxis': {
                    'minPadding': 0.2,
                    'maxPadding': 0.2,
                    'floor': 0,
                    'title': {
                        'text': 'y',
                        'margin': 10,
                    },
                },
                'plotOptions': {
                    'area': {
                        'marker': {
                            'radius': 1
                        },
                        'lineWidth': 1,
                        'states': {
                            'hover': {
                                'lineWidth': 1
                            }
                        },
                        'threshold': None,
                    }
                },
            }

        elif tif == 'piza':
            ret = {
                'chart': {
                    'plotBackgroundColor': None,
                    'plotBorderWidth': 0,
                    'plotShadow': False,
                    # 'spacing': [0, 0, 0, 0],
                    'margin': [0, 0, 0, 0],
                },
                'title': {
                    'text': _('Unknown'),
                    'align': 'left',
                    'style': {"color": "#444444", "fontSize": "12px"},
                    'verticalAlign': 'top',
                },
                'legend': {
                    'align': 'left',
                    'verticalAlign': 'top',
                    'floating': False,
                    'itemStyle': {'fontWeight': 'normal'},
                    'layout': 'vertical',
                    'y': 8,
                },
                'subtitle': {
                    'text': '',
                    'align': 'right',
                    'floating': True,
                    'verticalAlign': 'top',
                },
                'plotOptions': {
                    'pie': {
                        'size': '140%',
                        'dataLabels': {
                            'enabled': False,
                            'fontSize': '8px',
                            'fontWeight': 'normal'
                        },
                        'showInLegend': True,
                        'startAngle': -90,
                        'endAngle': 90,
                        'center': ['65%', '120%'],
                    }
                },
                'tooltip': {
                    'pointFormat': '<b>{point.percentage:.1f}%</b><br/>{point.y}'
                },
            }
        ret['migraf'] = "#%s" % jdata['grafico']
        ret['credits'] = False
        ret['series'] = []

        if dogoid is None or dogoid == '':
            return ret

        # Conversion del campo tiempo segun la base
        if DATABASES['default']['ENGINE'].find('postgresql') != -1:
            dbtc = "extract(epoch from tiempo)*1000"
        elif DATABASES['default']['ENGINE'].find('mysql') != -1:
            dbtc = "CAST(UNIX_TIMESTAMP(tiempo)*1000 AS UNSIGNED)"
        else:
            return ret

        # Registros en el tiempo
        v = DogoStat.objects.extra(select={'timestamp': dbtc})\
            .filter(tipo=tgraf)\
            .filter(tiempo__gte=jdata['desde'])\
            .filter(tiempo__lte=jdata['hasta'])

        if dogoid != 'all':
            try:
                dm = Dogomail.objects.get(id=dogoid)
                ret['title']['text'] = dm.nombre
                v = v.filter(dogo_id=dogoid)
            except:
                return ret


        if tgraf == 'total':
            if dogoid == 'all':
                ret['title']['text'] = _('All relays')
            ret['yAxis']['title']['text'] = _('mails')
            datos = [
                {
                    'name': _('Incoming'),
                    'type': 'line',
                    'color': 'green',
                    'data': [],
                },
                {
                    'name': _('Outgoing'),
                    'type': 'line',
                    'color': 'blue',
                    'data': [],
                },
            ]
            vv = v.filter(clave='entrante').values('timestamp', 'clave', 'valor').order_by('tiempo')
            for i in vv:
                datos[0]['data'].append([i['timestamp'], int(i['valor'])])
            vv = v.filter(clave='saliente').values('timestamp', 'clave', 'valor').order_by('tiempo')
            for i in vv:
                datos[1]['data'].append([i['timestamp'], int(i['valor'])])
            ret['series'] = datos

        elif tgraf == 'status':
            ret['title']['text'] = _('Mail status')
            datos = {
                'type': 'pie',
                'innerSize': '60%',
                'data': [],
            }
            vv = v.values('clave').annotate(total=models.Sum('valor')).order_by('total').reverse()
            for i in vv:
                val = {'name': ESTADO_LABEL[i['clave']], 'y': i['total']}
                if i['clave'] in ESTADO_COLOR:
                    val['color'] = ESTADO_COLOR[i['clave']]
                datos['data'].append(val)
            ret['series'].append(datos)

        elif tgraf == 'rejects':
            ret['title']['text'] = _('Mail rejections')
            datos = {
                'type': 'pie',
                'innerSize': '60%',
                'data': [],
            }
            vv = v.values('clave').annotate(total=models.Sum('valor')).order_by('total').reverse()
            for i in vv:
                val = {'name': i['clave'], 'y': i['total']}
                datos['data'].append(val)
            ret['series'].append(datos)

        return ret

    @classmethod
    def get_tops(cls, jbody):
        ret = {
            'draw': jbody['draw'],
            'recordsTotal': 0,
            'recordsFiltered': 0,
            'error': "",
            'data': [],
        }
        cli = None
        if 'colhidden' in jbody:
            for ch in jbody['colhidden']:
                if ch[0] == 'cliente':
                   cli = ch[1]
        Mensaje = apps.get_model('mail', 'Mensaje')
        mms = Mensaje.objects.filter(rcv_time__gte=jbody['desde']).filter(rcv_time__lte=jbody['hasta'])
        if cli:
            mms = mms.filter(cliente=cli)

        i = 0
        for s in mms.values('sender').annotate(total=models.Count('sender')).order_by('total').reverse():
            if i == 5:
                break
            i += 1
            dirmail = s['sender']
            direnvi = mms.filter(estado=2, sender=dirmail).count()
            dirrech = mms.filter(estado=3, sender=dirmail).count()
            if s['sender'] == '':
                dirmail = 'MAILER-DAEMON'

            ret['data'].append([dirmail, s['total'], direnvi, dirrech])

        return ret

    @classmethod
    def get_topr(cls, jbody):
        ret = {
            'draw': jbody['draw'],
            'recordsTotal': 0,
            'recordsFiltered': 0,
            'error': "",
            'data': [],
        }
        cli = None
        if 'colhidden' in jbody:
            for ch in jbody['colhidden']:
                if ch[0] == 'cliente':
                   cli = ch[1]
        Mensaje = apps.get_model('mail', 'Mensaje')
        Destinatario = apps.get_model('mail', 'Destinatario')
        mms = Mensaje.objects.filter(rcv_time__gte=jbody['desde']).filter(rcv_time__lte=jbody['hasta'])
        if cli:
            mms = mms.filter(cliente=cli)
        dms = Destinatario.objects.filter(mensaje__in=mms)

        i = 0
        for s in dms.values('receptor').annotate(total=models.Count('receptor')).order_by('total').reverse():
            if i == 5:
                break
            i += 1
            dirmail = s['receptor']
            direnvi = dms.filter(estado=2, receptor=dirmail).count()
            dirrech = dms.filter(estado=3, receptor=dirmail).count()
            if s['receptor'] == '':
                dirmail = 'MAILER-DAEMON'
            ret['data'].append([dirmail, s['total'], direnvi, dirrech])

        return ret

    @classmethod
    def filtro_usuario(self, user, jbody):
        if user.groups.count() > 0:
            clients = False
            operator = False
            for g in user.groups.all():
                if g.name == 'clients':
                    clients = True
                if g.name == 'operator':
                    operator = True
            if clients or operator:
                # Busco los clientes que tiene asignado el usuario por dominio
                clis = set()
                for d in user.dominio_set.all():
                    clis.add(d.cliente.id)
                if len(clis) > 0:
                    if 'colhidden' in jbody:
                        jbody['colhidden'].append(['cliente', str(clis.pop())])
                        jbody['colsearch'] = True
                    else:
                        jbody['colhidden'] = [['cliente', str(clis.pop())],]
                        jbody['colsearch'] = True
        return jbody
