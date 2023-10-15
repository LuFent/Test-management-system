from django.core.management.base import BaseCommand, CommandError
from users.models import AppUser


class Command(BaseCommand):
    help = "Add admin"

    def add_arguments(self, parser):
        parser.add_argument("--email", type=str)
        parser.add_argument("--name", type=str)
        parser.add_argument("--password", type=str)

    def handle(self, *args, **options):
        email = options.get("email")
        if not email:
            self.stdout.write(self.style.ERROR("Provide email"))
            return

        name = options.get("name")
        if not name:
            self.stdout.write(self.style.ERROR("Provide name"))
            return

        password = options.get("password")
        if not password:
            self.stdout.write(self.style.ERROR("Provide password"))
            return

        try:
            AppUser.objects.create_superuser(email, password, name)
        except Exception as e:
            self.style.ERROR(e)

        self.style.SUCCESS("Created")
