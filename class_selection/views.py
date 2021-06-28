import pymysql
from django.contrib.postgres import serializers
from django.core.serializers import serialize
from django.db import OperationalError
from django.http.request import HttpRequest
from django.http.response import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from class_selection import forms
from class_selection import models
from class_selection.forms import Department, Major
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from info_mgt.models import Campus, Department, Major, Teacher, Course, MajorHasCourse, Class


# TODO: those following pages' templates are not implemented yet.

def index(request):
    return_dict = {'web_title': '在线选课',
                   'page_title': '在线选课',
                   'request_user': request.user, }
    time_zero = models.sel_time.objects.get(type=0)
    time_one = models.sel_time.objects.get(type=1)
    return_dict['time_zero'] = time_zero
    return_dict['time_one'] = time_one
    return render(request, 'index.html', return_dict)


def admin_class(req):  # 管理员选退课
    current_user_group = req.user.groups.first()
    if not current_user_group or current_user_group.name != 'admin':
        identity = 0  # This user can not use this function
        return render(req, 'admin_class.html', {
            'web_title': '课程选择',
            'page_title': '课程选择',
            'request_user': req.user,
            'identity': identity
        })
    this_user = req.user
    if req.method == 'GET':
        return render(req, 'admin_class.html', {
            'web_title': '手动选课',
            'page_title': '手动选课',
            'request_user': req.user,
        })
    if req.method == 'POST':
        try:
            students = models.Student.objects.get(pk=req.POST.get('Student_id'))
        except Exception:
            non_stu = True
            return render(req, 'admin_class.html', {
                'web_title': '手动选课',
                'page_title': '手动选课',
                'request_user': req.user,
                'non_stu': non_stu,
            })
        else:
            try:
                classes = models.Class.objects.get(pk=req.POST.get('Class_id'))
            except Exception:
                non_class = True
                return render(req, 'admin_class.html', {
                    'web_title': '手动选课',
                    'page_title': '手动选课',
                    'request_user': req.user,
                    'non_class': non_class,
                })
            else:
                capacity = classes.course.capacity - classes.memberCnt
        if req.POST.get("option") == 'In':
            try:
                duplicate_check = models.StuHasClass.objects.get(Student=students, Class=classes)
            except models.StuHasClass.DoesNotExist:
                pass
            else:
                if duplicate_check:
                    duplicated = True
                    return render(req, 'admin_class.html', {
                        'web_title': '手动选课',
                        'page_title': '手动选课',
                        'request_user': req.user,
                        'request_class': classes,
                        'pre_capacity': capacity,
                        'duplicate': duplicated,
                    })

            if capacity <= 0:
                space_out = True
                return render(req, 'admin_class.html', {
                    'web_title': '手动选课',
                    'page_title': '手动选课',
                    'request_user': req.user,
                    'request_class': classes,
                    'pre_capacity': capacity,
                    'space_out': space_out,
                })
            else:
                class_non = False
                classroom = models.ClassHasRoom.objects.filter(Class=classes)
                if len(classroom) == 0:
                    class_non = True
                    return render(req, 'admin_class.html', {
                        'web_title': '手动选课',
                        'page_title': '手动选课',
                        'request_user': req.user,
                        'class_non': class_non,
                    })
                else:
                    for i in classroom:
                        if i.day is None or i.start_at is None or i.end_at is None:
                            class_non = True

                            return render(req, 'admin_class.html', {
                                'web_title': '手动选课',
                                'page_title': '手动选课',
                                'request_user': req.user,
                                'class_non': class_non,
                            })

                myclass_list = models.StuHasClass.objects.filter(Student=students)  # 加的判断冲突选课的
                myclass = [["" for i in range(7)] for i in range(13)]
                for i in range(0, len(myclass_list)):
                    myclasstime = models.ClassHasRoom.objects.filter(Class=myclass_list[i].Class)
                    for k in range(0, len(myclasstime)):
                        myclassday = myclasstime[k].day - 1
                        myclassstart = myclasstime[k].start_at - 1
                        myclassdur = myclasstime[k].duration
                        myclassname = myclasstime[k].Class.course.name
                        for j in range(0, 12):
                            if j in range(myclassstart, myclassstart + myclassdur):
                                myclass[j][myclassday] = myclassname
                myclasstime = models.ClassHasRoom.objects.filter(Class=classes)
                for k in range(0, len(myclasstime)):
                    myclassday = myclasstime[k].day - 1
                    myclassstart = myclasstime[k].start_at - 1
                    myclassdur = myclasstime[k].duration
                    myclassname = myclasstime[k].Class.course.name
                    for j in range(0, 12):
                        if j in range(myclassstart, myclassstart + myclassdur):
                            if myclass[j][myclassday] != "":
                                conflict_err = True
                                return render(req, 'admin_class.html', {
                                    'web_title': '手动选课',
                                    'page_title': '手动选课',
                                    'request_user': req.user,
                                    'request_class': classes,
                                    'pre_capacity': capacity,
                                    'conflict_err': conflict_err,  # 需要前端输出弹窗
                                })  # 添加的内容到此结束
                models.StuHasClass.objects.create(Student=students, Class=classes)
                classes.memberCnt += 1
                classes.save()
                capacity -= 1
                in_success = True
                return render(req, 'admin_class.html', {
                    'web_title': '手动选课',
                    'page_title': '手动选课',
                    'request_user': req.user,
                    'request_class': classes,
                    'pre_capacity': capacity,
                    'in_success': in_success,
                })
        elif req.POST.get("option") == 'Out':
            try:
                delete_check = models.StuHasClass.objects.get(Student=students, Class=classes)
            except Exception:
                delete_unable = True
                return render(req, 'admin_class.html', {
                    'web_title': '手动选课',
                    'page_title': '手动选课',
                    'request_user': req.user,
                    'request_class': classes,
                    'pre_capacity': capacity,
                    'delete_check': delete_unable,
                })
            else:
                if delete_check == 0:
                    delete_unable = True
                    return render(req, 'admin_class.html', {
                        'web_title': '手动选课',
                        'page_title': '手动选课',
                        'request_user': req.user,
                        'request_class': classes,
                        'pre_capacity': capacity,
                        'delete_check': delete_unable,
                    })
            classes.memberCnt -= 1
            classes.save()
            capacity += 1
            models.StuHasClass.objects.get(Student=students, Class=classes).delete()
            out_success = True
            return render(req, 'admin_class.html', {
                'web_title': '手动选课',
                'page_title': '手动选课',
                'request_user': req.user,
                'request_class': classes,
                'pre_capacity': capacity,
                'out_success': out_success,
            })


