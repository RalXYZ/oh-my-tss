import datetime

from django.db import OperationalError, transaction, DataError
from django.db.models import Q
from django.http.response import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
import weasyprint
from django.template.loader import render_to_string

from info_mgt.models import Campus, Class, Major
from oh_my_tss.errview import err_403, err_404, err_50x
from .genetic import *
from .models import Classroom, ClassHasRoom, Application, Building


def index(request):
    class_list = Class.objects.all()
    for i in class_list:
        rooms = ClassHasRoom.objects.filter(Class_id=i.id)
        if not rooms:  # 如果教学班没有时段记录，则生成时段记录
            times = i.course.duration.split()
            with transaction.atomic():  # 通过事务避免只生成了部分时段记录
                for j in times:
                    new_section = ClassHasRoom(Class_id=i.id, duration=int(j))
                    new_section.save()
    return HttpResponseRedirect(reverse('room_class'))


def add_room(request):  # 打开添加教室的页面
    current_user_group = request.user.groups.first()
    if not current_user_group or current_user_group.name != 'admin':
        return err_403(request)
    return_dict = {'web_title': '添加教室',
                   'page_title': '添加教室',
                   'request_user': request.user,
                   'cur_submodule': 'add_room', }
    try:
        campus_list = Campus.objects.all().order_by('id')
    except OperationalError:
        return_dict['info_retrieve_failure'] = True
    else:
        return_dict['campus_list'] = campus_list
        try:
            if request.method == 'GET':
                building_list = Building.objects.filter(campus_id=campus_list.first().id)
            elif request.method == 'POST' and request.POST.get('campus'):
                building_list = Building.objects.filter(campus_id=request.POST.get('campus'))
                return_dict['selected_campus'] = int(request.POST.get('campus'))
        except OperationalError:  # 捕捉数据库操作的异常
            return_dict['info_retrieve_failure'] = True
        else:
            return_dict['building_list'] = building_list
    if request.GET.get('succeeded'):  # 之前有教室添加成功
        return_dict['add_success'] = True
    elif request.GET.get('failed'):  # 之前教室因为其他原因添加失败
        return_dict['add_failure'] = True
    elif request.GET.get('duplicated'):  # 之前教室因为门牌号重复而添加失败
        return_dict['duplicate'] = True
    elif request.GET.get('outofrange'):
        return_dict['outofrange'] = True
    return render(request, 'add_room.html', return_dict)


def add_room_submit(request):  # 提交添加教室的信息
    current_user_group = request.user.groups.first()
    if not current_user_group or current_user_group.name != 'admin':
        return err_403(request)
    if request.method == 'POST':
        # room_campus_id = request.POST.get('campus')
        room_building_id = request.POST.get('building')
        room_number = request.POST.get('room_id')
        room_type = request.POST.get('room_type')
        room_capacity = request.POST.get('room_capacity')
        try:
            duplicate_check = Classroom.objects.get(building_id=room_building_id, room_number=room_number)
        except Classroom.DoesNotExist:
            pass
        else:
            if duplicate_check:
                return HttpResponseRedirect(reverse('add_room') + '?duplicated=true')
        new_room = Classroom(building_id=room_building_id, room_number=room_number, type=room_type,
                             capacity=room_capacity)
        try:
            new_room.save()
        except DataError:
            return HttpResponseRedirect(reverse('add_room') + '?outofrange=true')
        except OperationalError:
            return HttpResponseRedirect(reverse('add_room') + '?failed=true')
        else:
            return HttpResponseRedirect(reverse('add_room') + '?succeeded=true')


def modify_room(request, page=0):  # 打开修改教室页面
    current_user_group = request.user.groups.first()
    if not current_user_group or current_user_group.name != 'admin':
        return err_403(request)
    if request.method == 'GET':
        return_dict = {'web_title': '修改教室信息',
                       'page_title': '修改教室信息',
                       'request_user': request.user,
                       'cur_submodule': 'modify_room'}
        if request.GET.get('delete_success'):
            return_dict['delete_room_successfully'] = True
        elif request.GET.get('delete_failure'):
            return_dict['delete_room_failed'] = True
        try:
            room_list = Classroom.objects.all().order_by('-building_id', 'room_number')
        except OperationalError:
            return_dict['info_retrieve_failure'] = True
        else:
            page_sum = len(room_list) // 10 + 1
            if page > page_sum:
                return HttpResponse(404)
            return_dict['room_list'] = room_list[page * 10: page * 10 + 10]
            return_dict['cur_page'] = page + 1
            return_dict['prev_page'] = (page - 1)
            return_dict['prev_disabled'] = (page == 0)
            return_dict['next_page'] = page + 1
            return_dict['next_disabled'] = (page + 1 >= page_sum)
            return_dict['page_sum'] = page_sum
        if request.GET.get('success'):
            return_dict['modify_succeeded'] = True
        elif request.GET.get('failure'):
            return_dict['modify_failed'] = True
        elif request.GET.get('duplication'):
            return_dict['duplicated'] = True
        elif request.GET.get('no_such_room'):
            return_dict['no_such_room'] = True
        elif request.GET.get('outofrange'):
            return_dict['outofrange'] = True
        return render(request, 'modify_room.html', return_dict)


