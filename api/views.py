"""Implementación de la API contra el modelo de datos de ``pagos``."""

import uuid
from decimal import Decimal

from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from django.db.models import Max
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from pagos.models import (
    CuentaBancaria,
    Empresa,
    InformacionPago,
    MetodoPago,
    Moneda,
    PerfilUsuario,
    Reembolso,
    SaldoEmpresa,
    Tarjeta,
    Ticket,
    TicketHistorial,
    TicketMensaje,
    Transaccion,
)

from . import presenters
from .permissions import HasCompany, IsAdminRole, company_for, role_for
from .serializers import (
    CompanyCreateRequestSerializer,
    LoginRequestSerializer,
    PasswordChangeRequestSerializer,
    PaymentRequestSerializer,
    ProfileUpdateRequestSerializer,
    TechnicianCreateRequestSerializer,
    TicketAssignRequestSerializer,
    TicketCreateRequestSerializer,
    TicketMessageRequestSerializer,
    TicketUpdateRequestSerializer,
    WithdrawQuerySerializer,
)

User = get_user_model()

TICKET_STATUS_TO_DB = {
    'open': Ticket.Estado.ABIERTO,
    'in_progress': Ticket.Estado.EN_PROCESO,
    'closed': Ticket.Estado.CERRADO,
}

PAYMENT_METHOD_TO_CATALOG = {
    'card': 'Tarjeta',
    'cash': 'Efectivo',
    'transfer': 'Transferencia',
}

BALANCE_ORDER = {'EUR': 0, 'USD': 1, 'GBP': 2}


def documented(*codes):
    """Anota los status codes para que drf-spectacular incluya la vista."""
    return extend_schema(
        request=None,
        responses={code: OpenApiResponse(description='Respuesta de la API.') for code in codes},
    )


def error_response(code, message, http_status):
    return Response({'code': code, 'message': message}, status=http_status)


def parse_uuid(value):
    try:
        return uuid.UUID(str(value))
    except (TypeError, ValueError, AttributeError):
        return None


def ticket_for(request, number):
    """Ticket visible para el usuario autenticado, o None."""
    try:
        number = int(number)
    except (TypeError, ValueError):
        return None

    ticket = (
        Ticket.objects.select_related('empresa', 'tecnico')
        .prefetch_related('mensajes__autor', 'historial__autor')
        .filter(numero=number)
        .first()
    )
    if not ticket:
        return None
    company = company_for(request.user)
    if role_for(request.user) == 'comercio' and ticket.empresa_id != (company.pk if company else None):
        return None
    return ticket


# ---------------------------------------------------------------- Autenticación

@documented(200, 400, 401)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.query_params.get('user')
    if not username:
        return error_response(
            'MISSING_USER', "Falta el parámetro de consulta 'user'.", status.HTTP_400_BAD_REQUEST
        )

    serializer = LoginRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = authenticate(
        request=request,
        username=username.strip(),
        password=serializer.validated_data['password'],
    )
    if user is None:
        return error_response(
            'INVALID_CREDENTIALS', 'Usuario o contraseña incorrectos.', status.HTTP_401_UNAUTHORIZED
        )

    token, _ = Token.objects.get_or_create(user=user)
    return Response(
        {
            'token': token.key,
            'token_type': 'Bearer',
            'expires_in': 3600,
            'user': presenters.user_payload(user),
        },
        status=status.HTTP_200_OK,
    )


@documented(200, 401)
@api_view(['POST'])
def logout(request):
    if request.auth:
        request.auth.delete()
    return Response({'message': 'Sesión cerrada correctamente.'}, status=status.HTTP_200_OK)


# ------------------------------------------------------------------------ Caja