def time_control(req):
    current_user_group = req.user.groups.first()
    if not current_user_group or current_user_group.name != 'admin':
        identity = 0  # This user can not use this function
        return render(req, 'time_control.html', {
            'web_title': '课程选择',
            'page_title': '课程选择',
            'request_user': req.user,
            'identity': identity
        })
    if req.method == "POST":
        return_dict = {
            'web_title': '管理时间',
            'page_title': '管理时间',
            'request_user': req.user,
        }
        stage = req.POST.get("stage")  # cxjd/bxjd
        start_time = req.POST.get("stage_time1")  # datetime格式
        end_time = req.POST.get("stage_time2")

        if end_time < start_time:
            time_err = True
            return render(req, 'time_control.html', {
                'web_title': '管理时间',
                'page_title': '管理时间',
                'request_user': req.user,
                'time_err': time_err,
            })

        if stage == "cxjd":  # 初选设置
            stage_num = 0
            update_result = models.sel_time.objects.get(type=stage_num)
            update_result.start = start_time
            update_result.end = end_time
            update_result.save()
            stage1_suc = True
            return render(req, 'time_control.html', {
                'web_title': '管理时间',
                'page_title': '管理时间',
                'request_user': req.user,
                'stage1_suc': stage1_suc,
            })

        elif stage == "bxjd":  # 补选设置
            stage_num = 1
            stage1_time = models.sel_time.objects.get(type=0)
            stage1_end = stage1_time.end
            if str(stage1_end) > start_time:
                stage_err = True
                return render(req, 'time_control.html', {
                    'web_title': '管理时间',
                    'page_title': '管理时间',
                    'request_user': req.user,
                    'stage_err': stage_err,
                })
            else:
                update_result = models.sel_time.objects.get(type=stage_num)
                update_result.start = start_time
                update_result.end = end_time
                update_result.save()
                stage2_suc = True
                return render(req, 'time_control.html', {
                    'web_title': '管理时间',
                    'page_title': '管理时间',
                    'request_user': req.user,
                    'stage2_suc': stage2_suc,
                })
        else:
            return_dict["error"] = True

        return render(req, "time_control.html", return_dict)
    elif req.method == 'GET':
        return render(req, 'time_control.html', {
            'web_title': '管理时间',
            'page_title': '管理时间',
            'request_user': req.user,
        })


