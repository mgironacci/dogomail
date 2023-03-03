#!/bin/bash
# Script de despliegue y pruebas
IP_TEST_SERVER_WEB=186.148.232.30
IP_PROD_SERVER_WEB=186.148.232.50

# Entornos
ENT=$1
if [ "$ENT" != "webtest" -a "$ENT" != "webprod" -a "$ENT" != "build" -a "$ENT" != "unitest" ]
then
 echo "Entorno $ENT desconocido"
 exit 1
fi

if [ "$ENT" = "build" ]
then
 # Por ahora no se ejecuta hasta no tener python 3.6 en itgit
 exit 0
 pyflakes3 dogoweb/ >/dev/null 2>pyflakes.out
 if [ -s pyflakes.out ]
 then
  cat pyflakes.out
  rm pyflakes.out
  exit 1
 fi
 rm pyflakes.out

elif [ "$ENT" = "unitest" ]
then
 python3 /usr/bin/bandit -i -ll -r dogoweb
 exit 0

elif [ "$ENT" = "webtest" ]
then
 ssh -q dogotest@$IP_TEST_SERVER_WEB <<EOF
source /usr/share/virtualenvwrapper/virtualenvwrapper.sh
cd dogoweb
git pull
workon dogomail
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
sudo recarga-uwsgi
EOF

elif [ "$ENT" = "webprod" ]
then
 ssh -q dogomail@$IP_PROD_SERVER_WEB <<EOF
source /usr/share/virtualenvwrapper/virtualenvwrapper.sh
cd dogoweb
git pull
workon dogomail
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
sudo recarga-uwsgi
EOF

fi
