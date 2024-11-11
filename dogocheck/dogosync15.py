#!/usr/bin/env python

import os
import threading
import sys
import time
import datetime
import MySQLdb as MDB
from pid import PidFile, PidFileError, PidFileAlreadyRunningError, PidFileAlreadyLockedError
import configparser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
allconf = configparser.ConfigParser()
allconf.read(BASE_DIR+'/dogosync.ini')
config = allconf['DEFAULT']

if config.get('DB_ENGINE') != 'mysql':
    print("Error: Solo soporte mysql por ahora")
    sys.exit(1)
luser = config.get('DB_USER')
lpass = config.get('DB_PASSWORD')
lbase = config.get('DB_NAME')
lhost = config.get('DB_HOST')
lport = config.getint('DB_PORT')

ACCIONES = True
DEBUG = False
try:
    if sys.argv[1] == '-n':
        ACCIONES = False
    elif sys.argv[1] == '-nd' or sys.argv[1] == '-dn':
        ACCIONES = False
        DEBUG = True
    elif sys.argv[1] == '-d':
        DEBUG = True
except:
    pass

DISP_ESTADO = {
    None: 1,
    0:  1,
    1:  2,
    2:  4,
    3:  3,
    4:  5,
    5:  1,
    6:  1,
    7:  1,
    8:  2,
    20: 1,
}

#  1 |        4 | Chequeo de virus                                                      | Virus
#  2 |        4 | Cantidad de mensajes de una misma IP en cierto tiempo                 | por IP
#  3 |        4 | Cantidad de mensajes del mismo remitente en cierto tiempo             | por Remit.
#  4 |        4 | Cantidad de mensajes con el mismo asunto en cierto tiempo             | por Asunto
#  5 |        4 | Cantidad de mesajes con igual hash de cuerpo en cierto tiempo         | por Cuerpo
#  6 |        2 | No se especifica remitente (vacio)                                    | sin Remit.
#  7 |        4 | Chequeo con Spamassassin                                              | SA
#  8 |        3 | combined.NJABL.org - Lista combinada de dialups, proxys abiertos, etc | NJABL
#  9 |        3 | cbl.abuseat.org - Lista de proxys abiertos abusados                   | AbuseAT
# 10 |        3 | opm.blitzed.org - Lista de proxys abiertos abusados                   | Blitzed
# 11 |        3 | relays.ordb.org - Lista de relays abiertos                            | ORDB
# 12 |        3 | spamcop.net                                                           | SpamCop
# 13 |        3 | No MX para el dominio                                                 | Sin MX
# 14 |        2 | Sender Policy Framework (SPF)                                         | SPF
# 15 |        2 | Verificacion casilla remitente                                        | Verif. Remit.
# 16 |        3 | Lista negra propia                                                    | Lista negra
# 17 |        3 | Regla propia                                                          | Regla

MOD_TEST = {
    1:  14,
    2:  13,
    3:  13,
    4:  13,
    5:  13,
    6:  6,
    7:  12,
    8:  4,
    9:  4,
    10: 4,
    11: 4,
    12: 4,
    13: 7,
    14: 1,
    15: 6,
    16: 9,
    17: 15,
}


def busca_dogos():
    ret = []
    lcon = MDB.connect(host=lhost, port=lport, user=luser, passwd=lpass, db=lbase)
    lcur = lcon.cursor()
    lcur.execute('select id, dirip4, CONVERT_TZ(ultvis,"+00:00","SYSTEM"), sqlusr, sqlpas from mail_dogomail where activo=1 and tipodm="dogo1"')
    for d in lcur.fetchall():
        ret.append(d)
    return ret


