"""Adapta los errores de validación de DRF al schema `Error` del contrato."""

from rest_framework import status
from rest_framework.views import exception_handler


def _flatten(errors):
    if isinstance(errors, dict):
        return '; '.join(f'{key}: {_flatten(value)}' for key, value in errors.items())
    if isinstance(errors, list):
        return '; '.join(_flatten(item) for item in errors)
    return str(errors)


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return None

    if response.status_code == status.HTTP_400_BAD_REQUEST:
        response.data = {
            'code': 'VALIDATION_ERROR',
            'message': _flatten(response.data),
        }
    return response
