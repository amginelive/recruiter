# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-23 09:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0012_auto_20170621_1634'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='last_read_message',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='chat.Message', verbose_name='Last read message'),
        ),
    ]
