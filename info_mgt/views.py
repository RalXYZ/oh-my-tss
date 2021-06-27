from django.http.request import HttpRequest
from django.http.response import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import make_password,check_password
# import models
from info_mgt.forms import LoginForm
from info_mgt.forms import SelfInfoForm, LoginForm, CourseEditForm, ClassAddForm, AddForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.db.models import Q

from oh_my_tss.settings import BASE_DIR
from oh_my_tss.errview import *
from . import models
import os
from .models import Major, Student, Teacher


def index(req):
    return render(req, 'info_mgt.html', {
        'web_title': '信息管理',
        'page_title': '信息管理',
        # 'form': SignupForm
    })


# TODO: those following pages' templates are not implemented yet.

def info_view(req):
    try:
        avatar = models.Avatar.objects.get(user=req.user)
        res_url = '/static/media/img/' + str(avatar.avatar.name)
    except ObjectDoesNotExist:
        res_url = '/static/media/img/' + 'default.png'
        pass

    return render(req, 'info_view.html', {
        'web_title': '个人信息',
        'page_title': '个人信息',
        'request_user': req.user,
        'url': res_url
    })


def info_view_with_username(req, username):
    try:
        this_user = models.User.objects.get(username=username)
    except:
        return err_404(req)

    try:
        avatar = models.Avatar.objects.get(user=this_user)
        res_url = '/static/media/img/' + str(avatar.avatar.name)
    except ObjectDoesNotExist:
        res_url = '/static/media/img/' + 'default.png'
        pass

    return render(req, 'info_view.html', {
        'web_title': '个人信息',
        'page_title': '个人信息',
        'request_user': this_user,
        'url': res_url
    })


def info_edit(req, username='#'):
    def is_valid(req):
        flag1 = True
        flag2 = False
        try:
            flag1 = True
            query = models.User.objects.get(username=req.POST['username'])
        except:
            query = None
        if query is None:
            flag1 = False
        if req.POST['password'] == req.POST['password_again']:
            flag2 = True
        if flag1 and flag2:
            return True
        else:
            return False

    if req.method == 'POST':
        if (is_valid(req) and username == req.user.username) or (is_valid(req) and req.user.has_perm('info_mgt.change_student') and req.user.has_perm('info_mgt.change_teacher')):
            new_username = req.POST['username']
            if new_username is None:
                new_username = req.user.username
            new_last_name = req.POST['last_name']
            if new_last_name is None:
                new_last_name = req.user.last_name
            new_first_name = req.POST['first_name']
            if new_first_name is None:
                new_first_name = req.user.first_name
            new_email = req.POST['email']
            if new_email is None:
                new_email = req.user.email
            new_avatar = req.FILES.get('avatar')

            password1 = req.POST['password']
            password2 = req.POST['password_again']
            try:
                if username != '#':
                    temp = models.User.objects.get(username=username)
                    query = models.Avatar.objects.filter(user=temp)
                else:
                    query = models.Avatar.objects.filter(user=req.user.username)
            except:
                query = None

            if query is None and new_avatar is not None:
                if username != '#':
                    temp = models.User.objects.get(username=username)
                    result2 = models.Avatar.objects.create(user=temp, avatar=new_avatar)
                else:
                    result2 = models.Avatar.objects.create(user=req.user, avatar=new_avatar)
                f = open(os.path.join(BASE_DIR, 'static', 'media', 'img', new_avatar.name), 'wb+')
                for chunk in new_avatar.chunks():
                    f.write(chunk)
                f.close()
            elif new_avatar is not None:
                result2 = query.update(avatar=new_avatar)
                f = open(os.path.join(BASE_DIR, 'static', 'media', 'img', new_avatar.name), 'wb+')
                for chunk in new_avatar.chunks():
                    f.write(chunk)
                f.close()
            else:
                result2 = True
            if username != '#':
                query_set = models.User.objects.filter(username=username)
            else:
                query_set = models.User.objects.filter(username=req.user.username)
            if req.POST['password'] is not None:
                result = query_set.update(username=new_username, last_name=new_last_name,
                                          first_name=new_first_name, email=new_email, password=make_password(password1))
            else:
                result = query_set.update(username=new_username, last_name=new_last_name,
                                          first_name=new_first_name, email=new_email)
        else:
            result = 0
            result_2 = 0
        return render(req, 'info_edit.html', {
            'web_title': '个人信息修改', 'page_title': '个人信息修改', 'request_user': req.user,
            'form': SelfInfoForm, 'edit': True,
            'edit_result': True if result != 0 and result2 != 0 else False
        })
    elif req.method == 'GET':
        obj = req.user
        # avatar_obj = models.Avatar.objects.filter(user=req.user)
        # print(avatar_obj)
        return render(req, 'info_edit.html', {
            'web_title': '个人信息修改', 'page_title': '个人信息修改', 'request_user': req.user,
            'form': SelfInfoForm, 'edit': False})
    else:
        return err_404(req)


