from django.urls import path
from . import views

urlpatterns = [
    path('fundi-onboarding/', views.fundi_onboarding, name='fundi_onboarding'),
    path('profile/', views.profile_view, name='profile'),
    path('signup/customer/', views.customer_signup_view, name='customer_signup'),
]