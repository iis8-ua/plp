# Implementación frontend — PLP · Pasa La Pasta

Documento de progreso y decisiones de la implementación realizada a partir de `docs/analisis-figma.md`.

| Campo | Valor |
|---|---|
| Stack | Vue 3 + TypeScript + Vite + Tailwind CSS + Vue Router + Pinia |
| Carpeta | `frontend/` |
| Modo de datos | API real sobre MySQL; datos de demostración con `seed_demo` |
| Build | `npm run build` correcto |
| Typecheck | `npm run typecheck` correcto |
| QA funcional | Flujos E2E y tests de backend verificados; pendiente repetir el QA en navegador contra la API |
| QA visual | Comparación con capturas de Figma a 1440 × 1024 y 390 × 844 (previa a la eliminación de los mocks) |

---

## 1. Estado por fases

### FASE 1 — Fundamentos ✅

- Proyecto Vite + Vue 3 + TypeScript configurado.
- Tailwind CSS con tokens semánticos y variables CSS en `src/assets/styles/tokens.css`.
- Tipografía Inter (Google Fonts) con fallback del sistema.
- Componentes UI reutilizables:
  - `AppButton` (primario, secundario, neutral, ghost, peligro, peligro outline; 40/44/48 px).
  - `AppIcon` (27 iconos SVG locales).
  - `AppInput`, `AppTextarea`, `AppSelect` accesible.
  - `StatusBadge`, `AppAvatar`, `AppModal`, `ConfirmDialog`, `AppToastHost`.
  - `AppPagination`, `EmptyState`, `PageErrorState`, `InlineAlert`, `ActionMenu`.
  - `DataTable` con vista de tabla en escritorio y tarjetas en móvil.
  - `StatCard`, `Timeline`, `BalanceChips`.
- Layouts:
  - `AuthLayout` + `AuthCard`.
  - `BackofficeLayout` (sidebar técnico + header).
  - `MerchantLayout` (sidebar comercio + header).
- Router con guardas de autenticación, portal y rol.
- Stores Pinia por dominio.
- Cliente API tipado (`src/services/`) sin capa de datos locales.

### FASE 2 — Portal técnico ✅

- Acceso técnico con validaciones y errores de credenciales.
- Bandeja de tickets:
  - 4 tarjetas de métricas.
  - Búsqueda, filtros de estado/comercio/fecha, orden y limpieza.
  - Tabla, badges, acciones, paginación y estado vacío.
- Detalle de ticket:
  - Incidencia, datos, descripción, respuesta, gestión, historial y eliminación.
  - Cambio de estado con aviso de cambios sin guardar.
  - Toast de éxito y banner de error.
  - Vista 404 de ticket.
- Modales y menús: confirmar eliminación, acciones de fila y selector de estado.

### FASE 3 — Administración de comercios ✅

- Listado con métricas, búsqueda, filtro por estado, orden y paginación.
- Alta de comercio con validaciones (obligatorio y máximo 100 caracteres).
- Baja con confirmación.
- **Reactivación** con confirmación (decisión aprobada).
- Menú de acciones por fila.
- Toasts de alta, baja y reactivación.
- Estados vacío y sin coincidencias.
- **Acceso exclusivo del administrador**:
  - El rol técnico no ve “Comercios” en la navegación.
  - Guarda real de ruta: `/tecnico/comercios` declara `meta.roles: ['admin']` y la guarda de `router/guards.ts` valida el rol antes de entrar.
  - Si el técnico accede por URL directa, se le redirige a `/tecnico/comercios/restringido` (frame 33), que muestra “Acceso restringido”.
  - La guarda es una restricción de navegación en el cliente; la autorización definitiva debe aplicarla el backend.

### FASE 4 — Portal del comercio ✅

- Acceso del comercio con los mismos estados que el acceso técnico.
- Inicio: saludos, saldos por moneda, resumen de pagos y últimos pagos.
- Estado sin pagos.
- Pagos recibidos: filtros de estado, moneda y fecha, búsqueda, orden, tabla y paginación.
- Detalle de pago:
  - Estados aceptado y rechazado, con el importe en su moneda.
  - Método de pago, concepto, fecha y nº de transacción.
  - Historial con segundos.
  - Acción de devolución según estado.
  - Pago no encontrado.
- Saldo y retiradas:
  - Tarjetas por moneda (EUR, USD y GBP).
  - Formulario con moneda, importe y “Retirar todo”.
  - Validaciones de importe y saldo insuficiente por moneda.
  - Confirmación con resumen y saldo resultante.
  - Toast de éxito, actualización de saldo y banner de error.

