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