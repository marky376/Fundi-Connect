

from django.contrib.auth.decorators import login_required
from .models import Job, JobApplication, Category, JobImage
from .pesapal_api import initiate_pesapal_payment, verify_pesapal_payment
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django import forms

# Form for updating job status
class JobStatusUpdateForm(forms.Form):
    status = forms.ChoiceField(choices=Job.STATUS_CHOICES, label="New Status")


@login_required
def job_update_status(request, job_id):
    job = get_object_or_404(Job, id=job_id, customer=request.user)
    if request.method == 'POST':
        form = JobStatusUpdateForm(request.POST)
        if form.is_valid():
            new_status = form.cleaned_data['status']
            job.status = new_status
            job.save()
            messages.success(request, f"Job status updated to '{job.get_status_display()}'.")
            return redirect('jobs:job_detail_jobs', job_id=job.id)
    else:
        form = JobStatusUpdateForm(initial={'status': job.status})
    return render(request, 'jobs/job_update_status.html', {'job': job, 'form': form, 'status_choices': Job.STATUS_CHOICES})

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

@login_required
@require_POST
def accept_application(request, job_id, application_id):
    job = get_object_or_404(Job, id=job_id)
    application = get_object_or_404(JobApplication, id=application_id, job=job)
    if request.user != job.customer:
        messages.error(request, 'You are not authorized to accept applications for this job.')
        return redirect('jobs:job_detail_jobs', job_id=job_id)
    if application.status != 'pending':
        messages.info(request, 'This application has already been processed.')
        return redirect('jobs:job_detail_jobs', job_id=job_id)
    application.status = 'accepted'
    application.save()
    # Fundi payment logic
    from .models import Payment
    fundi_fee = 100 if job.budget_min and job.budget_min > 500 else 50 if job.budget_max and job.budget_max <= 500 else 0
    if fundi_fee > 0:
        Payment.objects.create(
            amount=fundi_fee,
            commission=0,
            fundi_amount=0,
            status='pending',
            customer=request.user,
            fundi=application.fundi,
            job=job
        )
    messages.success(request, f'Accepted {application.fundi.get_full_name() or application.fundi.email} for this job. Fundi fee: KES {fundi_fee}.')
    return redirect('jobs:job_detail_jobs', job_id=job_id)

# All imports at the top
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from users.models import User
from django.db.models import Q

@login_required
def job_messages(request, job_id, fundi_id):
    from .models import Message
    job = get_object_or_404(Job, id=job_id)
    fundi = get_object_or_404(User, id=fundi_id, role='fundi')
    # Only allow if fundi is accepted for this job
    accepted = JobApplication.objects.filter(job=job, fundi=fundi, status='accepted').exists()
    if not accepted or (request.user != job.customer and request.user != fundi):
        messages.error(request, 'You are not authorized to view this conversation.')
        return redirect('jobs:job_detail_jobs', job_id=job_id)

@login_required
def payment_initiate(request, job_id, fundi_id):
    job = get_object_or_404(Job, id=job_id)
    fundi = get_object_or_404(User, id=fundi_id, role='fundi')
    amount = 100 if job.budget_min and job.budget_min >= 500 else 50 if job.budget_max and job.budget_max < 500 else 0
    if request.method == 'POST' and amount > 0:
        phone_number = request.POST.get('phone_number')
        description = f'Fundi fee for job {job.title}'
        callback_url = request.build_absolute_uri(reverse('jobs:pesapal_callback'))
        result = initiate_pesapal_payment(amount, description, phone_number, callback_url)
        # Redirect to Pesapal payment page (replace with actual redirect_url)
        return redirect(result.get('redirect_url', '/'))
    return redirect('jobs:my_applications')

@csrf_exempt
def pesapal_callback(request):
    # This endpoint will be called by Pesapal after payment
    payment_id = request.GET.get('payment_id')
    job_id = request.GET.get('job_id')
    fundi_id = request.GET.get('fundi_id')
    if payment_id and job_id and fundi_id:
        result = verify_pesapal_payment(payment_id)
        if result.get('status') == 'completed':
            job = get_object_or_404(Job, id=job_id)
            fundi = get_object_or_404(User, id=fundi_id, role='fundi')
            payment = job.payments.filter(fundi=fundi).order_by('-created_at').first()
            if payment:
                payment.status = 'completed'
                payment.save()
    return redirect('jobs:my_applications')
    # Fundi payment check
    fundi_payment = None
    fundi_payment_completed = False
    if request.user == fundi:
        fundi_payment = job.payments.filter(fundi=fundi, status__in=['pending', 'completed']).order_by('-created_at').first()
        fundi_payment_completed = fundi_payment and fundi_payment.status == 'completed'

    # Prevent fundi from messaging customer after acceptance
    can_chat = True
    accepted = JobApplication.objects.filter(job=job, fundi=fundi, status='accepted').exists()
    if request.user == fundi and accepted:
        can_chat = False
    elif request.user == fundi and fundi_payment and not fundi_payment_completed:
        can_chat = False

    if request.method == 'POST' and can_chat and (request.user == job.customer or request.user == fundi):
        content = request.POST.get('content', '').strip()
        if content:
            recipient = fundi if request.user == job.customer else job.customer
            Message.objects.create(job=job, sender=request.user, recipient=recipient, content=content)
            messages.success(request, 'Message sent.')
            return redirect('jobs:job_messages', job_id=job.id, fundi_id=fundi.id)

    messages_qs = Message.objects.filter(job=job, sender__in=[job.customer, fundi], recipient__in=[job.customer, fundi]).order_by('created_at')
    return render(request, 'jobs/job_messages.html', {
        'job': job,
        'fundi': fundi,
        'messages': messages_qs,
        'fundi_payment': fundi_payment,
        'fundi_payment_completed': fundi_payment_completed,
        'can_chat': can_chat,
    })
