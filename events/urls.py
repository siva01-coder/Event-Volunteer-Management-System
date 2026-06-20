from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('volunteer/dashboard/', views.volunteer_dashboard,
         name='volunteer_dashboard'),
    path('register/<str:event_id>/', views.register_for_event,
         name='register_for_event'),
    path('approve/<int:registration_id>/',
         views.approve_registration, name='approve_registration'),
    path('reject/<int:registration_id>/',
         views.reject_registration, name='reject_registration'),
    path('task/<int:task_id>/status/',
         views.update_task_status, name='update_task_status'),
    path('create/', views.create_event, name='create_event'),
    path('assign-task/<int:registration_id>/',
         views.assign_task, name='assign_task'),
]
