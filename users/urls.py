from django.urls import path
from . import views

urlpatterns = [
    path('fundi-onboarding/', views.fundi_onboarding, name='fundi_onboarding'),
    path('profile/', views.profile_view, name='profile'),
    path('signup/customer/', views.customer_signup_view, name='customer_signup'),
    path('signup/', views.FundiSignupView.as_view(), name='signup'),
    path('login/', views.custom_login_view, name='login'),
    path('login/customer/', views.customer_login_view, name='customer_login'),
    path('request-otp/', views.request_otp_view, name='request_otp'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
]