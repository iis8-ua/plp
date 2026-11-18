# Backend TPV (mocks)

Proyecto Django + Django REST Framework que implementa **sólo las rutas, la autenticación simulada y los códigos de estado** definidos en `../api/api.yaml`. La lógica de negocio sigue siendo mock; MySQL se configura para el despliegue pero los mocks todavía no consultan tablas propias.

El proyecto (`manage.py`, `tpv/`) y la app Django con el modelo de datos (`pagos/`) están en `backend/`; la app que implementa la API mock está en `../api/`, junto a la especificación.

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
python manage.py test api pagos
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

`POST /login?user=tpv01` con body `{"password": "secret"}` devuelve un token mock.

## Disparadores de error

| Endpoint                             | Código | Cómo provocarlo                                                        |
| ------------------------------------ | ------ | ---------------------------------------------------------------------- |
| `/login`                             | 400    | Sin `?user=`                                                           |
| `/login`                             | 401    | Usuario o password incorrectos                                         |
| `/logout`                            | 500    | Cabecera `X-Mock-Error: true`                                          |
| `/withdraw`                          | 400    | Sin `amount`, no numérico, o `amount > 1000`                           |
| `/pay`                               | 400    | Body ausente/inválido (falta algún campo obligatorio)                  |
| `/pay`                               | 409    | `total_amount > 1000`                                                  |
| `/pay`                               | 422    | `payment_data.card_number` terminado en `0002`                         |
| `/pay`                               | 500    | `payment_data.card_number` terminado en `0005`, o `X-Mock-Error: true` |
| `/refunds/request`                   | 404    | `transaction_id` mal formado o distinto de `txn_001` / `txn_002`       |
| `/refunds/accept`, `/refunds/reject` | 500    | Cabecera `X-Mock-Error: true`                                          |
| `/ticket/update`                     | 404    | `id` mal formado o distinto de `tkt_001` / `tkt_002`                   |

El resto de las combinaciones devuelven el código de éxito de la spec (`200`, `202`).
