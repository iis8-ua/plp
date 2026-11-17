# Análisis del diseño — PLP · Pasa La Pasta

> Análisis previo a la implementación frontend. **No se ha generado código ni modificado configuración del proyecto.** Este documento es el único artefacto creado.

| Campo | Valor |
|---|---|
| Archivo Figma | **PLP - Pasa La Pasta** |
| fileKey | `ObSDRIxWFqQwnTz6OMKB7D` |
| Página | `0:1` — **Page 1** (única página) |
| Frames de nivel superior | **76** |
| Lienzo por frame | 1440 × 1024 px (escritorio) |
| Componentes/instancias Figma | **0** |
| Variables/estilos Figma | **0** (`get_variable_defs` → `{}`) |
| Librerías suscritas | **0** |
| Tipografía | **Inter** (400/500/600/700) |
| Fecha del análisis | 17 nov 2026 |

---

## 0. Resumen ejecutivo

- Los 76 frames no son 76 páginas: equivalen a **9 páginas funcionales** más estados, modales, menús, toasts y errores.
- Existen **tres módulos** con dos shells compartidos:
  - **Backoffice** (Portal técnico + Administración de comercios): misma barra lateral y cabecera.
  - **Portal del comercio**: barra lateral y cabecera propias.
- El archivo **no usa componentes de Figma, variables ni estilos**. Todo está construido con frames y texto duplicados (la barra lateral aparece ~50 veces). La implementación debe componentizar desde cero.
- El diseño es **exclusivamente escritorio** (1440 px). No hay referencias responsive.
- **No se usan sombras**: la jerarquía se resuelve con bordes de 1 px, fondos blancos y radios suaves.
- Hay varios flujos representados parcialmente (reembolsos, navegación del comercio, reactivación de comercios). Se detallan en “Inconsistencias” y “Pendientes”.

---

## 1. Inventario de las 76 pantallas

Módulos: **T** = Portal técnico (01–23), **C** = Administración de comercios (24–51), **P** = Portal del comercio (52–76).

| # | nodeId | Frame | Mód. | Tipo |
|---:|---|---|:---:|---|
| 01 | `2:2` | 01 · Acceso técnicos | T | Página base (login) |
| 02 | `2:4` | 02 · Bandeja de tickets | T | Página base (listado) |
| 03 | `2:8` | 03 · Detalle del ticket | T | Página base (detalle) |
| 04 | `2:275` | 04 · Estado en proceso | T | Estado de detalle (cambio sin guardar) |
| 05 | `2:352` | 05 · Feedback preparado | T | Estado de formulario (respuesta escrita) |
| 06 | `2:429` | 06 · Ticket actualizado | T | Estado guardado + toast de éxito |
| 07 | `2:517` | 07 · Bandeja actualizada | T | Estado de listado (fila actualizada) |
| 08 | `2:692` | 08 · Sin resultados | T | Estado vacío de listado |
| 09 | `2:872` | 09 · Error al guardar | T | Estado de error (banner) |
| 10 | `2:950` | 10 · Acceso completado | T | Estado de login (formulario relleno) |
| 11 | `2:974` | 11 · Falta usuario | T | Validación inline |
| 12 | `2:999` | 12 · Credenciales incorrectas | T | Error de formulario |
| 13 | `2:1025` | 13 · Ticket no encontrado | T | Página de error 404 |
| 14 | `2:1104` | 14 · Sesión cerrada | T | Estado post-logout |
| 15 | `2:1309` | 15 · Ticket eliminado | T | Estado de listado (fila eliminada) |
| 16 | `2:1484` | 16 · Contraseña visible | T | Estado de input |
| 17 | `2:1508` | 17 · Confirmar eliminación | T | Modal de confirmación |
| 18 | `2:1518` | 18 · Menú del ticket | T | Menú/popover de acciones |
| 19 | `2:1525` | 19 · Estados del ticket | T | Select desplegable |
| 20 | `2:1537` | 20 · Detalle actualizado | T | Estado guardado (historial ampliado) |
| 21 | `2:1617` | 21 · Preparar cierre | T | Estado de formulario (cierre sin guardar) |
| 22 | `2:1692` | 22 · Ticket cerrado | T | Estado guardado (cerrado) |
| 23 | `2:1769` | 23 · Bandeja tras cierre | T | Estado de listado |
| 24 | `12:56` | 24 · Comercios | C | Página base (listado) |
| 25 | `12:375` | 25 · Comercio creado · Éxito | C | Listado + toast |
| 26 | `12:565` | 26 · Comercios · Alta aplicada | C | Estado de listado |
| 27 | `12:745` | 27 · Comercio dado de baja · Éxito | C | Listado + toast |
| 28 | `12:922` | 28 · Comercios · Baja aplicada | C | Estado de listado |
| 29 | `12:1094` | 29 · Alta y baja aplicadas · Éxito | C | Listado + toast |
| 30 | `12:1275` | 30 · Comercios · Alta y baja aplicadas | C | Estado de listado |
| 31 | `12:1451` | 31 · Comercios · Estado vacío | C | Estado vacío global |
| 32 | `12:1628` | 32 · Comercios · Sin coincidencias | C | Estado vacío filtrado |
| 33 | `12:1806` | 33 · Comercios · Acceso restringido | C | Estado de permisos |
| 34 | `12:1987` | 34 · Comercios · Activos | C | Variante de filtro |
| 35 | `12:2160` | 35 · Comercios · Dados de baja | C | Variante de filtro |
| 36 | `12:2333` | 36 · Comercios · Más recientes | C | Variante de orden |
| 37 | `12:2506` | 37 · Comercios · Segunda página | C | Variante de paginación |
| 38 | `12:2679` | 38 · Nuevo comercio | C | Modal (alta) |
| 39 | `12:2693` | 39 · Nuevo comercio · Preparado | C | Modal con datos |
| 40 | `12:2707` | 40 · Nuevo comercio · Nombre obligatorio | C | Validación |
| 41 | `12:2722` | 41 · Nuevo comercio · Nombre demasiado largo | C | Validación |
| 42 | `12:2738` | 42 · Nuevo comercio · Error de acción | C | Error de servidor/red |
| 43 | `12:2755` | 43 · Confirmar baja | C | Modal de confirmación |
| 44 | `12:2765` | 44 · Acciones del comercio | C | Menú de acciones |
| 45 | `12:2771` | 45 · Filtro de comercios | C | Select desplegable |
| 46 | `12:2780` | 46 · Ordenar comercios | C | Select desplegable |
| 47 | `12:2787` | 47 · Alta tras baja · Éxito | C | Listado + toast |
| 48 | `12:2963` | 48 · Primer comercio · Éxito | C | Listado + toast |
| 49 | `12:3143` | 49 · Comercios · Primer comercio | C | Estado de listado |
| 50 | `12:3243` | 50 · Primer comercio dado de baja · Éxito | C | Listado + toast |
| 51 | `12:3344` | 51 · Comercios · Primer comercio de baja | C | Estado de listado |
| 52 | `12:5086` | 52 · Comercio · Acceso | P | Página base (login comercio) |
| 53 | `12:5088` | 53 · Comercio · Inicio | P | Página base (dashboard) |
| 54 | `12:5138` | 54 · Comercio · Saldo | P | Página base (saldo/retirada) |
| 55 | `12:5188` | 55 · Comercio · Pagos recibidos | P | Página base (listado) |
| 56 | `12:5237` | 56 · Comercio · Detalle de pago aceptado | P | Página base (detalle) |
| 57 | `12:5311` | 57 · Comercio · Acceso completado | P | Estado de login (formulario relleno) |
| 58 | `12:5336` | 58 · Comercio · Falta usuario | P | Validación inline |
| 59 | `12:5362` | 59 · Comercio · Credenciales incorrectas | P | Error de formulario |
| 60 | `12:5389` | 60 · Comercio · Contraseña visible | P | Estado de input |
| 61 | `12:5723` | 61 · Comercio · Inicio sin pagos | P | Estado vacío |
| 62 | `12:5861` | 62 · Comercio · Retirada de 300 EUR | P | Formulario relleno |
| 63 | `12:5958` | 63 · Comercio · Importe no válido | P | Validación |
| 64 | `12:6056` | 64 · Comercio · Saldo insuficiente para retirar | P | Validación |
| 65 | `12:6154` | 65 · Comercio · Retirada realizada | P | Saldo + toast |
| 66 | `12:6258` | 66 · Comercio · Saldo actualizado | P | Saldo actualizado (sin toast) |
| 67 | `12:6362` | 67 · Comercio · Pagos sin coincidencias | P | Estado vacío filtrado |
| 68 | `12:6539` | 68 · Comercio · Pago rechazado | P | Detalle (estado) |
| 69 | `12:6643` | 69 · Comercio · Pago reembolsado | P | Detalle (estado) |
| 70 | `12:6758` | 70 · Comercio · Pago en proceso | P | Detalle (estado) |
| 71 | `12:6862` | 71 · Comercio · Pago aceptado en GBP | P | Detalle (variante moneda) |
| 72 | `12:6965` | 72 · Comercio · Pago no encontrado | P | Error de detalle |
| 73 | `12:7073` | 73 · Comercio · Error de retirada | P | Error de acción (banner) |
| 74 | `12:7172` | 74 · Comercio · Sesión cerrada | P | Estado post-logout |
| 75 | `12:7201` | 75 · Comercio · Confirmar retirada | P | Modal de confirmación |
| 76 | `12:7232` | 76 · Comercio · Moneda de retirada | P | Select desplegable |

