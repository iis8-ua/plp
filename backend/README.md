# Backend TPV

Proyecto Django + Django REST Framework que implementa la API descrita en `../api/api.yaml`
sobre el modelo de datos de la app `pagos` (MySQL en despliegue, SQLite en local y tests).

- `backend/tpv/`: configuración Django.
- `backend/pagos/`: modelo de datos (empresas, monedas, saldos, transacciones, reembolsos y tickets).
- `../api/`: vistas, serializers, autenticación y contrato OpenAPI.

## Arrancar

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Tests:

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

El contenedor ejecuta `migrate` y `seed_demo` antes de arrancar gunicorn.

- API: `http://localhost:8000`
- Frontend Vue: `http://localhost:8080`

Sin `DB_ENGINE=mysql` (por ejemplo en CI o en local) Django usa SQLite. En los contenedores se
activa MySQL con las variables `MYSQL_*`.

## Autenticación

`POST /login?user=<usuario>` con el body `{"password": "<contraseña>"}` devuelve un token de DRF
y el usuario con su rol. El resto de peticiones usan `Authorization: Bearer <token>`.

| Usuario | Contraseña | Rol | Empresa |
| --- | --- | --- | --- |
| `admin` | `admin` | `admin` | — |
| `tpv01` | `secret` | `tecnico` | — |
| `comercio` | `comercio` | `comercio` | Librería Horizonte |
| `cruiz`, `dtorres`, `egarcia`, `msanchez`, `promero` | `tecnico123` | `tecnico` | — |

Los roles se guardan en `pagos.PerfilUsuario`. Las rutas de administrador (`/companies*`,
`/technicians*`) comprueban el rol del token; ya no existe `X-Admin-Token`.

`POST /logout` invalida el token de la sesión.

## Modelo y datos

- **Empresas**: `estado` (`activo` / `dado-de-baja`); la baja es lógica y se puede reactivar.
- **Saldos**: una fila por empresa y moneda (`EUR`, `USD`, `GBP`). `POST /withdraw` descuenta de la
  moneda indicada.
- **Pagos**: `Transaccion` + `InformacionPago` + `Tarjeta`/`CuentaBancaria`, con `referencia`,
  `num_factura`, `motivo`, moneda, comisión (sin aplicar) y estado (`PENDIENTE`, `APROBADA`,
  `RECHAZADA`, `REEMBOLSADA`). Cada cambio de estado se guarda en `TransaccionHistorial` con su
  motivo. `POST /pay` abona el importe completo al saldo si el pago se aprueba.
- **Devoluciones**: `Reembolso` sobre una transacción, con `motivo` y estado. Solo se solicitan
  sobre pagos aprobados. Aceptar descuenta el importe del saldo de la empresa; rechazar solo cambia
  el estado.
- **Tickets**: `Ticket` + `TicketMensaje` + `TicketHistorial`. El comercio solo accede a los tickets
  de su empresa; el equipo técnico ve todos. Cada ticket tiene un `tecnico` asignado (opcional);
  el administrador puede asignar a cualquier técnico, el técnico puede asignarse el ticket y
  desasignarse los suyos.
- **Empresas**: datos fiscales y de contacto (`razon_social`, `cif`, `tipo_empresa`,
  `actividad_economica`, dirección, contacto y web) además del nombre y estado. El alta crea
  también la cuenta de acceso del comercio (usuario, contraseña inicial y rol `comercio`).
- **Técnicos**: usuarios con rol `tecnico`; el administrador puede listarlos y crear nuevos accesos
  desde `/technicians`. La contraseña inicial solo se devuelve en la creación.
- **Perfil**: `/profile` devuelve y actualiza los datos del usuario (o de la empresa si es un
  comercio) y `/profile/password` cambia la contraseña.

`seed_demo` es idempotente y crea los usuarios, empresas, saldos, 7 pagos, 5 devoluciones y
14 tickets de ejemplo (repartidos entre los técnicos).

## Códigos de error habituales

| Endpoint | Código | Caso |
| --- | --- | --- |
| `/login` | 400 | Falta `?user=` |
| `/login` | 401 | Credenciales incorrectas |
| `/balance`, `/payments`, `/refunds` | 403 | Usuario sin empresa (admin/técnico) |
| `/withdraw` | 400 | Importe no válido, moneda sin saldo o saldo insuficiente |
| `/pay` | 422 | Pago rechazado (tarjeta terminada en `0002`) |
| `/refunds/request` | 404 | Transacción inexistente o de otra empresa |
| `/refunds/request` | 400 | El pago no está aprobado (`PAYMENT_NOT_REFUNDABLE`) |
| `/refunds/request` | 409 | Ya hay una devolución pendiente |
| `/refunds/accept` | 400 | Saldo insuficiente o devolución ya resuelta |
| `/refunds/accept`, `/refunds/reject` | 404 | Devolución inexistente o de otra empresa |
| `/companies*` | 403 | El usuario no es administrador |
| `/technicians` | 403 | El usuario no es administrador |
| `/technicians` (POST) | 400 | Usuario o correo duplicado, o contraseña corta |
| `/ticket/update` | 403 | El usuario es un comercio |
| `/ticket/message` | 404 | Ticket inexistente o de otra empresa |
| `/ticket/assign` | 400/403 | Técnico inexistente o usuario sin permisos |
| `/profile/password` | 400 | Contraseña actual incorrecta o nueva demasiado corta |
