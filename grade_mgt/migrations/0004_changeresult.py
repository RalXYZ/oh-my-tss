# Generated by Django 3.2.4 on 2021-06-26 23:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('info_mgt', '0003_rename_major_teacher_department'),
        ('grade_mgt', '0003_courseresult_is_submit'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChangeResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permit', models.BooleanField(null=True)),
                ('submit_time', models.DateTimeField()),
                ('reason', models.CharField(max_length=100)),
                ('class_performance', models.IntegerField(blank=True, null=True)),
                ('exam_result', models.IntegerField(blank=True, null=True)),
                ('final_result', models.IntegerField(blank=True, null=True)),
                ('Class', models.ManyToManyField(to='info_mgt.Class')),
                ('student', models.ManyToManyField(to='info_mgt.Student')),
            ],
        ),
    ]