def modify_certain_room(request, room_id):  # 修改特定教室信息的页面
    current_user_group = request.user.groups.first()
    if not current_user_group or current_user_group.name != 'admin':
        return err_403(request)
    return_dict = {'web_title': '修改教室信息',
                   'page_title': '修改教室信息',
                   'request_user': request.user,
                   'cur_submodule': 'modify_room'}
    try:
        room_to_modify = Classroom.objects.get(pk=room_id)
    except OperationalError:
        return_dict['info_retrieve_failure'] = True
    except Classroom.DoesNotExist:
        return HttpResponseRedirect(reverse('modify_room') + '?no_such_room=true')
    else:
        return_dict['original_info'] = room_to_modify
    try:
        if request.method == 'GET':
            campus_list = Campus.objects.all().order_by('id')
            building_list = Building.objects.filter(campus_id=room_to_modify.building.campus_id)
        elif request.method == 'POST':
            campus_list = Campus.objects.all().order_by('id')
            building_list = Building.objects.filter(campus_id=request.POST.get('campus'))
            return_dict['selected_campus'] = int(request.POST.get('campus'))
    except OperationalError:
        return_dict['info_retrieve_failure'] = True
    else:
        return_dict['campus_list'] = campus_list
        return_dict['building_list'] = building_list
        return render(request, 'modify_certain_room.html', return_dict)


def modify_room_submit(request, room_id):  # 提交修改的教室信息
    current_user_group = request.user.groups.first()
    if not current_user_group or current_user_group.name != 'admin':
        return err_403(request)
    if not room_id:
        return err_404(request)  # 必须在url中给出教室编号
    if request.method == 'POST':
        try:
            room_to_modify = Classroom.objects.get(pk=room_id)
        except OperationalError:
            return HttpResponseRedirect(reverse('modify_room') + '?failure=true')
        except Classroom.DoesNotExist:
            return HttpResponseRedirect(reverse('modify_room') + '?no_such_room=true')
        new_room_number = request.POST.get('room_number')
        new_building_id = request.POST.get('building')
        try:
            duplicate = Classroom.objects.get(building_id=new_building_id, room_number=new_room_number)
        except Classroom.DoesNotExist:
            pass
        else:
            if duplicate.id != room_id:
                return HttpResponseRedirect(reverse('modify_room') + '?duplication=true')
        room_to_modify.building_id = request.POST.get('building')
        room_to_modify.room_number = request.POST.get('room_number')
        room_to_modify.type = request.POST.get('room_type')
        room_to_modify.capacity = request.POST.get('room_capacity')
        try:
            room_to_modify.save()
        except DataError:
            return HttpResponseRedirect(reverse('modify_room') + '?outofrange=true')
        except OperationalError:
            return HttpResponseRedirect(reverse('modify_room') + '?failure=true')
        else:
            return HttpResponseRedirect(reverse('modify_room') + '?success=true')
    else:
        return HttpResponseRedirect(reverse('modify_room'))


def delete_room(request, room_id):
    current_user_group = request.user.groups.first()
    if not current_user_group or current_user_group.name != 'admin':
        return err_403(request)
    if not room_id:
        return HttpResponseRedirect(reverse('modify_room'))
    if request.method == 'GET':
        success = '?delete_success=true'
        failure = '?delete_failure=true'
        try:
            Classroom.objects.get(pk=room_id).delete()
        except Classroom.DoesNotExist:
            return HttpResponseRedirect(reverse('modify_room') + '?no_such_room=true')
        except OperationalError:
            return HttpResponseRedirect(reverse('modify_room') + failure)
        else:
            return HttpResponseRedirect(reverse('modify_room') + success)


def auto_schedule(request, page=0):  # 打开自动排课页面
    current_user_group = request.user.groups.first()
    if not current_user_group or current_user_group.name != 'admin':
        return err_403(request)
    if request.method == 'GET':
        return_dict = {'web_title': '自动排课',
                       'page_title': '自动排课',
                       'request_user': request.user,
                       'cur_submodule': 'auto_schedule'}
        if request.GET.get('partial'):
            return_dict['class_not_schedule'] = True
        elif request.GET.get('all'):
            return_dict['class_schedule'] = True
        try:
            schedule_list = Class.objects.filter(classhasroom__classroom__isnull=True, year=2021,
                                                 term__in={'AU', 'WI', 'AW'}).distinct().order_by('id')
            scheduled_list = Class.objects.filter(classhasroom__classroom__isnull=False, year=2021,
                                                  term__in={'AU', 'WI', 'AW'}).distinct().order_by('id')
        except OperationalError:
            return err_50x(request, 500)
        else:
            schedule_list = schedule_list.union(scheduled_list)
            for i in schedule_list:
                i.teacher_name = i.teacher.first_name + ' ' + i.teacher.last_name
            return_dict['schedule_list'] = schedule_list[page * 10: page * 10 + 10]
            page_sum = len(schedule_list) // 10 + 1
            if page >= page_sum:
                return err_404(request)
            return_dict['cur_page'] = page + 1
            return_dict['prev_page'] = (page - 1)
            return_dict['prev_disabled'] = (page == 0)
            return_dict['next_page'] = page + 1
            return_dict['next_disabled'] = (page + 1 >= page_sum)
            return_dict['page_sum'] = page_sum
        return render(request, 'auto_schedule.html', return_dict)


