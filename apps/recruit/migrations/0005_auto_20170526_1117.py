# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-26 10:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recruit', '0004_auto_20170526_0256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='connectionrequest',
            name='connectee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='connectee_requests', to='users.Candidate', verbose_name='Connectee'),
        ),
        migrations.AlterField(
            model_name='connectionrequest',
            name='connecter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='connecter_requests', to='users.Candidate', verbose_name='Connecter'),
        ),
    ]
