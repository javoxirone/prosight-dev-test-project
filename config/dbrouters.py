from typing import Any, ClassVar

from django.conf import settings
from django.db.models import Model


class LocusDatabaseRouter:
    """Route locus models to the external RNACentral database alias."""

    route_app_labels: ClassVar[frozenset[str]] = frozenset({"locus"})

    def db_for_read(self, model: type[Model], **hints: Any) -> str | None:
        """Return the database alias for locus model reads."""
        if model._meta.app_label in self.route_app_labels:
            return str(settings.LOCUS_DATABASE_ALIAS)
        return None

    def db_for_write(self, model: type[Model], **hints: Any) -> str | None:
        """Return the database alias for locus model writes.

        Writes are not used by the API, but routing keeps tests and admin scripts explicit.
        """
        if model._meta.app_label in self.route_app_labels:
            return str(settings.LOCUS_DATABASE_ALIAS)
        return None

    def allow_relation(self, obj1: Model, obj2: Model, **hints: Any) -> bool | None:
        """Allow relations inside the locus app."""
        if {obj1._meta.app_label, obj2._meta.app_label} <= self.route_app_labels:
            return True
        return None

    def allow_migrate(
        self,
        db: str,
        app_label: str,
        model_name: str | None = None,
        **hints: Any,
    ) -> bool | None:
        """Prevent unmanaged external tables from being migrated."""
        if app_label in self.route_app_labels:
            return False
        if db == settings.LOCUS_DATABASE_ALIAS:
            return False
        return None
