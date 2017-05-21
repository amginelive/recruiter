# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-21 12:49
from __future__ import unicode_literals

from django.db import migrations
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0002_auto_20170517_1812'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='country',
            field=django_countries.fields.CountryField(max_length=2, verbose_name='Country'),
        ),
    ]