@documented(200, 400, 401)
@api_view(['POST'])
@permission_classes([HasCompany])
def withdraw(request):
    serializer = WithdrawQuerySerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    amount = Decimal(str(serializer.validated_data['amount']))
    currency = serializer.validated_data.get('currency', 'EUR')
    company = company_for(request.user)

    with transaction.atomic():
        saldo = (
            SaldoEmpresa.objects.select_for_update()
            .filter(empresa=company, moneda_id=currency)
            .first()
        )
        if saldo is None:
            return error_response(
                'CURRENCY_NOT_AVAILABLE',
                'No hay saldo disponible en esa moneda.',
                status.HTTP_400_BAD_REQUEST,
            )
        if amount > saldo.saldo:
            return error_response(
                'INVALID_AMOUNT',
                'El importe no es válido o supera el saldo disponible.',
                status.HTTP_400_BAD_REQUEST,
            )
        saldo.saldo = saldo.saldo - amount
        saldo.save(update_fields=['saldo'])

    return Response(
        {'withdrawn': float(amount), 'currency': currency, 'balance': float(saldo.saldo)},
        status=status.HTTP_200_OK,
    )


@documented(200, 401)
@api_view(['GET'])
@permission_classes([HasCompany])
def balance(request):
    company = company_for(request.user)
    accounts = list(company.saldos.select_related('moneda'))
    accounts.sort(key=lambda saldo: BALANCE_ORDER.get(saldo.moneda_id, 99))

    return Response(
        {
            'company': company.nombre,
            'balances': [
                {'currency': saldo.moneda_id, 'amount': float(saldo.saldo)} for saldo in accounts
            ],
        },
        status=status.HTTP_200_OK,
    )


@documented(200, 400, 401)
@api_view(['POST'])
@permission_classes([HasCompany])
def pay(request):
    serializer = PaymentRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    company = company_for(request.user)

    method_name = PAYMENT_METHOD_TO_CATALOG[data['payment_method']]
    metodo, _ = MetodoPago.objects.get_or_create(
        nombre=method_name, defaults={'id': uuid.uuid4()}
    )
    payment_data = data.get('payment_data', {})
    holder = payment_data.get('holder') or 'Cliente'

    with transaction.atomic():
        info = InformacionPago.objects.create(metodo=metodo, titular=holder)
        if method_name == 'Tarjeta':
            digits = (payment_data.get('card_number') or '')[-4:] or '0000'
            Tarjeta.objects.create(
                informacion=info,
                marca='VISA',
                ultimos4=digits,
                caducidad=payment_data.get('expiry') or '12/30',
                token=f'tok_{uuid.uuid4().hex}',
            )
        elif method_name == 'Transferencia':
            CuentaBancaria.objects.create(
                informacion=info,
                iban=payment_data.get('iban') or 'ES0000000000000000000000',
            )

        reference = f'P-{Transaccion.objects.count() + 1000}'
        while Transaccion.objects.filter(referencia=reference).exists():
            reference = f'P-{int(reference.split("-")[1]) + 1}'

        tx = Transaccion.objects.create(
            receptor=company,
            informacion=info,
            concepto=', '.join(product['name'] for product in data['products']),
            cantidad=Decimal(str(data['total_amount'])),
            moneda=Moneda.objects.get(codigo='EUR'),
            estado=Transaccion.Estado.APROBADA,
            referencia=reference,
        )

    return Response(
        {
            'transaction_id': str(tx.id),
            'status': 'approved',
            'authorized_amount': float(tx.cantidad),
        },
        status=status.HTTP_200_OK,
    )


# ------------------------------------------------------------------- Reembolsos

def refund_queryset(company):
    return (
        Reembolso.objects.filter(transaccion__receptor=company)
        .select_related('transaccion__informacion', 'transaccion__moneda')
        .order_by('-fecha')
    )