def do_auto_schedule(request):  # 进行自动排课。。。麻烦（（（
    current_user_group = request.user.groups.first()
    if not current_user_group or current_user_group.name != 'admin':
        return err_403(request)
    section_list = ClassHasRoom.objects.filter(Class__year=2021, Class__term__in={'AU', 'WI', 'AW'})
    s = []
    for i in section_list:
        compulsory_list = Major.objects.filter(majorhascourse__course_id=i.Class.course_id,
                                               majorhascourse__course_type='C')
        if not compulsory_list:
            compulsory_list = Major.objects.none()
        s.append(Schedule(i.id, i.Class.course_id, i.Class_id, i.Class.teacher_id, i.duration, compulsory_list,
                          i.Class.course.capacity, i.Class.term))
    ga = GeneticOptimize()
    room_range = Classroom.objects.filter(type='O')
    for i in room_range:
        i.campus_id = i.building.campus_id
    res = ga.evolution(schedules=s, roomRange=room_range, slotnum=13)
    direct_link = reverse('auto_schedule')
    conflict_count = 0
    with transaction.atomic():
        for i in res:
            conflict_check = ClassHasRoom.objects.filter(
                Q(classroom_id=i.roomId) & Q(Class__year=2021) & Q(Class__term=i.term)
                & ~Q(Q(end_at__lt=i.slot)
                     | Q(start_at__gt=i.slot + i.duration - 1))
                & Q(day=i.weekDay) & ~Q(id=i.sectionId))
            if len(conflict_check) > 0 or (i.duration == 4 and (i.slot != 1 or i.slot != 6)) \
                    or (i.duration == 3 and i.slot not in {3, 6, 11}) \
                    or (i.duration == 2 and i.slot not in {1, 3, 6, 7, 9, 11}) \
                    or (i.duration == 5 and i.slot not in {1, 6}):  # 如果有冲突或开始的节数不合适，该课程不被排入课表
                same_class_section_list = ClassHasRoom.objects.filter(Class_id=i.classId)
                for j in same_class_section_list:  # 已经排进去同一个教学班的其他时段再删掉
                    new_section = ClassHasRoom(id=j.id, Class_id=j.Class_id, duration=j.duration)
                    j.delete()
                    new_section.save()
                conflict_count += 1
            else:  # 把这个时段排进去
                this_section = ClassHasRoom.objects.get(pk=i.sectionId)
                this_section.classroom_id = i.roomId
                this_section.start_at = i.slot
                this_section.end_at = i.slot + this_section.duration - 1
                this_section.day = i.weekDay
                this_section.save()
        if conflict_count > 0:
            direct_link += '?partial=1'
        else:
            direct_link += '?all=1'
    return HttpResponseRedirect(direct_link)


