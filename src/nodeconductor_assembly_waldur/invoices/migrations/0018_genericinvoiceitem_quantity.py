# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-09-20 16:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0017_genericinvoiceitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='genericinvoiceitem',
            name='quantity',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
