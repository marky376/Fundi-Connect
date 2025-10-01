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