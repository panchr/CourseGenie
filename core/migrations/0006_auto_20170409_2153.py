# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-04-09 21:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_requirement_intrinsic_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='course_id',
            field=models.CharField(default=b'', max_length=10, unique=True),
        ),
    ]