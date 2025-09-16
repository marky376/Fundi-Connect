
from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.job_list, name='jobs'),
    path('new/', views.job_create, name='job_create'),
    path('<int:job_id>/', views.job_detail, name='job_detail_jobs'),
    path('<int:job_id>/apply/', views.job_apply, name='job_apply'),
    path('<int:job_id>/edit/', views.job_edit, name='job_edit'),
    path('<int:job_id>/delete/', views.job_delete, name='job_delete'),
    path('applications/', views.my_applications, name='my_applications'),
    path('my-jobs/', views.my_jobs, name='my_jobs'),
    path('<int:job_id>/nudge/', views.nudge_fundis, name='nudge_fundis'),
    path('apply/<int:job_id>/', views.apply, name='apply'),
    path('<int:job_id>/messages/<int:fundi_id>/', views.job_messages, name='job_messages'),
    path('<int:job_id>/accept/<int:application_id>/', views.accept_application, name='accept_application'),
]