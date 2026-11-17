"""Datos en memoria y reglas de los mocks.

No hay base de datos: el estado vive en memoria y se pierde al reiniciar el
proceso. Sirve para fijar el contrato mientras no exista el backend definitivo.
"""

from copy import deepcopy

INITIAL_BALANCES = {'EUR': 1250.00, 'USD': 420.00, 'GBP': 180.00}
MOCK_BALANCES = dict(INITIAL_BALANCES)

# Usuarios del sistema. `role` viaja en la respuesta de /login y el token
# (`mock-token-<usuario>`) permite resolver al usuario en cada petición.
MOCK_USERS = {
    "admin": {
        "password": "admin",
        "user": {
            "id": "usr_admin",
            "name": "Laura Martínez",
            "role": "admin",
            "subtitle": "Administradora",
        },
    },
    "tpv01": {
        "password": "secret",
        "user": {
            "id": "usr_tpv01",
            "name": "Laura Martínez",
            "role": "tecnico",
            "subtitle": "Técnica de soporte",
        },
    },
    "comercio": {
        "password": "comercio",
        "user": {
            "id": "usr_comercio",
            "name": "Librería Horizonte",
            "role": "comercio",
            "subtitle": "Comercio",
            "company_id": "emp_001",
            "company_name": "Librería Horizonte",
        },
    },
}

VALID_TRANSACTION_IDS = {
    'txn_001',
    'txn_002',
    'txn_003',
    'txn_004',
    'txn_005',
    'txn_006',
    'txn_007',
}

_INITIAL_COMPANIES = [
    {
        "id": "emp_001",
        "nombre": "Librería Horizonte",
        "balance": INITIAL_BALANCES['EUR'],
        "status": "activo",
        "registered_at": "2026-09-12T09:00:00Z",
    },
    {
        "id": "emp_002",
        "nombre": "Tienda del Barrio SL",
        "balance": 450.25,
        "status": "activo",
        "registered_at": "2026-10-03T09:00:00Z",
    },
    {
        "id": "emp_003",
        "nombre": "Café Central",
        "balance": 0.0,
        "status": "dado-de-baja",
        "registered_at": "2026-08-21T09:00:00Z",
    },
]

MOCK_COMPANIES = deepcopy(_INITIAL_COMPANIES)

MOCK_PAYMENTS = [
    {
        "transaction_id": "txn_001",
        "reference": "P-1048",
        "amount": 42.50,
        "currency": "EUR",
        "client": "Lucía García",
        "invoice": "LH-F2026-1048",
        "payment_method": "card",
        "status": "approved",
        "products": [
            {"product_id": "P-148", "name": "Lecturas y papelería", "quantity": 1, "unit_price": 42.50}
        ],
        "created_at": "2026-11-17T10:42:00Z",
    },
    {
        "transaction_id": "txn_002",
        "reference": "P-1043",
        "amount": 28.90,
        "currency": "EUR",
        "client": "Elena Martín",
        "invoice": "LH-F2026-1043",
        "payment_method": "card",
        "status": "approved",
        "products": [
            {"product_id": "P-143", "name": "Compra duplicada", "quantity": 1, "unit_price": 28.90}
        ],
        "created_at": "2026-11-17T10:20:00Z",
    },
    {
        "transaction_id": "txn_003",
        "reference": "P-1039",
        "amount": 35.00,
        "currency": "EUR",
        "client": "Diego Torres",
        "invoice": "LH-F2026-1039",
        "payment_method": "cash",
        "status": "approved",
        "products": [
            {"product_id": "P-139", "name": "Producto no esperado", "quantity": 1, "unit_price": 35.00}
        ],
        "created_at": "2026-11-16T17:40:00Z",
    },
    {
        "transaction_id": "txn_004",
        "reference": "P-1035",
        "amount": 25.00,
        "currency": "EUR",
        "client": "Ana López",
        "invoice": "LH-F2026-1035",
        "payment_method": "card",
        "status": "approved",
        "products": [
            {"product_id": "P-135", "name": "Devolución de artículos", "quantity": 1, "unit_price": 25.00}
        ],
        "created_at": "2026-11-16T15:12:00Z",
    },
    {
        "transaction_id": "txn_005",
        "reference": "P-1027",
        "amount": 18.50,
        "currency": "EUR",
        "client": "Carlos Ruiz",
        "invoice": "LH-F2026-1027",
        "payment_method": "card",
        "status": "rejected",
        "products": [
            {"product_id": "P-127", "name": "Fuera de plazo", "quantity": 1, "unit_price": 18.50}
        ],
        "created_at": "2026-11-15T09:30:00Z",
    },
    {
        "transaction_id": "txn_006",
        "reference": "P-1046",
        "amount": 120.00,
        "currency": "USD",
        "client": "Marta Vidal",
        "invoice": "LH-F2026-1046",
        "payment_method": "card",
        "status": "approved",
        "products": [
            {"product_id": "P-146", "name": "Pedido internacional", "quantity": 1, "unit_price": 120.00}
        ],
        "created_at": "2026-11-17T09:05:00Z",
    },
    {
        "transaction_id": "txn_007",
        "reference": "P-1041",
        "amount": 75.00,
        "currency": "GBP",
        "client": "Pablo Sanz",
        "invoice": "LH-F2026-1041",
        "payment_method": "transfer",
        "status": "approved",
        "products": [
            {"product_id": "P-141", "name": "Material de oficina", "quantity": 1, "unit_price": 75.00}
        ],
        "created_at": "2026-11-16T08:45:00Z",
    },
]

