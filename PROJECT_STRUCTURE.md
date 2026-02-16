# IncluTalk - Estructura del Proyecto

```
inclutalk/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── security.py
│   │   │   ├── jwt.py
│   │   │   └── middleware.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── institution.py
│   │   │   ├── user.py
│   │   │   ├── session.py
│   │   │   └── metrics.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── institution.py
│   │   │   ├── user.py
│   │   │   ├── session.py
│   │   │   └── lsp.py
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── institutions.py
│   │   │   ├── users.py
│   │   │   ├── sessions.py
│   │   │   ├── stt.py
│   │   │   ├── lsp.py
│   │   │   ├── metrics.py
│   │   │   └── websocket.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── institution_service.py
│   │   │   ├── user_service.py
│   │   │   ├── session_service.py
│   │   │   ├── stt_service.py
│   │   │   └── metrics_service.py
│   │   ├── ml/
│   │   │   ├── __init__.py
│   │   │   ├── feature_extraction.py
│   │   │   ├── model.py
│   │   │   ├── predict.py
│   │   │   └── models/
│   │   │       └── .gitkeep
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── rate_limiter.py
│   │       └── logger.py
│   ├── alembic/
│   │   ├── versions/
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── scripts/
│   │   ├── seed_data.py
│   │   └── create_admin.py
│   ├── tests/
│   │   └── __init__.py
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── .env.example
│   └── README.md
│
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── vite-env.d.ts
│   │   ├── api/
│   │   │   ├── client.ts
│   │   │   ├── auth.ts
│   │   │   ├── institutions.ts
│   │   │   ├── users.ts
│   │   │   ├── sessions.ts
│   │   │   ├── stt.ts
│   │   │   └── lsp.ts
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   ├── Card.tsx
│   │   │   │   └── Loading.tsx
│   │   │   ├── auth/
│   │   │   │   └── LoginForm.tsx
│   │   │   ├── operator/
│   │   │   │   ├── VoiceToTextPanel.tsx
│   │   │   │   ├── SignToTextPanel.tsx
│   │   │   │   ├── TextToVoicePanel.tsx
│   │   │   │   ├── CameraCapture.tsx
│   │   │   │   ├── SignDetection.tsx
│   │   │   │   └── PhraseBuilder.tsx
│   │   │   └── admin/
│   │   │       ├── UserList.tsx
│   │   │       ├── MetricsDashboard.tsx
│   │   │       └── BillingInfo.tsx
│   │   ├── pages/
│   │   │   ├── Login.tsx
│   │   │   ├── AdminDashboard.tsx
│   │   │   ├── OperatorDashboard.tsx
│   │   │   └── AttentionView.tsx
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   ├── useMediaPipe.ts
│   │   │   ├── useSpeechRecognition.ts
│   │   │   └── useSpeechSynthesis.ts
│   │   ├── context/
│   │   │   └── AuthContext.tsx
│   │   ├── types/
│   │   │   └── index.ts
│   │   └── utils/
│   │       ├── constants.ts
│   │       └── helpers.ts
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── README.md
│
└── README.md
```