@documented(202, 404, 409)
@api_view(['POST'])
@permission_classes([HasCompany])
def refund_request(request):
    company = company_for(request.user)
    transaction_id = parse_uuid(request.query_params.get('transaction_id'))
    transaction_obj = (
        Transaccion.objects.filter(id=transaction_id, receptor=company).first()
        if transaction_id
        else None
    )
    if transaction_obj is None:
        return error_response(
            'TRANSACTION_NOT_FOUND',
            'La transacción indicada no existe o su identificador no es válido.',
            status.HTTP_404_NOT_FOUND,
        )

    if Reembolso.objects.filter(
        transaccion=transaction_obj, estado=Reembolso.Estado.PENDIENTE
    ).exists():
        return error_response(
            'REFUND_ALREADY_PENDING',
            'Ya existe una devolución pendiente para esa transacción.',
            status.HTTP_409_CONFLICT,
        )

    reason = request.query_params.get('reason', '').strip()[:255]
    refund = Reembolso.objects.create(
        transaccion=transaction_obj,
        cantidad=transaction_obj.cantidad,
        motivo=reason or None,
    )

    return Response(
        {
            'request_id': str(refund.id),
            'transaction_id': str(transaction_obj.id),
            'status': 'pending',
        },
        status=status.HTTP_202_ACCEPTED,
    )


def pending_refund_for_company(refund_id, company):
    return (
        Reembolso.objects.select_related('transaccion__moneda')
        .filter(id=refund_id, transaccion__receptor=company)
        .first()
    )


@documented(200, 400, 401, 404)
@api_view(['POST'])
@permission_classes([HasCompany])
def refund_accept(request):
    company = company_for(request.user)
    refund_id = parse_uuid(request.query_params.get('id'))
    refund = pending_refund_for_company(refund_id, company) if refund_id else None
    if refund is None:
        return error_response(
            'REFUND_NOT_FOUND',
            'La devolución indicada no existe o no pertenece a tu empresa.',
            status.HTTP_404_NOT_FOUND,
        )
    if refund.estado != Reembolso.Estado.PENDIENTE:
        return error_response(
            'REFUND_NOT_PENDING', 'La devolución ya está resuelta.', status.HTTP_400_BAD_REQUEST
        )

    currency = refund.transaccion.moneda_id
    with transaction.atomic():
        saldo = (
            SaldoEmpresa.objects.select_for_update()
            .filter(empresa=company, moneda_id=currency)
            .first()
        )
        if saldo is None or refund.cantidad > saldo.saldo:
            return error_response(
                'INSUFFICIENT_BALANCE',
                'El saldo disponible no cubre el importe de la devolución.',
                status.HTTP_400_BAD_REQUEST,
            )
        saldo.saldo = saldo.saldo - refund.cantidad
        saldo.save(update_fields=['saldo'])

        refund.estado = Reembolso.Estado.ACEPTADO
        refund.save(update_fields=['estado'])

        transaction_obj = refund.transaccion
        if refund.cantidad >= transaction_obj.cantidad:
            transaction_obj.estado = Transaccion.Estado.REEMBOLSADA
            transaction_obj.save(update_fields=['estado'])

    return Response(
        {'refund': presenters.refund_payload(refund), 'balance': float(saldo.saldo)},
        status=status.HTTP_200_OK,
    )


@documented(200, 400, 401, 404)
@api_view(['POST'])
@permission_classes([HasCompany])
def refund_reject(request):
    company = company_for(request.user)
    refund_id = parse_uuid(request.query_params.get('id'))
    refund = pending_refund_for_company(refund_id, company) if refund_id else None
    if refund is None:
        return error_response(
            'REFUND_NOT_FOUND',
            'La devolución indicada no existe o no pertenece a tu empresa.',
            status.HTTP_404_NOT_FOUND,
        )
    if refund.estado != Reembolso.Estado.PENDIENTE:
        return error_response(
            'REFUND_NOT_PENDING', 'La devolución ya está resuelta.', status.HTTP_400_BAD_REQUEST
        )

    refund.estado = Reembolso.Estado.RECHAZADO
    refund.save(update_fields=['estado'])

    saldo = SaldoEmpresa.objects.filter(
        empresa=company, moneda_id=refund.transaccion.moneda_id
    ).first()
    return Response(
        {
            'refund': presenters.refund_payload(refund),
            'balance': float(saldo.saldo) if saldo else 0.0,
        },
        status=status.HTTP_200_OK,
    )


