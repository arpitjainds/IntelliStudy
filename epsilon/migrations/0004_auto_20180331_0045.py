# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-03-31 00:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('epsilon', '0003_enroll_level'),
    ]

    operations = [
        migrations.AlterField(
            model_name='has',
            name='level',
            field=models.CharField(choices=[('beginner', 'beginner'), ('intermediate', 'intermediate'), ('advanced', 'advanced')], default='beginner', max_length=20),
        ),
    ]