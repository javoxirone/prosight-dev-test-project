from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.locus.services import SIDELOADING_PARAM, LocusAccessService


class CanUseLocusSideloading(BasePermission):
    """Allow sideloading only for admin users."""

    message = "You do not have permission to use locus sideloading."

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Return whether the request may use requested sideloading."""
        requested = LocusAccessService.parse_sideloading(
            request.query_params.get(SIDELOADING_PARAM),
        )
        return "locusMembers" not in requested or LocusAccessService.is_admin_user(request.user)
