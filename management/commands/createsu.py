import os
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Creates a superuser."

    def handle(self, *args, **options):
        username = "admin"
        nickname = "admin"
        if not User.objects.filter(nickname=nickname).exists():
            email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
            password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
            if password is None:
                raise ValueError("Password not found")
            if email is None:
                raise ValueError("Email not found")

            User.objects.create_superuser(
                username=username,
                email=email, 
                password=password,
                nickname=nickname
            )
            print("Superuser has been created.")
        else:
            print("Superuser exists")