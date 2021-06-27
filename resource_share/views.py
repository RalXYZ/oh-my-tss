import os
from django.http.response import HttpResponseNotModified, HttpResponsePermanentRedirect
from django.shortcuts import redirect, render
from .models import *
from info_mgt.models import *
from django.views.decorators.http import require_GET,require_POST
from grade_mgt.models import *
from class_selection.models import *
from django.http import HttpResponse
from grade_mgt.views import *
from django.core.files import File
from django.utils.http import urlquote
# Create your views here.
def index(request):
    rootpath=os.getcwd()
    request.session['rootpath']=rootpath
    class_resource = Source.objects.exclude(Class=None).values_list('Class', flat=True)
    # print(class_resource)
    userid=request.user.id
    stu_list=list(Student.objects.values().filter(user_id=userid))
    if stu_list:
        studentid=stu_list[0]['id']
        # print(studentid)
        classlist=list(StuHasClass.objects.values('Class_id').filter(Student_id=studentid))
        print(classlist)
        listtoshow=[]
        classtakentime=[]
        classidlist=[]
        wlist=[]
        for class1 in classlist:
            classid=class1['Class_id']
            classidlist.append(classid)
            courselist=list(Class.objects.values('course_id').filter(id=classid))
            courseid=courselist[0]['course_id']
            courseinfo=list(Course.objects.values('name').filter(id=courseid))
            classres=list(ClassHasRoom.objects.values('id','day','start_at','duration','Class_id').filter(Class_id=classid))
            # print(classres)
            for classres1 in classres:
                classres1['date']=numswitch(classres1['day'])
                classres1['timespan']=getspan(classres1['start_at'],classres1['duration'])
                classtakentime.append({'Class_id':classres1['Class_id'],'date':numswitch(classres1['day']),'timespan':getspan(classres1['start_at'],classres1['duration'])})
            listtoshow.append(classres1)
            # print(listtoshow)
        print(classtakentime)
        for classid1 in classidlist:
            wlist.append({'Class_id':classid1,'time':[]})
        # print(wlist)
        # print(classtakentime)
        for wlist1 in wlist:
            classid=wlist1['Class_id']
            courselist=list(Class.objects.values('course_id').filter(id=classid))
            courseid=courselist[0]['course_id']
            courseinfo=list(Course.objects.values('name').filter(id=courseid))
            coursename=courseinfo[0]['name']
            wlist1['course_id']=courseid
            wlist1['coursename']=coursename
            anwserlist=[]
            for classtaken in classtakentime:
                if (classtaken['Class_id']==wlist1['Class_id']):
                    anwserlist.append({'date':classtaken['date'],'timespan':classtaken['timespan']})
            wlist1['time']=anwserlist
        print(wlist)
        return render(request,"resource_share.html",{
            'web_title':'课程资源',
            'page_title':'课程资源',
            'wlist':wlist
        })
    else:
        courselist=list(Class.objects.values().filter(teacher_id=userid).order_by('course_id'))
        listtoshow=[]
        classtakentime=[]
        wlist=[]
        classidlist=[]
        for course in courselist:
            classid=course['id']            
            classidlist.append(classid)
            classres=list(ClassHasRoom.objects.values('id','day','start_at','duration','Class_id').filter(Class_id=classid))            
            for classres1 in classres:
                classres1['date']=numswitch(classres1['day'])
                classres1['timespan']=getspan(classres1['start_at'],classres1['duration'])
                classtakentime.append({'Class_id':classres1['Class_id'],'date':numswitch(classres1['day']),'timespan':getspan(classres1['start_at'],classres1['duration'])})
            listtoshow.append(classres1)
        for classid1 in classidlist:
            wlist.append({'Class_id':classid1,'time':[]})
        for wlist1 in wlist:
            anwserlist=[]
            for classtaken in classtakentime:
                if (classtaken['Class_id']==wlist1['Class_id']):
                    anwserlist.append({'date':classtaken['date'],'timespan':classtaken['timespan']})
            wlist1['time']=anwserlist
        course_dict={}
        for course in courselist:
            course_dict[course['course_id']]=[]
        for course in courselist:
            course_dict[course['course_id']].append(course)
        coursename=[]
        i=0
        for course_id,courseinfo in course_dict.items():
            course=list(Course.objects.values('name').filter(id=course_id))
            course[0]['info_list']=courseinfo
            templist=[]
            for wlist1 in wlist:
                for courseinfo1 in courseinfo:
                    if wlist1['Class_id']==courseinfo1['id']:
                       templist.append(wlist1)
            course[0]['class_list']=templist  
            coursename.append(course[0])
        print(coursename)
        return render(request,"resource_share_teacher.html",{
            'web_title':'课程资源',
            'page_title':'课程资源',
            'wholelist':coursename
        })
    return render(request,"resource_share.html",{
        'web_title':'资源共享',
        'page_title':'资源共享',
        'class_resource':class_resource
    })
    
