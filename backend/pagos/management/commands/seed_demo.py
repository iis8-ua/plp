"""Carga datos de demostración sobre el modelo real (idempotente).

Uso:
    python manage.py seed_demo
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

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
    TransaccionHistorial,
)

User = get_user_model()


def aware(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


class Command(BaseCommand):
    help = 'Crea usuarios, empresas, saldos, pagos, devoluciones y tickets de demostración.'

    def handle(self, *args, **options):
        with transaction.atomic():
            users = self.crear_usuarios()
            empresas = self.crear_empresas()
            self.crear_saldos(empresas)
            metodos = self.crear_metodos()
            self.crear_pagos(empresas['horizonte'], metodos)
            self.crear_devoluciones()
            self.crear_tickets(empresas['horizonte'], empresas['barrio'], users)

        self.stdout.write(self.style.SUCCESS('Datos de demostración cargados.'))

    # ------------------------------------------------------------------ Usuarios

    def crear_usuarios(self):
        definiciones = [
            ('admin', 'admin', 'Laura', 'Martínez', 'admin', None, 'laura.martinez@plp.es'),
            ('tpv01', 'secret', 'Laura', 'Martínez', 'tecnico', None, 'laura.martinez@plp.es'),
            ('comercio', 'comercio', 'Librería', 'Horizonte', 'comercio', 'horizonte', 'contacto@libreriahorizonte.es'),
            ('cruiz', 'tecnico123', 'Carlos', 'Ruiz', 'tecnico', None, 'carlos.ruiz@plp.es'),
            ('dtorres', 'tecnico123', 'Diego', 'Torres', 'tecnico', None, 'diego.torres@plp.es'),
            ('egarcia', 'tecnico123', 'Elena', 'García', 'tecnico', None, 'elena.garcia@plp.es'),
            ('msanchez', 'tecnico123', 'Marta', 'Sánchez', 'tecnico', None, 'marta.sanchez@plp.es'),
            ('promero', 'tecnico123', 'Pablo', 'Romero', 'tecnico', None, 'pablo.romero@plp.es'),
        ]

        usuarios = {}
        for username, password, first_name, last_name, rol, empresa_key, email in definiciones:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                },
            )
            if created:
                user.set_password(password)
                user.save(update_fields=['password'])
            elif not user.email:
                user.email = email
                user.save(update_fields=['email'])
            profile, profile_created = PerfilUsuario.objects.get_or_create(
                usuario=user,
                defaults={'rol': rol},
            )
            if not profile_created:
                PerfilUsuario.objects.filter(pk=profile.pk).update(rol=rol)
            usuarios[username] = user

        return usuarios

    # ------------------------------------------------------------------ Empresas

    def crear_empresas(self):
        definiciones = {
            'horizonte': ('Librería Horizonte', Empresa.Estado.ACTIVA, '2026-09-12T09:00:00Z'),
            'barrio': ('Tienda del Barrio SL', Empresa.Estado.ACTIVA, '2026-10-03T09:00:00Z'),
            'central': ('Café Central', Empresa.Estado.BAJA, '2026-08-21T09:00:00Z'),
        }

        empresas = {}
        for key, (nombre, estado, fecha) in definiciones.items():
            empresa, created = Empresa.objects.get_or_create(
                nombre=nombre, defaults={'estado': estado}
            )
            if created:
                Empresa.objects.filter(pk=empresa.pk).update(fecha_registro=aware(fecha))
            empresas[key] = empresa

        horizonte = empresas['horizonte']
        if not horizonte.razon_social:
            horizonte.razon_social = 'Librería Horizonte, S.L.'
            horizonte.cif = 'B12345678'
            horizonte.tipo_empresa = 'Sociedad limitada'
            horizonte.actividad_economica = 'Comercio al por menor de libros'
            horizonte.direccion = 'Calle de Alcalá, 42 · Local 2'
            horizonte.codigo_postal = '28014'
            horizonte.ciudad = 'Madrid'
            horizonte.provincia = 'Madrid'
            horizonte.pais = 'España'
            horizonte.telefono = '+34 912 345 678'
            horizonte.email = 'contacto@libreriahorizonte.es'
            horizonte.web = 'https://libreriahorizonte.es'
            horizonte.save()

        PerfilUsuario.objects.filter(
            usuario__username='comercio', empresa__isnull=True
        ).update(empresa=empresas['horizonte'])
        return empresas

    def crear_saldos(self, empresas):
        saldos = {
            'horizonte': {'EUR': '1250.00', 'USD': '420.00', 'GBP': '180.00'},
            'barrio': {'EUR': '450.25', 'USD': '0.00', 'GBP': '0.00'},
            'central': {'EUR': '0.00', 'USD': '0.00', 'GBP': '0.00'},
        }

        for key, valores in saldos.items():
            for currency, amount in valores.items():
                SaldoEmpresa.objects.get_or_create(
                    empresa=empresas[key],
                    moneda_id=currency,
                    defaults={'saldo': Decimal(amount)},
                )

    # ------------------------------------------------------------------ Catálogos

    def crear_metodos(self):
        metodos = {}
        for nombre in ('Tarjeta', 'Transferencia', 'Bizum', 'Efectivo'):
            metodo, _ = MetodoPago.objects.get_or_create(nombre=nombre)
            metodos[nombre] = metodo
        return metodos

    # --------------------------------------------------------------------- Pagos

    PAGOS = [
        ('P-1048', 'txn-001', 'Lucía García', 'LH-F2026-1048', '42.50', 'EUR', 'Tarjeta', 'APROBADA', '2026-11-17T10:42:00Z'),
        ('P-1043', 'txn-002', 'Elena Martín', 'LH-F2026-1043', '28.90', 'EUR', 'Tarjeta', 'APROBADA', '2026-11-17T10:20:00Z'),
        ('P-1039', 'txn-003', 'Diego Torres', 'LH-F2026-1039', '35.00', 'EUR', 'Efectivo', 'APROBADA', '2026-11-16T17:40:00Z'),
        ('P-1035', 'txn-004', 'Ana López', 'LH-F2026-1035', '25.00', 'EUR', 'Tarjeta', 'APROBADA', '2026-11-16T15:12:00Z'),
        ('P-1027', 'txn-005', 'Carlos Ruiz', 'LH-F2026-1027', '18.50', 'EUR', 'Tarjeta', 'RECHAZADA', '2026-11-15T09:30:00Z'),
        ('P-1046', 'txn-006', 'Marta Vidal', 'LH-F2026-1046', '120.00', 'USD', 'Tarjeta', 'APROBADA', '2026-11-17T09:05:00Z'),
        ('P-1041', 'txn-007', 'Pablo Sanz', 'LH-F2026-1041', '75.00', 'GBP', 'Transferencia', 'APROBADA', '2026-11-16T08:45:00Z'),
    ]

    def crear_pagos(self, empresa, metodos):
        for referencia, _slug, client, invoice, amount, currency, method, estado, fecha in self.PAGOS:
            tx = Transaccion.objects.filter(referencia=referencia).first()
            if tx is None:
                info = InformacionPago.objects.create(
                    metodo=metodos[method], titular=client
                )
                if method == 'Tarjeta':
                    Tarjeta.objects.create(
                        informacion=info,
                        marca='VISA',
                        ultimos4='1111',
                        caducidad='12/30',
                        token=f'tok_{referencia.lower().replace("-", "_")}',
                    )
                elif method == 'Transferencia':
                    CuentaBancaria.objects.create(
                        informacion=info,
                        iban='ES9121000418450200051332',
                    )

                tx = Transaccion.objects.create(
                    receptor=empresa,
                    informacion=info,
                    concepto=f'Compra {invoice}',
                    cantidad=Decimal(amount),
                    comision=Decimal('0.00'),
                    moneda_id=currency,
                    estado=getattr(Transaccion.Estado, estado),
                    num_factura=invoice,
                    referencia=referencia,
                )
                Transaccion.objects.filter(pk=tx.pk).update(fecha=aware(fecha))

            motivo = 'Pago correcto' if tx.estado == Transaccion.Estado.APROBADA else 'Pago rechazado'
            if not tx.motivo:
                tx.motivo = motivo
                tx.save(update_fields=['motivo'])

            if not tx.historial.exists():
                evento = TransaccionHistorial.objects.create(
                    transaccion=tx,
                    estado=tx.estado,
                    motivo=motivo,
                )
                TransaccionHistorial.objects.filter(pk=evento.pk).update(fecha=aware(fecha))

    # -------------------------------------------------------------- Devoluciones

    DEVOLUCIONES = [
        ('P-1048', '42.50', 'PENDIENTE', 'Producto no esperado', '2026-11-17T11:15:00Z'),
        ('P-1043', '28.90', 'PENDIENTE', 'Compra duplicada', '2026-11-17T10:20:00Z'),
        ('P-1039', '35.00', 'ACEPTADO', 'Cancelación del pedido', '2026-11-16T17:40:00Z'),
        ('P-1035', '25.00', 'ACEPTADO', 'Devolución de artículos', '2026-11-16T15:12:00Z'),
        ('P-1027', '18.50', 'RECHAZADO', 'Fuera de plazo', '2026-11-15T09:30:00Z'),
    ]

    def crear_devoluciones(self):
        for referencia, amount, estado, motivo, fecha in self.DEVOLUCIONES:
            tx = Transaccion.objects.filter(referencia=referencia).first()
            if tx is None:
                continue
            refund, created = Reembolso.objects.get_or_create(
                transaccion=tx,
                motivo=motivo,
                defaults={
                    'cantidad': Decimal(amount),
                    'estado': getattr(Reembolso.Estado, estado),
                },
            )
            if created:
                Reembolso.objects.filter(pk=refund.pk).update(fecha=aware(fecha))

    # ------------------------------------------------------------------- Tickets

    ASUNTOS = [
        'Consulta sobre una devolución',
        'Pago pendiente de confirmación',
        'Actualizar datos del comercio',
        'Consulta sobre la comisión de PLP',
        'Revisión de una retirada de saldo',
        'Error al generar la liquidación',
        'Cambio de cuenta bancaria',
        'Devolución no reflejada en el banco',
        'Problema con el terminal TPV',
        'Solicitud de factura mensual',
        'Dudas sobre el plazo de abono',
        'Incidencia al iniciar sesión',
        'Consulta sobre límites de retirada',
    ]

    ESTADOS = [
        'ABIERTO', 'EN_PROCESO', 'CERRADO', 'CERRADO', 'CERRADO',
        'ABIERTO', 'EN_PROCESO', 'CERRADO', 'CERRADO', 'ABIERTO',
        'CERRADO', 'CERRADO', 'CERRADO',
    ]

    RESPUESTAS = [
        'Estamos revisando la incidencia y te confirmamos en cuanto tengamos novedades.',
        'Hemos comprobado la operación y todo apunta a un retraso del banco.',
        'La incidencia está resuelta. Cualquier duda, responde a este mismo ticket.',
    ]

    def crear_tickets(self, horizonte, barrio, users):
        comercio = users['comercio']
        tecnico = users['tpv01']

        for index, asunto in enumerate(self.ASUNTOS):
            numero = 1088 - index
            if Ticket.objects.filter(numero=numero).exists():
                continue

            estado = getattr(Ticket.Estado, self.ESTADOS[index])
            creado = aware(f'2026-11-{17 - (index % 4):02d}T{9 + (index % 8):02d}:{(index * 7) % 60:02d}:00Z')
            actualizado = creado + timedelta(hours=2)

            ticket = Ticket.objects.create(
                numero=numero,
                empresa=horizonte,
                asunto=asunto,
                descripcion=f'{asunto}. La Librería Horizonte necesita revisar este caso con soporte.',
                estado=estado,
            )
            self.crear_conversacion(ticket, comercio, tecnico, asunto, estado, creado, actualizado)
            Ticket.objects.filter(pk=ticket.pk).update(
                creado=creado, actualizado=actualizado
            )

        if not Ticket.objects.filter(numero=1075).exists():
            ticket = Ticket.objects.create(
                numero=1075,
                empresa=barrio,
                asunto='Error al confirmar una devolución',
                descripcion='La devolución no llega a confirmarse desde el portal.',
                estado=Ticket.Estado.CERRADO,
            )
            self.crear_conversacion(
                ticket,
                users['comercio'],
                tecnico,
                'Error al confirmar una devolución',
                Ticket.Estado.CERRADO,
                aware('2026-11-13T09:18:00Z'),
                aware('2026-11-14T16:20:00Z'),
            )
            Ticket.objects.filter(pk=ticket.pk).update(
                creado=aware('2026-11-13T09:18:00Z'),
                actualizado=aware('2026-11-14T16:20:00Z'),
            )

        asignaciones = {
            1088: 'tpv01',
            1087: 'tpv01',
            1086: 'cruiz',
            1085: 'cruiz',
            1084: 'dtorres',
            1083: 'cruiz',
            1082: 'tpv01',
            1081: 'msanchez',
            1080: 'promero',
            1079: 'egarcia',
            1078: 'dtorres',
            1077: 'egarcia',
        }
        for numero, username in asignaciones.items():
            Ticket.objects.filter(numero=numero, tecnico__isnull=True).update(
                tecnico=users[username]
            )

    def crear_conversacion(self, ticket, comercio, tecnico, asunto, estado, creado, actualizado):
        mensajes = [
            (comercio, TicketMensaje.Rol.COMERCIO, f'Hola, necesito ayuda con: {asunto.lower()}.', creado),
        ]
        if estado in (Ticket.Estado.EN_PROCESO, Ticket.Estado.CERRADO):
            mensajes.append((tecnico, TicketMensaje.Rol.TECNICO, self.RESPUESTAS[ticket.numero % 3], actualizado))
        if estado == Ticket.Estado.CERRADO:
            mensajes.append((comercio, TicketMensaje.Rol.COMERCIO, 'Gracias, queda aclarado.', actualizado))
            mensajes.append((tecnico, TicketMensaje.Rol.TECNICO, 'Confirmamos la resolución y cerramos la consulta.', actualizado))

        for autor, rol, mensaje, fecha in mensajes:
            item = TicketMensaje.objects.create(
                ticket=ticket, autor=autor, rol=rol, mensaje=mensaje
            )
            TicketMensaje.objects.filter(pk=item.pk).update(creado=fecha)

        eventos = [('Ticket abierto', 'Ticket creado por el comercio.', comercio, creado)]
        if estado != Ticket.Estado.ABIERTO:
            eventos.append(('Abierto → En proceso', 'Laura Martínez revisa la consulta.', tecnico, actualizado))
        if estado == Ticket.Estado.CERRADO:
            eventos.append(('En proceso → Cerrado', 'Consulta resuelta con el comercio.', tecnico, actualizado))

        for titulo, descripcion, autor, fecha in eventos:
            evento = TicketHistorial.objects.create(
                ticket=ticket, titulo=titulo, descripcion=descripcion, autor=autor
            )
            TicketHistorial.objects.filter(pk=evento.pk).update(fecha=fecha)
