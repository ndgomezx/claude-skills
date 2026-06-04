---
name: engram
description: >
  Memoria persistente para agentes de IA. Guarda decisiones, bugfixes,
  patrones y contexto entre sesiones usando SQLite local + FTS5.
  Sin servicios externos, sin API keys, sin costo por uso.
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
  source: https://github.com/Gentleman-Programming/engram
  version: "1.0"
---

# engram — Memoria Persistente Local (Claude Code)

Binario Go con SQLite + FTS5. Sin Pinecone, sin Gemini, sin red.
Todo queda en `~/.engram/engram.db`.

```
Claude Code → MCP stdio → engram binary → SQLite (~/.engram/engram.db)
```

## Instalación

```bash
# macOS
brew install gentleman-programming/tap/engram

# Configurar en Claude Code (una sola vez)
claude plugin marketplace add Gentleman-Programming/engram && claude plugin install engram
```

Otros métodos → https://github.com/Gentleman-Programming/engram/blob/main/docs/INSTALLATION.md

---

## Herramientas MCP (19)

| Categoría | Herramientas |
|---|---|
| Guardar / Editar | `mem_save`, `mem_update`, `mem_delete`, `mem_suggest_topic_key` |
| Buscar / Recuperar | `mem_search`, `mem_context`, `mem_timeline`, `mem_get_observation` |
| Ciclo de sesión | `mem_session_start`, `mem_session_end`, `mem_session_summary` |
| Conflictos | `mem_judge`, `mem_compare` |
| Utilidades | `mem_save_prompt`, `mem_stats`, `mem_capture_passive`, `mem_merge_projects`, `mem_current_project`, `mem_doctor` |

---

## Disparadores — cuándo actuar

Activa esta skill cuando el usuario:
- Pide guardar una decisión, bugfix, patrón o aprendizaje
- Pregunta "¿qué hicimos con X?", "¿cómo resolvimos Y?", "recordame lo de Z"
- Menciona un tema sin dar contexto — buscar primero en memoria
- Comienza a trabajar en algo que puede haberse hecho antes
- Cierra una sesión o dice "terminamos por hoy"

---

## Pasos para Claude

### Al iniciar sesión
```
1. Llamar mem_current_project → detecta el proyecto activo
2. Llamar mem_context          → recupera contexto de sesiones anteriores
3. Si el usuario menciona un tema concreto → mem_search con esas palabras
```

### Guardar memoria (mem_save)
Llamar INMEDIATAMENTE después de cualquiera de estos eventos:
- Bugfix completado
- Decisión de arquitectura o diseño
- Descubrimiento no obvio del codebase
- Cambio de configuración
- Patrón establecido (nombres, estructura, convención)
- Preferencia o restricción del usuario

**Formato obligatorio:**
```
title:    Verbo + qué (corto y buscable, ej: "Fijé N+1 en UserList")
type:     bugfix | decision | architecture | discovery | pattern | config | preference
scope:    project (default) | personal | global
topic_key: (opcional) clave estable para temas evolutivos, ej: "architecture/auth-model"
content:
  **What**: Una oración — qué se hizo
  **Why**: Qué lo motivó (bug, rendimiento, pedido del usuario)
  **Where**: Archivos o rutas afectadas
  **Learned**: Gotchas, edge cases, sorpresas (omitir si no hay)
```

**Reglas de topic_key:**
- Temas distintos nunca deben sobreescribirse entre sí
- Reusar el mismo `topic_key` para actualizar un tema en evolución (evita duplicados)
- Si no estás seguro del key → llamar `mem_suggest_topic_key` primero
- Si tenés el ID exacto → usar `mem_update` en lugar de `mem_save`

### Buscar memoria
```
usuario: "¿cómo resolvimos el bug de autenticación?"

1. mem_context   → contexto de sesiones recientes (rápido)
2. Si no encontró → mem_search(query="bug autenticación")
3. Si encontró ID relevante → mem_get_observation(id) para contenido completo
4. Si mem_save devuelve candidates[] con judgment_required: true
   → inspeccionar candidatos y llamar mem_judge con el veredicto
```

### Búsqueda proactiva
```
Antes de empezar trabajo que pudo haberse hecho antes:
→ mem_search(query="<tema>", all_projects=false)
→ Si hay resultados, informarlos al usuario antes de continuar
```

### Cerrar sesión (OBLIGATORIO antes de "listo" / "terminamos")
```
mem_session_summary con:
  ## Goal          — objetivo de la sesión
  ## Instructions  — restricciones o contexto que dio el usuario
  ## Discoveries   — hallazgos importantes
  ## Accomplished  — qué se completó
  ## Next Steps    — pendientes
  ## Relevant Files — archivos clave modificados o leídos
```

---

## Tipos de observación

| type | Cuándo usarlo |
|---|---|
| `decision` | Elegimos X en lugar de Y |
| `architecture` | Estructura del sistema, patrones de diseño |
| `bugfix` | Causa raíz de un bug y cómo se arregló |
| `discovery` | Algo no obvio encontrado en el codebase |
| `pattern` | Convención o patrón establecido |
| `config` | Setup, variables de entorno, herramientas |
| `preference` | Preferencia o restricción del usuario |

## Scopes

| scope | Uso |
|---|---|
| `project` | Específico de este repositorio (default) |
| `personal` | Preferencias del usuario, independiente del proyecto |
| `global` | Decisiones que aplican a todos los proyectos |

---

## ⚠️ Riesgos de uso

Ver [RISKS.md](RISKS.md) para análisis completo.

**Resumen rápido:**
- El archivo `~/.engram/engram.db` contiene toda la memoria — hacer backup
- No guardar datos sensibles: contraseñas, tokens, PII (aunque es local, puede sincronizarse)
- La búsqueda FTS5 es exacta por palabras, no semántica — buscar con sinónimos si falla
- Conflictos entre memorias deben resolverse con `mem_judge` para mantener coherencia
