# PLP: Pasa La Pasta

PLP es un Terminal de Punto de Venta con alcance académico (no opera con dinero real).

## Estructura del proyecto

- [`/api`](/api/): Incluye la especificación e implementación de la API del proyecto
- [`/frontend`](/frontend/): Frontend en Vue 3 + TypeScript + Vite + Tailwind CSS
- [`/backend`](/backend/): Implementación del backend en Python con Django
- [`/docs`](/docs/): Análisis de Figma e implementación del frontend

## Frontend

El frontend consume la API real; no incluye mocks. Arranca primero el backend (`http://localhost:8000`) o el stack completo con Docker.

```bash
cd frontend
npm install
npm run dev
```

Credenciales del backend:

| Portal | Usuario | Contraseña | Rol |
| --- | --- | --- | --- |
| Técnico (administrador) | `admin` | `admin` | `admin` |
| Técnico | `tpv01` | `secret` | `tecnico` |
| Comercio | `comercio` | `comercio` | `comercio` |

Consulta [`frontend/README.md`](/frontend/README.md) y [`docs/implementacion-frontend.md`](/docs/implementacion-frontend.md).
