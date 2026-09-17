# Guía de Pruebas Locales y Verificación End-to-End

Este documento detalla el procedimiento para verificar el funcionamiento integrado de **AI Master Tutor** a través de sus tres capas: la **Extensión de Navegador** (extracción DOM), el **Backend** (FastAPI + pgvector + ChromaDB + LiteLLM) y el **Frontend** (Next.js Dashboard).

---

## 1. Arranque de la Infraestructura

Antes de probar, asegúrate de levantar los servicios locales ejecutando:

```bash
chmod +x start.sh
./start.sh
# O alternativamente:
bash start.sh
# O con Makefile:
make dev
```

Esto ejecutará de forma coordinada:
- **PostgreSQL 16 + pgvector:** `localhost:5432` (contenedor `ai_master_tutor_db`)
- **Backend API (FastAPI):** `http://localhost:8000` (Docs en `http://localhost:8000/api/v1/docs`)
- **Frontend Dashboard (Next.js):** `http://localhost:3000`

---

## 2. Instalación y Uso de la Extensión en Google Chrome

Sigue estos pasos para cargar la extensión directamente sin compilar:

1. Abre Google Chrome y navega a la URL interna:
   ```text
   chrome://extensions/
   ```
2. En la esquina superior derecha, activa el interruptor **Modo de desarrollador** (*Developer mode*).
3. Haz clic en el botón **Cargar descomprimida** (*Load unpacked*).
4. En el explorador de archivos, selecciona la carpeta:
   ```text
   /home/ddamago/Projects/ai-master-tutor/extension
   ```
5. La extensión **AI Master Tutor - Extractor** aparecerá en tu lista de extensiones activas.
6. **Prueba de Extracción:**
   - Navega a cualquier página con contenido educativo o artículo técnico (ej. Wikipedia, Moodle universitario, o documentación técnica).
   - Haz clic en el ícono de rompecabezas de extensiones y fija **AI Master Tutor**.
   - Abre el popup: verás el badge de plataforma detectada y el número de caracteres disponibles.
   - Pulsa el botón **EXTRAER Y ENVIAR AL TUTOR**.
   - El estado pasará a azul cobalto (*"Indexando Conocimiento..."*) y luego a verde (*"✓ Material Indexado"*).

---

## 3. Verificación de Embeddings en PostgreSQL (pgvector)

Para certificar que los fragmentos extraídos generaron embeddings vectoriales de 768 dimensiones y se guardaron en PostgreSQL:

### A. Consulta Interactiva con `psql` dentro del Contenedor Docker:
Ejecuta en tu terminal:

```bash
docker exec -it ai_master_tutor_db psql -U postgres -d ai_master_tutor -c "
SELECT 
    id, 
    title, 
    source_type, 
    vector_dims(embedding) AS dimensiones_vector,
    created_at 
FROM study_materials 
ORDER BY created_at DESC 
LIMIT 5;
"
```

**Resultado esperado:**
- La columna `dimensiones_vector` debe mostrar exactamente el valor `768`.
- El `source_type` reflejará la plataforma detectada (`moodle`, `q10`, `canvas` o `manual`).

### B. Comprobación de Búsqueda por Similitud Coseno Manual:
Puedes verificar la distancia vectorial ejecutando una consulta directa:

```bash
docker exec -it ai_master_tutor_db psql -U postgres -d ai_master_tutor -c "
SELECT 
    title, 
    1 - (embedding <=> (SELECT embedding FROM study_materials LIMIT 1)) AS similitud_coseno
FROM study_materials 
LIMIT 5;
"
```

---

## 4. Prueba del Endpoint del Tutor (Simulación Modo `ACTIVE_RECALL`)

Para simular una interacción desde el frontend cuando el estudiante activa el modo de **Active Recall** sobre el material que acaba de estudiar:

### A. Ejecución de la Petición `curl`:
Ejecuta en tu terminal:

```bash
curl -X POST http://localhost:8000/api/v1/tutor/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query": "ACTIVE_RECALL: Evalúa mi entendimiento sobre el tema que acabo de cargar. Hazme una pregunta socrática desafiante y dame una pista.",
    "top_k_context": 3,
    "bypass_cache": false
  }' | jq .
```

### B. Respuesta esperada (JSON):
```json
{
  "answer": "...",
  "cached": false,
  "cache_type": null,
  "sources": [
    {
      "material_id": "...",
      "title": "...",
      "source_type": "...",
      "similarity_score": 0.8245
    }
  ]
}
```

### C. Verificación del Caché Semántico Local (ChromaDB):
Si repites la misma consulta (o una paráfrasis muy similar semánticamente) inmediatamente después:

```bash
curl -X POST http://localhost:8000/api/v1/tutor/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query": "ACTIVE_RECALL: Evalúa mi entendimiento sobre el tema que acabo de cargar. Hazme una pregunta socrática desafiante y dame una pista.",
    "top_k_context": 3,
    "bypass_cache": false
  }' | jq .
```

**Resultado esperado:**
- `"cached": true`
- `"cache_type": "semantic"`
- Tiempo de respuesta inmediato (0 a 5 ms) sin consumir cuotas de las APIs externas.

---

## 5. Verificación de Repasos Espaciados (Algoritmo SM-2)

### A. Consultar tarjetas vencidas hoy:
```bash
curl -X GET http://localhost:8000/api/v1/recall/due | jq .
```

### B. Calificar un repaso para actualizar el intervalo SM-2:
Sustituye `<ITEM_ID>` por el UUID de la tarjeta y envía una calificación de 0 a 5 (ej. `5` para recuerdo perfecto):

```bash
curl -X POST http://localhost:8000/api/v1/recall/items/<ITEM_ID>/review \
  -H "Content-Type: application/json" \
  -d '{"rating": 5}' | jq .
```

El objeto devuelto mostrará el nuevo `interval` (días) y el `easiness_factor` actualizado según la fórmula del algoritmo SuperMemo-2.
