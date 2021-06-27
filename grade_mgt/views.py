from django.db.models import manager
from class_selection.forms import Major
from django.db.models.aggregates import Count
from class_schedule.models import ClassHasRoom, Classroom
from typing import Coroutine
from django.db import models, reset_queries
from django.shortcuts import redirect, render
from django.http.response import HttpResponse
# from grade_mgt.models import CourseResult
from info_mgt.models import Class, Course, Teacher, Major, Student, Avatar
from grade_mgt.models import CourseResult, ChangeResult
from class_selection.models import StuHasClass
from .models import *
import json
from django.contrib.auth.models import User
from django.utils import timezone
# Create your views here.

def index(request):
    # return HttpResponse(request.user.id)
    userid=request.user.id
    print(userid)

    stu_list=list(Student.objects.values().filter(user_id=userid))
    admin_list=list(Avatar.objects.filter(user_id=userid))
    print(admin_list)
    print(stu_list)
    i=0

    
    if stu_list:
        
        stuid=stu_list[0]['id']
        print(stuid)
        graderesult=CourseResult.objects.all().filter(student=stuid).filter(is_submit=1)
        gradelist=list(CourseResult.objects.values('final_result').filter(student=stuid).filter(is_submit=1))
        courseresult2=[]
        i=0
        gp=0
        credit=0

        sumscore=0
        sumgp=0
        sum=0
        avg=0
        avggp=0
        #print(gradelist)
        for graderes in graderesult:
            courseresult1=list(graderes.course.all().values('id','name','credit'))
            # print(courseresult1[0])
            courseresult1[0]['final_result']=gradelist[i]['final_result']

            credit=courseresult1[0]['credit']
            grade=gradelist[i]['final_result']
            gp = calculategp(grade)
            courseresult1[0]['gp']=gp
            courseresult2.append(courseresult1[0])
            #print(gradelist)
            sumscore=sumscore+credit
            sumgp=sumgp+gp*credit
            sum=sum+grade*credit

            i=i+1
            
                       

            # print(courseresult1)
        # print(courseresult2)
        # # resultid=graderesult1[0]['id']
        # # test1=list(Course.objects.values())
        # # courseresult1=list(CourseResult.objects.values())
        if(sumscore==0):
            avg=0
            avggp=0
        else:
            avg=sum/sumscore
            avggp=sumgp/sumscore

        
        #print(courseresult2)
        #print(gradelist)
        # # return HttpResponse(graderesult1)
        return render(request,"grade_mgt.html",{
            'web_title':'成绩管理',
            'page_title':"成绩管理",
            'course_list':courseresult2,
            'grade_list':gradelist,
            'sum':sumscore,
            'avg':avg,
            'avggp':avggp
        })

    elif admin_list:                   
        result=gotchangelist()  
        return render(request,"grade_mgt_admin.html",{
            'web_title':'成绩管理',
            'page_title':"成绩管理",
            'result':result
        })

    else:
        userid=request.user.id
        # print(userid)
        courselist=list(Class.objects.values().filter(teacher_id=userid).order_by('course_id'))
        # print(courselist)
        listtoshow=[]
        classtakentime=[]
        wlist=[]
        classidlist=[]
        for course in courselist:
            classid=course['id']
            # print(classid)
            classidlist.append(classid)
            classres=list(ClassHasRoom.objects.values('id','day','start_at','duration','Class_id').filter(Class_id=classid))
            # print(classres)
            for classres1 in classres:
                classres1['date']=numswitch(classres1['day'])
                classres1['timespan']=getspan(classres1['start_at'],classres1['duration'])
                classtakentime.append({'Class_id':classres1['Class_id'],'date':numswitch(classres1['day']),'timespan':getspan(classres1['start_at'],classres1['duration'])})
            listtoshow.append(classres1)
        # print(listtoshow)
        # print(classidlist)
        for classid1 in classidlist:
            wlist.append({'Class_id':classid1,'time':[]})
        # print(wlist)
        # print(classtakentime)
        for wlist1 in wlist:
            anwserlist=[]
            for classtaken in classtakentime:
                if (classtaken['Class_id']==wlist1['Class_id']):
                    anwserlist.append({'date':classtaken['date'],'timespan':classtaken['timespan']})
            wlist1['time']=anwserlist
        # print(wlist)
            
        course_dict={}
        for course in courselist:
            course_dict[course['course_id']]=[]
        for course in courselist:
            course_dict[course['course_id']].append(course)
        # print(course_dict)
        coursename=[]
        i=0
        for course_id,courseinfo in course_dict.items():
            # print(course_id)
            # print(courseinfo)
            course=list(Course.objects.values('name').filter(id=course_id))
            # classinfo=list(Class.objects.values('year','term').filter(course_id=course_id).filter(teacher_id=userid))
            # print(course)
            # extrainfo=list(ClassHasRoom.objects.values().filter())
            # course[0]['time']=classinfo
            course[0]['info_list']=courseinfo
            # course[0]['class_list']=wlist[i]
            # i+=1
            templist=[]
            for wlist1 in wlist:
                for courseinfo1 in courseinfo:
                    if wlist1['Class_id']==courseinfo1['id']:
                       templist.append(wlist1)
            course[0]['class_list']=templist  
            coursename.append(course[0])
        # print(coursename)
        return render(request, "grade_detail_course.html", {
        'web_title': '成绩管理',
        'page_title': "成绩管理",
        'wholelist':coursename
    }) 

