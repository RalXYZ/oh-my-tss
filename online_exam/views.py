import datetime
import random

import pymysql
from django.db import connection
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from info_mgt.models import Course
from online_exam.models import Question, Paper, Test, Score, StudentAnswer
from django.utils import timezone


# Create your views here.
def index(request):

    if request.method == 'POST':
        current_user_group = request.user.groups.first()
        print(current_user_group)
        if not current_user_group or current_user_group.name == 'student':
            return HttpResponseRedirect(reverse('login'))
        course = request.POST.get("course")
        chapter = request.POST.get("chapter")
        if course != '' or chapter != '':
            result = []
            if course != '' and chapter == '':
                message = Course.objects.get(name=course)
                resultset = Question.objects.filter(course_id=message.id)
                print(resultset)
                for i in resultset:
                    result.append((i.content, i.id))
            elif course == '' and chapter != '':
                return render(request, 'online_exam_main.html', {
                    'web_title': '在线测验系统',
                    'page_title': '进入题库',
                    'test_param': 'TEST PARAM',
                    'emptysearch': '2'
                })
            else:
                message = Course.objects.filter(name=course)
                print(message)
                for i in message:
                    course_id = i.id
                resultset = Question.objects.filter(course_id=course_id, chapter=chapter)
                print(resultset)
                for i in resultset:
                    result.append((i.content, i.id))
            return render(request, 'online_exam_search_out.html', {
                'web_title': '在线测验系统',
                'page_title': '进入题库',
                'test_param': 'TEST PARAM',
                'question_content': result,
                'course': course,
                'chapter': chapter
            })
        else:
            return render(request, 'online_exam_main.html', {
                'web_title': '在线测验系统',
                'page_title': '进入题库',
                'test_param': 'TEST PARAM',
                'emptysearch': '1'
            })
    return render(request, 'online_exam_main.html', {
        'web_title': '在线测验系统',
        'page_title': '进入题库',
        'test_param': 'TEST PARAM',
        'emptysearch': '0'
    })

def index1(request):

    if request.method == 'POST':
        current_user_group = request.user.groups.first()
        print(current_user_group)
        if not current_user_group or current_user_group.name == 'student':
            return HttpResponseRedirect(reverse('login'))
        course = request.POST.get("course")
        chapter = request.POST.get("chapter")
        if course != '' or chapter != '':
            result = []
            if course != '' and chapter == '':
                message = Course.objects.get(name=course)
                resultset = Question.objects.filter(course_id=message.id)
                print(resultset)
                for i in resultset:
                    result.append((i.content, i.id))
            elif course == '' and chapter != '':
                return render(request, 'online_exam_main.html', {
                    'web_title': '在线测验系统',
                    'page_title': '进入题库',
                    'test_param': 'TEST PARAM',
                    'emptysearch': '2'
                })
            else:
                message = Course.objects.filter(name=course)
                print(message)
                for i in message:
                    course_id = i.id
                resultset = Question.objects.filter(course_id=course_id, chapter=chapter)
                print(resultset)
                for i in resultset:
                    result.append((i.content, i.id))
            return render(request, 'online_exam_search_out.html', {
                'web_title': '在线测验系统',
                'page_title': '进入题库',
                'test_param': 'TEST PARAM',
                'question_content': result,
                'course': course,
                'chapter': chapter
            })
        else:
            return render(request, 'online_exam_main.html', {
                'web_title': '在线测验系统',
                'page_title': '进入题库',
                'test_param': 'TEST PARAM',
                'emptysearch': '1'
            })
    return render(request, 'online_exam_main.html', {
        'web_title': '在线测验系统',
        'page_title': '进入题库',
        'test_param': 'TEST PARAM',
        'emptysearch': '0'
    })

def del_question(req):
    nid = req.GET.get('nid', None)
    course = req.GET.get('course', None)
    chapter = req.GET.get('chapter', None)
    delobj = Question.objects.get(id=nid)
    delobj.delete()
    # result = []
    # if course!='' and chapter=='':
    #     message = Course.objects.get(name=course)
    #     resultset = Question.objects.filter(course_id=message.id)
    #     print(resultset)
    #     for i in resultset:
    #         result.append((i.content,i.id))
    # else:
    #     message = Course.objects.filter(name=course)
    #     print(message)
    #     for i in message:
    #         course_id = i.id
    #     resultset = Question.objects.filter(course_id=course_id,chapter=chapter)
    #     print(resultset)
    #     for i in resultset:
    #         result.append((i.content,i.id))
    return redirect('/online_exam/')


