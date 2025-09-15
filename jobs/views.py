from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Job, JobApplication, Category, JobImage
from .forms import JobForm, JobApplicationForm


def job_list(request):
    """List all jobs with filtering"""
    jobs = Job.objects.filter(status='open').order_by('-created_at')
    categories = Category.objects.all()
    
    # Search and filters
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    location_filter = request.GET.get('location', '')
    urgency_filter = request.GET.get('urgency', '')
    
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if category_filter:
        jobs = jobs.filter(category__name=category_filter)
    
    if location_filter:
        jobs = jobs.filter(location__icontains=location_filter)
        
    if urgency_filter:
        jobs = jobs.filter(urgency=urgency_filter)
    
    # Pagination
    paginator = Paginator(jobs, 12)
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
    
    return render(request, 'jobs/job_list.html', context)


def job_detail(request, job_id):
    """Show job details"""
    job = get_object_or_404(Job, id=job_id)
    user_has_applied = False
    
    if request.user.is_authenticated and request.user.role == 'fundi':
        user_has_applied = job.applications.filter(fundi=request.user).exists()
    
    context = {
        'job': job,
        'user_has_applied': user_has_applied,
    }
    
    return render(request, 'jobs/job_detail.html', context)


@login_required
def job_create(request):
    """Create a new job posting"""
    if request.user.role != 'customer':
        messages.error(request, 'Only customers can post jobs.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES)
        if form.is_valid():
            job = form.save(commit=False)
            job.customer = request.user
            job.save()
            
            # Handle multiple image uploads
            images = request.FILES.getlist('images')
            for image in images:
                JobImage.objects.create(job=job, image=image)
            
            messages.success(request, 'Job posted successfully!')
            return redirect('job_detail_jobs', job_id=job.id)
    else:
        form = JobForm()
    
    return render(request, 'jobs/job_create.html', {'form': form})


@login_required
def job_apply(request, job_id):
    """Apply for a job"""
    job = get_object_or_404(Job, id=job_id)
    
    if request.user.role != 'fundi':
        messages.error(request, 'Only Fundis can apply for jobs.')
        return redirect('job_detail_jobs', job_id=job_id)
    
    if not request.user.onboarding_complete:
        messages.error(request, 'Please complete your profile first.')
        return redirect('fundi_onboarding')
    
    # Check if already applied
    if job.applications.filter(fundi=request.user).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('job_detail_jobs', job_id=job_id)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.fundi = request.user
            application.save()
            
            messages.success(request, 'Application submitted successfully!')
            return redirect('job_detail_jobs', job_id=job_id)
    else:
        form = JobApplicationForm()
    
    return render(request, 'jobs/job_apply.html', {'form': form, 'job': job})


@login_required
def job_edit(request, job_id):
    """Edit a job posting"""
    job = get_object_or_404(Job, id=job_id, customer=request.user)
    
    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully!')
            return redirect('job_detail_jobs', job_id=job.id)
    else:
        form = JobForm(instance=job)
    
    return render(request, 'jobs/job_edit.html', {'form': form, 'job': job})


@login_required
def job_delete(request, job_id):
    """Delete a job posting"""
    job = get_object_or_404(Job, id=job_id, customer=request.user)
    
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job deleted successfully!')
        return redirect('my_jobs')
    
    return render(request, 'jobs/job_delete.html', {'job': job})


@login_required
def my_applications(request):
    """Show user's job applications"""
    if request.user.role != 'fundi':
        messages.error(request, 'Only Fundis can view applications.')
        return redirect('dashboard')
    
    applications = request.user.job_applications.all().order_by('-created_at')
    paginator = Paginator(applications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'jobs/my_applications.html', {'page_obj': page_obj})


@login_required
def my_jobs(request):
    """Show user's posted jobs"""
    if request.user.role != 'customer':
        messages.error(request, 'Only customers can view posted jobs.')
        return redirect('dashboard')
    
    jobs = request.user.posted_jobs.all().order_by('-created_at')
    paginator = Paginator(jobs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'jobs/my_jobs.html', {'page_obj': page_obj})
