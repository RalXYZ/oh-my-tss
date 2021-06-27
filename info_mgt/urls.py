from django.urls import path
from django.views import generic
from . import views

urlpatterns = [
    # path('', generic.RedirectView.as_view(url='./main'), name='index'),
    path('', views.index, name='index'),

    path('account', views.account_list, name='account_list'),
    path('account/<int:page>', views.account_list, name='account_list'),
    path('account/add', views.account_add, name="account_add"),
    path('account/add/<str:username>', views.account_add, name="account_add"),
    path('account/edit', views.account_edit, name="account_edit"),
    path('account/edit/<str:username>', views.account_edit, name="account_edit"),
    path('account/delete/<str:username>', views.account_delete, name='account_delete'),

    path('info', views.info_view, name='info_view'),
    path('info/view', views.info_view, name='info_view'),
    path('info/view/<str:username>', views.info_view_with_username, name='info_view'),
    path('info/edit', views.info_edit, name="info_edit"),
    path('info/edit/<str:username>', views.info_edit, name="info_edit"),
    
    path('course', views.course_list, name='course_list'),
    path('course/<int:page>', views.course_list, name='course_list'),
    path('course/detail/<str:name>', views.course_detail, name='course_display'),
    path('course/delete/<str:name>', views.course_delete, name='course_delete'),
    path('course/<str:option>/<str:in_course_name>', views.course_edit, name='course_edit'),

    path('class', views.class_list, name='class_list'),
    path('class/add', views.class_add, name='class_add'),
    path('class/<int:page>', views.class_list, name='class_list'),
]