def stu_class(req):  # 学生课表
    current_user_group = req.user.groups.first()
    if not current_user_group or current_user_group.name != 'student':
        return render(req, 'stu_class.html', {
            'web_title': '课程选择',
            'page_title': '课程选择',
            'request_user': req.user,
            'identity': 0
        })
    this_user = req.user
    students = models.Student.objects.filter(user=this_user)
    myclass_list = models.StuHasClass.objects.filter(Student=students[0])
    myclass = [["" for i in range(7)] for i in range(13)]
    for i in range(0, len(myclass_list)):
        myclasstime = models.ClassHasRoom.objects.filter(Class=myclass_list[i].Class)
        for k in range(0, len(myclasstime)):
            myclassday = myclasstime[k].day - 1
            myclassstart = myclasstime[k].start_at - 1
            myclassdur = myclasstime[k].duration
            myclassname = myclasstime[k].Class.course.name
            for j in range(0, 12):
                if j in range(myclassstart, myclassstart + myclassdur):
                    myclass[j][myclassday] = myclassname
    return render(req, 'stu_class.html', {
        'web_title': '学生课表',
        'page_title': '学生课表',
        'request_user': req.user,
        'schedule': myclass
    })


def tea_class(request):
    current_user_group = request.user.groups.first()
    if not current_user_group or current_user_group.name != 'teacher':
        identity = 0  # This user can not use this function
        return render(request, 'tea_class.html', {
            'web_title': '课程选择',
            'page_title': '课程选择',
            'request_user': request.user,
            'identity': identity
        })
    if request.method == 'GET':
        return_dict = {'web_title': '教师课表',
                       'page_title': '教师课表',
                       'request_user': request.user,
                       'cur_submodule': 'tea_class', }
        try:
            class_list = models.Class.objects.filter(teacher=request.user.id)
        except OperationalError:
            return_dict['info_retrieve_failure'] = True
        else:
            return_dict['class_list'] = class_list

        return render(request, 'tea_class.html', return_dict)


def stu_detail(req, class_id):
    return_dict = {'web_title': '学生详情',
                   'page_title': '学生详情',
                   }
    students_list = models.StuHasClass.objects.filter(Class=class_id)
    return_dict['students_list'] = students_list
    return render(req, 'stu_detail.html', return_dict)