def grade_detail(request):
    courseid=0
    if request.POST:
        dict_p = request.POST
        for k,v in dict_p.items():
            if (v=='查看详情'):
                courseid=k
                request.session['passcourseid']=courseid
    else:
        courseid=request.session.get('passcourseid')
    courseinfo=list(Course.objects.values('id','name','credit').filter(id=courseid))
    classinfo=list(Class.objects.values('year','term').filter(course_id=courseid))
    # print(classinfo)
    courseinfo[0]['year']=classinfo[0]['year']
    courseinfo[0]['term']=classinfo[0]['term']
    gradeinfo=CourseResult.objects.all().filter()
    # print(gradeinfo)
    # print("courseid:"+courseid)
    gradeinfolist=[]
    for gradein in gradeinfo:
        gradelist1=list(gradein.course.all().values('id','courseresult'))
        print(gradelist1[0]['id'])
        print(gradelist1[0]['courseresult'])
        # print(type(courseid))
        # print(type(gradelist1[0]['id']))
        if (gradelist1[0]['id'] == int(courseid)):
            courseresultid=gradelist1[0]['courseresult']
            gradeinfolist=list(CourseResult.objects.values().filter(id=courseresultid))
            break
    print(gradeinfolist)
    courseinfo[0]['class_performance']=gradeinfolist[0]['class_performance']
    courseinfo[0]['exam_result']=gradeinfolist[0]['exam_result']
    courseinfo[0]['final_result']=gradeinfolist[0]['final_result']
    courseinfo[0]['gp']=calculategp(gradeinfolist[0]['final_result'])
        # print(gradelist1)
    # print("gradeinfo"+gradeinfo)
    # print(courseinfo)

    return render(request,"grade_detail.html",{
        'web_title':'成绩详情',
        'page_title':'成绩详情',
        'detail_info':courseinfo
    })

# def detailcourseindex(request):
#     userid=request.user.id
#     courselist=Class.objects.values().filter(teacher_id=userid)
#     return render(request, "grade_detail_course.html", {
#         'web_title': '成绩管理',
#         'page_title': "成绩管理",
#     })

