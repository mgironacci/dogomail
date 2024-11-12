#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import MySQLdb
from datetime import datetime, timedelta
import pickle, time
import sys, os, re
from pid import PidFile, PidFileError, PidFileAlreadyRunningError, PidFileAlreadyLockedError

# Configuracion
host = "localhost"
puerto = 3306
usuario = "dogomail"
clave = "dogo123"
base = "dogomail"
LOG_FILE = "/var/log/mail.log"
LAST_RUN_FILE = "/var/tmp/mail_log_last_run.txt"
SEARCH_PATTERN = r"(\w+\s+\d+\s+\d+:\d+:\d+)\s+\w+\s+sm-mta\[\d+\]:\s+(\w+):\s+collect: premature EOM: unexpected close"

# Conexion base
con = MySQLdb.connect(host=host, port=puerto, user=usuario, passwd=clave, db=base)
result = []
cons = con.cursor()


def load_last_run():
    if os.path.exists(LAST_RUN_FILE):
        with open(LAST_RUN_FILE, 'r') as f:
            last_run = f.read().strip()
            try:
                return datetime.strptime(last_run, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return None
    return None


def save_last_run(time):
    with open(LAST_RUN_FILE, 'w') as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S"))


def parse_log(last_run_time):
    results = []
    timestamp = None
    with open(LOG_FILE, 'r', encoding='utf-8', errors='replace') as f:
        try:
            for line in f:
                match = re.search(SEARCH_PATTERN, line)
                if match:
                    timestamp_str, msgid = match.groups()
                    timestamp = datetime.strptime(timestamp_str, "%b %d %H:%M:%S")
                    timestamp = timestamp.replace(year=datetime.now().year)

                    # Procesar solo líneas después del último tiempo de ejecución
                    if not last_run_time or timestamp > last_run_time:
                        results.append(msgid)
        except Exception as e:
            print(line)
            print(str(e))
    return results, timestamp


def update_database(msgid):
    # Busco el mensaje
    cons.execute("SELECT id from run_mensaje where msgid=%s", (msgid,))
    for a in cons.fetchall():
        cons.execute("UPDATE run_destinatario SET disposicion_id = 4 WHERE mensaje_id = %s and disposicion_id=0", (a[0],))
    con.commit()


try:
    with PidFile('dogofix15', '/var/lock'):
        last_run_time = load_last_run()

        # Analiza el log y encuentra los mensajes nuevos
        mensajes, last_time = parse_log(last_run_time)

        for msgid in mensajes:
            update_database(msgid)

        # Actualizar el archivo de ejecucion
        if last_time:
            save_last_run(last_time)

except PidFileError as e:
    if isinstance(e, PidFileAlreadyRunningError) or isinstance(e, PidFileAlreadyLockedError):
        sys.exit(2)
    else:
        print("Error %s: %s" % (type(e), str(e)))
    sys.exit(1)