def rsdetail(request):
    
    classID=0
    if request.POST:
        # classID = request.POST.get('查看资源')
        for k,v in request.POST.items():
            if (v=="查看资源"):
                classID=k
        request.session['class']=classID
    else:
        classID=request.session['class']
    classid=classID
    queryset = Source.objects.filter(Class=classID).values_list('id', flat=True)    #获取课程id对应的课程文件夹
    if not queryset:
        file_path="media"+"\\"+"SEF"+"\\"+str(classID)
        os.mkdir(file_path)
        os.mkdir(file_path+"\\"+"assignment")
        os.mkdir(file_path+"\\"+"resource")
        res=Source.objects.create(file_path=file_path,file_name=classID, file_type="2",parent=1)
        classes = Class.objects.filter(id = classid).first()
        courselist=list(Class.objects.values('course_id').filter(id=classid))
        courseid=courselist[0]['course_id']
        course = Course.objects.filter(id=courseid).first()
        userid=request.user.id
        user = User.objects.filter(id=userid).first()
        res.course.add(course)
        res.Class.add(classes)
        res.user.add(user)
        res=list(Source.objects.values('id').filter(Class=classid).filter(file_name=classID).filter(parent=1))
        parentid=res[0]['id']
        ass=Source.objects.create(file_path=file_path+"\\"+"assignment",file_name="assignment",file_type="2",parent=parentid)
        ass.course.add(course)
        ass.Class.add(classes)
        ass.user.add(user)
        resource=Source.objects.create(file_path=file_path+"\\"+"resource",file_name="resource",file_type="2",parent=parentid)
        resource.course.add(course)
        resource.Class.add(classes)
        resource.user.add(user)
    queryset = Source.objects.filter(Class=classID).values_list('id', flat=True)    #获取课程id对应的课程文件夹
    root = queryset[0]  #获取课程文件夹的id
    root_resource = Source.objects.filter(parent=root, file_name="resource").values_list('id', flat=True)[0]   #得到课程资源文件夹的id
    request.session['root_resource'] = root_resource
    #root_assignment = Source.objects.filter(parent=root, file_name="assignment").values_list('id', flat=True)   #得到课程作业文件夹的id
    

    parent_object = None
    folder_id = request.GET.get('folder','')
    print(folder_id)
    if folder_id.isdecimal():
        parent_object = Source.objects.filter(id=int(folder_id), file_type=2).values_list('id', flat=True)[0]
        request.session['cur_folderID'] = folder_id
    else:
        request.session['cur_folderID'] = root_resource
    # 当前目录下所有的文件 & 文件夹获取到即可
    
    if parent_object:
        #print(parent_object)
        # 进入了某目录
        files = list(Source.objects.filter(parent=parent_object, file_type=1).order_by('-file_type').values())
        folder= list(Source.objects.filter(parent=parent_object, file_type=2).order_by('-file_type').values())
    else:
        # 资源根目录
        files = list(Source.objects.filter(parent=root_resource, file_type=1).order_by('-file_type').values())
        folder= list(Source.objects.filter(parent=root_resource, file_type=2).order_by('-file_type').values())
    # print(type(files))
    # print(files[0]['id'])
    for file in files:
        fileinfo = list(Source.objects.values('user').filter(id=file['id']))
        userid=fileinfo[0]['user']
        userinfo=list(User.objects.values('last_name','first_name').filter(id=userid))
        if userinfo:
            name=userinfo[0]['last_name']+userinfo[0]['first_name']
            file['uploader']=name
    for fold in folder:
        fileinfo = list(Source.objects.values('user').filter(id=fold['id']))
        userid=fileinfo[0]['user']
        userinfo=list(User.objects.values('last_name','first_name').filter(id=userid))
        if userinfo:
            name=userinfo[0]['last_name']+userinfo[0]['first_name']
            fold['uploader']=name
    print(files)
    print(folder)
    context = {
        'web_title':'资源共享',
        'page_title':'资源共享',
        "files": files,
        'folder': folder
    }
    return render(request, 'resource_share_detail.html', context)



    # files = os.listdir("media")
    # folder=[]
    # realfile=[]
    # for file in files:
    #     if os.path.isdir("media"+"\\"+file):
    #         folder.append(file)
    #     else:
    #         realfile.append(file)
    # print(files)
    # return render(request,"resource_share_detail.html",{
    #     'web_title':'资源共享',
    #     'page_title':'资源共享',
    #     'files':realfile,
    #     'folder':folder
    # })
