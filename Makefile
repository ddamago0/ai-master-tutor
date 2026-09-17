.PHONY: dev up down db-logs backend frontend test

# Levanta toda la infraestructura con el script de arranque
dev:
	@chmod +x start.sh
	@./start.sh

# Levanta únicamente el contenedor de PostgreSQL con pgvector
up:
	docker compose up -d postgres

# Detiene todos los contenedores de Docker
down:
	docker compose down

# Ver logs de la base de datos PostgreSQL
db-logs:
	docker compose logs -f postgres

# Levanta de forma aislada el backend
backend:
	cd backend && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Levanta de forma aislada el frontend
frontend:
	cd frontend && npm run dev
