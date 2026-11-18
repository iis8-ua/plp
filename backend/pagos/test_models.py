"""Tests del modelo de datos de pagos y transacciones.

La suite se ejecuta sobre SQLite (igual que el resto de `api`), que también
aplica los CHECK y las FK, así que las restricciones del esquema se prueban de
verdad contra la base de datos.
"""

from decimal import Decimal

from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase

from .models import (
    CuentaBancaria,
    Empresa,
    InformacionPago,
    MetodoPago,
    Moneda,
    Reembolso,
    SaldoEmpresa,
    Tarjeta,
    Transaccion,
)


class CatalogosInicialesTests(TestCase):
    def test_metodos_de_pago_sembrados(self):
        self.assertEqual(
            list(MetodoPago.objects.values_list('nombre', flat=True)),
            ['Bizum', 'Tarjeta', 'Transferencia'],
        )

    def test_monedas_sembradas(self):
        self.assertEqual(
            list(Moneda.objects.values_list('codigo', 'decimales')),
            [('EUR', 2), ('GBP', 2), ('USD', 2)],
        )


class ModeloPagosTests(TestCase):
    def setUp(self):
        self.metodo = MetodoPago.objects.get(nombre='Tarjeta')
        self.eur = Moneda.objects.get(codigo='EUR')
        self.usd = Moneda.objects.get(codigo='USD')
        self.empresa = Empresa.objects.create(nombre='Comercio Ejemplo SL')
        self.otra_empresa = Empresa.objects.create(nombre='Tienda del Barrio SL')
        self.info = self.crear_info('Ana Pérez')
        self.tarjeta = Tarjeta.objects.create(
            informacion=self.info,
            marca='VISA',
            ultimos4='1111',
            caducidad='12/30',
            token='tok_ana',
        )

    def crear_info(self, titular='Titular'):
        return InformacionPago.objects.create(metodo=self.metodo, titular=titular)

    def crear_transaccion(self, **kwargs):
        datos = {
            'receptor': self.empresa,
            'informacion': self.info,
            'concepto': 'Compra',
            'cantidad': Decimal('10.00'),
            'moneda': self.eur,
        }
        datos.update(kwargs)
        return Transaccion.objects.create(**datos)

    # ------------------------------------------------------------ Transacciones

    def test_estado_por_defecto(self):
        transaccion = self.crear_transaccion()

        self.assertEqual(transaccion.estado, Transaccion.Estado.PENDIENTE)
        self.assertEqual(transaccion.comision, Decimal('0'))
        self.assertIsNotNone(transaccion.fecha)
        self.assertIsNone(transaccion.num_factura)

    def test_cantidad_debe_ser_positiva(self):
        for cantidad in ('0', '-5'):
            with self.subTest(cantidad=cantidad):
                with self.assertRaises(IntegrityError), transaction.atomic():
                    self.crear_transaccion(cantidad=Decimal(cantidad))

    def test_comision_no_puede_ser_negativa(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.crear_transaccion(comision=Decimal('-0.01'))

    def test_comision_no_puede_superar_la_cantidad(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.crear_transaccion(comision=Decimal('10.01'))

        al_limite = self.crear_transaccion(comision=Decimal('10.00'))
        self.assertEqual(al_limite.comision, al_limite.cantidad)

    def test_informacion_de_pago_es_unica_por_transaccion(self):
        self.crear_transaccion()

        with self.assertRaises(IntegrityError), transaction.atomic():
            self.crear_transaccion(concepto='Otra compra')

    def test_factura_unica_por_empresa(self):
        self.crear_transaccion(num_factura='F-001')

        with self.assertRaises(IntegrityError), transaction.atomic():
            self.crear_transaccion(
                informacion=self.crear_info('Otro titular'),
                num_factura='F-001',
            )

        # La numeración es independiente en cada empresa.
        otra = self.crear_transaccion(
            receptor=self.otra_empresa,
            informacion=self.crear_info('Tercero'),
            num_factura='F-001',
        )
        self.assertEqual(otra.num_factura, 'F-001')

    def test_varias_facturas_nulas_no_colisionan(self):
        self.crear_transaccion()

        for titular in ('Segundo', 'Tercero'):
            with self.subTest(titular=titular):
                transaccion = self.crear_transaccion(
                    informacion=self.crear_info(titular), num_factura=None
                )
                self.assertIsNone(transaccion.num_factura)

        self.assertEqual(Transaccion.objects.count(), 3)

    def test_borrar_empresa_con_transacciones_esta_protegido(self):
        self.crear_transaccion()

        with self.assertRaises(ProtectedError):
            self.empresa.delete()

    # ------------------------------------------------------------------- Tarjetas

    def test_token_de_tarjeta_unico(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Tarjeta.objects.create(
                informacion=self.crear_info('Otro titular'),
                marca='VISA',
                ultimos4='2222',
                caducidad='01/31',
                token='tok_ana',
            )

    def test_borrado_en_cascada_de_tarjeta(self):
        tarjeta_id = self.tarjeta.pk

        self.info.delete()

        self.assertFalse(Tarjeta.objects.filter(pk=tarjeta_id).exists())
        self.assertFalse(InformacionPago.objects.filter(pk=tarjeta_id).exists())

    def test_cuenta_bancaria_comparte_pk_con_su_informacion(self):
        info = self.crear_info('Luis Gómez')
        cuenta = CuentaBancaria.objects.create(
            informacion=info, iban='ES9121000418450200051332'
        )

        self.assertEqual(cuenta.pk, info.pk)
        self.assertEqual(info.cuenta_bancaria.iban, 'ES9121000418450200051332')
        self.assertEqual(CuentaBancaria.objects.get(pk=info.pk), cuenta)

    # -------------------------------------------------------------------- Saldos

    def test_saldo_pk_compuesta(self):
        eur = SaldoEmpresa.objects.create(
            empresa=self.empresa, moneda=self.eur, saldo=Decimal('10.00')
        )
        usd = SaldoEmpresa.objects.create(
            empresa=self.empresa, moneda=self.usd, saldo=Decimal('5.00')
        )

        self.assertEqual(eur.pk, (self.empresa.pk, 'EUR'))
        self.assertEqual(SaldoEmpresa.objects.get(pk=(self.empresa.pk, 'EUR')), eur)
        self.assertEqual(usd.saldo, Decimal('5.00'))

        with self.assertRaises(IntegrityError), transaction.atomic():
            SaldoEmpresa.objects.create(
                empresa=self.empresa, moneda=self.eur, saldo=Decimal('1.00')
            )

    def test_saldo_no_puede_ser_negativo(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            SaldoEmpresa.objects.create(
                empresa=self.empresa, moneda=self.eur, saldo=Decimal('-0.01')
            )

    # ---------------------------------------------------------------- Reembolsos

    def test_reembolso_pendiente_y_cantidad_positiva(self):
        transaccion = self.crear_transaccion()
        reembolso = Reembolso.objects.create(
            transaccion=transaccion, cantidad=Decimal('5.00')
        )

        self.assertEqual(reembolso.estado, Reembolso.Estado.PENDIENTE)
        self.assertIsNone(reembolso.motivo)

        with self.assertRaises(IntegrityError), transaction.atomic():
            Reembolso.objects.create(transaccion=transaccion, cantidad=Decimal('0'))

    # ----------------------------------------------------------------- Catálogos

    def test_nombre_de_metodo_de_pago_unico(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            MetodoPago.objects.create(nombre='Tarjeta')