def detailclassindex(request):
    isordered=0
    sub=0
    order='up_id'
    if request.POST:
        dict_P = request.POST
        for k,v in dict_P.items():
            if (k=='排序'):
                isordered=1
                classid = request.session.get('pastinfo')
                if (v=='按学号降序'):
                    order='down_id'
                elif (v=='按学号升序'):
                    order='up_id'
                elif (v=='按成绩降序'):
                    order='down_grade'
                else:
                    order='up_grade'                    
            if(v=='submit'):
                sub=1
                isordered=1
                classid = request.session.get('pastinfo')
        if isordered==0:
            classid=0
            for k,v in dict_P.items():
                if (v=='查看详情'):
                    classid=k
            request.session['pastinfo']=classid
            courselist=list(Class.objects.values('course_id').filter(id=classid))
            course_id=courselist[0]['course_id']
            request.session['pastcourseinfo']=course_id
            order='up_id'

    else:
        classid = request.session.get('pastinfo')
    classinfo=list(Class.objects.values().filter(id=classid))
    courseid=classinfo[0]['course_id']
    courseinfo=list(Course.objects.values('name').filter(id=courseid))
    classtaketimetemp=[]
    classtime=[]
    classtimeinfo=list(ClassHasRoom.objects.values('id','day','start_at','duration','Class_id').filter(Class_id=classid))
    for classtime_info in classtimeinfo:
        classtime_info['date']=numswitch(classtime_info['day'])
        classtime_info['timespan']=getspan(classtime_info['start_at'],classtime_info['duration'])
        classtaketimetemp.append({'Class_id':classtime_info['Class_id'],'date':numswitch(classtime_info['day']),'timespan':getspan(classtime_info['start_at'],classtime_info['duration'])})
    for i in classtaketimetemp:
        classtime.append({'date':i['date'],'timespan':i['timespan']})
    # print(classtime)
    # print(classtimeinfo)
    # print(classtaketimetemp)
    # print(courseinfo)
    # print(classinfo)
    # return HttpResponse(count)
    stulist=list(StuHasClass.objects.values('Student_id').filter(Class_id=classid))
    stuinfolist=[]
    stugrade=[]
    is_sub=0

    sum=0
    count=0
    
    
    print(stulist)
    for stu in stulist:
        student=list(Student.objects.values().filter(id=stu['Student_id']))
        # print(student)
        stunamelist=list(User.objects.values('last_name','first_name').filter(id=student[0]['user_id']))
        # print(stunamelist)
        majorlist=list(Major.objects.values('name').filter(id=student[0]['major_id']))
        # print(majorlist)
        student[0]['major']=majorlist[0]['name']
        name=stunamelist[0]['last_name']+stunamelist[0]['first_name']
        # print(name)
        student[0]['name']=name
        # print(student)
        
        resultqueue=list(CourseResult.objects.all().values('is_submit','final_result').filter(Class=classid).filter(student=stu['Student_id']))
        #print(resultqueue)
        
        if resultqueue:
            stugrade.append({'id':stu['Student_id'],'grade':resultqueue[0]['final_result']})
            student[0]['grade']=resultqueue[0]['final_result']
            student[0]['gp']=calculategp(student[0]['grade'])
            is_sub=resultqueue[0]['is_submit']

            count=count+1
            sum=sum+student[0]['grade']
        stuinfolist.append(student[0])
    if (is_sub==0 and sub==1):
        CourseResult.objects.filter(Class=classid).update(is_submit = 1)
        is_sub=1

    if(count==0):
        avg=0
        avggp=0
    else:
        avg=sum/count
        avggp=calculategp(avg)

    if (order=='up_id'):
        stuinfolist.sort(key=lambda x:x['id'],reverse=False)
    elif (order=='down_id'):
        stuinfolist.sort(key=lambda x:x['id'],reverse=True)
    elif (order=="down_grade"):
        stuinfolist.sort(key=lambda x:x['grade'],reverse=True)
    else:
        stuinfolist.sort(key=lambda x:x['grade'],reverse=False)

    print(stuinfolist)
    grade=stugrade
    gradespan={'jiu':0,'ba':0,'qi':0,'liu':0,'fail':0}
    print(stugrade)
    for g in grade:
        if g['grade']>=90:
            gradespan['jiu']+=1
        elif g['grade']>=80:
            gradespan['ba']+=1
        elif g['grade']>=70:
            gradespan['qi']+=1
        elif g['grade']>=60:
            gradespan['liu']+=1
        else:
            gradespan['fail']+=1
    
    # resultqueue=list(CourseResult.objects.all().values().filter(Class=classid))

    # print(resultqueue)
    # resultlist=[]
    # for result in resultqueue:
    #     resultlist1=list(result.Class.all().values())
    #     resultlist.append(resultlist1)
    # print(resultlist)

    return render(request, "grade_detail_class.html", {
        'web_title': '成绩管理',
        'page_title': "成绩管理",
        'classinfo':classinfo,
        'courseinfo':courseinfo,
        'classtime':classtime,
        'stuinfo':stuinfolist,
        'is_submit':is_sub,
        'gradespan':json.dumps(gradespan),

        'avg':avg,
        'avggp':avggp
        # 'stulist':stulist
    })