from .models import Job, JobApplication, Category, JobImage
from .forms import JobForm, JobApplicationForm

# Fundi applies for a job
@login_required
def apply(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if request.user.active_role != 'fundi':
        messages.error(request, 'Only fundis can apply for jobs.')
        return redirect('jobs:job_detail_jobs', job_id=job_id)
    # Enforce phone verification for job application
    if not getattr(request.user, 'phone_verified', True):
        messages.warning(request, 'Please verify your phone number to apply for jobs.')
        return redirect('verify_otp')
    if not request.user.is_verified:
        # Show countdown and redirect via template
        return render(request, 'jobs/verify_redirect.html', {'redirect_url': '/contact/', 'seconds': 5})
    # Check if already applied
    existing = JobApplication.objects.filter(job=job, fundi=request.user).first()
    if existing:
        messages.info(request, 'You have already applied for this job.')
        return redirect('jobs:job_detail_jobs', job_id=job_id)
    # Create application
    JobApplication.objects.create(job=job, fundi=request.user, status='pending')
    messages.success(request, 'Application submitted!')
    return redirect('jobs:job_detail_jobs', job_id=job_id)

@login_required
def my_applications(request):
    # Only for fundis
    if not hasattr(request.user, 'active_role') or request.user.active_role != 'fundi':
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('/')
    applications = JobApplication.objects.filter(fundi=request.user).select_related('job').order_by('-created_at')
    # Paginate applications
    paginator = Paginator(applications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'jobs/my_applications.html', {'page_obj': page_obj})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from users.models import User

@login_required
def nudge_fundis(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if request.user.active_role != 'customer' or job.customer != request.user:
        messages.error(request, 'You are not authorized to nudge fundis for this job.')
        return redirect('job_detail_jobs', job_id=job_id)
    # Find fundis matching job location and category
    fundis = User.objects.filter(active_role='fundi', location__icontains=job.location)
    notified_count = 0
    for fundi in fundis:
        # For demo: use Django messages, but can be replaced with email/in-app notification
        # Optionally filter by skills/category
        notified_count += 1
    messages.success(request, f'Nudged {notified_count} fundis near {job.location}.')
    return redirect('job_detail_jobs', job_id=job_id)
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
            user_has_applied = job.applications.filter(fundi=request.user, active_role='fundi').exists()
    
    applicants = []
    payment_completed = False
    if request.user.is_authenticated and request.user.role == 'customer' and job.customer == request.user:
        # Check if payment for this job is completed
        payment_completed = job.payments.filter(status='completed').exists()
        if payment_completed:
            applicants = job.applications.select_related('fundi').all()

    context = {
        'job': job,
        'user_has_applied': user_has_applied,
        'applicants': applicants,
        'payment_completed': payment_completed,
    }
    return render(request, 'jobs/job_detail.html', context)


@login_required
def job_create(request):
    """Create a new job posting"""
    if request.user.active_role != 'customer':
        messages.error(request, 'Only customers can post jobs.')
        return redirect('dashboard')
    if not request.user.is_verified:
        # Show countdown and redirect via template
        return render(request, 'jobs/verify_redirect.html', {'redirect_url': '/contact/', 'seconds': 5})
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
    
    if request.user.active_role != 'fundi':
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
            # Create notification for customer
            from users.models import Notification
            Notification.objects.create(
                user=job.customer,
                message=f"{request.user.get_full_name() or request.user.email} applied for your job '{job.title}'",
                url=f"/jobs/{job.id}/"
            )
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
    if request.user.active_role != 'fundi':
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
    if request.user.active_role != 'customer':
        messages.error(request, 'Only customers can view posted jobs.')
        return redirect('dashboard')
    
    jobs = request.user.posted_jobs.all().order_by('-created_at')
    paginator = Paginator(jobs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'jobs/my_jobs.html', {'page_obj': page_obj})
