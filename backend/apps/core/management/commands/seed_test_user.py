import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = (
        "Crea o actualiza el usuario de prueba a partir de las variables de "
        "entorno TEST_USER_USERNAME / TEST_USER_PASSWORD / TEST_USER_EMAIL "
        "definidas en backend/.env. No recibe credenciales por línea de "
        "comandos para que no queden en el historial de la shell."
    )

    def handle(self, *args, **options):
        username = os.environ.get("TEST_USER_USERNAME")
        password = os.environ.get("TEST_USER_PASSWORD")
        email = os.environ.get("TEST_USER_EMAIL", "")

        if not username or not password:
            raise CommandError(
                "Definí TEST_USER_USERNAME y TEST_USER_PASSWORD en "
                "backend/.env antes de correr este comando."
            )

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=username, defaults={"email": email}
        )
        user.email = email or user.email
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save()

        accion = "creado" if created else "actualizado"
        self.stdout.write(
            self.style.SUCCESS(f"Usuario de prueba '{username}' {accion}.")
        )
