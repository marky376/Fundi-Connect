from django.contrib.auth import authenticate

def custom_login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        # Check if user exists by email
        try:
            db_user = User.objects.get(email=email)
        except User.DoesNotExist:
            db_user = None
        if user is not None:
            if getattr(user, 'role', None) == 'fundi':
                messages.error(request, 'This email belongs to a Fundi. Please use the Fundi login form.')
                return redirect('customer_login')
            login(request, user)
            messages.success(request, 'Logged in successfully!')
            return redirect('dashboard')
        else:
            if db_user:
                if db_user.role == 'fundi':
                    messages.error(request, 'This email belongs to a Fundi. Please use the Fundi login form.')
                elif db_user.role == 'customer':
                    messages.error(request, 'Invalid password for customer account.')
                else:
                    messages.error(request, 'Invalid credentials.')
            else:
                messages.error(request, 'Invalid email or password. Please try again.')
    return render(request, 'users/login.html')

def customer_login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        try:
            db_user = User.objects.get(email=email)
        except User.DoesNotExist:
            db_user = None
        if user is not None and getattr(user, 'role', None) == 'customer':
            login(request, user)
            messages.success(request, 'Logged in successfully as customer!')
            return redirect('dashboard')
        else:
            if db_user:
                if db_user.role == 'fundi':
                    messages.error(request, 'This email belongs to a Fundi. Please use the Fundi login form.')
                elif db_user.role == 'customer':
                    messages.error(request, 'Invalid password for customer account.')
                else:
                    messages.error(request, 'Invalid credentials.')
            else:
                messages.error(request, 'Invalid email or password for customer. Please try again.')
    return render(request, 'users/customer_login.html')
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
            # Save profile photo and ID document
            fundi_profile.profile_photo = form.cleaned_data['profile_photo']
            fundi_profile.id_document = form.cleaned_data['id_document']
            fundi_profile.verification_status = 'pending'
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
    # Restrict access for unverified users
    if not request.user.is_verified:
        messages.warning(request, 'Your account is not verified yet. Please wait for admin approval.')
        # Optionally, restrict dashboard and job access elsewhere
    if request.user.role == 'fundi':
        try:
            context['fundi_profile'] = request.user.fundi_profile
            context['portfolio_images'] = request.user.fundi_profile.portfolio_images.all()
        except FundiProfile.DoesNotExist:
            context['fundi_profile'] = None
        # Handle location and file update for fundi
        if request.method == 'POST' and 'location' in request.POST:
            location = request.POST.get('location', '').strip()
            latitude = request.POST.get('latitude', '').strip()
            longitude = request.POST.get('longitude', '').strip()
            profile_photo = request.FILES.get('profile_photo')
            id_document = request.FILES.get('id_document')
            updated = False
            if location:
                request.user.location = location
                request.user.save()
                updated = True
            else:
                messages.error(request, 'Location cannot be empty.')
            # Update latitude/longitude if provided
            fundi_profile = context['fundi_profile']
            if latitude and longitude and fundi_profile:
                try:
                    fundi_profile.latitude = float(latitude)
                    fundi_profile.longitude = float(longitude)
                    updated = True
                except ValueError:
                    messages.error(request, 'Invalid latitude/longitude values.')
            # Update profile photo and ID document if uploaded
            if fundi_profile:
                if profile_photo:
                    fundi_profile.profile_photo = profile_photo
                    updated = True
                if id_document:
                    fundi_profile.id_document = id_document
                    updated = True
                fundi_profile.save()
            if updated:
                messages.success(request, 'Profile updated successfully!')
                return redirect('profile')
    elif request.user.role == 'customer':
        # Handle location and file update for customer
        if request.method == 'POST' and 'location' in request.POST:
            location = request.POST.get('location', '').strip()
            latitude = request.POST.get('latitude', '').strip()
            longitude = request.POST.get('longitude', '').strip()
            profile_photo = request.FILES.get('profile_photo')
            id_document = request.FILES.get('id_document')
            updated = False
            if location:
                request.user.location = location
                updated = True
            else:
                messages.error(request, 'Location cannot be empty.')
            # Update latitude/longitude if provided
            if latitude and longitude:
                try:
                    request.user.latitude = float(latitude)
                    request.user.longitude = float(longitude)
                    updated = True
                except ValueError:
                    messages.error(request, 'Invalid latitude/longitude values.')
            if profile_photo:
                request.user.profile_photo = profile_photo
                updated = True
            if id_document:
                request.user.id_document = id_document
                updated = True
            if updated:
                request.user.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('profile')
    return render(request, 'users/profile.html', context)


from .forms import CustomerSignupForm

def customer_signup_view(request):
    if request.method == 'POST':
        form = CustomerSignupForm(request.POST)
        if form.is_valid():
            user = form.save(request)
            from django.contrib.auth import BACKEND_SESSION_KEY
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = CustomerSignupForm()
    return render(request, 'users/customer_signup.html', {'form': form})