def account_edit(req, username='#'):
    def is_valid(req):
        flag1 = True
        flag2 = False
        try:
            flag1 = True
            query = models.User.objects.get(username=req.POST['username'])
        except:
            query = None
        if query is None:
            flag1 = False
        if req.POST['password'] == req.POST['password_again']:
            flag2 = True
        if flag1 and flag2:
            return True
        else:
            return False
    if req.user.has_perm('info_mgt.change_student') and req.user.has_perm('info_mgt.change_teacher'):
        if req.method == 'POST':
            if is_valid(req):
                new_username = req.POST['username']
                if new_username is None:
                    new_username = req.user.username
                new_last_name = req.POST['last_name']
                if new_last_name is None:
                    new_last_name = req.user.last_name
                new_first_name = req.POST['first_name']
                if new_first_name is None:
                    new_first_name = req.user.first_name
                new_email = req.POST['email']
                if new_email is None:
                    new_email = req.user.email
                new_avatar = req.FILES.get('avatar')
                new_major = req.POST['major']
                password1 = req.POST['password']
                password2 = req.POST['password_again']

                try:
                    query = models.Avatar.objects.filter(user=req.user)
                except:
                    query = None


                if query is None and new_avatar is not None:
                    result2 = models.Avatar.objects.create(user=req.user, avatar=new_avatar)
                    f = open(os.path.join(BASE_DIR, 'static', 'media', 'img', new_avatar.name), 'wb+')
                    for chunk in new_avatar.chunks():
                        f.write(chunk)
                    f.close()
                elif new_avatar is not None:
                    result2 = query.update(avatar=new_avatar)
                    f = open(os.path.join(BASE_DIR, 'static', 'media', 'img', new_avatar.name), 'wb+')
                    for chunk in new_avatar.chunks():
                        f.write(chunk)
                    f.close()

                result_2 = 1
                if new_major is not None:
                    this_user = models.User.objects.get(username=new_username)
                    if Student.objects.get(user_id=this_user.id):
                        query_set = Student.objects.filter(user_id=this_user.id)
                        try:
                            this_major = models.Major.objects.get(name=new_major)
                            result_1 = query_set.update(major_id=this_major.id, user_id=this_user.id)
                        except:
                            pass
                    elif Teacher.objects.get(user_id=this_user.id):
                        query_set = Teacher.objects.filter(user_id=this_user.id)
                        try:
                            this_major = models.Department.objects.get(name=new_major)
                            result_1 = query_set.update(department_id=this_major.id, user_id=this_user.id)
                        except:
                            pass

                query_set = models.User.objects.filter(username=username)
                if req.POST['password'] is not None:
                    result_0 = query_set.update(username=new_username, last_name=new_last_name,
                                              first_name=new_first_name, email=new_email, password=make_password(password1))
                else:
                    result_0 = query_set.update(username=new_username, last_name=new_last_name,
                                                first_name=new_first_name, email=new_email)
                result_0 = 1
            else:
                result_0 = 0
                result_2 = 0
            return render(req, 'account_edit.html', {
                'web_title': '用户信息修改',
                'page_title': '用户信息修改',
                'request_user': req.user,
                'forms': SelfInfoForm(),
                'edit': True,
                'edit_result': True if result_0 != 0 and result_2 != 0 else False
            })
        elif req.method == 'GET':
            if username != '#':
                obj = models.User.objects.get(username=username)
                return render(req, 'account_edit.html', {
                    'web_title': '用户信息修改',
                    'page_title': '用户信息修改',
                    'request_user': req.user,
                    'forms': SelfInfoForm(),
                    'edit': False
                })
            else:
                obj = req.user
                return render(req, 'account_edit.html', {
                    'web_title': '用户信息修改',
                    'page_title': '用户信息修改',
                    'request_user': req.user,
                    'forms': SelfInfoForm,
                    'edit': False
                })
        else:
            return err_404(req)
    else:
        return err_403(req)


