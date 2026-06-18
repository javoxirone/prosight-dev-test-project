from collections.abc import Mapping
from typing import Any

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User as DjangoUser
from django.db.models import QuerySet
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.locus.models import RncLocus
from apps.locus.selectors import LocusSelector

SIDELOADING_PARAM = "sideloading"
ALLOWED_SIDELOADS = {"locusMembers"}


class LocusAccessService:
    """Evaluate user permissions and access scopes for locus data."""

    @staticmethod
    def is_admin_user(user: DjangoUser | AnonymousUser) -> bool:
        """Return whether a user has full locus access."""
        return bool(
            user.is_authenticated
            and (user.is_superuser or user.is_staff or user.username == "admin")
        )

    @staticmethod
    def is_limited_user(user: DjangoUser | AnonymousUser) -> bool:
        """Return whether a user is subject to region restrictions."""
        limited_usernames = set(settings.LIMITED_LOCUS_USERNAMES)
        return bool(user.is_authenticated and user.username in limited_usernames)

    @classmethod
    def get_allowed_region_ids(cls, user: DjangoUser | AnonymousUser) -> tuple[int, ...] | None:
        """Return allowed region identifiers, or ``None`` when unrestricted."""
        if cls.is_limited_user(user):
            return tuple(settings.LIMITED_LOCUS_REGION_IDS)
        return None

    @staticmethod
    def parse_sideloading(value: str | None) -> set[str]:
        """Parse and validate the sideloading query parameter."""
        if not value:
            return set()

        requested = {item.strip() for item in value.split(",") if item.strip()}
        unsupported = requested - ALLOWED_SIDELOADS
        if unsupported:
            allowed = ", ".join(sorted(ALLOWED_SIDELOADS))
            invalid = ", ".join(sorted(unsupported))
            raise ValidationError(
                {SIDELOADING_PARAM: f"Unsupported sideloading '{invalid}'. Allowed: {allowed}."}
            )
        return requested

    @classmethod
    def ensure_sideloading_allowed(
        cls,
        user: DjangoUser | AnonymousUser,
        value: str | None,
    ) -> bool:
        """Validate sideloading and return whether locus members should be included."""
        requested = cls.parse_sideloading(value)
        include_members = "locusMembers" in requested
        if include_members and not cls.is_admin_user(user):
            raise PermissionDenied("You do not have permission to use locus sideloading.")
        return include_members


class LocusQueryService:
    """Application service for listing loci."""

    @classmethod
    def list_loci(
        cls,
        user: DjangoUser | AnonymousUser,
        params: Mapping[str, Any],
    ) -> QuerySet[RncLocus]:
        """Return an optimized queryset for the current request and user."""
        include_members = LocusAccessService.ensure_sideloading_allowed(
            user,
            params.get(SIDELOADING_PARAM),
        )

        queryset = LocusSelector.base_queryset()
        allowed_region_ids = LocusAccessService.get_allowed_region_ids(user)
        if allowed_region_ids is not None:
            queryset = LocusSelector.apply_region_scope(queryset, allowed_region_ids)

        queryset = LocusSelector.apply_filters(queryset, params)
        queryset = LocusSelector.apply_ordering(queryset, params.get("ordering"))
        return LocusSelector.apply_eager_loading(queryset, include_members)