**Recuento:** 23 frames del portal técnico + 28 de administración + 25 del portal del comercio = **76**.

---

## 2. Agrupación por páginas y estados

### 2.1 Páginas funcionales (9)

| Página | Ruta propuesta | Frames que la representan | Nº |
|---|---|---|:--:|
| **Acceso técnico** | `/acceso-tecnico` | 01, 10, 11, 12, 14, 16 | 6 |
| **Bandeja de tickets** | `/tecnico/tickets` | 02, 07, 08, 15, 23 | 5 |
| **Detalle del ticket** | `/tecnico/tickets/:id` | 03, 04, 05, 06, 09, 20, 21, 22 | 8 |
| **Ticket no encontrado** | misma ruta, estado 404 | 13 | 1 |
| **Comercios** | `/tecnico/comercios` | 24–37, 47–51 | 19 |
| **Acceso comercio** | `/acceso-comercio` | 52, 57, 58, 59, 60, 74 | 6 |
| **Inicio del comercio** | `/comercio/inicio` | 53, 61 | 2 |
| **Pagos recibidos** | `/comercio/pagos` | 55, 67 | 2 |
| **Detalle de pago** | `/comercio/pagos/:id` | 56, 68, 69, 70, 71, 72 | 6 |
| **Saldo y retiradas** | `/comercio/saldo` | 54, 62, 63, 64, 65, 66, 73 | 7 |

**Overlays** (no son páginas; se abren sobre una de las anteriores):

| Overlay | Frames | Se abre desde |
|---|---|---|
| Confirmar eliminación de ticket | 17 | Detalle del ticket |
| Menú de acciones del ticket | 18 | Fila de bandeja / detalle |
| Selector de estado del ticket | 19 | Tarjeta “Gestión” |
| Modal Nuevo comercio | 38–42 | Comercios |
| Confirmar baja de comercio | 43 | Menú de fila de comercio |
| Menú de acciones del comercio | 44 | Fila de comercio |
| Filtro de estado de comercios | 45 | Barra de filtros |
| Ordenación de comercios | 46 | Barra de filtros |
| Confirmar retirada | 75 | Saldo |
| Selector de moneda | 76 | Formulario de retirada |

### 2.2 Estructuras compartidas

**Estructura A — Autenticación (12 frames)**
- Fondo degradado, logo superior izquierdo, etiqueta de portal, tarjeta central de 464 × 624, pie de página.
- Dos variantes de copy: técnicos y comercios.
- Estados: base (01/52), formulario relleno (10/57), falta usuario (11/58), credenciales incorrectas (12/59), contraseña visible (16/60), sesión cerrada (14/74).

**Estructura B — Backoffice (33 frames)**
- Barra lateral de 224 px + cabecera de 96 px + área de trabajo de 1152 px.
- Navegación: **Tickets**, **Comercios**; usuario técnico y “Cerrar sesión”.
- Subgrupos: tickets (02–09, 13, 15, 17–23) y comercios (24–37, 43–51).
- Las páginas de comercios reutilizan exactamente el mismo shell que tickets.

**Estructura C — Portal del comercio (17 frames con shell)**
- Barra lateral de 224 px con: **Inicio**, **Pagos**, **Saldo**, **Devoluciones**, **Tickets**.
- Cabecera con nombre del comercio (“Librería Horizonte”), rol “Comercio” y avatar con iniciales.
- Subgrupos: inicio (53, 61), pagos (55, 56, 67–72), saldo (54, 62–66, 73).

### 2.3 Formularios, modales, confirmaciones y errores

| Categoría | Frames |
|---|---|
| **Formularios** | Login técnico (01), login comercio (52), gestión/respuesta de ticket (03–06, 09, 20–22), alta de comercio (38–42), retirada de fondos (54, 62–66, 73), filtros/buscadores (02, 24, 55) |
| **Modales** | 17 (eliminar ticket), 38–42 (nuevo comercio), 43 (confirmar baja), 75 (confirmar retirada) |
| **Confirmaciones explícitas** | 17, 43, 75 (+ aviso “Esta acción es permanente” en detalle de ticket) |
| **Errores de validación** | 11, 40, 41, 58, 63, 64 |
| **Errores de credenciales** | 12, 59 |
| **Errores de acción/servidor** | 09, 42, 73 |
| **Estados vacíos** | 08, 31, 32, 61, 67 |
| **Errores de recurso** | 13 (404 ticket), 72 (pago no encontrado) |
| **Toasts de éxito** | 06, 25, 27, 29, 47, 48, 50, 65 |
| **Menús/desplegables** | 18, 19, 44, 45, 46, 76 |

### 2.4 Distribución de frames por página

| Página | Base | Estados/variantes | Overlays asociados | Total |
|---|:--:|:--:|:--:|:--:|
| Acceso técnico | 1 | 5 | — | 6 |
| Bandeja de tickets | 1 | 4 | 2 (18, 19) | 7 |
| Detalle del ticket | 1 | 7 | 1 (17) | 9 |
| Comercios | 1 | 18 | 9 (38–46) | 28 |
| Acceso comercio | 1 | 5 | — | 6 |
| Inicio comercio | 1 | 1 | — | 2 |
| Pagos | 1 | 1 | — | 2 |
| Detalle de pago | 1 | 5 | — | 6 |
| Saldo | 1 | 6 | 2 (75, 76) | 9 |
| **Total** | **9** | **52** | **14** | **76** |

