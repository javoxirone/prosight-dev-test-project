import factory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser

from apps.locus.models import RncLocus, RncLocusMember


class UserFactory(factory.django.DjangoModelFactory):
    """Create Django users for API tests."""

    class Meta:
        """Factory metadata."""

        model = get_user_model()

    username = factory.Sequence(lambda number: f"user-{number}")
    password = factory.PostGenerationMethodCall("set_password", "password123")
    is_active = True


class AdminUserFactory(UserFactory):
    """Create an admin-equivalent user."""

    username = "admin"
    is_staff = True
    is_superuser = True


class NormalUserFactory(UserFactory):
    """Create a normal user."""

    username = "normal"


class LimitedUserFactory(UserFactory):
    """Create a limited user."""

    username = "limited"


class RncLocusFactory(factory.django.DjangoModelFactory):
    """Create unmanaged locus rows in the test database."""

    class Meta:
        """Factory metadata."""

        model = RncLocus

    id = factory.Sequence(lambda number: number + 1)
    assembly_id = factory.Sequence(lambda number: f"assembly-{number}")
    locus_name = factory.Sequence(lambda number: f"locus-{number}")
    public_locus_name = factory.Sequence(lambda number: f"PUBLIC-{number}")
    chromosome = "1"
    strand = "+"
    locus_start = factory.Sequence(lambda number: 100 + number)
    locus_stop = factory.Sequence(lambda number: 200 + number)
    member_count = 1


class RncLocusMemberFactory(factory.django.DjangoModelFactory):
    """Create unmanaged locus member rows in the test database."""

    class Meta:
        """Factory metadata."""

        model = RncLocusMember

    id = factory.Sequence(lambda number: number + 1)
    urs_taxid = factory.Sequence(lambda number: f"URS{number:010d}_9606")
    region_id = factory.Sequence(lambda number: 86_000_000 + number)
    locus = factory.SubFactory(RncLocusFactory)
    membership_status = "member"


def as_user(user: AbstractBaseUser) -> AbstractBaseUser:
    """Return the supplied user with a precise type for tests."""
    return user
