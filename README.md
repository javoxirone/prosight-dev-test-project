# Prosight Locus API

Django REST API for `GET /api/v1/locus/` backed by the public RNACentral PostgreSQL tables:

- `rnacen.rnc_locus`
- `rnacen.rnc_locus_members`

The locus tables are unmanaged Django models. The service uses a local PostgreSQL database for Django auth/JWT users and the provided external database as a read-only data source.

## Stack

- Python 3.13+
- Django 5+
- Django REST Framework
- PostgreSQL
- SimpleJWT
- drf-spectacular
- django-filter
- pytest, pytest-django, factory_boy
- Ruff, Mypy
- Docker Compose

## Quick Start

```bash
# Optional: copy this if you want to override defaults.
cp .env.example .env
make up
```

The API will be available at `http://localhost:8000`.

The container startup command runs:

```bash
python manage.py migrate --noinput
python manage.py bootstrap_users
python manage.py runserver 0.0.0.0:8000
```

## Predefined Users

| Username | Password | Behavior |
| --- | --- | --- |
| `admin` | `admin123` | Full access, can use `sideloading=locusMembers` |
| `normal` | `normal123` | Locus fields only, sideloading returns `403` |
| `limited` | `limited123` | Automatically restricted to region IDs `86118093`, `86696489`, `88186467` |

## Authentication

Obtain a JWT access token:

```bash
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}'
```

Use the access token:

```bash
curl http://localhost:8000/api/v1/locus/?page=1&pageSize=100 \
  -H 'Authorization: Bearer <access-token>'
```

Anonymous requests return `401 Unauthorized`.

## Endpoint

```http
GET /api/v1/locus/
```

Supported query parameters:

| Parameter | Description |
| --- | --- |
| `id` | Exact locus ID |
| `assemblyId` | Exact assembly ID |
| `regionId` | Member region ID from `rnc_locus_members.region_id` |
| `membershipStatus` | Member membership status, for example `member` |
| `ordering` | Comma-separated allow-listed fields. Supports `-` descending prefix |
| `sideloading` | Admin-only. Currently supports `locusMembers` |
| `page` | Page number |
| `pageSize` | Page size, default `1000`, max `10000` |

Allowed ordering fields:

```text
id, assemblyId, locusName, publicLocusName, chromosome, strand, locusStart, locusStop, memberCount
```

Examples:

```http
GET /api/v1/locus/?id=3106326
GET /api/v1/locus/?assemblyId=GRCh38
GET /api/v1/locus/?regionId=85682522
GET /api/v1/locus/?membershipStatus=member
GET /api/v1/locus/?ordering=-memberCount
GET /api/v1/locus/?sideloading=locusMembers
```

Paginated responses contain:

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 3106326,
      "assemblyId": "...",
      "locusName": "...",
      "publicLocusName": "...",
      "chromosome": "...",
      "strand": "...",
      "locusStart": 123,
      "locusStop": 456,
      "memberCount": 5
    }
  ]
}
```

With admin sideloading:

```json
{
  "id": 123,
  "assemblyId": "...",
  "locusMembers": [
    {
      "id": 456,
      "ursTaxid": "URS000000001_9606",
      "regionId": 85682522,
      "locusId": 123,
      "membershipStatus": "member"
    }
  ]
}
```

## API Documentation

OpenAPI schema:

```http
GET /api/schema/
```

Swagger UI:

```http
GET /api/docs/
```

The schema documents JWT auth, filtering, pagination, ordering, and the `sideloading` parameter.

## Tests and Quality

```bash
make test
make lint
```

`make test` runs pytest with coverage. Tests create the unmanaged locus tables inside the test database; no migrations are generated for external tables.

For local sandbox environments without a running PostgreSQL server, the test settings include an opt-in SQLite fallback:

```bash
USE_SQLITE_FOR_TESTS=true pytest
```

Production and Docker execution use PostgreSQL by default.

## Architecture

The `apps/locus` app keeps responsibilities separated:

- `models.py`: unmanaged external table mappings
- `filters.py`: filter validation and relation filters
- `selectors.py`: queryset construction, ordering, eager loading
- `services.py`: business rules and access scoping
- `permissions.py`: DRF permission classes
- `serializers.py`: camelCase response contract
- `views.py`: thin DRF list view
- `urls.py`: route registration

Performance safeguards:

- The endpoint uses ORM filtering and relationships only.
- Sideloading uses `prefetch_related` to avoid N+1 queries.
- Sideloading is omitted by default to keep large list responses lean.
- Ordering is allow-listed to avoid accidental expensive or unsafe fields.
