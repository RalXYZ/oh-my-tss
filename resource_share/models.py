from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.db.models.base import ModelState
from django.db.models.fields.related import ForeignKey
from django.utils import tree
from info_mgt.models import Student, Course, Class


class Source(models.Model):
    file_type_choices = (
        (1, '文件'),
        (2, '文件夹')
    )
    file_path = models.CharField(max_length=256, null=True, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    file_name = models.CharField(max_length=100)
    file_type = models.CharField(max_length=10, choices=file_type_choices)
    parent = models.CharField(max_length=100, null=True, blank=True)
    Class = models.ManyToManyField(Class)
    user = models.ManyToManyField(User)     # 外键
    course = models.ManyToManyField(Course)
    created_at = models.DateField(auto_now_add=True)    # 自动添加上传时间，之后不会再更改
    updated_at = models.DateField(auto_now=True)    # 自动更新修改时间，每次执行操作都会相应的更改
    canbesearched = models.BooleanField(null=True,default=False)


class Assignment(models.Model):
    course = models.ManyToManyField(Course)  # 外键
    Class = models.ManyToManyField(Class)
    folder_id = models.ManyToManyField(Source)
    assignment_name = models.CharField(max_length=20,null=True)
    assignment_start = models.DateTimeField()
    assignment_end = models.DateTimeField()
    assignment_intro = models.TextField()
    assignment_ratio = models.IntegerField(null=True, blank=True)  # 不能默认为0，否则不能区分是录入失败还是成绩真的为0


class AssignmentGrade(models.Model):
    student = models.ManyToManyField(Student)  # 外键
    course = models.ManyToManyField(Course)  # 外键
    Class = models.ManyToManyField(Class)
    Assignment = models.ManyToManyField(Assignment)
    file = models.ManyToManyField(Source)
    assignment_result = models.IntegerField(null=True, blank=True)
    is_submit = models.BooleanField(null=True,)


class Authority(models.Model):
    hasauthority = models.BooleanField(null=True)
    Class = models.ManyToManyField(Class)
