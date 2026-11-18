# TPV VIRTUAL ("PLP - Pasa La Pasta")

## 1. Introducción

PLP es una plataforma de pagos en la que los **comercios** reciben cobros y los **clientes** los realizan con tarjeta. Además del cobro, el sistema cubre consulta de pagos, devoluciones, saldo multimoneda, tickets de soporte con asignación a técnicos, gestión de comercios y perfiles de usuario.

La implementación actual es una **API REST/JSON** sobre Django + Django REST Framework y MySQL, documentada en `api/api.yaml` (contrato principal), `API.txt` (resumen) y `pasarela_pagos.sql` (DDL). El frontend es Vue 3 + TypeScript + Vite.

## 2. Alcance

### 2.1 Dentro del alcance

- Autenticación por token y roles: **administrador, técnico y comercio**.
- Alta de comercios con su cuenta de acceso, baja lógica y reactivación.
- Pagos con tarjeta/efectivo/transferencia y ciclo de estados.
- Consulta de pagos del comercio autenticado.
- Devoluciones totales con aceptación/rechazo por parte del comercio.
- Saldo por moneda y retirada de fondos.
- Tickets de soporte con conversación, historial, asignación y desasignación.
- Gestión de técnicos (listado y alta) y perfiles de usuario con cambio de contraseña.

### 2.2 Fuera del alcance / pendiente

- Liquidación real con entidades financieras: los pagos se **simulan**.
- Pasarela real de abono a la tarjeta del cliente.
- Certificación PCI-DSS; solo se aplican sus principios (tokenización, sin PAN ni CVV).
- Cuentas de cliente: el pago es **invitado**.
- Facturación electrónica legal.
- Interoperación con otros proyectos (RF-49): **no implementada**.
- Desactivación de técnicos: el estado existe, pero no hay endpoint.
- Caducidad real de tokens: los tokens de DRF no expiran.

## 3. Actores y roles

| Actor | Descripción | Acceso |
|---|---|---|
| **Cliente** | Persona que paga con tarjeta. No se registra. | Pago invitado |
| **Comercio** | Empresa que cobra, consulta pagos, gestiona devoluciones, saldo y tickets. | Login (rol `comercio`) |
| **Técnico** | Equipo de soporte: ve todos los tickets, se asigna/desasigna los suyos, responde y elimina. | Login (rol `tecnico`) |
| **Administrador** | Gestiona comercios y técnicos, asigna tickets y accede a todo. | Login (rol `admin`) |
| **Sistema externo** | Proyecto de un compañero para interoperar. | Pendiente |

## 4. Requisitos funcionales

**Prioridad (MoSCoW):** Must = imprescindible · Should = deseable · Could = opcional.

### 4.1 Autenticación y autorización

| ID | Requisito | Endpoint | Prioridad |
|---|---|---|---|
| RF-01 | Login con usuario y contraseña; devuelve token DRF, usuario, rol, empresa y `force_password_change`. Errores: 400 sin usuario; 401 credenciales incorrectas. | `POST /login` | Must |
| RF-02 | Cierre de sesión invalidando el token. | `POST /logout` | Must |
| RF-03 | Endpoints protegidos con `Authorization: Bearer <token>`; permisos por rol (`admin`, `tecnico`, `comercio`). | — | Must |
| RF-04 | Solo el administrador puede crear comercios, listarlos, darlos de baja y reactivarlos. El alta crea también la cuenta de acceso. | `PUT /companies/add`, `GET /companies`, `DELETE /companies/delete`, `PUT /companies/reactivate` | Must |
| RF-05 | El equipo técnico (`tecnico`/`admin`) puede eliminar tickets; el comercio no. | `DELETE /ticket/delete` | Must |
| RF-06 | Aislamiento: cada comercio solo accede a sus pagos, devoluciones, saldo y tickets. | — | Must |
| RF-07 | Cambio de contraseña con verificación de la actual; mínimo 8 caracteres. | `POST /profile/password` | Must |
| RF-08 | Cambio obligatorio de contraseña en el primer acceso cuando se marca al crear la cuenta. | — | Should |

### 4.2 Comercios y saldo

