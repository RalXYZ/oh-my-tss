# Generated by Django 3.2.3 on 2021-06-16 09:24

import datetime
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('info_mgt', '0002_avatar'),
    ]

    operations = [
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('campus_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='info_mgt.campus')),
            ],
        ),
        migrations.CreateModel(
            name='Classroom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_number', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('capacity', models.IntegerField(default=100, validators=[django.core.validators.MinValueValidator(1)])),
                ('type', models.CharField(choices=[('O', 'Common Classroom'), ('G', 'Gymnasium'), ('C', 'Computer Room')], default='O', max_length=1)),
                ('building_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='class_schedule.building')),
            ],
        ),
        migrations.CreateModel(
            name='ClassHasRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.IntegerField(blank=True, default=1, null=True, validators=[django.core.validators.MaxValueValidator(7), django.core.validators.MinValueValidator(1)])),
                ('start_at', models.IntegerField(blank=True, default=1, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(13)])),
                ('duration', models.IntegerField(default=2, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(4)])),
                ('class_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='info_mgt.class')),
                ('classroom_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='class_schedule.classroom')),
            ],
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submit_time', models.DateTimeField(default=datetime.datetime.now)),
                ('content', models.TextField(max_length=100)),
                ('reply_time', models.DateTimeField(blank=True, null=True)),
                ('is_accepted', models.BooleanField(blank=True, null=True)),
                ('reply', models.TextField(blank=True, max_length=100, null=True)),
                ('class_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='info_mgt.class')),
                ('teacher_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='info_mgt.teacher')),
            ],
        ),
    ]