### FASE 5 — Devoluciones ✅

- Pantalla `Devoluciones` del comercio (frames 76–78):
  - Métricas de solicitadas, aceptadas y rechazadas.
  - Buscador por cliente o ID de pago, filtros de estado y fecha, orden y limpieza.
  - Tabla con fecha, ID pago, cliente, importe, motivo, estado y acciones; paginación.
  - Las solicitudes pendientes muestran **Aceptar** y **Rechazar**; el resto, **Ver pago**.
  - El comercio gestiona la devolución: al aceptar se abona al cliente y **se descuenta del saldo** de esa moneda.
  - Modal de aceptación con saldo actual, importe y saldo resultante.
- Modal de solicitud desde el detalle de pago: datos del pago, importe total no editable y motivo opcional.
- Integración con `GET /refunds`, `POST /refunds/request`, `POST /refunds/accept` y `POST /refunds/reject`.
- El botón de solicitud queda deshabilitado si ya existe una devolución para el pago.

### FASE 7 — Soporte del comercio ✅

- Sustituida la pantalla “próximamente” (frames 79–81).
- Listado `Soporte` en `/comercio/tickets`:
  - Métricas de abiertos, en proceso y cerrados.
  - Buscador por ID o asunto, filtro de estado y limpieza.
  - Tabla con ID, asunto, estado, creación y última actualización; indicador de respuesta nueva del técnico.
  - Paginación y acción “+ Nuevo ticket”.
- Modal de nuevo ticket con asunto y descripción obligatorios.
- Detalle `/comercio/tickets/:id`:
  - Migas, asunto, estado, fecha y descripción.
  - Conversación comercio ↔ técnico y formulario para añadir comentario.
  - Historial de estados del ticket.

### FASE 8 — Tickets, técnicos y perfiles ✅

- Bandeja de tickets rediseñada para técnico y administrador:
  - Cuatro métricas, filtros y orden.
  - Pestañas “Asignados a mí / Sin asignar / Todos”.
  - Columna de responsable y acciones por rol.
- Asignación de tickets:
  - El técnico puede asignarse el ticket a sí mismo.
  - El administrador asigna o reasigna con buscador de técnicos y número de tickets abiertos.
  - El historial registra la asignación.
- Detalle del ticket con responsable, gestión, conversación, historial y eliminación para el equipo técnico.
- **Técnicos** (solo administrador):
  - Métricas, buscador, filtro por estado y tabla con correo/usuario/rol/estado.
  - Alta de técnico con generación de contraseña y “obligar a cambiarla”.
  - Modal de confirmación con usuario/contraseña y botones de copia.
  - “Ver perfil” con actividad del técnico.
- **Mi perfil**:
  - Administrador y técnico: datos personales, actividad y cambio de contraseña.
  - Comercio: datos fiscales, dirección, contacto y cambio de contraseña.
  - Acceso desde el bloque de perfil de la barra lateral.
- **Alta de comercio** pasa de modal a página completa con datos fiscales, dirección y contacto.
- La barra lateral muestra “Comercios” y “Técnicos” solo al administrador; el técnico que entra por URL directa a Comercios ve el acceso restringido.

### FASE 6 — Responsive y revisión visual ✅

- Escritorio mantiene la referencia de 1440 × 1024.
- Tablet:
  - Sidebar en drawer.
  - Métricas en 2 columnas.
  - Formularios y grids adaptados.
- Móvil:
  - Header compacto con menú hamburguesa.
  - Drawer con overlay y botón de cierre.
  - Tablas convertidas en tarjetas con etiquetas.
  - Paginación simplificada.
  - Modales a ancho completo y altura máxima.
- Comparación visual realizada sobre las pantallas principales y los estados críticos.

---

## 2. Cobertura de las 76 pantallas

No se creó una ruta por cada frame. Los frames se agruparon en páginas funcionales y sus estados se implementaron mediante interacción, datos y overlays.

