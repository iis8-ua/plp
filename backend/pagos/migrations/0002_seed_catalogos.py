"""Carga los catálogos iniciales definidos en ``pasarela_pagos.sql``.

Los UUID son fijos para que la migración sea idempotente y reproducible en
cualquier entorno (el SQL original usaba ``UUID()``, que genera valores
distintos en cada ejecución).
"""

from django.db import migrations

METODOS_PAGO = [
    ('f47ac10b-58cc-4372-a567-0e02b2c3d479', 'Tarjeta'),
    ('6fa459ea-ee8a-4ca4-894e-db77e160355e', 'Transferencia'),
    ('16fd2706-8baf-433b-82eb-8c7fada847da', 'Bizum'),
]

MONEDAS = [
    ('EUR', 'Euro', 2),
    ('USD', 'Dólar estadounidense', 2),
    ('GBP', 'Libra esterlina', 2),
]


def crear_catalogos(apps, schema_editor):
    MetodoPago = apps.get_model('pagos', 'MetodoPago')
    Moneda = apps.get_model('pagos', 'Moneda')

    for id_, nombre in METODOS_PAGO:
        MetodoPago.objects.get_or_create(id=id_, defaults={'nombre': nombre})

    for codigo, nombre, decimales in MONEDAS:
        Moneda.objects.get_or_create(
            codigo=codigo,
            defaults={'nombre': nombre, 'decimales': decimales},
        )


def borrar_catalogos(apps, schema_editor):
    MetodoPago = apps.get_model('pagos', 'MetodoPago')
    Moneda = apps.get_model('pagos', 'Moneda')

    MetodoPago.objects.filter(id__in=[id_ for id_, _ in METODOS_PAGO]).delete()
    Moneda.objects.filter(codigo__in=[codigo for codigo, _, _ in MONEDAS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('pagos', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(crear_catalogos, borrar_catalogos),
    ]