@documented(200, 401)
@api_view(['GET'])
@permission_classes([HasCompany])
def refunds(request):
    company = company_for(request.user)
    return Response(
        [presenters.refund_payload(refund) for refund in refund_queryset(company)],
        status=status.HTTP_200_OK,
    )


# -------------------------------------------------------------------- Empresas

@documented(200, 401, 403)
@api_view(['GET'])
@permission_classes([IsAdminRole])
def companies(request):
    return Response(
        [presenters.company_payload(company) for company in Empresa.objects.all()],
        status=status.HTTP_200_OK,
    )


@documented(200, 400, 403)
@api_view(['PUT'])
@permission_classes([IsAdminRole])
def company_add(request):
    serializer = CompanyCreateRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = dict(serializer.validated_data)

    username = data.pop('username').strip()
    password = data.pop('password')
    force_change = data.pop('force_change', True)

    if User.objects.filter(username__iexact=username).exists():
        return error_response(
            'USERNAME_TAKEN', 'Ese nombre de usuario ya existe.', status.HTTP_400_BAD_REQUEST
        )

    with transaction.atomic():
        company = Empresa.objects.create(**data)
        SaldoEmpresa.objects.bulk_create(
            [
                SaldoEmpresa(empresa=company, moneda=moneda, saldo=Decimal('0'))
                for moneda in Moneda.objects.all()
            ]
        )
        user = User.objects.create_user(
            username=username,
            email=data['email'],
            password=password,
            first_name=data['nombre'],
            last_name='',
        )
        PerfilUsuario.objects.create(
            usuario=user,
            rol=PerfilUsuario.Rol.COMERCIO,
            empresa=company,
            force_password_change=force_change,
        )

    payload = presenters.company_payload(company)
    payload['username'] = username
    payload['password'] = password
    return Response(payload, status=status.HTTP_200_OK)


def company_for_admin(company_id):
    company_uuid = parse_uuid(company_id)
    if company_uuid is None:
        return None
    return Empresa.objects.filter(pk=company_uuid).first()


@documented(200, 403, 404)
@api_view(['DELETE'])
@permission_classes([IsAdminRole])
def company_delete(request):
    company = company_for_admin(request.query_params.get('id'))
    if company is None:
        return error_response(
            'COMPANY_NOT_FOUND',
            'La empresa indicada no existe o su identificador no es válido.',
            status.HTTP_404_NOT_FOUND,
        )

    company.estado = Empresa.Estado.BAJA
    company.save(update_fields=['estado'])
    return Response(presenters.company_payload(company), status=status.HTTP_200_OK)


@documented(200, 403, 404)
@api_view(['PUT'])
@permission_classes([IsAdminRole])
def company_reactivate(request):
    company = company_for_admin(request.query_params.get('id'))
    if company is None:
        return error_response(
            'COMPANY_NOT_FOUND',
            'La empresa indicada no existe o su identificador no es válido.',
            status.HTTP_404_NOT_FOUND,
        )

    company.estado = Empresa.Estado.ACTIVA
    company.save(update_fields=['estado'])
    return Response(presenters.company_payload(company), status=status.HTTP_200_OK)


# ---------------------------------------------------------------- Técnicos

def technician_activity(user):
    tickets = Ticket.objects.filter(tecnico=user)
    return {
        'assigned': tickets.count(),
        'open': tickets.filter(estado=Ticket.Estado.ABIERTO).count(),
        'in_progress': tickets.filter(estado=Ticket.Estado.EN_PROCESO).count(),
        'closed': tickets.filter(estado=Ticket.Estado.CERRADO).count(),
    }