---

## 3. Componentes reutilizables

> No existen componentes de Figma. Los “componentes” son patrones visuales repetidos que deben implementarse una sola vez.

### 3.1 Layout

| Componente | Variantes | Dónde aparece |
|---|---|---|
| `AuthLayout` / `AuthCard` | Técnicos / Comercios | 01, 10–12, 14, 16, 52, 57–60, 74 |
| `BackofficeLayout` (shell) | Tickets / Comercios | 02–09, 13, 15, 20–23, 24–37, 47–51 |
| `MerchantLayout` (shell) | — | 53–56, 61–73 |
| `AppSidebar` | Técnico (2 ítems) / Comercio (5 ítems) | 33 + 17 frames |
| `AppHeader` | Avatar foto (técnico) / iniciales (comercio) | mismos 50 frames |
| `PageHeader` | Título + descripción + acción + timestamp | 02, 03, 24, 53, 54, 55, 56 |
| `LogoPlaceholder` | 136×122, 128×115, 108×96 | Todos los shells y logins |

### 3.2 Controles

| Componente | Variantes / medidas | Dónde aparece |
|---|---|---|
| `AppButton` | Primario `#321A83`; secundario outline morado; neutral outline `#E2E8F0`; peligro sólido `#B91C1C`; peligro outline; deshabilitado `#E2E8F0`. Alturas 40 / 44 / 48 | Todo el producto |
| `AppIconButton` | 40×40, radio 8 (ojo, cerrar, `···`) | 16, 38–42, 60, 18, 44 |
| `AppInput` | Texto, búsqueda, contraseña, importe. Altura 44/48; borde `#E2E8F0`; foco `#321A83`; error `#EF4444` | 01, 02, 11, 12, 24, 38–42, 52, 54, 55, 58–64 |
| `AppTextarea` | 688×132; contador de estado (“Respuesta lista para enviar”) | 03–06, 09, 20–22 |
| `AppSelect` | Alturas 44; anchos 192–360; variante ancha 688 (moneda) | 02, 19, 24, 45, 46, 54, 55, 75, 76 |
| `AppSearchInput` | Icono 20×20 + placeholder 13 px | 02, 24, 55 |
| `AppCheckbox` | No representado | — |

### 3.3 Datos

| Componente | Variantes / medidas | Dónde aparece |
|---|---|---|
| `AppTable` | Tickets (columnas ID/Comercio/Asunto/Estado/Creación/Actualización/Acciones); Comercios (Nombre/ID/Registro/Estado/Acciones); Pagos (Fecha/Cliente/Concepto/Importe/Estado/Motivo/Acciones). Cabecera 44 px `#F8FAFC`; filas 62 px | 02, 07, 08, 15, 23, 24–37, 47–51, 53, 55, 61, 67 |
| `AppPagination` | “Anterior” 96×40, página 40×40, “Siguiente” 156×40 | 02, 07, 15, 23, 24–37, 47–51, 55, 67 |
| `StatCard` | Técnico 270×140 (4 col.); Comercios/Saldo 368×140 (3 col.); resumen de pagos 368×104; punto de color 8×8 | 02, 07, 08, 15, 23, 24–37, 47–51, 53, 54, 61–66, 73 |
| `BalanceCard` | 368×140; variante destacada fondo lavanda | 53, 54, 61–66, 73 |
| `BalanceChips` | 3 monedas + “Ver saldo” | 55, 56, 67–72 |
| `StatusBadge` | Ticket: Abierto / En proceso / Cerrado. Comercio: Activo / Dado de baja. Pago: Aceptado / Rechazado / En proceso / Reembolsado. 28 px, radio 14 | Listados y detalles |
| `Avatar` | 40×40 foto; 40×40 iniciales; 32×32 iniciales | Cabeceras, fila de comercios |
| `Timeline` | Punto + línea vertical + evento + autor | 03–06, 09, 20–22, 56, 68–72 |
| `Breadcrumbs` | “Tickets / #1042”, “Pagos > Pago #P-1048” | 03, 20–22, 56, 68–72 |
| `EmptyState` | Título + descripción + CTA / solo texto | 08, 31, 32, 61, 67 |
| `PageErrorState` | 404 o recurso no encontrado | 13, 72 |

### 3.4 Feedback y overlays

| Componente | Variantes | Dónde aparece |
|---|---|---|
| `AppModal` | 480×316, 528×352, 560×392; overlay `rgba(15,23,42,0.45)`; radio 10/12 | 17, 38–42, 43, 75 |
| `ConfirmDialog` | Eliminar ticket, dar de baja comercio, confirmar retirada | 17, 43, 75 |
| `AppToast` | Éxito 56 px; fondo `#D1FAE5`, borde `#A7F3D0`, texto `#047857` | 06, 25, 27, 29, 47, 48, 50, 65 |
| `InlineAlert` | Error de formulario (40 px) y banner de error (64/70 px) | 12, 59, 09, 42, 73 |
| `DropdownMenu` | Menú de ticket (208×112), menú de comercio; ítems 44 px | 18, 44 |
| `SelectMenu` | Estados (344 px), filtro (224 px), orden (316 px), monedas (688 px) | 19, 45, 46, 76 |
| `FieldError` / `HelperText` | 12–13 px; error `#B91C1C` | 11, 40–42, 58, 63, 64 |
| `UnsavedHint` | “Cambios sin guardar” | 04, 05, 09, 21 |

---

## 4. Sistema visual

### 4.1 Paleta

Valores extraídos de los frames representativos. No hay variables de Figma; todos los colores están aplicados directamente.