def major_scheme(request):
    current_user_group = request.user.groups.first()
    if not current_user_group:
        identity = 2
        return render(request, 'major_scheme.html', {
            'web_title': '课程选择',
            'page_title': '课程选择',
            'request_user': request.user,
            'identity': identity
        })
    return_dict = {
        'web_title': '培养方案',
        'page_title': '培养方案',
        'request_user': request.user,
        'cur_submodule': 'major_scheme',
    }

    # 显示页面
    if request.method == 'GET':
        current_user_group = request.user.groups.first()
        if current_user_group.name == 'student':
            try:
                course_list = MajorHasCourse.objects.filter(major=request.user.student.major)
            except OperationalError:
                return_dict['info_retrieve_failure'] = True
            else:
                return_dict['course_list'] = course_list
        try:
            department_list = Department.objects.all()
        except OperationalError:
            return_dict['info_retrieve_failure'] = True
        else:
            return_dict['department_list'] = department_list
        try:
            major_list = Major.objects.all()
        except OperationalError:
            return_dict['info_retrieve_failure'] = True
        else:
            return_dict['major_list'] = major_list

            # print(course_list)
        return render(request, 'major_scheme.html', return_dict)

    elif request.method == 'POST':

        if request.POST.get('dept'):  # 点击第一个下拉框，第二个下拉框会筛选major信息
            department_list = Department.objects.all()
            return_dict['department_list'] = department_list
            major_list = Major.objects.filter(department=request.POST.get('dept'))
            return_dict['major_list'] = major_list
            return_dict['selected_dept'] = int(request.POST.get('dept'))
            return render(request, 'major_scheme.html', return_dict)

        else:  # 点击查看培养方案，重置两个下拉框内容并返回培养方案内课程表及课程信息
            try:
                department_list = Department.objects.all()
            except OperationalError:
                return_dict['info_retrieve_failure'] = True
            else:
                return_dict['department_list'] = department_list
            try:
                major_list = Major.objects.all()
            except OperationalError:
                return_dict['info_retrieve_failure'] = True
            else:
                return_dict['major_list'] = major_list
            mymajor = request.POST.get("major")
            if mymajor != None:
                try:
                    major_ret = MajorHasCourse.objects.filter(major=int(mymajor))
                except OperationalError:
                    return_dict['info_retrieve_failure'] = True

                    # print(course_info)
                return_dict["course_list"] = major_ret
                return_dict["major_name"] = Major.objects.filter(id=int(mymajor))[0].name
                return render(request, 'major_scheme.html', return_dict)
            else:
                return HttpResponseRedirect('/class_selection/major_scheme')


def requset(args):
    pass


def stu_class_list(request):
    return_dict = {
        'page_title': '课程列表',
        'web_title': '在线选课',
        'request_user': request.user,
    }
    has_class_list = models.StuHasClass.objects.filter(Student_id=request.user.student.id)
    class_list = [0 for i in range(len(has_class_list))]
    for i in range(0, len(has_class_list)):
        class_list[i] = models.Class.objects.get(pk=has_class_list[i].Class_id)
    return_dict['has_class_list'] = has_class_list
    return_dict['class_list'] = class_list
    return render(request, 'stu_class_list.html', return_dict)