def manipulate_schedule(request):  # 打开手动调课页面
    current_user_group = request.user.groups.first()
    if not current_user_group or current_user_group.name != 'admin':
        return err_403(request)
    if request.method == 'GET':
        return_dict = {'web_title': '手动课程调整',
                       'page_title': '手动课程调整',
                       'request_user': request.user,
                       'cur_submodule': 'manipulate_schedule'}
        try:
            campus_list = Campus.objects.all()
        except OperationalError:
            return err_50x(request, 500)
        else:
            return_dict['campus_list'] = campus_list
        logic = request.GET.get('logic')
        if logic:  # 有查询提交
            class_list_1 = Class.objects.none()
            class_list_2 = Class.objects.none()
            type1 = request.GET.get('cx_cxlb_1')
            cxnr1 = request.GET.get('cx_cxnr_1')
            if type1 == 'kcbh':  # 查询课程编号
                if cxnr1:
                    try:
                        class_list_1 = Class.objects.filter(course_id=cxnr1, year=2021, term__in={'AU', 'WI', 'AW'})
                    except:
                        return err_50x(request, 500)
            elif type1 == 'skjs':  # 查询授课教师
                try:
                    cxnr1 = cxnr1.split()
                    class_list_1 = Class.objects.filter(
                        Q(teacher__first_name__in=cxnr1) | Q(teacher__last_name__in=cxnr1), year=2021,
                        term__in={'AU', 'WI', 'AW'})
                except:
                    return err_50x(request, 500)
            elif type1 == 'jxbbh':  # 查询教学班编号
                if cxnr1:
                    try:
                        class_list_1 = Class.objects.filter(id=cxnr1, year=2021, term__in={'AU', 'WI', 'AW'})
                    except:
                        return err_50x(request, 500)

            elif type1 == 'kcmc':  # 查询课程名称
                try:
                    class_list_1 = Class.objects.filter(course__name__contains=cxnr1, year=2021,
                                                        term__in={'AU', 'WI', 'AW'})
                except:
                    return err_50x(request, 500)
            elif type1 == 'sksj':  # 查询上课时间
                day = request.GET.get('day1')
                try:
                    class_list_1 = Class.objects.filter(classhasroom__day=day, year=2021, term__in={'AU', 'WI', 'AW'})
                except:
                    return err_50x(request, 500)
            elif type1 == 'skxq':  # 查询上课校区
                campus_id = request.GET.get('campus1')
                try:
                    classroom_list = Classroom.objects.filter(building__campus_id=campus_id)
                    class_list_1 = Class.objects.filter(classhasroom__classroom__in=classroom_list, year=2021,
                                                    term__in={'AU', 'WI', 'AW'})
                except:
                    return err_50x(request, 500)
            type2 = request.GET.get('cx_cxlb_2')
            cxnr2 = request.GET.get('cx_cxnr_2')
            if type2 == 'kcbh':  # 查询课程编号
                if cxnr2:
                    try:
                        class_list_2 = Class.objects.filter(course_id=cxnr2, year=2021, term__in={'AU', 'WI', 'AW'})
                    except:
                        return err_50x(request, 500)
            elif type2 == 'skjs':  # 查询授课教师
                try:
                    cxnr2 = cxnr2.split()
                    class_list_2 = Class.objects.filter(
                        Q(teacher__first_name__in=cxnr2) | Q(teacher__last_name__in=cxnr2), year=2021,
                        term__in={'AU', 'WI', 'AW'})
                except:
                    return err_50x(request, 500)
            elif type2 == 'jxbbh':  # 查询教学班编号
                if cxnr2:
                    try:
                        class_list_2 = Class.objects.filter(id=cxnr2, year=2021, term__in={'AU', 'WI', 'AW'})
                    except:
                        return err_50x(request, 500)
            elif type2 == 'kcmc':  # 查询课程名称
                try:
                    class_list_2 = Class.objects.filter(course__name__contains=cxnr2, year=2021,
                                                        term__in={'AU', 'WI', 'AW'})
                except:
                    return err_50x(request, 500)
            elif type2 == 'sksj':  # 查询上课时间
                day = request.GET.get('day2')
                try:
                    class_list_2 = Class.objects.filter(classhasroom__day=day, year=2021, term__in={'AU', 'WI', 'AW'})
                except:
                    return err_50x(request, 500)
            elif type2 == 'skxq':  # 查询上课校区
                campus_id = request.GET.get('campus2')
                try:
                    classroom_list = Classroom.objects.filter(building__campus_id=campus_id)
                    class_list_2 = Class.objects.filter(classhasroom__classroom__in=classroom_list, year=2021,
                                                        term__in={'AU', 'WI', 'AW'})
                except:
                    return err_50x(request, 500)
            if len(class_list_1) > 0 and len(class_list_2) > 0:
                if logic == 'and':
                    class_list_1 = class_list_1.intersection(class_list_2)
                elif logic == 'or':
                    class_list_1 = class_list_1.union(class_list_2)
                    for i in class_list_1:
                        i.first_section_id = ClassHasRoom.objects.filter(Class_id=i.id)[0].id
                        i.teacher_name = i.teacher.first_name + ' ' + i.teacher.last_name
                return_dict['courses'] = class_list_1
            elif len(class_list_1) > 0:
                for i in class_list_1:
                    i.first_section_id = ClassHasRoom.objects.filter(Class_id=i.id)[0].id
                    i.teacher_name = i.teacher.first_name + ' ' + i.teacher.last_name
                return_dict['courses'] = class_list_1
            elif len(class_list_2) > 0:
                for i in class_list_2:
                    i.first_section_id = ClassHasRoom.objects.filter(Class_id=i.id)[0].id
                    i.teacher_name = i.teacher.first_name + ' ' + i.teacher.last_name
                return_dict['courses'] = class_list_2
                # else:
                #     for i in class_list:
                #         i.teacher_name = i.teacher.first_name + ' ' + i.teacher.last_name
                #     return_dict['courses'] = class_list
        return render(request, 'manipulate_schedule.html', return_dict)


