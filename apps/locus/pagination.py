from rest_framework.pagination import PageNumberPagination


class LocusPageNumberPagination(PageNumberPagination):
    """Page-number pagination with API-required page size controls."""

    page_size = 1000
    page_size_query_param = "pageSize"
    max_page_size = 10_000