| Token propuesto | Hex / valor | Uso observado |
|---|---|---|
| `brand-900` | `#1E0F52` | Fondo de la barra lateral |
| `brand-800` | `#2D205C` | Tonos secundarios de la barra lateral |
| `brand-700` | `#321A83` | Primario: CTA, activo, cifras, enlaces |
| `brand-600` | `#4D3D7E` | Tonos de apoyo en sidebar |
| `brand-400` | `#7767A4` | Bordes/acentos suaves |
| `brand-300` | `#C9BFEF` | Texto de navegación y microetiquetas sobre oscuro |
| `brand-200` | `#D6CCF3` | Borde de tarjeta destacada |
| `brand-100` | `#EDE9FA` | Fondo destacado (saldo EUR, avatares) |
| `accent-500` | `#14B8A6` | Indicador activo de 3 px |
| `bg-app` | `#F8FAFC` | Fondo general y cabecera de tabla |
| `surface` | `#FFFFFF` | Tarjetas, cabecera, barra de filtros |
| `border` | `#E2E8F0` | Borde de 1 px en tarjetas, inputs, botones |
| `border-soft` | `#F1F5F9` | Fondo de badges neutros y avatares inactivos |
| `text-primary` | `#0F172A` | Títulos y texto principal |
| `text-secondary` | `#475569` | Texto secundario |
| `text-muted` | `#64748B` | Descripciones, metadatos, cabecera de tabla |
| `success-bg` | `#D1FAE5` | Badge/Toast de éxito |
| `success-border` | `#A7F3D0` | Borde del toast |
| `success-text` | `#047857` | Texto de éxito |
| `warning-bg` | `#FEF3C7` | Badge “Abierto” / “En proceso” |
| `warning-text` | `#B45309` | Texto de advertencia |
| `info-bg` | `#E0F2FE` | Badge “En proceso” (ticket) |
| `info-text` | `#0369A1` | Texto informativo |
| `danger-bg` | `#FEE2E2` | Badge “Rechazado” |
| `danger-soft` | `#FEF2F2` | Banner de error |
| `danger-border` | `#FECACA` | Borde de banner de error |
| `danger` | `#B91C1C` | Texto/botón de eliminar |
| `danger-border-strong` | `#EF4444` | Borde de input con error |
| `neutral-bg` | `#F1F5F9` | Badge “Dado de baja” / “Reembolsado” |
| `neutral-text` | `#475569` | Texto de badge neutro |
| `overlay` | `rgba(15,23,42,0.45)` | Fondo de modales |
| `sidebar-line` | `rgba(201,191,239,0.25)` | Separador de sidebar |
| `sidebar-border` | `rgba(201,191,239,0.60)` | Borde discontinuo del logo |
| `sidebar-surface` | `rgba(255,255,255,0.06)` | Fondo del logo |
| `gradient-login` | `linear-gradient(136.52deg, #F2EDFA 0%, #F8FAFC 39.29%, #E9E1F7 71.43%)` | Fondo de acceso |

> El color `#321A83` se usa tanto para marca como para texto de énfasis y foco. No hay token de hover/pressed documentado.

### 4.2 Tipografía

- **Familia única:** Inter.
- **Pesos:** 400 Regular, 500 Medium, 600 SemiBold, 700 Bold (700 solo en contadores y algún énfasis).
- **Interlineado:** `1.5` en todos los textos analizados.

| Rol | Tamaño | Peso | Color |
|---|---:|---:|---|
| Título de cabecera de app | 24 px | 600 | `#0F172A` |
| Título de página (listados) | 24 px | 600 | `#0F172A` |
| Título de detalle de ticket | 26 px | 600 | `#0F172A` |
| Título de login | 28 px | 600 | `#0F172A` |
| Título de modal | 24 px | 600 | `#0F172A` |
| Título de tarjeta/sección | 18 px | 600 | `#0F172A` |
| Título de pago | 20 px | 600 | `#0F172A` |
| Cifra de stat | 36 px | 600 | según estado |
| Etiqueta de stat | 14 px | 500 | `#64748B` |
| Contexto de stat | 12 px | 400 | `#64748B` |
| Cuerpo / descripción | 14 px | 400 | `#64748B` |
| Etiqueta de formulario | 14 px | 500 | `#0F172A` |
| Texto de botón | 14 px | 600 | blanco / `#321A83` / `#B91C1C` |
| Navegación de sidebar | 15 px | 500 / 600 activo | `#C9BFEF` / blanco |
| Microetiqueta de sidebar | 10 px | 600 | `#C9BFEF` |
| Cabecera de tabla | 12 px | 600 | `#64748B` |
| Celda de tabla | 13 px | 400 | `#0F172A` |
| ID de ticket | 13 px | 600 | `#321A83` |
| Metadato de tabla | 12 px | 400/500 | `#64748B` |
| Badge | 12 px (14 px en detalle de pago) | 500 | según estado |
| Toast | 14 px | 500 | `#047857` / `#B91C1C` |
| Microetiqueta de detalle | 10 px | 600 | `#64748B` |
| Pie de login | 13 px | 400 | `#64748B` |

Escala completa observada: **10, 11, 12, 13, 14, 15, 18, 20, 22, 24, 26, 28, 32, 36 px**.

### 4.3 Bordes, radios y sombras

- **Sombras:** ninguna en los frames analizados. Ni tarjetas, ni modales, ni menús.
- **Grosor de borde:** 1 px en todos los contenedores, inputs y botones.
- **Radios observados:**

| Radio | Uso |
|---:|---|
| 1.5 px | Indicador activo de sidebar (3 × 48) |
| 4 px | Punto de indicador de stat (8 × 8) |
| 8 px | Botones, inputs, navegación, avatares de iniciales, menús de ítems |
| 10 px | Tarjetas, tabla, modales de confirmación, toasts |
| 12 px | Tarjeta de login, modal de nuevo comercio |
| 14 px | Badges (28 px de alto) |
| 20 px | Avatares circulares (40 × 40) |
| 24 px | Contenedor del icono de advertencia (48 × 48) |

> Hay inconsistencia entre 10 y 12 px para modales, y entre 8 y 10 px para toasts.

### 4.4 Espaciado

- Base de **4 px**; pasos usados: 4, 8, 12, 16, 20, 24, 32.
- **Padding de contenido:** 32 px (área de trabajo desde x=256, y=128).
- **Padding de tarjetas:** 20 px (stats) y 24 px (detalle y modales).
- **Celdas de tabla:** 20 px horizontal.
- **Separación entre tarjetas:** 24 px.
- **Separación entre secciones:** 24–32 px.
- **Barra lateral:** ítems de 48 px de alto, 12 px de separación, 16 px de margen lateral.
- **Cabecera:** 96 px; borde inferior de 1 px.

### 4.5 Dimensiones generales

| Elemento | Medida |
|---|---|
| Lienzo | 1440 × 1024 px |
| Barra lateral | 224 × 1024 px |
| Cabecera | 1216 × 96 px (desde x=224) |
| Área de trabajo | 1152 px de ancho; inicia en x=256, y=128 |
| Logo de sidebar | 136 × 122.4 px |
| Avatar de cabecera | 40 × 40 px |
| Stat card técnico | 270 × 140 px (4 columnas) |
| Stat card comercios/saldo | 368 × 140 px (3 columnas) |
| Stat card resumen de pagos | 368 × 104 px |
| Tarjeta de tabla | 1152 px de ancho |
| Cabecera de tabla | 44 px |
| Fila de tabla | 62 px |
| Input / selector | 44 px (formularios principales 48 px) |
| Botón pequeño | 40 px |
| Botón estándar | 44 px |
| CTA de login | 48 px |
| Modal confirmación ticket | 480 × 316 px |
| Modal nuevo comercio | 528 × 352 px |
| Modal confirmar retirada | 560 × 392 px |
| Toast | 56 px de alto; 510/584 px de ancho |
| Banner de error | 64/70 px de alto; 584 px de ancho |
| Paginación | 40 px de alto |

### 4.6 Tokens CSS propuestos

Nombres de referencia para implementar en Tailwind/CSS. **No se ha creado ningún archivo de estilos.**

