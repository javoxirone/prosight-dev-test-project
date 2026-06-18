from collections.abc import Iterable
from typing import cast

from django.conf import settings
from django.db.models import Prefetch, QuerySet
from rest_framework.exceptions import ValidationError

from apps.locus.filters import LocusFilter
from apps.locus.models import RncLocus, RncLocusMember

ORDERING_FIELD_MAP: dict[str, str] = {
    "id": "id",
    "assemblyId": "assembly_id",
    "locusName": "locus_name",
    "publicLocusName": "public_locus_name",
    "chromosome": "chromosome",
    "strand": "strand",
    "locusStart": "locus_start",
    "locusStop": "locus_stop",
    "memberCount": "member_count",
}


class LocusSelector:
    """Build optimized ORM querysets for the locus endpoint."""

    @staticmethod
    def base_queryset() -> QuerySet[RncLocus]:
        """Return the base read queryset for loci."""
        return RncLocus.objects.using(settings.LOCUS_DATABASE_ALIAS).all()

    @staticmethod
    def apply_region_scope(
        queryset: QuerySet[RncLocus],
        region_ids: Iterable[int],
    ) -> QuerySet[RncLocus]:
        """Restrict loci to rows related to the provided member regions."""
        return queryset.filter(locus_members__region_id__in=tuple(region_ids)).distinct()

    @staticmethod
    def apply_filters(queryset: QuerySet[RncLocus], params: object) -> QuerySet[RncLocus]:
        """Validate and apply request filters."""
        filterset = LocusFilter(data=params, queryset=queryset)
        if not filterset.is_valid():
            raise ValidationError(filterset.errors)
        return cast("QuerySet[RncLocus]", filterset.qs)

    @staticmethod
    def apply_ordering(
        queryset: QuerySet[RncLocus],
        ordering: str | None,
    ) -> QuerySet[RncLocus]:
        """Apply explicit allow-listed ordering to the queryset."""
        if not ordering:
            return queryset.order_by("id")

        order_by: list[str] = []
        for raw_field in ordering.split(","):
            field = raw_field.strip()
            if not field:
                continue

            is_descending = field.startswith("-")
            public_name = field[1:] if is_descending else field
            database_name = ORDERING_FIELD_MAP.get(public_name)
            if database_name is None:
                allowed = ", ".join(sorted(ORDERING_FIELD_MAP))
                raise ValidationError(
                    {"ordering": f"Unsupported ordering field '{public_name}'. Allowed: {allowed}."}
                )
            order_by.append(f"-{database_name}" if is_descending else database_name)

        if not order_by:
            return queryset.order_by("id")
        if "id" not in {field.removeprefix("-") for field in order_by}:
            order_by.append("id")
        return queryset.order_by(*order_by)

    @staticmethod
    def apply_eager_loading(
        queryset: QuerySet[RncLocus],
        include_members: bool,
    ) -> QuerySet[RncLocus]:
        """Add eager loading required by the selected response shape."""
        if not include_members:
            return queryset

        member_queryset = RncLocusMember.objects.using(settings.LOCUS_DATABASE_ALIAS).order_by("id")
        return queryset.prefetch_related(
            Prefetch("locus_members", queryset=member_queryset),
        )