@documented(200, 400, 401, 403)
@api_view(['GET', 'POST'])
@permission_classes([IsAdminRole])
def technicians(request):
    if request.method == 'POST':
        serializer = TechnicianCreateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        username = data['username'].strip()
        email = data['email'].strip()

        if User.objects.filter(username__iexact=username).exists():
            return error_response(
                'USERNAME_TAKEN', 'Ese nombre de usuario ya existe.', status.HTTP_400_BAD_REQUEST
            )
        if User.objects.filter(email__iexact=email).exists():
            return error_response(
                'EMAIL_TAKEN', 'Ese correo ya está registrado.', status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=data['password'],
            first_name=data['name'],
            last_name='',
        )
        PerfilUsuario.objects.create(
            usuario=user,
            rol=PerfilUsuario.Rol.TECNICO,
            force_password_change=data.get('force_change', True),
        )

        payload = presenters.technician_payload(user, technician_activity(user))
        payload['password'] = data['password']
        return Response(payload, status=status.HTTP_200_OK)

    users = (
        User.objects.filter(perfil__rol=PerfilUsuario.Rol.TECNICO)
        .select_related('perfil')
        .order_by('first_name', 'last_name')
    )
    return Response(
        [
            presenters.technician_payload(user, technician_activity(user))
            for user in users
        ],
        status=status.HTTP_200_OK,
    )


# --------------------------------------------------------------------- Perfil

COMPANY_PROFILE_FIELDS = (
    'nombre',
    'razon_social',
    'cif',
    'tipo_empresa',
    'actividad_economica',
    'direccion',
    'codigo_postal',
    'ciudad',
    'provincia',
    'pais',
    'telefono',
    'email',
    'web',
)


def profile_response(user):
    role = role_for(user)
    company = company_for(user)
    activity = technician_activity(user) if role == 'tecnico' else None
    return presenters.profile_payload(user, company if role == 'comercio' else None, activity)


@documented(200, 400, 401)
@api_view(['GET', 'PUT'])
def profile(request):
    user = request.user

    if request.method == 'PUT':
        serializer = ProfileUpdateRequestSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if role_for(user) == 'comercio':
            company = company_for(user)
            if company is None:
                return error_response(
                    'COMPANY_REQUIRED',
                    'El usuario no está vinculado a una empresa.',
                    status.HTTP_400_BAD_REQUEST,
                )
            for field in COMPANY_PROFILE_FIELDS:
                if field in data:
                    setattr(company, field, data[field])
            company.save()
        else:
            if 'name' in data:
                user.first_name = data['name']
                user.last_name = ''
            if 'email' in data:
                user.email = data['email']
            user.save()

    return Response(profile_response(user), status=status.HTTP_200_OK)