```
--plp-color-brand-900: #1E0F52
--plp-color-brand-800: #2D205C
--plp-color-brand-700: #321A83
--plp-color-brand-600: #4D3D7E
--plp-color-brand-400: #7767A4
--plp-color-brand-300: #C9BFEF
--plp-color-brand-200: #D6CCF3
--plp-color-brand-100: #EDE9FA
--plp-color-accent-500: #14B8A6

--plp-color-bg: #F8FAFC
--plp-color-surface: #FFFFFF
--plp-color-border: #E2E8F0
--plp-color-border-soft: #F1F5F9
--plp-color-text: #0F172A
--plp-color-text-secondary: #475569
--plp-color-text-muted: #64748B

--plp-color-success-bg: #D1FAE5
--plp-color-success-border: #A7F3D0
--plp-color-success-text: #047857
--plp-color-warning-bg: #FEF3C7
--plp-color-warning-text: #B45309
--plp-color-info-bg: #E0F2FE
--plp-color-info-text: #0369A1
--plp-color-danger-bg: #FEE2E2
--plp-color-danger-soft: #FEF2F2
--plp-color-danger-border: #FECACA
--plp-color-danger: #B91C1C
--plp-color-danger-strong: #EF4444
--plp-color-neutral-bg: #F1F5F9
--plp-color-neutral-text: #475569
--plp-color-overlay: rgba(15, 23, 42, 0.45)

--plp-radius-sm: 4px
--plp-radius-md: 8px
--plp-radius-lg: 10px
--plp-radius-xl: 12px
--plp-radius-pill: 14px
--plp-radius-full: 9999px

--plp-font-sans: Inter, system-ui, sans-serif
--plp-leading: 1.5
```

> Los tokens de hover, focus, pressed, disabled y las sombras **no están definidos en Figma**; habría que acordarlos.

---

## 5. Navegación y funcionalidad

### 5.1 Navegación principal

**Backoffice (técnico y administración)**

```
Acceso técnico (/acceso-tecnico)
        │  login correcto
        ▼
Bandeja de tickets (/tecnico/tickets)
        │  "Ver"
        ▼
Detalle del ticket (/tecnico/tickets/:id)

Barra lateral: Tickets ⇄ Comercios (/tecnico/comercios)
Cabecera: usuario técnico · Cerrar sesión → Sesión cerrada → Acceso técnico
```

- “Comercios” comparte shell y cabecera con “Tickets”.
- El frame 33 “Acceso restringido” sugiere que la sección de comercios puede estar limitada por rol.
- El menú de la fila (18) ofrece “Cambiar estado” y “Eliminar”.

**Portal del comercio**

```
Acceso comercio (/acceso-comercio)
        │  login correcto
        ▼
Inicio (/comercio/inicio)
        ├─ Pagos (/comercio/pagos) → Detalle de pago (/comercio/pagos/:id)
        ├─ Saldo (/comercio/saldo) → Confirmar retirada (modal)
        ├─ Devoluciones  ← sin pantalla
        └─ Tickets       ← sin pantalla
Cabecera: Librería Horizonte · Cerrar sesión → Sesión cerrada → Acceso comercio
```

### 5.2 Flujos de acceso y cierre

| Paso | Técnico | Comercio |
|---|---|---|
| Formulario base | 01 | 52 |
| Formulario relleno | 10 | 57 |
| Falta usuario | 11 — “Introduce tu usuario” | 58 — mismo patrón |
| Credenciales incorrectas | 12 — alerta en el formulario | 59 — mismo patrón |
| Contraseña visible | 16 | 60 |
| Acceso correcto | No representado (no hay pantalla de éxito ni transición) | No representado |
| Cierre de sesión | 14 — “Sesión cerrada” + “Volver a iniciar sesión” | 74 — mismo patrón |

**Representado visualmente:** campos, mostrar/ocultar contraseña, errores de validación y credenciales, pantalla de sesión cerrada.
**Por implementar:** llamada real de login, persistencia del token, redirección por rol, guardas de ruta, tiempo de expiración, estado de carga del botón.

### 5.3 Flujo de tickets

```
Bandeja 02
 ├─ Buscar / filtrar por estado, comercio y fecha
 ├─ Ordenar ("Abiertos más antiguos primero")
 ├─ Limpiar filtros → 08 (sin resultados)
 ├─ Paginación
 ├─ Ver → Detalle 03
 └─ "···" → Menú 18 → Cambiar estado (19) / Eliminar (17)

Detalle 03
 ├─ Cambiar estado → 04 (En proceso, sin guardar)
 ├─ Escribir respuesta → 05 ("Respuesta lista para enviar")
 ├─ Guardar cambios → 06 (toast + historial) o 09 (error)
 ├─ Preparar cierre → 21 (Cerrado, sin guardar) → Guardar → 22 (cerrado)
 ├─ Eliminar → 17 → confirmar → 15 (bandeja sin el ticket)
 ├─ Volver a la bandeja → 07 / 23
 └─ Ticket inexistente → 13 (404)
```

**Datos visibles que cambian entre estados:**
- 02: 128 tickets, 24 abiertos, 16 en proceso, 88 cerrados; #1042 aparece “Abierto”.
- 07: 128 tickets, 23 abiertos, 17 en proceso, 88 cerrados; #1042 pasa a “En proceso”.
- 15: 127 tickets; desaparece #1042.
- 23: 127 tickets tras cierre (bandeja recalculada).
- 21/22: el estado de “Gestión” cambia a “Cerrado”; el historial añade “Abierto → Cerrado” con la respuesta y la autora.

**Validaciones y reglas observadas:**
- No se puede guardar sin cambios: aparece “Cambios sin guardar”.
- La respuesta al comercio se conserva si falla el guardado (09).
- El estado del badge de la incidencia y el selector pueden diferir mientras hay cambios sin guardar.
- “Eliminar ticket” exige confirmación y advierte que es permanente.

### 5.4 Flujo de comercios

```
Comercios 24
 ├─ Buscar por nombre
 ├─ Filtrar por estado (45) → 34 activos / 35 dados de baja
 ├─ Ordenar (46) → 36 más recientes
 ├─ Paginar → 37 segunda página
 ├─ Limpiar filtros → 32 sin coincidencias
 ├─ "+ Nuevo comercio" → Modal 38
 │    ├─ 39 con datos
 │    ├─ 40 nombre obligatorio
 │    ├─ 41 nombre > 100 caracteres
 │    ├─ 42 error de acción (conserva el nombre)
 │    └─ éxito → 25 (toast) → 26 (alta aplicada)
 └─ Fila "···" (44) → Dar de baja → 43 confirmar
      └─ éxito → 27 (toast) → 28 (baja aplicada)
```

**Estados especiales:**
- 31: sin comercios (panel vacío grande + CTA).
- 32: filtros sin coincidencias (conserva barra de filtros + “Limpiar filtros”).
- 33: acceso restringido.
- 47–51: altas/bajas sucesivas y caso del primer comercio.
- Los comercios dados de baja muestran “—” en Acciones (“Sin acciones”).

**Validaciones del alta:**
- Campo obligatorio: “El nombre es obligatorio”.
- Longitud: “El nombre no puede superar los 100 caracteres”; contador “108 / 100”.
- Ayuda permanente: “Máx. 100 caracteres”.
- Error de acción: banner “No se ha podido completar la acción. Inténtalo de nuevo” + “El nombre se ha conservado para que puedas reintentarlo.”

### 5.5 Flujo del portal del comercio

**Inicio (53)**
- Saludo “Hola, Librería Horizonte”.
- 3 tarjetas de saldo por moneda (EUR destacada).
- 3 resúmenes de pagos: aceptados 128, rechazados 8, en proceso 3.
- “Retirar fondos” → Saldo.
- Tabla “Últimos pagos” + “Ver todos los pagos” → Pagos.
- 61: variante sin pagos (“Aún sin pagos”).

