"""Traducción de modelos a los payloads de ``api/api.yaml``."""

PAYMENT_STATUS = {
    'PENDIENTE': 'pending',
    'APROBADA': 'approved',
    'RECHAZADA': 'rejected',
    'REEMBOLSADA': 'refunded',
}

REFUND_STATUS = {
    'PENDIENTE': 'pending',
    'ACEPTADO': 'accepted',
    'RECHAZADO': 'rejected',
}

TICKET_STATUS = {
    'ABIERTO': 'open',
    'EN_PROCESO': 'in_progress',
    'CERRADO': 'closed',
}

PAYMENT_METHODS = {
    'Tarjeta': 'card',
    'Transferencia': 'transfer',
    'Bizum': 'bizum',
    'Efectivo': 'cash',
}

ROLE_SUBTITLES = {
    'admin': 'Administrador',
    'tecnico': 'Técnica de soporte',
    'comercio': 'Comercio',
}


def iso(value):
    if not value:
        return ''
    return value.isoformat().replace('+00:00', 'Z')


def full_name(user):
    if user is None:
        return ''
    return user.get_full_name() or user.username


def user_payload(user):
    profile = getattr(user, 'perfil', None)
    role = profile.rol if profile else 'tecnico'
    company = profile.empresa if profile else None
    payload = {
        'id': str(user.pk),
        'name': full_name(user),
        'role': role,
        'subtitle': ROLE_SUBTITLES.get(role, ''),
        'force_password_change': bool(getattr(profile, 'force_password_change', False)),
    }
    if company:
        payload['company_id'] = str(company.pk)
        payload['company_name'] = company.nombre
    return payload


def payment_payload(tx):
    info = tx.informacion
    return {
        'transaction_id': str(tx.id),
        'reference': tx.referencia or '',
        'client': info.titular,
        'invoice': tx.num_factura or '',
        'concept': tx.concepto,
        'amount': float(tx.cantidad),
        'currency': tx.moneda_id,
        'payment_method': PAYMENT_METHODS.get(info.metodo.nombre, info.metodo.nombre.lower()),
        'status': PAYMENT_STATUS.get(tx.estado, tx.estado.lower()),
        'created_at': iso(tx.fecha),
    }


def refund_payload(refund):
    tx = refund.transaccion
    return {
        'id': str(refund.id),
        'transaction_id': str(tx.id),
        'reference': tx.referencia or '',
        'client': tx.informacion.titular,
        'amount': float(refund.cantidad),
        'currency': tx.moneda_id,
        'reason': refund.motivo or '',
        'status': REFUND_STATUS.get(refund.estado, refund.estado.lower()),
        'created_at': iso(refund.fecha),
    }


def company_payload(company):
    return {
        'id': str(company.pk),
        'nombre': company.nombre,
        'status': company.estado,
        'registered_at': iso(company.fecha_registro),
        'razon_social': company.razon_social,
        'cif': company.cif,
        'tipo_empresa': company.tipo_empresa,
        'actividad_economica': company.actividad_economica,
        'direccion': company.direccion,
        'codigo_postal': company.codigo_postal,
        'ciudad': company.ciudad,
        'provincia': company.provincia,
        'pais': company.pais,
        'telefono': company.telefono,
        'email': company.email,
        'web': company.web,
    }


def assignee_payload(user):
    if user is None:
        return None
    return {'id': str(user.pk), 'name': full_name(user)}


def technician_payload(user, activity=None):
    return {
        'id': str(user.pk),
        'name': full_name(user),
        'email': user.email,
        'username': user.username,
        'role': 'tecnico',
        'status': 'Activo' if user.is_active else 'Inactivo',
        'activity': activity
        or {'assigned': 0, 'in_progress': 0, 'closed': 0, 'open': 0},
    }


def profile_payload(user, company=None, activity=None):
    profile = getattr(user, 'perfil', None)
    role = profile.rol if profile else 'tecnico'
    payload = {
        'id': str(user.pk),
        'name': full_name(user),
        'email': user.email,
        'username': user.username,
        'role': role,
        'status': 'Activo' if user.is_active else 'Inactivo',
        'company': company_payload(company) if company else None,
        'activity': activity,
        'force_password_change': bool(getattr(profile, 'force_password_change', False)),
    }
    return payload


def message_payload(message):
    return {
        'id': str(message.pk),
        'author': full_name(message.autor),
        'role': message.rol,
        'message': message.mensaje,
        'created_at': iso(message.creado),
    }


def history_payload(event):
    return {
        'id': str(event.pk),
        'at': iso(event.fecha),
        'title': event.titulo,
        'description': event.descripcion,
        'author': full_name(event.autor),
    }


def ticket_payload(ticket):
    messages = [message_payload(message) for message in ticket.mensajes.all()]
    last_reply = next(
        (message['message'] for message in reversed(messages) if message['role'] == 'tecnico'),
        '',
    )
    return {
        'id': str(ticket.numero),
        'company_id': str(ticket.empresa_id),
        'company_name': ticket.empresa.nombre,
        'subject': ticket.asunto,
        'description': ticket.descripcion,
        'status': TICKET_STATUS.get(ticket.estado, ticket.estado.lower()),
        'reply': last_reply,
        'assignee': assignee_payload(ticket.tecnico),
        'created_at': iso(ticket.creado),
        'updated_at': iso(ticket.actualizado),
        'messages': messages,
        'history': [history_payload(event) for event in ticket.historial.all()],
    }