@require_POST
def up(request):
    classid= request.session['class']
    file = request.FILES.get('myfile')
    # print(file)
    # print(file.size)
    folder_id = request.session['cur_folderID']
    folder_path = Source.objects.filter(id=folder_id).values_list('file_path', flat=True)[0]
    file_path = os.path.join(folder_path,file.name)
    destination = open(file_path,'wb+')
    for chunk in file.chunks():
        destination.write(chunk)
    destination.close()
    res = Source.objects.create(file_path=file_path, file_size=file.size, file_name=file.name, file_type='1', parent=folder_id,canbesearched=True)
    classes = Class.objects.filter(id = classid).first()
    courselist=list(Class.objects.values('course_id').filter(id=classid))
    courseid=courselist[0]['course_id']
    course = Course.objects.filter(id=courseid).first()
    userid=request.user.id
    user = User.objects.filter(id=userid).first()
    res.course.add(course)
    res.Class.add(classes)
    res.user.add(user)
    #print(res)
    if folder_id == request.session['cur_folderID']:
        return_page = "/resource_share/resource_share_detail/?folder=" + str(folder_id)
    else:
        return_page = "/resource_share/resource_share_detail/"
    print(return_page)
    return redirect(return_page)

@require_GET
def down(request,fileID):
    print(fileID)
    DBfile = Source.objects.filter(id=fileID)
    file_path = DBfile.values_list('file_path', flat=True)[0]
    filename = DBfile.values_list('file_name', flat=True)[0]
    print(file_path)
    with open(file_path,'rb') as f:
        file = File(f)
        response = HttpResponse(file.chunks(),content_type="APPLICATION/OCET-STREAM")
        response['Content-Disposition'] = 'attachment; filename=' + urlquote(filename)
        response['Content-Length']=os.path.getsize(file_path)
    return response

def new(request):
    if request.POST:
        New_folder_name = request.POST.get('newfolder')
    folder_id = request.session['cur_folderID']
    folder_path = Source.objects.filter(id=folder_id).values_list('file_path', flat=True)[0]
    New_folder_path = folder_path + '\\' + New_folder_name
    os.mkdir(New_folder_path)
    res = Source.objects.create(file_path=New_folder_path,file_name=New_folder_name, file_type='2', parent=folder_id)
    classid= request.session['class']
    classes = Class.objects.filter(id = classid).first()
    courselist=list(Class.objects.values('course_id').filter(id=classid))
    courseid=courselist[0]['course_id']
    course = Course.objects.filter(id=courseid).first()
    userid=request.user.id
    user = User.objects.filter(id=userid).first()
    res.course.add(course)
    res.Class.add(classes)
    res.user.add(user)
    #print(res)
    if folder_id == request.session['cur_folderID']:
        return_page = "/resource_share/resource_share_detail/?folder=" + str(folder_id)
    else:
        return_page = "/resource_share/resource_share_detail/"
    print(return_page)
    return redirect(return_page)