def generate_paper(req):
    current_user_group = req.user.groups.first()
    print(current_user_group)
    if not current_user_group or current_user_group.name == 'student':
        return HttpResponseRedirect(reverse('login'))
    return render(req, 'online_exam_generate_paper.html', {
        'web_title': '在线测验系统',
        'page_title': '生成试卷',
        'test_param': 'TEST PARAM',
    })


def searchout(req):

    return render(req, 'online_exam_search_out.html', {
        'web_title': '在线测验系统',
        'page_title': '在线测验子系统',
        'test_param': 'TEST PARAM',
    })

def testinfo(request):
    current_user_group = request.user.groups.first()
    print(current_user_group)
    if not current_user_group:
        return HttpResponseRedirect(reverse('login'))
    elif current_user_group.name != 'teacher':
        return redirect('/online_exam/stu_testinfo/')
    t_id = request.user.id
    cursor = connection.cursor()
    list = []
    cursor.execute("select test_id from online_exam_test_teachers where teacher_id='%s'"%(t_id))
    tests = cursor.fetchall()
    print(tests)
    for item in tests:
        cursor.execute("select course_id from online_exam_test_courses where test_id='%s'" % (item[0]))
        courseid = cursor.fetchall()
        cursor.execute("select count(*) from online_exam_test_students where test_id='%s'" % (item[0]))
        stu_num = cursor.fetchall()
        cursor.execute("select start,end,paper_id from online_exam_test where id='%s'" % (item[0]))
        start = cursor.fetchall()
        print(item,start)
        print(courseid,stu_num)
        list.append((item[0], start[0][0], start[0][1], courseid[0][0], stu_num[0][0], start[0][2]))
    time1 = datetime.datetime.now()
    return render(request, 'online_exam_test_info.html', {
        'list': list,
        'time1': time1,
        'web_title': '在线测验系统',
        'page_title': '考试信息',
        'test_param': 'TEST PARAM',
    })


def calGrade(req):
    cursor = connection.cursor()
    dict = {'0': 'A', '1': 'B', '2': 'C', '3': 'D', '4': 'T', '5': 'F'}
    if req.method == 'POST':
        list = []
        num = req.POST.get('num')
        for i in range(int(num)):
            list.append(req.POST.get(str(i + 1)))
        print("list",list)
        testid = req.POST.get('testid')
        cursor.execute("select paper_id from online_exam_test where id='%s'" % (testid))
        pid = cursor.fetchall()
        cursor.execute("select * from online_exam_paper_questions where paper_id='%s'" % (pid[0][0]))
        result = cursor.fetchall()
        print("result",result)
        res = 0
        score = 0
        i = 0
        s_id = req.user.id
        for question in result:
            cursor.execute("select * from online_exam_question where id = '%s'" % (question[2]))
            result1 = cursor.fetchall()
            res += result1[0][4]
            q_id = question[2]
            print("answer",result1[0][3])
            if (list[i].strip())[0] == dict[result1[0][3]]:
                score += result1[0][4]
                it = StudentAnswer.objects.create(paper_id = pid[0][0],question_id = q_id,is_right=True,student_id= s_id,score=result1[0][4],test_id = testid)
            else:
                it = StudentAnswer.objects.create(paper_id=pid[0][0], question_id=q_id, is_right=False, student_id=s_id,
                                                  score=0,test_id=testid)
            i += 1
            it.save()
        weight = score / res
        time1 = datetime.datetime.now()
        it = Score.objects.create(paper_id=pid[0][0],student_id=s_id,score=score,weight=weight,date=time1,test_id=testid)
        it.save()
    return redirect('../main/')


