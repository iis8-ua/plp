"""Comprobaciones de autenticación simuladas y helpers de respuesta de error."""

from rest_framework import status
from rest_framework.response import Response

from . import mocks

# Cualquier token no vacío se acepta como válido, salvo estos dos (para probar el 401).
INVALID_TOKENS = {"invalid", "expired"}

TOKEN_PREFIX = "mock-token-"


def _bearer_token(request):
    header = request.headers.get("Authorization", "")
    return header[7:].strip() if header.startswith("Bearer ") else ""


def current_user(request):
    """Resuelve el usuario a partir de `mock-token-<usuario>`, o None."""
    token = _bearer_token(request)
    if not token.startswith(TOKEN_PREFIX):
        return None
    return mocks.MOCK_USERS.get(token[len(TOKEN_PREFIX):], {}).get("user")


def error_response(code, message, http_status):
    """Respuesta con la forma del schema `Error` de api/api.yaml."""
    return Response({"code": code, "message": message}, status=http_status)


def bearer_guard(request):
    """Devuelve una Response 401 si falta el Bearer, o None si es válido."""
    token = _bearer_token(request)
    if not token or token.lower() in INVALID_TOKENS:
        return error_response(
            "UNAUTHORIZED",
            "Falta el token Bearer o no es válido.",
            status.HTTP_401_UNAUTHORIZED,
        )
    return None


def admin_guard(request):
    """Devuelve una Response 403 si falta la credencial de administrador."""
    if not request.headers.get("X-Admin-Token", "").strip():
        return error_response(
            "FORBIDDEN",
            "Esta operación requiere permisos de administrador.",
            status.HTTP_403_FORBIDDEN,
        )
    return None


def forced_error(request):
    """Permite forzar un 500 desde el cliente con la cabecera X-Mock-Error: true."""
    return request.headers.get("X-Mock-Error", "").lower() == "true"