| Página | Frames cubiertos | Implementación |
|---|---|---|
| Acceso técnico | 01, 10, 11, 12, 14, 16 | Login, formulario relleno, falta usuario, credenciales, contraseña visible y sesión cerrada |
| Bandeja de tickets | 02, 07, 08, 15, 23 | Listado, actualización de fila, filtros sin resultados, eliminación y recálculo |
| Detalle del ticket | 03, 04, 05, 06, 09, 20, 21, 22 | Estado base, cambios sin guardar, respuesta, toast, error, guardado y cierre |
| Ticket no encontrado | 13 | Estado 404 dentro del layout |
| Comercios | 24–37, 47–51 | Listado, filtros, orden, paginación, vacíos, restricción y toasts |
| Nuevo comercio | 38–42 | Modal base, relleno, obligatorio, longitud y error de acción |
| Confirmar baja | 43 | Modal de confirmación |
| Acciones/filtros/orden de comercios | 44, 45, 46 | Menú y selects |
| Acceso comercio | 52, 57, 58, 59, 60, 74 | Login y estados |
| Inicio del comercio | 53, 61 | Dashboard y estado sin pagos |
| Pagos | 55, 67 | Listado y sin coincidencias |
| Detalle de pago | 56, 68–72 | Aceptado y rechazado con los datos del contrato actual; el resto de variantes de Figma no tienen respaldo en la API |
| Saldo | 54, 62–66, 73 | Saldo, formulario, validaciones, confirmación, éxito y error |
| Confirmar retirada | 75 | Modal con resumen y saldo resultante |
| Devoluciones del comercio | 76 | Métricas, filtros, tabla, acciones y paginación |
| Solicitar devolución | 77 | Modal con datos del pago y motivo opcional |
| Aceptar devolución | 78 | Modal con saldo actual y resultante |
| Soporte del comercio | 79 | Métricas, filtros, tabla y paginación |
| Nuevo ticket | 80 | Modal con asunto y descripción obligatorios |
| Detalle del ticket del comercio | 81 | Datos, conversación, comentario e historial |
| Bandeja de tickets del equipo | 02, 34 | Variantes técnico/administrador, asignación y responsables |
| Detalle del ticket del equipo | 03, 34 | Gestión, asignación, historial y eliminación |
| Asignar técnico | 34 | Buscador y lista de técnicos con carga |
| Técnicos | 82, 83, 84 | Listado, alta y confirmación con credenciales |
| Mi perfil | 85, 86, 87, 88 | Administrador, técnico, comercio y cambio de contraseña |
| Nuevo comercio | 38 | Alta completa con datos fiscales y contacto |
| Menú y estados del ticket | 17, 18, 19 | Modal, menú y selector |

**Páginas nuevas no presentes en Figma**, construidas con el sistema visual existente:

- `/comercio/devoluciones` y `/comercio/tickets` (ampliadas en los frames 75–81).
- `/tecnico/comercios/restringido` (frame 33, estado de permisos con ruta propia).
- `/comercio/tickets/:id` (detalle de soporte del comercio).

---

## 3. Decisiones funcionales aplicadas

1. **Comercios solo para administrador**: navegación oculta para técnicos, `meta.roles: ['admin']` con guarda real y redirección a la ruta de acceso restringido.
2. **Reactivación de comercios**: se implementa con confirmación contra `PUT /companies/reactivate?id=`, con baja lógica en `DELETE /companies/delete`.
3. **Devoluciones**: el comercio gestiona las solicitudes de sus clientes; aceptar abona al cliente y descuenta el importe del saldo de esa moneda.
4. **Tickets del comercio**: listado, alta, conversación e historial implementados; el comercio solo ve los tickets de su empresa.
5. **Responsive**: escritorio intacto; adaptaciones para tablet y móvil.
6. **Sin mocks**: el frontend consume únicamente `api/api.yaml`; no hay capa demo ni datos locales.
7. **Rol desde el backend**: `/login` devuelve el usuario y su rol; el frontend ya no lo deduce del nombre de usuario.

---

## 4. Arquitectura implementada

```
frontend/
├── public/images/avatar-laura.jpg
├── public/images/logo-plp.svg
├── src/
│   ├── assets/styles/        # tokens.css + main.css
│   ├── layouts/              # AuthLayout, BackofficeLayout, MerchantLayout
│   ├── modules/
│   │   ├── auth/             # TechLogin, MerchantLogin, SessionClosed
│   │   ├── tech/
│   │   │   ├── tickets/      # vistas + filtros, estado, historial, modales
│   │   │   └── merchants/    # vistas + filtros, alta, acciones, confirmación
│   │   └── merchant/
│   │       ├── home/
│   │       ├── payments/
│   │       ├── balance/
│   │       ├── refunds/        # listado + filtros + modales
│   │       └── tickets/        # soporte, nuevo ticket y detalle
│   ├── router/               # rutas + guardas
│   ├── shared/
│   │   ├── components/       # ui, layout y data
│   │   └── utils/            # formatos y estados
│   ├── stores/               # auth, ui, tickets, support, merchants, payments, balance, refunds
│   ├── services/             # cliente HTTP + servicios por dominio
│   └── types/
├── nginx.conf
├── tailwind.config.ts
└── vite.config.ts
```

