from django.contrib.auth import authenticate

def custom_login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password. Please try again.')
    return render(request, 'users/login.html')
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from allauth.account.views import SignupView
from .models import User, FundiProfile, PortfolioImage
from .forms import FundiSignupForm, FundiOnboardingForm
import json


class FundiSignupView(SignupView):
    template_name = 'users/signup.html'
    form_class = FundiSignupForm
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Set role to fundi after successful signup
        self.user.role = 'fundi'
        self.user.save()
        return response


@login_required
def fundi_onboarding(request):
    if request.user.role != 'fundi':
        return redirect('dashboard')
    
    if request.user.onboarding_complete:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = FundiOnboardingForm(request.POST, request.FILES)
        if form.is_valid():
            # Create or get FundiProfile
            fundi_profile, created = FundiProfile.objects.get_or_create(user=request.user)
            
            # Update profile data
            fundi_profile.skills = form.cleaned_data['skills']
            fundi_profile.description = form.cleaned_data['description']
            fundi_profile.experience_years = form.cleaned_data['experience_years']
            fundi_profile.hourly_rate = form.cleaned_data['hourly_rate']
            fundi_profile.save()
            
            # Update user location and mark onboarding complete
            request.user.location = form.cleaned_data['location']
            request.user.onboarding_complete = True
            request.user.save()
            
            # Handle portfolio images
            portfolio_images = request.FILES.getlist('portfolio_images')
            for image in portfolio_images:
                PortfolioImage.objects.create(fundi=fundi_profile, image=image)
            
            messages.success(request, 'Your Fundi profile has been created successfully!')
            return redirect('dashboard')
    else:
        form = FundiOnboardingForm()
    
    return render(request, 'users/fundi_onboarding.html', {'form': form})


@login_required
def profile_view(request):
    context = {'user': request.user}
    if request.user.role == 'fundi':
        try:
            context['fundi_profile'] = request.user.fundi_profile
            context['portfolio_images'] = request.user.fundi_profile.portfolio_images.all()
        except FundiProfile.DoesNotExist:
            context['fundi_profile'] = None
    return render(request, 'users/profile.html', context)


from .forms import CustomerSignupForm

def customer_signup_view(request):
    if request.method == 'POST':
        form = CustomerSignupForm(request.POST)
        if form.is_valid():
            user = form.save(request)
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = CustomerSignupForm()
    return render(request, 'users/signup.html', {'form': form})
