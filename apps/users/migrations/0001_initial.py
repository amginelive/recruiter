# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-23 04:34
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_countries.fields
import phonenumber_field.modelfields
import users.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('recruit', '0001_initial'),
        ('auth', '0008_alter_user_username_max_length'),
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Email Address')),
                ('first_name', models.CharField(max_length=30, verbose_name='First Name')),
                ('last_name', models.CharField(max_length=30, verbose_name='Last Name')),
                ('slug', models.SlugField(blank=True, null=True, verbose_name='Alias/Slug')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('get_ads', models.BooleanField(default=True, verbose_name='Receive ads by email?')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date Joined')),
                ('account_type', models.IntegerField(choices=[(1, 'Candidate'), (2, 'Agent')], default=1, help_text='User role selected during registration', verbose_name='Account Type')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name_plural': 'Users',
                'verbose_name': 'User',
            },
        ),
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(editable=False, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(editable=False, verbose_name='Updated At')),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, verbose_name='Phone')),
                ('photo', models.ImageField(blank=True, help_text='200x200px', null=True, upload_to='images/photo/%Y/', verbose_name='Photo')),
                ('status', models.IntegerField(choices=[(0, 'Active'), (1, 'Inactive'), (2, 'Moderation')], default=0, verbose_name='Status')),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='agents', to='companies.Company', verbose_name='Company')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='agent', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Agents',
                'verbose_name': 'Agent',
            },
        ),
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(editable=False, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(editable=False, verbose_name='Updated At')),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, verbose_name='Phone')),
                ('photo', models.ImageField(blank=True, help_text='200x200px', null=True, upload_to='images/photo/%Y/', verbose_name='Photo')),
                ('status', models.IntegerField(choices=[(0, 'Active'), (1, 'Inactive'), (2, 'Moderation')], default=0, verbose_name='Status')),
                ('title', models.CharField(blank=True, max_length=200, null=True, verbose_name='Job title')),
                ('job_location', models.CharField(blank=True, max_length=200, null=True, verbose_name='Desired job location')),
                ('job_type', models.IntegerField(blank=True, choices=[(0, 'Contract'), (1, 'Permanent')], null=True, verbose_name='Job type')),
                ('city', models.CharField(max_length=200, verbose_name='City')),
                ('country', django_countries.fields.CountryField(max_length=2, verbose_name='Country')),
                ('experience', models.SmallIntegerField(blank=True, null=True, verbose_name='Experience (full years)')),
                ('cv', models.FileField(blank=True, max_length=150, null=True, upload_to=users.models.get_cv_path, verbose_name='CV')),
                ('skills', models.ManyToManyField(related_name='candidates', to='recruit.Skill', verbose_name='Skills')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='candidate', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