def index_teacher(request):
    return render(request, "grade_mgt_teacher.html", {
        'web_title': '成绩管理',
        'page_title': "成绩管理",
    })

def updating(request):
    classid = request.session.get('pastinfo')
    classinfo=list(Class.objects.values().filter(id=classid))
    courseid=classinfo[0]['course_id']
    courseinfo=list(Course.objects.values('name').filter(id=courseid))
    classtaketimetemp=[]
    classtime=[]
    classtimeinfo=list(ClassHasRoom.objects.values('id','day','start_at','duration','Class_id').filter(Class_id=classid))
    for classtime_info in classtimeinfo:
        classtime_info['date']=numswitch(classtime_info['day'])
        classtime_info['timespan']=getspan(classtime_info['start_at'],classtime_info['duration'])
        classtaketimetemp.append({'Class_id':classtime_info['Class_id'],'date':numswitch(classtime_info['day']),'timespan':getspan(classtime_info['start_at'],classtime_info['duration'])})
    for i in classtaketimetemp:
        classtime.append({'date':i['date'],'timespan':i['timespan']})
    # print(classtime)
    # print(classtimeinfo)
    # print(classtaketimetemp)
    # print(courseinfo)
    # print(classinfo)
    # return HttpResponse(count)
    stulist=list(StuHasClass.objects.values('Student_id').filter(Class_id=classid))
    stuinfolist=[]
    stugrade=[]
    is_sub=0
    # print(stulist)
    for stu in stulist:
        student=list(Student.objects.values().filter(id=stu['Student_id']))
        # print(student)
        stunamelist=list(User.objects.values('last_name','first_name').filter(id=student[0]['user_id']))
        # print(stunamelist)
        majorlist=list(Major.objects.values('name').filter(id=student[0]['major_id']))
        # print(majorlist)
        student[0]['major']=majorlist[0]['name']
        name=stunamelist[0]['last_name']+stunamelist[0]['first_name']
        # print(name)
        student[0]['name']=name
        # print(student)
        resultqueue=list(CourseResult.objects.all().values('is_submit','final_result','class_performance','exam_result').filter(Class=classid).filter(student=stu['Student_id']))
        if resultqueue:
            stugrade.append({'id':stu['Student_id'],'grade':resultqueue[0]['final_result'],'class_performance':resultqueue[0]['class_performance'],'exam_result':resultqueue[0]['exam_result']})
            student[0]['class_performance']=resultqueue[0]['class_performance']
            student[0]['exam_result']=resultqueue[0]['exam_result']
            student[0]['grade']=resultqueue[0]['final_result']
            student[0]['gp']=calculategp(student[0]['grade'])
            is_sub=resultqueue[0]['is_submit']
        stuinfolist.append(student[0])
    # print(stuinfolist)
    grade=stugrade
    return render(request,"grade_detail_class_updating.html",{
        'webtitle':'成绩录入',
        'pagetitile':'成绩录入',
        'classinfo':classinfo,
        'courseinfo':courseinfo,
        'classtime':classtime,
        'stuinfo':stuinfolist,
        'is_submit':is_sub,
    })