def return_previous_level(request):
    folderID = request.session['cur_folderID']
    print("sssss")
    print(folderID)
    parent = Source.objects.filter(id=folderID).values_list('parent', flat=True)[0]
    request.session['cur_folderID'] = parent
    if folderID == request.session['cur_folderID']:
        return_page = "/resource_share/resource_share_detail/?folder=" + str(folderID)
    else:
        return_page = "/resource_share/resource_share_detail/"
    print(return_page)
    return redirect(return_page)

def return_share_index(request):
    request.session['cur_folderID'] = None
    request.session['class'] = None
    return_page = "/resource_share/"
    return redirect(return_page)

@require_POST
def up_assignment(request):
    userid=request.user.id
    student_id=0
    stu_list=list(Student.objects.values().filter(user_id=userid))
    if stu_list:
        student_id=stu_list[0]['id']
    file = request.FILES.get('my_assignment')
    courseID = request.session['pastcourseinfo']
    classID = request.session['pastinfo']
    homework_id = request.session['pasthw']
    folder_id = Assignment.objects.filter(course=courseID ,Class=classID, id=homework_id).values_list('folder_id', flat=True)[0]
    print(folder_id)
    folder_path = Source.objects.filter(id=folder_id).values_list('file_path', flat=True)[0]
    file_path = os.path.join(folder_path,file.name)
    destination = open(file_path,'wb+')
    for chunk in file.chunks():
        destination.write(chunk)
    destination.close()

    res1 = Source.objects.create(file_path=file_path, file_size=file.size, file_name=file.name, parent=folder_id)    #先存文件，得到文件的ID
    res1.user.add(userid)
    res2 = AssignmentGrade.objects.create(is_submit=True) #存作业
    print(res1) 
    res2.student.add(student_id)
    res2.course.add(courseID)
    res2.Class.add(classID)
    res2.Assignment.add(homework_id)
    res2.file.add(res1.id)
    # print(list(res2))
    return_page = "/resource_share/homework_detail"
    print(return_page)
    return redirect(return_page)


def rewriteroot(request):
    os.chdir(request.session.get('rootpath'))
    return;

def rename(request):
    rewriteroot(request)
    dict_p = request.POST
    newname=""
    fileid=0
    for k,v in dict_p.items():
        if (k=='这种名字'):
            newname=v
        elif (v=='重命名'):
            fileid=k
    sourceinfo=list(Source.objects.values('file_path','file_name').filter(id=fileid))
    oldname=sourceinfo[0]['file_name']
    oldpath=sourceinfo[0]['file_path']
    newpath=oldpath.replace(oldname,newname)
    rootpath=os.getcwd()
    rootpath+="\\"
    rootpath+=oldpath
    rootpath=rootpath.replace(oldname,"")
    print(rootpath)
    os.chdir(rootpath)
    os.rename(oldname,newname)
    res=Source.objects.values().filter(id=fileid)
    res.update(file_name=newname,file_path=newpath)
    rewriteroot(request)
    return redirect(rsdetail)
def loopdelete(request,fileid,parent):
    childlist = list(Source.objects.values().filter(parent=parent))
    if childlist:
        for child in childlist:
            loopdelete(request,child['id'],child['id'])
    filelist=list(Source.objects.values().filter(id=fileid))
    filepath=filelist[0]['file_path']
    filename=filelist[0]['file_name']
    rewriteroot(request)
    rootpath=os.getcwd()
    rootpath+="\\"
    rootpath+=filepath
    des=rootpath
    rootpath=rootpath.replace(filename,"")
    os.chdir(rootpath)
    if os.path.isdir(des):
        os.rmdir(des)
    else:
        os.remove(des)
    filetodel = Source.objects.get(id=fileid)
    filetodel.Class.clear()
    filetodel.course.clear()
    filetodel.delete()
    rewriteroot(request)
    return;
def deletefile(request):
    dict_p = request.POST
    fileid=0
    for k,v in dict_p.items():
        if (v=="删除"):
            fileid=k
    filetodel = Source.objects.get(id=fileid)
    childlist = list(Source.objects.values().filter(parent=fileid))
    loopdelete(request,fileid,fileid)
    return redirect(rsdetail)
