# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-22 04:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(editable=False, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(editable=False, verbose_name='Updated At')),
                ('name', models.CharField(max_length=200, verbose_name='Company name')),
                ('domain', models.CharField(help_text='If your email is john@squareballoon.com, your domain name will be squareballon.com.', max_length=200, unique=True, verbose_name='Domain name')),
                ('overview', models.CharField(blank=True, max_length=255, null=True, verbose_name='Overview')),
                ('alias', models.SlugField(max_length=120, verbose_name='Alias/Slug')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('logo', models.ImageField(blank=True, help_text='Logo size 600x200px, .jpg, .png, .gif formats', null=True, upload_to='images/company/logo/%Y', verbose_name='Logo')),
                ('address_1', models.CharField(blank=True, max_length=80, null=True, verbose_name='Address line 1')),
                ('address_2', models.CharField(blank=True, max_length=80, null=True, verbose_name='Address line 2')),
                ('zip', models.CharField(blank=True, max_length=10, null=True, verbose_name='Postal code / ZIP')),
                ('city', models.CharField(max_length=80, verbose_name='City')),
                ('country', django_countries.fields.CountryField(max_length=2, verbose_name='Country')),
                ('website', models.URLField(blank=True, null=True, verbose_name='Website')),
                ('is_charity', models.BooleanField(default=False, verbose_name='Is it a charity organization?')),
                ('allow_auto_invite', models.BooleanField(default=False, verbose_name='Allow auto invite?')),
                ('status', models.IntegerField(choices=[(0, 'active'), (1, 'inactive')], default=0, verbose_name='Status')),
            ],
            options={
                'verbose_name': 'Company',
                'verbose_name_plural': 'Companies',
            },
        ),
        migrations.CreateModel(
            name='CompanyInvitation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(editable=False, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(editable=False, verbose_name='Updated At')),
                ('sent_to', models.EmailField(max_length=254, verbose_name='Email of recipient')),
                ('invite_key', models.CharField(max_length=30, unique=True, verbose_name='Invitation key')),
            ],
            options={
                'verbose_name': 'Company Invitation',
                'verbose_name_plural': 'Company Invitations',
            },
        ),
        migrations.CreateModel(
            name='CompanyRequestInvitation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(editable=False, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(editable=False, verbose_name='Updated At')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='Request Invitation key')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invitation_request', to='companies.Company', verbose_name='Company')),
            ],
            options={
                'verbose_name': 'Company Request Invitation',
                'verbose_name_plural': 'Company Request Invitations',
            },
        ),
    ]
