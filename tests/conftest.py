from collections.abc import Generator

import pytest
from django.db import connection
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.locus.models import RncLocus, RncLocusMember


@pytest.fixture(scope="session", autouse=True)
def create_unmanaged_locus_tables(
    django_db_setup: None,
    django_db_blocker: pytest.FixtureRequest,
) -> Generator[None]:
    """Create unmanaged external-model tables inside the test database."""
    del django_db_setup
    with django_db_blocker.unblock():
        existing_tables = connection.introspection.table_names()
        with connection.schema_editor() as schema_editor:
            if RncLocus._meta.db_table not in existing_tables:
                schema_editor.create_model(RncLocus)
            if RncLocusMember._meta.db_table not in existing_tables:
                schema_editor.create_model(RncLocusMember)
    yield


@pytest.fixture(autouse=True)
def clean_locus_tables(db: None) -> Generator[None]:
    """Keep unmanaged table data isolated between tests."""
    del db
    RncLocusMember.objects.all().delete()
    RncLocus.objects.all().delete()
    yield
    RncLocusMember.objects.all().delete()
    RncLocus.objects.all().delete()


@pytest.fixture
def api_client() -> APIClient:
    """Return a DRF test API client."""
    return APIClient()


@pytest.fixture
def authenticated_client(api_client: APIClient):
    """Return a helper that authenticates the API client with JWT."""

    def _authenticate(user: object) -> APIClient:
        token = AccessToken.for_user(user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return api_client

    return _authenticate
