# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-04-20 01:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_semester_term'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='semester',
            options={'ordering': ('year', '-term')},
        ),
        migrations.AddField(
            model_name='semester',
            name='year',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterUniqueTogether(
            name='semester',
            unique_together=set([('year', 'term', 'calendar')]),
        ),
        migrations.RemoveField(
            model_name='semester',
            name='name',
        ),
    ]