def stu_testinfo(req):
    cursor = connection.cursor()
    list = []
    s_id = req.user.id
    cursor.execute("select * from online_exam_test")
    tests = cursor.fetchall()
    time1 = datetime.datetime.now()
    for item in tests:
        cursor.execute("select course_id from online_exam_test_courses where test_id='%s'" % (item[0]))
        courseid = cursor.fetchall()
        cursor.execute("select count(*) from online_exam_test_students where test_id='%s'" % (item[0]))
        stu_num = cursor.fetchall()
        t1 = (time1-item[1]).total_seconds()
        t2 = (item[2]-time1).total_seconds()
        join_t = cursor.execute("select score from online_exam_studentanswer where test_id = '%s' and student_id = '%s'" % (item[0],s_id))
        if t1 > 0 and t2>0 and join_t == 0:
            join = True
        else:
            join = False
        list.append((item[0], item[1], item[2], courseid[0][0], stu_num[0][0], item[3], join))
    return render(req, 'online_exam_stu_testinfo.html', {
        'list': list,
        'web_title': '在线测验系统',
        'page_title': '在线测验子系统',
        'test_param': 'TEST PARAM',
    })

def stu_exam(req):
    if req.method == "GET":
        testid = req.GET.get('test_id')
        cursor = connection.cursor()
        list = []
        time1 = datetime.datetime.now()
        cursor.execute("select course_id from online_exam_test_courses where test_id='%s'" % (testid))
        courseid = cursor.fetchall()
        cursor.execute("select count(*) from online_exam_test_students where test_id='%s'" % (testid))
        stu_num = cursor.fetchall()
        cursor.execute("select paper_id from online_exam_test where id='%s'" % (testid))
        pid = cursor.fetchall()
        cursor.execute("select start from online_exam_test where id='%s'" % (testid))
        start = cursor.fetchall()
        cursor.execute("select end from online_exam_test where id='%s'" % (testid))
        end = cursor.fetchall()
        cursor.execute("select count(*) from online_exam_paper_questions where paper_id='%s'" % (pid[0][0]))
        itemn = cursor.fetchall()
        list.append((testid, start[0][0], end[0][0], courseid[0][0], stu_num[0][0], pid[0][0], itemn[0][0], time1))
        list1 = []
        seconds = (end[0][0]-time1).total_seconds()
        cursor.execute("select * from online_exam_paper_questions where paper_id='%s'" % (pid[0][0]))
        result = cursor.fetchall()
        for question in result:
            cursor.execute("select * from online_exam_question where id = '%s'" % (question[2]))
            result1 = cursor.fetchall()
            list1.append((result1[0][2], result1[0][4]))
    return render(req, 'online_exam_stu_exam.html', {
        'list1': list1,
        'list': list,
        'seconds':seconds,
        'web_title': '在线测验系统',
        'page_title': '在线测验子系统',
        'test_param': 'TEST PARAM',
    })


def teach_detail(req):
    dict = {'0': 'A', '1': 'B', '2': 'C', '3': 'D', '4': 'T', '5': 'F'}
    if req.method == "GET":
        testid = req.GET.get('test_id')
        cursor = connection.cursor()
        list = []
        time1 = datetime.datetime.now()
        cursor.execute("select course_id from online_exam_test_courses where test_id='%s'" % (testid))
        courseid = cursor.fetchall()
        cursor.execute("select count(*) from online_exam_test_students where test_id='%s'" % (testid))
        stu_num = cursor.fetchall()
        cursor.execute("select paper_id from online_exam_test where id='%s'" % (testid))
        pid = cursor.fetchall()
        cursor.execute("select start from online_exam_test where id='%s'" % (testid))
        start = cursor.fetchall()
        cursor.execute("select end from online_exam_test where id='%s'" % (testid))
        end = cursor.fetchall()
        list.append((testid, start[0][0], end[0][0], courseid[0][0], stu_num[0][0], pid[0][0]))
        list1 = []
        cursor.execute("select * from online_exam_paper_questions where paper_id='%s'" % (pid[0][0]))
        result = cursor.fetchall()
        for question in result:
            cursor.execute("select * from online_exam_question where id = '%s'" % (question[2]))
            result1 = cursor.fetchall()
            list1.append((result1[0][1], result1[0][2], result1[0][4]))
    return render(req, 'online_exam_teach_detail.html', {
        'list': list,
        'list1': list1,
        'web_title': '在线测验系统',
        'page_title': '在线测验子系统',
        'test_param': 'TEST PARAM',
    })