# Hilo para cada servidor
class HiloSync(threading.Thread):
    def __init__(self, rt):
        threading.Thread.__init__(self)
        self.dogoid = rt[0]
        self.dogoip = rt[1]
        self.ultvis = rt[2] - datetime.timedelta(minutes=1)
        self.sqlusr = rt[3]
        self.sqlpas = rt[4]

    def run(self):
        lcon = MDB.connect(host=lhost, port=lport, user=luser, passwd=lpass, db=lbase)
        lcur = lcon.cursor()
        hay_warn = False
        hay_errn = False
        try:
            rcon = MDB.connect(host=self.dogoip, port=3306, user=self.sqlusr, passwd=self.sqlpas, db='dogomail')
            rcur = rcon.cursor()
        except:
            # Aviso el estado que no pude conectar
            lcur.execute('update mail_dogomail set estado="down" where id=%s', (self.dogoid,))
            lcon.commit()
            return

        # Actualizo al estado que pude conectar
        lcur.execute('update mail_dogomail set estado="normal", ultvis=CONVERT_TZ(NOW(),"SYSTEM","+00:00") where id=%s', (self.dogoid,))
        lcon.commit()

        # AutoReglas
        ahora = time.time()
        arreglas = {}
        rcur.execute('''select
            id, test_id, valor, activo, hora, cantidad, descripcion, confirmada
            from reglas
            where lastupd >= %s
            order by id''', (self.ultvis,))
        for o in rcur.fetchall():
            dats = [self.dogoid, o[0], MOD_TEST[o[1]]]
            dats += o[2:]
            dats += [o[3], o[5], o[7]]
            #print(dats)
            lcur.execute('''insert into spam_autoreglas
             (dogo_id,rdogoid,testid,valor,activo,hora,cantidad,descripcion,confirmada,cambiado_el)
             values (%s,%s,%s,%s,%s,%s,%s,%s,%s,CONVERT_TZ(NOW(),"SYSTEM","+00:00"))
             on duplicate key update
                 id=LAST_INSERT_ID(id),
                 activo=%s,
                 cantidad=%s,
                 confirmada=%s,
                 cambiado_el=CONVERT_TZ(NOW(),"SYSTEM","+00:00")
             ''', dats)
            arreglas[o[0]] = lcur.lastrowid
        lcon.commit()
        print("Autoreglas: {}".format(time.time()-ahora))
        # Mensajes
        ahora = time.time()
        mensajes = {}
        rcur.execute('''select
             m.id, msgid, fecha_rec, remitente, tamanio, ip_orig, substring(asunto, 1, 200), bodyhash, origen_local, etapa_id, es_cliente, e.headers
             from run_mensaje m left join run_encabezados e on (m.id=e.mensaje_id)
             where m.lastupd >= %s
             order by id''', (self.ultvis,))
        for o in rcur.fetchall():
            dats = [self.dogoid]
            dats += o[0:11]
            dats.append(0)
            dats += o[1:11]
            if DEBUG:
                print(dats)
            lcur.execute('''insert into mail_mensaje
                (dogo_id,rdogoid,msgids,rcv_time,sender,sizemsg,ip_orig,subject,bodysha,es_local,etapa,es_cliente,estado, creado_el, modifi_el)
                values (%s,%s,%s,CONVERT_TZ(%s,"SYSTEM","+00:00"),%s,%s,%s,%s,%s,%s,%s,%s,%s,CONVERT_TZ(NOW(),"SYSTEM","+00:00"),CONVERT_TZ(NOW(),"SYSTEM","+00:00"))
                on duplicate key update
                    id=LAST_INSERT_ID(id),
                    msgids=%s,
                    rcv_time=CONVERT_TZ(%s,"SYSTEM","+00:00"),
                    sender=%s,
                    sizemsg=%s,
                    ip_orig=%s,
                    subject=%s,
                    bodysha=%s,
                    es_local=%s,
                    etapa=%s,
                    es_cliente=%s,
                    modifi_el=CONVERT_TZ(NOW(),"SYSTEM","+00:00")
             ''', dats)
            mensajes[o[0]] = lcur.lastrowid
            lcur.execute('insert into mail_mensajeheader (mensaje_id, headers) values (%s,%s) on duplicate key update headers=%s', [mensajes[o[0]], o[11], o[11]])
        lcon.commit()
        print("Mensajes: {}".format(time.time()-ahora))
        mensajesk = [str(m) for m in mensajes.keys()]
        # Destinos
        ahora = time.time()
        if len(mensajesk) > 0:
            rcur.execute('''select
                id, mensaje_id, substring(destinatario, 1, 150), disposicion_id, existe, destino_local, regla_rej_id
                from run_destinatario
                where mensaje_id in (%s) or lastupd >= '%s'
                order by id''' % (",".join(mensajesk), self.ultvis))
        else:
            rcur.execute('''select
                id, mensaje_id, substring(destinatario, 1, 150), disposicion_id, existe, destino_local, regla_rej_id
                from run_destinatario
                where lastupd >= '%s'
                order by id''' % (self.ultvis))
        for o in rcur.fetchall():
            if o[1] in mensajes.keys():
                dats = [self.dogoid, o[0], mensajes[o[1]], o[2]]
                dats.append(DISP_ESTADO[o[3]])
                dats += [o[4], o[5]]
                dats.append(DISP_ESTADO[o[3]])
                dats += [o[4], o[5]]
                if DEBUG:
                    print(dats)
                lcur.execute('''insert into mail_destinatario
                    (dogo_id,rdogoid,mensaje_id,receptor,estado,existe,es_local,creado_el,modifi_el)
                    values (%s,%s,%s,%s,%s,%s,%s,CONVERT_TZ(NOW(),"SYSTEM","+00:00"),CONVERT_TZ(NOW(),"SYSTEM","+00:00"))
                    on duplicate key update
                        id=LAST_INSERT_ID(id),
                        estado=%s,
                        existe=%s,
                        es_local=%s,
                        modifi_el=CONVERT_TZ(NOW(),"SYSTEM","+00:00")
                ''', dats)
                if o[6] is not None:
                    lcur.execute('update mail_mensaje set autoregla_id=%s, modifi_el=CONVERT_TZ(NOW(),"SYSTEM","+00:00") where id=%s' % (arreglas[o[6]], mensajes[o[1]]))
            else:
                dats = [DISP_ESTADO[o[3]], o[4], o[5], self.dogoid, o[0]]
                if DEBUG:
                    print(dats)
                lcur.execute('''update mail_destinatario set
                    estado=%s,
                    existe=%s,
                    es_local=%s,
                    modifi_el=CONVERT_TZ(NOW(),"SYSTEM","+00:00")
                    where dogo_id=%s and rdogoid=%s
                ''', dats)
        # Mensajes sin destinatarios los marco como rechazados
        if len(mensajesk) > 0:
            lcur.execute('update mail_mensaje set estado=3, modifi_el=CONVERT_TZ(NOW(),"SYSTEM","+00:00") where id in (%s) and estado=0' % (",".join(mensajesk)))
        lcon.commit()
        print("Destinos: {}".format(time.time()-ahora))
        # Asigno cliente segun dominio destinos
        ahora = time.time()
        lcur.execute('select cliente_id,nombre from mail_dominio where cliente_id is not null')
        domscli = lcur.fetchall()
        for d in domscli:
            lcur.execute('update mail_mensaje set cliente_id=%s where cliente_id is null and id in (SELECT mensaje_id FROM mail_destinatario WHERE LOWER(receptor) LIKE LOWER("%%%s") AND creado_el >= NOW() - INTERVAL 1 DAY)' % (str(d[0]), str(d[1])))
            lcon.commit()
        print("Cliente destinos: {}".format(time.time()-ahora))
        ahora = time.time()
        # Reportes
        if len(mensajesk) > 0:
            rcur.execute('''select
                id, mensaje_id, test_id, estado, result, puntaje, desc_resul
                from run_spam
                where mensaje_id in (%s) or lastupd >= '%s'
                order by id''' % (",".join(mensajesk), self.ultvis))
        else:
            rcur.execute('''select
                id, mensaje_id, test_id, estado, result, puntaje, desc_resul
                from run_spam
                where lastupd >= '%s'
                order by id''' % (self.ultvis))
        for o in rcur.fetchall():
            if o[1] in mensajes.keys():
                try:
                    dats = [self.dogoid, o[0], mensajes[o[1]], MOD_TEST[o[2]]]
                    dats += o[3:]
                    dats.append(o[3])
                    # print(dats)
                    lcur.execute('''insert into mail_testspam
                        (dogo_id,rdogoid,mensaje_id,modulo_id,estado,result,puntaje,desc_resul)
                        values (%s,%s,%s,%s,%s,%s,%s,%s)
                        on duplicate key update
                            id=LAST_INSERT_ID(id),
                            estado=%s 
                    ''', dats)
                except Exception as e:
                    sys.stderr.write("ERROR: Fallo el INSERT con los siguientes valores:\r\n")
                    sys.stderr.write(str(dats))
                    sys.stderr.write("\r\nORIGEN:\r\n")
                    sys.stderr.write(str(o))
                    sys.stderr.write("\r\nCAUSA:\r\n")
                    sys.stderr.write(str(e))
                    sys.stderr.write("\r\n")
            else:
                try:
                    dats = []
                    dats += o[3:]
                    dats += [self.dogoid, o[0], MOD_TEST[o[2]]]
                    # print(dats)
                    lcur.execute('''update mail_testspam set
                        estado=%s,
                        result=%s,
                        puntaje=%s,
                        desc_resul=%s
                        where dogo_id=%s and rdogoid=%s and modulo_id=%s
                    ''', dats)
                except Exception as e:
                    sys.stderr.write("ERROR: Fallo el UPDATE con los siguientes valores:\r\n")
                    sys.stderr.write(str(dats))
                    sys.stderr.write("\r\nORIGEN:\r\n")
                    sys.stderr.write(str(o))
                    sys.stderr.write("\r\nCAUSA:\r\n")
                    sys.stderr.write(str(e))
                    sys.stderr.write("\r\n")
        print("Reportes: {}".format(time.time()-ahora))
        # Actualizo estados en 0 en base a destinatarios
        ahora = time.time()
        for e in [1, 4, 2, 3, 5]:
            lcur.execute('update mail_mensaje m, mail_destinatario d set m.estado=%d where m.id=d.mensaje_id and m.estado=0 and d.estado=%d' % (e, e))
        lcon.commit()
        print("Estados destinos: {}".format(time.time()-ahora))

        if hay_errn:
            lcur.execute('update mail_dogomail set estado="critical" where id=%s', (self.dogoid,))
        elif hay_warn:
            lcur.execute('update mail_dogomail set estado="warning" where id=%s', (self.dogoid,))
        lcon.commit()


try:
    with PidFile('dogosync15', '/var/lock'):
        # Buscamos routers a monitorear
        dogos = busca_dogos()

        # Diccionario con los hilos
        hilos = dict()

        # Por cada router levanto un thread
        for r in dogos:
            hilos[r[0]] = HiloSync(r)
            hilos[r[0]].start()
        for r in dogos:
            hilos[r[0]].join()
except PidFileError as e:
    if isinstance(e, PidFileAlreadyRunningError) or isinstance(e, PidFileAlreadyLockedError):
        sys.exit(2)
    else:
        print("Error %s: %s" % (type(e), str(e)))
    sys.exit(1)
