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
    lcon = MDB.connect(host=lhost, port=lport, user=luser, passwd=lpass, db=lbase)
    lcur = lcon.cursor()
    lcur.execute('select id, dirip4, CONVERT_TZ(ultacc,"+00:00","SYSTEM"), sqlusr, sqlpas from mail_dogomail where activo=1 and tipodm="dogo1"')
    for d in lcur.fetchall():
        ret.append(d)
    return ret


# Hilo para cada servidor
class HiloSync(threading.Thread):
    def __init__(self, rt):
        threading.Thread.__init__(self)
        self.dogoid = rt[0]
        self.dogoip = rt[1]
        self.ultacc = rt[2] - datetime.timedelta(minutes=1)
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
        lcur.execute('update mail_dogomail set estado="normal", ultacc=CONVERT_TZ(NOW(),"SYSTEM","+00:00") where id=%s', (self.dogoid,))
        lcon.commit()

        # Aplico acciones en el dogomail
        if ACCIONES:
            ahora = time.time()
            lcur.execute("select id,rdogotp,rdogoid,rcampo,rvalor from mail_acciondogo where dogo_id=%s and ejecel is null", (self.dogoid,))
            for a in lcur.fetchall():
                if a[1] == 'run_mensaje' and a[3] == 'disposicion':
                    if a[4] == '6':
                        nuevodisp = 6
                    elif a[4] == '2':
                        nuevodisp = 2
                    elif a[4] == '3':
                        nuevodisp = 3
                    else:
                        continue
                    rcur.execute('update run_destinatario set disposicion_id=%s where mensaje_id=%s', (nuevodisp, int(a[2])))
                    rcon.commit()
                    lcur.execute('update mail_acciondogo set ejecel=CONVERT_TZ(NOW(),"SYSTEM","+00:00") where id=%s', (a[0],))
                    lcon.commit()
                elif a[1] == 'reglas' and a[3] == 'activo':
                    rcur.execute('update reglas set activo=%s where id=%s', (int(a[4]), int(a[2])))
                    rcon.commit()
                    lcur.execute('update mail_acciondogo set ejecel=CONVERT_TZ(NOW(),"SYSTEM","+00:00") where id=%s', (a[0],))
                    lcon.commit()
                elif a[1] == 'reglas' and a[3] == 'confirmada':
                    rcur.execute('update reglas set confirmada=%s where id=%s', (int(a[4]), int(a[2])))
                    rcon.commit()
                    lcur.execute('update mail_acciondogo set ejecel=CONVERT_TZ(NOW(),"SYSTEM","+00:00") where id=%s', (a[0],))
                    lcon.commit()
            print("Acciones: {}".format(time.time() - ahora))

            # Aplico cambios en listas
            ahora = time.time()
            lcur.execute("select id, tipo, ip, remitente, destino, activo from spam_listas where cambiado_el>=%s", (self.ultacc,))
            for a in lcur.fetchall():
                try:
                    dats = []
                    dats += a
                    dats += a
                    rcur.execute('''insert into listas 
                        (rdogoid, tipo, ip, remitente, destino, activa, creado_el)
                        values (%s, %s, %s, %s, %s, %s, CONVERT_TZ(NOW(),"SYSTEM","+00:00"))
                        on duplicate key update
                            rdogoid=%s,
                            tipo=%s,
                            ip=%s,
                            remitente=%s,
                            destino=%s,
                            activa=%s
                        ''', dats)
                except Exception as e:
                    sys.stderr.write("ERROR: Fallo el INSERT/UPDATE de listas con los siguientes valores:\r\n")
                    sys.stderr.write(str(dats))
                    sys.stderr.write("\r\nORIGEN:\r\n")
                    sys.stderr.write(str(a))
                    sys.stderr.write("\r\nCAUSA:\r\n")
                    sys.stderr.write(str(e))
                    sys.stderr.write("\r\n")

            rcon.commit()
            print("Listas: {}".format(time.time() - ahora))

            # Aplico cambios en reglas spam
            ahora = time.time()
            lcur.execute("""
                SELECT sr.id, sr.accion, sr.orden, sr.ip, sr.remitente, sr.destino, sr.asunto, sr.cuerpo, sr.activo, 
                       COALESCE(md.nombre, '') AS dominio
                FROM spam_regla sr
                LEFT JOIN mail_dominio md ON sr.cliente_id = md.cliente_id
                WHERE sr.cambiado_el >= %s
            """, (self.ultacc,))
            for a in lcur.fetchall():
                try:
                    rcur.execute('''
                        INSERT INTO spam_regla (rdogoid, accion, orden, ip, remitente, destino, asunto, cuerpo, activo, dominio)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            accion=VALUES(accion),
                            orden=VALUES(orden),
                            ip=VALUES(ip),
                            remitente=VALUES(remitente),
                            destino=VALUES(destino),
                            asunto=VALUES(asunto),
                            cuerpo=VALUES(cuerpo),
                            activo=VALUES(activo),
                            dominio=VALUES(dominio)
                    ''', a)
                except Exception as e:
                    sys.stderr.write("ERROR: Fallo el INSERT/UPDATE de listas con los siguientes valores:\r\n")
                    sys.stderr.write(str(dats))
                    sys.stderr.write("\r\nORIGEN:\r\n")
                    sys.stderr.write(str(a))
                    sys.stderr.write("\r\nCAUSA:\r\n")
                    sys.stderr.write(str(e))
                    sys.stderr.write("\r\n")

            rcon.commit()
            # Borrado de reglas
            try:
                lcur.execute("SELECT id FROM spam_regla")
                valid_ids = set(row[0] for row in lcur.fetchall())

                if valid_ids:
                    tids = ', '.join(['%s'] * len(valid_ids))
                    delete_query = "DELETE FROM spam_regla WHERE rdogoid NOT IN ({})".format(tids)
                    rcur.execute(delete_query, list(valid_ids))
                    rcon.commit()
            except Exception as e:
                sys.stderr.write("ERROR: Fallo el DELETE de reglas ({})\r\n".format(str(e)))

            # Me traigo los maches
            try:
                rcur.execute('SELECT SUM(maches),rdogoid FROM spam_regla GROUP BY rdogoid')
                maches = rcur.fetchall()
                lcur.executemany('UPDATE spam_regla set maches=%s WHERE id=%s', maches)
                lcon.commit()
            except Exception as e:
                sys.stderr.write("ERROR: Fallo el update de maches de reglas ({})\r\n".format(str(e)))
            print("Reglas: {}".format(time.time() - ahora))

try:
    with PidFile('dogoaccion15', '/var/lock'):
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
