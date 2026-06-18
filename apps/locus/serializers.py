from typing import Any

from rest_framework import serializers

from apps.locus.models import RncLocus, RncLocusMember


class RncLocusMemberSerializer(serializers.ModelSerializer[RncLocusMember]):
    """Serialize a locus member using camelCase field names."""

    ursTaxid = serializers.CharField(source="urs_taxid")
    regionId = serializers.IntegerField(source="region_id")
    locusId = serializers.IntegerField(source="locus_id")
    membershipStatus = serializers.CharField(source="membership_status")

    class Meta:
        """Serializer metadata."""

        model = RncLocusMember
        fields = ("id", "ursTaxid", "regionId", "locusId", "membershipStatus")
        read_only_fields = fields


class RncLocusSerializer(serializers.ModelSerializer[RncLocus]):
    """Serialize a locus using camelCase field names."""

    assemblyId = serializers.CharField(source="assembly_id")
    locusName = serializers.CharField(source="locus_name")
    publicLocusName = serializers.CharField(source="public_locus_name")
    locusStart = serializers.IntegerField(source="locus_start")
    locusStop = serializers.IntegerField(source="locus_stop")
    memberCount = serializers.IntegerField(source="member_count")
    locusMembers = RncLocusMemberSerializer(source="locus_members", many=True, read_only=True)

    class Meta:
        """Serializer metadata."""

        model = RncLocus
        fields = (
            "id",
            "assemblyId",
            "locusName",
            "publicLocusName",
            "chromosome",
            "strand",
            "locusStart",
            "locusStop",
            "memberCount",
            "locusMembers",
        )
        read_only_fields = fields

    def get_fields(self) -> dict[str, Any]:
        """Remove sideloaded members unless explicitly requested."""
        fields = super().get_fields()
        if not self.context.get("include_locus_members", False):
            fields.pop("locusMembers", None)
        return fields
