# Backend TPV (mocks)

Proyecto Django + Django REST Framework que implementa las rutas, la autenticación simulada, los códigos de estado y **estado en memoria** (tickets y empresas mutables) definidos en `../api/api.yaml`. No hay persistencia: al reiniciar el proceso se vuelve a los datos iniciales.

El proyecto (`manage.py`, `tpv/`) sigue en `backend/`; la app Django que implementa la API está en `../api/`, junto a la especificación.

## Arrancar

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py runserver
```

Tests de los códigos de estado:

```bash
python manage.py test api
```

Verificación del esquema generado desde el código:

```bash
python manage.py spectacular --file /tmp/api.from-code.yaml --validate
```

## Docker

Desde la raíz del repositorio:

```bash
cp .env.example .env   # cambiar las contraseñas
docker compose up --build
```

- API: `http://localhost:8000`
- Frontend Vue: `http://localhost:8080`

Sin `DB_ENGINE=mysql` (por ejemplo en CI o en local) Django usa SQLite. En los contenedores se activa MySQL con las variables `MYSQL_*`.

## Autenticación simulada

| Cabecera                        | Comportamiento                                                                                                                          |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `Authorization: Bearer <token>` | Válida en las rutas marcadas con Bearer en la spec. Cualquier token no vacío sirve, salvo `invalid` o `expired`, que devuelven **401**. |
| `X-Admin-Token: <valor>`        | Obligatoria en las rutas «SÓLO EL ADMIN». Si falta, devuelve **403**. `GET /companies` exige además el Bearer.                          |

`POST /login?user=<usuario>` con el body `{"password": "<contraseña>"}` devuelve el token y el usuario autenticado (incluido su rol).

| Usuario | Contraseña | Rol | Uso |
| --- | --- | --- | --- |
| `admin` | `admin` | `admin` | Portal técnico con acceso a Comercios |
| `tpv01` | `secret` | `tecnico` | Portal técnico sin acceso a Comercios |
| `comercio` | `comercio` | `comercio` | Portal del comercio (`emp_001`) |

## Estado en memoria

- **Saldo**: tres cuentas (`EUR`, `USD`, `GBP`) con retiradas independientes. `POST /withdraw` acepta `currency` (EUR por defecto).
- **Tickets**: incidencias de soporte con `subject`, `status`, `reply`, historial y conversación (`messages`). `PUT /ticket/update` acepta `{status, reply}`, `POST /ticket/message` añade mensajes y `POST /ticket/add` crea tickets. El rol `comercio` solo ve y modifica los tickets de su empresa.
- **Empresas**: `DELETE /companies/delete` hace baja lógica (`status: dado-de-baja`) y `PUT /companies/reactivate?id=` las reactiva. Ambas requieren administrador.
- **Pagos y devoluciones**: cada operación incluye su `currency` y su `client`; una devolución nueva hereda moneda y cliente del pago. `POST /refunds/accept` descuenta el importe del saldo de esa moneda y `POST /refunds/reject` solo cambia el estado.

Los cambios se pierden al reiniciar el servidor; no hay base de datos implicada.

## Disparadores de error

| Endpoint                             | Código | Cómo provocarlo                                                        |
| ------------------------------------ | ------ | ---------------------------------------------------------------------- |
| `/login`                             | 400    | Sin `?user=`                                                           |
| `/login`                             | 401    | Usuario o password incorrectos                                         |
| `/logout`                            | 500    | Cabecera `X-Mock-Error: true`                                          |
| `/withdraw`                          | 400    | Sin `amount`, no numérico, moneda no soportada, o `amount` mayor que el saldo de esa moneda |
| `/pay`                               | 400    | Body ausente/inválido (falta algún campo obligatorio)                  |
| `/pay`                               | 409    | `total_amount > 1000`                                                  |
| `/pay`                               | 422    | `payment_data.card_number` terminado en `0002`                         |
| `/pay`                               | 500    | `payment_data.card_number` terminado en `0005`, o `X-Mock-Error: true` |
| `/refunds/request`                   | 404    | `transaction_id` mal formado o distinto de `txn_001`…`txn_007`         |
| `/refunds/accept`                    | 400    | El saldo de la moneda no cubre el importe                              |
| `/refunds/accept`, `/refunds/reject` | 404    | No hay devolución pendiente para esa transacción                       |
| `/refunds/accept`, `/refunds/reject` | 500    | Cabecera `X-Mock-Error: true`                                          |
| `/ticket/update`                     | 400    | Body sin `status` ni `reply`                                           |
| `/ticket/message`                    | 400    | Mensaje vacío                                                          |
| `/ticket/message`                    | 404    | `id` inexistente o de otra empresa                                     |
| `/ticket/update`                     | 404    | `id` inexistente                                                       |
| `/ticket/delete`                     | 404    | `id` inexistente                                                       |
| `/companies/delete`                  | 404    | `id` inexistente                                                       |
| `/companies/reactivate`              | 404    | `id` inexistente                                                       |

El resto de las combinaciones devuelven el código de éxito de la spec (`200`, `202`).
