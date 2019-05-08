#!/usr/bin/env python

import os
import sys
import django
from django.utils import timezone
from datetime import datetime
from pprint import pprint
from pid import PidFile, PidFileError, PidFileAlreadyRunningError, PidFileAlreadyLockedError


try:
    with PidFile('dogo-stats', '/var/lock'):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dogoweb.settings")
        django.setup()

        try:
            hora = timezone.make_aware(datetime.strptime(sys.argv[1], '%Y-%m-%d %H:%M'))
            pprint(hora)
        except:
            hora = None

        from stats.models import DogoStat

        # Actualizar estadisticas dogomail
        DogoStat.actualizar(hora)
except PidFileError as e:
    if isinstance(e, PidFileAlreadyRunningError) or isinstance(e, PidFileAlreadyLockedError):
        sys.exit(2)
    else:
        print("Error %s: %s" % (type(e), str(e)))
    sys.exit(1)
