# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-04-08 02:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20170405_0137'),
    ]

    operations = [
        migrations.CreateModel(
            name='NestedReq',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveSmallIntegerField()),
                ('courses', models.ManyToManyField(to='core.Course')),
                ('requirement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nested_reqs', to='core.Requirement')),
            ],
        ),
        migrations.RemoveField(
            model_name='record',
            name='grade',
        ),
        migrations.AddField(
            model_name='calendar',
            name='certificates',
            field=models.ManyToManyField(to='core.Certificate'),
        ),
        migrations.AddField(
            model_name='calendar',
            name='degree',
            field=models.ForeignKey(default='B.S.E.', on_delete=django.db.models.deletion.CASCADE, to='core.Degree'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='calendar',
            name='track',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Track'),
        ),
        migrations.AlterField(
            model_name='area',
            name='short_name',
            field=models.CharField(max_length=3, unique=True),
        ),
        migrations.AlterField(
            model_name='certificate',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='certificate',
            name='short_name',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='degree',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='degree',
            name='short_name',
            field=models.CharField(max_length=15, unique=True),
        ),
        migrations.AlterField(
            model_name='department',
            name='name',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='department',
            name='short_name',
            field=models.CharField(max_length=3, unique=True),
        ),
        migrations.AlterField(
            model_name='major',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='major',
            name='short_name',
            field=models.CharField(max_length=15, unique=True),
        ),
        migrations.AlterField(
            model_name='record',
            name='semester',
            field=models.CharField(default=b'', max_length=25),
        ),
        migrations.AlterField(
            model_name='semester',
            name='name',
            field=models.CharField(max_length=25, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='major',
            unique_together=set([('name', 'degree')]),
        ),
        migrations.AlterUniqueTogether(
            name='progress',
            unique_together=set([('calendar', 'requirement')]),
        ),
        migrations.AlterUniqueTogether(
            name='track',
            unique_together=set([('major', 'name')]),
        ),
    ]