def search(request):
    if request.POST:
        q=""
        dict_p=request.POST
        # print(dict_p)
        # return HttpResponse("")
        for k,v in dict_p.items():
            if (k=="搜"):
                q=v
        request.session['lastq']=q
    else:
        q=request.session.get('lastq')
    classID=request.session['class']
    # print(classID)
    # print(q)
    searchresult=list(Source.objects.values().filter(Class=classID).filter(canbesearched=1).filter(file_type=1).filter(file_name__icontains=q))
    print(searchresult)
    for file in searchresult:
        fileinfo = list(Source.objects.values('user').filter(id=file['id']))
        userid=fileinfo[0]['user']
        userinfo=list(User.objects.values('last_name','first_name').filter(id=userid))
        if userinfo:
            name=userinfo[0]['last_name']+userinfo[0]['first_name']
            file['uploader']=name
    return render(request,"resource_share_search.html",
    {
        'web_title':'资源查询',
        'page_title':'资源查询',
        "files": searchresult
    })


def homework(request):
    userid=request.user.id
    stu_list=list(Student.objects.values().filter(user_id=userid))
    if stu_list:
        studentid=stu_list[0]['id']
        # print(studentid)
        classlist=list(StuHasClass.objects.values('Class_id').filter(Student_id=studentid))
        print(classlist)
        listtoshow=[]
        classtakentime=[]
        classidlist=[]
        wlist=[]
        for class1 in classlist:
            classid=class1['Class_id']
            classidlist.append(classid)
            courselist=list(Class.objects.values('course_id').filter(id=classid))
            courseid=courselist[0]['course_id']
            courseinfo=list(Course.objects.values('name').filter(id=courseid))
            classres=list(ClassHasRoom.objects.values('id','day','start_at','duration','Class_id').filter(Class_id=classid))
            # print(classres)
            for classres1 in classres:
                classres1['date']=numswitch(classres1['day'])
                classres1['timespan']=getspan(classres1['start_at'],classres1['duration'])
                classtakentime.append({'Class_id':classres1['Class_id'],'date':numswitch(classres1['day']),'timespan':getspan(classres1['start_at'],classres1['duration'])})
            listtoshow.append(classres1)
            # print(listtoshow)
        print(classtakentime)
        for classid1 in classidlist:
            wlist.append({'Class_id':classid1,'time':[]})
        # print(wlist)
        # print(classtakentime)
        for wlist1 in wlist:
            classid=wlist1['Class_id']
            courselist=list(Class.objects.values('course_id').filter(id=classid))
            courseid=courselist[0]['course_id']
            courseinfo=list(Course.objects.values('name').filter(id=courseid))
            coursename=courseinfo[0]['name']
            wlist1['course_id']=courseid
            wlist1['coursename']=coursename
            anwserlist=[]
            for classtaken in classtakentime:
                if (classtaken['Class_id']==wlist1['Class_id']):
                    anwserlist.append({'date':classtaken['date'],'timespan':classtaken['timespan']})
            wlist1['time']=anwserlist
        print(wlist)
        return render(request,"homework.html",{
            'web_title':'课程作业',
            'page_title':'课程作业',
            'wlist':wlist
        })
    else:
        courselist=list(Class.objects.values().filter(teacher_id=userid).order_by('course_id'))
        listtoshow=[]
        classtakentime=[]
        wlist=[]
        classidlist=[]
        for course in courselist:
            classid=course['id']            
            classidlist.append(classid)
            classres=list(ClassHasRoom.objects.values('id','day','start_at','duration','Class_id').filter(Class_id=classid))            
            for classres1 in classres:
                classres1['date']=numswitch(classres1['day'])
                classres1['timespan']=getspan(classres1['start_at'],classres1['duration'])
                classtakentime.append({'Class_id':classres1['Class_id'],'date':numswitch(classres1['day']),'timespan':getspan(classres1['start_at'],classres1['duration'])})
            listtoshow.append(classres1)
        for classid1 in classidlist:
            wlist.append({'Class_id':classid1,'time':[]})
        for wlist1 in wlist:
            anwserlist=[]
            for classtaken in classtakentime:
                if (classtaken['Class_id']==wlist1['Class_id']):
                    anwserlist.append({'date':classtaken['date'],'timespan':classtaken['timespan']})
            wlist1['time']=anwserlist
        course_dict={}
        for course in courselist:
            course_dict[course['course_id']]=[]
        for course in courselist:
            course_dict[course['course_id']].append(course)
        coursename=[]
        i=0
        for course_id,courseinfo in course_dict.items():
            course=list(Course.objects.values('name').filter(id=course_id))
            course[0]['info_list']=courseinfo
            templist=[]
            for wlist1 in wlist:
                for courseinfo1 in courseinfo:
                    if wlist1['Class_id']==courseinfo1['id']:
                       templist.append(wlist1)
            course[0]['class_list']=templist  
            coursename.append(course[0])
        print(coursename)
        return render(request,"homework_teacher.html",{
            'web_title':'课程作业',
            'page_title':'课程作业',
            'wholelist':coursename
        })