def grade_update(request):
    classid=request.session.get('pastinfo')
    courselist=list(Class.objects.values('course_id').filter(id=classid))
    gradelist=[]
    courseid=courselist[0]['course_id']
    dict_P = request.POST
    i=1
    tempdict={}
    for k,v in dict_P.items():
        if (k != "csrfmiddlewaretoken"):
            if (i%3==1):
                tempdict['class_performance']=v
                i+=1
            elif (i%3==2):
                tempdict['exam_result']=v
                i+=1
            else:
                tempdict['final_result']=v
                tempdict['stu_id']=k
                print(tempdict)
                gradelist.append({'stu_id':tempdict['stu_id'],'class_performance':tempdict['class_performance'],'exam_result':tempdict['exam_result'],'final_result':tempdict['final_result']})
                i+=1   
    print(gradelist)
    for result in gradelist:
        res = CourseResult.objects.values().filter(Class=classid).filter(student=result['stu_id'])
        if res:
            #print('no')
            res.update(class_performance=result['class_performance'],exam_result=result['exam_result'],final_result=result['final_result'])
        else:
            #print('yes')
            res = CourseResult.objects.create(is_submit=0,class_performance=result['class_performance'],exam_result=result['exam_result'],final_result=result['final_result'])
            stu = Student.objects.filter(id=result['stu_id']).first()
            cour = Course.objects.filter(id=courseid).first()
            clas = Class.objects.filter(id=classid).first()
            res.student.add(stu)
            res.course.add(cour)
            res.Class.add(clas)
            res = CourseResult.objects.values().filter(Class=classid).filter(student=result['stu_id'])
        #print(res)
    return redirect('grade_detail_class')

def change_submit(request):
    time=timezone.localtime()
    
    time=time.strftime('%Y-%m-%d %H:%M:%S')
    print(time)
    classid=request.session.get('pastinfo')
    courselist=list(Class.objects.values('course_id').filter(id=classid))
    gradelist=[]
    courseid=courselist[0]['course_id']
    dict_P = request.POST
    i=1
    tempdict={}
    for k,v in dict_P.items():
        if (k != "csrfmiddlewaretoken"):
            if (i%3==1):
                tempdict['class_performance']=v
                i+=1
            elif (i%3==2):
                tempdict['exam_result']=v
                i+=1
            else:
                tempdict['final_result']=v
                tempdict['stu_id']=k
                print(tempdict)
                gradelist.append({'stu_id':tempdict['stu_id'],'class_performance':tempdict['class_performance'],'exam_result':tempdict['exam_result'],'final_result':tempdict['final_result']})
                i+=1   
        if (k=='reason'):
            tempreason=v

    #print(gradelist)
    for result in gradelist:
        res = ChangeResult.objects.values().filter(Class=classid).filter(student=result['stu_id']).filter(permit=0)
        if res:
            res.update(permit=0, submit_time=time,reason=tempreason,class_performance=result['class_performance'],exam_result=result['exam_result'],final_result=result['final_result'])
        else:
            res = ChangeResult.objects.create(permit=0, submit_time=time,reason=tempreason,class_performance=result['class_performance'],exam_result=result['exam_result'],final_result=result['final_result'])
            stu = Student.objects.filter(id=result['stu_id']).first()
            cour = Course.objects.filter(id=courseid).first()
            clas = Class.objects.filter(id=classid).first()
            res.student.add(stu)
            res.Class.add(clas)
            res = ChangeResult.objects.values().filter(Class=classid).filter(student=result['stu_id'])
        #print(res)
    return redirect('grade_detail_class')

def operator_admin(request):
    
    dict_P = request.POST
    op=-1
    #print("op")
    for k,v in dict_P.items():
        if (v=='同意'):
            classid=k
            op=1
            res = ChangeResult.objects.values().filter(Class=classid).filter(permit=0)
            break
        if (v=='不同意'):
            classid=k
            op=0
            res = ChangeResult.objects.values().filter(Class=classid).filter(permit=0)
            break
    if(op==0):
        op=0
        res.update(permit=1)
    elif(op==1):
        op=1  
        i=0      
        stu=StuHasClass.objects.all().values().filter(Class_id=classid)
        print(classid)
        # oldlist=list(CourseResult.objects.values('student').filter(Class=classid))
        stulist=list(StuHasClass.objects.values('Student_id').filter(Class_id=classid))
        for st in stu:
            stu_id=stulist[i]['Student_id']
            print(stu_id)
            new=list(res.values('class_performance','exam_result','final_result').filter(student=stu_id))
            # print(new)
            up=CourseResult.objects.values().filter(Class=classid).filter(student=stu_id)
            # print(up)
            if new and up:
                up.update(class_performance=new[0]['class_performance'],exam_result=new[0]['exam_result'],final_result=new[0]['final_result'])
            i=i+1
            

        res.update(permit=1)

    result=gotchangelist() 
    return render(request,"grade_mgt_admin.html",{
        'web_title':'成绩管理',
        'page_title':"成绩管理",
        'result':result
    })

        