_INITIAL_REFUNDS = [
    {
        "id": "ref_001",
        "transaction_id": "txn_001",
        "reference": "P-1048",
        "amount": 42.50,
        "currency": "EUR",
        "client": "Lucía García",
        "status": "pending",
        "reason": "Producto no esperado",
        "created_at": "2026-11-17T11:15:00Z",
    },
    {
        "id": "ref_002",
        "transaction_id": "txn_002",
        "reference": "P-1043",
        "amount": 28.90,
        "currency": "EUR",
        "client": "Elena Martín",
        "status": "pending",
        "reason": "Compra duplicada",
        "created_at": "2026-11-17T10:20:00Z",
    },
    {
        "id": "ref_003",
        "transaction_id": "txn_003",
        "reference": "P-1039",
        "amount": 35.00,
        "currency": "EUR",
        "client": "Diego Torres",
        "status": "accepted",
        "reason": "Cancelación del pedido",
        "created_at": "2026-11-16T17:40:00Z",
    },
    {
        "id": "ref_004",
        "transaction_id": "txn_004",
        "reference": "P-1035",
        "amount": 25.00,
        "currency": "EUR",
        "client": "Ana López",
        "status": "accepted",
        "reason": "Devolución de artículos",
        "created_at": "2026-11-16T15:12:00Z",
    },
    {
        "id": "ref_005",
        "transaction_id": "txn_005",
        "reference": "P-1027",
        "amount": 18.50,
        "currency": "EUR",
        "client": "Carlos Ruiz",
        "status": "rejected",
        "reason": "Fuera de plazo",
        "created_at": "2026-11-15T09:30:00Z",
    },
]

MOCK_REFUNDS = deepcopy(_INITIAL_REFUNDS)

_TICKET_SUBJECTS = [
    "Consulta sobre una devolución",
    "Pago pendiente de confirmación",
    "Actualizar datos del comercio",
    "Consulta sobre la comisión de PLP",
    "Revisión de una retirada de saldo",
    "Error al generar la liquidación",
    "Cambio de cuenta bancaria",
    "Devolución no reflejada en el banco",
    "Problema con el terminal TPV",
    "Solicitud de factura mensual",
    "Dudas sobre el plazo de abono",
    "Incidencia al iniciar sesión",
    "Consulta sobre límites de retirada",
]

_TICKET_STATUSES = [
    "open",
    "in_progress",
    "closed",
    "closed",
    "closed",
    "open",
    "in_progress",
    "closed",
    "closed",
    "open",
    "closed",
    "closed",
    "closed",
]

_TECH_REPLIES = [
    "Estamos revisando la incidencia y te confirmamos en cuanto tengamos novedades.",
    "Hemos comprobado la operación y todo apunta a un retraso del banco.",
    "La incidencia está resuelta. Cualquier duda, responde a este mismo ticket.",
]

_STATUS_LABELS = {
    "open": "Abierto",
    "in_progress": "En proceso",
    "closed": "Cerrado",
}


