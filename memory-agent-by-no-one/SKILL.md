---
name: memory-agent-by-no-one
description: >
  Agente de memoria persistente entre sesiones. Guarda decisiones, bugfixes,
  patrones y contexto usando SQLite local + FTS5. Sin servicios externos,
  sin API keys, sin costo por uso.
  Motor interno: engram (https://github.com/Gentleman-Programming/engram).
  Trigger: cuando el usuario pide recordar algo, guardar contexto, o
  buscar trabajo pasado.
triggers:
  - "recuerda que"
  - "guarda esto"
  - "¿qué sé sobre"
  - "¿qué hicimos con"
  - "acordate de"
  - "busca en la memoria"
  - "¿cómo resolvimos"
  - "recuérdame lo de"
  - "remember that"
  - "save this"
  - "what do we know about"
  - "how did we solve"
  - "recall"
license: Apache-2.0
metadata:
  author: no-one
  version: "1.0"
  engine: engram by Gentleman-Programming
  engine_source: https://github.com/Gentleman-Programming/engram
---

# memory-agent by no one

Agente de memoria persistente para sesiones de desarrollo.
Motor interno: **[engram](https://github.com/Gentleman-Programming/engram)** — binario Go, SQLite + FTS5, cero dependencias externas.

```
Claude / Antigravity / Codex / VS Code
         ↓ MCP stdio
      engram binary
         ↓
  SQLite (~/.engram/engram.db)
```

---

## Instalación del motor (engram)

```bash
# macOS
brew install gentleman-programming/tap/engram

# Linux / Windows → https://github.com/Gentleman-Programming/engram/blob/main/docs/INSTALLATION.md
```

## Configuración por agente

| Agente | Comando |
|---|---|
| **Claude Code** | `claude plugin marketplace add Gentleman-Programming/engram && claude plugin install engram` |
| **Codex** | `engram setup codex` |
| **Gemini CLI** | `engram setup gemini-cli` |
| **VS Code / Copilot** | `code --add-mcp '{"name":"engram","command":"engram","args":["mcp"]}'` |
| **Antigravity** | Config manual (ver abajo) |
| **Cursor / Windsurf** | Config manual JSON |
| **Cualquier agente MCP** | `engram mcp` (stdio) |

### Antigravity — config manual
Agregar a `~/.gemini/antigravity/mcp_config.json`:
```json
{
  "mcpServers": {
    "engram": {
      "command": "engram",
      "args": ["mcp"]
    }
  }
}
```

### Bob / agentes MCP genéricos
Si el agente soporta MCP stdio, agregar en su config:
```json
{
  "mcpServers": {
    "engram": {
      "command": "engram",
      "args": ["mcp"]
    }
  }
}
```
> Bob no tiene integración oficial probada con engram. Funciona si soporta MCP stdio estándar.

---

## Herramientas MCP disponibles (19)

| Categoría | Herramientas |
|---|---|
| Guardar / Editar | `mem_save`, `mem_update`, `mem_delete`, `mem_suggest_topic_key` |
| Buscar / Recuperar | `mem_search`, `mem_context`, `mem_timeline`, `mem_get_observation` |
| Ciclo de sesión | `mem_session_start`, `mem_session_end`, `mem_session_summary` |
| Conflictos | `mem_judge`, `mem_compare` |
| Utilidades | `mem_save_prompt`, `mem_stats`, `mem_capture_passive`, `mem_merge_projects`, `mem_current_project`, `mem_doctor` |

---

## Disparadores — cuándo actuar

Activar cuando el usuario:
- Pide guardar una decisión, bugfix, patrón o aprendizaje
- Pregunta "¿qué hicimos con X?", "¿cómo resolvimos Y?", "recordame lo de Z"
- Menciona un tema sin dar contexto — buscar en memoria antes de responder
- Comienza trabajo que puede haberse hecho antes
- Cierra una sesión o dice "terminamos por hoy"

---

## Pasos para el agente

### Al iniciar sesión
```
1. mem_current_project  → detecta el proyecto activo
2. mem_context          → recupera contexto de sesiones anteriores
3. Si el usuario menciona un tema concreto → mem_search con esas palabras
```

### Guardar memoria — llamar INMEDIATAMENTE después de:
- Bugfix completado
- Decisión de arquitectura o diseño
- Descubrimiento no obvio del codebase
- Cambio de configuración o entorno
- Patrón establecido (nombres, estructura, convención)
- Preferencia o restricción aprendida del usuario

**Formato obligatorio de mem_save:**
```
title:     Verbo + qué — corto y buscable  (ej: "Fijé N+1 en UserList")
type:      bugfix | decision | architecture | discovery | pattern | config | preference
scope:     project (default) | personal | global
topic_key: (opcional) clave estable para temas evolutivos  (ej: "architecture/auth-model")
content:
  **What**: Una oración — qué se hizo
  **Why**: Qué lo motivó (bug, rendimiento, pedido del usuario)
  **Where**: Archivos o rutas afectadas
  **Learned**: Gotchas, edge cases, sorpresas (omitir si no hay)
```

**Reglas de topic_key:**
- Temas distintos nunca sobreescriben el mismo key
- Reusar el mismo key para actualizar un tema en evolución (evita duplicados)
- Si no estás seguro del key → llamar `mem_suggest_topic_key` primero
- Si tenés el ID exacto → usar `mem_update` en lugar de `mem_save`

### Buscar memoria
```
usuario: "¿cómo resolvimos el bug de autenticación?"

1. mem_context   → contexto de sesiones recientes (rápido, barato)
2. Si no encontró → mem_search(query="bug autenticación")
3. Si encontró ID relevante → mem_get_observation(id) para contenido completo
4. Si mem_save devolvió candidates[] + judgment_required: true
   → inspeccionar candidatos y resolver con mem_judge
```

### Búsqueda proactiva
Antes de empezar trabajo que pudo haberse hecho antes:
```
mem_search(query="<tema>") → informar resultados al usuario antes de continuar
```

### Cerrar sesión — OBLIGATORIO antes de "listo" / "terminamos"
```
mem_session_summary con:
  ## Goal           — objetivo de la sesión
  ## Instructions   — restricciones o contexto dado por el usuario
  ## Discoveries    — hallazgos importantes
  ## Accomplished   — qué se completó
  ## Next Steps     — pendientes
  ## Relevant Files — archivos clave modificados o leídos
```

---

## Tipos y scopes

| type | Cuándo |
|---|---|
| `decision` | Elegimos X en lugar de Y |
| `architecture` | Estructura del sistema, patrones de diseño |
| `bugfix` | Causa raíz de un bug y cómo se arregló |
| `discovery` | Algo no obvio encontrado en el codebase |
| `pattern` | Convención o patrón establecido |
| `config` | Setup, variables de entorno, herramientas |
| `preference` | Preferencia o restricción del usuario |

| scope | Uso |
|---|---|
| `project` | Específico de este repositorio (default) |
| `personal` | Preferencias del usuario, cross-project |
| `global` | Decisiones que aplican a todos los proyectos |

---

## ⚠️ Riesgos de uso

Ver [RISKS.md](RISKS.md) para análisis completo.

**Resumen rápido:**
- `~/.engram/engram.db` contiene toda la memoria — hacer backup periódico
- No guardar contraseñas, tokens ni PII (aunque es local, puede sincronizarse via git)
- FTS5 es búsqueda exacta por palabras — buscar con sinónimos si la primera búsqueda falla
- Si `mem_save` devuelve `judgment_required: true` → resolver conflicto con `mem_judge`
