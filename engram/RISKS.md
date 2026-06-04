# Riesgos de uso — engram (Gentleman-Programming)

> Versión: binario Go + SQLite local. Sin Pinecone, sin Gemini, sin servicios cloud obligatorios.

## Resumen ejecutivo

engram es local-first: toda la memoria vive en `~/.engram/engram.db`. Esto elimina los riesgos de privacidad del cloud, pero introduce riesgos propios de gestión de archivos locales, integridad de datos y sincronización opcional.

---

## 1. Pérdida de datos

| Riesgo | Severidad | Probabilidad |
|---|---|---|
| Corrupción de `engram.db` por fallo de disco | Alta | Baja |
| Borrado accidental con `mem_delete` (hard delete) | Alta | Media |
| Pérdida al migrar de equipo sin hacer sync | Media | Media |

**Mitigaciones:**
```bash
# Backup manual del archivo de base de datos
cp ~/.engram/engram.db ~/.engram/engram.db.bak

# Usar git sync incorporado para replicar entre máquinas
engram sync
git add .engram/ && git commit -m "sync engram memories"
```
- Preferir `mem_delete` sin `hard=true` (soft delete, recuperable)
- Exportar periódicamente: `GET /export` o desde el TUI

---

## 2. Privacidad local

Aunque los datos no salen de tu máquina por defecto:

- El archivo `engram.db` es legible por cualquier proceso con acceso al home del usuario
- Si usas **Engram Cloud** (opcional), las memorias se replican a servidores externos
- El **git sync** sube memorias comprimidas al repositorio — si el repo es público, las memorias quedan expuestas

**Mitigaciones:**
```bash
chmod 600 ~/.engram/engram.db
# Si usas git sync, asegurarte de que el repo sea privado
# Agregar .engram/ a .gitignore si no querés sincronizar
```

---

## 3. Confiabilidad de la búsqueda

FTS5 es búsqueda **full-text exacta**, no semántica:

- Buscar "autenticación" NO encuentra notas que digan "auth" o "login"
- Buscar "JWT" NO encuentra notas sobre "tokens" si no usan esa palabra
- Sinónimos o abreviaturas requieren múltiples búsquedas

**Mitigaciones:**
- Usar títulos descriptivos con palabras clave al guardar (`mem_save`)
- Si la primera búsqueda falla, intentar con sinónimos o términos alternativos
- Usar `mem_context` primero (basado en proyecto/sesión, más tolerante)

---

## 4. Consistencia de memorias (conflictos)

- `mem_save` con el mismo `topic_key` sobreescribe el contenido anterior (incrementa `revision_count`)
- Dos agentes o sesiones guardando información contradictoria generan `candidates[]` con `judgment_required: true`
- Sin llamar `mem_judge`, los conflictos quedan como `pending` y contaminan los resultados de búsqueda con anotaciones `conflict: contested by #<id>`

**Mitigaciones:**
- Siempre resolver los `judgment_required: true` con `mem_judge`
- Si el confidence es < 0.7, preguntar al usuario antes de juzgar
- Usar `mem_compare` para análisis semántico proactivo entre memorias relacionadas

---

## 5. Crecimiento del archivo de base de datos

- Cada sesión, observación y prompt se acumula indefinidamente
- Sin limpieza periódica, `engram.db` puede volverse grande con el tiempo
- Las soft-deleted observations ocupan espacio hasta que se hard-delete o compactan

**Mitigaciones:**
```bash
engram tui  # revisar y limpiar memorias obsoletas visualmente
mem_stats   # monitorear cantidad de observaciones por proyecto
```

---

## 6. Disponibilidad del binario

- Si el binario `engram` no está instalado o actualizado, el MCP falla completamente
- Actualizaciones de engram pueden cambiar el esquema de SQLite (migraciones automáticas, pero posible downtime)

**Mitigaciones:**
```bash
# Verificar que engram está corriendo
mem_doctor

# Mantener actualizado
brew upgrade engram
```

---

## 7. Engram Cloud (opcional) — riesgos adicionales

Si se habilita la sincronización cloud:

| Riesgo | Descripción |
|---|---|
| Datos en servidores externos | Las memorias se replican a la infraestructura de Gentleman-Programming |
| Mutaciones cross-machine | Otro agente en otra máquina puede sobreescribir memorias |
| Dependencia de disponibilidad | Si el cloud está caído, la sincronización falla (pero lo local sigue funcionando) |

---

## Evaluación comparativa vs. engram (Pinecone/Gemini)

| | Esta versión (SQLite local) | Versión Pinecone/Gemini |
|---|---|---|
| Privacidad | Alta — todo local | Baja — datos a EE.UU. |
| Costo | Gratis | Por token/consulta |
| Tipo de búsqueda | FTS5 full-text exacta | Semántica por vectores |
| Disponibilidad offline | Total | Ninguna |
| Riesgo de pérdida | Backup manual necesario | Pinecone lo gestiona |
| Dependencias | Binario Go (cero deps) | Node.js + APIs externas |

---

## Evaluación de riesgo general

```
Pérdida de datos:    ████░░░░░░  Medio (mitigable con backup)
Privacidad local:    ██░░░░░░░░  Bajo (datos en tu máquina)
Privacidad cloud:    ██████░░░░  Medio-Alto (si se habilita sync)
Confiabilidad FTS5:  ███░░░░░░░  Bajo-Medio (búsqueda exacta)
Conflictos memoria:  ████░░░░░░  Medio (requiere discipline)
Crecimiento DB:      ██░░░░░░░░  Bajo (gestionable con TUI)
```

**Recomendación**: Apropiado para cualquier proyecto, incluidos datos sensibles, siempre que no se habilite la sincronización cloud con repositorios públicos. Hacer backup periódico de `~/.engram/engram.db`.
