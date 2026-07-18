# Sistema de Diseño — blog2025

## Colores

### Primarios

| Variable | Hex | Tailwind | Uso |
|----------|:---:|----------|-----|
| `--primary-300` | `#93c5fd` | `bg-primary-300 text-primary-300` | Acentos suaves, badges, gradient-text |
| `--primary-500` | `#0d6efd` | `bg-primary-500 text-primary-500` | Botón primary, links, acento principal |
| `--primary-600` | `#0b5ed7` | `bg-primary-600 text-primary-600` | Hover de botones, interactive, footer gradient |
| `--primary-700` | `#1e40af` | `bg-primary-700 text-primary-700` | Fondos oscuros, hero, títulos |
| `--primary-900` | `#084298` | `bg-primary-900` | Final del gradient del footer |

### Secundarios

| Color | Hex | Tailwind | Uso |
|-------|:---:|----------|-----|
| Green | `#22c55e` | `bg-green-500 text-green-500` | WhatsApp, éxito, disponible |
| Gray | `#64748b` | `text-gray-500 bg-gray-100` | Texto secundario, bordes, placeholders |
| Red | `#ef4444` | `bg-red-500 text-red-500` | Errores, peligro |

## Botones

| Variante | Estilo | Hover |
|----------|--------|-------|
| Primary | `bg-primary-500 text-white` | `hover:bg-primary-600` |
| Secondary | `border-2 border-gray-300 text-gray-600` | `hover:border-gray-400 hover:text-gray-800` |
| Secondary (fondo oscuro) | `border-2 border-white/30 text-white/70` | `hover:border-white/60 hover:text-white` |
| Success | `bg-green-500 text-white` | `hover:bg-green-600` |
| Ghost | `text-gray-500` | `hover:bg-gray-100` |

## Fondos de sección

| Sección | Clase |
|---------|-------|
| Hero | `bg-primary-700` |
| Secciones claras | `bg-slate-50` |
| Secciones blancas | `bg-white` |
| Secciones oscuras | `bg-primary-700` |
| Footer | `bg-gradient-to-br from-primary-600 via-primary-500 to-primary-900` |

## Tipografía

| Propiedad | Valor |
|-----------|-------|
| Fuente | Inter (system-ui, sans-serif) |
| Tamaño base | 15px |
| Títulos sección | `text-3xl lg:text-4xl font-bold text-primary-700` (claro) / `text-white` (oscuro) |

## Componentes reutilizables

| Componente | Clases base |
|------------|-------------|
| Badge de sección (claro) | `text-xs font-bold uppercase tracking-widest text-primary-500 bg-primary-500/10 border border-primary-500/20 rounded-full px-4 py-1.5` |
| Badge de sección (oscuro) | `text-xs font-bold uppercase tracking-widest text-white bg-white/10 border border-white/20 rounded-full px-4 py-1.5` |
| Glass card | `glass-card` (fondo blanco, borde `#e2e8f0`, sombra suave) |
| Glass card (oscuro) | `glass` (fondo rgba(255,255,255,0.03), blur, borde rgba(255,255,255,0.06)) |
| Divisor entre secciones | `<hr class="border-0 h-px bg-gradient-to-r from-transparent via-gray-200 to-transparent max-w-5xl mx-auto">` |