@documented(200, 400, 401)
@api_view(['POST'])
def profile_password(request):
    serializer = PasswordChangeRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    if not request.user.check_password(serializer.validated_data['current_password']):
        return error_response(
            'INVALID_PASSWORD', 'La contraseña actual no es correcta.', status.HTTP_400_BAD_REQUEST
        )

    request.user.set_password(serializer.validated_data['new_password'])
    request.user.save(update_fields=['password'])
    PerfilUsuario.objects.filter(usuario=request.user).update(force_password_change=False)

    return Response({'message': 'Contraseña actualizada correctamente.'}, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------- Pagos

@documented(200, 401)
@api_view(['GET'])
@permission_classes([HasCompany])
def payments(request):
    company = company_for(request.user)
    queryset = (
        Transaccion.objects.filter(receptor=company)
        .select_related('informacion__metodo', 'moneda')
        .order_by('-fecha')
    )
    return Response(
        [presenters.payment_payload(transaction_obj) for transaction_obj in queryset],
        status=status.HTTP_200_OK,
    )


# --------------------------------------------------------------------- Tickets

def merchant_company(request):
    return company_for(request.user)


def ticket_queryset(request):
    queryset = (
        Ticket.objects.select_related('empresa', 'tecnico')
        .prefetch_related('mensajes__autor', 'historial__autor')
        .order_by('-actualizado')
    )
    if role_for(request.user) == 'comercio':
        queryset = queryset.filter(empresa=merchant_company(request))
    return queryset


@documented(200, 401)
@api_view(['GET'])
def tickets(request):
    return Response(
        [presenters.ticket_payload(ticket) for ticket in ticket_queryset(request)],
        status=status.HTTP_200_OK,
    )


@documented(200, 400, 401)
@api_view(['POST'])
def ticket_add(request):
    serializer = TicketCreateRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    role = role_for(request.user)
    company = merchant_company(request)
    if role != 'comercio':
        company = company_for_admin(data['company_id'])
    if company is None:
        return error_response(
            'COMPANY_REQUIRED',
            'El ticket debe estar asociado a una empresa válida.',
            status.HTTP_400_BAD_REQUEST,
        )

    number = (Ticket.objects.aggregate(max_number=Max('numero'))['max_number'] or 1000) + 1
    ticket = Ticket.objects.create(
        numero=number,
        empresa=company,
        asunto=data['subject'],
        descripcion=data.get('description', ''),
        estado=TICKET_STATUS_TO_DB.get(data.get('status', 'open'), Ticket.Estado.ABIERTO),
    )
    TicketMensaje.objects.create(
        ticket=ticket,
        autor=request.user,
        rol=TicketMensaje.Rol.COMERCIO if role == 'comercio' else TicketMensaje.Rol.TECNICO,
        mensaje=data.get('description') or data['subject'],
    )
    TicketHistorial.objects.create(
        ticket=ticket,
        titulo='Ticket abierto',
        descripcion='Ticket creado por el comercio.',
        autor=request.user,
    )

    return Response(presenters.ticket_payload(ticket), status=status.HTTP_200_OK)


@documented(200, 400, 401, 404)
@api_view(['POST'])
def ticket_message(request):
    ticket = ticket_for(request, request.query_params.get('id'))
    if ticket is None:
        return error_response(
            'TICKET_NOT_FOUND',
            'El ticket indicado no existe o su identificador no es válido.',
            status.HTTP_404_NOT_FOUND,
        )

    serializer = TicketMessageRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    role = 'comercio' if role_for(request.user) == 'comercio' else 'tecnico'
    TicketMensaje.objects.create(
        ticket=ticket,
        autor=request.user,
        rol=TicketMensaje.Rol.COMERCIO if role == 'comercio' else TicketMensaje.Rol.TECNICO,
        mensaje=serializer.validated_data['message'].strip(),
    )
    ticket.save()

    return Response(presenters.ticket_payload(ticket), status=status.HTTP_200_OK)


@documented(200, 400, 401, 403, 404)
@api_view(['PUT'])
def ticket_update(request):
    if role_for(request.user) == 'comercio':
        return error_response(
            'FORBIDDEN',
            'La gestión de tickets está reservada al equipo de soporte.',
            status.HTTP_403_FORBIDDEN,
        )

    ticket = ticket_for(request, request.query_params.get('id'))
    if ticket is None:
        return error_response(
            'TICKET_NOT_FOUND',
            'El ticket indicado no existe o su identificador no es válido.',
            status.HTTP_404_NOT_FOUND,
        )

    serializer = TicketUpdateRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    reply = (data.get('reply') or '').strip()
    new_status = data.get('status')

    if reply:
        TicketMensaje.objects.create(
            ticket=ticket,
            autor=request.user,
            rol=TicketMensaje.Rol.TECNICO,
            mensaje=reply,
        )
        TicketHistorial.objects.create(
            ticket=ticket,
            titulo='Respuesta añadida',
            descripcion=reply,
            autor=request.user,
        )

    if new_status:
        db_status = TICKET_STATUS_TO_DB.get(new_status)
        if db_status and db_status != ticket.estado:
            previous = ticket.estado
            ticket.estado = db_status
            TicketHistorial.objects.create(
                ticket=ticket,
                titulo=f'{dict(Ticket.Estado.choices)[previous]} → {dict(Ticket.Estado.choices)[db_status]}',
                descripcion=(
                    'Incidencia resuelta. El ticket se ha cerrado.'
                    if db_status == Ticket.Estado.CERRADO
                    else 'Estado del ticket actualizado desde el portal de soporte.'
                ),
                autor=request.user,
            )

    ticket.save()
    return Response(presenters.ticket_payload(ticket), status=status.HTTP_200_OK)


@documented(200, 400, 401, 403, 404)
@api_view(['PUT'])
def ticket_assign(request):
    role = role_for(request.user)
    if role not in ('tecnico', 'admin'):
        return error_response(
            'FORBIDDEN',
            'Solo el equipo técnico puede asignar tickets.',
            status.HTTP_403_FORBIDDEN,
        )

    ticket = ticket_for(request, request.query_params.get('id'))
    if ticket is None:
        return error_response(
            'TICKET_NOT_FOUND',
            'El ticket indicado no existe o su identificador no es válido.',
            status.HTTP_404_NOT_FOUND,
        )

    serializer = TicketAssignRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    if data.get('unassign'):
        if ticket.tecnico is None:
            return Response(presenters.ticket_payload(ticket), status=status.HTTP_200_OK)
        if role == 'tecnico' and ticket.tecnico_id != request.user.pk:
            return error_response(
                'FORBIDDEN',
                'Solo puedes desasignarte los tickets que tienes asignados.',
                status.HTTP_403_FORBIDDEN,
            )

        previous = presenters.full_name(ticket.tecnico)
        ticket.tecnico = None
        ticket.save(update_fields=['tecnico', 'actualizado'])
        TicketHistorial.objects.create(
            ticket=ticket,
            titulo='Responsable retirado',
            descripcion=f'{previous} ya no está asignado al ticket.',
            autor=request.user,
        )
        return Response(presenters.ticket_payload(ticket), status=status.HTTP_200_OK)

    if role == 'tecnico':
        technician = request.user
    else:
        try:
            technician_pk = int(data.get('technician_id') or '')
        except (TypeError, ValueError):
            technician_pk = None
        technician = (
            User.objects.filter(
                pk=technician_pk, perfil__rol=PerfilUsuario.Rol.TECNICO, is_active=True
            ).first()
            if technician_pk
            else None
        )
        if technician is None:
            return error_response(
                'TECHNICIAN_NOT_FOUND',
                'El técnico indicado no existe o no está activo.',
                status.HTTP_400_BAD_REQUEST,
            )

    ticket.tecnico = technician
    ticket.save(update_fields=['tecnico', 'actualizado'])
    TicketHistorial.objects.create(
        ticket=ticket,
        titulo='Responsable asignado',
        descripcion=f'Asignado a {presenters.full_name(technician)}.',
        autor=request.user,
    )

    return Response(presenters.ticket_payload(ticket), status=status.HTTP_200_OK)


@documented(200, 401, 404)
@api_view(['DELETE'])
def ticket_delete(request):
    if role_for(request.user) not in ('tecnico', 'admin'):
        return error_response(
            'FORBIDDEN',
            'Solo el equipo técnico puede eliminar tickets.',
            status.HTTP_403_FORBIDDEN,
        )

    ticket = ticket_for(request, request.query_params.get('id'))
    if ticket is None:
        return error_response(
            'TICKET_NOT_FOUND',
            'El ticket indicado no existe o su identificador no es válido.',
            status.HTTP_404_NOT_FOUND,
        )

    ticket.delete()
    return Response({'message': 'Ticket eliminado correctamente.'}, status=status.HTTP_200_OK)