def _build_tickets():
    """Genera los tickets de soporte de Librería Horizonte (deterministas)."""
    tickets = []

    for index, subject in enumerate(_TICKET_SUBJECTS):
        ticket_id = str(1088 - index)
        status = _TICKET_STATUSES[index]
        day = 17 - (index % 4)
        hour = 9 + (index % 8)
        minute = (index * 7) % 60
        created_at = f"2026-11-{day:02d}T{hour:02d}:{minute:02d}:00Z"
        updated_day = min(17, day + (1 if status != "open" else 0))
        updated_at = f"2026-11-{updated_day:02d}T{min(18, hour + 2):02d}:{(minute + 25) % 60:02d}:00Z"

        messages = [
            {
                "id": f"{ticket_id}-m1",
                "author": "Librería Horizonte",
                "role": "comercio",
                "message": f"Hola, necesito ayuda con lo siguiente: {subject.lower()}.",
                "created_at": created_at,
            }
        ]

        if status in ("in_progress", "closed"):
            messages.append(
                {
                    "id": f"{ticket_id}-m2",
                    "author": "Laura Martínez",
                    "role": "tecnico",
                    "message": _TECH_REPLIES[index % len(_TECH_REPLIES)],
                    "created_at": updated_at,
                }
            )

        if status == "closed":
            messages.append(
                {
                    "id": f"{ticket_id}-m3",
                    "author": "Librería Horizonte",
                    "role": "comercio",
                    "message": "Gracias, queda aclarado.",
                    "created_at": updated_at,
                }
            )
            messages.append(
                {
                    "id": f"{ticket_id}-m4",
                    "author": "Laura Martínez",
                    "role": "tecnico",
                    "message": "Confirmamos la resolución y cerramos la consulta. Puedes responder si lo necesitas.",
                    "created_at": updated_at,
                }
            )

        history = [
            {
                "id": f"{ticket_id}-h1",
                "at": created_at,
                "title": "Ticket abierto",
                "description": "Ticket creado por el comercio.",
                "author": "Librería Horizonte",
            }
        ]
        if status != "open":
            history.append(
                {
                    "id": f"{ticket_id}-h2",
                    "at": updated_at,
                    "title": "Abierto → En proceso",
                    "description": "Laura Martínez revisa la consulta.",
                    "author": "Laura Martínez",
                }
            )
        if status == "closed":
            history.append(
                {
                    "id": f"{ticket_id}-h3",
                    "at": updated_at,
                    "title": "En proceso → Cerrado",
                    "description": "Consulta resuelta con el comercio.",
                    "author": "Laura Martínez",
                }
            )

        last_technician_message = next(
            (m["message"] for m in reversed(messages) if m["role"] == "tecnico"), ""
        )

        tickets.append(
            {
                "id": ticket_id,
                "company_id": "emp_001",
                "company_name": "Librería Horizonte",
                "subject": subject,
                "description": (
                    f"{subject}. El comercio ha abierto este ticket para revisar el caso con el "
                    "equipo de soporte de PLP."
                ),
                "status": status,
                "reply": last_technician_message,
                "created_at": created_at,
                "updated_at": updated_at,
                "messages": messages,
                "history": history,
            }
        )

    tickets.append(
        {
            "id": "1075",
            "company_id": "emp_002",
            "company_name": "Tienda del Barrio SL",
            "subject": "Error al confirmar una devolución",
            "description": "La devolución no llega a confirmarse desde el portal.",
            "status": "closed",
            "reply": "Se reenvió la confirmación y quedó resuelta.",
            "created_at": "2026-11-13T09:18:00Z",
            "updated_at": "2026-11-14T16:20:00Z",
            "messages": [
                {
                    "id": "1075-m1",
                    "author": "Tienda del Barrio SL",
                    "role": "comercio",
                    "message": "La devolución no llega a confirmarse desde el portal.",
                    "created_at": "2026-11-13T09:18:00Z",
                },
                {
                    "id": "1075-m2",
                    "author": "Laura Martínez",
                    "role": "tecnico",
                    "message": "Se reenvió la confirmación y quedó resuelta.",
                    "created_at": "2026-11-14T16:20:00Z",
                },
            ],
            "history": [
                {
                    "id": "1075-h1",
                    "at": "2026-11-13T09:18:00Z",
                    "title": "Ticket abierto",
                    "description": "Ticket creado por el comercio.",
                    "author": "Tienda del Barrio SL",
                },
                {
                    "id": "1075-h2",
                    "at": "2026-11-14T16:20:00Z",
                    "title": "Abierto → Cerrado",
                    "description": "Consulta resuelta con el comercio.",
                    "author": "Laura Martínez",
                },
            ],
        }
    )

    return tickets


_INITIAL_TICKETS = _build_tickets()
MOCK_TICKETS = deepcopy(_INITIAL_TICKETS)


def find_ticket(ticket_id):
    """Devuelve el ticket en memoria o None."""
    return next((ticket for ticket in MOCK_TICKETS if ticket["id"] == ticket_id), None)


def find_company(company_id):
    """Devuelve la empresa en memoria o None."""
    return next((company for company in MOCK_COMPANIES if company["id"] == company_id), None)


def company_name(company_id, fallback=""):
    """Nombre de la empresa, o el valor de reserva si no existe."""
    company = find_company(company_id)
    return company["nombre"] if company else fallback


def find_payment(transaction_id):
    """Devuelve el pago en memoria o None."""
    return next(
        (payment for payment in MOCK_PAYMENTS if payment["transaction_id"] == transaction_id),
        None,
    )


def find_refund(transaction_id):
    """Devuelve la devolución pendiente de una transacción, o None."""
    return next(
        (
            refund
            for refund in MOCK_REFUNDS
            if refund["transaction_id"] == transaction_id
        ),
        None,
    )


def reset_mocks():
    """Restaura el estado inicial (útil en tests)."""
    MOCK_BALANCES.clear()
    MOCK_BALANCES.update(INITIAL_BALANCES)
    MOCK_COMPANIES[:] = deepcopy(_INITIAL_COMPANIES)
    MOCK_TICKETS[:] = deepcopy(_INITIAL_TICKETS)
    MOCK_REFUNDS[:] = deepcopy(_INITIAL_REFUNDS)
