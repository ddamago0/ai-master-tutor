#!/usr/bin/env bash
# ==============================================================================
# AI Master Tutor - Local Infrastructure & Fullstack Startup Script
# ==============================================================================

set -e

# Project directories
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

echo "======================================================================"
echo "          INICIANDO ENTORNO LOCAL - AI MASTER TUTOR                   "
echo "======================================================================"

# 1. Ensure environment files exist
if [ ! -f "$BACKEND_DIR/.env" ] && [ -f "$BACKEND_DIR/.env.example" ]; then
    echo "[+] Creando backend/.env a partir de .env.example..."
    cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
fi

if [ ! -f "$FRONTEND_DIR/.env.local" ] && [ -f "$FRONTEND_DIR/.env.example" ]; then
    echo "[+] Creando frontend/.env.local a partir de .env.example..."
    cp "$FRONTEND_DIR/.env.example" "$FRONTEND_DIR/.env.local"
fi

# 2. Start PostgreSQL + pgvector container
echo "[+] Levantando contenedor PostgreSQL 16 con pgvector..."
if docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker-compose"
else
    echo "[-] Error: docker compose / docker-compose no encontrado en PATH."
    exit 1
fi

$DOCKER_COMPOSE -f "$ROOT_DIR/docker-compose.yml" up -d postgres

# Wait for PostgreSQL to be healthy
echo "[+] Esperando a que PostgreSQL este listo para recibir conexiones..."
for i in {1..30}; do
    if docker exec ai_master_tutor_db pg_isready -U postgres >/dev/null 2>&1; then
        echo "[✓] PostgreSQL + pgvector esta listo y respondiendo."
        break
    fi
    sleep 1
    if [ "$i" -eq 30 ]; then
        echo "[-] Advertencia: Tiempo de espera agotado esperando a PostgreSQL."
    fi
done

# Cleanup hook on exit / SIGINT
cleanup() {
    echo ""
    echo "[!] Deteniendo servidores locales..."
    if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        kill "$BACKEND_PID" 2>/dev/null || true
    fi
    if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        kill "$FRONTEND_PID" 2>/dev/null || true
    fi
    echo "[✓] Servidores detenidos. Los contenedores de Docker siguen activos."
    echo "    (Para detener la base de datos: $DOCKER_COMPOSE down)"
    exit 0
}
trap cleanup SIGINT SIGTERM

# 3. Start Backend (FastAPI + Uvicorn)
echo "[+] Iniciando Backend FastAPI en http://localhost:8000..."
cd "$BACKEND_DIR"

# Detect Python virtualenv if present
if [ -f "$BACKEND_DIR/.venv/bin/activate" ]; then
    source "$BACKEND_DIR/.venv/bin/activate"
elif [ -f "$BACKEND_DIR/venv/bin/activate" ]; then
    source "$BACKEND_DIR/venv/bin/activate"
elif [ -f "$ROOT_DIR/.venv/bin/activate" ]; then
    source "$ROOT_DIR/.venv/bin/activate"
fi

# Launch uvicorn
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait briefly for FastAPI to bind
sleep 2

# 4. Start Frontend (Next.js)
echo "[+] Iniciando Frontend Next.js en http://localhost:3000..."
cd "$FRONTEND_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "[!] node_modules no encontrado en frontend. Ejecutando npm install..."
    npm install
fi

npm run dev &
FRONTEND_PID=$!

echo "======================================================================"
echo " [✓] SERVICIOS EN EJECUCION EXITOSA:"
echo "     - Base de Datos: localhost:5432 (PostgreSQL + pgvector)"
echo "     - Backend API:   http://localhost:8000/docs (Swagger UI)"
echo "     - Frontend Web:  http://localhost:3000 (Dashboard)"
echo "     - Extension:     Cargar 'extension/' en chrome://extensions"
echo "======================================================================"
echo " Presiona Ctrl+C para detener el Backend y Frontend."

# Wait for background processes
wait