def hwdetail(request):
    userid=request.user.id
    studentid=0
    stu_list=list(Student.objects.values().filter(user_id=userid))
    if stu_list:
        studentid=stu_list[0]['id']
    if request.POST:
        dict_p = request.POST
        homeworkid=0
        print(dict_p)
        for k,v in dict_p.items():
            if (v=='查看详情'):
                homeworkid=k
        request.session['pasthw']=homeworkid
    else:
        homeworkid = request.session.get('pasthw')
    
    assinfo=list(Assignment.objects.values('id','assignment_name','assignment_start','assignment_end','assignment_intro','course','assignment_ratio','Class').filter(id=homeworkid))
    print(assinfo)
    for ass in assinfo:
        ass['assignment_start']=timezone.localtime(ass['assignment_start'])
        ass['assignment_end']=timezone.localtime(ass['assignment_end'])
    classid=assinfo[0]['Class']
    courselist=list(Class.objects.values('course_id').filter(id=classid))
    courseid=courselist[0]['course_id']
    courseinfo=list(Course.objects.values('name').filter(id=courseid))
    coursename=courseinfo[0]['name']
    assinfo[0]['coursename']=coursename
    msg=""
    pigaiflag=0
    msg1=""
    tijiaoflag=0
    gradeinfo=list(AssignmentGrade.objects.values('assignment_result').filter(Class=classid).filter(student=studentid))
    if gradeinfo:
        if gradeinfo[0]['assignment_result']:
            grade=gradeinfo[0]['assignment_result']
            pigaiflag=1
            msg1="已提交"
        else:
            msg="未批改"
            pigaiflag=0
            msg1="已提交"
    else:
        msg1="未提交"
        msg="未批改"
        tijiaoflag=1
    if (pigaiflag==1 and tijiaoflag==0):
        return render(request,"homework_detail.html",{
            'web_title':'作业详情',
            'page_title':'作业详情',
            'assinfo':assinfo,
            'grade':grade,
            "msg1":msg1
        })
    elif(pigaiflag==0 and tijiaoflag==0):
        return render(request,"homework_detail.html",{
            'web_title':'作业详情',
            'page_title':'作业详情',
            'assinfo':assinfo,
            "msg1":msg1,
            'msg':msg
        })
    elif (pigaiflag==0 and tijiaoflag==1):
        return render(request,"homework_detail.html",{
            'web_title':'作业详情',
            'page_title':'作业详情',
            'assinfo':assinfo,
            "msg1":msg1,
            "msg":msg
        })


