"""Datos en memoria y reglas de los mocks. No hay base de datos ni lógica de negocio."""

MOCK_BALANCE = 1000.00

MOCK_USERS = {"tpv01": "secret"}

# Identificadores que el mock considera "existentes".
VALID_TRANSACTION_IDS = {"txn_001", "txn_002"}
VALID_TICKET_IDS = {"tkt_001", "tkt_002"}

MOCK_COMPANIES = [
    {"id": "emp_001", "nombre": "Comercio Ejemplo SL", "balance": MOCK_BALANCE},
    {"id": "emp_002", "nombre": "Tienda del Barrio SL", "balance": 450.25},
]

MOCK_PAYMENTS = [
    {
        "transaction_id": "txn_001",
        "amount": 12.50,
        "payment_method": "card",
        "status": "approved",
        "products": [
            {"product_id": "P-123", "name": "Café", "quantity": 2, "unit_price": 1.50}
        ],
        "created_at": "2026-11-17T10:30:00Z",
    },
    {
        "transaction_id": "txn_002",
        "amount": 30.00,
        "payment_method": "cash",
        "status": "approved",
        "products": [
            {"product_id": "P-456", "name": "Libro", "quantity": 1, "unit_price": 30.00}
        ],
        "created_at": "2026-11-17T11:05:00Z",
    },
]

MOCK_REFUNDS = [
    {
        "id": "ref_001",
        "transaction_id": "txn_001",
        "amount": 12.50,
        "status": "pending",
        "reason": "Producto defectuoso",
        "created_at": "2026-11-17T12:00:00Z",
    }
]

MOCK_TICKETS = [
    {
        "id": "tkt_001",
        "company_id": "emp_001",
        "total": 12.50,
        "products": [
            {"product_id": "P-123", "name": "Café", "quantity": 2, "unit_price": 1.50}
        ],
        "issued_at": "2026-11-17T10:30:00Z",
    },
    {
        "id": "tkt_002",
        "company_id": "emp_002",
        "total": 30.00,
        "products": [
            {"product_id": "P-456", "name": "Libro", "quantity": 1, "unit_price": 30.00}
        ],
        "issued_at": "2026-11-17T11:05:00Z",
    },
]