def account_add(req):
    def is_valid(req):
        flag1 = True
        flag2 = False
        flag3 = False
        try:
            flag1 = True
            query = models.User.objects.get(username=req.POST['username'])
        except:
            query = None
        if query is not None:
            flag1 = False
        if req.POST['password'] == req.POST['password_again'] and req.POST['password'] is not None and req.POST['password_again'] is not None:
            flag2 = True
        if req.POST['role'] == 'student':
            query = models.Major.objects.get(name=req.POST['major'])
            if query is not None:
                flag3 = True
        elif req.POST['role'] == 'teacher':
            query = models.Department.objects.get(name=req.POST['major'])
            if query is not None:
                flag3 = True
        if flag1 and flag2 and flag3:
            return True
        else:
            return False

    if req.user.has_perm('info_mgt.add_student') or req.user.has_perm('info_mgt.add_teacher'):
        if req.method == 'POST':
            if is_valid(req):
                new_username = req.POST['username']
                new_last_name = req.POST['last_name']
                new_first_name = req.POST['first_name']
                new_email = req.POST['email']
                new_major = req.POST['major']
                new_avatar = req.FILES.get('avatar')
                new_group = req.POST['role']
                pass_word1 = req.POST['password']
                pass_word2 = req.POST['password_again']
                result_0 = models.User.objects.create(username=new_username, last_name=new_last_name,
                                                      first_name=new_first_name, email=new_email, password=make_password(pass_word1))

                this_user = models.User.objects.get(username=new_username)

                if this_user and new_group and result_0:
                    if new_group == 'teacher':
                        target_group = Group.objects.get(name="teacher")
                        this_user.groups.add(target_group)
                        try:
                            this_major = models.Department.objects.get(name=new_major)
                            result_0 = models.Teacher.objects.create(department_id=this_major.id, user_id=this_user.id)
                        except:
                            result_0 = False
                    elif new_group == 'student':
                        target_group = Group.objects.get(name="student")
                        this_user.groups.add(target_group)
                        try:
                            this_major = models.Major.objects.get(name=new_major)
                            result_0 = models.Student.objects.create(major_id=this_major.id, user_id=this_user.id)
                        except:
                            result_0 = False

                query = models.Avatar.objects.filter(user=this_user)
                if len(query) == 0 and new_avatar is not None and result_0:
                    result_2 = models.Avatar.objects.create(user=this_user, avatar=new_avatar)
                    f = open(os.path.join(BASE_DIR, 'static', 'media', 'img', new_avatar.name), 'wb+')
                    for chunk in new_avatar.chunks():
                        f.write(chunk)
                    f.close()
                elif new_avatar is not None and result_0:
                    result_2 = query.update(avatar=new_avatar)
                    f = open(os.path.join(BASE_DIR, 'static', 'media', 'img', new_avatar.name), 'wb+')
                    for chunk in new_avatar.chunks():
                        f.write(chunk)
                    f.close()
                else:
                    result_2 = True
            else:
                result_0 = 0
                result_2 = 0
            return render(req, 'account_add.html', {
                'web_title': '用户信息添加',
                'page_title': '用户信息添加',
                'request_user': req.user,
                'forms': AddForm,
                'result': 'success',
                'edit_result': True if result_0 != 0 and result_2 != 0 else False
            })
        elif req.method == 'GET':
            obj = req.user
            return render(req, 'account_add.html', {
                'web_title': '用户信息添加',
                'page_title': '用户信息添加',
                'request_user': req.user,
                'result': 'wait',
                'forms': AddForm,
                'edit_result': True
            })
        else:
            return err_404(req)
    else:
        return err_403(req)