def generate_paper_auto(request):
    user_id = request.user.id
    if request.method == 'GET':
        return render(request, 'online_exam_generate_paper_auto.html', {
            'web_title': '在线测验系统',
            'page_title': '自动生成试卷',
            'test_param': 'TEST PARAM',
            'majorlist': [{'id': 1, 'title': '123'},
                          {'id': 2, 'title': '123'}],
            'user_id': user_id
        })
    else:
        course = request.POST.get("course")
        chapterstart = request.POST.get("chapter1")
        chapterend = request.POST.get("chapter2")
        hard = request.POST.get('hard')
        totalscore = request.POST.get('totalscore')
        generate_auto(course, user_id, chapterstart, chapterend, hard, int(totalscore))
        return render(request, 'online_exam_generate_paper_auto_end.html', {
            'web_title': '在线测验系统',
            'page_title': '生成试卷',
            'test_param': 'TEST PARAM',
        })


def generate_auto(course, teacher_id, chapterstart, chapterend, hard, totalscore):
    message = Course.objects.get(name=course)
    course_id = message.id
    chapterstart = int(chapterstart)
    chapterend = int(chapterend)
    questionlist = []
    name = '自动出卷' + str(timezone.now())
    total_score = 0
    paperadd = Paper.objects.create(name=name, course_id=course_id, teacher_id=teacher_id, generate_time=timezone.now())
    for i in range(chapterstart, chapterend + 1):
        quest = Question.objects.filter(course_id=course_id, chapter=i)
        for j in quest:
            k = random.randint(1, 10)
            if k > 5:
                if total_score + j.value <= totalscore:
                    total_score += j.value
                    paperadd.questions.add(j)
    return


def generate_paper_handle(request):  # 手动出卷
    if request.method == 'POST':
        course = request.POST.get("course")
        message = Course.objects.get(name=course)
        resultset = Question.objects.filter(course_id=message.id)
        result = []
        for i in resultset:
            result.append((i.content, i.value, i.id, i.difficulty))
        return render(request, 'online_exam_generate_paper_handle_search.html', {
            'web_title': '在线测验系统',
            'page_title': '手动生成试卷',
            'test_param': 'TEST PARAM',
            'course': course,
            'questionlist': result
        })
    else:
        return render(request, 'online_exam_generate_paper_handle.html', {
            'web_title': '在线测验系统',
            'page_title': '手动生成试卷',
            'test_param': 'TEST PARAM',
        })


def generate_paper_handle_end(request):
    if request.method == 'POST':
        course = request.POST.get('course')
        course_id = Course.objects.get(name=course).id
        uid = request.POST.getlist('uid')
        paperadd = Paper.objects.create(name='手动出卷', course_id=course_id, teacher_id=1, generate_time=timezone.now())
        for id in uid:
            quest = Question.objects.filter(id=int(id))
            paperadd.questions.add(*quest)
        return render(request, 'online_exam_generate_paper_handle_end.html', {
            'web_title': '在线测验系统',
            'page_title': '手动生成试卷',
            'test_param': 'TEST PARAM',
        })


def add_question(request):
    if request.method == 'POST':
        course = request.POST.get('course')
        value = request.POST.get('value')
        chapter = request.POST.get('chapter')
        m_course = Course.objects.get(name=course)
        question_type = request.POST.get('question_type')
        right_answer = request.POST.get('right_answer')
        content = request.POST.get('content')
        dif = request.POST.get('difficulty')
        if len(content) > 0 and right_answer != None:
            Question.objects.create(course=m_course, type=question_type, content=content,
                                    answer=str(int(right_answer) - 1), value=value, chapter=chapter, difficulty=dif)
        return redirect('/online_exam/')
    else:
        course = request.GET.get('course', None)
        return render(request, 'online_exam_add_question.html', {
            'web_title': '在线测验系统',
            'page_title': '添加题目',
            'test_param': 'TEST PARAM',
            'course': course
        })


