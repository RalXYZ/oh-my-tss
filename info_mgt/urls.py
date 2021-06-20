from django.urls import path
from django.views import generic
from . import views

urlpatterns = [
    # path('', generic.RedirectView.as_view(url='./main'), name='index'),
    path('', views.index, name='index'),
    path('account', views.account_list, name='account_list'),
    path('account/<int:page>', views.account_list, name='account_list'),
    path('course/<int:page>', views.course_list, name='course_list'),

    path('course', views.course_list, name='course_list'),
    path('course/detail', views.course_display, name='course_display'),
    path(r'course/<str:option>', views.course_edit, name='course_edit'),

    path('info', views.info_view, name='info_view'),
    path('info/view', views.info_view, name='info_view'),
    path('info/edit', views.info_edit, name="info_edit")
]