def account_list(req, page=0):
    accounts = []

    if req.user.has_perm('info_mgt.view_student') and req.user.has_perm('info_mgt.view_teacher'):

        account_sum = len(User.objects.all())

        for i in range(account_sum):
            groups = User.objects.all()[i].groups.all()
            account = User.objects.all()[i]

            name = account.first_name + ' ' + account.last_name
            major = ''
            username = account.username

            try:
                major = account.student.major.name
            except:
                try:
                    major = account.teacher.department.name
                except:
                    major = ''

            accounts.append({
                'name': name,
                'major': major,
                'username': username
            })
        # accounts.append(User.objects.all()[4].student)

        if req.method == 'POST' and req.POST['name']:
            accounts = [x for x in accounts if x['name'] == req.POST['name']]

        page_sum = max((len(accounts) - 1) // 10 + 1, 1)

        if page >= page_sum:
            return err_404(req)

    else:
        return err_403(req)

    disp_accounts = accounts[page * 10:(page + 1) * 10]

    # if req.user.has_perm('info_mgt.view_course'):

    #     if req.method == 'POST' and req.POST['name']:
    #         courses = models.Course.objects.filter(name=req.POST['name'])
    #     else:
    #         courses = models.Course.objects.all()[page * 10: page * 10 + 10]

    #     page_sum = len(courses) // 10 + 1

    #     if page >= page_sum:
    #         return err_404(req)

    return render(req, 'accountlist.html', {
        'web_title': '信息管理',
        'page_title': '账户信息管理',
        'cur_submodule': 'account',
        'accounts': disp_accounts,
        'cur_page': page + 1,
        'prev_page': page - 1,
        'prev_disabled': page == 0,
        'next_page': page + 1,
        'next_disabled': page + 1 >= page_sum,
        'page_sum': page_sum,
        'last_search': req.POST['name'] if req.method == 'POST' else None,
    })


def account_delete(req, username):
    if req.user.has_perm('info_mgt.delete_student') and req.user.has_perm(
            'info_mgt.delete_teacher') and req.method == 'GET':
        User.objects.filter(username=username).delete()
        return HttpResponseRedirect('/info_mgt/account')
    else:
        return err_403(req)


def course_list(req, page=0):
    if req.user.has_perm('info_mgt.view_course'):

        if req.method == 'POST' and req.POST['name']:
            courses = models.Course.objects.filter(name=req.POST['name'])
        else:
            courses = models.Course.objects.all()

        page_sum = max((len(courses) - 1) // 10 + 1, 1)

        disp_courses = courses[page * 10:(page + 1) * 10]

        if page >= page_sum:
            return err_404(req)
        return render(req, 'courselist.html', {
            'web_title': '课程管理',
            'page_title': '课程信息管理',
            'cur_submodule': 'course',
            'courses': disp_courses,
            'cur_page': page + 1,
            'prev_page': page - 1,
            'prev_disabled': page == 0,
            'next_page': page + 1,
            'next_disabled': page + 1 >= page_sum,
            'page_sum': page_sum,
            'last_search': req.POST['name'] if req.method == 'POST' else None,
        })
    else:
        return err_403(req)


def course_detail(req, name):
    if req.user.has_perm('info_mgt.view_course'):
        course = models.Course.objects.get(name=name)
        return render(req, 'course_detail.html', {
            'web_title': '课程管理',
            'page_title': '课程详情',
            'cur_submodule': 'course',
            'request_course': course
        })
    else:
        return err_403(req)


def course_edit(req, option, in_course_name):
    if req.user.has_perm('info_mgt.change_course'):
        if req.method == 'POST':
            course_name = req.POST.get('name')
            course_desc = req.POST.get('description')
            if len(course_desc) >= 512:
                course_desc = course_desc[0:512]
            course_credit = req.POST.get('credit')
            course_capacity = req.POST.get('capacity')
            course_duration = req.POST.get('duration')
            if option == 'edit':
                query_set = models.Course.objects.filter(name=in_course_name)
                n_updates = query_set.update(
                    name=course_name,
                    description=course_desc,
                    credit=course_credit,
                    capacity=course_capacity,
                    duration=course_duration
                )
                return render(req, 'course_edit.html', {
                    'web_title': '课程管理',
                    'page_title': '修改课程详情',
                    'cur_submodule': 'course',
                    'form': CourseEditForm(instance=models.Course.objects.filter(name=course_name)[0]),
                    'edit_result': True if n_updates != 0 else False
                })
            elif option == 'new':
                if len(course_name) > 0 and len(course_desc) > 0 and course_credit > 0 and course_capacity > 0 and len(course_duration) > 0:
                    ins = models.Course.objects.create(
                        name=course_name,
                        description=course_desc,
                        credit=course_credit,
                        capacity=course_capacity,
                        duration=course_duration
                    )
                    return render(req, 'course_edit.html', {
                        'web_title': '课程管理',
                        'page_title': '添加课程',
                        'cur_submodule': 'course',
                        'form': CourseEditForm,
                        'new_result': True if ins else False
                    })
                else:
                    return render(req, 'course_edit.html', {
                        'web_title': '课程管理',
                        'page_title': '添加课程',
                        'cur_submodule': 'course',
                        'form': CourseEditForm,
                        'new_result': False
                    })
            elif option == 'delete':
                return err_403(req)
            else:
                # TODO: report a 404 error
                return err_404(req)
        elif req.method == 'GET':
            if option == 'edit':
                page_title = '修改课程详情'
                course_data = models.Course.objects.get(name=in_course_name)
                form_obj = CourseEditForm(instance=course_data)
                return render(req, 'course_edit.html', {
                    'web_title': '课程管理',
                    'page_title': '修改课程详情',
                    'cur_submodule': 'course',
                    'form': form_obj
                })
            elif option == 'new':
                page_title = '添加课程'
                return render(req, 'course_edit.html', {
                    'web_title': '课程管理',
                    'page_title': '添加课程',
                    'cur_submodule': 'course',
                    'form': CourseEditForm
                })
            elif option == 'delete':
                models.Course.objects.get(name=in_course_name).delete()
                return HttpResponseRedirect('/info_mgt/course')
        else:
            return err_403(req)
    else:
        return err_403(req)


def course_delete(req, name):
    if req.user.has_perm('info_mgt.delete_course') and req.method == 'GET':
        models.Course.objects.get(name=name).delete()
        return HttpResponseRedirect('/info_mgt/course')
    else:
        return err_403(req)


def class_list(req, page=0):
    if req.user.has_perm('info_mgt.view_class'):
        classes = models.Class.objects.all()
        page_sum = (len(classes) - 1) // 10 + 1
        disp_classes = classes[page * 10:(page + 1) * 10]
        if page >= page_sum:
            return err_404(req)
        return render(req, 'classlist.html', {
            'web_title': '教学班级',
            'page_title': '教学班级管理',
            'cur_submodule': 'class',
            'classes': disp_classes,
            'cur_page': page + 1,
            'prev_page': page - 1,
            'prev_disabled': page == 0,
            'next_page': page + 1,
            'next_disabled': page + 1 >= page_sum,
            'page_sum': page_sum,
        })
    else:
        return err_403(req)


def class_add(req):
    if req.user.has_perm('info_mgt.add_class'):
        if req.method == 'GET':
            return render(req, 'class_add.html', {
                'web_title': '教学班管理',
                'page_title': '添加教学班',
                'cur_submodule': 'class',
                'form': ClassAddForm
            })
        elif req.method == 'POST':
            course_name = req.POST['course']
            first_name = req.POST['first_name']
            last_name = req.POST['last_name']
            year = req.POST['year']
            term = req.POST['term']
            course_ex = models.Course.objects.filter(name=course_name)
            teacher_ex = models.User.objects.filter(Q(first_name=first_name), Q(last_name=last_name))
            if len(course_ex) == 0:
                return render(req, 'class_add.html', {
                    'web_title': '教学班管理',
                    'page_title': '添加教学班',
                    'cur_submodule': 'class',
                    'form': ClassAddForm,
                    'new_result': 1
                })
            elif len(teacher_ex) == 0:
                return render(req, 'class_add.html', {
                    'web_title': '教学班管理',
                    'page_title': '添加教学班',
                    'cur_submodule': 'class',
                    'form': ClassAddForm,
                    'new_result': 2
                })
            else:
                models.Class.objects.create(
                    course=course_ex[0],
                    teacher=teacher_ex[0],
                    year=year,
                    term=term
                )
                return render(req, 'class_add.html', {
                    'web_title': '教学班管理',
                    'page_title': '添加教学班',
                    'cur_submodule': 'class',
                    'form': ClassAddForm,
                    'new_result': 0
                })
    else:
        return err_403(req)


def login_view(req):
    if req.method == 'GET':
        return render(req, 'login.html', {
            'form': LoginForm
        })
    elif req.method == 'POST':
        # Authentication
        username = req.POST['username']
        password = req.POST['password']
        user = authenticate(req, username=username, password=password)
        if user is not None:
            login(req, user)
            # TODO: Redirect to a success page.
            return HttpResponseRedirect('/info_mgt')
        else:
            # TODO: Return an 'invalid login' error message.
            return render(req, 'login.html', {
                'form': LoginForm,
                'login_err_tips': True
            })
    else:
        pass


def logout_view(request):
    logout(request)
    # TODO: Redirect to a success page.
    return HttpResponseRedirect('/info_mgt')


'''
{% if blog.article %}  <!-- permission to visit articles in the blog -->
    <p>You have permission to do something in this blog app.</p>
    {% if perms.blog.add_article %}
        <p>You can add articles.</p>
    {% endif %}
    {% if perms.blog.comment_article %}
        <p>You can comment articles!</p>
    {% endif %}
{% else %}
    <p>You don't have permission to do anything in the blog app.</p>
{% endif %}
'''
