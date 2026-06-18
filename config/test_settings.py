import os

from .settings import *  # noqa: F403

LOCUS_DATABASE_ALIAS = "default"
DATABASE_ROUTERS: list[str] = []
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

if os.getenv("USE_SQLITE_FOR_TESTS", "").lower() in {"1", "true", "yes"}:
    DATABASES["default"] = {  # noqa: F405
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
