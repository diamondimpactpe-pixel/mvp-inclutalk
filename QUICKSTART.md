# 🚀 IncluTalk - Guía de Inicio Rápido

## 📦 Instalación y Ejecución

### Opción 1: Docker (Recomendado)

```bash
# 1. Iniciar servicios
cd backend
cp .env.example .env
docker-compose up -d

# 2. Esperar a que PostgreSQL esté listo (30 segundos)
sleep 30

# 3. Ejecutar migraciones
docker-compose exec backend alembic upgrade head

# 4. Seed de datos
docker-compose exec backend python scripts/seed_data.py

# Backend corriendo en http://localhost:8000
```

### Opción 2: Local Development

#### Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
# Editar .env con tu configuración

# Iniciar PostgreSQL (manual o Docker)
docker run -d -p 5432:5432 \
  -e POSTGRES_USER=inclutalk_user \
  -e POSTGRES_PASSWORD=inclutalk_pass \
  -e POSTGRES_DB=inclutalk_db \
  postgres:15-alpine

# Ejecutar migraciones
alembic upgrade head

# Seed datos
python scripts/seed_data.py

# Iniciar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Iniciar desarrollo
npm run dev

# Frontend en http://localhost:3000
```

## 🔑 Credenciales de Prueba

```
Admin:
Email: admin@hospital.com
Password: Admin123!

Operador:
Email: operator@hospital.com
Password: Operator123!
```

## 🧪 Probar la API

```bash
# Health check
curl http://localhost:8000/health

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"operator@hospital.com","password":"Operator123!"}'

# Vocabulario LSP
curl http://localhost:8000/api/v1/lsp/vocabulary
```

## 📱 Usar la Aplicación

1. Abrir http://localhost:3000
2. Login con credenciales de operador
3. Click en "Iniciar Atención"
4. Probar flujo de atención

## 🎯 Modo Demo

Por defecto, el sistema funciona en **DEMO MODE**:
- LSP predictions son simuladas (no requiere modelo real)
- STT usa frases de ejemplo
- TTS usa Web Speech API del navegador

## 🐛 Troubleshooting

### Backend no inicia
```bash
# Ver logs
docker-compose logs backend

# Revisar conexión a DB
docker-compose ps
```

### Frontend no conecta con backend
```bash
# Verificar CORS en backend/.env
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# Verificar proxy en frontend/vite.config.ts
```

### Error en migraciones
```bash
# Reset base de datos
docker-compose down -v
docker-compose up -d
# Esperar 30 segundos y repetir migraciones
```

## 📚 Documentación API

Una vez iniciado el backend:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

