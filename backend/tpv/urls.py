"""URL configuration for tpv project."""

from django.urls import include, path
from django.http import JsonResponse


def index(request):
    return JsonResponse({
        "name": "API PLP · TPV",
        "version": "1.0.0",
        "status": "ok",
        "docs": "https://pasalapasta.spaincentral.cloudapp.azure.com/docs.html",
        "contact": "soporte.pasalapasta@gmail.com",
    })

urlpatterns = [
    path('', index),
    path('', include('api.urls')),
]
