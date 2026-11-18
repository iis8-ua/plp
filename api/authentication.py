"""Autenticación por token de DRF con el prefijo que usa el frontend."""

from rest_framework.authentication import TokenAuthentication


class BearerTokenAuthentication(TokenAuthentication):
    keyword = 'Bearer'