| ID | Requisito | Endpoint | Prioridad |
|---|---|---|---|
| RF-09 | Alta de comercio con datos fiscales y de contacto, credenciales y 3 saldos iniciales (EUR/USD/GBP). Solo admin. | `PUT /companies/add` | Must |
| RF-10 | Baja lógica del comercio conservando el histórico; reactivación posterior. | `DELETE /companies/delete`, `PUT /companies/reactivate` | Must |
| RF-11 | Listado de comercios con estado, fecha de registro y datos fiscales. Solo admin. | `GET /companies` | Should |
| RF-12 | Consulta del saldo del comercio autenticado desglosado por moneda. | `GET /balance` | Must |
| RF-13 | Retirada por moneda: 200; 400 si el importe es inválido o supera el saldo de esa moneda. | `POST /withdraw` | Must |
| RF-14 | Perfil del comercio editable (razón social y CIF de solo lectura). | `GET /profile`, `PUT /profile` | Should |

### 4.3 Pagos

| ID | Requisito | Endpoint | Prioridad |
|---|---|---|---|
| RF-15 | Registrar un pago con importe, método, productos y datos de pago. Requiere usuario con empresa. | `POST /pay` | Must |
| RF-16 | El pago registra comercio receptor, concepto, importe, moneda, referencia, factura (nullable), fecha y estado. | — | Must |
| RF-17 | Estados del pago: `PENDIENTE`, `APROBADA`, `RECHAZADA`, `REEMBOLSADA`. La API los expone como `pending`, `approved`, `rejected`, `refunded`. | — | Must |
| RF-18 | `POST /pay` crea la transacción en `PENDIENTE`, la procesa y la finaliza en `APROBADA` o `RECHAZADA` (tarjeta terminada en 0002). | `POST /pay` | Must |
| RF-19 | El número de factura es único por comercio; puede ser nulo. | — | Must |
| RF-20 | Multimoneda en pagos y saldos; `POST /pay` usa EUR y no acepta moneda en el cuerpo. | — | Should |
| RF-21 | No se almacenan PAN ni CVV; se guarda token, últimos 4 y caducidad en tarjetas. | — | Must |
| RF-22 | No se aplica comisión: `COMISION` queda a 0. | — | Must |
| RF-23 | Un pago aprobado incrementa el saldo de la empresa por el importe completo. Un pago rechazado no lo modifica. | — | Must |
| RF-24 | El motivo del estado se persiste en la transacción y en su historial; la API lo devuelve en `reason`. | — | Must |

### 4.4 Consulta de pagos

| ID | Requisito | Endpoint | Prioridad |
|---|---|---|---|
| RF-25 | El comercio consulta sus pagos con cliente (titular), referencia, factura, concepto, importe, moneda, estado, método y fecha. | `GET /payments` | Must |
| RF-26 | No se muestran pagos de otros comercios. | — | Must |

### 4.5 Devoluciones

| ID | Requisito | Endpoint | Prioridad |
|---|---|---|---|
| RF-27 | Solicitud de devolución total de una transacción propia, con motivo opcional. 202; 404 si no existe o es de otra empresa; 409 si ya hay una pendiente. | `POST /refunds/request` | Must |
| RF-28 | Aceptar o rechazar una devolución por su UUID. 200; 400 si ya está resuelta o el saldo no cubre el importe; 404 si no existe o es de otra empresa. | `POST /refunds/accept?id=`, `POST /refunds/reject?id=` | Must |
| RF-29 | Solo devoluciones totales: el importe coincide con el del pago. | — | Must |
| RF-30 | Al aceptar se descuenta el importe del saldo de esa moneda y, si es total, la transacción pasa a `REEMBOLSADA`. | — | Must |
| RF-31 | Listado de devoluciones de la empresa con cliente, referencia, importe, moneda, motivo, estado y fecha. | `GET /refunds` | Should |
| RF-32 | Solo se puede solicitar devolución si el pago está en estado `APROBADA`; si no, 400 `PAYMENT_NOT_REFUNDABLE`. | — | Must |

### 4.6 Tickets de soporte

| ID | Requisito | Endpoint | Prioridad |
|---|---|---|---|
| RF-33 | El comercio abre un ticket con asunto y descripción; se crea el primer mensaje y el evento de apertura. | `POST /ticket/add` | Must |
| RF-34 | El comercio ve solo sus tickets; técnicos y administradores ven todos. | `GET /tickets` | Must |
| RF-35 | Conversación con mensajes de comercio y técnico, autor y fecha. | `POST /ticket/message` | Must |
| RF-36 | Técnicos/administradores cambian estado (`open`, `in_progress`, `closed`) y añaden respuesta; se registra en historial. | `PUT /ticket/update` | Must |
| RF-37 | Asignación de tickets: el admin asigna a cualquier técnico; el técnico se asigna los suyos. | `PUT /ticket/assign` | Must |
| RF-38 | Desasignación: el técnico puede desasignarse sus tickets; el admin puede desasignar cualquiera. | `PUT /ticket/assign` con `unassign` | Must |
| RF-39 | Eliminación de tickets por técnicos/administradores; borra mensajes e historial en cascada. | `DELETE /ticket/delete` | Should |
| RF-40 | Historial de estados y asignaciones con fecha, título, descripción y autor. | — | Must |
| RF-41 | Los tickets usan un número visible único (`1086`, `1087`…). | — | Should |

