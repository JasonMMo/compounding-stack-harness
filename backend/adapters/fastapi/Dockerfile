# backend/adapters/fastapi/Dockerfile
# Build context: repo root (docker build -f backend/adapters/fastapi/Dockerfile .)
#
# Runtime layout inside image:
#   WORKDIR = /app/backend/adapters/fastapi
#   middle/contract/    → /app/middle/contract/
#   presets/ddl/        → /app/presets/ddl/
#
# contract_loader.py resolves: __file__.parents[2] == /app (repo root) → middle/contract/ ✓
# catalog_validator.py resolves: __file__.parents[2] == /app (repo root) → presets/ddl/catalog.yaml ✓

FROM python:3.12-slim

# Prevent .pyc files and enable unbuffered stdout (container log visibility)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8

WORKDIR /app/backend/adapters/fastapi

# Install dependencies first (layer-cache friendly)
COPY backend/adapters/fastapi/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy adapter source files
COPY backend/adapters/fastapi/ ./

# Copy runtime dependencies (read by contract_loader.py and catalog_validator.py)
COPY middle/contract/ /app/middle/contract/
COPY presets/ddl/ /app/presets/ddl/

EXPOSE 8081

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]