### Stores

| Store | Responsabilidad |
|---|---|
| `auth` | Sesión, rol, login/logout, persistencia |
| `ui` | Toasts y drawer móvil |
| `tickets` | Listado, filtros, orden, paginación, guardado y borrado (portal técnico) |
| `support` | Soporte del comercio: listado, alta, comentarios y paginación |
| `merchants` | Listado, filtros, alta, baja y reactivación |
| `payments` | Listado, filtros, pagos y detalle |
| `balance` | Saldo disponible y retiradas |
| `refunds` | Devoluciones: filtros, orden, paginación, aceptar y rechazar |

---

## 5. Integración con la API

| Función | Endpoint | Estado |
|---|---|---|
| Login | `POST /login?user=` | Implementado; devuelve token, usuario y rol |
| Logout | `POST /logout` | Implementado |
| Saldo | `GET /balance` | Implementado (saldo por moneda) |
| Retirada | `POST /withdraw?amount=&currency=` | Implementado (por moneda) |
| Pagos | `GET /payments` | Implementado |
| Tickets | `GET /tickets` | Implementado (tickets de soporte) |
| Actualizar ticket | `PUT /ticket/update?id=` | Implementado (`status` y `reply`) |
| Eliminar ticket | `DELETE /ticket/delete?id=` | Implementado (requiere admin) |
| Comercios | `GET /companies` | Implementado (requiere admin) |
| Alta de comercio | `PUT /companies/add?nombre=` | Implementado |
| Baja de comercio | `DELETE /companies/delete?id=` | Implementado (baja lógica) |
| Reactivación | `PUT /companies/reactivate?id=` | Implementado |
| Devoluciones | `GET /refunds` | Implementado |
| Solicitar devolución | `POST /refunds/request?transaction_id=&reason=` | Implementado |
| Aceptar devolución | `POST /refunds/accept?id=` | Implementado; descuenta saldo |
| Rechazar devolución | `POST /refunds/reject?id=` | Implementado |
| Pagos | `POST /pay` | Implementado; crea transacción real |
| Tickets | `GET /tickets` | Implementado (filtrados por empresa para el comercio) |
| Mensaje de ticket | `POST /ticket/message?id=` | Implementado |
| Asignar ticket | `PUT /ticket/assign?id=` | Implementado |
| Técnicos | `GET /technicians`, `POST /technicians` | Implementado (admin) |
| Perfil | `GET /profile`, `PUT /profile` | Implementado |
| Cambiar contraseña | `POST /profile/password` | Implementado |

### Brechas del contrato que se asumen en la UI

- `GET /payments` no devuelve tarjeta, comisión ni neto: la tabla y el detalle muestran cliente, factura, concepto, importe, estado y fecha.
- No existe `GET /payments/{id}`: el detalle se resuelve con la lista; un acceso directo recarga antes de buscar.
- `POST /refunds/accept` descuenta el importe del saldo de esa moneda; no hay pasarela real de abono al cliente.
- El backend y la base de datos son la fuente de verdad: los cambios persisten entre reinicios.
- El rol de administrador se valida en servidor a partir del token de DRF; la guarda del cliente solo protege la navegación.

---

## 6. Sistema visual aplicado

- Tokens en `src/assets/styles/tokens.css` y `tailwind.config.ts`.
- Colores principales:
  - Marca: `#1E0F52`, `#321A83`, `#EDE9FA`.
  - Acento: `#14B8A6`.
  - Neutros: `#F8FAFC`, `#FFFFFF`, `#E2E8F0`, `#0F172A`, `#475569`, `#64748B`.
  - Estados: ámbar, azul, verde, rojo y neutro.
- Tipografía Inter, interlineado 1.5.
- Sin sombras; bordes de 1 px.
- Radios: 8, 10, 12, 14 y circular.
- Layout: sidebar 224 px, header 96 px, contenido 1152 px.
- Tabla: cabecera 44 px, filas 62 px.
- Formularios: 44/48 px.
- Botones: 40/44/48 px.

---

## 7. Verificación realizada

### Comandos

```bash
cd frontend
npm install
npm run typecheck
npm run build
```

```bash
docker run --rm -v "$PWD":/app -w /app/backend -e DB_ENGINE=sqlite plp-backend python manage.py test api pagos
```