def manipulate_certain_class(request, section_id):  # 打开处理特定课程的页面
    current_user_group = request.user.groups.first()
    if not current_user_group or current_user_group.name != 'admin':
        return err_403(request)
    if request.method == 'GET':
        return_dict = {'web_title': '手动课程调整',
                       'page_title': '手动课程调整',
                       'request_user': request.user,
                       'cur_submodule': 'manipulate_schedule'}
        if request.GET.get('failed'):
            return_dict['failure'] = True
        if request.GET.get('succeeded'):
            return_dict['success'] = True
        if request.GET.get('conflict'):
            return_dict['conflict'] = True
        try:
            room_to_modify = ClassHasRoom.objects.get(pk=section_id)
            class_to_modify = room_to_modify.Class
            class_to_modify.teacher_name = class_to_modify.teacher.first_name + ' ' + class_to_modify.teacher.last_name
            campus_list = Campus.objects.all()
            selected_campus_id = request.GET.get('campus')
            selected_building_id = request.GET.get('building')
            if not selected_campus_id:
                if room_to_modify.classroom:
                    selected_campus_id = room_to_modify.classroom.building.campus_id
                else:
                    selected_campus_id = Campus.objects.all().first().id
            if not selected_building_id:
                if room_to_modify.classroom and int(selected_campus_id) == room_to_modify.classroom.building.campus_id:
                    selected_building_id = room_to_modify.classroom.building.id
                else:
                    selected_building_id = Building.objects.filter(campus_id=selected_campus_id).first().id
            building_list = Building.objects.filter(campus_id=selected_campus_id)
            classroom_list = Classroom.objects.filter(building_id=selected_building_id)
        except OperationalError:
            pass
        except ClassHasRoom.DoesNotExist:
            return HttpResponseRedirect(reverse('manipulate_schedule'))
        else:
            return_dict['room_to_modify'] = room_to_modify
            return_dict['course'] = class_to_modify
            return_dict['campus'] = campus_list
            return_dict['building_list'] = building_list
            return_dict['selected_campus'] = int(selected_campus_id)
            return_dict['selected_building'] = int(selected_building_id)
            return_dict['classroom_list'] = classroom_list
        return render(request, 'manipulate.html', return_dict)


def submit_manipulate(request, class_has_room_id):  # 提交手动调课（针对一个时段）
    current_user_group = request.user.groups.first()
    if not current_user_group or current_user_group.name != 'admin':
        return err_403(request)
    if not class_has_room_id:
        return err_404(request)
    if request.method == 'POST':
        new_day = int(request.POST.get('skrq'))
        new_start_at = int(request.POST.get('qssj'))
        new_room_id = int(request.POST.get('jshm'))
        try:
            section_to_modify = ClassHasRoom.objects.get(pk=class_has_room_id)
        except ClassHasRoom.DoesNotExist:
            return HttpResponseRedirect(reverse('manipulate_schedule'))
        else:
            new_end_at = new_start_at + section_to_modify.duration - 1
            try:
                conflict_check = ClassHasRoom.objects.filter(Q(Q(classroom_id=new_room_id)
                                                               | Q(Class__teacher=section_to_modify.Class.teacher)) &
                                                             Q(Class__term=section_to_modify.Class.term) &
                                                             Q(Class__year=section_to_modify.Class.year)
                                                             & ~Q(Q(end_at__lt=new_start_at)
                                                                  | Q(start_at__gt=new_end_at))
                                                             & Q(day=new_day) & ~Q(id=class_has_room_id))
            except OperationalError:
                return HttpResponseRedirect(reverse('manipulate_certain_class', args=[class_has_room_id]) + '?failed=1')
            else:
                if len(conflict_check) > 0:
                    return HttpResponseRedirect(
                        reverse('manipulate_certain_class', args=[class_has_room_id]) + '?conflict=1')
                else:
                    section_to_modify.day = new_day
                    section_to_modify.start_at = new_start_at
                    section_to_modify.end_at = new_end_at
                    section_to_modify.classroom_id = new_room_id
                    try:
                        section_to_modify.save()
                    except OperationalError:
                        return HttpResponseRedirect(
                            reverse('manipulate_certain_class', args=[class_has_room_id]) + '?failed=1')
                    else:
                        return HttpResponseRedirect(
                            reverse('manipulate_certain_class', args=[class_has_room_id]) + '?succeeded=1')


def application(request):  # 打开提出调课申请页面
    current_user_group = request.user.groups.first()
    if not current_user_group or current_user_group.name != 'teacher':
        return err_403(request)
    if request.method == 'GET':
        return_dict = {'web_title': '提出调课申请',
                       'page_title': '提出调课申请',
                       'request_user': request.user,
                       'cur_submodule': 'application'}
        if request.GET.get('succeeded'):
            return_dict['success'] = True
        if request.GET.get('failed'):
            return_dict['failure'] = True
        try:
            class_list = Class.objects.filter(teacher_id=request.user.id, year=2021, term__in={'AU', 'WI', 'AW'})
        except OperationalError:
            pass
        else:
            for i in class_list:
                i.not_scheduled = False
                for c in i.classhasroom_set.all():
                    if not c.classroom:
                        i.not_scheduled = True
                        break
            return_dict['my_class_list'] = class_list
        return render(request, 'app_init.html', return_dict)


