from django.db import models
from django.contrib.auth.models import User

# models for online exam.
import info_mgt


class Question(models.Model):  # 题目
    TYPE = (
        ('0', '选择题'),
        ('1', '判断题'),
    )
    ANSWER = (
        ('0', 'A'),
        ('1', 'B'),
        ('2', 'C'),
        ('3', 'D'),
        ('4', 'T'),
        ('5', 'F'),
    )
    course = models.ForeignKey(info_mgt.models.Course, on_delete=models.CASCADE)  # 外键
    type = models.CharField(choices=TYPE, max_length=20, default='选择题', verbose_name='题目类型')  # int 0选择1判断
    content = models.TextField()  # 题目内容
    answer = models.CharField(choices=ANSWER, max_length=2, default='A', verbose_name='题目答案')  # 答案
    value = models.FloatField()  # 分值
    chapter = models.IntegerField(default=1)  #所属章节
    difficulty = models.IntegerField(default=1)#难度


class Paper(models.Model):  # 试卷
    name = models.CharField(max_length=128, verbose_name='试卷名')  # 试卷名

    course = models.ForeignKey(info_mgt.models.Course, on_delete=models.CASCADE)  # 外键
    teacher = models.ForeignKey(info_mgt.models.Teacher, on_delete=models.CASCADE)  # 教师id
    generate_time = models.DateTimeField(auto_now=True)  # 生成试卷的时间,自动添加最后保存时间
    questions = models.ManyToManyField(Question)  # 字符串


class Test(models.Model):
    start = models.DateTimeField()  # 开始时间
    end = models.DateTimeField()  # 结束时间
    teachers = models.ManyToManyField(info_mgt.models.Teacher)
    courses = models.ManyToManyField(info_mgt.models.Course)
    students = models.ManyToManyField(info_mgt.models.Student)
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE,default=1)

class Score(models.Model):

    student = models.ForeignKey(info_mgt.models.Student, on_delete=models.CASCADE)
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    date = models.DateTimeField()
    score = models.FloatField()
    weight = models.FloatField()  # 分数在总成绩中的占比
    test = models.ForeignKey(Test, on_delete=models.CASCADE)


class StudentAnswer(models.Model):
    student = models.ForeignKey(info_mgt.models.Student, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_right = models.BooleanField()
    score = models.FloatField()
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    paper_id = models.IntegerField()