Resultado: **sin errores de tipos ni de build**; **39 tests del backend en verde** (API + modelo).

### Integración con la API y la base de datos

Comprobado contra el stack Docker (`backend` + MySQL) con datos reales:

- `POST /login` con `admin`, `tpv01` y `comercio` devuelve token de DRF y `user.role`.
- `GET /balance`, `/payments`, `/refunds` y `/tickets` están filtrados por la empresa del token.
- Importes y saldos llegan como números; los estados de pago incluyen `pending`, `approved`, `rejected` y `refunded`.
- Aceptar una devolución por `id` descuenta el saldo y marca la transacción como `refunded`.
- Un ticket creado y su comentario siguen existiendo tras reiniciar el backend.
- `GET /companies` responde 200 al admin y 403 al técnico usando solo el token.
- `seed_demo` carga usuarios, empresas, saldos, pagos, devoluciones y tickets en la base de datos.

### QA en navegador

- **Pendiente**: repetir los flujos E2E contra la API real (login de los tres roles, tickets, comercios, pagos, saldo y devoluciones). Los resultados anteriores correspondían al modo demo, ya eliminado.
- **Pendiente**: revisar el estado de acceso restringido (`/tecnico/comercios/restringido`) y las nuevas columnas de pagos/saldo.

### QA visual

Capturas comparadas a 1440 × 1024 y 390 × 844:

- Acceso técnico.
- Bandeja, detalle y modal de ticket.
- Comercios y modal de alta con error.
- Inicio, pagos y detalle de pago del comercio.
- Saldo, error de importe y modal de devolución.
- Devoluciones (versión anterior, antes de los frames 76–78).
- Tablas y navegación en móvil.

Correcciones aplicadas tras la comparación:

- Alturas y espaciado de la tarjeta de acceso.
- Fondo lavanda de la tarjeta de saldo destacada.
- Formato español de importes con separador de miles.
- Orden inicial de tickets para mostrar los casos del diseño.
- Botones de guardar/cancelar activos como en Figma.
- Historial de pagos con segundos sin duplicar la hora.
- Orden de ayuda y error en formularios.
- Anchos de columnas de pagos y clientes.
- Nombre del comercio en la barra lateral.
- Botón de cierre del drawer móvil.
- Enlaces con semántica correcta (`AppButton` con `to`).

---

## 8. Desviaciones y pendientes

### Desviaciones conscientes

1. **Logo**: se usa el SVG aportado por el equipo (`public/images/logo-plp.svg`); en el sidebar se invierte a blanco para el fondo morado.
2. **Avatar técnico**: se usa la imagen del diseño descargada de Figma (`avatar-laura.jpg`).
3. **Paginación**: se muestran números de página además de anterior/siguiente. Figma solo muestra un número en los frames revisados.
4. **Reactivación**: nueva acción no presente en Figma, aprobada funcionalmente.
5. **Devoluciones**: el comercio gestiona las solicitudes y aceptar descuenta su saldo, según los mockups 76–78.
6. **Soporte del comercio**: listado, alta y conversación con historial, según los mockups 79–81.
7. **Asignación de tickets**: técnico y administrador tienen acciones distintas; el técnico solo puede asignarse a sí mismo.
8. **Mi perfil**: el comercio edita datos de su empresa; técnicos y administradores editan sus datos personales.
9. **Móvil/tablet**: no hay diseño de referencia; se aplicaron patrones coherentes.
10. **Título “Administradora”**: el rol admin muestra ese subtítulo; Figma muestra “Técnica de soporte” para Laura.
11. **Pagos**: la API no aporta tarjeta, comisión ni neto; se muestran cliente, factura, concepto, importe, estado y fecha.
12. **Estados de pago**: se exponen los cuatro del modelo (`pending`, `approved`, `rejected`, `refunded`) con badge y filtro.

### Pendiente de producto/backend

- Flujo administrativo de aceptar/rechazar devoluciones (fuera del portal del comercio).
- Repetir el QA en navegador del nuevo estado de acceso restringido (`/tecnico/comercios/restringido`).
- Comparar visualmente los frames 75–88 (devoluciones, soporte, técnicos y perfiles) una vez levantado el frontend.
- Definir la desactivación de técnicos: el filtro de estado existe, pero aún no hay endpoint para cambiar `is_active`.
- Validar con el equipo si la paginación debe limitarse a anteriores/siguientes.
- Revisión de accesibilidad con usuarios reales y pruebas en navegadores/dispositivos.
