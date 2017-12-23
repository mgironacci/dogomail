# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Control',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('idm', models.CharField(max_length=50)),
                ('nombre', models.CharField(max_length=50)),
                ('activo', models.BooleanField(default=True)),
                ('permiso', models.ForeignKey(to='auth.Permission')),
            ],
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('idm', models.CharField(max_length=50)),
                ('nombre', models.CharField(unique=True, max_length=50)),
                ('url', models.CharField(max_length=200)),
                ('url_base', models.CharField(max_length=200)),
                ('orden', models.PositiveIntegerField()),
                ('icono', models.CharField(max_length=100)),
                ('activo', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Pantalla',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('idm', models.CharField(max_length=50)),
                ('nombre', models.CharField(max_length=50)),
                ('url', models.CharField(max_length=200)),
                ('orden', models.PositiveIntegerField()),
                ('icono', models.CharField(max_length=100)),
                ('activo', models.BooleanField(default=True)),
                ('menu', models.ForeignKey(to='seg.Menu')),
                ('permiso', models.ForeignKey(to='auth.Permission')),
            ],
        ),
    ]
