from typing import Any

from django.db.models import QuerySet
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.locus.models import RncLocus
from apps.locus.pagination import LocusPageNumberPagination
from apps.locus.permissions import CanUseLocusSideloading
from apps.locus.serializers import RncLocusSerializer
from apps.locus.services import SIDELOADING_PARAM, LocusAccessService, LocusQueryService


@extend_schema_view(
    get=extend_schema(
        tags=["Locus"],
        operation_id="listLoci",
        description=(
            "List RNACentral loci with optional filters, ordering, pagination, and admin-only "
            "locus member sideloading."
        ),
        parameters=[
            OpenApiParameter(
                "id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Locus ID.",
            ),
            OpenApiParameter(
                "assemblyId",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Assembly identifier.",
            ),
            OpenApiParameter(
                "regionId",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Member region ID loaded from rnc_locus_members.region_id.",
            ),
            OpenApiParameter(
                "membershipStatus",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Member membership status, for example 'member'.",
            ),
            OpenApiParameter(
                "ordering",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description=(
                    "Comma-separated ordering fields. Allowed: id, assemblyId, locusName, "
                    "publicLocusName, chromosome, strand, locusStart, locusStop, memberCount. "
                    "Prefix with '-' for descending."
                ),
                examples=[
                    OpenApiExample("Ascending locus start", value="locusStart"),
                    OpenApiExample("Descending member count", value="-memberCount"),
                ],
            ),
            OpenApiParameter(
                SIDELOADING_PARAM,
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                enum=["locusMembers"],
                description="Admin-only sideloading option.",
            ),
            OpenApiParameter("page", OpenApiTypes.INT, OpenApiParameter.QUERY),
            OpenApiParameter("pageSize", OpenApiTypes.INT, OpenApiParameter.QUERY),
        ],
        responses={200: RncLocusSerializer},
    ),
)
class LocusListAPIView(generics.ListAPIView[RncLocus]):
    """List loci for authenticated users."""

    serializer_class = RncLocusSerializer
    pagination_class = LocusPageNumberPagination
    permission_classes = (IsAuthenticated, CanUseLocusSideloading)

    def get_queryset(self) -> QuerySet[RncLocus]:
        """Return the queryset for this request."""
        return LocusQueryService.list_loci(self.request.user, self.request.query_params)

    def get_serializer_context(self) -> dict[str, Any]:
        """Attach response-shape flags to serializer context."""
        context = super().get_serializer_context()
        include_members = "locusMembers" in LocusAccessService.parse_sideloading(
            self.request.query_params.get(SIDELOADING_PARAM),
        )
        context["include_locus_members"] = include_members
        return context
