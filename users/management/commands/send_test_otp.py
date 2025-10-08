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
        # Attempt to send OTP and report delivery status
        ok = send_otp_to_email(user)
        if ok:
            self.stdout.write(self.style.SUCCESS(f'Sent OTP to {email}. OTP stored in user.otp_code'))
            self.stdout.write(f'OTP: {user.otp_code}')
        else:
            self.stdout.write(self.style.ERROR(f'Failed to deliver OTP to {email}. OTP stored in user.otp_code for testing.'))
            self.stdout.write(f'OTP: {user.otp_code}')
