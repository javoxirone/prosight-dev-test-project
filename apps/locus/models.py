from django.db import models


class RncLocus(models.Model):
    """RNACentral locus row mapped to ``rnacen.rnc_locus``."""

    id = models.BigAutoField(primary_key=True)
    assembly_id = models.TextField()
    locus_name = models.TextField()
    public_locus_name = models.TextField()
    chromosome = models.TextField()
    strand = models.TextField()
    locus_start = models.IntegerField()
    locus_stop = models.IntegerField()
    member_count = models.IntegerField()

    class Meta:
        """Model metadata."""

        managed = False
        db_table = "rnc_locus"
        ordering = ("id",)

    def __str__(self) -> str:
        """Return a readable locus identifier."""
        return f"{self.public_locus_name} ({self.id})"


class RncLocusMember(models.Model):
    """RNACentral locus member row mapped to ``rnacen.rnc_locus_members``."""

    id = models.BigAutoField(primary_key=True)
    urs_taxid = models.TextField()
    region_id = models.IntegerField(unique=True)
    locus = models.ForeignKey(
        RncLocus,
        db_column="locus_id",
        related_name="locus_members",
        on_delete=models.DO_NOTHING,
        db_constraint=False,
    )
    membership_status = models.TextField()

    class Meta:
        """Model metadata."""

        managed = False
        db_table = "rnc_locus_members"
        ordering = ("id",)

    def __str__(self) -> str:
        """Return a readable locus member identifier."""
        return f"{self.urs_taxid} ({self.region_id})"