def stu_select(req, null=None):
    identity = 1
    current_user_group = req.user.groups.first()
    if not current_user_group or current_user_group.name != 'student':
        identity = -1  # This user can not use this function
        return render(req, 'stu_select.html', {
            'web_title': '课程选择',
            'page_title': '课程选择',
            'request_user': req.user,
            'identity': identity
        })
    time_zero = models.sel_time.objects.get(type=0)
    timenow = timezone.now()
    if (str(timenow)[0:19] < str(time_zero.start)[0:19] or str(timenow)[0:19] > str(time_zero.end)[0:19]):
        return render(req, 'stu_select.html', {
            'web_title': '课程选择',
            'page_title': '课程选择',
            'request_user': req.user,
            'identity': 2
        })
    class_info = {}
    if req.method == "POST" and req.POST.get("my_option") == "selectclass":
        # print()
        return_dict = {
            'web_title': '课程选择',
            'page_title': '课程选择',
            'request_user': req.user,
            'identity': identity
        }
        content = req.POST.get("cx_input_1")
        choice = req.POST.get("cxkc_1")
        # print(choice1)
        # print(content1)
        req.session['choice'] = choice
        req.session['content'] = content
        print(choice)
        print(content)
        if choice == "skjs":
            teacher_name = content.split(' ', 1)
            if len(teacher_name) < 2:
                tab_missing = True
                return_dict = {
                    'web_title': '课程选择',
                    'page_title': '课程选择',
                    'request_user': req.user,
                    'identity': identity,
                    'tab_missing': tab_missing,
                }
                return render(req, 'stu_select.html', return_dict)
            user = models.User.objects.filter(first_name=teacher_name[1], last_name=teacher_name[0])
            if len(user) > 0:
                class_info = models.Class.objects.filter(teacher=user[0])
                for j in range(1, len(user)):
                    tmp = models.Class.objects.filter(teacher=user[j])
                    class_info = class_info | tmp
            else:
                tea_non = True
                return_dict = {
                    'web_title': '课程选择',
                    'page_title': '课程选择',
                    'request_user': req.user,
                    'identity': identity,
                    'tea_non': tea_non,
                }
                return render(req, 'stu_select.html', return_dict)
        elif choice == "kcmc":
            class_name = models.Course.objects.filter(name__contains=content)
            if len(class_name) > 0:
                class_info = models.Class.objects.filter(course=class_name[0].id)
                for i in range(1, len(class_name)):
                    class_id = models.Class.objects.filter(course=class_name[i].id)
                    class_info = class_info | class_id
            else:
                class_info = {}
        elif choice == "kcbh":
            class_info = models.Class.objects.filter(course=int(content))
        return_dict["class_info"] = class_info
        students = models.Student.objects.get(user_id=req.user.id)
        my_hasclass = models.StuHasClass.objects.filter(Student=students)
        print(my_hasclass)

        if len(my_hasclass) > 0:
            my_class_set = models.Class.objects.filter(pk=my_hasclass[0].Class.id)
            for j in range(1, len(my_hasclass)):
                tmp = models.Class.objects.filter(pk=my_hasclass[j].Class.id)
                my_class_set = my_class_set | tmp
        else:
            my_class_set = {}
        return_dict["my_class"] = my_class_set
        print(my_class_set)
        '''
        is_selected = {}
        class_idlist = {}
        exist_class = {}
        for i in range(0, len(class_info)):
            exist = models.StuHasClass.objects.filter(Class=class_info[i], Student=req.user.student)
            is_selected[i] = len(exist)
            class_idlist[i] = class_info[i].id
        exist_class['is_selected'] = is_selected
        exist_class['class_idlist'] = class_idlist
        return_dict["exist_class"] = exist_class
        '''
    elif req.method == "POST" and req.POST.get("my_option") == "chooseclass":
        return_dict = {
            'web_title': '课程选择',
            'page_title': '课程选择',
            'request_user': req.user,
        }
        dict_p = req.POST
        print(dict_p)
        choose_option = 1
        for k, v in dict_p.items():
            if v == "select":
                class_id = k
                choose_option = 1
            if v == "drop":
                class_id = k
                choose_option = 0

        stu_id = req.user.student.id
        students = models.Student.objects.get(pk=stu_id)
        classes = models.Class.objects.get(pk=class_id)

        if choose_option == 0:
            classes.memberCnt -= 1
            classes.save()
            models.StuHasClass.objects.get(Student=students, Class=classes).delete()
        else:
            class_non = False
            classroom=models.ClassHasRoom.objects.filter(Class=classes)
            if len(classroom)==0:
                class_non = True
                return_dict = {
                    'web_title': '课程选择',
                    'page_title': '课程选择',
                    'request_user': req.user,
                    'identity': identity,
                    'class_non': class_non,
                }
            else:
                for i in classroom:
                    if i.day is null or i.start_at is null or i.end_at is null:
                        class_non = True
                        return_dict = {
                            'web_title': '课程选择',
                            'page_title': '课程选择',
                            'request_user': req.user,
                            'identity': identity,
                            'class_non': class_non,
                        }
            if not class_non:
                conflict_err = False
                space_out = False
                myclass_list = models.StuHasClass.objects.filter(Student=students)  # 加的判断冲突选课的
                myclass = [["" for i in range(7)] for i in range(13)]
                for i in range(0, len(myclass_list)):
                    myclasstime = models.ClassHasRoom.objects.filter(Class=myclass_list[i].Class)
                    for k in range(0, len(myclasstime)):
                        myclassday = myclasstime[k].day - 1
                        myclassstart = myclasstime[k].start_at - 1
                        myclassdur = myclasstime[k].duration
                        myclassname = myclasstime[k].Class.course.name
                        for j in range(0, 12):
                            if j in range(myclassstart, myclassstart + myclassdur):
                                myclass[j][myclassday] = myclassname
                myclasstime = models.ClassHasRoom.objects.filter(Class=classes)
                for k in range(0, len(myclasstime)):
                    myclassday = myclasstime[k].day - 1
                    myclassstart = myclasstime[k].start_at - 1
                    myclassdur = myclasstime[k].duration
                    myclassname = myclasstime[k].Class.course.name
                    for j in range(0, 12):
                        if j in range(myclassstart, myclassstart + myclassdur):
                            if myclass[j][myclassday] != "":
                                conflict_err = True
                                break
                if conflict_err == True:
                    return_dict = {
                        'web_title': '课程选择',
                        'page_title': '课程选择',
                        'request_user': req.user,
                        'conflict_err': conflict_err,
                    }
                else:
                    if classes.course.capacity > classes.memberCnt:
                        models.StuHasClass.objects.create(Student=students, Class=classes)
                        classes.memberCnt += 1
                        classes.save()
                    else:
                        space_out = True
                        return_dict = {
                            'web_title': '课程选择',
                            'page_title': '课程选择',
                            'request_user': req.user,
                            'space_out': space_out,
                        }
        choice = req.session.get('choice')
        content = req.session.get('content')
        print(choice)
        print(choice)
        print(content)
        if choice == "skjs":
            teacher_name = content.split(' ', 1)
            if len(teacher_name) < 2:
                tab_missing = True
                return_dict = {
                    'web_title': '课程选择',
                    'page_title': '课程选择',
                    'request_user': req.user,
                    'identity': identity,
                    'tab_missing': tab_missing,
                }
                return render(req, 'stu_select.html', return_dict)
            user = models.User.objects.filter(first_name=teacher_name[1], last_name=teacher_name[0])
            if len(user) > 0:
                class_info = models.Class.objects.filter(teacher=user[0])
                for j in range(1, len(user)):
                    tmp = models.Class.objects.filter(teacher=user[j])
                    class_info = class_info | tmp
            else:
                tea_non = True
                return_dict = {
                    'web_title': '课程选择',
                    'page_title': '课程选择',
                    'request_user': req.user,
                    'identity': identity,
                    'tea_non': tea_non,
                }
                return render(req, 'stu_select.html', return_dict)
        elif choice == "kcmc":
            class_name = models.Course.objects.filter(name__contains=content)
            class_info = models.Class.objects.filter(course=class_name[0].id)
            for i in range(1, len(class_name)):
                class_id = models.Class.objects.filter(course=class_name[i].id)
                class_info = class_info | class_id
        elif choice == "kcbh":
            class_info = models.Class.objects.filter(course=int(content))
        else:
            class_info = models.Class.objects.all()
        return_dict["class_info"] = class_info
        students = models.Student.objects.get(user_id=req.user.id)
        my_hasclass = models.StuHasClass.objects.filter(Student=students)
        print(my_hasclass)

        if len(my_hasclass) > 0:
            my_class_set = models.Class.objects.filter(pk=my_hasclass[0].Class.id)
            for j in range(1, len(my_hasclass)):
                tmp = models.Class.objects.filter(pk=my_hasclass[j].Class.id)
                my_class_set = my_class_set | tmp
        else:
            my_class_set = {}
        return_dict["my_class"] = my_class_set
        print(my_class_set)
    elif req.method == "GET":
        return_dict = {
            'web_title': '课程选择',
            'page_title': '课程选择',
            'request_user': req.user,
            'identity': identity
        }
        req.session['choice'] = "all"
        req.session['content'] = "all"
        class_info = models.Class.objects.all()
        return_dict["class_info"] = class_info

        students = models.Student.objects.get(user_id=req.user.id)
        my_hasclass = models.StuHasClass.objects.filter(Student=students)
        print(my_hasclass)

        if len(my_hasclass) > 0:
            my_class_set = models.Class.objects.filter(pk=my_hasclass[0].Class.id)
            for j in range(1, len(my_hasclass)):
                tmp = models.Class.objects.filter(pk=my_hasclass[j].Class.id)
                my_class_set = my_class_set | tmp
        else:
            my_class_set = {}
        return_dict["my_class"] = my_class_set
        print(my_class_set)
    return render(req, 'stu_select.html', return_dict)