def submit_application(request):  # 提交调课申请
    current_user_group = request.user.groups.first()
    if not current_user_group or current_user_group.name != 'teacher':
        return err_403(request)
    if request.method == 'POST':
        class_id = request.POST.get('class_selection')
        content = request.POST.get('content')
        new_application = Application(teacher_id=request.user.id, Class_id=class_id, content=content,
                                      submit_time=datetime.datetime.now())
        try:
            new_application.save()
        except OperationalError:
            return HttpResponseRedirect(reverse('application') + '?failed=1')
        else:
            return HttpResponseRedirect(reverse('application') + '?succeeded=1')


def view_application(request):
    current_user_group = request.user.groups.first()
    if not current_user_group or current_user_group.name != 'teacher':
        return err_403(request)
    if request.method == 'GET':
        return_dict = {'web_title': '查看调课申请',
                       'page_title': '查看调课申请',
                       'request_user': request.user,
                       'cur_submodule': 'application'}
        try:
            app_list = Application.objects.filter(teacher_id=request.user.id).order_by('-submit_time')
        except OperationalError:
            pass
        else:
            for i in app_list:
                if i.admin:
                    i.handler = i.admin.first_name + ' ' + i.admin.last_name
            return_dict['applications'] = app_list
        return render(request, 'application.html', return_dict)


def view_spec_application(request, app_id):
    current_user_group = request.user.groups.first()
    if not current_user_group or current_user_group.name != 'teacher':
        return err_403(request)
    if request.method == 'GET':
        return_dict = {'web_title': '查看调课申请',
                       'page_title': '查看调课申请',
                       'request_user': request.user,
                       'cur_submodule': 'application'}
        try:
            app = Application.objects.get(pk=app_id)
        except Application.DoesNotExist:
            return_dict['no_such_app'] = True
        except OperationalError:
            pass
        else:
            app.Class.unscheduled = False
            if app.admin:
                app.handler = app.admin.first_name + ' ' + app.admin.last_name
            for c in app.Class.classhasroom_set.all():
                if not c.classroom:
                    app.Class.unscheduled = True
                    break
            return_dict['app'] = app
        return render(request, 'app_spec.html', return_dict)


def handle_application(request, page=0):  # 打开处理调课申请页面
    current_user_group = request.user.groups.first()
    if not current_user_group or current_user_group.name != 'admin':
        return err_403(request)
    if request.method == 'GET':
        return_dict = {'web_title': '处理调课申请',
                       'page_title': '处理调课申请',
                       'request_user': request.user,
                       'cur_submodule': 'handle_application'}
        if request.GET.get('failed'):
            return_dict['failure'] = True
        if request.GET.get('succeeded'):
            return_dict['success'] = True
        try:
            application_list = Application.objects.filter(reply_time__isnull=True)
        except OperationalError:
            pass
        else:
            for i in application_list:
                i.applicant = i.teacher.first_name + ' ' + i.teacher.last_name
                for k in i.Class.classhasroom_set.all():
                    if not k.classroom:
                        i.Class.unscheduled = True
                        break
                    i.Class.unscheduled = False
            return_dict['applications_unhandled_list'] = application_list
            page_sum = len(application_list) // 10 + 1
            if page >= page_sum:
                return HttpResponse(404)
            return_dict['cur_page'] = page + 1
            return_dict['prev_page'] = (page - 1)
            return_dict['prev_disabled'] = (page == 0)
            return_dict['next_page'] = page + 1
            return_dict['next_disabled'] = (page + 1 >= page_sum)
            return_dict['page_sum'] = page_sum
        return render(request, 'handle_application.html', return_dict)


def handle_certain_application(request, application_id):  # 打开一条特定的申请的处理页面
    current_user_group = request.user.groups.first()
    if not current_user_group or current_user_group.name != 'admin':
        return err_403(request)
    if request.method == 'GET':
        return_dict = {'web_title': '处理调课申请',
                       'page_title': '处理调课申请',
                       'request_user': request.user,
                       'cur_submodule': 'handle_application'}
        try:
            application_to_handle = Application.objects.get(pk=application_id)
        except:
            pass
        else:
            application_to_handle.applicant = application_to_handle.teacher.first_name + ' ' + application_to_handle.teacher.last_name
            for k in application_to_handle.Class.classhasroom_set.all():
                if not k.classroom:
                    application_to_handle.Class.unscheduled = True
                    break
                application_to_handle.Class.unscheduled = False
            return_dict['app'] = application_to_handle
        return render(request, 'process.html', return_dict)


