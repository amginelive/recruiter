# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-10 02:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruit', '0005_companyrequestinvitation'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='allow_auto_invite',
            field=models.BooleanField(default=False, verbose_name='Allow auto invite?'),
        ),
    ]
