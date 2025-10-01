from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):
    help = 'Repair user roles: ensure active_role is included in roles, or reset to customer.'

    def handle(self, *args, **options):
        users = User.objects.all()
        fixed = 0
        for u in users:
            roles = set(u.roles or [])
            if u.active_role not in roles:
                # If active_role is missing, prefer keeping a fundi role only if user has fundi-related data
                if 'customer' not in roles:
                    roles.add('customer')
                # Reset active role to customer to avoid accidental onboarding redirects
                old = u.active_role
                u.roles = list(roles)
                u.active_role = 'customer'
                u.save()
                self.stdout.write(f'Fixed {u.email}: active_role {old} -> customer; roles={u.roles}')
                fixed += 1

        self.stdout.write(self.style.SUCCESS(f'Done. Fixed {fixed} users.'))
