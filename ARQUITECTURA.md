# AI Master Tutor - Especificación de Arquitectura

## 1. Visión General
AI Master Tutor es un sistema educativo interactivo de alto rendimiento y costo cero. Utiliza técnicas avanzadas de retención del aprendizaje (**Active Recall** y **Spaced Repetition**) sobre el material de estudio del usuario, prescindiendo de integraciones propietarias o credenciales de plataformas universitarias (Moodle, Q10).

---

## 2. Topología de Componentes (Monorepo)

```
ai-master-tutor/
├── backend/            # API asíncrona FastAPI, RAG híbrido y LLM Gateway
├── frontend/           # Aplicación Web Next.js (App Router, Tailwind, Dark editorial)
├── extension/          # Extensión Chrome Manifest V3 (DOM Extractor de LMS)
└── docker-compose.yml  # Servicios locales de soporte (PostgreSQL + pgvector)
```

---

## 3. Decisiones de Arquitectura

### 3.1 Frontend (`frontend/`)
- **Framework:** Next.js 14+ con App Router y TypeScript.
- **Estilo:** Dark, editorial y minimalista con Tailwind CSS.
- **Responsabilidad:** Visualización interactiva de sesiones de Active Recall, gestión de mazos/temas, métricas de retención y carga manual de archivos de estudio (PDF/DOCX).

### 3.2 Ingesta de Datos (`extension/` y Web Upload)
- **Extensión Chrome (Manifest V3):** Ejecuta scripts de contenido aislados en plataformas LMS (Moodle, Q10, Canvas) para parsear el contenido de texto directamente desde el DOM sin requerir credenciales de usuario.
- **Carga Web:** Carga manual de documentos PDF, DOCX y texto plano mediante endpoints asíncronos en el backend.

### 3.3 Backend (`backend/`)
- **Framework:** FastAPI (Python 3.11+) asíncrono con Pydantic v2 y SQLAlchemy 2.0 (asyncpg).
- **Estructura modular:**
  - `core/`: Configuraciones, seguridad y middlewares.
  - `models/`: Entidades relacionales (Usuarios, Cursos, Tarjetas de Repaso, Historial).
  - `schemas/`: Contratos de datos (Pydantic models para I/O).
  - `services/`: Ingesta, chunking, motor de repaso espaciado (SM-2 / FSRS) y RAG.
  - `api/v1/`: Rutas versionadas y desacopladas.

### 3.4 Base de Datos & Estrategia RAG Híbrida
- **PostgreSQL 16 + pgvector:** Almacenamiento primario relacional (usuarios, sesiones, flashcards, metadata) y embeddings para búsqueda semántica a largo plazo.
- **ChromaDB Local:** Base vectorial local ligera utilizada como **caché semántico** para consultas redundantes, reduciendo drásticamente latencia y consumo de cuotas.

### 3.5 LLM Gateway de Costo Cero (LiteLLM)
- **Capa de Abstracción:** LiteLLM gestiona llamadas uniformes entre múltiples proveedores de nivel gratuito:
  1. Google Gemini Flash (Google AI Studio)
  2. Groq (Llama 3 / Mixtral para inferencia ultrarrápida)
  3. Cohere (Embeddings y Rerank gratuito)
- **Estrategia de Fallback:** Si un proveedor satura su cuota o responde con error de rate limit (429), la petición conmuta transparentemente al siguiente proveedor en la cadena de prioridad.
- **Doble Nivel de Caché:**
  1. Exact Cache (hash de prompt idéntico).
  2. Semantic Cache (ChromaDB para similitud coseno > umbral, ej. 0.95).
