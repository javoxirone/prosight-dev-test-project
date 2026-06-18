from django.apps import AppConfig


class LocusConfig(AppConfig):
    """Configure the locus application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.locus"
    label = "locus"