### 4.7 Técnicos

| ID | Requisito | Endpoint | Prioridad |
|---|---|---|---|
| RF-42 | El administrador lista los técnicos con correo, usuario, estado y actividad. | `GET /technicians` | Must |
| RF-43 | El administrador crea técnicos con nombre, correo, usuario, contraseña inicial y cambio obligatorio opcional. La contraseña solo se devuelve al crear. | `POST /technicians` | Must |
| RF-44 | Validación de usuario y correo duplicados y contraseña mínima de 8 caracteres. | — | Must |
| RF-45 | Desactivación de técnicos: pendiente (no hay endpoint). | — | Could |

### 4.8 Perfiles

| ID | Requisito | Endpoint | Prioridad |
|---|---|---|---|
| RF-46 | Consultar el perfil propio: usuario, rol, estado, empresa (si comercio) y actividad (si técnico). | `GET /profile` | Must |
| RF-47 | Actualizar nombre y correo (admin/técnico) o datos de la empresa (comercio). | `PUT /profile` | Must |
| RF-48 | Cambiar contraseña verificando la actual. | `POST /profile/password` | Must |

### 4.9 Interoperabilidad

| ID | Requisito | Endpoint | Prioridad |
|---|---|---|---|
| RF-49 | Interoperar con al menos un proyecto de compañeros mediante API REST/JSON. | — | Must (pendiente) |

## 5. Requisitos no funcionales

| ID | Categoría | Requisito |
|---|---|---|
| RNF-01 | Seguridad | Contraseñas hasheadas por Django (PBKDF2 por defecto); tokens Bearer de DRF (sin caducidad actualmente); HTTPS en producción. |
| RNF-02 | Seguridad / PCI | No se almacenan PAN ni CVV; solo token, últimos 4 y caducidad. |
| RNF-03 | Integridad | Retiradas y devoluciones son atómicas y bloquean el saldo; no se permiten saldos negativos. |
| RNF-04 | Concurrencia | `select_for_update` en saldo para retiradas y devoluciones. |
| RNF-05 | Auditoría | Tickets y pagos: historial de estados con fecha y motivo. Las asignaciones de tickets también se registran. |
| RNF-06 | Rendimiento | Respuestas por debajo de 500 ms en el entorno de práctica. |
| RNF-07 | Disponibilidad | Persistencia en MySQL; migraciones y seed al arrancar el contenedor. |
| RNF-08 | Mantenibilidad | Contrato en `api/api.yaml`, DDL en `pasarela_pagos.sql` y app `pagos` separada de las vistas. |
| RNF-09 | Interoperabilidad | REST/JSON; CORS resuelto por proxy de Vite/nginx. |
| RNF-10 | Usabilidad | Códigos HTTP coherentes y errores `{ code, message }`. |
| RNF-11 | Compatibilidad | MySQL 8+ y navegadores modernos. |
| RNF-12 | Privacidad | Datos mínimos: titular y últimos 4 dígitos. |

## 6. Modelo de datos actual

| Tabla | Entidad | Observaciones |
|---|---|---|
| `EMPRESAS` | Comercio | Estado (`activo`/`dado-de-baja`) y datos fiscales/contacto. |
| `PERFILES_USUARIO` | Usuario | Rol y empresa; se apoya en `auth_user`. |
| `TRANSACCIONES` | Pago | `REFERENCIA`, `NUM_FACTURA`, `MOTIVO`, moneda, comisión (sin aplicar) y 4 estados. |
| `TRANSACCION_HISTORIAL` | Historial de pago | Estado, motivo y fecha de cada cambio. |
| `INFORMACION_PAGOS` + `TARJETAS` / `CUENTAS_BANCARIAS` | Datos de pago | Tokenizados. |
| `REEMBOLSOS` | Devolución | Estado (`PENDIENTE/ACEPTADO/RECHAZADO`), motivo y cantidad. |
| `METODOS_PAGO` | Catálogo | Tarjeta, Transferencia, Bizum y Efectivo. |
| `MONEDAS` + `SALDOS_EMPRESAS` | Multimoneda | EUR, USD y GBP. |
| `TICKETS` | Ticket | Número visible, estado, empresa y técnico asignado. |
| `TICKET_MENSAJES` | Conversación | Autor y rol. |
| `TICKET_HISTORIAL` | Historial | Estados y asignaciones. |
| `auth_user`, `authtoken_token` | Autenticación | Gestionadas por Django. |

