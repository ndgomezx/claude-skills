# Riesgos de uso — engram

## Resumen ejecutivo

engram conecta Claude Code con Pinecone y Google Gemini para memoria semántica persistente. Esto introduce dependencias de servicios externos y puntos de riesgo que el equipo debe evaluar antes de adoptar la herramienta.

---

## 1. Privacidad y fuga de datos

| Riesgo | Severidad | Probabilidad |
|---|---|---|
| Datos sensibles indexados en Pinecone (EE.UU.) | Alta | Media |
| Textos enviados a Gemini para embedding | Alta | Alta (siempre) |
| Claves API en texto plano en `settings.json` | Alta | Alta |

**Mitigaciones:**
- Establecer una política de qué datos pueden guardarse (nunca: PII, tokens, contraseñas, datos de clientes).
- Usar variables de entorno del sistema en lugar de `settings.json` si es posible.
- Revisar periódicamente qué está indexado con `mcp__engram__list`.

---

## 2. Costos de API

| Servicio | Modelo de costo | Riesgo |
|---|---|---|
| Gemini Embeddings | Por token enviado | Documentos grandes o upserts masivos |
| Pinecone | Por vectores almacenados + consultas | Plan gratuito: 100K vectores |

**Mitigaciones:**
- Establecer límites de uso en las consolas de Pinecone y Google AI Studio.
- Evitar upserts automáticos sin control (p.ej. no indexar conversaciones enteras).
- Monitorear el uso mensual.

---

## 3. Confiabilidad de resultados

La búsqueda semántica devuelve documentos **similares**, no necesariamente **correctos**:

- Un score de 0.9 significa similitud vectorial, no veracidad.
- Información desactualizada puede rankearse más alta que información reciente.
- Namespace equivocado puede devolver resultados de otro proyecto.

**Mitigaciones:**
- Siempre incluir `date` en metadata para detectar información obsoleta.
- Tratar los resultados como hints, no como hechos.
- Validar contra el código o documentación primaria.

---

## 4. Seguridad de claves

El archivo `~/.claude/settings.json` almacena las claves en texto plano.

**Vectores de ataque:**
- Malware con acceso al sistema de archivos.
- Accidental commit del archivo a un repositorio.
- Compartir la pantalla o el archivo con terceros.

**Mitigaciones:**
```bash
# Permisos restrictivos en el archivo
chmod 600 ~/.claude/settings.json

# Agregar al .gitignore global
echo "settings.json" >> ~/.gitignore_global
git config --global core.excludesfile ~/.gitignore_global
```

---

## 5. Consistencia de datos

- **Sin versionado**: un `upsert` con el mismo ID sobreescribe sin historial.
- **Sin transacciones**: si el proceso falla a mitad de un upsert masivo, el índice queda en estado inconsistente.
- **Sin confirmación de escritura**: Pinecone puede tardar segundos en hacer disponible un vector recién insertado.

**Mitigaciones:**
- Usar IDs con timestamp para evitar sobreescrituras accidentales.
- Hacer backups periódicos exportando con `mcp__engram__list`.

---

## 6. Dependencia de servicios externos

Si Pinecone o Gemini están caídos:
- La skill falla completamente (sin fallback local).
- Claude no puede recuperar contexto de sesiones anteriores.
- Los errores pueden no ser informativos para el usuario.

**Mitigaciones:**
- Documentar decisiones importantes también en archivos locales (CLAUDE.md, ADRs).
- No depender de engram como única fuente de memoria para información crítica.

---

## 7. Riesgo de vendor lock-in

Los embeddings de Gemini no son compatibles directamente con embeddings de otros modelos (OpenAI, Cohere, etc.). Migrar a otro proveedor requiere re-indexar todo el contenido.

---

## Evaluación de riesgo general

```
Privacidad:      ████████░░  Alto
Costos:          █████░░░░░  Medio
Confiabilidad:   ██████░░░░  Medio-Alto
Seguridad:       ███████░░░  Alto
Consistencia:    ████░░░░░░  Medio
Disponibilidad:  █████░░░░░  Medio
```

**Recomendación**: Apropiado para uso personal o en equipos con datos no sensibles. Evaluar antes de usar con datos de clientes o información confidencial del negocio.
