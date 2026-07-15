# Tecport Lead Intelligence — Frontend

Interfaz de chat para el sistema de inteligencia comercial. React + TypeScript + Vite + Tailwind + TanStack Query.

## Requisitos

- Node.js 20+
- El backend corriendo en `http://localhost:8000` (ver `backend/README` / instrucciones del backend) con al menos un usuario creado.

## Configuración

```bash
cd frontend
npm install
```

Variables de entorno (`.env`, ya incluido para desarrollo local):

```env
VITE_BACKEND_URL=http://localhost:8000
```

## Ejecutar en desarrollo

```bash
npm run dev
```

Abre `http://localhost:5173`. Inicia sesión con un usuario creado en el backend (`python create_user.py "Nombre" correo@empresa.com`).

## Estructura

- `src/features/auth` — login, sesión, rutas protegidas.
- `src/features/chat` — sidebar, composer, mensajes, línea de tiempo de la conversación.
- `src/features/searches` — tarjeta de criterios (editable) y progreso de búsqueda.
- `src/features/results` — tabla de resultados, panel de detalle, exportación.
- `src/features/lists` — listas guardadas.
- `src/components/ui` — primitivos de interfaz (botón, input, card, badge, sheet, etc).

## Notas de diseño

- Todo el flujo (interpretación, progreso, resultados, exportación) vive dentro de la conversación — no hay páginas separadas para cada paso.
- La sesión se maneja con una cookie httpOnly que pone el backend; el frontend nunca toca el token directamente (`credentials: 'include'` en todas las llamadas).
- El panel derecho (`ResultDetailDrawer`) solo se abre al seleccionar un resultado, sin cambiar de página.
