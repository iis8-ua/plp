"""Implementación mock de los 17 endpoints definidos en api/api.yaml.

Sólo se comprueban rutas, autenticación simulada, validación de entrada y códigos
de estado. No hay persistencia ni lógica de negocio. Los disparadores de cada
error están documentados en backend/README.md.
"""

import re
from datetime import datetime, timezone

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import mocks
from .guards import admin_guard, bearer_guard, current_user, error_response, forced_error
from .serializers import (
    LoginRequestSerializer,
    PaymentRequestSerializer,
    TicketCreateRequestSerializer,
    TicketMessageRequestSerializer,
    TicketUpdateRequestSerializer,
    WithdrawQuerySerializer,
)

ID_PATTERN = re.compile(r'^[A-Za-z0-9_-]+$')

TICKET_STATUS_LABELS = {
    'open': 'Abierto',
    'in_progress': 'En proceso',
    'closed': 'Cerrado',
}


def _now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


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

    entry = mocks.MOCK_USERS.get(user)
    if not entry or entry['password'] != serializer.validated_data['password']:
        return error_response(
            'INVALID_CREDENTIALS', 'Usuario o contraseña incorrectos.', status.HTTP_401_UNAUTHORIZED
        )

    return Response(
        {
            'token': f'mock-token-{user}',
            'token_type': 'Bearer',
            'expires_in': 3600,
            'user': entry['user'],
        },
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
    currency = serializer.validated_data.get('currency', 'EUR')

    if amount > mocks.MOCK_BALANCES[currency]:
        return error_response(
            'INVALID_AMOUNT',
            'El importe no es válido o supera el saldo disponible.',
            status.HTTP_400_BAD_REQUEST,
        )

    mocks.MOCK_BALANCES[currency] = round(mocks.MOCK_BALANCES[currency] - amount, 2)
    return Response(
        {'withdrawn': amount, 'currency': currency, 'balance': mocks.MOCK_BALANCES[currency]},
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
            'balances': [
                {'currency': currency, 'amount': amount}
                for currency, amount in mocks.MOCK_BALANCES.items()
            ],
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
    if amount > mocks.MOCK_BALANCES['EUR']:
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

    payment = mocks.find_payment(transaction_id)
    refund_id = f'ref_{len(mocks.MOCK_REFUNDS) + 1:03d}'
    reason = request.query_params.get('reason', '').strip() or 'Solicitud desde el portal del comercio'
    mocks.MOCK_REFUNDS.append(
        {
            'id': refund_id,
            'transaction_id': transaction_id,
            'reference': payment['reference'] if payment else '',
            'amount': payment['amount'] if payment else 0.0,
            'currency': payment['currency'] if payment else 'EUR',
            'client': payment['client'] if payment else '',
            'status': 'pending',
            'reason': reason,
            'created_at': _now(),
        }
    )

    return Response(
        {'request_id': refund_id, 'transaction_id': transaction_id, 'status': 'pending'},
        status=status.HTTP_202_ACCEPTED,
    )


def _pending_refund(transaction_id):
    return next(
        (
            refund
            for refund in mocks.MOCK_REFUNDS
            if refund['transaction_id'] == transaction_id and refund['status'] == 'pending'
        ),
        None,
    )


@documented(200, 400, 401, 404, 500)
@api_view(['POST'])
def refund_accept(request):
    denied = _bearer_or_401(request)
    if denied:
        return denied

    if forced_error(request):
        return error_response(
            'REFUND_ERROR', 'No se pudo aceptar el reembolso.', status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    transaction_id = request.query_params.get('transaction_id', '')
    refund = _pending_refund(transaction_id)
    if not refund:
        return error_response(
            'REFUND_NOT_FOUND',
            'No hay una devolución pendiente para esa transacción.',
            status.HTTP_404_NOT_FOUND,
        )

    currency = refund['currency']
    available = mocks.MOCK_BALANCES.get(currency, 0.0)
    if refund['amount'] > available:
        return error_response(
            'INSUFFICIENT_BALANCE',
            'El saldo disponible no cubre el importe de la devolución.',
            status.HTTP_400_BAD_REQUEST,
        )

    mocks.MOCK_BALANCES[currency] = round(available - refund['amount'], 2)
    refund['status'] = 'accepted'

    return Response(
        {'refund': refund, 'balance': mocks.MOCK_BALANCES[currency]},
        status=status.HTTP_200_OK,
    )


@documented(200, 401, 404, 500)
@api_view(['POST'])
def refund_reject(request):
    denied = _bearer_or_401(request)
    if denied:
        return denied

    if forced_error(request):
        return error_response(
            'REFUND_ERROR', 'No se pudo rechazar el reembolso.', status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    transaction_id = request.query_params.get('transaction_id', '')
    refund = _pending_refund(transaction_id)
    if not refund:
        return error_response(
            'REFUND_NOT_FOUND',
            'No hay una devolución pendiente para esa transacción.',
            status.HTTP_404_NOT_FOUND,
        )

    refund['status'] = 'rejected'

    return Response(
        {'refund': refund, 'balance': mocks.MOCK_BALANCES.get(refund['currency'], 0.0)},
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

    nombre = request.query_params.get('nombre', '')
    company = {
        'id': f'emp_{len(mocks.MOCK_COMPANIES) + 1:03d}',
        'nombre': nombre,
        'balance': 0.0,
        'status': 'activo',
        'registered_at': _now(),
    }
    mocks.MOCK_COMPANIES.append(company)
    return Response(company, status=status.HTTP_200_OK)


@documented(200, 403, 404)
@api_view(['DELETE'])
def company_delete(request):
    denied = _admin_or_403(request)
    if denied:
        return denied

    company_id = request.query_params.get('id', '')
    company = mocks.find_company(company_id)
    if not company:
        return error_response(
            'COMPANY_NOT_FOUND',
            'La empresa indicada no existe o su identificador no es válido.',
            status.HTTP_404_NOT_FOUND,
        )

    company['status'] = 'dado-de-baja'
    return Response(company, status=status.HTTP_200_OK)


@documented(200, 403, 404)
@api_view(['PUT'])
def company_reactivate(request):
    denied = _admin_or_403(request)
    if denied:
        return denied

    company_id = request.query_params.get('id', '')
    company = mocks.find_company(company_id)
    if not company:
        return error_response(
            'COMPANY_NOT_FOUND',
            'La empresa indicada no existe o su identificador no es válido.',
            status.HTTP_404_NOT_FOUND,
        )

    company['status'] = 'activo'
    return Response(company, status=status.HTTP_200_OK)


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

    serializer = TicketCreateRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    user = current_user(request) or {}
    company_id = data.get('company_id') or user.get('company_id', '')
    name = data.get('company_name') or mocks.company_name(company_id, user.get('name', company_id))

    now = _now()
    ticket_id = str(max(int(ticket['id']) for ticket in mocks.MOCK_TICKETS) + 1)
    subject = data['subject']
    description = data.get('description', '')
    ticket = {
        'id': ticket_id,
        'company_id': company_id,
        'company_name': name,
        'subject': subject,
        'description': description,
        'status': data.get('status', 'open'),
        'reply': '',
        'created_at': now,
        'updated_at': now,
        'messages': [
            {
                'id': f'{ticket_id}-m1',
                'author': name,
                'role': 'comercio',
                'message': description or subject,
                'created_at': now,
            }
        ],
        'history': [
            {
                'id': f'{ticket_id}-h1',
                'at': now,
                'title': 'Ticket abierto',
                'description': 'Ticket creado por el comercio.',
                'author': name,
            }
        ],
    }
    mocks.MOCK_TICKETS.append(ticket)
    return Response(ticket, status=status.HTTP_200_OK)


@documented(200, 403, 404)
@api_view(['DELETE'])
def ticket_delete(request):
    denied = _admin_or_403(request)
    if denied:
        return denied

    ticket_id = request.query_params.get('id', '')
    ticket = mocks.find_ticket(ticket_id)
    if not ticket:
        return error_response(
            'TICKET_NOT_FOUND',
            'El ticket indicado no existe o su identificador no es válido.',
            status.HTTP_404_NOT_FOUND,
        )

    mocks.MOCK_TICKETS.remove(ticket)
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
    ticket = mocks.find_ticket(ticket_id)
    if not ticket:
        return error_response(
            'TICKET_NOT_FOUND',
            'El ticket indicado no existe o su identificador no es válido.',
            status.HTTP_404_NOT_FOUND,
        )

    serializer = TicketUpdateRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    now = _now()
    reply = (data.get('reply') or '').strip()
    new_status = data.get('status')
    author = (current_user(request) or {}).get('name', 'Equipo de soporte PLP')

    if reply and reply != ticket['reply']:
        ticket['reply'] = reply
        ticket.setdefault('messages', []).append(
            {
                'id': f'{ticket_id}-m{len(ticket.get("messages", [])) + 1}',
                'author': author,
                'role': 'tecnico',
                'message': reply,
                'created_at': now,
            }
        )
        ticket['history'].append(
            {
                'id': f'{ticket_id}-reply-{len(ticket["history"]) + 1}',
                'at': now,
                'title': 'Respuesta añadida',
                'description': reply,
                'author': author,
            }
        )

    if new_status and new_status != ticket['status']:
        previous = ticket['status']
        ticket['status'] = new_status
        ticket['history'].append(
            {
                'id': f'{ticket_id}-status-{len(ticket["history"]) + 1}',
                'at': now,
                'title': f'{TICKET_STATUS_LABELS.get(previous, previous)} → {TICKET_STATUS_LABELS.get(new_status, new_status)}',
                'description': (
                    'Incidencia resuelta. El ticket se ha cerrado.'
                    if new_status == 'closed'
                    else 'Estado del ticket actualizado desde el portal de soporte.'
                ),
                'author': 'Equipo de soporte PLP',
            }
        )

    ticket['updated_at'] = now
    return Response(ticket, status=status.HTTP_200_OK)


@documented(200, 400, 401, 404)
@api_view(['POST'])
def ticket_message(request):
    denied = _bearer_or_401(request)
    if denied:
        return denied

    ticket_id = request.query_params.get('id', '')
    ticket = mocks.find_ticket(ticket_id)
    user = current_user(request) or {'name': 'Comercio', 'role': 'comercio'}
    if not ticket or (
        user.get('role') == 'comercio' and user.get('company_id') != ticket['company_id']
    ):
        return error_response(
            'TICKET_NOT_FOUND',
            'El ticket indicado no existe o su identificador no es válido.',
            status.HTTP_404_NOT_FOUND,
        )

    serializer = TicketMessageRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    message = serializer.validated_data['message'].strip()

    now = _now()
    role = 'comercio' if user.get('role') == 'comercio' else 'tecnico'
    ticket.setdefault('messages', []).append(
        {
            'id': f'{ticket_id}-m{len(ticket.get("messages", [])) + 1}',
            'author': user.get('name', 'Comercio'),
            'role': role,
            'message': message,
            'created_at': now,
        }
    )
    ticket['updated_at'] = now
    if role == 'tecnico':
        ticket['reply'] = message

    return Response(ticket, status=status.HTTP_200_OK)


@documented(200, 401)
@api_view(['GET'])
def tickets(request):
    denied = _bearer_or_401(request)
    if denied:
        return denied

    user = current_user(request) or {}
    if user.get('role') == 'comercio':
        company_id = user.get('company_id')
        data = [ticket for ticket in mocks.MOCK_TICKETS if ticket['company_id'] == company_id]
    else:
        data = mocks.MOCK_TICKETS

    return Response(data, status=status.HTTP_200_OK)
