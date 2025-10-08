
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.views.decorators.http import require_POST, require_GET
import random
from django.core.mail import send_mail
from django.conf import settings
from .gmail_oauth import send_via_gmail_oauth2
from django.core.cache import cache
from django.http import HttpResponse

# Management view to enable fundi role
@login_required
@require_POST
def enable_fundi_role_view(request):
    user = request.user
    if 'fundi' not in user.roles:
        user.roles.append('fundi')
        user.active_role = 'fundi'
        user.save()
        request.session['active_role'] = 'fundi'
        messages.success(request, "Fundi role enabled! You can now switch between fundi and customer modes.")
    else:
        user.active_role = 'fundi'
        user.save()
        request.session['active_role'] = 'fundi'
        messages.info(request, "Switched to fundi mode.")
    return redirect('dashboard')

@login_required
@require_GET
def enable_customer_role_view(request):
    user = request.user
    if 'customer' not in user.roles:
        user.roles.append('customer')
        user.active_role = 'customer'
        user.save()
        request.session['active_role'] = 'customer'
        messages.success(request, "Customer role enabled! You can now post jobs and interact as a customer.")
    else:
        user.active_role = 'customer'
        user.save()
        request.session['active_role'] = 'customer'
        messages.info(request, "Switched to customer mode.")
    return redirect('dashboard')

@login_required
@require_POST
def switch_role_view(request):
    user = request.user
    # role should come from POST payload now
    next_role = request.POST.get('role')
    # Rate-limit: prevent rapid role flipping (60s per user)
    cooldown_key = f'user_role_switch_cooldown:{user.pk}'
    if cache.get(cooldown_key):
        return HttpResponse('Role switch rate limit exceeded. Try again later.', status=429)
    if not next_role:
        messages.error(request, "No role specified for switching.")
        return redirect('dashboard')

    # Switching to Fundi: if user already has the fundi role, just switch; otherwise
    # treat this as an explicit customer request to become a fundi: add the role
    # and redirect to the onboarding flow.
    if next_role == 'fundi':
        if user.has_role('fundi'):
            user.switch_role('fundi')
            request.session['active_role'] = 'fundi'
            messages.success(request, "Switched to Fundi mode.")
            # If onboarding incomplete, send to onboarding
            cache.set(cooldown_key, True, 60)
            if not user.onboarding_complete:
                return redirect('fundi_onboarding')
            return redirect('fundi_dashboard')
        else:
            # User is explicitly requesting to become a fundi: add role and start onboarding
            user.roles = list(set(user.roles + ['fundi']))
            user.active_role = 'fundi'
            user.save()
            request.session['active_role'] = 'fundi'
            cache.set(cooldown_key, True, 60)
            messages.success(request, "Fundi role enabled — please complete your fundi onboarding.")
            return redirect('fundi_onboarding')

    # Switching to Customer: only allow if user already has the customer role
    if next_role == 'customer':
        if user.has_role('customer'):
            user.switch_role('customer')
            request.session['active_role'] = 'customer'
            cache.set(cooldown_key, True, 60)
            messages.success(request, "Switched to Customer mode.")
            return redirect('customer_dashboard')
        else:
            messages.error(request, "You don't have the Customer role.")
            return redirect('dashboard')

    messages.error(request, "Role switch failed or not allowed.")
    return redirect('dashboard')

