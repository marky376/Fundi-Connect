from django import forms
from django.contrib.auth.forms import UserCreationForm
from allauth.account.forms import SignupForm
from .models import User, FundiProfile
import json


class FundiSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    # Phone number field removed
    def save(self, request):
        user = super().save(request)
        # Ensure both roles are present for fundi onboarding
        user.roles = list(set(user.roles + ['fundi', 'customer']))
        user.active_role = 'fundi'
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user


class CustomerSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    # Phone number field removed
    def save(self, request):
        user = super().save(request)
        # Ensure the user has the customer role and is set to customer mode
        user.roles = list(set(user.roles + ['customer']))
        user.active_role = 'customer'
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user


class FundiOnboardingForm(forms.Form):
    location = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Nairobi, Westlands'
        })
    )
    profile_photo = forms.ImageField(required=True, help_text='Upload your profile photo')
    id_document = forms.ImageField(required=True, help_text='Upload your ID document')
    # Phone number field removed
    def clean_location(self):
        location = self.cleaned_data['location']
        if not location.strip():
            raise forms.ValidationError('Location is required.')
        return location
    
    skills = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter skills separated by commas (e.g., Plumbing, Electrical)'
        }),
        help_text='Enter your skills separated by commas'
    )
    
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Tell customers about yourself and your experience...'
        }),
        required=False
    )
    
    experience_years = forms.IntegerField(
        min_value=0,
        max_value=50,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0'
        }),
        help_text='Years of professional experience'
    )
    
    hourly_rate = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0.00',
            'step': '0.01'
        }),
        help_text='Your hourly rate in KES (optional)'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Handle portfolio images separately in the view
    
    def clean_skills(self):
        skills_str = self.cleaned_data['skills']
        skills_list = [skill.strip() for skill in skills_str.split(',') if skill.strip()]
        if len(skills_list) < 1:
            raise forms.ValidationError('Please enter at least one skill.')
        return skills_list