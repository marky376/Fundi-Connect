# FundiConnect - Job Marketplace Platform

A Django-based job marketplace platform connecting skilled workers (Fundis) with customers in Kenya.

## Features

- **User Authentication**: Role-based authentication with customers and fundis
- **Job Management**: Post, apply, and manage job requests
- **Profile System**: Detailed profiles for fundis with skills and portfolio
- **Review System**: Rating and review system for completed jobs
- **Responsive Design**: Bootstrap-based responsive frontend
- **Admin Interface**: Comprehensive Django admin for platform management

## Technology Stack

- **Backend**: Django 5.2.6
- **Frontend**: Bootstrap 5.3.0, HTMX
- **Database**: SQLite (development)
- **Authentication**: django-allauth
- **Image Processing**: Pillow
- **Forms**: django-crispy-forms with Bootstrap 5

## Quick Start

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd FundiConnect2
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install django==5.2.6 django-allauth pillow django-crispy-forms crispy-bootstrap5 django-htmx
   ```

4. Run database migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

7. Visit http://127.0.0.1:8000/ to access the application

## Project Structure

```
FundiConnect2/
├── fundiconnect/          # Main project settings
├── users/                 # User management app
│   ├── models.py         # User, FundiProfile, PortfolioImage models
│   ├── views.py          # Authentication and profile views
│   ├── forms.py          # User registration and profile forms
│   └── admin.py          # Admin configuration for users
├── jobs/                 # Job management app
│   ├── models.py         # Job, Category, JobApplication models
│   ├── views.py          # Job posting and application views
│   ├── forms.py          # Job creation forms
│   └── admin.py          # Admin configuration for jobs
├── core/                 # Core app for shared functionality
├── templates/            # HTML templates
│   ├── base/            # Base templates
│   ├── core/            # Landing page templates
│   ├── users/           # User authentication templates
│   └── jobs/            # Job-related templates
└── static/              # Static files (CSS, JS, images)
```

## User Roles

### Customers
- Post job requests
- Review applications from fundis
- Rate and review completed work
- Manage posted jobs

### Fundis (Skilled Workers)
- Create detailed profiles with skills and portfolio
- Apply for available jobs
- Communicate with customers
- Build reputation through reviews

## Key Models

### User Model
- Extended Django User with role field
- Supports both customer and fundi roles
- Email-based authentication

### Job Model
- Job postings with categories and requirements
- Status tracking (open, in_progress, completed, cancelled)
- Budget range and urgency levels

### FundiProfile Model
- Detailed profiles for skilled workers
- Skills stored as JSON
- Portfolio images and ratings

## Admin Interface

Access the admin interface at `/admin/` with superuser credentials.

Features:
- User management with role-based filtering
- Job posting management
- Application tracking
- Review monitoring
- Category management

## Development

### Adding New Features

1. Create new models in appropriate app
2. Generate and run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
3. Add admin configuration if needed
4. Create views and forms
5. Add URL patterns
6. Create templates

### Static Files

During development, static files are served automatically. For production, collect static files:

```bash
python manage.py collectstatic
```

## Security Notes

- CSRF protection enabled
- Secret key should be environment variable in production
- Debug mode should be False in production
- Use HTTPS in production

## Role switching & onboarding

This project uses a two-part role model for users:

- `roles` (list): a JSON list of roles the user has been granted (for example: `['customer']` or `['customer','fundi']`).
- `active_role` (string): the currently active role for the session (for example: `'customer'` or `'fundi'`).

Users start as `customer` by default. Becoming a Fundi is an explicit opt-in: a customer clicks "Switch to Fundi Mode" in the UI, confirms the action in a modal, and the server grants the `fundi` role and redirects the user to the Fundi onboarding flow. Customers will not be forced into Fundi onboarding automatically.

Cooldown / rate-limiting
- To avoid accidental or abusive rapid role flipping, role switches are rate-limited per-user (60 seconds). The server uses Django's cache framework to enforce a per-user cooldown and will return HTTP 429 (Too Many Requests) while the cooldown is active. In development the default locmem cache is used; in production use a shared cache backend (Redis or Memcached) so cooldowns work consistently across processes/hosts.

Security & deployment notes
- Role switching is a state-changing action and therefore uses POST with CSRF protection. The frontend confirmation modal sends a POST with the CSRF token.
- Ensure `DEBUG=False`, configure `ALLOWED_HOSTS`, and use a durable cache backend in production.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support, email admin@fundiconnect.co.ke or create an issue on GitHub.

from django.db import models
from django.conf import settings
from decimal import Decimal

# --- Escrow System Models ---

class Job(models.Model):
    """
    Represents a single job posted by a customer, bidded on by a fundi,
    and managed through the escrow payment flow.
    """
    
    # --- Job Status Choices ---
    # These are critical for managing the state of the escrow
    STATUS_PENDING = 'PENDING'    # Job posted, awaiting fundi bids and customer funding
    STATUS_FUNDED = 'FUNDED'      # Customer has paid into escrow, awaiting work
    STATUS_IN_PROGRESS = 'IN_PROGRESS' # Fundi has started the work
    STATUS_COMPLETED = 'COMPLETED'  # Customer marked as complete, fundi payout triggered
    STATUS_DISPUTED = 'DISPUTED'    # Customer or Fundi reported an issue
    STATUS_CANCELLED = 'CANCELLED'  # Job cancelled before completion

    JOB_STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_FUNDED, 'Funded'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_DISPUTED, 'Disputed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    # --- Core Job Details ---
    # NOTE: Adjust 'settings.AUTH_USER_MODEL' if you have separate Customer/Fundi models
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='posted_jobs'
    )
    fundi = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        related_name='accepted_jobs',
        null=True, 
        blank=True  # A job has no fundi until one is assigned
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255, blank=True)
    
    # --- Financial & Status Details ---
    status = models.CharField(
        max_length=20, 
        choices=JOB_STATUS_CHOICES, 
        default=STATUS_PENDING
    )
    job_value = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00 # This is the agreed-upon price
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"'{self.title}' for {self.customer.username} - {self.status}"


class Transaction(models.Model):
    """
    Logs every financial movement. This creates an auditable ledger
    for all payments in, commissions, and payouts out.
    """
    
    # --- Transaction Status Choices ---
    STATUS_PENDING = 'PENDING'
    STATUS_SUCCESSFUL = 'SUCCESSFUL'
    STATUS_FAILED = 'FAILED'
    
    TRANSACTION_STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_SUCCESSFUL, 'Successful'),
        (STATUS_FAILED, 'Failed'),
    ]
    
    # --- Transaction Type Choices ---
    TYPE_FUNDING = 'FUNDING'   # Customer paying IN to escrow
    TYPE_PAYOUT = 'PAYOUT'     # Fundi getting paid OUT of escrow
    TYPE_REFUND = 'REFUND'     # Customer being refunded
    
    TRANSACTION_TYPE_CHOICES = [
        (TYPE_FUNDING, 'Funding'),
        (TYPE_PAYOUT, 'Payout'),
        (TYPE_REFUND, 'Refund'),
    ]

    # --- Core Transaction Details ---
    job = models.ForeignKey(
        Job, 
        on_delete=models.CASCADE, 
        related_name='transactions'
    )
    
    # We store both users for easy querying, even though they are on the job
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        related_name='transactions',
        null=True
    )
    fundi = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        related_name='payouts',
        null=True,
        blank=True
    )

    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS_CHOICES, default=STATUS_PENDING)
    
    # --- Financials ---
    # This is the gross amount of the transaction
    amount = models.DecimalField(max_digits=10, decimal_places=2) 
    
    # Our commission. Only applies to FUNDING types.
    platform_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00
    )
    
    # Net amount. For PAYOUT, this is amount - platform_fee
    payout_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00
    )

    # --- Provider Details ---
    payment_provider = models.CharField(max_length=50, blank=True) # e.g., 'mpesa', 'pesapal'
    provider_reference = models.CharField(max_length=255, blank=True) # The M-Pesa code or Pesapal ID
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} for Job {self.job.id} - {self.status}"
