# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-06 12:10
from __future__ import unicode_literals

from django.db import migrations, models
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_remove_candidate_connections'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='candidate',
            name='job_location',
        ),
        migrations.AddField(
            model_name='candidate',
            name='desired_city',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Desired City'),
        ),
        migrations.AddField(
            model_name='candidate',
            name='desired_country',
            field=django_countries.fields.CountryField(blank=True, max_length=2, null=True, verbose_name='Desired Country'),
        ),
        migrations.AddField(
            model_name='candidate',
            name='willing_to_relocate',
            field=models.NullBooleanField(verbose_name='Willing to relocate?'),
        ),
    ]