**Pagos (55)**
- Chips de saldo EUR/USD/GBP + “Ver saldo”.
- Buscador “Cliente, concepto o nº de factura”.
- Filtros: estado, moneda, fecha; “Limpiar”; orden “Más recientes primero”.
- Tabla: Fecha, Cliente, Concepto, Importe, Estado, Motivo, Acciones (“Ver”).
- 143 pagos, 5 por página.
- 67: sin coincidencias + “Limpiar filtros”.

**Detalle de pago (56, 68–72)**
- Cabecera + “Volver al listado”.
- Estado + título del pago.
- Datos: cliente, tarjeta, concepto, fecha/hora, nº factura.
- Resumen económico: importe total, comisión PLP, neto abonado (o “Neto original (revertido)”).
- Acciones: “Solicitar devolución” (activo solo en Aceptado).
- Historial del pago.
- Variantes:
  - 68 Rechazado: “Tarjeta no aceptada”; sin botón; aviso “Solo se pueden devolver pagos aceptados”.
  - 69 Reembolsado: “Devolución completada”; botón deshabilitado.
  - 70 En proceso: “Pendiente de confirmación”; botón deshabilitado.
  - 71 Aceptado en GBP: mismos componentes, importes en GBP.
  - 72 Pago no encontrado: estado de error.

**Saldo (54, 62–66, 73)**
- 3 tarjetas de saldo por moneda.
- Formulario “Retirar fondos”: moneda (76), importe, “Retirar todo”, “Retirar”.
- Validaciones:
  - 63: “El importe no es válido”.
  - 64: “El importe supera tu saldo disponible”.
- 62: importe 300,00 EUR preparado.
- 75: confirmación con resumen (disponible, importe, saldo resultante) y “Confirmar retirada”.
- 65: toast “Retirada realizada. Tu nuevo saldo es 950,00 EUR”; saldo actualizado; formulario vacío.
- 66: saldo actualizado sin toast.
- 73: banner “No se ha podido completar la acción. Inténtalo de nuevo”.

**Representado visualmente:** formularios, validaciones, confirmación, estados de éxito/error, estados de pago.
**Por implementar:** envío real, cálculo de comisiones, flujo de devolución, navegación de “Devoluciones” y “Tickets”, persistencia del saldo, bloqueo de doble envío, cierre de modales con teclado.

### 5.6 Representado vs. pendiente de implementar

| Capacidad | Representado en Figma | A implementar |
|---|:--:|---|
| Login y errores | Sí | Llamada API, token, redirección por rol |
| Guardas de ruta | Solo estado “Acceso restringido” | Guards reales |
| Listado y filtros de tickets | Sí | Estado, debounce, paginación server-side |
| Detalle y cambio de estado | Sí | Persistencia y recálculo |
| Alta/baja de comercios | Sí | API y refresco de listados |
| Retirada de fondos | Sí | Cálculo, confirmación y actualización |
| Pagos y detalle | Sí | Datos reales, paginación |
| Reembolsos | Solo botón | Confirmación, API, estados |
| “Devoluciones” del comercio | No | Diseño y pantalla |
| “Tickets” del comercio | No | Diseño y pantalla |
| Reactivación de comercio | No | Decisión funcional |
| Responsive | No | Diseño adaptable |
| Hover/focus/pressed | No | Definir estados |
| Notificaciones auto-dismiss | Solo visual | Temporización |
| Cierre de modal con Esc/overlay | No definido | Implementar |

---

## 6. Arquitectura recomendada (Vue 3 + TS + Vite + Tailwind)

### 6.1 Principios

1. **Un solo componente por patrón**: sidebar, header, botón, tabla, badge, modal, toast, input, select, paginación.
2. **Dos layouts de producto** (`BackofficeLayout`, `MerchantLayout`) y uno de autenticación (`AuthLayout`).
3. **Tres módulos de dominio** con vistas, componentes y stores propias; lo común vive en `shared`.
4. **Rutas separadas por módulo** y guardas por rol.
5. **Estado de UI (modales, toasts) separado del estado de dominio** (tickets, comercios, pagos).
6. **Tokens de diseño** en CSS variables + extensión de Tailwind; nada de hex sueltos en componentes.

### 6.2 Estructura de carpetas propuesta

