from django.http import JsonResponse
# API endpoint for live fundi locations
def fundi_locations_api(request):
    skill_filter = request.GET.get('skill')
    available_filter = request.GET.get('available')
    fundis = User.objects.filter(active_role='fundi', fundi_profile__latitude__isnull=False, fundi_profile__longitude__isnull=False)
    if skill_filter:
        fundis = fundis.filter(fundi_profile__skills__icontains=skill_filter)
    if available_filter == 'true':
        fundis = fundis.filter(fundi_profile__availability=True)
    data = []
    for fundi in fundis:
        fp = fundi.fundi_profile
        data.append({
            'id': fundi.id,
            'name': f'{fundi.first_name} {fundi.last_name}',
            'latitude': float(fp.latitude),
            'longitude': float(fp.longitude),
            'skills': fp.skills,
            'location': fundi.location,
            'available': fp.availability,
        })
    return JsonResponse({'fundis': data})
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from jobs.models import Job, Category
from users.models import User
from django.core.paginator import Paginator


def dashboard(request):
    """Main dashboard view - shows different content based on user role"""
    if not request.user.is_authenticated:
        # Show public landing page for anonymous users
        jobs = Job.objects.filter(status='open').order_by('-created_at')[:6]
        categories = Category.objects.all()[:8]
        return render(request, 'core/landing.html', {
            'jobs': jobs,
            'categories': categories
        })
    
    # Enforce email verification for all logged-in users
    if hasattr(request.user, 'is_verified') and not request.user.is_verified:
        messages.warning(request, 'Please verify your email to access all features.')
        return redirect('verify_otp')

    # Check if fundi needs to complete onboarding - only if the user actually has the fundi role
    if ('fundi' in getattr(request.user, 'roles', []) and
        request.user.active_role == 'fundi' and 
        not request.user.onboarding_complete):
        return redirect('fundi_onboarding')

    # Show role-specific dashboard
    if request.user.active_role == 'customer':
        # Customer dashboard - show their posted jobs and available fundis
        user_jobs = request.user.posted_jobs.all().order_by('-created_at')[:5]
        available_jobs = Job.objects.filter(status='open').order_by('-created_at')[:6]
        fundis = User.objects.filter(active_role='fundi', location__isnull=False).exclude(location='').select_related('fundi_profile')
        from users.models import Notification
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
        return render(request, 'core/customer_dashboard.html', {
            'user_jobs': user_jobs,
            'available_jobs': available_jobs,
            'fundis': fundis,
            'notifications': notifications
        })

    elif request.user.active_role == 'fundi':
        # Fundi dashboard - show available jobs filtered by fundi skills/category
        fundi_skills = request.user.fundi_profile.skills if hasattr(request.user, 'fundi_profile') else []
        available_jobs = Job.objects.filter(
            status='open',
            category__name__in=fundi_skills
        ).exclude(
            applications__fundi=request.user
        ).order_by('-created_at')[:6]

        my_applications = request.user.job_applications.all().order_by('-created_at')[:5]
        assigned_jobs = request.user.assigned_jobs.filter(
            status__in=['in_progress', 'completed']
        ).order_by('-updated_at')[:5]

        return render(request, 'core/fundi_dashboard.html', {
            'available_jobs': available_jobs,
            'my_applications': my_applications,
            'assigned_jobs': assigned_jobs
        })

    # Default dashboard for other roles
    return render(request, 'core/dashboard.html')


def job_list(request):
    """List all available jobs with filtering and search"""
    jobs = Job.objects.filter(status='open')
    categories = Category.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    # Category filter
    category_filter = request.GET.get('category', '')
    if category_filter:
        jobs = jobs.filter(category__name=category_filter)
    
    # Location filter
    location_filter = request.GET.get('location', '')
    if location_filter:
        jobs = jobs.filter(location__icontains=location_filter)
    
    # Urgency filter
    urgency_filter = request.GET.get('urgency', '')
    if urgency_filter:
        jobs = jobs.filter(urgency=urgency_filter)
    
    # Pagination
    paginator = Paginator(jobs, 12)  # Show 12 jobs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'location_filter': location_filter,
        'urgency_filter': urgency_filter,
    }
    
    return render(request, 'core/job_list.html', context)


def job_detail(request, job_id):
    """Show detailed view of a specific job"""
    job = get_object_or_404(Job, id=job_id)
    user_has_applied = False
    
    if request.user.is_authenticated and request.user.active_role == 'fundi':
        user_has_applied = job.applications.filter(fundi=request.user).exists()
    
    context = {
        'job': job,
        'user_has_applied': user_has_applied,
    }
    
    return render(request, 'core/job_detail.html', context)


def about(request):
    """About page"""
    return render(request, 'core/about.html')


def contact(request):
    """Contact page"""
    return render(request, 'core/contact.html')
