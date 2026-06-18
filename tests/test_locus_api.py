import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from tests.factories import (
    AdminUserFactory,
    LimitedUserFactory,
    NormalUserFactory,
    RncLocusFactory,
    RncLocusMemberFactory,
)

pytestmark = pytest.mark.django_db


def test_anonymous_user_receives_401(api_client: APIClient) -> None:
    """Anonymous requests must be rejected."""
    response = api_client.get(reverse("locus-list"))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_admin_can_list_locus_rows(authenticated_client: object) -> None:
    """Admin users can access locus rows."""
    locus = RncLocusFactory(id=3106326, assembly_id="GRCh38", member_count=5)
    RncLocusMemberFactory(locus=locus, region_id=85682522)
    client = authenticated_client(AdminUserFactory())

    response = client.get(reverse("locus-list"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == 3106326
    assert response.data["results"][0]["assemblyId"] == "GRCh38"


def test_normal_user_cannot_use_sideloading(authenticated_client: object) -> None:
    """Normal users receive 403 when requesting sideloading."""
    RncLocusMemberFactory()
    client = authenticated_client(NormalUserFactory())

    response = client.get(reverse("locus-list"), {"sideloading": "locusMembers"})

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_limited_user_is_automatically_restricted_to_allowed_regions(
    authenticated_client: object,
) -> None:
    """Limited users must never see rows outside their configured regions."""
    allowed_locus = RncLocusFactory(id=1, public_locus_name="ALLOWED")
    denied_locus = RncLocusFactory(id=2, public_locus_name="DENIED")
    RncLocusMemberFactory(locus=allowed_locus, region_id=86118093)
    RncLocusMemberFactory(locus=denied_locus, region_id=99999999)
    client = authenticated_client(LimitedUserFactory())

    response = client.get(reverse("locus-list"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["publicLocusName"] == "ALLOWED"


def test_limited_user_region_filter_outside_scope_returns_empty(
    authenticated_client: object,
) -> None:
    """Explicit region filters cannot bypass limited-user region scope."""
    denied_locus = RncLocusFactory(id=2, public_locus_name="DENIED")
    RncLocusMemberFactory(locus=denied_locus, region_id=99999999)
    client = authenticated_client(LimitedUserFactory())

    response = client.get(reverse("locus-list"), {"regionId": 99999999})

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []


def test_filtering_by_supported_parameters(authenticated_client: object) -> None:
    """Supported filters are applied through ORM relationships."""
    matching_locus = RncLocusFactory(id=10, assembly_id="ASM", public_locus_name="MATCH")
    other_locus = RncLocusFactory(id=11, assembly_id="OTHER", public_locus_name="OTHER")
    RncLocusMemberFactory(
        locus=matching_locus,
        region_id=85682522,
        membership_status="member",
    )
    RncLocusMemberFactory(
        locus=other_locus,
        region_id=85682523,
        membership_status="highlighted",
    )
    client = authenticated_client(AdminUserFactory())

    response = client.get(
        reverse("locus-list"),
        {
            "id": 10,
            "assemblyId": "ASM",
            "regionId": 85682522,
            "membershipStatus": "member",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["publicLocusName"] == "MATCH"


def test_invalid_integer_filter_returns_400(authenticated_client: object) -> None:
    """Invalid integer filters return a validation error."""
    client = authenticated_client(AdminUserFactory())

    response = client.get(reverse("locus-list"), {"id": "not-an-int"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_ordering_supports_allowed_camel_case_fields(authenticated_client: object) -> None:
    """Ordering accepts allow-listed camelCase field names."""
    RncLocusFactory(id=1, member_count=2, public_locus_name="LOW")
    RncLocusFactory(id=2, member_count=10, public_locus_name="HIGH")
    client = authenticated_client(AdminUserFactory())

    response = client.get(reverse("locus-list"), {"ordering": "-memberCount"})

    assert response.status_code == status.HTTP_200_OK
    assert [row["publicLocusName"] for row in response.data["results"]] == ["HIGH", "LOW"]


def test_unsupported_ordering_returns_400(authenticated_client: object) -> None:
    """Ordering cannot use arbitrary fields."""
    client = authenticated_client(AdminUserFactory())

    response = client.get(reverse("locus-list"), {"ordering": "membershipStatus"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_pagination_uses_page_size_query_parameter(authenticated_client: object) -> None:
    """The endpoint returns standard page-number pagination metadata."""
    RncLocusFactory(id=1)
    RncLocusFactory(id=2)
    RncLocusFactory(id=3)
    client = authenticated_client(AdminUserFactory())

    response = client.get(reverse("locus-list"), {"page": 1, "pageSize": 2})

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 3
    assert response.data["next"] is not None
    assert response.data["previous"] is None
    assert len(response.data["results"]) == 2


def test_sideloading_returns_locus_members_for_admin(authenticated_client: object) -> None:
    """Admin sideloading embeds related locus members without raw SQL joins."""
    locus = RncLocusFactory(id=50)
    RncLocusMemberFactory(
        locus=locus,
        id=500,
        urs_taxid="URS000000001_9606",
        region_id=86696489,
        membership_status="member",
    )
    client = authenticated_client(AdminUserFactory())

    response = client.get(reverse("locus-list"), {"sideloading": "locusMembers"})

    assert response.status_code == status.HTTP_200_OK
    result = response.data["results"][0]
    assert result["locusMembers"] == [
        {
            "id": 500,
            "ursTaxid": "URS000000001_9606",
            "regionId": 86696489,
            "locusId": 50,
            "membershipStatus": "member",
        }
    ]


def test_locus_members_are_not_returned_without_sideloading(authenticated_client: object) -> None:
    """Default responses contain only locus fields."""
    locus = RncLocusFactory(id=60)
    RncLocusMemberFactory(locus=locus)
    client = authenticated_client(AdminUserFactory())

    response = client.get(reverse("locus-list"))

    assert response.status_code == status.HTTP_200_OK
    assert "locusMembers" not in response.data["results"][0]


def test_serializer_uses_camel_case_locus_output(authenticated_client: object) -> None:
    """Serializer output uses the required camelCase contract."""
    RncLocusFactory(
        id=70,
        assembly_id="ASM70",
        locus_name="internal",
        public_locus_name="public",
        chromosome="X",
        strand="-1",
        locus_start=123,
        locus_stop=456,
        member_count=7,
    )
    client = authenticated_client(AdminUserFactory())

    response = client.get(reverse("locus-list"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["results"][0] == {
        "id": 70,
        "assemblyId": "ASM70",
        "locusName": "internal",
        "publicLocusName": "public",
        "chromosome": "X",
        "strand": "-1",
        "locusStart": 123,
        "locusStop": 456,
        "memberCount": 7,
    }


def test_invalid_sideloading_value_returns_400(authenticated_client: object) -> None:
    """Unsupported sideloading values are rejected explicitly."""
    client = authenticated_client(AdminUserFactory())

    response = client.get(reverse("locus-list"), {"sideloading": "unknown"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
