# Atomic Design - Frontend INAOE RAG

## Estructura de Componentes

El proyecto sigue los principios de **Atomic Design** de Brad Frost:

```
src/components/
├── ui/           # ÁTOMOS - Componentes base primitivos
├── ui-custom/    # MOLÉCULAS - Componentes personalizados compuestos
└── chat/         # ORGANISMOS - Componentes de dominio específico
```

---

## 🔵 ÁTOMOS (`ui/`)

Componentes primitivos e indivisibles. No contienen lógica de negocio.

| Componente | Descripción |
|------------|-------------|
| `button.tsx` | Botón base con variantes |
| `input.tsx` | Campo de entrada de texto |
| `label.tsx` | Etiqueta para formularios |
| `badge.tsx` | Etiqueta visual pequeña |
| `avatar.tsx` | Imagen de perfil circular |
| `skeleton.tsx` | Placeholder de carga |
| `spinner.tsx` | Indicador de carga animado |
| `separator.tsx` | Línea divisoria |
| `checkbox.tsx` | Casilla de verificación |
| `switch.tsx` | Toggle on/off |
| `slider.tsx` | Control deslizante |
| `progress.tsx` | Barra de progreso |
| `tooltip.tsx` | Información emergente |
| `select.tsx` | Selector desplegable |
| `textarea.tsx` | Área de texto multilínea |
| `scroll-area.tsx` | Contenedor con scroll |

**Total: 53 átomos** (Radix UI primitives + custom)

---

## 🟢 MOLÉCULAS (`ui-custom/`)

Combinaciones de átomos con funcionalidad específica.

| Componente | Composición |
|------------|-------------|
| `AnimatedBackground.tsx` | Canvas + Motion |
| `TypingIndicator.tsx` | Dots + Animation |
| (otros componentes custom) | |

---

## 🟠 ORGANISMOS (`chat/`)

Componentes complejos con lógica de dominio para el chat RAG.

| Componente | Responsabilidad |
|------------|-----------------|
| `ChatHeader.tsx` | Barra superior con navegación y acciones |
| `Sidebar.tsx` | Panel lateral con historial y selector de modelos |
| `WelcomeScreen.tsx` | Pantalla inicial con sugerencias |
| `ChatInput.tsx` | Entrada de mensajes con botón enviar |
| `MessageBubble.tsx` | Mensaje individual (user/assistant) |
| `SourceCard.tsx` | Tarjeta de fuente citada |

---

## 📐 TEMPLATES (`App.tsx`)

Composición de organismos en layouts.

```tsx
<App>
  <AnimatedBackground />      // Fondo
  <Sidebar />                 // Organismo: navegación
  <ChatHeader />              // Organismo: header
  <WelcomeScreen | Messages>  // Organismo: contenido
  <ChatInput />               // Organismo: input
</App>
```

---

## 🔄 Flujo de Datos

```
App (Template)
├── selectedModel (state)
├── useChat(selectedModel)
│   ├── sessions
│   ├── sendMessage()
│   └── createNewSession()
│
├── Sidebar ← (selectedModel, onModelChange)
├── ChatHeader ← (title, onNewChat)
├── WelcomeScreen/Messages ← (messages)
└── ChatInput ← (onSend, isLoading)
```

---

## ✅ Cumplimiento de Principios

| Principio | Cumple | Notas |
|-----------|--------|-------|
| **Átomos reutilizables** | ✅ | 53 componentes UI base |
| **Separación de concerns** | ✅ | ui / ui-custom / chat |
| **Composición sobre herencia** | ✅ | Props y children |
| **Single responsibility** | ✅ | 1 componente = 1 función |
| **Props tipadas** | ✅ | TypeScript interfaces |
| **Estado centralizado** | ✅ | Hook useChat en App |

---

## 📁 Estructura Final

```
frontend/
├── react-app/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/           # 53 átomos (Radix)
│   │   │   ├── ui-custom/    # 3 moléculas
│   │   │   └── chat/         # 6 organismos
│   │   ├── hooks/
│   │   │   └── useChat.ts    # Lógica de chat + API
│   │   ├── types/
│   │   │   └── index.ts      # Tipos TypeScript
│   │   ├── lib/
│   │   │   └── utils.ts      # Utilidades (cn, etc)
│   │   ├── App.tsx           # Template principal
│   │   └── main.tsx          # Entry point
│   ├── public/
│   │   └── inaoe-logo.png
│   └── package.json
└── Dockerfile
```
