"""Modelo de datos de pagos y transacciones.

Traduce a Django el esquema ``Grupo05-TPV-Especificacion/pasarela_pagos.sql``.
Cada modelo vive en su propio módulo y se reexporta aquí: Django descubre los
modelos al importar ``api.models`` y el resto del código puede seguir usando
``from api.models import Transaccion``.

Diferencias inevitables respecto al SQL de referencia:

* Los UUID se guardan con ``UUIDField``: en MySQL eso es ``char(32)`` sin
  guiones, no ``CHAR(36)``.
* ``ENUM`` y ``TINYINT`` no tienen tipo nativo en Django; se modelan con
  ``CharField`` + ``choices`` y ``PositiveSmallIntegerField`` respectivamente.
* Las fechas usan ``auto_now_add`` (se rellenan al insertar desde el ORM), por
  lo que el DDL no incluye ``DEFAULT CURRENT_TIMESTAMP``.
"""

# Se importan en orden de dependencias.
from .moneda import Moneda
from .metodo_pago import MetodoPago
from .empresa import Empresa
from .informacion_pago import InformacionPago
from .tarjeta import Tarjeta
from .cuenta_bancaria import CuentaBancaria
from .transaccion import Transaccion
from .reembolso import Reembolso
from .saldo_empresa import SaldoEmpresa

__all__ = [
    'CuentaBancaria',
    'Empresa',
    'InformacionPago',
    'MetodoPago',
    'Moneda',
    'Reembolso',
    'SaldoEmpresa',
    'Tarjeta',
    'Transaccion',
]
