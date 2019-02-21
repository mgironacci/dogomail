#!/usr/bin/env python

import os
import threading
import sys
import MySQLdb as MDB
from pid import PidFile, PidFileError, PidFileAlreadyRunningError, PidFileAlreadyLockedError


def busca_dogos():
    ret = []
    lcon = MDB.connect(host='localhost', user='root', passwd='x', db='dogomail_2')
    lcur = lcon.cursor()
    lcur.execute("select id, dirip4 from mail_dogomail where activo=1 and tipodm='dogo2'")
    for d in lcur.fetchall():
        ret.append(d)
    return ret

# Hilo para cada servidor
class HiloSync(threading.Thread):
    def __init__(self, rt):
        threading.Thread.__init__(self)
        self.rtr = rt

    def run(self):
        lcon = MDB.connect(host='localhost', user='root', passwd='x', db='dogomail_2')
        lcur = lcon.cursor()
        rcon = MDB.connect(host='127.0.0.1', port=3308, user='dogomail', passwd='dogomail123', db='dogomail')
        rcur = rcon.cursor()
        # Mensajes
        rcur.execute('''select
             id, msgid, fecha_rec, remitente, tamanio, ip_orig, asunto, bodyhash, origen_local, etapa_id, es_cliente
             from run_mensaje
             where fecha_rec >= NOW() - INTERVAL 1 MINUTE
             order by id''')
        for o in rcur.fetchall():
            dats = [self.rtr[0]]
            dats += o
            dats.append(0)
            dats += o[1:]
            print(dats)
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
        lcon.commit()


try:
    with PidFile('dogosync', '/var/lock'):
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