def submit_handle(request, application_id):  # 提交申请处理结果
    current_user_group = request.user.groups.first()
    if not current_user_group or current_user_group.name != 'admin':
        return err_403(request)
    if not application_id:
        return err_404(request)
    if request.method == 'POST':
        reply = request.POST.get('reply')
        accepted_or_not = request.POST.get('choice')
        try:
            application_to_handle = Application.objects.get(pk=application_id)
        except:
            return HttpResponseRedirect(reverse('handle_application'))
        else:
            application_to_handle.reply = reply
            if accepted_or_not == 'accepted':
                application_to_handle.is_accepted = True
            else:
                application_to_handle.is_accepted = False
            application_to_handle.admin = request.user
            application_to_handle.reply_time = datetime.datetime.now()
            try:
                application_to_handle.save()
            except OperationalError:
                return HttpResponseRedirect(reverse('handle_application') + '?failed=1')
            else:
                return HttpResponseRedirect(reverse('handle_application') + '?succeeded=1')


def teacher_class(request):  # 按教师查询课表页面
    current_user_group = request.user.groups.first()
    if not current_user_group or current_user_group.name != 'teacher':
        return err_403(request)
    if request.method == 'GET':  # 获取3个查询条件
        if not request.GET.get('term') and not request.GET.get('year'):
            return HttpResponseRedirect(reverse('teacher_class') + '?year=2021-2022&term=AU')
        return_dict = {'web_title': '教师课表查询', 'page_title': '教师课表查询', 'request_user': request.user,
                       'cur_submodule': 'teacher_class', 'name': request.user.first_name + ' ' + request.user.last_name}
        year = request.GET.get('year')
        term = request.GET.get('term')
        return_dict['year'] = year
        return_dict['term'] = term
        if term == 'AU':
            return_dict['term_char'] = '秋'
        elif term == 'SP':
            return_dict['term_char'] = '春'
        elif term == 'WI':
            return_dict['term_char'] = '冬'
        elif term == 'SU':
            return_dict['term_char'] = '夏'
        if year == '2021-2022' and (term == 'SP' or term == 'SU'):
            year = 2022
        elif year == '2021-2022' and (term == 'AU' or term == 'WI'):
            year = 2021
        elif year == '2020-2021' and (term == 'SP' or term == 'SU'):
            year = 2021
        elif year == '2020-2021' and (term == 'AU' or term == 'WI'):
            year = 2020
        elif year == '2019-2020' and (term == 'SP' or term == 'SU'):
            year = 2020
        elif year == '2019-2020' and (term == 'AU' or term == 'WI'):
            year = 2019
        elif year == '2018-2019' and (term == 'SP' or term == 'SU'):
            year = 2019
        elif year == '2018-2019' and (term == 'AU' or term == 'WI'):
            year = 2018
        if term in {'SU', 'SP'}:
            term_range = {term, 'SS'}
        else:
            term_range = {term, 'AW'}
        section_list = ClassHasRoom.objects.filter(Class__teacher_id=request.user.id, Class__year=year,
                                                   Class__term__in=term_range, classroom__isnull=False)
        for i in section_list:
            i.name = i.Class.course.name
            i.room = i.classroom.building.campus.name + i.classroom.building.name + str(i.classroom.room_number)
            for j in range(1, 8):
                for k in range(1, 14):
                    if i.day == j and i.start_at == k:
                        if k < 10:
                            num = str(k)
                        elif k == 10:
                            num = 'a'
                        elif k == 11:
                            num = 'b'
                        elif k == 12:
                            num = 'c'
                        elif k == 13:
                            num = 'd'
                        return_dict['course' + str(j) + num] = i
        return render(request, 'teacher_class.html', return_dict)


