# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2019-04-13 19:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20190412_0247'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='deny',
            field=models.BooleanField(default=False),
        ),
    ]