def combineanalysis(req):
    # 这里估计要根据html相应的改，暂且发送的请求里叫做testID吧
    testID = req.GET.get('testID')
    cursor = connection.cursor()

    # cursor.execute(
    #     "select first_name,last_name,date,score from auth_user natural join online_exam_score where paper_id=%d" % paperID)
    # cursor.execute(
    #     "select first_name,last_name,date,score from auth_user natural join online_exam_score where paper_id=1234")
    cursor.execute("select first_name, last_name, date, score, student_id from auth_user, online_exam_score where online_exam_score.student_id = auth_user.id and test_id=%s", [testID])
    rst1 = cursor.fetchall()
    print(rst1)
    cursor.execute(
        "select question_id,count(id) from online_exam_studentanswer "
        "where test_id=%d and is_right=1 group by question_id" % int(testID))
    #cursor.execute(
    #    "select question_id,count(id) from online_exam_studentanswer where is_right=1 group by question_id")
    rst2 = cursor.fetchall()
    return render(req, 'online_exam_combine_analysis.html', {
        'web_title': '在线测验系统',
        'page_title': '试卷分析',
        'test_param': 'TEST PARAM',
        'score_content': rst1,
        'correct': rst2
    })

def stusingleselect(req):
    # nid = req.GET.get('nid')
    # name = req.GET.get('name')
    student_id = req.GET.get('student_id')

    cursor = connection.cursor()
    # cursor.execute("select id from online_exam_paper where name='%s'" % (name))
    # result = cursor.fetchall()
    # cursor.execute("select student_id,date,score from online_exam_score where paper_id=%d" % (result[0][0]))
    # result2 = cursor.fetchall()
    cursor.execute("select online_exam_paper.id, name from online_exam_paper, online_exam_score where online_exam_paper.id = online_exam_score.paper_id and online_exam_score.student_id = %s",[student_id])
    result = cursor.fetchall()
    return render(req, 'online_exam_stu_single_select.html', {
        'web_title': '在线测验系统',
        'page_title': '在线测验子系统',
        'test_param': 'TEST PARAM',
        'student_id': student_id,
        'score_content': result
    })


def stusingle(req):
    if req.method == "GET":
        # nid = req.GET.get('nid')
        # name = req.GET.get('name')
        student_id = req.GET.get('student_id')
        if not student_id:
            student_id = req.user.id
        id_select = '1234'
        cursor = connection.cursor()
        # cursor.execute("select id from online_exam_paper where name='%s'" % (name))
        # result = cursor.fetchall()
        # cursor.execute("select student_id,date,score from online_exam_score where paper_id=%d" % (result[0][0]))
        # result2 = cursor.fetchall()
        cursor.execute("select content,score,is_right from online_exam_studentanswer,online_exam_question "
                       "where student_id= %s and online_exam_studentanswer.question_id = online_exam_question.id and paper_id = %s",
                       [student_id, id_select])
        result = cursor.fetchall()
        return render(req, 'online_exam_stu_single.html', {
            'web_title': '在线测验系统',
            'page_title': '成绩分析',
            'test_param': 'TEST PARAM',
            'id_select': 100000,
            'student_id': student_id,
            'score_content': result
        })
    else:
        # nid = req.GET.get('nid')
        # name = req.GET.get('name')
        id_select = req.POST.get("id_select")
        student_id = req.POST.get("student_id")
        cursor = connection.cursor()
        # cursor.execute("select id from online_exam_paper where name='%s'" % (name))
        # result = cursor.fetchall()
        # cursor.execute("select student_id,date,score from online_exam_score where paper_id=%d" % (result[0][0]))
        # result2 = cursor.fetchall()
        # cursor.execute("select content,score,is_right from online_exam_studentanswer,online_exam_question where student_id= 1 and online_exam_studentanswer.question_id = online_exam_question.id and paper_id = %s",[id_select,])

        cursor.execute("select content,score,is_right from online_exam_studentanswer,online_exam_question "
                       "where student_id= %s and online_exam_studentanswer.question_id = online_exam_question.id and paper_id = %s",
                       [student_id, id_select])

        result = cursor.fetchall()
        return render(req, 'online_exam_stu_single.html', {
            'web_title': '在线测验系统',
            'page_title': '成绩分析',
            'test_param': 'TEST PARAM',
            'id_select': id_select,
            'student_id': student_id,
            'score_content': result
        })


