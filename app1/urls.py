from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('', views.index, name='index'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('faculty_dashboard/', views.faculty_dashboard, name='faculty_dashboard'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('logout/', views.logout_view, name='logout'),

    path('admin_dashboard/notice_board/', views.notice_board, name='notice_board'),
    path('admin_dashboard/add_notice/', views.add_notice, name='add_notice'),
    path('admin_dashboard/add_faculty/', views.add_faculty, name='add_faculty'),
    path('admin_dashboard/faculty_list/', views.faculty_list, name='faculty_list'),
    path('admin_dashboard/delete_notice/<int:notice_id>/', views.notice_board, name='delete_notice'),
    path('admin_dashboard/delete_faculty/<int:user_id>/', views.faculty_list, name='delete_faculty'),
    
    path('faculty_dashboard/uni_notice_board/', views.uni_notice_board, name='uni_notice_board'),
    path('faculty_dashboard/create_classroom/', views.create_classroom, name='create_classroom'),
    path('faculty_dashboard/classroom_list/', views.classroom_list, name='classroom_list'),
    path('faculty_dashboard/add_student/', views.add_student, name='add_student'),
    path('faculty_dashboard/announcements_list/', views.announcements_list, name='announcements_list'),
    path('faculty_dashboard/resources_list/', views.resources_list, name='resources_list'),
    path('faculty_dashboard/add_ann_res/', views.add_ann_res, name='add_ann_res'),
    path('faculty_dashboard/add_ann_res/ann_form/<int:classroom_id>/', views.ann_form, name='ann_form'),
    path('faculty_dashboard/add_ann_res/res_form/<int:classroom_id>/', views.res_form, name='res_form'),

    path('faculty_dashboard/add_attendance/', views.add_attendance, name='add_attendance'),
    path('add_attendance/att_form/<int:classroom_id>/', views.att_form, name='att_form'),
    path('attendance_list/', views.attendance_list, name='attendance_list'),

    path('student_dashboard/uni_notice_board_s/', views.uni_notice_board_s, name='uni_notice_board_s'),
    path('student_dashboard/classroom_list_s/', views.classroom_list_s, name='classroom_list_s'),
    path('student_dashboard/classroom_announcements_s/', views.classroom_announcements_s, name='classroom_announcements_s'),
    path('student_dashboard/classroom_resources_s/', views.classroom_resources_s, name='classroom_resources_s'),
    path('student_dashboard/add_classroom_request_s/', views.add_classroom_request_s, name='add_classroom_request_s'),
]

