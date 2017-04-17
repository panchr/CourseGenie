# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-04-12 01:11
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0006_auto_20170409_2153'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='requirement',
            unique_together=set([('content_type', 'object_id', 't')]),
        ),
    ]