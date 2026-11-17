"""Tests de los códigos de estado exigidos por api/api.yaml."""

from rest_framework.test import APIClient, APITestCase

from . import mocks

BEARER = {'HTTP_AUTHORIZATION': 'Bearer mock-token'}
COMERCIO = {'HTTP_AUTHORIZATION': 'Bearer mock-token-comercio'}
TECNICO = {'HTTP_AUTHORIZATION': 'Bearer mock-token-tpv01'}
ADMIN = {'HTTP_X_ADMIN_TOKEN': 'admin-token'}
BOTH = {**BEARER, **ADMIN}

PRODUCTS = [{'product_id': 'P-1', 'name': 'Café', 'quantity': 1, 'unit_price': 1.5}]
PAY_BODY = {
    'total_amount': 12.5,
    'payment_method': 'card',
    'products': PRODUCTS,
    'payment_data': {'card_number': '4111111111111111'},
}
TICKET_BODY = {
    'company_id': 'emp_001',
    'subject': 'Consulta sobre una liquidación',
    'description': 'Necesito el desglose de la liquidación del 16 de noviembre.',
}
TICKET_UPDATE = {'status': 'in_progress', 'reply': 'Revisando la pasarela.'}


class ApiStatusCodesTests(APITestCase):
    def setUp(self):
        mocks.reset_mocks()
        self.client = APIClient()

    def test_login(self):
        self.assertEqual(self.client.post('/login').status_code, 400)
        self.assertEqual(
            self.client.post('/login?user=tpv01', {'password': 'bad'}, format='json').status_code,
            401,
        )

        response = self.client.post(
            '/login?user=tpv01', {'password': 'secret'}, format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user']['role'], 'tecnico')
        self.assertEqual(response.data['token'], 'mock-token-tpv01')

    def test_login_admin_and_merchant_roles(self):
        admin = self.client.post('/login?user=admin', {'password': 'admin'}, format='json')
        self.assertEqual(admin.data['user']['role'], 'admin')

        merchant = self.client.post(
            '/login?user=comercio', {'password': 'comercio'}, format='json'
        )
        self.assertEqual(merchant.data['user']['role'], 'comercio')
        self.assertEqual(merchant.data['user']['company_id'], 'emp_001')

    def test_logout(self):
        self.assertEqual(self.client.post('/logout').status_code, 401)
        self.assertEqual(self.client.post('/logout', **BEARER).status_code, 200)
        self.assertEqual(
            self.client.post('/logout', HTTP_X_MOCK_ERROR='true', **BEARER).status_code,
            500,
        )

    def test_withdraw(self):
        self.assertEqual(self.client.post('/withdraw?amount=10').status_code, 401)
        self.assertEqual(self.client.post('/withdraw', **BEARER).status_code, 400)
        self.assertEqual(self.client.post('/withdraw?amount=abc', **BEARER).status_code, 400)
        self.assertEqual(self.client.post('/withdraw?amount=2000', **BEARER).status_code, 400)
        self.assertEqual(
            self.client.post('/withdraw?amount=10&currency=CHF', **BEARER).status_code, 400
        )

        eur = self.client.post('/withdraw?amount=10', **BEARER)
        self.assertEqual(eur.status_code, 200)
        self.assertEqual(eur.data['currency'], 'EUR')
        self.assertEqual(eur.data['balance'], 1240.0)

        usd = self.client.post('/withdraw?amount=20&currency=USD', **BEARER)
        self.assertEqual(usd.status_code, 200)
        self.assertEqual(usd.data['currency'], 'USD')
        self.assertEqual(usd.data['balance'], 400.0)

        too_much_usd = self.client.post('/withdraw?amount=500&currency=USD', **BEARER)
        self.assertEqual(too_much_usd.status_code, 400)

        balance = self.client.get('/balance', **BEARER)
        amounts = {item['currency']: item['amount'] for item in balance.data['balances']}
        self.assertEqual(amounts, {'EUR': 1240.0, 'USD': 400.0, 'GBP': 180.0})

    def test_balance(self):
        self.assertEqual(self.client.get('/balance').status_code, 401)
        response = self.client.get('/balance', **BEARER)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item['currency'] for item in response.data['balances']], ['EUR', 'USD', 'GBP']
        )

    def test_pay(self):
        self.assertEqual(self.client.post('/pay', {}, format='json').status_code, 400)
        self.assertEqual(self.client.post('/pay', PAY_BODY, format='json').status_code, 200)

        too_much = {**PAY_BODY, 'total_amount': 2000}
        self.assertEqual(self.client.post('/pay', too_much, format='json').status_code, 409)

        declined = {**PAY_BODY, 'payment_data': {'card_number': '4000000000000002'}}
        self.assertEqual(self.client.post('/pay', declined, format='json').status_code, 422)

        broken = {**PAY_BODY, 'payment_data': {'card_number': '4000000000000005'}}
        self.assertEqual(self.client.post('/pay', broken, format='json').status_code, 500)

    def test_refund_request(self):
        self.assertEqual(self.client.post('/refunds/request?transaction_id=nope').status_code, 404)

        created = self.client.post(
            '/refunds/request?transaction_id=txn_006&reason=Motivo%20de%20prueba'
        )
        self.assertEqual(created.status_code, 202)
        self.assertEqual(created.data['status'], 'pending')

        refunds = self.client.get('/refunds', **BEARER)
        last = refunds.data[-1]
        self.assertEqual(last['transaction_id'], 'txn_006')
        self.assertEqual(last['reference'], 'P-1046')
        self.assertEqual(last['amount'], 120.00)
        self.assertEqual(last['currency'], 'USD')
        self.assertEqual(last['client'], 'Marta Vidal')
        self.assertEqual(last['reason'], 'Motivo de prueba')

    def test_refund_accept_discounts_balance(self):
        self.assertEqual(self.client.post('/refunds/accept?transaction_id=txn_001').status_code, 401)

        accepted = self.client.post('/refunds/accept?transaction_id=txn_001', **COMERCIO)
        self.assertEqual(accepted.status_code, 200)
        self.assertEqual(accepted.data['refund']['status'], 'accepted')
        self.assertEqual(accepted.data['balance'], 1207.5)

        balance = self.client.get('/balance', **BEARER)
        amounts = {item['currency']: item['amount'] for item in balance.data['balances']}
        self.assertEqual(amounts['EUR'], 1207.5)

        again = self.client.post('/refunds/accept?transaction_id=txn_001', **COMERCIO)
        self.assertEqual(again.status_code, 404)

    def test_refund_reject_keeps_balance(self):
        rejected = self.client.post('/refunds/reject?transaction_id=txn_002', **COMERCIO)
        self.assertEqual(rejected.status_code, 200)
        self.assertEqual(rejected.data['refund']['status'], 'rejected')
        self.assertEqual(rejected.data['balance'], 1250.0)

    def test_refund_accept_forced_error(self):
        self.assertEqual(
            self.client.post(
                '/refunds/accept?transaction_id=txn_001',
                HTTP_X_MOCK_ERROR='true',
                **COMERCIO,
            ).status_code,
            500,
        )

    def test_refunds(self):
        self.assertEqual(self.client.get('/refunds').status_code, 401)
        response = self.client.get('/refunds', **BEARER)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 5)
        self.assertEqual(response.data[0]['client'], 'Lucía García')
        self.assertEqual(response.data[0]['currency'], 'EUR')

    def test_companies_add_and_delete_are_admin_only(self):
        self.assertEqual(self.client.put('/companies/add?nombre=Prueba').status_code, 403)
        self.assertEqual(
            self.client.put('/companies/add?nombre=Prueba', **BEARER).status_code, 403
        )

        created = self.client.put('/companies/add?nombre=Prueba', **ADMIN)
        self.assertEqual(created.status_code, 200)
        self.assertEqual(created.data['nombre'], 'Prueba')
        self.assertEqual(created.data['status'], 'activo')

        self.assertEqual(self.client.delete('/companies/delete?id=emp_001').status_code, 403)
        deleted = self.client.delete('/companies/delete?id=emp_001', **ADMIN)
        self.assertEqual(deleted.status_code, 200)
        self.assertEqual(deleted.data['status'], 'dado-de-baja')

        self.assertEqual(
            self.client.delete('/companies/delete?id=nope', **ADMIN).status_code, 404
        )

    def test_companies_reactivate_is_admin_only(self):
        self.assertEqual(self.client.put('/companies/reactivate?id=emp_003').status_code, 403)
        self.assertEqual(
            self.client.put('/companies/reactivate?id=emp_003', **BEARER).status_code, 403
        )
        self.assertEqual(
            self.client.put('/companies/reactivate?id=nope', **ADMIN).status_code, 404
        )

        reactivated = self.client.put('/companies/reactivate?id=emp_003', **ADMIN)
        self.assertEqual(reactivated.status_code, 200)
        self.assertEqual(reactivated.data['status'], 'activo')

    def test_companies_requires_bearer_and_admin(self):
        self.assertEqual(self.client.get('/companies').status_code, 401)
        self.assertEqual(self.client.get('/companies', **ADMIN).status_code, 401)
        self.assertEqual(self.client.get('/companies', **BEARER).status_code, 403)
        response = self.client.get('/companies', **BOTH)
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.data[0])

    def test_payments(self):
        self.assertEqual(self.client.get('/payments').status_code, 401)
        response = self.client.get('/payments', **BEARER)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 7)
        self.assertEqual(response.data[0]['client'], 'Lucía García')
        self.assertEqual(response.data[0]['invoice'], 'LH-F2026-1048')
        self.assertIn('USD', [payment['currency'] for payment in response.data])

    def test_ticket_add(self):
        self.assertEqual(self.client.post('/ticket/add', TICKET_BODY, format='json').status_code, 401)
        self.assertEqual(
            self.client.post('/ticket/add', {}, format='json', **COMERCIO).status_code, 400
        )

        created = self.client.post('/ticket/add', TICKET_BODY, format='json', **COMERCIO)
        self.assertEqual(created.status_code, 200)
        self.assertEqual(created.data['id'], '1089')
        self.assertEqual(created.data['company_id'], 'emp_001')
        self.assertEqual(created.data['company_name'], 'Librería Horizonte')
        self.assertEqual(len(created.data['messages']), 1)
        self.assertEqual(created.data['messages'][0]['role'], 'comercio')

    def test_ticket_delete_is_admin_only(self):
        self.assertEqual(self.client.delete('/ticket/delete?id=1086').status_code, 403)
        self.assertEqual(
            self.client.delete('/ticket/delete?id=1086', **ADMIN).status_code, 200
        )
        self.assertEqual(
            self.client.delete('/ticket/delete?id=1086', **ADMIN).status_code, 404
        )

    def test_ticket_update(self):
        self.assertEqual(
            self.client.put('/ticket/update?id=1086', TICKET_UPDATE, format='json').status_code,
            401,
        )
        self.assertEqual(
            self.client.put(
                '/ticket/update?id=nope', TICKET_UPDATE, format='json', **TECNICO
            ).status_code,
            404,
        )
        self.assertEqual(
            self.client.put('/ticket/update?id=1086', {}, format='json', **TECNICO).status_code,
            400,
        )

        response = self.client.put(
            '/ticket/update?id=1086', TICKET_UPDATE, format='json', **TECNICO
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'in_progress')
        self.assertEqual(response.data['reply'], 'Revisando la pasarela.')
        last_message = response.data['messages'][-1]
        self.assertEqual(last_message['role'], 'tecnico')
        self.assertEqual(last_message['message'], 'Revisando la pasarela.')

    def test_ticket_message(self):
        self.assertEqual(
            self.client.post('/ticket/message?id=1086', {'message': 'Hola'}, format='json').status_code,
            401,
        )
        self.assertEqual(
            self.client.post(
                '/ticket/message?id=1086', {'message': '   '}, format='json', **COMERCIO
            ).status_code,
            400,
        )
        self.assertEqual(
            self.client.post(
                '/ticket/message?id=1075', {'message': 'Hola'}, format='json', **COMERCIO
            ).status_code,
            404,
        )

        response = self.client.post(
            '/ticket/message?id=1086', {'message': 'Gracias, todo aclarado.'}, format='json', **COMERCIO
        )
        self.assertEqual(response.status_code, 200)
        last_message = response.data['messages'][-1]
        self.assertEqual(last_message['role'], 'comercio')
        self.assertEqual(last_message['author'], 'Librería Horizonte')
        self.assertEqual(last_message['message'], 'Gracias, todo aclarado.')

    def test_tickets_are_filtered_by_company(self):
        self.assertEqual(self.client.get('/tickets').status_code, 401)

        merchant = self.client.get('/tickets', **COMERCIO)
        self.assertEqual(merchant.status_code, 200)
        self.assertEqual(len(merchant.data), 13)
        self.assertTrue(all(ticket['company_id'] == 'emp_001' for ticket in merchant.data))

        technician = self.client.get('/tickets', **TECNICO)
        self.assertEqual(len(technician.data), 14)
        self.assertIn('1075', [ticket['id'] for ticket in technician.data])
