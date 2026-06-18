from django.contrib import admin

from apps.locus.models import RncLocus, RncLocusMember


@admin.register(RncLocus)
class RncLocusAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Read-only admin for loci."""

    list_display = ("id", "assembly_id", "public_locus_name", "chromosome", "member_count")
    search_fields = ("id", "assembly_id", "public_locus_name")
    ordering = ("id",)

    def has_add_permission(self, request: object) -> bool:
        """Disable adding external rows."""
        return False

    def has_change_permission(self, request: object, obj: RncLocus | None = None) -> bool:
        """Disable changing external rows."""
        return False

    def has_delete_permission(self, request: object, obj: RncLocus | None = None) -> bool:
        """Disable deleting external rows."""
        return False


@admin.register(RncLocusMember)
class RncLocusMemberAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Read-only admin for locus members."""

    list_display = ("id", "urs_taxid", "region_id", "locus_id", "membership_status")
    search_fields = ("id", "urs_taxid", "region_id")
    ordering = ("id",)

    def has_add_permission(self, request: object) -> bool:
        """Disable adding external rows."""
        return False

    def has_change_permission(self, request: object, obj: RncLocusMember | None = None) -> bool:
        """Disable changing external rows."""
        return False

    def has_delete_permission(self, request: object, obj: RncLocusMember | None = None) -> bool:
        """Disable deleting external rows."""
        return False
