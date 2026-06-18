import os
from datetime import timedelta
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name: str, default: bool = False) -> bool:
    """Return a boolean environment variable value."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    """Return a comma-separated environment variable as a list."""
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]


def env_int_tuple(name: str, default: str = "") -> tuple[int, ...]:
    """Return a comma-separated integer environment variable as a tuple."""
    return tuple(int(item) for item in env_list(name, default))


SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-development-key")
DEBUG = env_bool("DEBUG", default=True)
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0,testserver")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_filters",
    "rest_framework",
    "drf_spectacular",
    "apps.locus",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES: list[dict[str, Any]] = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES: dict[str, dict[str, Any]] = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "prosight"),
        "USER": os.getenv("POSTGRES_USER", "prosight"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "prosight"),
        "HOST": os.getenv("POSTGRES_HOST", "localhost"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
        "CONN_MAX_AGE": int(os.getenv("POSTGRES_CONN_MAX_AGE", "60")),
    },
    "rnacentral": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("LOCUS_DB_NAME", "pfmegrnargs"),
        "USER": os.getenv("LOCUS_DB_USER", "reader"),
        "PASSWORD": os.getenv("LOCUS_DB_PASSWORD", "NWDMCE5xdipIjRrp"),
        "HOST": os.getenv("LOCUS_DB_HOST", "hh-pgsql-public.ebi.ac.uk"),
        "PORT": os.getenv("LOCUS_DB_PORT", "5432"),
        "CONN_MAX_AGE": int(os.getenv("LOCUS_DB_CONN_MAX_AGE", "60")),
        "OPTIONS": {
            "options": os.getenv("LOCUS_DB_OPTIONS", "-c search_path=rnacen,public"),
        },
    },
}

LOCUS_DATABASE_ALIAS = os.getenv("LOCUS_DATABASE_ALIAS", "rnacentral")
DATABASE_ROUTERS = ["config.dbrouters.LocusDatabaseRouter"]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("JWT_ACCESS_MINUTES", "60"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("JWT_REFRESH_DAYS", "7"))),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Prosight Locus API",
    "DESCRIPTION": "Read-only REST API for RNACentral locus data.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SECURITY": [{"jwtAuth": []}],
}

LIMITED_LOCUS_REGION_IDS = env_int_tuple(
    "LIMITED_LOCUS_REGION_IDS",
    "86118093,86696489,88186467",
)
LIMITED_LOCUS_USERNAMES = tuple(env_list("LIMITED_LOCUS_USERNAMES", "limited"))
