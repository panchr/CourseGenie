# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-03-31 18:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='requirement',
            name='notes',
            field=models.CharField(default=b'', max_length=255),
        ),
        migrations.AddField(
            model_name='track',
            name='major',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='core.Major'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='course',
            unique_together=set([('number', 'department')]),
        ),
        migrations.AlterUniqueTogether(
            name='crosslisting',
            unique_together=set([('course', 'number', 'department')]),
        ),
        migrations.AlterUniqueTogether(
            name='requirement',
            unique_together=set([('object_id', 't')]),
        ),
    ]
