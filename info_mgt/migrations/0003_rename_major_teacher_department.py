# Generated by Django 3.2.3 on 2021-06-17 16:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_mgt', '0002_avatar'),
    ]

    operations = [
        migrations.RenameField(
            model_name='teacher',
            old_name='major',
            new_name='department',
        ),
    ]
