# Generated by Django 3.2.3 on 2021-06-26 10:49

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('class_schedule', '0004_auto_20210622_0135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classhasroom',
            name='start_at',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(13)]),
        ),
    ]