```
frontend/
├── public/
│   └── assets/
│       ├── icons/                 # iconos SVG (ticket, shop, logout, search, chevron…)
│       └── images/                # avatar de Laura, logo definitivo
├── src/
│   ├── main.ts
│   ├── App.vue
│   ├── assets/
│   │   └── styles/
│   │       ├── tokens.css         # variables del sistema visual
│   │       └── main.css           # Tailwind + base
│   ├── router/
│   │   ├── index.ts
│   │   ├── guards.ts
│   │   ├── routes.auth.ts
│   │   ├── routes.tech.ts
│   │   └── routes.merchant.ts
│   ├── layouts/
│   │   ├── AuthLayout.vue
│   │   ├── BackofficeLayout.vue
│   │   └── MerchantLayout.vue
│   ├── modules/
│   │   ├── auth/
│   │   │   ├── views/
│   │   │   │   ├── TechLoginView.vue
│   │   │   │   └── MerchantLoginView.vue
│   │   │   ├── components/
│   │   │   │   ├── LoginForm.vue
│   │   │   │   ├── PasswordField.vue
│   │   │   │   └── LoginFooter.vue
│   │   │   └── stores/auth.store.ts
│   │   ├── tech/
│   │   │   ├── tickets/
│   │   │   │   ├── views/
│   │   │   │   │   ├── TicketsListView.vue
│   │   │   │   │   └── TicketDetailView.vue
│   │   │   │   ├── components/
│   │   │   │   │   ├── TicketFilters.vue
│   │   │   │   │   ├── TicketTable.vue
│   │   │   │   │   ├── TicketRowActions.vue
│   │   │   │   │   ├── TicketStatusBadge.vue
│   │   │   │   │   ├── TicketStatusSelect.vue
│   │   │   │   │   ├── TicketReplyForm.vue
│   │   │   │   │   ├── TicketHistory.vue
│   │   │   │   │   ├── TicketSummaryCard.vue
│   │   │   │   │   ├── SaveFeedback.vue        # toast + banner de error
│   │   │   │   │   └── DeleteTicketDialog.vue
│   │   │   │   ├── stores/tickets.store.ts
│   │   │   │   └── types/ticket.ts
│   │   │   └── merchants/
│   │   │       ├── views/MerchantsListView.vue
│   │   │       ├── components/
│   │   │       │   ├── MerchantFilters.vue
│   │   │       │   ├── MerchantTable.vue
│   │   │       │   ├── MerchantRowMenu.vue
│   │   │       │   ├── MerchantFormModal.vue
│   │   │       │   ├── DeleteMerchantDialog.vue
│   │   │       │   └── MerchantStatusBadge.vue
│   │   │       ├── stores/merchants.store.ts
│   │   │       └── types/merchant.ts
│   │   └── merchant/
│   │       ├── home/
│   │       │   ├── views/MerchantHomeView.vue
│   │       │   └── components/PaymentSummary.vue
│   │       ├── payments/
│   │       │   ├── views/
│   │       │   │   ├── PaymentsListView.vue
│   │       │   │   └── PaymentDetailView.vue
│   │       │   ├── components/
│   │       │   │   ├── PaymentFilters.vue
│   │       │   │   ├── PaymentTable.vue
│   │       │   │   ├── PaymentStatusBadge.vue
│   │       │   │   ├── PaymentSummaryCard.vue
│   │       │   │   ├── PaymentHistory.vue
│   │       │   │   └── RefundAction.vue
│   │       │   ├── stores/payments.store.ts
│   │       │   └── types/payment.ts
│   │       └── balance/
│   │           ├── views/BalanceView.vue
│   │           ├── components/
│   │           │   ├── BalanceCards.vue
│   │           │   ├── BalanceChips.vue
│   │           │   ├── WithdrawForm.vue
│   │           │   ├── CurrencySelect.vue
│   │           │   └── WithdrawConfirmDialog.vue
│   │           ├── stores/balance.store.ts
│   │           └── types/balance.ts
│   ├── shared/
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── AppSidebar.vue
│   │   │   │   ├── AppHeader.vue
│   │   │   │   ├── PageHeader.vue
│   │   │   │   ├── AuthCard.vue
│   │   │   │   ├── BrandLogo.vue
│   │   │   │   └── Breadcrumbs.vue
│   │   │   ├── ui/
│   │   │   │   ├── AppButton.vue
│   │   │   │   ├── IconButton.vue
│   │   │   │   ├── AppInput.vue
│   │   │   │   ├── AppTextarea.vue
│   │   │   │   ├── AppSelect.vue
│   │   │   │   ├── AppBadge.vue
│   │   │   │   ├── AppModal.vue
│   │   │   │   ├── ConfirmDialog.vue
│   │   │   │   ├── AppToast.vue
│   │   │   │   ├── InlineAlert.vue
│   │   │   │   ├── EmptyState.vue
│   │   │   │   ├── Pagination.vue
│   │   │   │   └── StatusDot.vue
│   │   │   └── data/
│   │   │       ├── AppTable.vue
│   │   │       ├── StatCard.vue
│   │   │       ├── BalanceCard.vue
│   │   │       ├── Avatar.vue
│   │   │       └── Timeline.vue
│   │   ├── composables/
│   │   │   ├── useToast.ts
│   │   │   ├── useModal.ts
│   │   │   ├── usePagination.ts
│   │   │   ├── useFilters.ts
│   │   │   └── useFormat.ts
│   │   ├── services/
│   │   │   ├── http.ts
│   │   │   ├── auth.service.ts
│   │   │   ├── tickets.service.ts
│   │   │   ├── merchants.service.ts
│   │   │   ├── payments.service.ts
│   │   │   └── balance.service.ts
│   │   ├── stores/ui.store.ts
│   │   ├── types/
│   │   │   ├── common.ts
│   │   │   ├── status.ts
│   │   │   └── currency.ts
│   │   └── utils/
│   │       ├── format-currency.ts
│   │       ├── format-date.ts
│   │       └── initials.ts
│   └── mocks/                     # datos de los frames mientras el backend no está listo
├── tailwind.config.ts
├── vite.config.ts
├── tsconfig.json
└── package.json
```

### 6.3 Rutas

| Ruta | Layout | Vista | Guarda |
|---|---|---|---|
| `/acceso-tecnico` | `AuthLayout` | `TechLoginView` | Solo invitados |
| `/acceso-comercio` | `AuthLayout` | `MerchantLoginView` | Solo invitados |
| `/tecnico/tickets` | `BackofficeLayout` | `TicketsListView` | Rol técnico |
| `/tecnico/tickets/:id` | `BackofficeLayout` | `TicketDetailView` | Rol técnico |
| `/tecnico/comercios` | `BackofficeLayout` | `MerchantsListView` | Rol técnico/admin (ver frame 33) |
| `/comercio/inicio` | `MerchantLayout` | `MerchantHomeView` | Rol comercio |
| `/comercio/pagos` | `MerchantLayout` | `PaymentsListView` | Rol comercio |
| `/comercio/pagos/:id` | `MerchantLayout` | `PaymentDetailView` | Rol comercio |
| `/comercio/saldo` | `MerchantLayout` | `BalanceView` | Rol comercio |
| `/` y `/:pathMatch(.*)*` | — | Redirección / 404 | — |

Los **modales y menús no deberían ser rutas** en la primera versión: son estado de UI sobre la página. Solo “Nuevo comercio” podría tener ruta hija si se quiere enlace directo.

### 6.4 Estado (Pinia)

| Store | Responsabilidad |
|---|---|
| `auth.store` | Rol, token, usuario/comercio, login/logout, persistencia |
| `ui.store` | Toasts, modal de confirmación, estado de carga global |
| `tickets.store` | Listado, filtros, paginación, ticket activo, guardado, borrado |
| `merchants.store` | Listado, filtros, orden, paginación, alta, baja, acceso restringido |
| `payments.store` | Listado, filtros, pago activo, estados, devolución |
| `balance.store` | Saldos por moneda, formulario de retirada, confirmación, resultado |

### 6.5 Tipos y estados

```ts
type TicketStatus = 'abierto' | 'en-proceso' | 'cerrado'
type MerchantStatus = 'activo' | 'dado-de-baja'
type PaymentStatus = 'aceptado' | 'rechazado' | 'en-proceso' | 'reembolsado'
type Currency = 'EUR' | 'USD' | 'GBP'
type UserRole = 'tecnico' | 'comercio'
```

- Importes: `number` con dos decimales, formateo español (coma decimal, punto de miles) y sufijo de moneda.
- Fechas: formato “17 nov 2026 · 09:42” y “12 nov 2026”.

### 6.6 Integración con la API existente

La especificación `api/api.yaml` ya define endpoints que encajan con las pantallas:

| Pantalla | Endpoints previstos |
|---|---|
| Acceso técnico / comercio | `POST /login`, `POST /logout` |
| Bandeja y detalle de ticket | `GET /tickets`, `POST /ticket/add`, `PUT /ticket/update`, `DELETE /ticket/delete` |
| Comercios | `GET /companies`, `PUT /companies/add`, `DELETE /companies/delete` |
| Inicio y saldo | `GET /balance`, `POST /withdraw` |
| Pagos | `GET /payments` |
| Detalle de pago / devolución | `GET /refunds`, `POST /refunds/request`, `POST /refunds/accept`, `POST /refunds/reject` |

> La API contempla reembolsos, pero el diseño solo muestra el botón “Solicitar devolución”. Falta la pantalla de confirmación y resultado.

### 6.7 Convenciones recomendadas

- Componentes en PascalCase, stores `*.store.ts`, servicios `*.service.ts`.
- Tailwind con tokens semánticos (`bg-surface`, `text-muted`, `border-default`).
- Sin hex sueltos en las vistas.
- Iconos como SVG locales (los assets de Figma son temporales).
- Utilidades de formato centralizadas (`format-currency`, `format-date`, `initials`).
- Mocks basados en los datos exactos de los frames hasta conectar el backend.

---

## 7. Inconsistencias detectadas

