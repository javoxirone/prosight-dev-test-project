from django.urls import path

from apps.locus.views import LocusListAPIView

urlpatterns = [
    path("locus/", LocusListAPIView.as_view(), name="locus-list"),
]
