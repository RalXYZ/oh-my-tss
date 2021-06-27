from django.conf.urls import url
from django.urls import path
from django.views import generic
from . import views

urlpatterns = [
    path('',views.index,name="index"),
    path('resource_share_detail/',views.rsdetail,name="rsdetail"),
    path('resource_share_detail/return_previous_level',views.return_previous_level,name='return_previous_level'),
    path('resource_share_detail/return_share_index',views.return_share_index,name='return_share_index'),
    path('homework',views.homework,name="homework"),
    path('homework_detail',views.hwdetail,name="hwdetail"),
    path('homework_list',views.hwlist,name="hwlist"),
    path('homework_list_t',views.hwlist_t,name="hwlist_t"),
    path('homework_assign',views.hwass,name="homework_assign"),
    path('homework_detail_t',views.hwdetail_t,name="hwdetail_t"),
    path('addassignment',views.addassignment,name="addassignment"),
    path('homework_detail_t_update',views.homework_detail_update,name="homework_detail_t_update"),
    path('homework_delete',views.homeworkdelete,name="homework_delete"),
    path('up/', views.up, name="up"),
    path('up_assignment/', views.up_assignment, name="up_assignment"),
    # path('download/', views.down,name="download"),
    # url(r'^download/(?P<fileID>.+)$', views.down, name='download'),
    path('download/(?P<fileID>.+)', views.down,name="download"),
    path("new/", views.new, name="new"),
    path('rename/',views.rename,name="rename"),
    path('deletefile',views.deletefile,name="deletefile"),
    path('resource_share_search',views.search,name="search"),
    path('homework_correct',views.homework_correct,name="homework_correct"),
    path('ingrade',views.ing,name="ing")


]