# OTP verification view
@login_required
@csrf_exempt
def verify_otp_view(request):
    user = request.user
    if user.is_verified:
        return redirect('dashboard')
    if request.method == 'POST':
        otp = request.POST.get('otp', '').strip()
        if otp and user.otp_code == otp:
            user.is_verified = True
            user.otp_code = ''
            user.save()
            messages.success(request, 'Email verified successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
    return render(request, 'users/verify_otp.html')

# OTP generation and sending via Gmail SMTP
def send_otp_to_email(user):
    otp = str(random.randint(100000, 999999))
    user.otp_code = otp
    user.otp_created_at = timezone.now()
    user.save()
    subject = "Your FundiConnect OTP"
    message = f"Your FundiConnect OTP is: {otp}"
    # Use DEFAULT_FROM_EMAIL from settings (falls back to EMAIL_HOST_USER)
    # Default from address
    default_from = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', 'no-reply@example.com')
    from_email = default_from
    recipient_list = [user.email]

    # If Gmail OAuth2 settings are provided, attempt to use XOAUTH2 SMTP
    if getattr(settings, 'GMAIL_OAUTH2_CLIENT_ID', '') and getattr(settings, 'GMAIL_OAUTH2_REFRESH_TOKEN', ''):
        # When using Gmail OAuth2, ensure the SMTP 'from' matches the authenticated user
        # to avoid XOAUTH2 rejection due to from/account mismatch.
        from_email = getattr(settings, 'EMAIL_HOST_USER', from_email)
        try:
            send_via_gmail_oauth2(subject, message, from_email, recipient_list)
            print(f"OTP sent to {user.email} via Gmail OAuth2: {otp}")
            return True
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Gmail OAuth2 send failed, falling back to send_mail: {e}")

    try:
        send_mail(subject, message, from_email, recipient_list)
        print(f"OTP sent to {user.email}: {otp}")
        return True
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Failed to send OTP: {e}")
        return False

def request_otp_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        send_otp_to_email(request.user)
        messages.success(request, 'OTP sent to your email address.')
        return redirect('verify_otp')
    return render(request, 'users/request_otp.html')
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

def customer_login_view(request):
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
        user = self.request.user
        # Ensure both roles are present for fundi onboarding
        user.roles = list(set(user.roles + ['fundi', 'customer']))
        user.active_role = 'fundi'
        user.save()
        return response


@login_required
def fundi_onboarding(request):
    # Only allow users who already have the fundi role to access onboarding.
    if 'fundi' not in getattr(request.user, 'roles', []):
        messages.error(request, "You don't have the Fundi role. Please enable the Fundi role first.")
        return redirect('dashboard')
    if request.user.active_role != 'fundi':
        messages.info(request, 'Please switch to Fundi mode to continue onboarding.')
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
    if request.user.active_role == 'fundi':
        try:
            context['fundi_profile'] = request.user.fundi_profile
            context['portfolio_images'] = request.user.fundi_profile.portfolio_images.all()
        except FundiProfile.DoesNotExist:
            context['fundi_profile'] = None
        # Handle location, email, and file update for fundi
        if request.method == 'POST' and 'location' in request.POST:
            email = request.POST.get('email', '').strip()
            location = request.POST.get('location', '').strip()
            latitude = request.POST.get('latitude', '').strip()
            longitude = request.POST.get('longitude', '').strip()
            profile_photo = request.FILES.get('profile_photo')
            id_document = request.FILES.get('id_document')
            updated = False
            if email:
                # Check for unique email
                if User.objects.filter(email=email).exclude(pk=request.user.pk).exists():
                    messages.error(request, 'This email is already in use by another account.')
                else:
                    request.user.email = email
                    updated = True
            else:
                messages.error(request, 'Email cannot be empty.')
            if location:
                request.user.location = location
                updated = True
            else:
                messages.error(request, 'Location cannot be empty.')
            if updated:
                request.user.save()
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
    elif request.user.active_role == 'customer':
        # Handle location, email, and file update for customer
        if request.method == 'POST' and 'location' in request.POST:
            email = request.POST.get('email', '').strip()
            location = request.POST.get('location', '').strip()
            latitude = request.POST.get('latitude', '').strip()
            longitude = request.POST.get('longitude', '').strip()
            profile_photo = request.FILES.get('profile_photo')
            id_document = request.FILES.get('id_document')
            updated = False
            if email:
                # Check for unique email
                if User.objects.filter(email=email).exclude(pk=request.user.pk).exists():
                    messages.error(request, 'This email is already in use by another account.')
                else:
                    request.user.email = email
                    updated = True
            else:
                messages.error(request, 'Email cannot be empty.')
            if location:
                request.user.location = location
                updated = True
            else:
                messages.error(request, 'Location cannot be empty.')
            if updated:
                request.user.save()
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
            # Defensive: ensure the saved user is in customer mode
            if 'customer' not in user.roles:
                user.roles = list(set(user.roles + ['customer']))
            user.active_role = 'customer'
            user.save()
            from django.contrib.auth import BACKEND_SESSION_KEY
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = CustomerSignupForm()
    return render(request, 'users/customer_signup.html', {'form': form})
