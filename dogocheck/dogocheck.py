#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Programa que mantiene sincronizado los datos del router con el control central web

import sys, os, time, re
import MySQLdb
from pprint import pprint
import daemon, logging, logging.config, pwd, signal
import pymailq, base64
from pymailq import store, control, selector, utils
import ConfigParser
import traceback
import subprocess
from subprocess import CalledProcessError
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer

aconf = "/etc/dogomail/dogocheck.cfg"
if os.geteuid() == 1000:
    aconf = "/home/mgironacci/Proyectos/dogomail/dogocheck/dogocheck.cfg"

# Levantamos archivo de configuracion
config = ConfigParser.ConfigParser()
config.read(aconf)

# Levantamos logger desde archivo de configuracion
logging.config.fileConfig(aconf)
milog = logging.getLogger("dogocheck")

# Levantamos pymailq desde archivo de configuracion
pymailq.load_config(aconf)

# Base local
lhost = config.get("main","db_host","127.0.0.1")
try:
    lport = config.getint("main","db_port")
except:
    lport = 3306
luser = config.get("main","db_user","root")
lpass = config.get("main","db_pass","x")
ldata = config.get("main","db_data","dogomail_check")

# Servicio XMLRPC
srv_addr = config.get("main","bind_address","localhost")
try:
    srv_port = config.getint("main","bind_port")
except:
    srv_port = 7890

# Salida
def salir(*args):
    sigs = {2:"SIGINT",15:"SIGTERM"}
    milog.info("Fin del proceso por %s" % sigs[args[0]])
    sys.exit(0)

signal.signal(signal.SIGTERM,salir)
signal.signal(signal.SIGINT,salir)

# Conexion
def conectar():
    return MySQLdb.connect(host = lhost, port = lport, user = luser, passwd = lpass, db = ldata, cursorclass = pymysql.cursors.DictCursor)

# Funcion para actualizar la base de datos local
def actualizar_local():

    milog.debug("Inicio actualizar_local()")

    # Conectamos
    mibd = conectar()
    bcur = mibd.cursor()

    # Desconecto
    mibd.commit()
    mibd.close()

class API:
    def __init__(self):
        self.pstore = store.PostqueueStore()
        self.selector = selector.MailSelector(self.pstore)
        self.qcontrol = control.QueueControl()
        self._store_load()

    def _store_load(self, filename=None):
        try:
            self.pstore.load(filename=filename)
            # Automatic load of selector if it is empty and never used.
            if not len(self.selector.mails) and not len(self.selector.filters):
                self.selector.reset()
            return "%d mails loaded from queue" % (len(self.pstore.mails))
        except (OSError, IOError, CalledProcessError), exc:
            return "*** Error: unable to load store: %s" % (exc,)

    def hola(self):
        return "hola"

    def store_status(self):
        self._store_load()
        if self.pstore is None or self.pstore.loaded_at is None:
            return "store is not loaded"
        return "store loaded with %d mails at %s" % (len(self.pstore.mails), self.pstore.loaded_at)

    def store_summary(self):
        self._store_load()
        if self.pstore is None or self.pstore.loaded_at is None:
            return "store is not loaded"
        return self.pstore.summary()
    
# Funcion base del demonio
def procesar():
    milog.info("Inicio del proceso")

    server = SimpleXMLRPCServer((srv_addr,srv_port))
    server.register_introspection_functions()

    server.register_instance(API())

    server.serve_forever()

# Demonizacion del programa
if len(sys.argv)>1:
    procesar()
else:
    milog.removeHandler(milog.handlers[1])
    # Para python 2.4
    context = daemon.DaemonContext(uid = pwd.getpwnam(config.get("main","proc_user","root")).pw_uid,
                                   files_preserve = [milog.handlers[0].stream.fileno()])
    context.open()
    try:
        procesar()
    finally:
        context.close()
    # Para resto de pythones
    #with daemon.DaemonContext(uid=pwd.getpwnam(config.get("main", "proc_user", "root")).pw_uid,
    #                          files_preserve=[milog.handlers[0].stream.fileno()]):
    #    procesar()
