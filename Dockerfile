# Stage 1: Build React Frontend Dashboard
FROM node:20-slim AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Python Backend with Playwright, Chromium & Static Dashboard
FROM python:3.11-slim

# Install system dependencies for Playwright & Chromium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    ca-certificates \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m playwright install chromium

# Copy Backend Source
COPY backend/ backend/

# Copy Built Frontend from Stage 1
COPY --from=frontend-builder /frontend/dist frontend/dist

EXPOSE 8000

CMD ["python", "-m", "backend.main"]
