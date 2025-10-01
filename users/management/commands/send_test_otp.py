from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
from users.views import send_otp_to_email


class Command(BaseCommand):
    help = "Send a test OTP to an email address (creates user if necessary)."

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email address to send OTP to')

    def handle(self, *args, **options):
        email = options['email']
        User = get_user_model()
        user, created = User.objects.get_or_create(email=email, defaults={'username': email.split('@')[0]})
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created test user: {email}'))
        # Use console backend if DEBUG is on or EMAIL_BACKEND overridden in env
        send_otp_to_email(user)
        self.stdout.write(self.style.SUCCESS(f'Sent OTP to {email}. OTP stored in user.otp_code'))
        self.stdout.write(f'OTP: {user.otp_code}')
