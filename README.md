# 🚀 IncluTalk MVP

**Plataforma B2B SaaS para Atención Inclusiva con Lengua de Señas Peruana (LSP)**

IncluTalk es una aplicación web que permite conversación por turnos entre personal de ventanilla y usuarios de LSP, integrando:
- **VOZ → TEXTO** (Speech-to-Text)
- **LSP (Señas) → TEXTO** (Visión + LSTM)
- **TEXTO → VOZ** (Text-to-Speech)

---

## 📋 Características Principales

### ✅ Funcionalidades Core
- **Reconocimiento de Señas**: Modelo LSTM con MediaPipe para detectar palabras de LSP
- **Vocabulario Acotado**: 40+ palabras para escenarios de atención al cliente
- **Multi-tenant**: Arquitectura segura para múltiples instituciones
- **Roles**: Superadmin, Admin (institución), Operator (ventanilla)
- **Métricas**: Tracking de sesiones, intentos, confianza promedio
- **Privacidad**: No guarda conversaciones por defecto, solo métricas agregadas

### 🎯 Modelo de Negocio
- **Base mensual**: S/ 150 (incluye 1 punto de atención)
- **Punto adicional**: S/ 90 por ventanilla extra

---

## 🏗️ Arquitectura

### Backend
- **FastAPI** + Python 3.11
- **PostgreSQL** (base de datos)
- **SQLAlchemy** + Alembic (ORM y migraciones)
- **JWT** (autenticación)
- **TensorFlow/Keras** (modelo LSTM para LSP)
- **MediaPipe** (extracción de keypoints)
- **Whisper** (STT, opcional)

### Frontend
- **React** 18 + **TypeScript**
- **Vite** (build tool)
- **Tailwind CSS** (estilos)
- **MediaPipe Tasks Vision** (detección de manos en navegador)
- **Axios** (API client)

---

## 🚀 Quick Start

### Prerrequisitos
- Docker & Docker Compose
- Node.js 18+ (para desarrollo frontend)
- Python 3.11+ (para desarrollo backend)

### 1️⃣ Clonar y Configurar

```bash
# Clonar el repositorio
cd inclutalk

# Backend: Copiar .env
cd backend
cp .env.example .env
# Editar .env con tus configuraciones

cd ..
```

### 2️⃣ Iniciar con Docker

```bash
cd backend
docker-compose up -d
```

Esto iniciará:
- PostgreSQL en puerto 5432
- Backend FastAPI en puerto 8000

### 3️⃣ Ejecutar Migraciones

```bash
cd backend

# Activar entorno virtual (opcional)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar migraciones
alembic upgrade head
```

### 4️⃣ Crear Usuario Inicial

```bash
# Ejecutar script de seed
python scripts/seed_data.py
```

Esto creará:
- **Institución**: "Hospital Central"
- **Admin**: admin@hospital.com / Admin123!
- **Operador**: operator@hospital.com / Operator123!

### 5️⃣ Iniciar Frontend

```bash
cd ../frontend

# Instalar dependencias
npm install

# Iniciar desarrollo
npm run dev
```

Frontend disponible en: http://localhost:3000

---

## 📡 API Endpoints

### Autenticación
```
POST   /api/v1/auth/login       - Login
POST   /api/v1/auth/refresh     - Refresh token
GET    /api/v1/auth/me          - Usuario actual
POST   /api/v1/auth/logout      - Logout
```

### Sesiones
```
POST   /api/v1/sessions/start                - Iniciar sesión
GET    /api/v1/sessions/{id}                 - Obtener sesión
POST   /api/v1/sessions/{id}/end             - Finalizar sesión
PATCH  /api/v1/sessions/{id}/metrics         - Actualizar métricas
```

### LSP Recognition
```
POST   /api/v1/lsp/predict      - Predecir seña
GET    /api/v1/lsp/vocabulary   - Vocabulario disponible
```

---

## 🧠 Modelo de IA (LSP Recognition)

### Arquitectura
- **Input**: Secuencia de 15 frames con keypoints de MediaPipe
- **Features**: 300 dimensiones por frame (manos + pose)
- **Model**: LSTM de 2 capas
- **Output**: Clasificación entre 40+ palabras

### Demo Mode
Por defecto, el sistema funciona en **demo mode** (sin modelo real):
- Predicciones simuladas con confianza aleatoria (0.5-0.95)
- Perfecto para testing UI/UX
- Para usar modelo real: entrenar y colocar en `backend/app/ml/models/lsp_model.h5`

### Entrenamiento (Opcional)
```python
# Ver documentación en backend/app/ml/README.md
# Requiere dataset de videos de LSP etiquetados
```

---

## 🔒 Seguridad

- ✅ **JWT** con tokens de access y refresh
- ✅ **Bcrypt** para hashing de contraseñas
- ✅ **Rate limiting** (60 req/min por defecto)
- ✅ **CORS** configurado
- ✅ **Multi-tenant**: isolation por institución
- ✅ **Validación de contraseñas**: mínimo 8 caracteres, mayúsculas, números, símbolos

---

## 📊 Base de Datos

### Tablas Principales
```
institutions  - Organizaciones B2B
users         - Usuarios (admins y operadores)
sessions      - Sesiones de atención
metrics_daily - Métricas agregadas
```

### Migraciones
```bash
# Crear nueva migración
alembic revision --autogenerate -m "Descripción"

# Aplicar migraciones
alembic upgrade head

# Revertir última migración
alembic downgrade -1
```

---

## 🎨 Frontend

### Estructura
```
src/
├── api/          - Cliente API (axios)
├── components/   - Componentes React
├── pages/        - Páginas principales
├── hooks/        - Custom hooks
├── context/      - Context providers
├── types/        - TypeScript types
└── utils/        - Utilidades
```

### Flujo de Atención
1. Operador hace login
2. Click en "Iniciar Atención"
3. **Turno Personal**: Habla → STT → Texto visible
4. **Turno Usuario**: 
   - Opción A: Señas → Cámara → MediaPipe → Predicción
   - Opción B: Escribir texto
5. **Salida**: Texto → TTS (voz) + Display
6. Repetir turnos
7. "Finalizar sesión"

---

## 🧪 Testing

### Backend
```bash
cd backend
pytest tests/
```

### Frontend
```bash
cd frontend
npm run test
```

---

## 📦 Deployment

### Backend (Production)
```bash
# Build Docker image
docker build -t inclutalk-backend .

# Run con variables de entorno
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e SECRET_KEY=... \
  inclutalk-backend
```

### Frontend (Production)
```bash
cd frontend
npm run build
# Servir carpeta dist/ con nginx, vercel, etc.
```

---

## 📝 Consideraciones de Privacidad

Por defecto, IncluTalk **NO guarda**:
- ❌ Texto de conversaciones
- ❌ Audio grabado
- ❌ Video de cámara

Solo guarda:
- ✅ Métricas agregadas (duración, intentos, confianza promedio)
- ✅ Notas del operador (opcional, no conversación verbatim)

Configurable en `.env`:
```
SAVE_CONVERSATION_TEXT=False
SAVE_AUDIO_VIDEO=False
COLLECT_METRICS=True
```

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crear feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

---

## 📄 Licencia

Proyecto MVP - Todos los derechos reservados

---

## 👥 Equipo

Desarrollado para atención inclusiva en Perú 🇵🇪

---

## 📞 Soporte

Para problemas o preguntas:
- Issues: GitHub Issues
- Email: soporte@inclutalk.com

---

**¡Gracias por usar IncluTalk! 🙌**
