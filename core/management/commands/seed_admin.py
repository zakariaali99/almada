from django.core.management.base import BaseCommand

from core.models import User


class Command(BaseCommand):
    help = "Create a default admin user if one does not already exist."

    def add_arguments(self, parser):
        parser.add_argument("--username", default="admin")
        parser.add_argument("--password", default="admin123456")

    def handle(self, *args, **options):
        username = options["username"]
        password = options["password"]
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING("Admin user already exists."))
            return
        User.objects.create_superuser(username=username, password=password)
        self.stdout.write(self.style.SUCCESS(f"Created superuser: {username}"))