1. **No hay componentes ni variables en Figma.** La barra lateral se repite unas 50 veces; cualquier ajuste global exige tocar decenas de frames. La implementación debe corregirlo con componentes.
2. **Radios distintos para el mismo tipo de elemento.** Modales: 10 px en “Confirmar eliminación” y 12 px en “Nuevo comercio”. Toasts: 10 px en el detalle de ticket y 8 px en el portal del comercio.
3. **Anchos y alturas de feedback distintos.** Toast de 510 px frente a 584 px; banner de error de 70 px frente a 64 px.
4. **Nombre de capa incorrecto.** En el frame 06, la capa `Estado · En proceso` (`2:465`) contiene el texto “Abierto” (`2:466`).
5. **Badge y selector desincronizados a propósito.** En 04, 05, 09 y 21 el selector muestra el estado nuevo pero el badge de la incidencia mantiene el estado guardado. No hay una regla visual explícita para “cambio sin guardar” más allá del texto de ayuda.
6. **“Acceso completado” no es un estado de éxito.** Los frames 10 y 57 solo muestran el formulario relleno; no hay confirmación ni transición. El nombre induce a error.
7. **Estados duplicados.** 06 y 20 representan “ticket actualizado” (con y sin toast); 65 y 66 representan la retirada realizada (con y sin toast). Conviene unificar.
8. **Acción de devolución inconsistente.** En 69 y 70 el botón “Solicitar devolución” aparece deshabilitado; en 68 (Rechazado) desaparece. Debería seguir una única regla.
9. **Flujo de devolución incompleto.** No hay confirmación, ni estado de carga, ni éxito/error tras “Solicitar devolución”, aunque la API define `/refunds/*`.
10. **Navegación del comercio incompleta.** “Devoluciones” y “Tickets” existen en la barra lateral, pero no hay ninguna pantalla asociada.
11. **Comercios dados de baja sin acciones.** Las filas inactivas muestran “—” en Acciones; no hay forma de reactivar un comercio.
12. **Título duplicado en Pagos.** La cabecera superior y el título de página dicen ambos “Pagos recibidos”.
13. **“Comercios · Acceso restringido” (33) no está integrado en la navegación.** No se sabe si se oculta el ítem o se muestra el estado al entrar; hay que decidirlo.
14. **Colores con doble semántica.** El ámbar (`#FEF3C7` / `#B45309`) representa “Abierto” en tickets y “En proceso” en pagos; el azul representa “En proceso” en tickets. Es coherente internamente, pero conviene documentarlo como estados distintos por dominio.
15. **Logo provisional.** Todos los logos son marcadores con borde discontinuo (“Marcador de logo”); no existe el activo definitivo.
16. **Avatar distinto por rol.** Técnico usa fotografía; comercio usa iniciales. Puede ser intencional, pero no está documentado.
17. **Sin estados de hover, focus, pressed ni disabled completos.** Solo se ve el foco morado en el importe y un fondo gris de botón deshabilitado.
18. **Sin diseño responsive.** Todo está fijado a 1440 px; no hay pistas de comportamiento en anchos menores.
19. **Sin sombras.** Los modales se separan solo por el overlay y el borde; conviene mantenerlo o acordar una elevación.
20. **Datos y fechas fijos.** Los frames usan fechas y cantidades concretas; no hay indicación de estados de carga ni de datos vacíos parciales.

---

## 8. Aspectos pendientes de verificar

| Tema | Qué falta | Prioridad |
|---|---|---|
| **Logo y avatar reales** | Sustituir marcadores de logo y foto por activos definitivos | Alta |
| **Rol y permisos** | Confirmar si “Comercios” es solo para administradores (frame 33) | Alta |
| **Devoluciones del comercio** | Diseñar listado y flujo de solicitud/confirmación | Alta |
| **Tickets del comercio** | Diseñar la sección “Tickets” de la barra lateral | Alta |
| **Reactivación de comercios** | Decidir si un comercio dado de baja puede reactivarse | Media |
| **“Cambiar estado” desde el menú (18)** | Confirmar si navega al detalle o abre el selector en la fila | Media |
| **Comportamiento de 22 “Ticket cerrado”** | Verificar si el ticket cerrado sigue siendo editable | Media |
| **Layout de 72 “Pago no encontrado”** | Confirmar si mantiene el shell y qué acciones ofrece | Media |
| **Frames 34–37 y 47–51** | Verificar copy y totales exactos de cada variante | Media |
| **Frame 33** | Confirmar layout y acciones del estado restringido | Media |
| **Estados interactivos** | Definir hover, focus, pressed, disabled y foco visible | Alta |
| **Responsive** | Definir breakpoints y comportamiento de sidebar/tablas | Alta |
| **Cierre de modales** | Definir Esc, clic en overlay y foco atrapado | Media |
| **Duración de toasts** | Definir auto-cierre y posibilidad de descartar | Baja |
| **Paginación** | Confirmar tamaños: 5 tickets/pagos, 7 comercios | Media |
| **Formato de importes** | Confirmar símbolo/sufijo y separadores en EUR/USD/GBP | Media |
| **Internacionalización** | Confirmar si habrá más idiomas o solo español | Baja |
| **Accesibilidad** | Contraste, navegación por teclado y etiquetas ARIA | Alta |

---

## 9. Método y cobertura de Figma MCP

Para minimizar consultas se usó `get_metadata` sobre la página completa (`0:1`) y se reservó `get_design_context` para pantallas representativas:

| Consulta | Motivo |
|---|---|
| `get_metadata` página `0:1` | Inventario y jerarquía de los 76 frames |
| `get_design_context` `2:2` | Login técnico (tipografía, tarjeta, inputs, CTA) |
| `get_design_context` `12:5086` | Login comercio (variantes de copy) |
| `get_design_context` `2:4` | Bandeja: sidebar, header, stats, filtros, tabla, badges, paginación |
| `get_design_context` `2:8` | Detalle de ticket: tarjetas, formulario, historial, botones |
| `get_design_context` `12:56` | Comercios: stats, tabla, avatares, badges, CTA |
| `get_design_context` `12:5237` + `12:6539` + `12:6643` + `12:6758` + `12:6862` | Variantes del detalle de pago |
| `get_design_context` `12:5138` + `12:5958` + `12:6056` + `12:7073` | Saldo y validaciones de retirada |
| `get_design_context` `12:2679` + `12:2722` + `12:2738` | Modal de alta y errores |
| `get_design_context` `2:1508` + `2:1518` + `2:1525` + `12:7201` + `12:7232` | Modales, menús y selects |
| `get_design_context` `12:375` + `12:5188` + `2:517` | Toasts y estados de listado |
| Capturas puntuales | 02, 03, 07, 10, 13, 17, 24, 31, 38, 40–42, 44, 52, 54–56, 61, 63–71, 73 |
| `get_variable_defs` / `get_libraries` | Confirmar ausencia de tokens y librerías |

No se descargaron capturas de los 76 frames ni se repitieron consultas sobre componentes ya analizados.

---

## 10. Siguiente paso

Análisis aprobado. La implementación se ha realizado siguiendo las fases acordadas y se documenta en [`implementacion-frontend.md`](./implementacion-frontend.md).

Decisiones aprobadas antes de implementar:

1. Gestión de comercios exclusiva del administrador.
2. Devoluciones en el portal del comercio con los endpoints de `/refunds`; Tickets queda como “próximamente”.
3. Reactivación de comercios con confirmación, reutilizando el alta si no existe endpoint específico.
4. Responsive para tablet y móvil manteniendo 1440 × 1024 como referencia.
