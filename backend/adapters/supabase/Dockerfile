# backend/adapters/supabase/Dockerfile
# Build context: repo root (docker build -f backend/adapters/supabase/Dockerfile .)
#
# Runtime layout inside image:
#   WORKDIR = /app/backend/adapters/supabase
#   fastapi adapter dir → /app/backend/adapters/fastapi  (shared routers)
#   middle/contract/    → /app/middle/contract/
#   presets/ddl/        → /app/presets/ddl/
#
# sys.path injection in main.py adds /app/backend/adapters/fastapi so that
#   wire_response, catalog_validator, contract_loader, routers/* are importable.
#
# catalog_validator.py resolves: __file__.parents[2] == /app (repo root) → presets/ddl/catalog.yaml ✓
# contract_loader.py resolves:   __file__.parents[2] == /app (repo root) → middle/contract/ ✓
# supabase_store.py resolves:    __file__.parents[3] == /app (repo root) → presets/ddl/catalog.yaml ✓

FROM python:3.12-slim

# Prevent .pyc files and enable unbuffered stdout (container log visibility)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8

WORKDIR /app/backend/adapters/supabase

# Install dependencies first (layer-cache friendly)
COPY backend/adapters/supabase/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy this adapter's source files
COPY backend/adapters/supabase/ ./

# Copy shared fastapi adapter modules (routers, wire_response, catalog_validator, contract_loader)
COPY backend/adapters/fastapi/ /app/backend/adapters/fastapi/

# Copy runtime dependencies (read by contract_loader.py and catalog_validator.py)
COPY middle/contract/ /app/middle/contract/
COPY presets/ddl/ /app/presets/ddl/

EXPOSE 8081

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]
