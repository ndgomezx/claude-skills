---
name: engram
description: Semantic search and memory management for a local knowledge base using Pinecone vector database and Gemini embeddings. Use when the user wants to store notes, retrieve past context, search their knowledge base, or build persistent memory across sessions.
triggers:
  - "busca en mis notas"
  - "recuerda que"
  - "agrega esto a mi base de conocimiento"
  - "¿qué sé sobre"
  - "guarda esto"
  - "search my knowledge"
  - "remember that"
  - "add to knowledge base"
  - "what do I know about"
  - "retrieve context about"
---

# engram — Semantic Knowledge Base (Claude Code)

Motor de memoria persistente usando **Pinecone** (vector store) y **Gemini** (embeddings). Permite almacenar, buscar y gestionar notas y contexto entre sesiones.

## Prerequisitos

El MCP `engram` debe estar configurado en `~/.claude/settings.json` con las claves de API:

```json
{
  "mcpServers": {
    "engram": {
      "command": "npx",
      "args": ["-y", "@openclaw/engram-mcp"],
      "env": {
        "PINECONE_API_KEY": "<tu-clave-pinecone>",
        "PINECONE_INDEX": "<nombre-del-indice>",
        "GEMINI_API_KEY": "<tu-clave-gemini>"
      }
    }
  }
}
```

## Herramientas MCP disponibles

| Herramienta | Descripción |
|---|---|
| `mcp__engram__search` | Búsqueda semántica en la base de conocimiento |
| `mcp__engram__upsert` | Agregar o actualizar un documento |
| `mcp__engram__delete` | Eliminar un documento por ID |
| `mcp__engram__list` | Listar documentos en un namespace |
| `mcp__engram__namespaces` | Listar namespaces disponibles |

## Disparadores — cuándo usar esta skill

Activa esta skill cuando el usuario:
- Pide buscar en sus notas, memoria o base de conocimiento
- Quiere guardar contexto, decisiones técnicas, o aprendizajes
- Pregunta "¿qué sé sobre X?" o "recuérdame lo de Y"
- Necesita contexto de sesiones anteriores
- Quiere indexar documentación, decisiones o fragmentos de código

## Pasos para Claude

### 1. Buscar (search)
```
usuario: "busca lo que sé sobre autenticación JWT"

→ Llamar: mcp__engram__search(
    query="autenticación JWT",
    top_k=5,
    namespace="default"
  )
→ Presentar resultados con su score de relevancia
→ Si score < 0.5: indicar que no hay resultados confiables
```

### 2. Guardar (upsert)
```
usuario: "guarda esto: usamos RS256 para JWT porque el equipo de seguridad lo requiere"

→ Generar ID descriptivo: "jwt-rs256-decision-<timestamp>"
→ Llamar: mcp__engram__upsert(
    id="jwt-rs256-decision-1717488000",
    text="Usamos RS256 para JWT porque el equipo de seguridad lo requiere.",
    metadata={
      "type": "decision",
      "topic": "autenticación",
      "date": "<fecha-actual>"
    },
    namespace="default"
  )
→ Confirmar con el usuario
```

### 3. Eliminar (delete)
```
usuario: "elimina la nota sobre JWT RS256"

→ Primero buscar: mcp__engram__search(query="JWT RS256", top_k=3)
→ Mostrar al usuario qué documentos se encontraron
→ CONFIRMAR antes de eliminar
→ Llamar: mcp__engram__delete(id="<id-confirmado>")
```

### 4. Listar
```
usuario: "¿qué tengo guardado en mi base de conocimiento?"

→ Llamar: mcp__engram__list(namespace="default", limit=50)
→ Agrupar por metadata.type si está disponible
```

## Namespaces recomendados

| Namespace | Uso |
|---|---|
| `default` | Notas generales |
| `decisions` | Decisiones técnicas del proyecto |
| `code` | Fragmentos de código importantes |
| `research` | Investigación y referencias |
| `personal` | Contexto personal del usuario |

## Reglas importantes

1. **Nunca eliminar sin confirmar** — siempre mostrar al usuario qué se va a borrar.
2. **Scores bajos** (< 0.5): indicar explícitamente que la búsqueda no encontró coincidencias confiables.
3. **IDs descriptivos**: usar formato `<topic>-<subtopic>-<timestamp>` para facilitar gestión.
4. **Metadata siempre**: incluir al menos `type` y `date` al hacer upsert.
5. **Límite de contexto**: si hay muchos resultados, priorizar los de mayor score.

## ⚠️ Riesgos de uso

### Privacidad y datos
- **Riesgo alto**: todo el texto se envía a Pinecone (EE.UU.) y Gemini (Google) para generar embeddings. No guardar datos sensibles: contraseñas, tokens, datos personales de terceros, información confidencial de clientes.
- Los embeddings son difíciles de "desindexar" completamente; asumir que los datos persisten.

### Costos de API
- Gemini cobra por embedding (por token). Documentos grandes o upserts frecuentes pueden generar costos inesperados.
- Pinecone tiene límites en el plan gratuito (1 índice, 100K vectores). Superar el límite puede causar errores silenciosos.

### Confiabilidad de resultados
- La búsqueda semántica NO es búsqueda exacta. Puede devolver resultados relevantes pero con contexto incorrecto.
- Scores altos no garantizan que la información sea correcta o actual.
- No usar como única fuente de verdad — siempre validar contra el código o documentación original.

### Seguridad de claves
- Las claves `PINECONE_API_KEY` y `GEMINI_API_KEY` se almacenan en `settings.json` en texto plano.
- No compartir `settings.json` ni subirlo a repositorios públicos.
- Rotar claves si el archivo se expone accidentalmente.

### Consistencia de datos
- No hay versionado de documentos. Un `upsert` sobreescribe silenciosamente el documento anterior con el mismo ID.
- Si dos sesiones escriben con el mismo ID simultáneamente, puede haber pérdida de datos.

### Dependencia de servicios externos
- Si Pinecone o Gemini están caídos, la skill falla completamente.
- No hay fallback local — sin red, sin memoria.
