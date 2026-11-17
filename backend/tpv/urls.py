"""URL configuration for tpv project."""

from django.urls import include, path

urlpatterns = [
    path('', include('api.urls')),
]