## 7. Historias de usuario

### 7.1 Acceso y cuentas

- **US-01 · Iniciar sesión**: credenciales válidas → 200 con token y usuario (rol, empresa, cambio obligatorio); sin usuario → 400; incorrectas → 401. Debe enviarse `Authorization: Bearer`.
- **US-02 · Cerrar sesión**: 200 e invalidación del token; 401 sin token.
- **US-03 · Alta de comercio**: solo admin; datos fiscales obligatorios y cuenta de acceso (usuario/contraseña); 200 con credenciales una sola vez; 400 por usuario duplicado.
- **US-04 · Baja/reactivación**: solo admin; baja lógica conservando histórico; reactivación posterior.
- **US-05 · Listado de comercios**: solo admin; incluye estado y fecha.
- **US-06 · Perfil**: cada rol consulta y actualiza sus datos; comercio edita los de su empresa.
- **US-07 · Cambiar contraseña**: verificación de la actual, mínimo 8; cambio obligatorio en primer acceso si se marcó.

### 7.2 Pagos y saldo

- **US-08 · Pagar**: usuario con empresa; el pago pasa por `PENDIENTE` y termina en `APROBADA` (200) o `RECHAZADA` (422, tarjeta terminada en 0002). Al aprobarse se abona el importe completo al saldo; al rechazarse no se abona. 400 cuerpo inválido; sin PAN/CVV.
- **US-09 · Consultar pagos**: solo los de la empresa; cliente, referencia, factura, concepto, importe, moneda, estado, método y fecha.
- **US-10 · Consultar saldo**: array de cuentas por moneda; 403 sin empresa.
- **US-11 · Retirar**: por moneda; 200 y descuento atómico; 400 importe/saldo.

### 7.3 Devoluciones

- **US-12 · Solicitar**: transacción propia y **aprobada** + motivo opcional; 202; 400 si no está aprobada; 404; 409 duplicada.
- **US-13 · Aceptar/rechazar**: por UUID de devolución; 200; 400 ya resuelta/saldo; 404.
- **US-14 · Total**: importe igual al pago; aceptar descuenta saldo y marca `REEMBOLSADA` si es total.
- **US-15 · Listar**: devoluciones de la empresa con cliente, referencia, importe, moneda, motivo, estado y fecha.

### 7.4 Tickets

- **US-16 · Abrir ticket**: comercio; asunto y descripción; primer mensaje e historial.
- **US-17 · Consultar**: comercio solo los suyos; técnicos/admin todos.
- **US-18 · Conversar**: mensajes con autor, rol y fecha.
- **US-19 · Gestionar**: técnicos/admin cambian estado y responden; historial.
- **US-20 · Asignar/desasignar**: admin asigna a cualquier técnico; técnico se asigna/desasigna los suyos.
- **US-21 · Eliminar**: técnicos/admin; cascada de mensajes e historial.

### 7.5 Técnicos

- **US-22 · Listar técnicos**: solo admin; actividad y estado.
- **US-23 · Crear técnico**: solo admin; credenciales una sola vez; validaciones.

### 7.6 Interoperabilidad

- **US-26 · Integrar con un compañero**: pendiente; contrato, autenticación y flujo extremo a extremo por acordar.

## 8. Matriz de trazabilidad

| Módulo | Requisitos | Historias | Endpoints |
|---|---|---|---|
| Acceso y cuentas | RF-01 – RF-08 | US-01 – US-07 | `/login`, `/logout`, `/profile*` |
| Comercios y saldo | RF-09 – RF-14 | US-03 – US-05, US-10 – US-11 | `/companies/*`, `/balance`, `/withdraw` |
| Pagos | RF-15 – RF-26 | US-08 – US-09 | `/pay`, `/payments` |
| Devoluciones | RF-27 – RF-32 | US-12 – US-15 | `/refunds/*` |
| Tickets | RF-33 – RF-41 | US-16 – US-21 | `/ticket/*`, `/tickets` |
| Técnicos | RF-42 – RF-45 | US-22 – US-23 | `/technicians` |
| Perfiles | RF-46 – RF-48 | US-06 – US-07 | `/profile`, `/profile/password` |
| Interoperabilidad | RF-49 | US-26 | *(pendiente)* |

