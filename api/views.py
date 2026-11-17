"""Implementación mock de los 17 endpoints definidos en api/api.yaml.

Sólo se comprueban rutas, autenticación simulada, validación de entrada y códigos
de estado. No hay persistencia ni lógica de negocio. Los disparadores de cada
error están documentados en backend/README.md.
"""

import re

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import mocks
from .guards import admin_guard, bearer_guard, error_response, forced_error
from .serializers import (
    LoginRequestSerializer,
    PaymentRequestSerializer,
    TicketRequestSerializer,
    WithdrawQuerySerializer,
)

ID_PATTERN = re.compile(r'^[A-Za-z0-9_-]+$')


def documented(*codes):
    """Anota los status codes para que drf-spectacular incluya la vista."""
    return extend_schema(
        request=None,
        responses={code: OpenApiResponse(description='Respuesta mock.') for code in codes},
    )


def _bearer_or_401(request):
    return bearer_guard(request)


def _admin_or_403(request, also_bearer=False):
    if also_bearer:
        denied = bearer_guard(request)
        if denied:
            return denied
    return admin_guard(request)


# ---------------------------------------------------------------- Autenticación

@documented(200, 400, 401)
@api_view(['POST'])
def login(request):
    user = request.query_params.get('user')
    if not user:
        return error_response(
            'MISSING_USER', "Falta el parámetro de consulta 'user'.", status.HTTP_400_BAD_REQUEST
        )

    serializer = LoginRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    if mocks.MOCK_USERS.get(user) != serializer.validated_data['password']:
        return error_response(
            'INVALID_CREDENTIALS', 'Usuario o contraseña incorrectos.', status.HTTP_401_UNAUTHORIZED
        )

    return Response(
        {'token': 'mock-token', 'token_type': 'Bearer', 'expires_in': 3600},
        status=status.HTTP_200_OK,
    )


