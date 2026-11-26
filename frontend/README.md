# Frontend PLP · Pasa La Pasta

Implementación en **Vue 3 + TypeScript + Vite + Tailwind CSS + Vue Router + Pinia** del diseño de Figma `PLP - Pasa La Pasta`.

El frontend funciona **solo contra la API** (`api/api.yaml`). No hay capa de mocks ni datos de demostración en el código.

## Arranque

El backend tiene que estar disponible en `http://localhost:8000` (el proxy de Vite reenvía `/api`).

```bash
npm install
npm run dev
```

- Aplicación: `http://localhost:5173`
- API: `http://localhost:8000`

### Credenciales

| Portal | Usuario | Contraseña | Rol | Acceso |
|---|---|---|---|---|
| Técnico | `admin` | `admin` | Administrador | Tickets y Comercios |
| Técnico | `tpv01` | `secret` | Técnico | Solo Tickets (Comercios redirige a acceso restringido) |
| Comercio | `comercio` | `comercio` | Comercio | Inicio, Pagos, Saldo, Devoluciones y Tickets |

Cada portal valida que el rol del usuario coincida: una cuenta de comercio no puede entrar por el acceso técnico y viceversa.

### Documentación de la API

La documentación pública de los endpoints está en `/docs.html`:

- Docker: `http://localhost:8080/docs.html`
- Desarrollo: `http://localhost:5173/docs.html`

### Scripts

| Comando | Descripción |
|---|---|
| `npm run dev` | Servidor de desarrollo |
| `npm run typecheck` | Comprobación de tipos con `vue-tsc` |
| `npm run build` | Typecheck + build de producción |
| `npm run preview` | Previsualización del build |

### Variables de entorno

Copia `.env.example` a `.env`:

```env
VITE_API_BASE_URL=/api
```

- `VITE_API_BASE_URL`: prefijo de la API. En desarrollo lo resuelve el proxy de Vite y en Docker lo resuelve Nginx.
- Si el backend no responde, la app muestra un error de conexión; no hay datos de reserva.

## Rutas

| Ruta | Vista |
|---|---|
| `/acceso-tecnico` | Acceso del equipo técnico |
| `/acceso-comercio` | Acceso del comercio |
| `/sesion-cerrada` | Confirmación de cierre de sesión |
| `/tecnico/tickets` | Bandeja de tickets |
| `/tecnico/tickets/:id` | Detalle del ticket |
| `/tecnico/comercios` | Gestión de comercios (solo administrador) |
| `/tecnico/comercios/nuevo` | Alta de comercio |
| `/tecnico/comercios/restringido` | Acceso restringido para no administradores |
| `/tecnico/tecnicos` | Gestión de técnicos (solo administrador) |
| `/tecnico/perfil` | Mi perfil (equipo técnico) |
| `/comercio/inicio` | Inicio del comercio |
| `/comercio/pagos` | Pagos recibidos |
| `/comercio/pagos/:id` | Detalle de pago |
| `/comercio/saldo` | Saldo y retiradas |
| `/comercio/devoluciones` | Devoluciones (gestión y solicitud) |
| `/comercio/tickets` | Soporte: listado de tickets |
| `/comercio/tickets/:id` | Detalle del ticket |
| `/comercio/perfil` | Mi perfil (comercio) |

## Estructura

```
src/
├── layouts/           # Auth, backoffice y portal del comercio
├── modules/
│   ├── auth/          # Accesos y sesión cerrada
│   ├── tech/          # Tickets y comercios
│   └── merchant/      # Inicio, pagos, saldo, devoluciones y tickets
├── services/          # Cliente HTTP y servicios por dominio
├── shared/
│   ├── components/    # UI, layouts y datos reutilizables
│   └── utils/         # Formato y estados
├── stores/            # Pinia
├── router/            # Rutas y guardas
└── types/             # Tipos de dominio
```

## Integración con la API

| Función | Endpoint |
|---|---|
| Login (token + usuario/rol) | `POST /login?user=` |
| Logout | `POST /logout` |
| Saldo | `GET /balance` |
| Retirada | `POST /withdraw?amount=&currency=` |
| Pagos | `GET /payments` |
| Devoluciones | `GET /refunds` |
| Solicitar devolución | `POST /refunds/request?transaction_id=&reason=` |
| Aceptar devolución | `POST /refunds/accept?id=` |
| Rechazar devolución | `POST /refunds/reject?id=` |
| Tickets | `GET /tickets` |
| Actualizar ticket | `PUT /ticket/update?id=` |
| Asignar ticket | `PUT /ticket/assign?id=` |
| Mensaje de ticket | `POST /ticket/message?id=` |
| Eliminar ticket | `DELETE /ticket/delete?id=` |
| Comercios | `GET /companies` |
| Alta de comercio | `PUT /companies/add` (JSON) |
| Baja de comercio | `DELETE /companies/delete?id=` |
| Reactivación de comercio | `PUT /companies/reactivate?id=` |
| Técnicos | `GET /technicians`, `POST /technicians` |
| Desactivar/reactivar técnico | `PUT /technicians/deactivate?id=`, `PUT /technicians/reactivate?id=` |
| Perfil | `GET /profile`, `PUT /profile` |
| Cambiar contraseña | `POST /profile/password` |

### Límites del contrato

- Los importes y saldos llegan como números (`COERCE_DECIMAL_TO_STRING=False` en DRF).
- `GET /payments` devuelve `concept`, `client`, `reference`, `invoice` (puede ser vacío), moneda, estado, **motivo** e **historial**; no incluye tarjeta, comisión ni neto en la lista.
- `GET /payments` incluye `reason` persistido y `history` con los cambios de estado.
- No existe `GET /payments/{id}`: el detalle se resuelve con la lista de pagos; un acceso directo recarga la lista antes de buscar.
- Los estados de pago son `pending`, `approved`, `rejected` y `refunded`.
- Aceptar una devolución descuenta el importe del saldo de esa moneda y, si es total, marca el pago como `refunded`.
- El comercio solo recibe los tickets de su empresa; las respuestas y el historial se guardan en base de datos.
- La autenticación es un token de DRF enviado como `Authorization: Bearer <token>`; caduca a los 3600 segundos y la app cierra la sesión al recibir 401. Los datos persisten entre reinicios.

## Docker

El `Dockerfile` compila la app y la sirve con Nginx. `nginx.conf` redirige `/api` al servicio `backend` y aplica fallback SPA.

```bash
docker compose up --build
```

- Frontend: `http://localhost:8080`

## Estado

Implementadas las fases 1–6: fundamentos visuales, portal técnico, administración de comercios, portal del comercio, devoluciones y responsive. Ver `../docs/implementacion-frontend.md` para el detalle de decisiones y verificación.