def release(request):
    if request.method == 'GET':
        teacher_id = request.user.id
        cursor = connection.cursor()
        course_id = []
        course_name = []
        paper_id = []
        paper_name = []
        if teacher_id is not None:
            cursor.execute("select id,course_id from online_exam_paper where teacher_id='%s'" % teacher_id)
            test_id = cursor.fetchall()  # 得到所有的试卷id
            for one_id in test_id:
                course_id.append(one_id[1])
                paper_id.append(one_id[0])
                cursor.execute(
                    "select name from info_mgt_course  where id = %s " % one_id[1])
                course_nm = cursor.fetchall()
                course_name.extend(course_nm)
                cursor.execute("select name from online_exam_paper where id = {}".format(one_id[0]))
                paper_nm = cursor.fetchall()
                paper_name.extend(paper_nm)
            print(course_name, course_id, paper_name, paper_id)
            res = []
            for item in range(len(course_id)):
                res.append((course_id[item], course_name[item], paper_id[item], paper_name[item]))
            print(res)
        else:
            res = []
        return render(request, 'online_exam_release_test.html', {
            'web_title': '在线测验系统',
            'page_title': '发布测试',
            'test_param': 'TEST PARAM',
            'tests': res,
            'student_id': None,
        })
    if request.method == "POST":
        teacher_id = request.user.id
        paper_id = request.POST.get('paper_id', None)
        course_id = request.POST.get('course_id', None)
        start = request.POST.get('start_time')
        start0 = list(start)
        start = []
        for item in start0:
            if item == 'T':
                start.append(' ')
            else:
                start.append(item)
        start.append(':')
        start.append('0')
        start.append('0')
        print("start:", start)
        start = ''.join(start)
        end = request.POST.get('end_time')
        end0 = list(end)
        end = []
        for item in end0:
            if item == 'T':
                end.append(' ')
            else:
                end.append(item)
        end.append(':')
        end.append('0')
        end.append('0')
        end = ''.join(end)
        print("start: ", start)
        print("end :", end)
        start = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
        end = datetime.datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
        cursor = connection.cursor()
        # sql = "insert into online_exam_test values ({0},{1},{2})".format(start, end, paper_id)
        # print(sql)
        myadd = Test.objects.create(start=start, end=end, paper_id=paper_id)
        # cursor.execute(sql)
        test_id = myadd.id
        print("test_id: ", test_id)
        # mycourse = Course.objects.get(course_id=course_id)
        sql = "insert into online_exam_test_courses(test_id, course_id) values({0},{1})".format(test_id, course_id)
        print(sql)
        cursor.execute(sql)
        cursor.execute("insert into online_exam_test_teachers(test_id, teacher_id) values({0},{1})".format(test_id, teacher_id))
        sql = "select info_mgt_majorhascourse.major_id from info_mgt_class  join info_mgt_majorhascourse on info_mgt_class.course_id=info_mgt_majorhascourse.course_id where teacher_id = {0} and info_mgt_class.course_id = {1}".format(teacher_id,course_id)
        print(sql)
        cursor.execute(sql)
        student_id_all = []
        major_id_all = cursor.fetchall()
        for major in major_id_all:
            sql = "select id from info_mgt_student where major_id = {0}".format(major[0])
            cursor.execute(sql)
            student_id = cursor.fetchall()
            print("student_id:",student_id)
            student_id_all.extend(student_id)
        student_id_all = list(set(student_id_all))
        print("student_id_all:",student_id_all)
        print("course_id_all:",major_id_all)
        for student_id in student_id_all:
            sql = "insert into online_exam_test_students(test_id,student_id) values ({0},{1})".format(test_id,student_id[0])
            cursor.execute(sql)


        return redirect("./?teacher_id={}".format(teacher_id))


def delete_test(request):
    paper_id = request.GET.get('paper_id', None)
    teacher_id = request.GET.get('teacher_id', None)
    cursor = connection.cursor()
    cursor.execute("delete from  online_exam_paper where paper_id = {0}".format(paper_id))
    cursor.execute("delete from online_exam_paper_questions where paper_id = {0}".format(paper_id))
    redirect("./online_exam_release_test?teacher_id={}".format(teacher_id))
