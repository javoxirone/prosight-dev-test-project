from dataclasses import dataclass
from typing import Any

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


@dataclass(frozen=True)
class UserSpec:
    """Predefined user configuration."""

    username: str
    password: str
    is_staff: bool = False
    is_superuser: bool = False


PREDEFINED_USERS = (
    UserSpec("admin", "admin123", is_staff=True, is_superuser=True),
    UserSpec("normal", "normal123"),
    UserSpec("limited", "limited123"),
)


class Command(BaseCommand):
    """Create or update the predefined API users."""

    help = "Create admin, normal, and limited users required by the task."

    def handle(self, *args: Any, **options: Any) -> None:
        """Execute the command."""
        user_model = get_user_model()
        for spec in PREDEFINED_USERS:
            user, _created = user_model.objects.get_or_create(username=spec.username)
            user.is_staff = spec.is_staff
            user.is_superuser = spec.is_superuser
            user.is_active = True
            user.set_password(spec.password)
            user.save(update_fields=["password", "is_staff", "is_superuser", "is_active"])
            self.stdout.write(self.style.SUCCESS(f"Ensured user '{spec.username}'"))
