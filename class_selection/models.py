from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from info_mgt.models import Campus, Class, Teacher, Student
from class_schedule.models import ClassHasRoom
from class_schedule.models import ClassHasRoom
# from django.contrib import admin
import datetime


class StuHasClass(models.Model):
    Student = models.ForeignKey(Student, on_delete=models.CASCADE)
    Class = models.ForeignKey(ClassHasRoom, on_delete=models.CASCADE)