def hwlist(request):
    userid=request.user.id
    studentid=0
    stu_list=list(Student.objects.values().filter(user_id=userid))
    if stu_list:
        studentid=stu_list[0]['id']
    if request.POST:
        dict_P = request.POST
        classid=0
        for k,v in dict_P.items():
            if (v=='查看作业'):
                classid=k
        request.session['pastinfo']=classid
        courselist=list(Class.objects.values('course_id').filter(id=classid))
        course_id=courselist[0]['course_id']
        request.session['pastcourseinfo']=course_id
    else:
        classid = request.session.get('pastinfo')
    #print(classid)
    asslist=list(Assignment.objects.values().filter(Class=classid))
    #print(asslist)
    infolist=[]
    submit = dict(AssignmentGrade.objects.filter(Class=classid).values_list('Assignment', 'is_submit'))
    print("sssss")
    # print(ifsubmit)
    courselist=list(Class.objects.values('course_id').filter(id=classid))
    course_id=courselist[0]['course_id']
    courselist=list(Course.objects.values('name').filter(id=course_id))
    coursename= courselist[0]['name']
   
    count = 0
    for ass in asslist:
        if submit:
            if submit[ass['id']]:
                ifsubmit = "已提交"
            else:
                ifsubmit = "未提交"
        else:
            ifsubmit = "未提交"
        infolist.append({'id':ass['id'],
                        'name':ass['assignment_name'],
                        'start':timezone.localtime(ass['assignment_start']),
                        'end':timezone.localtime(ass['assignment_end']),
                        'ifsubmit':ifsubmit
                        })
    print(infolist)
    return render(request,"homework_list.html",{
        'web_title':'课程作业列表',
        'page_title':'课程作业列表',
        'infolist':infolist,
        'coursename':coursename
    })

def hwlist_t(request):
    if request.POST:
        dict_P = request.POST
        classid=0
        for k,v in dict_P.items():
            if (v=='布置作业'):
                classid=k
        request.session['pastinfo']=classid
        courselist=list(Class.objects.values('course_id').filter(id=classid))
        course_id=courselist[0]['course_id']
        request.session['pastcourseinfo']=course_id
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
    assignmentlist=list(Assignment.objects.values('id','assignment_name','assignment_start','assignment_end').filter(Class=classid))
    # print(assignmentlist)
    wlist=[]
    for ass in assignmentlist:
        wlist.append(
            {'name':ass['assignment_name'],
            'start':timezone.localtime(ass['assignment_start']),
            'end':timezone.localtime(ass['assignment_end']),
            'id':ass['id'],
            })
    print(wlist)
    return render(request,"homework_list_t.html",{
        'web_title':'课程作业',
        'page_title':'课程作业',
        'classinfo':classinfo,
        'courseinfo':courseinfo,
        'classtime':classtime,
        'asslist':wlist
    })

def hwass(request):
    return render(request,"homework_assign.html",{
        'web_title':'布置课程作业',
        'page_title':'布置课程作业'
    })
def addassignment(request):
    classid = request.session.get('pastinfo')
    courselist=list(Class.objects.values('course_id').filter(id=classid))
    courseid=courselist[0]['course_id']
    dict_p = request.POST
    print(dict_p)
    homeworkname=""
    starttime=""
    endtime=""
    homeworkratio=""
    homeworkintro=""
    for k,v in dict_p.items():
        if (k=='作业名'):
            homeworkname=v
        elif (k=='开始时间'):
            starttime=v
        elif (k=='截止时间'):
            endtime=v
        elif (k=='作业占比'):
            homeworkratio=v
        elif (k=='作业详情'):
            homeworkintro=v
    homeworking=Assignment.objects.create(assignment_start=starttime,assignment_end=endtime,assignment_intro=homeworkintro,assignment_ratio=homeworkratio,assignment_name=homeworkname)
    courses = Course.objects.filter(id=courseid).first()
    classes = Class.objects.filter(id=classid).first()
    folder = Source.objects.filter(Class=classid).filter(file_name="assignment").first()
    homeworking.folder_id.add(folder)
    homeworking.course.add(courses)
    homeworking.Class.add(classes)
    homeworking = Assignment.objects.values().filter(Class=classid)
    # return HttpResponse(dict_p)
    return redirect("hwlist_t")

def hwdetail_t(request):
    if request.POST:
        dict_p = request.POST
        homeworkid=0
        print(dict_p)
        for k,v in dict_p.items():
            if (v=='查看详情'):
                homeworkid=k
        request.session['pasthw']=homeworkid
    else:
        homeworkid = request.session.get('pasthw')
    # print(homeworkid)
    info=list(Assignment.objects.values('id','assignment_name','assignment_start','assignment_end','assignment_intro','course','assignment_ratio').filter(id=homeworkid))
    # print(info)
    info[0]['start']=timezone.localtime(info[0]['assignment_start'])
    info[0]['end']=timezone.localtime(info[0]['assignment_end'])
    courselist=list(Course.objects.values('name').filter(id=info[0]['course']))
    info[0]['coursename']=courselist[0]['name']
    print(info)
    return render(request,"homework_detail_t.html",{
        'web_title':'作业详情',
        'page_title':'作业详情',
        'info':info
    })
