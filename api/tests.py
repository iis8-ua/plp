"""Tests de la API contra el modelo de datos real."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from pagos.models import (
    Empresa,
    Reembolso,
    SaldoEmpresa,
    Ticket,
    Transaccion,
)


class ApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_demo', verbosity=0)
        cls.tokens = {
            user: Token.objects.get_or_create(
                user=get_user_model().objects.get(username=user)
            )[0].key
            for user in ('admin', 'tpv01', 'comercio')
        }

    def setUp(self):
        self.client = APIClient()

    def login(self, user):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.tokens[user]}')

    # ------------------------------------------------------------------ Auth

    def test_login(self):
        self.assertEqual(self.client.post('/login').status_code, 400)
        self.assertEqual(
            self.client.post('/login?user=tpv01', {'password': 'bad'}, format='json').status_code,
            401,
        )

        response = self.client.post(
            '/login?user=comercio', {'password': 'comercio'}, format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['token_type'], 'Bearer')
        self.assertEqual(response.data['user']['role'], 'comercio')
        self.assertEqual(response.data['user']['name'], 'Librería Horizonte')
        self.assertEqual(response.data['user']['company_name'], 'Librería Horizonte')

    def test_login_roles(self):
        admin = self.client.post('/login?user=admin', {'password': 'admin'}, format='json')
        self.assertEqual(admin.data['user']['role'], 'admin')
        self.assertNotIn('company_id', admin.data['user'])

        tecnico = self.client.post('/login?user=tpv01', {'password': 'secret'}, format='json')
        self.assertEqual(tecnico.data['user']['role'], 'tecnico')

    def test_logout_invalidates_token(self):
        self.assertEqual(self.client.post('/logout').status_code, 401)

        self.login('comercio')
        self.assertEqual(self.client.post('/logout').status_code, 200)
        self.assertEqual(self.client.get('/balance').status_code, 401)

    # ---------------------------------------------------------------- Caja

    def test_balance_is_scoped_to_company(self):
        self.assertEqual(self.client.get('/balance').status_code, 401)

        self.login('comercio')
        response = self.client.get('/balance')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['company'], 'Librería Horizonte')
        self.assertEqual(
            [(item['currency'], item['amount']) for item in response.data['balances']],
            [('EUR', 1250.0), ('USD', 420.0), ('GBP', 180.0)],
        )

        self.login('admin')
        self.assertEqual(self.client.get('/balance').status_code, 403)

    def test_withdraw_by_currency(self):
        self.login('comercio')

        self.assertEqual(self.client.post('/withdraw').status_code, 400)
        self.assertEqual(
            self.client.post('/withdraw?amount=2000&currency=EUR').status_code, 400
        )
        self.assertEqual(
            self.client.post('/withdraw?amount=10&currency=CHF').status_code, 400
        )

        eur = self.client.post('/withdraw?amount=10&currency=EUR')
        self.assertEqual(eur.status_code, 200)
        self.assertEqual(eur.data['balance'], 1240.0)

        usd = self.client.post('/withdraw?amount=20&currency=USD')
        self.assertEqual(usd.status_code, 200)
        self.assertEqual(usd.data['balance'], 400.0)

        saldo = SaldoEmpresa.objects.get(
            empresa__nombre='Librería Horizonte', moneda_id='EUR'
        )
        self.assertEqual(saldo.saldo, Decimal('1240.00'))

    # --------------------------------------------------------------- Pagos

    def test_payments_are_scoped_and_numeric(self):
        self.login('comercio')
        response = self.client.get('/payments')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 7)

        first = response.data[0]
        self.assertEqual(first['reference'], 'P-1048')
        self.assertEqual(first['client'], 'Lucía García')
        self.assertEqual(first['invoice'], 'LH-F2026-1048')
        self.assertEqual(first['concept'], 'Compra LH-F2026-1048')
        self.assertIsInstance(first['amount'], float)
        self.assertEqual(first['currency'], 'EUR')
        self.assertEqual(first['status'], 'approved')

        self.login('admin')
        self.assertEqual(self.client.get('/payments').status_code, 403)

    def test_payment_statuses_are_exposed(self):
        self.login('comercio')
        response = self.client.get('/payments')
        statuses = {payment['reference']: payment['status'] for payment in response.data}
        self.assertEqual(statuses['P-1027'], 'rejected')

    def test_pay_creates_real_transaction(self):
        self.login('comercio')
        before = Transaccion.objects.count()

        response = self.client.post(
            '/pay',
            {
                'total_amount': 12.5,
                'payment_method': 'card',
                'products': [
                    {'product_id': 'P-1', 'name': 'Café', 'quantity': 1, 'unit_price': 12.5}
                ],
                'payment_data': {'card_number': '4111111111111111', 'holder': 'Ana Pérez'},
            },
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'approved')
        self.assertEqual(Transaccion.objects.count(), before + 1)

    # ---------------------------------------------------------- Devoluciones

    def test_refunds_are_scoped_and_include_payment_data(self):
        self.login('comercio')
        response = self.client.get('/refunds')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 5)

        first = response.data[0]
        self.assertEqual(first['reference'], 'P-1048')
        self.assertEqual(first['client'], 'Lucía García')
        self.assertEqual(first['currency'], 'EUR')
        self.assertEqual(first['status'], 'pending')

    def test_refund_request_creates_and_prevents_duplicates(self):
        self.login('comercio')
        tx = Transaccion.objects.get(referencia='P-1046')

        created = self.client.post(
            f'/refunds/request?transaction_id={tx.id}&reason=Motivo%20de%20prueba'
        )
        self.assertEqual(created.status_code, 202)
        self.assertEqual(len(self.client.get('/refunds').data), 6)

        duplicate = self.client.post(f'/refunds/request?transaction_id={tx.id}')
        self.assertEqual(duplicate.status_code, 409)

    def test_refund_accept_discounts_balance(self):
        self.login('comercio')
        refund = Reembolso.objects.get(
            transaccion__referencia='P-1048', estado=Reembolso.Estado.PENDIENTE
        )

        response = self.client.post(f'/refunds/accept?id={refund.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['refund']['status'], 'accepted')
        self.assertEqual(response.data['balance'], 1207.5)

        saldo = SaldoEmpresa.objects.get(
            empresa__nombre='Librería Horizonte', moneda_id='EUR'
        )
        self.assertEqual(saldo.saldo, Decimal('1207.50'))

        refund.refresh_from_db()
        self.assertEqual(refund.estado, Reembolso.Estado.ACEPTADO)
        self.assertEqual(
            refund.transaccion.estado, Transaccion.Estado.REEMBOLSADA
        )

        self.assertEqual(
            self.client.post(f'/refunds/accept?id={refund.id}').status_code, 400
        )

    def test_refund_reject_keeps_balance(self):
        self.login('comercio')
        refund = Reembolso.objects.get(
            transaccion__referencia='P-1043', estado=Reembolso.Estado.PENDIENTE
        )

        response = self.client.post(f'/refunds/reject?id={refund.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['refund']['status'], 'rejected')

        saldo = SaldoEmpresa.objects.get(
            empresa__nombre='Librería Horizonte', moneda_id='EUR'
        )
        self.assertEqual(saldo.saldo, Decimal('1250.00'))

    def test_refund_of_other_company_is_hidden(self):
        self.login('comercio')
        refund = Reembolso.objects.filter(
            transaccion__receptor__nombre='Librería Horizonte'
        ).first()
        Empresa.objects.get(nombre='Tienda del Barrio SL')
        self.assertIsNotNone(refund)

        # Un id inexistente devuelve 404 sin filtrar información.
        self.assertEqual(
            self.client.post('/refunds/accept?id=00000000-0000-0000-0000-000000000000').status_code,
            404,
        )

    # ------------------------------------------------------------- Empresas

    def test_companies_require_admin_role(self):
        self.assertEqual(self.client.get('/companies').status_code, 401)

        self.login('tpv01')
        self.assertEqual(self.client.get('/companies').status_code, 403)

        self.login('admin')
        response = self.client.get('/companies')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

    def test_company_add_delete_and_reactivate(self):
        self.login('admin')

        created = self.client.put(
            '/companies/add',
            {
                'nombre': 'Prueba',
                'razon_social': 'Prueba, S.L.',
                'cif': 'B00000000',
                'tipo_empresa': 'Sociedad limitada',
                'actividad_economica': 'Comercio',
                'direccion': 'Calle Prueba 1',
                'codigo_postal': '28001',
                'ciudad': 'Madrid',
                'provincia': 'Madrid',
                'pais': 'España',
                'telefono': '+34 600 000 000',
                'email': 'prueba@example.com',
            },
            format='json',
        )
        self.assertEqual(created.status_code, 200)
        company_id = created.data['id']
        self.assertEqual(created.data['status'], 'activo')
        self.assertEqual(created.data['razon_social'], 'Prueba, S.L.')
        self.assertEqual(
            SaldoEmpresa.objects.filter(empresa_id=company_id).count(), 3
        )

        deleted = self.client.delete(f'/companies/delete?id={company_id}')
        self.assertEqual(deleted.status_code, 200)
        self.assertEqual(deleted.data['status'], 'dado-de-baja')

        reactivated = self.client.put(f'/companies/reactivate?id={company_id}')
        self.assertEqual(reactivated.status_code, 200)
        self.assertEqual(reactivated.data['status'], 'activo')

        self.assertEqual(self.client.delete('/companies/delete?id=nope').status_code, 404)

        self.assertEqual(
            self.client.put('/companies/add', {}, format='json').status_code, 400
        )

    # -------------------------------------------------------------- Tickets

    def test_tickets_are_scoped_by_company(self):
        self.login('comercio')
        merchant = self.client.get('/tickets')
        self.assertEqual(merchant.status_code, 200)
        self.assertEqual(len(merchant.data), 13)
        self.assertTrue(all(ticket['company_name'] == 'Librería Horizonte' for ticket in merchant.data))

        self.login('tpv01')
        technician = self.client.get('/tickets')
        self.assertEqual(len(technician.data), 14)

    def test_ticket_create_message_and_detail(self):
        self.login('comercio')
        created = self.client.post(
            '/ticket/add',
            {
                'company_id': str(Empresa.objects.get(nombre='Librería Horizonte').id),
                'subject': 'Consulta de prueba',
                'description': 'Detalle de la consulta',
            },
            format='json',
        )
        self.assertEqual(created.status_code, 200)
        self.assertEqual(created.data['id'], '1089')
        self.assertEqual(len(created.data['messages']), 1)

        updated = self.client.post(
            '/ticket/message?id=1089',
            {'message': '¿Alguna novedad?'},
            format='json',
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.data['messages'][-1]['role'], 'comercio')

        # El comercio no puede escribir en tickets de otra empresa.
        self.assertEqual(
            self.client.post(
                '/ticket/message?id=1075', {'message': 'Hola'}, format='json'
            ).status_code,
            404,
        )

    def test_ticket_update_and_delete_require_staff(self):
        self.login('comercio')
        self.assertEqual(
            self.client.put('/ticket/update?id=1086', {'status': 'closed'}, format='json').status_code,
            403,
        )

        self.login('tpv01')
        updated = self.client.put(
            '/ticket/update?id=1086',
            {'status': 'closed', 'reply': 'Incidencia resuelta.'},
            format='json',
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.data['status'], 'closed')
        self.assertEqual(updated.data['messages'][-1]['role'], 'tecnico')

        self.assertEqual(self.client.delete('/ticket/delete?id=1076').status_code, 200)
        self.assertEqual(self.client.delete('/ticket/delete?id=1076').status_code, 404)

        self.login('comercio')
        self.assertEqual(self.client.delete('/ticket/delete?id=1077').status_code, 403)

        self.login('admin')
        self.assertEqual(self.client.delete('/ticket/delete?id=1077').status_code, 200)
        self.assertFalse(Ticket.objects.filter(numero=1077).exists())

    def test_ticket_assignment(self):
        self.login('admin')
        carlos = get_user_model().objects.get(username='cruiz')
        assigned = self.client.put(
            '/ticket/assign?id=1088',
            {'technician_id': str(carlos.pk)},
            format='json',
        )
        self.assertEqual(assigned.status_code, 200)
        self.assertEqual(assigned.data['assignee']['name'], 'Carlos Ruiz')

        self.login('tpv01')
        self_assign = self.client.put('/ticket/assign?id=1076', {}, format='json')
        self.assertEqual(self_assign.status_code, 200)
        self.assertEqual(self_assign.data['assignee']['name'], 'Laura Martínez')

        self.login('comercio')
        self.assertEqual(
            self.client.put('/ticket/assign?id=1088', {}, format='json').status_code,
            403,
        )

    def test_technicians_list_and_create(self):
        self.login('tpv01')
        self.assertEqual(self.client.get('/technicians').status_code, 403)

        self.login('admin')
        listed = self.client.get('/technicians')
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(len(listed.data), 6)
        self.assertEqual(len({item['email'] for item in listed.data}), 6)

        created = self.client.post(
            '/technicians',
            {
                'name': 'Ana López',
                'email': 'ana.lopez@plp.es',
                'username': 'alopez',
                'password': 'PLP!Ana2026#',
                'force_change': True,
            },
            format='json',
        )
        self.assertEqual(created.status_code, 200)
        self.assertEqual(created.data['username'], 'alopez')
        self.assertEqual(created.data['password'], 'PLP!Ana2026#')
        self.assertEqual(len(self.client.get('/technicians').data), 7)

        duplicate = self.client.post(
            '/technicians',
            {
                'name': 'Otra',
                'email': 'otra@plp.es',
                'username': 'alopez',
                'password': 'PLP!Ana2026#',
            },
            format='json',
        )
        self.assertEqual(duplicate.status_code, 400)

    def test_profile_by_role(self):
        self.login('comercio')
        profile = self.client.get('/profile')
        self.assertEqual(profile.status_code, 200)
        self.assertEqual(profile.data['company']['nombre'], 'Librería Horizonte')
        self.assertEqual(profile.data['company']['cif'], 'B12345678')

        updated = self.client.put(
            '/profile',
            {'nombre': 'Librería Horizonte Centro', 'telefono': '+34 910 000 000'},
            format='json',
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.data['company']['nombre'], 'Librería Horizonte Centro')
        self.assertEqual(updated.data['company']['telefono'], '+34 910 000 000')

        self.login('tpv01')
        technician = self.client.get('/profile')
        self.assertEqual(technician.data['role'], 'tecnico')
        self.assertIn('activity', technician.data)
        self.assertIn('assigned', technician.data['activity'])

        renamed = self.client.put(
            '/profile',
            {'name': 'Laura M. Martínez', 'email': 'laura@plp.es'},
            format='json',
        )
        self.assertEqual(renamed.status_code, 200)
        self.assertEqual(renamed.data['name'], 'Laura M. Martínez')
        self.assertEqual(renamed.data['email'], 'laura@plp.es')

    def test_profile_password_change(self):
        self.login('comercio')
        wrong = self.client.post(
            '/profile/password',
            {'current_password': 'nope', 'new_password': 'NuevaClave123'},
            format='json',
        )
        self.assertEqual(wrong.status_code, 400)

        changed = self.client.post(
            '/profile/password',
            {'current_password': 'comercio', 'new_password': 'NuevaClave123'},
            format='json',
        )
        self.assertEqual(changed.status_code, 200)

        self.assertEqual(
            self.client.post(
                '/login?user=comercio',
                {'password': 'comercio'},
                format='json',
            ).status_code,
            401,
        )
        self.assertEqual(
            self.client.post(
                '/login?user=comercio',
                {'password': 'NuevaClave123'},
                format='json',
            ).status_code,
            200,
        )
