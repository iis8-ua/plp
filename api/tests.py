"""Tests de los códigos de estado exigidos por api/api.yaml."""

from rest_framework.test import APIClient, APITestCase

BEARER = {'HTTP_AUTHORIZATION': 'Bearer mock-token'}
ADMIN = {'HTTP_X_ADMIN_TOKEN': 'admin-token'}
BOTH = {**BEARER, **ADMIN}

PRODUCTS = [{'product_id': 'P-1', 'name': 'Café', 'quantity': 1, 'unit_price': 1.5}]
PAY_BODY = {
    'total_amount': 12.5,
    'payment_method': 'card',
    'products': PRODUCTS,
    'payment_data': {'card_number': '4111111111111111'},
}
TICKET_BODY = {'total': 12.5, 'products': PRODUCTS}


class ApiStatusCodesTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_login(self):
        self.assertEqual(self.client.post('/login').status_code, 400)
        self.assertEqual(
            self.client.post('/login?user=tpv01', {'password': 'bad'}, format='json').status_code,
            401,
        )
        self.assertEqual(
            self.client.post('/login?user=tpv01', {'password': 'secret'}, format='json').status_code,
            200,
        )

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
        self.assertEqual(self.client.post('/withdraw?amount=10', **BEARER).status_code, 200)

    def test_balance(self):
        self.assertEqual(self.client.get('/balance').status_code, 401)
        self.assertEqual(self.client.get('/balance', **BEARER).status_code, 200)

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
        self.assertEqual(
            self.client.post('/refunds/request?transaction_id=txn_001').status_code, 202
        )

    def test_refund_accept_and_reject(self):
        for path in ('/refunds/accept', '/refunds/reject'):
            with self.subTest(path=path):
                self.assertEqual(self.client.post(path).status_code, 401)
                self.assertEqual(
                    self.client.post(f'{path}?transaction_id=txn_001', **BEARER).status_code, 200
                )
                self.assertEqual(
                    self.client.post(
                        f'{path}?transaction_id=txn_001',
                        HTTP_X_MOCK_ERROR='true',
                        **BEARER,
                    ).status_code,
                    500,
                )

    def test_refunds(self):
        self.assertEqual(self.client.get('/refunds').status_code, 401)
        self.assertEqual(self.client.get('/refunds', **BEARER).status_code, 200)

    def test_companies_add_and_delete_are_admin_only(self):
        self.assertEqual(self.client.put('/companies/add?nombre=Prueba').status_code, 403)
        self.assertEqual(
            self.client.put('/companies/add?nombre=Prueba', **BEARER).status_code, 403
        )
        self.assertEqual(
            self.client.put('/companies/add?nombre=Prueba', **ADMIN).status_code, 200
        )
        self.assertEqual(self.client.delete('/companies/delete?id=emp_001').status_code, 403)
        self.assertEqual(
            self.client.delete('/companies/delete?id=emp_001', **ADMIN).status_code, 200
        )

    def test_companies_requires_bearer_and_admin(self):
        self.assertEqual(self.client.get('/companies').status_code, 401)
        self.assertEqual(self.client.get('/companies', **ADMIN).status_code, 401)
        self.assertEqual(self.client.get('/companies', **BEARER).status_code, 403)
        self.assertEqual(self.client.get('/companies', **BOTH).status_code, 200)

    def test_payments(self):
        self.assertEqual(self.client.get('/payments').status_code, 401)
        self.assertEqual(self.client.get('/payments', **BEARER).status_code, 200)

    def test_ticket_add(self):
        self.assertEqual(self.client.post('/ticket/add', TICKET_BODY, format='json').status_code, 401)
        self.assertEqual(
            self.client.post('/ticket/add', {}, format='json', **BEARER).status_code, 400
        )
        self.assertEqual(
            self.client.post('/ticket/add', TICKET_BODY, format='json', **BEARER).status_code, 200
        )

    def test_ticket_delete_is_admin_only(self):
        self.assertEqual(self.client.delete('/ticket/delete?id=tkt_001').status_code, 403)
        self.assertEqual(
            self.client.delete('/ticket/delete?id=tkt_001', **ADMIN).status_code, 200
        )

    def test_ticket_update(self):
        self.assertEqual(self.client.put('/ticket/update?id=tkt_001', TICKET_BODY, format='json').status_code, 401)
        self.assertEqual(
            self.client.put('/ticket/update?id=nope', TICKET_BODY, format='json', **BEARER).status_code,
            404,
        )
        self.assertEqual(
            self.client.put('/ticket/update?id=tkt_001', {}, format='json', **BEARER).status_code,
            400,
        )
        self.assertEqual(
            self.client.put('/ticket/update?id=tkt_001', TICKET_BODY, format='json', **BEARER).status_code,
            200,
        )

    def test_tickets(self):
        self.assertEqual(self.client.get('/tickets').status_code, 401)
        self.assertEqual(self.client.get('/tickets', **BEARER).status_code, 200)