def gotchangelist():
    changelist=[]
    courselist0=[]
    courselist=[]
    result=[]
    change=ChangeResult.objects.all().filter(permit=0).order_by('submit_time')
    changelist=list(ChangeResult.objects.values('Class','submit_time','reason').filter(permit=0))
    print(change)
    i=0
    j=0
       
    for changeres in change:
        classid=changelist[j]['Class']
        print(j)
        #print(classid)
        courselist0=list(changeres.Class.all().values('id','year','term','course','teacher').filter(id=classid))
        check=0
        for k in result:
            if k['Class']==classid:
                check=1
                break
        print(courselist0)
        print(check)
        if (courselist0 and check==0):
            result.append(changelist[j])
            print(changelist[j])
            courseid=courselist0[0]['course']
            teacherid=courselist0[0]['teacher']
            result[i]['localtime']=timezone.localtime(result[i]['submit_time'])
            print(result[i]['submit_time'].strftime('%Y-%m-%d %H:%M:%S'))
            print(result[i]['localtime'].strftime('%Y-%m-%d %H:%M:%S'))
            
            time1=timezone.now()
            time1=time1.strftime('%Y-%m-%d %H:%M:%S')
            print(time1)
            time2=timezone.localtime()
            time2=time2.strftime('%Y-%m-%d %H:%M:%S')
            print(time2)
            result[i]['courseid']=courseid
            result[i]['year']=courselist0[0]['year']
            result[i]['term']=courselist0[0]['term']
            result[i]['coursename']=list(Course.objects.values('name').filter(id=courseid))[0]['name']
            teachernamelist=list(User.objects.values('first_name','last_name').filter(id=teacherid))
            result[i]['teachername']=teachernamelist[0]['first_name']+' '+teachernamelist[0]['last_name']

            classtaketimetemp=[]
            classtime=[]
            classtimeinfo=list(ClassHasRoom.objects.values('id','day','start_at','duration','Class_id').filter(Class_id=classid))
            for classtime_info in classtimeinfo:
                classtime_info['date']=numswitch(classtime_info['day'])
                classtime_info['timespan']=getspan(classtime_info['start_at'],classtime_info['duration'])
                classtaketimetemp.append({'Class_id':classtime_info['Class_id'],'date':numswitch(classtime_info['day']),'timespan':getspan(classtime_info['start_at'],classtime_info['duration'])})
            for ii in classtaketimetemp:
                classtime.append({'date':ii['date'],'timespan':ii['timespan']})
            result[i]['time']=classtime
            # print(i)
            i=i+1

                
        j=j+1  
    print(result)
    return result     





def getspan(start,duration):
    i = duration
    res=[]
    while (i>0):
        res.append(start)
        start+=1
        i-=1
    return res
def numswitch(num):
    res="一"
    if (num==1):
        res="一"
    elif (num==2):
        res="二"
    elif (num==3):
        res="三"
    elif (num==4):
        res="四"
    elif (num==5):
        res="五"
    elif (num==6):
        res="六"
    else:
        res="七"
    return res
def calculategp(grade):
    gp=0
    if (grade>=95):
            gp=5.0
    elif (grade>=92):
        gp=4.8
    elif (grade>=89):
        gp=4.5
    elif (grade>=86):
        gp=4.2
    elif (grade>=83):
        gp=3.9
    elif (grade>=80):
        gp=3.6
    elif (grade>=77):
        gp=3.3
    elif (grade>=74):
        gp=3.0
    elif (grade>=71):
        gp=2.7
    elif (grade>=68):
        gp=2.4
    elif (grade>=65):
        gp=2.1
    elif (grade>=62):
        gp=1.8
    elif (grade>=60):
        gp=1.5
    else:
        gp=0
    return gp