def homework_detail_update(request):
    dict_p = request.POST
    homeworkid=0
    homeworkname=""
    start=""
    end=""
    homeworkratio=0
    homeworkintro=""
    is_start=0
    is_end=0
    flag=0
    for k,v in dict_p.items():
        if (flag==0 and v=='保存修改'):
            homeworkid = k
            flag=1
        elif (k=='作业名称'):
            homeworkname=v
        elif (k=='开始时间'):
            if (v != ""):
                is_start=1
                start=v
        elif (k=='截止时间'):
            if (v != ""):
                is_end=1
                end=v
        elif (k=='作业占比'):
            homeworkratio=v
        elif (k=='作业详情'):
            homeworkintro=v
    res = Assignment.objects.values().filter(id=homeworkid)
    if res:
        res.update(assignment_intro=homeworkintro,assignment_ratio=homeworkratio,assignment_name=homeworkname)
        if is_start:
            res.update(assignment_start=start)
        if is_end:
            res.update(assignment_end=end)
    res = list(Assignment.objects.values().filter(id=homeworkid))
    print(res)
    return redirect("hwlist_t")

def homeworkdelete(request):
    dict_p = request.POST
    homeworkid = 0
    print(dict_p)
    for k,v in dict_p.items():
        if (v=='删除'):
            homeworkid=k
    homeworktodel = Assignment.objects.get(id=homeworkid)
    homeworktodel.Class.clear()
    homeworktodel.course.clear()
    homeworktodel.delete()
    return redirect("hwlist_t")

def homework_correct(request):
    assid=0
    if request.POST:
        dict_p = request.POST
        for k,v in dict_p.items():
            if (v=='批改'):
                assid=k
                request.session['thisassid']=assid
    else:
        assid = request.session.get('thisassid')
    assid = request.session.get('thisassid')
    # print(request.session.get('class'))
    # print(request.session.get('thisassid'))
    # print(assid)
    foldlist=list(Assignment.objects.values('folder_id','Class').filter(id=assid))
    # print(foldlist)
    folderid = foldlist[0]['folder_id']
    classid = foldlist[0]['Class']
    # print(folderid)
    # print(assid)
    # print(classid)
    sourcelist = list(Source.objects.values().filter(parent=folderid))
    for file in sourcelist:
        fileinfo = list(Source.objects.values('user').filter(id=file['id']))
        userid=fileinfo[0]['user']
        userinfo=list(User.objects.values('last_name','first_name').filter(id=userid))
        if userinfo:
            name=userinfo[0]['last_name']+userinfo[0]['first_name']
            file['uploader']=name
            file['userid']=userid
            studentid=0
            stu_list=list(Student.objects.values().filter(user_id=userid))
            if stu_list:
                studentid=stu_list[0]['id']
            assgrade=list(AssignmentGrade.objects.values('assignment_result').filter(Assignment=assid).filter(student=studentid))
            if assgrade:
                file['assgrade']=assgrade[0]['assignment_result']
            else:
                file['assgrade']=0
    print(sourcelist)
    return render(request, "homework_correct.html",
    {
        'web_title':'作业批改',
        'page_title':'作业批改',
        "files": sourcelist
    })

def ing(request):
    # return HttpResponse("1")
    print("aaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    userid=0
    grade=0
    if request.POST:
        dict_p = request.POST
        for k,v in dict_p.items():
            if (v=="提交成绩"):
                userid=k
            elif (k=="grade"):
                grade=v
    # return HttpResponse(grade)
    print(userid)
    assid = request.session.get('thisassid')
    print(assid)
    studentid=0
    stu_list=list(Student.objects.values().filter(user_id=userid))
    if stu_list:
        studentid=stu_list[0]['id']
    print(studentid)
    queryset= AssignmentGrade.objects.filter(Assignment=assid).filter(student=studentid)
    queryset.update(assignment_result=grade)
    return redirect(homework_correct)