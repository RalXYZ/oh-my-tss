# Generated by Django 3.2.3 on 2021-06-20 18:20

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('class_schedule', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='application',
            old_name='class_id',
            new_name='Class',
        ),
        migrations.RenameField(
            model_name='application',
            old_name='teacher_id',
            new_name='teacher',
        ),
        migrations.RenameField(
            model_name='building',
            old_name='campus_id',
            new_name='campus',
        ),
        migrations.RenameField(
            model_name='classhasroom',
            old_name='class_id',
            new_name='Class',
        ),
        migrations.RenameField(
            model_name='classhasroom',
            old_name='classroom_id',
            new_name='classroom',
        ),
        migrations.RenameField(
            model_name='classroom',
            old_name='building_id',
            new_name='building',
        ),
        migrations.AddField(
            model_name='classhasroom',
            name='end_at',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(13)]),
        ),
    ]