def room_class(request):
    current_user_group = request.user.groups.first()
    if not current_user_group or current_user_group.name not in {'admin', 'teacher'}:
        return err_403(request)
    return_dict = {'web_title': '教室课表查询', 'page_title': '教室课表查询', 'request_user': request.user,
                   'cur_submodule': 'teacher_class', 'name': request.user.first_name + ' ' + request.user.last_name}
    campus_list = Campus.objects.all()
    return_dict['campus_list'] = campus_list
    if request.method == 'POST':
        selected_campus = request.POST.get('campus')
        if selected_campus:
            selected_campus = int(selected_campus)
            return_dict['selected_campus'] = selected_campus
            building_list = Building.objects.filter(campus_id=selected_campus)
            return_dict['building_list'] = building_list
        else:
            selected_building = request.POST.get('building')
            if selected_building:
                selected_building = int(selected_building)
                selected_campus = Building.objects.get(pk=selected_building).campus_id
                building_list = Building.objects.filter(campus_id=selected_campus)
                return_dict['building_list'] = building_list
                return_dict['selected_campus'] = selected_campus
                return_dict['selected_building'] = selected_building
                return_dict['room_list'] = Classroom.objects.filter(building_id=selected_building).order_by(
                    'room_number')
    elif request.method == 'GET':
        room = request.GET.get('room_id')
        year = request.GET.get('year')
        term = request.GET.get('term')
        if room and year and term:
            return_dict['selected_room'] = int(room)
            this_room = Classroom.objects.get(pk=room)
            return_dict['selected_building'] = this_room.building_id
            return_dict['selected_campus'] = this_room.building.campus_id
            return_dict['building_list'] = Building.objects.filter(pk=return_dict['selected_building'])
            return_dict['campus_list'] = Campus.objects.all()
            return_dict['room_list'] = Classroom.objects.filter(building_id=this_room.building_id).order_by(
                'room_number')
            return_dict['year'] = year
            return_dict['term'] = term
            if term == 'AU':
                return_dict['term_char'] = '秋'
            elif term == 'SP':
                return_dict['term_char'] = '春'
            elif term == 'WI':
                return_dict['term_char'] = '冬'
            elif term == 'SU':
                return_dict['term_char'] = '夏'
            if year == '2021-2022' and (term == 'SP' or term == 'SU'):
                year = 2022
            elif year == '2021-2022' and (term == 'AU' or term == 'WI'):
                year = 2021
            elif year == '2020-2021' and (term == 'SP' or term == 'SU'):
                year = 2021
            elif year == '2020-2021' and (term == 'AU' or term == 'WI'):
                year = 2020
            elif year == '2019-2020' and (term == 'SP' or term == 'SU'):
                year = 2020
            elif year == '2019-2020' and (term == 'AU' or term == 'WI'):
                year = 2019
            elif year == '2018-2019' and (term == 'SP' or term == 'SU'):
                year = 2019
            elif year == '2018-2019' and (term == 'AU' or term == 'WI'):
                year = 2018
            if term in {'SU', 'SP'}:
                term_range = {term, 'SS'}
            else:
                term_range = {term, 'AW'}
            return_dict['room_name'] = this_room.building.campus.name + this_room.building.name + str(
                this_room.room_number)
            section_list = ClassHasRoom.objects.filter(Class__year=year, Class__term__in=term_range, classroom_id=room)

            for i in section_list:
                i.name = i.Class.course.name
                i.teacher = i.Class.teacher.first_name + ' ' + i.Class.teacher.last_name
                for j in range(1, 8):
                    for k in range(1, 14):
                        if i.day == j and i.start_at == k:
                            if k < 10:
                                num = str(k)
                            elif k == 10:
                                num = 'a'
                            elif k == 11:
                                num = 'b'
                            elif k == 12:
                                num = 'c'
                            elif k == 13:
                                num = 'd'
                            return_dict['course' + str(j) + num] = i
        else:
            return_dict['building_list'] = Building.objects.filter(campus_id=campus_list[0].id)
    return render(request, 'room_class.html', return_dict)


def download(request):
    current_user_group = request.user.groups.first()
    if not current_user_group or current_user_group.name != 'teacher':
        return err_403(request)
    if request.method == 'GET':
        context = {}
        year = request.GET.get('year_selected')
        term = request.GET.get('term_selected')
        context['year'] = year
        context['term'] = term
        context['name'] = request.user.first_name + request.user.last_name
        if term == 'AU':
            context['term_char'] = '秋'
        elif term == 'SP':
            context['term_char'] = '春'
        elif term == 'WI':
            context['term_char'] = '冬'
        elif term == 'SU':
            context['term_char'] = '夏'
        if year == '2021-2022' and (term == 'SP' or term == 'SU'):
            year = 2022
        elif year == '2021-2022' and (term == 'AU' or term == 'WI'):
            year = 2021
        elif year == '2020-2021' and (term == 'SP' or term == 'SU'):
            year = 2021
        elif year == '2020-2021' and (term == 'AU' or term == 'WI'):
            year = 2020
        elif year == '2019-2020' and (term == 'SP' or term == 'SU'):
            year = 2020
        elif year == '2019-2020' and (term == 'AU' or term == 'WI'):
            year = 2019
        elif year == '2018-2019' and (term == 'SP' or term == 'SU'):
            year = 2019
        elif year == '2018-2019' and (term == 'AU' or term == 'WI'):
            year = 2018
        if term in {'SU', 'SP'}:
            term_range = {term, 'SS'}
        else:
            term_range = {term, 'AW'}
        section_list = ClassHasRoom.objects.filter(Class__teacher_id=request.user.id, Class__year=year,
                                                   Class__term__in=term_range, classroom__isnull=False)
        for i in section_list:
            i.name = i.Class.course.name
            i.campus = i.classroom.building.campus.name
            i.building = i.classroom.building.name
            i.room = str(i.classroom.room_number)
            for j in range(1, 8):
                for k in range(1, 14):
                    if i.day == j and i.start_at == k:
                        if k < 10:
                            num = str(k)
                        elif k == 10:
                            num = 'a'
                        elif k == 11:
                            num = 'b'
                        elif k == 12:
                            num = 'c'
                        elif k == 13:
                            num = 'd'
                        context['course' + str(j) + num] = i
        html = render_to_string('schedule_table.html', context)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = '课表'
        weasyprint.HTML(string=html).write_pdf(response)
        return response
