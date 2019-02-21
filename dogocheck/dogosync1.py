#!/usr/bin/env python

import os
import threading
import sys
import MySQLdb as MDB
from pid import PidFile, PidFileError, PidFileAlreadyRunningError, PidFileAlreadyLockedError


luser = 'mgironacci'
lpass = 'x'

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
}


def busca_dogos():
    ret = []
    lcon = MDB.connect(host='localhost', user=luser, passwd=lpass, db='dogomail_2')
    lcur = lcon.cursor()
    lcur.execute("select id, dirip4 from mail_dogomail where activo=1 and tipodm='dogo0'")
    for d in lcur.fetchall():
        ret.append(d)
    return ret


# Hilo para cada servidor
class HiloSync(threading.Thread):
    def __init__(self, rt):
        threading.Thread.__init__(self)
        self.rtr = rt

    def run(self):
        lcon = MDB.connect(host='localhost', user=luser, passwd=lpass, db='dogomail_2')
        lcur = lcon.cursor()
        rcon = MDB.connect(host='127.0.0.1', port=3307, user='dogomail', passwd='dogomail123', db='dogomail')
        rcur = rcon.cursor()
        # AutoReglas
        arreglas = {}
        rcur.execute('''select
            id, test_id, valor, activo, hora, cantidad, descripcion, confirmada
            from reglas
            where hora >= NOW() - INTERVAL 20 MINUTE
            order by id''')
        for o in rcur.fetchall():
            dats = [self.rtr[0], o[0], MOD_TEST[o[1]]]
            dats += o[2:]
            dats += [o[3], o[5], o[7]]
            #print(dats)
            lcur.execute('''insert into spam_autoreglas
             (dogo_id,rdogoid,testid,valor,activo,hora,cantidad,descripcion,confirmada,cambiado_el)
             values (%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
             on duplicate key update
                 activo=%s,
                 cantidad=%s,
                 confirmada=%s,
                 cambiado_el=NOW()
             ''', dats)
            arreglas[o[0]] = lcur.lastrowid
        lcon.commit()
        # Mensajes
        mensajes = {}
        rcur.execute('''select
            id, msgid, fecha_rec, remitente, tamanio, ip_orig, asunto, bodyhash, origen_local, etapa_id, es_cliente
            from run_mensaje
            where fecha_rec >= NOW() - INTERVAL 5 MINUTE
            order by id''')
        for o in rcur.fetchall():
            dats = [self.rtr[0]]
            dats += o
            dats.append(0)
            dats += o[1:]
            #print(dats)
            lcur.execute('''insert into mail_mensaje
                (dogo_id,rdogoid,msgids,rcv_time,sender,sizemsg,ip_orig,subject,bodysha,es_local,etapa,es_cliente,estado)
                values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                on duplicate key update
                    msgids=%s,
                    rcv_time=%s,
                    sender=%s,
                    sizemsg=%s,
                    ip_orig=%s,
                    subject=%s,
                    bodysha=%s,
                    es_local=%s,
                    etapa=%s,
                    es_cliente=%s
             ''', dats)
            mensajes[o[0]] = lcur.lastrowid
        lcon.commit()
        mensajesk = [str(m) for m in mensajes.keys()]
        # Destinos
        rcur.execute('''select
            id, mensaje_id, destinatario, disposicion_id, existe, destino_local, regla_rej_id
            from run_destinatario
            where mensaje_id in (%s)
            order by id''' % ",".join(mensajesk))
        for o in rcur.fetchall():
            dats = [self.rtr[0], o[0], mensajes[o[1]], o[2]]
            dats.append(DISP_ESTADO[o[3]])
            dats += [o[4], o[5]]
            dats.append(DISP_ESTADO[o[3]])
            dats += [o[4], o[5]]
            #print(dats)
            lcur.execute('''insert into mail_destinatario
                (dogo_id,rdogoid,mensaje_id,receptor,estado,existe,es_local)
                values (%s,%s,%s,%s,%s,%s,%s)
                on duplicate key update
                    estado=%s,
                    existe=%s,
                    es_local=%s
            ''', dats)
            if o[6] is not None:
                lcur.execute("update mail_mensaje set autoregla_id=%s where id=%s" % (arreglas[o[6]], mensajes[o[1]]))
        lcon.commit()
        # Reportes
        rcur.execute('''select
            id, mensaje_id, test_id, estado, result, puntaje, desc_resul
            from run_spam
            where mensaje_id in (%s)
            order by id''' % ",".join(mensajesk))
        for o in rcur.fetchall():
            dats = [self.rtr[0], o[0], mensajes[o[1]], MOD_TEST[o[2]]]
            dats += o[3:]
            dats.append(o[3])
            #print(dats)
            try:
                lcur.execute('''insert into mail_testspam
                    (dogo_id,rdogoid,mensaje_id,modulo_id,estado,result,puntaje,desc_resul)
                    values (%s,%s,%s,%s,%s,%s,%s,%s)
                    on duplicate key update
                        estado=%s 
                ''', dats)
            except Exception as e:
                pass
        lcon.commit()


try:
    with PidFile('dogosync1', '/var/lock'):
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
