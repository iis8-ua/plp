"""Autenticación por token de DRF con el prefijo que usa el frontend."""

from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed


def token_ttl_seconds():
    return int(getattr(settings, 'TOKEN_TTL_SECONDS', 3600))


def token_is_expired(token):
    return token.created < timezone.now() - timedelta(seconds=token_ttl_seconds())


def issue_token(user):
    """Devuelve un token válido; renueva el existente si ha caducado."""
    token, created = Token.objects.get_or_create(user=user)
    if not created and token_is_expired(token):
        token.delete()
        token = Token.objects.create(user=user)
    return token


class BearerTokenAuthentication(TokenAuthentication):
    keyword = 'Bearer'

    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)
        if token_is_expired(token):
            token.delete()
            raise AuthenticationFailed('El token ha caducado. Inicia sesión de nuevo.')
        return user, token
