#!/bin/bash

echo "🎨 Generando Frontend Completo..."

# ============================================================================
# PACKAGE.JSON
# ============================================================================

cat > frontend/package.json << 'EOF'
{
  "name": "inclutalk-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "@mediapipe/tasks-vision": "^0.10.8",
    "axios": "^1.6.2"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.2.2",
    "vite": "^5.0.8",
    "tailwindcss": "^3.3.6",
    "postcss": "^8.4.32",
    "autoprefixer": "^10.4.16"
  }
}
EOF

# ============================================================================
# VITE CONFIG
# ============================================================================

cat > frontend/vite.config.ts << 'EOF'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
EOF

# ============================================================================
# TSCONFIG
# ============================================================================

cat > frontend/tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
EOF

cat > frontend/tsconfig.node.json << 'EOF'
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
EOF

# ============================================================================
# TAILWIND CONFIG
# ============================================================================

cat > frontend/tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
        },
        accent: {
          500: '#f59e0b',
          600: '#d97706',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Poppins', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
EOF

cat > frontend/postcss.config.js << 'EOF'
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOF

# ============================================================================
# INDEX.HTML
# ============================================================================

cat > frontend/index.html << 'EOF'
<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>IncluTalk - Atención Inclusiva</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@600;700;800&display=swap" rel="stylesheet">
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
EOF

# ============================================================================
# TYPES
# ============================================================================

cat > frontend/src/types/index.ts << 'EOF'
export interface User {
  id: number;
  email: string;
  username: string;
  role: 'superadmin' | 'admin' | 'operator';
  institution_id?: number;
  institution_name?: string;
  full_name: string;
  is_active: number;
}

export interface Session {
  id: number;
  institution_id: number;
  operator_id?: number;
  started_at: string;
  ended_at?: string;
  turns_count: number;
  stt_attempts: number;
  lsp_attempts: number;
  lsp_failed_attempts: number;
  text_fallback_count: number;
  avg_confidence: number;
  total_duration_seconds: number;
  is_active: boolean;
  duration_minutes: number;
}

export interface LSPPrediction {
  label: string;
  confidence: number;
  is_confident: boolean;
  threshold: number;
  alternatives?: Array<{label: string; confidence: number}>;
}

export interface LSPKeypoint {
  x: number;
  y: number;
  z?: number;
  visibility?: number;
}

export interface LSPFrame {
  timestamp: number;
  face_landmarks?: LSPKeypoint[];
  left_hand_landmarks?: LSPKeypoint[];
  right_hand_landmarks?: LSPKeypoint[];
  pose_landmarks?: LSPKeypoint[];
}
EOF

# ============================================================================
# CONSTANTS
# ============================================================================

cat > frontend/src/utils/constants.ts << 'EOF'
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const API_V1_PREFIX = '/api/v1';

export const LSP_VOCABULARY = [
  'DNI', 'CITA', 'PAGO', 'RECLAMO', 'CONSULTA',
  'NOMBRE', 'FECHA', 'MONTO', 'VENCIDO', 'PERDIDO',
  'RENOVAR', 'EMERGENCIA', 'AYUDA', 'GRACIAS', 'SI',
  'NO', 'HOLA', 'ADIOS', 'ESPERAR', 'FIRMAR'
];

export const CONFIDENCE_THRESHOLD = 0.70;
export const SEQUENCE_LENGTH = 15;
export const CAPTURE_DURATION_MS = 3000;
EOF

echo "✅ Frontend configuration creado"