@documented(200, 401, 500)
@api_view(['POST'])
def logout(request):
    denied = _bearer_or_401(request)
    if denied:
        return denied

    if forced_error(request):
        return error_response(
            'LOGOUT_ERROR', 'No se pudo cerrar la sesión.', status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return Response(
        {'message': 'Sesión cerrada correctamente.'}, status=status.HTTP_200_OK
    )


# ------------------------------------------------------------------------ Caja

@documented(200, 400, 401)
@api_view(['POST'])
def withdraw(request):
    denied = _bearer_or_401(request)
    if denied:
        return denied

    serializer = WithdrawQuerySerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    amount = serializer.validated_data['amount']

    if amount > mocks.MOCK_BALANCE:
        return error_response(
            'INVALID_AMOUNT',
            'El importe no es válido o supera el saldo disponible.',
            status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {'withdrawn': amount, 'balance': round(mocks.MOCK_BALANCE - amount, 2)},
        status=status.HTTP_200_OK,
    )


@documented(200, 401)
@api_view(['GET'])
def balance(request):
    denied = _bearer_or_401(request)
    if denied:
        return denied

    return Response(
        {
            'company': mocks.MOCK_COMPANIES[0]['nombre'],
            'balance': mocks.MOCK_BALANCE,
            'currency': 'EUR',
        },
        status=status.HTTP_200_OK,
    )


@documented(200, 400, 409, 422, 500)
@api_view(['POST'])
def pay(request):
    serializer = PaymentRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    amount = serializer.validated_data['total_amount']
    card_number = serializer.validated_data.get('payment_data', {}).get('card_number', '')

    if forced_error(request) or card_number.endswith('0005'):
        return error_response(
            'PAYMENT_ERROR', 'Error interno al procesar el pago.', status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    if amount > mocks.MOCK_BALANCE:
        return error_response(
            'INSUFFICIENT_BALANCE', 'Saldo insuficiente.', status.HTTP_409_CONFLICT
        )
    if card_number.endswith('0002'):
        return error_response(
            'PAYMENT_REJECTED', 'El pago ha sido rechazado.', status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    return Response(
        {'transaction_id': 'txn_mock_001', 'status': 'approved', 'authorized_amount': amount},
        status=status.HTTP_200_OK,
    )


# ------------------------------------------------------------------- Reembolsos

@documented(202, 404)
@api_view(['POST'])
def refund_request(request):
    transaction_id = request.query_params.get('transaction_id', '')
    if (
        not transaction_id
        or not ID_PATTERN.fullmatch(transaction_id)
        or transaction_id not in mocks.VALID_TRANSACTION_IDS
    ):
        return error_response(
            'TRANSACTION_NOT_FOUND',
            'La transacción indicada no existe o su identificador no es válido.',
            status.HTTP_404_NOT_FOUND,
        )

    return Response(
        {'request_id': 'req_mock_001', 'transaction_id': transaction_id, 'status': 'pending'},
        status=status.HTTP_202_ACCEPTED,
    )


@documented(200, 401, 500)
@api_view(['POST'])
def refund_accept(request):
    denied = _bearer_or_401(request)
    if denied:
        return denied

    if forced_error(request):
        return error_response(
            'REFUND_ERROR', 'No se pudo aceptar el reembolso.', status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return Response(
        {
            'transaction_id': request.query_params.get('transaction_id', ''),
            'status': 'accepted',
            'message': 'Reembolso actualizado correctamente.',
        },
        status=status.HTTP_200_OK,
    )


@documented(200, 401, 500)
@api_view(['POST'])
def refund_reject(request):
    denied = _bearer_or_401(request)
    if denied:
        return denied

    if forced_error(request):
        return error_response(
            'REFUND_ERROR', 'No se pudo rechazar el reembolso.', status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return Response(
        {
            'transaction_id': request.query_params.get('transaction_id', ''),
            'status': 'rejected',
            'message': 'Reembolso actualizado correctamente.',
        },
        status=status.HTTP_200_OK,
    )


@documented(200, 401)
@api_view(['GET'])
def refunds(request):
    denied = _bearer_or_401(request)
    if denied:
        return denied
    return Response(mocks.MOCK_REFUNDS, status=status.HTTP_200_OK)


# -------------------------------------------------------------------- Empresas

@documented(200, 403)
@api_view(['PUT'])
def company_add(request):
    denied = _admin_or_403(request)
    if denied:
        return denied

    return Response(
        {
            'id': 'emp_mock_001',
            'nombre': request.query_params.get('nombre', ''),
            'balance': mocks.MOCK_BALANCE,
        },
        status=status.HTTP_200_OK,
    )


@documented(200, 403)
@api_view(['DELETE'])
def company_delete(request):
    denied = _admin_or_403(request)
    if denied:
        return denied
    return Response(
        {'message': 'Empresa eliminada correctamente.'}, status=status.HTTP_200_OK
    )


@documented(200, 401, 403)
@api_view(['GET'])
def companies(request):
    denied = _admin_or_403(request, also_bearer=True)
    if denied:
        return denied
    return Response(mocks.MOCK_COMPANIES, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------- Pagos

@documented(200, 401)
@api_view(['GET'])
def payments(request):
    denied = _bearer_or_401(request)
    if denied:
        return denied
    return Response(mocks.MOCK_PAYMENTS, status=status.HTTP_200_OK)


# --------------------------------------------------------------------- Tickets

@documented(200, 400, 401)
@api_view(['POST'])
def ticket_add(request):
    denied = _bearer_or_401(request)
    if denied:
        return denied

    serializer = TicketRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    return Response(
        {'id': 'tkt_mock_001', 'message': 'Ticket guardado correctamente.'},
        status=status.HTTP_200_OK,
    )


@documented(200, 403)
@api_view(['DELETE'])
def ticket_delete(request):
    denied = _admin_or_403(request)
    if denied:
        return denied
    return Response(
        {'message': 'Ticket eliminado correctamente.'}, status=status.HTTP_200_OK
    )


@documented(200, 400, 401, 404)
@api_view(['PUT'])
def ticket_update(request):
    denied = _bearer_or_401(request)
    if denied:
        return denied

    ticket_id = request.query_params.get('id', '')
    if not ticket_id or not ID_PATTERN.fullmatch(ticket_id) or ticket_id not in mocks.VALID_TICKET_IDS:
        return error_response(
            'TICKET_NOT_FOUND',
            'El ticket indicado no existe o su identificador no es válido.',
            status.HTTP_404_NOT_FOUND,
        )

    serializer = TicketRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    return Response(
        {'id': ticket_id, 'message': 'Ticket guardado correctamente.'},
        status=status.HTTP_200_OK,
    )


@documented(200, 401)
@api_view(['GET'])
def tickets(request):
    denied = _bearer_or_401(request)
    if denied:
        return denied
    return Response(mocks.MOCK_TICKETS, status=status.HTTP_200_OK)
