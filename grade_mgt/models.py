from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from info_mgt.models import Student,Course,Class


class CourseResult(models.Model):
    student = models.ManyToManyField(Student)  # 外键
    course = models.ManyToManyField(Course)  # 外键
    Class = models.ManyToManyField(Class)
    is_submit = models.BooleanField(null=True)
    class_performance = models.IntegerField(null=True, blank=True)
    exam_result = models.IntegerField(null=True, blank=True)
    final_result = models.IntegerField(null=True, blank=True)
class ChangeResult(models.Model):
    Class = models.ManyToManyField(Class)  # 外键
    student = models.ManyToManyField(Student)  # 外键
    permit = models.BooleanField(null=True)
    submit_time = models.DateTimeField()
    reason = models.CharField(max_length=100)
    class_performance = models.IntegerField(null=True, blank=True)
    exam_result = models.IntegerField(null=True, blank=True)
    final_result = models.IntegerField(null=True, blank=True)
