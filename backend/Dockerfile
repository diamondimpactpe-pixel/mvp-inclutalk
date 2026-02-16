FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (incluye ffmpeg para whisper)
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

#TEMPORAL
RUN echo "=== REQUIREMENTS INSIDE IMAGE ===" && nl -ba requirements.txt | sed -n '20,40p'

# Asegura pip/setuptools/wheel (evita: No module named pkg_resources)
#RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir --upgrade pip wheel && \
    pip install --no-cache-dir "setuptools==79.0.1"
    
# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Instala whisper sin aislamiento de build (evita pkg_resources missing)
RUN pip install --no-cache-dir --no-build-isolation openai-whisper==20231117

# Copy application
COPY . .


# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
