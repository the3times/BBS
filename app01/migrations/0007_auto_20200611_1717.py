# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2020-06-11 17:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0006_auto_20200611_1649'),
    ]

    operations = [
        migrations.RenameField(
            model_name='blog',
            old_name='site_name',
            new_name='blog_name',
        ),
        migrations.RenameField(
            model_name='blog',
            old_name='site_theme',
            new_name='blog_theme',
        ),
        migrations.RenameField(
            model_name='blog',
            old_name='site_title',
            new_name='blog_title',
        ),
        migrations.RenameField(
            model_name='category',
            old_name='site',
            new_name='blog',
        ),
        migrations.RenameField(
            model_name='tag',
            old_name='site',
            new_name='blog',
        ),
    ]