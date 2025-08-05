from django.urls import path
from . import views

urlpatterns = [
    path('clock-in-out/', views.clock_in_out, name='clock_in_out'),
    path('history/', views.attendance_history, name='attendance_history'),
    path('leave/request/', views.request_leave, name='request_leave'),
    path('leave/list/', views.leave_list, name='leave_list'),
    path('leave/approve/<int:pk>/', views.approve_reject_leave, name='approve_reject_leave'),
    path('holidays/', views.public_holidays_list, name='public_holidays_list'),
]
