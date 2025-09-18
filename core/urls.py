from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('customer-dashboard/', views.dashboard, name='customer_dashboard'),
    path('fundi-dashboard/', views.dashboard, name='fundi_dashboard'),
    path('jobs/', views.job_list, name='job_list'),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('api/fundi-locations/', views.fundi_locations_api, name='fundi_locations_api'),
]