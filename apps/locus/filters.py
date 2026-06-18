from typing import Any

import django_filters
from django.conf import settings
from django.db.models import QuerySet

from apps.locus.models import RncLocus, RncLocusMember


class LocusFilter(django_filters.FilterSet):  # type: ignore[misc]
    """Validate and apply supported locus query filters."""

    id = django_filters.NumberFilter(field_name="id")
    assemblyId = django_filters.CharFilter(field_name="assembly_id", lookup_expr="exact")
    regionId = django_filters.NumberFilter(method="filter_region_id")
    membershipStatus = django_filters.CharFilter(method="filter_membership_status")

    class Meta:
        """Filter metadata."""

        model = RncLocus
        fields = ("id", "assemblyId", "regionId", "membershipStatus")

    def filter_region_id(
        self,
        queryset: QuerySet[RncLocus],
        name: str,
        value: Any,
    ) -> QuerySet[RncLocus]:
        """Filter loci by member region identifier."""
        return queryset.filter(locus_members__region_id=value).distinct()

    def filter_membership_status(
        self,
        queryset: QuerySet[RncLocus],
        name: str,
        value: str,
    ) -> QuerySet[RncLocus]:
        """Filter loci by member membership status."""
        return queryset.filter(locus_members__membership_status=value).distinct()


def get_region_id_choices(limit: int = 10_000) -> QuerySet[RncLocusMember]:
    """Return region identifiers from the data source for dynamic choice use cases."""
    return (
        RncLocusMember.objects.using(settings.LOCUS_DATABASE_ALIAS)
        .order_by("region_id")
        .only("region_id")[:limit]
    )
