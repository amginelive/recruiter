# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-10 13:15
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recruit', '0003_auto_20170427_1932'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyRequestInvitation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='Request Invitation key')),
            ],
        ),
        migrations.AddField(
            model_name='company',
            name='allow_auto_invite',
            field=models.BooleanField(default=False, verbose_name='Allow auto invite?'),
        ),
        migrations.AddField(
            model_name='company',
            name='domain',
            field=models.CharField(max_length=200, unique=True, verbose_name='Domain name'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='company',
            name='address_1',
            field=models.CharField(blank=True, max_length=80, null=True, verbose_name='Address line 1'),
        ),
        migrations.AddField(
            model_name='companyrequestinvitation',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invitation_request', to='recruit.Company'),
        ),
        migrations.AddField(
            model_name='companyrequestinvitation',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invitation_request', to=settings.AUTH_USER_MODEL),
        ),
    ]
